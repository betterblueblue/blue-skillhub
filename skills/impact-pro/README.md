# ImpactRadar Pro — 现有系统多栈变更影响分析

## 这个 Skill 是干什么的

面向已验证技术栈规则覆盖范围内的多栈现有系统，把模糊的功能迭代、新功能接入或高风险变更意图，通过靶向提问变成基于证据的影响分析；加载专属规则，未知栈先用通用规则备用扫描，按 light/full 两档输出，统一写入 `change-impact/` 目录并协助执行。

它不是从 0 到 1 搭建新系统的生成器，而是在已有代码、schema、接口、配置、测试和业务约束中，辅助完成一次安全可追溯的系统变更。新功能开发指的是接入现有系统的新功能，不是空项目脚手架。

它可以搭配 `RuleBlade` 使用：`RuleBlade` 提供通用编码行为约束，`impact-pro` 负责多栈 profile 化上下文发现、影响分析、文档产出和受监督执行流程。

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

## ⚠ 模型敏感性

本技能的**分析深度（Phase 2 技术栈检测/上下文发现、证据核实、Phase 3 苏格拉底提问、定级）**依赖执行模型。强模型（Opus / 同级）能扎实取证、严守确认门；弱模型（Sonnet / Haiku / 更弱）可能：profile 技术栈检测误判、证据核实不严（行号/表名偏差）、定级偏松。

- **强模型**：日常可靠。
- **弱模型**：产出（尤其 context-pack 的【已核实】项、profile 命中、设计文档影响面）**需人工复核**。

强制规则区（逐步确认 / 写入边界 / 凭证脱敏 / 高风险拦截）是模型无关的硬门——弱模型也绕不过逐 Step 确认;但"分析有多深、profile 命中多准、证据多扎实"随模型起伏。Level 1 profile 在弱模型下尤其需要人工补位（profile 多为单一 demo 首轮验证）。

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

V9 证明人工交互模式下澄清质量显著优于"自问自答"。但 V9 也发现 agent 倾向于固定问 3 题就停止，即使链路追踪已发现额外的副作用风险点。v4.1 已修复此问题（见迭代记录）。

## 核心能力

