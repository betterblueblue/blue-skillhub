# -*- coding: utf-8 -*-
"""全管道 smoke：合成一个小语料，跑 去重→统计→素材→照见候选，
验证每个环节脚本以 0 退出、关键产物写出且 JSON 可读。全程用临时 WORD_MIRROR_HOME，不碰真实数据。"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(SKILL, 'scripts')


def run_script(name, env):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, name)],
                          capture_output=True, text=True, env=env)


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


class PipelineSmokeTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='wm-pipe-')
        data = os.path.join(self.root, 'data')
        # 环境变量指向临时根；_find_base 需要其下有 data/ 子目录
        self.env = dict(os.environ, WORD_MIRROR_HOME=self.root)
        write_jsonl(os.path.join(data, 'corpus_all.jsonl'), [
            {'agent': 'codex', 'date': '2026-07-02', 'proj': 'a', 'sid': 's', 'msg': '我决定把项目重做一遍'},
            {'agent': 'codex', 'date': '2026-07-02', 'proj': 'a', 'sid': 's', 'msg': '我决定把项目重做一遍'},  # 重复，应被去重
            {'agent': 'claude-code', 'date': '2026-08-03', 'proj': 'a', 'sid': 's', 'msg': '帮我写个爬虫抓这个页面'},
        ])
        write_jsonl(os.path.join(data, 'corpus_dedup.jsonl'), [
            {'agent': 'codex', 'date': '2026-07-02', 'proj': 'a', 'sid': 's', 'msg': '我决定把项目重做一遍'},
            {'agent': 'claude-code', 'date': '2026-08-03', 'proj': 'a', 'sid': 's', 'msg': '帮我写个爬虫抓这个页面'},
        ])
        write_jsonl(os.path.join(data, 'ai_messages.jsonl'), [
            {'agent': 'codex', 'date': '2026-07-02', 'proj': 'a', 'sid': 's', 'msg': '好的，我按你说的重做'},
        ])

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _step(self, script):
        r = run_script(script, self.env)
        self.assertEqual(r.returncode, 0, '%s 退出码 %s，stderr=%s' % (script, r.returncode, r.stderr[-300:]))

    def test_pipeline_runs(self):
        self._step('dedup.py')
        self._step('compute_stats.py')
        self._step('distill_materials.py')
        self._step('distill_insights.py')

    def test_dedup_removes_duplicates(self):
        run_script('dedup.py', self.env)
        with open(os.path.join(self.root, 'data', 'corpus_dedup.jsonl'), encoding='utf-8') as f:
            rows = [json.loads(l) for l in f if l.strip()]
        self.assertEqual(len(rows), 2)  # 两条不同，重复那条被去重

    def test_stats_outputs_valid_json(self):
        run_script('compute_stats.py', self.env)
        for name in ('stats_wordfreq.json', 'stats_agents.json', 'stalled_topics.json'):
            p = os.path.join(self.root, 'data', name)
            self.assertTrue(os.path.exists(p), name + ' 未生成')
            with open(p, encoding='utf-8') as f:
                json.load(f)  # 可解析

    def test_materials_outputs_valid_json(self):
        run_script('distill_materials.py', self.env)
        for name in ('materials_decisions.json', 'materials_capability.json', 'materials_monthly.json', 'materials_projects.json'):
            p = os.path.join(self.root, 'data', name)
            self.assertTrue(os.path.exists(p), name + ' 未生成')
            with open(p, encoding='utf-8') as f:
                json.load(f)

    def test_insights_outputs_valid_json(self):
        run_script('distill_insights.py', self.env)
        p = os.path.join(self.root, 'data', 'materials_insights.json')
        self.assertTrue(os.path.exists(p))
        with open(p, encoding='utf-8') as f:
            json.load(f)


if __name__ == '__main__':
    unittest.main()