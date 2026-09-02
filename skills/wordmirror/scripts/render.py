# -*- coding: utf-8 -*-
"""言镜生成网页：把 data 里的内容变成 HTML。样式在 ../assets/templates/，数据在数据目录。
用法：
    python render.py read            # 首页 + 01 你的情况 + 10 翻给你看
    python render.py monthly [YYYY-MM]  # 月报（默认最近有数据的月份）
    python render.py tracker         # 03 说过要做的事
    python render.py all             # 全部
不依赖提取脚本（scripts/）——单装用户数据就位后同样能出（数据由 ingest 生成）。
零联网，产物是双击就能打开的单个文件。
"""
import os, sys, re, json, datetime, base64
import html as H

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # 复用数据定位：wm.DATA / wm.PRODUCTS

TPL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'templates')
OUT = os.path.join(wm.PRODUCTS, 'html')
MON = os.path.join(wm.PRODUCTS, 'monthly')
SHELL = open(os.path.join(TPL, 'read_shell.html'), encoding='utf-8').read()


def _hero_img_css():
    """hero 背景画：assets/templates/hero-dawn.jpg 存在就内嵌成 base64（产物仍是零外联单文件）。
    没有画就返回 none，模板里的纯 CSS 晨景渐变兑底。"""
    p = os.path.join(TPL, 'hero-dawn.jpg')
    if not os.path.exists(p):
        return 'none'
    with open(p, 'rb') as f:
        b = base64.b64encode(f.read()).decode('ascii')
    return 'url("data:image/jpeg;base64,%s")' % b


HERO_IMG = _hero_img_css()


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def page(title, eyebrow, body, home='index.html'):
    """组装页面：开场的大标题和折射线自动进夜幕 hero，其余落回纸白阅读带。"""
    m = re.match(r'^(.*?</h1>)(\s*<div class="refract"></div>)?(.*)$', body, re.S)
    if m:
        hero, rest = m.group(1) + (m.group(2) or ''), m.group(3)
    else:
        hero, rest = '', body
    return (SHELL.replace('__TITLE__', H.escape(title))
                 .replace('__HOME__', home)
                 .replace('__EYEBROW__', eyebrow)
                 .replace('__HERO_IMG__', HERO_IMG)
                 .replace('__HERO__', hero)
                 .replace('__BODY__', rest))


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
            out.append('<h2>%s</h2>' % inline(ln[3:]))
        elif ln.startswith('### '):
            out.append('<h3>%s</h3>' % inline(ln[4:]))
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


def build_portrait():
    p = os.path.join(wm.DATA, 'profile', 'portrait.md')
    if not os.path.exists(p):
        print('01 那页：你的情况还没整理出来，先生成空态页')
        body = ['<h1 class="display">我是谁，<br>怎么跟我共事</h1>',
                '<div class="refract"></div>',
                '<div class="band"><p>还没初始化——说一句「初始化 wordmirror」，AI 会先探测、提取、再整理出你的情况。</p></div>']
        return ('html/01_我是谁.html',
                page('我是谁 · 言镜', '说明书', '\n'.join(body)))
    md = open(p, encoding='utf-8', errors='replace').read()
    ver = re.search(r'# 我是谁（(v\d+) · (\d{4}-\d{2}-\d{2})）', md)
    tag, date = (ver.group(1), ver.group(2)) if ver else ('v1', '')
    body = ['<h1 class="display">我是谁，<br>怎么跟我共事</h1>']
    src = _portrait_src()
    if src:
        body.append('<div class="band"><p>%s</p></div>' % inline(src))
    idx = md.find('## 一句话')
    body.append(render_markdown(md[idx:] if idx != -1 else md))
    return ('html/01_我是谁.html',
            page('我是谁 · 言镜', '说明书 %s <span class="dot">·</span> %s' % (tag, date), '\n'.join(body)))


