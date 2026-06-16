# 层 2 审计：Profile + Adapter 逐行审

> 2026-06-16 · 基于 layer-audit-plan.md 第二层
> 审计范围：11 个 profiles + 3 个 db-adapters + adapter 选择逻辑专项

---

## 总览

| 分类 | 文件数 | P0 | P1 | P2 |
|------|--------|----|----|-----|
| Profiles | 9 (不含 _schema/_template) | 1 | 29 | 32 |
| db-adapters | 3 | 0 | 0 | 2 (Medium) |
| adapter 选择逻辑 | 1 | 0 | 2 | 3 |
| **合计** | 13 | **1** | **31** | **37** |

---

## 🔴 P0 发现

### P0-1: java-spring-mybatis `db_introspection` 硬编码 mysql.md

**文件**：`skills/impact-pro/profiles/java-spring-mybatis.md`

**问题**：`schema_source` 硬编码指向 `mysql.md`。Spring Boot + MyBatis 项目完全可能连接 PostgreSQL，此时 agent 会加载 MySQL 方言查询（`SHOW CREATE TABLE`、`INFORMATION_SCHEMA.STATISTICS`），在 PG 上直接报错。

**影响范围**：所有使用 java-spring-mybatis profile 但连接非 MySQL 数据库的项目。

**修复建议**：schema_source 改为运行时探测逻辑，或在 profile 中声明 "默认 MySQL，运行时 DB 类型探测可覆盖"。

---

## 🟡 P1 发现

### 跨 Profile 共性问题（系统性）

#### P1-S1: 全部 9 个 profile 缺少 `high_frequency_pattern_check` 键

**影响**：`_schema.md` 定义此键为必填，`_template.md` 有示例值，但 9 个 profile 均未填写。

**涉及文件**：所有 9 个 profile

**修复**：逐 profile 补充此键。

#### P1-S2: 7 个后端 profile 的 `discovery_globs` 缺少 `ui` 键

**影响**：`_schema.md` 新增 `ui` 为必填键。仅 generic.md 和 2 个前端 profile 有此键。后端 profile 应至少写 `ui: []` 表明已考虑。

**涉及文件**：java-spring-mybatis, node-express-prisma, go-gin-gorm, python-fastapi-sqlmodel, dotnet-aspnet-efcore

**修复**：补 `ui: []` 或按栈补充前端 glob。

#### P1-S3: 多 DB profile 的 `db_introspection.schema_source` 未指向 adapter

**影响**：node-express-prisma / go-gin-gorm / dotnet-aspnet-efcore / python-fastapi-sqlmodel 的 `schema_source` 指向代码文件（如 `prisma/schema.prisma`、`models.go`），而非 `db-adapters/` 下的 adapter。Phase 2 Step 2.2 的指令是 "读取 `db-adapters/[dbname].md`"，无法解析代码路径。

**涉及文件**：node-express-prisma, go-gin-gorm, dotnet-aspnet-efcore, python-fastapi-sqlmodel

**修复**：schema_source split 为 `schema_discovery_path`（代码级发现路径）和 `default_db_adapter`（默认 adapter，可被运行时覆盖）。

### 逐 Profile P1 发现

#### java-spring-mybatis

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | discovery_globs 缺 `ui` 键 | `_schema.md` L24 要求 ui 键，profile 无 |
| P1-2 | migration glob `**/*.sql` 过宽 | 匹配所有 SQL 文件，非仅迁移 |
| P1-3 | context_discovery 缺 `high_frequency_pattern_check` | 八键只填七键 |
| P1-4 | limitations 未记录 MySQL 硬编码限制 | schema_source 硬编码 mysql.md 未声明 |
| P1-5 | exclude_patterns 过薄 | 缺少 Maven/Gradle 产物目录 |

P2 问题（5 项）：matchers 含 RuoYi 专属 Druid；style_axes/validation_strategy 多处 RuoYi 模式泄露；commands 的 checkstyle 非通用；Level 2 证据不充分。

#### node-express-prisma

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | discovery_globs 缺 `ui` 键 | profile L31-79 完全缺失 |
| P1-2 | context_discovery 缺 `high_frequency_pattern_check` | profile L83-124 无此键 |
| P1-3 | db_introspection 多数据库盲区 | Prisma 支持 5 种 provider，schema_source 未指引导 adapter 选择 |

P2 问题（6 项）：fastify 在 matchers 但未验收；@prisma/adapter-pg 是 Prisma 7+ 专属；prisma 作为依赖 matcher 是 CLI devDependency；style_axes 格式不合规；exclude_patterns 缺 generated/coverage；validation_strategy 未覆盖 .js。

#### go-gin-gorm

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | matchers 含 RealWorld 示例特有目录 | `users`/`articles` 目录非 Go/Gin/GORM 通用标志 |
| P1-2 | dto 键只覆盖示例特有命名 | 仅 serializers/validators，缺 *dto*/*request*/*response* |
| P1-3 | ui 键完全缺失 | schema 要求 |
| P1-4 | context_discovery 缺 `high_frequency_pattern_check` | 必填键遗漏 |
| P1-5 | db_introspection 未关联 adapter | GORM 支持多 DB 驱动，无 adapter 引导 |
| P1-6 | discovery_globs 含示例特有 glob | `**/common/database.go`/`**/hello.go` |

