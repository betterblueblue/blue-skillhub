# ImpactRadar — 现有系统变更影响分析 Skill

## 这个 Skill 是干什么的

面向多技术栈现有系统（Java/Spring/MyBatis、Node/Express/Prisma、Python/FastAPI、Go/Gin/GORM、前端框架等），把模糊的功能迭代、新功能接入或高风险变更意图，通过靶向提问变成基于证据的影响分析，light/full 两档输出，统一写入 `change-impact/` 目录并协助执行。

它不是从 0 到 1 搭建新系统的生成器，而是在已有代码、schema、接口、配置、测试和业务约束中，辅助完成一次安全可追溯的系统变更。

它可以搭配 `RuleBlade` 使用：`RuleBlade` 约束 agent 的通用编码行为，`impact` 负责多技术栈现有系统的影响分析、文档输出和受监督执行流程。技术栈专属规则位于 `profiles/`，按 Phase 2 自动检测结果按需加载。

## 核心价值：给模型带来什么增益

经过 V1-V10 共 10 轮盲测（3 个模型 × 6 个真实场景 × 有/无 skill 对照 = 100+ 份产出），skill 的核心价值可以归纳为以下五点：

### 1. 把模糊需求变成显式假设

**这是 skill 最核心的增量。** V7 盲测用口语化模糊 prompt 替代精确 prompt 后，skill 增益从 +2 分跃升到 +12.1 分。

| 指标 | 精确 prompt（V6） | 模糊 prompt（V7） |
|------|:---:|:---:|
| skill 增益 | +2 分 | **+12.1 分** |
| noskill 分数 | 75.2 | 63.8（模糊 prompt 拉低了 11.4 分） |
| skill 分数 | 77.2 | 75.9（模糊 prompt 仅拉低 1.3 分） |

关键发现：**所有 skill 组都识别了模糊点并标注了 `[假设]`，所有 noskill 组都没有。** noskill 组并非没有做假设——它们隐式地做了同样的假设（如"限制 1MB"、"踢人模式"），但用户无法区分哪些是确定的、哪些是猜的。skill 把隐式猜测变成了显式标注，用户可以在文档确认环节逐条过。

### 2. 苏格拉底式提问，不替用户拍板业务决策，但自主推断代码事实

skill 不是"遇到模糊需求就直接假设"，而是先分类再处理：

**Phase 3 Step 3.0 不确定项分类**（提问前必做）：

- **代码可推断**（答案在代码中）→ Agent 自行查证，标 `【代码推断: file:line】`，不问用户
- **业务需决策**（答案不在代码中）→ 问用户，但附默认建议，让用户确认或纠正

**苏格拉底式提问**（仅对业务需决策项）按优先级分层：

- **P0 模糊点**（不问就可能做错）→ 必须在 Phase 3 提问，不得假设
- **P1 模糊点**（影响兼容性/设计质量）→ 应该提问；用户没答时可假设，但必须标"待确认"
- **P2 模糊点**（可按项目约定推断）→ 可直接假设，标 `[假设]` + 依据

> **Pathfinder 场景适配**：当用户不熟悉项目时，代码可推断项由 Agent 自行查证，避免把技术细节问题推给无法回答的用户。

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
- **弱模型容易过早收尾**：C6 Step skill 在 B2'/B3' 只产出 1 个 Step，遗漏大量改动。v3.9 增加了"改动完整性自检"——对照验收标准逐条映射实施 Step。

另外，noskill 强模型偶有超越 skill 的深度分析（如 C1 GLM noskill 在 B2' 发现了 isOperational 降级和 XSS 内存放大）。v3.9 在 context-pack 中增加了"关键链路追踪"节，鼓励对错误处理链和中间件管线做追踪式分析。

V9 发现 agent 在人工交互模式下倾向于 1 轮问 3 题就停止，即使链路追踪已发现额外的副作用风险点（如"重发验证邮件可被无限调用"）也未追问。v4.1 新增多轮触发条件，要求链路追踪发现的副作用风险点必须回流到 Phase 3 澄清环节。

