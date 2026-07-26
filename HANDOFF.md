# 交接文档

> 写给完全没有上下文的新会话。最近更新：2026-07-26（全天 7 个 commit，`2222124` → `a4c165f`，全部已推送）。
> 本文档覆盖十五个独立任务。A-F、A7、H、I 是 intent-chain 六件套与 impact 的建设期记录（均已完成）；J-N 是 2026-07-26 单日完成的验证与收尾（详情见各任务节）；blue-interview 另册（部分完成，待补测）。

## 当前状态与下一步（新会话从这里开始）

**intent-chain 六件套**：阶段性收口。两轮真实冒烟通过（Sonnet 5 模拟用户），确认次数 21 → 15（-29%，预期再降至 ~12-13），校验器测试 311 → 329 零回归，轻量档已上线（可感知能力 ≤5 触发，B′ 方案）。链路跑批：`python skills/_common/chain_validate.py intent-chain/{链路目录}`。

**发布主线（impact + pathfinder）**：release-gate 五条硬标准 **4 达标 + 1 待核**（详见 `docs/skill-eval/release-gate.md`）。2026-07-26 收口动作：

1. **D16 已闭环**：搜索盲区规则落地（`phase-2-context-discovery.md` Step 2.3 第 9 条）后完成复跑验证——按用户决策放弃调用不可用的 gpt-5.4-mini / MiniMax M3，改由 Sonnet 模拟 runner 执行（2 试次全覆盖原漏项 `.env:16` + `.github` CI 核查，完整交付试次 `impact_validate` 31/0/0，判分方独立复跑一致），记录在 `eval/runs/real-projects/2026-07-26-sonnet-sim-d16/`；原 FAIL / 无数据记录保留披露。§6.5 矛盾更正同日完成。
2. **标准 2 计法已拍板**：按场景计（至少一个 runner ≤2 轮修复内收敛即达标），标准 2 达标；D2/D3 的 composer FAIL 作为证据资产披露在支持矩阵。
3. **D16 × M3、D3 × M3 补跑随口径修订销项**（M3 移出承诺范围）。

pathfinder references 最后抽查已完成（2026-07-26，发现并修复 7 条文档同步缺口，L0 测试 43 PASS）——**五条硬标准全部达标，发布线达线**。收尾清单进展（同日）：QUICKSTART（仓库根目录）、pathfinder CHANGELOG 与 v1.0 首次定版、环境兼容说明（`docs/environment-compatibility.md`）已完成；仓库门面已拍板（2026-07-26）：eval/archive 历史评测记录**保留公开**（与"数据诚实"理念一致，是发布主张的证据链）；degradation-trap 保留（eval 定义资产）；大体积 fixture 本就未跟踪、不在远端。**达线后收尾清单全部完成，发布线收官。**

**其他待办**：W3 D5 漂移复核机械化（需先设计排除规则，见任务 L）；用户真实项目走一遍轻量档（毕业考）；sonnet-sim-d16 新发现两项待处理（V24 Check E 固定窗口假阳性、case prompt"先不要写代码"歧义，见该运行记录）。

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

**遗留（未修，属固有限制）**：直引号包裹任意文本即可过引号白名单——静态检查无法验证引语出处，已在两个模板的填写指引中加"引号即采信、禁止伪造"约束。

**追加修复（同日）**：verify_validate 的 design.md 从可选改为必传——CLI 缺第 4 个路径或文件不存在直接报错退出（不再静默降级）；validate() 的 design_content 为空时 V8 FAIL（与 architecture.md 同等待遇）。测试 55 passed（+3：缺 design FAIL、CLI 缺参数、CLI 路径不存在）。

**遗留 TODO**：P3（真实 0→1 项目跑通 intent-chain 全链路）——用户确认暂不跑，V8 新语义（状态分流）等真实运行时一并检验。

---

## 任务 K：intent-chain 首次真实冒烟 + 确认粒度统一 + 轻量档（2026-07-26，已完成）

### 冒烟测试

