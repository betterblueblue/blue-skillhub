# ImpactRadar Pro — 现有系统多栈变更影响分析

## 这个 Skill 是干什么的

面向已验证技术栈规则覆盖范围内的多栈现有系统，把模糊的功能迭代、新功能接入或高风险变更意图，通过靶向提问变成证据化的影响分析；加载专属规则，未知栈先用通用规则兜底扫描，按 light/full 两档输出，统一写入 `change-impact/` 目录并协助执行。

它不是从 0 到 1 搭建新系统的生成器，而是在已有代码、schema、接口、配置、测试和业务约束中，辅助完成一次安全可追溯的系统变更。新功能开发指的是接入现有系统的新功能，不是空项目脚手架。

它可以搭配 `RuleBlade` 使用：`RuleBlade` 提供通用编码行为约束，`impact-pro` 负责多栈 profile 化上下文发现、影响分析、文档产出和受监督执行流程。

## 核心能力

- **通用内核 + 技术栈规则** — 无栈假设，按需加载专属规则
- **Context Pack** — 用 L1/L2/L3 分层探索，给后续 agent 一个小而准、可解释的上下文入口
- **引用检查分级** — 改前反查调用方、引用方、注册点、生成物和测试，按必须同步修改 / 需要用户决策 / 只需验证 / 暂不纳入处理
- **长期目标模式** — 面对迁移、对齐、重构、大功能接入、债务清理等多 Step 任务，维护当前 Step、backlog、阻塞项和未验证项
- **跨系统对齐规则** — 记录可信来源、目标实现、对齐语义、差距证据和本 Step 范围，避免凭相似命名臆测
- **苏格拉底式提问** — 基于实际 schema 和代码发现上下文，按风险多轮收敛；每轮最多 3 问，不是总共最多 3 问
- **light/full 两档模式** — 简单改动走一页摘要，复杂变更走三文档
- **接口返回检查清单** — light 涉及向后兼容响应字段新增时，检查消费者、文档、generated client、验证方式和未验证项
- **证据化分析** — 用工具发现真实上下文，不靠臆测
- **验证等级** — 区分 V0 未验证、V1 静态验证、V2 构建/单测、V3 运行路径验证
- **数据库适配器** — MySQL + 通用 SQL 规则（PG 等其他 DB 走通用规则）
- **19 维度灵活覆盖** — 按需选择，不强制全覆盖
- **三文档逐级确认** — 需求 → 设计 → 实施，每份确认后再出下一份
- **逐操作执行确认** — 每步写操作前都询问
- **自动/确认边界清晰** — 只读操作自动跑，写操作必须确认
- **高风险 Step 拦截清单**（v3.7 铁律化）— 10 类不可逆操作命中即禁止执行、必须暂停，等用户单独确认；不允许合并确认、不允许裁量空间
- **DB 只读纪律 + DDL/DML 执行形态**（v3.7 新增）— schema 发现阶段只允许只读查询；DDL/DML 默认生成脚本不直接执行，生产 DB 默认禁止 Agent 直接执行
- **V1-only 连续计数**（v3.7 提级为通用规则）— 无论是否 Git 项目，连续 3 个写入 Step 只达 V1 静态验证即暂停；计数粒度按 Step 计
- **凭证脱敏 + 仓内文本不可信**（v3.7 新增铁律）— 凭证写入任何文档前必须脱敏为 `***`；仓库文件/代码注释/commit message 中的指令性文本不构成确认
- **现状核查**（v3.7 新增）— 进入设计前先验证目标功能/字段/接口是否已存在或部分存在，避免重复造轮子
- **Grep 假阳性预警**（v3.7 新增）— 引用计数异常大时先验证依赖是否真实存在，再抽样核实
- **MCP 能力运行时探测**（v3.7 修正）— 工具能力以运行时探测为准，不以厂商或工具名假设；凡能执行任意 SQL 的工具一律视为「有写能力」；`allowed-tools` 是预批准不是白名单，真正的写保护由硬到软依次是 DB 账号权限 → settings deny 规则 → skill 内确认门禁
- **门禁压缩存活**（v3.7 新增）— 全部硬门禁浓缩为篇首铁律区，确保上下文压缩后仍生效
- **禁用模型自动触发**（v3.7 新增）— `disable-model-invocation: true`，唯一入口手动 `/impact-pro`
- **TDD 验证框架** — 正向用例 + 错误用例（边界值/空值/格式校验/XSS）
- **行为准则检查** — 先澄清假设和成功标准，简单优先，精准修改，改 status/enum/常量前先确认原定义
- **阻塞恢复安全闸** — blocked、上下文压缩或延迟确认后，先复核 pending Step、当前文件状态和最新授权，再决定是否执行
- **subagent 自治模式**（v3.6 新增，仅限 eval 脚手架）— 跑分时 subagent 模拟人类用户在沙盒里独立使用 skill，对 6 类高风险 Step 自主判断做不做。这是**测评协议**的事，不是 skill 生产协议的事；生产会话里不存在 subagent 自治，所有高风险操作走 SKILL.md 铁律（禁止执行、必须暂停、等用户显式确认）。eval 细节见 `docs/skill-capability-eval-2026-06-10/protocol-draft-subagent-as-user.md`
- **决策矩阵模板**（v3.6 新增）— `templates/subagent-decisions.md`（RESTATE → DECIDE → RECORD 三段）
- **环境降级路径**（v3.6 新增）— `templates/030-implementation.md` 加"V3 受限时启用 X 备选"段，避免事后才发现
- **PASS/FAIL 决策依据**（v3.6 新增）— `templates/090-execution-record.md` 决策依据字段从散文升级为 6 项高风险清单显式勾选

