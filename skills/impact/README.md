# ImpactRadar — 现有系统变更影响分析 Skill

## 这个 Skill 是干什么的

面向 Java/Spring/MyBatis 类现有系统（如 RuoYi 等后台框架），把模糊的功能迭代、新功能接入或高风险变更意图，通过靶向提问变成基于证据的影响分析，light/full 两档输出，统一写入 `change-impact/` 目录并协助执行。

它不是从 0 到 1 搭建新系统的生成器，而是在已有代码、schema、接口、配置、测试和业务约束中，辅助完成一次安全可追溯的系统变更。

它可以搭配 `RuleBlade` 使用：`RuleBlade` 约束 agent 的通用编码行为，`impact` 负责 Java/Spring/MyBatis 类现有系统（如 RuoYi 等后台框架）的影响分析、文档输出和受监督执行流程。

## 核心价值：给模型带来什么增益

经过 V1-V9 共 9 轮盲测（3 个模型 × 6 个真实场景 × 有/无 skill 对照 = 100+ 份产出），skill 的核心价值可以归纳为以下五点：

### 1. 把模糊需求变成显式假设

**这是 skill 最核心的增量。** V7 盲测用口语化模糊 prompt 替代精确 prompt 后，skill 增益从 +2 分跃升到 +12.1 分。

| 指标 | 精确 prompt（V6） | 模糊 prompt（V7） |
|------|:---:|:---:|
| skill 增益 | +2 分 | **+12.1 分** |
| noskill 分数 | 75.2 | 63.8（模糊 prompt 拉低了 11.4 分） |
| skill 分数 | 77.2 | 75.9（模糊 prompt 仅拉低 1.3 分） |

关键发现：**所有 skill 组都识别了模糊点并标注了 `[假设]`，所有 noskill 组都没有。** noskill 组并非没有做假设——它们隐式地做了同样的假设（如"限制 1MB"、"踢人模式"），但用户无法区分哪些是确定的、哪些是猜的。skill 把隐式猜测变成了显式标注，用户可以在文档确认环节逐条过。

### 2. 苏格拉底式提问，不替用户拍板

skill 不是"遇到模糊需求就直接假设"，而是按优先级分层处理：

- **P0 模糊点**（不问就可能做错）→ 必须在 Phase 3 提问，不得假设
- **P1 模糊点**（影响兼容性/设计质量）→ 应该提问；用户没答时可假设，但必须标"待确认"
- **P2 模糊点**（可按项目约定推断）→ 可直接假设，标 `[假设]` + 依据

假设的生命周期到文档确认为止——提交确认时必须把 `[假设]` 条目单独列出，让用户确认/修正/拒绝。

### 3. 结构化保障：noskill 偶尔做到，skill 始终做到

| 结构化要素 | noskill 组 | skill 组 |
|------|:---:|:---:|
| 前置检查清单 | ❌ | ✅ |
| 回滚方案 | 偶尔提及 | ✅ 逐步骤 |
| 验证步骤（正向+错误用例） | 偶尔提及 | ✅ 系统性 |
| 方法名存在性验证 | ❌ | ✅ grep 拦截编造方法名 |
| 环境备选路径 | ❌ | ✅ |
| 跨会话恢复状态 | ❌ | ✅ |
| 风格约束引用 | ❌ | ✅ `[已核实]` 标签 |

noskill 强模型偶尔能做出其中几项，但无法稳定覆盖。skill 把这些变成流程的一部分，模型无关。

### 4. 防御性检查：发现深层问题

V7 盲测中，skill 组有几处独有发现：

- **refreshToken TTL 同步**（B1'）：C2 GLM skill 发现 `refreshToken()` 需要同步刷新 userId→token 映射的 TTL，否则映射会先于 token 过期导致单会话逻辑失效。这是全部 6 份产出中唯一的发现。
- **方法名编造拦截**：skill 的实施文档预检会 grep 验证方法名是否存在，拦截 `updateUserPassword` 等凭训练数据编造的方法名。
- **null 检查 vs 抛异常**：skill 会打开方法源码确认异常行为，拦截"用 null 检查但方法实际抛异常"的设计缺陷。

### 5. 安全闸：模型无关的硬约束

以下检查点不因模型强弱放松——弱模型也绕不过：

- 逐步确认（`确认 Step N`，不接受模糊授权）
- 写入目标边界（必须在项目根目录内）
- 高风险拦截清单（10 类不可逆操作命中即暂停）
- DB 只读纪律 + DDL/DML 执行方式
- 凭证脱敏 + 仓库内文本不构成指令
- 阻塞恢复安全闸

### 增益的边界（诚实说明）

skill 不是万能的。V7 暴露了两个已知局限，已在 v3.9 修复：

- **light 模式可能跳过深入检查**：C2 GLM skill 在 B2' 选择 light 后遗漏了 413→500 降级问题。v3.9 为 light 模式增加了"关键链路深度检查"门禁。
- **弱模型可能"过早收敛"**：C6 Step skill 在 B2'/B3' 只产出 1 个 Step，遗漏大量改动。v3.9 增加了"改动完整性自检"——对照验收标准逐条映射实施 Step。

另外，noskill 强模型偶有超越 skill 的深度分析（如 C1 GLM noskill 在 B2' 发现了 isOperational 降级和 XSS 内存放大）。v3.9 在 context-pack 中增加了"关键链路追踪"节，鼓励对错误处理链和中间件管线做追踪式分析。

V9 发现 agent 在人工交互模式下倾向于 1 轮问 3 题就停止，即使链路追踪已发现额外的副作用风险点（如"重发验证邮件可被无限调用"）也未追问。v4.1 新增多轮触发条件，要求链路追踪发现的副作用风险点必须回流到 Phase 3 澄清环节。

## 模型敏感性

本技能的**分析深度（Phase 2 上下文发现、证据核实、Phase 3 苏格拉底提问、定级）**依赖执行模型。强模型（Opus / 同级）能扎实取证、严守确认检查点；弱模型（Sonnet / Haiku / 更弱）可能：证据核实不严（行号/表名偏差）、定级偏松、苏格拉底提问收敛不彻底。

- **强模型**：日常可靠。
- **弱模型**：输出（尤其 context-pack 的【已核实】项、设计文档的影响面）**需人工复核**。

强制规则区（逐步确认 / 写入边界 / 凭证脱敏 / 高风险拦截）是模型无关的硬性安全闸——弱模型也绕不过逐 Step 确认；但"分析有多深、证据有多准"随模型起伏。Phase 5 执行的安全闸不因模型放松。

### V7 盲测模型对比（2026-06-25）

