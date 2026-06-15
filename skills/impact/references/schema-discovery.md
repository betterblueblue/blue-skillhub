# Schema 发现 SQL 查询

> **跨 DB 注意**：以下查询默认使用 MySQL 的 `DATABASE()` 获取当前 schema。在 PostgreSQL 中应替换为 `current_database()` 或 `current_schema()`；在 SQL Server 中替换为 `DB_NAME()`；在 Oracle 中替换为 `SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA')` 或从 `USER_TAB_COLUMNS` 等视图直接查询（Oracle 的 `INFORMATION_SCHEMA` 兼容性有限）。执行前先确认目标数据库类型并选择对应的 schema 函数。

## 完整 schema 发现（有任意 SQL 执行能力时）

- 搜索表：`search_objects({ pattern: "表名关键词" })`
- 表结构（MySQL）：`SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='目标表' AND TABLE_SCHEMA=DATABASE()`
- 表结构（PostgreSQL）：`SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='目标表' AND TABLE_SCHEMA=current_schema()`
- 外键引用（MySQL）：`SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA=DATABASE() AND (REFERENCED_TABLE_NAME='目标表' OR TABLE_NAME='目标表')`
- 外键引用（PostgreSQL）：`SELECT tc.table_name, kcu.column_name, ccu.table_name AS referenced_table_name, ccu.column_name AS referenced_column_name FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.constraint_schema = current_schema() AND (ccu.table_name = '目标表' OR tc.table_name = '目标表')`
- 视图引用（通用）：`SELECT TABLE_NAME, VIEW_DEFINITION FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = [schema函数] AND VIEW_DEFINITION LIKE '%目标表%'`
- 触发器引用（通用）：`SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM INFORMATION_SCHEMA.TRIGGERS WHERE EVENT_OBJECT_TABLE='目标表' OR ACTION_STATEMENT LIKE '%目标表%'`
- 行数估算（MySQL）：`SELECT TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='目标表' AND TABLE_SCHEMA=DATABASE()`
- 行数估算（PostgreSQL）：`SELECT n_live_tup FROM pg_stat_user_tables WHERE relname='目标表'`

## 受限发现（只有表结构类工具时）

用 `mcp__database__describeTable` 拿表结构；其余依赖项标注为缺口。
