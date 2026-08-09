from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import openai
from openai import OpenAI


# ---------------------------------------------------------------------
# Shared backend types
# ---------------------------------------------------------------------


class BackendError(RuntimeError):
    """Raised when an LLM backend cannot complete a request."""


@dataclass(frozen=True)
class BackendToolCall:
    call_id: str
    name: str
    arguments_json: str


@dataclass(frozen=True)
class BackendToolOutput:
    call_id: str
    output: str


@dataclass(frozen=True)
class BackendTurn:
    output_text: str
    tool_calls: list[BackendToolCall]

    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0

    provider_total_duration_ns: int | None = None
    provider_load_duration_ns: int | None = None
    provider_prompt_eval_duration_ns: int | None = None
    provider_eval_duration_ns: int | None = None

    request_id: str | None = None


# ---------------------------------------------------------------------
# Backend interface
# ---------------------------------------------------------------------


class LLMBackend:
    """Common interface used by the Implementation Planner."""

    def start_run(
        self,
        instructions: str,
        task: str,
        tools: list[dict[str, Any]],
    ) -> None:
        raise NotImplementedError

    def run_turn(
        self,
        tool_outputs: list[BackendToolOutput] | None = None,
    ) -> BackendTurn:
        raise NotImplementedError

    def add_user_message(
        self,
        text: str,
    ) -> None:
        raise NotImplementedError

    def metadata(
        self,
    ) -> dict[str, Any]:
        raise NotImplementedError


