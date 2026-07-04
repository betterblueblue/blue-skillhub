#!/usr/bin/env python3
"""Tests for the Claude Code impact write gate hook."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".claude" / "hooks" / "impact-write-gate.py"


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def user_message(text: str) -> dict[str, object]:
    return {"role": "user", "content": text}


class HookFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state = self.root / "state"
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "src").mkdir()
        self.transcript = self.root / "transcript.jsonl"

    def close(self) -> None:
        self.tmp.cleanup()

    def protect(self) -> None:
        (self.project / ".impact-protected").write_text("", encoding="utf-8")

    def run_hook(self, event: dict[str, object]) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IMPACT_WRITE_GATE_STATE_DIR"] = str(self.state)
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(event, ensure_ascii=False),
            capture_output=True,
            text=True,
            env=env,
            timeout=10,
        )

    def edit_event(self) -> dict[str, object]:
        return {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(self.project / "src" / "item.ts")},
            "cwd": str(self.project),
            "transcript_path": str(self.transcript),
            "session_id": "test-session",
        }

    def change_impact_event(self) -> dict[str, object]:
        return {
            "tool_name": "Write",
            "tool_input": {"file_path": str(self.project / "change-impact" / "req" / "000-context-pack.md")},
            "cwd": str(self.project),
            "transcript_path": str(self.transcript),
            "session_id": "test-session",
        }

    def bash_event(self, command: str) -> dict[str, object]:
        return {
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "cwd": str(self.project),
            "transcript_path": str(self.transcript),
            "session_id": "test-session",
        }

    def write_ready_impact_state(self, step: int = 3, failed: int = 0, mode: str = "light") -> None:
        req = self.project / "change-impact" / "req"
        req.mkdir(parents=True, exist_ok=True)
        (req / "000-context-pack.md").write_text("# Context\n", encoding="utf-8")
        if mode == "full":
            (req / "010-requirements.md").write_text("# Requirements\n", encoding="utf-8")
            (req / "020-design.md").write_text("# Design\n", encoding="utf-8")
            (req / "030-implementation.md").write_text("# Implementation\n", encoding="utf-8")
        else:
            (req / "040-light.md").write_text("# Light\n", encoding="utf-8")
        (req / "060-preflight.md").write_text("# Preflight\n", encoding="utf-8")
        (req / "_active-state.md").write_text(
            f"""# Active State

## 状态头

- 模式：{mode}
- Phase 3 状态：已完成
- Phase 3.5 定级：{mode}
- 是否需要确认：true
- 待执行 Step：Step {step}
- 上次提示 Step：Step {step}
- 上次确认 Step：none
- 上次完成 Step：none

## 最近验证

- 命令：`python impact_validate.py`
- 结果：17 passed, {failed} failed, 0 warnings
""",
            encoding="utf-8",
        )


class TestImpactWriteGate(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = HookFixture()

    def tearDown(self) -> None:
        self.fx.close()

    def test_unprotected_project_allows_write_tool(self) -> None:
        write_jsonl(self.fx.transcript, [user_message("随便改一下")])

        result = self.fx.run_hook(self.fx.edit_event())

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_protected_project_blocks_edit_without_step_confirmation(self) -> None:
        self.fx.protect()
        write_jsonl(self.fx.transcript, [user_message("真实 /impact：快速改一下")])

        result = self.fx.run_hook(self.fx.edit_event())

        self.assertEqual(result.returncode, 2)
        self.assertIn("blocked write under protected project", result.stderr)
        self.assertIn("确认 Step N", result.stderr)

    def test_protected_project_allows_one_write_per_step_confirmation(self) -> None:
        self.fx.protect()
        self.fx.write_ready_impact_state(step=3)
        write_jsonl(self.fx.transcript, [user_message("确认 Step 3")])
        event = self.fx.edit_event()

        first = self.fx.run_hook(event)
        second = self.fx.run_hook(event)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 2)
        self.assertIn("already been consumed", second.stderr)

    def test_protected_project_blocks_write_like_bash_without_confirmation(self) -> None:
        self.fx.protect()
        write_jsonl(self.fx.transcript, [user_message("快速改一下")])

        result = self.fx.run_hook(self.fx.bash_event("echo hi > src/item.ts"))

        self.assertEqual(result.returncode, 2)
        self.assertIn("blocked write under protected project", result.stderr)

    def test_read_only_bash_is_allowed_without_confirmation(self) -> None:
        self.fx.protect()
        write_jsonl(self.fx.transcript, [user_message("快速看一下")])

        result = self.fx.run_hook(self.fx.bash_event("git status --short"))

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_write_with_confirmation_requires_phase4_and_preflight(self) -> None:
        self.fx.protect()
        write_jsonl(self.fx.transcript, [user_message("确认 Step 3")])

        result = self.fx.run_hook(self.fx.edit_event())

        self.assertEqual(result.returncode, 2)
        self.assertIn("before impact Phase 4 + preflight are ready", result.stderr)

    def test_change_impact_doc_write_does_not_require_preflight(self) -> None:
        self.fx.protect()
        write_jsonl(self.fx.transcript, [user_message("确认 Step 1")])

        result = self.fx.run_hook(self.fx.change_impact_event())

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_write_allows_when_active_state_matches_confirmed_step(self) -> None:
        self.fx.protect()
        self.fx.write_ready_impact_state(step=4, mode="full")
        write_jsonl(self.fx.transcript, [user_message("确认 Step 4")])

        result = self.fx.run_hook(self.fx.edit_event())

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_write_blocks_when_latest_validation_has_failed(self) -> None:
        self.fx.protect()
        self.fx.write_ready_impact_state(step=4, failed=1)
        write_jsonl(self.fx.transcript, [user_message("确认 Step 4")])

        result = self.fx.run_hook(self.fx.edit_event())

        self.assertEqual(result.returncode, 2)
        self.assertIn("最近验证", result.stderr)

    def test_source_write_blocks_when_confirmed_step_does_not_match_active_state(self) -> None:
        self.fx.protect()
        self.fx.write_ready_impact_state(step=4)
        write_jsonl(self.fx.transcript, [user_message("确认 Step 5")])

        result = self.fx.run_hook(self.fx.edit_event())

        self.assertEqual(result.returncode, 2)
        self.assertIn("not waiting for Step 5", result.stderr)

    def test_write_like_bash_to_source_requires_ready_state(self) -> None:
        self.fx.protect()
        write_jsonl(self.fx.transcript, [user_message("确认 Step 3")])

        result = self.fx.run_hook(self.fx.bash_event("echo hi > src/item.ts"))

        self.assertEqual(result.returncode, 2)
        self.assertIn("before impact Phase 4 + preflight are ready", result.stderr)


if __name__ == "__main__":
    unittest.main()
