# -*- coding: utf-8 -*-
"""ds · 言镜（wordmirror）命令行入口。

用法：
    python ds.py init    探测你机器上有哪些 agent 的存档
    python ds.py ingest  全链路：提取 → 去重 → 会话卡 → 数字底座 → 素材 → 渲染产物
    python ds.py ask "问题关键词"   在你说过的话里搜
    python ds.py contrast "话题"    这个话题最早和最近的说法并排看
    python ds.py promise           看欠账本（说要做没做闭环的事）
    python ds.py promise add 要做的事 / promise done 关键词
    python ds.py export            生成随身说明书（仅脱敏公开层，画像全文不外发）
    python ds.py install <目录>    把 skill 包装进指定 skills 目录（--all 自动探测）
    python ds.py monthly [YYYY-MM] 生成月度三页纸
    python ds.py open    用浏览器打开产物入口页
    python ds.py check   跑全量自检（项数以输出为准）
    python ds.py where   显示数据目录在哪、画像多新

设计原则（DESIGN.md）：每人自己跑自己的；全部本地；探测不硬编码。
"""
import os, sys, subprocess, json, webbrowser, glob, re, shutil, datetime

# 定位两层（data-locations.md 的同款顺序）：
# 全局层（画像/语料/月报——"你是谁"，不分项目）：
#   1) 环境变量 WORD_MIRROR_HOME（旧名 DIGITAL_SELF_HOME 兼容）  2) ~/.wordmirror（旧 ~/.digital-self 兼容）
#   3) 仓库布局（脚本旁有 data/，开发实例）  4) 都没有 → 默认 ~/.wordmirror，首次写入时创建
# 项目层（欠账/写回——"这个项目的事"）：<当前目录>/.wordmirror/，在哪个目录干活账记哪
def _find_base():
    env = os.environ.get('WORD_MIRROR_HOME') or os.environ.get('DIGITAL_SELF_HOME')
    if env and os.path.isdir(os.path.join(env, 'data')):
        return env
    home = os.path.join(os.path.expanduser('~'), '.wordmirror')
    if os.path.isdir(os.path.join(home, 'data')):
        return home
    legacy = os.path.join(os.path.expanduser('~'), '.digital-self')
    if os.path.isdir(os.path.join(legacy, 'data')):
        return legacy
    guess = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if os.path.isdir(os.path.join(guess, 'data')):
        return guess
    return home  # 标准默认位置，首次写入时自动创建

def _promises_file():
    """账本分两层：在仓库实例目录里干活 → 全局 data/；在其他项目目录 → 该目录 .wordmirror/。"""
    cwd = os.getcwd()
    if os.path.normcase(os.path.abspath(cwd)) == os.path.normcase(os.path.abspath(BASE)):
        return os.path.join(DATA, 'promises.jsonl')
    return os.path.join(cwd, '.wordmirror', 'promises.jsonl')

def _ledger_paths():
    """开场/查询要看的所有账本：当前项目层 + 全局层（去重）。"""
    paths = [_promises_file()]
    g = os.path.join(DATA, 'promises.jsonl')
    if os.path.normcase(os.path.abspath(g)) != os.path.normcase(os.path.abspath(paths[0])):
        paths.append(g)
    return paths

BASE = _find_base()
ENGINE = os.path.join(BASE, 'engine')
DATA = os.path.join(BASE, 'data')
PRODUCTS = os.path.join(BASE, 'products')

def run(script, **kw):
    """跑 engine 下的脚本，透传输出。"""
    path = os.path.join(ENGINE, script)
    if not os.path.exists(path):
        print('缺少引擎脚本 engine/%s —— 只装了 skill 包时 init/ingest 用不了。' % script)
        print('解决办法：设环境变量 WORD_MIRROR_HOME 指向完整仓库根，或克隆完整仓库。')
        sys.exit(1)
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, encoding='utf-8', **kw)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.returncode != 0:
        print(r.stderr[:500])
        sys.exit(1)
    return r

def cmd_init():
    print('第一步：看看你机器上有哪些 agent 的存档')
    print()
    run('detect_agents.py')
    print()
    print('下一步：python ds.py ingest  （开始提取你说过的所有话）')

