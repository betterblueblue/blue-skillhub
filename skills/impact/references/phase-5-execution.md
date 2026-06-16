# Phase 5: 执行与验证详细规则

> 本文件包含 Phase 5 执行与验证的完整规则。SKILL.md 正文只保留概要与高风险拦截清单（硬性规则级），详细执行规则见此。
> 适用栈：Java / Spring / MyBatis（如 RuoYi 等后台框架；impact 专用）。多栈请使用 impact-pro + 加载对应 profile。

## 写入目标边界

每个涉及写入的 Step 必须先声明目标项目根目录，并把所有写入对象解析为绝对路径、表名、配置键或外部对象。文件写入必须满足：

- 绝对路径位于目标项目根目录内。
- `change-impact/` 目录也必须位于目标项目根目录内，不能写到 agent 当前工作目录或其他仓库。
- 不能只写相对路径就执行；相对路径必须先按目标项目根目录解析并回显。
- 解析后的路径不在目标项目根目录内，或无法证明在目标项目根目录内时，视为 P0 阻塞，不得写入。
- 如果发现写错目录，必须立刻停止，报告已发生的写入、清理结果和残留风险；清理自己的误写不等于本 Step 通过。

## V1-only 连续计数（通用规则）

连续多个写入 Step 都只能达到 V1 静态验证时，必须维护 V1-only 计数——**无论目标项目是否为 Git 仓库**。默认连续 3 个写入 Step 仍无法达到 V2/V3 时暂停，要求用户选择：

1. 继续承担静态验证风险
2. 先补运行环境
3. 缩小本轮范围

用户确认继续后，计数和未验证项仍要写入执行记录。计数在达到 V2/V3 验证后清零。

**计数粒度**：按「已确认并执行的写入 Step」计——一个 Step 内修改多个文件仍计 1；该 Step 达到 V2/V3 则清零，仅有 V1 则 +1。「写入 Step」包括：写文件、改代码、生成 migration/SQL、修改配置、修改测试、执行 DDL/DML、外部系统写操作。

## 非 Git 项目回退保护

如果目标目录不是 Git 仓库，或无法获得可靠 `git status/diff`：

- 写操作前必须说明"无法使用 git 审计/回滚"。
- 列出本 Step 将修改的文件、表、配置或外部对象。
- 给出替代审计方式：before/after 摘要、文件 hash、备份路径或用户确认接受无 git 风险。
- 回滚方式不明确时，不得执行高风险写操作。

## 阻塞恢复安全闸

当任务从 blocked、长时间等待、上下文压缩、线程恢复或用户延迟确认后继续时，不得直接写文件。必须先完成恢复检查：

1. 读取 `change-impact/{需求名称}/_active-state.md`（若存在）、`030-implementation.md` 或 `040-light.md`、`060-preflight.md`、`090-execution-record.md`。
2. 复述当前 pending Step 的编号、目标和计划修改对象。
3. 重新只读检查目标文件/对象当前状态，确认 Step 仍适用。
4. 检查是否出现新的冲突、用户改动、同类改动已完成或风险升级。
5. 判断用户最新消息是否明确匹配 `确认 Step N`。
6. 如果 Step 范围、文件状态或风险等级变化，必须重新给出 Step 说明并等待新的 `确认 Step N`。

如果恢复检查通过且最新用户消息已经明确匹配 `确认 Step N`，该确认可继续有效；如果当前任务被要求"只读/不要执行"，则说明"确认有效但本轮不执行"。不得同时写"无需重新确认"和"继续等待同一个确认"。

等待 `确认 Step N` 期间允许继续只读探索；新发现只能进入 backlog，不能改变当前 Step 范围。如果新发现会改变当前 Step 风险等级，必须重新说明并重新确认。

## 跨会话恢复状态文件

`_active-state.md` 是 Phase 4/5 的轻量恢复检查点，模板见 `templates/_active-state.md`。它用于恢复上下文，不是执行授权。

### 创建和更新触发

- 用户确认写入本需求目录的第一份文档后，创建 `change-impact/{需求名称}/_active-state.md`。
- 每次写入或更新 `000-context-pack.md`、`010-requirements.md`、`020-design.md`、`030-implementation.md`、`040-light.md`、`060-preflight.md`、`090-execution-record.md` 后，更新文档状态。
- 每次准备询问 `确认 Step N` 前，先把 `pending_step`、写入对象、回滚方式、验证方式和 `confirmation_required: true` 写入 `_active-state.md`。
- 每次 Step 成功、失败、跳过、阻塞、验证等级变化或 V1-only 计数变化后，立即更新 `_active-state.md`。
- 任务完成时，将 `current_phase` 标为 `complete`、`pending_step` 标为 `none`、`confirmation_required` 标为 `false`。