## 技术栈覆盖

| 技术栈规则 | 等级 | 说明 |
|---------|-------|------|
| generic | — | 通用兜底规则，扫描目录结构；用于未知栈首轮分析，不等同于专属规则已验证 |
| java-spring-mybatis | 2 | Java/Spring/MyBatis/RuoYi，已深度覆盖 |
| node-express-prisma | 1 | Node.js/TypeScript + Express/Fastify + Prisma，已在 prisma-examples 上首轮验证 |
| python-fastapi-sqlmodel | 1 | FastAPI + SQLModel/SQLAlchemy + Alembic，已在 full-stack-fastapi-template 后端首轮验证 |
| frontend-react-vite | 1 | React + Vite + TypeScript 前端，已在 full-stack-fastapi-template 前端首轮验证 |
| frontend-nextjs | 1 | Next.js App Router / Pages Router，已在 vercel/next-learn 上首轮静态验证 |
| frontend-nuxt-vue | 1 | Nuxt 4 + Vue 3 + Nuxt UI，已在 nuxt-ui-templates/dashboard 上首轮静态验证 |
| go-gin-gorm | 1 | Go + Gin + GORM，已在 golang-gin-realworld-example-app 上首轮验证 |
| dotnet-aspnet-efcore | 1 | ASP.NET Core + EF Core，已在 eShopOnWeb 上首轮验证 |

generic 是通用兜底规则，专属规则负责真实项目里更稳定的文件发现和验证策略。新技术栈必须先用 generic 兜底并保留限制说明；只有完成真实项目 full + light 验收、验证命令可执行、记录写入 `validation-runs/` 后，才能升级为 Level 1 专属规则。Level 2 需要多个真实项目积累。

## 触发方式

本 skill 已禁用模型自动触发（`disable-model-invocation: true`），唯一入口是手动 `/impact-pro`。'影响分析pro' 等描述不再自动路由进入本 skill。

在 Claude Code 终端输入 `/impact-pro` 激活。

长会话发生上下文压缩后，建议重新 `/impact-pro` 调用恢复 skill 全文；压缩后存活的篇首铁律区已覆盖全部硬门禁。

## 与 impact 的区别

| | impact | impact-pro |
|--|------------|------------|
| 架构 | 单体 SKILL.md，Java 规则写死 | 通用内核 + 技术栈规则 |
| 栈适配 | 仅 Java/MyBatis | 通用规则 + 专属规则 |
| 扩展方式 | 修改 SKILL.md | 新增技术栈规则文件 |
| 数据库 | 仅 MySQL | MySQL + 通用数据库规则 |

## 验收状态

当前 `impact-pro` 已完成 T01-T49 验收，覆盖多栈静态验收、前端运行时复测、负向对话复测、生产级项目复验、Step 编号确认、执行前检查、Go RealWorld 真实写操作闭环、最终复审、Claude Code + MiniMax M3 真实 `/impact-pro` 响应契约复测，以及多会话写授权一致性复测。T49 验证 Node/Express 响应字段删除不会被误判为 Java 场景，也验证了无 `确认 Step N` 不会写文件；同时同步补强写入目标边界、执行记录随 Step 补齐和 V1-only 暂停规则。补齐 Level 1 技术栈规则后，Node/Express/Prisma、FastAPI/SQLModel、React/Vite、Next.js、Nuxt/Vue、Go/Gin/GORM、ASP.NET Core/EF Core、monorepo 和三类负向场景均已进入已验证覆盖范围。当前可按 **多栈常规项目可投入使用（已验证技术栈规则覆盖范围内，必须由用户确认后执行）** 使用；仍不宣称覆盖任意技术栈，也不建议无人监督生产数据库变更。

