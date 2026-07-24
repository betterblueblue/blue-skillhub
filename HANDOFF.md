# 交接文档

> 写给完全没有上下文的新会话。最近更新：2026-07-24。
> 本文档覆盖五个独立任务：intent-anchor 改造（已完成）、intent-prd / intent-issues 新建（已完成）、intent-dev / intent-verify 拆分与性能安全要求前移（已完成）、README 同步与输出目录/命名统一（已完成）、blue-interview 优化（部分完成，待补测）。

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
| `templates/阶段核对表.md` | brainstorm/PRD、任务拆分、开发完成三阶段加设计标准和术语检查项 |
| `scripts/intent_validate.py` | REQUIRED_SECTIONS 加第 12/13 节，V2 改为 13 个章节，V9 扩展到 S1-S7，新增 V10（设计标准校验）和 V11（术语表校验） |
| `tests/fixtures/valid-intent.md` | 加第 12/13 节和 S6/S7 复核记录 |
| `tests/test_intent_validate.py` | 期望检查数 9→11，新增 TestDesignStandards 和 TestTerminology 测试类 |
| `README.md` | 工作流图加 S6/S7，检查项数量 9→11，语义复核 S1-S5→S1-S7 |
| `INTENT.md` | 能力表第 11 项和不可妥协项第 3 条的 S1-S5→S1-S7 |

### 验证状态

- `python -m pytest skills/intent-anchor/tests/test_intent_validate.py -v` → 33 passed，退出码 0
- `.claude` 运行态已还原到 HEAD 版本（19 passed，确认不包含本次改动）
- 独立验收报告结论：原始 3 项改造需求全部 PASS，初次验收发现的 3 处文档漏改和 1 处 CRLF 噪音已全部修复
- 验收路径改动（第 14 节 / S8 / V12）新增 6 个测试，全部通过

### 踩过的坑

1. **改错位置**：第一次改到了 `.claude` 下的运行态副本，用户纠正后改回源码位置，并还原了 `.claude`
2. **中文引号 SyntaxError**：Python 字符串中包含中文引号 `"` `"` 导致语法错误，用 Unicode 码位精确修复
3. **CRLF 噪音**：`intent_validate.py` 行尾从 LF 变为 CRLF 导致 git diff 显示全文件重写（603 增/527 删），还原为 LF 后恢复正常（80 增/4 删）
4. **中文引号 SyntaxError（第二次）**：新增 V12 验收路径校验时，闭合引号 U+0022 被替换成 U+201D（右花引号），导致 Python 字符串未闭合。用字节级替换修复了 3 处

### git 状态

已提交为 `bc6511b`。任务 A2 的改动在此之上继续，未提交。

---

## 任务 A2：intent-prd / intent-issues 新建（已完成）

### 背景

任务 A 完成后，用户发现端到端实测缺失：开发完的系统没有走一遍完整用户路径验证。根本原因是 to-prd / to-issues 是第三方 skill，不认识 INTENT.md 结构，验收约束只能靠交接 prompt 注入，传递不可靠。

用户决定自己做配套的 intent-prd 和 intent-issues，和 intent-anchor 组成完整链路。命名用 `intent-` 前缀区分：有 INTENT.md 用 intent-prd / intent-issues，没有就用原版 to-prd / to-issues。

### 改造范围

- intent-anchor 再改一轮：加第 14 节（验收路径）、S8、V12、Step 9、stage-gate 检查项、Phase 4 交接 prompt 简化为指向 intent-prd / intent-issues
- 新建 `skills/intent-prd/`：原生读取 INTENT.md 生成 PRD，Acceptance Criteria 使用 Given/When/Then 结构
- 新建 `skills/intent-issues/`：原生读取 INTENT.md + PRD 拆分工单，Acceptance criteria 从 Given/When/Then 拆解为可勾选条目
- `prd_validate.py` 新增 V8 检查（Given/When/Then 结构）
- `.claude` 和 `.codex` 下的运行态副本不修改

