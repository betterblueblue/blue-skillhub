# -*- coding: utf-8 -*-
"""统一提取管道：13 个 agent 的用户原话 -> corpus_all.jsonl
输出格式: {agent, date, proj, sid, msg}"""
import json, os, glob, re, sqlite3, datetime

H = os.path.expanduser('~')
import os
BASE = os.environ.get('WORD_MIRROR_HOME') or os.path.expanduser(os.path.join('~', '.wordmirror'))
OUT = os.path.join(BASE, 'data', 'corpus_all.jsonl')

BOILER_PREFIX = (
    '# AGENTS.md', '# Context from my IDE setup', 'The following is the Codex agent history',
    'The Codex agent has requested', '>>> APPROVAL', 'Assess the exact planned action',
    'Planned action JSON', '>>> TRANSCRIPT', '<subagent_notification',
    '<in-app-browser-context', '<codex_internal_context', '<environment_context',
    '<turn_aborted', 'Reviewed Codex session id', '</image', '<image ',
    '<local-command-caveat', '<command-name>', '<system-reminder', '[Request interrupted',
    '<skill name=', 'You are AtomCode', '# Apps are currently in',
    'The approval policy changed',  # dsh 把审批策略变更也注入 user/message，非用户原话
)

def clean(m):
    m = m.strip()
    if not m: return None
    for key in ('## My request for Codex:', '## My request for Qoder:'):
        if key in m:
            m = m.split(key, 1)[1].strip()
    if not m: return None
    for p in BOILER_PREFIX:
        if m.startswith(p): return None
    if m.startswith('{') and ('"command"' in m[:300] or '"cwd"' in m[:300] or '"arguments"' in m[:300]): return None
    if m.startswith('|# Files mentioned') or m.startswith('|<in-app-browser'): return None
    if re.match(r'^\[\d+\] (tool|assistant)', m): return None
    if re.match(r'^<[\w-]+[ >]', m): return None
    m2 = re.sub(r'^\[\$[\w-]+\]\([^)]*\)\s*', '', m)
    return m2.strip() or None

def write(out, agent, date, proj, sid, msg):
    if msg and len(msg) >= 2:
        out.write(json.dumps({'agent': agent, 'date': date, 'proj': proj, 'sid': sid, 'msg': msg}, ensure_ascii=False) + '\n')
        return 1
    return 0

def d2s(ts):
    try:
        if isinstance(ts, (int, float)) and ts:
            return datetime.datetime.fromtimestamp(ts/1000 if ts > 1e12 else ts).strftime('%Y-%m-%d')
        return str(ts)[:10] if ts else ''
    except Exception:
        return ''

stats = {}
def rec(agent, n, files):
    stats[agent] = (n, files)

def ex_codex(out):
    n = f = 0
    base = os.path.join(H, '.codex', 'sessions')
    for year in sorted(os.listdir(base)):
        yd = os.path.join(base, year)
        if not os.path.isdir(yd): continue
        for month in sorted(os.listdir(yd)):
            md = os.path.join(yd, month)
            if not os.path.isdir(md): continue
            for day in sorted(os.listdir(md)):
                dd = os.path.join(md, day)
                if not os.path.isdir(dd): continue
                for fn in os.listdir(dd):
                    if not fn.endswith('.jsonl'): continue
                    f += 1
                    sid = cwd = None
                    for line in open(os.path.join(dd, fn), encoding='utf-8', errors='replace'):
                        try: o = json.loads(line)
                        except Exception: continue
                        t, p = o.get('type'), o.get('payload', {})
                        if t == 'session_meta':
                            sid, cwd = p.get('id'), p.get('cwd'); continue
                        if t == 'event_msg' and p.get('type') == 'user_message':
                            m = p.get('message')
                            if isinstance(m, str):
                                n += write(out, 'codex', d2s(o.get('timestamp','')), cwd, sid, clean(m))
    rec('codex', n, f)