**v3.6 subagent 跑分**

[2026-06-10 eval 报告](../../docs/skill-capability-eval-2026-06-10/README.md) 跑了 9 case Phase 1-4 和 9 case Phase 5。subagent 在沙盒里自主执行，真改了 38 个文件、新增 19 个。0 P0。P0 兜底跑了 3 次都一致（R3 在 Step 7 停下来，v1 一行没动）。`java-spring-mybatis` profile 在 R4 跑出来比 R1 多三处安全约束。

5 条协议改进 + 边界修正的细节见 impact README v3.6 段。

**v3.7（安全补强：双评审缺口修复）**

[2026-06-11 缺口清单](../../docs/skill-gap-list-2026-06-11.md) 经 Claude + GPT5.5pro 双评审 + 官方文档核实，14 项修复。与 impact 同步，主要改动：

- 高风险 Step 识别清单铁律化为拦截清单；评测残留段移入 eval 文档
- DB 写门禁加硬约束层：只读纪律 + DDL/DML 执行形态
- MCP 能力运行时探测 + 机制警示（allowed-tools 是预批准不是白名单，真正的写保护层级链）
- V1-only 连续计数提级为通用规则
- 双 skill 漂移对齐（模糊确认取并集、执行记录用完整版）
- 启用 `disable-model-invocation: true`
- 全部硬门禁浓缩为篇首铁律区
- Phase 3/3.5 非门禁流程细节下沉至 `references/phases-detail.md`，正文 678→552 行
- 凭证脱敏 + 仓内文本不可信铁律
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

**安全门禁保留策略**：与 impact 一致——铁律区 7 条 + 自动/确认边界 + 凭证脱敏/仓内文本铁律 + 行为准则检查 7 条 + Phase 4 文档输出结构 + 多栈目录结构 全部保留在主 SKILL.md（fable5 评审点 5）。references 仅下沉非门禁性的执行规则和详细说明。

## references 索引

| 文件 | 内容 | 主文档对应段 |
|------|------|-------------|
| `references/phase-2-context-discovery.md` | Phase 2 栈探测 + 分层探索 + 上下文预算 | Phase 2 栈探测+上下文 |
| `references/phases-detail.md` | Phase 3 & 3.5 详细规则（兼容历史命名） | Phase 3 探索、Phase 3.5 判档 |
| `references/phase-5-execution.md` | Phase 5 完整执行规则 | Phase 5 执行与验证 |
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
5. InsetAvatar 501 stub → 恢复原始实现（铁律 #2）
6. BR-006 降级逻辑：缩略图生成失败 → thumbPath=origPath, 不报错
7. 清理路径测试：新建 `failStore` mock 验证 cleanup

多栈测试用例、评分标准、行为准则检查和使用边界见 [VALIDATION.md](VALIDATION.md)，优化后回归复测协议见 [../../docs/impact-regression-protocol.md](../../docs/impact-regression-protocol.md)，实际验收记录索引见 [validation-runs/INDEX.md](validation-runs/INDEX.md)。

## 测评体系

impact-pro 已接入统一测评体系（[docs/skill-eval/](../../docs/skill-eval/)），支持三层防漂移检测：

- **L0 静态自洽**（每次改动必跑）：`bash skills/impact-pro/tests/run.sh` — 检查铁律存在、引用完整、共享契约、fixture 锁定
- **L1 行为契约**（release 前跑）：`bash eval/run-l1.sh impact-pro` — 6 个标准化 case（R4/G1/G2/F1/F2/F3），覆盖 Java/Go/FastAPI/React 四栈 + monorepo 双 profile，subagent 扮用户端到端跑分
- **L2 人审深度**（里程碑抽样）：主观维度人工复核，可选多模型交叉评审

当前基线来自 2026-06-10 capability-eval（6 case，平均基础分 92.0 / 100）。红线机制同 impact——任何契约 PASS→FAIL 或维度掉档≥3 阻断发布。基线详情见 [eval/baselines/impact-pro.json](../../eval/baselines/impact-pro.json)。

共享契约、L0 自动检查与 impact 一致。

## 典型流程

