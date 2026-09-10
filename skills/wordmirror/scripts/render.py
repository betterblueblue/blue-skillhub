# -*- coding: utf-8 -*-
"""言镜生成网页：把 data 里的内容变成 HTML。样式在 ../assets/templates/，数据在数据目录。
用法（v7 起为单页统一展示，锚点导航，无跨页跳转）：
    python render.py read            # 统一单页（hero + 六节：01 你是谁 / 02 那几条线 / 03 说话算数 / 04 你没看见的 / 05 AI 眼里的你 / 06 这几个月）
    python render.py tracker         # 已并入统一页 03 节，只打印提示
    python render.py monthly         # 已废弃：月报并入统一页 06 节，只打印提示
    python render.py all             # = read
不依赖提取脚本（scripts/）——单装用户数据就位后同样能出（数据由 ingest 生成）。
零联网，产物是双击就能打开的单个文件。
"""
import os, sys, re, json, datetime
import html as H

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # 复用数据定位：wm.DATA / wm.PRODUCTS

TPL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'templates')
OUT = os.path.join(wm.PRODUCTS, 'html')
MON = os.path.join(wm.PRODUCTS, 'monthly')
SHELL = open(os.path.join(TPL, 'read_shell.html'), encoding='utf-8').read()


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def render_unified(title, hero, body, rail, footnote=''):
    """v7 组装：单页壳。占位符 __HERO__ / __BODY__ / __RAIL__ / __FOOTNOTE__。"""
    return (SHELL.replace('__TITLE__', H.escape(title))
                 .replace('__HERO__', hero)
                 .replace('__BODY__', body)
                 .replace('__RAIL__', rail)
                 .replace('__FOOTNOTE__', H.escape(footnote)))


def section(sid, eyebrow, title, sub, content):
    """v7 节：眉标 + 节标题 + 一句副题 + 内容。奇偶节灰/白大色块交替（B 方案分区）。
    content 缺失时由调用方给诚实空态。"""
    idx = next(i for i, s in enumerate(SECTIONS) if s[0] == sid)
    tone = 'tone-gray' if idx % 2 == 0 else 'tone-white'
    head = ['<section id="%s" class="sec %s reveal">' % (sid, tone),
            '<div class="sec-eyebrow">%s</div>' % H.escape(eyebrow),
            '<h2>%s</h2>' % inline(title)]
    if sub:
        head.append('<p class="section-lead">%s</p>' % inline(sub))
    head.append(content)
    head.append('</section>')
    return '\n'.join(head)


# 六节的锚点/眉标/标题/副题（统一页导航和右栏索引与此严格对应）
SECTIONS = [
    ('sec-portrait',  '01 · 我是谁',    '你是谁，怎么跟你共事', '先把自己摆上台面：这份索引不是名片，而是此刻的你愿意怎样被记住、被调用。'),
    ('sec-lines',     '02 · 那几条线',  '那几条线，各自走到了哪', '把手上的事一条条摆开：怎么起的、哪里拐的、现在停在哪。状态只有三种，写在标题里。'),
    ('sec-promises',  '03 · 说话算数',  '说过要做的事，后来都去了哪里', '这里不替你打分，只把你亲口说过要做的事放回来，看它们后来停在哪里。'),
    ('sec-insights',  '04 · 你没看见的', '这几件，你可能没看见', '上半是新发现，下半是有证据的反差账，只摆原话和日期，结论你自己下。'),
    ('sec-ai-eyes',   '05 · AI 眼里的你', 'AI 眼里的你', '你在不同工具里的样子，和这些 AI 对你说过的话，都摆在这节。哪里说准了，你自己判断。'),
    ('sec-wrapped',   '06 · 这几个月',  '走过的这几个月，你是怎么过的', '页首是这个月跟上个月的对账，往回一路走到开始的地方。没有给你下结论，只把转向、坚持和停下来的时刻重新摆出来。'),
]


def inline(s):
    s = H.escape(s)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)


# 带日期原话的三种合法写法（口径统一在这里，新增写法只改这张表）：
#   「原话」（YYYY-MM-DD） / 「原话」（YYYY-MM-DD，来源） / - YYYY-MM-DD「原话」 / （「原话」，YYYY-MM-DD）
_QUOTE_PATTERNS = [
    (re.compile(r'「([^」]+)」[（(]\s*(\d{4}-\d{2}-\d{2})(?:\s*，\s*([^」）)]+))?[）)]'),
     lambda m: (m.group(2), m.group(1), (m.group(3) or '').strip())),
    (re.compile(r'[（(]\s*「([^」]+)」\s*，\s*(\d{4}-\d{2}-\d{2})\s*[）)]'),
     lambda m: (m.group(2), m.group(1), '')),
    (re.compile(r'(\d{4}-\d{2}-\d{2})「([^」]+)」'),
     lambda m: (m.group(1), m.group(2), '')),
]


def _extract_quotes(line):
    """一行里抽出带日期的原话，返回 ([(日期, 原话, 来源)...], 剩下的话)。
    没带日期的「引号」不动——那不是能上卡的原话，留在正文里。"""
    quotes = []
    for pat, grab in _QUOTE_PATTERNS:
        line = pat.sub(lambda m: (quotes.append(grab(m)), '')[1], line)
    return quotes, line.strip()


