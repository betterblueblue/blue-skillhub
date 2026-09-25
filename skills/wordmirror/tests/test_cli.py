# -*- coding: utf-8 -*-
"""wm.py CLI 回归：决定类写回可选字段、corr 命令、坏行拦截、旧格式兼容。临时 WORD_MIRROR_HOME，不碰真实数据。"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WM = os.path.join(SKILL, 'scripts', 'wm.py')


def run(args, env):
    return subprocess.run([sys.executable, WM] + args, capture_output=True, text=True, env=env)


class WmCliTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='wm-cli-')
        os.makedirs(os.path.join(self.root, 'data'), exist_ok=True)
        self.env = dict(os.environ, WORD_MIRROR_HOME=self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _read_wb(self):
        p = os.path.join(self.root, 'data', 'user_writebacks.jsonl')
        return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()] if os.path.exists(p) else []

    def _read_corr(self):
        p = os.path.join(self.root, 'data', 'profile', 'corrections.jsonl')
        rows = []
        if os.path.exists(p):
            for l in open(p, encoding='utf-8'):
                if not l.strip():
                    continue
                try:
                    rows.append(json.loads(l))
                except Exception:
                    pass  # 与 corr list 一致：坏行跳过，不崩
        return rows

    def test_wb_decision_fields(self):
        r = run(['wb', 'add', '先不迁移X', '--kind', 'decision', '--reason', '收益不足', '--revisit', '条件变化', '--status', 'active'], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self._read_wb()[0]
        self.assertEqual(row['kind'], 'decision')
        self.assertEqual(row['reason'], '收益不足')
        self.assertEqual(row['revisit_when'], '条件变化')
        self.assertEqual(row['status'], 'active')
        self.assertEqual(row['msg'], '先不迁移X')

    def test_wb_plain_backcompat(self):
        r = run(['wb', 'add', '普通事实', '--topic', 't'], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self._read_wb()[0]
        # 老格式记录不强制带新字段
        self.assertNotIn('kind', row)
        self.assertEqual(row['topic'], 't')

    def test_wb_empty_rejected(self):
        r = run(['wb', 'add'], self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self._read_wb(), [])

    def test_wb_gets_id(self):
        run(['wb', 'add', '定了用 B 方案', '--topic', 't'], self.env)
        row = self._read_wb()[0]
        self.assertTrue(row.get('id', '').startswith('wb-'))

    def test_wb_date_backfill(self):
        # 补录历史决定：--date 写原始日期，不是登记当天
        r = run(['wb', 'add', '还是去找工作了', '--date', '2026-06-07', '--ref', '原话'], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self._read_wb()[0]['date'], '2026-06-07')
        r = run(['wb', 'add', '坏日期', '--date', '6月7日'], self.env)
        self.assertNotEqual(r.returncode, 0)

    def test_wb_supersedes(self):
        run(['wb', 'add', '不考了', '--topic', 'exam'], self.env)
        old_id = self._read_wb()[0]['id']
        r = run(['wb', 'add', '还是在职考', '--topic', 'exam', '--supersedes', old_id], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = self._read_wb()
        self.assertEqual(len(rows), 2)                      # 旧行保留，历史不删
        self.assertEqual(rows[1]['supersedes'], old_id)
        out = run(['wb', 'list'], self.env).stdout          # list 只显示生效的
        self.assertIn('还是在职考', out)
        self.assertNotIn('不考了', out.replace('还是在职考', ''))
        # 指向不存在的 id → 拦下不写
        r = run(['wb', 'add', '顶替幽灵', '--supersedes', 'wb-00000000000000'], self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(len(self._read_wb()), 2)

    def test_corr_add_and_list(self):
        r = run(['corr', 'add', '把候选当结论', '--rule', '先回查原话'], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self._read_corr()[0]
        self.assertEqual(row['rule'], '先回查原话')
        self.assertEqual(row['correction'], '把候选当结论')
        rl = run(['corr', 'list'], self.env)
        self.assertEqual(rl.returncode, 0)
        self.assertIn('先回查原话', rl.stdout)

    def test_corr_requires_rule(self):
        r = run(['corr', 'add', '只有纠正没规则'], self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self._read_corr(), [])

    def test_corr_bad_line_blocks(self):
        run(['corr', 'add', 'A', '--rule', 'R'], self.env)
        p = os.path.join(self.root, 'data', 'profile', 'corrections.jsonl')
        with open(p, 'a', encoding='utf-8') as f:
            f.write('{not json}\n')  # 塞入坏行
        r = run(['corr', 'add', 'B', '--rule', 'R2'], self.env)
        self.assertNotEqual(r.returncode, 0)
        rows = self._read_corr()
        self.assertEqual(len([x for x in rows if x.get('correction') == 'B']), 0)  # 坏行挡下，没写进去

    def test_progress_resume(self):
        self.assertNotEqual(run(['progress', 'done', 'detect'], self.env).returncode, 0)  # 没 start 不让记
        run(['progress', 'start'], self.env)
        run(['progress', 'done', 'detect'], self.env)
        run(['progress', 'done', 'extract_user', '--note', '1200 条'], self.env)
        r = run(['progress'], self.env)
        self.assertIn('下一步：extract_ai', r.stdout)
        self.assertNotEqual(run(['progress', 'done', 'bogus'], self.env).returncode, 0)  # 未知步骤拦下
        st = json.load(open(os.path.join(self.root, 'data', 'progress.json'), encoding='utf-8'))
        self.assertEqual(st['steps']['extract_user']['note'], '1200 条')
        run(['progress', 'start'], self.env)  # 新一轮清空
        self.assertIn('下一步：detect', run(['progress'], self.env).stdout)


if __name__ == '__main__':
    unittest.main()
