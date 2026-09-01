# -*- coding: utf-8 -*-
"""vecsearch · 言镜按意思搜（在你自己电脑上，用 chroma + 本机模型）。

用法（AI 查旧话、字面搜不到时调这里；建了索引就按意思搜，没建就按字面搜）：
    python vecsearch.py build            建索引（把你说的话和确认过的事实都存进去）
    python vecsearch.py build --update   补索引：只加新说的话
    python vecsearch.py query "问题"      按意思搜，输出最相关的几条（带日期）
    python vecsearch.py status           看索引状态（多少条、用什么模型、多久没更新）

设计原则（DESIGN.md + README 诚实边界）：
- 模型必须在本机跑（sentence-transformers / paraphrase-multilingual-MiniLM-L12-v2，
  117MB，下载到 ~/.cache/huggingface，是下载工具，不是把你的话传出去）
- 索引的存法跟着 chromadb 的版本走（0.4x 和 1.x 不通用）。装了新版本就固定用它，
  别在两个版本之间来回读同一个索引目录——旧版打开新版建的目录会报错（数据不坏，但会吓人）。
  要迁移：删掉 data/chroma_index/，用新版本重跑 build（你说的话都在 jsonl 里，索引随时能重建）
- 索引存在数据目录 data/chroma_index/，跟着数据走，不会发出去
- 没装依赖或没建索引 → 自动退回按字面搜，功能照旧（ask 里处理）
- 和 corpus_dedup.jsonl 保持一致：build --update 只补新的，删掉的话不会自动清（重建即可）
"""
import os, sys, json, glob, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ds

MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
INDEX_DIR = os.path.join(ds.DATA, 'chroma_index')
META_FILE = os.path.join(INDEX_DIR, '_meta.json')
BATCH = 256


def _deps_ok(quiet=True):
    try:
        import chromadb  # noqa: F401
        import sentence_transformers  # noqa: F401
        return True
    except ImportError as e:
        if not quiet:
            print('缺依赖：%s' % e)
        return False


def _open_collection():
    import chromadb
    client = chromadb.PersistentClient(path=INDEX_DIR)
    return client.get_or_create_collection('wordmirror_corpus', metadata={'hnsw:space': 'cosine'})


def _collection_version_mismatch():
    """索引目录是大版本不兼容的另一代 chromadb 建的 → 提示重建而不是让用户看 sqlite 报错。
    判据：能打开库但按 schema 查询失败（旧版 0.4x 读新版 1.x 目录就是这个症状）。"""
    try:
        _open_collection().count()
        return False
    except Exception:
        return _deps_ok() and os.path.isdir(INDEX_DIR) and bool(glob.glob(os.path.join(INDEX_DIR, 'chroma.sqlite3')))


def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def _iter_rows():
    """语料行：corpus_dedup 为主，user_writebacks 也入库（写回是确认过的事实，检索该能查到）。"""
    for f in ('corpus_dedup.jsonl', 'user_writebacks.jsonl'):
        p = os.path.join(ds.DATA, f)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            msg = (o.get('msg') or '').strip()
            if not msg:
                continue
            o['_src'] = f
            yield o


def _row_id(o):
    """行指纹 = 来源 + 日期 + 原文哈希。语料重跑 ingest 去重后 id 稳定，增量同步靠它。"""
    import hashlib
    key = '%s|%s|%s' % (o['_src'], o.get('date', ''), o.get('msg', ''))
    return hashlib.sha1(key.encode('utf-8')).hexdigest()[:16]


def _norm(o):
    return {'date': o.get('date', o.get('source', '?')), 'agent': o.get('agent', o.get('source', '?')),
            'proj': o.get('proj', o.get('topic', '')), 'src': o['_src']}


