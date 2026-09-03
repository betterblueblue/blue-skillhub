# -*- coding: utf-8 -*-
"""照见候选提取器（mirror 的机器部分，只产候选，AI 按 mirror-protocol 筛选定稿）。

SOP 第 3 步的机器部分：把散落在语料/欠账/写回里的"事实落差"粗筛成候选，
写 data/materials_insights.json。LLM 只做筛选 + 话术（见 references/mirror-protocol.md）。

三类候选（只粗筛、宁多勿漏，AI 再筛）：
  say_do     说了没做：open 欠账 >30 天，且之后没再提
  flip       前后说法并排：同一 topic 最早/最新相隔 >30 天（是否矛盾交给 AI）
  word_drift 词频漂移：最近两个有数据的月，本月>=10 且本月/上月>=2 的词

（"反复提没下文"不在这里产——它归 references/distill-report-protocol.md 的 recurs.md，由 AI 读语料自己归纳）

容错：语料不存在/为空 → 打印一句正常退出，不 crash；promises 缺失 → 只跳过对应类型。

输出: data/materials_insights.json —— list[{id, type, fact, evidence:[{date,msg,src}], confidence}]
"""
import json, re, collections, os, datetime, sys

import _common as common
DATA = common.DATA
BS = chr(92)
TODAY = datetime.date.today()
TODAY8 = TODAY.strftime('%Y%m%d')

# ---- 容错：语料不存在/为空 → 正常退出（不 crash，ingest 照常继续）----
_cdp = os.path.join(DATA, 'corpus_dedup.jsonl')
rows, skipped = common.read_jsonl(_cdp)
if not rows:
    print('照见候选跳过（语料不存在、为空或全是坏行），正常退出。')
    sys.exit(0)
if skipped:
    print('警告：语料中有 %d 行坏行已跳过。' % skipped)
rows.sort(key=lambda r: r['date'])

# kw() 过滤再加高频虚词/动作词（单字 + 多字），让 say_do 只留真正的实体词（项目/主题/专有词）
FUNC = set(common.WORDS) | set(['还', '就', '也', '都', '要', '想', '会', '能', '没', '很',
                               '吧', '吗', '呢', '把', '给', '跟', '和', '与', '及', '或',
                               '但', '而', '并', '只', '才', '又', '最', '太', '真', '挺',
                               '有点', '一下', '你', '我', '他', '她', '它', '这', '那',
                               '是', '有', '说', '干', '弄', '整', '来', '去', '到', '在',
                               '上', '下'])

def kw(text):
    """从一句话里抽'实体词'候选：以功能单字为切分界，剩下的连续片段作为关键词。
    中文无空格，不能用 [\\u4e00-\\u9fff]+ 整段抓——那样会把功能字粘进实体词
    （如「把项目C 做完并上线」会被抓成「把项目C」「做完并上线」），later 检查会漏匹配。"""
    seps = ('的了吗呢吧把给跟和与及或但而并只才又最太真挺还有点一下你我这那是说有'
            '干弄整来去到在上下，。！？、；：""''（）()…~·|/\\ ')
    parts = re.split(r'[' + re.escape(seps) + r']+', text)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) >= 2 and p not in FUNC:
            out.append(p)
    if not out:
        flat = re.sub(r'\s+', '', text)
        out = [flat[:6]] if flat else []
    # 去重保序
    return list(dict.fromkeys(out))

# ---- 输入：两层 promises + 写回（都容忍缺失）----
prom_files = {}  # path -> rows
g = os.path.join(DATA, 'promises.jsonl')
proj = os.path.join(os.getcwd(), '.wordmirror', 'promises.jsonl')
for p in [g, proj]:
    if os.path.exists(p):
        plist = []
        for l in open(p, encoding='utf-8'):
            l = l.strip()
            if not l:
                continue
            try:
                plist.append(json.loads(l))
            except Exception:
                continue
        prom_files[p] = plist

wbs = []
_wbp = os.path.join(DATA, 'user_writebacks.jsonl')
if os.path.exists(_wbp):
    for l in open(_wbp, encoding='utf-8'):
        l = l.strip()
        if not l:
            continue
        try:
            wbs.append(json.loads(l))
        except Exception:
            continue

def _promise_tag(p):
    return 'promise:全局' if os.path.normcase(os.path.abspath(p)) == os.path.normcase(os.path.abspath(g)) else 'promise:项目'

cands = []
seq = 0
def emit(type_, fact, evidence, confidence):
    global seq
    seq += 1
    cands.append({'id': 'gap-%s-%d' % (TODAY8, seq), 'type': type_,
                  'fact': fact, 'evidence': evidence, 'confidence': confidence})

