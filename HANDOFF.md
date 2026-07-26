# 交接文档

> 写给完全没有上下文的新会话。最近更新：2026-07-26。
> 本文档覆盖十一个独立任务：intent-anchor 改造（已完成）、intent-prd / intent-issues 新建（已完成）、intent-dev / intent-verify 拆分与性能安全要求前移（已完成）、README 同步与输出目录/命名统一（已完成）、intent-chain 校验脚本重构（已完成）、intent-design 新建与下游消费（已完成）、impact V23/V24 可校验契约补丁（已完成）、intent-chain 评审修复 P0+P1+文档一致性（已完成，已强模型验证）、impact 评审缺点修复 V23 白名单+SKILL.md 精简+评测脚本修复（已完成，已强模型验证）、强模型验证+校验器盲区修复（任务 J，已完成，未提交）、blue-interview 优化（部分完成，待补测）。

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

Phase 2 新增 Step 8：逐项审查能力表中的"能力"和"描述"列，识别行业黑话。为每个术语给出人话翻译和界面文案，记录到 INTENT.md 第 13 节。无术语时记录"无术语需要翻译"。

**改动 3：验收路径**

Phase 2 新增 Step 9：从保留能力推导用户可感知的端到端验收路径，每条路径含入口、2-5 步关键步骤和预期结果。记录到 INTENT.md 第 14 节。

**改动 4：性能/安全要求**

Phase 2 新增 Step 10-11：主动询问用户是否有性能和安全要求。有则逐条记录（含能力 ID 和用户确认原话），无则记录用户确认"没有"。

**改动 5：语义复核**

Phase 2.5 新增 S1-S10 语义复核记录表，写入 INTENT.md 第 10 节。

**改动 6：结构校验**

`intent_validate.py` 从 4 项检查扩展到 14 项（V1-V14），覆盖设计标准、术语表、验收路径、性能和安全要求的完整性与交叉引用。

**改动 7：INTENT.md 模板**

`templates/INTENT.md` 新增第 12-16 节骨架。

**改动 8：Phase 4 交接 prompt**

更新交接 prompt，提及 intent-prd / intent-issues 原生读取 INTENT.md 约束。

**改动 9：安装清单**

`docs/install-and-verify-checklist.md` 新增 intent-anchor / intent-prd / intent-issues 安装步骤。

### 验证

- `intent_validate.py` 14 项 PASS（fixture）
- `test_intent_validate.py` 42 passed
- `test_prd_validate.py` 30 passed
- `test_issues_validate.py` 38 passed

### 状态

已提交。运行态副本需用户手动复制。

---

## 任务 B：intent-prd / intent-issues 新建（已完成）

### 背景

用户决定自己开发 IntentPRD 和 IntentIssues，替代第三方 to-prd / to-issues，因为第三方 skill 不认识 INTENT.md 结构。

### 改了什么

**IntentPRD**：从 INTENT.md 生成 PRD，原生映射能力表→User Stories、验收路径→Acceptance Criteria、设计标准→Design Standards、术语表→Terminology Constraints、性能/安全要求→对应子节。`prd_validate.py` 10 项检查。

**IntentIssues**：从 INTENT.md + PRD 拆工单，按垂直切片组织。自动检查验收路径覆盖、保留能力覆盖、设计标准传递、术语表传递、性能/安全要求传递、PRD Then 覆盖。`issues_validate.py` 11 项检查（含 V11 架构模块引用检查）。

### 验证

- `test_prd_validate.py` 30 passed
- `test_issues_validate.py` 38 passed

### 状态

已提交。

---

## 任务 C：intent-dev / intent-verify 拆分（已完成）

### 背景

将原 to-implement 拆为 intent-dev（工单开发）和 intent-verify（端到端验收），分离开发级验证和整体验收职责。

### 改了什么

**IntentDev**：TDD 循环开发，V0/V1/V2 验证等级，`dev_validate.py` 4 项检查。
**IntentVerify**：全量回归 + 端到端验收路径 + 条件性验证 + 漂移复核 + 技术漂移复核，`verify_validate.py` 8 项检查。

### 验证

- `test_dev_validate.py` 全通过
- `test_verify_validate.py` 42→47 passed（P1 修复后新增 5 项）

### 状态

