#!/usr/bin/env python3
"""Behavior tests for verify_validate.py.

Run:
  python -m pytest skills/intent-verify/tests/test_verify_validate.py -v
  python skills/intent-verify/tests/test_verify_validate.py
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
    from verify_validate import validate
finally:
    sys.path.pop(0)


def _content() -> str:
    return (FIXTURE_DIR / "valid-verify-record.md").read_text(encoding="utf-8")


def _intent() -> str:
    return (FIXTURE_DIR / "valid-intent.md").read_text(encoding="utf-8")


def _result(content: str, check_id: str) -> tuple[str, str, str]:
    matches = [item for item in validate(content, _intent()) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


class TestValidFixture(unittest.TestCase):
    def test_valid_verify_record_passes_all_checks(self):
        results = validate(_content(), _intent())
        self.assertEqual(7, len(results))
        self.assertTrue(
            all(status == "PASS" for _check_id, status, _message in results),
            results,
        )


class TestNonEmpty(unittest.TestCase):
    def test_empty_file_fails(self):
        results = validate("", _intent())
        self.assertEqual("FAIL", results[0][1])


class TestRegressionSection(unittest.TestCase):
    def test_missing_regression_section_fails(self):
        content = _content().replace("## 回归验证结果", "## X")
        result = _result(content, "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("回归验证", result[2])

    def test_missing_test_command_fails(self):
        content = _content().replace("全量测试命令", "X")
        result = _result(content, "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("全量测试命令", result[2])

    def test_regression_result_not_passing_fails(self):
        content = _content().replace("- 结果：通过", "- 结果：未通过")
        result = _result(content, "V2")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未通过", result[2])

    def test_valid_regression_passes(self):
        result = _result(_content(), "V2")
        self.assertEqual("PASS", result[1])


class TestPathRecords(unittest.TestCase):
    def test_no_path_records_fails(self):
        content = _content().replace("### 路径 P01:", "### X:")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])

    def test_missing_given_fails(self):
        content = _content().replace("- Given:", "- X:")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Given", result[2])

    def test_missing_when_fails(self):
        content = _content().replace("- When:", "- X:")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("When", result[2])

    def test_missing_then_fails(self):
        content = (
            _content()
            .replace("- [x] Then:", "- X Then:")
            .replace("- [x] And:", "- X And:")
        )
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Then", result[2])

    def test_missing_verify_method_fails(self):
        content = _content().replace("- 验证方式：", "- X：")
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("验证方式", result[2])

    def test_valid_paths_pass(self):
        result = _result(_content(), "V3")
        self.assertEqual("PASS", result[1])


class TestV3Evidence(unittest.TestCase):
    def test_unchecked_then_fails(self):
        content = _content().replace(
            "- [x] Then: 记录文件存在",
            "- [ ] Then: 记录文件存在",
        )
        result = _result(content, "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("未勾选", result[2])

    def test_then_not_v3_fails(self):
        content = _content().replace(
            "- [x] Then: 记录文件存在 — V3，",
            "- [x] Then: 记录文件存在 — V2，",
        )
        result = _result(content, "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("V3", result[2])

    def test_all_unchecked_thens_fails(self):
        content = _content().replace("- [x] Then:", "- [ ] Then:").replace(
            "- [x] And:", "- [ ] And:"
        )
        result = _result(content, "V4")
        self.assertEqual("FAIL", result[1])

    def test_valid_v3_passes(self):
        result = _result(_content(), "V4")
        self.assertEqual("PASS", result[1])


class TestConditionalSection(unittest.TestCase):
    def test_missing_conditional_section_fails(self):
        content = _content().replace("## 条件性验证结果", "## X")
        result = _result(content, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("条件性验证", result[2])

    def test_missing_perf_section_fails(self):
        content = _content().replace("### 性能验证", "### X")
        result = _result(content, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("性能验证", result[2])

    def test_missing_security_section_fails(self):
        content = _content().replace("### 安全验证", "### X")
        result = _result(content, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("安全验证", result[2])

    def test_valid_conditional_passes(self):
        result = _result(_content(), "V5")
        self.assertEqual("PASS", result[1])


class TestFinalReview(unittest.TestCase):
    def test_missing_gate_fails(self):
        content = _content().replace("## 最终复核", "## X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("最终复核", result[2])

    def test_missing_regression_summary_fails(self):
        content = _content().replace("### 回归验证结果汇总", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("回归验证结果汇总", result[2])

    def test_missing_capability_table_fails(self):
        content = _content().replace("### 保留能力逐项核对", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("保留能力", result[2])

    def test_missing_path_table_fails(self):
        content = _content().replace("### 验收路径逐条验证", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("验收路径", result[2])

    def test_path_table_then_not_passing_fails(self):
        content = _content().replace(
            "| P01 | 生成并查看交接记录 | V3 | 手动走通 | 是 | 是 | 是 |",
            "| P01 | 生成并查看交接记录 | V3 | 手动走通 | 是 | 是 | 否 |",
        )
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("Then 全通过", result[2])

    def test_path_table_without_v3_fails(self):
        content = _content().replace(
            "| P01 | 生成并查看交接记录 | V3 |",
            "| P01 | 生成并查看交接记录 | V2 |",
        )
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("V3", result[2])

    def test_missing_conditional_summary_fails(self):
        content = _content().replace("### 条件性验证结果汇总", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("条件性验证结果汇总", result[2])

    def test_missing_drift_table_fails(self):
        content = _content().replace("### 漂移复核", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("漂移复核", result[2])

    def test_missing_conclusion_fails(self):
        content = _content().replace("### 结论", "### X")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("结论", result[2])

    def test_conclusion_without_verdict_fails(self):
        content = _content().replace("- 结果：通过", "- 结果：待定")
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("判定", result[2])

    def test_valid_gate_passes(self):
        result = _result(_content(), "V6")
        self.assertEqual("PASS", result[1])


class TestCrossValidation(unittest.TestCase):
    def test_valid_cross_validation_passes(self):
        result = _result(_content(), "V7")
        self.assertEqual("PASS", result[1])

    def test_missing_path_in_verify_fails(self):
        """verify-record 缺少 INTENT.md 中的路径时 V7 失败。"""
        content = _content().replace("### 路径 P01:", "### 路径 P99:")
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("缺少", result[2])

    def test_extra_path_in_verify_fails(self):
        """verify-record 有 INTENT.md 中不存在的路径时 V7 失败。"""
        # 在 E2E 段末尾插入一条多余路径
        content = _content().replace(
            "## 条件性验证结果",
            "### 路径 P99: 不存在的路径\n\n- Given: test — 就绪\n- When: test — 已执行\n- [x] Then: test — V3，test\n- 验证方式：手动走通\n\n---\n\n## 条件性验证结果",
        )
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])

    def test_missing_capability_in_verify_fails(self):
        """保留能力核对表缺少 INTENT.md 中的能力时 V7 失败。"""
        content = _content().replace("| C01 |", "| C99 |")
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])

    def test_security_marked_not_applicable_when_intent_has_requirement_fails(self):
        """INTENT.md 有安全要求但验收记录标注不适用时 V7 失败。"""
        content = _content().replace(
            "- INTENT.md/PRD 中是否有安全要求：是",
            "- INTENT.md/PRD 中是否有安全要求：否",
        ).replace(
            "- 结果：通过\n\n---\n\n## 最终复核",
            "- 结果：不适用\n\n---\n\n## 最终复核",
        )
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("安全", result[2])


if __name__ == "__main__":
    unittest.main()