def render_markdown(md):
    """portrait.md 用到的 md 子集：##/###/-/**/表格/引用行。"""
    lines = md.splitlines()
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith('<!--'):
            i += 1
            continue
        if ln.startswith('## '):
            out.append('<h3>%s</h3>' % inline(ln[3:]))
        elif ln.startswith('### '):
            out.append('<h4>%s</h4>' % inline(ln[4:]))
        elif ln.startswith('> ') and not (ln.startswith('> 数据源') or ln.startswith('> 这些结论来自')):
            out.append('<p><strong>%s</strong></p>' % inline(ln[2:]))
        elif ln.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s\-|]+\|$', lines[i + 1]):
            rows = []
            j = i
            while j < len(lines) and lines[j].startswith('|'):
                rows.append([c.strip() for c in lines[j].strip('|').split('|')])
                j += 1
            head, body_rows = rows[0], rows[2:]
            out.append('<table><tr>%s</tr>' % ''.join('<th>%s</th>' % inline(c) for c in head))
            for r in body_rows:
                cells = []
                for k, c in enumerate(r):
                    if k == 0 and re.match(r'\d{4}-\d{2}', c):
                        cells.append('<td class="mono">%s</td>' % H.escape(c))
                    else:
                        cells.append('<td>%s</td>' % inline(c))
                out.append('<tr>%s</tr>' % ''.join(cells))
            out.append('</table>')
            i = j - 1
        elif re.match(r'^\d+\. ', ln):
            out.append('<ol>')
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                out.append('<li>%s</li>' % inline(re.sub(r'^\d+\. ', '', lines[i])))
                i += 1
            out.append('</ol>')
            continue
        elif ln.startswith('- '):
            out.append('<ul>')
            while i < len(lines) and lines[i].startswith('- '):
                out.append('<li>%s</li>' % inline(lines[i][2:]))
                i += 1
            out.append('</ul>')
            continue
        elif re.match(r'^「.+」（\d{4}-\d{2}-\d{2}）$', ln.strip()):
            mq = re.match(r'^「(.+)」（(\d{4}-\d{2}-\d{2})）$', ln.strip())
            out.append('<div class="quote"><span class="q-eyebrow">%s · 你当时这样说</span><span class="q-text">「%s」</span></div>'
                       % (H.escape(mq.group(2)), H.escape(mq.group(1))))
        elif ln.strip():
            out.append('<p>%s</p>' % inline(ln))
        i += 1
    return '\n'.join(out)


def load_insights():
    """读照见定稿 insights.jsonl（每行一条），容忍缺失/坏行。"""
    p = os.path.join(wm.DATA, 'profile', 'insights.jsonl')
    out = []
    if not os.path.exists(p):
        return out
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


INSIGHT_TYPE = {'say_do': '说了没做', 'recur': '反复提没下文', 'flip': '前后矛盾', 'word_drift': '口头禅变化'}
INSIGHT_STATUS = {'active': '还没说', 'confirmed': '你认了', 'dismissed': '你否了'}


def insight_card(o):
    """照见卡：让证据原话成为主角，类型和状态退为辅助。"""
    t = INSIGHT_TYPE.get(o.get('type', ''), o.get('type', '提醒'))
    st = INSIGHT_STATUS.get(o.get('status', 'active'), o.get('status', '还没说'))
    quotes = []
    for e in (o.get('evidence') or [])[:2]:
        if isinstance(e, dict):
            quotes.append('<div class="insight-quote"><div class="date">%s</div><div class="txt">「%s」</div></div>'
                          % (H.escape(str(e.get('date', ''))), H.escape(str(e.get('msg', '')))))
    main = ('<div class="insight-quote-main">%s</div>' % quotes[0]) if quotes else ''
    return ('<article class="insight-card"><div class="insight-type">%s · %s</div>%s'
            '<p class="insight-fact">%s</p>%s</article>'
            % (H.escape(t), H.escape(st), main, H.escape(o.get('fact', '')), ''.join(quotes[1:])))


# ---------- READ 页 ----------

def _portrait_src():
    """画像头部的数字从 stats + 语料实时算，不读画像里手写的旧数字（ingest 重跑会过期）。"""
    ag_p = os.path.join(wm.DATA, 'stats_agents.json')
    if not os.path.exists(ag_p):
        return None
    try:
        ag = load_json(ag_p)
    except Exception:
        return None
    if not ag:
        return None
    total = sum(v.get('msgs', 0) for v in ag.values())
    d0 = d1 = ''
    for o in load_jsonl('corpus_dedup.jsonl'):
        d = o.get('date', '')
        if not d:
            continue
        if not d0 or d < d0:
            d0 = d
        if not d1 or d > d1:
            d1 = d
    tops = sorted(ag.items(), key=lambda kv: -kv[1].get('msgs', 0))[:5]
    parts = ' / '.join('%s %s' % (AGENT_NAMES.get(k, k), v.get('msgs', 0)) for k, v in tops)
    return ('这些结论来自：%s ~ %s，你在 %d 个 AI 工具里说的 %s 条原话（重复的只算一次，%s）'
            % (d0, d1, len(ag), format(total, ','), parts))


