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
SOURCE_ROOTS = {"app", "backend", "docs", "frontend", "prisma", "src", "test", "tests"}
SOURCE_FILE_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "tsconfig.json",
    "vite.config.ts",
    "next.config.js",
    "pyproject.toml",
    "requirements.txt",
    "pom.xml",
    "build.gradle",
}
SOURCE_SUFFIXES = {
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".json",
    ".kt",
    ".prisma",
    ".py",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}
SOURCE_BASH_TARGET_RE = re.compile(
    r"(^|[\\/\s'\"`])(?:app|backend|docs|frontend|prisma|src|test|tests)[\\/]"
    r"|(^|[\\/\s'\"`])(?:package\.json|package-lock\.json|pnpm-lock\.yaml|"
    r"yarn\.lock|tsconfig\.json|pyproject\.toml|requirements\.txt|pom\.xml)\b"
    r"|\bgit\s+(apply|checkout|reset|clean|restore|merge|rebase|pull)\b",
    re.IGNORECASE,
)

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


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def relative_parts(path: Path, root: Path) -> tuple[str, ...]:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).parts
    except ValueError:
        return ()


def is_change_impact_path(path: Path, root: Path) -> bool:
    parts = relative_parts(path, root)
    return bool(parts and parts[0] == "change-impact")


def is_source_like_path(path: Path, root: Path) -> bool:
    parts = relative_parts(path, root)
    if not parts or parts[0] == "change-impact":
        return False
    if parts[0] in SOURCE_ROOTS:
        return True
    name = path.name
    return name in SOURCE_FILE_NAMES or path.suffix.lower() in SOURCE_SUFFIXES


def bash_needs_phase_gate(command: str) -> bool:
    if "change-impact" in command and not SOURCE_BASH_TARGET_RE.search(command):
        return False
    return bool(SOURCE_BASH_TARGET_RE.search(command))


def needs_phase_gate(event: dict[str, Any], path: Path, root: Path) -> bool:
    tool = str(event.get("tool_name") or event.get("toolName") or "")
    tool_input = event.get("tool_input") or event.get("toolInput") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    if tool == "Bash":
        return bash_needs_phase_gate(str(tool_input.get("command") or ""))

    return is_source_like_path(path, root)


def protected_root(path: Path) -> Path | None:
    start = path if path.exists() and path.is_dir() else path.parent
    current = start.resolve(strict=False)
    while True:
        if (current / MARKER).exists():
            return current
        if current.parent == current:
            return None
        current = current.parent


def active_field(text: str, label: str) -> str | None:
    match = re.search(rf"(?m)^\s*-\s*{re.escape(label)}\s*[:：]\s*(.+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip("`")


def normalize_step(value: str | None) -> str | None:
    if value is None:
        return None
    match = re.search(r"\bStep\s*([0-9]+)\b", value, re.IGNORECASE)
    if match:
        return match.group(1)
    cleaned = value.strip().strip("[]` ").lower()
    if cleaned in {"none", "无", "无需", "不适用"}:
        return "none"
    return None


def latest_validation_is_green(text: str) -> bool:
    section_match = re.search(r"(?ms)^##\s+最近验证\s*(.*?)(?:^##\s+|\Z)", text)
    if not section_match:
        return False
    section = section_match.group(1)
    result_match = re.search(
        r"(?m)^\s*[-*]?\s*结果\s*[:：]\s*\d+\s*passed.*?([0-9]+)\s*failed?",
        section,
        re.IGNORECASE,
    )
    return bool(result_match and int(result_match.group(1)) == 0)


def mode_docs_exist(req_dir: Path, state_text: str) -> bool:
    mode = (active_field(state_text, "模式") or "").lower()
    grading = (active_field(state_text, "Phase 3.5 定级") or "").lower()
    is_full = "full" in mode or "full" in grading
    is_light = "light" in mode or "light" in grading or "快速通道" in grading

    if is_full:
        required = ["000-context-pack.md", "010-requirements.md", "020-design.md", "030-implementation.md"]
    elif is_light:
        required = ["000-context-pack.md", "040-light.md"]
    else:
        return False
    return all((req_dir / name).exists() for name in required)


def phase_ready_for_source_write(root: Path, step: str) -> tuple[bool, str]:
    change_impact = root / "change-impact"
    if not change_impact.exists():
        return False, "change-impact directory is missing"

    candidates = sorted(change_impact.glob("*/_active-state.md"))
    if not candidates:
        return False, "no change-impact/*/_active-state.md found"

    reasons: list[str] = []
    for state_path in candidates:
        req_dir = state_path.parent
        try:
            state_text = state_path.read_text(encoding="utf-8")
        except OSError as exc:
            reasons.append(f"{req_dir.name}: cannot read _active-state.md: {exc}")
            continue

        pending = normalize_step(active_field(state_text, "待执行 Step"))
        prompted = normalize_step(active_field(state_text, "上次提示 Step"))
        if step not in {pending, prompted}:
            reasons.append(f"{req_dir.name}: active-state is not waiting for Step {step}")
            continue
        if not (req_dir / "060-preflight.md").exists():
            reasons.append(f"{req_dir.name}: 060-preflight.md missing")
            continue
        if not mode_docs_exist(req_dir, state_text):
            reasons.append(f"{req_dir.name}: Phase 4 documents incomplete for declared mode")
            continue
        if not latest_validation_is_green(state_text):
            reasons.append(f"{req_dir.name}: 最近验证 is missing or not 0 failed")
            continue
        return True, f"{req_dir.name}: Phase 4 and preflight ready"

    return False, "; ".join(reasons[:3]) or "no ready impact active-state found"


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
    protected_targets: list[tuple[Path, Path]] = []
    for target in targets:
        root = protected_root(target)
        if root:
            protected_targets.append((target, root))
            if root not in roots:
                roots.append(root)

    if not roots:
        return 0

    transcript = event.get("transcript_path") or event.get("transcriptPath")
    confirmation = latest_user_confirmation(str(transcript) if transcript else None)
    if confirmation is None:
        protected_list = ", ".join(str(root) for root in roots)
        return block(f"blocked write under protected project: {protected_list}")

    gated_roots: list[Path] = []
    for target, root in protected_targets:
        if root in gated_roots or not needs_phase_gate(event, target, root):
            continue
        ready, reason = phase_ready_for_source_write(root, str(confirmation["step"]))
        if not ready:
            return block(
                "blocked source/test/config write before impact Phase 4 + preflight are ready: "
                f"{root} ({reason})"
            )
        gated_roots.append(root)

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
