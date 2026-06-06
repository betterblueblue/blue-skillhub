# Generic SQL Adapter

> 通用 SQL 发现模板。无法确定 DB 类型时使用此 adapter。

## schema_queries

```yaml
schema_queries:
  table_structure: |
    -- 通用表结构查询（适配 MySQL/PostgreSQL）
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = '目标表'
    ORDER BY ordinal_position

  indexes: |
    -- 索引信息
    SELECT index_name, column_name, non_unique
    FROM information_schema.statistics
    WHERE table_name = '目标表'
    ORDER BY index_name, seq_in_index

  foreign_keys: |
    -- 外键引用
    SELECT
      tc.table_name, kcu.column_name,
      ccu.table_name AS referenced_table,
      ccu.column_name AS referenced_column
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
    WHERE tc.table_name = '目标表' AND tc.constraint_type = 'FOREIGN KEY'
```

## introspection_commands

```yaml
introspection_commands:
  cli_check: |
    # 检查是否可直连数据库
    # mysql -u user -p -h host -D database -e "SELECT 1"
    # psql -u user -h host -d database -c "SELECT 1"
  orm_check: |
    # 检查 ORM 配置文件确定数据库类型
    # application.yml / application.properties 中的 spring.datasource.url
```

## notes

```yaml
notes:
  limitations:
    - 无 execute_sql 时仅能查询表结构，无法运行数据验证 SQL
    - 外键/视图/触发器依赖具体 DB dialect，可能不兼容
    - 行数统计需 DB-specific SQL
```
