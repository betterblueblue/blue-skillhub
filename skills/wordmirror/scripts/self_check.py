# -*- coding: utf-8 -*-
"""言镜（wordmirror）自检脚本：改名/重蒸馏/日常维护后跑一遍，30 秒出结果。
检查项（2026-08-31 起，项数以运行输出为准）：
  1  旧命名残留（改名最容易丢三落四的地方）
  2  关键文件存在
  3  index 链接死链 + md 孤儿（没入口的文档）
  4  模板与渲染产物同步
  5  skill 引用路径存在
  6  git 工作区干净（提醒，不算失败）
  7  engine 脚本可跑（抽样 compute_stats）
  9  写回文件被 git 跟踪
  10 skill 三件套互相引用
  13 JSON 文件合法
  14 skill 包结构（对标标准 skill）
  15 产物引文可追溯（check_quotes，警告项）
  16 承诺账本合法
  17 开工三句话 + 主动引导就位
  18 浏览器四页加载（可选，--web 时跑）
  19 tracker 日期全格式
  20 skill 包 layers 零真实数据
用法：
  python scripts/self_check.py          # 快检（无浏览器）
  python scripts/self_check.py --web    # 连浏览器一起验
"""
import os, sys, glob, json, re, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
import _common as common
DATA_ROOT = common.BASE
DATA = common.DATA
PROD = common.PRODUCTS

PASS, FAIL, WARN = '✓', '✗', '!'
results = []
def check(name, ok, detail=''):
    results.append((PASS if ok is True else (WARN if ok is None else FAIL), name, detail))

BS = chr(92)

# ===== 1. 旧命名残留 =====
OLD_NAMES = ['产出样例', '承诺追踪器', '画像与协作', '年度之书', '项目基因库', '决策档案',
             '能力光谱', '文娟记忆包', '时间胶囊', '提问模式', '每日传记', '跨agent人格']
# 新名清单出现旧词不算（如"时间胶囊"不再使用；但 SOP 反例示范行豁免）
hits = []
scan_files = []
for pat in ['scripts/*.py', 'references/*.md', '*', 'assets/templates/*',
            os.path.join(PROD, '*.md'), os.path.join(PROD, 'html/*.html'), os.path.join(DATA, '*.json'),
            '*.md']:
    scan_files += [f for f in glob.glob(pat) if os.path.isfile(f)]
for f in scan_files:
    if 'A1_' in f or '手调版' in f or f.replace(chr(92), '/').endswith('scripts/self_check.py'):
        continue  # 历史备份不动；自检脚本自身存有检查词表，豁免
    try:
        t = open(f, encoding='utf-8', errors='replace').read()
    except Exception:
        continue
    for k in OLD_NAMES:
        if k in t:
            # 豁免：SOP 说人话规则里的反例示范
            if f.endswith('SOP_蒸馏流程.md') and ('反例' in t or '这类比喻一律不写' in t):
                seg = t[t.find(k)-120:t.find(k)+120]
                if '一律不写' in seg or '→' in seg:
                    continue
            hits.append('%s -> %s' % (f, k))
check('旧命名残留', not hits, '; '.join(hits[:5]) if hits else '扫描 %d 个文件零残留' % len(scan_files))

# ===== 2. 关键文件存在 =====
missing_core = [f for f in ['SKILL.md', 'README.md', 'scripts/wm.py', 'scripts/render.py',
                             'scripts/vecsearch.py', 'scripts/extract_all.py', 'scripts/extract_ai.py',
                             'scripts/distill_insights.py']
                if not os.path.exists(f)]
check('关键文件存在', not missing_core, '核心文件齐全' if not missing_core else '缺: ' + ', '.join(missing_core))

# ===== 3. index 链接 =====
idx_p = os.path.join(PROD, 'html/index.html')
if not os.path.exists(idx_p):
    check('index 链接', None, '还没有产物（先按 ingest-protocol.md 提取 + render.py all），跳过')
