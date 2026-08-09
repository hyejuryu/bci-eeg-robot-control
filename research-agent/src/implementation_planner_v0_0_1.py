from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any

from llm_backend import (
    BackendError,
    BackendToolOutput,
    BackendTurn,
    LLMBackend,
    OllamaChatBackend,
    OpenAIResponsesBackend,
)

from repo_read_tools import (
    RepoReadError,
    get_repo_root,
    read_repo_file,
    search_repo,
)


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

MAX_MODEL_TURNS = 12
MAX_TOOL_CALLS = 30

PROTOCOL_PATH = (
    "research-agent/docs/operating_protocol_v0.1.md"
)

PLANNER_SCOPE_PATH = (
    "research-agent/docs/"
    "implementation_planner_v0.0.1_scope.md"
)

RESEARCH_SPEC_PATH = (
    "research-agent/results/pilot-001/pilot_spec.md"
)

# ---------------------------------------------------------------------
# Run trace
# ---------------------------------------------------------------------


@dataclass
class PlannerTrace:
    model_turns: int = 0
    tool_calls: int = 0
    search_calls: int = 0
    read_calls: int = 0

    inspected_paths: set[str] = field(
        default_factory=set
    )

    read_history: list[dict[str, Any]] = field(
        default_factory=list
    )

    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0

    token_usage_by_turn: list[
        dict[str, int]
    ] = field(
        default_factory=list
    )

    total_backend_call_wall_seconds: float = 0.0

    timing_by_turn: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    request_ids: list[str] = field(
        default_factory=list
    )

    def record_usage(
        self,
        turn: BackendTurn,
        backend_call_wall_seconds: float,
    ) -> None:

        self.input_tokens += (
            turn.input_tokens
        )

        self.cached_input_tokens += (
            turn.cached_input_tokens
        )

        self.cache_write_tokens += (
            turn.cache_write_tokens
        )

        self.output_tokens += (
            turn.output_tokens
        )

        self.token_usage_by_turn.append(
            {
                "turn": self.model_turns,
                "input_tokens": (
                    turn.input_tokens
                ),
                "cached_input_tokens": (
                    turn.cached_input_tokens
                ),
                "cache_write_tokens": (
                    turn.cache_write_tokens
                ),
                "output_tokens": (
                    turn.output_tokens
                ),
            }
        )

        self.total_backend_call_wall_seconds += (
            backend_call_wall_seconds
        )

        self.timing_by_turn.append(
            {
                "turn": self.model_turns,
                "backend_call_wall_seconds": (
                    backend_call_wall_seconds
                ),
                "provider_total_duration_ns": (
                    turn.provider_total_duration_ns
                ),
                "provider_load_duration_ns": (
                    turn.provider_load_duration_ns
                ),
                "provider_prompt_eval_duration_ns": (
                    turn.provider_prompt_eval_duration_ns
                ),
                "provider_eval_duration_ns": (
                    turn.provider_eval_duration_ns
                ),
            }
        )

        if turn.request_id:
            self.request_ids.append(
                turn.request_id
            )


# ---------------------------------------------------------------------
# Repository snapshot
# GPT-5.6 sol과 Ollama + local llm 비교용
# ---------------------------------------------------------------------


def get_repo_commit() -> str:
    """Return the current Git HEAD commit SHA."""
    repo_root = get_repo_root()

    result = subprocess.run(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Unable to identify Git HEAD."
        )

    return result.stdout.strip()


