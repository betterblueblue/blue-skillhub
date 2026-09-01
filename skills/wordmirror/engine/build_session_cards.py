# -*- coding: utf-8 -*-
"""会话卡生成器：user 语料 + ai 语料 -> 每会话一张卡 sessions.jsonl
卡结构: {sid, agent, date, proj, user_summary(前3条用户消息), ai_conclusion(最实质回复), n_user, n_ai}"""
import json, os, re, collections

import os
BASE = os.environ.get('WORD_MIRROR_HOME') or os.path.expanduser(os.path.join('~', 'WordMirror'))
WORK = os.path.join(BASE, 'data')
users = [json.loads(l) for l in open(WORK + '/corpus_dedup.jsonl', encoding='utf-8')]
ais = [json.loads(l) for l in open(WORK + '/ai_messages.jsonl', encoding='utf-8')]

# 按 (agent, sid) 聚合
sessions = {}
for r in users:
    k = (r['agent'], r.get('sid') or '')
    sessions.setdefault(k, {'users': [], 'proj': r.get('proj',''), 'date': r.get('date','')})
    sessions[k]['users'].append(r['msg'])
for r in ais:
    k = (r['agent'], r.get('sid') or '')
    if k in sessions:  # 只给有用户消息的会话配 AI 回复
        sessions[k].setdefault('ais', []).append(r['msg'])

def summarize_user(msgs):
    """取前 3 条有实质内容的用户消息拼成摘要"""
    out = []
    for m in msgs:
        m = m.strip().replace('\n', ' ')
        if len(m) < 4: continue
        out.append(m[:150])
        if len(out) >= 3: break
    return ' / '.join(out)

def pick_ai(msgs):
    """AI 结论：取最长的一条（通常是最实质的总结回复），截 400 字"""
    if not msgs: return ''
    best = max(msgs, key=len)
    best = re.sub(r'\s+', ' ', best).strip()
    return best[:400]

cards = []
for (agent, sid), s in sessions.items():
    u_msgs = s['users']
    if len(u_msgs) < 2:  # 单条消息的会话价值低，跳过
        continue
    ai_msgs = s.get('ais', [])
    # 日期取中位
    dates = sorted([x for x in [s['date']] if x])
    cards.append({
        'agent': agent,
        'sid': sid[:12],
        'date': s['date'],
        'proj': (s['proj'] or '').split(chr(92))[-1][:40] if s['proj'] else '',
        'n_user': len(u_msgs),
        'n_ai': len(ai_msgs),
        'user_summary': summarize_user(u_msgs),
        'ai_conclusion': pick_ai(ai_msgs),
    })

# 排序：按日期
cards.sort(key=lambda c: c['date'] or '')
with open(WORK + '/sessions.jsonl', 'w', encoding='utf-8') as f:
    for c in cards:
        f.write(json.dumps(c, ensure_ascii=False) + '\n')

print('会话卡总数:', len(cards))
print('按 agent:', dict(collections.Counter(c['agent'] for c in cards)))
print('有 AI 结论的卡:', sum(1 for c in cards if c['ai_conclusion']))
# 样例
print()
print('=== 样例卡（高互动会话）===')
top = sorted(cards, key=lambda c: -(c['n_user'] + c['n_ai']))[:3]
for c in top:
    print(json.dumps(c, ensure_ascii=False)[:500])
    print('---')