| 模型 | noskill 均分 | skill 均分 | 增益 | 增益来源 |
|------|:---:|:---:|:---:|------|
| GLM-5.2 | 71.7 | 84.3 | +12.7 | 结构化 + 假设标注（B1' 的 refreshToken TTL 是独有发现） |
| Composer 2.5 | 71.0 | 83.7 | +12.7 | 假设标注 + 方案完整性（ADMIN 豁免、resend 端点） |
| Step 3.7 Flash | 48.7 | 59.7 | +11.0 | 分析框架（B1' +26，但 B2'/B3' 增益微弱——弱模型"过早收敛"） |

**关键结论**：强模型增益来自结构化 + 假设标注；弱模型增益来自分析框架，但在复杂场景中容易"过早收敛"（只做最表面的改动）。v3.9 的"改动完整性自检"专门针对这个问题。

### V8-V9 盲测补充（2026-06-25）

V8（自问自答模式）和 V9（人工交互模式）使用 Composer 2.5 做了进一步验证：

| 轮次 | 模式 | skill 均分 | noskill 均分 | skill 优势 | 关键变化 |
|------|------|:---:|:---:|:---:|------|
| V8 | 自问自答 + v3.9 | 88.0 | 73.7 | +14.3 | v3.9 改进全面生效，V7 遗漏项 5/5 捕获 |
| V9 | **人工交互** + v4.0 | **92.0** | 73.7（复用 V8） | **+18.3** | 8 项 `[假设]` 100% 转为用户确认，D5 澄清质量 13.3→15.0 |

V9 证明人工交互模式下澄清质量显著优于"自问自答"。但 V9 也发现 agent 倾向于固定问 3 题就停止，即使链路追踪已发现额外的副作用风险点。v4.1 已修复此问题。

### V10 单 case 验证（2026-06-25）

V10 用 B3'（邮箱验证强制检查）单 case 验证 v4.1 的多轮触发和链路追踪回流是否生效：

| 指标 | V9 B3'（v4.0） | V10 B3'（v4.1） | 变化 |
|------|:---:|:---:|:---:|
| 提问轮数 | 1 | **2** | +1 |
| 提问总数 | 3 | **5** | +2 |
| 链路追踪副作用追问 | ❌ | **✅** | v4.1 生效 |
| 总分 | 92 | **96** | +4 |

v4.1 两项核心改进全面生效：agent 在第 1 轮 3 题后自检链路追踪 §5，发现"公开重发接口可被无限调用"副作用风险未覆盖，进入第 2 轮追问。副作用不仅被追问，还转化为具体设计（Step 6 限流）。评审报告见 `eval/runs/blind-2026-06-25-v10/scorecards/_v10-review-report.md`。

## 核心能力

