# 交接文档

> 写给完全没有上下文的新会话。最近更新：2026-07-26。
> 本文档覆盖八个独立任务：intent-anchor 改造（已完成）、intent-prd / intent-issues 新建（已完成）、intent-dev / intent-verify 拆分与性能安全要求前移（已完成）、README 同步与输出目录/命名统一（已完成）、intent-chain 校验脚本重构（已完成）、intent-design 新建与下游消费（已完成）、impact V23/V24 可校验契约补丁（已完成）、blue-interview 优化（部分完成，待补测）。

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
| `intent-verify/templates/verify-record.md` | 章节标题和注释改名 |
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
- grep 确认全文不再有大写的 intent.md / prd.md / issues.md / dev-record.md / verify-record.md 引用（fixture 文件名除外）
- 独立验收报告发现 commit `6e45539` 执行不完整：SKILL.md、模板注释、交接 prompt、validate.py 文档字符串中共约 30 处大写产物名残留；两个模板文件（INTENT.md、阶段核对表.md）存放路径仍为旧目录结构；docs 链路图未更新为小写
- 验收报告中的所有 FAIL 项已在 commit `6c1f2b9` 中修复
- 概念名大写引用（如"把目标写进 INTENT.md"）保持大写，与模板文件名约定一致，不构成问题

### git 状态

五个 commit 均已推送：`024c06b` → `36b4ba0` → `2167a6e` → `6e45539` → `6c1f2b9`。基线：`a11f12d`。

---

## 任务 A5：intent-chain 校验脚本重构（已完成）

### 背景

任务 A4 后，链路五个 skill 的校验脚本（`*_validate.py`）存在三个结构性问题：

1. **Markdown 解析逻辑分散重复**：`section()`、`subsection()`、`table_rows()`、`has_placeholder()` 四个函数在 5 个校验脚本里各自复制一份，共约 250 行重复代码。改解析逻辑要同时改 5 处，容易漏。
2. **V2 证据检查太宽松**：`intent-dev` 的 V2 检查只要求证据段里同时出现"命令"和"输出"两个关键词，但没有校验是否真的包含命令文本和输出文本。开发记录模板里有占位提示但没人强制填。
3. **没有需求漂移追溯**：INTENT.md 从 anchor 产出后被 PRD、Issues、Dev、Verify 逐级引用，但没有任何手段检查"下游引用的关键决策是否和 anchor 原始定义一致"。如果用户中途改了 INTENT.md 的决策或验收路径编号，下游文档不会感知到。

### 改了什么（3 项改动，7 个文件）

**改动 1：提取公共 Markdown 解析模块**

新建 `skills/_common/markdown_parser.py`，集中 4 个函数：

| 函数 | 用途 |
|---|---|
| `section(text, name)` | 提取 `## {name}` 到下一个同级标题之间的内容 |
| `subsection(text, name)` | 提取 `### {name}` 到下一个同级标题之间的内容 |
| `table_rows(text)` | 解析 Markdown 表格，返回每行字段字典 |
| `has_placeholder(text, name)` | 检查模板占位符 `{name}` 是否未被替换 |

`prd_validate.py`、`issues_validate.py`、`verify_validate.py` 删除各自的本地实现，改为从 `_common.markdown_parser` 导入。`intent_validate.py` 和 `dev_validate.py` 也导入公共模块（这两个文件保留了少量本地适配代码，因为解析逻辑有细微差异）。

**改动 2：强化 V2 证据检查**

