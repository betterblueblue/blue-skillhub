#!/usr/bin/env python3
"""Behavior tests for adversarial_validate.py.

Run:
  python -m pytest skills/intent-adversarial/tests/test_adversarial_validate.py -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from adversarial_validate import validate  # noqa: E402

INTENT = """# INTENT

## 15. 性能要求

| 要求 ID | 性能要求 | 对应能力 | 用户确认 |
|---|---|---|---|
| PF01 | 接口 ≤ 1s | C01 | 确认 |

### 并发一致性要求

| 要求 ID | 一致性断言 | 对应能力 | 用户确认 |
|---|---|---|---|
| CC01 | 库存不为负 | C06 | 确认 |

## 16. 安全要求

| 要求 ID | 安全要求 | 对应能力 | 用户确认 |
|---|---|---|---|
| SF01 | 密码强哈希 | C08 | 确认 |
| SF04 | 越权防护 | C06 | 确认 |
"""

VALID_RECORD = """# Adversarial Record

## 1. 验证概述

SF 2 条 / CC 1 条；放大至 1000 服装 2000 订单。

## 2. 数据准备

seed-realworld + 放大；清理方式：seed:real。

## 3. 安全攻击结果

| 类别 | 用例 | 关联 SF | 结果 | DB 核查 |
|---|---|---|---|---|
| 垂直越权 | USER 调终审 | SF01 | 防御成功(403) | 无 |
| 横向越权 | A 删 B 收藏 | SF04 | 防御成功(静默) | 无变化 |

## 4. 并发一致性结果

| 要求 ID | 一致性断言 | 并发场景 | 实测结果 | 通过 |
|---|---|---|---|---|
| CC01 | 库存不为负 | 50 抢 10 | 成功 10，库存 0 | 是 |

## 5. 性能基准

| 接口 | avg | p50 | p95 | rps | 5xx |
|---|---|---|---|---|---|
| 列表 | 10 | 9 | 14 | 250 | 0 |

## 6. 缺陷清单

| 缺陷 ID | 严重度 | 描述 | 证据 | 状态 |
|---|---|---|---|---|

## 7. 结论

通过。
"""

HIGH_OPEN_RECORD = VALID_RECORD.replace(
    "## 6. 缺陷清单\n\n| 缺陷 ID | 严重度 | 描述 | 证据 | 状态 |\n|---|---|---|---|---|\n",
    "## 6. 缺陷清单\n\n| 缺陷 ID | 严重度 | 描述 | 证据 | 状态 |\n|---|---|---|---|---|\n"
    "| FIX-001 | 高 | 超卖 | 50 单/库存-40 | open |\n",
)


class TestAdversarialValidate(unittest.TestCase):
    def test_valid_record_passes(self):
        results = validate(VALID_RECORD, INTENT)
        self.assertTrue(all(status == "PASS" for _c, status, _m in results), results)
        self.assertEqual(6, len(results))

    def test_missing_section_fails(self):
        content = VALID_RECORD.replace("## 5. 性能基准\n\n| 接口 | avg | p50 | p95 | rps | 5xx |\n|---|---|---|---|---|---|\n| 列表 | 10 | 9 | 14 | 250 | 0 |\n", "")
        results = validate(content, INTENT)
        a2 = [r for r in results if r[0] == "A2"][0]
        self.assertEqual("FAIL", a2[1])
        self.assertIn("性能基准", a2[2])

    def test_sf_not_covered_fails(self):
        content = VALID_RECORD.replace("| 横向越权 | A 删 B 收藏 | SF04 |", "| 横向越权 | A 删 B 收藏 | SF09 |")
        results = validate(content, INTENT)
        a3 = [r for r in results if r[0] == "A3"][0]
        self.assertEqual("FAIL", a3[1])
        self.assertIn("SF04", a3[2])

    def test_cc_uncovered_or_failed_fails(self):
        content = VALID_RECORD.replace("| CC01 | 库存不为负 | 50 抢 10 | 成功 10，库存 0 | 是 |", "| CC01 | 库存不为负 | 50 抢 10 | 超卖 | 否 |")
        results = validate(content, INTENT)
        a4 = [r for r in results if r[0] == "A4"][0]
        self.assertEqual("FAIL", a4[1])
        self.assertIn("CC01", a4[2])

    def test_high_open_defect_blocks(self):
        results = validate(HIGH_OPEN_RECORD, INTENT)
        a5 = [r for r in results if r[0] == "A5"][0]
        self.assertEqual("FAIL", a5[1])
        self.assertIn("FIX-001", a5[2])

    def test_unfixed_wording_still_blocks(self):
        """子串判断时代 unfixed / not fixed 会被当成已修复放行。"""
        for status in ("unfixed", "not fixed"):
            with self.subTest(status=status):
                content = HIGH_OPEN_RECORD.replace("| open |", f"| {status} |")
                results = validate(content, INTENT)
                a5 = [r for r in results if r[0] == "A5"][0]
                a6 = [r for r in results if r[0] == "A6"][0]
                self.assertEqual("FAIL", a5[1], a5)
                # 记录结论写的是「通过」，高危缺陷未关闭时 A6 也要拦
                self.assertEqual("FAIL", a6[1], a6)

    def test_chinese_fixed_status_passes(self):
        """中文状态「已修复」应算关闭，不能被误拦。"""
        content = HIGH_OPEN_RECORD.replace("| open |", "| 已修复（复验 3/3 通过） |")
        results = validate(content, INTENT)
        a5 = [r for r in results if r[0] == "A5"][0]
        self.assertEqual("PASS", a5[1], a5)

    def test_empty_file_fails(self):
        results = validate("", INTENT)
        self.assertEqual("FAIL", results[0][1])


if __name__ == "__main__":
    unittest.main()