def _where_card():
    """01 顶部"你现在站在哪里"：读 current-context.md，把当前主线/阶段/最近决定/最要紧事摆成一张状态卡。"""
    p = os.path.join(wm.DATA, 'profile', 'current-context.md')
    if not os.path.exists(p):
        return ''
    labels = {'当前主线': '在忙什么', '当前阶段': '阶段', '最近明确决定': '最近定下的',
              '当前最要紧的事': '最要紧的', '当前更需要的支持': '现在更需要', '暂时不要': '暂时不做'}
    rows = []
    for line in open(p, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line.startswith('- '):
            continue
        kv = line[2:].split('：', 1)
        if len(kv) != 2:
            continue
        key, val = kv[0].strip(), kv[1].strip()
        if key == '更新于' or not val:
            continue
        rows.append('<div class="where-row"><span class="where-label">%s</span>'
                    '<span class="where-val">%s</span></div>' % (H.escape(labels.get(key, key)), inline(val)))
    if not rows:
        return ''
    return ('<div class="where-card"><div class="where-head">你现在站在哪里</div>'
            + ''.join(rows) + '</div>')


def build_portrait():
    """01 我是谁 → 统一页 sec-portrait 节。"""
    sid, eyebrow, title, sub = SECTIONS[0]
    p = os.path.join(wm.DATA, 'profile', 'portrait.md')
    if not os.path.exists(p):
        print('01 节：你的情况还没整理出来，先生成诚实空态')
        content = '<div class="band"><p>还没初始化——说一句「初始化 wordmirror」，AI 会先探测、提取、再整理出你的情况。</p></div>'
        return section(sid, eyebrow, title, sub, content)
    md = open(p, encoding='utf-8', errors='replace').read()
    ver = re.search(r'# (?:你|我)是谁（(v\d+) · (\d{4}-\d{2}-\d{2})）', md)
    tag, date = (ver.group(1), ver.group(2)) if ver else ('v1', '')
    src = _portrait_src()
    content = ''
    if src:
        content += '<div class="band"><p>%s</p></div>' % inline(src)
    wh = _where_card()
    if wh:
        content += wh
    idx = md.find('## 一句话')
    content += render_markdown(md[idx:] if idx != -1 else md)
    return section(sid, '%s · %s · %s' % (eyebrow, tag, date) if date else '%s · %s' % (eyebrow, tag),
                   title, sub, content)


def _status_badge(title):
    """从线标题里抽状态（·还在走 / ·已经收线 / ·没了下文），拆成小徽章。"""
    m = re.search(r'^(.*?)[·\s]*(还在走|已经收线|没了下文)$', title)
    if not m:
        return title, ''
    cls = {'还在走': 'badge-live', '已经收线': 'badge-done', '没了下文': 'badge-drop'}[m.group(2)]
    return m.group(1).strip(), '<span class="badge %s">%s</span>' % (cls, m.group(2))


def _timeline_section(section):
    """普通阶段渲染：原话是锚点，叙述是回望。"""
    lines = section.splitlines()
    if not lines:
        return ''
    title = lines[0].strip()[4:] if lines[0].startswith('### ') else (lines[0].strip()[3:] if lines[0].startswith('## ') else '')
    title, badge = _status_badge(title)
    text, quotes, hook = [], [], ''
    for line in lines[1:]:
        line = line.strip()
        if not line or line.startswith('<!--'):
            continue
        got, line = _extract_quotes(line)
        quotes.extend((q, d) for d, q, s in got)
        if '现在的问题是' in line:
            hook = line.strip(' -—')
            continue
        line = line.strip(' -—')
        if line:
            text.append(line[2:] if line.startswith('- ') else line)
    out = ['<article class="timeline-chapter">', '<div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s %s</h2></div>' % (inline(title), badge)]
    if quotes:
        quote, date = quotes[0]
        out.append('<div class="quote timeline-quote"><span class="q-eyebrow">%s · 你当时这样说</span><span class="q-text">「%s」</span></div>' % (H.escape(date), H.escape(quote)))
    if text:
        out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in text))
    for quote, date in quotes[1:]:
        out.append('<div class="timeline-echo"><span class="mono">%s</span><span>「%s」</span></div>' % (H.escape(date), H.escape(quote)))
    if hook:
        out.append('<div class="line-hook">%s</div>' % inline(hook))
    out.append('</article>')
    return '\n'.join(out)


def _timeline_special(section, title, kind):
    lines = section.splitlines()[1:]
    quotes, events, prose, hook = [], [], [], ''
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('<!--'):
            continue
        got, line = _extract_quotes(line)
        quotes.extend((d, q) for d, q, s in got)
        if '现在的问题是' in line:
            hook = line.strip(' -—')
            continue
        em = re.match(r'^-\s+(\d{4}-\d{2}-\d{2})\s+(.+)$', line)
        if em:
            events.append(em.groups()); continue
        line = line.strip(' -—')
        if line: prose.append(line[2:] if line.startswith('- ') else line)
    title, badge = _status_badge(title)
    out = ['<article class="timeline-chapter timeline-%s">' % kind, '<div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s %s</h2></div>' % (inline(title), badge)]
    if kind == 'facing' and len(quotes) >= 2:
        if '以前的我' in title or '以前的你' in title:
            labels = ('以前的你', '后来的你')
        elif '以前的想法' in title:
            labels = ('以前的想法', '后来的选择')
        else:
            labels = ('第一句话', '第二句话')
        out.append('<div class="facing-row"><div class="facing-col"><div class="facing-label">%s</div>%s</div><div class="facing-col"><div class="facing-label">%s</div>%s</div></div>' % (labels[0], _quote_markup(*quotes[0]), labels[1], _quote_markup(*quotes[1])))
    elif quotes:
        out.append(_quote_markup(*quotes[0]))
        if kind == 'persistent':
            out.extend('<div class="timeline-echo"><span class="mono">%s</span><span>「%s」</span></div>' % (H.escape(d), H.escape(q)) for d, q in quotes[1:])
        else:
            out.extend(_quote_markup(d, q) for d, q in quotes[1:])
    if events:
        out.append('<div class="follow">%s</div>' % ''.join('<div class="follow-node"><span class="mono">%s</span><span>%s</span></div>' % (H.escape(d), inline(t)) for d, t in events))
    if prose:
        out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in prose))
    if hook:
        out.append('<div class="line-hook">%s</div>' % inline(hook))
    out.append('</article>')
    return '\n'.join(out)


