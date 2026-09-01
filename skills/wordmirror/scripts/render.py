# -*- coding: utf-8 -*-
"""言镜渲染器（skill 自带能力）：data → HTML 产物。样式出自 ../templates/，数据在数据目录。
用法：
    python render.py read            # index + 01 画像页 + 10 Wrapped
    python render.py monthly [YYYY-MM]  # 月度三页纸（默认最近有语料的月份）
    python render.py tracker         # 03 承诺看板
    python render.py all             # 全部
不依赖 engine/——单装用户数据就位后同样能出（语料由 ingest 生成）。
零外部请求，产物是 file:// 双击可开的单文件。
"""
import os, sys, re, json, datetime
import html as H

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ds  # 复用数据定位：ds.DATA / ds.PRODUCTS

TPL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
OUT = os.path.join(ds.PRODUCTS, 'html')
MON = os.path.join(ds.PRODUCTS, 'monthly')
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
        if ln.startswith('## '):
            out.append('<h2>%s</h2>' % inline(ln[3:]))
        elif ln.startswith('### '):
            out.append('<h3>%s</h3>' % inline(ln[4:]))
        elif ln.startswith('> ') and not ln.startswith('> 数据源'):
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


# ---------- READ 页 ----------

def build_portrait():
    p = os.path.join(ds.DATA, 'profile', 'portrait.md')
    if not os.path.exists(p):
        print('跳过 01 画像页：portrait.md 还没生成（先初始化）')
        return None
    md = open(p, encoding='utf-8', errors='replace').read()
    ver = re.search(r'# 我是谁（(v\d+) · (\d{4}-\d{2}-\d{2})）', md)
    tag, date = (ver.group(1), ver.group(2)) if ver else ('v1', '')
    src = re.search(r'> 数据源：(.+)', md)
    body = ['<h1 class="display">我是谁，<br>怎么跟我共事</h1>']
    if src:
        body.append('<div class="band"><p>%s</p></div>' % inline(src.group(1)))
    body.append(render_markdown(md[md.index('## 一句话'):]))
    return ('html/01_我是谁_怎么跟我共事.html',
            page('我是谁 · 言镜', '说明书 %s <span class="dot">·</span> %s <span class="dot">·</span> 言镜整理' % (tag, date), '\n'.join(body)))


def build_wrapped():
    months = load_json(os.path.join(ds.DATA, 'materials_monthly.json'))
    wf = load_json(os.path.join(ds.DATA, 'stats_wordfreq.json'))
    ag = load_json(os.path.join(ds.DATA, 'stats_agents.json'))
    total = sum(a['msgs'] for a in ag.values())
    keys = sorted(months)
    span = '%s ~ %s' % (keys[0], keys[-1])
    top = sorted(wf.items(), key=lambda t: -t[1])[:5]
    top_html = ''.join('<span class="pill">%s <b>%d</b> 次</span>' % (H.escape(w), n) for w, n in top)

    body = ['<h1 class="display">这九个月，<br>翻给你看</h1>']
    body.append('<div class="bignum-row">'
                '<div class="bignum"><div class="n">%s</div><div class="note">条原话，都是你说给 AI 的</div></div>'
                '<div class="bignum"><div class="n">%d</div><div class="note">个 AI 工具跟你聊过</div></div>'
                '<div class="bignum"><div class="n mono" style="font-size:26px;padding-top:8px;">%s</div>'
                '<div class="note">从第一条到最新一条</div></div></div>' % (format(total, ','), len(ag), span))
    body.append('<h2>你最高频的词，暴露了你的工作方式</h2>')
    body.append('<div style="margin:16px 0 8px;">%s</div>' % top_html)
    body.append('<h2>按月翻</h2>')
    for k in keys:
        m = months[k]
        topics = ''.join('<span class="pill">%s</span>' % H.escape(t) for t, _ in m.get('top_topics', [])[:3])
        body.append('<div class="card">')
        body.append('<div class="eyebrow">%s <span class="dot">·</span> %d 条</div>' % (k, m.get('n', 0)))
        body.append('<div style="margin-bottom:8px;">%s</div>' % topics)
        if m.get('opener'):
            body.append('<div class="quote"><span class="q-eyebrow">开场第一句</span>'
                        '<div class="q-text">「%s」</div></div>' % H.escape(m['opener'][:120]))
        if m.get('closer'):
            body.append('<div class="quote"><span class="q-eyebrow">收尾一句</span>'
                        '<div class="q-text">「%s」</div></div>' % H.escape(m['closer'][:120]))
        body.append('</div>')
    return ('html/10_这九个月翻给你看.html',
            page('这九个月翻给你看 · 言镜', 'Wrapped · %s <span class="dot">·</span> 按月回顾' % span, '\n'.join(body)))