def cmd_ingest():
    steps = [
        ('提取你说的话', 'extract_all.py'),
        ('提取 AI 的回复', 'extract_ai.py'),
        ('拼会话卡', 'build_session_cards.py'),
        ('算数字底座（你的口头禅/消息长度/分 agent 特征）', 'compute_stats.py'),
        ('挖素材（决定时刻/被问住的瞬间/月度切片/项目基因）', 'distill_materials.py'),
        ('渲染产物页面', 'generate_html_pages.py'),
    ]
    print('ds ingest · 开始（全部本地，不出你这台机器）')
    print('=' * 56)
    for i, (label, script) in enumerate(steps, 1):
        print('[%d/%d] %s ...' % (i, len(steps), label))
        run(script)
    # 去重步骤（extract_all 产出未去重版，这里生成主力文件）
    print('[%d/%d] 去重 ...' % (len(steps), len(steps)))
    _dedup()
    # 汇报第一口糖
    _sugar_report()
    print('=' * 56)
    print('完成。看结果：')
    print('  python ds.py open   （浏览器打开「这几个月翻给你看」）')

def _dedup():
    src = os.path.join(DATA, 'corpus_all.jsonl')
    dst = os.path.join(DATA, 'corpus_dedup.jsonl')
    import re
    import hashlib
    seen, out = set(), []
    for line in open(src, encoding='utf-8'):
        o = json.loads(line)
        # 去重键 = 全文归一化哈希。截前 150 字符会把长消息误判成同一条
        k = hashlib.sha1(re.sub(r'\s+', '', o['msg']).encode('utf-8')).hexdigest()
        if k in seen:
            continue
        seen.add(k)
        out.append(o)
    with open(dst, 'w', encoding='utf-8') as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')
    print('     去重完成：%d → %d 条' % (len(seen) + 0 or 0, len(out)) if False else '     去重完成：共 %d 条' % len(out))

def _sugar_report():
    # 第一口糖：数字汇报 + 提示画像方向
    try:
        n = sum(1 for _ in open(os.path.join(DATA, 'corpus_dedup.jsonl'), encoding='utf-8'))
    except FileNotFoundError:
        return
    print()
    print('你跟 AI 说过的话：%d 条（去重后）' % n)
    if n < 500:
        print('（还不到 500 条——画像会很薄，先攒着，以后再跑会越来越厚）')
    elif n < 3000:
        print('（中等量级：口头禅和习惯已经很准，决定类文档开始有料）')
    else:
        print('（重度用户量级：全部产物都会很扎实）')

def cmd_ask(query):
    if not query:
        print('用法：python ds.py ask "关键词"')
        sys.exit(1)
    # 简单 grep：跨两个主力文件
    import re
    hits = []
    for f in ['corpus_dedup.jsonl', 'user_writebacks.jsonl']:
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            if query.lower() in line.lower():
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                hits.append(o)
    if not hits:
        print('没找到含「%s」的话。换个词试试？' % query)
        return
    hits.sort(key=lambda o: o.get('date', ''))
    print('找到 %d 条（按时间排）:' % len(hits))
    for o in hits[-15:]:
        msg = o.get('msg', '').replace(chr(10), ' ')[:110]
        print('  %s | %-10s | %s' % (o.get('date', '?'), o.get('agent', o.get('source', '?')), msg))
    if len(hits) > 15:
        print('  …（共 %d 条，只显示最近 15 条）' % len(hits))

def cmd_open():
    for name in ['index.html', '10_这九个月翻给你看.html']:
        p = os.path.join(PRODUCTS, 'html', name)
        if os.path.exists(p):
            webbrowser.open('file:///' + p.replace(chr(92), '/'))
            print('已打开：%s' % name)
            return
    print('产物页面不存在，先跑 python ds.py ingest')

def cmd_check():
    run('self_check.py')

def cmd_where():
    print('数据目录：%s' % DATA)
    print('产物目录：%s' % PRODUCTS)
    cwd = os.getcwd()
    if os.path.normcase(os.path.abspath(cwd)) != os.path.normcase(os.path.abspath(BASE)):
        proj = os.path.join(cwd, '.wordmirror', 'promises.jsonl')
        mark = '（已有项目账本）' if os.path.exists(proj) else '（首次记账时创建）'
        print('项目账本：%s %s' % (os.path.dirname(proj), mark))
    n = _try_count()
    print('语料条数：%s' % (n if n else '（还没跑过 ingest）'))
    info = _profile_age()
    if info:
        days, d = info
        tip = '今天刚更新' if days == 0 else ('已 %d 天，该补最近的情况了' % days if days > 30 else '已 %d 天' % days)
        print('画像日期：%s（%s）' % (d, tip))
    else:
        print('画像：还没有，先跑 ingest 再让 agent 生成')