## 模型敏感性

本技能的**分析深度（Phase 2 上下文发现、证据核实、Phase 3 苏格拉底提问、定级）**依赖执行模型。强模型（Opus / 同级）能扎实取证、严守确认检查点；弱模型（Sonnet / Haiku / 更弱）可能：证据核实不严（行号/表名偏差）、定级偏松、苏格拉底提问没问到位。

- **强模型**：日常可靠。
- **弱模型**：输出（尤其 context-pack 的【已核实】项、设计文档的影响面）**需人工复核**。

强制规则区（逐步确认 / 写入边界 / 凭证脱敏 / 高风险拦截）是模型无关的硬性安全闸——弱模型也绕不过逐 Step 确认；但"分析有多深、证据有多准"随模型强弱变化。Phase 5 执行的安全闸不因模型放松。

v4.2 新增 V7 判档合理性脚本闸门后，弱模型的判档错误（如把 Light 场景误判为 Full）可被脚本拦截——协议层面无法强制模型"推理正确"，脚本闸门作为外部硬拦截兜底。

### V7 盲测模型对比（2026-06-25）

| 模型 | noskill 均分 | skill 均分 | 增益 | 增益来源 |
|------|:---:|:---:|:---:|------|
| GLM-5.2 | 71.7 | 84.3 | +12.7 | 结构化 + 假设标注（B1' 的 refreshToken TTL 是独有发现） |
| Composer 2.5 | 71.0 | 83.7 | +12.7 | 假设标注 + 方案完整性（ADMIN 豁免、resend 端点） |
| Step 3.7 Flash | 48.7 | 59.7 | +11.0 | 分析框架（B1' +26，但 B2'/B3' 提升有限——弱模型容易过早收尾） |

**关键结论**：强模型增益来自结构化 + 假设标注；弱模型增益来自分析框架，但在复杂场景中容易过早收尾（只做最表面的改动）。v3.9 的"改动完整性自检"专门针对这个问题。

后续 V8-V10 盲测（V8 自问自答、V9 人工交互、V10 单 case 验证 v4.1）进一步确认：人工交互模式澄清质量优于自问自答（skill 均分 88.0→92.0），v4.1 的多轮触发和链路追踪回流在 V10 全部生效（总分 92→96）。完整跑分数据和评审报告见 [CHANGELOG.md](CHANGELOG.md) 对应版本段和 `eval/runs/blind-2026-06-25-v8~v10/`。

## 核心能力