P2 问题（2 项）：limitations 未记录示例特有匹配器；Level 1 仅在 demo 上验证。

#### python-fastapi-sqlmodel

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | discovery_globs 缺 `ui` 键 | 行 36-78 无此键 |
| P1-2 | context_discovery 缺 `high_frequency_pattern_check` | 行 83-123 |
| P1-3 | db_introspection 未关联 adapter | schema_source 指向代码文件，无运行时 DB 类型引导 |
| P1-4 | validation_strategy grep 覆盖不足 | `table=True` 仅搜 `**/app/models.py`，未覆盖目录结构 |

P2 问题（8 项）：matchers 过于通用；dto 含 models.py 导致 entity/dto 重叠；migration 未覆盖 SQL 脚本；exclude_patterns 缺 Python 构建产物；limitations 缺 async/sync、Pydantic v1/v2、多数据库；file_patterns 缺 schemas。

#### dotnet-aspnet-efcore

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | eShopOnWeb 特化内容未隔离 | `ApplicationCore/**/*.cs` glob 和 `dotnet run --project src/Web` 是项目专属 |
| P1-2 | discovery_globs 缺 `ui` 键 | schema 必需 |
| P1-3 | context_discovery 缺 `high_frequency_pattern_check` | 必填键遗漏 |
| P1-4 | db_introspection 无 adapter 落地 | 依赖暗示 SQL Server，但 db-adapters/ 无 sqlserver.md |
| P1-5 | validation_strategy grep 不通用 | eShopOnWeb 专属模式 |

P2 问题（4 项）。

#### frontend-react-vite

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | discovery_globs dto/ui 重叠 | dto 与 data_access/entity 重复；ui 的 `**/src/**/*.tsx` 过宽 |
| P1-2 | context_discovery 缺 `high_frequency_pattern_check` | 必填键遗漏 |
| P1-3 | Level 1 双变更验收未闭环 | T06 用 generic profile 完成的 light 验收，不构成自身 light 验收证据 |

P2 问题（4 项）：matchers 过于通用；style_axes 新增 schema 未定义轴；limitations 遗漏 CSS-in-JS 等；validation_strategy 遗漏 .test.tsx/.scss。

#### frontend-nextjs

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | matchers 依赖误命中 | react/react-dom/zod/prisma/postgres 五个通用依赖合计 15 分 |
| P1-2 | discovery_globs 分类错误 | `**/app/**/route.ts` 同时出现在 data_access 和 api；api 含 UI 文件 |
| P1-3 | context_discovery 缺 `high_frequency_pattern_check` | 必填键遗漏 |
| P1-4 | db_introspection.schema_source 是散文描述 | 非 db-adapters/ 下的 adapter 引用 |

P2 问题（5 项）：matchers 含通用项；service/ui glob 过宽；style_axes 含 schema 未定义轴；validation_strategy 缺 prisma/styles；Level 描述不一致。

#### frontend-nuxt-vue

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | data_access 的 `**/server/**/*.ts` 过宽 | 与 api 大面积重叠 |
| P1-2 | ui/dto glob 过宽 | `**/app/**/*.vue` 和 `**/*.d.ts` 假阳性高 |
| P1-3 | context_discovery 缺 `high_frequency_pattern_check` | 必填键遗漏 |

P2 问题（5 项）：matchers.files 中 package.json 信号过弱；commands 硬编码 npm；validation_strategy 未覆盖 Nuxt 3 非 app/ 目录；limitations 缺 auto-imports/layer system 等；Level 1 描述不一致。

#### generic

| # | 问题 | 证据 |
|---|------|------|
| P1-1 | `**/*.sql` 三重计数 | data_access/migration/data_models 三处都有 |
| P1-2 | `**/*.yaml`/`**/*.yml` 全覆盖假阳性 | config 和 data_models 重叠 |
| P1-3 | context_discovery 缺 `high_frequency_pattern_check` | 必填键遗漏 |

P2 问题（4 项）：entity/data_access glob 重叠未声明；exclude_patterns 缺 Python/Go 产物；validation_strategy 过空；limitations 未记录已知 glob 坑。

---

## db-adapters 审计

### mysql.md

| 检查项 | 状态 | 说明 |
|--------|------|------|
| foreign_keys 只从 KEY_COLUMN_USAGE 取真实存在的列 | ✅ | 5 列全部存在，已修复 UPDATE_RULE/DELETE_RULE |
| indexes 查询 STATISTICS 视图列名是否 MySQL 真实存在 | ✅ | 全部真实列名 |
| notes 版本兼容说明 | ⚠️ Medium | 缺少 8.0 新增视图/降序索引等说明 |

### postgresql.md

