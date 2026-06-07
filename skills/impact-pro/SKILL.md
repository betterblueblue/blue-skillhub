---
name: impact-pro
description: 通用（多语言/多栈）变更影响分析 Skill，是 impact 的栈无关升级版。自动探测技术栈、加载专属 profile，按 light/full 两档输出文档并协助执行。仅在以下情况使用：用户显式说 'impact-pro'/'影响分析pro'，或项目非 Java/Spring/MyBatis（如 Node/Python/Go/.NET 等）需要通用影响分析时。Java/Spring/MyBatis 项目默认用 impact。
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, mcp__dbhub__search_objects, mcp__dbhub__execute_sql, mcp__database__search_objects, mcp__database__describeTable
---

> **架构说明**：本文件是通用内核，不含任何栈专属规则。技术栈规则位于 `profiles/`（编程语言/框架），数据库规则位于 `db-adapters/`。Phase 2 自动探测并按需加载。

# ImpactRadar — 通用变更影响分析

## 目标

把模糊的变更意图，通过靶向提问变成证据化的影响分析，自动适配任意技术栈，按 light/full 两档输出文档并协助执行。

## 核心原则

1. **栈无关** — SKILL.md 内核零栈假设，所有栈规则在 `profiles/` 按需读取
2. **证据化分析** — 用工具发现真实上下文，不靠臆测
3. **不替用户拍板** — 提供证据化的影响分析与选项，业务决策交给用户
4. **两档模式** — light 简单改动走一页摘要，full 复杂变更走三文档
5. **可扩展 profile** — 新技术栈只需加一个 profile 文件，无需改本内核
6. **证据不足先标注** — 找不到 schema/API/model/test 时必须写入未确认项，不得用猜测填空
7. **破坏性请求先拦截** — DROP/DELETE/批量重构/删除接口/破坏兼容请求必须先做影响发现和确认，不能直接执行

## 目录结构

```
impact-pro/
├── SKILL.md              # 通用内核（本文件）
├── profiles/             # 技术栈 profile
│   ├── _schema.md        # profile 统一接口定义
│   ├── _template.md      # 新 profile 空白模板
│   ├── generic.md         # 强兜底（任意栈）
│   ├── java-spring-mybatis.md  # Java/Spring/MyBatis profile
│   ├── node-express-prisma.md
│   ├── python-fastapi-sqlmodel.md
│   ├── frontend-react-vite.md
│   ├── frontend-nextjs.md
│   ├── frontend-nuxt-vue.md
│   ├── go-gin-gorm.md
│   └── dotnet-aspnet-efcore.md
├── db-adapters/          # 数据库 adapter
│   ├── generic-sql.md     # 通用 SQL 发现模板
│   └── mysql.md          # MySQL 专用
├── templates/            # 文档模板（复用 impact v3.0）
│   ├── light.md
│   ├── requirements.md
│   ├── design.md
│   └── implementation.md
└── README.md
```

## 自动 / 确认边界

| 类别 | 是否需用户确认 |
|------|----------------|
| 只读搜索、文件扫描、git log/show、grep/lint、单元测试 | **无需确认，自动执行** |
| 写文件、改代码（Edit/Write）、DDL、配置变更 | **必须逐项确认** |

测试失败的任何修复操作（Edit/Write/DDL/DML）都必须用户确认，不自动执行。

## 流程总览

```
Phase 1 意图捕获
   → Phase 2 栈探测 + Profile 加载 + 上下文发现
   → Phase 2.5 判档 + 确认（light / full）
   → Phase 3 苏格拉底式探索（按选中维度提问）
   → Phase 4 文档输出（light：一页摘要 / full：三文档逐份确认）
   → Phase 5 执行与验证（逐操作确认）
```

## Phase 1: 意图捕获

> "你想做什么变更？涉及哪些表/字段/模块都可以，模糊的想法也行。"

等待回复后进入 Phase 2。

## Phase 2: 栈探测 + Profile 加载 + 上下文发现

按顺序执行，不重复。

### Step 2.1: 栈探测

1. 扫描根目录识别技术栈（见 `profiles/_schema.md` 的 `matchers`）：
   - 读 `pom.xml` → Java Maven
   - 读 `build.gradle` → Java Gradle
   - 读 `package.json` → Node.js
   - 读 `go.mod` → Go
   - 读 `requirements.txt` / `pyproject.toml` → Python
   - 读 `Dockerfile` → 容器化项目（识别基础镜像）
   - 读 `docker-compose.yml` → 识别 DB 类型
   - 读 datasource 配置 → 识别 DB 类型

2. 按 `profiles/_schema.md` 的打分机制选出匹配 profile：
   - 高置信命中（依赖命中 + 文件命中）→ 回显一行确认
   - 低置信 / 无命中 → 加载 `profiles/generic.md`
   - 多栈同仓 / monorepo → 列出候选 profile 和目录边界，不强行压成单 profile

3. 向用户确认：
   > "检测到 **[栈名]**，将加载 `profiles/[name].md` 中的专属规则。确认？"

