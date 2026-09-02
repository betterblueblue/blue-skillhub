# -*- coding: utf-8 -*-
"""去重：corpus_all.jsonl → corpus_dedup.jsonl。
去重键 = 日期 + 全文归一化哈希：同一天的同内容只留一条，跨日期的同内容保留（保住引文日期）。"""
import os, re, json, hashlib

BASE = os.environ.get('WORD_MIRROR_HOME') or os.path.expanduser(os.path.join('~', '.wordmirror'))
DATA = os.path.join(BASE, 'data')
SRC = os.path.join(DATA, 'corpus_all.jsonl')
DST = os.path.join(DATA, 'corpus_dedup.jsonl')

seen, out = set(), []
n_in = 0
for line in open(SRC, encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    o = json.loads(line)
    n_in += 1
    k = hashlib.sha1((o.get('date', '') + '|' + re.sub(r'\s+', '', o['msg'])).encode('utf-8')).hexdigest()
    if k in seen:
        continue
    seen.add(k)
    out.append(o)

with open(DST, 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + '\n')

print('去重：%d 条 → %d 条' % (n_in, len(out)))
