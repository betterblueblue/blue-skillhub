# ImpactRadar 迭代历史

> 本文件是 impact skill 的完整版本历史。README 只放摘要表，详细变更、跑分数据和评审报告链接都在这里。

## 迭代记录

### v1.0（初始版本）

第一个版本输出结构化 prompt 给下一个 agent 做影响分析。没有文档，没有执行能力。

### v2.0（核心重构）

- 去掉 prompt 输出，改为输出三份完整文档
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
- light/full 两档模式（简单改动走一页摘要，不强制走三文档）
- 自动/确认边界表（清晰区分只读操作和写操作）
- MCP 能力探测（先判断工具可用性再分支，不对着不可用工具报错）
- 退出条件（用户说简化就简化，不强制走完整流程）
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
- 全部硬性安全闸浓缩为篇首强制规则区（上下文压缩后仍保留），确保上下文压缩后仍生效

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

回应 gpt5.5pro 评审的"把 SKILL.md 拆分到 references"建议。Anthropic 官方 [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) 明文："Keep SKILL.md body under 500 lines for optimal performance"。本次拆分后：

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

**v4.2（2026-06-26：战略定位验证 — 脚本闸门兜底弱模型判档错误）**

2026-06-26 战略定位验证实验确认：Composer 2.5 + skill 均分 79.0，Opus 4.x + CLAUDE.md 均分 73.0（Δ=6.0），Step 3.7 Flash + skill v4.1 均分 79.7（v3.8 baseline 59.7，+20.0）。实验结论：skill 在证据精度维度领先（+10 分），但在深度推理维度 Opus 占优；弱模型 v4.1 过早收尾和证据遗漏已修复，但 B2' 判档错误仍未修复。

针对 P1 确认的判档问题，新增 V7 脚本闸门：

- **全量词覆盖门禁（FAIL）**：用户原话出现全量词时，产出必须包含覆盖范围分析，缺失则 FAIL 拦截
- **过度判档检测（WARN）**：Full 模式但步骤少且文件少 → 提示可能应为 Light
- **判档不足检测（WARN）**：Light 模式但需修改文件多 → 提示可能应为 Full

评审结果见 `eval/runs/strategic-verify-2026-06-26/JUDGE-RESULT.md`，战略定位修订见 [docs/skill-review-2026-06-26.md](../../docs/skill-review-2026-06-26.md) §6.2-§6.4。

**v4.3（2026-06-28：不确定项分类 + 判档表事实一致性检查）**

针对 Pathfinder 场景下用户不熟悉项目、无法回答技术细节问题的痛点，以及 experiment-v1 中判档表事实与 context-pack 不一致的遗留问题，落地两项改进：

- **Phase 3 Step 3.0 不确定项分类**：提问前先分类——代码可推断项（鉴权范围、param 命名、正则、返回字段脱敏等）由 Agent 自行查证并标 `【代码推断: file:line】`，不问用户；业务需决策项才问用户，附默认建议。Pathfinder 场景下避免把技术细节推给无法回答的用户。
- **判档表事实一致性检查**（检查 3）：实施文档预检新增检查——判档决策表中的事实陈述须与 `000-context-pack.md` 已确认事实一致，防止过期或错误事实在文档间传播。

改进覆盖 8 个文件：SKILL.md、references/phases-detail.md、references/phase-4-output.md、templates/000-context-pack.md、templates/010-requirements.md、templates/040-light.md、templates/_active-state.md、README.md。

**v4.3.1（2026-06-28：V9 脚本闸门实现）**

将检查 3 从 agent 内部自觉执行升级为 `impact_validate.py` V9 脚本闸门，弱模型也绕不过：

- **矛盾检测（WARN）**：提取判档决策表中的事实声明，与 `000-context-pack.md` §7 已确认事实交叉比对。对同一 camelCase 实体（如 `updateUserById`），检查描述中是否出现相反描述词对（含/不含、存在/不存在、已实现/未实现）
- **未确认事实检测（WARN）**：判档表引用了 §7 中没有对应条目的实体时报 WARN，提示补充到 §7 或标注「待核实」
- 实现要点：camelCase 实体提取 + 实体上下文窗口比对 + 子串去重（解决「含」是「不含」子串的误判问题）

新增 7 个单元测试覆盖：无判档表/无 §7/一致/矛盾/未确认/无共享实体/段标题定位。

**5 模型端到端对比（2026-06-28：筛选性价比优化目标）**

在同一个真实项目（realworld-express-prisma）上，让 Composer 2.5、Kimi K2.6、GLM-5.1、Step 3.7 Flash、GLM-5.2 五个模型分别执行三个任务：Pathfinder 摸底 + Impact light（请求体大小限制）+ Impact full（强制邮箱验证）。评分采用三层固化体系：