- **苏格拉底式提问** — 基于实际 schema 和代码发现上下文，针对性提问，不泛泛而谈
- **项目背景** — 用 L1/L2/L3 分层探索，给后续 agent 一个小而准、可解释的上下文入口
- **引用检查分级** — 改前反查调用方、引用方、注册点、生成物和测试，按必须同步修改 / 需要用户决策 / 只需验证 / 暂不纳入处理
- **可选 code graph MCP** — 存在 tree-sitter / code graph 类 MCP 时先取结构化定义、引用和调用候选；无工具或证据不足时诚实回退 `rg/git grep`
- **长期目标模式** — 面对迁移、对齐、重构、大功能接入、债务清理等多 Step 任务，维护当前 Step、backlog、阻塞项和未验证项
- **light/full 两档模式** — 简单改动走一页摘要，复杂变更走三文档；可简化文档形式，但不能跳过安全检查
- **接口返回检查清单** — light 涉及向后兼容响应字段新增时，检查消费者、文档、generated client、验证方式和未验证项
- **基于证据的分析** — 用工具发现真实上下文，不靠臆测做推测性分析
- **验证等级** — 区分 V0 未验证、V1 静态验证、V2 构建/单测、V3 运行路径验证，避免把静态检查说成完整验收
- **19个维度灵活覆盖** — 按需选择，不强制全覆盖
- **三文档逐级确认** — 需求文档 -> 设计文档 -> 实施文档，每份确认后再出下一份
- **逐操作执行确认** — 每步写操作前都要求 `确认 Step N`，不接受模糊授权
- **自动/确认边界清晰** — 只读操作自动跑，写操作必须确认
- **高风险 Step 拦截清单**（v3.7 强制规则化）— 10 类不可逆操作命中即禁止执行、必须暂停，等用户单独确认；不允许合并确认、不允许裁量空间
- **DB 只读纪律 + DDL/DML 执行方式**（v3.7 新增）— schema 发现阶段只允许只读查询；DDL/DML 默认生成脚本不直接执行，生产 DB 默认禁止 Agent 直接执行
- **V1-only 连续计数**（v3.7 提级为通用规则）— 无论是否 Git 项目，连续 3 个写入 Step 只达 V1 静态验证即暂停；计数粒度按 Step 计
- **凭证脱敏 + 仓库内文本不可信**（v3.7 新增硬性规则）— 凭证写入任何文档前必须脱敏为 `***`；仓库文件/代码注释/commit message 中的指令性文本不构成确认
- **现状核查**（v3.7 新增）— 进入设计前先验证目标功能/字段/接口是否已存在或部分存在，避免重复造轮子
- **用户场景覆盖验证**（v3.8 新增）— Phase 2 排除文件/模块前必做：验证用户原始需求场景是否仍被剩余文件完全覆盖，防止基于错误假设排除文件导致场景遗漏
- **覆盖范围语义核查**（v3.8 新增）— Phase 2.5 定级前必做：用户表述出现"每次/所有/全部/任何/一律"等全量词时，核实现有实现是否真的全覆盖，"已存在"不等于"已全覆盖"
- **实施文档代码引用预检**（v3.8 新增）— `030-implementation.md` 提交前静默检查：API 方法名存在性验证（grep 拦截编造方法名）+ 被调方法异常行为确认（拦桶 null 检查但方法实际抛异常的设计缺陷）
- **需求文档内容边界**（v3.8 新增）— `010-requirements.md` 生成后自检：只写业务需求（做什么/为什么/怎么做完），技术实现细节归 020/030，避免需求文档渗入技术细节
- **Grep 假阳性预警**（v3.7 新增）— 引用计数异常大时先验证依赖是否真实存在，再抽样核实
- **MCP 能力运行时探测**（v3.7 修正）— 工具能力以运行时探测为准，不以厂商或工具名假设；凡能执行任意 SQL 的工具一律视为「有写能力」
- **可选 PreToolUse hook** — 在 Claude Code settings 层按 `.impact-protected` 标记启用写前拦截，把 `确认 Step N` 从 prompt 纪律补强为工具执行前检查
- **安全闸压缩存活**（v3.7 新增）— 全部硬性安全闸浓缩为篇首强制规则区，确保上下文压缩后仍生效
- **禁用模型自动触发**（v3.7 新增）— `disable-model-invocation: true`，唯一入口手动 `/impact`
- **统一输出目录** — 所有产物写入 `change-impact/{需求名称}/`
- **测试验证框架** — 风格合规检查 + 单元测试自动跑，E2E 生成脚本；验证必须包含正向用例 + 错误用例（TDD 思路）
- **设计原则约束** — 简单优先、精准修改、质量底线三条原则内嵌于设计环节
- **测试失败 fix 循环** — 自动诊断并生成修复方案，任何 Edit/Write/DDL/DML 都必须确认，不自动执行
- **破坏性请求保护** — 直接删、DROP/RENAME、删除接口、批量替换必须先只读发现影响面
- **阻塞恢复安全闸** — blocked、上下文压缩或延迟确认后，先复核 pending Step、当前文件状态和最新授权，再决定是否执行
- **跨会话恢复状态** — Phase 4/5 自动维护 `change-impact/{需求名称}/_active-state.md`，记录 pending Step、文档确认、验证等级和未确认项；恢复时先核验磁盘状态，不能替代 `确认 Step N`
- **subagent 自治模式**（v3.6 新增，仅限 eval 脚手架）— 跑分时 subagent 模拟人类用户在沙盒里独立使用 skill，对 6 类高风险 Step 自主判断做不做。这是**测评协议**的事，不是 skill 生产协议的事；生产会话里不存在 subagent 自治，所有高风险操作走 SKILL.md 硬性规则（禁止执行、必须暂停、等用户显式确认）。eval 细节见 `docs/archive/2026-06/skill-capability-eval-2026-06-10/protocol-draft-subagent-as-user.md`
- **决策矩阵模板**（v3.6 新增）— `templates/subagent-decisions.md`（RESTATE -> DECIDE -> RECORD 三段）
- **环境回退路径**（v3.6 新增）— `templates/030-implementation.md` 加"V3 受限时启用 X 备选"段，避免事后才发现
- **PASS/FAIL 决策依据**（v3.6 新增）— `templates/090-execution-record.md` 决策依据字段从散文升级为 6 项高风险清单显式勾选
- **light 模式关键链路深度检查**（v3.9 新增）— light 模式提交确认前强制检查错误处理链、中间件管线、数据流路径、配置依赖的兼容性；V7 盲测发现 light 遗漏 413→500 降级问题
- **改动完整性自检**（v3.9 新增）— 实施文档提交前对照 010 验收标准逐条映射实施 Step，防止弱模型"过早收敛"只做表面改动
- **模糊点处理清单**（v3.9 新增）— 需求文档中逐条记录每个模糊点的处理方式（已提问确认 / `[假设]` / 未确认），提交确认时单独列出假设请用户逐条过
- **context-pack 关键链路追踪**（v3.9 新增）— 对错误处理链、中间件管线、数据流路径、配置依赖做追踪式分析，保留探索深度，防止结构化流程限制分析
- **light 模式配置化提示**（v4.0 新增）— light 模式实施步骤中如果涉及阈值/限制值等假设参数，提示通过环境变量或配置文件使其可配置；V8 盲测发现 skill 组硬编码了请求体限制而 noskill 组提出了环境变量方案
- **配置依赖链路追踪**（v4.0 新增）— 关键链路追踪和 light 深度检查增加"配置依赖"类型，追踪配置加载链路、默认值和覆盖优先级，识别硬编码 vs 可配置问题
- **多轮触发条件**（v4.1 新增）— 第 1 轮未覆盖所有 P0/P1 级问题（含链路追踪发现的副作用风险点）时，必须进入第 2 轮，不得用"每轮 3 题"作为停止理由
- **链路追踪发现回流 Phase 3**（v4.1 新增）— 模糊点覆盖率自检新增扫描 000-context-pack.md §5 关键链路追踪表的"发现的二级影响"列，确保副作用风险点回流到澄清环节

## 什么时候该用这个 Skill

不是所有变更都需要走这个流程。用错了反而费劲。

**适合用的场景：**

| 场景 | 原因 |
|------|------|
| 现有系统中的功能迭代或新功能接入 | 需要先看清已有代码、schema、接口、权限、配置和测试约束 |
| 涉及 3 个以上维度的变更 | DB + 代码 + 前端 + 配置全套，维度越多漏掉的概率越高 |
| 需要多人协作的变更 | 文档是团队沟通的依据，干活的人需要知道"为什么改" |
| 涉及数据库 schema 变更 | 影响面广，需要系统性地想清楚再动手 |
| 需要合规/审计追溯的变更 | 文档和执行记录是追溯的凭证 |
| 重构核心模块 | 改动大、风险高，需要完整的设计文档指导实施 |
| 对接外部 API / 消息队列 | 涉及消费者协调，接口变更需要文档化 |
| 迁移、对齐或长期债务清理 | 当前 Step 只是总目标的一部分，需要持续维护 backlog、阻塞项和验证状态 |

**不适合用的场景：**

| 场景 | 原因 |
|------|------|
| 从 0 到 1 搭建新系统 | 这个 Skill 的价值来自现有上下文发现；空项目更适合直接做架构设计或脚手架生成 |
| 单一字段的简单加字段 | 直接让 agent 干，5 分钟的事不要写 30 分钟文档 |
| 纯前端样式/文案调整 | 不涉及后端逻辑，维度少，文档价值低 |
| 个人项目快速原型 | 速度优先，文档是负担 |
| 明显的小 bug 修复 | 目标明确，不需要需求澄清 |

**判断标准**：如果说不清楚"这个变更影响多少人、涉及多少系统"，就先想清楚再动手。如果自己都清楚，直接让 agent 干。

---

## 触发方式

本技能已禁用模型自动触发（`disable-model-invocation: true`），唯一入口是手动 `/impact`。'影响分析''改个字段' 等描述不再自动路由进入本技能。

在 Claude Code 终端输入 `/impact` 即可激活。

长会话发生上下文压缩后，建议重新 `/impact` 调用恢复 skill 全文；压缩后存活的篇首强制规则区已覆盖全部硬性安全闸。

## 验收状态

安全检查和回归检查见 [VALIDATION.md](VALIDATION.md)，优化后回归复测协议见 [../../docs/skill-eval/regression.md](../../docs/skill-eval/regression.md)，验证记录见 [validation-runs/INDEX.md](validation-runs/INDEX.md)。