def _quote_markup(date, quote):
    return '<div class="quote timeline-quote"><span class="q-eyebrow">%s · 你当时这样说</span><span class="q-text">「%s」</span></div>' % (H.escape(date), H.escape(quote))


def render_timeline(md):
    """按阶段和白话栏目分派不同的回望版式。"""
    sections = re.split(r'(?=^### )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        if section.startswith('### '):
            title = section.splitlines()[0][4:].strip()
        else:
            title = ''
        kind = None
        if '以前的我' in title or '以前的你' in title or '原来这两句话有关' in title:
            kind = 'facing'
        elif '这句话后来去了哪里' in title:
            kind = 'turning'
        elif '隔了几个月' in title:
            kind = 'persistent'
        elif '这件事后来怎么样了' in title:
            kind = 'setaside'
        elif '现在的我' in title or '现在的你' in title:
            kind = 'now'
        if kind:
            out.append(_timeline_special(section, title, kind))
        elif title:
            out.append(_timeline_section(section))
        else:
            body = '\n'.join(l for l in section.splitlines() if l.strip() and not l.startswith('## '))
            if body.strip():
                out.append('<p class="timeline-note">%s</p>' % inline(body))
    return '\n'.join(out)


def build_wrapped():
    """06 这几个月 → 统一页 sec-wrapped 节。页首本期对账，后面按阶段回看。原话是锚点，脚本只排版。"""
    sid, eyebrow, title, sub = SECTIONS[5]
    p = os.path.join(wm.DATA, 'profile', 'timeline.md')
    if not os.path.exists(p):
        print('06 节：这几个月怎么过的还没整理出来，先生成诚实空态')
        content = '<div class="band"><p>这节的内容还没整理出来——说一句「更新报告」，AI 会按 distill-report-protocol 写好。</p></div>'
        return section(sid, eyebrow, title, sub, content)
    md = open(p, encoding='utf-8', errors='replace').read()
    content = render_timeline(md)
    return section(sid, eyebrow, title, sub, content)


def _note_card():
    """首页"给现在的你"：Agent 蒸馏写 note.md，只一件事、证据带日期、不诊断。"""
    p = os.path.join(wm.DATA, 'profile', 'note.md')
    inner = ''
    if os.path.exists(p):
        md = open(p, encoding='utf-8', errors='replace').read().strip()
        if md:
            inner = render_markdown(md)
    if not inner:
        inner = '<p>这期还没想说的——等你再多聊几句，AI 会把值得停下来看的那一件事放在这里。</p>'
    return ['<div class="note-card"><div class="note-head">给现在的你</div>' + inner + '</div>']


def _unified_stats():
    """hero 大数字带 + 右栏状态，全部来自真实数据，缺就给诚实空态。"""
    ag_p = os.path.join(wm.DATA, 'stats_agents.json')
    ag = {}
    if os.path.exists(ag_p):
        try:
            ag = load_json(ag_p)
        except Exception:
            ag = {}
    total = sum(a.get('msgs', 0) for a in ag.values()) if isinstance(ag, dict) else 0
    n_agents = len(ag) if isinstance(ag, dict) else 0

    promises = _promises_all_layers()
    n_open = sum(1 for o in promises if o.get('status') == 'open')
    n_done = sum(1 for o in promises if o.get('status') == 'closed')

    ins = [o for o in load_insights() if o.get('type') != 'recur']
    n_ins = sum(1 for o in ins if o.get('status') in ('active', None, ''))

    months_p = os.path.join(wm.DATA, 'materials_monthly.json')
    span = ''
    mm = {}
    if os.path.exists(months_p):
        try:
            mm = load_json(months_p)
        except Exception:
            mm = {}
    if mm:
        span = '%s 起' % sorted(mm)[0]

    cells = [
        (format(total, ','), '段', '有效对话'),
        (str(n_agents), '个', 'AI 工具聊过天'),
        ('%d/%d' % (n_done, n_done + n_open) if (n_done + n_open) else '—', '', '承诺已落地'),
        (str(n_ins), '条', '这期想提醒你'),
    ]
    band = ['<div class="stat-band">']
    for v, unit, k in cells:
        band.append('<div class="cell"><div class="v tnum">%s<small>%s</small></div><div class="k">%s</div></div>'
                    % (v, unit, k))
    band.append('</div>')
    return ''.join(band), promises, ins, span


def build_unified():
    """v7 统一单页：hero（大标题 + 大数字带）+ 六节 + 右栏（当前状态 + 节索引）。"""
    stat_band, promises, ins, span = _unified_stats()
    n_open = sum(1 for o in promises if o.get('status') == 'open')
    n_ins = sum(1 for o in ins if o.get('status') in ('active', None, ''))

    hero = ['<h1>回到我说过的话。</h1>',
            '<p class="hero-lede">这是我与 AI 交互的档案。它不是仪表盘，而是一册安静的自我索引：'
            '我是谁，我在忙哪几条线，哪些话说了却没落地，AI 眼里的我，以及这几个月是怎样走到这里的。</p>',
            stat_band]

    main_col = []
    note = _note_card()
    if note:
        main_col.extend(note)
    for builder in (build_portrait, build_lines, build_tracker, build_insights, build_ai_eyes, build_wrapped):
        main_col.append(builder())

    # 右栏：当前状态（真实数据，无则诚实空态）+ 节索引
    items = []
    if n_open:
        items.append(('<span class="mark" aria-hidden="true">○</span><div><div class="t">还没做完的事</div>'
                      '<div class="d">%d 件开着，没下文</div></div>' % n_open))
    if n_ins:
        items.append(('<span class="mark" aria-hidden="true">✓</span><div><div class="t">这期想提醒你的</div>'
                      '<div class="d">%d 条，见 04 节</div></div>' % n_ins))
    if span:
        items.append(('<span class="mark" aria-hidden="true">◷</span><div><div class="t">记录跨度</div>'
                      '<div class="d">%s</div></div>' % H.escape(span)))
    rail = ['<div class="panel"><div class="panel-head">当前状态<span class="live"><i aria-hidden="true"></i>进行中</span></div>']
    if items:
        rail.extend('<div class="status-item">%s</div>' % it for it in items)
    else:
        rail.append('<div class="status-item"><span class="mark" aria-hidden="true">○</span><div><div class="t">还没有数据</div>'
                    '<div class="d">先跑一次 ingest，再回来回望</div></div></div>')
    rail.append('</div>')
    rail.append('<div class="panel"><div class="panel-head">本节索引</div><nav class="rail-nav" aria-label="档案章节">')
    for sid, eyebrow, title, _ in SECTIONS:
        num, _, label = eyebrow.partition(' · ')
        rail.append('<a href="#%s"><span class="no tnum">%s</span>%s</a>' % (sid, H.escape(num), H.escape(label)))
    rail.append('</nav></div>')
    rail.append('<p class="rail-note">言镜 · 私人交互档案<br/>仅存档 · 不外传</p>')

    footnote = '生成于 %s' % datetime.date.today().isoformat()
    return ('html/index.html',
            render_unified('言镜 WordMirror · 私人 AI 交互档案',
                           '\n'.join(hero), '\n'.join(main_col), '\n'.join(rail), footnote))


def build_insights():
    """04 你没看见的 → 统一页 sec-insights 节：新发现（noticed.md）+ 有据反差账（insights.jsonl）。
    没有发现就诚实写没有，不凑数。"""
    sid, eyebrow, title, sub = SECTIONS[3]
    ins = [o for o in load_insights() if o.get('type') != 'recur']
    body = ['<h3>这期读出来的</h3>']
    np = os.path.join(wm.DATA, 'profile', 'noticed.md')
    if os.path.exists(np):
        body.append(render_markdown(open(np, encoding='utf-8', errors='replace').read()))
    else:
        body.append('<div class="band"><p>这期还没找到值得写的新发现——不凑数。每期至少要有一条你读完才知道的事，连续两期没有，就该修找的方法了。</p></div>')
    active = [o for o in ins if o.get('status') in ('active', None, '')]
    body.append('<h3>挂着的事</h3>')
    if not active:
        body.append('<div class="band"><p>现在没有挂着的事。等你说的话多了，这里会摆出你说了没做、前后相反、习惯突变的事。</p></div>')
    else:
        body.append('<div class="insight-grid">' + ''.join(insight_card(o) for o in active) + '</div>')
    rest = [o for o in ins if o not in active]
    if rest:
        body.append('<h3>已经说过的</h3>')
        body.append('<div class="insight-grid">' + ''.join(insight_card(o) for o in rest) + '</div>')
    return section(sid, eyebrow, title, sub, '\n'.join(body))


AGENT_NAMES = {
    'codex': 'Codex',
    'claude-code': 'Claude Code',
    'qwen': 'Qwen',
    'workbuddy': 'WorkBuddy',
    'pi': 'Pi',
    'atomcode': 'AtomCode',
    'antigravity': 'Google Antigravity',
    'zcode': 'zcode',
    'grok': 'Grok',
    'cursor': 'Cursor',
    'catpaw': 'CatPaw',
    'dsh': 'DeepSeek Harness',
}


def _agent_fields(prose):
    """把工具卡说明拆成字段；空字段不占页面。"""
    fields = []
    labels = {'主要干': '主要用来', '怎么跟你说话': '在这里怎么说话', '代表原话': '代表原话', '原话': '代表原话'}
    for text in prose:
        parts = re.split(r'(?=(?:主要干|怎么跟你说话|代表原话|原话)[:：])', text)
        for part in parts:
            part = part.strip(' -—：:')
            if not part:
                continue
            m = re.match(r'^(主要干|怎么跟你说话|代表原话|原话)[:：]\s*(.*)$', part)
            if not m:
                fields.append(('', part))
                continue
            value = m.group(2).strip()
            if not value or value in ('。', '.'):
                continue
            fields.append((labels[m.group(1)], value))
    return fields


def _parse_agent_section(section):
    """解析各工具章节：###/加粗工具头都能分组；空字段不渲染。"""
    lines = section.splitlines()
    title = lines[0][3:].strip() if lines and lines[0].startswith('## ') else ''
    blocks = []

    def new_block():
        b = {'head': '', 'quotes': [], 'prose': []}
        blocks.append(b)
        return b

    cur = None
    for raw in lines[1:]:
        line = raw.strip()
        if not line or line.startswith('<!--'):
            continue
        if line.startswith('### '):
            if line[4:].strip() == '在这里，你是什么样':
                continue
            cur = new_block()
            cur['head'] = line[4:].strip()
            continue
        if line.startswith('**') and line.endswith('**') and line.count('**') >= 2:
            cur = new_block()
            cur['head'] = line[2:-2].strip()
            continue
        if cur is None:
            cur = new_block()
        got, line = _extract_quotes(line)
        cur['quotes'].extend(got)
        line = line.strip(' -—：:')
        if not line or re.fullmatch(r'(?:代表原话|原话|主要干|怎么跟你说话)[:：]?。?', line):
            continue
        if re.match(r'^(?:代表原话|原话)[:：]\s*[。.]?$', line):
            continue
        cur['prose'].append(line[2:] if line.startswith('- ') else line)
    return title, blocks


def _agent_quote(date, quote, source=''):
    return '<div class="quote agent-quote"><span class="q-eyebrow">%s%s</span><span class="q-text">「%s」</span></div>' % (H.escape(date), (' · ' + H.escape(source)) if source else '', H.escape(quote))


def _md_page(name, md_name, sec_index):
    """读 data/profile/<md_name>.md 渲染成统一页的一节。
    判断类内容由 Agent 蒸馏写成 MD（见 references/distill-report-protocol.md），脚本只渲染，不下结论。
    MD 没写好时生成诚实空态节，告诉用户怎么补，不 404、也不拿脚本凑数。"""
    sid, eyebrow, title, sub = SECTIONS[sec_index]
    p = os.path.join(wm.DATA, 'profile', md_name)
    if not os.path.exists(p):
        print('%s：还没整理出来，先生成诚实空态（见 references/distill-report-protocol.md）' % name)
        content = ('<div class="band"><p>这节的内容还没整理出来——要 AI 读完你的聊天记录后写。'
                   '说一句「更新报告」，AI 就会按 references/distill-report-protocol.md 写好这节。</p></div>')
        return section(sid, eyebrow, title, sub, content)
    md = open(p, encoding='utf-8', errors='replace').read()
    return section(sid, eyebrow, title, sub, render_markdown(md))


def build_lines():
    """02 那几条线 → 统一页 sec-lines 节：每条线一节——怎么起的、哪里拐的、现在停在哪。
    状态只有三种（还在走 / 已经收线 / 没了下文），写在小节标题里，不替用户解释。"""
    sid, eyebrow, title, sub = SECTIONS[1]
    p = os.path.join(wm.DATA, 'profile', 'lines.md')
    if not os.path.exists(p):
        return _md_page('02 节', 'lines.md', 1)
    md = open(p, encoding='utf-8', errors='replace').read()
    return section(sid, eyebrow, title, sub, render_lines(md))


def render_lines(md):
    """按线分节渲染；带「- 日期 事件」后续的小节走时间线版式，其余走阶段卡。"""
    sections = re.split(r'(?=^### )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        if section.startswith('### '):
            title = section.splitlines()[0][4:].strip()
            has_events = re.search(r'^-\s+\d{4}-\d{2}-\d{2}\s+', section, flags=re.MULTILINE)
            out.append(_timeline_special(section, title, 'turning') if has_events else _timeline_section(section))
        else:
            body = '\n'.join(l for l in section.splitlines() if l.strip() and not l.startswith('## '))
            if body.strip():
                out.append('<p class="timeline-note">%s</p>' % inline(body))
    return '\n'.join(out)


def _tool_taglines(md):
    """从工具卡头提取 名称 → 一行画像，给排行条加层次。"""
    out = {}
    for raw in md.splitlines():
        line = raw.strip()
        if line.startswith('**') and line.endswith('**'):
            head = line[2:-2].strip()
            name, sep, tag = head.partition('：')
            if sep and name.strip() and tag.strip():
                out[name.strip().lower().replace('-', ' ')] = tag.strip()
    return out


def _tagline_for(taglines, names):
    for cand in names:
        cand = cand.lower().replace('-', ' ')
        if cand in taglines:
            return taglines[cand]
    for key, tag in taglines.items():
        for cand in names:
            cand = cand.lower().replace('-', ' ')
            if cand and (cand in key or key in cand):
                return tag
    return ''


def build_ai_eyes():
    """05 AI 眼里的你 → 统一页 sec-ai-eyes 节：分工具统计 + agent 写的合并观察（工具场景卡 + AI 怎么看你）。"""
    sid, eyebrow, title, sub = SECTIONS[4]
    p = os.path.join(wm.DATA, 'profile', 'ai-eyes.md')
    if not os.path.exists(p):
        return _md_page('05 节', 'ai-eyes.md', 4)
    md = open(p, encoding='utf-8', errors='replace').read()
    body = []

    ag_p = os.path.join(wm.DATA, 'stats_agents.json')
    if os.path.exists(ag_p):
        try:
            ag = load_json(ag_p)
        except Exception:
            ag = {}
        if isinstance(ag, dict) and ag:
            agents = sorted(ag.items(), key=lambda kv: -kv[1].get('msgs', 0))
            total_msgs = sum(v.get('msgs', 0) for v in ag.values())
            total = total_msgs or 1
            top_name = AGENT_NAMES.get(agents[0][0], agents[0][0])
            top_share = round(100 * agents[0][1].get('msgs', 0) / total)
            body.append(
                '<div class="stats build-agents-rank">'
                f'<div class="stat"><div class="n">{len(ag)}</div><div class="note">个 AI 工具，跟你有过来往</div></div>'
                f'<div class="stat"><div class="n">{format(total_msgs, ",")}</div><div class="note">条原话，分布在它们之间</div></div>'
                f'<div class="stat"><div class="n" style="font-size:24px;">{H.escape(top_name)}</div><div class="note">你用得最多的那个</div></div>'
                f'<div class="stat"><div class="n">{top_share}%</div><div class="note">第一名占了这么多</div></div>'
                '</div>')
            body.append('<h3>先从这里看</h3>')
            taglines = _tool_taglines(md)
            for name, v in agents:
                msgs = v.get('msgs', 0)
                pct = round(100 * msgs / total)
                disp = AGENT_NAMES.get(name, name)
                tag = _tagline_for(taglines, (name, disp))
                body.append('<div class="rank-item">')
                body.append(
                    f'<div class="rank-row">'
                    f'<div class="rank-name">{H.escape(disp)}</div>'
                    f'<div class="rank-track"><div class="rank-fill" style="width:{pct}%;"></div></div>'
                    f'<div class="rank-count">{format(msgs, ",")} 条 · {pct}%</div>'
                    f'</div>'
                )
                if tag:
                    body.append('<div class="rank-note">%s</div>' % inline(tag))
                body.append('</div>')

    body.append(render_ai_eyes(md))
    return section(sid, eyebrow, title, sub, '\n'.join(body))


def render_ai_eyes(md):
    """合并版式：工具卡与 AI 观察栏目分开渲染，避免所有内容挤成一张卡。"""
    md = re.sub(r'^### (?=(换了 AI|不同 AI 都看见|AI 这样看你|AI 也看错过|现在，AI 应该))', '## ', md, flags=re.MULTILINE)
    sections = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        title = section.splitlines()[0][3:].strip() if section.startswith('## ') else ''
        if not title:
            continue
        if '\n### ' in section:
            _, blocks = _parse_agent_section(section)
            blocks = [b for b in blocks if b['head'] and (b['quotes'] or b['prose'])]
            out.append('<article class="agent-section agent-agents"><div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s</h2></div>' % inline(title))
            for b in blocks:
                # 卡头拆成两半：工具名做徽章，冒号后面的一句人话做副题
                head = b['head'] or title
                name, _, tagline = head.partition('：')
                label = ('<div class="agent-scene-label"><span class="agent-name">%s</span>'
                         % inline(name.strip()))
                if tagline.strip():
                    label += '<span class="agent-tagline">%s</span>' % inline(tagline.strip())
                label += '</div>'
                fields = _agent_fields(b['prose'])
                if not fields and not b['quotes']:
                    continue
                out.append('<div class="agent-scene">%s' % label)
                for field, value in fields:
                    if field:
                        out.append('<div class="agent-field"><span class="agent-field-label">%s</span><span class="agent-field-value">%s</span></div>' % (inline(field), inline(value)))
                    else:
                        out.append('<div class="agent-field-value agent-field-plain">%s</div>' % inline(value))
                out.extend(_agent_quote(d, q, name.strip()) for d, q, _ in b['quotes'])
                out.append('</div>')
            out.append('</article>')
            continue
        if '换了 AI' in title:
            kind = 'switch'
        elif '不同 AI 都看见' in title:
            kind = 'common'
        elif '看错过' in title:
            kind = 'mistake'
        elif '现在' in title and '认识' in title:
            kind = 'now'
        else:
            kind = 'single'
        if kind == 'switch':
            t, quotes, prose = _parse_ai_section(section)
            out.append('<article class="ai-view-section ai-common"><div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s</h2></div>' % inline(title))
            if len(quotes) >= 2:
                out.append('<div class="facing-row agent-facing"><div class="facing-col"><div class="facing-label">第一种说法</div>%s</div><div class="facing-col"><div class="facing-label">另一种说法</div>%s</div></div>' % (_ai_quote(*quotes[0]), _ai_quote(*quotes[1])))
                quotes = quotes[2:]
            out.extend(_ai_quote(d, q, s) for d, q, s in quotes)
            if prose:
                out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in prose))
            out.append('</article>')
            continue
        out.append(_render_ai_section(section, kind))
    return '\n'.join(out)