| 检查项 | 状态 | 说明 |
|--------|------|------|
| foreign_keys 用 pg_catalog | ✅ | 使用 pg_constraint + pg_class，信息完整 |
| indexes 覆盖 partial/表达式索引 | ✅ | pg_get_indexdef 返回完整 DDL |
| 与 mysql.md 查询字段语义对齐 | ⚠️ Medium | `not_null` vs `IS_NULLABLE` 语义反转；`is_unique` vs `NON_UNIQUE` 语义反转；foreign_keys 字段结构不同 |

### generic-sql.md

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 通用性诚实声明 | ✅ | indexes=MySQL 专属、foreign_keys=PG 专属声明完整 |
| table_structure 真跨库 | ⚠️ Medium | PG 多 schema 环境下无 `table_schema` 限定，可能返回重复行 |
| 方言声明与实际查询一致 | ✅ | 三种策略各自正确 |

---

## 🔴 专项：Phase 2 adapter 选择逻辑

### 核心发现：schema_source 硬编码优先，无运行时覆盖

Phase 2 文档的 adapter 加载逻辑：

```
Step 2.2: 读取 db-adapters/[dbname].md → 获取 schema_queries / introspection_commands
```

其中 `[dbname]` 完全来自 `profile.db_introspection.schema_source`。

**问题**：
1. Step 2.1 有 DB 类型识别（docker-compose / datasource 配置），但输出**未连接**到 Step 2.2 的 adapter 选择
2. `postgresql.md` 已有 `detection_signals` 字段，但 Phase 2 **未引用**
3. `schema_source` 字段语义不一致：有的写 adapter 文件名，有的写代码路径，有的写动态指令，有的写"不适用"

### Bug 清单

| # | 严重度 | Bug | 影响 |
|---|--------|-----|------|
| B1 | P1 | java-spring-mybatis schema_source 硬编码 mysql.md | Spring Boot 连 PG 时 SQL 全部失败 |
| B2 | P1 | Phase 2 无 "运行时 DB 类型探测覆盖 profile 硬编码" 优先级规则 | 所有 profile |
| B3 | P2 | schema_source 语义不一致（adapter 文件名/代码路径/动态指令/不适用） | 多 DB profile |
| B4 | P2 | Phase 2 无 "无 DB 则跳过 schema 发现" 显式保护 | 前端 profile |
| B5 | P2 | postgresql.md detection_signals 被架空 | 运行时探测机制 |
| B6 | P3 | generic-sql.md 的 fallback 链未定义 | 未知 DB 类型场景 |

### 建议的 Adapter 选择优先级链

```
1. 运行时 DB 类型探测（最高优先级）
   - 来自 Step 2.1: docker-compose.yml / datasource 配置 / 环境变量
   - 来自 db-adapters/*.md 的 detection_signals
   - 来自 MCP 工具运行时探测
   → 确定具体 DB 类型 → 加载 db-adapters/{type}.md

2. Profile schema_source 指向具体 adapter 文件（次优先级）
   - 仅当运行时探测未命中时
   → 按字段值加载

3. Profile schema_source 指向代码路径（第三优先级）
   - 从代码路径推断 DB 类型
   → 推断成功加载对应 adapter，否则回退 generic-sql.md

4. Profile schema_source = "不适用"（跳过）
   - 跳过 adapter 加载和 schema 发现
   - Context Pack 标注 "无 DB 层"

5. 无法确定 → generic-sql.md（兜底）
   - 标注 "DB 类型未确认，generic adapter 可能部分失败"
```

关键修复：
- Step 2.1 的 DB 类型识别结果必须作为 Step 2.2 的输入
- `detection_signals` 字段必须在 Step 2.2 被使用
- `schema_source` 字段需 split 为 `schema_discovery_path` + `default_db_adapter`
- 需显式 "无 DB 跳过" 保护逻辑

---

## 健康度评分

| Profile | P0 | P1 | P2 | 健康度 |
|---------|----|----|-----|--------|
| java-spring-mybatis | 1 | 5 | 5 | 🔴 |
| node-express-prisma | 0 | 3 | 6 | 🟡 |
| go-gin-gorm | 0 | 6 | 2 | 🟡 |
| python-fastapi-sqlmodel | 0 | 4 | 8 | 🟡 |
| dotnet-aspnet-efcore | 0 | 5 | 4 | 🟡 |
| frontend-react-vite | 0 | 3 | 4 | 🟡 |
| frontend-nextjs | 0 | 4 | 5 | 🟡 |
| frontend-nuxt-vue | 0 | 3 | 5 | 🟡 |
| generic | 0 | 3 | 4 | 🟡 |
| mysql.md | 0 | 0 | 1 | 🟢 |
| postgresql.md | 0 | 0 | 1 | 🟡 |
| generic-sql.md | 0 | 0 | 1 | 🟡 |

### 最优先修复项

1. **P0-1**: java-spring-mybatis schema_source 硬编码 mysql.md
2. **P1-S1**: 全部 profile 补 high_frequency_pattern_check（机械操作）
3. **P1-S2**: 后端 profile 补 ui 键（机械操作）
4. **P1-S3**: adapter 选择优先级链写入 Phase 2 文档
5. **P1-S4**: 多 DB profile 的 schema_source 语义修复