### intent-anchor 改动（第 14 节验收路径）

**Phase 2 新增 Step 9**：从保留能力推导端到端验收路径（路径级粒度：入口 → 关键步骤 → 预期结果），请用户确认，记录到第 14 节。用户可感知的保留能力至少出现在一条路径中，基础设施类能力不强制。

**涉及的文件**

| 文件 | 改动 |
|---|---|
| `SKILL.md` | Phase 2 加 Step 9，Phase 2.5 表格加 S8，强制规则 S1-S7→S1-S8，Phase 4 交接 prompt 简化为指向 intent-prd / intent-issues，必需章节加第 14 节 |
| `templates/INTENT.md` | 新增第 14 节（验收路径） |
| `references/semantic-audit.md` | 新增 S8（验收路径）规则，执行要求更新为 S1-S8 |
| `templates/阶段核对表.md` | brainstorm/PRD、任务拆分、开发完成三阶段加验收路径检查项 |
| `scripts/intent_validate.py` | REQUIRED_SECTIONS 加第 14 节，V2 改为 14 个章节，V9 扩展到 S1-S8，新增 V12（验收路径校验），新增 PATH_ID_RE |
| `tests/fixtures/valid-intent.md` | 加第 14 节和 S8 复核记录 |
| `tests/test_intent_validate.py` | 期望检查数 11→12，新增 TestAcceptancePaths 测试类（6 个测试） |
| `README.md` | 工作流图加 S8，检查项数量 11→12，语义复核 S1-S7→S1-S8 |
| `INTENT.md` | 能力表第 11 项和不可妥协项第 3 条的 S1-S7→S1-S8 |

### intent-prd（全新 skill）

原生读取 INTENT.md，不需要交接 prompt 注入约束。强制要求 INTENT.md 作为输入，没有则不跑。

INTENT.md 到 PRD 的映射：

| INTENT.md 章节 | PRD 段 |
|---|---|
| 第 1 节 | Problem Statement |
| 第 4+5 节 | Solution |
| 第 4 节保留能力 | User Stories（每个至少一个 story） |
| 第 12 节 | Implementation Decisions > Design Standards |
| 第 13 节 | Implementation Decisions > Terminology Constraints |
| 第 14 节 | Acceptance Criteria（原版 to-prd 没有此段） |
| 第 6 节 | Out of Scope |

文件结构：

```text
skills/intent-prd/
├── SKILL.md
├── README.md
├── templates/PRD.md
├── scripts/prd_validate.py        ← 8 项检查（V1-V8），含交叉验证
└── tests/
    ├── fixtures/valid-prd.md
    └── test_prd_validate.py        ← 21 个测试
```

### intent-issues（全新 skill）

原生读取 INTENT.md + PRD，按垂直切片（tracer bullet）拆分工单。强制要求两者作为输入。

核心能力：
- 工单的 Acceptance criteria 自动引用验收路径编号（如 `[P01]`）
- 输出前自动检查：所有验收路径被至少一个工单覆盖
- Coverage Verification 节自动核对路径和能力覆盖

文件结构：

```text
skills/intent-issues/
├── SKILL.md
├── README.md
├── templates/issue-template.md
├── scripts/issues_validate.py     ← 7 项检查（V1-V7），含交叉验证
└── tests/
    ├── fixtures/valid-issues.md
    └── test_issues_validate.py     ← 22 个测试
```

### 验证状态

- `python -m pytest skills/intent-anchor/tests/test_intent_validate.py skills/intent-prd/tests/test_prd_validate.py skills/intent-issues/tests/test_issues_validate.py -v` → 76 passed，退出码 0
- 第一轮验收（建 skill 后）：发现 2 项漏改，已修复——intent-issues 命令行参数 3→2、3 个模板 HTML 注释旧名称→新名称
- Given/When/Then 改造：PRD Acceptance Criteria 和工单 Acceptance criteria 改为 Given/When/Then 结构，prd_validate.py 新增 V8 检查，新增 5 个测试
- 第二轮验收（Given/When/Then 改造后）：发现 3 项文档/风格问题，已修复——HANDOFF 测试总数 65→70、HANDOFF Phase 4 描述修正、SKILL.md 直引号→弯引号
- 两轮验收后 76 项测试全部通过