def build_index():
    ag = load_json(os.path.join(ds.DATA, 'stats_agents.json'))
    tr_p = os.path.join(ds.DATA, 'tracker_items.json')
    rows = []
    if os.path.exists(tr_p):
        tr = load_json(tr_p)
        rows = tr if isinstance(tr, list) else tr.get('items', [])
    stalled = sum(1 for r in rows if r.get('status') == 'stalled')
    total = sum(a['msgs'] for a in ag.values())

    cards = [
        ('01', '我是谁，怎么跟我共事', '你的说明书：你是谁、在忙什么、AI 该怎么跟你配合', '01_我是谁_怎么跟我共事.html'),
        ('03', '我说过要做的事，现在都怎么样了', '哪件说了没下文，一眼看清', '03_我说过要做的事_现在都怎么样了.html'),
        ('10', '这九个月翻给你看', '一个月一页，翻回去看', '10_这九个月翻给你看.html'),
    ]
    monthly = sorted(os.listdir(MON)) if os.path.isdir(MON) else []
    if monthly:
        cards.append(('08', '%s · 这个月你对 AI 说了什么' % monthly[-1].replace('.html', ''),
                      '当月的量、决定、办完的事', 'monthly/' + monthly[-1]))
    body = ['<h1 class="display">言镜</h1>',
            '<p style="font-size:18px;color:var(--body-strong);">你跟 AI 说过的话，全存档在这了。'
            '换了新的 AI 干活时，让它先读你的说明书——不用每次从头自我介绍。</p>',
            '<div class="bignum-row">'
            '<div class="bignum"><div class="n">%s</div><div class="note">条对话记录（去掉重复后）</div></div>'
            '<div class="bignum"><div class="n">%d</div><div class="note">个 AI 工具的聊天记录</div></div>'
            '<div class="bignum"><div class="n" style="color:var(--stalled);">%d</div>'
            '<div class="note">件说了没下文的事（超 30 天），最扎眼</div></div></div>' % (format(total, ','), len(ag), stalled)]
    body.append('<h2>页面</h2>')
    for num, title, desc, href in cards:
        body.append('<div class="card"><div class="eyebrow">%s</div>'
                    '<p style="font-size:19px;margin-bottom:4px;"><strong><a href="%s">%s</a></strong></p>'
                    '<p style="color:var(--muted);">%s</p></div>'
                    % (num, href, H.escape(title), H.escape(desc)))
    body.append('<h2>文档</h2>')
    if os.path.isdir(os.path.join(ds.PRODUCTS)):
        docs = sorted(f for f in os.listdir(ds.PRODUCTS) if f.endswith('.md'))
        for f in docs:
            title = re.sub(r'^\d+_|\.md$', '', f).replace('_', ' · ')
            body.append('<div class="card" style="padding:16px 24px;">'
                        '<p style="margin:0;"><strong><a href="file:///%s">%s</a></strong></p></div>'
                        % (os.path.join(ds.PRODUCTS, f).replace('\\', '/'), H.escape(title)))
    return ('html/index.html',
            page('数字自己档案馆 · 言镜', '总入口 <span class="dot">·</span> 言镜 · wordmirror', '\n'.join(body), home='index.html'))


