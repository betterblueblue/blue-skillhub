# -*- coding: utf-8 -*-
"""vecsearch · 言镜语义检索（本地向量索引，chroma + 本地嵌入模型）。

用法（一般不直接跑，ds.py ask 会自动走这里；有索引用语义，没索引降回关键词）：
    python vecsearch.py build            建索引（corpus_dedup + user_writebacks 全量入库）
    python vecsearch.py build --update   增量：只加新语料（按行指纹去重）
    python vecsearch.py query "问题"      语义查询，输出 top 结果（带日期，供 agent 引用）
    python vecsearch.py status           索引状态（条数、模型、新鲜度）

设计原则（DESIGN.md + README 诚实边界）：
- 嵌入模型必须在本机跑（sentence-transformers / paraphrase-multilingual-MiniLM-L12-v2，
  117MB，下载到 ~/.cache/huggingface，是下载工具不是上传数据）
- 索引存储格式跟 chromadb 大版本走（0.4x 与 1.x 互不兼容）。装了新版本（≥1.0）就固定用新版本，
  别在两个大版本之间来回读写同一个索引目录——旧版读新版目录直接报错，虽不损坏数据但会吓人。
  需要迁移时：删掉 data/chroma_index/ 用新版本重跑 build（语料都在 jsonl 里，索引随时可重建）
- 索引存在数据目录 data/chroma_index/，跟着数据走，永不外传
- 没装依赖或没建索引 → 安静降级回关键词检索，功能照旧（ask 里处理）
- 与 corpus_dedup.jsonl 的一致性：build --update 按行指纹同步，删掉的语料不自动清（重建即可）
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


def _open_collection():
    import chromadb
    client = chromadb.PersistentClient(path=INDEX_DIR)
    return client.get_or_create_collection('wordmirror_corpus', metadata={'hnsw:space': 'cosine'})


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
        print('（都是免费本机库；首次建索引还会下载 %.0fMB 的多语言嵌入模型到 ~/.cache/huggingface）' % 117)
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
    print('索引完成：共 %d 条（新增 %d，已在库 %d）→ %s' % (col.count(), n_new, n_dup, INDEX_DIR))
    print('查询试一下：python ds.py ask "你的问题"   （自动走语义检索）')


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
        print('索引目录是用另一代 chromadb（大版本不同）建的，本版本打不开。')
        print('数据没坏——语料都在 corpus_dedup.jsonl 里。删掉 %s 后跑 vec build 重建即可。' % INDEX_DIR)
        return True
    return False


def status():
    if not _deps_ok(quiet=False):
        return
    if not os.path.isdir(INDEX_DIR):
        print('还没有向量索引。跑 python ds.py vec build 建一个（语料多的话要几分钟）。')
        return
    if _warn_if_version_mismatch():
        return
    meta = {}
    if os.path.exists(META_FILE):
        meta = json.load(open(META_FILE, encoding='utf-8'))
    col = _open_collection()
    print('向量索引：%d 条 | 模型 %s | 建于 %s' % (col.count(), meta.get('model', '?'), meta.get('built', '?')))
    try:
        n = sum(1 for _ in open(os.path.join(ds.DATA, 'corpus_dedup.jsonl'), encoding='utf-8'))
        if n and abs(n - col.count()) > 50:
            print('（语料 %d 条 vs 索引 %d 条——跑 python ds.py vec build --update 同步）' % (n, col.count()))
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
            print('索引不可用（没建或依赖缺失），走关键词检索吧。')
            sys.exit(1)
        if not hits:
            print('语义检索没找到相关的。')
            sys.exit(0)
        print('语义检索 %d 条（按相关度排）:' % len(hits))
        for h in hits:
            tag = '写回' if h['src'] == 'user_writebacks.jsonl' else '原话'
            print('  %.2f | %s | %-10s | %s | %s' % (h['score'], h['date'], h['agent'], tag, h['msg'][:110]))
    elif cmd == 'status':
        status()
    else:
        print(__doc__)