def ex_claude(out):
    n = f = 0
    for path in glob.glob(os.path.join(H, '.claude', 'projects', '*', '*.jsonl')):
        f += 1
        proj = os.path.basename(os.path.dirname(path))
        sid = os.path.splitext(os.path.basename(path))[0]
        for line in open(path, encoding='utf-8', errors='replace'):
            try: o = json.loads(line)
            except Exception: continue
            if o.get('type') != 'user': continue
            c = o.get('message', {}).get('content')
            texts = []
            if isinstance(c, str): texts.append(c)
            elif isinstance(c, list):
                for part in c:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        texts.append(part.get('text',''))
            for t in texts:
                n += write(out, 'claude-code', d2s(o.get('timestamp','')), proj, sid, clean(t))
    rec('claude-code', n, f)

def ex_qwen(out):
    n = f = 0
    for path in glob.glob(os.path.join(H, '.qwen', 'projects', '*', 'chats', '*.jsonl')):
        f += 1
        proj = os.path.basename(os.path.dirname(os.path.dirname(path)))
        sid = os.path.splitext(os.path.basename(path))[0]
        for line in open(path, encoding='utf-8', errors='replace'):
            try: o = json.loads(line)
            except Exception: continue
            if o.get('type') != 'user': continue
            texts = []
            msg = o.get('message', {})
            c = msg.get('content')
            if isinstance(c, str): texts.append(c)
            elif isinstance(c, list):
                for part in c:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        texts.append(part.get('text',''))
            for part in (msg.get('parts') or []):
                if isinstance(part, dict) and isinstance(part.get('text'), str):
                    texts.append(part['text'])
            for t in texts:
                n += write(out, 'qwen', d2s(o.get('timestamp','')), o.get('cwd') or proj, sid, clean(t))
    rec('qwen', n, f)

def ex_workbuddy(out):
    n = f = 0
    for path in glob.glob(os.path.join(H, '.workbuddy', 'projects', '*', '*.jsonl')):
        f += 1
        proj = os.path.basename(os.path.dirname(path))
        sid = os.path.splitext(os.path.basename(path))[0]
        for line in open(path, encoding='utf-8', errors='replace'):
            try: o = json.loads(line)
            except Exception: continue
            if o.get('type') != 'message' or o.get('role') != 'user': continue
            texts = []
            for part in o.get('content', []):
                if isinstance(part, dict) and isinstance(part.get('text'), str):
                    texts.append(part['text'])
            m = '\n'.join(texts)
            m = re.sub(r'<system-reminder.*?</system-reminder>', ' ', m, flags=re.S)
            m = re.sub(r'<cb_summary>.*?</cb_summary>', ' ', m, flags=re.S)
            m = re.sub(r'<user_query>(.*?)</user_query>', r'\1', m, flags=re.S)
            m = re.sub(r'<previous_assistant_message>.*?</previous_assistant_message>', ' ', m, flags=re.S)
            n += write(out, 'workbuddy', d2s(o.get('timestamp','')), proj, sid, clean(m))
    rec('workbuddy', n, f)

def ex_zcode(out):
    n = 0
    try:
        con = sqlite3.connect(os.path.join(H, '.zcode', 'cli', 'db', 'db.sqlite'))
        cur = con.cursor()
        # user message id 集合（message.data 只有元数据，正文在 part 表）
        user_msgs, msg_sess, msg_time = {}, {}, {}
        for (mid, sid, tc, data) in cur.execute('select id, session_id, time_created, data from message'):
            try: o = json.loads(data)
            except Exception: continue
            if o.get('role') == 'user':
                user_msgs[mid] = True
                msg_sess[mid] = sid
                msg_time[mid] = tc
        sess_proj = {}
        for (sid, d) in cur.execute('select id, directory from session'):
            sess_proj[sid] = d or ''
        for (pid, mid, sid, tc, data) in cur.execute('select id, message_id, session_id, time_created, data from part'):
            if mid not in user_msgs: continue
            try: o = json.loads(data)
            except Exception: continue
            t = o.get('text')
            if isinstance(t, str) and t.strip():
                m = re.sub(r'<system-reminder.*?</system-reminder>', ' ', t, flags=re.S)
                n += write(out, 'zcode', d2s(msg_time.get(mid) or tc), sess_proj.get(sid, sid[:8]), sid, clean(m))
    except Exception as e:
        print('zcode err', e)
    rec('zcode', n, 1)