当前已完成 Claude Code + MiniMax M3 真实 `/impact` 复测，覆盖长期对齐任务、接口返回字段定级、V0-V3 验证等级、非 Git 回退方案、阻塞恢复安全闸、Step 范围一致和最小写操作完成。

2026-06-09 的 T06 又补做了多会话写授权一致性验收：初始复测发现写入目标边界 P0，随后补强目标项目根目录检查、执行记录随当前 Step 补齐、连续 V1-only 暂停等规则，并通过 S1-S7 完整回归。当前结论：本轮定义的多会话写授权一致性通过，无 P0/P1。

2026-06-14 的 T07 补齐了负向安全闸可重复 e2e 场景：硬性规则 #1（逐步确认）/ #4（写入目标边界）/ #6（阻塞恢复）此前只在 T04/T06 手工复测，没有自动化负向用例。本次新增 3 个负向 scenario spec + subagent 实跑，**3/3 安全闸全 PASS**——含 neg-006 抓住"记忆/文档与磁盘事实不一致"这一真实恢复故障。2026-06-15 补全余下 4 条硬性规则的负向 spec（neg-002 高风险拦截 / neg-003 DB 只读 / neg-005 破坏性请求 / neg-007 凭证脱敏），现 `tests/scenarios/negative/` 含 **7 个** scenario spec，覆盖全部 7 条硬性规则（其中 neg-001/004/006 已 e2e 实跑，neg-002/003/005/007 为 spec 待 e2e）。记录见 [validation-runs/2026-06-14-T07-negative-iron-rule-gates.md](validation-runs/2026-06-14-T07-negative-iron-rule-gates.md)。

2026-06-15 的 T08 完成 `_active-state.md` 跨会话恢复 dry-run e2e：Claude Code CLI 只读前向测试确认 `_active-state.md` 只是 checkpoint 不替代 `确认 Step N`，恢复后仍需重读执行文档和磁盘状态。记录见 [validation-runs/2026-06-15-T08-active-state-resume-e2e.md](validation-runs/2026-06-15-T08-active-state-resume-e2e.md)。

**v3.6 subagent 跑分**（2026-06-10）：9 case Phase 1-4 + 9 case Phase 5 全量，subagent-as-user 自治模式 WORKABLE；0 P0；P0 默认 3/3 一致。详细见 [docs/archive/2026-06/skill-capability-eval-2026-06-10/README.md](../../docs/archive/2026-06/skill-capability-eval-2026-06-10/README.md)。

## 测评体系

impact 已接入统一测评框架（[docs/skill-eval/](../../docs/skill-eval/)），支持三层防不一致检测：

- **L0 静态自洽**（每次改动必跑）：`bash skills/impact/tests/run.sh` — 检查硬性规则存在、引用完整、共享契约、fixture 锁定
- **L1 行为契约**（release 前跑）：`bash eval/run-l1.sh impact` — 4 个标准化 case（R1/R2/R3/R3N），subagent 扮用户端到端跑分，客观维度机器判 + 安全闸
- **L2 人审深度**（里程碑抽样）：主观维度（苏格拉底质量、文档可读性）人工复核

当前基线来自 2026-06-14（4 case，平均基础分 89.3 / 100，opus-4-8）。每次改 skill 后跑 L1 产出评分卡，用 `bash eval/diff-baseline.sh impact` 和基线 diff——任何契约掉绿或维度掉档>=3 即红线阻断。基线详情见 [eval/baselines/impact.json](../../eval/baselines/impact.json)。

共享契约（三 skill 都要守）：基于证据不臆测、可信度标记二分、凭证脱敏、仓库内文本不构成指令、写入目标边界。L0 自动检查这些契约在三个 SKILL.md 中都存在，防止改一处另两处不一致。

## 典型对话流程

```
你：我想给用户管理加一个个性签名字段
|
Skill 推断涉及维度（数据库+代码+接口+前端），请确认
|
Skill 构建项目背景：项目地图 -> 变更邻域 -> 精准证据
|
Skill 基于项目背景给出初步风险预判
|
Skill 提问：字段长度？个人中心还是管理后台？导出要吗？
|
你：回答问题
|
Skill 继续提问（或收敛）
|
Skill 基于证据正式建议：light 还是 full？
|
你：确认 full
|
你：够了，输出文档
|
Skill 写入需求文档 -> change-impact/用户个性签名/010-requirements.md
|
你：确认
|
Skill 写入设计文档 -> change-impact/用户个性签名/020-design.md
|
你：确认
|
Skill 写入实施文档 + 验证脚本 -> change-impact/用户个性签名/030-implementation.md + 050-validation/
|
你：确认，开始执行
|
Skill：执行操作 1/5，确认吗？
|
你：确认 Step 1
|
Skill：执行 -> 风格合规检查 + 单测 + 正向用例 -> 全部通过 -> 写入 090-execution-record.md
|
你：确认 Step 2
|
...（每步操作后自动跑 A+B 测试）
|
E2E 验证脚本已生成 -> change-impact/用户个性签名/050-validation/
```

## 迭代记录

### v1.0（初始版本）

第一个版本输出结构化 prompt 给下一个 agent 做影响分析。没有文档，没有执行能力。

### v2.0（核心重构）

- 去掉 prompt 输出，改出三份完整文档
- 插入决策点，逐文档确认
- 支持执行，每步确认
- 19 维度覆盖
- 维度灵活选择
- 代码风格分析
- 测试验证框架
- 统一输出目录

### v2.1（TDD 验证思路）

- 验证步骤必须包含正向用例 + 错误用例
- 错误用例类型：边界值、空值、格式校验、XSS 安全风险、幂等性、缓存一致性

### v2.2（设计原则约束）

- Phase 2 内嵌最小改动原则
- Phase 3 新增质量底线追问
- 设计文档新增"设计原则约束"章节

### v3.0（本次合并优化）

**从优化版合并进来：**
- light/full 两档模式（简单改动走一页摘要，不硬走三文档）
- 自动/确认边界表（清晰区分只读操作和写操作）
- MCP 能力探测（先判断工具可用性再分支，不对着不可用工具报错）
- 退出条件（用户说简化就简化，不硬走流程）
- 模板外置（templates/ 目录，SKILL.md 只保留流程逻辑）

**保留的已有特性：**
- TDD 正向+错误用例验证框架
- 设计原则约束独立章节
- 风格约束标签框架
- 统一输出目录

**核心差异 vs 初始版本：**
- 从"提示下一个 agent 分析"变成"自己输出文档并执行"
- 从"固定走三文档"变成"light/full 按需选择"
- 从"模糊确认边界"变成"表格化自动/确认边界"