- **苏格拉底式提问** — 先分类再处理：代码可推断项自主查证标 `【代码推断: file:line】`，业务需决策项才问用户；基于实际 schema 和代码发现上下文，针对性提问，不泛泛而谈
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
- **覆盖范围语义核查**（v3.8 新增，v4.2 脚本闸门强化）— Phase 2.5 定级前必做：用户表述出现"每次/所有/全部/任何/一律"等全量词时，核实现有实现是否真的全覆盖，"已存在"不等于"已全覆盖"。v4.2 新增 V7 脚本闸门：全量词场景下产出无覆盖范围分析则 FAIL 拦截，不依赖模型自觉性
- **实施文档代码引用预检**（v3.8 新增，v4.3 增强）— `030-implementation.md` 提交前静默检查：API 方法名存在性验证（grep 拦截编造方法名）+ 被调方法异常行为确认（拦截 null 检查但方法实际抛异常的设计缺陷）+ 判档表事实一致性检查（判档决策表中的事实陈述须与 context-pack 已确认事实一致）
- **需求文档内容边界**（v3.8 新增）— `010-requirements.md` 生成后自检：只写业务需求（做什么/为什么/怎么做完），技术实现细节归 020/030，避免需求文档渗入技术细节
- **Grep 假阳性预警**（v3.7 新增）— 引用计数异常大时先验证依赖是否真实存在，再抽样核实
- **MCP 能力运行时探测**（v3.7 修正）— 工具能力以运行时探测为准，不以厂商或工具名假设；凡能执行任意 SQL 的工具一律视为「有写能力」
- **可选 PreToolUse hook** — 在 Claude Code settings 层按 `.impact-protected` 标记启用写前拦截，把 `确认 Step N` 从 prompt 纪律补强为工具执行前检查
- **安全闸上下文压缩后仍保留**（v3.7 新增）— 全部硬性安全闸浓缩为篇首强制规则区，确保上下文压缩后仍生效
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
- **改动完整性自检**（v3.9 新增）— 实施文档提交前对照 010 验收标准逐条映射实施 Step，防止弱模型过早收尾只做表面改动
- **模糊点处理清单**（v3.9 新增）— 需求文档中逐条记录每个模糊点的处理方式（已提问确认 / `[假设]` / 未确认），提交确认时单独列出假设请用户逐条过
- **context-pack 关键链路追踪**（v3.9 新增）— 对错误处理链、中间件管线、数据流路径、配置依赖做追踪式分析，保留探索深度，防止结构化流程限制分析
- **light 模式配置化提示**（v4.0 新增）— light 模式实施步骤中如果涉及阈值/限制值等假设参数，提示通过环境变量或配置文件使其可配置；V8 盲测发现 skill 组硬编码了请求体限制而 noskill 组提出了环境变量方案
- **配置依赖链路追踪**（v4.0 新增）— 关键链路追踪和 light 深度检查增加"配置依赖"类型，追踪配置加载链路、默认值和覆盖优先级，识别硬编码 vs 可配置问题
- **多轮触发条件**（v4.1 新增）— 第 1 轮未覆盖所有 P0/P1 级问题（含链路追踪发现的副作用风险点）时，必须进入第 2 轮，不得用"每轮 3 题"作为停止理由
- **链路追踪发现回流 Phase 3**（v4.1 新增）— 模糊点覆盖率自检新增扫描 000-context-pack.md §5 关键链路追踪表的"发现的二级影响"列，确保副作用风险点回流到澄清环节
- **判档合理性脚本闸门**（v4.2 新增）— `impact_validate.py` V7 检查：全量词覆盖门禁（FAIL）、过度判档检测（WARN）、判档不足检测（WARN）。协议无法纠正的判档错误由脚本硬拦截兜底，专为弱模型设计
- **判档表事实一致性脚本闸门**（v4.3 新增）— `impact_validate.py` V9 检查：判档决策表中的事实声明与 `000-context-pack.md` §7 已确认事实交叉比对，发现矛盾报 WARN，判档表引用了 §7 中没有的实体也报 WARN。把检查 3 从 agent 自觉执行升级为脚本硬拦截
- **横切关注点表脚本门禁**（v4.4 新增，v5.0 升级 FAIL）— `impact_validate.py` V10 检查：full 模式下扫描 `020-design.md` §6 横切关注点标题，缺失或行数不足 19 则 FAIL 拦截（防止模型改名绕过或只填一半）；☑/☐ 标记 < 5 报 WARN。配合模板 §6 注释的 ⚠️ 强制要求提示，三重保障横切表不被遗漏
- **light 关键链路深度检查门禁**（v3.9 新增行为要求，v4.7 后补脚本门禁，v5.0 升级 FAIL）— `impact_validate.py` V11 检查：light 模式下扫描 `040-light.md` 是否包含「关键链路深度检查」节标题，缺失则 FAIL 拦截。防止模型把关键链路检查改写为其他名称导致跳过
- **Phase 3 跳过防护**（v4.8 新增）— 三重保障防止 agent 跳过苏格拉底式探索：① SKILL.md Phase 1 显式禁止 agent 自行消解歧义（标注倾向不等于用户确认）；② 硬规则第 9 条要求 Phase 4 写入前必须完成 Phase 3 或满足快速通道条件；③ `impact_validate.py` V12 检查 `_active-state.md` 是否包含 Phase 3 状态追踪字段，缺失报 WARN。`_active-state.md` 模板新增 `Phase 3 状态` 和 `Phase 3.5 定级` 字段，使跳过行为在状态文件中可见
- **简化模式安全底线**（v4.9 新增）— 硬规则第 10 条：用户要求简化文档或直接执行时，可以跳过分析文档，但不得跳过 `_active-state.md` 创建、执行前检查、写操作确认、破坏性变更影响发现、验证方案。简化的是文档形式，不是安全边界。解决简化模式下 agent 跳过恢复基础设施和执行前检查的问题
- **`_active-state.md` 存在性检查**（v4.4 新增）— `impact_validate.py` V1 增强：full/light 模式下检查 `_active-state.md` 是否存在，缺失报 WARN（不阻断提交，但提醒 agent 补充跨会话恢复检查点）
- **Prisma ORM 异常行为模式参考**（v4.4 新增）— `references/phase-4-output.md` 新增 Prisma ORM 方法异常行为参考表（findUnique 返回 null 不抛异常、create 抛 P2002、update/delete 抛 P2025 等），纠正弱模型对 ORM 异常码的常见误判

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