def ex_grok(out):
    n = 0
    path = os.path.join(H, '.grok', 'logs', 'unified.jsonl')
    if not os.path.exists(path):
        return rec('grok', 0, 0)
    for line in open(path, encoding='utf-8', errors='replace'):
        try: o = json.loads(line)
        except Exception: continue
        if o.get('src') != 'shell': continue
        ctx = o.get('ctx', {})
        if isinstance(ctx, dict) and ctx.get('prompt_text'):
            n += write(out, 'grok', d2s(o.get('ts','')), 'grok', str(o.get('sid','')), clean(str(ctx['prompt_text'])))
    rec('grok', n, 1)

def ex_pi(out):
    n = f = 0
    for path in glob.glob(os.path.join(H, '.pi', 'agent', 'sessions', '*', '*.jsonl')):
        f += 1
        proj = os.path.basename(os.path.dirname(path))
        for line in open(path, encoding='utf-8', errors='replace'):
            try: o = json.loads(line)
            except Exception: continue
            if o.get('type') != 'message': continue
            msg = o.get('message', {})
            if msg.get('role') != 'user': continue
            texts = []
            for part in msg.get('content', []):
                if isinstance(part, dict) and part.get('type') == 'text':
                    texts.append(part.get('text',''))
            n += write(out, 'pi', d2s(o.get('timestamp','')), proj, str(o.get('id','')), clean('\n'.join(texts)))
    rec('pi', n, f)

def ex_atomcode(out):
    n = f = 0
    for path in glob.glob(os.path.join(H, '.atomcode', 'datalog', '*', '*.jsonl')):
        f += 1
        proj = os.path.basename(os.path.dirname(path))
        base = os.path.splitext(os.path.basename(path))[0]
        date = base[:10]
        for line in open(path, encoding='utf-8', errors='replace'):
            try: o = json.loads(line)
            except Exception: continue
            for msg in o.get('messages', []):
                if str(msg.get('role', '')).lower() != 'user': continue
                c = msg.get('content', {})
                t = c.get('Text') if isinstance(c, dict) else None
                if t:
                    n += write(out, 'atomcode', date, proj, base, clean(t))
    rec('atomcode', n, f)

def ex_antigravity(out):
    # 数据源：brain transcript.jsonl（明文，type=USER_INPUT 即用户原话）；conversations/*.db 是 protobuf 二进制，弃用
    n = f = 0
    for tf in glob.glob(os.path.join(H, '.gemini', 'antigravity', 'brain', '*', '.system_generated', 'logs', 'transcript.jsonl')):
        f += 1
        cid = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(tf))))
        for line in open(tf, encoding='utf-8', errors='replace'):
            try: o = json.loads(line)
            except Exception: continue
            if o.get('type') != 'USER_INPUT': continue
            c = o.get('content', '')
            if not isinstance(c, str) or not c.strip(): continue
            c = re.sub(r'^<USER_REQUEST>\s*', '', c).strip()
            c = re.sub(r'</USER_REQUEST>.*$', '', c, flags=re.S).strip()
            n += write(out, 'antigravity', d2s(o.get('created_at', '')), cid[:8], cid, clean(c))
    rec('antigravity', n, f)