def _timeline_section(section):
    """普通阶段渲染：原话是锚点，叙述是回望。"""
    lines = section.splitlines()
    if not lines:
        return ''
    title = lines[0].strip()[3:] if lines[0].startswith('## ') else ''
    text, quotes = [], []
    for line in lines[1:]:
        line = line.strip()
        if not line or line.startswith('<!--'):
            continue
        got, line = _extract_quotes(line)
        quotes.extend((q, d) for d, q, s in got)
        line = line.strip(' -—')
        if line:
            text.append(line[2:] if line.startswith('- ') else line)
    out = ['<article class="timeline-chapter">', '<div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s</h2></div>' % inline(title)]
    if quotes:
        quote, date = quotes[0]
        out.append('<div class="quote timeline-quote"><span class="q-eyebrow">%s · 你当时这样说</span><span class="q-text">「%s」</span></div>' % (H.escape(date), H.escape(quote)))
    if text:
        out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in text))
    for quote, date in quotes[1:]:
        out.append('<div class="timeline-echo"><span class="mono">%s</span><span>「%s」</span></div>' % (H.escape(date), H.escape(quote)))
    out.append('</article>')
    return '\n'.join(out)


def _timeline_special(section, title, kind):
    lines = section.splitlines()[1:]
    quotes, events, prose = [], [], []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('<!--'):
            continue
        got, line = _extract_quotes(line)
        quotes.extend((d, q) for d, q, s in got)
        em = re.match(r'^-\s+(\d{4}-\d{2}-\d{2})\s+(.+)$', line)
        if em:
            events.append(em.groups()); continue
        line = line.strip(' -—')
        if line: prose.append(line[2:] if line.startswith('- ') else line)
    out = ['<article class="timeline-chapter timeline-%s">' % kind, '<div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s</h2></div>' % inline(title)]
    if kind == 'facing' and len(quotes) >= 2:
        if '以前的我' in title:
            labels = ('以前的我', '后来的我')
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
    out.append('</article>')
    return '\n'.join(out)


def _quote_markup(date, quote):
    return '<div class="quote timeline-quote"><span class="q-eyebrow">%s · 你当时这样说</span><span class="q-text">「%s」</span></div>' % (H.escape(date), H.escape(quote))


def render_timeline(md):
    """按阶段和白话栏目分派不同的回望版式。"""
    sections = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        title = section.splitlines()[0][3:].strip() if section.startswith('## ') else ''
        kind = None
        if '以前的我' in title or '原来这两句话有关' in title:
            kind = 'facing'
        elif '这句话后来去了哪里' in title:
            kind = 'turning'
        elif '隔了几个月' in title:
            kind = 'persistent'
        elif '这件事后来怎么样了' in title:
            kind = 'setaside'
        elif '现在的我' in title:
            kind = 'now'
        out.append(_timeline_special(section, title, kind) if kind else _timeline_section(section))
    return '\n'.join(out)


def build_wrapped():
    """09 走过的这几个月：以带日期的原话为锚点，按阶段渲染成回望卡。"""
    p = os.path.join(wm.DATA, 'profile', 'timeline.md')
    if not os.path.exists(p):
        print('09 那页：这几个月怎么过的还没整理出来，先生成空态页')
        body = ['<h1 class="display">走过的这几个月，<br>我是怎么过的</h1>',
                '<div class="refract"></div>',
                '<div class="band"><p>这页的内容还没整理出来——说一句「更新报告」，AI 会按 distill-report-protocol 写好。</p></div>']
        return ('html/09_走过的这几个月.html',
                page('走过的这几个月 · 言镜', '按时间回看', '\n'.join(body)))
    md = open(p, encoding='utf-8', errors='replace').read()
    body = ['<h1 class="display">走过的这几个月，<br>我是怎么过的</h1>',
            '<div class="refract"></div>',
            '<p class="timeline-intro">把当时说过的话，放回当时的时间里。这里没有给你下结论，只把那些转向、坚持和停下来的时刻重新摆出来。</p>',
            render_timeline(md)]
    return ('html/09_走过的这几个月.html',
            page('走过的这几个月 · 言镜', '按时间回看', '\n'.join(body)))