def _parse_ai_section(section):
    """解析 AI 观察章节：原标题、带来源引文、普通承接文字。"""
    lines = section.splitlines()
    title = lines[0][3:].strip() if lines and lines[0].startswith('## ') else ''
    quotes, prose = [], []
    for raw in lines[1:]:
        line = raw.strip()
        if not line or line.startswith('<!--'):
            continue
        got, line = _extract_quotes(line)
        quotes.extend(got)
        line = line.strip(' -—：:')
        if line:
            prose.append(line[2:] if line.startswith('- ') else line)
    return title, quotes, prose


def _ai_quote(date, quote, source=''):
    source = source or 'AI 原话'
    return ('<div class="quote ai-quote"><span class="q-eyebrow">%s · %s</span>'
            '<span class="q-text">「%s」</span></div>'
            % (H.escape(date), H.escape(source), H.escape(quote)))


def _render_ai_section(section, kind='single'):
    title, quotes, prose = _parse_ai_section(section)
    cls = 'ai-view-section ai-%s' % kind
    out = ['<article class="%s"><div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s</h2></div>' % (cls, inline(title))]
    if kind in ('common', 'mistake') and len(quotes) >= 2:
        left, right = quotes[0], quotes[1]
        labels = ('AI 这样说', '另一处也这样说') if kind == 'common' else ('AI 当时这样说', '后来需要重新看')
        out.append('<div class="facing-row ai-facing"><div class="facing-col"><div class="facing-label">%s</div>%s</div><div class="facing-col"><div class="facing-label">%s</div>%s</div></div>' % (labels[0], _ai_quote(*left), labels[1], _ai_quote(*right)))
        quotes = quotes[2:]
    else:
        out.extend(_ai_quote(d, q, s) for d, q, s in quotes)
    if prose:
        out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in prose))
    out.append('</article>')
    return '\n'.join(out)