def _profile_age():
    """从 portrait.md 顶部抳第一个日期，算画像多少天没更新。"""
    p = os.path.join(DATA, 'profile', 'portrait.md')
    if not os.path.exists(p):
        return None
    m = re.search(r'(\d{4}-\d{2}-\d{2})', open(p, encoding='utf-8', errors='replace').read())
    if not m:
        return None
    d = datetime.date.fromisoformat(m.group(1))
    return (datetime.date.today() - d).days, m.group(1)

# ===== 欠账本（说要做的事，两层：项目 + 全局）=====

def _load_promises(path, strict=False):
    out = []
    if os.path.exists(path):
        for i, line in enumerate(open(path, encoding='utf-8'), 1):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                if strict:
                    # 写操作不许碰损坏的账本——重写整份文件会把坏行永久吞掉
                    print('账本 %s 第 %d 行不是合法 JSON。先手工修复或删掉那行再操作，我不替你静默改账。' % (path, i))
                    sys.exit(1)
                print('警告：欠账本 %s 第 %d 行不是合法 JSON，跳过（查询不受影响）' % (path, i))
                continue
            o['_line'] = i
            out.append(o)
    return out

def _ledger_tag(path):
    """项目账本 = 当前目录 .wordmirror 下的那本；其余（含默认 ~/.wordmirror）都算全局账本。"""
    proj = os.path.join(os.getcwd(), '.wordmirror', 'promises.jsonl')
    return '项目账本' if os.path.normcase(os.path.abspath(path)) == os.path.normcase(os.path.abspath(proj)) else '全局账本'

def _tracker_note(today):
    """档案 tracker 里的搁置事项也报一声——只读提醒，不动账（SKILL.md 开工检查的数据源）。"""
    try:
        tr = json.load(open(os.path.join(DATA, 'tracker_items.json'), encoding='utf-8'))
        tr = tr if isinstance(tr, list) else tr.get('items', [])
        st = sorted((r for r in tr if r.get('status') == 'stalled'), key=lambda r: r.get('date', ''))
    except Exception:
        return
    if not st:
        return
    r0 = st[0]
    days = (today - datetime.date.fromisoformat(r0['date'])).days if r0.get('date') else '?'
    print('另外，档案 tracker 里还有 %d 件搁置的事，最老一件：' % len(st))
    print('  %s 记的（%d 天）| %s' % (r0.get('date', '?'), days, r0.get('title', r0.get('desc', ''))))