def build_index():
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

    ins = [o for o in load_insights() if o.get('type') != 'recur']
    n_ins = len(ins)

    body = ['<h1 class="display">以言为镜，<br><span class="accent">可以知自己</span></h1>',
            '<div class="refract"></div>',
            '<p style="color:var(--muted);max-width:560px;">你跟好几个 AI 说过的话，都在这儿了。'
            '欠着没做的、反复提又放下的、前后改口的——一眼看清。</p>']

    body.append('<div class="stats">'
                '<div class="stat"><div class="n">%s</div><div class="note">条原话，都是你说给 AI 的</div></div>'
                '<div class="stat"><div class="n">%d</div><div class="note">个 AI 工具，跟你聊过天</div></div>'
                '<div class="stat"><div class="n">%d</div><div class="note">件欠着的事，一直没下文</div></div>'
                '<div class="stat"><div class="n">%d</div><div class="note">件事，今天想提醒你</div></div>'
                '</div>' % (format(total, ','), n_agents, n_open, n_ins))

    body.append('<h2>今天想提醒你的几件事</h2>')
    active = [o for o in ins if o.get('status') in ('active', None, '')][:3]
    if active:
        body.append('<div class="insight-grid">' + ''.join(insight_card(o) for o in active) + '</div>')
    else:
        body.append('<div class="band"><p>现在还没什么要提醒你的。等你说的话多了，这里会挑出你说了没做、前后矛盾的事。</p></div>')

    body.append('<h2>这个月的你</h2>')
    mm = {}
    months_p = os.path.join(wm.DATA, 'materials_monthly.json')
    if os.path.exists(months_p):
        try:
            mm = load_json(months_p)
        except Exception:
            mm = {}
    if mm:
        latest = sorted(mm)[-1]
        m = mm[latest]
        topics = ''.join('<span class="pill">%s</span>' % H.escape(t) for t, _ in m.get('top_topics', [])[:3])
        body.append('<div class="band"><p><strong>%s</strong> 你说了 <strong>%s</strong> 条话，主要在忙：%s</p></div>'
                    % (H.escape(latest), format(m.get('n', 0), ','), topics or '（还没什么主题）'))
    else:
        body.append('<div class="band"><p>这个月的数据还没出来，先跑 ingest。</p></div>')

    body.append('<h2>翻开更多</h2>')
    cards = [
        ('01', '我是谁', '我的情况、当前在忙什么、怎么跟我配合', '01_我是谁.html'),
        ('02', '我做过的重要决定', '那些决定后来去了哪里', '02_我做过的重要决定.html'),
        ('03', '说过要做的事', '这些事后来各自怎么样了', '03_说过要做的事.html'),
        ('04', '该注意的事', '有哪些你自己还没注意到的事', '04_该注意的事.html'),
        ('05', '我反复提的事', '你是不是一直在问同一个问题', '05_我反复提的事.html'),
        ('06', '我在各个 AI 里的样子', '换了工具，我是不是换了说法', '06_我在各个AI里的样子.html'),
        ('07', '我总让 AI 干什么', '我把什么活交给了 AI', '07_我总让AI干什么.html'),
        ('08', 'AI 怎么看我', '不同 AI 是怎样认识我的', '08_AI怎么看我.html'),
        ('09', '走过的这几个月', '这几个月我是怎么走过来的', '09_走过的这几个月.html'),
    ]
    body.append('<div class="card-grid">')
    for num, title, desc, href in cards:
        body.append('<a class="nav-card" href="%s"><div class="idx">%s</div><h3>%s</h3><p>%s</p></a>'
                    % (href, H.escape(num), H.escape(title), H.escape(desc)))
    body.append('</div>')

    return ('html/index.html',
            page('言镜 · 首页', '今日镜面', '\n'.join(body), home='index.html'))


def build_insights():
    ins = [o for o in load_insights() if o.get('type') != 'recur']
    body = ['<h1 class="display">这几件，<br>你可能没注意到</h1>',
            '<div class="refract"></div>',
            '<p class="timeline-intro">这里都是你有证据、但未必注意到的反差。只摆你的原话和日期，结论你自己下。</p>']
    active = [o for o in ins if o.get('status') in ('active', None, '')]
    if not active:
        body.append('<div class="band"><p>现在还没什么要提醒你的。等你说的话多了，这里会挑出你说了没做、前后矛盾的事。</p></div>')
    else:
        body.append('<h2>还没跟你说的</h2>')
        body.append('<div class="insight-grid">' + ''.join(insight_card(o) for o in active) + '</div>')
        rest = [o for o in ins if o not in active]
        if rest:
            body.append('<h2>已经说过的</h2>')
            body.append('<div class="insight-grid">' + ''.join(insight_card(o) for o in rest) + '</div>')
    return ('html/04_该注意的事.html',
            page('该注意的事 · 言镜', '该注意的事', '\n'.join(body)))


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