### 完整链路

```text
intent-anchor → intent.md（意图、能力、验收路径、设计标准、术语表、性能/安全要求）
    ↓ 强制输入
intent-prd → prd.md（原生引用能力表和验收路径，Acceptance Criteria 用 Given/When/Then 结构）
    ↓ 强制输入
intent-issues → issues.md（自动引用路径编号，自动检查覆盖）
    ↓ 强制输入
intent-dev → dev-record.md（TDD 循环，每条 Then 按实际运行结果判定验证等级）
    ↓ 强制输入
intent-verify → verify-record.md（全量回归 + 端到端验收路径 + 条件性验证 + 漂移复核）

所有产物统一存放在目标项目的 `intent-chain/{YYYY-MM-DD}-{NNN}-{意图名称}/` 目录下。
```

### git 状态

已提交为 `783d263`，已推送到远程。基线：`bc6511b`。

后续优化（未提交）：intent-prd Phase 4 交接 prompt 清理方案 A 遗留约束注入；issues_validate.py 新增 V6（设计标准传递检查）和 V7（术语表传递检查），新增 6 个测试。三个 skill 合计 76 测试通过。

---

## 任务 A3：intent-dev / intent-verify 拆分与性能安全要求前移（已完成）

### 背景

任务 A2 完成后，链路是 intent-anchor → intent-prd → intent-issues → 开发 → intent-verify。但有两个问题：

1. **性能和安全要求没有收集点**：intent-verify 的 Phase 4 条件性验证会检查性能和安全要求，但这些要求之前没有在任何环节被主动收集。如果用户不说，就永远没有。
2. **"Stage Gate Check" 命名不直观**：原名含义是"阶段门禁检查"，容易被误解为阶段性检查。实际是全部开发完成后的最终检查，应叫"最终复核"。

### 改造范围

- intent-anchor 再改一轮：Phase 2 加 Step 10/11（主动问性能和安全要求），新增第 15/16 节、S9/S10、V13/V14
- intent-verify 全文 Stage Gate Check → 最终复核
- intent-anchor 模板文件 `stage-gate-check.md` 重命名为 `阶段核对表.md`
- `.claude` 和 `.codex` 下的运行态副本不修改

### 改了什么（2 处改动，涉及 16 个文件）

**改动 1：性能/安全要求前移到 intent-anchor**

Phase 2 新增 Step 10（问性能要求）和 Step 11（问安全要求）。必须主动询问，不能等用户提出。有要求逐条记录到第 15/16 节，没要求记录用户确认"没有"。语义复核新增 S9/S10，校验器新增 V13/V14。

**改动 2：Stage Gate Check 改名为"最终复核"**

intent-verify 的 Phase 5 标题、正文、交接 prompt、verify-record 模板、verify_validate.py 常量和消息、README、测试类名全部改名。intent-anchor 中的 `stage-gate-check.md` 文件也重命名为 `阶段核对表.md`。

**涉及的文件**