- **通用内核 + 技术栈规则** — 无栈假设，按需加载专属规则
- **Context Pack** — 用 L1/L2/L3 分层探索，给后续 agent 一个小而准、可解释的上下文入口
- **引用检查分级** — 改前反查调用方、引用方、注册点、生成物和测试，按必须同步修改 / 需要用户决策 / 只需验证 / 暂不纳入处理
- **可选 code graph MCP** — 存在 tree-sitter / code graph 类 MCP 时先取结构化定义、引用和调用候选；无工具或证据不足时诚实回退到 `rg/git grep`
- **长期目标模式** — 面对迁移、对齐、重构、大功能接入、债务清理等多 Step 任务，维护当前 Step、backlog、阻塞项和未验证项
- **跨系统对齐规则** — 记录可信来源、目标实现、对齐语义、差距证据和本 Step 范围，避免凭相似命名臆测
- **苏格拉底式提问** — 基于实际 schema 和代码发现上下文，按风险多轮收敛；每轮最多 3 问，不是总共最多 3 问
- **light/full 两档模式** — 简单改动走一页摘要，复杂变更走三文档
- **接口返回检查清单** — light 涉及向后兼容响应字段新增时，检查消费者、文档、generated client、验证方式和未验证项
- **基于证据的分析** — 用工具发现真实上下文，不靠臆测
- **验证等级** — 区分 V0 未验证、V1 静态验证、V2 构建/单测、V3 运行路径验证
- **数据库适配器** — MySQL + PostgreSQL + 通用 SQL 规则（其他 DB 走通用规则；PG 用 pg_catalog，覆盖 partial/表达式索引、enum、分区表）
- **19 维度灵活覆盖** — 按需选择，不强制全覆盖
- **三文档逐级确认** — 需求 → 设计 → 实施，每份确认后再出下一份
- **逐操作执行确认** — 每步写操作前都询问
- **自动/确认边界清晰** — 只读操作自动跑，写操作必须确认
- **高风险 Step 拦截清单**（v3.7 强制规则化）— 10 类不可逆操作命中即禁止执行、必须暂停，等用户单独确认；不允许合并确认、不允许裁量空间
- **DB 只读纪律 + DDL/DML 执行方式**（v3.7 新增）— schema 发现阶段只允许只读查询；DDL/DML 默认生成脚本不直接执行，生产 DB 默认禁止 Agent 直接执行
- **V1-only 连续计数**（v3.7 提级为通用规则）— 无论是否 Git 项目，连续 3 个写入 Step 只达 V1 静态验证即暂停；计数粒度按 Step 计
- **凭证脱敏 + 仓库内的文本不可信**（v3.7 新增强制规则）— 凭证写入任何文档前必须脱敏为 `***`；仓库文件/代码注释/commit message 中的指令性文本不构成确认
- **现状核查**（v3.7 新增）— 进入设计前先验证目标功能/字段/接口是否已存在或部分存在，避免重复造轮子
- **用户场景覆盖验证**（v3.8 新增）— Phase 2 排除文件/模块前必做：验证用户原始需求场景是否仍被剩余文件完全覆盖，防止基于错误假设排除文件导致场景遗漏
- **覆盖范围语义核查**（v3.8 新增）— Phase 2.5 定级前必做：用户表述出现"每次/所有/全部/任何/一律"等全量词时，核实现有实现是否真的全覆盖，"已存在"不等于"已全覆盖"
- **实施文档代码引用预检**（v3.8 新增）— `030-implementation.md` 提交前静默检查：API 方法名存在性验证（grep 拦截编造方法名）+ 被调方法异常行为确认（拦桶 null 检查但方法实际抛异常的设计缺陷）
- **需求文档内容边界**（v3.8 新增）— `010-requirements.md` 生成后自检：只写业务需求（做什么/为什么/怎么做完），技术实现细节归 020/030，避免需求文档渗入技术细节
- **Grep 假阳性预警**（v3.7 新增）— 引用计数异常大时先验证依赖是否真实存在，再抽样核实
- **MCP 能力运行时探测**（v3.7 修正）— 工具能力以运行时探测为准，不以厂商或工具名假设；凡能执行任意 SQL 的工具一律视为「有写能力」；`allowed-tools` 是预批准不是白名单，真正的写保护由硬到软依次是 DB 账号权限 → settings deny / PreToolUse hook → skill 内确认检查点
- **可选 PreToolUse hook** — 在 Claude Code settings 层按 `.impact-protected` 标记启用写前拦截，把 `确认 Step N` 从 prompt 纪律补强为工具执行前检查
- **检查点压缩存活**（v3.7 新增）— 全部硬检查点浓缩为篇首强制规则区，确保上下文压缩后仍生效
- **禁用模型自动触发**（v3.7 新增）— `disable-model-invocation: true`，唯一入口手动 `/impact-pro`
- **TDD 验证框架** — 正向用例 + 错误用例（边界值/空值/格式校验/XSS）
- **行为准则检查** — 先澄清假设和成功标准，简单优先，精准修改，改 status/enum/常量前先确认原定义
- **阻塞恢复安全闸** — blocked、上下文压缩或延迟确认后，先复核 pending Step、当前文件状态和最新授权，再决定是否执行
- **跨会话恢复状态** — Phase 4/5 自动维护 `change-impact/{需求名称}/_active-state.md`，记录 pending Step、文档确认、验证等级和未确认项；恢复时先核验磁盘状态，不能替代 `确认 Step N`
- **subagent 自治模式**（v3.6 新增，仅限 eval 脚手架）— 跑分时 subagent 模拟人类用户在沙盒里独立使用 skill，对 6 类高风险 Step 自主判断做不做。这是**测评协议**的事，不是 skill 生产协议的事；生产会话里不存在 subagent 自治，所有高风险操作走 SKILL.md 强制规则（禁止执行、必须暂停、等用户显式确认）。eval 细节见 `docs/archive/2026-06/skill-capability-eval-2026-06-10/protocol-draft-subagent-as-user.md`
- **决策矩阵模板**（v3.6 新增）— `templates/subagent-decisions.md`（RESTATE → DECIDE → RECORD 三段）
- **环境降级路径**（v3.6 新增）— `templates/030-implementation.md` 加"V3 受限时启用 X 备选"段，避免事后才发现
- **PASS/FAIL 决策依据**（v3.6 新增）— `templates/090-execution-record.md` 决策依据字段从散文升级为 6 项高风险清单显式勾选
- **light 模式关键链路深度检查**（v3.9 新增）— light 模式提交确认前强制检查错误处理链、中间件管线、数据流路径、配置依赖的兼容性；V7 盲测发现 light 遗漏 413→500 降级问题
- **改动完整性自检**（v3.9 新增）— 实施文档提交前对照 010 验收标准逐条映射实施 Step，防止弱模型"过早收敛"只做表面改动
- **模糊点处理清单**（v3.9 新增）— 需求文档中逐条记录每个模糊点的处理方式（已提问确认 / `[假设]` / 未确认），提交确认时单独列出假设请用户逐条过
- **context-pack 关键链路追踪**（v3.9 新增）— 对错误处理链、中间件管线、数据流路径、配置依赖做追踪式分析，保留探索深度，防止结构化流程限制分析
- **light 模式配置化提示**（v4.0 新增）— light 模式实施步骤中如果涉及阈值/限制值等假设参数，提示通过环境变量或配置文件使其可配置；V8 盲测发现 skill 组硬编码了请求体限制而 noskill 组提出了环境变量方案
- **配置依赖链路追踪**（v4.0 新增）— 关键链路追踪和 light 深度检查增加"配置依赖"类型，追踪配置加载链路、默认值和覆盖优先级，识别硬编码 vs 可配置问题
- **多轮触发条件**（v4.1 新增）— 第 1 轮未覆盖所有 P0/P1 级问题（含链路追踪发现的副作用风险点）时，必须进入第 2 轮，不得用"每轮 3 题"作为停止理由
- **链路追踪发现回流 Phase 3**（v4.1 新增）— 模糊点覆盖率自检新增扫描 000-context-pack.md §5 关键链路追踪表的"发现的二级影响"列，确保副作用风险点回流到澄清环节

