# -*- coding: utf-8 -*-
"""原型：「AI 眼里的你」四种形态（起雾镜 / 手机主屏 / 聊天窗 / 线索墙）。
读本机数据，产物写到数据目录 products/prototype/，不进 git。
用法：python _prototype/build_ai_eyes_proto.py
"""
import os, sys, json, re, random, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
import _common as common

DATA, PROD = common.DATA, common.PRODUCTS
PROFILE = os.path.join(DATA, 'profile')
TODAY = datetime.date.today()
AGENT_NAMES = {'claude-code': 'Claude Code', 'codex': 'Codex', 'catpaw': 'CatPaw', 'antigravity': 'Antigravity',
               'zcode': 'zcode', 'dsh': 'DeepSeek', 'workbuddy': 'WorkBuddy', 'pi': 'Pi', 'qwen': 'Qwen'}


def read(name):
    p = os.path.join(PROFILE, name)
    return open(p, encoding='utf-8', errors='replace').read() if os.path.exists(p) else ''


def corpus():
    rows = []
    for l in open(os.path.join(DATA, 'corpus_dedup.jsonl'), encoding='utf-8'):
        if l.strip():
            o = json.loads(l)
            o['msg'] = (o.get('msg') or '').strip()
            if o['msg'] and valid(o.get('date')):
                rows.append(o)
    return rows


def valid(d):
    return bool(re.match(r'\d{4}-\d{2}-\d{2}$', str(d or '')))


def catchphrases(rows, n=12):
    """短句高频 = 口头禅；带首次/最近日期，点开可反查。"""
    by = collections.defaultdict(list)
    for o in rows:
        m = o['msg']
        if 2 <= len(m) <= 12 and not m.startswith(('/', '<', '[')):
            by[m].append(o['date'])
    top = sorted(by.items(), key=lambda kv: -len(kv[1]))[:n]
    return [{'text': k, 'n': len(v), 'first': min(v), 'last': max(v)} for k, v in top]


CODEISH = re.compile(r'[\\/{}<>`=]|https?:')
ASK = re.compile(r'^(帮我|帮忙|先|跑|提交|推送|改|看看|看下|检查|修|写|加|删|部署|测|生成|整理|查|更新|优化|重构)')


def hands(rows, n=14):
    """镜子两肩：最常让 AI 干的活。原型用动词开头的短指令粗筛；正式版由 Agent 从 portrait.md「你总让 AI 干什么」取。"""
    c = collections.Counter(o['msg'] for o in rows if 3 <= len(o['msg']) <= 16 and ASK.match(o['msg']) and not CODEISH.search(o['msg']))
    return [{'text': t, 'n': k} for t, k in c.most_common(n)]


def typical(items, median, k=3):
    """聊天窗：长度最接近这个工具中位数的几句，气泡长短才代表平时的说话方式。"""
    pool = [o for o in items if len(o['msg']) <= 80 and '\n' not in o['msg'] and not CODEISH.search(o['msg'])]
    random.seed(11)
    random.shuffle(pool)
    pool.sort(key=lambda o: abs(len(o['msg']) - median))
    out, seen = [], set()
    for o in pool:
        if o['msg'] not in seen:
            seen.add(o['msg']); out.append({'t': o['msg'], 'd': o['date']})
        if len(out) == k:
            break
    return sorted(out, key=lambda m: m['d'])


def mirror_quotes(rows, n=900):
    """镜中人像用的原话：短句、去掉代码和路径，高频的多放几次。"""
    pool = [o for o in rows if 4 <= len(o['msg']) <= 26 and not CODEISH.search(o['msg'])]
    random.seed(7)
    pick = random.sample(pool, min(n, len(pool)))
    return [{'t': o['msg'].replace('\n', ' '), 'd': o['date'], 'a': AGENT_NAMES.get(o['agent'], o['agent'])} for o in pick]