`dev_validate.py` 的 `_has_command_output()` 方法原来只检查关键词存在性，改为：
- 必须同时包含命令文本（`$` 或 `` ` `` 开头的代码块）**和**输出文本（非空行）
- 两者缺一则 V2 报 warning，提示"证据段缺少命令或输出"

**改动 3：基线对比功能**

`intent_validate.py` 新增 `--baseline <git_ref>` 参数：
- 读取 git 历史中指定 ref（如 `HEAD~1`、`main`）的 INTENT.md 版本
- 对比当前版本与基线版本的**决策段**（第 6 节）和**验收路径段**（第 14 节）
- 如果决策内容变化或路径编号变化，输出 warning 提示"关键决策与基线 {ref} 不一致，请确认下游文档是否需要同步更新"
- 不阻断校验（只 warning 不 error），因为用户可能确实有意修改

### 涉及的文件

| 文件 | 改动 |
|---|---|
| `skills/_common/markdown_parser.py` | 新建，4 个公共函数 |
| `skills/intent-anchor/scripts/intent_validate.py` | 导入公共模块，新增 `--baseline` 参数和 `_compare_baseline()` |
| `skills/intent-dev/scripts/dev_validate.py` | 导入公共模块，`_has_command_output()` 强化检查逻辑 |
| `skills/intent-prd/scripts/prd_validate.py` | 删除本地解析函数，改为导入 |
| `skills/intent-issues/scripts/issues_validate.py` | 删除本地解析函数，改为导入 |
| `skills/intent-verify/scripts/verify_validate.py` | 删除本地解析函数，改为导入 |
| `README.md` | 3 分钟上手安装命令加 `_common` 目录 |

### 验证状态

- `python -m pytest skills/ -q` → 145 passed，退出码 0（比之前 143 多 2 个：V2 强化的正向测试和反向测试）
- `python skills/intent-anchor/scripts/intent_validate.py tests/fixtures/valid-intent.md --baseline HEAD` → 正常退出，无 warning（基线与当前一致）
- 手动验证：修改 fixture 的决策段后加 `--baseline HEAD` → 输出 warning，确认功能生效

### git 状态

已提交为 `9873c55`，已推送到远程。基线：`6c1f2b9`。

### 设计说明

- **公共模块放 `_common/` 而非 `intent-anchor/`**：因为所有 5 个 skill 都依赖它，放在任何一个 skill 下都不合适。`_common/` 是中性目录，不绑定任何具体 skill。
- **基线对比只 warning 不 error**：用户可能有意修改决策，不应阻断正常校验流程。warning 提示足够引起注意。
- **V2 检查强化但不改 V2 的检查编号和报错消息结构**：保持测试兼容，只改内部判断逻辑。

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

## 待办：CI 门禁失效（2026-07-25 发现，用户决定暂不处理）

`.github/workflows/eval-checks.yml` 在 master 上有两步会失败，CI 实际处于长期红灯状态，等于没有门禁。

| # | 失败步骤 | 原因 | 修法 |
|---|---|---|---|
| 1 | `validate_real_projects.py` | `delivery-results.json` results[19] 引用的 `eval/runs/real-projects/2026-07-04-minimax-m3-delivery-d19r2/README.md` 不存在——该文件（302 行）在 commit `a11f12d` 中被误删，同目录其他文件（change-impact/ 7 份 + diff/ 2 份）都还在 | `git show a11f12d^:eval/runs/real-projects/2026-07-04-minimax-m3-delivery-d19r2/README.md` 可完整取回 |
| 2 | Validate skill metadata | `skills/vl-vision/SKILL.md` 缺 `allowed-tools` 字段。vl-vision 建于 2026-06-29（`7c08272`），metadata 检查加于 2026-07-10（`b6aa7a3`），加检查时未回看已有文件 | 补 `allowed-tools`，或让检查跳过 vl-vision。vl-vision 自称"非核心 Skill，不参与评测体系"，选哪种取决于是否要让它可被模型调用——产品决定，待用户拍板 |

另有一处覆盖缺口（非失败）：CI 只单独跑了 intent-anchor 的测试，intent-prd / intent-issues / intent-dev / intent-verify 四个 skill 的 99 个测试未进 CI（`tests/run.sh` 那一步只对有 run.sh 的目录生效，这四个没有）。

复现命令：

```bash
python eval/real-projects/scripts/validate_real_projects.py   # 退出码 1
```

本地已确认其余 CI 步骤通过：JSON 全量解析、check_delivery 单测（41 passed）、`sync_templates.py --check`（10/10）、`pytest skills/`（260 passed）。

---

## 任务 A6：intent-design 新建与下游消费（已完成）

### 背景

用户看到一个普遍问题：AI 在方案设计阶段容易过度设计，为了覆盖理论上可能但现实中不会发生的边界条件，引入不必要的复杂度（比如动底层架构）。根本原因是设计阶段没有强制把架构假设和代价写清楚，下游也没有校验点拦住。

用户决定新建 `intent-design` skill，在 PRD 和 Issues 之间插入一个设计环节，强制产出 `architecture.md`（全局架构假设）和 `design.md`（功能设计），并让下游 skill（intent-issues / intent-verify / intent-dev）消费 `architecture.md`。

### 改造范围

分两步：

1. **新建 intent-design skill**：SKILL.md + templates（architecture.md / design.md）+ scripts（design_validate.py）+ tests
2. **下游 skill 消费 architecture.md**：intent-prd / intent-issues / intent-verify / intent-dev 的 SKILL.md、校验脚本、模板、fixture、测试全部更新，把 architecture.md 从可选变为强制输入

### 改了什么

**第 1 步：新建 intent-design（全新 skill）**

| 文件 | 内容 |
|---|---|
| `skills/intent-design/SKILL.md` | 5 个 Phase：输入校验 → 写 architecture.md → 写 design.md → 自检 → 交接。强制要求 PRD 作为输入 |
| `skills/intent-design/templates/architecture.md` | 模板：架构概览、模块与边界、技术选型、关键数据流、额外结构与假设、重要决策的详细说明 |
| `skills/intent-design/templates/design.md` | 模板：设计概览、能力设计（逐个保留能力）、与架构文档的对照 |
| `skills/intent-design/scripts/design_validate.py` | 校验：architecture.md 8 项（A1-A8）、design.md 5 项（D1-D5）、交叉 2 项（X1-X2），共 15 项 |
| `skills/intent-design/tests/test_design_validate.py` | 行为测试 |

**第 2 步：下游强制消费 architecture.md**

| skill | 改动 |
|---|---|
| intent-prd | Phase 4 交接 prompt 指向 intent-design（强制，非可选） |
| intent-issues | Phase 1 前置条件加 architecture.md；Phase 4 校验命令含 architecture.md；Phase 5 交接 prompt 带 architecture.md；issue-template 加"涉及模块"子节；issues_validate.py V11 从可选变强制 |
| intent-verify | Phase 1 前置条件加 architecture.md；加"技术漂移复核"章节；verify_validate.py V8 从可选变强制 |
| intent-dev | Phase 1 引用 architecture.md / design.md；Phase 3 交接带 architecture.md |
| README.md | intent-chain 流程图加 intent-design 必经环节；描述更新 |

对应的 fixture 和测试同步更新：valid-issues.md 加"涉及模块"、valid-verify-record.md 加"技术漂移复核"、test_issues_validate.py 和 test_verify_validate.py 加强制检查测试。

### 验证状态

- `python -m pytest skills/ -q` → 302 passed，退出码 0
- 全链路冒烟测试：`design_validate.py` → `issues_validate.py` → `verify_validate.py` 串行调用，全部通过
- Lint 无错误

### git 状态

已提交。基线：`9873c55`。

---

## 任务 A7：impact V23/V24 可校验契约补丁（已完成）

### 背景

`impact` skill 的 Full 模式有两个结构性缺口：

1. **设计阶段不约束过度设计**：方案为了假想风险额外加缓存、锁、事件、配置项等结构时，没有强制说明具体场景、依据和补做成本。用户只要求"修改订单备注"，方案却准备加分布式锁——这种情况没有校验点拦截。
2. **设计到实施没有映射校验**：020-design.md 的设计项（Dxx）和 030-implementation.md 的 Step 之间没有双向一致性检查。设计写了 D01 但实施 Step 引用 D02、映射表指向不存在的 Step、Step 标"流程步骤"但实际执行 DML——这些都能通过。

用户决定做一次"最小完整修复"：不新增 Skill、不引入架构文档，只给 Impact Full 模式补两条可校验契约（V23 和 V24），并修正 Light 模式的反向引导。

### 改了什么（14 个文件，+1589 / -26）

**V23：额外结构与假设检查（020-design.md §5.1）**

020-design.md 新增 §5.1 模板，要求：当方案为了用户未明确要求、且当前需求没有直接证明会发生的场景额外增加结构时，必须填写五列表（关联设计项 / 加了什么结构 / 为了解决什么情况 / 这种情况的依据 / 以后再补的成本）。无额外结构时写"无额外结构"。

V23 校验逻辑修复了 6 条绕过路径：
- strip HTML comments 后再检查"无额外结构"，防止模板注释绕过
- 空表从 PASS 改为 FAIL
- 五列字段全部检查非空和占位内容（`[占位`/`TODO`/`...`）
- 扩展模糊证据词表（扩展性/健壮性/为了性能/为了安全/以防万一等 13 词）
- 同时检查"为了解决什么情况"列的模糊描述
- 关联设计项交叉验证 §3 中是否存在

无依据项（"无依据，属于假设"）须列入确认清单；执行阶段（preflight 声明可执行或源码 Step 已写入）仍未确认则升级为 FAIL。

**V24：设计到实施映射检查（020 Dxx ↔ 030 Step ↔ 090 Step）**

030-implementation.md 新增 §2.2 设计到实施对照表，Step 新增"设计项"字段。090-execution-record.md Step 也加"设计项"字段。

V24 校验逻辑包含 7 项检查：
- Check A：020 无 Dxx 但 030 有源码/DML Step → FAIL
- Check B：020 每个 Dxx 必须出现在 §2.2 映射表
- Check C/C2：映射表和 Step 中引用的 Dxx 必须在 020 §3 中存在
- Check D：映射表引用的 Step 编号必须在 030 §3 中实际存在
- Check E：有 source/DML 内容的 Step 必须引用至少一个 Dxx（"流程步骤"标记不豁免）
- Check F：映射表与实际 Step 的设计项逐条对照
- Check G：090 的设计项与 030 一致，030 有设计项时 090 不能缺字段

020 §3 新增稳定编号（D01、D02...），检测重复编号 → FAIL。

**P1 修复**

- `_extract_blockquote_section` 函数：识别引用块加粗文本（`> **需要你确认的假设**`），解决确认清单无法提取的问题。测试断言退出码（Phase 4 WARN 不导致 FAIL，执行阶段 FAIL）。
- 设计偏离流程：`phase-5-execution.md` 改为"暂停 → 提出文档修订 Step → 用户确认 → 更新 020/030 → 重跑 validator → 提出新源码 Step → 用户再次确认"。`090-execution-record.md` 要求 Full 模式首次进入执行时同时读取 020 和 030。

**P2 公开契约同步**

- README / skills/impact/README.md / SKILL.md / phase-4-output.md 声明 V1-V24
- .gitignore 排除 `skills/impact/tests/e2e/` 目录
- `_active-state.md` 含退出码和原始 SUMMARY

**Light 模式**

`040-light.md` 确保不增加 V23/V24 检查，保持 Light 模式简单。

### 涉及的文件

| 文件 | 改动 |
|---|---|
| `skills/impact/scripts/impact_validate.py` | +591 行：V23/V24 校验逻辑、辅助函数、正则 |
| `skills/impact/tests/test_scripts/test_impact_validate.py` | +894 行：V23/V24 测试（含 12 条绕过路径反例） |
| `skills/impact/templates/020-design.md` | §5.1 额外结构与假设模板，§3 稳定编号 |
| `skills/impact/templates/030-implementation.md` | §2.2 设计到实施对照表，Step 设计项字段 |
| `skills/impact/templates/040-light.md` | Light 模式不增加 V23/V24 |
| `skills/impact/templates/060-preflight.md` | 设计映射检查 |
| `skills/impact/templates/090-execution-record.md` | 设计项字段，首次读取 020+030 |
| `skills/impact/references/phase-5-execution.md` | 设计偏离流程调整 |
| `skills/impact/references/phase-4-output.md` | V23/V24 声明 |
| `skills/impact/README.md` | V1-V24 |
| `skills/impact/SKILL.md` | §5.1/§2.2/V23/V24 |
| `README.md` | V1-V24 |
| `.gitignore` | e2e 测试目录排除 |

### 验证状态

- `python -m pytest skills/impact/tests/test_scripts/test_impact_validate.py -v` → 81 passed
- 真实项目验证（RuoYi email-validation）：V23 PASS、V24 PASS（V15/V18 失败是 Phase 4 fixture 预期行为）
- `git diff --ignore-all-space --stat` 确认 impact_validate.py 为 591 行纯增量（0 删除）
- 行尾一致 CRLF（与原始文件一致），`git diff --check` 的 trailing whitespace 报错为 CRLF + `core.autocrlf=false` 误报

### 踩过的坑

1. **V24 初版有 6 条可复现绕过路径**：评审发现 D01→Step 99 不存在也通过、映射表引用不存在的 Dxx 不检查、"流程步骤"含 DML 绕过检查等。逐条修复并补反例测试。
2. **V23 初版模板注释可直接绕过**：`_strip_html_comments` 在检查"无额外结构"之前执行，但初版是在整份文档中搜索而非先提取 §5.1。修复为先提取 §5.1 → strip comments → 再检查。
3. **行尾噪音**：`impact_validate.py` 原始为 CRLF，编辑后保持 CRLF，但 `git diff --check` 仍报 trailing whitespace（`\r` 被视为 trailing whitespace）。`--ignore-all-space` 确认实际改动为纯增量。

### git 状态

已提交为 `cf1e6f8`，已推送到远程。基线：intent-design 提交。

---

## 待办：intent-design 真实项目验证留证

会话中约定用一个真实的 0→1 小项目生成 `architecture.md` 和 `design.md`，确认两份文档能产出实际内容。当前仓库没有保留对应的 `intent-chain/` 示例目录或运行记录，因此无法确认是尚未执行，还是执行后删除了临时产物。

完成标准：选择一个真实小项目运行到 intent-design，记录项目、产物路径、校验命令和结果。产物是否入库由用户另行决定。

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

任务 A4（已提交 024c06b → 36b4ba0 → 2167a6e → 6e45539 → 6c1f2b9，已推送）：README 同步与输出目录/命名统一。
  - README.md 补全 intent-dev/intent-verify，更新检查项数量
  - 输出目录从 5 个独立目录合并到 intent-chain/{链路目录}/
  - 产物文件名统一小写：intent.md / prd.md / issues.md / dev-record.md / verify-record.md
  - 下游 skill 从输入文件路径推导链路目录，不再独立计算日期序号
  - 独立验收发现 6e45539 遗漏约 30 处大写引用和 2 个模板路径，已在 6c1f2b9 修复
  - 243 passed
  - 概念名大写引用（如"把目标写进 INTENT.md"）保持大写，与模板文件名约定一致

任务 A5（已提交 9873c55，已推送）：intent-chain 校验脚本重构。
  - 提取公共 Markdown 解析模块 skills/_common/markdown_parser.py，5 个校验脚本统一导入
  - 强化 intent-dev V2 证据检查：命令和输出必须同时存在
  - intent-anchor 新增 --baseline <git_ref> 参数，对比决策段和验收路径段，只 warning 不 error
  - README 安装命令加 _common 目录
  - 145 passed（比之前多 2 个 V2 测试）
  - .claude/.codex 运行态不修改

任务 A6（已提交，已推送）：intent-design 新建与下游消费。
  - 新建 intent-design skill：强制产出 architecture.md（全局架构假设）和 design.md（功能设计）
  - 在 PRD 和 Issues 之间插入设计环节，强制把架构假设和代价写清楚
  - 下游 skill（intent-prd / intent-issues / intent-verify / intent-dev）强制消费 architecture.md
  - intent-issues V11、intent-verify V8 从可选变强制检查
  - README intent-chain 流程图加 intent-design 必经环节
  - 302 passed，全链路冒烟测试通过
  - 起因：AI 方案设计阶段容易过度设计，强制文档化架构假设和代价来拦住
  - TODO：用一个真实的 0→1 小项目运行到 intent-design，并记录产物路径、校验命令和结果

任务 A7（已提交 cf1e6f8，已推送）：impact V23/V24 可校验契约补丁。
  - V23（额外结构与假设）：020 §5.1 强制填写五列表（关联设计项/加了什么结构/为了解决什么情况/依据/补做成本）
  - V24（设计到实施映射）：020 Dxx ↔ 030 Step ↔ 090 Step 双向一致性检查，7 项检查
  - 修复 V23 6 条绕过路径（模板注释绕过、空表 PASS、字段占位、弱词、模糊描述、关联设计项存在性）
  - 修复 V24 6 条绕过路径（Step 不存在、Dxx 不存在、无 Dxx 但有源码 Step、流程步骤含 DML、090 缺字段、映射不一致）
  - P1：引用块加粗文本提取、设计偏离流程改为先确认再写文件
  - P2：README/SKILL.md/phase-4-output.md 声明 V1-V24
  - 14 文件 +1589/-26，81 passed，RuoYi 真实项目 V23/V24 PASS
  - 起因：impact Full 模式不约束过度设计、设计到实施无映射校验

任务 B（待补测）：blue-interview P1/P2/P3/P8/P9 已落地，P3 试跑通过，P1/P2/P8/P9 待补测。
  skill 被 .gitignore 忽略，不入库。未经同意禁止修改。

详情：见仓库根目录 HANDOFF.md。
```