## 技术栈覆盖

| 技术栈规则 | 等级 | 说明 |
|---------|-------|------|
| generic | — | 通用备用规则，扫描目录结构；用于未知栈首轮分析，不等同于专属规则已验证 |
| java-spring-mybatis | 2 | Java/Spring/MyBatis/RuoYi，已深度覆盖 |
| node-express-prisma | 1 | Node.js/TypeScript + Express/Fastify + Prisma，已在 prisma-examples 上首轮验证 |
| python-fastapi-sqlmodel | 1 | FastAPI + SQLModel/SQLAlchemy + Alembic，已在 full-stack-fastapi-template 后端首轮验证；T50 补 open-webui 真实项目样本池 |
| frontend-react-vite | 1 | React + Vite + TypeScript 前端，已在 full-stack-fastapi-template 前端首轮验证 |
| frontend-nextjs | 1 | Next.js App Router / Pages Router，已在 vercel/next-learn 上首轮静态验证；T50 补 cal.com 真实项目样本池 |
| frontend-nuxt-vue | 1 | Nuxt 4 + Vue 3 + Nuxt UI，已在 nuxt-ui-templates/dashboard 上首轮静态验证；T50 补 nuxt.com 真实项目样本池 |
| go-gin-gorm | 1 | Go + Gin + GORM，已在 golang-gin-realworld-example-app 上首轮验证 |
| dotnet-aspnet-efcore | 1 | ASP.NET Core + EF Core，已在 eShopOnWeb 上首轮验证 |

generic 是通用备用规则，专属规则负责真实项目里更稳定的文件发现和验证策略。T50 的真实项目样本池只降低后续复验选题成本，不等同生产级通过。新技术栈必须先用 generic 备用并保留限制说明；只有完成真实项目 full + light 验收、验证命令可执行、记录写入 `validation-runs/` 后，才能升级为 Level 1 专属规则。Level 2 需要多个真实项目积累。

## 触发方式

本 skill 已禁用模型自动触发（`disable-model-invocation: true`），唯一入口是手动 `/impact-pro`。'影响分析pro' 等描述不再自动路由进入本 skill。