def _parse_agent_section(section):
    """解析各工具章节：## 大标题 + ### 子标题分组；子块内收集引文和承接文字。"""
    lines = section.splitlines()
    title = lines[0][3:].strip() if lines and lines[0].startswith('## ') else ''
    blocks = []

    def new_block():
        b = {'head': '', 'quotes': [], 'prose': []}
        blocks.append(b)
        return b

    cur = new_block()
    for raw in lines[1:]:
        line = raw.strip()
        if not line or line.startswith('<!--'):
            continue
        if line.startswith('### '):
            cur = new_block()
            cur['head'] = line[4:].strip()
            continue
        got, line = _extract_quotes(line)
        cur['quotes'].extend(got)
        line = line.strip(' -—：:')
        if line:
            cur['prose'].append(line[2:] if line.startswith('- ') else line)
    return title, blocks


def _agent_quote(date, quote, source=''):
    return '<div class="quote agent-quote"><span class="q-eyebrow">%s%s</span><span class="q-text">「%s」</span></div>' % (H.escape(date), (' · ' + H.escape(source)) if source else '', H.escape(quote))


def render_agents(md):
    """把各工具的统计说明排成“不同场景里的自己”，兼容旧版 agents.md。"""
    sections = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        title, blocks = _parse_agent_section(section)
        blocks = [b for b in blocks if b['head'] or b['quotes'] or b['prose']]
        if not title:
            continue
        if '换了 AI' in title:
            current = 'facing'
        elif '哪些东西一直' in title:
            current = 'shared'
        elif '现在回头看' in title:
            current = 'now'
        elif '在这里' in title:
            current = 'agents'
        else:
            current = 'legacy'
        cls = 'agent-section agent-%s' % current
        out.append('<article class="%s"><div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s</h2></div>' % (cls, inline(title)))
        all_quotes = [q for b in blocks for q in b['quotes']]
        if current == 'facing' and len(all_quotes) >= 2:
            out.append('<div class="facing-row agent-facing"><div class="facing-col"><div class="facing-label">第一种说法</div>%s</div><div class="facing-col"><div class="facing-label">另一种说法</div>%s</div></div>' % (_agent_quote(*all_quotes[0]), _agent_quote(*all_quotes[1])))
        elif current == 'agents':
            # 每个 AI 一张场景卡：### 子标题做卡头，承接文字 + 原话都收进卡里
            for b in blocks:
                out.append('<div class="agent-scene"><div class="agent-scene-label">%s</div>' % inline(b['head'] or title))
                if b['prose']:
                    out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in b['prose']))
                out.extend(_agent_quote(*q) for q in b['quotes'])
                out.append('</div>')
        else:
            for b in blocks:
                if b['head']:
                    out.append('<div class="agent-scene-label">%s</div>' % inline(b['head']))
                out.extend(_agent_quote(*q) for q in b['quotes'])
                if b['prose']:
                    out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in b['prose']))
        out.append('</article>')
    return '\n'.join(out)


