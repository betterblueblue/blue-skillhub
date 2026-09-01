---
name: wordmirror
description: 用户本人的说明书：他是谁、在忙什么、怎么跟他说话。任何 agent 加载本 skill 即认识用户。当用户提到"我之前说过什么""我上次怎么想的""按我的习惯来""记住这个决定""我说话有什么口头禅""我哪几个项目没下文""更新我的画像""我要做X""这个事做完了"，或用户犹豫纠结、agent 需要用户背景/偏好/历史决策才能答好问题时使用。
allowed-tools: Read, Grep, Glob, Bash, Edit
---

# 言镜 · wordmirror · 认识我

本 skill 的数据只在用户本机。加载即视为认识用户，回答默认遵守 habits.md。

## 第一步：认识用户（加载后立即）

从**数据目录**（定位见 `references/data-locations.md`）读两个文件：
**portrait.md**（用户是谁、在忙什么、干活的脾气）、**habits.md**（跟用户说话的规矩、口头禅的真实意思）。

读不到这两个文件 = 用户数据还没生成 → 走 `references/init-protocol.md`（初始化流程）。

读完画像和规矩，开工前看三个小本子（合计不超过三句话，说完就干正事）：

1. **欠账（两层都看）**：当前目录 `.wordmirror/promises.jsonl`（若存在）+ 数据目录 `data/promises.jsonl`（若存在）里 status=open 的，加上 `data/tracker_items.json` 里 status=stalled 的，挑最老的一件提一句："你 X 天前说的 XX 还没下文"
2. **资料新鲜度**：portrait.md 顶部日期距今超过 30 天 → 提一句"画像有 X 天没更新了，要不要补最近的情况"
3. 两条都没有 → 直接开工，一句废话不说

## 按需加载（什么场景读什么）

| 用户说 / 场景 | 读这个 | 然后做 |
|---|---|---|
| "我之前说过什么 / 我上次怎么想的 / 某话题我的观点" | `references/query-protocol.md` | 按协议检索原话，回答必须带日期 |
| "记住这个 / 我决定了X / 状态变了" | `references/writeback-protocol.md` | 按协议写回，一条事实一行 |
| "把我的情况告诉这个 agent / 分享我的画像" | `references/privacy-rules.md` | 先过脱敏清单，绝不直接给 private 层 |
| "更新数据 / 重新提取 / 画像过期了" | `references/ingest-protocol.md` | 跑 scripts/ds.py ingest |
| 首次使用 / 读不到 portrait.md | `references/init-protocol.md` | 按四步初始化（探测→提取→生成画像→验证） |
| "哪些事说了没下文 / 我的项目都怎么样了" | `references/query-protocol.md` 第 3 节 | 查搁置主题，按天数排 |
| 用户开始写代码、改文档、长时间协作 | 不用额外读，habits.md 已够 | 按习惯规矩干活 |
| 任何收尾时刻（认识完用户/初始化完/出完产物） | "主动引导"节 + 硬规则第 4 条 | 一句话亮家底，句号 |
| 用户犹豫、纠结、比较选项 | `references/query-protocol.md`；可跑 `ds.py contrast 话题` | 先把这个话题最早和最近的说法并排摆出来，再谈建议，AI 不替用户下结论 |
| 用户说"我要做X / 准备Y" | `references/writeback-protocol.md` 承诺记账 | 记入 promises.jsonl（open），当场说一声 |
| 用户说"X做完了 / 这事黄了" | `references/writeback-protocol.md` 承诺记账 | 对应账目改成 closed/dropped，当场说一声 |
| "把说明书导出 / 贴到别的 AI 用" | 跑 `scripts/ds.py export` | 生成随身说明书，告诉用户文件在哪 |

## 主动引导（功能要亮出来，别闷着）

用户不知道这个 skill 能出什么——不引导，月报、看板这些产物就永远没人用。所以：

1. **首次加载认识完用户**，收尾时用一句话带过家底："除了查记忆，这 skill 还能出月度报告、欠账看板（HTML）、随身说明书，想要哪个直接说。"
2. **刚产出/更新了 md**（画像、随身说明书），紧跟一句配套引导（对照下表）。引导不超过一句，用户说不用就闭嘴，下不为例。

| 你刚出了 / 用户提到 | 补一句 |
|---|---|
| portrait.md / habits.md 更新 | "要不要看『我说过要做的事』的 HTML 看板？哪件没下文一眼看清" |
| 用户聊到"这个月干了啥" / 月底月初 | "出个月度三页纸？语料都在，一分钟的事"（`ds.py monthly`） |
| 某话题前后说法对不上 | "我把这话最早和最近的版本并排给你看？"（`ds.py contrast`） |
| 用户要给别人介绍自己 / 贴到别的 AI | "出一页随身说明书？"（`ds.py export`） |
| 出了任何 HTML 产物 | 告诉用户文件在哪，双击就能看，单文件零依赖 |

> 注意：月报（`ds.py monthly`）和 HTML 看板依赖 engine/ 目录——只装了 skill 包时出不了，如实告知"这功能在完整仓库里"，别引导用户去跑会报错的命令。`contrast` / `export` / 欠账本不依赖引擎，随时能出。

## 硬规则（任何时候）

1. 引用我的原话必须带日期；编我没说过的话，一次都不行
2. 用户数据（数据目录里的 portrait.md 含隐私）只在本机本会话用，不进任何外部请求——除非我当次明确说"可以"（详见 references/privacy-rules.md）
3. 数据目录怎么找：见 `references/data-locations.md`（按机器自动定位，不写死路径）
4. **加载或初始化收尾，必须亮一次家底**：用一句话告诉用户本 skill 还能出什么（月度三页纸、欠账看板 HTML、随身说明书、新旧说法对比）。不管走的是哪条路径——认识用户、初始化蒸馏、写回更新——收尾都要带这一句。引导不超过一句，用户说不用就停。详见"主动引导"节

## 数据从哪来

本 skill 的画像由 wordmirror（言镜）管道从用户各 agent 的历史对话蒸馏生成；重新生成方法在 `references/ingest-protocol.md`。
