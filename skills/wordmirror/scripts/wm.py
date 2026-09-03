# -*- coding: utf-8 -*-
"""wm · 言镜（wordmirror）——记账/写回 + 按意思搜 + 数据绑定的命令行工具。

查旧话、看数据、出报告、提取存档，这些活 AI 按 SKILL.md / references 自己干（逐个脚本跑），
不在这做编排。这里只留 AI 干不了、或必须保格式的命令：

记账 / 写回（只走命令，保证格式对、坏行拦得住）：
    python wm.py promise           看说过要做的事
    python wm.py promise add 要做的事 / promise done 关键词 / promise drop 关键词
    python wm.py wb add "事实" --topic 主题 [--agent 工具名]   记下一条确认过的事
    python wm.py wb list           看记下的事

按意思搜（向量，AI 现场算不了）：
    python wm.py vec build [--update] / vec query "问题" / vec status

数据绑定（数据在别处时接上）：
    python wm.py bind <仓库根> / bind --clear

设计原则（references/DESIGN.md）：每人自己跑自己的；数据全程在自己电脑上；不写死路径。
"""
import os, sys, subprocess, json, datetime, re

from _common import BASE, BASE_SOURCE, DATA, PRODUCTS, WORDS, topic, read_jsonl, valid_date

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


def cmd_vec(args):
    """语义检索入口。转发给 vecsearch.py（依赖 chromadb + sentence-transformers，本机跑）。"""
    sub = args[0] if args else 'status'
    rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vecsearch.py')
    r = subprocess.run([sys.executable, rp, sub] + args[1:])
    sys.exit(r.returncode)


def cmd_bind(args):
    """数据在别处时，用 bind 把两者接上。指针在 ~/.wordmirror/bind.json。"""
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
        # 解析可选元数据 --agent/--date/--proj/--ref，其余为要做的事
        text_parts, agent, src_date, proj, ref = [], 'cli', '', '', ''
        i = 1
        while i < len(args):
            if args[i] == '--agent' and i + 1 < len(args):
                agent = args[i + 1]; i += 2
            elif args[i] == '--date' and i + 1 < len(args):
                src_date = args[i + 1]; i += 2
            elif args[i] == '--proj' and i + 1 < len(args):
                proj = args[i + 1]; i += 2
            elif args[i] == '--ref' and i + 1 < len(args):
                ref = args[i + 1]; i += 2
            else:
                text_parts.append(args[i]); i += 1
        text = ' '.join(text_parts).strip()
        if not text:
            print('用法：python wm.py promise add 要做的事 [--agent 工具名] [--date 原始日期] [--proj 项目] [--ref 原话]')
            sys.exit(1)
        if src_date and not valid_date(src_date):
            print('原始日期必须是有效的 YYYY-MM-DD。')
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
        row = {'date': src_date or datetime.date.today().isoformat(), 'text': text,
               'status': 'open', 'agent': agent}
        if proj:
            row['proj'] = proj
        if ref:
            row['ref'] = ref
        with open(pf, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
        print('记下了：%s（%s）' % (text, pf))
    elif sub == 'revise':
        kw_parts, updates = [], {}
        i = 1
        while i < len(args):
            if args[i] in ('--date', '--proj', '--ref') and i + 1 < len(args):
                key = {'--date': 'date', '--proj': 'proj', '--ref': 'ref'}[args[i]]
                updates[key] = args[i + 1]
                i += 2
            else:
                kw_parts.append(args[i]); i += 1
        kw = ' '.join(kw_parts).strip()
        # 仅用于修正已登记事项的来源元数据，不改变状态或历史原话
        if not kw or not updates:
            print('用法：python wm.py promise revise 关键词 [--date 原始日期] [--proj 项目] [--ref 原话]')
            sys.exit(1)
        if 'date' in updates and not valid_date(updates['date']):
            print('原始日期必须是有效的 YYYY-MM-DD。')
            sys.exit(1)
        hits = []
        for pf in _ledger_paths():
            items = _load_promises(pf, strict=True)
            for o in items:
                if kw in o.get('text', ''): hits.append((pf, items, o))
        if len(hits) != 1:
            print('关键词命中 %d 条，未修改；请使用能唯一定位事项的关键词。' % len(hits))
            sys.exit(1)
        pf, items, hit = hits[0]
        hit.update(updates)
        with open(pf, 'w', encoding='utf-8') as f:
            for o in items:
                line = dict(o); line.pop('_line', None)
                f.write(json.dumps(line, ensure_ascii=False) + '\n')
        print('已修正：%s（%s）' % (hit['text'], pf))
        return
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

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == 'promise':
        cmd_promise(sys.argv[2:])
    elif cmd == 'bind':
        cmd_bind(sys.argv[2:])
    elif cmd == 'vec':
        cmd_vec(sys.argv[2:])
    elif cmd == 'wb':
        cmd_wb(sys.argv[2:])
    else:
        print('不认识的命令：%s' % cmd)
        print(__doc__)

if __name__ == '__main__':
    main()
