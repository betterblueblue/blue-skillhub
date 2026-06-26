# MySQL DB Adapter

> 适用于 MySQL 5.7+ / MySQL 8.0。

## schema_queries

```yaml
schema_queries:
  table_structure: |
    SELECT
      COLUMN_NAME,
      DATA_TYPE,
      COLUMN_TYPE,
      IS_NULLABLE,
      COLUMN_DEFAULT,
      COLUMN_COMMENT,
      EXTRA
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '目标表'
      AND TABLE_SCHEMA = DATABASE()
    ORDER BY ORDINAL_POSITION

  indexes: |
    SELECT
      INDEX_NAME,
      COLUMN_NAME,
      NON_UNIQUE,
      INDEX_TYPE,
      COMMENT
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_NAME = '目标表'
      AND TABLE_SCHEMA = DATABASE()
    ORDER BY INDEX_NAME, SEQ_IN_INDEX

  foreign_keys: |
    SELECT
      TABLE_NAME,
      COLUMN_NAME,
      REFERENCED_TABLE_NAME,
      REFERENCED_COLUMN_NAME,
      CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
      AND (REFERENCED_TABLE_NAME = '目标表' OR TABLE_NAME = '目标表')
      AND REFERENCED_TABLE_NAME IS NOT NULL

  views: |
    SELECT
      TABLE_NAME,
      VIEW_DEFINITION
    FROM INFORMATION_SCHEMA.VIEWS
    WHERE TABLE_SCHEMA = DATABASE()
      AND VIEW_DEFINITION LIKE '%目标表%'

  triggers: |
    SELECT
      TRIGGER_NAME,
      EVENT_OBJECT_TABLE,
      ACTION_TIMING,
      EVENT_MANIPULATION,
      ACTION_STATEMENT,
      CREATED
    FROM INFORMATION_SCHEMA.TRIGGERS
    WHERE EVENT_OBJECT_TABLE = '目标表'
       OR ACTION_STATEMENT LIKE '%目标表%'

  table_rows: |
    SELECT TABLE_ROWS
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = '目标表'
      AND TABLE_SCHEMA = DATABASE()

  all_tables: |
    SELECT TABLE_NAME, TABLE_COMMENT, TABLE_ROWS
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME

  ddl: |
    SHOW CREATE TABLE 目标表
```

## introspection_commands

```yaml
introspection_commands:
  mysql_cli: |
    # 直连检查
    mysql -u user -p -D database -e "SELECT 1"
    # 导出表结构
    mysqldump -u user -p -d database table_name
  docker: |
    # 容器内执行
    docker exec -it container_name mysql -u user -p -D database
```

## notes

```yaml
notes:
  limitations:
    - INFORMATION_SCHEMA 查询对大表可能较慢，行数是估算值
    - MySQL 5.7 不支持 CHECK 约束的详细信息查询
    - 触发器 ACTION_STATEMENT 长度受限
```
