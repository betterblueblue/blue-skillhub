# -*- coding: utf-8 -*-
"""ds · 言镜（wordmirror）命令行入口。

用法：
    python ds.py init    探测你机器上有哪些 agent 的存档
    python ds.py ingest  全流程：提取你说过的话 → 去掉重复的 → 生成网页
    python ds.py ask "问题关键词"   在你说过的话里搜
    python ds.py contrast "话题"    这个话题最早和最近的说法并排看
    python ds.py promise           看说过要做的事（哪些还没做完）
    python ds.py promise add 要做的事 / promise done 关键词
    python ds.py wb add "事实" --topic 主题   记下一条你确认过的事（--ref 附依据）
    python ds.py wb list           看记下的事
    python ds.py export            生成随身说明书（只含能公开的内容，完整情况不外发）
    python ds.py install <目录>    把 skill 包装进指定 skills 目录（--all 自动找）
    python ds.py monthly [YYYY-MM] 生成这个月的报告
    python ds.py open    用浏览器打开首页
    python ds.py check   跑一遍自检（检查项看输出）
    python ds.py where   显示数据放在哪、你的情况多久没更新、怎么找到的
    python ds.py bind <仓库根>  把已有完整仓库的数据接上（--clear 取消）
    python ds.py vec build [--update]  建/更新按意思搜的索引（在你自己电脑上，见 scripts/vecsearch.py）
    python ds.py vec status        看按意思搜的索引状态

设计原则（DESIGN.md）：每人自己跑自己的；数据全程在自己电脑上；不写死路径。
"""
import os, sys, subprocess, json, webbrowser, glob, re, shutil, datetime

# 定位两层（data-locations.md 的同款顺序）：
# 全局层（画像/语料/月报——"你是谁"，不分项目）：
#   1) 环境变量 WORD_MIRROR_HOME（旧名 DIGITAL_SELF_HOME 兼容）
#   2) bind 指针 ~/.wordmirror/bind.json（ds.py bind 写入——skill 装在别处、数据在完整仓库时用）
#   3) ~/.wordmirror（旧 ~/.digital-self 兼容）
#   4) 脚本祖先逐级向上找仓库布局（data/ 下有语料签名才算，防无关 data/ 目录劫持）
#   5) 都没有 → 默认 ~/.wordmirror，首次写入时自动创建
# 项目层（欠账/写回——"这个项目的事"）：<当前目录>/.wordmirror/，在哪个目录干活账记哪
def _find_base():
    """返回 (数据仓库根, 定位方式说明)。"""
    def _has_data(p):
        return os.path.isdir(os.path.join(p, 'data'))
    env = os.environ.get('WORD_MIRROR_HOME') or os.environ.get('DIGITAL_SELF_HOME')
    if env and _has_data(env):
        how = 'WORD_MIRROR_HOME' if os.environ.get('WORD_MIRROR_HOME') else 'DIGITAL_SELF_HOME'
        return env, '环境变量 %s' % how
    home = os.path.join(os.path.expanduser('~'), '.wordmirror')
    bind_p = os.path.join(home, 'bind.json')
    if os.path.isfile(bind_p):
        try:
            target = json.load(open(bind_p, encoding='utf-8')).get('home', '')
        except Exception:
            target = ''
        if target and _has_data(target):
            return target, 'bind 指针（%s）' % bind_p
    if _has_data(home):
        return home, '标准位置 ~/.wordmirror'
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
    return home, '默认 ~/.wordmirror（还没有数据，首次写入时创建）'

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
    print('ds ingest · 开始（全程在你自己电脑上跑，数据不上传）')
    print('=' * 56)
    for i, (label, script) in enumerate(steps, 1):
        print('[%d/%d] %s ...' % (i, len(steps), label))
        run(script)
    # 去重步骤（extract_all 产出未去重版，这里生成主力文件）
    print('[%d/%d] 去掉重复的 ...' % (len(steps), len(steps)))
    _dedup()
    # 汇报第一口糖
    _sugar_report()
    print('=' * 56)
    print('完成。看结果：')
    print('  python ds.py open   （浏览器打开「翻给你看」入口页）')

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
        print('（中等量级：口头禅和习惯已经很准，决定类文档开始有料）')
    else:
        print('（重度用户量级：全部产物都会很扎实）')

