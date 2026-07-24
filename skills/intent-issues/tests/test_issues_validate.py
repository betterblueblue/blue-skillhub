#!/usr/bin/env python3
"""Behavior tests for issues_validate.py.

Run:
  python -m pytest skills/intent-issues/tests/test_issues_validate.py -v
  python skills/intent-issues/tests/test_issues_validate.py
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
    from issues_validate import validate
finally:
    sys.path.pop(0)


def _issues_content() -> str:
    return (FIXTURE_DIR / "valid-issues.md").read_text(encoding="utf-8")


def _intent_content() -> str:
    return INTENT_FIXTURE.read_text(encoding="utf-8")


def _result(issues: str, intent: str, check_id: str) -> tuple[str, str, str]:
    matches = [item for item in validate(issues, intent) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


class TestValidFixture(unittest.TestCase):
    def test_valid_issues_passes_all_checks(self):
        results = validate(_issues_content(), _intent_content())
        self.assertEqual(5, len(results))
        self.assertTrue(
            all(status == "PASS" for _check_id, status, _message in results),
            results,
        )


class TestRequiredSubsections(unittest.TestCase):
    def test_missing_what_to_build_fails(self):
        content = _issues_content().replace("### What to build", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("What to build", result[2])

    def test_missing_acceptance_criteria_fails(self):
        content = _issues_content().replace("### Acceptance criteria", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Acceptance criteria", result[2])

    def test_missing_blocked_by_fails(self):
        content = _issues_content().replace("### Blocked by", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Blocked by", result[2])

    def test_missing_user_stories_fails(self):
        content = _issues_content().replace("### User stories covered", "### X")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("User stories covered", result[2])

    def test_no_issues_fails(self):
        content = _issues_content().replace("## Issue 1:", "## X:")
        result = _result(content, _intent_content(), "V2")
        self.assertEqual("FAIL", result[1])

    def test_empty_file_fails(self):
        results = validate("", _intent_content())
        self.assertEqual("FAIL", results[0][1])


class TestPathCoverage(unittest.TestCase):
    def test_missing_path_in_criteria_fails(self):
        content = _issues_content().replace("[P01]", "")
        result = _result(content, _intent_content(), "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("P01", result[2])

    def test_all_paths_covered_passes(self):
        result = _result(_issues_content(), _intent_content(), "V3")
        self.assertEqual("PASS", result[1])


class TestCapabilityCoverage(unittest.TestCase):
    def test_missing_capability_in_stories_fails(self):
        content = _issues_content().replace("[C01]", "")
        result = _result(content, _intent_content(), "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("C01", result[2])

    def test_all_capabilities_covered_passes(self):
        result = _result(_issues_content(), _intent_content(), "V4")
        self.assertEqual("PASS", result[1])


class TestCoverageVerification(unittest.TestCase):
    def test_missing_coverage_section_fails(self):
        content = _issues_content().replace("## Coverage Verification", "## X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Coverage Verification", result[2])

    def test_missing_path_coverage_subsection_fails(self):
        content = _issues_content().replace("### 验收路径覆盖", "### X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("验收路径覆盖", result[2])

    def test_missing_capability_coverage_subsection_fails(self):
        content = _issues_content().replace("### 保留能力覆盖", "### X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("保留能力覆盖", result[2])

    def test_missing_new_capability_subsection_fails(self):
        content = _issues_content().replace("### 新增能力", "### X")
        result = _result(content, _intent_content(), "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("新增能力", result[2])

    def test_valid_coverage_passes(self):
        result = _result(_issues_content(), _intent_content(), "V5")
        self.assertEqual("PASS", result[1])


if __name__ == "__main__":
    unittest.main()
