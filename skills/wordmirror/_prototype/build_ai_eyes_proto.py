# -*- coding: utf-8 -*-
"""「AI 眼里的你」开发壳：模板和数据组装都已并入生产（assets/templates/ai_eyes.html + render.py）。
--demo 出假数据版（截图、视觉检查用，不含真实原话）；不带参数 = 走 render.py 出真实数据版。
用法：python _prototype/build_ai_eyes_proto.py [--demo]
"""
import os, sys, json, random, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
import render

TPL = os.path.join(os.path.dirname(HERE), 'assets', 'templates', 'ai_eyes.html')
TODAY = datetime.date.today()


def demo_data():
    """全是编的数据：给截图检查视觉用，不含任何真实原话。"""
    random.seed(3)
    said = ['继续', '好的', '可以啊', '先跑一下测试', '帮我看看这个报错', '提交推送', '这个不对', '再简单一点', '牛啊',
            '先别动代码', '我想做个小程序', '周末再弄', '今天先到这', '这个方案可以', '明天面试', '帮我改下简历',
            '换个思路', '有没有更好的办法', '我准备开始跑步了', '下周一定整理笔记', '先记下来', '看看效果', '行吧']
    days = lambda: '2026-%02d-%02d' % (random.randint(3, 9), random.randint(1, 28))
    phrases = [{'text': t, 'n': n, 'first': '2026-03-0%d' % (i % 9 + 1), 'last': '2026-09-%02d' % (20 - i)}
               for i, (t, n) in enumerate([('继续', 92), ('好的', 61), ('可以啊', 40), ('提交推送', 33), ('牛啊', 21),
                                            ('先跑一下测试', 18), ('这个不对', 15), ('再简单一点', 12), ('行吧', 9), ('今天先到这', 7)])]
    typ = {
        'Claude Code': ['先跑一下测试看看', '这个报错帮我看下', '改完提交推送'],
        'Codex': ['把登录模块重构一下，先写测试再改，改完跑一遍全量', '这个任务你自己拆，拆完一步步做，别问我', '把上周那个接口的边界情况都补上测试'],
        'Cursor': ['改一下', '这行删了', '行'],
        'Gemini': ['这个库最新版本是多少，有啥大改动', '帮我找找这个问题有没有官方说法', '对比一下这两个方案'],
        'Kimi': ['这是我整理的一整份面试材料，帮我提炼成三点，每点给一个例子，语气别太正式', '这段会议记录太乱了，帮我按时间理一遍，谁说了什么列出来', '把这篇文章压到三百字，保留数字'],
        'Qwen': ['试试你', '翻译一下这段', '写个周报开头'],
    }
    agents = []
    for name, n, med, title in [('Claude Code', 5200, 14, '你的主开发台'), ('Codex', 4800, 31, '长任务交给它'), ('Cursor', 900, 9, '顺手改两行'),
                                ('Gemini', 620, 22, '查资料的地方'), ('Kimi', 410, 40, '整段材料丢过去'), ('Qwen', 260, 12, '偶尔试试')]:
        agents.append({'agent': name, 'n': n, 'median': med, 'title': title,
                       'phrases': [{'text': t, 'n': random.randint(5, 60)} for t in random.sample(said, 5)],
                       'typical': sorted([{'t': t, 'd': days()} for t in typ[name]], key=lambda m: m['d']),
                       'sample': {'t': random.choice(said), 'd': days()}})
    lines_ = [
        {'name': '换工作', 'status': '还在走', 'kind': 'open', 'question': '先多投几家，还是先把项目经历讲顺',
         'facts': [{'d': '2026-05-02', 'q': '我准备换个方向试试'}, {'d': '2026-06-18', 'q': '帮我改下简历'}, {'d': '2026-08-09', 'q': '明天面试，帮我过一遍'}]},
        {'name': '自己的小程序', 'status': '还在走', 'kind': 'open', 'question': '继续加功能，还是先给朋友用起来',
         'facts': [{'d': '2026-04-11', 'q': '我想做个记账小程序'}, {'d': '2026-07-01', 'q': '先把登录做完'}, {'d': '2026-09-12', 'q': '这个方案可以'}]},
        {'name': '跑步', 'status': '一直停在“准备做”', 'kind': 'stalled', 'question': '是真想开始，还是先放一放',
         'facts': [{'d': '2026-03-20', 'q': '我准备开始跑步了'}, {'d': '2026-06-05', 'q': '下周一定开始跑'}]},
        {'name': '整理读书笔记', 'status': '没了下文', 'kind': 'stalled', 'question': '',
         'facts': [{'d': '2026-04-02', 'q': '下周一定整理笔记'}, {'d': '2026-05-30', 'q': '笔记先记下来再说'}]},
        {'name': '考证', 'status': '已经收线', 'kind': 'closed', 'question': '',
         'facts': [{'d': '2026-03-01', 'q': '这个月开始刷题'}, {'d': '2026-05-15', 'q': '不考了，先找工作'}]},
    ]
    promises_ = [{'text': t, 'd': d, 'days': (TODAY - datetime.date.fromisoformat(d)).days, 'ref': ''}
                 for t, d in [('开始跑步', '2026-03-20'), ('整理读书笔记', '2026-04-02'), ('给小程序写个说明', '2026-07-01')]]
    return {'today': TODAY.isoformat(), 'total': 12240, 'span': ['2026-03-01', '2026-09-20'], 'phrases': phrases,
            'mirror': [{'t': random.choice(said), 'd': days(), 'a': random.choice(agents)['agent']} for _ in range(600)],
            'agents': agents, 'lines': lines_, 'promises': promises_,
            'hands': [{'text': t, 'n': n} for t, n in [('先跑一下测试', 48), ('提交推送', 33), ('帮我看看这个报错', 27), ('改下简历', 14),
                                                        ('整理一下笔记', 9), ('查一下文档', 8), ('写个脚本', 6)]]}


def inject(data):
    tpl = open(TPL, encoding='utf-8').read()
    return tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))


def main():
    if '--demo' in sys.argv:
        out = os.path.join(HERE, 'ai_eyes_demo.html')
        open(out, 'w', encoding='utf-8').write(inject(demo_data()))
        print('演示版（假数据）写好了：%s' % out)
        return
    j = render.build_ai_eyes_page()
    if j:
        render.write_out(*j)
    else:
        print('语料为空或模板缺失，没生成。先跑 ingest，或检查 assets/templates/ai_eyes.html 在不在。')


if __name__ == '__main__':
    main()