在 Claude Code 终端输入 `/impact-pro` 激活。

长会话发生上下文压缩后，建议重新 `/impact-pro` 调用恢复 skill 全文；压缩后存活的篇首强制规则区已覆盖全部硬检查点。

## 与 impact 的区别

| | impact | impact-pro |
|--|------------|------------|
| 架构 | 单体 SKILL.md，Java 规则写死 | 通用内核 + 技术栈规则 |
| 栈适配 | 仅 Java/MyBatis | 通用规则 + 专属规则 |
| 扩展方式 | 修改 SKILL.md | 新增技术栈规则文件 |
| 数据库 | 仅 MySQL | MySQL + PostgreSQL + 通用 SQL |

## 验收状态

当前 `impact-pro` 已完成 T01-T50 验收，覆盖多栈静态验收、前端运行时复测、负向对话复测、生产级项目复验、Step 编号确认、执行前检查、Go RealWorld 真实写操作完成、最终复审、Claude Code + MiniMax M3 真实 `/impact-pro` 响应契约复测、多会话写授权一致性复测，以及 profile 真实项目样本池扩充。T49 验证 Node/Express 响应字段删除不会被误判为 Java 场景，也验证了无 `确认 Step N` 不会写文件；同时同步补强写入目标边界、执行记录随 Step 补齐和 V1-only 暂停规则。补齐 Level 1 技术栈规则后，Node/Express/Prisma、FastAPI/SQLModel、React/Vite、Next.js、Nuxt/Vue、Go/Gin/GORM、ASP.NET Core/EF Core、monorepo 和三类负向场景均已进入已验证覆盖范围。当前可按 **多栈常规项目可投入使用（已验证技术栈规则覆盖范围内，必须由用户确认后执行）** 使用；仍不宣称覆盖任意技术栈，也不建议无人监督生产数据库变更。

**v3.6 subagent 跑分**

[2026-06-10 eval 报告](../../docs/archive/2026-06/skill-capability-eval-2026-06-10/README.md) 跑了 9 case Phase 1-4 和 9 case Phase 5。subagent 在沙盒里自主执行，真改了 38 个文件、新增 19 个。0 P0。P0 回退跑了 3 次都一致（R3 在 Step 7 停下来，v1 一行没动）。`java-spring-mybatis` profile 在 R4 跑出来比 R1 多三处安全约束。

5 条协议改进 + 边界修正的细节见 impact README v3.6 段。

**v3.7（安全补强：双评审缺口修复）**

[2026-06-11 缺口清单](../../docs/archive/2026-06/skill-gap-list-2026-06-11.md) 经 Claude + GPT5.5pro 双评审 + 官方文档核实，14 项修复。与 impact 同步，主要改动：

- 高风险 Step 识别清单强制规则化为拦截清单；评测残留段移入 eval 文档
- DB 写检查点加硬约束层：只读纪律 + DDL/DML 执行方式
- MCP 能力运行时探测 + 机制警示（allowed-tools 是预批准不是白名单，真正的写保护层级链）
- V1-only 连续计数提级为通用规则
- 双 skill 不一致对齐（模糊确认取并集、执行记录用完整版）
- 启用 `disable-model-invocation: true`
- 全部硬检查点浓缩为篇首强制规则区
- Phase 3/3.5 非检查点流程细节下沉至 `references/phases-detail.md`，正文 678→552 行
- 凭证脱敏 + 仓库内的文本不可信强制规则
- 现状核查 + Grep 假阳性预警
- 模板补段（light 加 Out of Scope / 风格合规、需求文档加未确认项章节）
- 执行记录时间戳必须来自真实系统命令；alembic head 必须读文件确认

**v3.7.1（结构瘦身：拆 references 达 < 500 行）**

