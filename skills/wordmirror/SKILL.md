---
name: wordmirror
description: 用户明确要回顾自己的原话或承诺、按已记录的偏好办事、记住或更正一件事、查看或更新个人报告、向别人分享公开说明书时使用。普通任务和进度说明不触发。
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# 言镜 · wordmirror

> 本文里"你"指 Agent，"用户"指说话的人。给用户看的页面文案统一用"你"称呼用户（见 `references/distill-report-protocol.md`）。

让用户在任何 AI 里开工时都被认识：用户是谁、在忙什么、跟用户说话要守什么规矩；用户随口问"我说过啥"，能翻出带日期的原话。

**分工：判断归你，脚本只做管道。** 脚本负责提取存档、去重、算统计素材、把 MD 排成 HTML、记账写回、按意思搜。报告里的每一句话都由你读原话后写出来；统计和正则候选只是素材，不许直接上页。报告的目的是以言为镜：原话是主角，数字退到背景，没有证据就留白。

> **脚本路径**：本技能目录是 `${CLAUDE_SKILL_DIR}`。下文命令里的 `scripts/…` 和引用的 `references/…` 都相对这个目录，不是当前项目目录；`data/…` 在数据目录里（见「数据在哪」）。这个路径没被替换成实际目录时（别的客户端），用本 SKILL.md 所在目录的绝对路径。

## 先选任务，再读数据

- **公开分享**：直接走 `references/privacy-rules.md`。个人资料只从 `data/layers/public.md` 取；不读画像、原话、纠正记录、承诺或私有脱敏清单，也不运行初始化或进度检查。公开层缺失或内容不够，就请用户当次提供可公开的文字。
- **本机使用**：按下表只读本次需要的文件。问既有偏好时读 `data/profile/habits.md`；请求恢复工作情境时读 `data/profile/current-context.md`。只有用户要求初始化、更新报告或继续上次更新时，才查 `wm.py progress` 或启动对应流程。
- **普通任务**：「我要做一个设置页」「这个修复做完了」不是记账请求。直接做原任务，不读写言镜数据，不提醒用户更新画像。

## 主动到哪一步

先判断用户处在探索、决策、执行、验证、收尾、复盘还是闲聊，再定说多少：

- **L0 不读取**：任务不需要历史，就不查个人资料。
- **L1 一句提醒**：命中已确认的决定或纠正，带一句依据。
- **L2 方向提醒**：当前动作可能和旧决定冲突，问是重新打开还是只做验证。
- **L3 行动确认**：改文件、写长期记忆、删除、推送、对外分享、改变决定，先确认。

准备可以主动，提醒最多一句，判断不替用户，行动必须确认。执行期少展开，探索期给相关历史，决策期帮着看取舍。

## 用户说什么 → 读哪份协议

| 用户说 | 你做什么 | 协议 |
|---|---|---|
| "我之前说过什么 / 上次怎么想 / 哪些没下文 / 前后说法变了吗" | 在 `data/corpus_dedup.jsonl` 里搜，同义词和口语变体都试；字面搜不到再用 `python scripts/vecsearch.py status` / `query` 按意思搜（没建索引先问用户）。结论先行，引文带日期和 agent；前后对比只并排摆，不判谁对 | `references/query-protocol.md` |
| "帮我记住 X / 把那条承诺标成完成 / 更正我记过的数字" | 只写用户指定的内容。承诺走 `wm.py promise add/done/drop`，事实走 `wm.py wb add`，纠正走 `wm.py corr add`。不能确定要改哪条时先问 | `references/writeback-protocol.md` |
| "把我的情况告诉这个 AI / 出一页能贴走的" | 只读 `data/layers/public.md`，绝不碰 portrait.md；去隐私后拼成随身说明书，发出前给用户过目 | `references/privacy-rules.md` |
| "更新数据 / 更新我的报告 / 情况过期了" | 由你编排，不让用户自己跑 CLI：按 8 步提取，再读原话写六页，补录承诺和照见，渲染、自检，每步记进度 | `references/ingest-protocol.md` → `references/distill-report-protocol.md` |
| 单独重写某一页 / 某个产物 | 按提示词总表的八字段执行 | `references/distill-prompts.md` |
| "看看报告页面" | `python scripts/render.py all`，告诉用户文件在哪、双击就能看；没有 MD 的页显示空态，不用候选凑 | `references/distill-report-protocol.md` |
| "帮我初始化言镜" | 探测 → 提取 → 写 portrait/habits 和六页 → 判断承诺和照见 → 渲染 → 自检 → 念给用户听、当场纠错。其他任务缺文件时说明缺什么，不自动初始化 | `references/init-protocol.md` |

六页各自回答的问题：01 你是谁（现在在哪、怎么共事）/ 02 那几条线（怎么起、哪里拐、停在哪）/ 03 说话算数（说过要做的事后来怎样）/ 04 你没看见的（有原话撑着的事实落差，没有就空着）/ 05 AI 眼里的你（换工具换没换说法、AI 看错过几次）/ 06 这几个月（这个月比上个月变了什么）。

## 数据在哪

- **全局层**（用户是谁，跟着人走）：`WORD_MIRROR_HOME` → `~/.wordmirror/bind.json` → `~/.wordmirror/`，详见 `references/data-locations.md`。主力文件在 `data/`：`corpus_dedup.jsonl`（用户每句话 `{agent, date, proj, sid, msg}`）、`user_writebacks.jsonl`、`profile/portrait.md`、`profile/habits.md`、`progress.json`、`chroma_index/`（可选）。
- **项目层**（这个项目说过要做的事）：`<当前目录>/.wordmirror/promises.jsonl`。里面是原话，提醒用户在项目 `.gitignore` 加一行 `.wordmirror/`。
- 只写 `~/.wordmirror` 和项目层 `.wordmirror/`；skill 包内不写任何个人数据。

## 硬规则

1. 引用用户原话必须带日期，只从搜出来的原话里取，不凭记忆默写；编一次都不行。查不到就直说查不到。
2. 用户数据只在本机用，不进任何外部请求，除非用户当次明确说可以（`references/privacy-rules.md`）。
3. 记账和写回只走 `wm.py promise / wb / corr` 命令，不手写 jsonl。
4. **亮家底**：仅在初始化收尾时，用一句话告诉用户还能出六页回望、承诺网页和随身说明书；用户说不用就停。
5. **不评判、不定性、不诊断**：不贴性格标签，不推断动机，不诊断情绪，不说"我注意到你最近……"式的价值判断。
6. **可以说破事实落差，守四条**：只点说与做不一致、反复提起没下文、前后说法相反、口头禅频率突变；每条带日期和原话；用问句收尾，结论归用户；用户说"别说了"立刻停，纠正过的不再点。开场最多一条（`references/mirror-protocol.md`）。
7. 页面文案说人话：标题、小节名、正文都不用内部词和翻译腔。写完页面必须跑 `python scripts/render.py all` 和 `python scripts/self_check.py`，把实际结果告诉用户。

## 主动引导

仅在用户已请求的本机回顾或更新里推荐相关下一步，不在普通任务中因日期、近况或完成工作而主动查资料。