### 写入边界

- `_active-state.md` 只能写在当前需求目录：`change-impact/{需求名称}/_active-state.md`。
- 只有用户已确认写入该需求目录后，才可自动维护 `_active-state.md`；只读分析阶段不得偷偷落盘。
- `_active-state.md` 的自动维护只覆盖流程状态，不授权修改源码、SQL、配置、测试、外部系统，也不能替代 `确认 Step N`。
- 如果用户拒绝写执行记录或状态文件，可以继续执行已确认的业务写操作，但最终回复必须标注"恢复状态未写，本轮不可安全自动恢复"。

### 恢复时冲突处理

- `_active-state.md` 与 `090-execution-record.md` 冲突时，以执行记录为准，并把冲突写入 `_active-state.md` 的 `Resume Notes`。
- `_active-state.md` 与当前磁盘文件状态冲突时，以磁盘事实为准；必须重新给出 Step 说明并等待新的 `确认 Step N`。
- Git HEAD 或 diff 与 `_active-state.md` 记录不一致时，标记状态可能过期，对 pending Step 涉及文件重新取证。
- 找到多个 `_active-state.md` 时，按用户指定需求目录优先；用户未指定时，只读列出候选并询问，不自行选择继续写。

## DDL/DML 执行方式

默认方式：**生成脚本，不直接执行**——

1. DDL/DML 写成 SQL 脚本（或 migration 文件）落入 `change-impact/{需求名称}/050-validation/`
2. 同时生成对应回滚脚本
3. 输出人工执行步骤，由用户或 DBA 在外部执行

**生产 DB：默认禁止 Agent 直接执行 DDL/DML。** 除非仓库或团队配置中显式声明允许 Agent 使用生产写连接，否则只走脚本方式。

**非生产环境（dev/staging）的例外路径**，必须同时满足：

- 用户确认文本绑定**目标库 + SQL 文件 + 操作类型**，不只是 `确认 Step N`。格式示例：
  `确认 Step 4,在 staging 库执行 change-impact/xxx/050-validation/004_update_user_status.sql`
- DELETE / UPDATE 先生成并执行只读预检（`SELECT COUNT(*) FROM ... WHERE ...`），把预计影响行数回显给用户后再确认
- 回滚脚本已生成 + 执行记录就绪 + 未命中高风险拦截清单（或命中但已单独确认）

## 执行流程

> **执行 [N/总]: [操作名称]**
> - 维度：[维度]
> - 操作：`[命令或代码]`
> - 影响范围：[描述]
> - 回滚方式：[描述]
> - 语义约定：[已确认定义/不涉及/未确认]
> - 验证方式：[测试/检查命令/手工验收]
>
> 确认执行 `Step N: [操作名称]`？请回复：`确认 Step N` / `跳过 Step N` / 其他指令

- `确认 Step N` -> 执行 -> 自动跑风格检查 + 单测 -> 通过 -> 写执行记录 + 更新 `_active-state.md` -> 下一步
- `跳过 Step N` -> 更新 `_active-state.md` 为跳过，下一步
- 其他 -> 等待指令

确认必须指向当前步骤编号；模糊确认（如"嗯""可以""都行""继续""yes""全部确认"）不得视为写操作确认，需追问具体 Step。

## 验证方案（必须有，按类型选形态）

在 `change-impact/{需求名称}/050-validation/` **必须生成验证方案**：

- 涉及 **UI 流程** -> Playwright E2E 脚本（正向用例 + 错误用例：边界值、空值、格式校验、XSS）
- 涉及 **API** -> curl/httpie/REST Client 脚本或集成测试（验证接口入参出参）
- **纯 DB / 后端** -> SQL 验证脚本（表结构断言、行数核对、数据一致性、外键完整性）

验证命令必须来自项目证据：只有在发现 `pom.xml`/`mvnw`/`build.gradle`/`package.json`/`go.mod`/测试配置等真实入口后，才能写具体编译、测试或运行命令。找不到时写"V2/V3 不可用/需补证据"，不得套用 `mvn`、`npm test`、`go test` 等占位命令。

## 风格合规检查（自动执行）

按设计文档约束跑 grep/Bash：

```
- [ ] 依赖注入符合项目约定（field 或 constructor injection）
- [ ] 日志使用 Slf4j + {} 占位符
- [ ] 不新增重复的自定义异常类
- [ ] Entity 注解在字段上（不在 getter）
- [ ] 分层规范（Controller 不直接调 Repository）
```

栈专属风格项（Go 的 error wrapping、Python 的 type hint、Next.js 的 Server Action 边界等）由 profile 追加。

