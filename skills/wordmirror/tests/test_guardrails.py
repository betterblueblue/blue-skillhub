# -*- coding: utf-8 -*-
"""wm.py 护栏回归：欠账本坏行拦截与两层记账、bind 绑定、写回坏行拦截与默认日期、没建索引时按意思搜安静返回空。

从仓库根 tests/test_wordmirror_guardrails.py 挪来（那份还在 import 改名前的 ds.py，2026-09-01 起就跑不起来）。
只保留现在仍成立、test_cli.py 又没覆盖的几条；「wb add 空内容被拒」test_cli.py 已有，没有再抄一份。
临时目录夹具；bind 相关用例把 HOME/USERPROFILE 指到临时目录，不碰真实的 ~/.wordmirror。
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(SKILL, 'scripts')
WM = os.path.join(SCRIPTS, 'wm.py')


def run(args, env, cwd=None):
    return subprocess.run([sys.executable, WM] + args, capture_output=True, text=True,
                          encoding='utf-8', errors='replace',
                          env=dict(env, PYTHONIOENCODING='utf-8'), cwd=cwd)


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


class GuardrailTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='wm-guard-')
        self.root = os.path.join(self.tmp, 'repo')          # 数据仓库（WORD_MIRROR_HOME）
        self.data = os.path.join(self.root, 'data')
        write_jsonl(os.path.join(self.data, 'corpus_dedup.jsonl'),
                    [{'agent': 'zcode', 'date': '2026-08-01', 'proj': 'demo', 'sid': 's1', 'msg': '我说过要把 demo 收尾'}])
        self.env = dict(os.environ, WORD_MIRROR_HOME=self.root)
        self.project = os.path.join(self.tmp, 'project')    # 数据仓库之外的某个项目目录
        os.makedirs(self.project)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _fake_home_env(self):
        """bind 指针写在 ~/.wordmirror/bind.json：把主目录换成临时目录，隔离真实数据。"""
        home = os.path.join(self.tmp, 'home')
        os.makedirs(home, exist_ok=True)
        env = dict(os.environ, HOME=home, USERPROFILE=home)
        env.pop('WORD_MIRROR_HOME', None)
        env.pop('DIGITAL_SELF_HOME', None)
        return env, os.path.join(home, '.wordmirror', 'bind.json')

    # —— 欠账本：坏行停写 + 两层记账 ——

    def test_corrupt_project_ledger_blocks_write(self):
        ledger = os.path.join(self.project, '.wordmirror', 'promises.jsonl')
        os.makedirs(os.path.dirname(ledger))
        with open(ledger, 'w', encoding='utf-8') as f:
            f.write('{不是合法json}\n')
        r = run(['promise', 'done', 'demo'], self.env, cwd=self.project)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('不是合法 JSON', r.stdout + r.stderr)

    def test_promise_add_outside_repo_goes_to_project_layer(self):
        r = run(['promise', 'add', '要做的事'], self.env, cwd=self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        ledger = os.path.join(self.project, '.wordmirror', 'promises.jsonl')
        self.assertTrue(os.path.exists(ledger))
        row = json.loads(open(ledger, encoding='utf-8').read().strip())
        self.assertEqual(row['status'], 'open')

    # —— bind：数据在别处时的接桥 ——

    def test_bind_writes_pointer_and_clear_removes(self):
        env, pointer = self._fake_home_env()
        r = run(['bind', self.root], env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(pointer))
        home_val = json.load(open(pointer, encoding='utf-8'))['home']
        self.assertEqual(os.path.normcase(home_val), os.path.normcase(self.root))
        r = run(['bind', '--clear'], env)
        self.assertEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(pointer))

    def test_bind_rejects_dir_without_data(self):
        env, pointer = self._fake_home_env()
        empty = os.path.join(self.tmp, 'empty')
        os.makedirs(empty)
        r = run(['bind', empty], env)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(pointer))

    # —— 写回：坏行拦截 + 默认日期 ——

    def test_wb_add_blocks_corrupt_file(self):
        wb = os.path.join(self.data, 'user_writebacks.jsonl')
        with open(wb, 'w', encoding='utf-8') as f:
            f.write('{坏行}\n')
        r = run(['wb', 'add', '新事实'], self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('不是合法 JSON', r.stdout + r.stderr)
        self.assertIn('坏行', open(wb, encoding='utf-8').read())  # 坏行还在，没被吞

    def test_wb_add_defaults_date_to_today(self):
        r = run(['wb', 'add', 'demo 项目确认关闭', '--topic', 'project/demo', '--ref', '用户原话「没有消息」'], self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        wb = os.path.join(self.data, 'user_writebacks.jsonl')
        rows = [json.loads(l) for l in open(wb, encoding='utf-8') if l.strip()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['msg'], 'demo 项目确认关闭')
        self.assertEqual(rows[0]['topic'], 'project/demo')
        self.assertEqual(rows[0]['date'], datetime.date.today().isoformat())

    # —— 按意思搜：没建索引时安静返回空，AI 退回自己搜文件 ——

    def test_vecsearch_query_returns_none_without_index(self):
        code = ("import sys; sys.path.insert(0, %r); import vecsearch; "
                "print(repr(vecsearch.query('任何问题')))" % SCRIPTS)
        r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
                           encoding='utf-8', errors='replace', env=dict(self.env, PYTHONIOENCODING='utf-8'))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip().splitlines()[-1], 'None')


if __name__ == '__main__':
    unittest.main()