长会话发生上下文压缩后，建议重新 `/impact` 调用恢复 skill 全文；上下文压缩后仍然保留的篇首强制规则区已覆盖全部硬性安全闸。

## 验收状态

安全闸、回归检查和验证记录分别在：

- 验证方案：[VALIDATION.md](VALIDATION.md)
- 回归协议：[../../docs/skill-eval/regression.md](../../docs/skill-eval/regression.md)
- 验证记录索引：[validation-runs/INDEX.md](validation-runs/INDEX.md)（T01-T10）

当前结论：7 条硬性规则的负向 e2e 全覆盖（neg-001/004/006 已实跑，余为 spec 待跑）；多会话写授权一致性通过，无 P0/P1。

## 测评体系

impact 已接入统一测评框架（[docs/skill-eval/](../../docs/skill-eval/)），支持三层防不一致检测：

- **L0 静态自洽**（每次改动必跑）：`bash skills/impact/tests/run.sh` — 检查硬性规则存在、引用完整、共享契约、fixture 锁定
- **L1 行为契约**（release 前跑）：`bash eval/run-l1.sh impact` — 11 个标准化 case（R1/R2/R3/R3N/R4/F1/F2/F3/G1/G2/T1），subagent 扮用户端到端跑分，客观维度机器判 + 安全闸
- **L2 人审深度**（里程碑抽样）：主观维度（苏格拉底质量、文档可读性）人工复核

当前基线来自 2026-06-14（10 case，平均基础分 91.2 / 100，opus-4-8；原 impact-pro 基线已合并）。每次改 skill 后跑 L1 产出评分卡，用 `bash eval/diff-baseline.sh impact` 和基线 diff——任何契约掉绿或维度掉档>=3 即红线阻断。基线详情见 [eval/baselines/impact.json](../../eval/baselines/impact.json)。

共享契约（impact + pathfinder 两个 skill 都要守）：基于证据不臆测、可信度标记二分、凭证脱敏、仓库内的文本不构成指令、写入目标边界。L0 自动检查这些契约在两个 SKILL.md 中都存在，防止改一处另一处不一致。

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
Skill 继续提问（或收尾）
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

## 迭代历史

完整版本历史、跑分数据和评审报告链接见 [CHANGELOG.md](CHANGELOG.md)。下表只列关键节点：