def ex_catpaw(out):
    # CatPaw IDE 版：transcript.txt 里 user:\n<user_query>...</user_query> 是用户原话；
    # assistant: 后面是 AI 回复，[Thinking]/[Tool call]/[Tool result] 是内部过程（跳过）。
    # transcript 无逐条时间戳 → 日期用文件 mtime 近似（会话文件的最后改动时间）。
    n = f = 0
    base = os.path.join(H, '.catpaw', 'projects')
    if not os.path.isdir(base):
        return rec('catpaw', 0, 0)
    for proj_dir in os.listdir(base):
        pd = os.path.join(base, proj_dir)
        if not os.path.isdir(pd):
            continue
        for sess_dir in os.listdir(pd):
            tf = os.path.join(pd, sess_dir, 'agent-transcripts', 'transcript.txt')
            if not os.path.isfile(tf):
                continue
            f += 1
            # 项目目录名形如 'idee--agent-反代'，取 '--' 之后的部分
            proj = proj_dir.split('--', 1)[1] if '--' in proj_dir else proj_dir
            sid = sess_dir
            date = datetime.date.fromtimestamp(os.path.getmtime(tf)).strftime('%Y-%m-%d')
            buf = []
            in_user = False
            for line in open(tf, encoding='utf-8', errors='replace'):
                st = line.strip()
                if st == 'user:':
                    if in_user and buf:
                        m = clean('\n'.join(buf))
                        if m:
                            n += write(out, 'catpaw', date, proj, sid, m)
                    in_user = True
                    buf = []
                    continue
                if st == 'assistant:' or st.startswith('[Thinking]') or st.startswith('[Tool call]') or st.startswith('[Tool result]'):
                    if in_user and buf:
                        m = clean('\n'.join(buf))
                        if m:
                            n += write(out, 'catpaw', date, proj, sid, m)
                    in_user = False
                    buf = []
                    continue
                if in_user:
                    t = st
                    if t == '<user_query>' or t == '</user_query>':
                        continue
                    if t.startswith('<user_query>'):
                        t = t[len('<user_query>'):].strip()
                    if t.endswith('</user_query>'):
                        t = t[:-len('</user_query>')].strip()
                    if t:
                        buf.append(t)
            if in_user and buf:
                m = clean('\n'.join(buf))
                if m:
                    n += write(out, 'catpaw', date, proj, sid, m)
    rec('catpaw', n, f)

def ex_dsh(out):
    # DeepSeek Harness：~/.dsh/sessions/*/*/session.jsonl.zstd（zstd 压缩 jsonl）。
    # 用户原话 = type=user/message 的 data.content[].text；session 行给 cwd（项目）和 id。
    n = f = 0
    base = os.path.join(H, '.dsh', 'sessions')
    if not os.path.isdir(base):
        return rec('dsh', 0, 0)
    try:
        import zstandard
    except ImportError:
        print('dsh 跳过：缺 zstandard，先 pip install zstandard 再跑')
        return rec('dsh', 0, 0)
    dctx = zstandard.ZstdDecompressor()
    for proj_dir in os.listdir(base):
        pd = os.path.join(base, proj_dir)
        if not os.path.isdir(pd):
            continue
        for sess_dir in os.listdir(pd):
            sf = os.path.join(pd, sess_dir, 'session.jsonl.zstd')
            if not os.path.isfile(sf):
                continue
            f += 1
            sid = sess_dir
            proj = proj_dir.strip('-')
            try:
                with open(sf, 'rb') as fh:
                    with dctx.stream_reader(fh) as r:
                        data = r.read()
            except Exception:
                continue
            for ln in data.decode('utf-8', 'replace').splitlines():
                try:
                    o = json.loads(ln)
                except Exception:
                    continue
                t = o.get('type')
                if t == 'session':
                    cwd = o.get('cwd', '')
                    if cwd:
                        proj = os.path.basename(cwd.rstrip('\\/'))
                    continue
                if t == 'user/message':
                    texts = []
                    for part in (o.get('data') or {}).get('content', []):
                        if isinstance(part, dict) and part.get('type') == 'text':
                            texts.append(part.get('text', ''))
                    m = clean('\n'.join(texts))
                    if m:
                        n += write(out, 'dsh', d2s(o.get('time', '')), proj, sid, m)
    rec('dsh', n, f)

