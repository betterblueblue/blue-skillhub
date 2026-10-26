# -*- coding: utf-8 -*-
"""造一个全假数据的 WordMirror home（_prototype/demo_home/），用 render.py 渲染出 index.html 演示版。
用法：python _prototype/build_index_demo.py
产物：_prototype/demo_home/products/html/index.html（假数据，可录屏可截图）
"""
import json, os, random, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.join(HERE, 'demo_home')
DATA = os.path.join(HOME, 'data')
PROFILE = os.path.join(DATA, 'profile')

D0, D1 = datetime.date(2026, 3, 1), datetime.date(2026, 9, 20)

AGENTS = ['claude-code', 'codex', 'cursor', 'kimi', 'qwen', 'pi']
MSGS = {
    'claude-code': ['先跑一下测试看看', '这个报错帮我看下', '改完提交推送', '把这篇稿子帮我顺一遍',
                    '博客主题那个 CSS 又跑偏了', '部署脚本再检查一遍', '我想把博客搬到新平台',
                    '帮我选个静态站生成器', '评论区先不接了', '这个方案可以', '今天先到这'],
    'codex': ['把登录模块重构一下，先写测试再改', '这个任务你自己拆，拆完一步步做',
              '把上周那个接口的边界情况都补上测试', '我想做个记账小程序', '先把登录做完',
              '记账的分类先写死五种', '月底导出一版报表', '这个方案可以'],
    'cursor': ['改一下', '这行删了', '行', '换个颜色', '字号大一点'],
    'kimi': ['这是我整理的一整份产品反馈，帮我提炼成三点', '这段会议记录太乱了帮我按时间理一遍',
             '把这篇文章压到三百字，保留数字'],
    'qwen': ['试试你', '翻译一下这段', '写个周报开头'],
    'pi': ['这段报错啥意思', '帮我看下这个配置'],
}
FILLER = ['继续', '好的', '可以啊', '嗯', '对', '行', '然后呢', '再来一遍', '看看效果', '牛啊', '行吧']

# 节奏：3 月清淡 → 6 月搬博客忙起来 → 8-9 月小程序冲刺，中间留些没说话的日子
INTENSITY = [('2026-03', 0.10), ('2026-04', 0.14), ('2026-05', 0.22), ('2026-06', 0.45),
             ('2026-07', 0.30), ('2026-08', 0.55), ('2026-09', 0.40)]


def gen_corpus():
    random.seed(7)
    rows, d = [], D0
    weights = dict(INTENSITY)
    while d <= D1:
        mk = d.strftime('%Y-%m')
        inten = weights.get(mk, 0.2)
        if random.random() < inten:
            n = max(1, int(random.gauss(inten * 60, 12)))
            for i in range(n):
                ag = random.choices(AGENTS, [40, 28, 12, 10, 6, 4])[0]
                pool = MSGS[ag] + FILLER
                rows.append({'agent': ag, 'date': d.isoformat(),
                             'proj': random.choice(['blog', 'ledger', 'misc']),
                             'sid': 'demo-%s-%d' % (mk, i), 'msg': random.choice(pool)})
        d += datetime.timedelta(days=1)
    return rows