def build_agents():
    ag_p = os.path.join(wm.DATA, 'stats_agents.json')
    if not os.path.exists(ag_p):
        print('跳过 06 那页：统计素材还没生成（先跑 ingest）')
        return None
    ag = load_json(ag_p)
    if not ag:
        print('跳过 06 那页：没有分 agent 数据')
        return None

    agents = sorted(ag.items(), key=lambda kv: -kv[1].get('msgs', 0))
    total_msgs = sum(v.get('msgs', 0) for v in ag.values())
    total = total_msgs or 1
    top_name = AGENT_NAMES.get(agents[0][0], agents[0][0]) if agents else '—'
    top_share = round(100 * agents[0][1].get('msgs', 0) / total) if agents else 0

    body = ['<h1 class="display">我在各个 AI 里的样子</h1>',
            '<div class="refract"></div>',
            '<p style="color:var(--muted);max-width:560px;">你在不同工具里说的话、干的事、说话习惯，都不一样。这页把它们并排摆出来。</p>']

    body.append(
        '<div class="stats build-agents-rank">'
        f'<div class="stat"><div class="n">{len(ag)}</div><div class="note">个 AI 工具，跟你有过来往</div></div>'
        f'<div class="stat"><div class="n">{format(total_msgs, ",")}</div><div class="note">条原话，分布在它们之间</div></div>'
        f'<div class="stat"><div class="n" style="font-size:24px;">{H.escape(top_name)}</div><div class="note">你用得最多的那个</div></div>'
        f'<div class="stat"><div class="n">{top_share}%</div><div class="note">第一名占了这么多</div></div>'
        '</div>'
    )

    body.append('<h2>先从这里看</h2>')
    for name, v in agents:
        msgs = v.get('msgs', 0)
        pct = round(100 * msgs / total)
        disp = AGENT_NAMES.get(name, name)
        body.append(
            f'<div class="rank-row">'
            f'<div class="rank-name">{H.escape(disp)}</div>'
            f'<div class="rank-track"><div class="rank-fill" style="width:{pct}%;"></div></div>'
            f'<div class="rank-count">{format(msgs, ",")} 条 · {pct}%</div>'
            f'</div>'
        )

    # 判断部分：不同工具里的样子由 Agent 读语料写 agents.md，脚本只负责排版
    md_path = os.path.join(wm.DATA, 'profile', 'agents.md')
    if os.path.exists(md_path):
        body.append(render_agents(open(md_path, encoding='utf-8', errors='replace').read()))
    else:
        body.append('<div class="band"><p>每个 AI 里你主要干啥、怎么跟它说话，还没整理出来——'
                    '说一句「更新报告」，AI 会按 distill-report-protocol 写好。</p></div>')

    return ('html/06_我在各个AI里的样子.html',
            page('我在各个 AI 里的样子 · 言镜', '按工具看', '\n'.join(body)))


def _md_page(name, md_name, title, eyebrow, filename):
    """读 data/profile/<md_name>.md 渲染成页。
    判断类内容由 Agent 蒸馏写成 MD（见 references/distill-report-protocol.md），脚本只渲染，不下结论。
    MD 没写好时生成一个空态页，告诉用户怎么补，不 404、也不拿脚本凑数。"""
    p = os.path.join(wm.DATA, 'profile', md_name)
    if not os.path.exists(p):
        print('%s：还没整理出来，先生成空态页（见 references/distill-report-protocol.md）' % name)
        body = ['<h1 class="display">%s</h1>' % title,
                '<div class="refract"></div>',
                '<div class="band"><p>这页的内容还没整理出来——要 AI 读完你的聊天记录后写。'
                '说一句「更新报告」，AI 就会按 references/distill-report-protocol.md 写好这页。</p></div>']
        return (filename, page(title + ' · 言镜', eyebrow, '\n'.join(body)))
    md = open(p, encoding='utf-8', errors='replace').read()
    body = ['<h1 class="display">%s</h1>' % title,
            '<div class="refract"></div>',
            render_markdown(md)]
    return (filename, page(title + ' · 言镜', eyebrow, '\n'.join(body)))


def build_decisions():
    p = os.path.join(wm.DATA, 'profile', 'decisions.md')
    if not os.path.exists(p):
        return _md_page('02 那页', 'decisions.md', '我做过的重要决定', '决定', 'html/02_我做过的重要决定.html')
    md = open(p, encoding='utf-8', errors='replace').read()
    body = ['<h1 class="display">我做过的重要决定</h1>',
            '<div class="refract"></div>',
            '<p class="timeline-intro">那些当时说出口的决定，后来把我带到了哪里。</p>',
            render_decisions(md)]
    return ('html/02_我做过的重要决定.html',
            page('我做过的重要决定 · 言镜', '决定', '\n'.join(body)))


def render_decisions(md):
    """决定页复用时间线版式：普通主题保留，白话栏目展示决定的后续关系。"""
    sections = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        title = section.splitlines()[0][3:].strip() if section.startswith('## ') else ''
        if not title:
            continue
        if '这句话后来去了哪里' in title:
            out.append(_timeline_special(section, title, 'turning'))
        elif '以前的想法' in title or '后来的选择' in title:
            out.append(_timeline_special(section, title, 'facing'))
        elif '还没有答案' in title:
            out.append(_timeline_special(section, title, 'setaside'))
        else:
            out.append(_timeline_section(section))
    return '\n'.join(out)


