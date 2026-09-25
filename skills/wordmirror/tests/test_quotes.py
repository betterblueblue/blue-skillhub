# -*- coding: utf-8 -*-
"""引文可追溯性检查测试：覆盖 匹配 / 日期错误 / 找不到原话 / AI 来源 四种情况。"""
import json
import os
import shutil
import sys
import tempfile
import unittest

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL, 'scripts'))

import check_quotes


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


class QuotesTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='wm-quote-')
        data = os.path.join(self.root, 'data')
        write_jsonl(os.path.join(data, 'corpus_dedup.jsonl'), [
            {'agent': 'codex', 'date': '2026-07-02', 'proj': 'a', 'sid': 's', 'msg': '我决定把项目重做一遍'},
        ])
        write_jsonl(os.path.join(data, 'ai_messages.jsonl'), [
            {'agent': 'codex', 'date': '2026-08-01', 'proj': 'a', 'sid': 's', 'msg': '这周你的状态不错'},
        ])
        self.data = data
        self.products = os.path.join(self.root, 'products')
        os.makedirs(self.products, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _write_report(self, text):
        p = os.path.join(self.data, 'profile', 'portrait.md')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)

    def test_all_ok(self):
        self._write_report('「我决定把项目重做一遍」（2026-07-02）\n'
                           '- 2026-07-02「我决定把项目重做一遍」\n'
                           '「这周你的状态不错」（2026-08-01，codex）\n')
        self.assertEqual(check_quotes.check_quotes(self.data, self.products), [])

    def test_fabricated_flagged(self):
        self._write_report('「这句话是我编的」（2026-07-02）\n')
        v = check_quotes.check_quotes(self.data, self.products)
        self.assertEqual(len(v), 1)
        self.assertIn('未在用户语料中找到', v[0][3])

    def test_quote_stats_classify_verified_and_unverifiable(self):
        self._write_report('「我决定把项目重做一遍」（2026-07-02）\n'
                           '「这句话是我编的」（2026-07-02）\n')
        stats = {}
        v = check_quotes.check_quotes(self.data, self.products, stats=stats)
        self.assertEqual(len(v), 1)
        self.assertEqual(stats['checked'], 2)
        self.assertEqual(stats['verified'], 1)
        self.assertEqual(stats['truncated'], 0)
        self.assertEqual(stats['unverifiable'], 1)

    def test_date_wrong_still_passes(self):
        # 话确实说过，只是报告写的日期与语料不同：跨日期语料下日期匹配噪声大，
        # 检查只判「话有没有说过」，不判日期——这条应通过。
        self._write_report('「我决定把项目重做一遍」（2026-08-09）\n')
        self.assertEqual(check_quotes.check_quotes(self.data, self.products), [])

    def test_truncated_quote_passes(self):
        # 报告用省略号截断长原话：任一片段能在语料中找到即可通过。
        self._write_report('「我决定把项目…做一遍」（2026-07-02）\n')
        self.assertEqual(check_quotes.check_quotes(self.data, self.products), [])

    def test_ai_quote_without_tool_is_checked_against_user(self):
        # 无工具的引文按用户语料查；这句话在用户语料没有 -> 应被标记
        self._write_report('「这周你的状态不错」（2026-08-01）\n')
        v = check_quotes.check_quotes(self.data, self.products)
        self.assertEqual(len(v), 1)

    def test_plain_text_not_flagged(self):
        # 不带（日期）的普通句子/标题不误报
        self._write_report('我最近在忙一个项目，决定把 "重做" 这件事提上日程。\n')
        self.assertEqual(check_quotes.check_quotes(self.data, self.products), [])


if __name__ == '__main__':
    unittest.main()