def build(update=False):
    if not _deps_ok(quiet=False):
        print('先装依赖：pip install chromadb sentence-transformers')
        print('（都是免费的本机工具；第一次建还要下载一个约 117MB 的模型到 ~/.cache/huggingface）')
        sys.exit(1)
    if _warn_if_version_mismatch():
        sys.exit(1)
    model = _load_model()
    col = _open_collection()
    have = set()
    if update and col.count() > 0:
        have = set(_existing_ids(col))
    rows, ids, docs, metas = [], [], [], []
    n_new = n_dup = 0
    for o in _iter_rows():
        rid = _row_id(o)
        if rid in have:
            n_dup += 1
            continue
        have.add(rid)
        rows.append(o); ids.append(rid)
        docs.append(o['msg'][:2000])  # 模型输入截断，超长消息只索引前 2000 字
        metas.append(_norm(o))
        n_new += 1
        if len(ids) >= BATCH:
            emb = model.encode([d for d in docs], normalize_embeddings=True)
            col.upsert(ids=ids, embeddings=emb.tolist(), documents=docs, metadatas=metas)
            print('  已入库 %d 条（累计 %d）...' % (len(ids), col.count()))
            ids, docs, metas = [], [], []
    if ids:
        emb = model.encode(docs, normalize_embeddings=True)
        col.upsert(ids=ids, embeddings=emb.tolist(), documents=docs, metadatas=metas)
    # 标记写回类型，检索结果里区分"聊天原话"和"确认过的事实"
    meta = {'model': MODEL_NAME, 'rows': col.count(), 'built': ds.datetime.date.today().isoformat()}
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)
    print('建好了：共 %d 条（新加 %d，已在里面 %d）→ %s' % (col.count(), n_new, n_dup, INDEX_DIR))
    print('试一下：python vecsearch.py query "你的问题"   （按意思搜）')


def _existing_ids(col):
    """全量翻页取已入库 id（chroma 0.4 的 get 不支持 ids=None 全取，用 offset 翻页）。"""
    got = []
    while True:
        res = col.get(limit=1000, offset=len(got))
        got += res['ids']
        if len(res['ids']) < 1000:
            return got


def query(q, top=15):
    if not _deps_ok() or not os.path.isdir(INDEX_DIR):
        return None
    try:
        col = _open_collection()
        if col.count() == 0:
            return None
        model = _load_model()
        emb = model.encode([q], normalize_embeddings=True)[0].tolist()
        res = col.query(query_embeddings=[emb], n_results=min(top, col.count()))
        out = []
        for i, rid in enumerate(res['ids'][0]):
            meta = res['metadatas'][0][i]
            out.append({'id': rid, 'score': 1 - res['distances'][0][i],
                        'date': meta.get('date', '?'), 'agent': meta.get('agent', '?'),
                        'proj': meta.get('proj', ''), 'src': meta.get('src', ''),
                        'msg': (res['documents'][0][i] or '').replace(chr(10), ' ')[:150]})
        return out
    except Exception:
        return None


def _warn_if_version_mismatch():
    """索引目录是大版本不兼容的另一代 chromadb 建的：给出人话提示+出路，别让用户面对 sqlite 报错。"""
    if _collection_version_mismatch():
        print('这份索引是另一个版本的 chromadb 建的，当前版本打不开。')
        print('数据没坏——你说的话都在 corpus_dedup.jsonl 里。删掉 %s 后跑 vec build 重新建即可。' % INDEX_DIR)
        return True
    return False


def status():
    if not _deps_ok(quiet=False):
        return
    if not os.path.isdir(INDEX_DIR):
        print('还没有按意思搜的索引。跑 python ds.py vec build 建一个（话多的话要几分钟）。')
        return
    if _warn_if_version_mismatch():
        return
    meta = {}
    if os.path.exists(META_FILE):
        meta = json.load(open(META_FILE, encoding='utf-8'))
    col = _open_collection()
    print('按意思搜的索引：%d 条 | 模型 %s | 建于 %s' % (col.count(), meta.get('model', '?'), meta.get('built', '?')))
    try:
        # 索引口径 = corpus_dedup + user_writebacks（见 _iter_rows），两边都数才不误报
        n = 0
        for f in ('corpus_dedup.jsonl', 'user_writebacks.jsonl'):
            p = os.path.join(ds.DATA, f)
            if os.path.exists(p):
                n += sum(1 for _ in open(p, encoding='utf-8'))
        if n - col.count() > 50:
            print('（数据里共 %d 条，索引里是 %d 条，有 %d 条还没入库——跑 python ds.py vec build --update 补齐）' % (n, col.count(), n - col.count()))
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'build':
        build(update='--update' in sys.argv)
    elif cmd == 'query':
        if len(sys.argv) < 3:
            print('用法：python vecsearch.py query "问题"')
            sys.exit(1)
        hits = query(' '.join(sys.argv[2:]))
        if hits is None:
            print('按意思搜用不了（没建或依赖没装），改按字面搜了。')
            sys.exit(1)
        if not hits:
            print('按意思没搜到相关的。')
            sys.exit(0)
        print('按意思搜到 %d 条（越相关排越前）:' % len(hits))
        for h in hits:
            tag = '写回' if h['src'] == 'user_writebacks.jsonl' else '原话'
            print('  %.2f | %s | %-10s | %s | %s' % (h['score'], h['date'], h['agent'], tag, h['msg'][:110]))
    elif cmd == 'status':
        status()
    else:
        print(__doc__)
