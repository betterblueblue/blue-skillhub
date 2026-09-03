# 初始化协议 · 第一次使用 / 新机器

> 触发场景：skill 加载后读不到 portrait.md / habits.md（数据还没生成），或用户说"初始化""第一次设置""在这台机器上启用"。
> 原则：**skill 包出厂不含任何用户数据**——portrait/habits 由用户自己的对话整理出来，属于用户。

## 初始化流程（对用户说，一步步来）

### 第 1 步：探测（只读，不改任何东西）

你自己看这台机器上有哪些 agent 的存档（常见位置 `~/.claude/projects`、`~/.codex/`、各 AI 的记录目录），数一下各有多少文件。一个都没有 → 这个 skill 现在用不了，告诉用户"先正常用一段时间 AI 再来"。

### 第 2 步：提取（第一次跑，量大的话要几分钟）

按 `references/ingest-protocol.md` 的 **8 步逐步执行**（探测 → 提取你的话 → 提取 AI 回复 → 去重 → 会话卡 → 数字底座 → 素材 → 渲染），每步一个脚本，顺序不能乱。

输出：每步脚本打印产物条数；第 8 步的渲染必须放到第 6 步完成之后，不能在最终内容定稿前提前宣布报告完成。

**依赖先探测，别再每次都问**：zstandard（dsh 用）先跑 `python -c "import zstandard"`，能 import 就直接用；按意思搜索引先跑 `python scripts/vecsearch.py status`，建过就直接用。**只有真没装/真没建，才问用户一次要不要装/建。**

### 第 3 步：整理情况和报告（Agent 判断，不能只跑脚本）

数据就位后，**你（AI）来读原话并写成最终内容**，写到数据目录（定位见 `references/data-locations.md`）下：

- `portrait.md` —— 按 `references/portrait-template.md` 的结构
- `habits.md` —— 按 `references/habits-template.md` 的结构
- 6 份报告 MD：`decisions.md`、`recurs.md`、`tasks.md`、`ai-view.md`、`agents.md`、`timeline.md`

整理方法：读 `data/stats_*.json` 和 `data/materials_*.json` 只当线索，再抽读 `corpus_dedup.jsonl` / `ai_messages.jsonl` 核实。**说人话规则**：用户的词优先，禁用发明术语；每条判断要有原话+日期支撑；没有料就留白，不能把统计或候选直接上页。**每个产物的具体写法见 `references/distill-prompts.md` 第二部分的对应提示词。**

### 第 4 步：补录说过要做的事

从历史原话中筛选明确承诺（“我要做 / 我准备做 / 我打算做”），排除技术执行指令、普通执行指令、示例文本、讨论中的假设、AI 生成模板句和“我在想要不要”。逐条调用 `python scripts/wm.py promise add "事项" --date 原始日期 --proj 项目 --ref 原话 --agent initialization` 写入承诺账本；不要手写 JSONL。**补录历史承诺必须带 `--date` 原始日期（不是登记当天），判断标准和写回字段见 `references/distill-prompts.md` 的 promises 提示词。**

- `promises.jsonl` 可以为空，但必须完成判断，并明确告诉用户“目前没有足够明确的承诺被登记”。
- 有承诺时，登记后运行 `python scripts/wm.py promise` 验证账本可读。

### 第 5 步：筛选并定稿照见

读取 `data/materials_insights.json`，逐条回查语料。只有确实存在“说了没做 / 前后说法相反 / 口头禅变化”的证据才追加到 `data/profile/insights.jsonl`，格式和状态遵循 `references/mirror-protocol.md`。**筛选和成文标准见 `references/distill-prompts.md` 的 insights 提示词。**

- 候选是假阳性就丢掉，不直接复制。
- `insights.jsonl` 可以为空，但不能静默跳过；要向用户说明“本次没有足够可靠的照见”。
- 不做动机推断、性格标签或心理诊断。

### 第 6 步：渲染、自检和交付

所有画像、6 份报告 MD、promises 和 insights 定稿后，才运行：

```bash
python scripts/render.py all
python scripts/self_check.py
```

核对 03、04 是否有数据或明确空态原因；把实际生成的页面路径、03/04 状态、以及自检结果告诉用户。初始化只有完成上述交接才算完成。

### 第 7 步：验证 + 告知

- 让用户看一眼你的情况要点（念给他听），当场纠错——用户说"不对"的直接改
- 自己确认数据目录找对了（按 `references/data-locations.md`，主力文件在不在）
- **收尾必带一句**（硬规则第 4 条）："以后你的情况能出这个月的报告、说过要做的事的网页、随身说明书，想要哪个直接说。"——用户是第一次接触这个 skill，不告诉他能出这些，他永远不知道
- 完成。此后正常使用：按 SKILL.md 的"每类事怎么做"走

## 数据和程序的分界（重要）

| 属于 skill 包（出厂自带） | 属于用户（初始化生成） |
|---|---|
| SKILL.md / references/ / scripts/ / assets/layers/（模板） | portrait.md / habits.md |
| protocols、模板、隐私清单 | data/ 全部（你说的话、对话记录、统计） |
| 别人 clone 得到同样的东西 | 每个人完全不同 |

**用户数据永远不进 skill 包目录**——skill 可以随时升级覆盖，用户数据不受影响。
