# 交接文档

> 写给完全没有上下文的新会话。最近更新：2026-07-24。
> 本文档覆盖两个独立任务：intent-anchor 改造（已完成）、blue-interview 优化（部分完成，待补测）。

---

## 任务 A：intent-anchor 改造（已完成）

### 背景

用户在 EnterpriseMatchHub 项目中使用 intent-anchor → to-prd → to-issues 链路后，发现实现结果存在质量问题：

- 原型页在项目目录里，但没成为 UI 验收标准，实现时做成线框就标 done
- "金刚区"等行业黑话原样进了文档和界面文案
- FRANCHISE / TRANSFER / COOP 等英文码直接显示在界面上

用户归因：意图方向对，缺"UI 以原型为准"硬约束；PRD 功能对，黑话多，缺原型验收章；Issues 验收没绑 prototype。

### 改造范围

- 只改 `e:\agent\blue-skillhub\skills\intent-anchor`（源码）
- to-prd / to-issues 是第三方 skill，不直接改，通过 intent-anchor Phase 4 交接 prompt 注入约束（方案 A）
- `.claude` 和 `.codex` 下的运行态副本不修改

### 改了什么（3 处改动，9 个文件）

**改动 1：识别设计标准**

Phase 2 新增 Step 7：检查项目目录中是否存在 `prototype/`、`*.fig`、设计稿导出、可点 HTML 等素材。有则请用户确认作为 UI 验收基线，记录到 INTENT.md 第 12 节。无则记录用户确认"没有"。不得跳过。

**改动 2：标记术语**

Phase 2 新增 Step 8：逐项审查能力表中的"能力"和"描述"列，识别行业黑话，给出人话翻译和界面文案，记录到 INTENT.md 第 13 节。无术语时记录"无术语需要翻译"。

**改动 3：增强交接 prompt**

Phase 4 交接 prompt 新增：
- 设计标准约束：PRD 列出设计文件路径、工单 Acceptance criteria 包含"对照 {设计文件} 结构一致"、Done 定义包含 UI 对照
- 术语约束：界面使用人话翻译、原始术语只允许在开发文档中

**涉及的文件**

| 文件 | 改动 |
|---|---|
| `SKILL.md` | Phase 2 加 Step 7/8，Phase 2.5 表格加 S6/S7，强制规则第 4 条更新为 S1-S7，Phase 4 交接 prompt 加约束，必需章节列表加第 12/13 节 |
| `templates/INTENT.md` | 新增第 12 节（设计标准）和第 13 节（术语表） |
| `references/semantic-audit.md` | 新增 S6（设计标准）和 S7（术语标记）规则，执行要求更新为 S1-S7 |
| `templates/stage-gate-check.md` | brainstorm/PRD、任务拆分、开发完成三阶段加设计标准和术语检查项 |
| `scripts/intent_validate.py` | REQUIRED_SECTIONS 加第 12/13 节，V2 改为 13 个章节，V9 扩展到 S1-S7，新增 V10（设计标准校验）和 V11（术语表校验） |
| `tests/fixtures/valid-intent.md` | 加第 12/13 节和 S6/S7 复核记录 |
| `tests/test_intent_validate.py` | 期望检查数 9→11，新增 TestDesignStandards 和 TestTerminology 测试类 |
| `README.md` | 工作流图加 S6/S7，检查项数量 9→11，语义复核 S1-S5→S1-S7 |
| `INTENT.md` | 能力表第 11 项和不可妥协项第 3 条的 S1-S5→S1-S7 |

### 验证状态

- `python -m pytest skills/intent-anchor/tests/test_intent_validate.py -v` → 27 passed，退出码 0
- `.claude` 运行态已还原到 HEAD 版本（19 passed，确认不包含本次改动）
- 独立验收报告结论：原始 3 项改造需求全部 PASS，初次验收发现的 3 处文档漏改和 1 处 CRLF 噪音已全部修复

### 踩过的坑

1. **改错位置**：第一次改到了 `.claude` 下的运行态副本，用户纠正后改回源码位置，并还原了 `.claude`
2. **中文引号 SyntaxError**：Python 字符串中包含中文引号 `"` `"` 导致语法错误，用 Unicode 码位精确修复
3. **CRLF 噪音**：`intent_validate.py` 行尾从 LF 变为 CRLF 导致 git diff 显示全文件重写（603 增/527 删），还原为 LF 后恢复正常（80 增/4 删）

### git 状态

改动均未提交，处于工作区未暂存状态。基线：`HEAD`（commit `b333c8a`）。

---

## 任务 B：blue-interview 优化（部分完成，待补测）

> 以下内容来自 2026-07-09 会话，保持原样。skill 被 `.gitignore` 忽略，不入库。

### 背景

围绕仓库内 skill：`skills/blue-interview/`（中文面试教练）。

目标：中文面试备考场景下，能否给准备面试的用户带来实质性帮助。

### 已落地（5 项改动，2 个文件）

| ID | 问题 | 状态 |
|---|---|---|
| P1 | 分析后未强制开口 | 已落地，未测到 |
| P2 | 重说易被绕过 | 已落地，未测到 |
| P3 | HR/敏感题陪练不足 | 已落地，试跑基本通过 |
| P8 | ASR 误差被当表达问题 | 已落地 |
| P9 | 跨题重复 | 已落地 |

已改文件（被 `.gitignore` 忽略，不入库）：
- `references/hr-pressure-playbook.md`：76 → 156 行
- `SKILL.md`：331 → 349 行

### 待补测

- P1（分析后开口）：说"帮我分析这个 JD"看是否开口
- P2（重说降级）：被要求重说后说"不想重说，直接给终稿"看是否降级
- P8（ASR）：用语音输入看是否整轮不再纠 ASR 误差
- P9（跨题去重）：连续练 3 题看是否跨题去重

### 试跑结果（2026-07-09，grok-4.5）

日志：`blue-interview-log/2026-07-09-122014-command-messageblue-interviewcommand-message.txt`

练了 4 题（自我介绍→离职原因→空窗期→薪资期望），全部标已过。P3 基本通过，P1/P2 未测到，P8/P9 试跑后发现并已修复。

### 禁令

未经明确同意禁止修改 `skills/blue-interview/`。

---

## 新会话开场最短上下文

```text
任务 A（已完成）：intent-anchor 改造——Phase 2 加设计标准识别和术语标记，Phase 4 交接 prompt 注入约束。
  9 个文件已改，27 测试通过，未提交 git。基线 HEAD=b333c8a。
  .claude/.codex 运行态不修改，已还原。

任务 B（待补测）：blue-interview P1/P2/P3/P8/P9 已落地，P3 试跑通过，P1/P2/P8/P9 待补测。
  skill 被 .gitignore 忽略，不入库。未经同意禁止修改。

详情：见仓库根目录 HANDOFF.md。
```
