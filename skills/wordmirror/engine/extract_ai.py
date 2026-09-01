# -*- coding: utf-8 -*-
"""AI 消息提取器：8 个 agent 的 assistant 侧 -> ai_messages.jsonl
输出: {agent, date, proj, sid, msg}  msg 取 AI 回复正文（截断到前 1200 字符，蒸馏够用）"""
import json, os, glob, re, sqlite3, datetime

H = os.path.expanduser('~')
import os
BASE = os.environ.get('WORD_MIRROR_HOME') or os.path.expanduser(os.path.join('~', 'WordMirror'))
OUT = os.path.join(BASE, 'data', 'ai_messages.jsonl')
MAXLEN = 1200

def write(out, agent, date, proj, sid, msg):
    if msg and len(msg) >= 10:
        out.write(json.dumps({'agent': agent, 'date': date, 'proj': proj, 'sid': sid, 'msg': msg[:MAXLEN]}, ensure_ascii=False) + '\n')
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

BOILER_AI = (
    'The user wants me', 'I need to', 'I\'ll start', 'Let me',  # 这些是思考,过滤
)

def ex_codex(out):
    n = f = 0
    base = os.path.join(H, '.codex', 'sessions')
    for year in sorted(os.listdir(base)):
        yd = os.path.join(base, year)
        if not os.path.isdir(yd): continue
        for month in sorted(os.listdir(yd)):
            md = os.path.join(base, year, month)
            if not os.path.isdir(md): continue
            for day in sorted(os.listdir(md)):
                dd = os.path.join(base, year, month, day)
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
                        # agent_message = AI 给用户的正式回复（非工具/思考）
                        if t == 'event_msg' and p.get('type') == 'agent_message':
                            m = p.get('message')
                            if isinstance(m, str) and len(m) > 30:
                                n += write(out, 'codex', d2s(o.get('timestamp','')), cwd, sid, m)
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
            if o.get('type') != 'assistant': continue
            msg = o.get('message', {})
            texts = []
            for part in (msg.get('content') or []):
                if isinstance(part, dict) and part.get('type') == 'text':
                    texts.append(part.get('text',''))
            m = '\n'.join(texts).strip()
            if len(m) > 30:
                n += write(out, 'claude-code', d2s(o.get('timestamp','')), proj, sid, m)
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
            if o.get('type') != 'assistant': continue
            msg = o.get('message', {})
            texts = []
            c = msg.get('content')
            if isinstance(c, str): texts.append(c)
            elif isinstance(c, list):
                for part in c:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        texts.append(part.get('text',''))
            for part in (msg.get('parts') or []):
                if isinstance(part, dict) and isinstance(part.get('text'), str):
                    texts.append(part['text'])
            m = '\n'.join(texts).strip()
            if len(m) > 30:
                n += write(out, 'qwen', d2s(o.get('timestamp','')), proj, sid, m)
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
            if o.get('type') != 'message' or o.get('role') != 'assistant': continue
            if o.get('status') == 'incomplete': continue  # 429错误等
            texts = []
            for part in o.get('content', []):
                if isinstance(part, dict) and isinstance(part.get('text'), str):
                    texts.append(part['text'])
            m = '\n'.join(texts).strip()
            if len(m) > 30:
                n += write(out, 'workbuddy', d2s(o.get('timestamp','')), proj, sid, m)
    rec('workbuddy', n, f)

def ex_zcode(out):
    n = 0
    try:
        con = sqlite3.connect(os.path.join(H, '.zcode', 'cli', 'db', 'db.sqlite'))
        cur = con.cursor()
        ai_msgs, msg_sess, msg_time = {}, {}, {}
        for (mid, sid, tc, data) in cur.execute('select id, session_id, time_created, data from message'):
            try: o = json.loads(data)
            except Exception: continue
            if o.get('role') == 'assistant':
                ai_msgs[mid] = True
                msg_sess[mid] = sid
                msg_time[mid] = tc
        sess_proj = {}
        for (sid, d) in cur.execute('select id, directory from session'):
            sess_proj[sid] = d or ''
        for (pid, mid, sid, tc, data) in cur.execute('select id, message_id, session_id, time_created, data from part'):
            if mid not in ai_msgs: continue
            try: o = json.loads(data)
            except Exception: continue
            t = o.get('text')
            if isinstance(t, str) and len(t) > 30:
                n += write(out, 'zcode', d2s(msg_time.get(mid) or tc), sess_proj.get(sid, sid[:8]), sid, t)
    except Exception as e:
        print('zcode err', e)
    rec('zcode', n, 1)

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
            if msg.get('role') != 'assistant': continue
            texts = []
            for part in msg.get('content', []):
                if isinstance(part, dict) and part.get('type') == 'text':
                    texts.append(part.get('text',''))
            m = '\n'.join(texts).strip()
            if len(m) > 30:
                n += write(out, 'pi', d2s(o.get('timestamp','')), proj, str(o.get('id','')), m)
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
                if str(msg.get('role','')).lower() != 'assistant': continue
                c = msg.get('content', {})
                t = c.get('Text') if isinstance(c, dict) else None
                if t and len(t) > 30:
                    n += write(out, 'atomcode', date, proj, base, t)
    rec('atomcode', n, f)

