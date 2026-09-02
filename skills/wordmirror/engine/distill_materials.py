# -*- coding: utf-8 -*-
"""专题素材提取器：SOP 第 3 步的机器部分。
LLM 只负责最后的成文——素材（决策句/被问住句/月度切片/项目基因）全部由此脚本产出。
输出: data/materials_*.json"""
import json, re, collections, os, datetime

BASE = os.environ.get('WORD_MIRROR_HOME') or os.path.expanduser(os.path.join('~', '.wordmirror'))
DATA = os.path.join(BASE, 'data')
BS = chr(92)

rows = [json.loads(l) for l in open(os.path.join(DATA, 'corpus_dedup.jsonl'), encoding='utf-8')]
rows.sort(key=lambda r: r['date'])

def topic(r):
    p = (r.get('proj') or '').replace('\\', '/')
    seg = p.rstrip('/').split('/')[-1] if p else ''
    seg = seg.strip('-').replace('--', ' ').strip()
    # 纯十六进制哈希（如 antigravity 的 cid 前 8 位）不是主题
    if seg and re.fullmatch(r'[0-9a-fA-F]{6,40}', seg):
        return '(none)'
    return seg[:30] if seg else '(none)'

def sents(msg):
    return [s.strip() for s in re.split(r'[。！？\n]', msg.replace(chr(10), ' ')) if 6 < len(s.strip()) < 160]

NOISE = re.compile(r'^\[|^PS |^http|^Use |^Base dir|^#\d|^{"')

# ---- 3.1 决策素材 ----
dec_pat = re.compile(r'^我(决定|要|打算|准备|先|还是)|就(这样|选|定|用)|^先不|^放弃|^算了|选定|就这么|^优先')
decisions = []
seen = set()
for r in rows:
    for s in sents(r['msg']):
        if dec_pat.search(s) and not NOISE.match(s) and s[:25] not in seen:
            seen.add(s[:25])
            decisions.append({'date': r['date'], 'proj': topic(r), 'text': s})
json.dump(decisions, open(os.path.join(DATA, 'materials_decisions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('决策候选句:', len(decisions))

# ---- 3.6 能力素材：被问住 + 自信陈述 ----
stuck_pat = re.compile(r'这个我还真不知道|我还真不知道|不知道啊|不会啊|忘了|不记得|整不了|不会写|确实没有')
conf_pat = re.compile(r'我(做过|负责|搭建|开发|实现|写过|参与过|主导|带过)|我们(的项目|系统)')
stuck, conf = [], []
s_seen, c_seen = set(), set()
for r in rows:
    for s in sents(r['msg']):
        if stuck_pat.search(s) and not NOISE.match(s) and s[:25] not in s_seen:
            s_seen.add(s[:25]); stuck.append({'date': r['date'], 'text': s})
        if conf_pat.search(s) and len(s) > 15 and not NOISE.match(s) and s[:25] not in c_seen:
            c_seen.add(s[:25]); conf.append({'date': r['date'], 'text': s})
json.dump({'stuck': stuck, 'confident': conf}, open(os.path.join(DATA, 'materials_capability.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('被问住句:', len(stuck), '· 自信陈述:', len(conf))

# ---- 3.3 月度切片 ----
months = collections.defaultdict(list)
for r in rows:
    if r['date']: months[r['date'][:7]].append(r)
monthly = {}
for m, rs in sorted(months.items()):
    monthly[m] = {
        'n': len(rs),
        'top_topics': collections.Counter(topic(r) for r in rs).most_common(3),
        'opener': rs[0]['msg'][:80],
        'closer': rs[-1]['msg'][:80],
        'longest': max(rs, key=lambda r: len(r['msg']) if len(r['msg']) < 3000 else 0)['msg'][:120],
    }
json.dump(monthly, open(os.path.join(DATA, 'materials_monthly.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('月度切片:', len(monthly), '个月')

# ---- 3.5 项目基因 ----
proj_cards = collections.defaultdict(list)
for r in rows:
    proj_cards[topic(r)].append(r)
genes = {}
for t, rs in sorted(proj_cards.items(), key=lambda x: -len(x[1]))[:15]:
    rs.sort(key=lambda r: r['date'])
    genes[t] = {
        'n': len(rs), 'span': '%s ~ %s' % (rs[0]['date'], rs[-1]['date']),
        'first': rs[0]['msg'][:120].replace(chr(10), ' '),
        'last': rs[-1]['msg'][:120].replace(chr(10), ' '),
        'longest': max(rs, key=lambda r: len(r['msg']) if len(r['msg']) < 3000 else 0)['msg'][:200].replace(chr(10), ' '),
    }
json.dump(genes, open(os.path.join(DATA, 'materials_projects.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('项目基因:', len(genes), '个 top 项目')

print('\n输出 4 份素材 → data/materials_*.json（LLM 成文的唯一输入，禁止跳过此步直接凭语料感觉写）')
