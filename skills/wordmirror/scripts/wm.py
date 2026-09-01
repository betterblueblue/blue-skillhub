# -*- coding: utf-8 -*-
"""wm · 言镜（wordmirror）—— AI 干不了的重活工具 + 记账/写回的唯一入口。

查旧话、看数据在哪、导出说明书这些活 AI 用自己的本事就能干（见 SKILL.md），
不在这做命令。这里只留两类：

三件 AI 干不了的活：
    python wm.py ingest            提取你各 AI 的原始记录 → 去掉重复的 → 生成网页
    python wm.py vec build [--update]   建/更新按意思搜的索引（见 scripts/vecsearch.py）
    python wm.py vec status        看按意思搜的索引状态
    python wm.py monthly [YYYY-MM] 生成这个月的报告（调 render.py）
    python wm.py open              用浏览器打开首页

记账 / 写回（中护栏：只走命令，保证格式对、坏行拦得住）：
    python wm.py promise           看说过要做的事（哪些还没做完）
    python wm.py promise add 要做的事 / promise done 关键词 / promise drop 关键词
    python wm.py wb add "事实" --topic 主题 [--agent 工具名]   记下一条你确认过的事（--ref 附依据）
    python wm.py wb list           看记下的事

地基 / 护栏：
    python wm.py bind <仓库根>     把已有完整仓库的数据接上（--clear 取消）
    python wm.py check             跑一遍自检（检查项看输出）

设计原则（DESIGN.md）：每人自己跑自己的；数据全程在自己电脑上；不写死路径。
"""
import os, sys, subprocess, json, webbrowser, re, datetime

# 定位两层（data-locations.md 的同款顺序）：
# 全局层（画像/语料/月报——"你是谁"，不分项目）：
#   1) 环境变量 WORD_MIRROR_HOME（旧名 DIGITAL_SELF_HOME 兼容）
#   2) bind 指针 ~/wordmirror/bind.json（数据在别处时接上）
#   3) ~/wordmirror（旧 ~/.digital-self 兼容）
#   4) 脚本祖先逐级向上找仓库布局（data/ 下有语料签名才算，防无关 data/ 目录劫持）
#   5) 都没有 → 默认 ~/wordmirror，首次写入时自动创建
# 项目层（欠账/写回——"这个项目的事"）：<当前目录>/.wordmirror/，在哪个目录干活账记哪
def _find_base():
    """返回 (数据仓库根, 定位方式说明)。"""
    def _has_data(p):
        return os.path.isdir(os.path.join(p, 'data'))
    env = os.environ.get('WORD_MIRROR_HOME') or os.environ.get('DIGITAL_SELF_HOME')
    if env:
        how = 'WORD_MIRROR_HOME' if os.environ.get('WORD_MIRROR_HOME') else 'DIGITAL_SELF_HOME'
        if _has_data(env):
            return env, '环境变量 %s' % how
        return env, '环境变量 %s（还没有数据，首次写入时创建）' % how
    home = os.path.join(os.path.expanduser('~'), 'wordmirror')
    bind_p = os.path.join(home, 'bind.json')
    if os.path.isfile(bind_p):
        try:
            target = json.load(open(bind_p, encoding='utf-8')).get('home', '')
        except Exception:
            target = ''
        if target and _has_data(target):
            return target, 'bind 指针（%s）' % bind_p
    if _has_data(home):
        return home, '标准位置 ~/wordmirror'
    legacy = os.path.join(os.path.expanduser('~'), '.digital-self')
    if _has_data(legacy):
        return legacy, '旧目录 ~/.digital-self'
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if _has_data(d) and any(os.path.exists(os.path.join(d, 'data', f))
                                for f in ('corpus_dedup.jsonl', 'corpus_all.jsonl')):
            return d, '仓库布局（向上找到 %s）' % d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return home, '默认 ~/wordmirror（还没有数据，首次写入时创建）'

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

BASE, BASE_SOURCE = _find_base()
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(SKILL_DIR, 'engine')
DATA = os.path.join(BASE, 'data')
PRODUCTS = os.path.join(BASE, 'products')

def run(script, **kw):
    """跑 engine 下的脚本，把数据根目录经环境变量透传。"""
    path = os.path.join(ENGINE, script)
    if not os.path.exists(path):
        print('缺少引擎脚本 engine/%s —— 检查 skill 包是否完整。' % script)
        sys.exit(1)
    env = dict(os.environ)
    env['WORD_MIRROR_HOME'] = BASE
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, encoding='utf-8', env=env, **kw)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.returncode != 0:
        print(r.stderr[:500])
        sys.exit(1)
    return r