| 层级 | 指标 | 满分 | 说明 |
|------|------|------|------|
| 第一层：硬性门禁 | G1 文件产出完整性 | PASS/FAIL | Skill 要求的产出文件是否全部生成且非空 |
| | G2 章节完整性 | PASS/FAIL | Pathfinder 15 核心节齐全 + Impact 文档结构完整 |
| | G3 事实准确性 | PASS/FAIL | 产出事实与 Ground Truth 一致，无编造；≥2 处直接 FAIL |
| | G4 Script Gate | PASS/FAIL | `pf_validate.py` 执行且无 FAIL |
| 第二层：流程合规 | G5 不确定项分类 | 8 | Step 3.0 代码可推断 vs 业务需决策正确区分 |
| | G6 L1 上下文交接 | 8 | Impact 实际读取并复用 Pathfinder 地图 |
| | G7 影响覆盖完整性 | 8 | C2 七层影响全覆盖（schema/注册/登录/端点/邮件/auth/JWT） |
| | G8 定级与流程完整性 | 8 | light/full 判档正确 + 判档决策表 + `_active-state.md` |
| | G9 文档间一致性 | 8 | 010/020/030 三文档间无自相矛盾 |
| 第三层：产出质量 | Q1 需求文档完整性 | 10 | 验收标准覆盖度、假设标注质量、模糊点处理 |
| | Q2 设计方案深度 | 10 | 替代方案对比、横切关注点表、向后兼容评估 |
| | Q3 实施可执行性 | 10 | 步骤清晰度、代码示例质量、前置检查、回滚方案 |
| | Q4 代码风格适配 | 10 | 风格约束提取精度、是否带行号证据引用 |
| | Q5 验证严谨性 | 10 | 验证用例覆盖、API 方法存在性检查、异常行为确认 |
| | Q6 设计决策质量 | 10 | 方案选择理由、被否方案论证、语义约定确认 |

> 第一层任一 FAIL 直接降级为 B 级，不参与计分；第二层和第三层合计为总分（满分 100）。等级定义：S 级（门禁全 PASS + 合规≥36 + 质量≥54）、A 级（门禁全 PASS + 合规≥28 + 质量≥36）、B 级（门禁有 FAIL 或合规<28 或质量<36）。

**对比结果：**

| 模型 | 门禁 | 合规 (/40) | 质量 (/60) | 总分 (/100) | 等级 | 关键发现 |
|------|------|-----------|-----------|------------|------|---------|
| GLM-5.2 | 全 PASS | 40 | 56 | **96** | **S** | 质量明显领先：独有方法存在性验证 + 异常行为确认 + 5 方案对比 + 19 维横切表 |
| Step 3.7 Flash | 全 PASS | 40 | 50 | **90** | A | 弱模型最佳表现：文件最齐全、事实零错误、12 条代码风格观察（最多） |
| Composer 2.5 | 全 PASS | 40 | 46 | **86** | A | 合规满分但质量深度不足：无横切表（Q2=7）、无方法验证（Q5=6） |
| GLM-5.1 | 全 PASS | 36 | 48 | **84** | A | C1/C2 均缺 `_active-state.md`（G8 扣 4 分） |
| Kimi K2.6 | G3 FAIL | 26 | 45 | **71** | **B** | 事实编造（将 PostgreSQL 说成 SQLite + 命名约定错），C1 缺 context-pack + 分类 |

**筛选决策：** 淘汰 Kimi K2.6（B 级，G3 事实编造一票否决）和 GLM-5.1（84 分，合规扣分多、质量中等）。选定 Composer 2.5 和 Step 3.7 Flash 作为性价比优化目标——两个模型合规均满分（40/40），失分集中在产出质量维度，说明 Skill 流程让合规性都达标了，优化空间在质量深度。GLM-5.2 作为标杆（96 分），用于衡量优化效果。评审报告见 `eval/runs/e2e-model-comparison-2026-06-28/REVIEW.md`。

**v4.4（2026-06-28：e2e 优化验证 — 横切表门禁 + Prisma 异常参考 + _active-state 检查）**

针对 5 模型对比中 Composer 2.5 和 Step 3.7 Flash 暴露的失分点，做了三轮 Skill 模板优化（R1 基线 → R2 四项优化 → R3 五项优化）。R1 对比中发现三个模型方差问题：Composer 2.5 改名绕过横切表、两模型遗漏 `_active-state.md`、Step 3.7 Flash 对 Prisma ORM 异常码误判。针对这三个问题落地改进：