4. 多 profile 场景：
   - 先按变更意图定位主目录（如 `backend/`、`frontend/`、`packages/api/`）
   - 后端 + 前端共同受影响时，同时加载两个 profile
   - 文档中按模块拆分影响范围、实施步骤和验证方案
   - 不允许只分析命中最高的一个 profile 后忽略另一个受影响模块

### Step 2.2: Profile 加载

根据确认结果，Read 对应的 profile 文件：

- 读取 `profiles/[name].md` 获取：
  - `discovery_globs` — 查找哪些文件
  - `style_axes` — 风格观察轴（只给提示，不下结论）
  - `commands` — 构建/测试/启动命令
  - `validation_strategy` — 验证策略

- 读取 `db-adapters/[dbname].md` 获取：
  - `schema_queries` — schema 发现 SQL
  - `introspection_commands` — DB 检查命令

### Step 2.3: 上下文发现（使用 profile 规则）

按 `discovery_globs` 查找相关文件，用 profile 的分析维度扫描代码：

1. 扫描 `discovery_globs` 匹配的文件
2. 按 profile 的 `style_axes` 提取风格特征（只描述，不下结论）
3. 按 db-adapter 的 `schema_queries` 发现数据库 schema
4. 构建上下文地图（影响文件、API 端点、依赖关系）
5. 生成证据账本：
   - **已确认**：文件路径 / 命令输出 / DB 查询 / 测试结果
   - **未确认**：找不到、工具不可用、无权限、需用户决策
   - **禁止推断**：未确认项不得写成事实

**Token 保护**：文件读取上限 20 个，超出提示用户。

### 维度判断（19 维度，Profile 可能已扩展）

根据意图推断涉及维度并交用户确认/调整：

> "根据描述，我推断涉及以下维度：[列表]。请确认或补充。"

## Phase 2.5: 判档 + 确认

依据 Phase 2 发现，给出档位建议并确认：

判档不是按文件数量决定，而是按风险触发条件决定。必须先输出判档证据：

```text
建议档位：[light/full]
允许 light 的证据：[路径/命令/代码]
触发 full 的证据：[路径/命令/代码，若无则写无]
未确认项：[缺失证据/需用户决策]
```

### 允许 light 的条件

同时满足以下条件，才可建议 light：

- 影响面局限：通常只涉及单页面、单组件、单 handler 文案、单测试断言、局部样式、局部配置展示
- 无结构变更：不改 DB schema、migration、实体字段、DTO 结构、OpenAPI/GraphQL 契约、generated client
- 无核心逻辑变更：不改权限、认证、支付、状态机、事务、缓存失效、消息队列、外部服务副作用
- 无破坏兼容：不删除字段/接口/路由，不重命名公开契约，不改变 HTTP status 或错误结构
- 验证闭环简单：可通过局部 lint/test/E2E 或手动 UI 检查验证
- 证据充分：已找到相关文件和测试/命令；未确认项不会影响安全性和兼容性

典型 light：UI placeholder、按钮文案、toast 文案、footer 文案、局部样式/图标、API 自然语言 message、前端本地状态展示、文档或日志文案。

### 必须 full 的条件

出现任一条件，默认建议 full：

- DB schema、migration、索引、唯一约束、外键、存量数据或回填
- API/DTO/OpenAPI/GraphQL 契约变更，或 generated client 需要再生成
- 权限、认证、支付、订单、状态机、审计、风控等高风险业务逻辑
- 跨模块、跨服务、前后端联动、monorepo 多 profile 共同实施
- 缓存、消息队列、异步任务、文件存储、邮件/短信/第三方 API 等外部副作用
- 删除、重命名、DROP、批量替换、破坏兼容、迁移旧接口
- 证据不足但涉及 DB/API/权限/状态机等高风险区域

典型 full：新增表字段并在接口返回；新增状态值并影响状态流转；前端新增入口调用后端 API；修改登录、支付、订单、邀请链接、邮件发送；Next.js Server Action 或 Nuxt server API 涉及写入、缓存刷新或外部依赖。

### 升降档规则

- 用户可以要求从 full 简化输出，但不能跳过破坏性变更发现、证据账本、写操作确认和验证方案
- 用户可以要求 light 升级为 full，以获得三文档和更完整验证
- 当证据不足且风险区域高，必须先按 full 或“暂停并补证据”处理，不能用 light 掩盖未知
- UI-only 变更如果发现 generated client、服务端写入、权限或外部副作用，应立即升级 full

> "这次变更看起来是 **[light / full]**（理由：…）。light 产一页影响摘要后直接执行；full 产三文档。确认走哪档？"

**退出条件**：用户随时说「直接改 / 别写文档 / 简化」，可以简化文档形式，但不能跳过写操作确认和破坏性变更影响发现。

### 破坏性请求安全闸

当用户要求「直接删」「全部替换」「不用分析」「删旧接口」「DROP/RENAME 表字段」「批量重构」时：

1. 不执行写操作
2. 先只读搜索引用和消费者
3. 回显破坏面和未确认项
4. 至少追问兼容期、回滚、消费者、迁移策略
5. 用户确认后仍按 Phase 5 逐项确认执行