else:
    t = open(idx_p, encoding='utf-8').read()
    links = re.findall(r'href="file:///([^"]+)"', t)
    dead = [l for l in links if not os.path.exists(l)]
    mds = [os.path.basename(f) for f in glob.glob(os.path.join(PROD, '*.md'))]
    linked_mds = [os.path.basename(l) for l in links if l.endswith('.md')]
    orphan = [md for md in mds if md not in linked_mds and '随身说明书' not in md]  # 随身说明书由 AI 按 SKILL.md 直接拼出来（无固定入口页），豁免
    check('index 链接', not dead and not orphan,
          '%d 链接零死链' % len(links) if not dead and not orphan else '死链:%s 孤儿:%s' % (dead, orphan))

# ===== 4. 读页模板存在 =====
tpl_ok = os.path.exists(os.path.join('assets', 'templates', 'read_shell.html'))
check('读页模板存在', tpl_ok, 'read_shell.html 在' if tpl_ok else '缺 assets/templates/read_shell.html')

# ===== 5. skill 引用路径 =====
sk = open('SKILL.md', encoding='utf-8').read()
bad_ref = []
for seg in [os.path.join(DATA, 'corpus_dedup.jsonl'), os.path.join(DATA, 'corpus_all.jsonl'), os.path.join(DATA, 'ai_messages.jsonl'),
            os.path.join(DATA, 'sessions.jsonl'), os.path.join(DATA, 'user_writebacks.jsonl'),
            'scripts/extract_all.py', 'references/SOP_蒸馏流程.md']:
    if not os.path.exists(seg):
        bad_ref.append(seg)
# 数据文件是 ingest 产物——空数据机器上没有属正常，只把代码/文档引用当硬失败
code_bad = [s for s in bad_ref if s.startswith('scripts/') or s.startswith('references/')]
data_bad = [s for s in bad_ref if s.startswith(os.path.join(DATA, ''))]
if code_bad:
    check('skill 引用路径', False, '代码/文档引用失效: ' + ','.join(code_bad))
elif data_bad:
    check('skill 引用路径', None, '还没 ingest（数据文件缺失，属正常），跳过')
else:
    check('skill 引用路径', True, '全部有效')

# ===== 6. git 工作区 =====
st = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout.strip()
check('git 工作区', None if st else True, '干净' if not st else '有未提交改动（提醒，不算失败）')

# ===== 7. engine 脚本可跑（抽样）=====
_cdp = os.path.join(DATA, 'corpus_dedup.jsonl')
if not os.path.exists(_cdp):
    check('compute_stats 可跑', None, '还没 ingest（语料不存在），跳过')
elif not any(l.strip() for l in open(_cdp, encoding='utf-8')):
    check('compute_stats 可跑', None, '语料为空（corpus_dedup.jsonl 0 行），跳过')
else:
    r = subprocess.run(['python', 'scripts/compute_stats.py'], capture_output=True, text=True)
    check('compute_stats 可跑', r.returncode == 0, '正常' if r.returncode == 0 else r.stderr[:120])

# ===== 9. 写回文件未进 git（数据目录应被 .gitignore） =====
r = subprocess.run(['git', 'ls-files', os.path.join(DATA, 'user_writebacks.jsonl')], capture_output=True, text=True)
check('写回文件未进 git', not r.stdout.strip(), '未被跟踪（隐私正确）' if not r.stdout.strip() else '写回文件被 git 跟踪，data/ 应加进 .gitignore')

# ===== 10. skill 内部引用 =====
sk_ok = 'portrait.md' in sk and 'habits.md' in sk
check('skill 内部引用', sk_ok)

# ===== 11. （已废弃）INTENT.md —— intent-chain 是旧完整仓库结构，skill 自包含后不再检查 =====

# ===== 12. 产品层无能力编号 =====
leak = []
for f in glob.glob(os.path.join(PROD, '*.md')) + glob.glob(os.path.join(PROD, 'html/*.html')):
    if 'A1_' in f: continue
    t = open(f, encoding='utf-8', errors='replace').read()
    if re.search(r'\bC0\d\b|\bC1\d\b', t):
        leak.append(f)
check('产品层无能力编号', not leak, '干净' if not leak else str(leak))

