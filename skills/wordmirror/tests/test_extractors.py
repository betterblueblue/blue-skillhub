# -*- coding: utf-8 -*-
"""提取器 fixture 冒烟测试：给每个 JSONL/文本提取器一份最小脱敏样本，
验证至少能提取出预期原话、输出字段完整；空 HOME 时全部提取器干净跳过不崩。
SQLite/zstd（cursor/zcode/dsh）不伪造脆弱二进制 schema，用空 HOME 守护兜底。"""
import io
import json
import os
import sys
import tempfile
import unittest

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL, 'scripts'))

import extract_all
import extract_ai


def write_file(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def run(home, fn):
    """把某提取器跑在一个临时 HOME 下，返回解析出的行列表。"""
    buf = io.StringIO()
    extract_all.H = home
    extract_ai.H = home
    fn(buf)
    rows = []
    for line in buf.getvalue().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class ExtractorSmokeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix='wm-fixture-')
        # 统一 1754000000 =. 2025-07-31 UTC；只在断言里用，不依赖真实时区判断
        self.ts = 1754000000

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _expect(self, rows, agent, msg):
        hit = [r for r in rows if r.get('agent') == agent and r.get('msg') == msg]
        self.assertTrue(hit, '提取器应产出 (%s, %s)，实际: %s' % (agent, msg, rows))
        return hit[0]

    def test_codex(self):
        d = os.path.join(self._tmp, '.codex', 'sessions', '2026', '08', '01')
        write_file(os.path.join(d, 'a.jsonl'),
                   '{"type":"session_meta","payload":{"id":"sid1","cwd":"/proj"}}\n'
                   '{"type":"event_msg","payload":{"type":"user_message","message":"请检查这段代码"},"timestamp":1754000000}\n')
        rows = run(self._tmp, extract_all.ex_codex)
        self._expect(rows, 'codex', '请检查这段代码')

    def test_claude(self):
        p = os.path.join(self._tmp, '.claude', 'projects', 'projA', 'sessionX.jsonl')
        write_file(p, '{"type":"user","message":{"content":"帮我写个爬虫"},"timestamp":1754000000}\n')
        rows = run(self._tmp, extract_all.ex_claude)
        self._expect(rows, 'claude-code', '帮我写个爬虫')

    def test_qwen(self):
        p = os.path.join(self._tmp, '.qwen', 'projects', 'projB', 'chats', 'chat1.jsonl')
        write_file(p, '{"type":"user","message":{"content":"翻译这段"},"timestamp":1754000000}\n')
        rows = run(self._tmp, extract_all.ex_qwen)
        self._expect(rows, 'qwen', '翻译这段')

    def test_workbuddy(self):
        p = os.path.join(self._tmp, '.workbuddy', 'projects', 'projC', 's.jsonl')
        write_file(p, '{"type":"message","role":"user","content":[{"text":"做完了"}],"timestamp":1754000000}\n')
        rows = run(self._tmp, extract_all.ex_workbuddy)
        self._expect(rows, 'workbuddy', '做完了')

    def test_pi(self):
        p = os.path.join(self._tmp, '.pi', 'agent', 'sessions', 'projD', 'sess.jsonl')
        write_file(p, '{"type":"message","message":{"role":"user","content":[{"type":"text","text":"你好"}]},"id":"m1","timestamp":1754000000}\n')
        rows = run(self._tmp, extract_all.ex_pi)
        self._expect(rows, 'pi', '你好')

    def test_atomcode(self):
        p = os.path.join(self._tmp, '.atomcode', 'datalog', 'projE', '2026-08-01.jsonl')
        write_file(p, '{"messages":[{"role":"user","content":{"Text":"写一个函数"}}]}\n')
        rows = run(self._tmp, extract_all.ex_atomcode)
        r = self._expect(rows, 'atomcode', '写一个函数')
        self.assertEqual(r.get('date'), '2026-08-01')

    def test_antigravity(self):
        p = os.path.join(self._tmp, '.gemini', 'antigravity', 'brain', 'CID12345', '.system_generated', 'logs', 'transcript.jsonl')
        write_file(p, '{"type":"USER_INPUT","content":"<USER_REQUEST>帮我看看报错</USER_REQUEST>","created_at":1754000000}\n')
        rows = run(self._tmp, extract_all.ex_antigravity)
        self._expect(rows, 'antigravity', '帮我看看报错')

    def test_grok(self):
        p = os.path.join(self._tmp, '.grok', 'logs', 'unified.jsonl')
        write_file(p, '{"ts":1754000000,"sid":"g1","src":"shell","ctx":{"prompt_text":"早上好"}}\n')
        rows = run(self._tmp, extract_all.ex_grok)
        self._expect(rows, 'grok', '早上好')

    def test_catpaw(self):
        p = os.path.join(self._tmp, '.catpaw', 'projects', 'projF--nice', 'sess1', 'agent-transcripts', 'transcript.txt')
        write_file(p, 'user:\n<user_query>请检查输入</user_query>\nassistant:\n好的\n')
        rows = run(self._tmp, extract_all.ex_catpaw)
        r = self._expect(rows, 'catpaw', '请检查输入')
        self.assertEqual(r.get('proj'), 'nice')

    def test_ai_side_codex(self):
        d = os.path.join(self._tmp, '.codex', 'sessions', '2026', '08', '01')
        write_file(os.path.join(d, 'a.jsonl'),
                   '{"type":"event_msg","payload":{"type":"agent_message","message":"这是AI给你的一段完整正式回复正文，请直接采用这个方案，后续我会详细展开每一步的验证过程。"},"timestamp":1754000000}\n')
        buf = io.StringIO()
        extract_ai.H = self._tmp
        extract_ai.ex_codex(buf)
        rows = [json.loads(l) for l in buf.getvalue().splitlines() if l.strip()]
        self.assertTrue([r for r in rows if r.get('agent') == 'codex' and '这是AI给你的一段完整正式回复正文' in r.get('msg', '')])

    def test_empty_home_no_crash(self):
        """空 HOME：每个用户/AI 提取器都应干净跳过（0 条、不异常）——含 SQLite/zstd 的 cursor/zcode/dsh。"""
        for fn in extract_all.ALL:
            buf = io.StringIO()
            extract_all.H = self._tmp
            fn(buf)  # 不应抛异常
        for fn in extract_ai.ALL:
            buf = io.StringIO()
            extract_ai.H = self._tmp
            fn(buf)


if __name__ == '__main__':
    unittest.main()