| 文件 | 改动 |
|---|---|
| `intent-anchor/SKILL.md` | Phase 2 加 Step 10/11，语义复核表加 S9/S10，必需章节加第 15/16 节，模板引用 `阶段核对表.md` |
| `intent-anchor/templates/INTENT.md` | 新增第 15 节（性能要求）和第 16 节（安全要求），补全模板中缺失的 S6-S10 子节 |
| `intent-anchor/scripts/intent_validate.py` | REQUIRED_SECTIONS 加第 15/16 节，V2 改为 16 个章节，V9 扩展到 S1-S10，新增 V13（性能要求校验）和 V14（安全要求校验） |
| `intent-anchor/references/semantic-audit.md` | 新增 S9 和 S10 规则，执行要求更新为 S1-S10 |
| `intent-anchor/README.md` | 工作流图加 S9/S10，检查项数量 12→14，新增 V13/V14 描述表 |
| `intent-anchor/tests/fixtures/valid-intent.md` | 加第 15/16 节和 S9/S10 复核记录 |
| `intent-anchor/tests/test_intent_validate.py` | 期望检查数 12→14，一行自查测试加 S9/S10，新增 TestPerformanceRequirements（4 个测试）和 TestSecurityRequirements（5 个测试） |
| `intent-anchor/templates/阶段核对表.md` | 从 `stage-gate-check.md` 重命名（内容不变） |
| `intent-verify/SKILL.md` | Phase 5 标题、正文、交接 prompt 中 Stage Gate Check → 最终复核 |
| `intent-verify/scripts/verify_validate.py` | GATE_HEADING 常量和所有 V6 消息改名 |
| `intent-verify/templates/VERIFY-RECORD.md` | 章节标题和注释改名 |
| `intent-verify/README.md` | 描述和检查项表格改名 |
| `intent-verify/tests/fixtures/valid-verify-record.md` | 章节标题改名 |
| `intent-verify/tests/test_verify_validate.py` | 测试类名 TestStageGateCheck → TestFinalReview，断言文案改名 |
| `HANDOFF.md` | 历史引用中的 stage-gate-check.md → 阶段核对表.md |
| `docs/intent-anchor-validation-instruction.md` | 历史引用中的 stage-gate-check.md → 阶段核对表.md |

### 验证状态

- `python -m pytest skills/ --tb=short -q` → 243 passed, 5 subtests passed，退出码 0
- 中间踩坑：编辑器将中文弯引号 `"没有"` 替换为 ASCII 直引号 `"没有"` 导致 Python 语法错误，用脚本批量修复 5 处后通过

### git 状态

已提交为 `a11f12d`，已推送到远程。基线：`783d263`。

文档修复 `388d3fb`：SKILL.md 和 README.md 中 3 处 S1-S8 → S1-S10（强制规则 #4、Phase 2.5 标题、文件结构注释），已推送。

---

## 任务 A4：README 同步与输出目录/命名统一（已完成）

### 背景

任务 A3 完成后，intent-dev 和 intent-verify 两个新 skill 未被主 README.md 记录，IntentAnchor 的检查项数量和语义复核范围仍停留在旧版。同时，各 skill 的输出产物分散在 5 个独立目录（intent-anchor/、prd/、issues/、dev/、verify/），文件命名也不一致。

### 改了什么（4 个 commit）

**commit `024c06b`：README.md 同步更新**

- Mermaid 流程图 B3 节点加入 IntentDev → IntentVerify
- 场景表、常用完整路线、从零开始开发 intro 补全链路
- 3 分钟上手安装命令加 intent-dev 和 intent-verify
- IntentAnchor 段：S1-S8 → S1-S10、12 → 14 项检查
- IntentIssues 段：5 → 7 项检查
- 新增 IntentDev 和 IntentVerify 小节（4 项和 6 项检查）
- 目录速览加 intent-dev/ 和 intent-verify/

**commit `36b4ba0`：输出产物统一大写命名**

- 模板文件重命名：dev-record.md → DEV-RECORD.md，verify-record.md → VERIFY-RECORD.md
- 所有 SKILL.md、validate.py、README.md、fixture 中的产物名引用改为大写
- fixture 文件名保持小写（与 valid-intent.md、valid-prd.md 一致）