已提交。

---

## 任务 D：README 同步与输出目录/命名统一（已完成）

### 改了什么

- README 新增「从零开始开发」完整链路图和各 skill 说明
- 统一输出目录为 `intent-chain/{链路目录}/`
- 统一文件命名：intent.md、prd.md、architecture.md、design.md、issues.md、dev-record.md、verify-record.md

### 状态

已提交。

---

## 任务 E：intent-chain 校验脚本重构（已完成）

### 改了什么

- 提取公共 `markdown_parser.py`（section/subsection/table_rows/has_placeholder）
- 四个校验脚本统一引用，消除重复实现

### 状态

已提交。

---

## 任务 F：intent-design 新建与下游消费（已完成）

### 改了什么

- 新建 IntentDesign skill：从 INTENT.md + PRD 产出 architecture.md 和 design.md
- `design_validate.py` 15 项检查（A1-A8, D1-D5, X1-X2）
- 假设表把过度设计变成显式决策
- IntentIssues V11 强制检查 architecture.md 模块引用
- IntentDev 前置条件加入 architecture.md 和 design.md
- IntentVerify 前置条件加入 architecture.md 和 design.md

### 验证

- `test_design_validate.py` 35→39 passed（P0 修复后新增 4 项）

### 状态

已提交。

---

## 任务 A7：impact V23/V24 可校验契约补丁（已提交 cf1e6f8）

### 改了什么

- V23（额外结构与假设）：020 §5.1 强制填写五列表
- V24（设计到实施映射）：020 Dxx ↔ 030 Step ↔ 090 Step 双向一致性检查
- 修复 V23 6 条绕过路径、V24 6 条绕过路径
- 14 文件 +1589/-26，81 passed，RuoYi 真实项目 V23/V24 PASS

### 状态

已提交 cf1e6f8，已推送。

---

## 任务 H：intent-chain 评审修复 P0+P1+文档一致性（已完成，已强模型验证——见任务 J）

### 1. 用户最初提出的需求

用户提供了一份针对 intent-chain 的评审意见，要求逐条核对并修复。原话核心：

> "你先看看这个评审意见 有问题和我交流 intent-chain"

评审意见列出了以下问题：
- A7 可以被 HTML 注释绕过
- A7 证据列只查禁用词，不是真正的证据类型检查
- V8 技术漂移复核只检查标题存在
- design.md 是强制文件但下游自动检查较弱
- 还没有真实 0→1 项目证据
- README 快捷入口仍有一处从 PRD 直接写到 Issues，遗漏 IntentDesign
- IntentAnchor 交接提示没有明确说明设计环节是强制步骤
- IntentDev 一边写"不代替用户开发代码"，一边又要求按 TDD 写测试和代码，公开契约不够统一

### 2. 用户后来确认的补充、范围变化和明确排除项

- **文档一致性**：用户要求先交流思路再动手。讨论后确认：
  - A1（README 快捷入口补 IntentDesign）：直接改
  - A2（交接 Prompt）：用户提出"能否不搞交接"，最终决定删除全部 5 个 skill 的交接 Prompt，替换为一句话指向 README 链路图
  - A3（README design.md "作为输入"表述）：直接改
  - B（IntentDev 定位）：用户确认选"实施者"方向——AI 写测试和功能代码，用户确认结果后写入项目
  - C 类（V8/V6 文档描述与实际行为不一致）：用户说"我看不懂 做不了决定"，最终决定这一批不修，等 P1 代码修复时一起处理

- **P0 代码修复**：用户确认"要"开始做 P0
- **P1 代码修复**：用户确认"继续做"
- **IntentVerify 需不需要 design.md**：用户确认"先保持现状 + 修正文档表述（A3 那条），P1 时再决定要不要把 design.md 纳入实际比对"——P1 实际做了之后，design.md 已纳入 verify_validate.py 交叉检查
- **P3（真实项目验证）**：用户未要求处理，明确是已知 TODO

### 3. 成功标准

