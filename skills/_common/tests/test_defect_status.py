#!/usr/bin/env python3
"""defect_status.defect_is_closed 判定表。

Run:
  python -m pytest skills/_common/tests/test_defect_status.py -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from defect_status import defect_is_closed
finally:
    sys.path.pop(0)


class TestDefectIsClosed(unittest.TestCase):
    def test_closed_statuses(self):
        for status in (
            "fixed",
            "Fixed",
            "fixed(复验通过)",
            "`fixed`",
            "**fixed**",
            "已修复",
            "已修复（复验 3/3 通过）",
            "open→fixed(复验证据)",
            "open -> fixed",
        ):
            with self.subTest(status=status):
                self.assertTrue(defect_is_closed(status))

    def test_open_statuses(self):
        # 子串判断时代 unfixed / not fixed 会被误判为已修复
        for status in (
            "open",
            "unfixed",
            "not fixed",
            "未修复",
            "修复中",
            "fixed→reopened",
            "",
        ):
            with self.subTest(status=status):
                self.assertFalse(defect_is_closed(status))


if __name__ == "__main__":
    unittest.main()