def build_recurring():
    p = os.path.join(wm.DATA, 'profile', 'recurs.md')
    if not os.path.exists(p):
        return _md_page('05 那页', 'recurs.md', '我反复提的事', '反复提的事', 'html/05_我反复提的事.html')
    md = open(p, encoding='utf-8', errors='replace').read()
    body = ['<h1 class="display">我反复提的事，<br>是不是在问同一个问题</h1>',
            '<div class="refract"></div>',
            '<p class="timeline-intro">有些话题换了名字、换了项目，过一阵还是会回来。这里不替你解释原因，只把它们放在一起。</p>',
            render_recurring(md)]
    return ('html/05_我反复提的事.html',
            page('我反复提的事 · 言镜', '反复提的事', '\n'.join(body)))


def render_recurring(md):
    """按白话标题渲染反复主题；旧主题章节继续使用阶段回望版式。"""
    sections = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        title = section.splitlines()[0][3:].strip() if section.startswith('## ') else ''
        if not title:
            continue
        if '这几句话' in title:
            kind = 'facing'
        elif '一直回来' in title:
            kind = 'persistent'
        elif '没有走完' in title:
            kind = 'setaside'
        elif '转去了别处' in title:
            kind = 'turning'
        else:
            kind = None
        out.append(_timeline_special(section, title, kind) if kind else _timeline_section(section))
    return '\n'.join(out)


def build_tasks():
    p = os.path.join(wm.DATA, 'profile', 'tasks.md')
    if not os.path.exists(p):
        return _md_page('07 那页', 'tasks.md', '我总让 AI 干什么', '按任务看', 'html/07_我总让AI干什么.html')
    md = open(p, encoding='utf-8', errors='replace').read()
    body = ['<h1 class="display">我总让 AI 干什么</h1>',
            '<div class="refract"></div>',
            '<p class="timeline-intro">你把哪些活交给了 AI，自己又一直抓着哪些部分？</p>',
            render_tasks(md)]
    return ('html/07_我总让AI干什么.html',
            page('我总让 AI 干什么 · 言镜', '按任务看', '\n'.join(body)))


def render_tasks(md):
    """把任务分类从占比列表改成具体工作的回望卡。"""
    sections = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        title = section.splitlines()[0][3:].strip() if section.startswith('## ') else ''
        if not title:
            continue
        lines = section.splitlines()[1:]
        quotes, prose = [], []
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith('<!--'):
                continue
            got, line = _extract_quotes(line)
            quotes.extend(got)
            line = line.strip(' -—：:')
            if line:
                prose.append(line[2:] if line.startswith('- ') else line)
        out.append('<article class="task-section"><div class="timeline-chapter-head"><span class="timeline-kicker"></span><h2>%s</h2></div>' % inline(title))
        if quotes:
            out.append('<div class="task-quotes">%s</div>' % ''.join(_agent_quote(d, q, s) for d, q, s in quotes))
        if prose:
            out.append('<div class="timeline-note">%s</div>' % ''.join('<p>%s</p>' % inline(t) for t in prose))
        out.append('</article>')
    return '\n'.join(out)


def build_ai_view():
    p = os.path.join(wm.DATA, 'profile', 'ai-view.md')
    if not os.path.exists(p):
        return _md_page('08 那页', 'ai-view.md', 'AI 怎么看我', 'AI 眼中的你', 'html/08_AI怎么看我.html')
    md = open(p, encoding='utf-8', errors='replace').read()
    body = ['<h1 class="display">AI 怎么看我</h1>',
            '<div class="refract"></div>',
            '<p class="timeline-intro">你说给不同 AI 的话，慢慢变成了它们对你的认识。这页把它们说过的话放在一起，哪里说准了，哪里还需要你自己判断。</p>',
            render_ai_view(md)]
    return ('html/08_AI怎么看我.html',
            page('AI 怎么看我 · 言镜', 'AI 眼中的你', '\n'.join(body)))


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


def render_ai_view(md):
    """按白话栏目渲染 AI 观察；旧版工具章节也能继续显示。"""
    sections = re.split(r'(?=^## )', md, flags=re.MULTILINE)
    out = []
    for section in sections:
        if not section.strip():
            continue
        title = section.splitlines()[0][3:].strip() if section.startswith('## ') else ''
        if not title:
            continue
        if '不同 AI 都看见' in title:
            kind = 'common'
        elif '看错过' in title:
            kind = 'mistake'
        elif '现在' in title and '认识' in title:
            kind = 'now'
        else:
            kind = 'single'
        out.append(_render_ai_section(section, kind))
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


