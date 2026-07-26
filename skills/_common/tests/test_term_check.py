#!/usr/bin/env python3
"""term_check.py 行为测试：术语落地反查 + 豁免规则。

Run:
  python -m pytest skills/_common/tests/test_term_check.py -v
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from term_check import check
finally:
    sys.path.pop(0)

INTENT_WITH_TERM = """# INTENT

## 12. 设计标准

| 设计素材 ID | 类型 | 路径 | 验收范围 | 用户确认 |
|---|---|---|---|---|
| D01 | 可点原型 | `prototype/`（screens/*.html） | 已建页面 | "对的" |

## 13. 术语表

| 原始术语 | 人话翻译 | 用于界面的文案 | 出现在能力 ID |
|---|---|---|---|
| 金刚区 | 首页图标导航区 | 首页功能入口 | C01 |
"""

INTENT_NO_TERM = """# INTENT

## 12. 设计标准

无设计标准素材。用户明确确认："没有"。

## 13. 术语表

无术语需要翻译。
"""


def _make_project(intent_text: str, files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    chain = root / "intent-chain" / "2026-07-27-001-术语测试"
    chain.mkdir(parents=True)
    (chain / "intent.md").write_text(intent_text, encoding="utf-8")
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return chain


class TestTermCheck(unittest.TestCase):
    def test_term_in_ui_file_fails(self):
        chain = _make_project(INTENT_WITH_TERM, {
            "app/src/pages/home.vue": "<template>\n  <view>金刚区分类</view>\n</template>\n",
        })
        passes, fails = check(chain)
        self.assertTrue(any("金刚区" in f and "home.vue" in f for f in fails), fails)

    def test_clean_ui_passes(self):
        chain = _make_project(INTENT_WITH_TERM, {
            "app/src/pages/home.vue": "<template>\n  <view>首页功能入口</view>\n</template>\n",
        })
        passes, fails = check(chain)
        self.assertEqual([], fails, fails)
        self.assertTrue(any("零出现" in p for p in passes), passes)

    def test_comment_line_exempt(self):
        chain = _make_project(INTENT_WITH_TERM, {
            "app/src/pages/home.vue": "<template>\n  <!-- 原型里叫金刚区 -->\n  <view>首页功能入口</view>\n</template>\n",
        })
        passes, fails = check(chain)
        self.assertEqual([], fails, fails)

    def test_design_material_dir_exempt(self):
        chain = _make_project(INTENT_WITH_TERM, {
            "prototype/screens/home.html": "<div>金刚区</div>\n",
            "app/src/pages/home.vue": "<view>首页功能入口</view>\n",
        })
        passes, fails = check(chain)
        self.assertEqual([], fails, fails)

    def test_node_modules_exempt(self):
        chain = _make_project(INTENT_WITH_TERM, {
            "app/node_modules/lib/x.vue": "<view>金刚区</view>\n",
            "app/src/pages/home.vue": "<view>首页功能入口</view>\n",
        })
        passes, fails = check(chain)
        self.assertEqual([], fails, fails)

    def test_no_terms_passes(self):
        chain = _make_project(INTENT_NO_TERM, {
            "app/src/pages/home.vue": "<view>金刚区</view>\n",
        })
        passes, fails = check(chain)
        self.assertEqual([], fails)
        self.assertTrue(any("术语表为空" in p for p in passes), passes)


if __name__ == "__main__":
    unittest.main()