def _jsonl_count(p):
    if not os.path.exists(p):
        return 0
    return sum(1 for line in open(p, encoding='utf-8') if line.strip())

def _ledger_snapshot():
    """ingest 前快照：writebacks + 两层 promises 的行数，用于结束后确认没被清空。"""
    n_wb = _jsonl_count(os.path.join(DATA, 'user_writebacks.jsonl'))
    n_prom = sum(_jsonl_count(p) for p in _ledger_paths())
    return n_wb, n_prom

def cmd_ingest():
    before = _ledger_snapshot()
    steps = [
        ('提取你说的话', 'extract_all.py'),
        ('提取 AI 的回复', 'extract_ai.py'),
        # 去重要放在消费脚本之前——extract_all 产出未去重版，下面三个脚本都读 dedup 版
        ('去掉重复的', '_dedup'),
        ('拼会话卡', 'build_session_cards.py'),
        ('算数字底座（你的高频词/消息长度/分 agent 特征）', 'compute_stats.py'),
        ('挖素材（决定时刻/被问住的瞬间/月度切片/项目基因）', 'distill_materials.py'),
        ('挖照见候选（说vs做/反复/前后矛盾/口头禅漂移）', 'distill_insights.py'),
        ('渲染产物页面', 'generate_html_pages.py'),
    ]
    print('wm ingest · 开始（全程在你自己电脑上跑，数据不上传）')
    print('=' * 56)
    for i, (label, script) in enumerate(steps, 1):
        print('[%d/%d] %s ...' % (i, len(steps), label))
        if script == '_dedup':
            _dedup()
        else:
            run(script)
    # 汇报第一口糖
    _sugar_report()
    after = _ledger_snapshot()
    if after[0] < before[0] or after[1] < before[1]:
        print('警告：ingest 后 writebacks（%d→%d）/ promises（%d→%d）行数变少，疑似被清空或覆盖，请检查。' % (before[0], after[0], before[1], after[1]))
    print('=' * 56)
    print('完成。看结果：')
    print('  python wm.py open   （浏览器打开「翻给你看」入口页）')

def _dedup():
    src = os.path.join(DATA, 'corpus_all.jsonl')
    dst = os.path.join(DATA, 'corpus_dedup.jsonl')
    import re
    import hashlib
    seen, out = set(), []
    for line in open(src, encoding='utf-8'):
        o = json.loads(line)
        # 去重键 = 日期 + 全文归一化哈希。带日期：同一天的同内容才去重，跨日期的同内容保留（保住引文日期）
        k = hashlib.sha1((o.get('date', '') + '|' + re.sub(r'\s+', '', o['msg'])).encode('utf-8')).hexdigest()
        if k in seen:
            continue
        seen.add(k)
        out.append(o)
    with open(dst, 'w', encoding='utf-8') as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')
    print('     去掉重复后：共 %d 条' % len(out))

def _sugar_report():
    # 第一口糖：数字汇报 + 提示画像方向
    try:
        n = sum(1 for _ in open(os.path.join(DATA, 'corpus_dedup.jsonl'), encoding='utf-8'))
    except FileNotFoundError:
        return
    print()
    print('你跟 AI 说过的话：%d 条（重复的只算一次）' % n)
    if n < 500:
        print('（还不到 500 条——了解得还比较粗，先用着，以后会越来越全）')
    elif n < 3000:
        print('（中等量级：高频词和习惯已经很准，决定类文档开始有料）')
    else:
        print('（重度用户量级：全部产物都会很扎实）')

def cmd_vec(args):
    """语义检索入口。转发给 vecsearch.py（依赖 chromadb + sentence-transformers，本机跑）。"""
    sub = args[0] if args else 'status'
    rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vecsearch.py')
    r = subprocess.run([sys.executable, rp, sub] + args[1:])
    sys.exit(r.returncode)