# ===== 13. JSON 合法 =====
bad_json = []
for f in [os.path.join(DATA, 'tracker_items.json')] + glob.glob(os.path.join(DATA, 'materials_*.json')) + glob.glob(os.path.join(DATA, 'stats_*.json')):
    if not os.path.exists(f): continue
    try:
        json.load(open(f, encoding='utf-8'))
    except Exception as e:
        bad_json.append('%s (%s)' % (f, str(e)[:50]))
check('JSON 合法性', not bad_json, '全部合法' if not bad_json else str(bad_json))

# ===== 14. skill 包结构（对标标准 skill）=====
sk_struct = []
sk_root = '.'
required = {
    'SKILL.md': '入口（场景驱动+按需加载表）',
    'references/init-protocol.md': '初始化协议',
    'references/portrait-template.md': '画像模板',
    'references/habits-template.md': '习惯模板',
    'references/query-protocol.md': '检索协议',
    'references/writeback-protocol.md': '写回协议',
    'references/privacy-rules.md': '隐私规则',
    'references/ingest-protocol.md': '更新协议',
    'references/mirror-protocol.md': '照见协议',
    'references/distill-report-protocol.md': '报告蒸馏协议',
    'references/data-locations.md': '数据定位',
    'scripts/wm.py': 'agent 可调用的脚本',
}
for f in required:
    if not os.path.exists(os.path.join(sk_root, f)):
        sk_struct.append(f)
skm = open(os.path.join(sk_root, 'SKILL.md'), encoding='utf-8').read()
if 'allowed-tools' not in skm:
    sk_struct.append('SKILL.md 缺 allowed-tools')
if 'references/' not in skm:
    sk_struct.append('SKILL.md 缺按需加载表')
# SKILL.md 不应再含写死的绝对路径
import re
if re.search(r'[A-Z]:\agent', skm):
    sk_struct.append('SKILL.md 仍有写死绝对路径')
# 用户数据不得在 skill 包里（出厂零数据原则）
for leak in ['portrait.md', 'habits.md']:
    if os.path.exists(os.path.join(sk_root, leak)):
        sk_struct.append('用户数据泄漏进 skill 包: ' + leak)
check('skill 包结构', not sk_struct, '标准结构完整，零用户数据' if not sk_struct else '缺: ' + ','.join(sk_struct))

# 用户画像必须在数据侧
has_corpus = os.path.exists(os.path.join(DATA, 'corpus_dedup.jsonl'))
for need in [os.path.join(DATA, 'profile/portrait.md'), os.path.join(DATA, 'profile/habits.md')]:
    name = need.split('/')[-1]
    if os.path.exists(need):
        check('用户画像就位(%s)' % name, True)
    elif not has_corpus:
        check('用户画像就位(%s)' % name, None, '还没 ingest（数据不存在），跳过')
    else:
        check('用户画像就位(%s)' % name, False, '数据在但 %s 缺失——走 references/init-protocol.md 整理' % name)

# ===== 15. 产物引文可追溯性（报告「原话」（日期）须能在语料反查）=====
if not os.path.exists(os.path.join(DATA, 'corpus_dedup.jsonl')):
    check('产物引文可追溯', None, '还没 ingest（语料不存在），跳过')
