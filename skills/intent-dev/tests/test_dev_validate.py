#!/usr/bin/env python3
"""Behavior tests for dev_validate.py.

Run:
  python -m pytest skills/intent-dev/tests/test_dev_validate.py -v
  python skills/intent-dev/tests/test_dev_validate.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from dev_validate import validate
finally:
    sys.path.pop(0)


def _dev_content() -> str:
    return (FIXTURE_DIR / "valid-dev-record.md").read_text(encoding="utf-8")


def _issues_content() -> str:
    return (FIXTURE_DIR / "valid-issues.md").read_text(encoding="utf-8")


def _result(dev: str, issues: str, check_id: str) -> tuple[str, str, str]:
    matches = [item for item in validate(dev, issues) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


class TestValidFixture(unittest.TestCase):
    def test_valid_dev_record_passes_all_checks(self):
        results = validate(_dev_content(), _issues_content())
        self.assertEqual(4, len(results))
        self.assertTrue(
            all(status == "PASS" for _check_id, status, _message in results),
            results,
        )


class TestNonEmpty(unittest.TestCase):
    def test_empty_file_fails(self):
        results = validate("", _issues_content())
        self.assertEqual("FAIL", results[0][1])


class TestIssueRecords(unittest.TestCase):
    def test_no_issue_records_fails(self):
        content = _dev_content().replace("## Issue 1:", "## X:")
        result = _result(content, _issues_content(), "V2")
        self.assertEqual("FAIL", result[1])

    def test_missing_scenario_block_fails(self):
        content = _dev_content().replace("**[P01]", "**X")
        result = _result(content, _issues_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("场景块", result[2])

    def test_missing_tdd_section_fails(self):
        content = _dev_content().replace("### TDD 过程", "### X")
        result = _result(content, _issues_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("TDD", result[2])

    def test_missing_red_section_fails(self):
        content = _dev_content().replace("#### Red", "#### X")
        result = _result(content, _issues_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Red", result[2])

    def test_missing_green_section_fails(self):
        content = _dev_content().replace("#### Green", "#### X")
        result = _result(content, _issues_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Green", result[2])

    def test_missing_status_fails(self):
        content = _dev_content().replace("- 状态：done", "- X：done")
        result = _result(content, _issues_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("状态", result[2])

    def test_fewer_records_than_issues_fails(self):
        content = _dev_content().replace("## Issue 1:", "## X:")
        result = _result(content, _issues_content(), "V2")
        self.assertEqual("FAIL", result[1])


class TestThenVerificationLevel(unittest.TestCase):
    def test_no_then_lines_fails(self):
        content = (
            _dev_content()
            .replace("- [x] Then:", "- X Then:")
            .replace("- [x] And:", "- X And:")
        )
        result = _result(content, _issues_content(), "V3")
        self.assertEqual("FAIL", result[1])

    def test_missing_level_fails(self):
        content = _dev_content().replace(
            "- [x] Then: 记录文件存在 — V2，命令 `npm test` 输出: 4 passed",
            "- [x] Then: 记录文件存在",
        )
        result = _result(content, _issues_content(), "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("验证等级", result[2])

    def test_v2_without_command_output_fails(self):
        content = _dev_content().replace(
            "- [x] Then: 记录文件存在 — V2，命令 `npm test` 输出: 4 passed",
            "- [x] Then: 记录文件存在 — V2",
        )
        result = _result(content, _issues_content(), "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("命令输出", result[2])

    def test_valid_levels_passes(self):
        result = _result(_dev_content(), _issues_content(), "V3")
        self.assertEqual("PASS", result[1])


class TestDoneRequiresV2(unittest.TestCase):
    def test_done_with_v1_only_fails(self):
        content = _dev_content().replace(
            "- [x] Then: 记录文件存在 — V2，命令 `npm test` 输出: 4 passed",
            "- [x] Then: 记录文件存在 — V1，代码审查: src/handoff.js L23",
        )
        result = _result(content, _issues_content(), "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("V1", result[2])

    def test_done_with_unchecked_then_fails(self):
        content = _dev_content().replace(
            "- [x] Then: 记录文件存在 — V2，命令 `npm test` 输出: 4 passed",
            "- [ ] Then: 记录文件存在 — V0",
        )
        result = _result(content, _issues_content(), "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未通过", result[2])

    def test_done_with_all_v2_passes(self):
        result = _result(_dev_content(), _issues_content(), "V4")
        self.assertEqual("PASS", result[1])


if __name__ == "__main__":
    unittest.main()
