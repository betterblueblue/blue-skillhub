# 初始化协议 · 第一次使用 / 新机器

> 触发场景：skill 加载后读不到 portrait.md / habits.md（数据还没生成），或用户说"初始化""第一次设置""在这台机器上启用"。
> 原则：**skill 包出厂不含任何用户数据**——portrait/habits 由用户自己的对话整理出来，属于用户。

## 初始化流程（对用户说，一步步来）

### 第 1 步：探测（只读，不改任何东西）

你自己看这台机器上有哪些 agent 的存档（常见位置 `~/.claude/projects`、`~/.codex/`、各 AI 的记录目录），数一下各有多少文件。一个都没有 → 这个 skill 现在用不了，告诉用户"先正常用一段时间 AI 再来"。

### 第 2 步：提取（第一次跑，量大的话要几分钟）

```bash
python <skill目录>/scripts/wm.py ingest
```

输出：你说过的话有多少条 + 量级提示（<500 条会提示"了解得还比较粗"）。

### 第 3 步：整理出你的情况（portrait.md / habits.md）

数据就位后，**你（AI）来写这两份文件**，写到数据目录（定位见 `references/data-locations.md`）下：

- `portrait.md` —— 按 `references/portrait-template.md` 的结构，从你说过的话里整理
- `habits.md` —— 按 `references/habits-template.md` 的结构

整理方法：读 `data/stats_wordfreq.json`（高频词频率，通用词表计数）+ `data/materials_*.json`（素材）+ 抽读你说过的话，按模板章节填。**说人话规则**：用户的词优先，禁用发明术语；每条判断要有原话+日期支撑。

### 第 4 步：验证 + 告知

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