## Phase 3: 苏格拉底式探索

按选中维度分组提问，每轮 ≤ 3 题，基于真实上下文，不泛泛而谈。

### 维度分组（Profile 可覆盖）

| 组 | 维度 | 优先级 |
|----|------|--------|
| A | 数据库、代码、接口/契约 | 必问 |
| B | 配置、凭证/密钥、安全/权限 | 高 |
| C | 缓存、存储/文件、消息队列/事件 | 中 |
| D | 其余维度 | 低（按需） |

### 质量底线追问

当变更涉及功能的质量要求空白/模糊时追问：

> "关于 [功能]，有具体质量要求吗？比如格式、样式、交互细节，还是与现有同类功能保持一致即可？"

### 风险靶向追问（按发现触发）

- **DROP/RENAME**：发现 N 个文件引用，删除/重命名后会报错，是否需过渡期/别名？
- **多表外键**：[表A] 被外键引用，是否级联？
- **存量数据**：该表 N 行，现有数据如何处理？是否需迁移脚本？
- **API 破坏**：发现 [path] 返回此字段，现有消费者是否中断？
- **缓存**：N 个缓存 Key 存此数据，失效策略？
- **消息队列**：变更会发布到 [Topic]，消费者是否受影响？
- **版本兼容**：N 个版本消费者，是否需同时更新？
- **证据不足**：未找到合法值/状态枚举/schema/test，是否提供约定或允许我继续查证？
- **DB 无权限**：当前只能从代码/迁移推断 schema，是否提供连接或接受未确认标注？

### 停止条件

关键风险已覆盖；用户说「够了/输出吧」；超 5 轮未收敛则主动提议输出已确认信息。

### 决策点

> "需求已较清晰。现在输出文档？将写入 `change-impact/{需求名称}/`。"

## Phase 4: 文档输出

目录结构：

```
change-impact/{需求名称}/
├── requirements.md          # full
├── design.md              # full
├── implementation.md       # full
├── light.md               # light
├── 300-验证脚本/          # E2E / API / SQL 验证
└── 900-执行记录.md        # 时间戳追加
```

- **light** → `templates/light.md`，一页输出，确认后直接进 Phase 5
- **full** → `templates/requirements.md` → `design.md` → `implementation.md`，**每份确认后再出下一份**

**文件名合规化**：空格→下划线，去特殊字符，≤ 50 字符。

### 设计文档的「代码风格报告」

每个风格项基于 profile 的 `style_axes` 提取，附**完整、未截断**的参考代码片段。

### 证据账本与未确认项

每份文档必须包含：

- 已确认事实：路径、命令、DB 查询或测试证据
- 未确认项：缺失文件、无权限、命令不可用、业务决策空白
- 不采用的推断：说明为什么不把猜测写入方案

涉及前端-only 变更时，不生成数据库实施步骤；涉及 DB 但无 DB 权限时，不声称已确认行数、索引、外键。

### 设计原则约束（写进设计文档）

- **简单优先**：不添加用户未要求的功能，不做推测性设计
- **精准修改**：只改必须改的文件，不"改进"相邻代码
- **质量底线**：最小改动 ≠ 最低质量；变更范围内功能须达项目同等质量标准

## Phase 5: 执行与验证

用户确认文档后进入。**所有「写类」操作逐项确认。**

### 执行流程

> **执行 [N/总]: [操作名称]**
> - 维度：[维度]
> - 操作：`[命令或代码]`
> - 影响范围：[描述]
> - 回滚方式：[描述]
>
> 确认执行？(yes / no / 其他指令)

- `yes` → 执行 → 自动跑静态检查 + 单测 → 通过 → 写执行记录 → 下一步
- `no` → 跳过，下一步
- 其他 → 等待指令

### 验证方案（必须有，按类型选形态）

在 `change-impact/{需求名称}/300-验证脚本/` 必须生成：

- 涉及 **UI 流程** → Playwright E2E 脚本（正向用例 + 错误用例）
- 涉及 **API** → curl/httpie/REST Client 脚本或集成测试
- **纯 DB / 后端** → SQL 验证脚本（表结构断言、行数核对、数据一致性）

### 风格合规检查（自动执行）

按 profile 的 `style_axes` 和 `validation_strategy` 跑 grep/Bash 检查。

### 测试失败处理

```
失败 → 诊断类型：
  编译错误 / 断言失败 / 风格不符 → 自动诊断，生成修复方案；确认后执行修复，重跑
  超时 / 服务起不来 / 端口占用 → 环境问题，停止等用户
通过 → 下一步
```

**任何 Edit/Write/DDL/DML 操作都必须用户确认。**

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

- **栈无关** — 本内核不含任何栈假设，所有规则来自 profile
- **影响分析须证据化** — 基于真实文件/代码/DB，不臆测
- **不替用户拍板** — 给分析与选项，业务决策交用户
- **输出语言跟随用户** — 中文问中文答，英文问英文答
- **full 模式逐份确认文档，所有写操作逐项确认**
- **可随时降档** — 用户要简化就简化，不硬走三文档
- **测试失败先诊断** — 诊断自动，修复必须确认