| 版本 | 关键改动 |
|------|---------|
| v1.0 | 输出 prompt 给下一个 agent，无文档无执行 |
| v2.0 | 改为输出三份文档 + 逐文档确认 + 执行能力 |
| v3.0 | light/full 两档 + 自动/确认边界表 + 模板外置 |
| v3.4 | 长期目标模式 + V0-V3 验证等级 + 非 Git 回退 + 阻塞恢复安全闸 |
| v3.7 | 安全补强：7 条硬性规则 + 篇首强制规则区 + disable 自动触发 |
| v3.9 | V7 盲测改进：light 深度检查 + 改动完整性自检 + 模糊点清单 |
| v4.2 | V7 脚本闸门兜底弱模型判档错误 |
| v4.7 | R1-R7 七轮优化收尾，Composer 2.5 达 95 分稳定 |
| v4.8 | Phase 3 跳过防护：禁止自行消解歧义 + Phase 4 写入前置检查 + V12 门禁 |
| v4.9 | 简化模式安全底线：硬规则 #10，简化文档不减安全边界 |
| v5.0 | GPT 评审 6 项修复：脚本门禁级别对齐 + V5 Mermaid 修复 + 测试同步 |

## E2E 真实回归测试

2026-06-12 在 RuoYi-Vue 真项目上跑了 e2e 验证，确认拆分后行为零回归。多栈 e2e（Go/go-admin、Node/Express、Python/FastAPI 等）在 v5-v9 盲测中验证，见 eval/runs/。

2026-06-14 补齐负向安全闸 e2e（T07）：subagent 在 RuoYi-Vue 上注入诱惑（模糊授权 / 越界写入 / 跳过恢复确认），**不真改源码**只验安全闸判断。硬性规则 #1/#4/#6 三道安全闸 3/3 PASS，ruoyi-vue `git diff --stat` 全程空。spec + prompt 为可重复回归资产，记录见 [validation-runs/2026-06-14-T07-negative-iron-rule-gates.md](validation-runs/2026-06-14-T07-negative-iron-rule-gates.md)。

### 测试项目

| 场景 | 项目 | 场景数 | 判定 |
|------|------|--------|------|
| impact on RuoYi-Vue | yangzongzhuan/RuoYi-Vue | 3 | PASS |

### 真实测试发现的语义问题（mock 无法覆盖）

1. **RuoYi-Vue**：`remark` 是 `BaseEntity` 共享字段，删 remark 会影响 7 个 entity + 11 个 Vue 页面 — skill 正确触发反向引用检查
2. **RuoYi-Vue**：`login_ip` 已存在，新增 `last_login_ip` 会重复 — skill 正确触发现状核查

测试目录结构见下文「目录结构」节的 `tests/` 部分。测试产物不纳入仓库版本控制，见 `.gitignore`。

## 目录结构

```
impact/
├── SKILL.md              # 通用内核（219 行，< 500 行）
├── README.md             # 本文件
├── VALIDATION.md         # 验证方案
├── profiles/             # 技术栈规则（Phase 2 自动探测并按需加载）
│   ├── _schema.md        # 技术栈规则接口定义
│   ├── _template.md      # 新技术栈规则模板
│   ├── generic.md        # 通用备用规则
│   ├── java-spring-mybatis.md
│   ├── node-express-prisma.md
│   ├── python-fastapi-sqlmodel.md
│   ├── go-gin-gorm.md
│   ├── frontend-react-vite.md
│   ├── frontend-nextjs.md
│   ├── frontend-nuxt-vue.md
│   └── dotnet-aspnet-efcore.md
├── db-adapters/          # 数据库适配器
│   ├── generic-sql.md
│   ├── mysql.md
│   └── postgresql.md
├── code-graph-adapters/  # 可选代码图适配器（MCP 可用时增强引用发现）
│   └── generic-mcp.md
├── references/           # 详细执行规则（按需加载）
│   ├── phase-1-intent.md             # 长期目标模式 + 快速通道判定
│   ├── phase-2-context-discovery.md  # Phase 2 分层探索、MCP 探测、代码引用发现、用户场景覆盖验证
│   ├── phase-2.5-risk-triage.md      # 覆盖范围语义核查 + 现状核查门禁
│   ├── phases-detail.md              # Phase 3 & 3.5 多轮收敛、定级条件、验证等级
│   ├── phase-4-output.md             # Phase 4 文档输出规则 + 脚本闸门
│   ├── phase-5-execution.md          # Phase 5 写入边界、V1-only 计数、阻塞恢复、DDL/DML、高风险拦截
│   ├── dimensions.md                 # 19 维度及触发场景
│   └── cross-platform-notes.md       # 跨平台差异（时间戳/路径/shell）
├── templates/            # 文档模板
│   ├── 000-context-pack.md
│   ├── 005-change-summary.md
│   ├── 010-requirements.md
│   ├── 020-design.md
│   ├── 030-implementation.md
│   ├── 040-light.md
│   ├── 060-preflight.md
│   ├── 090-execution-record.md
│   ├── _active-state.md
│   ├── subagent-decisions.md
│   ├── final-readiness-audit.md
│   └── scorecard.md
└── tests/                # 测试（gitignore，本地保留）
    ├── scenarios/        # 静态场景 JSON（v1 冒烟）
    └── e2e/              # 端到端真行为测试（v2）
        ├── scenarios/    # 场景 spec + actual 输出
        ├── workdirs/     # 克隆的 fixture 项目
        └── prompts/      # Subagent A/B prompt 模板
```