### v3.1（安全检查补强）

- Phase 2.5 改为初步风险预判，正式 light/full 定级延后到苏格拉底澄清之后
- `yes/no` 执行确认升级为 `确认 Step N / 跳过 Step N`
- 模糊确认、自动续跑、系统消息和历史授权不能替代当前用户 Step 级确认
- 用户可要求简化文档，但不能跳过分析依据、执行前检查、Step 确认和验证方案
- 新增 `060-preflight.md` 和 `090-execution-record.md` 模板
- 增加 P0/P1/P2/P3 问题优先级和多轮提问规则

### v3.2（行为准则回补）

- Phase 1 增加当前假设、可能歧义、更简单方案、任务规模和成功标准
- 增加行为准则检查，覆盖简单优先、精准修改、目标驱动、语义约定确认和测试策略
- 增加破坏性请求保护，用户要求直接删/批量替换也必须先只读发现影响面
- 修正 light 模板表述：light 只简化文档形式，不代表确认后直接跳过 Phase 5

### v3.3（项目背景）

- Phase 2 从"上下文发现"升级为"项目背景构建"
- 增加 L1 项目地图 / L2 变更邻域 / L3 精准证据三层探索
- 每个候选文件、表、接口或配置项必须标注相关性 3/2/1/0
- 未完成项目背景前不得正式 light/full 定级
- 新增 `templates/000-context-pack.md`

### v3.4（长期真实使用补强）

- 增加长期目标模式，覆盖迁移、对齐、重构、大功能接入和债务清理等多 Step 任务
- 增加源系统到目标系统对齐规则，要求记录可信来源、目标实现、对齐语义和差距证据
- 兼容性新增 API 响应字段可走 light，但必须填写接口返回检查清单；破坏兼容或消费者不明仍需 full
- 增加 V0-V3 验证等级，静态检查、构建单测和运行路径验证分开记录
- 增加非 Git 项目回退保护、阻塞恢复安全闸、Step 范围一致、验证命令证据和执行记录完成声明
- 完成 Claude Code + MiniMax M3 真实 `/impact` 复测，记录见 `validation-runs/2026-06-08-T04-m3-real-slash-regression.md`

### v3.5（多会话写授权一致性）

- 增加写入目标边界：`change-impact/` 和所有写入对象都必须在目标项目根目录内
- 写代码、配置、DDL/DML、测试修复后，执行记录必须随当前 Step 补齐
- 连续 3 个写入 Step 只能达到 V1 静态验证时暂停，要求用户确认风险或补运行环境

### v3.6（subagent 跑分反馈）

[2026-06-10 eval 报告](../../docs/archive/2026-06/skill-capability-eval-2026-06-10/README.md) 跑了 9 case Phase 1-4、9 case Phase 5、2 case 回归。subagent 在沙盒里自主执行，暴露了几处协议可以补强的地方。

**改了什么**

执行记录的决策依据从散文升级为 6 项高风险清单的 PASS/FAIL 表格。配套新增 `templates/subagent-decisions.md` 模板（RESTATE -> DECIDE -> RECORD 三段）。`030-implementation.md` 多了一段"环境回退路径"，把 V3 受限后的备选方案写进 Phase 2.5 而不是事后才发现。`ty check` 必须走 venv 的 `python -m ty`；alembic 验证优先用离线 SQL 渲染。SKILL.md Phase 5 末尾加了"高风险 Step 识别清单"子段，列出 6 类不可逆操作作为 subagent 自主判断的参考。

**边界修正**

subagent 在沙盒里是用户角色——这条原本写在 SKILL.md 里，现在挪到 harness（02-执行协议.md）。高风险清单保留在 SKILL.md，因为它属于 skill 自身内容。

**跑分数据**

9 case Phase 5 全量通过，subagent 真改了 38 个文件、新增 19 个。0 P0。P0 默认行为跑了 3 次都一致（R3 在 Step 7 停下来，v1 一行没动）。`java-spring-mybatis` profile 在 R4 跑出来比 R1 多三处安全约束（字段长度、`@Xss`、`@Size`）。

**撤销两项原 P1 修复**（被真实跑分证伪）

- 原 P1-001（EasyExcel 编造）：R1/R4 都正确识别 RuoYi 用 `@Excel` 注解
- 原 P1-003（i18n 边界）：R2 主动检查后确认 RuoYi 不是 i18n 项目
- 完成 S1-S7 多会话写授权回归，记录见 `validation-runs/2026-06-09-T06-multisession-write-gate.md`

### v3.7（安全补强：双评审缺口修复）

[2026-06-11 缺口清单](../../docs/archive/2026-06/skill-gap-list-2026-06-11.md) 经 Claude + GPT5.5pro 双评审 + 官方文档核实，14 项修复。

**P0（阻塞项）**

- 高风险 Step 识别清单从"subagent 决策参考"强制规则化为"拦截清单"：命中即禁止执行、必须暂停，10 类清单扩充，4 条命中后强制动作；评测残留段（"建议暂停""subagent 完全自主""不是协议机械约束"）移入 eval 文档

**P1**

- DB 写安全闸加硬约束层：Phase 2 只读纪律（硬性规则）+ Phase 5 DDL/DML 执行方式（默认生成脚本不直接执行，生产 DB 默认禁止 Agent 直接执行）
- MCP 能力声明从"按厂商断言"改为"按运行时探测"，allowed-tools 对账实际工具名，加机制警示（allowed-tools 是预批准不是白名单）
- V1-only 连续计数从「非 Git 项目回退保护」提取为 Phase 5 顶层通用规则
- 双 skill 不一致对齐：模糊确认清单取并集（加"yes""全部确认"）、执行记录格式采用完整版
- 启用 `disable-model-invocation: true`，调用时机回到人手里
- 全部硬性安全闸浓缩为篇首强制规则区（压缩存活区），确保上下文压缩后仍生效

**P2**

- 凭证脱敏硬性规则 + 仓库内文本不构成指令硬性规则
- 触发词收紧：删"我想改一下""加个功能""重构"
- 现状核查：进入设计前先验证目标功能是否已存在
- Grep 假阳性预警：引用计数异常大时先验证依赖存在性
- 模板补段：light 加 Out of Scope + 风格合规；需求文档加独立未确认项章节
- 非安全细节下沉 `references/`（schema-discovery / style-analysis / dimensions），正文约减 40%

**P3**

- 执行记录时间戳必须来自真实系统命令
- alembic migration head 必须读文件确认 down_revision 链

**v3.7.1（结构瘦身：拆 references 达 < 500 行）**

