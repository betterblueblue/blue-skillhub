#!/usr/bin/env python3
"""V25 风险分级定向回归的行为测试(R2-IMP1)。

Run:
  python -m pytest skills/impact/tests/test_scripts/test_v25_regression.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "impact_validate.py"

BASELINE = "- 基线:项目已有测试全过(命令与结果:60 passed)"

RECORD_WITH_PERMISSION_STEP = (
    "## [2026-01-01] Step 1: 改权限角色\n\n"
    "- 确认类型:改代码\n"
    "- 操作内容:`edit 权限模块`\n"
)


def _make_req_dir() -> Path:
    td = Path(tempfile.mkdtemp())
    rd = td / "req"
    rd.mkdir()
    (rd / "020-design.md").write_text("# 020\n", encoding="utf-8")
    (rd / "030-implementation.md").write_text("# 030\n", encoding="utf-8")
    (rd / "000-context-pack.md").write_text("# 000\n", encoding="utf-8")
    (rd / "_active-state.md").write_text("# state\n", encoding="utf-8")
    return rd


def _run(req_dir: Path) -> list[str]:
    out = subprocess_run_validator(req_dir)
    return [l for l in out.splitlines() if "V25:" in l]


def subprocess_run_validator(req_dir: Path) -> str:
    import subprocess
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(req_dir), "--mode", "full"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.stdout or ""


class TestV25RiskTieredRegression(unittest.TestCase):
    def test_baseline_only_passes(self):
        # 普通业务改动:只有基线,无高风险维度 → PASS
        rd = _make_req_dir()
        (rd / "090-execution-record.md").write_text(
            "## 回归验证\n\n" + BASELINE + "\n- 结论:通过\n", encoding="utf-8"
        )
        lines = _run(rd)
        self.assertTrue(any("PASS" in l for l in lines), lines)

    def test_missing_section_with_write_steps_warns(self):
        # 有写类 Step 记录但缺回归验证节 → WARN 提示补记
        rd = _make_req_dir()
        (rd / "090-execution-record.md").write_text(
            "## [2026-01-01] Step 1: 改代码\n\n- 确认类型:改代码\n- 操作内容:`edit src/x.ts`\n",
            encoding="utf-8",
        )
        lines = _run(rd)
        self.assertTrue(any("缺「回归验证」节" in l for l in lines), lines)

    def test_permission_step_without_dimension_warns(self):
        # 改权限类 Step 但定向维度未记录 → WARN
        rd = _make_req_dir()
        (rd / "090-execution-record.md").write_text(
            RECORD_WITH_PERMISSION_STEP + "\n## 回归验证\n\n" + BASELINE + "\n- 结论:通过\n",
            encoding="utf-8",
        )
        lines = _run(rd)
        self.assertTrue(any("permission" in l and "未回归" in l for l in lines), lines)

    def test_dimension_recorded_passes(self):
        # 权限类 Step 且越权抽测已记录 → 无 WARN
        rd = _make_req_dir()
        (rd / "090-execution-record.md").write_text(
            RECORD_WITH_PERMISSION_STEP + "\n## 回归验证\n\n" + BASELINE
            + "\n- 权限/角色类:越权抽测 2 条,防御成功\n- 结论:通过\n",
            encoding="utf-8",
        )
        lines = _run(rd)
        self.assertFalse(any("未回归" in l for l in lines), lines)


def subprocess_run_validator_alias(req_dir):  # pragma: no cover
    pass


if __name__ == "__main__":
    unittest.main()