# ---------- 月报 ----------

def load_jsonl(name):
    return load_jsonl_path(os.path.join(wm.DATA, name))


def load_jsonl_path(p):
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _promises_all_layers():
    """两层账本都收：当前目录项目层 + 全局层（月报口径——宣传说"划掉的欠账进月报"，就得两层都算）。"""
    rows = []
    for p in wm._ledger_paths():
        for o in load_jsonl_path(p):
            o = dict(o)
            o['_ledger'] = wm._ledger_tag(p)
            rows.append(o)
    return rows



# ---------- 说过要做的事（03，读两层 promises） ----------

def _promise_card(o, status_label):
    """一件事的回望卡：只展示账本已有字段，不替用户补写后来。"""
    date = o.get('date', '')
    end = o.get('closed_date', '') or date
    try:
        age = max(0, (datetime.date.today() - datetime.date.fromisoformat(date)).days)
    except (TypeError, ValueError):
        age = None
    age_text = '%d 天' % age if age is not None else '日期不明'
    badge_cls = {'open': 'badge-live', 'closed': 'badge-done', 'dropped': 'badge-drop'}.get(o.get('status'), '')
    return ('<article class="promise-card">'
            '<div class="promise-card-head"><span class="mono">%s</span><span class="promise-status badge %s">%s</span></div>'
            '<div class="promise-text">「%s」</div>'
            '<div class="promise-meta">%s · %s%s</div>'
            '</article>'
            % (H.escape(date), H.escape(badge_cls), H.escape(status_label), H.escape(o.get('text', '')),
               H.escape(age_text), H.escape(o.get('_ledger', '')),
               (' · 收线于 %s' % H.escape(end)) if o.get('closed_date') else ''))