def cmd_bind(args):
    """数据在别处时，用 bind 把两者接上。指针在 ~/wordmirror/bind.json。"""
    home = os.path.join(os.path.expanduser('~'), 'wordmirror')
    bind_p = os.path.join(home, 'bind.json')
    if args and args[0] == '--clear':
        if os.path.isfile(bind_p):
            os.remove(bind_p)
            print('已解绑：%s 已删除。定位回到默认顺序（见 references/data-locations.md）。' % bind_p)
        else:
            print('本来就没有绑定（%s 不存在）。' % bind_p)
        return
    if not args:
        print('用法：python wm.py bind <完整仓库根目录>   # 绑定已有数据（该目录下须有 data/）')
        print('      python wm.py bind --clear            # 解绑')
        return
    target = os.path.abspath(args[0])
    if not os.path.isdir(os.path.join(target, 'data')):
        print('%s 下面没有 data/——要指向完整仓库的根目录（里面应有 data/corpus_dedup.jsonl）。' % target)
        sys.exit(1)
    os.makedirs(home, exist_ok=True)
    with open(bind_p, 'w', encoding='utf-8') as f:
        json.dump({'home': target}, f, ensure_ascii=False)
    print('已绑定：%s（指针写在 %s）' % (target, bind_p))
    print('之后查旧话、生成网页、记账都用这份数据了。')
    print('解绑：python wm.py bind --clear')

def cmd_open():
    for name in ['index.html', '10_翻给你看.html']:
        p = os.path.join(PRODUCTS, 'html', name)
        if os.path.exists(p):
            webbrowser.open('file:///' + p.replace(chr(92), '/'))
            print('已打开：%s' % name)
            return
    print('产物页面不存在，先跑 python wm.py ingest')

def cmd_check():
    run('self_check.py')

# ===== 写回（"记住这个"——走命令保证格式，见 writeback-protocol.md 硬门槛）=====