def _load_synonyms():
    """近义词组：内置常见组 + 数据目录 synonyms.json 用户自扩（格式 {"词": ["近义词", ...]}）。
    纯字面 grep 记不住原词就查不到——这层扩词是廉价补丁，不是语义检索。"""
    groups = [
        ['求职', '找工作', '投简历', '面试'],
        ['放弃', '不做了', '算了', '弃了', '砍了'],
        ['决定', '定了', '拍板', '敲定'],
        ['简历', 'CV'],
        ['备考', '复习', '学习'],
        ['测试', '单测', '回归'],
        ['部署', '上线', '发布'],
        ['离职', '辞职'],
    ]
    p = os.path.join(DATA, 'synonyms.json')
    if os.path.exists(p):
        try:
            with open(p, encoding='utf-8') as f:
                for k, vs in json.load(f).items():
                    groups.append([k] + list(vs))
        except Exception:
            pass
    return groups

def _expand_query(q):
    """把查询词扩成近义词组（原词永远排第一）。查不到 synonyms.json 就只有原词。"""
    words = [q]
    for g in _load_synonyms():
        if q in g:
            words += [w for w in g if w != q]
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out

def cmd_vec(args):
    """语义检索入口。转发给 vecsearch.py（依赖 chromadb + sentence-transformers，本机跑）。"""
    sub = args[0] if args else 'status'
    rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vecsearch.py')
    r = subprocess.run([sys.executable, rp, sub] + args[1:])
    sys.exit(r.returncode)


def cmd_ask(query):
    if not query:
        print('用法：python ds.py ask "关键词"')
        sys.exit(1)
    # 语义优先：有索引走向量检索（问法和原话字面不同也能命中），没索引/查询失败降回关键词+近义词。
    # 短查询（1-2 字）语义区分度差，直接走关键词。
    try:
        import vecsearch
        hits = vecsearch.query(query) if len(query) > 2 else None
    except Exception:
        hits = None
    if hits:
        print('按意思搜到 %d 条（越相关排越前）:' % len(hits))
        for h in hits:
            tag = '写回' if h['src'] == 'user_writebacks.jsonl' else '原话'
            print('  %.2f | %s | %-10s | %s | %s' % (h['score'], h['date'], h['agent'], tag, h['msg'][:110]))
        print('（按意思相近排的，问题写具体一点更准；想按字面找，直接搜文件即可）')
        return
    _ask_keyword(query)


def _ask_keyword(query):
    # 关键词检索：跨两个主力文件；查询词自动带近义词组（用户记不住自己当时的原词是常态）
    variants = _expand_query(query)
    hits = []
    for f in ['corpus_dedup.jsonl', 'user_writebacks.jsonl']:
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            if any(v.lower() in line.lower() for v in variants):
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
    if len(variants) > 1:
        print('（「%s」也搜了近义词：%s）' % (query, '、'.join(variants[1:])))
    for o in hits[-15:]:
        msg = o.get('msg', '').replace(chr(10), ' ')[:110]
        print('  %s | %-10s | %s' % (o.get('date', '?'), o.get('agent', o.get('source', '?')), msg))
    if len(hits) > 15:
        print('  …（共 %d 条，只显示最近 15 条）' % len(hits))

def cmd_bind(args):
    """skill 装在 A 处、数据在 B 处（完整仓库）时，用 bind 把两者接上。指针在 ~/.wordmirror/bind.json。"""
    home = os.path.join(os.path.expanduser('~'), '.wordmirror')
    bind_p = os.path.join(home, 'bind.json')
    if args and args[0] == '--clear':
        if os.path.isfile(bind_p):
            os.remove(bind_p)
            print('已解绑：%s 已删除。定位回到默认顺序（见 references/data-locations.md）。' % bind_p)
        else:
            print('本来就没有绑定（%s 不存在）。' % bind_p)
        return
    if not args:
        print('用法：python ds.py bind <完整仓库根目录>   # 绑定已有数据（该目录下须有 data/）')
        print('      python ds.py bind --clear            # 解绑')
        return
    target = os.path.abspath(args[0])
    if not os.path.isdir(os.path.join(target, 'data')):
        print('%s 下面没有 data/——要指向完整仓库的根目录（里面应有 data/corpus_dedup.jsonl）。' % target)
        sys.exit(1)
    os.makedirs(home, exist_ok=True)
    with open(bind_p, 'w', encoding='utf-8') as f:
        json.dump({'home': target}, f, ensure_ascii=False)
    print('已绑定：%s（指针写在 %s）' % (target, bind_p))
    print('验证：python ds.py where   （定位方式应显示 bind 指针）')
    print('解绑：python ds.py bind --clear')

def cmd_open():
    for name in ['index.html', '10_翻给你看.html']:
        p = os.path.join(PRODUCTS, 'html', name)
        if os.path.exists(p):
            webbrowser.open('file:///' + p.replace(chr(92), '/'))
            print('已打开：%s' % name)
            return
    print('产物页面不存在，先跑 python ds.py ingest')

