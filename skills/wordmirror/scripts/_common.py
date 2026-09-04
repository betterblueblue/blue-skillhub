# -*- coding: utf-8 -*-
"""WordMirror 脚本共用的数据定位、语料读取和文本工具。"""
import datetime
import json
import os
import re


def _find_base():
    """返回 (数据仓库根, 定位方式说明)。"""
    def _has_data(p):
        return os.path.isdir(os.path.join(p, 'data'))
    env = os.environ.get('WORD_MIRROR_HOME')
    if env:
        if _has_data(env):
            return env, '环境变量 WORD_MIRROR_HOME'
        return env, '环境变量 WORD_MIRROR_HOME（还没有数据，首次写入时创建）'
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


BASE, BASE_SOURCE = _find_base()
DATA = os.path.join(BASE, 'data')
PRODUCTS = os.path.join(BASE, 'products')

# 词频统计词表：只保留有解释价值的动作/决策/纠错/领域/阶段词，去掉纯功能词。
WORD_FREQ = ['继续', '完成', '搞定', '做完', '算了', '不做了', '放弃', '定了', '决定',
             '写', '改', '做', '用', '建', '删', '加', '提', '记', '查', '翻', '试',
             '代码', '项目', '方案', '数据库', '接口', '前端', '后端', '部署', '发布', '上线',
             '问题', '报错', '错了', '不对', '还原', '从头', '重新', '重试', '等一下',
             '月报', '周报', '总结', '复盘', 'TODO', 'OK', '版本']

# 关键词过滤词表：say_do/照见做「实体词」抽取时要去掉的噪声词。
# 覆盖原 WORDS 全部 + 高频虚词/动作单字——实体词抽取里"写/做/用"这类也是噪声分隔符，
# 与词频统计（它们算信号）是两回事，分开维护。
FUNC_WORDS = ['这个', '那个', '这样', '那样', '可以', '应该', '需要', '觉得', '认为', '可能',
              '看看', '试试', '试试看', '先', '再', '然后', '但是', '所以', '因为', '如果',
              '我们', '你们', '他们', '自己', '什么', '怎么', '为什么', '哪里', '多少',
              '继续', '完成', '搞定', '做完', '算了', '不做了', '放弃', '定了', '决定',
              '写', '改', '做', '用', '建', '删', '加', '提', '记', '查', '翻', '试',
              '代码', '项目', '方案', '数据库', '接口', '前端', '后端', '部署', '发布', '上线',
              '谢谢', '好的', '明白', '清楚了', '麻烦', '帮忙', '帮我', '安排',
              '问题', '报错', '错了', '不对', '还原', '从头', '重新', '重试', '等一下',
              '月报', '周报', '总结', '复盘', 'TODO', 'OK', '版本',
              '是的', '嗯', '对', '好', '行', '了解', '同步', '确认', '理解',
              '还', '就', '也', '都', '要', '想', '会', '能', '没', '很',
              '吧', '吗', '呢', '把', '给', '跟', '和', '与', '及', '或',
              '但', '而', '并', '只', '才', '又', '最', '太', '真', '挺',
              '有点', '一下', '你', '我', '他', '她', '它', '这', '那',
              '是', '有', '说', '干', '弄', '整', '来', '去', '到', '在',
              '上', '下']

# 兼容别名：compute_stats/stats_wordfreq 用 WORD_FREQ；旧名 WORDS 对齐过滤用途留给词频。
WORDS = WORD_FREQ


def topic(r):
    p = (r.get('proj') or '').replace('\\', '/')
    seg = p.rstrip('/').split('/')[-1] if p else ''
    seg = seg.strip('-').replace('--', ' ').strip()
    if seg and re.fullmatch(r'[0-9a-fA-F]{6,40}', seg):
        return '(none)'
    return seg[:30] if seg else '(none)'


def read_jsonl(path):
    rows, skipped = [], 0
    if not os.path.exists(path):
        return rows, skipped
    with open(path, encoding='utf-8', errors='replace') as _fh:
        for line in _fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                skipped += 1
    return rows, skipped


def valid_date(value):
    try:
        datetime.date.fromisoformat(value)
        return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value))
    except (TypeError, ValueError):
        return False
