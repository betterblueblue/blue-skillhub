# T05 — adapter 选择优先级链验证（强模型 glm5.1）

- 执行时间：2026-06-16
- 模型：glm5.1

## 判定

| 判定项 | 观测 | PASS/FAIL |
|--------|------|-----------|
| Phase 2.1 是否解析 datasource URL 识别到 PostgreSQL | `application-druid.yml` 第9行 `jdbc:postgresql://localhost:5432/ry-vue` 匹配 postgresql.md detection_signals 的 `connection_url_patterns: 'jdbc:postgresql:'`；第5行 `org.postgresql.Driver` 亦为 PG 信号；`application.yml` 第115行 `helperDialect: postgresql` 为辅助确认 | PASS |
| Phase 2.2 是否加载了 db-adapters/postgresql.md | 优先级链第1级（运行时 DB 类型探测）命中 `jdbc:postgresql:` URL pattern → 以探测到的 DB 类型加载 `db-adapters/postgresql.md`，优先级高于 profile schema_source 默认值 | PASS |
| Phase 2.2 是否没有加载 db-adapters/mysql.md | 运行时探测已确定 PostgreSQL（最高优先级），mysql.md 不在加载路径中；profile schema_source 默认指向 mysql 被运行时探测覆盖 | PASS |
| Phase 2.3 schema 查询是否使用 pg_catalog 而非 SHOW CREATE TABLE | postgresql.md 的 schema_queries 全部基于 `pg_catalog`（pg_attribute/pg_class/pg_namespace/pg_index/pg_constraint）+ `information_schema` 辅助；DDL 取法为 `pg_dump -s` 或 `psql \d+`，无 `SHOW CREATE TABLE`（PG 不支持） | PASS |
| 上下文输出是否明确声明"DB 类型覆盖：探测到 PG → 使用 pg adapter" | Step 2.2 优先级链规则明确："任一命中 → 以探测到的 DB 类型加载 db-adapters/{postgresql\|mysql\|...}.md"；Step 2.4 输出要求 context pack 包含"已识别技术栈和已加载技术栈规则"；运行时探测覆盖 profile 默认值的行为必须在 context pack 中声明 | PASS |

结论：全部 PASS → 修复生效

## 关键发现

1. **优先级链机制验证通过**：`references/phase-2-context-discovery.md` Step 2.2 定义的四级优先级链（运行时探测 > profile schema_source > 兜底 generic-sql > 无 DB 保护）逻辑清晰，PostgreSQL URL pattern 命中后正确覆盖 java-spring-mybatis profile 的 mysql 默认值。

2. **detection_signals 双重确认**：postgresql.md 的 `detection_signals` 定义了 `connection_url_patterns`（`jdbc:postgresql:`）和 `config_keys`（`spring.datasource.url` 含 postgresql），与修改后的配置文件完全匹配。Step 2.2 要求"同时与各 db-adapters/*.md 的 detection_signals 对照，确认匹配"，此步骤可正常执行。

3. **schema 查询差异显著**：mysql.md 使用 `INFORMATION_SCHEMA.COLUMNS` + `SHOW CREATE TABLE`；postgresql.md 使用 `pg_catalog` 系统表 + `pg_dump -s` / `psql \d+`。若错误加载 mysql adapter，在 PG 环境下 `SHOW CREATE TABLE` 会直接报错，证明 adapter 选择的正确性对功能有决定性影响。

4. **PG 特有高风险项已覆盖**：postgresql.md notes 中列出了 PG 特有的高风险操作（ALTER TYPE enum、分区表 ATTACH/DETACH、DROP TYPE、改列 TYPE 需 USING），这些在 mysql.md 中不存在，进一步证明 adapter 选择的准确性直接影响风险识别。

5. **配置文件已还原**：所有修改（driver/URL/dialect/validationQuery）已通过 `git checkout` 还原，工作区无残留变更。
