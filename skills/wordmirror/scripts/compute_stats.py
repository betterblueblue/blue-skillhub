# -*- coding: utf-8 -*-
"""数字底座计算器：SOP 第 1 步。
一次出全：信号词频率 / 消息长度 / 分 agent 特征 / 月度主题 / 搁置主题。
产物文档里引用的每个数字都必须能从这里复现。"""
import json, collections, statistics, os, datetime, sys

import _common as common
DATA = common.DATA
TODAY = datetime.date.today().isoformat()

rows, skipped = common.read_jsonl(os.path.join(DATA, 'corpus_dedup.jsonl'))
if skipped:
    print('警告：语料中有 %d 行坏行已跳过。' % skipped)
rows.sort(key=lambda r: r['date'])
BS = chr(92)

if not rows:
    print('语料为空：corpus_dedup.jsonl 里一条话都没有。')
    print('说明各 AI 的存档还没提取出来（或提取后全是空行）——先让 agent 走初始化，')
    print('有存档了再按 references/ingest-protocol.md 提取，否则统计（中位数/最长等）无从算起。')
    sys.exit(1)

print('=' * 60)
print('数字底座 · 生成于 %s · 语料 %d 条' % (TODAY, len(rows)))
print('=' * 60)

# 1. 词频（在语料里数统一词表的出现次数；词表定义在 _common.py）
print('\n[1] 词频（通用词表计数，top 高频）')
freq = {w: sum(m['msg'].count(w) for m in rows) for w in common.WORDS}
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
        # 长消息占比 / 短消息占比 / 提问占比——三个通用维度，不用活人专属词
        'long_per_100': round(100 * sum(1 for m in ms if len(m['msg']) > 200) / len(ms), 1),
        'short_per_100': round(100 * sum(1 for m in ms if len(m['msg']) <= 20) / len(ms), 1),
        'thanks_per_100': round(100 * sum(m['msg'].count('谢谢') for m in ms) / len(ms), 1),
        'question_pct': round(100 * sum(('？' in m['msg'] or '?' in m['msg']) for m in ms) / len(ms), 1),
        'top_projects': collections.Counter(common.topic(m) for m in ms).most_common(3),
    }
    agent_stats[a] = s
    print('  %-13s %5d条 中位%3d字 长%.1f 短%.1f 谢%.1f 问%.0f%%' % (
        a, s['msgs'], s['median_len'], s['long_per_100'], s['short_per_100'], s['thanks_per_100'], s['question_pct']))
json.dump(agent_stats, open(os.path.join(DATA, 'stats_agents.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 4. 月度主题
print('\n[4] 月度主题（top3）')
months = collections.defaultdict(collections.Counter)
for r in rows:
    if r['date']: months[r['date'][:7]][common.topic(r)] += 1
for m in sorted(months):
    print('  %s | %d 条 | %s' % (m, sum(months[m].values()), ', '.join('%s(%d)' % kv for kv in months[m].most_common(3))))

# 5. 搁置主题（30 天+ 未动；只看近半年活跃过的主题，避免远古归档误报搁置）
print('\n[5] 搁置主题（30 天+ 未动）')
last = {}
recent_cutoff = (datetime.date.today() - datetime.timedelta(days=180)).isoformat()
for r in rows:
    if r['date'] < recent_cutoff: continue
    c = common.topic(r)
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