def agent_mirrors(rows, ai_eyes):
    titles = dict(re.findall(r'\*\*([\w\-]+)：([^*]+)\*\*', ai_eyes))
    stats = collections.defaultdict(list)
    for o in rows:
        stats[o['agent']].append(o)
    out = []
    for ag, items in sorted(stats.items(), key=lambda kv: -len(kv[1]))[:6]:
        lens = sorted(len(o['msg']) for o in items)
        cp = catchphrases(items, 5)
        longest = max((o for o in items if len(o['msg']) <= 60), key=lambda o: len(o['msg']))
        med = lens[len(lens) // 2]
        out.append({'agent': AGENT_NAMES.get(ag, ag), 'n': len(items), 'median': med,
                    'title': titles.get(ag, ''), 'phrases': cp, 'typical': typical(items, med),
                    'sample': {'t': longest['msg'], 'd': longest['date']}})
    return out


def lines(md):
    """lines.md → 每条线：标题、状态、带日期的事实行、现在的问题。"""
    out = []
    for sec in re.split(r'\n(?=### )', md):
        m = re.match(r'### (.+?)·(.+)', sec)
        if not m:
            continue
        facts = []
        for d, rest in re.findall(r'(\d{4}-\d{2}(?:-\d{2})?)\s*(.+)', sec):
            q = re.search(r'「([^」]+)」', rest)
            facts.append({'d': d, 'q': q.group(1) if q else rest.strip('。 ')[:60]})
        seen, uniq = set(), []
        for f in facts:
            if f['d'] + f['q'] not in seen:
                seen.add(f['d'] + f['q']); uniq.append(f)
        qm = re.search(r'现在的问题是：(.+)', sec)
        st = m.group(2).strip()
        kind = 'closed' if '收线' in st else ('stalled' if '准备' in st or '下文' in st else 'open')
        out.append({'name': m.group(1).strip(), 'status': st, 'kind': kind, 'facts': uniq[:6],
                    'question': qm.group(1).strip() if qm else ''})
    return out


def promises():
    p = os.path.join(DATA, 'promises.jsonl')
    rows = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()] if os.path.exists(p) else []
    rows = [o for o in rows if o.get('status') == 'open' and valid(o.get('date'))]
    for o in rows:
        o['days'] = (TODAY - datetime.date.fromisoformat(o['date'])).days
    rows.sort(key=lambda o: -o['days'])
    return [{'text': o['text'], 'd': o['date'], 'days': o['days'], 'ref': o.get('ref', '')} for o in rows]