def _convert_tools_for_ollama(
    tools: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert Planner function tools to Ollama chat format."""
    converted: list[
        dict[str, Any]
    ] = []

    for tool in tools:
        if tool.get("type") != "function":
            raise BackendError(
                "Ollama backend received an unsupported tool type."
            )

        name = tool.get("name")
        parameters = tool.get(
            "parameters"
        )

        if (
            not isinstance(name, str)
            or not isinstance(
                parameters,
                dict,
            )
        ):
            raise BackendError(
                "Ollama backend received an invalid function tool."
            )

        converted.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": (
                        tool.get(
                            "description",
                            "",
                        )
                    ),
                    "parameters": (
                        parameters
                    ),
                },
            }
        )

    return converted


# ---------------------------------------------------------------------
# OpenAI Responses backend
# ---------------------------------------------------------------------


class OpenAIResponsesBackend(
    LLMBackend
):
    """OpenAI Responses API backend."""

    def __init__(
        self,
        model: str = "gpt-5.6-sol",
        reasoning_effort: str = "medium",
    ) -> None:
        self.model = model
        self.reasoning_effort = reasoning_effort

        self._client = OpenAI()

        self._instructions: str | None = None
        self._tools: list[
            dict[str, Any]
        ] | None = None

        self._input_items: list[Any] = []

    def start_run(
        self,
        instructions: str,
        task: str,
        tools: list[dict[str, Any]],
    ) -> None:
        self._instructions = instructions
        self._tools = tools

        self._input_items = [
            {
                "role": "user",
                "content": task,
            }
        ]

    def run_turn(
        self,
        tool_outputs: list[BackendToolOutput] | None = None,
    ) -> BackendTurn:
        if (
            self._instructions is None
            or self._tools is None
        ):
            raise BackendError(
                "Backend run has not been initialized."
            )

        for tool_output in (
            tool_outputs or []
        ):
            self._input_items.append(
                {
                    "type": (
                        "function_call_output"
                    ),
                    "call_id": (
                        tool_output.call_id
                    ),
                    "output": (
                        tool_output.output
                    ),
                }
            )

        try:
            response = (
                self._client.responses.create(
                    model=self.model,
                    reasoning={
                        "effort": (
                            self.reasoning_effort
                        ),
                    },
                    instructions=(
                        self._instructions
                    ),
                    tools=self._tools,
                    input=self._input_items,
                    store=False,
                )
            )

        except openai.APIError as exc:
            raise BackendError(
                "OpenAI API request failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        self._input_items += list(
            response.output
        )

        tool_calls: list[
            BackendToolCall
        ] = []

        for item in response.output:
            if (
                getattr(
                    item,
                    "type",
                    None,
                )
                != "function_call"
            ):
                continue

            tool_calls.append(
                BackendToolCall(
                    call_id=item.call_id,
                    name=item.name,
                    arguments_json=(
                        item.arguments
                    ),
                )
            )

        usage = getattr(
            response,
            "usage",
            None,
        )

        input_tokens = 0
        cached_input_tokens = 0
        cache_write_tokens = 0
        output_tokens = 0

        if usage is not None:
            input_tokens = (
                getattr(
                    usage,
                    "input_tokens",
                    0,
                )
                or 0
            )

            output_tokens = (
                getattr(
                    usage,
                    "output_tokens",
                    0,
                )
                or 0
            )

            details = getattr(
                usage,
                "input_tokens_details",
                None,
            )

            if details is not None:
                cached_input_tokens = (
                    getattr(
                        details,
                        "cached_tokens",
                        0,
                    )
                    or 0
                )

                cache_write_tokens = (
                    getattr(
                        details,
                        "cache_write_tokens",
                        0,
                    )
                    or 0
                )

        return BackendTurn(
            output_text=(
                response.output_text
                or ""
            ),
            tool_calls=tool_calls,
            input_tokens=input_tokens,
            cached_input_tokens=(
                cached_input_tokens
            ),
            cache_write_tokens=(
                cache_write_tokens
            ),
            output_tokens=output_tokens,
            request_id=getattr(
                response,
                "_request_id",
                None,
            ),
        )

    def add_user_message(
        self,
        text: str,
    ) -> None:
        self._input_items.append(
            {
                "role": "user",
                "content": text,
            }
        )

    def metadata(
        self,
    ) -> dict[str, Any]:
        return {
            "backend": "openai_responses",
            "model": self.model,
            "reasoning_effort": (
                self.reasoning_effort
            ),
        }


# ---------------------------------------------------------------------
# Ollama native chat backend
# ---------------------------------------------------------------------


class OllamaChatBackend(
    LLMBackend
):
    """Ollama native chat API backend."""

    def __init__(
        self,
        model: str = "gpt-oss:20b",
        thinking: str = "high",
        context_length: int = 32768,
        base_url: str = "http://127.0.0.1:11434",
        keep_alive: str = "5m",
        request_timeout_seconds: int = 1800,
    ) -> None:
        if context_length <= 0:
            raise BackendError(
                "Ollama context length must be positive."
            )

        self.model = model
        self.thinking = thinking
        self.context_length = (
            context_length
        )
        self.base_url = (
            base_url.rstrip("/")
        )
        self.keep_alive = keep_alive
        self.request_timeout_seconds = (
            request_timeout_seconds
        )

        self._messages: list[
            dict[str, Any]
        ] = []

        self._tools: list[
            dict[str, Any]
        ] | None = None

        self._call_counter = 0

        self._tool_name_by_call_id: dict[
            str,
            str,
        ] = {}

    def start_run(
        self,
        instructions: str,
        task: str,
        tools: list[dict[str, Any]],
    ) -> None:
        self._tools = (
            _convert_tools_for_ollama(
                tools
            )
        )

        self._messages = [
            {
                "role": "system",
                "content": instructions,
            },
            {
                "role": "user",
                "content": task,
            },
        ]

        self._call_counter = 0
        self._tool_name_by_call_id = {}

    def _post_chat(
        self,
    ) -> dict[str, Any]:
        if self._tools is None:
            raise BackendError(
                "Backend run has not been initialized."
            )

        payload = {
            "model": self.model,
            "messages": self._messages,
            "tools": self._tools,
            "stream": False,
            "think": self.thinking,
            "options": {
                "num_ctx": (
                    self.context_length
                ),
            },
            "keep_alive": self.keep_alive,
        }

        request = Request(
            (
                f"{self.base_url}"
                "/api/chat"
            ),
            data=json.dumps(
                payload,
                ensure_ascii=False,
            ).encode("utf-8"),
            headers={
                "Content-Type": (
                    "application/json"
                ),
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=(
                    self.request_timeout_seconds
                ),
            ) as response:
                response_text = (
                    response.read().decode(
                        "utf-8"
                    )
                )

        except HTTPError as exc:
            error_body = (
                exc.read().decode(
                    "utf-8",
                    errors="replace",
                )
            )

            raise BackendError(
                "Ollama API HTTP error "
                f"{exc.code}: {error_body}"
            ) from exc

        except (
            URLError,
            TimeoutError,
            OSError,
        ) as exc:
            raise BackendError(
                "Ollama API request failed: "
                f"{exc}"
            ) from exc

        try:
            result = json.loads(
                response_text
            )

        except json.JSONDecodeError as exc:
            raise BackendError(
                "Ollama returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise BackendError(
                "Ollama returned an invalid response."
            )

        return result

    def run_turn(
        self,
        tool_outputs: list[
            BackendToolOutput
        ] | None = None,
    ) -> BackendTurn:
        if self._tools is None:
            raise BackendError(
                "Backend run has not been initialized."
            )

        for tool_output in (
            tool_outputs or []
        ):
            tool_name = (
                self._tool_name_by_call_id.pop(
                    tool_output.call_id,
                    None,
                )
            )

            if tool_name is None:
                raise BackendError(
                    "Unknown Ollama tool-call ID: "
                    f"{tool_output.call_id}"
                )

            self._messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": (
                        tool_output.output
                    ),
                }
            )

        result = self._post_chat()

        message = result.get(
            "message"
        )

        if not isinstance(
            message,
            dict,
        ):
            raise BackendError(
                "Ollama response is missing a valid message."
            )

        assistant_message: dict[
            str,
            Any,
        ] = {
            "role": "assistant",
            "content": (
                message.get(
                    "content",
                    "",
                )
                or ""
            ),
        }

        thinking = message.get(
            "thinking"
        )

        if thinking:
            assistant_message[
                "thinking"
            ] = thinking

        raw_tool_calls = (
            message.get(
                "tool_calls"
            )
            or []
        )

        if raw_tool_calls:
            assistant_message[
                "tool_calls"
            ] = raw_tool_calls

        self._messages.append(
            assistant_message
        )

        tool_calls: list[
            BackendToolCall
        ] = []

        for raw_call in raw_tool_calls:
            function = raw_call.get(
                "function",
                {}
            )

            name = function.get(
                "name"
            )

            arguments = function.get(
                "arguments",
                {},
            )

            if not isinstance(
                name,
                str,
            ):
                raise BackendError(
                    "Ollama returned a tool call without a valid name."
                )

            if isinstance(
                arguments,
                str,
            ):
                arguments_json = (
                    arguments
                )
            else:
                arguments_json = (
                    json.dumps(
                        arguments,
                        ensure_ascii=False,
                    )
                )

            self._call_counter += 1

            call_id = (
                "ollama_call_"
                f"{self._call_counter}"
            )

            self._tool_name_by_call_id[
                call_id
            ] = name

            tool_calls.append(
                BackendToolCall(
                    call_id=call_id,
                    name=name,
                    arguments_json=(
                        arguments_json
                    ),
                )
            )

        return BackendTurn(
            output_text=(
                assistant_message[
                    "content"
                ]
            ),
            tool_calls=tool_calls,
            input_tokens=int(
                result.get(
                    "prompt_eval_count",
                    0,
                )
                or 0
            ),
            cached_input_tokens=0,
            cache_write_tokens=0,
            output_tokens=int(
                result.get(
                    "eval_count",
                    0,
                )
                or 0
            ),
            provider_total_duration_ns=(
                int(result["total_duration"])
                if result.get(
                    "total_duration"
                ) is not None
                else None
            ),
            provider_load_duration_ns=(
                int(result["load_duration"])
                if result.get(
                    "load_duration"
                ) is not None
                else None
            ),
            provider_prompt_eval_duration_ns=(
                int(
                    result[
                        "prompt_eval_duration"
                    ]
                )
                if result.get(
                    "prompt_eval_duration"
                ) is not None
                else None
            ),
            provider_eval_duration_ns=(
                int(
                    result[
                        "eval_duration"
                    ]
                )
                if result.get(
                    "eval_duration"
                ) is not None
                else None
            ),
            request_id=None,
        )


    def add_user_message(
        self,
        text: str,
    ) -> None:
        self._messages.append(
            {
                "role": "user",
                "content": text,
            }
        )

    def metadata(
        self,
    ) -> dict[str, Any]:
        return {
            "backend": (
                "ollama_native_chat"
            ),
            "model": self.model,
            "thinking": self.thinking,
            "context_length": (
                self.context_length
            ),
            "base_url": self.base_url,
            "keep_alive": (
                self.keep_alive
            ),
        }