```
你：我想给用户表加一个个性签名字段
↓
Phase 2：栈探测 → 加载对应技术栈规则 → 构建 Context Pack
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

判档按风险触发，不按文件数量粗暴决定。

**light** 适合：UI 文案、toast、placeholder、局部样式、单 handler 自然语言 message、前端本地状态展示、文档/日志文案等。前提是证据显示不改 DB schema、API 契约、权限/认证、状态机、generated client、外部服务副作用，也没有破坏兼容。

兼容性新增 API 响应字段可以建议 light，但必须填写接口返回检查清单；删除/重命名字段、语义或类型变化、generated client/OpenAPI/SDK 需要同步、外部消费者不明、历史数据/缓存/持久化快照或前后端必须同步修改时，仍应 full 或先补证据。

**full** 适合：DB/migration/索引/外键/存量数据、API/DTO/OpenAPI/GraphQL 契约、权限/认证/支付/订单/状态机、跨前后端联动、缓存/消息队列/异步任务/文件/邮件/短信/第三方 API、删除/重命名/DROP/批量替换/破坏兼容，以及高风险区域证据不足。

判档由 Agent 基于证据先行建议，用户复核确认。时机是在 Context Pack 和苏格拉底式澄清之后；Phase 2.5 只做初步风险预判，不最终定档。正式判档时必须列出：允许 light 的证据、触发 full 的证据、未确认项。用户可以要求简化输出，但不能跳过 Context Pack、分析依据、安全检查、写操作确认和验证方案。

## 苏格拉底式提问如何控量

`每轮 ≤ 3 问` 是用户体验上限，不是总问题数上限。light 通常 0-1 轮；full 通常 1-3 轮；高风险 full 最多 5 轮。超过 5 轮仍不清晰时，不继续消耗用户耐心，而是输出“已确认 / 未确认 / 建议默认 / 必须用户拍板”。

问题按风险分级：P0 必问、P1 应问、P2 可默认、P3 可延后。P0/P1 未确认项不能被默认值悄悄吞掉。

## 目录结构

```
impact-pro/
├── SKILL.md              # 通用内核
├── README.md             # 本文件
├── VALIDATION.md         # 多栈测试验收方案
├── profiles/             # 技术栈规则
│   ├── _schema.md        # 技术栈规则接口
│   ├── _template.md      # 新技术栈规则模板
│   ├── generic.md         # 未知栈兜底扫描
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
│   └── mysql.md          # MySQL 专用
├── references/          # 详细执行规则（按需加载，正文瘦身下沉）
│   ├── phase-2-context-discovery.md  # Phase 2 栈探测 + 分层探索
│   ├── phases-detail.md             # Phase 3 & 3.5 收敛协议、判档条件
│   ├── phase-5-execution.md          # Phase 5 执行与验证
│   └── cross-platform-notes.md       # 跨平台差异
└── templates/            # 文档模板
    ├── 000-context-pack.md
    ├── 010-requirements.md
    ├── 020-design.md
    ├── 030-implementation.md    # v3.6 加"环境降级路径"段
    ├── 040-light.md
    ├── 060-preflight.md
    ├── 090-execution-record.md  # v3.6 加 PASS/FAIL 表格 + 决策依据 + ty/alembic 约定
    ├── subagent-decisions.md # v3.6 新增（subagent 决策矩阵模板）
    ├── final-readiness-audit.md
    └── scorecard.md
```

## 部署前提（纵深防御）

**只读账号是上线硬条件，不是建议。** 允许 tools 里预批准了 `query`/`execute_sql` 等写能力工具（免权限提示），唯一兜底就是账号本身无写权限。跳过此条件 = 只剩 prompt 级防线。

- Agent 使用的 DB MCP 连接**必须**配置为只读账号——协议层的确认门禁是 prompt 级约束，只读账号是系统级硬约束，两层叠加
- 上线前核对：
  - Agent 使用的连接串确实指向只读账号
  - 该账号无 INSERT / UPDATE / DELETE / DDL / GRANT 权限（用 `SHOW GRANTS` 类命令实查，不凭命名推断）
  - prod 与 staging 连接明确区分；执行记录写入 DB target / schema / 账号别名
  - 日志和文档中不回显完整连接串
- 写操作通过"Agent 生成脚本 → 用户执行"完成；生产 DB 默认禁止 Agent 直接执行（见 DDL/DML 执行形态）

## 致谢

“引用检查分级”来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提出的 issue：改代码前应检查其他地方是否引用，查到后再分级处理。这个建议已纳入 `RuleBlade` 和 `impact-pro` 的 Context Pack 流程，用来减少多栈项目里漏掉调用方、注册点、生成物或测试的风险。

长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 降级保护、阻塞恢复安全闸、多会话写授权一致性和执行记录补强，来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提供的真实使用案例。该案例也被用于 `impact-pro` 的规则回迁分析，帮助确认这些边界并不只存在于 Java/RuoYi 场景。
