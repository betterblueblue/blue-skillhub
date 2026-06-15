#!/usr/bin/env python3
"""Claude Code PreToolUse hook for impact / impact-pro write gates.

The hook is opt-in. It only protects projects that contain a `.impact-protected`
marker in their root. For protected projects, write tools are allowed only when
the latest real user message in the current transcript starts with
`确认 Step N`; that confirmation is consumed once per protected root.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


BLOCK_EXIT = 2
MARKER = ".impact-protected"
STATE_ENV = "IMPACT_WRITE_GATE_STATE_DIR"
DISABLE_ENV = "IMPACT_WRITE_GATE_DISABLE"

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
CONFIRM_RE = re.compile(r"^\s*确认\s+Step\s+([0-9]+)\b", re.IGNORECASE)
MULTI_STEP_RE = re.compile(r"(全部|所有|all\b|Step\s+[0-9]+.*Step\s+[0-9]+)", re.IGNORECASE)

WRITE_LIKE_BASH = re.compile(
    r"""
    (^|[;&|]\s*)(rm|mv|cp|mkdir|touch|chmod|chown|ln)\b
    |(^|[;&|]\s*)git\s+(apply|checkout|reset|clean|restore|merge|rebase|pull)\b
    |(^|[;&|]\s*)(npm|pnpm|yarn)\s+(install|i|add|remove|update|upgrade)\b
    |\b(sed|perl)\b[^\n]*\s-i\b
    |\b(Set-Content|Add-Content|Out-File|New-Item|Remove-Item|Move-Item|Copy-Item)\b
    |\btee\b
    |(?<![0-9])>>?(?!&)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def block(message: str) -> int:
    sys.stderr.write(f"[impact-write-gate] {message}\n")
    sys.stderr.write(
        "需要当前对话里的用户显式回复 `确认 Step N`；"
        "每条确认只放行一次受保护根内的写工具调用。\n"
    )
    return BLOCK_EXIT


def read_stdin_text() -> str:
    data = sys.stdin.buffer.read()
    if not data.strip(b"\x00 \t\r\n"):
        return ""

    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return data.decode(encoding).lstrip("\ufeff")
        except UnicodeDecodeError:
            continue

    return data.decode(errors="replace").lstrip("\ufeff")


def read_event() -> dict[str, Any]:
    raw = read_stdin_text()
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"hook input is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("hook input JSON must be an object")
    return parsed


def resolve_path(value: str, cwd: Path) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(value))
    path = Path(expanded)
    if not path.is_absolute():
        path = cwd / path
    return path.resolve(strict=False)


def is_write_like_bash(command: str) -> bool:
    return bool(WRITE_LIKE_BASH.search(command))


def target_paths(event: dict[str, Any]) -> list[Path]:
    tool = str(event.get("tool_name") or event.get("toolName") or "")
    tool_input = event.get("tool_input") or event.get("toolInput") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    cwd = resolve_path(str(event.get("cwd") or os.getcwd()), Path(os.getcwd()))

    if tool in WRITE_TOOLS:
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        file_path = tool_input.get(key)
        return [resolve_path(str(file_path), cwd)] if file_path else []

    if tool == "Bash":
        command = str(tool_input.get("command") or "")
        if not is_write_like_bash(command):
            return []
        return [cwd]

    return []


def protected_root(path: Path) -> Path | None:
    start = path if path.exists() and path.is_dir() else path.parent
    current = start.resolve(strict=False)
    while True:
        if (current / MARKER).exists():
            return current
        if current.parent == current:
            return None
        current = current.parent


def content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                item_type = item.get("type")
                if item_type == "text" and isinstance(item.get("text"), str):
                    parts.append(item["text"])
        return "\n".join(part for part in parts if part)
    return ""


def user_text_from_line(obj: dict[str, Any]) -> str | None:
    message = obj.get("message")
    if isinstance(message, dict):
        role = message.get("role") or obj.get("role") or obj.get("type")
        if role != "user":
            return None
        return content_to_text(message.get("content"))

    role = obj.get("role") or obj.get("type")
    if role != "user":
        return None
    return content_to_text(obj.get("content") or obj.get("text"))


def latest_user_confirmation(transcript_path: str | None) -> dict[str, Any] | None:
    if not transcript_path:
        return None

    path = Path(os.path.expanduser(os.path.expandvars(transcript_path)))
    if not path.exists():
        return None

    latest: tuple[int, str] | None = None
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            text = user_text_from_line(obj)
            if text and text.strip():
                latest = (line_no, text.strip())

    if latest is None:
        return None

    line_no, text = latest
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    match = CONFIRM_RE.match(first_line)
    if not match or MULTI_STEP_RE.search(first_line):
        return None

    return {
        "line": line_no,
        "text": first_line,
        "step": match.group(1),
        "transcript": str(path.resolve(strict=False)),
    }


def state_file() -> Path:
    base = os.environ.get(STATE_ENV)
    if base:
        root = Path(os.path.expanduser(os.path.expandvars(base)))
    else:
        home = Path.home()
        root = home / ".claude" / "impact-write-gate"
        if not str(home) or str(home) == ".":
            root = Path(tempfile.gettempdir()) / "impact-write-gate"
    root.mkdir(parents=True, exist_ok=True)
    return root / "used-confirmations.json"


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"used": {}}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {"used": {}}
    except (OSError, json.JSONDecodeError):
        return {"used": {}}


def save_state(path: Path, data: dict[str, Any]) -> None:
    temp = path.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temp.replace(path)


def confirmation_key(event: dict[str, Any], root: Path, confirmation: dict[str, Any]) -> str:
    session = str(event.get("session_id") or event.get("sessionId") or "unknown-session")
    payload = json.dumps(
        {
            "session": session,
            "root": str(root.resolve(strict=False)),
            "transcript": confirmation["transcript"],
            "line": confirmation["line"],
            "text": confirmation["text"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    if os.environ.get(DISABLE_ENV) == "1":
        return 0

    try:
        event = read_event()
    except ValueError as exc:
        return block(str(exc))

    targets = target_paths(event)
    if not targets:
        return 0

    roots = []
    for target in targets:
        root = protected_root(target)
        if root and root not in roots:
            roots.append(root)

    if not roots:
        return 0

    transcript = event.get("transcript_path") or event.get("transcriptPath")
    confirmation = latest_user_confirmation(str(transcript) if transcript else None)
    if confirmation is None:
        protected_list = ", ".join(str(root) for root in roots)
        return block(f"blocked write under protected project: {protected_list}")

    try:
        path = state_file()
        state = load_state(path)
        used = state.setdefault("used", {})
        keys = [confirmation_key(event, root, confirmation) for root in roots]
        if any(key in used for key in keys):
            return block(f"`确认 Step {confirmation['step']}` has already been consumed")

        for root, key in zip(roots, keys):
            used[key] = {
                "root": str(root),
                "step": confirmation["step"],
                "line": confirmation["line"],
                "text": confirmation["text"],
            }
        save_state(path, state)
    except OSError as exc:
        return block(f"cannot persist one-time confirmation state: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