**commit `2167a6e`：输出目录统一到 intent-chain/{链路目录}/**

- 从 5 个独立目录（intent-anchor/、prd/、issues/、dev/、verify/）合并到 1 个父目录 `intent-chain/{YYYY-MM-DD}-{NNN}-{意图名称}/`
- 下游 skill 不再独立计算日期序号路径，从输入文件路径推导链路目录
- 涉及 21 个文件：SKILL.md × 5、validate.py × 5、README.md × 5、模板 × 3、fixture × 2、主 README × 1

**commit `6e45539`：输出产物文件名统一小写**

- 产物文件名从大写改回小写：intent.md、prd.md、issues.md、dev-record.md、verify-record.md
- 涉及 20 个文件，271 处替换
- 测试 243 passed

### 最终结构

```
intent-chain/
├── 2026-07-24-001-团队进度助手/
│   ├── intent.md
│   ├── prd.md
│   ├── issues.md
│   ├── dev-record.md
│   └── verify-record.md
└── 2026-07-25-001-另一个产品/
    └── ...
```

### 验证状态

- `python -m pytest skills/ -q` → 243 passed, 5 subtests passed
- grep 确认全文不再有大写的 INTENT.md / PRD.md / ISSUES.md / DEV-RECORD.md / VERIFY-RECORD.md 引用（fixture 文件名除外）

### git 状态

四个 commit 均已推送：`024c06b` → `36b4ba0` → `2167a6e` → `6e45539`。基线：`a11f12d`。

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
任务 A（已提交 bc6511b）：intent-anchor 改造——Phase 2 加设计标准识别（Step 7）和术语标记（Step 8），
  Phase 4 交接 prompt 注入设计标准和术语约束（后被 A2 简化）。
  .claude/.codex 运行态不修改，已还原。

任务 A2（已提交 783d263，已推送）：在 A 基础上加验收路径（Step 9 / S8 / V12 / 第 14 节），
  新建 intent-prd（8 项校验，含 V8 Given/When/Then 结构检查）和 intent-issues（7 项校验，含 V6/V7 设计标准与术语传递检查），
  Phase 4 交接 prompt 简化为指向 intent-prd / intent-issues。
  PRD 的 Acceptance Criteria 和工单的 Acceptance criteria 均使用 Given/When/Then 结构。
  三个 skill 合计 76 测试通过，两轮独立验收问题全部修复。
  有 INTENT.md 用 intent-prd / intent-issues，没有用原版 to-prd / to-issues。

后续优化（已包含在 783d263 中）：
  - intent-prd Phase 4 交接 prompt 清理方案 A 遗留约束注入（只指路，不注入约束）
  - issues_validate.py 新增 V6（设计标准传递检查）和 V7（术语表传递检查），新增 6 个测试

任务 A3（已提交 a11f12d，已推送）：在 A2 基础上加性能/安全要求前移和 Stage Gate Check 改名。
  - intent-anchor Phase 2 加第 10/11 项（主动问性能和安全要求），新增第 15/16 节、S9/S10、V13/V14
  - 新建 intent-dev（4 项校验）和 intent-verify（6 项校验），从原 Stage Gate Check 拆分
  - intent-verify 全文 Stage Gate Check → 最终复核
  - intent-anchor 模板 stage-gate-check.md 重命名为 阶段核对表.md
  - 全部 skill 合计 243 passed
  - 中间踩坑：中文弯引号被替换为 ASCII 直引号导致 Python 语法错误，批量修复 5 处后通过
  - 文档修复 388d3fb：3 处 S1-S8 → S1-S10，已推送
  - 独立验收 25 项检查全部通过

任务 A4（已提交 024c06b → 36b4ba0 → 2167a6e → 6e45539，已推送）：README 同步与输出目录/命名统一。
  - README.md 补全 intent-dev/intent-verify，更新检查项数量
  - 输出目录从 5 个独立目录合并到 intent-chain/{链路目录}/
  - 产物文件名统一小写：intent.md / prd.md / issues.md / dev-record.md / verify-record.md
  - 下游 skill 从输入文件路径推导链路目录，不再独立计算日期序号
  - 243 passed

任务 B（待补测）：blue-interview P1/P2/P3/P8/P9 已落地，P3 试跑通过，P1/P2/P8/P9 待补测。
  skill 被 .gitignore 忽略，不入库。未经同意禁止修改。

详情：见仓库根目录 HANDOFF.md。
```