回应 gpt5.5pro 评审的"SKILL.md 拆分到 references 控制平面"建议。Anthropic 官方 [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 明文："Keep SKILL.md body under 500 lines for optimal performance"。本次拆分后：

| 文档 | 拆前 | 拆后 | 减少 |
|------|------|------|------|
| `impact-pro/SKILL.md` | 556 行 | 292 行 | -264 |
| `impact/SKILL.md`（同步） | 632 行 | 256 行 | -376 |

新增/扩展 `references/`：

- `phase-2-context-discovery.md` — Phase 2 完整执行规则（栈无关骨架 + 引用 profile/db-adapter 加载点）
- `phase-5-execution.md` — Phase 5 完整执行规则（profile/db-adapter 注入点保留，DDL/DML 段加 "栈/DB 专属形态由 db-adapters/ 补充" 提示）
- `cross-platform-notes.md` — 跨平台差异（从 impact 同步）

`phases-detail.md` 保持不动（已覆盖 Phase 3 & 3.5 详细规则）。

**安全检查点保留策略**：与 impact 一致——强制规则区 7 条 + 自动/确认边界 + 凭证脱敏/仓库内的文本强制规则 + 行为准则检查 7 条 + Phase 4 文档输出结构 + 多栈目录结构 全部保留在主 SKILL.md（fable5 评审点 5）。references 仅下沉非检查点性的执行规则和详细说明。

**v3.7.2（2026-06-15：生产就绪性修复）**

全面评审后修复 8 个问题，三 skill 联合测试全绿（impact 179/0, impact-pro 74/1, pathfinder 43/0）：

- **自动化测试场景扩充**：从 2 场景(go-gin-gorm×2)→4 场景(+ java-spring-mybatis + frontend-nextjs)，覆盖栈 1→3
- **profile 修复**：`go-gin-gorm.md` migration glob 去 `hello.go`/`main.go`；`frontend-nuxt-vue.md` DTO glob 收窄；`frontend-nextjs.md` 去测试框架依赖匹配
- **风格约束引用修正**：`phase-5-execution.md` / `030-implementation.md` 中"标签框架"→`style_axes`，指向现有定义
- **workdirs 膨胀治理**：`tests/e2e/workdirs/` 加 `.gitignore` + `README.md`，fixture 不再入 git
- **T50 真实项目样本**：为 FastAPI/Next.js/Nuxt 未生产级 profile 补 open-webui/cal.com/nuxt.com 样本

**v3.8（2026-06-24：盲测协议补强）**

6 个真实开发场景盲测（v1/v2/v3 三轮）后，针对模型暴露的问题补强协议。与 impact 同步。改进点见盲测报告 `eval/runs/blind-2026-06-24-v3-{composer25,step37flash}/`，完整改进过程见 [docs/skill-improvement-2026-06-24.md](../../docs/archive/2026-06/skill-improvement-2026-06-24.md)。

- **IP1-A 用户场景覆盖验证**（Phase 2）：排除文件前验证需求场景是否仍被剩余文件覆盖；模型曾因错误假设"controller 透传 phone"排除 controller 导致场景遗漏
- **I2-A 覆盖范围语义核查**（Phase 2.5）：全量词场景核实现有实现是否真全覆盖；模型曾把"已有功能"误判为 light
- **I1-A 实施文档代码引用预检**（Phase 4）：API 方法名存在性 grep 验证（拦截编造方法名）+ 被调方法异常行为确认（拦截 null 检查但方法实际抛异常）
- **010-requirements.md 内容边界**（Phase 4）：需求文档只写业务需求，技术实现下沉到 020/030

**v3.8.1（2026-06-25：v4 干净环境复测 + 模型选型）**

v4 干净环境复测引入 DeepSeek-V4-Flash，修复环境污染后源码级核实。impact-pro 的 B3（Prisma 项目加手机号）是三模型产出完整度差异最大的 case：

| 模型 | B3 产出 | 判档 | 质量评价 |
|------|---------|:---:|---------|
| Composer 2.5 | 8 文件（context-pack + full 三文档 + preflight + 验证脚本） | full | 完整链路，设计含方法存在性预检 |
| Step 3.7 Flash | 3 文件（010/020/030） | full | 设计文档质量高（P2002 冲突处理、代码风格报告），但缺 context-pack 和 preflight |
| DeepSeek-V4-Flash | 1 文件（混合内容的 context-pack） | light | 严重不足：需求/设计/实施混在一个文件，混入代码片段，未按协议拆分 |

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

### 模型选型（v4 干净环境实测）

完整模型能力评价见 [docs/model-eval-2026-06-25.md](../../docs/archive/2026-06/model-eval-2026-06-25.md)。

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 简单场景（单栈、维度少） | Composer 或 Step | Step 的 B3 设计文档质量合格 |
| 复杂场景（跨栈、多维度） | **仅 Composer 2.5** | DeepSeek 产出不完整；Step 缺 context-pack/preflight |
| 涉及覆盖范围判断 | **仅 Composer 2.5** | Step/DeepSeek 会误判 light（同 impact） |

评审报告见 `eval/runs/blind-2026-06-24-v4-{composer25,step37flash,deepseek-v4-flash}/`，最终结论见 [eval/runs/BLIND-TEST-FINAL-CONCLUSION.md](../../eval/runs/BLIND-TEST-FINAL-CONCLUSION.md)。

## references 索引

| 文件 | 内容 | 主文档对应段 |
|------|------|-------------|
| `references/phase-2-context-discovery.md` | Phase 2 技术栈检测 + 分层探索 + 上下文预算（含用户场景覆盖验证） | Phase 2 技术栈检测+上下文 |
| `references/phases-detail.md` | Phase 3 & 3.5 详细规则（兼容历史命名，含覆盖范围语义核查） | Phase 3 探索、Phase 3.5 定级 |
| `references/phase-5-execution.md` | Phase 5 完整执行规则（含 API 方法名预检、被调方法异常行为确认） | Phase 5 执行与验证 |
| `references/cross-platform-notes.md` | 跨平台差异（时间戳/路径/shell） | 跨平台执行 |

## E2E 真实回归测试

2026-06-12 在真 Go 项目 go-admin 上跑完完整 e2e（加头像上传接口），产出 8 份 change-impact 文档 + 6 文件代码改动，Subagent B 评审 9 维：首次 FAIL（4 代码问题 + 3 测试缺口），修复后重评审通过。

### S3 测试详情

| 维度 | 首次 | 修复后 |
|------|------|--------|
| doc_completeness | ✅ PASS | ✅ PASS |
| doc_quality | ✅ PASS | ✅ PASS |
| code_correctness | ❌ FAIL | ✅ PASS |
| code_minimality | ✅ PASS | ✅ PASS |
| iron_rules | ✅ PASS | ✅ PASS |
| compile | ⏭️ SKIP | ⏭️ SKIP |
| style_consistency | ✅ PASS | ✅ PASS |
| unit_tests | ❌ FAIL | ✅ PASS |
| performance | ⚠️ WARN | ⚠️ WARN |

### 修复项

1. Upload 签名 `interface{}` → `context.Context` + `*AvatarUploadReq`
2. `mime.ExtensionsByType` 空切片保护
3. 加 magic-byte 二次校验（`ValidateImageMagicBytes`）
4. 硬编码路径 → `config.ExtConfig.Upload.AvatarDir`
5. InsetAvatar 501 stub → 恢复原始实现（强制规则 #2）
6. BR-006 回退逻辑：缩略图生成失败 → thumbPath=origPath, 不报错
7. 清理路径测试：新建 `failStore` mock 验证 cleanup

多栈测试用例、评分标准、行为准则检查和使用边界见 [VALIDATION.md](VALIDATION.md)，优化后回归复测协议见 [../../docs/skill-eval/regression.md](../../docs/skill-eval/regression.md)，实际验收记录索引见 [validation-runs/INDEX.md](validation-runs/INDEX.md)。

## 测评框架

impact-pro 已接入统一测评框架（[docs/skill-eval/](../../docs/skill-eval/)），支持三层防不一致检测：

- **L0 静态自洽**（每次改动必跑）：`bash skills/impact-pro/tests/run.sh` — 检查强制规则存在、引用完整、共享契约、fixture 锁定
- **L1 行为契约**（release 前跑）：`bash eval/run-l1.sh impact-pro` — 6 个标准化 case（R4/G1/G2/F1/F2/F3），覆盖 Java/Go/FastAPI/React 四栈 + monorepo 双 profile，subagent 扮用户端到端跑分
- **L2 人审深度**（里程碑抽样）：主观维度人工复核，可选多模型交叉评审

当前基线来自 2026-06-14（6 case，平均基础分 93.0 / 100，opus-4-8）。红线机制同 impact——任何契约 PASS→FAIL 或维度掉档≥3 阻断发布。基线详情见 [eval/baselines/impact-pro.json](../../eval/baselines/impact-pro.json)。

共享契约、L0 自动检查与 impact 一致。

## 典型流程

```
你：我想给用户表加一个个性签名字段
↓
Phase 2：技术栈检测 → 加载对应技术栈规则 → 构建 Context Pack
↓
Phase 2.5：初步风险预判（不最终定档）
↓
Phase 3：靶向提问（字段长度？哪些接口？缓存？迁移脚本？）
↓
Phase 3.5：Agent 基于证据建议 light/full，用户复核确认
↓
Phase 4：输出文档（light 一页 / full 三文档逐份确认）
↓
Phase 5：执行（每步确认，写前检查目标路径，按证据运行验证）
```

## light / full 如何判定

定级按风险触发，不按文件数量粗暴决定。

**light** 适合：UI 文案、toast、placeholder、局部样式、单 handler 自然语言 message、前端本地状态展示、文档/日志文案等。前提是证据显示不改 DB schema、API 契约、权限/认证、状态机、generated client、外部服务副作用，也没有破坏兼容。

兼容性新增 API 响应字段可以建议 light，但必须填写接口返回检查清单；删除/重命名字段、语义或类型变化、generated client/OpenAPI/SDK 需要同步、外部消费者不明、历史数据/缓存/持久化快照或前后端必须同步修改时，仍应 full 或先补证据。

**full** 适合：DB/migration/索引/外键/存量数据、API/DTO/OpenAPI/GraphQL 契约、权限/认证/支付/订单/状态机、跨前后端联动、缓存/消息队列/异步任务/文件/邮件/短信/第三方 API、删除/重命名/DROP/批量替换/破坏兼容，以及高风险区域证据不足。

定级由 Agent 基于证据先行建议，用户复核确认。时机是在 Context Pack 和苏格拉底式澄清之后；Phase 2.5 只做初步风险预判，不最终定档。正式定级时必须列出：允许 light 的证据、触发 full 的证据、未确认项。用户可以要求简化输出，但不能跳过 Context Pack、分析依据、安全检查、写操作确认和验证方案。

## 苏格拉底式提问如何控量

`每轮 ≤ 3 问` 是用户体验上限，不是总问题数上限。light 通常 0-1 轮；full 通常 1-3 轮；高风险 full 最多 5 轮。超过 5 轮仍不清晰时，不继续消耗用户耐心，而是输出"已确认 / 未确认 / 建议默认 / 必须用户拍板"。

问题按风险分级：P0 必问、P1 应问、P2 可默认、P3 可延后。P0/P1 未确认项不能被默认值悄悄吞掉。

**多轮触发条件**（v4.1 新增）：第 1 轮未覆盖所有 P0/P1 级问题（含用户原话模糊点 + 链路追踪发现的副作用风险点）时，必须进入第 2 轮，不得用"每轮 3 题"作为停止理由。V9 盲测发现 agent 倾向于固定问 3 题就停止，即使链路追踪已发现额外的副作用风险点（如"重发验证邮件可被无限调用"）也未追问。

## 目录结构

```
impact-pro/
├── SKILL.md              # 通用内核
├── README.md             # 本文件
├── VALIDATION.md         # 多栈测试验收方案
├── profiles/             # 技术栈规则
│   ├── _schema.md        # 技术栈规则接口
│   ├── _template.md      # 新技术栈规则模板
│   ├── generic.md         # 未知栈备用扫描
│   ├── java-spring-mybatis.md  # Java/Spring/MyBatis (Level 2)
│   ├── node-express-prisma.md  # Node/Express/Prisma (Level 1)
│   ├── python-fastapi-sqlmodel.md # FastAPI/SQLModel (Level 1)
│   ├── frontend-react-vite.md  # React/Vite 前端 (Level 1)
│   ├── frontend-nextjs.md      # Next.js App Router/Pages Router (Level 1)
│   ├── frontend-nuxt-vue.md    # Nuxt/Vue 前端 (Level 1)
│   ├── go-gin-gorm.md       # Go/Gin/GORM (Level 1)
│   └── dotnet-aspnet-efcore.md # ASP.NET Core/EF Core (Level 1)
├── db-adapters/          # 数据库适配器
│   ├── generic-sql.md    # 通用 SQL 模板
│   ├── mysql.md          # MySQL 专用
│   └── postgresql.md     # PostgreSQL 专用(pg_catalog/无 SHOW CREATE TABLE/schema 命名空间)
├── code-graph-adapters/  # 可选代码图适配器（MCP 可用时增强引用发现）
│   └── generic-mcp.md
├── references/          # 详细执行规则（按需加载，正文瘦身下沉）
│   ├── phase-2-context-discovery.md  # Phase 2 技术栈检测 + 分层探索
│   ├── phases-detail.md             # Phase 3 & 3.5 收敛协议、定级条件
│   ├── phase-5-execution.md          # Phase 5 执行与验证
│   └── cross-platform-notes.md       # 跨平台差异
└── templates/            # 文档模板
    ├── 000-context-pack.md
    ├── 010-requirements.md
    ├── 020-design.md
    ├── 030-implementation.md    # v3.6 加"环境降级路径"段
    ├── 040-light.md
    ├── _active-state.md
    ├── 060-preflight.md
    ├── 090-execution-record.md  # v3.6 加 PASS/FAIL 表格 + 决策依据
    ├── subagent-decisions.md # v3.6 新增（subagent 决策矩阵模板）
    ├── final-readiness-audit.md
    └── scorecard.md
└── tests/                # 自动化测试
    ├── run.sh            # L0 静态自洽运行器
    ├── lib/validate.sh   # 共享验证函数库
    ├── scenarios/        # JSON scenario spec（go-gin-gorm×2, java-spring-mybatis×1, frontend-nextjs×1）
    └── e2e/              # E2E 测试（scenarios/ + prompts/ + workdirs/）
```

## 共享模板同步

`templates/` 下的共享模板以 `impact-pro/templates/` 为唯一源（另一个使用这些模板的 skill 是 `impact`）。修改共享模板后跑同步：

```bash
python scripts/sync_templates.py          # 同步到 impact/templates/
python scripts/sync_templates.py --check  # 只检查不一致，L0 测试会调用
```

`impact-pro` 独有的模板（`final-readiness-audit.md`、`scorecard.md`）不参与同步。

## 部署前提（纵深防御）

**只读账号是上线硬条件，不是建议。** 允许 tools 里预批准了 `query`/`execute_sql` 等写能力工具（免权限提示），唯一回退就是账号本身无写权限。跳过此条件 = 只剩 prompt 级防线。

- Agent 使用的 DB MCP 连接**必须**配置为只读账号——协议层的确认检查点是 prompt 级约束，只读账号是系统级硬约束，两层叠加
- 可选启用 `.claude/hooks/impact-write-gate.*`：在目标项目根放 `.impact-protected` 后，PreToolUse hook 会拦截受保护根内的写工具调用，只有当前对话最新用户消息显式 `确认 Step N` 才放行一次
- 上线前核对：
  - Agent 使用的连接串确实指向只读账号
  - 该账号无 INSERT / UPDATE / DELETE / DDL / GRANT 权限（用 `SHOW GRANTS` 类命令实查，不凭命名推断）
  - prod 与 staging 连接明确区分；执行记录写入 DB target / schema / 账号别名
  - 日志和文档中不回显完整连接串
- 写操作通过"Agent 生成脚本 → 用户执行"完成；生产 DB 默认禁止 Agent 直接执行（见 DDL/DML 执行方式）

## 致谢

“引用检查分级”来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提出的 issue：改代码前应检查其他地方是否引用，查到后再分级处理。这个建议已纳入 `RuleBlade` 和 `impact-pro` 的 Context Pack 流程，用来减少多栈项目里漏掉调用方、注册点、生成物或测试的风险。

长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 回退保护、阻塞恢复安全闸、多会话写授权一致性和执行记录补强，来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提供的真实使用案例。该案例也被用于 `impact-pro` 的规则回迁分析，帮助确认这些边界并不只存在于 Java/RuoYi 场景。