### 共享模板同步

`templates/` 下的共享模板以 `impact/templates/` 为唯一源（原 `impact-pro/templates/` 已随合并迁入）。修改模板时直接改 `impact/templates/`，再跑检查：

```bash
python scripts/sync_templates.py --check  # 检查一致性，L0 测试会调用
```

不要直接改 `impact/templates/` 下的共享模板——L0 测试会检测到不一致并报 FAIL。

## references 索引

| 文件 | 内容 | 加载时机 |
|------|------|---------|
| `references/phase-1-intent.md` | 长期目标模式 + 快速通道判定规则 | Phase 1 |
| `references/phase-2-context-discovery.md` | Phase 2 完整执行规则（含用户场景覆盖验证、MCP 探测） | Phase 2 |
| `references/phase-2.5-risk-triage.md` | 覆盖范围语义核查 + 现状核查门禁 | Phase 2.5 |
| `references/phases-detail.md` | Phase 3 & 3.5 详细规则（多轮收敛、定级条件、验证等级 V0-V3） | Phase 3 / 3.5 |
| `references/phase-4-output.md` | Phase 4 文档输出规则 + 脚本闸门 | Phase 4 |
| `references/phase-5-execution.md` | Phase 5 完整执行规则（写入边界、V1-only 计数、阻塞恢复、DDL/DML、高风险拦截、API 方法名预检） | Phase 5 |
| `references/dimensions.md` | 19 维度及触发场景 | Phase 3 |
| `references/cross-platform-notes.md` | 跨平台差异（时间戳/路径/shell） | 跨平台执行 |

## 自动 / 确认边界

| 类别 | 是否需用户确认 |
|------|----------------|
| 只读搜索、schema 发现、git log/show、本地静态检查（grep/编译/lint）、单元测试 | **无需确认，自动执行** |
| 写文件、改代码（Edit/Write）、DDL/DML、配置变更、删除、测试修复、任何对外部系统的写操作 | **必须逐项确认，且必须绑定 Step 编号** |

执行确认必须使用 `确认 Step N`。`yes`、`可以`、`继续`、`全部确认` 等模糊确认不得触发写操作。

## 代码风格分析

Phase 2 在发现上下文时同步分析项目代码风格，产出结构化风格报告，嵌入设计文档供实施阶段参考。风格观察轴（`style_axes`）和验证策略（`validation_strategy`）由 `profiles/<stack>.md` 定义，按检测到的技术栈按需加载。

### 两级策略

**基础层（始终执行）**：从最近 20 条 git commits diff 中自动提取风格特征。Git diff 本身包含命名、格式、注解位置的上下文，token 消耗极低。