def build_tracker():
    """03 说过要做的事 → 统一页 sec-promises 节：把清单改成"后来去了哪里"，不再计算说到做到率。"""
    sid, eyebrow, title, sub = SECTIONS[2]
    rows = _promises_all_layers()
    open_rows = sorted((o for o in rows if o.get('status') == 'open'), key=lambda o: o.get('date', ''))
    done_rows = sorted((o for o in rows if o.get('status') == 'closed'), key=lambda o: o.get('closed_date', '') or o.get('date', ''), reverse=True)
    drop_rows = sorted((o for o in rows if o.get('status') == 'dropped'), key=lambda o: o.get('closed_date', '') or o.get('date', ''), reverse=True)

    body = []
    if open_rows:
        body.append('<h3>还没做完</h3>')
        body.append('<p class="section-lead">账本里还开着的事。它们是"还没做完"，不是自动判定的失败。</p>')
        body.append('<div class="promise-grid">%s</div>' % ''.join(_promise_card(o, '还没做完') for o in open_rows))
    if done_rows:
        body.append('<h3>办完了</h3>')
        body.append('<div class="promise-grid">%s</div>' % ''.join(_promise_card(o, '办完了') for o in done_rows))
    if drop_rows:
        body.append('<h3>已经收线</h3>')
        body.append('<p class="section-lead">只有账本明确记为不做了的，才放在这里。</p>')
        body.append('<div class="promise-grid">%s</div>' % ''.join(_promise_card(o, '已经收线') for o in drop_rows))
    if not rows:
        body.append('<div class="band"><p>还没记过要做的事。你明确说"我要做 X"时，AI 才会把它记下来。</p></div>')
    return section(sid, eyebrow, title, sub, '\n'.join(body))


# ---------- 入口 ----------

def write_out(rel, content):
    p = os.path.join(wm.PRODUCTS, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print('生成 -> products/%s' % rel)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    month = sys.argv[2] if len(sys.argv) > 2 and re.match(r'\d{4}-\d{2}$', sys.argv[2]) else None
    if cmd in ('tracker', 'monthly'):
        # v7：03 并入统一页 sec-promises 节、月报并入 sec-wrapped 节，命令保留只打提示
        print('已并入统一单页（html/index.html）：%s 内容分别见 03 节 / 06 节。直接跑 python render.py all。' % cmd)
        return
    jobs = [build_unified()]
    for j in jobs:
        if j:
            write_out(*j)


if __name__ == '__main__':
    main()