## 测试失败处理

```
失败 -> 诊断类型：
  编译错误 / 断言失败 / 风格不符 -> 自动诊断，生成修复方案；确认后执行修复，重跑
  超时 / 服务起不来 / 端口占用 -> 环境问题，停止等用户
通过 -> 下一步
```

**任何 Edit/Write/DDL/DML 操作都必须用户确认，不自动执行。**

## 高风险 Step 拦截清单（硬性规则级）

执行任何 Step 前先核对——命中以下任何一项，**禁止执行，必须暂停**，等待用户对该 Step 的显式 `确认 Step N`：

- DROP TABLE / DROP COLUMN / DROP INDEX / DROP CONSTRAINT / TRUNCATE
- 无 WHERE 的 DELETE / UPDATE；有 WHERE 但影响行数未知或过大的批量 DELETE / UPDATE
- ALTER TABLE 影响已有列、约束、索引、默认值、NOT NULL、UNIQUE
- GRANT / REVOKE / 权限角色变更
- CREATE OR REPLACE VIEW / FUNCTION / TRIGGER / PROCEDURE（覆盖已有对象）
- 数据回填、状态迁移、历史数据修正
- 删旧接口 / 删旧 Controller 类 / 删路由；删除公共导出、公共类型、SDK 字段、API response 字段
- 删除文件且无备份
- 修改 status / enum / 错误码 / 权限标识
- 任何不可逆操作（生产 DB DDL、外部系统写操作等）

命中后：

1. Step 说明必须显式标注「高风险/不可逆」及命中条目。
2. 该 Step 必须单独确认，禁止与其他 Step 合并确认。
3. 命中条目、暂停原因和用户确认原文必须写入执行记录。
4. 用户未确认前，只允许继续只读分析。

> **维护注意**：本清单是 SKILL.md 硬性规则 #2 的完整版。两处必须保持同步——改本清单要同步改强制规则区，改强制规则区要同步改本清单。简明版（命中即拦截的清单项）保留在 SKILL.md 强制规则区，详细执行规则（命中后处理 4 步）在本文件。

## 实施步骤的风格约束标签

| 标签 | 含义 | 标签 | 含义 |
|------|------|------|------|
| [Java-实体] | Entity 类约束 | [SQL] | MyBatis XML 格式 |
| [DI] | 依赖注入方式 | [前端] | Vue/Element UI 规范 |
| [日志] | 日志框架与格式 | [安全] | 权限/认证 |
| [异常] | 异常使用规范 | | |

栈专属标签由 profile 追加（Go 的 `[err-wrap]`、Python 的 `[type-hint]`、Next.js 的 `[RSC]` 等）。

## 执行记录

时间戳必须来自真实系统命令输出，不得由模型自行编写（**跨平台命令见 `references/cross-platform-notes.md`**）。

每步追加写入 `change-impact/{需求名称}/090-execution-record.md`（不覆盖历史），格式见 `templates/090-execution-record.md`：

```
## [YYYY-MM-DD HH:MM:SS] Step N: <名称>
- 状态：待确认 / 已确认 / 成功 / 失败 / 跳过
- 确认类型：写文件 / 改代码 / DDL / DML / 配置变更 / 测试修复 / 外部系统写操作
- 维度：<维度>
- 操作对象：<文件 / 表 / 配置键 / 测试 / 外部服务>
- 回滚方式：<描述>
- 用户确认：<确认 Step N / 跳过 Step N / 未确认>
- 执行结果：<摘要>
- 验证结果：通过 / 失败
```

执行记录是 Phase 5 的一部分。写代码、写配置、DDL/DML、测试修复或外部系统写操作执行后，必须在同一个 Step 里追加 `090-execution-record.md`，记录用户确认原文、写入对象、验证等级和未运行验证原因。Step 说明里必须把"追加执行记录"列为本步动作；如果用户只确认代码/配置/测试文件而拒绝执行记录，允许执行已确认写操作，但必须在最终回复中明确标注"执行记录未写，本步记录不完整"，不得宣称 Step 完整完成。

验证脚本和执行记录也属于写入对象。如果需要生成、修改或修复它们，必须纳入当前 Step 的影响范围和目标路径检查；如果验证脚本有错误但用户未确认修复，只能记录为 P2/P1 缺口，不能悄悄修。

## 维护注意

- 硬性规则级安全闸（拦截清单 10 条、必须确认、DB 写禁生产）在 SKILL.md 强制规则区有精简版本。
- 本文件详细规则的修改不影响强制规则区，但反过来——改强制规则区必须同步改本文件对应段。
- 跨平台差异（时间戳、路径、shell）见 `references/cross-platform-notes.md`，不在本文件重复。
