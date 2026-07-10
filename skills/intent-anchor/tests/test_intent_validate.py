#!/usr/bin/env python3
"""Tests for intent_validate.py.

Run: python -m pytest skills/intent-anchor/tests/test_intent_validate.py -v
     or: python skills/intent-anchor/tests/test_intent_validate.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "intent_validate.py"

# Import validate function directly
sys.path.insert(0, str(SCRIPT.parent))
try:
    from intent_validate import validate
finally:
    sys.path.pop(0)


VALID_CAP_ROWS = """| # | 能力 | 描述 | 来源 | 标记 | 决策 |
|---|------|------|------|------|------|
| 1 | 用户认证 | 登录注册 | 类比 | 👍 | 保留 |
| 2 | 权限管理 | RBAC控制 | 类比 | 👍 | 保留 |
| 3 | 审计日志 | 操作记录 | 类比 | 👍 | 保留 |
| 4 | 数据导出 | 导出CSV | 反面 | ❌ | 放弃 |
| 5 | 通知系统 | 邮件通知 | 场景 | 🤔 | 推迟 |
"""

VALID_INTENT_BODY = f"""
## 1. 一句话意图
做一个用户管理系统

## 2. 场景类型
内部工具

## 3. 源系统或类比物
| 名称 | 路径/链接 | 说明 |
|------|----------|------|
| 参考 | /path | 参考 |

## 4. 完整能力清单
{VALID_CAP_ROWS}

## 5. 不可妥协项

1. 用户认证
2. 权限管理
3. 审计日志

## 6. 可推迟项

| 能力 | 推迟原因 | 预计何时做 |
|------|----------|-----------|
| 通知系统 | Phase 2 | 后续 |

## 7. 漂移模式检查

| 模式 | 是否命中 | 说明 |
|------|---------|------|
| D1 重新发明 | ✅ | |
| D2 砍到无关 | ✅ | |
| D3 降级代替 | ✅ | |
| D4 单循环锁定 | ✅ | |
| D5 沉默输出 | ✅ | |
| D6 不追求吃核心 | ✅ | |
| D7 上下文蒸发 | ✅ | |
| D8/D9 源系统/类比物蒸发 | ✅ | |

## 8. 覆盖率

```
保留：3 条
推迟：1 条
放弃：1 条
总计：5 条

放弃项逐条报告：
| # | 能力 | 不可妥协项? | 用户确认 | 确认内容 |
|---|------|------------|---------|---------|
| 1 | 数据导出 | 否 | ✅ | 用户说不需要 |
```

## 9. 用户确认记录

| 日期 | 确认内容 |
|------|---------|
| 2026-07-10 | 确认能力清单 |

## 10. 语义自检结果

### S1 源系统完整性
已检查

### S2 确认可追溯性
已检查

### S3 不可妥协项
已检查

### S4 锚定真实性
已检查

### S5 漂移自检
已检查

## 11. 三重锚定原始记录
原始记录
"""


def _make_intent(cap_rows: str = VALID_CAP_ROWS, cs_items: str = "1. 用户认证\n2. 权限管理\n3. 审计日志") -> str:
    """Build a complete INTENT.md with customizable capability rows and 不可妥协项."""
    default_cs = "1. 用户认证\n2. 权限管理\n3. 审计日志"
    body = VALID_INTENT_BODY.replace(VALID_CAP_ROWS, cap_rows).replace(default_cs, cs_items)
    return f"""# Intent

{body}"""


class TestV3DecisionColumnValidation(unittest.TestCase):
    """V3: Decision column must be exactly one of {'保留', '推迟', '放弃'}."""

    def test_invalid_decision_fails(self):
        """Decision column with '不保留' should FAIL V3."""
        bad_rows = """| # | 能力 | 描述 | 来源 | 标记 | 决策 |
|---|------|------|------|------|------|
| 1 | 用户认证 | 登录注册 | 类比 | 👍 | 不保留 |
| 2 | 权限管理 | RBAC控制 | 类比 | 👍 | 保留 |
| 3 | 数据导出 | 导出CSV | 反面 | ❌ | 放弃 |
| 4 | 通知系统 | 邮件通知 | 场景 | 🤔 | 推迟 |
"""
        content = _make_intent(cap_rows=bad_rows)
        results = validate(content)
        v3 = [r for r in results if r[0] == "V3"]
        self.assertEqual(v3[0][1], "FAIL", f"Expected V3 FAIL for '不保留', got: {v3}")
        self.assertIn("非法", v3[0][2])

    def test_empty_decision_fails(self):
        """Empty decision column should FAIL V3."""
        bad_rows = """| # | 能力 | 描述 | 来源 | 标记 | 决策 |
