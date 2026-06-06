---
name: impact
description: 苏格拉底式变更澄清与实施。把模糊的变更意图变成证据化的影响分析，light/full 两档输出，统一写入 change-impact/ 目录并协助执行。Use when user says '我想改一下', '改个字段', '删张表', '影响分析', '变更需求', '加个功能', '重构', 'impact'.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, mcp__dbhub__search_objects, mcp__dbhub__execute_sql, mcp__database__search_objects, mcp__database__describeTable

> **MCP 能力说明**：只有 DBHub MCP 有 `execute_sql`；Database MCP（Bytebase MCP 等）只有 `describeTable`，无 `execute_sql`。正文描述已按此区分。

---

# ImpactRadar — 苏格拉底式变更澄清与实施

## 目标

把模糊的变更意图，通过靶向提问变成**证据化的影响分析**，并据此输出文档、协助执行。

## 核心原则

1. **先想清楚，再动手** — 通过靶向提问暴露盲区
2. **影响分析必须基于真实证据** — 用工具发现真实 schema/代码，不靠臆测
3. **不替用户拍板** — 提供证据化的影响分析与选项，业务决策交给用户
4. **两档模式** — light 简单改动走一页摘要，full 复杂变更走三文档
5. **维度按需覆盖** — 19 维度灵活选择，不强制全覆盖

## 自动 / 确认边界

| 类别 | 是否需用户确认 |
|------|----------------|
| 只读搜索、schema 发现、`git log/show`、本地静态检查（grep/编译/lint）、单元测试 | **无需确认，自动执行** |
| 写文件/生成文档、改代码（Edit/Write）、DDL、配置变更、任何对外部系统的写操作 | **必须逐项确认** |

测试失败的自动修复**仅限于自动类别内的动作**（重跑检查、改尚未确认的草稿）；一旦修复需要改动已确认/已落地的代码，回到「必须确认」。

## 流程总览

```
Phase 1 意图捕获
   → Phase 2 上下文发现（MCP 能力探测 + 代码搜索 + 风格分析）
   → Phase 2.5 判档 + 确认（light / full）
   → Phase 3 苏格拉底式探索（按选中维度提问）
   → Phase 4 文档输出（light：一页摘要 / full：三文档逐份确认）
   → Phase 5 执行与验证（逐操作确认）
```

## Phase 1: 意图捕获

> "你想做什么变更？涉及哪些表/字段/模块都可以，模糊的想法也行。"

等待回复后进入 Phase 2。

## Phase 2: 上下文发现

静默使用工具发现上下文。**不臆测，只基于发现的证据。**

### MCP 能力探测

先探测工具可用性，再决定能做什么：

1. 尝试 `mcp__dbhub__search_objects` 或 `mcp__database__search_objects`
2. 判断是否有 `execute_sql`：
   - **有 `execute_sql`** → 走「完整 schema 发现」
   - **只有 `describeTable`** → 走「受限发现」：仅表结构；视图/触发器/外键/行数标注为「不可自动发现，需人工补充」
   - **两者都不可用** → 告知用户降级为纯代码搜索模式，询问是否继续

### 完整 schema 发现

- 搜索表：`search_objects({ pattern: "表名关键词" })`
- 表结构：`SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='目标表' AND TABLE_SCHEMA=DATABASE()`
- 外键引用：`SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA=DATABASE() AND (REFERENCED_TABLE_NAME='目标表' OR TABLE_NAME='目标表')`
- 视图引用：`SELECT TABLE_NAME, VIEW_DEFINITION FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA=DATABASE() AND VIEW_DEFINITION LIKE '%目标表%'`
- 触发器引用：`SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM INFORMATION_SCHEMA.TRIGGERS WHERE EVENT_OBJECT_TABLE='目标表' OR ACTION_STATEMENT LIKE '%目标表%'`
- 行数估算：`SELECT TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='目标表' AND TABLE_SCHEMA=DATABASE()`

### 受限发现

用 `mcp__database__describeTable` 拿表结构；其余依赖项标注为缺口。

### 代码引用发现

1. MyBatis XML：`Grep` 搜索表名在 `**/*.xml`
2. JPA/Entity：`Grep` 搜索表名在 `**/*.java`
3. Service/Repository/Mapper：`Grep` 搜索在 `**/*Service*.java`、`**/*Repository*.java`、`**/*Mapper*.java`
4. Controller：`Grep` 搜索在 `**/*Controller*.java`
5. 配置文件：`Grep` 搜索 `**/application*.yml`、`**/application*.properties`
6. 对关键文件使用 `Read` 了解使用方式

### 代码风格分析