def ex_antigravity(out):
    n = f = 0
    for tf in glob.glob(os.path.join(H, '.gemini', 'antigravity', 'brain', '*', '.system_generated', 'logs', 'transcript.jsonl')):
        f += 1
        cid = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(tf))))
        for line in open(tf, encoding='utf-8', errors='replace'):
            try: o = json.loads(line)
            except Exception: continue
            # AI 的正式回复类型
            if o.get('type') not in ('MODEL_FINAL', 'FINAL_RESPONSE', 'AGENT_RESPONSE', 'MODEL_RESPONSE'): continue
            c = o.get('content', '')
            if isinstance(c, str) and len(c) > 30:
                n += write(out, 'antigravity', d2s(o.get('created_at','')), cid[:8], cid, c)
    rec('antigravity', n, f)

def ex_catpaw(out):
    # CatPaw IDE 版 AI 回复：assistant: 后正文；[Tool call]/[Tool result] 起的工具块整段跳过。
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
            proj = proj_dir.split('--', 1)[1] if '--' in proj_dir else proj_dir
            sid = sess_dir
            date = datetime.date.fromtimestamp(os.path.getmtime(tf)).strftime('%Y-%m-%d')
            buf = []
            in_ai = False
            in_tool = False
            for line in open(tf, encoding='utf-8', errors='replace'):
                st = line.strip()
                if st == 'assistant:':
                    if in_ai and buf:
                        m = '\n'.join(buf).strip()
                        if len(m) >= 10:
                            n += write(out, 'catpaw', date, proj, sid, m)
                    in_ai = True
                    in_tool = False
                    buf = []
                    continue
                if st == 'user:' or st == '<user_query>':
                    if in_ai and buf:
                        m = '\n'.join(buf).strip()
                        if len(m) >= 10:
                            n += write(out, 'catpaw', date, proj, sid, m)
                    in_ai = False
                    in_tool = False
                    buf = []
                    continue
                if st.startswith('[Tool call]') or st.startswith('[Tool result]'):
                    in_tool = True
                    continue
                if st.startswith('[Thinking]'):
                    in_tool = False
                    continue
                if in_ai and not in_tool:
                    buf.append(line.rstrip('\n'))
            if in_ai and buf:
                m = '\n'.join(buf).strip()
                if len(m) >= 10:
                    n += write(out, 'catpaw', date, proj, sid, m)
    rec('catpaw', n, f)

def ex_dsh(out):
    # DeepSeek Harness AI 回复：正式文本走 text-chunks 事件（data.texts 数组），
    # 按 (turn, step) 聚合；思考走 reasoning-chunks，不采。
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
            steps = {}
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
                if t == 'text-chunks':
                    d = o.get('data') or {}
                    key = (d.get('turn'), d.get('step'))
                    s = steps.setdefault(key, {'texts': [], 'time': o.get('time', '')})
                    for x in (d.get('texts') or []):
                        if isinstance(x, str):
                            s['texts'].append(x)
                    if not s['time']:
                        s['time'] = o.get('time', '')
            for key in sorted(steps):
                s = steps[key]
                m = ''.join(s['texts']).strip()
                if len(m) >= 10:
                    n += write(out, 'dsh', d2s(s['time']), proj, sid, m)
    rec('dsh', n, f)

def ex_cursor(out):
    # Cursor AI 气泡：type=2 的 bubbleId，正文在 text 字段（markdown）。
    n = f = 0
    appdata = os.environ.get('APPDATA')
    if not appdata:
        appdata = os.path.join(H, 'AppData', 'Roaming')
    base = os.path.join(appdata, 'Cursor', 'User')
    if not os.path.isdir(base):
        return rec('cursor', 0, 0)
    dbs = []
    g = os.path.join(base, 'globalStorage', 'state.vscdb')
    if os.path.isfile(g):
        dbs.append(g)
    ws = os.path.join(base, 'workspaceStorage')
    if os.path.isdir(ws):
        for d in os.listdir(ws):
            p = os.path.join(ws, d, 'state.vscdb')
            if os.path.isfile(p):
                dbs.append(p)
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
            if o.get('type') != 2:
                continue
            t = o.get('text')
            if isinstance(t, str) and len(t) >= 10:
                parts = key.split(':')
                cid = parts[1] if len(parts) > 1 else ''
                proj = cid_ws.get(cid, cid[:8])
                n += write(out, 'cursor', (o.get('createdAt') or '')[:10], proj, cid, t)
    rec('cursor', n, f)

ALL = [ex_codex, ex_claude, ex_qwen, ex_workbuddy, ex_zcode, ex_pi, ex_atomcode, ex_antigravity, ex_catpaw, ex_dsh, ex_cursor]

if __name__ == '__main__':
    with open(OUT, 'w', encoding='utf-8') as out:
        for fn in ALL:
            try:
                fn(out)
            except Exception as e:
                print(fn.__name__, 'ERR', e)
    print('===== AI 消息统计 =====')
    total = 0
    for a, (n, f) in sorted(stats.items()):
        print('%-14s msgs=%6d files=%d' % (a, n, f))
        total += n
    print('TOTAL ai msgs:', total)