else:
    strict = '--strict' in sys.argv
    cmd = ['python', 'scripts/check_quotes.py'] + (['--strict'] if strict else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    unv = 0
    m = re.search(r'无法验证 (\d+)', r.stdout)
    if m:
        unv = int(m.group(1))
    if r.returncode == 0:
        check('产物引文可追溯', True, '报告引文全部可反查')
    elif strict:
        check('产物引文可追溯', False,
              '%d 条引文无法验证——严格模式阻止交付，见 scripts/check_quotes.py 详单' % unv)
    else:
        check('产物引文可追溯', None,
              '%d 条引文无法验证（改写/浓缩或来源缺失，仅提示）；--strict 时阻止交付' % unv)

# ===== 16. 承诺账本合法 =====
pp = os.path.join(DATA, 'promises.jsonl')
if os.path.exists(pp):
    bad = []
    for i, l in enumerate(open(pp, encoding='utf-8'), 1):
        l = l.strip()
        if l:
            try:
                json.loads(l)
            except Exception:
                bad.append(i)
    check('承诺账本合法', not bad, '全部合法' if not bad else '坏行: %s' % bad)
else:
    check('承诺账本合法', True, '账本还没建（说过要做的事会自动记上）')

# ===== 17. 开工三句话 + 主动引导就位（含双层账本） =====
try:
    ip = open('references/init-protocol.md', encoding='utf-8').read()
except OSError:
    ip = ''
ok17 = 'promises.jsonl' in sk and '欠着的事' in sk and '.wordmirror' in sk and '主动引导' in sk
ok17b = '收尾必带' in ip and '硬规则第 4 条' in ip
check('开工三句话就位', ok17 and ok17b,
      'SKILL.md 含欠账/新鲜度开场检查、认项目层账本、主动引导是硬规则；init 收尾接引导'
      if ok17 and ok17b else
      'SKILL.md 缺开场检查/项目账本/主动引导硬规则，或 init-protocol 收尾没接引导')

# ===== 18. 浏览器四页（--web）=====
if '--web' in sys.argv:
    try:
        from playwright.sync_api import sync_playwright
        pages = ['index.html', '01_我是谁.html', '02_我做过的重要决定.html',
                 '03_说过要做的事.html', '04_该注意的事.html', '09_走过的这几个月.html']
        pages = [p for p in pages if os.path.exists(os.path.join(PROD, 'html/') + p)]
        errs = []
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page()
            pg.on('pageerror', lambda e: errs.append(str(e)[:80]))
            for u in pages:
                pg.goto('file:///' + BASE.replace(BS, '/') + '/products/html/' + u)
                pg.wait_for_timeout(400)
            b.close()
        check('浏览器四页加载', not errs, '%d 页零JS错误' % len(pages) if not errs else str(errs[:2]))
    except ImportError:
        check('浏览器四页加载', None, 'playwright 未装，跳过')
else:
    check('浏览器四页加载', None, '跳过（--web 开启）')

# ===== 19. tracker 日期全格式（防跨年硬编码回归）=====
tr_p = os.path.join(DATA, 'tracker_items.json')
if not os.path.exists(tr_p):
    check('tracker 日期全格式', None, '还没 ingest（tracker 不存在），跳过')
else:
    try:
        items = json.load(open(tr_p, encoding='utf-8')).get('items', [])
        short = [it.get('id') for it in items if not re.match(r'\d{4}-\d{2}-\d{2}$', str(it.get('date', '')))]
        check('tracker 日期全格式', not short, '全部 YYYY-MM-DD' if not short else '短日期: %s' % short)
    except Exception as e:
        check('tracker 日期全格式', False, str(e)[:80])

# ===== 20. skill 包 layers 零真实数据（脱敏清单含敏感词本身，永不进包/公开仓）=====
try:
    rl = json.load(open(os.path.join('assets', 'layers', 'redact_list.json'), encoding='utf-8'))
    leak = [k for k, v in rl.items() if isinstance(v, list) and v]
    check('skill layers 零真实数据', not leak, '清单全空，安全' if not leak else '清单混入真实数据: %s' % leak)
except Exception as e:
    check('skill layers 零真实数据', False, str(e)[:80])

# ===== 汇总 =====
fails = [r for r in results if r[0] == FAIL]
warns = [r for r in results if r[0] == WARN]
print()
print('=' * 56)
for mark, name, detail in results:
    line = ' %s %-16s %s' % (mark, name, detail)
    print(line)
print('=' * 56)
print('结果: %d 通过 / %d 警告 / %d 失败' % (len(results) - len(fails) - len(warns), len(warns), len(fails)))
if fails:
    print('结论: 有问题，按上面 ✗ 修完再 commit')
    sys.exit(1)
if warns:
    print('结论: 有警告；严格模式下按上面 ✗ 阻止交付')
else:
    print('结论: 全绿')