**基础层（始终执行，Git 可用时优先）**：
- Git 可用：
  1. `git log --oneline -20 -- <module_path>` 获取 commit 列表
  2. 对每条 commit 先跑 `git show --stat <hash>` 预筛：跳过无关 commit（如仅改文档/配置的 commit）
  3. 对筛选后的 commit 跑 `git show <hash>` 取 diff，**每条 diff 限制 ≤ 200 行**，超出则截断并记录
  4. 从 diff 中提取：类/方法命名、Lombok 使用、依赖注入方式、`@Transactional` 位置、异常风格、日志框架+占位符、API 响应包装、分层模式、DTO/VO 使用
- Git 不可用：扫描代表性文件（Service/Controller/Entity/Config 各 1-2 个）+ `.editorconfig`/`checkstyle`/`pmd`
- **Token 上限**：≤ 20 条 diff（每条 ≤ 200 行）或 ≤ 6 个文件，超出提示用户

**深入层（仅本次涉及的维度，每维度 ≤ 3 文件）**：代码、数据库、接口、配置、日志、事务、安全、测试、包结构、空值处理、常量定义、时间处理等。

提取内容：命名规范、Lombok 使用、依赖注入方式、`@Transactional` 位置、异常风格、日志框架+占位符、API 响应包装、分层模式、DTO/VO 使用。

### 维度判断

根据意图推断涉及维度并交用户确认/调整：

| 维度 | 触发场景 |
|------|---------|
| 数据库 | 表/字段/索引/约束 |
| 代码 | 逻辑/函数/类/模块 |
| 配置 | 参数/开关/环境变量 |
| 接口/契约 | API/Request/Response |
| 消息队列/事件 | Kafka/MQ/Topic/Event |
| 缓存 | Cache/Redis/KV |
| 基础设施 | Docker/K8s/CI |
| 前端 | 页面/组件/交互 |
| 文档/注释 | 文档/README/Changelog |
| 监控/告警 | 指标/告警/Dashboard |
| 测试/用例 | 测试/用例 |
| 日志/埋点 | 日志/埋点/上报 |
| 凭证/密钥 | 密码/Key/证书 |
| 网络/路由 | DNS/端口/负载均衡 |
| 存储/文件 | S3/OSS/文件/Blob |
| 安全/权限 | 权限/RBAC/Auth |
| 版本兼容性 | 版本/向后兼容 |
| 事务/一致性 | 事务/分布式锁 |
| 依赖包/SDK | 依赖/库/版本升级 |

### 构建上下文地图（= 最小改动基准）

从发现结果中梳理：直接影响的表/列/文件、间接影响（外键/视图/JOIN）、读写该数据的代码、暴露该数据的 API、依赖的业务逻辑、相关配置/缓存 Key/监控指标。

**最小改动原则（Phase 2 内嵌）**：只记录本次变更涉及的范围，不主动扩大。

## Phase 2.5: 判档 + 确认

依据 Phase 2 发现，给出档位建议并确认：

- **light（默认）**：单表/单字段、无外键级联、无存量数据风险、无 API 破坏。→ 一页影响摘要，确认后直接执行
- **full（复杂）**：多表/外键级联、有存量数据、破坏 API 兼容、跨多个维度。→ 三文档（需求→设计→实施）

> "这次变更看起来是 **[light / full]**（理由：…）。light 产一页影响摘要后直接执行；full 产三文档。确认走哪档？"

**退出条件**：用户随时说「直接改 / 别写文档 / 简化」，立即降级为 light 或纯执行。

## Phase 3: 苏格拉底式探索

按选中维度分组提问，每轮 ≤ 3 题，基于真实上下文，不泛泛而谈。

### 维度分组

| 组 | 维度 | 优先级 |
|----|------|--------|
| A | 数据库、代码、接口/契约 | 必问 |
| B | 配置、凭证/密钥、安全/权限 | 高 |
| C | 缓存、存储/文件、消息队列/事件 | 中 |
| D | 其余维度 | 低（按需） |

### 质量底线追问

当变更涉及功能的质量要求空白/模糊时追问：

> "关于 [功能]，有具体质量要求吗？比如导出格式、显示样式、交互细节，还是与现有同类功能保持一致即可？"

### 风险靶向追问（按发现触发）

- **DROP/RENAME**：发现 N 个文件引用，删除/重命名后会报错，是否需过渡期/别名？API 返回此字段，现有消费者是否中断？
- **多表外键**：[表A] 被 [B/C/D] 外键引用，是否级联？
- **存量数据**：该表 N 行，现有数据如何处理？是否需迁移脚本？
- **视图/存储过程**：N 个引用此表，是否同步更新？
- **业务逻辑**：Service `[X]` 用此字段做 [逻辑]，是否受影响？
- **缓存**：N 个缓存 Key 存此数据，失效策略？
- **消息队列**：变更会发布到 [Topic]，消费者是否受影响？
- **版本兼容**：N 个版本消费者，是否需同时更新？