| 编号 | 成功标准 | 验证方式 |
|---|---|---|
| P0-A | `<!-- 无额外结构 -->` 不再能跳过假设表检查 | `test_html_comment_bypass_fails` |
| P0-B | 证据列填"模型判断确有必要"时 A7 FAIL；填代码位置或引号包裹原文时 PASS | `test_non_evidence_text_fails` + `test_code_location_evidence_passes` |
| P1-A V8 | 技术漂移复核写"已核对。"时 V8 FAIL；引用未定义模块时 FAIL | `test_tech_drift_only_text_fails` + `test_tech_drift_undefined_module_fails` |
| P1-A V6 | 漂移复核写"已核对。"时 V6 FAIL | `test_drift_only_text_fails` |
| P1-B | verify_validate.py 接收 design.md，模块不在 design.md 时 V8 FAIL | `test_tech_drift_with_design_passes` + `test_tech_drift_undefined_in_design_fails` |
| A1 | README 第 43 行快捷入口表含 IntentDesign | 文本检查 |
| A2 | 5 个 skill 的交接 Prompt 被替换为一句话 | 文本检查 |
| A3 | README 第 333 行不含"作为输入" | 文本检查 |
| B | IntentDev 第 19 行为"AI 写测试和功能代码"；"做不到"列表不含"代替用户写代码和测试" | 文本检查 |

### 4. 项目路径、分支、基线、未提交改动

- **项目绝对路径**：`e:\agent\blue-skillhub`
- **当前分支**：`master`
- **基线 commit**：`4734b78`（`feat(intent-verify): 补浏览器自动化（Playwright）验证层级`）
- **提交状态**：已提交为 `2492d9b`（fix(intent-chain): P0+P1 评审修复 + 文档一致性）

### 5. 本次实际修改的文件和修改目的

基线：`4734b78`（master 分支 HEAD）。与基线比较，当前工作区 diff 如下：

| 文件 | 修改目的 |
|---|---|
| `README.md` | A1：第 43 行快捷入口表补 IntentDesign；A3：第 333 行去掉"作为输入"；第 335 行更新 verify_validate.py 描述（含漂移复核数据行检查 + design.md 交叉检查） |
| `skills/intent-anchor/SKILL.md` | A2：Phase 4 从 13 行交接 Prompt 缩减为一句话 |
| `skills/intent-prd/SKILL.md` | A2：Phase 4 同上 |
| `skills/intent-design/SKILL.md` | A2：Phase 5 同上 |
| `skills/intent-dev/SKILL.md` | A2：Phase 3 保留步骤 1-3，删交接 Prompt；B：第 19 行改为"AI 写测试和功能代码"；"能够"列表更新；"做不到"列表删"代替用户写代码和测试" |
| `skills/intent-verify/SKILL.md` | A2：Phase 6 缩减为一句话；Phase 5 第 10 步和强制规则第 9 条改为"四个路径"；第 6 步和 frontmatter 加 design.md |
| `skills/intent-design/scripts/design_validate.py` | P0-A：新增 `_strip_html_comments`，检查"无额外结构"前剥离注释且要求非表格行；P0-B：证据列非"无依据"时要求匹配文件路径特征或引号包裹 |
| `skills/intent-design/tests/test_design_validate.py` | 新增 4 个测试：注释绕过、非证据文本、代码位置证据、无额外结构正文 |
| `skills/intent-verify/scripts/verify_validate.py` | P1-A：V6 漂移复核加数据行检查；V8 技术漂移复核加数据行 + 模块名与 architecture.md 交叉检查；P1-B：validate 新增可选参数 `design_content`，传入时额外与 design.md 交叉检查；CLI 支持可选第 4 参数 |
| `skills/intent-verify/tests/test_verify_validate.py` | 新增 5 个测试：技术漂移纯文本 FAIL、未定义模块 FAIL、传 design.md PASS、design.md 缺模块 FAIL、漂移复核纯文本 FAIL |