def get_working_tree_changes() -> list[str]:
    """Return uncommitted Git working-tree changes."""
    repo_root = get_repo_root()

    result = subprocess.run(
        [
            "git",
            "-c",
            "core.quotePath=false",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Unable to inspect Git working-tree status."
        )

    return [
        line
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def require_clean_working_tree() -> None:
    """Block a planner run when the Git working tree is dirty."""
    changes = get_working_tree_changes()

    if not changes:
        return

    displayed_changes = changes[:20]

    detail = "\n".join(
        f"- {change}"
        for change in displayed_changes
    )

    if len(changes) > 20:
        detail += (
            f"\n- ... and {len(changes) - 20} more change(s)"
        )

    raise RuntimeError(
        "Planner run requires a clean Git working tree.\n"
        "Commit, stash, or discard the changes before running "
        "the planner.\n\n"
        f"Detected changes:\n{detail}"
    )


# ---------------------------------------------------------------------
# Governing-document loader
# ---------------------------------------------------------------------


def load_full_tracked_text(
    relative_path: str,
    trace: PlannerTrace,
) -> str:
    """Read a complete Git-tracked text file in bounded chunks."""
    chunks: list[str] = []

    start_line = 1

    while True:
        result = read_repo_file(
            relative_path=relative_path,
            start_line=start_line,
            max_lines=1000,
        )

        chunks.append(
            result["content"]
        )

        trace.inspected_paths.add(
            relative_path
        )

        trace.read_history.append(
            {
                "path": relative_path,
                "start_line": result[
                    "start_line"
                ],
                "end_line": result[
                    "end_line"
                ],
                "source": (
                    "governing_loader"
                ),
            }
        )

        if not result["truncated"]:
            break

        start_line = (
            result["end_line"] + 1
        )

    return "\n".join(chunks)


# ---------------------------------------------------------------------
# LLM tool definitions
# ---------------------------------------------------------------------


TOOLS = [
    {
        "type": "function",
        "name": "search_repo",
        "description": (
            "Search Git-tracked repository paths "
            "and text content for a fixed string. "
            "Use this to discover candidate files "
            "or locations relevant to the current "
            "implementation-planning question."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The exact fixed-string "
                        "search query."
                    ),
                },
            },
            "required": [
                "query",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "read_repo_file",
        "description": (
            "Read a bounded line range from one "
            "Git-tracked UTF-8 text file. "
            "Use SEARCH results or direct project "
            "references to choose the file and "
            "line range."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": (
                        "Git-tracked path relative "
                        "to the repository root."
                    ),
                },
                "start_line": {
                    "type": "integer",
                    "description": (
                        "First line to read. "
                        "Line numbering starts at 1."
                    ),
                },
                "max_lines": {
                    "type": "integer",
                    "description": (
                        "Maximum number of lines "
                        "to return. Must be between "
                        "1 and 1000."
                    ),
                },
            },
            "required": [
                "relative_path",
                "start_line",
                "max_lines",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


# ---------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------


def execute_tool_call(
    tool_name: str,
    arguments: dict[str, Any],
    trace: PlannerTrace,
) -> str:
    """Execute one permitted repository tool call."""
    if trace.tool_calls >= MAX_TOOL_CALLS:
        return json.dumps(
            {
                "status": "ERROR",
                "error": (
                    "Planner tool-call limit "
                    "reached."
                ),
            },
            ensure_ascii=False,
        )

    trace.tool_calls += 1

    try:
        if tool_name == "search_repo":
            trace.search_calls += 1

            result = search_repo(
                query=arguments["query"],
            )

        elif tool_name == "read_repo_file":
            trace.read_calls += 1

            result = read_repo_file(
                relative_path=(
                    arguments[
                        "relative_path"
                    ]
                ),
                start_line=(
                    arguments[
                        "start_line"
                    ]
                ),
                max_lines=(
                    arguments[
                        "max_lines"
                    ]
                ),
            )

            trace.inspected_paths.add(
                result["path"]
            )

            trace.read_history.append(
                {
                    "path": result["path"],
                    "start_line": result[
                        "start_line"
                    ],
                    "end_line": result[
                        "end_line"
                    ],
                    "source": "llm_tool",
                }
            )

        else:
            result = {
                "status": "ERROR",
                "error": (
                    f"Unsupported tool: "
                    f"{tool_name}"
                ),
            }

    except (
        RepoReadError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        result = {
            "status": "ERROR",
            "error": str(exc),
        }

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------
# Final-output validation
# ---------------------------------------------------------------------


def extract_basis_paths(
    text: str,
) -> list[str]:
    """Extract backticked paths from inline BASIS fields."""
    paths: list[str] = []

    for line in text.splitlines():
        if not line.startswith(
            "BASIS:"
        ):
            continue

        value = line[
            len("BASIS:"):
        ].strip()

        if value == "NONE":
            continue

        paths.extend(
            re.findall(
                r"`([^`]+)`",
                value,
            )
        )

    return paths


def validate_planner_output(
    text: str,
    trace: PlannerTrace,
) -> list[str]:
    """Return validation errors for the final planner response."""
    errors: list[str] = []

    stripped = text.strip()

    if not stripped.startswith(
        "PLANNER_STATUS:"
    ):
        errors.append(
            "The first non-empty line must be "
            "PLANNER_STATUS."
        )

    status_match = re.search(
        (
            r"^PLANNER_STATUS:\s*"
            r"(COMPLETE|BLOCKED)\s*$"
        ),
        stripped,
        flags=re.MULTILINE,
    )

    if status_match is None:
        errors.append(
            "PLANNER_STATUS must be COMPLETE "
            "or BLOCKED."
        )

        return errors

    status = status_match.group(1)

    if status == "COMPLETE":
        required_sections = [
            "PRIOR_WORK",
            "REUSE",
            "NEW_IMPLEMENTATION",
            "VALIDATION",
            "EXECUTION_PLAN",
        ]

        for section in required_sections:
            if not re.search(
                rf"^{re.escape(section)}(?:\s*:)?\s*$",
                stripped,
                flags=re.MULTILINE,
            ):
                errors.append(
                    f"Missing required section: "
                    f"{section}"
                )

        if not re.search(
            (
                r"^OPEN_DECISIONS:\s*"
                r"(NONE|REQUIRED)\s*$"
            ),
            stripped,
            flags=re.MULTILINE,
        ):
            errors.append(
                "OPEN_DECISIONS must be NONE "
                "or REQUIRED."
            )

    elif status == "BLOCKED":
        for field_name in [
            "BLOCK_REASON:",
            "DETAIL:",
            "BASIS:",
        ]:
            if field_name not in stripped:
                errors.append(
                    f"Missing blocked field: "
                    f"{field_name}"
                )

        if not re.search(
            (
                r"^BLOCK_REASON:\s*"
                r"(MISSING_CONTEXT|ACCESS_ERROR|SPEC_CONFLICT|OTHER)\s*$"
            ),
            stripped,
            flags=re.MULTILINE,
        ):
            errors.append(
                "BLOCK_REASON must use an allowed label."
            )

    basis_paths = extract_basis_paths(
        stripped
    )

    for path in basis_paths:
        if path not in trace.inspected_paths:
            errors.append(
                "BASIS path was not READ during "
                f"this run: {path}"
            )

    return errors


# ---------------------------------------------------------------------
# Planner prompts
# ---------------------------------------------------------------------


def build_planner_instructions(
    planner_scope: str,
    protocol: str,
) -> str:
    return f"""
You are Implementation Planner v0.0.1.

The following records govern your behavior.

<IMPLEMENTATION_PLANNER_SCOPE>
{planner_scope}
</IMPLEMENTATION_PLANNER_SCOPE>

<OPERATING_PROTOCOL>
{protocol}
</OPERATING_PROTOCOL>

Additional operational requirements:

1. The planner MUST use only the provided SEARCH and READ tools for
   repository access.

2. The planner MUST NOT assume repository contents that have not been
   obtained during the current run.

3. The planner MUST treat SEARCH results as candidate evidence only.

4. The planner MUST NOT use a repository path as BASIS for a material
   judgment unless relevant content from that path has been READ during
   the current run.

5. The planner MUST inspect relevant direct references from governing
   records before using broader repository search when those references
   can address the current planning question.

6. The planner MAY use broader repository SEARCH when direct references
   are absent or insufficient.

7. Historical repository records MAY be used as context or evidence.

8. Historical repository records MUST NOT override the governing
   records.

9. If governing records materially conflict, the planner MUST return:

   PLANNER_STATUS: BLOCKED
   BLOCK_REASON: SPEC_CONFLICT

10. If repository evidence is insufficient for a reliable implementation
    proposal, the planner MUST return BLOCKED rather than infer missing
    project facts.

11. The planner MUST NOT:
    - execute code;
    - modify project files;
    - modify or reinterpret the frozen research specification;
    - introduce research methodology outside the frozen specification;
    - perform scientific interpretation.

12. The final response MUST be written in English.

Each material implementation judgment MUST use:

ITEM: <short item name>
PROJECT_RELATION: REUSE | EXTENSION | NEW
BASIS: `path/to/file` | `path/to/other/file`
RATIONALE: <1-3 sentences>

BASIS MUST appear on one line.

When planning is complete, the first line MUST be:

PLANNER_STATUS: COMPLETE

A COMPLETE response MUST contain:

PRIOR_WORK
REUSE
NEW_IMPLEMENTATION
VALIDATION
EXECUTION_PLAN
OPEN_DECISIONS: NONE | REQUIRED

If OPEN_DECISIONS is REQUIRED, each decision MUST contain:

DECISION: <human decision required>
BASIS: `path/to/file`
IMPACT: <1-3 sentences>

If planning is blocked, the response MUST use:

PLANNER_STATUS: BLOCKED
BLOCK_REASON: MISSING_CONTEXT | ACCESS_ERROR | SPEC_CONFLICT | OTHER
DETAIL: <1-3 sentences>
BASIS: `path/to/file`

BASIS: NONE MAY be used only when no relevant repository path is
available.
""".strip()


def build_planner_task(
    research_spec: str,
    repo_commit: str,
) -> str:
    return f"""
Prepare the implementation proposal required by the frozen research
specification below.

Repository snapshot:

GIT_HEAD:
{repo_commit}

<FROZEN_RESEARCH_SPEC>
{research_spec}
</FROZEN_RESEARCH_SPEC>

The planner MUST inspect repository records as required to prepare the
implementation proposal.

The planner MUST NOT implement or execute the proposed work.

The planner MUST stop after producing the Implementation Proposal or a
BLOCKED report.
""".strip()


# ---------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------


def run_agent_loop(
    backend: LLMBackend,
    instructions: str,
    task: str,
    trace: PlannerTrace,
    validate_final: bool,
) -> str:
    """
    Run the model/tool loop until the model returns final text.
    """
    backend.start_run(
        instructions=instructions,
        task=task,
        tools=TOOLS,
    )

    pending_tool_outputs: list[
        BackendToolOutput
    ] = []

    for _ in range(
        MAX_MODEL_TURNS
    ):
        trace.model_turns += 1

        backend_call_started = (
            time.perf_counter()
        )

        turn = backend.run_turn(
            tool_outputs=(
                pending_tool_outputs
            )
        )

        backend_call_wall_seconds = (
            time.perf_counter()
            - backend_call_started
        )

        pending_tool_outputs = []

        trace.record_usage(
            turn,
            backend_call_wall_seconds,
        )

        if turn.tool_calls:
            for call in turn.tool_calls:
                try:
                    arguments = json.loads(
                        call.arguments_json
                    )

                except json.JSONDecodeError:
                    tool_output = json.dumps(
                        {
                            "status": "ERROR",
                            "error": (
                                "Invalid tool-call "
                                "JSON arguments."
                            ),
                        },
                        ensure_ascii=False,
                    )

                else:
                    tool_output = (
                        execute_tool_call(
                            tool_name=call.name,
                            arguments=arguments,
                            trace=trace,
                        )
                    )

                pending_tool_outputs.append(
                    BackendToolOutput(
                        call_id=(
                            call.call_id
                        ),
                        output=tool_output,
                    )
                )

            continue

        final_text = (
            turn.output_text
            or ""
        ).strip()

        if not final_text:
            backend.add_user_message(
                "No final text was returned. "
                "Continue the task."
            )

            continue

        if not validate_final:
            return final_text

        validation_errors = (
            validate_planner_output(
                final_text,
                trace,
            )
        )

        if not validation_errors:
            return final_text

        correction = (
            "The proposed final response failed "
            "deterministic validation.\n\n"
            "Errors:\n- "
            + "\n- ".join(
                validation_errors
            )
            + "\n\nCorrect the proposal. "
            "Use READ first if a required BASIS "
            "path has not yet been inspected."
        )

        backend.add_user_message(
            correction
        )

    raise RuntimeError(
        "Planner exceeded the maximum "
        "model-turn limit."
    )


# ---------------------------------------------------------------------
# Tool-loop smoke test
# ---------------------------------------------------------------------


def run_tool_smoke_test(
    backend: LLMBackend,
) -> None:
    trace = PlannerTrace()

    repo_commit = (
        get_repo_commit()
    )

    backend_metadata = (
        backend.metadata()
    )

    instructions = """
You are performing a read-only repository tool-loop smoke test.

Available repository tools:

SEARCH
READ

You MUST perform the following sequence:

1. You MUST call SEARCH using the exact fixed string:
   decision_rule

2. You MUST inspect the SEARCH results and select one Python file that
   appears to implement the offline decision rule.

3. You MUST NOT select a file whose apparent primary purpose is figure
   generation when a decision-rule implementation file is available.

4. You MUST call READ on the selected file with:
   start_line = 1
   max_lines = 40

5. You MUST base the file selection only on information obtained through
   the provided tools during this run.

6. You MUST NOT use unverified repository knowledge from outside the
   current tool results.

7. After the required SEARCH and READ calls complete successfully, you
   MUST return exactly one line:

   TOOL_LOOP_OK: <repository path>

You MUST NOT perform any additional repository operation after the
required READ succeeds.
""".strip()

    task = (
        "Run the required SEARCH and READ "
        "tool test now."
    )

    final_text = run_agent_loop(
        backend=backend,
        instructions=instructions,
        task=task,
        trace=trace,
        validate_final=False,
    )

    result_path = (
        final_text.removeprefix(
            "TOOL_LOOP_OK:"
        ).strip()
    )

    smoke_pass = (
        trace.search_calls == 1
        and trace.model_turns == 3
        and trace.read_calls == 1
        and trace.tool_calls == 2
        and len(trace.read_history) == 1
        and len(final_text.splitlines()) == 1
        and final_text.startswith(
            "TOOL_LOOP_OK:"
        )
        and result_path
        == trace.read_history[0]["path"]
    )

    print(
        "\n=== TOOL LOOP RESULT ==="
    )
    print(final_text)

    print(
        "\n=== TOOL LOOP METADATA ==="
    )
    print(
        json.dumps(
            {
                "status": (
                    "PASS"
                    if smoke_pass
                    else "FAIL"
                ),
                "backend": (
                    backend_metadata[
                        "backend"
                    ]
                ),
                "model": (
                    backend_metadata[
                        "model"
                    ]
                ),
                "backend_settings": {
                    key: value
                    for key, value
                    in backend_metadata.items()
                    if key
                    not in {
                        "backend",
                        "model",
                    }
                },
                "git_head": repo_commit,
                "model_turns": (
                    trace.model_turns
                ),
                "tool_calls": (
                    trace.tool_calls
                ),
                "search_calls": (
                    trace.search_calls
                ),
                "read_calls": (
                    trace.read_calls
                ),
                "inspected_paths": sorted(
                    trace.inspected_paths
                ),
                "read_history": (
                    trace.read_history
                ),
                "input_tokens": (
                    trace.input_tokens
                ),
                "cached_input_tokens": (
                    trace.cached_input_tokens
                ),
                "cache_write_tokens": (
                    trace.cache_write_tokens
                ),
                "output_tokens": (
                    trace.output_tokens
                ),
                "token_usage_by_turn": (
                    trace.token_usage_by_turn
                ),
                "total_backend_call_wall_seconds": (
                    trace.total_backend_call_wall_seconds
                ),
                "timing_by_turn": (
                    trace.timing_by_turn
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


# ---------------------------------------------------------------------
# Full planner run
# ---------------------------------------------------------------------


def run_full_planner(
    backend: LLMBackend,
) -> None:
    require_clean_working_tree()

    trace = PlannerTrace()

    planner_scope = (
        load_full_tracked_text(
            PLANNER_SCOPE_PATH,
            trace,
        )
    )

    protocol = (
        load_full_tracked_text(
            PROTOCOL_PATH,
            trace,
        )
    )

    research_spec = (
        load_full_tracked_text(
            RESEARCH_SPEC_PATH,
            trace,
        )
    )

    repo_commit = (
        get_repo_commit()
    )

    backend_metadata = (
        backend.metadata()
    )

    instructions = (
        build_planner_instructions(
            planner_scope=planner_scope,
            protocol=protocol,
        )
    )

    task = build_planner_task(
        research_spec=research_spec,
        repo_commit=repo_commit,
    )

    final_text = run_agent_loop(
        backend=backend,
        instructions=instructions,
        task=task,
        trace=trace,
        validate_final=True,
    )

    print(
        "\n=== PLANNER RUN METADATA ==="
    )

    print(
        json.dumps(
            {
                "backend": (
                    backend_metadata[
                        "backend"
                    ]
                ),
                "model": (
                    backend_metadata[
                        "model"
                    ]
                ),
                "backend_settings": {
                    key: value
                    for key, value
                    in backend_metadata.items()
                    if key
                    not in {
                        "backend",
                        "model",
                    }
                },
                "git_head": repo_commit,

                "working_tree_status": "CLEAN",
                "model_turns": (
                    trace.model_turns
                ),
                "tool_calls": (
                    trace.tool_calls
                ),
                "search_calls": (
                    trace.search_calls
                ),
                "read_calls": (
                    trace.read_calls
                ),
                "inspected_paths": sorted(
                    trace.inspected_paths
                ),
                "read_history": (
                    trace.read_history
                ),
                "input_tokens": (
                    trace.input_tokens
                ),
                "cached_input_tokens": (
                    trace.cached_input_tokens
                ),
                "cache_write_tokens": (
                    trace.cache_write_tokens
                ),
                "output_tokens": (
                    trace.output_tokens
                ),
                "token_usage_by_turn": (
                    trace.token_usage_by_turn
                ),
                "total_backend_call_wall_seconds": (
                    trace.total_backend_call_wall_seconds
                ),
                "timing_by_turn": (
                    trace.timing_by_turn
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    print(
        "\n=== IMPLEMENTATION PLANNER OUTPUT ==="
    )

    print(final_text)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Implementation Planner "
            "v0.0.1 prototype."
        )
    )

    parser.add_argument(
        "--mode",
        choices=[
            "smoke",
            "planner",
        ],
        default="smoke",
    )

    parser.add_argument(
        "--backend",
        choices=[
            "openai",
            "ollama",
        ],
        default="openai",
    )

    parser.add_argument(
        "--ollama-model",
        default="gpt-oss:20b",
    )

    parser.add_argument(
        "--ollama-thinking",
        choices=[
            "low",
            "medium",
            "high",
        ],
        default="high",
    )

    parser.add_argument(
        "--ollama-context",
        type=int,
        default=32768,
    )

    args = parser.parse_args()

    try:
        if args.backend == "openai":
            backend: LLMBackend = (
                OpenAIResponsesBackend()
            )

        else:
            backend = (
                OllamaChatBackend(
                    model=(
                        args.ollama_model
                    ),
                    thinking=(
                        args.ollama_thinking
                    ),
                    context_length=(
                        args.ollama_context
                    ),
                )
            )

        if args.mode == "smoke":
            run_tool_smoke_test(
                backend
            )

        elif args.mode == "planner":
            run_full_planner(
                backend
            )

    except (
        BackendError,
        RepoReadError,
        RuntimeError,
    ) as exc:
        print(
            "\n=== PLANNER ERROR ==="
        )
        print(str(exc))


if __name__ == "__main__":
    main()