def demo_data():
    """全是编的数据：给截图检查视觉用，不含任何真实原话。"""
    random.seed(3)
    said = ['继续', '好的', '可以啊', '先跑一下测试', '帮我看看这个报错', '提交推送', '这个不对', '再简单一点', '牛啊',
            '先别动代码', '我想做个小程序', '周末再弄', '今天先到这', '这个方案可以', '明天面试', '帮我改下简历',
            '换个思路', '有没有更好的办法', '我准备开始跑步了', '下周一定整理笔记', '先记下来', '看看效果', '行吧']
    days = lambda: '2026-%02d-%02d' % (random.randint(3, 9), random.randint(1, 28))
    phrases = [{'text': t, 'n': n, 'first': '2026-03-0%d' % (i % 9 + 1), 'last': '2026-09-%02d' % (20 - i)}
               for i, (t, n) in enumerate([('继续', 92), ('好的', 61), ('可以啊', 40), ('提交推送', 33), ('牛啊', 21),
                                            ('先跑一下测试', 18), ('这个不对', 15), ('再简单一点', 12), ('行吧', 9), ('今天先到这', 7)])]
    typ = {
        'Claude Code': ['先跑一下测试看看', '这个报错帮我看下', '改完提交推送'],
        'Codex': ['把登录模块重构一下，先写测试再改，改完跑一遍全量', '这个任务你自己拆，拆完一步步做，别问我', '把上周那个接口的边界情况都补上测试'],
        'Cursor': ['改一下', '这行删了', '行'],
        'Gemini': ['这个库最新版本是多少，有啥大改动', '帮我找找这个问题有没有官方说法', '对比一下这两个方案'],
        'Kimi': ['这是我整理的一整份面试材料，帮我提炼成三点，每点给一个例子，语气别太正式', '这段会议记录太乱了，帮我按时间理一遍，谁说了什么列出来', '把这篇文章压到三百字，保留数字'],
        'Qwen': ['试试你', '翻译一下这段', '写个周报开头'],
    }
    agents = []
    for name, n, med, title in [('Claude Code', 5200, 14, '你的主开发台'), ('Codex', 4800, 31, '长任务交给它'), ('Cursor', 900, 9, '顺手改两行'),
                                ('Gemini', 620, 22, '查资料的地方'), ('Kimi', 410, 40, '整段材料丢过去'), ('Qwen', 260, 12, '偶尔试试')]:
        agents.append({'agent': name, 'n': n, 'median': med, 'title': title,
                       'phrases': [{'text': t, 'n': random.randint(5, 60)} for t in random.sample(said, 5)],
                       'typical': sorted([{'t': t, 'd': days()} for t in typ[name]], key=lambda m: m['d']),
                       'sample': {'t': random.choice(said), 'd': days()}})
    lines_ = [
        {'name': '换工作', 'status': '还在走', 'kind': 'open', 'question': '先多投几家，还是先把项目经历讲顺',
         'facts': [{'d': '2026-05-02', 'q': '我准备换个方向试试'}, {'d': '2026-06-18', 'q': '帮我改下简历'}, {'d': '2026-08-09', 'q': '明天面试，帮我过一遍'}]},
        {'name': '自己的小程序', 'status': '还在走', 'kind': 'open', 'question': '继续加功能，还是先给朋友用起来',
         'facts': [{'d': '2026-04-11', 'q': '我想做个记账小程序'}, {'d': '2026-07-01', 'q': '先把登录做完'}, {'d': '2026-09-12', 'q': '这个方案可以'}]},
        {'name': '跑步', 'status': '一直停在“准备做”', 'kind': 'stalled', 'question': '是真想开始，还是先放一放',
         'facts': [{'d': '2026-03-20', 'q': '我准备开始跑步了'}, {'d': '2026-06-05', 'q': '下周一定开始跑'}]},
        {'name': '整理读书笔记', 'status': '没了下文', 'kind': 'stalled', 'question': '',
         'facts': [{'d': '2026-04-02', 'q': '下周一定整理笔记'}, {'d': '2026-05-30', 'q': '笔记先记下来再说'}]},
        {'name': '考证', 'status': '已经收线', 'kind': 'closed', 'question': '',
         'facts': [{'d': '2026-03-01', 'q': '这个月开始刷题'}, {'d': '2026-05-15', 'q': '不考了，先找工作'}]},
    ]
    promises_ = [{'text': t, 'd': d, 'days': (TODAY - datetime.date.fromisoformat(d)).days, 'ref': ''}
                 for t, d in [('开始跑步', '2026-03-20'), ('整理读书笔记', '2026-04-02'), ('给小程序写个说明', '2026-07-01')]]
    return {'today': TODAY.isoformat(), 'total': 12240, 'span': ['2026-03-01', '2026-09-20'], 'phrases': phrases,
            'mirror': [{'t': random.choice(said), 'd': days(), 'a': random.choice(agents)['agent']} for _ in range(600)],
            'agents': agents, 'lines': lines_, 'promises': promises_,
            'hands': [{'text': t, 'n': n} for t, n in [('先跑一下测试', 48), ('提交推送', 33), ('帮我看看这个报错', 27), ('改下简历', 14),
                                                        ('整理一下笔记', 9), ('查一下文档', 8), ('写个脚本', 6)]]}


def main():
    if '--demo' in sys.argv:
        tpl = open(os.path.join(HERE, 'ai_eyes_proto.html'), encoding='utf-8').read()
        out = os.path.join(HERE, 'ai_eyes_demo.html')
        open(out, 'w', encoding='utf-8').write(tpl.replace('/*__DATA__*/null', json.dumps(demo_data(), ensure_ascii=False)))
        print('演示版（假数据）写好了：%s' % out)
        return
    rows = corpus()
    data = {
        'today': TODAY.isoformat(),
        'total': len(rows),
        'span': [min(o['date'] for o in rows), max(o['date'] for o in rows)],
        'phrases': catchphrases(rows),
        'mirror': mirror_quotes(rows),
        'agents': agent_mirrors(rows, read('ai-eyes.md')),
        'lines': lines(read('lines.md')),
        'promises': promises(),
        'hands': hands(rows),
    }
    tpl = open(os.path.join(HERE, 'ai_eyes_proto.html'), encoding='utf-8').read()
    html = tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    out_dir = os.path.join(PROD, 'prototype')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, 'ai_eyes.html')
    open(out, 'w', encoding='utf-8').write(html)
    print('写好了：%s（原话 %d 条，线 %d 条，没下文 %d 件）' % (out, len(rows), len(data['lines']), len(data['promises'])))


if __name__ == '__main__':
    main()