# ---- 1. say_do：说了没做 ----
if prom_files:
    for p, plist in prom_files.items():
        tag = _promise_tag(p)
        for o in plist:
            if o.get('status') != 'open':
                continue
            d = o.get('date', '')
            if not d:
                continue
            try:
                age = (TODAY - datetime.date.fromisoformat(d)).days
            except Exception:
                continue
            if age <= 30:
                continue
            text = o.get('text', '')
            if not text:
                continue
            kws = kw(text)
            # 之后（欠账日期之后）是否还有提到这些词的记录（语料 + 写回都算"再提"）
            later = any(r['date'] > d and any(k in r.get('msg', '') for k in kws) for r in rows) \
                or any(w.get('date', '') > d and any(k in w.get('msg', '') for k in kws) for w in wbs)
            if later:
                continue
            emit('say_do', '你 %s 月说要做「%s」，之后没再提。' % (d[:7], text[:40]),
                 [{'date': d, 'msg': text, 'src': tag}], 'high')

# ---- topic 聚合（flip 用）----
by_topic = collections.defaultdict(list)
for r in rows:
    by_topic[common.topic(r)].append(r)

# ---- 3. flip：前后说法并排（不判断是否矛盾，但只在端点消息有转折/否定信号时才产）----
# 窄触发：不窄触发的话，每个正常推进的 topic（≥2 条、跨度 >30 天）都产一条"最早 vs 最新"，
# 绝大多数是噪声（用户只是持续在做），AI 每次筛得累。端点消息里出现转折/否定词才产。
FLIP_MARKERS = ('改主意', '推翻', '反悔', '重新考虑', '撤回', '取消', '放弃', '不要', '算了',
                '不再', '不做了', '别做', '别用', '换成', '改用', '改成', '但是', '不过',
                '其实', '反而', '然而', '变卦')
for t, rs in by_topic.items():
    if t in ('(none)', ''):
        continue
    rs = [r for r in rs if r.get('date')]
    if len(rs) < 2:
        continue
    rs.sort(key=lambda r: r['date'])
    try:
        diff = (datetime.date.fromisoformat(rs[-1]['date']) - datetime.date.fromisoformat(rs[0]['date'])).days
    except Exception:
        continue
    if diff <= 30:
        continue
    first_msg, last_msg = rs[0].get('msg', ''), rs[-1].get('msg', '')
    if not any(m in first_msg or m in last_msg for m in FLIP_MARKERS):
        continue
    emit('flip', '「%s」最早（%s）与最新（%s）的说法并排如下，是否矛盾由你判断。' % (t, rs[0]['date'], rs[-1]['date']),
         [{'date': rs[0]['date'], 'msg': first_msg[:150], 'src': 'corpus'},
          {'date': rs[-1]['date'], 'msg': last_msg[:150], 'src': 'corpus'}], 'mid')

# ---- 4. word_drift：词频漂移 ----
def load_words():
    wf_p = os.path.join(DATA, 'stats_wordfreq.json')
    if os.path.exists(wf_p):
        try:
            wf = json.load(open(wf_p, encoding='utf-8'))
            if isinstance(wf, dict) and wf:
                return list(wf.keys())
        except Exception:
            pass
    return list(common.WORDS)

words = load_words()
month_map = collections.defaultdict(collections.Counter)  # month -> {word: count}
for r in rows:
    if not r.get('date'):
        continue
    m = r['date'][:7]
    msg = r.get('msg', '')
    for w in words:
        c = msg.count(w)
        if c:
            month_map[m][w] += c
months = sorted(month_map)
if len(months) >= 2:
    cur_m, prev_m = months[-1], months[-2]
    for w, cur_n in month_map[cur_m].items():
        if cur_n < 10:
            continue
        prev_n = month_map[prev_m].get(w, 0)
        # 漂移两分支：①上月有词且本月≥上月2倍；②上月 0 次、本月骤增（≥10）——后者信号更强，别漏
        if not ((prev_n > 0 and cur_n / prev_n >= 2) or (prev_n == 0 and cur_n >= 10)):
            continue
        ev = [{'date': r['date'], 'msg': r.get('msg', '')[:100], 'src': 'corpus'}
              for r in rows if r.get('date', '').startswith(cur_m) and w in r.get('msg', '')][:2]
        emit('word_drift', '「%s」这个月 %d 次，上月 %d 次。' % (w, cur_n, prev_n), ev, 'mid')

json.dump(cands, open(os.path.join(DATA, 'materials_insights.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('照见候选:', len(cands), '条')
for c in cands[:10]:
    print('  [%s/%s] %s' % (c['type'], c['confidence'], c['fact']))