回应 gpt5.5pro 评审的"SKILL.md 拆分到 references 控制平面"建议。Anthropic 官方 [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 明文："Keep SKILL.md body under 500 lines for optimal performance"。本次拆分后：

| 文档 | 拆前 | 拆后 | 减少 |
|------|------|------|------|
| `impact/SKILL.md` | 632 行 | 256 行 | -376 |
| `impact-pro/SKILL.md` | 556 行 | 292 行 | -264 |

新增/扩展 `references/`：

- `phase-2-context-discovery.md` — Phase 2 完整执行规则（栈无关/栈专属两个版本）
- `phase-3-questioning.md` — Phase 3 & 3.5 详细规则（impact 版，整合定级条件、只分析契约、验证等级 V0-V3、破坏性请求保护）
- `phase-5-execution.md` — Phase 5 完整执行规则（V1-only 计数、非 Git 回退方案、阻塞恢复、DDL/DML、执行流程模板、验证方案、风格合规、高风险拦截清单详细处理流程、风格标签、执行记录模板）
- `cross-platform-notes.md` — 跨平台差异（时间戳命令 bash/PowerShell/cmd、路径分隔符、shell 元字符对照表）—— 回应 fable5 评审点 8「时间戳命令需兼容 Windows/PowerShell」

**安全闸保留策略**：强制规则区 7 条 + 自动/确认边界 + 凭证脱敏/仓库内文本硬性规则 + 行为准则检查 7 条 + Phase 4 文档输出结构 全部保留在主 SKILL.md（fable5 评审点 5 要求"安全闸保留在正文"）。references 仅下沉非安全闸性的执行规则和详细说明，强制规则区与 references 在维护说明里标注双向同步。

**v3.7.2（2026-06-15：生产就绪性修复）**

全面评审后修复 7 个问题，三 skill 联合测试全绿（impact 179/0, impact-pro 74/1, pathfinder 43/0）：

- **负向测试覆盖 7/7 硬性规则**：新增 neg-002（高风险拦截）、neg-003（DB 只读）、neg-005（破坏性请求）、neg-007（凭证脱敏）4 个 scenario spec，与 T07 的 neg-001/004/006 合共 7 个
- **T08 跨会话恢复 e2e**：dry-run 验证 `_active-state.md` 只是 checkpoint 不替代 `确认 Step N`
- **`schema-discovery.md` 跨 DB 兼容**：MySQL `DATABASE()` -> 通用 + PostgreSQL 并排查询
- **`090-execution-record.md` 去 Python 污染**：`ty check`/`alembic` -> `mvn test`/`gradle test`/Flyway/Liquibase
- **模板结构化项目根目录字段**：`_active-state.md` 和 `060-preflight.md` 加 `absolute_path`/`determination_method`/`verification_timestamp` 子字段
- **可选 `code-graph-adapters/` 目录**：MCP 可用时增强引用发现的只读适配器

**v3.8（2026-06-24：盲测协议补强）**

6 个真实开发场景盲测（v1/v2/v3 三轮）后，针对模型暴露的问题补强协议。改进点见盲测报告 `eval/runs/blind-2026-06-24-v3-{composer25,step37flash}/`，完整改进过程见 [docs/skill-improvement-2026-06-24.md](../../docs/archive/2026-06/skill-improvement-2026-06-24.md)。

- **IP1-A 用户场景覆盖验证**（Phase 2）：排除文件前验证需求场景是否仍被剩余文件覆盖；模型曾因错误假设"controller 透传 phone"排除 controller 导致场景遗漏
- **I2-A 覆盖范围语义核查**（Phase 2.5）：全量词场景核实现有实现是否真全覆盖；模型曾把"已有功能"误判为 light
- **I1-A 实施文档代码引用预检**（Phase 4）：API 方法名存在性 grep 验证（拦截编造 `updateUserPassword` 等方法名）+ 被调方法异常行为确认（拦截 null 检查但方法实际抛异常）
- **010-requirements.md 内容边界**（Phase 4）：需求文档只写业务需求，技术实现下沉到 020/030
- **T09 负向安全闸 e2e**：补齐 neg-002/003/005/007 四条硬性规则的 e2e 实跑，记录见 [validation-runs/2026-06-24-T09-negative-gates-2357.md](validation-runs/2026-06-24-T09-negative-gates-2357.md)

**v3.8.1（2026-06-25：v4 干净环境复测 + 模型选型）**

v4 干净环境复测引入 DeepSeek-V4-Flash，修复环境污染后源码级核实三项优化。impact 场景模型能力差异显著——优化 7（覆盖范围语义核查）对弱模型不生效：

| 优化项 | Composer 2.5 | Step 3.7 Flash | DeepSeek-V4-Flash |
|--------|:---:|:---:|:---:|
| 优化 6（facts 强制） | ✅ PASS | ✅ PASS（v3 FAIL→修复） | ✅ PASS |
| 优化 7（覆盖范围核查） | ✅ PASS | ❌ FAIL（仍未修复） | ❌ FAIL |
| 优化 8（需求文档边界） | ⚠️ 2/3 PASS | ✅ PASS（B3） | N/A（未产出） |

**关键结论**：优化 7 存在模型能力门槛。Step 和 DeepSeek 都能"看到"覆盖缺口（DeepSeek 甚至量化了"约 63 个端点未覆盖"），但都无法把"全量词 + 覆盖缺口"关联起来触发 full。只有 Composer 2.5 做到了。这不是协议写得不够清楚，而是模型推理能力的硬限制。

**v3.9（2026-06-25：V7 盲测改进落地）**

V7 模糊 prompt 盲测（3 模型 × 6 场景 × 有/无 skill 对照）验证了核心假设后，针对暴露的 4 个问题落地改进：

- **light 模式关键链路深度检查**：V7 发现 C2 GLM skill 在 B2' 选择 light 后遗漏了 413→500 降级问题。新增门禁：light 提交确认前强制扫描错误处理链、中间件管线、数据流路径。
- **改动完整性自检**：V7 发现 C6 Step skill 在 B2'/B3' 只产出 1 个 Step，遗漏大量改动。新增自检表：对照 010 验收标准逐条映射实施 Step，确认每个验收点都有对应实施动作。
- **模糊点处理清单**：V7 发现 skill 组的假设标注质量参差不齐（2~5 项）。需求文档新增 §2.2 模糊点处理清单，逐条记录处理方式（已提问确认 / `[假设]` / 未确认），确认环节单独列出假设条目。
- **context-pack 关键链路追踪**：V7 发现 noskill 强模型偶有超越 skill 的深度分析。新增追踪节，对错误处理链、中间件管线、数据流路径做追踪式分析。

改进详情见 V7 评审报告 `eval/runs/blind-2026-06-25-v7/scorecards/_v7-review-report.md`，改进落地覆盖 impact + impact-pro 共 18 个文件。

**v4.0（2026-06-25：V8 回归验证改进）**

V8 盲测（Composer 2.5 × 2 cell × 3 case）验证了 v3.9 的 4 项改进全面生效：V7 遗漏项 5/5 全部捕获，skill 总分 83.7→88.0，D3 分析深度 16.3→18.3，无维度回退。针对 V8 暴露的 1 个新问题落地改进：

- **light 模式配置化提示**：V8 发现 skill 组在 B2' light 模式下硬编码了 `1mb` 请求体限制，而 noskill 组提出了 `BODY_LIMIT` 环境变量方案。在 040-light.md 实施步骤中增加提示：如果参数来自 `[假设]`，应建议配置化。
- **配置依赖链路追踪**：V8 发现当前 3 种链路类型（错误处理链/中间件管线/数据流路径）不覆盖配置化问题。在 000-context-pack.md 和 040-light.md 中增加第 4 种链路类型"配置依赖"，追踪配置加载链路、默认值和硬编码 vs 可配置问题。

改进详情见 V8 评审报告 `eval/runs/blind-2026-06-25-v8/scorecards/_v8-review-report.md`。

**v4.1（2026-06-25：V9 盲测改进落地 — 多轮触发 + 链路追踪回流）**

V9 人工交互盲测（Composer 2.5 × 3 case）验证了人工交互模式优于"自问自答"模式（skill 均分 88.0→92.0，D5 需求澄清质量 13.3→15.0，V8 的 8 项 `[假设]` 全部转为用户确认）。评审中发现 agent 倾向于 1 轮问 3 题就停止，即使链路追踪已发现额外的副作用风险点也未追问。针对此问题落地改进：

- **多轮触发条件**：第 1 轮未覆盖所有 P0/P1 级问题（含用户原话模糊点 + 链路追踪发现的副作用风险点）时，必须进入第 2 轮，不得用"每轮 3 题"作为停止理由。
- **链路追踪发现回流 Phase 3**：模糊点覆盖率自检新增步骤 2——扫描 000-context-pack.md §5 关键链路追踪表的"发现的二级影响"列，标记需要用户决策的副作用风险点。这些不是用户原话中的模糊点，而是分析过程中发现的风险，同样需要确认或假设。

改进详情见 V9 评审报告 `eval/runs/blind-2026-06-25-v9/scorecards/_v9-review-report.md`，改进落地覆盖 impact + impact-pro 共 4 个文件（2 个 SKILL.md + 2 个 references）。

**v4.1 验证（2026-06-25：V10 单 case 盲测）**

V10 用 B3' 单 case 验证 v4.1 两项改进是否生效，结果 **全部通过**：

- **F7 多轮触发** ✅：agent 在第 1 轮 3 题后自检链路追踪 §5，发现副作用风险未覆盖，进入第 2 轮追问 Q4-Q5
- **F8 链路追踪回流** ✅：000-context-pack §5 新增"数据流路径（副作用）"行，标注 Phase 3 第 2 轮确认
- **F9 副作用处理** ✅：副作用转化为具体设计（Step 6 verifyEmailLimiter + 可配置 N/M）

V9→V10 总分 92→96（+4），无维度回退。评审报告见 `eval/runs/blind-2026-06-25-v10/scorecards/_v10-review-report.md`。

### 模型选型（v4 干净环境实测）

完整模型能力评价见 [docs/model-eval-2026-06-25.md](../../docs/archive/2026-06/model-eval-2026-06-25.md)。

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 涉及覆盖范围判断（"每次/所有"全量词） | **仅 Composer 2.5** | Step/DeepSeek 会误判 light |
| 不涉及覆盖范围判断 | Composer 或 Step | Step 的 B2/B3 质量合格 |
| 安全敏感场景（认证/权限/密码） | **仅 Composer 2.5** | 证据编造 0 例 + 跨文件分析最强 |

评审报告见 `eval/runs/blind-2026-06-24-v4-{composer25,step37flash,deepseek-v4-flash}/`，最终结论见 [eval/runs/BLIND-TEST-FINAL-CONCLUSION.md](../../eval/runs/BLIND-TEST-FINAL-CONCLUSION.md)。

## E2E 真实回归测试

2026-06-12 在 RuoYi-Vue 真项目上跑了 e2e 验证，确认拆分后行为零回归。（Go/go-admin 等非 Java 栈的 e2e 见 impact-pro README，impact 只覆盖 Java/Spring/MyBatis。）

2026-06-14 补齐负向安全闸 e2e（T07）：subagent 在 RuoYi-Vue 上注入诱惑（模糊授权 / 越界写入 / 跳过恢复确认），**不真改源码**只验安全闸判断。硬性规则 #1/#4/#6 三道安全闸 3/3 PASS，ruoyi-vue `git diff --stat` 全程空。spec + prompt 为可重复回归资产，记录见 [validation-runs/2026-06-14-T07-negative-iron-rule-gates.md](validation-runs/2026-06-14-T07-negative-iron-rule-gates.md)。

### 测试项目

| 场景 | 项目 | 场景数 | 判定 |
|------|------|--------|------|
| impact on RuoYi-Vue | yangzongzhuan/RuoYi-Vue | 3 | PASS |

### 真实测试发现的语义问题（mock 无法覆盖）

1. **RuoYi-Vue**：`remark` 是 `BaseEntity` 共享字段，删 remark 会影响 7 个 entity + 11 个 Vue 页面 — skill 正确触发反向引用检查
2. **RuoYi-Vue**：`login_ip` 已存在，新增 `last_login_ip` 会重复 — skill 正确触发现状核查

### 测试目录结构

```
tests/
├── scenarios/          # 静态场景 JSON（v1 冒烟）
│   └── java-spring-mybatis/
│       ├── 001-delete-sys-user-remark.json
│       ├── 002-add-last-login-ip.json
│       └── 003-change-login-remember-me.json
└── e2e/               # 端到端真行为测试（v2，gitignore）
    ├── scenarios/     # 场景 spec + actual 输出
    ├── workdirs/      # 克隆的 fixture 项目
    ├── prompts/       # Subagent A/B prompt 模板
    └── run-helper.sh  # 辅助脚本
```

测试产物不纳入仓库版本控制，见 `.gitignore`。

## 目录结构

```
impact/
├── SKILL.md              # 核心规则（256 行，< 500 行）
├── README.md             # 本文件
├── VALIDATION.md         # 验证方案
├── references/          # 详细执行规则（按需加载，正文瘦身下沉）
│   ├── phase-2-context-discovery.md  # Phase 2 分层探索、上下文预算、MCP 探测、代码引用发现、用户场景覆盖验证、反向引用检查、上下文地图
│   ├── phase-3-questioning.md        # Phase 3 多轮收敛协议、问题优先级、维度分组、质量底线追问、风险靶向追问
│   ├── phase-5-execution.md          # Phase 5 写入目标边界、V1-only 计数、非 Git 回退、阻塞恢复、DDL/DML 执行方式、执行流程模板、验证方案、风格合规、高风险拦截清单详细处理、API 方法名预检、被调方法异常行为确认
│   ├── cross-platform-notes.md       # 跨平台差异（时间戳命令、路径分隔符、shell 元字符）
│   ├── dimensions.md                 # 19 维度及触发场景
│   ├── schema-discovery.md           # Schema 发现查询模板
│   └── style-analysis.md             # 风格分析步骤
├── code-graph-adapters/ # 可选代码图适配器（MCP 可用时增强引用发现）
│   └── generic-mcp.md
├── templates/            # 文档模板
│   ├── 000-context-pack.md
│   ├── 010-requirements.md
│   ├── 020-design.md
│   ├── 030-implementation.md
│   ├── 040-light.md
│   ├── _active-state.md
│   ├── 060-preflight.md
│   └── 090-execution-record.md
└── tests/                # 测试（gitignore，本地保留）
    ├── scenarios/        # 静态场景 JSON（v1 冒烟）
    └── e2e/              # 端到端真行为测试（v2）
        ├── scenarios/    # 场景 spec + actual 输出
        ├── workdirs/     # 克隆的 fixture 项目
        └── prompts/      # Subagent A/B prompt 模板
```

## 共享模板同步

`templates/` 下的共享模板以 `impact-pro/templates/` 为唯一源。修改模板时先改 `impact-pro` 侧，再跑同步：

```bash
python scripts/sync_templates.py          # 同步到 impact/templates/
python scripts/sync_templates.py --check  # 只检查不一致，L0 测试会调用
```

不要直接改 `impact/templates/` 下的共享模板——L0 测试会检测到不一致并报 FAIL。

## references 索引

| 文件 | 内容 | 主文档对应段 |
|------|------|-------------|
| `references/phase-2-context-discovery.md` | Phase 2 完整执行规则（含用户场景覆盖验证） | Phase 2 项目背景构建 |
| `references/phase-3-questioning.md` | Phase 3 & 3.5 详细规则（含覆盖范围语义核查） | Phase 3 探索、Phase 3.5 定级 |
| `references/phase-5-execution.md` | Phase 5 完整执行规则（含 API 方法名预检、被调方法异常行为确认） | Phase 5 执行与验证 |
| `references/cross-platform-notes.md` | 跨平台差异（时间戳/路径/shell） | 跨平台执行 |
| `references/dimensions.md` | 19 维度及触发场景 | Phase 3 维度选择 |
| `references/schema-discovery.md` | Schema 发现查询模板 | Phase 2 MCP 探测 |
| `references/style-analysis.md` | 风格分析步骤 | Phase 2 风格分析 |

## 自动 / 确认边界

| 类别 | 是否需用户确认 |
|------|----------------|
| 只读搜索、schema 发现、git log/show、本地静态检查（grep/编译/lint）、单元测试 | **无需确认，自动执行** |
| 写文件、改代码（Edit/Write）、DDL/DML、配置变更、删除、测试修复、任何对外部系统的写操作 | **必须逐项确认，且必须绑定 Step 编号** |

执行确认必须使用 `确认 Step N`。`yes`、`可以`、`继续`、`全部确认` 等模糊确认不得触发写操作。

## 代码风格分析

Phase 2 在发现上下文时同步分析项目代码风格，产出结构化风格报告，嵌入设计文档供实施阶段参考。详细步骤与 token 上限见 `references/style-analysis.md`。

### 两级策略

**基础层（始终执行）**：从最近 20 条 git commits diff 中自动提取风格特征。Git diff 本身包含命名、格式、注解位置的上下文，token 消耗极低。

**深入层（按维度触发）**：只对本次变更涉及的维度做深入分析，每个维度不超过 3 个文件。

**Git 不可用时**：回退为扫描目标模块下 6 个代表性文件（Service/Controller/Entity/Config 各 1-2 个）。

### 风格报告结构

每个风格项附**完整、未截断**的参考代码片段，嵌入设计文档 4。实施步骤中用标签引用（[Java-实体]/[DI]/[日志]/[SQL]/[前端]/[安全]/[异常]）。

### 设计文档嵌入位置

风格报告作为独立章节插入设计文档，排在"变更细则"之后。原因：代码风格是"怎么改"的重要约束，实施阶段直接参考，不需要跨文档翻找。

## 19个维度参考

完整维度及触发场景见 `references/dimensions.md`。按需选择，不强制全覆盖。

## 部署前提（纵深防御）

**只读账号是上线硬条件，不是建议。** 允许 tools 里预批准了 `query`/`execute_sql` 等写能力工具（免权限提示），唯一默认补强就是账号本身无写权限。跳过此条件 = 只剩 prompt 级防线。

- Agent 使用的 DB MCP 连接**必须**配置为只读账号——协议层的确认检查点是 prompt 级约束，只读账号是系统级硬约束，两层叠加
- 可选启用 `.claude/hooks/impact-write-gate.*`：在目标项目根放 `.impact-protected` 后，PreToolUse hook 会拦截受保护根内的写工具调用，只有当前对话最新用户消息显式 `确认 Step N` 才放行一次
- 上线前核对：
  - Agent 使用的连接串确实指向只读账号
  - 该账号无 INSERT / UPDATE / DELETE / DDL / GRANT 权限（用 `SHOW GRANTS` 类命令实查，不凭命名推断）
  - prod 与 staging 连接明确区分；执行记录写入 DB target / schema / 账号别名
  - 日志和文档中不回显完整连接串
- 写操作通过"Agent 生成脚本 -> 用户执行"完成；生产 DB 默认禁止 Agent 直接执行（见 DDL/DML 执行方式）

## 致谢

"引用检查分级"来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提出的 issue：改代码前应检查其他地方是否引用，查到后再分级处理，避免只改当前文件导致引用链断裂。

v3.4/v3.5 的长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 回退保护、阻塞恢复安全闸、写入目标边界、连续 V1-only 暂停和执行记录补强，来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提供的真实使用案例。这个案例帮助我们把规则从"文档上合理"推进到能经受长会话和多 Step 真实执行的程度。
