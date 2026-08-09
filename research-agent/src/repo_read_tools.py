from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Expected location:
#
# repo-root/
# └─ research-agent/
#    └─ src/
#       └─ repo_read_tools.py
#
# parents[2] points to repo-root.
EXPECTED_REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SEARCH_RESULTS = 20
MAX_SEARCH_RESULTS = 50

DEFAULT_READ_LINES = 300
MAX_READ_LINES = 1000

MAX_SEARCH_SNIPPET_CHARS = 240


# Secret-like files remain inaccessible even if accidentally tracked.
DENIED_BASENAMES = {
    ".env",
    "credentials",
    "credentials.json",
    "credentials.yaml",
    "credentials.yml",
    "secrets",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    "id_rsa",
    "id_ed25519",
}

DENIED_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}

# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------


class RepoReadError(RuntimeError):
    """Raised when a repository read operation violates tool rules."""


# ---------------------------------------------------------------------
# Repository helpers
# ---------------------------------------------------------------------


def get_repo_root() -> Path:
    """Return the canonical root of the current Git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=EXPECTED_REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.returncode != 0:
        raise RepoReadError(
            "Unable to identify the Git repository root."
        )

    repo_root = Path(result.stdout.strip()).resolve()

    if not repo_root.is_dir():
        raise RepoReadError(
            "Resolved Git repository root does not exist."
        )

    return repo_root


def list_git_tracked_files() -> list[str]:
    """Return repository-relative paths currently tracked by Git."""
    repo_root = get_repo_root()

    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        raise RepoReadError(
            "Unable to list Git-tracked files."
        )

    raw_paths = result.stdout.decode(
        "utf-8",
        errors="replace",
    )

    return [
        relative_path
        for relative_path in raw_paths.split("\0")
        if relative_path
    ]


# ---------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------


def _normalize_relative_path(relative_path: str) -> str:
    """Normalize and validate a repository-relative path."""
    if not isinstance(relative_path, str):
        raise RepoReadError(
            "Repository path must be a string."
        )

    raw = relative_path.strip()

    if not raw:
        raise RepoReadError(
            "Repository path must not be empty."
        )

    if PureWindowsPath(raw).is_absolute():
        raise RepoReadError(
            "Absolute paths are not allowed."
        )

    normalized = raw.replace("\\", "/")
    posix_path = PurePosixPath(normalized)

    if posix_path.is_absolute():
        raise RepoReadError(
            "Absolute paths are not allowed."
        )

    if ".." in posix_path.parts:
        raise RepoReadError(
            "Parent-directory traversal is not allowed."
        )

    if posix_path.parts and ":" in posix_path.parts[0]:
        raise RepoReadError(
            "Drive-qualified paths are not allowed."
        )

    clean_parts = [
        part
        for part in posix_path.parts
        if part not in ("", ".")
    ]

    if not clean_parts:
        raise RepoReadError(
            "Repository path must identify a file."
        )

    return PurePosixPath(*clean_parts).as_posix()


def _is_denied_path(relative_path: str) -> bool:
    """Return True when the path is outside Planner read authority."""
    path = PurePosixPath(relative_path)

    lower_parts = [
        part.lower()
        for part in path.parts
    ]

    if ".git" in lower_parts:
        return True

    basename = path.name.lower()

    if basename in DENIED_BASENAMES:
        return True

    if basename.startswith(".env."):
        return True

    suffix = Path(basename).suffix.lower()

    if suffix in DENIED_SUFFIXES:
        return True

    return False


def _validate_tracked_path(
    relative_path: str,
) -> tuple[str, Path]:
    """
    Validate that a path is repository-relative, allowed, and Git-tracked.
    """
    normalized = _normalize_relative_path(
        relative_path
    )

    if _is_denied_path(normalized):
        raise RepoReadError(
            f"Access denied for repository path: {normalized}"
        )

    tracked_files = set(
        list_git_tracked_files()
    )

    if normalized not in tracked_files:
        raise RepoReadError(
            f"File is not Git-tracked: {normalized}"
        )

    repo_root = get_repo_root()

    absolute_path = (
        repo_root / Path(normalized)
    ).resolve()

    try:
        absolute_path.relative_to(repo_root)
    except ValueError as exc:
        raise RepoReadError(
            "Resolved path escapes the repository root."
        ) from exc

    if not absolute_path.is_file():
        raise RepoReadError(
            f"Tracked path is not a readable file: {normalized}"
        )

    return normalized, absolute_path


def _ensure_text_file(
    absolute_path: Path,
) -> None:
    """Reject files that appear to contain binary data."""
    with absolute_path.open("rb") as file:
        sample = file.read(8192)

    if b"\x00" in sample:
        raise RepoReadError(
            "Binary files are not supported by READ."
        )


# ---------------------------------------------------------------------
# SEARCH tool
# ---------------------------------------------------------------------


def search_repo(
    query: str,
    max_results: int = DEFAULT_SEARCH_RESULTS,
) -> dict[str, Any]:
    """
    Search Git-tracked paths and text content for a fixed string.
    """
    if not isinstance(query, str):
        raise RepoReadError(
            "Search query must be a string."
        )

    query = query.strip()

    if not query:
        raise RepoReadError(
            "Search query must not be empty."
        )

    if not isinstance(max_results, int):
        raise RepoReadError(
            "max_results must be an integer."
        )

    if not 1 <= max_results <= MAX_SEARCH_RESULTS:
        raise RepoReadError(
            f"max_results must be between 1 and "
            f"{MAX_SEARCH_RESULTS}."
        )

    repo_root = get_repo_root()
    tracked_files = list_git_tracked_files()

    results: list[dict[str, Any]] = []
    seen: set[tuple[str, int | None]] = set()

    query_lower = query.lower()

    # -------------------------------------------------------------
    # 1. Path matches
    # -------------------------------------------------------------

    for relative_path in tracked_files:
        if len(results) >= max_results:
            break

        if _is_denied_path(relative_path):
            continue

        if query_lower in relative_path.lower():
            key = (
                relative_path,
                None,
            )

            if key in seen:
                continue

            results.append(
                {
                    "path": relative_path,
                    "match_type": "PATH",
                    "line_number": None,
                    "snippet": None,
                }
            )

            seen.add(key)

    # -------------------------------------------------------------
    # 2. Content matches
    # -------------------------------------------------------------

    grep_result = subprocess.run(
        [
            "git",
            "-c",
            "core.quotePath=false",
            "grep",
            "-n",
            "-I",
            "-i",
            "-F",
            "-e",
            query,
            "--",
            ".",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    # git grep:
    # 0 = at least one match
    # 1 = no match
    # >1 = command failure
    if grep_result.returncode not in (0, 1):
        raise RepoReadError(
            "Git content search failed."
        )

    if grep_result.returncode == 0:
        for line in grep_result.stdout.splitlines():

            if len(results) >= max_results:
                break

            parts = line.split(":", 2)

            if len(parts) != 3:
                continue

            (
                relative_path,
                line_number_raw,
                snippet,
            ) = parts

            relative_path = (
                relative_path.removeprefix("./")
            )

            if _is_denied_path(relative_path):
                continue

            try:
                line_number = int(
                    line_number_raw
                )
            except ValueError:
                continue

            key = (
                relative_path,
                line_number,
            )

            if key in seen:
                continue

            snippet = snippet.strip()

            if len(snippet) > MAX_SEARCH_SNIPPET_CHARS:
                snippet = (
                    snippet[
                        :MAX_SEARCH_SNIPPET_CHARS
                    ]
                    + "..."
                )

            results.append(
                {
                    "path": relative_path,
                    "match_type": "CONTENT",
                    "line_number": line_number,
                    "snippet": snippet,
                }
            )

            seen.add(key)

    return {
        "query": query,
        "result_count": len(results),
        "max_results": max_results,
        "results": results,
    }


# ---------------------------------------------------------------------
# READ tool
# ---------------------------------------------------------------------


def read_repo_file(
    relative_path: str,
    start_line: int = 1,
    max_lines: int = DEFAULT_READ_LINES,
) -> dict[str, Any]:
    """
    Read a bounded line range from one Git-tracked UTF-8 text file.
    """
    if not isinstance(start_line, int):
        raise RepoReadError(
            "start_line must be an integer."
        )

    if start_line < 1:
        raise RepoReadError(
            "start_line must be >= 1."
        )

    if not isinstance(max_lines, int):
        raise RepoReadError(
            "max_lines must be an integer."
        )

    if not 1 <= max_lines <= MAX_READ_LINES:
        raise RepoReadError(
            f"max_lines must be between 1 and "
            f"{MAX_READ_LINES}."
        )

    normalized, absolute_path = (
        _validate_tracked_path(
            relative_path
        )
    )

    _ensure_text_file(
        absolute_path
    )

    selected_lines: list[
        tuple[int, str]
    ] = []

    total_lines = 0

    try:
        with absolute_path.open(
            "r",
            encoding="utf-8",
            errors="strict",
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1,
            ):
                total_lines = line_number

                if line_number < start_line:
                    continue

                if (
                    line_number
                    >= start_line + max_lines
                ):
                    continue

                selected_lines.append(
                    (
                        line_number,
                        line,
                    )
                )

    except UnicodeDecodeError as exc:
        raise RepoReadError(
            f"File is not valid UTF-8 text: "
            f"{normalized}"
        ) from exc

    if total_lines > 0 and start_line > total_lines:
        raise RepoReadError(
            f"start_line {start_line} exceeds "
            f"file length ({total_lines} lines)."
        )

    if selected_lines:
        end_line = selected_lines[-1][0]
    else:
        end_line = 0

    numbered_content = "".join(
        f"{line_number}: {line}"
        for line_number, line
        in selected_lines
    )

    return {
        "path": normalized,
        "start_line": start_line,
        "end_line": end_line,
        "total_lines": total_lines,
        "truncated": end_line < total_lines,
        "content": numbered_content,
    }


# ---------------------------------------------------------------------
# Manual CLI
# ---------------------------------------------------------------------


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only SEARCH and READ tools for "
            "Implementation Planner v0.0.1."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    search_parser = subparsers.add_parser(
        "search",
        help=(
            "Search Git-tracked repository "
            "paths and text."
        ),
    )

    search_parser.add_argument(
        "query",
        help="Fixed-string search query.",
    )

    search_parser.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_SEARCH_RESULTS,
    )

    read_parser = subparsers.add_parser(
        "read",
        help=(
            "Read a bounded range from a "
            "Git-tracked text file."
        ),
    )

    read_parser.add_argument(
        "path",
        help=(
            "Git-tracked repository-relative "
            "path."
        ),
    )

    read_parser.add_argument(
        "--start-line",
        type=int,
        default=1,
    )

    read_parser.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_READ_LINES,
    )

    return parser


def main() -> None:
    parser = _build_cli()
    args = parser.parse_args()

    try:

        if args.command == "search":
            output = search_repo(
                query=args.query,
                max_results=args.max_results,
            )

        elif args.command == "read":
            output = read_repo_file(
                relative_path=args.path,
                start_line=args.start_line,
                max_lines=args.max_lines,
            )

        else:
            raise RepoReadError(
                f"Unsupported command: "
                f"{args.command}"
            )

    except RepoReadError as exc:
        output = {
            "status": "ERROR",
            "error": str(exc),
        }

    print(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()