Sonnet 5 子代理在 `E:\agent\intent-chain-smoke\todo-cli\`（仓库外）跑通六阶段全链（todo CLI，真实 pytest 10/10 绿，4 条路径 V3，六个校验器最终全 0）。31 分钟 / 35.8 万 token / 112 次工具调用。摩擦日志在该目录 `friction-log.md`。

发现并已修复（P0，已提交 `218d809`）：
- **A-1 路径契约矛盾**：任务 D 统一目录时漏改 `intent_validate.py` 的 `_path_error()`，旧契约卡死六阶段入口——已改为 `intent-chain/{链路目录}/intent.md` 新契约
- **B-1 空格分词误杀**："CLI 入口"被 `[、，,\s→]` 拆散——design_validate `_split_tokens` 和 verify_validate V8 涉及模块解析去掉 `\s`

### 确认粒度统一（P1，五条规则）

实测总确认 21 次（严格字面 27 次），anchor 一阶段占 9 次。修复：
- R1 已答不重问（anchor 强制规则 7 + 步骤 6/7/10/11；设计素材的目录检查保留）
- R2 AFK 工单批量授权（dev Phase 2：开工列文件清单一次确认=写入授权；HITL 保持逐工单）——同时解决"确认结果后写入项目"与 TDD 需先落盘的时序矛盾
- R3 issues Phase 3 从摘要级确认改为完整草稿全文确认
- R4 六个 skill 统一："确认"两字即构成全文确认，"继续/嗯/可以"不算
- R5 PRD 模板可选子节改为"没有则删除本子节"，与 SKILL.md「如果有」和 fixture 省略写法对齐

顺带修复：四个 skill 的"下一步参见 README"死链改为直接点名下一个 skill 和输入文件；intent-issues Phase 5 遗留的旧式交接块（内容还是错的）同步清理；intent-dev allowed-tools 补 Edit。

### 轻量档（B′ 方案）

- 触发：anchor Phase 1 新增定档步骤，四条件（可感知能力≤5/单用户无权限/无 DB/无对外 API）全满足 + 用户确认；档位+依据+原话写入 INTENT.md 第 2 节（模板已加档位行）
- 减负：prd/design 薄写法 + 路径确认并入草稿确认；issues 单 AFK 工单直行；verify 强度不降
- 保险：升档单向（anchor 强制规则 8）；**校验器零改动**（档位行探测：函数级 14 PASS/0 FAIL，CLI 新路径契约退出码 0）

### 验证

七套件 315 passed；skills 目录 grep 无残留 README 死链。改动均为 SKILL.md/模板文案，未触碰校验器逻辑。

### 后续（同日完成）

- W5 chain_validate.py 跑批、W7 防漂移测试已落地（任务 L）
- 轻量档二次冒烟已完成并收尾（任务 M）

---

## 任务 L：链路跑批 + 防漂移测试（2026-07-26，已完成）

### W5：chain_validate.py

`skills/_common/chain_validate.py`——一条命令按流水线顺序对链路目录跑全部六个校验器。行为：intent.md 缺失 FAIL（链路起点）；下游未产出标跳过（做到一半是常态）；已产出但前置缺失 FAIL；任一 FAIL 退出 1。测试 4 项（编排行为）。真实验证：对冒烟一号产物目录跑 6/6 PASS 退出 0。README 已加使用说明。

### W7：防漂移测试（+10 项）

- `skills/_common/tests/test_cross_validator_consistency.py`：锁定 impact V23 与 design A7 的四组正则拷贝（代码位置白名单/引号/引号剥离/无额外结构声明行）必须逐字符一致——单边修改即测试失败
- 五个 skill 各加 TestTemplateSync：校验器要求的必需章节/标题必须存在于模板（anchor 16 节、prd 8+3、design 6+3、issues 工单段落+覆盖段、verify 13 个标题常量）——从机制上杜绝"V8 模板缺节"类 bug。首跑全绿，说明现存模板无其他隐藏不同步
- intent-dev 无标题常量契约，不适用模板自检

### W3（D5 机械化）：本轮不做，已想清楚设计坑

推迟/放弃项的名字会合法出现在 PRD Out of Scope、INTENT 第 6 节等位置，朴素 grep 必然误报。需要先设计排除规则（只扫实现性内容区，跳过 Out of Scope/推迟说明），另轮单独处理。

### 验证

八套件 329 passed（+14）；chain_validate 真实链路 6/6 PASS。

### 遗留

- ~~轻量档二次冒烟结果待回~~ → 已回，见任务 M
- W3 D5 机械化（含排除规则设计）

---

## 任务 M：轻量档二次冒烟 + 收尾修复（2026-07-26，已完成）

### 二次冒烟结果（ledger-cli，Sonnet 5，轻量档路径）

- 六阶段全通，**21 次校验器调用全部一次 PASS、0 重试**（一号冒烟撞了 6 次路径 FAIL + 1 次误杀——A-1/B-1 修复的正向回归，含故意使用"CLI 入口"空格模块名）
- 总确认 **21 → 15 次（-29%）**：anchor 9→6（R1 生效，定档新增 1 次）、prd 3→1、design 2→1
- R1 检验：开场白四项（无性能/无安全/无素材/无不可妥协项）**六阶段零重复提问**
- E 类（一号的 E-1~E-4）、F 类死链、G 类严格失效（薄写法被拒）全部清零
- 真实产出：ledger CLI 四轮 TDD、13 pytest 全过、4 路径 V3
- 摩擦日志：`E:\agent\intent-chain-smoke\ledger-cli\friction-log.md`

### 收尾修复（四项，均为规则覆盖不全）

1. **G-1 定档两段式**：Phase 1 改为"暂定档位"（不需确认），Phase 2 新增步骤 12"正式定档"（能力盘点后用真实计数复核四条件 + 用户确认）
2. **上游已答不重问跨链路**：五个下游 skill 各加一条强制规则（上游文档已记录的信息直接引用不重问）；intent-dev Phase 1 步骤 4 明确"先查上游技术偏好再问用户"（修二号冒烟 A-3：dev 重复问 pytest）
3. **G-2 issues 路径确认并入**：轻量档节补上与 prd/design 一致的"路径确认并入草稿确认"；dev 批量授权句同步"命令确认并入开工确认"
4. **prd fixture 对齐 R5**：valid-prd.md 删除 Design Standards / Terminology 两个"无"stub 子节，与模板"没有则删除本子节"及 V5/V6"不适用"逻辑一致（修二号冒烟 A-2）

预期效果：issues 2→1、dev 3→2，总确认 ~12-13（待下轮冒烟或真实使用验证）。

### 验证

八套件 329 passed 零回归。verify 阶段的确认保持 2 次未合并——验收阶段的确认是有意保留的安全冗余。

---

## 任务 N：发布主线阶段 3 收尾——15 条失败归因 + release-gate + 支持矩阵（2026-07-26，已完成）

32 代理 workflow（15 归因 + 15 对抗核实 + 矩阵 + 综合）完成，**质疑者裁决 15/15 CONFIRMED**。

**归因结论**：15 条 FAIL/UNVERIFIED 里 13 条已闭环（多数是"门禁正常工作的证据资产"——skill-process-escape 7、model-behavior-caught 5、infra 1、gate-defect 1、coverage-gap 1）。**唯一阻塞发布：D16**（gpt-5.4-mini 配置迁移分析漏查被 gitignore 的 .env 和 .github CI）。

**产出**（均已落盘）：
- `docs/skill-eval/release-gate.md`——阶段 5 硬标准逐条达标判定
- `eval/real-projects/model-support-matrix.md`——4 runner × D1-D20；Composer 2.5 Fast 18/20 最可靠，gpt-5.4-mini 16/20 但最小 prompt 下有稳定流程逃逸
- `eval/real-projects/attribution-2026-07-26.md`——归因总表

**行动清单**：P0 ×2（impact 搜索指引补"配置迁移必查 --no-ignore 的 .env/.github"规则 + 复跑 D16；修 handoff-summary §6.5 与 D16 结果矛盾）；P1 ×3（D16 补 M3 数据、D3 M3 额度恢复后补跑、拍板 release-gate 标准 2"L 任务收敛"按 runner 还是按场景计）。

**进展（同日）**：P0 的便宜部分已完成——搜索盲区规则落地 `phase-2-context-discovery.md` Step 2.3 第 9 条，handoff-summary §6.5 两处矛盾更正，release-gate.md 已记进展。P1 之一"拍板标准 2 计法"已完成（2026-07-26 定为按场景计，标准 2 转达标）。**剩余：复跑 D16 × gpt-5.4-mini（需 runner 额度）+ 两个 P1（D16 补 M3 数据、D3 × M3 补跑）。**

---

## 任务 B（待补测）：blue-interview

blue-interview P1/P2/P3/P8/P9 已落地，P3 试跑通过，P1/P2/P8/P9 待补测。
skill 被 .gitignore 忽略，不入库。未经同意禁止修改。

详情：见 `skills/blue-interview/HANDOFF.md`。