def cmd_check():
    run('self_check.py')

def cmd_where():
    print('数据放在：%s' % DATA)
    print('找到数据的方式：%s' % BASE_SOURCE)
    print('生成的网页在：%s' % PRODUCTS)
    cwd = os.getcwd()
    if os.path.normcase(os.path.abspath(cwd)) != os.path.normcase(os.path.abspath(BASE)):
        proj = os.path.join(cwd, '.wordmirror', 'promises.jsonl')
        mark = '（已有记录）' if os.path.exists(proj) else '（第一次记时才建）'
        print('这个目录记的事：%s %s' % (os.path.dirname(proj), mark))
    n = _try_count()
    print('你说过的话：%s' % (n if n else '（还没跑过 ingest）'))
    info = _profile_age()
    if info:
        days, d = info
        tip = '今天刚更新' if days == 0 else ('已 %d 天，该补最近的情况了' % days if days > 30 else '已 %d 天' % days)
        print('你的情况整理于：%s（%s）' % (d, tip))
    else:
        print('你的情况：还没有，先跑 ingest 再让 AI 整理')

def _profile_age():
    """从 portrait.md 顶部拿第一个日期，算画像多少天没更新。"""
    p = os.path.join(DATA, 'profile', 'portrait.md')
    if not os.path.exists(p):
        return None
    m = re.search(r'(\d{4}-\d{2}-\d{2})', open(p, encoding='utf-8', errors='replace').read())
    if not m:
        return None
    d = datetime.date.fromisoformat(m.group(1))
    return (datetime.date.today() - d).days, m.group(1)

# ===== 写回（"记住这个"——走命令保证格式，见 writeback-protocol.md 硬门槛）=====

def cmd_wb(args):
    if not args or args[0] not in ('add', 'list'):
        print('用法：python ds.py wb add "事实内容" --topic 主题 [--ref 依据]')
        print('      python ds.py wb list           # 看已写回的事实')
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
    # add：解析 --topic/--ref 选项，其余为内容
    text, topic, ref = [], 'general', ''
    i = 1
    while i < len(args):
        if args[i] == '--topic' and i + 1 < len(args):
            topic = args[i + 1]; i += 2
        elif args[i] == '--ref' and i + 1 < len(args):
            ref = args[i + 1]; i += 2
        else:
            text.append(args[i]); i += 1
    msg = ' '.join(text).strip()
    if not msg:
        print('内容不能为空。用法：python ds.py wb add "事实内容" --topic 主题')
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
    row = {'date': datetime.date.today().isoformat(), 'source': 'cli',
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
    variants = _expand_query(query)
    hits = []
    for f in ['corpus_dedup.jsonl', 'user_writebacks.jsonl']:
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            if any(v.lower() in line.lower() for v in variants):
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
    if len(variants) > 1:
        print('（也搜了近义词：%s）' % '、'.join(variants[1:]))
    show(first, '最早')
    show(last, '最近')
    print('（中间变没变、为什么变，你自己判断——AI 不下结论）')

def cmd_export():
    """随身说明书：只出脱敏后的公开层——贴给任何 AI 的东西绝不含画像全文（references/privacy-rules.md）。"""
    pub_p = os.path.join(DATA, 'layers', 'public.md')
    pub = open(pub_p, encoding='utf-8', errors='replace').read().strip() if os.path.exists(pub_p) else ''
    if len(pub) < 40:  # 只剩模板头也算空
        print('能对外的那份内容（data/layers/public.md）还没有——对外只能用这份，不能把你的完整情况发出去。')
        print('先让 AI 按隐私规矩（references/privacy-rules.md）从你的情况里整理出那份内容，再跑 export。')
        sys.exit(1)
    out = os.path.join(PRODUCTS, 'ME_随身说明书.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('# 我的说明书（言镜导出，%s）\n\n' % datetime.date.today().isoformat())
        f.write('> 把下面整段贴给任何 AI 对话的开头，它就认识我了。\n')
        f.write('> 这份只放能公开的内容：真实姓名、公司、薪资这些，都已经去掉或换成代词了。\n\n---\n\n')
        f.write(pub)
        f.write('\n')
    print('已生成：%s（只含能公开的内容）' % out)
    print('用法：打开，复制全文，贴到任何 AI 对话的开头。')

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
    """月度三页纸：渲染是 skill 自带能力（scripts/render.py），不再依赖 engine。"""
    month = args[0] if args and re.match(r'\d{4}-\d{2}$', args[0]) else None
    rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render.py')
    r = subprocess.run([sys.executable, rp, 'monthly'] + ([month] if month else []))
    sys.exit(r.returncode)

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
