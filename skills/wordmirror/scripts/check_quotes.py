# -*- coding: utf-8 -*-
"""产物引文可追溯性检查：报告「原话」（日期）必须能在语料里反查。

协议（references/distill-report-protocol.md）要求报告里的引文格式：
  用户话「原话」（YYYY-MM-DD）            -> 在 data/corpus_dedup.jsonl 反查
  用户话 - YYYY-MM-DD「原话」             -> 同上（时间线写法）
  AI 话  「原话」（YYYY-MM-DD，工具）      -> 在 data/ai_messages.jsonl 反查

匹配规则（对真实语料稳健）：
  - 语义是「这句话至少说过」，不是逐字节复核：去掉空白和中文/英文标点后再比。
  - 报告常用「…」截断一条长原话：按省略号切成若干片段，任一片段能在语料中找到即算通过；
    只信足够长的片段（≥4 字），太短的片段不可靠而不判。
  - 语料按日期跨天保留同文，故「日期精确匹配」噪声大，这里只判话有没有说过，不判日期。
  - 找不到任何适配片段 = 报告里这话在语料里根本查不到（改写/编造/来源不符）→ 未通过。

普通中文引号、标题、总结句（不带（日期）后跟）不误报。

用法：
  python scripts/check_quotes.py            # 扫描 profile/*.md + products/*.md，有未通过则退出 1
"""
import glob
import os
import re
import sys

import _common as common

DATA = common.DATA
PRODUCTS = common.PRODUCTS

RE_SUFFIX = re.compile(r'「([^」]+)」（(\d{4}-\d{2}-\d{2})(?:[，,]\s*([^）]+))?）')
RE_PREFIX = re.compile(r'(?m)(?<![\d])(\d{4}-\d{2}-\d{2})「([^」]+)」')

# 括号里跟的限定词，只有是已知 agent/工具名才把这条引文当 AI 引文（去 ai_messages 查）；
# 其余（如「反代相关」「要 AI 给出推理依据」这类作者加的说明性注释）都按用户引文处理。
KNOWN_AGENTS = {'claude', 'claude-code', 'codex', 'qwen', 'workbuddy', 'zcode', 'grok',
                'pi', 'atomcode', 'antigravity', 'catpaw', 'dsh', 'cursor'}

_MIN_FRAG = 4  # 只信这么长的适配片段


def _norm(s):
    return re.sub(r'[\s，。、！？；：,.;:!?…“”‘’"\'（）()\-—]+', '', s or '')


def _needles(quote):
    """把一条报告引文变成候选片段：按省略号切分，去掉标点，去短、去重。"""
    frags = re.split(r'[…。．]+', quote or '')
    out = []
    for f in frags:
        nf = _norm(f)
        if len(nf) >= _MIN_FRAG:
            out.append(nf)
    return list(dict.fromkeys(out))


def _match(needles, normed_msgs):
    return any(nd in m for nd in needles for m in normed_msgs)


def _record_quote(quote, messages, out, path, line, reason, stats):
    """记录一条引文；把可验证、截断和无法验证分开统计。"""
    stats['checked'] += 1
    matched = bool(_needles(quote)) and _match(_needles(quote), messages)
    if matched:
        stats['verified'] += 1
        if re.search(r'[…．]+', quote):
            stats['truncated'] += 1
    else:
        stats['unverifiable'] += 1
        out.append((path, line, quote, reason))


def _populate(path, rows_user, rows_ai, user_present, ai_present, out, stats):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            text = f.read()
    except OSError:
        return
    for ln, line in enumerate(text.splitlines(), 1):
        for m in RE_SUFFIX.finditer(line):
            quote, _, qual = m.group(1), m.group(2), m.group(3)
            is_ai = bool(qual) and qual.strip() in KNOWN_AGENTS
            if is_ai:
                if not ai_present:
                    stats['checked'] += 1
                    stats['unverifiable'] += 1
                    stats['source_missing'] += 1
                    out.append((path, ln, quote, 'AI 语料缺失，无法校验 AI 来源引文'))
                else:
                    _record_quote(quote, rows_ai, out, path, ln,
                                  '未在 AI 语料中找到原话', stats)
            else:
                _record_quote(quote, rows_user, out, path, ln,
                              '未在用户语料中找到原话', stats)
        for m in RE_PREFIX.finditer(line):
            quote = m.group(2)
            _record_quote(quote, rows_user, out, path, ln,
                          '未在用户语料中找到原话', stats)


def _md_files(data, products):
    out = []
    for pat in (os.path.join(data, 'profile', '*.md'), os.path.join(products, '*.md')):
        out += [f for f in glob.glob(pat) if os.path.isfile(f)]
    return out


def check_quotes(data=DATA, products=PRODUCTS, out=None, stats=None):
    """扫描报告引文，返回未能验证的引文；可选填充分级统计。"""
    if out is None:
        out = []
    if stats is None:
        stats = {}
    stats.setdefault('checked', 0)
    stats.setdefault('verified', 0)
    stats.setdefault('truncated', 0)
    stats.setdefault('unverifiable', 0)
    stats.setdefault('source_missing', 0)
    rows_u, _ = common.read_jsonl(os.path.join(data, 'corpus_dedup.jsonl'))
    rows_a, _ = common.read_jsonl(os.path.join(data, 'ai_messages.jsonl'))
    for f in _md_files(data, products):
        _populate(f, [_norm(r.get('msg', '')) for r in rows_u],
                  [_norm(r.get('msg', '')) for r in rows_a],
                  bool(rows_u), bool(rows_a), out, stats)
    return out


def main():
    stats = {'checked': 0, 'verified': 0, 'truncated': 0,
             'unverifiable': 0, 'source_missing': 0}
    violations = check_quotes(stats=stats)
    md_count = len(_md_files(DATA, PRODUCTS))
    if not md_count:
        print('还没有报告可查（profile/*.md、products/*.md 均无），跳过引文检查。')
        return 0
    verified = stats['verified']
    truncated = stats['truncated']
    direct = verified - truncated
    unverifiable = stats['unverifiable']
    print('引文核验分级：共检查 %d 条 · 直接匹配 %d · 允许截断 %d · 无法验证 %d'
          % (stats['checked'], direct, truncated, unverifiable))
    if not violations:
        print('%d 个报告里所有带日期引文均可反查。' % md_count)
        return 0
    print('无法验证的引文（可能是改写/浓缩，也可能来源缺失；可核原语料）：')
    for path, ln, quote, reason in violations:
        bare = path.replace(DATA, 'data').replace(PRODUCTS, 'products')
        print('  ✗ %s:%s  「%s」   -> %s' % (bare, ln, quote[:24], reason))
    if '--strict' in sys.argv:
        print('严格模式：存在 %d 条无法验证的引用，阻止交付。' % unverifiable)
        return 2
    print('非严格模式：%d 条无法验证的引用，仅提示。' % unverifiable)
    return 1


if __name__ == '__main__':
    sys.exit(main())