# ---------- 月报 ----------

def load_jsonl(name):
    p = os.path.join(ds.DATA, name)
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


def build_monthly(month=None):
    corpus = load_jsonl('corpus_dedup.jsonl')
    if not corpus:
        print('语料还没生成，先跑 ingest（或让 agent 走初始化流程）')
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
        words = load_json(os.path.join(ds.DATA, 'stats_wordfreq.json'))
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

    kw = re.compile(r'决定|定了|就这么|弃了|放弃|算了|确认关闭|offer|收线|完成')
    decisions = [(o['date'], o.get('msg', '').replace('\n', ' ')[:100])
                 for o in cur if kw.search(o.get('msg', ''))][-8:]
    wbs = [(o.get('date', ''), o.get('msg', '')) for o in load_jsonl('user_writebacks.jsonl')
           if o.get('date', '').startswith(month)]
    try:
        items = load_json(os.path.join(ds.DATA, 'tracker_items.json'))
        items = items if isinstance(items, list) else items.get('items', [])
    except Exception:
        items = []
    done = [it for it in items if it.get('status') == 'done']
    promises = [o for o in load_jsonl('promises.jsonl')
                if o.get('status') in ('closed', 'dropped') and o.get('closed_date', '').startswith(month)]

    def esc(s):
        return H.escape(str(s))
    body = ['<h1 class="display">这个月，<br>你说给 AI 的话</h1>']
    body.append('<div class="bignum-row">'
                '<div class="bignum"><div class="n">%d</div><div class="note">条原话%s</div></div>'
                '<div class="bignum"><div class="n mono" style="font-size:26px;padding-top:8px;">%s</div>'
                '<div class="note">本月</div></div></div>' % (len(cur), esc(diff), month))
    if hot:
        body.append('<h2>口头禅变化</h2>')
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
    if promises:
        body.append('<ul>%s</ul>' % ''.join(
            '<li><span class="mono">%s</span> · 划掉：%s</li>' % (esc(o.get('closed_date', '')), esc(o.get('text', ''))) for o in promises))
    if done:
        body.append('<p style="color:var(--muted);">之前已经办完 %d 件。</p>' % len(done))
    if not promises and not done:
        body.append('<p>这个月还没有办完的事。你说一句"这事做完了"，AI 就会记上。</p>')
    body.append('<p style="color:var(--muted-soft);font-size:13px;">生成于 %s</p>' % datetime.date.today().isoformat())
    return (os.path.join('monthly', '%s.html' % month),
            page('言镜月报 · %s' % month, '月报 <span class="dot">·</span> %s' % month,
                 '\n'.join(body), home='../index.html'))


# ---------- tracker 看板 ----------

def build_tracker():
    tpl = open(os.path.join(TPL, 'tracker.html'), encoding='utf-8').read()
    tr_p = os.path.join(ds.DATA, 'tracker_items.json')
    if not os.path.exists(tr_p):
        print('跳过 03 看板：tracker_items.json 还没生成（先 ingest）')
        return None
    data_text = open(tr_p, encoding='utf-8').read().strip()
    out = tpl.replace('__TRACKER_DATA__', data_text)
    return ('html/03_我说过要做的事_现在都怎么样了.html', out)


# ---------- 入口 ----------

def write_out(rel, content):
    p = os.path.join(ds.PRODUCTS, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print('渲染 -> products/%s' % rel)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    month = sys.argv[2] if len(sys.argv) > 2 and re.match(r'\d{4}-\d{2}$', sys.argv[2]) else None
    jobs = []
    if cmd in ('read', 'all'):
        jobs += [build_portrait(), build_wrapped(), build_index()]
    if cmd in ('monthly', 'all'):
        jobs.append(build_monthly(month))
    if cmd in ('tracker', 'all'):
        jobs.append(build_tracker())
    for j in jobs:
        if j:
            write_out(*j)


if __name__ == '__main__':
    main()