### 停止条件

关键风险已覆盖；用户说「够了/输出吧」；超 5 轮未收敛则主动提议输出已确认信息。

### 决策点

> "需求已较清晰。现在输出文档？将写入 `change-impact/{需求名称}/`。"

## Phase 4: 文档输出

目录结构：

```
change-impact/{需求名称}/
├── 000-需求文档.md       # full
├── 100-设计文档.md       # full
├── 200-实施文档.md       # full
├── light-影响摘要.md     # light
├── 300-验证脚本/         # E2E 或 SQL/集成验证
└── 900-执行记录.md       # 时间戳追加
```

文件名合规化：空格→下划线，去特殊字符，≤ 50 字符。

- **light** → 用 `templates/light-影响摘要.md`，一页输出，确认后直接进 Phase 5
- **full** → 用 `templates/000-需求文档.md` → `100-设计文档.md` → `200-实施文档.md`，**每份确认后再出下一份**

### 设计文档的「代码风格报告」

每个风格项附**完整、未截断**的参考代码片段（截断片段如 `@Autowired priv...` 不可用）。

### 设计原则约束（写进设计文档）

- **简单优先**：不加用户未要求的功能，不做推测性设计
- **精准修改**：只改必须改的文件，不「顺手改进」相邻代码
- **质量底线**：最小改动 ≠ 最低质量；变更范围内功能须达项目同等质量标准

## Phase 5: 执行与验证

用户确认文档后进入。**所有「写类」操作逐项确认（见自动/确认边界）。**

### 执行流程

> **执行 [N/总]: [操作名称]**
> - 维度：[维度]
> - 操作：`[命令或代码]`
> - 影响范围：[描述]
> - 回滚方式：[描述]
>
> 确认执行？(yes / no / 其他指令)

- `yes` → 执行 → 自动跑风格检查 + 单测 → 通过 → 写执行记录 → 下一步
- `no` → 跳过，下一步
- 其他 → 等待指令

### 验证方案（必须有，按类型选形态）

在 `change-impact/{需求名称}/300-验证脚本/` **必须生成验证方案**：

- 涉及 **UI 流程** → Playwright E2E 脚本（正向用例 + 错误用例：边界值、空值、格式校验、XSS）
- 涉及 **API** → curl/httpie/REST Client 脚本或集成测试（验证接口入参出参）
- **纯 DB / 后端** → SQL 验证脚本（表结构断言、行数核对、数据一致性、外键完整性）

### 风格合规检查（自动执行）

按设计文档约束跑 grep/Bash：
```
- [ ] 依赖注入符合项目约定（field 或 constructor injection）
- [ ] 日志使用 Slf4j + {} 占位符
- [ ] 不新增重复的自定义异常类
- [ ] Entity 注解在字段上（不在 getter）
- [ ] 分层规范（Controller 不直接调 Repository）
```

### 测试失败处理

```
失败 → 诊断类型：
  编译错误 / 断言失败 / 风格不符 → 自动诊断，生成修复方案；确认后执行修复，重跑
  超时 / 服务起不来 / 端口占用 → 环境问题，停止等用户
通过 → 下一步
```

**任何 Edit/Write/DDL/DML 操作都必须用户确认，不自动执行。**

### 实施步骤的风格约束标签

| 标签 | 含义 | 标签 | 含义 |
|------|------|------|------|
| [Java-实体] | Entity 类约束 | [SQL] | MyBatis XML 格式 |
| [DI] | 依赖注入方式 | [前端] | Vue/Element UI 规范 |
| [日志] | 日志框架与格式 | [安全] | 权限/认证 |
| [异常] | 异常使用规范 | | |

### 执行记录

每步追加写入 `change-impact/{需求名称}/900-执行记录.md`（不覆盖历史）：

```
## [YYYY-MM-DD HH:MM:SS] Step N: <名称>
- 状态：成功 / 失败
- 维度：<维度>
- 命令：<命令>
- 测试结果：通过 / 失败
- 修复记录（如有）：…
```

## 行为准则

- **影响分析须证据化** — 基于真实 schema/代码，不臆测
- **不替用户拍板** — 给分析与选项，业务决策交用户
- **输出语言跟随用户** — 中文问中文答，英文问英文答
- **full 模式逐份确认文档，所有写操作逐项确认**（见自动/确认边界）
- **维度按需，不强制 19 维全覆盖**
- **可随时降档** — 用户要简化就简化，不硬走三文档
- **测试失败先诊断** — Bug 自修（守边界），环境/设计问题停等用户