### 6. 已运行的验证命令和结果

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pytest skills/intent-design/tests/test_design_validate.py -v` | 0 | 39 passed（原 35 + 新 4） |
| `python -m pytest skills/intent-verify/tests/test_verify_validate.py -v` | 0 | 47 passed（原 42 + 新 5） |
| `python -m pytest skills/intent-design/tests/test_design_validate.py skills/intent-verify/tests/test_verify_validate.py -v` | 0 | 86 passed |
| `read_lints`（6 个修改文件） | — | No linter errors found |

**未运行的验证**：
- 未用强模型（Claude Opus / GPT-4 等）在真实 0→1 项目中端到端验证
- 未运行 intent-anchor / intent-prd / intent-issues / intent-dev 的测试（本次未修改这些 skill 的校验器，但修改了 SKILL.md 文档内容）
- 未运行 impact / pathfinder 的测试（无关）

### 7. 已知风险、未确认内容、原有改动、不能覆盖的文件

**已知风险**：
- 所有改动未 commit、未 push，仅在工作区
- 未经验证：强模型在真实项目中运行 intent-chain 全链路时，新的 V8/V6 检查是否会误杀合规文档（fixture 覆盖了基本场景，但真实文档格式可能更复杂）
- P0-B 证据列检查的正则可能不覆盖所有合法代码路径格式（如 Windows 路径 `src\order\service.py:42` 的反斜杠已在正则中，但其他格式如 `file:///...` 未覆盖）
- P1-B design.md 交叉检查是可选的（向后兼容），IntentVerify SKILL.md 要求传 4 个路径，但不传 design.md 时 V8 仍能通过（只是不检查 design.md 一致性）

**未确认内容**：
- P3（真实 0→1 项目验证）是已知 TODO，不是 bug，用户未要求处理
- C 类（V8/V6 文档描述与实际行为不一致）已在 P1 代码修复中自动解决（校验器加强了，文档不用降级）

**不能覆盖或还原的文件**：
- 无。所有改动都是本次会话新产生的，不涉及用户原有改动。

**用户原有改动**：
- 用户当前打开的文件 `2026-07-25-151945-bro.txt`（评审意见原文）不在仓库中，不受本次改动影响。

---

## 任务 I：impact 评审缺点修复 — V23 白名单 + SKILL.md 精简 + 评测脚本修复（已完成，已强模型验证——见任务 J）

### 背景

用户对 Pathfinder → Impact 链路做了评审，列出 9 条缺点。逐条核实后，用户决定：
- 缺点 1/2/7/8：不处理
- 缺点 3（Full 模式成本较高 / SKILL.md 偏重）：精简 SKILL.md
- 缺点 4/5（绕开 Impact / 流程依从性）：SKILL 层面已到位，暂不处理
- 缺点 6（V23 证据检查不是严格白名单）：实施白名单
- 缺点 9（validate_real_projects.py 退出码 1）：修复

### 改了什么

**缺点 9：评测脚本修复**

- 创建 `eval/runs/real-projects/2026-07-04-minimax-m3-delivery-d19r2/README.md`（此前缺失，导致 `results[19]` 引用不存在）
- `validate_real_projects.py` 退出码从 1 变为 0

**缺点 6：V23 证据检查白名单**

修改 `skills/impact/scripts/impact_validate.py`：
- 新增 3 个白名单正则：`RE_CODE_LOCATION`（文件路径:行号）、`RE_QUOTE`（引号包裹的用户原话）、`RE_TEST_RESULT`（passed/failed/SELECT/命中等测试查询关键词）
- 证据列检查改为三层：先查黑名单（模糊词 → FAIL），再查"无依据"（→ 标记未确认），最后查白名单（不匹配 → FAIL）
- PASS 条件和 escalation 条件增加 `not non_whitelist_evidence` 守卫
- 效果："模型判断确有必要"不再能漏过（无模糊词但不匹配任何白名单 → FAIL）

新增 4 个测试用例（`skills/impact/tests/test_scripts/test_impact_validate.py`）：
- `test_model_judgment_fails`："模型判断确有必要" → FAIL
- `test_plain_text_fails`："根据经验需要" → FAIL
- `test_quote_evidence_passes`：用户原话「高峰期订单量会翻 3 倍」→ PASS
- `test_test_result_evidence_passes`："npm test 26 passed" → PASS

文档同步：
- `skills/impact/SKILL.md` Phase 4 必产出清单中 V23 描述更新
- `README.md` IntentDesign 证据类型说明更新

**缺点 3：SKILL.md 精简（334 行 → 260 行，减少 22%）**