def build_monthly(month=None):
    corpus = load_jsonl('corpus_dedup.jsonl')
    if not corpus:
        print('你说的话还没提取出来，先跑 ingest（或让 agent 走初始化）')
        sys.exit(1)
    months = sorted({o.get('date', '')[:7] for o in corpus if o.get('date')})
    month = month if (month and month in months) else months[-1]
    prev = months[months.index(month) - 1] if months.index(month) > 0 else None
    cur = [o for o in corpus if o.get('date', '').startswith(month)]
    prv = [o for o in corpus if prev and o.get('date', '').startswith(prev)]

    diff = ''
    if prev:
        d = len(cur) - len(prv)
        diff = '，比上月%s%d 条' % ('多' if d >= 0 else '少', abs(d))
    words = {}
    try:
        words = load_json(os.path.join(wm.DATA, 'stats_wordfreq.json'))
    except Exception:
        pass
    word_rows = []
    for w, v in words.items():
        try:
            v = int(v)
        except (TypeError, ValueError):
            continue
        c1 = sum(1 for o in cur if w in o.get('msg', ''))
        c0 = sum(1 for o in prv if w in o.get('msg', '')) if prev else 0
        if c1:
            word_rows.append((w, c1, c0))
    word_rows.sort(key=lambda t: t[1] - t[2], reverse=True)
    hot = word_rows[:5]

    # 决定/收线的口癖词表——只会多搜不会错搜（月报只挑几条展示，人工可筛）
    kw = re.compile(r'决定|定了|就这么|定下来|拍板|敲定|拍了|定了它|不再|不做了|不干了|弃了|放弃|算了|收线|关掉|关闭|结束|完成|搞定|办完|确认关闭|offer|录用|入职|上岗')
    decisions = [(o['date'], o.get('msg', '').replace('\n', ' ')[:100])
                 for o in cur if kw.search(o.get('msg', ''))][-8:]
    wbs = [(o.get('date', ''), o.get('msg', '')) for o in load_jsonl('user_writebacks.jsonl')
           if o.get('date', '').startswith(month)]
    try:
        items = load_json(os.path.join(wm.DATA, 'tracker_items.json'))
        items = items if isinstance(items, list) else items.get('items', [])
    except Exception:
        items = []
    done = [it for it in items if it.get('status') == 'done']
    promises = [o for o in _promises_all_layers()
                if o.get('status') in ('closed', 'dropped') and o.get('closed_date', '').startswith(month)]

    def esc(s):
        return H.escape(str(s))
    body = ['<h1 class="display">这个月，<br>你说给 AI 的话</h1>',
            '<div class="refract"></div>']
    body.append('<div class="bignum-row">'
                '<div class="bignum"><div class="n">%d</div><div class="note">条原话%s</div></div>'
                '<div class="bignum"><div class="n mono" style="font-size:26px;padding-top:8px;">%s</div>'
                '<div class="note">本月</div></div></div>' % (len(cur), esc(diff), month))
    if hot:
        body.append('<h2>高频词变化</h2>')
        body.append('<div style="margin:8px 0 16px;">%s</div>' % ''.join(
            '<span class="pill">「%s」<b>%d</b> 次%s</span>'
            % (esc(w), c1, ('，上月 %d' % c0) if prev else '，新出现') for w, c1, c0 in hot))
    body.append('<h2>本月决定</h2>')
    if wbs:
        body.append('<ul>%s</ul>' % ''.join(
            '<li><span class="mono">%s</span> · %s</li>' % (esc(d), esc(m)) for d, m in wbs))
    if decisions:
        body.append('<p style="color:var(--muted);">聊天记录里你拍板的话（挑了几条）：</p><ul>%s</ul>' %
                    ''.join('<li><span class="mono">%s</span> · %s</li>' % (esc(d), esc(m)) for d, m in decisions))
    if not wbs and not decisions:
        body.append('<p>这个月没有记下的决定。</p>')
    body.append('<h2>这个月办完的事</h2>')
    ledger_name = {'全局账本': '全局', '项目账本': '这个目录'}
    if promises:
        body.append('<ul>%s</ul>' % ''.join(
            '<li><span class="mono">%s</span> · 划掉：%s<span style="color:var(--muted);">（%s）</span></li>'
            % (esc(o.get('closed_date', '')), esc(o.get('text', '')),
               esc(ledger_name.get(o.get('_ledger'), o.get('_ledger') or ''))) for o in promises))
    if done:
        body.append('<p style="color:var(--muted);">之前已经办完 %d 件。</p>' % len(done))
    if not promises and not done:
        body.append('<p>这个月还没有办完的事。你说一句"这事做完了"，AI 就会记上。</p>')
    ins_top = [o for o in load_insights() if o.get('status') in ('active', None, '')][:3]
    body.append('<h2>这个月的提醒</h2>')
    if ins_top:
        body.append('<div class="insight-grid">' + ''.join(insight_card(o) for o in ins_top) + '</div>')
    else:
        body.append('<p>还没有提醒。</p>')
    body.append('<p style="color:var(--muted-soft);font-size:13px;">生成于 %s</p>' % datetime.date.today().isoformat())
    return (os.path.join('monthly', '%s.html' % month),
            page('言镜月报 · %s' % month, '月报 <span class="dot">·</span> %s' % month,
                 '\n'.join(body), home='../html/index.html'))


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
    return ('<article class="promise-card">'
            '<div class="promise-card-head"><span class="mono">%s</span><span class="promise-status">%s</span></div>'
            '<div class="promise-text">「%s」</div>'
            '<div class="promise-meta">%s · %s%s</div>'
            '</article>'
            % (H.escape(date), H.escape(status_label), H.escape(o.get('text', '')),
               H.escape(age_text), H.escape(o.get('_ledger', '')),
               (' · 收线于 %s' % H.escape(end)) if o.get('closed_date') else ''))