def cmd_wb(args):
    if not args or args[0] not in ('add', 'list'):
        print('用法：python wm.py wb add "事实内容" --topic 主题 [--ref 依据] [--agent 工具名]')
        print('      python wm.py wb list           # 看已写回的事实')
        return
    wb_p = os.path.join(DATA, 'user_writebacks.jsonl')
    if args[0] == 'list':
        if not os.path.exists(wb_p):
            print('还没有写回记录。')
            return
        rows = []
        for i, line in enumerate(open(wb_p, encoding='utf-8'), 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                print('警告：第 %d 行不是合法 JSON，跳过' % i)
        for o in rows[-20:]:
            print('  %s | %-8s | %s' % (o.get('date', '?'), o.get('source', o.get('topic', '?')), o.get('msg', '')[:70]))
        if len(rows) > 20:
            print('  …（共 %d 条，显示最近 20 条）' % len(rows))
        return
    # add：解析 --topic/--ref/--agent 选项，其余为内容
    text, topic, ref, agent = [], 'general', '', 'cli'
    i = 1
    while i < len(args):
        if args[i] == '--topic' and i + 1 < len(args):
            topic = args[i + 1]; i += 2
        elif args[i] == '--ref' and i + 1 < len(args):
            ref = args[i + 1]; i += 2
        elif args[i] == '--agent' and i + 1 < len(args):
            agent = args[i + 1]; i += 2
        else:
            text.append(args[i]); i += 1
    msg = ' '.join(text).strip()
    if not msg:
        print('内容不能为空。用法：python wm.py wb add "事实内容" --topic 主题')
        sys.exit(1)
    os.makedirs(DATA, exist_ok=True)
    # 坏行拦截：写操作前确认现有文件每行都合法（写入不修复也不吞坏行）
    if os.path.exists(wb_p):
        for i, line in enumerate(open(wb_p, encoding='utf-8'), 1):
            line = line.strip()
            if line:
                try:
                    json.loads(line)
                except Exception:
                    print('写回文件 %s 第 %d 行不是合法 JSON。先手工修复或删掉那行，我不替你静默改账。' % (wb_p, i))
                    sys.exit(1)
    row = {'date': datetime.date.today().isoformat(), 'source': agent,
           'topic': topic, 'msg': msg, 'ref': ref or '用户当次确认'}
    with open(wb_p, 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('记下了：%s（%s）' % (msg, wb_p))



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
    print('另外，还记着 %d 件事一直没动，最老一件：' % len(st))
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
            print('没有还没做完的事。')
            _tracker_note(today)
            return
        rows.sort(key=lambda t: t[1].get('date', ''))
        tag_plain = {'全局账本': '全局', '项目账本': '这个目录'}
        print('还没做完的事 %d 件（从老到新）:' % len(rows))
        for tag, o in rows:
            days = (today - datetime.date.fromisoformat(o['date'])).days if o.get('date') else '?'
            print('  [%s] %s 记的（%d 天）| %s' % (tag_plain.get(tag, tag), o.get('date', '?'), days, o.get('text', '')))
        _tracker_note(today)
        return
    sub = args[0]
    if sub == 'add':
        # 解析 --agent 选项（可选），其余为要做的事
        text_parts, agent = [], 'cli'
        i = 1
        while i < len(args):
            if args[i] == '--agent' and i + 1 < len(args):
                agent = args[i + 1]; i += 2
            else:
                text_parts.append(args[i]); i += 1
        text = ' '.join(text_parts).strip()
        if not text:
            print('用法：python wm.py promise add 要做的事 [--agent 工具名]')
            sys.exit(1)
        pf = _promises_file()
        os.makedirs(os.path.dirname(pf), exist_ok=True)
        # 坏行拦截：写操作前确认现有文件每行都合法（写入不修复也不吞坏行），与 wb add 对齐
        if os.path.exists(pf):
            for i, line in enumerate(open(pf, encoding='utf-8'), 1):
                line = line.strip()
                if line:
                    try:
                        json.loads(line)
                    except Exception:
                        print('欠账本 %s 第 %d 行不是合法 JSON。先手工修复或删掉那行，我不替你静默改账。' % (pf, i))
                        sys.exit(1)
        row = {'date': datetime.date.today().isoformat(), 'text': text,
               'status': 'open', 'agent': agent}
        with open(pf, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
        print('记下了：%s（%s）' % (text, pf))
    elif sub in ('done', 'drop'):
        kw = ' '.join(args[1:]).strip()
        if not kw:
            print('必须给关键词，否则分不清要划哪笔。用法：python wm.py promise done 关键词')
            sys.exit(1)
        # 先扫两层账本，收集全部 open 命中项（先不划，避免静默划错）
        hits = []  # (pf, items, o)
        for pf in _ledger_paths():
            items = _load_promises(pf, strict=True)  # 写操作前严格查损，坏账本宁可停也不吞
            for o in items:
                if o.get('status') == 'open' and kw in o.get('text', ''):
                    hits.append((pf, items, o))
        if not hits:
            print('没找到开着的事里含「%s」的。' % kw)
            sys.exit(1)
        if len(hits) > 1:
            print('关键词「%s」命中 %d 条开着的事项——为避免划错，先停手不划。请用更精确的关键词重跑，或按下面清单确认要划哪条：' % (kw, len(hits)))
            for n, (pf, _, o) in enumerate(hits, 1):
                print('  %d) [%s] %s 记的（%s）| %s' % (n, _ledger_tag(pf), o.get('date', '?'), pf, o.get('text', '')))
            sys.exit(1)
        pf, items, hit = hits[0]
        hit['status'] = 'closed' if sub == 'done' else 'dropped'
        hit['closed_date'] = datetime.date.today().isoformat()
        with open(pf, 'w', encoding='utf-8') as f:
            for o in items:
                line = dict(o); line.pop('_line', None)
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
        print('划掉了：%s（%s）' % (hit['text'], pf))
        return
    else:
        print('用法：python wm.py promise / promise add 文本 / promise done 关键词')

def cmd_monthly(args):
    """月度三页纸：渲染是 skill 自带能力（scripts/render.py），不再依赖 engine。"""
    month = args[0] if args and re.match(r'\d{4}-\d{2}$', args[0]) else None
    rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render.py')
    r = subprocess.run([sys.executable, rp, 'monthly'] + ([month] if month else []))
    sys.exit(r.returncode)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == 'ingest':
        cmd_ingest()
    elif cmd == 'open':
        cmd_open()
    elif cmd == 'check':
        cmd_check()
    elif cmd == 'promise':
        cmd_promise(sys.argv[2:])
    elif cmd == 'bind':
        cmd_bind(sys.argv[2:])
    elif cmd == 'vec':
        cmd_vec(sys.argv[2:])
    elif cmd == 'wb':
        cmd_wb(sys.argv[2:])
    elif cmd == 'monthly':
        cmd_monthly(sys.argv[2:])
    else:
        print('不认识的命令：%s' % cmd)
        print(__doc__)

if __name__ == '__main__':
    main()
