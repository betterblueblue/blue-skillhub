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


def page(title, eyebrow, body, home='index.html'):
    return (SHELL.replace('__TITLE__', H.escape(title))
                 .replace('__HOME__', home)
                 .replace('__EYEBROW__', eyebrow)
                 .replace('__BODY__', body))


def inline(s):
    s = H.escape(s)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)


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
    """照见卡：类型标签 + 事实 + 证据引文。"""
    t = INSIGHT_TYPE.get(o.get('type', ''), o.get('type', '提醒'))
    st = INSIGHT_STATUS.get(o.get('status', 'active'), o.get('status', '还没说'))
    quotes = []
    for e in (o.get('evidence') or [])[:2]:
        if isinstance(e, dict):
            quotes.append('<div class="insight-quote"><div class="date">%s</div><div class="txt">「%s」</div></div>'
                          % (H.escape(str(e.get('date', ''))), H.escape(str(e.get('msg', '')))))
    return ('<article class="insight-card"><div class="insight-type">%s · %s</div>'
            '<p class="insight-fact">%s</p>%s</article>'
            % (H.escape(t), H.escape(st), H.escape(o.get('fact', '')), ''.join(quotes)))


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
        print('跳过 01 那页：你的情况还没整理出来（先初始化）')
        return None
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


def build_wrapped():
    """09 走过的这几个月：内容由 Agent 读语料写 timeline.md，脚本只渲染，不挑月度主题/开场收尾原话。"""
    p = os.path.join(wm.DATA, 'profile', 'timeline.md')
    if not os.path.exists(p):
        print('跳过 09 那页：这几个月怎么过的还没整理出来（先跑蒸馏，见 distill-report-protocol）')
        return None
    md = open(p, encoding='utf-8', errors='replace').read()
    body = ['<h1 class="display">走过的这几个月，<br>我是怎么过的</h1>',
            '<div class="refract"></div>',
            render_markdown(md)]
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
        ('01', '我是谁', '我的情况、在忙什么、怎么跟我配合', '01_我是谁.html'),
        ('02', '我做过的重要决定', '我拍过板、放过话、又反悔过的话', '02_我做过的重要决定.html'),
        ('03', '说过要做的事', '我说话算不算数', '03_说过要做的事.html'),
        ('04', '该注意的事', '有哪些我自己没注意的事', '04_该注意的事.html'),
        ('05', '我反复提的事', '哪些事我一直没解决', '05_我反复提的事.html'),
        ('06', '我在各个 AI 里的样子', '哪个用得最多、主要干啥、怎么说话', '06_我在各个AI里的样子.html'),
        ('07', '我总让 AI 干什么', '我总把什么活丢给 AI', '07_我总让AI干什么.html'),
        ('08', 'AI 怎么看我', 'AI 眼里我是什么样', '08_AI怎么看我.html'),
        ('09', '走过的这几个月', '这几个月我是怎么过的', '09_走过的这几个月.html'),
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
    body = ['<h1 class="display">这几件，<br>你可能没注意</h1>',
            '<div class="refract"></div>',
            '<p style="color:var(--muted);max-width:560px;">这里都是你说了没做、反复提、前后矛盾的事。'
            '只摆事实、带日期和原话，结论你自己下。</p>']
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
        '<div class="stats">'
        f'<div class="stat"><div class="n">{len(ag)}</div><div class="note">个 AI 工具，跟你有过来往</div></div>'
        f'<div class="stat"><div class="n">{format(total_msgs, ",")}</div><div class="note">条原话，分布在它们之间</div></div>'
        f'<div class="stat"><div class="n" style="font-size:24px;">{H.escape(top_name)}</div><div class="note">你用得最多的那个</div></div>'
        f'<div class="stat"><div class="n">{top_share}%</div><div class="note">第一名占了这么多</div></div>'
        '</div>'
    )

    body.append('<h2>哪个用得最多</h2>')
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

    # 判断部分：主要干啥 + 怎么跟它说话，Agent 读语料写 agents.md，脚本不替它下结论
    md_path = os.path.join(wm.DATA, 'profile', 'agents.md')
    if os.path.exists(md_path):
        body.append(render_markdown(open(md_path, encoding='utf-8', errors='replace').read()))
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
        print('跳过 %s：还没整理出来（先跑蒸馏，见 references/distill-report-protocol.md）' % name)
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
    return _md_page('02 那页', 'decisions.md', '我做过的重要决定', '决定', 'html/02_我做过的重要决定.html')


def build_recurring():
    return _md_page('05 那页', 'recurs.md', '我反复提的事', '反复提的事', 'html/05_我反复提的事.html')


def build_tasks():
    return _md_page('07 那页', 'tasks.md', '我总让 AI 干什么', '按任务看', 'html/07_我总让AI干什么.html')


def build_ai_view():
    return _md_page('08 那页', 'ai-view.md', 'AI 怎么看我', 'AI 眼中的你', 'html/08_AI怎么看我.html')


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

def build_tracker():
    rows = _promises_all_layers()
    open_rows = [o for o in rows if o.get('status') == 'open']
    done_rows = [o for o in rows if o.get('status') == 'closed']
    drop_rows = [o for o in rows if o.get('status') == 'dropped']
    open_rows.sort(key=lambda o: o.get('date', ''))
    done_rows.sort(key=lambda o: o.get('closed_date', '') or o.get('date', ''), reverse=True)
    drop_rows.sort(key=lambda o: o.get('closed_date', '') or o.get('date', ''), reverse=True)
    n_open, n_done, n_drop = len(open_rows), len(done_rows), len(drop_rows)
    total_prom = n_open + n_done + n_drop
    rate = round(100 * n_done / total_prom) if total_prom else 0

    body = ['<h1 class="display">说过要做的事，<br>我说话算数吗</h1>',
            '<div class="refract"></div>']
    if total_prom:
        body.append(
            '<div class="stats">'
            f'<div class="stat"><div class="n">{n_done}</div><div class="note">件办完了</div></div>'
            f'<div class="stat"><div class="n">{n_open}</div><div class="note">件还欠着</div></div>'
            f'<div class="stat"><div class="n">{n_drop}</div><div class="note">件不做了</div></div>'
            f'<div class="stat"><div class="n">{rate}%</div><div class="note">说到做到率</div></div>'
            '</div>'
        )
        body.append('<h2>还没做的</h2>')
        if open_rows:
            body.append('<ul>' + ''.join(
                '<li><span class="mono">%s</span> · %s</li>'
                % (H.escape(o.get('date', '')), H.escape(o.get('text', ''))) for o in open_rows) + '</ul>')
        else:
            body.append('<p>没有欠着的事。</p>')
        body.append('<h2>办完的</h2>')
        if done_rows:
            body.append('<ul>' + ''.join(
                '<li><span class="mono">%s</span> · %s</li>'
                % (H.escape(o.get('closed_date', '') or o.get('date', '')), H.escape(o.get('text', ''))) for o in done_rows) + '</ul>')
        else:
            body.append('<p>还没有办完过。</p>')
        body.append('<h2>不做了的</h2>')
        if drop_rows:
            body.append('<ul>' + ''.join(
                '<li><span class="mono">%s</span> · %s</li>'
                % (H.escape(o.get('closed_date', '') or o.get('date', '')), H.escape(o.get('text', ''))) for o in drop_rows) + '</ul>')
        else:
            body.append('<p>没有不做了的事。</p>')
    else:
        body.append('<div class="band"><p>还没记过要做的事。说一句"我要做 X"，AI 就会记上。</p></div>')
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
