#!/usr/bin/env python3
"""Behavior tests for prd_validate.py.

Run:
  python -m pytest skills/intent-prd/tests/test_prd_validate.py -v
  python skills/intent-prd/tests/test_prd_validate.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
INTENT_FIXTURE = SKILL_DIR.parent / "intent-anchor" / "tests" / "fixtures" / "valid-intent.md"

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from prd_validate import validate
finally:
    sys.path.pop(0)


def _prd_content() -> str:
    return (FIXTURE_DIR / "valid-prd.md").read_text(encoding="utf-8")


def _intent_content() -> str:
    return INTENT_FIXTURE.read_text(encoding="utf-8")


def _result(prd: str, intent: str, check_id: str) -> tuple[str, str, str]:
    matches = [item for item in validate(prd, intent) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


class TestValidFixture(unittest.TestCase):
    def test_valid_prd_passes_all_checks(self):
        results = validate(_prd_content(), _intent_content())
        self.assertEqual(8, len(results))
        self.assertTrue(
            all(status == "PASS" for _check_id, status, _message in results),
            results,
        )


class TestRequiredSections(unittest.TestCase):
    def test_missing_acceptance_criteria_fails(self):
        content = _prd_content().replace("## Acceptance Criteria", "## X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Acceptance Criteria", result[2])

    def test_missing_intent_verification_fails(self):
        content = _prd_content().replace("## Intent Verification", "## X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Intent Verification", result[2])

    def test_empty_prd_fails(self):
        results = validate("", _intent_content())
        self.assertEqual("FAIL", results[0][1])


class TestCapabilityCoverage(unittest.TestCase):
    def test_missing_capability_in_stories_fails(self):
        content = _prd_content().replace("[C01]", "")
        result = _result(content, _intent_content(), "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("C01", result[2])

    def test_all_capabilities_present_passes(self):
        result = _result(_prd_content(), _intent_content(), "V3")
        self.assertEqual("PASS", result[1])


class TestAcceptancePathCoverage(unittest.TestCase):
    def test_missing_path_in_criteria_fails(self):
        content = _prd_content().replace("P01", "")
        result = _result(content, _intent_content(), "V4")
        self.assertEqual("FAIL", result[1])

    def test_all_paths_present_passes(self):
        result = _result(_prd_content(), _intent_content(), "V4")
        self.assertEqual("PASS", result[1])


class TestDesignStandards(unittest.TestCase):
    def test_no_design_standards_passes(self):
        result = _result(_prd_content(), _intent_content(), "V5")
        self.assertEqual("PASS", result[1])

    def test_design_standards_not_referenced_fails(self):
        intent = _intent_content()
        intent = intent.replace(
            "无设计标准素材。用户明确确认：\u201c没有设计素材，不作为验收基线\u201d。",
            "| 设计素材 ID | 类型 | 路径 | 验收范围 | 用户确认 |\n"
            "|---|---|---|---|---|\n"
            "| D01 | 可点原型 | prototype/admin | 管理端 | 确认 |",
        )
        result = _result(_prd_content(), intent, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("设计素材", result[2])


class TestTerminology(unittest.TestCase):
    def test_no_terminology_passes(self):
        result = _result(_prd_content(), _intent_content(), "V6")
        self.assertEqual("PASS", result[1])

    def test_terminology_not_referenced_fails(self):
        intent = _intent_content()
        intent = intent.replace(
            "无术语需要翻译。",
            "| 原始术语 | 人话翻译 | 用于界面的文案 | 出现在能力 ID |\n"
            "|---|---|---|---|\n"
            "| 交接棒 | 会话交接 | 会话交接 | C01 |",
        )
        result = _result(_prd_content(), intent, "V6")
        self.assertEqual("FAIL", result[1])


class TestIntentVerification(unittest.TestCase):
    def test_missing_coverage_subsection_fails(self):
        content = _prd_content().replace("### 保留能力覆盖", "### X")
        result = _result(content, _intent_content(), "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("保留能力覆盖", result[2])

    def test_missing_non_negotiable_subsection_fails(self):
        content = _prd_content().replace("### 不可妥协项核对", "### X")
        result = _result(content, _intent_content(), "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不可妥协项核对", result[2])

    def test_missing_new_capability_subsection_fails(self):
        content = _prd_content().replace("### 新增能力", "### X")
        result = _result(content, _intent_content(), "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("新增能力", result[2])

    def test_valid_verification_passes(self):
        result = _result(_prd_content(), _intent_content(), "V7")
        self.assertEqual("PASS", result[1])


class TestGivenWhenThen(unittest.TestCase):
    def test_valid_gwt_passes(self):
        result = _result(_prd_content(), _intent_content(), "V8")
        self.assertEqual("PASS", result[1])

    def test_missing_given_fails(self):
        content = _prd_content().replace("**Given**", "**前提**")
        result = _result(content, _intent_content(), "V8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Given", result[2])

    def test_missing_when_fails(self):
        content = _prd_content().replace("**When**", "**操作**")
        result = _result(content, _intent_content(), "V8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("When", result[2])

    def test_missing_then_fails(self):
        content = _prd_content().replace("**Then**", "**结果**")
        result = _result(content, _intent_content(), "V8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Then", result[2])

    def test_missing_scenario_block_fails(self):
        content = _prd_content().replace("### P01:", "### X:")
        result = _result(content, _intent_content(), "V8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("场景块", result[2])


if __name__ == "__main__":
    unittest.main()