def cmd_promise(args):
    if not args:
        infos = [(path, _load_promises(path)) for path in _ledger_paths()]
        rows = []
        for path, items in infos:
            for o in items:
                if o.get('status') == 'open':
                    rows.append((_ledger_tag(path), o))
        today = datetime.date.today()
        if not rows:
            print('欠账本干净，没有开着的事。')
            _tracker_note(today)
            return
        rows.sort(key=lambda t: t[1].get('date', ''))
        print('欠账 %d 笔（从老到新）:' % len(rows))
        for tag, o in rows:
            days = (today - datetime.date.fromisoformat(o['date'])).days if o.get('date') else '?'
            print('  [%s] %s 记的（%d 天）| %s' % (tag, o.get('date', '?'), days, o.get('text', '')))
        _tracker_note(today)
        return
    sub = args[0]
    if sub == 'add':
        text = ' '.join(args[1:]).strip()
        if not text:
            print('用法：python ds.py promise add 要做的事')
            sys.exit(1)
        pf = _promises_file()
        os.makedirs(os.path.dirname(pf), exist_ok=True)
        row = {'date': datetime.date.today().isoformat(), 'text': text,
               'status': 'open', 'agent': 'cli'}
        with open(pf, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
        print('记下了：%s（%s）' % (text, pf))
    elif sub in ('done', 'drop'):
        kw = ' '.join(args[1:]).strip()
        if not kw:
            print('必须给关键词，否则分不清要划哪笔。用法：python ds.py promise done 关键词')
            sys.exit(1)
        for pf in _ledger_paths():
            items = _load_promises(pf, strict=True)  # 写操作前严格查损，坏账本宁可停也不吞
            hit = next((o for o in items if o.get('status') == 'open' and kw in o.get('text', '')), None)
            if not hit:
                continue
            hit['status'] = 'closed' if sub == 'done' else 'dropped'
            hit['closed_date'] = datetime.date.today().isoformat()
            with open(pf, 'w', encoding='utf-8') as f:
                for o in items:
                    line = dict(o); line.pop('_line', None)
                    f.write(json.dumps(line, ensure_ascii=False) + '\n')
            print('划掉了：%s（%s）' % (hit['text'], pf))
            return
        print('没找到开着的事里含「%s」的。' % kw)
        sys.exit(1)
    else:
        print('用法：python ds.py promise / promise add 文本 / promise done 关键词')

def cmd_contrast(query):
    """同一话题最早 vs 最近的说法并排看——观点变没变，用户自己判断。"""
    if not query:
        print('用法：python ds.py contrast "话题关键词"')
        sys.exit(1)
    hits = []
    for f in ['corpus_dedup.jsonl', 'user_writebacks.jsonl']:
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            if query.lower() in line.lower():
                try:
                    hits.append(json.loads(line))
                except Exception:
                    continue
    if len(hits) < 2:
        print('「%s」只找到 %d 条，凑不成对比。' % (query, len(hits)))
        return
    hits.sort(key=lambda o: o.get('date', ''))
    first, last = hits[0], hits[-1]
    def show(o, tag):
        msg = o.get('msg', '').replace(chr(10), ' ')
        print('  【%s】%s | %s' % (tag, o.get('date', '?'), msg[:120]))
    print('「%s」共 %d 条，跨度 %s → %s：' % (query, len(hits), first.get('date', '?'), last.get('date', '?')))
    show(first, '最早')
    show(last, '最近')
    print('（中间变没变、为什么变，你自己判断——AI 不下结论）')

def cmd_export():
    """随身说明书：只出脱敏后的公开层——贴给任何 AI 的东西绝不含画像全文（references/privacy-rules.md）。"""
    pub_p = os.path.join(DATA, 'layers', 'public.md')
    pub = open(pub_p, encoding='utf-8', errors='replace').read().strip() if os.path.exists(pub_p) else ''
    if len(pub) < 40:  # 只剩模板头也算空
        print('公开层（data/layers/public.md）还没有内容——对外分享只能用脱敏公开层，不能导画像全文。')
        print('先让 agent 按隐私规矩（references/privacy-rules.md）从画像提炼 public.md，再跑 export。')
        sys.exit(1)
    out = os.path.join(PRODUCTS, 'ME_随身说明书.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('# 我的说明书（言镜导出，%s）\n\n' % datetime.date.today().isoformat())
        f.write('> 把下面整段贴给任何 AI（系统提示或对话开头都行），它就认识我了。\n')
        f.write('> 本说明书只含公开层：真实姓名、公司、薪资等隐私已按 redact_list 脱敏。\n\n---\n\n')
        f.write(pub)
        f.write('\n')
    print('已生成：%s（仅公开层）' % out)
    print('用法：打开复制全文，贴到任何 AI 的对话开头或系统提示里。')

def cmd_install(args):
    """把 skill 包拷进目标 skills 目录。--all 自动探测常见位置。"""
    src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # skill/wordmirror
    targets = []
    if args and args[0] == '--all':
        for d in ['~/.claude/skills', '~/.codex/skills', '~/.agents/skills']:
            p = os.path.expanduser(d)
            if os.path.isdir(p):
                targets.append(p)
        for p in glob.glob(os.path.expanduser('~/.meituan-catpaw') + '/*/skills'):
            if os.path.isdir(p):
                targets.append(p)
        if not targets:
            print('没找到常见的 skills 目录。用 python ds.py install <目录> 手动指定。')
            return
    elif args:
        targets = [os.path.abspath(args[0])]
    else:
        print('用法：python ds.py install <skills目录> 或 install --all')
        return
    for t in targets:
        dst = os.path.join(t, 'wordmirror')
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print('已安装：%s' % dst)

def cmd_monthly(args):
    if args and re.match(r'\d{4}-\d{2}$', args[0]):
        os.environ['DS_MONTH'] = args[0]
    run('make_monthly.py')

def _try_count():
    try:
        return sum(1 for _ in open(os.path.join(DATA, 'corpus_dedup.jsonl'), encoding='utf-8'))
    except FileNotFoundError:
        return None

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == 'init':
        cmd_init()
    elif cmd == 'ingest':
        cmd_ingest()
    elif cmd == 'ask':
        cmd_ask(sys.argv[2] if len(sys.argv) > 2 else '')
    elif cmd == 'open':
        cmd_open()
    elif cmd == 'check':
        cmd_check()
    elif cmd == 'where':
        cmd_where()
    elif cmd == 'promise':
        cmd_promise(sys.argv[2:])
    elif cmd == 'contrast':
        cmd_contrast(sys.argv[2] if len(sys.argv) > 2 else '')
    elif cmd == 'export':
        cmd_export()
    elif cmd == 'install':
        cmd_install(sys.argv[2:])
    elif cmd == 'monthly':
        cmd_monthly(sys.argv[2:])
    else:
        print('不认识的命令：%s' % cmd)
        print(__doc__)

if __name__ == '__main__':
    main()
