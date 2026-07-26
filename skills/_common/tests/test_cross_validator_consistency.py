#!/usr/bin/env python3
"""跨校验器一致性测试。

impact V23 与 intent-design A7 的证据白名单是同一逻辑的两份拷贝
（skill 独立分发，暂不单源化）。本测试锁定两边正则必须逐字符一致，
防止再次出现单边修改导致的行为漂移（2026-07 强模型验证时曾实际发生）。

Run:
  python -m pytest skills/_common/tests/test_cross_validator_consistency.py -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# 本文件位于 skills/_common/tests/ 下，向上三级即 skills/
SKILLS_ROOT = Path(__file__).resolve().parent.parent.parent

for rel in ("impact/scripts", "intent-design/scripts"):
    path = str(SKILLS_ROOT / rel)
    if path not in sys.path:
        sys.path.insert(0, path)

import impact_validate  # noqa: E402
import design_validate  # noqa: E402


class TestEvidenceWhitelistParity(unittest.TestCase):
    """四组必须逐字符一致的正则拷贝。改任何一边必须同步另一边。"""

    def test_code_location_pattern_identical(self):
        self.assertEqual(
            impact_validate.RE_CODE_LOCATION.pattern,
            design_validate.RE_EVIDENCE_CODE.pattern,
            "证据白名单（代码位置）两份拷贝不一致——改一边必须同步另一边",
        )

    def test_quote_pattern_identical(self):
        self.assertEqual(
            impact_validate.RE_QUOTE.pattern,
            design_validate.RE_EVIDENCE_QUOTE.pattern,
            "证据白名单（引号）两份拷贝不一致",
        )

    def test_quoted_span_pattern_identical(self):
        self.assertEqual(
            impact_validate.RE_QUOTED_SPAN.pattern,
            design_validate.RE_QUOTED_SPAN.pattern,
            "引号剥离正则两份拷贝不一致",
        )

    def test_no_extra_line_pattern_identical(self):
        self.assertEqual(
            impact_validate.RE_NO_EXTRA_LINE.pattern,
            design_validate.RE_NO_EXTRA_LINE.pattern,
            "无额外结构声明行正则两份拷贝不一致",
        )


if __name__ == "__main__":
    unittest.main()