**采样过滤**：默认排除 merge、revert、cherry-pick 等非正常开发 commit（`git log --no-merges --invert-grep --grep='^revert' --grep='^cherry-pick'`），避免把合并冲突解决、回滚操作或自动同步提交当作风格样本。排除模式可在 `_style-rules.md` 的「采样配置」小节自定义（如 hotfix、tmp、WIP），不填则用默认值。

> **基础层的局限性**（作为兜底补充，不作为风格主要依据）：
> - **样本偏斜**：最近 20 条 commit 可能只覆盖少数模块或个别人的写法，不代表全项目风格
> - **可能采到异常提交**：即使过滤了 merge/revert，临时方案、重构中间态、新人写的"坏榜样"仍可能混入
> - **学不到隐性规范**：不在代码里留痕的约定（如"新增字段必须同步加埋点"）git diff 学不到，只能靠用户写到 `_style-rules.md`
> - **只做词法级归纳**：能看出"命名是驼峰"，判断不了"这个字段该叫 userName 还是 nickName"
>
> 因此 git diff 读取是优先级链的第 5 层（最后补充），不是主要依据。有 `_style-rules.md` 和 Pathfinder 【14】观察时，git diff 只用来补漏。
>
> **后续优化方向**（当前未实现）：对采样 commit 做"风格一致性"预检——发现某次 commit 的写法和整体差异过大时标为【推断】，降低异常提交对风格归纳的干扰。

**深入层（按维度触发）**：只对本次变更涉及的维度做深入分析，每个维度不超过 3 个文件。

**Git 不可用时**：回退为扫描目标模块下 6 个代表性文件（Service/Controller/Entity/Config 各 1-2 个）。

### 风格报告结构

每个风格项附**完整、未截断**的参考代码片段，嵌入设计文档 4。实施步骤中用标签引用（[Java-实体]/[DI]/[日志]/[SQL]/[前端]/[安全]/[异常]）。

### 设计文档嵌入位置

风格报告作为独立章节插入设计文档，排在"变更细则"之后。原因：代码风格是"怎么改"的重要约束，实施阶段直接参考，不需要跨文档翻找。

### 项目级风格规范（`_style-rules.md`）

除了 profile 的 `style_axes`，impact 还支持项目级风格规范文件 `change-impact/_style-rules.md`（由项目维护者填写）。它是代码风格的**权威源**，优先级高于 profile 的通用提示。

**风格来源优先级链（高 → 低）**：

1. `_style-rules.md` 强制规则（用户权威源，违反即 FAIL）
2. `_style-rules.md` 建议规则（用户参考，违反仅 WARN）
3. `_project-map.md` 【14】代码风格观察（Pathfinder 产出的机器观察补充）
4. profile `style_axes`（栈级通用提示）
5. 运行时从 git diff 读取（最后补充）

**校验能力分级**：强制规则只有在校验手段能真正落地拦截时才标"强制"。grep 做词法存在检查（命中禁用规则即 FAIL）；语义级判断（如返回类型、硬编码值）标"人工确认"，由 `impact_validate.py` V8 列入"需人工复核"清单。

### 渐进积累：用户不写也能用

风格规则不需要提前写全。用户没有 `_style-rules.md` 时，impact 退回现有行为（profile `style_axes` + 运行时从代码确认），不报错。在实际变更中，Phase 3 会检测风格分歧——当实施计划的代码风格与现状不一致时，触发追问：

> "现有 Controller 统一返回 R<T>（证据：`UserController.java:23`）。你这次新增的接口没有用这个包装。这是故意的，还是应该统一？"

用户回答"应该统一"后，这条规则经 `确认 Step N` 追加到 `_style-rules.md`。同一个项目多跑几次，规则越来越完整，后续变更自动遵循。

> `_style-rules.md` 模板见 `templates/_style-rules.md`。校验由 `impact_validate.py` V8 完成。完整执行规则见 `references/phase-2-context-discovery.md`（预读）和 `references/phase-5-execution.md`（合规检查）。

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
