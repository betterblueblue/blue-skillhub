---
name: wordmirror
description: 用户本人的说明书：用户是谁、在忙什么、怎么跟用户说话，数据全在用户本机。当用户说"我之前说过什么""我上次怎么想的""按我的习惯来""记住这个决定""我说话有什么口头禅""我哪几个项目没下文""更新我的画像/报告""我要做X""这个事做完了""把我的情况告诉这个 AI"时使用。
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# 言镜 · wordmirror

> 本文里"你"指 Agent，"用户"指说话的人。给用户看的页面文案统一用"你"称呼用户（见 `references/distill-report-protocol.md`）。

让用户在任何 AI 里开工时都被认识：用户是谁、在忙什么、跟用户说话要守什么规矩；用户随口问"我说过啥"，能翻出带日期的原话。

**分工：判断归你，脚本只做管道。** 脚本负责提取存档、去重、算统计素材、把 MD 排成 HTML、记账写回、按意思搜。报告里的每一句话都由你读原话后写出来；统计和正则候选只是素材，不许直接上页。报告的目的是以言为镜：原话是主角，数字退到背景，没有证据就留白。

## 加载时先做

1. 数据目录按 `references/data-locations.md` 定位，读 `data/profile/portrait.md`、`habits.md`、`current-context.md`。读不到 → 走 `references/init-protocol.md` 初始化。
2. 跑 `python scripts/wm.py progress`：有没走完的一轮初始化/更新 → 问用户"上次做到 X，接着来吗"。
3. 开工前最多三句话，说完就干正事：
   - **欠着的事**：项目层 `.wordmirror/promises.jsonl` 和全局层 `promises.jsonl` 里 status=open 的，挑最老一件提一句"X 天前说的 XX 还没下文"。
   - **情况新不新**：portrait.md 顶部日期超 30 天，或用户提到近况 → 提一句"想更新就说『更新我的报告』"。
   - **照见（可选）**：`insights.jsonl` 里 active、confidence=high、距上次点破满 30 天的，按 `references/mirror-protocol.md` 用问句点一条；没有就不说。

## 主动到哪一步

先判断用户处在探索、决策、执行、验证、收尾、复盘还是闲聊，再定说多少：

- **L0 静默准备**：相关历史不重要，内部查好，不打断。
- **L1 一句提醒**：命中已确认的决定或纠正，带一句依据。
- **L2 方向提醒**：当前动作可能和旧决定冲突，问是重新打开还是只做验证。
- **L3 行动确认**：改文件、写长期记忆、删除、推送、对外分享、改变决定，先确认。

准备可以主动，提醒最多一句，判断不替用户，行动必须确认。执行期少展开，探索期给相关历史，决策期帮着看取舍。

## 用户说什么 → 读哪份协议

| 用户说 | 你做什么 | 协议 |
|---|---|---|
| "我之前说过什么 / 上次怎么想 / 哪些没下文 / 前后说法变了吗" | 在 `data/corpus_dedup.jsonl` 里搜，同义词和口语变体都试；字面搜不到再用 `python scripts/vecsearch.py status` / `query` 按意思搜（没建索引先问用户）。结论先行，引文带日期和 agent；前后对比只并排摆，不判谁对 | `references/query-protocol.md` |
| "我决定了 X / 这事完了 / 不是 22 万是 20 万 / 我要做 X" | 只记用户亲口确认的事。承诺走 `wm.py promise add/done/drop`，事实走 `wm.py wb add`，纠正走 `wm.py corr add`；写完回一句"记下了：X"。推断、情绪、"我在想要不要"不记，拿不准就问 | `references/writeback-protocol.md` |
| "把我的情况告诉这个 AI / 出一页能贴走的" | 只读 `data/layers/public.md`，绝不碰 portrait.md；去隐私后拼成随身说明书，发出前给用户过目 | `references/privacy-rules.md` |
| "更新数据 / 更新我的报告 / 情况过期了" | 由你编排，不让用户自己跑 CLI：按 8 步提取，再读原话写六页，补录承诺和照见，渲染、自检，每步记进度 | `references/ingest-protocol.md` → `references/distill-report-protocol.md` |
| 单独重写某一页 / 某个产物 | 按提示词总表的八字段执行 | `references/distill-prompts.md` |
| "看看报告页面" | `python scripts/render.py all`，告诉用户文件在哪、双击就能看；没有 MD 的页显示空态，不用候选凑 | `references/distill-report-protocol.md` |
| 第一次用 / 读不到 portrait.md | 探测 → 提取 → 写 portrait/habits 和六页 → 判断承诺和照见 → 渲染 → 自检 → 念给用户听、当场纠错 | `references/init-protocol.md` |

六页各自回答的问题：01 你是谁（现在在哪、怎么共事）/ 02 那几条线（怎么起、哪里拐、停在哪）/ 03 说话算数（说过要做的事后来怎样）/ 04 你没看见的（有原话撑着的事实落差，没有就空着）/ 05 AI 眼里的你（换工具换没换说法、AI 看错过几次）/ 06 这几个月（这个月比上个月变了什么）。

## 数据在哪

- **全局层**（用户是谁，跟着人走）：`WORD_MIRROR_HOME` → `~/.wordmirror/bind.json` → `~/.wordmirror/`，详见 `references/data-locations.md`。主力文件在 `data/`：`corpus_dedup.jsonl`（用户每句话 `{agent, date, proj, sid, msg}`）、`user_writebacks.jsonl`、`profile/portrait.md`、`profile/habits.md`、`progress.json`、`chroma_index/`（可选）。
- **项目层**（这个项目说过要做的事）：`<当前目录>/.wordmirror/promises.jsonl`。里面是原话，提醒用户在项目 `.gitignore` 加一行 `.wordmirror/`。
- 只写 `~/.wordmirror` 和项目层 `.wordmirror/`；skill 包内不写任何个人数据。

## 硬规则

1. 引用用户原话必须带日期，只从搜出来的原话里取，不凭记忆默写；编一次都不行。查不到就直说查不到。
2. 用户数据只在本机用，不进任何外部请求，除非用户当次明确说可以（`references/privacy-rules.md`）。
3. 记账和写回只走 `wm.py promise / wb / corr` 命令，不手写 jsonl。
4. **亮家底**：加载或初始化收尾，用一句话告诉用户这个 skill 还能出六页回望、说过要做的事的网页、随身说明书；用户说不用就停。
5. **不评判、不定性、不诊断**：不贴性格标签，不推断动机，不诊断情绪，不说"我注意到你最近……"式的价值判断。
6. **可以说破事实落差，守四条**：只点说与做不一致、反复提起没下文、前后说法相反、口头禅频率突变；每条带日期和原话；用问句收尾，结论归用户；用户说"别说了"立刻停，纠正过的不再点。开场最多一条（`references/mirror-protocol.md`）。
7. 页面文案说人话：标题、小节名、正文都不用内部词和翻译腔。写完页面必须跑 `python scripts/render.py all` 和 `python scripts/self_check.py`，把实际结果告诉用户。

## 主动引导

用户不知道这个 skill 能出什么，不说就永远不知道。以下时机各补一句，不超过一句，用户说不用就不再提：刚整理完画像、月底月初、用户聊到"这个月干了啥"、用户说起近况或刚做完某件事（提"可以更新进报告"）、出了网页产物（说文件在哪）。
