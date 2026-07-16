#!/usr/bin/env python3
"""Behavior tests for intent_validate.py.

Run:
  python -m pytest skills/intent-anchor/tests/test_intent_validate.py -v
  python skills/intent-anchor/tests/test_intent_validate.py
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "valid-intent.md"

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from intent_validate import _path_error, validate
finally:
    sys.path.pop(0)


def _valid_content() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def _result(content: str, check_id: str) -> tuple[str, str, str]:
    matches = [item for item in validate(content) if item[0] == check_id]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {check_id} result, got {matches}")
    return matches[0]


def _replace_section(content: str, heading: str, body: str) -> str:
    pattern = rf"^{re.escape(heading)}\s*$\n?.*?(?=^##\s+\d+\.\s|\Z)"
    replacement = f"{heading}\n\n{body.rstrip()}\n\n"
    updated, count = re.subn(
        pattern,
        lambda _match: replacement,
        content,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    if count != 1:
        raise AssertionError(f"Could not replace section {heading}")
    return updated


def _replace_subsection(content: str, heading: str, body: str) -> str:
    pattern = rf"^###\s+{re.escape(heading)}\s*$\n?.*?(?=^###\s+|^##\s+|\Z)"
    replacement = f"### {heading}\n\n{body.rstrip()}\n\n"
    updated, count = re.subn(
        pattern,
        lambda _match: replacement,
        content,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    if count != 1:
        raise AssertionError(f"Could not replace subsection {heading}")
    return updated


class TestValidFixture(unittest.TestCase):
    def test_current_fixture_passes_all_checks(self):
        results = validate(_valid_content())
        self.assertEqual(9, len(results))
        self.assertTrue(
            all(status == "PASS" for _check_id, status, _message in results),
            results,
        )

    def test_valid_fixture_has_no_percentage_gate(self):
        content = _valid_content()
        self.assertNotIn("%", content)
        self.assertEqual("PASS", _result(content, "V6")[1])


class TestDecisionContract(unittest.TestCase):
    def test_pending_capability_blocks_handoff(self):
        content = _valid_content().replace(
            "| C01 | 生成交接记录 | 会话结束前整理任务、进度、阻塞和下一步 | E01、E02 | 保留 | 用户明确确认 |",
            "| C01 | 生成交接记录 | 会话结束前整理任务、进度、阻塞和下一步 | E01、E02 | 待确认 | 模型建议（未确认） |",
        )
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("仍待确认", result[2])

    def test_delegated_model_cannot_abandon_capability(self):
        content = _valid_content().replace(
            "| C03 | 自动发送通知 | 交接完成后向外部聊天工具发消息 | E01 | 放弃 | 用户明确确认 |",
            "| C03 | 自动发送通知 | 交接完成后向外部聊天工具发消息 | E01 | 放弃 | 用户授权模型决定 |",
        )
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("只能保留或推迟", result[2])

    def test_unconfirmed_suggestion_cannot_be_recorded_as_deferred(self):
        content = _valid_content().replace(
            "| C02 | 自动归档旧记录 | 定期移动已经完成的历史交接文件 | E02 | 推迟 | 用户授权模型决定 |",
            "| C02 | 自动归档旧记录 | 定期移动已经完成的历史交接文件 | E02 | 推迟 | 模型建议（未确认） |",
        )
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("尚未确认", result[2])

    def test_explicit_user_choice_can_be_recorded_as_deferred(self):
        content = _valid_content().replace(
            "| C02 | 自动归档旧记录 | 定期移动已经完成的历史交接文件 | E02 | 推迟 | 用户授权模型决定 |",
            "| C02 | 自动归档旧记录 | 定期移动已经完成的历史交接文件 | E02 | 推迟 | 用户明确确认 |",
        )
        self.assertEqual("PASS", _result(content, "V3")[1])

    def test_unknown_evidence_id_fails(self):
        content = _valid_content().replace("| E01、E02 | 保留 |", "| E99 | 保留 |", 1)
        result = _result(content, "V3")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不存在的证据", result[2])


class TestNonNegotiableItems(unittest.TestCase):
    def test_zero_non_negotiable_items_is_valid_when_user_confirmed(self):
        content = _replace_section(
            _valid_content(),
            "## 5. 不可妥协项",
            "无不可妥协项。用户明确确认：“没有必须绝对保留的能力”。",
        )
        content = _replace_subsection(
            content,
            "S3 不可妥协项",
            "无不可妥协项。用户明确确认：“没有必须绝对保留的能力”。",
        )
        self.assertEqual("PASS", _result(content, "V4")[1])
        self.assertEqual("PASS", _result(content, "V9")[1])

    def test_non_negotiable_item_must_reference_retained_capability(self):
        content = _valid_content().replace(
            "| C01 | 没有交接记录就无法解决跨会话丢失问题 |",
            "| C02 | 没有交接记录就无法解决跨会话丢失问题 |",
            1,
        )
        result = _result(content, "V4")
        self.assertEqual("FAIL", result[1])
        self.assertIn("不是保留能力", result[2])


class TestScopeAndStatistics(unittest.TestCase):
    def test_missing_deferred_row_fails(self):
        content = _valid_content().replace(
            "| C02 | 自动归档旧记录 | 第一版先验证交接内容是否有用 | 历史文件开始影响查找时 |\n",
            "",
            1,
        )
        result = _result(content, "V5")
        self.assertEqual("FAIL", result[1])
        self.assertIn("推迟项 ID 不一致", result[2])

    def test_wrong_decision_counts_fail(self):
        content = _valid_content().replace("| 保留 | 1 |", "| 保留 | 2 |", 1)
        result = _result(content, "V6")
        self.assertEqual("FAIL", result[1])
        self.assertIn("决策统计不一致", result[2])


class TestDriftAndConfirmation(unittest.TestCase):
    def test_drift_status_cannot_use_ambiguous_icon(self):
        content = _valid_content().replace(
            "| D1 未确认新增 | 未命中 | 三项能力都能追溯到 E01 或 E02 |",
            "| D1 未确认新增 | ✅ | 三项能力都能追溯到 E01 或 E02 |",
            1,
        )
        result = _result(content, "V7")
        self.assertEqual("FAIL", result[1])
        self.assertIn("状态非法", result[2])

    def test_partial_confirmation_is_not_full_document_confirmation(self):
        content = _valid_content().replace(
            "| 2026-07-11 | INTENT.md 全文 | 用户明确确认 |",
            "| 2026-07-11 | 能力清单 | 用户明确确认 |",
            1,
        )
        result = _result(content, "V8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("全文", result[2])

    def test_continue_only_is_not_confirmation(self):
        content = _valid_content().replace(
            "“确认这份 INTENT.md。”",
            "“继续”",
            1,
        )
        result = _result(content, "V8")
        self.assertEqual("FAIL", result[1])
        self.assertIn("全文", result[2])

    def test_accept_is_full_document_confirmation(self):
        content = _valid_content().replace(
            "“确认这份 INTENT.md。”",
            "“接受”",
            1,
        )
        self.assertEqual("PASS", _result(content, "V8")[1])


class TestSemanticReviewEvidence(unittest.TestCase):
    def test_one_line_self_checks_do_not_pass(self):
        content = _replace_section(
            _valid_content(),
            "## 10. 语义复核记录",
            """### S1 证据覆盖
已检查

### S2 决策来源
已检查

### S3 不可妥协项
已检查

### S4 锚定充分性与冲突
已检查

### S5 漂移复核
已检查""",
        )
        result = _result(content, "V9")
        self.assertEqual("FAIL", result[1])
        self.assertIn("S1", result[2])

    def test_s2_must_match_capability_decision_source(self):
        content = _valid_content().replace(
            "| C02 | 推迟 | 用户授权模型决定 | “归档功能你决定，第一版简单点。” |",
            "| C02 | 推迟 | 用户明确确认 | “归档功能你决定，第一版简单点。” |",
            1,
        )
        result = _result(content, "V9")
        self.assertEqual("FAIL", result[1])
        self.assertIn("S2", result[2])


class TestOutputPath(unittest.TestCase):
    def test_valid_output_path(self):
        path = Path("project/intent-anchor/2026-07-11-001-跨会话交接.md")
        self.assertIsNone(_path_error(path))

    def test_latest_or_root_file_is_not_accepted_as_output_path(self):
        self.assertIsNotNone(_path_error(Path("INTENT.md")))
        self.assertIsNotNone(
            _path_error(Path("project/intent-anchor/latest.md"))
        )


if __name__ == "__main__":
    unittest.main()