- **V10 横切表 FAIL 门禁**：`impact_validate.py` 新增 V10 检查——full 模式下扫描 `020-design.md` `## 6. 横切关注点` 标题，缺失则 FAIL 拦截；行数 < 10 或 ☑/☐ 标记 < 5 报 WARN。解决 Composer 2.5 在 R2 中通过改名绕过横切表的问题
- **V1 `_active-state.md` WARN 检查**：V1 文件完整性检查新增 `_active-state.md` 存在性检查，缺失报 WARN。解决两模型在 R2 中遗漏跨会话恢复检查点的问题
- **Prisma ORM 异常行为模式参考**：`references/phase-4-output.md` 新增 Prisma ORM 方法异常行为参考表（`findUnique`/`findFirst` 返回 null 不抛异常、`create` 抛 P2002 唯一约束冲突、`update`/`delete` 抛 P2025 记录不存在）。解决 Step 3.7 Flash 将 `create` 误标为 P2025、将 `hashPassword` 误标为抛异常等 3 处错误
- **§6 标题防改名**：`templates/020-design.md` §6 注释增加 ⚠️ 强制要求 + 脚本检查提示，防止模型通过改名绕过 V10 检查

三轮优化验证结果：

| 模型 | R1（基线） | R2（四项优化） | R3（五项优化） | R1→R3 变化 | 关键提升 |
|------|-----------|--------------|--------------|-----------|---------|
| Composer 2.5 | 86/A | 86/A | **92/A** | +6 | Q2 设计深度 7→9（横切表恢复），G8 定级流程 4→8（`_active-state.md` 恢复） |
| Step 3.7 Flash | 90/A | 87/A | **92/A** | +2 | Q5 验证严谨性 8→9（Prisma 异常码纠正），G8 定级流程 4→8（`_active-state.md` 恢复） |

与标杆 GLM-5.2（96 分）的质量差距：Composer 2.5 从 R1 的 -10 缩小到 R3 的 **-4**，Step 3.7 Flash 从 -6 缩小到 **-4**。两模型质量分首次并列（52/60），剩余 -4 差距主要在 Q4（风格适配，缺行号引用）和 Q6（决策质量，方案对比深度）。评审报告见 `eval/runs/e2e-skill-optimization-2026-06-28/REVIEW-r3.md`。`impact_validate.py` 现有 V1-V11 共 11 项检查。

**v4.5（2026-06-28：R4 跨栈+弱引导验证）**

R3 优化后换到 Java/Spring Boot/MyBatis 栈 + 弱引导 prompt（不给文件列表、不提示涉及哪些层、不标 light/full）重新验证。R4 暴露了**模板引导不够**的根本问题：去掉 prompt 提示后，两模型都没跑 `impact_validate.py`，C25 完全自创章节结构（§3.2 和 §6 都丢了），S37 跳过 context-pack，S37 设计解读偏差（用户说"先存草稿"但默认 PUBLISHED）。C25=83/B、S37=85/B。评审报告见 `eval/runs/e2e-skill-optimization-2026-06-28/REVIEW-r4.md`。

**v4.6（2026-06-28：R5-R6 弱引导下强制规则修复）**

针对 R4 暴露的问题落地 O10-O16 共 7 项优化：

- **O10 §3.2 强制规则**：SKILL.md 强制规则加第 8 条（Phase 4 输出后必须跑 `impact_validate.py`，有 FAIL 不得提交）；030 模板 §3.2 标题改为 `⚠️ 强制必做 — 缺此节 V3 FAIL 阻止提交`
- **O11 §6 强制规则**：SKILL.md Phase 4 必产出清单明确列出 `## 6. 横切关注点` 为必含节；加"写每份文档前必须先 Read 对应模板，按模板章节结构产出，不得自创章节编号"
- **O12 context-pack 必产出**：phase-4-output.md 说明改为"light 和 full 模式均必产出"；V1 检查在 light 模式下对缺 context-pack 报 WARN
- **O13 设计意图映射**：phase-1-intent.md 新增"用户意图→设计假设映射"节
- **O14 脚本门禁**：_active-state.md 模板加 placeholder 禁止写 N/A
- **O16 读路径 SQL 判 light**：phases-detail.md 新增"仅调整读路径 SQL 的 WHERE/SELECT 投影属于 light"规则

R5 结果：C25 从 83 提升到 **95**（R4 暴露的三个问题全部解决），S37 从 85 提升到 **87**（§3.2 和 context-pack 修复，但设计解读偏差和跑脚本未生效）。R6 结果：S37 C1 正确判 light（O16 修复），S37 知道要跑脚本但找不到路径（O14 部分修复），S37 意外默认 DRAFT（O13 非确定性修复）。C25=95 不退步，S37=90。评审报告见 `eval/runs/e2e-skill-optimization-2026-06-28/REVIEW-r5.md` 和 `REVIEW-r6.md`。