def build_tracker():
    """03 说过要做的事：把清单改成“后来去了哪里”，不再计算说到做到率。"""
    rows = _promises_all_layers()
    open_rows = sorted((o for o in rows if o.get('status') == 'open'), key=lambda o: o.get('date', ''))
    done_rows = sorted((o for o in rows if o.get('status') == 'closed'), key=lambda o: o.get('closed_date', '') or o.get('date', ''), reverse=True)
    drop_rows = sorted((o for o in rows if o.get('status') == 'dropped'), key=lambda o: o.get('closed_date', '') or o.get('date', ''), reverse=True)

    body = ['<h1 class="display">说过要做的事，<br>后来都去了哪里</h1>',
            '<div class="refract"></div>',
            '<p class="timeline-intro">这里不替你打分，只把你亲口说过要做的事放回来，看它们后来停在哪里。</p>']
    if open_rows:
        body.append('<h2>还没做完</h2><p class="section-lead">账本里还开着的事。它们是“还没做完”，不是自动判定的失败。</p>')
        body.append('<div class="promise-grid">%s</div>' % ''.join(_promise_card(o, '还没做完') for o in open_rows))
    if done_rows:
        body.append('<h2>办完了</h2>')
        body.append('<div class="promise-grid">%s</div>' % ''.join(_promise_card(o, '办完了') for o in done_rows))
    if drop_rows:
        body.append('<h2>已经收线</h2><p class="section-lead">只有账本明确记为不做了的，才放在这里。</p>')
        body.append('<div class="promise-grid">%s</div>' % ''.join(_promise_card(o, '已经收线') for o in drop_rows))
    if not rows:
        body.append('<div class="band"><p>还没记过要做的事。你明确说“我要做 X”时，AI 才会把它记下来。</p></div>')
    return ('html/03_说过要做的事.html',
            page('说过要做的事 · 言镜', '说过要做的事', '\n'.join(body)))


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
    jobs = []
    if cmd in ('read', 'all'):
        jobs += [build_portrait(), build_decisions(), build_insights(), build_recurring(),
                 build_agents(), build_tasks(), build_ai_view(), build_wrapped(), build_index()]
    if cmd in ('tracker', 'all'):
        jobs.append(build_tracker())
    # 月报已并入 09 走过的这几个月（timeline.md 的「最近这个月」一节），不再单独脚本生成
    if cmd == 'monthly':
        print('月报已并入 09 页（timeline.md），不再单独生成。')
    for j in jobs:
        if j:
            write_out(*j)


if __name__ == '__main__':
    main()