|---|------|------|------|------|------|
| 1 | 用户认证 | 登录注册 | 类比 | 👍 | |
| 2 | 权限管理 | RBAC控制 | 类比 | 👍 | 保留 |
| 3 | 数据导出 | 导出CSV | 反面 | ❌ | 放弃 |
| 4 | 通知系统 | 邮件通知 | 场景 | 🤔 | 推迟 |
"""
        content = _make_intent(cap_rows=bad_rows)
        results = validate(content)
        v3 = [r for r in results if r[0] == "V3"]
        self.assertEqual(v3[0][1], "FAIL", f"Expected V3 FAIL for empty decision, got: {v3}")

    def test_valid_decisions_pass(self):
        """All valid decisions should PASS V3."""
        content = _make_intent()
        results = validate(content)
        v3 = [r for r in results if r[0] == "V3"]
        self.assertEqual(v3[0][1], "PASS", f"Expected V3 PASS, got: {v3}")


class TestV4RetainedCrossCheck(unittest.TestCase):
    """V4: 不可妥协项 must match capabilities with decision == '保留'."""

    def test_non_retained_name_fails(self):
        """不可妥协项 referencing a '放弃' capability should FAIL V4."""
        # 权限管理 is marked 放弃, not 保留
        bad_rows = """| # | 能力 | 描述 | 来源 | 标记 | 决策 |
|---|------|------|------|------|------|
| 1 | 用户认证 | 登录注册 | 类比 | 👍 | 保留 |
| 2 | 权限管理 | RBAC控制 | 类比 | 👍 | 放弃 |
| 3 | 审计日志 | 操作记录 | 类比 | 👍 | 保留 |
| 4 | 数据导出 | 导出CSV | 反面 | ❌ | 放弃 |
| 5 | 通知系统 | 邮件通知 | 场景 | 🤔 | 推迟 |
"""
        content = _make_intent(cap_rows=bad_rows, cs_items="1. 用户认证\n2. 权限管理\n3. 审计日志")
        results = validate(content)
        v4 = [r for r in results if r[0] == "V4"]
        self.assertEqual(v4[0][1], "FAIL", f"Expected V4 FAIL for non-retained item, got: {v4}")

    def test_retained_name_passes(self):
        """不可妥协项 referencing '保留' capabilities should PASS V4."""
        content = _make_intent()
        results = validate(content)
        v4 = [r for r in results if r[0] == "V4"]
        self.assertEqual(v4[0][1], "PASS", f"Expected V4 PASS, got: {v4}")


class TestV6AbandonNameCrossCheck(unittest.TestCase):
    """V6: Abandon report rows must contain capability names from §4 '放弃' items."""

    def test_wrong_name_in_report_fails(self):
        """Report rows with unrelated capability names should FAIL V6."""
        # Replace the report to use a name that's not in §4 放弃 items
        content = _make_intent()
        content = content.replace(
            "| 1 | 数据导出 | 否 | ✅ | 用户说不需要 |",
            "| 1 | 完全无关的能力 | 否 | ✅ | 用户说不需要 |",
        )
        results = validate(content)
        v6 = [r for r in results if r[0] == "V6"]
        self.assertEqual(v6[0][1], "FAIL", f"Expected V6 FAIL for wrong name, got: {v6}")

    def test_correct_name_in_report_passes(self):
        """Report rows with matching capability names should PASS V6."""
        content = _make_intent()
        results = validate(content)
        v6 = [r for r in results if r[0] == "V6"]
        self.assertEqual(v6[0][1], "PASS", f"Expected V6 PASS, got: {v6}")

    def test_rejected_confirmation_fails(self):
        """A matching abandon report marked with X must still FAIL V6."""
        content = _make_intent().replace(
            "| 1 | 数据导出 | 否 | ✅ | 用户说不需要 |",
            "| 1 | 数据导出 | 否 | ❌ | 用户尚未确认 |",
        )
        results = validate(content)
        v6 = [r for r in results if r[0] == "V6"]
        self.assertEqual(v6[0][1], "FAIL", f"Expected V6 FAIL for rejected confirmation, got: {v6}")


if __name__ == "__main__":
    unittest.main()
