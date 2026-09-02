# -*- coding: utf-8 -*-
"""数字底座计算器：SOP 第 1 步。
一次出全：信号词频率 / 消息长度 / 分 agent 特征 / 月度主题 / 搁置主题。
产物文档里引用的每个数字都必须能从这里复现。"""
import json, re, collections, statistics, os, datetime, sys

BASE = os.environ.get('WORD_MIRROR_HOME') or os.path.expanduser(os.path.join('~', '.wordmirror'))
DATA = os.path.join(BASE, 'data')
TODAY = datetime.date.today().isoformat()

rows = [json.loads(l) for l in open(os.path.join(DATA, 'corpus_dedup.jsonl'), encoding='utf-8')]
rows.sort(key=lambda r: r['date'])
BS = chr(92)

if not rows:
    print('语料为空：corpus_dedup.jsonl 里一条话都没有。')
    print('说明各 AI 的存档还没提取出来（或提取后全是空行）——先让 agent 走初始化，')
    print('有存档了再跑 wm.py ingest，否则统计（中位数/最长等）无从算起。')
    sys.exit(1)

def topic(r):
    p = (r.get('proj') or '').replace('\\', '/')
    seg = p.rstrip('/').split('/')[-1] if p else ''
    seg = seg.strip('-').replace('--', ' ').strip()
    # 纯十六进制哈希（如 antigravity 的 cid 前 8 位）不是主题
    if seg and re.fullmatch(r'[0-9a-fA-F]{6,40}', seg):
        return '(none)'
    return seg[:30] if seg else '(none)'

print('=' * 60)
print('数字底座 · 生成于 %s · 语料 %d 条' % (TODAY, len(rows)))
print('=' * 60)

# 1. 词频（在语料里数这些通用高频词的出现次数——词表通用，任何用户的常见词都能被数到）
print('\n[1] 词频（通用词表计数，top 高频）')
# 诚实边界：这是「通用高频词计数」（浅层），不是个性化口头禅识别——
# 词表里是"这个/那个/可以/应该"这类人人都在用的功能词，抓不到用户独有的口头禅。
# 真要做口头禅得走 n-gram 频率/分词统计（更重），当前取舍是：够用、零额外依赖、接口稳定。
# 想数更多词，往 WORDS 里加即可——方法是在每条消息里数出现次数（中文无需分词）。
WORDS = ['这个', '那个', '这样', '那样', '可以', '应该', '需要', '觉得', '认为', '可能',
         '看看', '试试', '试试看', '先', '再', '然后', '但是', '所以', '因为', '如果',
         '我们', '你们', '他们', '自己', '什么', '怎么', '为什么', '哪里', '多少',
         '继续', '完成', '搞定', '做完', '算了', '不做了', '放弃', '定了', '决定',
         '写', '改', '做', '用', '建', '删', '加', '提', '记', '查', '翻', '试',
         '代码', '项目', '方案', '数据库', '接口', '前端', '后端', '部署', '发布', '上线',
         '谢谢', '好的', '明白', '清楚了', '麻烦', '帮忙', '帮我', '安排',
         '问题', '报错', '错了', '不对', '还原', '从头', '重新', '重试', '等一下',
         '月报', '周报', '总结', '复盘', 'TODO', 'OK', '版本',
         '是的', '嗯', '对', '好', '行', '了解', '同步', '确认', '理解']
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
        # 长消息占比 / 短消息占比 / 提问占比——三个通用维度，不用活人专属词
        'long_per_100': round(100 * sum(1 for m in ms if len(m['msg']) > 200) / len(ms), 1),
        'short_per_100': round(100 * sum(1 for m in ms if len(m['msg']) <= 20) / len(ms), 1),
        'thanks_per_100': round(100 * sum(m['msg'].count('谢谢') for m in ms) / len(ms), 1),
        'question_pct': round(100 * sum(('？' in m['msg'] or '?' in m['msg']) for m in ms) / len(ms), 1),
        'top_projects': collections.Counter(topic(m) for m in ms).most_common(3),
    }
    agent_stats[a] = s
    print('  %-13s %5d条 中位%3d字 长%.1f 短%.1f 谢%.1f 问%.0f%%' % (
        a, s['msgs'], s['median_len'], s['long_per_100'], s['short_per_100'], s['thanks_per_100'], s['question_pct']))
json.dump(agent_stats, open(os.path.join(DATA, 'stats_agents.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 4. 月度主题
print('\n[4] 月度主题（top3）')
months = collections.defaultdict(collections.Counter)
for r in rows:
    if r['date']: months[r['date'][:7]][topic(r)] += 1
for m in sorted(months):
    print('  %s | %d 条 | %s' % (m, sum(months[m].values()), ', '.join('%s(%d)' % kv for kv in months[m].most_common(3))))

# 5. 搁置主题（30 天+ 未动；只看近半年活跃过的主题，避免远古归档误报搁置）
print('\n[5] 搁置主题（30 天+ 未动）')
last = {}
recent_cutoff = (datetime.date.today() - datetime.timedelta(days=180)).isoformat()
for r in rows:
    if r['date'] < recent_cutoff: continue
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