def ex_cursor(out):
    # Cursor：%APPDATA%\Cursor\User\{globalStorage,workspaceStorage}\state.vscdb（sqlite）。
    # 气泡在 cursorDiskKV 表：key=bubbleId:<composerId>:<bubbleId>，value JSON，
    # type=1 用户 / type=2 AI，正文在 richText（ProseMirror JSON，递归取 text 节点），
    # createdAt 是 ISO 日期；会话头 composerHeaders 给 composerId -> workspaceId 映射。
    n = f = 0
    bases = []
    appdata = os.environ.get('APPDATA')
    if appdata:
        bases.append(os.path.join(appdata, 'Cursor', 'User'))
    bases += [
        os.path.join(H, 'Library', 'Application Support', 'Cursor', 'User'),  # macOS
        os.path.join(H, '.config', 'Cursor', 'User'),                          # Linux
        os.path.join(H, 'AppData', 'Roaming', 'Cursor', 'User'),               # Windows 兜底
    ]

    def _texts(node, acc):
        if isinstance(node, dict):
            t = node.get('text')
            if isinstance(t, str):
                acc.append(t)
            for v in node.values():
                _texts(v, acc)
        elif isinstance(node, list):
            for v in node:
                _texts(v, acc)

    dbs = []
    for base in bases:
        if not os.path.isdir(base):
            continue
        g = os.path.join(base, 'globalStorage', 'state.vscdb')
        if os.path.isfile(g):
            dbs.append(g)
        ws = os.path.join(base, 'workspaceStorage')
        if os.path.isdir(ws):
            for d in os.listdir(ws):
                p = os.path.join(ws, d, 'state.vscdb')
                if os.path.isfile(p):
                    dbs.append(p)
    if not dbs:
        return rec('cursor', 0, 0)
    for db in dbs:
        f += 1
        cid_ws = {}
        try:
            con = sqlite3.connect(db)
            cur = con.cursor()
            try:
                for cid, wsid in cur.execute('select composerId, workspaceId from composerHeaders'):
                    cid_ws[cid] = wsid or ''
            except Exception:
                pass
            try:
                cur.execute("select key, value from cursorDiskKV where key like 'bubbleId:%' and value is not null")
                rows = cur.fetchall()
            except Exception:
                rows = []
            con.close()
        except Exception:
            continue
        for key, val in rows:
            s = val.decode('utf-8', 'replace') if isinstance(val, bytes) else val
            try:
                o = json.loads(s)
            except Exception:
                continue
            if o.get('type') != 1:
                continue
            rt = o.get('richText')
            if not isinstance(rt, str):
                continue
            try:
                doc = json.loads(rt)
            except Exception:
                continue
            acc = []
            _texts(doc, acc)
            m = clean(''.join(acc))
            if m:
                parts = key.split(':')
                cid = parts[1] if len(parts) > 1 else ''
                proj = cid_ws.get(cid, cid[:8])
                n += write(out, 'cursor', (o.get('createdAt') or '')[:10], proj, cid, m)
    rec('cursor', n, f)

ALL = [ex_codex, ex_claude, ex_qwen, ex_workbuddy, ex_zcode, ex_grok, ex_pi, ex_atomcode, ex_antigravity, ex_catpaw, ex_dsh, ex_cursor]

if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as out:
        for fn in ALL:
            try:
                fn(out)
            except Exception as e:
                print(fn.__name__, 'ERR', e)
    print('===== stats =====')
    total = 0
    for a, (n, f) in sorted(stats.items()):
        print('%-14s msgs=%6d files=%d' % (a, n, f))
        total += n
    print('TOTAL user msgs:', total)