| 精简项 | 操作 | 节省 |
|--------|------|------|
| 行为准则检查段 + 行为准则段 | 删除两段（与 CLAUDE.md 和核心原则重复） | -20 行 |
| 目录结构段 | 移到 `references/directory-structure.md` | -27 行 |
| Rule #12 澄清被拒绝 | 6 行 → 3 行（细节已在 `phases-detail.md`） | -3 行 |
| 快速通道段 | 11 行 → 3 行（细节已在 `phase-1-intent.md`） | -8 行 |
| Phase 4 段 | 删 Step 模板 + 脚本路径注释 + 压缩验证 bullets | -12 行 |
| 改进记录提示段 | 14 行 → 5 行，细节移到 `references/improvement-log.md` | -9 行 |

新增文件：
- `skills/impact/references/directory-structure.md`
- `skills/impact/references/improvement-log.md`

### 验证

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python eval/real-projects/scripts/validate_real_projects.py` | 0 | OK: 5 projects, 30 cases, delivery matrix checked |
| `python -m pytest skills/impact/tests/test_scripts/test_impact_validate.py -k V23 -v` | 0 | 19 passed（原 15 + 新 4） |
| `python -m pytest skills/impact/tests/test_scripts/test_impact_validate.py -v` | 0 | 85 passed（零回归） |

### 已知风险

- SKILL.md 精简后，上下文压缩时被移走的细节依赖 reference 文件存在。如果 reference 文件丢失，规则可能不完整。
- V23 白名单的 `RE_TEST_RESULT` 正则覆盖了常见测试/查询关键词（passed/failed/SELECT/COUNT/grep/npm/pytest 等），但可能不覆盖所有合法格式。
- 所有改动未经强模型在真实项目中端到端验证——V23 白名单是否误杀合规文档、SKILL.md 精简后弱模型是否仍能正确执行流程，都需要真实运行确认。

### 状态

已提交为 `60411d2`。2026-07-26 已经强模型（Fable 5）验证并修复发现的问题，见任务 J。

---

## 任务 J：强模型验证 + 校验器盲区修复（2026-07-26，已完成）

Fable 5 对任务 H/I 的产出做对抗性验证，发现并直接修复了以下问题：

**P0（会让正常使用失败）**

- **V8 模板不同步**：`templates/verify-record.md` 缺 `### 技术漂移复核` 子节，表格式（模块名/在 architecture.md 中/状态/说明）只存在于测试 fixture——已补进模板和 SKILL.md
- **V8 惩罚诚实**：校验器把"如实报告新增模块"判 FAIL——已改为按状态列分流：标"新增/缺失"的行免于存在性比对，改查说明列是否写明原因

**P1（证据白名单两头漏）**

- 误杀（实测 6/11 真证据被拒）：裸文件名、`第 N 行`中文行号、`Class.method()`、snake_case 标识符、弯引号/单引号原话、`无依据，属于假设。`带句号、引号内含"为了性能"的真实用户原话——已扩展白名单（impact V23 + design A7 同步）；黑名单只查引号外的部分
- 漏放（实测 4/7 假证据混过）：RE_TEST_RESULT 无单词边界，account（含 COUNT）/browser（含 rows）/裸 rows/record 均可混过——已加 ASCII 字母边界，rows/records 要求数字前缀
- "无额外结构"改为独立声明行才生效（"并非无额外结构"这类子串不再触发提前 PASS）；声明与数据行并存判矛盾 FAIL；表格解析前先剥 HTML 注释（注释内整表不再被当真行）
- V6 收紧："是（部分）""V3 未达成"这类搭车写法判 FAIL

**验证**：impact 94 passed（+9）、design 46 passed（+7）、verify 52 passed（+5）、七套件全量 308 passed、`validate_real_projects.py` 退出码 0、证据探测样本 19/19 分类正确（修复前 10/19 分错）。

**遗留（未修，属固有限制）**：直引号包裹任意文本即可过引号白名单——静态检查无法验证引语出处，已在两个模板的填写指引中加"引号即采信、禁止伪造"约束；verify_validate 的 design.md 参数仍是可选（路径错误时静默跳过交叉检查）。

---

## 任务 B（待补测）：blue-interview

blue-interview P1/P2/P3/P8/P9 已落地，P3 试跑通过，P1/P2/P8/P9 待补测。
skill 被 .gitignore 忽略，不入库。未经同意禁止修改。

详情：见 `skills/blue-interview/HANDOFF.md`。
