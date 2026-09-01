# -*- coding: utf-8 -*-
"""数字底座计算器：SOP 第 1 步。
一次出全：信号词频率 / 消息长度 / 分 agent 特征 / 月度主题 / 搁置主题。
产物文档里引用的每个数字都必须能从这里复现。"""
import json, re, collections, statistics, os, datetime

BASE = os.environ.get('WORD_MIRROR_HOME') or os.path.expanduser(os.path.join('~', 'WordMirror'))
DATA = os.path.join(BASE, 'data')
TODAY = datetime.date.today().isoformat()

rows = [json.loads(l) for l in open(os.path.join(DATA, 'corpus_dedup.jsonl'), encoding='utf-8')]
rows.sort(key=lambda r: r['date'])
BS = chr(92)

def topic(r):
    p = r.get('proj') or ''
    return p.split(BS)[-1] if BS in p else (p[:30] if p else '(none)')

print('=' * 60)
print('数字底座 · 生成于 %s · 语料 %d 条' % (TODAY, len(rows)))
print('=' * 60)

# 1. 信号词频率
print('\n[1] 信号词频率')
WORDS = ['bro', 'Bro', '牛逼', '我靠', '我操', '他妈的', '草', '就这样吧', '继续',
         '可以', '好的', '谢谢', '说人话', '熟悉一下', '帮我', '安排', '先不', '算了',
         '先看看', '验证', '看看', '试试', '核对', '全网检索', '评审']
freq = {w: sum(m['msg'].count(w) for m in rows) for w in WORDS}
for w, n in sorted(freq.items(), key=lambda x: -x[1]):
    if n: print('  %5d  %s' % (n, w))
json.dump(freq, open(os.path.join(DATA, 'stats_wordfreq.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 2. 消息长度
print('\n[2] 消息长度分布')
lens = [len(m['msg']) for m in rows]
print('  中位数 %d · 平均 %d · 最长 %d' % (statistics.median(lens), statistics.mean(lens), max(lens)))
print('  <=20字: %d (%.0f%%) · 100-500字: %d (%.0f%%) · >1000字: %d (%.0f%%)' % (
    sum(1 for l in lens if l <= 20), 100 * sum(1 for l in lens if l <= 20) / len(lens),
    sum(1 for l in lens if 100 <= l <= 500), 100 * sum(1 for l in lens if 100 <= l <= 500) / len(lens),
    sum(1 for l in lens if l > 1000), 100 * sum(1 for l in lens if l > 1000) / len(lens)))

# 3. 分 agent 特征
print('\n[3] 分 agent 特征')
by_agent = collections.defaultdict(list)
for r in rows: by_agent[r['agent']].append(r)
agent_stats = {}
for a, ms in sorted(by_agent.items(), key=lambda x: -len(x[1])):
    s = {
        'msgs': len(ms),
        'median_len': statistics.median([len(m['msg']) for m in ms]),
        'bro_per_100': round(100 * sum(m['msg'].lower().count('bro') for m in ms) / len(ms), 1),
        'swear_per_100': round(100 * sum(m['msg'].count(x) for m in ms for x in ['他妈', '我操', '你妈']) / len(ms), 1),
        'thanks_per_100': round(100 * sum(m['msg'].count('谢谢') for m in ms) / len(ms), 1),
        'question_pct': round(100 * sum(('？' in m['msg'] or '?' in m['msg']) for m in ms) / len(ms), 1),
        'top_projects': collections.Counter(topic(m) for m in ms).most_common(3),
    }
    agent_stats[a] = s
    print('  %-13s %5d条 中位%3d字 bro%.1f 脏%.1f 谢%.1f 问%.0f%%' % (
        a, s['msgs'], s['median_len'], s['bro_per_100'], s['swear_per_100'], s['thanks_per_100'], s['question_pct']))
json.dump(agent_stats, open(os.path.join(DATA, 'stats_agents.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 4. 月度主题
print('\n[4] 月度主题（top3）')
months = collections.defaultdict(collections.Counter)
for r in rows:
    if r['date']: months[r['date'][:7]][topic(r)] += 1
for m in sorted(months):
    print('  %s | %d 条 | %s' % (m, sum(months[m].values()), ', '.join('%s(%d)' % kv for kv in months[m].most_common(3))))

# 5. 搁置主题（6/1 后最后活跃）
print('\n[5] 搁置主题（30 天+ 未动）')
last = {}
for r in rows:
    if r['date'] < '2026-06-01': continue
    c = topic(r)
    if c not in last or r['date'] > last[c]: last[c] = r['date']
stalled = []
for c, d in last.items():
    gap = (datetime.date.fromisoformat(TODAY) - datetime.date.fromisoformat(d)).days
    stalled.append({'gap': gap, 'topic': c, 'last': d})
stalled.sort(key=lambda x: -x['gap'])
for s in stalled[:20]:
    if s['gap'] >= 30: print('  %3d 天 | %s | 最后 %s' % (s['gap'], s['topic'], s['last']))
json.dump(stalled, open(os.path.join(DATA, 'stalled_topics.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('\n输出: stats_wordfreq.json / stats_agents.json / stalled_topics.json → data/')