def write_jsonl(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        for o in rows:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')


def main():
    os.makedirs(PROFILE, exist_ok=True)
    corpus = gen_corpus()
    write_jsonl(os.path.join(DATA, 'corpus_dedup.jsonl'), corpus)

    stats = {}
    for o in corpus:
        stats.setdefault(o['agent'], {'msgs': 0})['msgs'] += 1
    json.dump(stats, open(os.path.join(DATA, 'stats_agents.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump({k: {'msgs': 0} for k, _ in INTENSITY},
              open(os.path.join(DATA, 'materials_monthly.json'), 'w', encoding='utf-8'))

    write_jsonl(os.path.join(DATA, 'promises.jsonl'), [
        {'text': '开始跑步', 'date': '2026-03-20', 'status': 'open', 'ref': ''},
        {'text': '整理读书笔记', 'date': '2026-04-02', 'status': 'open', 'ref': ''},
        {'text': '给小程序写个说明', 'date': '2026-07-01', 'status': 'open', 'ref': ''},
        {'text': '把博客搬到新平台', 'date': '2026-05-02', 'status': 'closed', 'closed_date': '2026-08-09', 'ref': ''},
        {'text': '每天练半小时吉他', 'date': '2026-03-01', 'status': 'dropped', 'ref': ''},
    ])

    write_jsonl(os.path.join(PROFILE, 'insights.jsonl'), [
        {'type': 'say_do', 'status': 'active', 'confidence': 'high',
         'fact': '跑步说了三次要开始，两次停在“下周”，还没有下文。',
         'evidence': [{'date': '2026-03-20', 'msg': '我准备开始跑步了'},
                      {'date': '2026-06-05', 'msg': '下周一定开始跑'}]},
        {'type': 'word_drift', 'status': 'active', 'confidence': 'mid',
         'fact': '七月之后「先跑一下测试」说得明显变多，测试这件事越来越顺手。',
         'evidence': [{'date': '2026-07-18', 'msg': '先跑一下测试看看'}]},
        {'type': 'flip', 'status': 'confirmed', 'confidence': 'high',
         'fact': '吉他三月说每天练，五月自己说先放一放，这条线已经收掉了。',
         'evidence': [{'date': '2026-05-15', 'msg': '先放一放，天冷了再说'}]},
    ])

    def w(name, text):
        open(os.path.join(PROFILE, name), 'w', encoding='utf-8').write(text)

    w('current-context.md', '''# 当前状态（演示数据）
- 更新于：2026-09-20
- 当前主线：把记账小程序的报表做完
- 当前阶段：小程序收尾期
- 最近明确决定：博客评论区先不接，保持纯静态
- 当前最要紧的事：月底导出一版能看的报表
- 当前更需要的支持：少开新坑
- 暂时不要：再折腾吉他
''')
    w('note.md', '''九月的你话明显变多，变多的部分几乎全在小程序上。跑步说了三次要开始，现在还停在「准备做」。不是催你，是这页镜子照出来的就这些。''')

    w('portrait.md', '''# 你是谁（演示数据）

## 一眼看见的

你和 AI 的关系很近：上半年一万多句话，六个工具轮着用。干活型的对话占大头，闲聊很少。

## 怎么跟你说话最顺

- 指令短，期望高。「改一下」「行」这种话占了不小比例。
- 说「自己拆」就真的要它自己拆完，不喜欢步步确认。
- 口头禅是「继续」，说过九十多次。

## 现在在哪

记账小程序收尾，博客刚搬完家，跑步还停在准备阶段。
''')
    w('lines.md', '''# 那几条线（演示数据）

## 个人博客 · 还在走
- 2026-05-02 「我打算把博客搬到新平台」
- 2026-06-18 「帮我选个静态站生成器」
- 2026-08-09 「这篇稿子帮我顺一遍」
现在的问题是：先搭起来再说，还是先把旧文章迁完

## 自己的小程序 · 还在走
- 2026-04-11 「我想做个记账小程序」
- 2026-07-01 「先把登录做完」
- 2026-09-12 「这个方案可以」
现在的问题是：继续加功能，还是先给朋友用起来

## 跑步 · 一直停在“准备做”
- 2026-03-20 「我准备开始跑步了」
- 2026-06-05 「下周一定开始跑」
现在的问题是：是真想开始，还是先放一放

## 整理读书笔记 · 没了下文
- 2026-04-02 「下周一定整理笔记」
- 2026-05-30 「笔记先记下来再说」

## 学吉他 · 已经收线
- 2026-03-01 「这个月每天练半小时」
- 2026-05-15 「先放一放，天冷了再说」
''')
    w('ai-eyes.md', '''# AI 眼里的你（演示数据）

### claude-code：天天一起干活的主力
句数最多的工位，博客搬迁和稿子都走它。

### codex：长任务都敢交给它
重构、补测试这类一整块的活基本都在它那儿。

### cursor：顺手改两行就找它
对话极短，多是顺手的小改动。

### kimi：整段材料丢给它理
长文本压缩、整理会议纪要这种活儿。

### qwen：偶尔喊来试试的新朋友
翻译、写开头，用得不深。

### pi：备胎但靠谱
偶尔顶上，解决报错和配置问题。
''')
    w('mirror.md', '''# 镜面上的话（演示数据）
- 2026-04-11 「我想做个记账小程序」 codex
- 2026-03-20 「我准备开始跑步了」 kimi
- 2026-05-02 「我打算把博客搬到新平台」 claude-code
- 2026-06-05 「下周一定开始跑」 qwen
- 2026-07-01 「先把登录做完」 codex
- 2026-09-12 「这个方案可以」 claude-code
''')
    w('noticed.md', '''这期读出来一件事：你对 Cursor 说话最短，常常只有两三个字；对 Claude Code 反而愿意写整段需求。同一个你，在两个工具里是两种说话方式。''')
    w('timeline.md', '''# 这几个月（演示数据）

## 本期对账
九月句数是全期最高，几乎都在小程序上。跑步又停了一个月。

### 搬家前的平静（2026-03 ~ 2026-05）
- 2026-03-20 「我准备开始跑步了」
- 2026-04-11 「我想做个记账小程序」
- 2026-05-02 「我打算把博客搬到新平台」

### 博客搬迁月（2026-06 ~ 2026-07）
- 2026-06-18 「帮我选个静态站生成器」
- 2026-07-01 「先把登录做完」

### 小程序冲刺（2026-08 ~ 2026-09）
- 2026-08-09 「这篇稿子帮我顺一遍」
- 2026-09-12 「这个方案可以」
''')

    env = dict(os.environ, WORD_MIRROR_HOME=HOME)
    r = subprocess.run([sys.executable, os.path.join(HERE, '..', 'scripts', 'render.py'), 'all'],
                       env=env, capture_output=True, text=True)
    print(r.stdout, r.stderr)
    print('演示 home：%s' % HOME)
    print('页面：%s' % os.path.join(HOME, 'products', 'html', 'index.html'))


if __name__ == '__main__':
    main()