**v4.7（2026-06-28：R7 脚本路径澄清 + _active-state 模板强制，优化收尾）**

针对 R6 遗留问题落地 O14（最终版）+ O18：

- **O14 脚本路径澄清**：`impact_validate.py` 从根目录 `scripts/` 移到 `skills/impact/scripts/`，消除路径歧义；SKILL.md、phase-4-output.md、_active-state.md 模板中所有引用统一为新路径
- **O18 _active-state 模板强制**：SKILL.md 模板章节结构强制规则扩展覆盖 `_active-state.md`

R7 结果：O18 完全修复（S37 的 _active-state.md 从自创格式改为跟模板），O14 路径修复但 S37 仍未实际执行脚本（标"待执行"而非当场跑完），O13 回退（S37 重新默认 PUBLISHED，证实 R6 的 DRAFT 修复是非确定性的）。C25=95 不退步，S37=90 持平。

**优化 loop 收尾**：R1-R7 共 7 轮验证，O1-O18 共 18 项优化措施。Composer 2.5 从 86 分提升到 95 分并稳定，弱引导+跨栈下不靠 prompt 提示即可高质量完成。Step 3.7 Flash 剩余问题（脚本执行、O13 非确定性）属 LLM 行为层面，skill 框架层面已做到极限。详细数据见 `eval/runs/e2e-skill-optimization-2026-06-28/REVIEW-r7.md`。

> **V11 补录**：`impact_validate.py` V11（light 模式关键链路深度检查门禁）在 v3.9 已作为行为要求写入 phase-4-output.md，但脚本实现和文档记录滞后。本次（v4.7 后）补齐脚本 V11 实现 + SKILL.md/README/phase-4-output.md 三处文档记录。V11 为 WARN 级，检查 040-light.md 是否包含「关键链路深度检查」节标题。

### v4.8（Phase 3 跳过防护）

真实运行发现：agent 在 SayClearContentManager 项目上执行 `/impact` 时，Phase 1 识别到需求存在多种理解，却自行选择一种理解后直接进入 Phase 2，跳过了 Phase 3 苏格拉底式探索、Phase 3.5 定级确认，并在无 `确认 Step N` 的情况下直接写了 3 个 Phase 4 文档。

**根因**：skill 没有显式禁止"识别歧义后自行选择理解继续"，快速通道的"无未确认项"条件也没说明 agent 自行识别的歧义也算未确认项。

**改了什么**

- SKILL.md Phase 1 新增「禁止自行消解歧义」规则：识别到歧义后，agent 自行选择一种理解不等于用户确认——必须停下来等用户选择或纠正
- SKILL.md 快速通道条件显式补充：agent 在 Phase 1 识别的歧义也属于未确认项，不得自行消解后再走快速通道
- SKILL.md 硬规则新增第 9 条「Phase 4 写入前置检查」：写文档前必须满足 ① 已完成 Phase 3 并获用户定级确认，或 ② 快速通道条件全部满足；提问后不等用户回答就继续执行（假提问）不构成确认
- `phase-1-intent.md` 同步快速通道条件澄清 + 新增「歧义 ≠ 假设」说明：从用户口语推断隐含意图是合理代码推断，但需求存在多种理解属于歧义，必须问用户
- `_active-state.md` 模板新增 `Phase 3 状态` 和 `Phase 3.5 定级` 两个字段，使 Phase 3 跳过在状态文件中可见
- `impact_validate.py` 新增 V12 门禁（WARN）：检查 `_active-state.md` 是否包含 Phase 3 状态追踪字段，缺失报 WARN

### 模型选型（v4 干净环境实测）

完整模型能力评价见 [docs/model-eval-2026-06-25.md](../../docs/archive/2026-06/model-eval-2026-06-25.md)。

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 涉及覆盖范围判断（"每次/所有"全量词） | **仅 Composer 2.5** | Step/DeepSeek 会误判 light |
| 不涉及覆盖范围判断 | Composer 或 Step | Step 的 B2/B3 质量合格 |
| 安全敏感场景（认证/权限/密码） | **仅 Composer 2.5** | 证据编造 0 例 + 跨文件分析最强 |

评审报告见 `eval/runs/blind-2026-06-24-v4-{composer25,step37flash,deepseek-v4-flash}/`，最终结论见 [eval/runs/BLIND-TEST-FINAL-CONCLUSION.md](../../eval/runs/BLIND-TEST-FINAL-CONCLUSION.md)。
