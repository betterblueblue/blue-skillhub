# PostgreSQL DB Adapter

> 适用于 PostgreSQL 10+。Phase 2 探测到 PG（连接串含 `postgresql://` / `jdbc:postgresql`，或 ORM 配置 dialect 为 `postgresql`/`psql`）时加载本 adapter。PG 与 MySQL 的关键差异:**无 SHOW CREATE TABLE**(用 `pg_dump -s` 或 `\d`)、**行数是估算值**(reltuples)、**有 schema 命名空间**、**enum/部分索引/表达式索引是独立对象**。

## detection_signals

```yaml
detection_signals:
  connection_url_patterns:
    - 'postgresql://'
    - 'jdbc:postgresql:'
  config_keys:
    - 'spring.datasource.url' (含 postgresql)
    - 'DATABASE_URL' (含 postgresql)
    - 'sqlalchemy.url' / 'DATABASE_URL' (含 postgresql)
    - prisma schema 'provider = "postgresql"'
    - typeorm 'type: "postgres"'
  cli: 'psql'
```

## schema_queries

> 目标表名替换 `目标表`。所有查询限定 `current_schema()`(或显式 `public` / 自定义 schema)以避开命名空间歧义。优先 `pg_catalog`(信息最全),辅以 `information_schema`。

```yaml
schema_queries:
  table_structure: |
    -- 列 + 类型 + NOT NULL + 默认值 + 注释(pg_catalog,最全)
    SELECT
      a.attname AS column_name,
      format_type(a.atttypid, a.atttypmod) AS data_type,
      a.attnotnull AS not_null,
      pg_get_expr(d.adbin, d.adrelid) AS column_default,
      col_description(a.attrelid, a.attnum) AS comment,
      (a.attidentity <> '') AS is_identity
    FROM pg_attribute a
    JOIN pg_class c  ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
    WHERE c.relname = '目标表'
      AND n.nspname = current_schema()
      AND a.attnum > 0 AND NOT a.attisdropped
    ORDER BY a.attnum

  indexes: |
    -- 索引(含 partial WHERE / 表达式索引 / 覆盖列,pg_get_indexdef 看完整定义)
    SELECT
      i.relname AS index_name,
      pg_get_indexdef(ix.indexrelid) AS index_def,
      ix.indisunique  AS is_unique,
      ix.indisprimary AS is_primary,
      am.amname AS index_method
    FROM pg_index ix
    JOIN pg_class cl ON cl.oid = ix.indrelid
    JOIN pg_class i  ON i.oid  = ix.indexrelid
    JOIN pg_namespace n ON n.oid = cl.relnamespace
    JOIN pg_am am ON am.oid = i.relam
    WHERE cl.relname = '目标表' AND n.nspname = current_schema()

  foreign_keys: |
    -- 外键(含 ON DELETE/UPDATE 动作,pg_get_constraintdef 给人读定义)
    SELECT
      con.conname AS constraint_name,
      cl.relname  AS table_name,
      cl2.relname AS referenced_table,
      pg_get_constraintdef(con.oid) AS fk_def
    FROM pg_constraint con
    JOIN pg_class cl  ON cl.oid  = con.conrelid
    JOIN pg_class cl2 ON cl2.oid = con.confrelid
    JOIN pg_namespace n ON n.oid = cl.relnamespace
    WHERE con.contype = 'f'
      AND n.nspname = current_schema()
      AND (cl.relname = '目标表' OR cl2.relname = '目标表')

  views: |
    SELECT schemaname, viewname, definition
    FROM pg_views
    WHERE schemaname = ANY (current_schemas(false))
      AND (viewname = '目标表' OR definition ILIKE '%目标表%')

  triggers: |
    -- 触发器(pg_get_triggerdef 看完整定义,排除系统内部触发器)
    SELECT
      t.tgname AS trigger_name,
      c.relname AS table_name,
      pg_get_triggerdef(t.oid) AS trigger_def,
      t.tgenabled AS enabled
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE NOT t.tgisinternal
      AND n.nspname = current_schema()
      AND c.relname = '目标表'

  table_rows: |
    -- ⚠ 估算值(reltuples,由 ANALYZE 更新),非精确。精确行数需 COUNT(*),生产大表慎用。
    SELECT c.reltuples::bigint AS estimated_rows,
           pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = '目标表' AND n.nspname = current_schema()

  all_tables: |
    -- 所有用户表(relkind 'r'=普通表,'p'=分区表)
    SELECT n.nspname AS schema_name,
           c.relname AS table_name,
           c.relkind,
           c.reltuples::bigint AS estimated_rows,
           obj_description(c.oid) AS comment
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r','p')
      AND n.nspname NOT IN ('pg_catalog','information_schema')
      AND n.nspname NOT LIKE 'pg_toast%'
    ORDER BY n.nspname, c.relname

  enum_types: |
    -- PG 的 enum 是独立对象(改 enum 值=高风险 ALTER TYPE)
    SELECT t.typname AS enum_name,
           string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) AS values
    FROM pg_type t
    JOIN pg_enum e ON e.enumtypid = t.oid
    JOIN pg_namespace n ON n.oid = t.typnamespace
    WHERE n.nspname = current_schema()
    GROUP BY t.typname

  ddl: |
    # PostgreSQL 没有 SHOW CREATE TABLE。取建表 DDL 的方式:
    # 1) pg_dump 导出 schema(推荐,产出可执行 CREATE TABLE):
    pg_dump -U user -d database -s -t '目标表'      # -s = schema-only
    # 2) psql 元命令(交互式,看结构/索引/约束/注释):
    \d+ 目标表
    # 3) 无 shell 时:用上面 table_structure + indexes + foreign_keys 自行拼装
```

## introspection_commands

```yaml
introspection_commands:
  psql: |
    # 直连检查
    psql -U user -d database -c "SELECT 1"
    # 列出表
    psql -U user -d database -c "\dt"
    # 表结构(列/类型/索引/约束/注释)
    psql -U user -d database -c "\d+ 目标表"
    # 导出某表 DDL
    psql -U user -d database -c "\d+ 目标表"
  docker: |
    docker exec -it container_name psql -U user -d database
  dump: |
    # 整库 schema-only(全量影响面分析时用)
    pg_dump -U user -d database -s -n public
```

## notes

```yaml
notes:
  limitations:
    - 'PG 无 SHOW CREATE TABLE,DDL 证据须用 pg_dump -s 或 psql \d 取(影响 DDL 证据收集方式)'
    - 'table_rows 是 reltuples 估算值(由 ANALYZE 更新),非精确;精确行数需 COUNT(*),生产大表慎用'
    - 'PG 有 schema 命名空间(不止 database):查询须限定 nspname(current_schema()/public/自定义);search_path 影响裸表名解析,跨 schema 同名表易混淆'
    - '部分索引(partial WHERE)、表达式索引、覆盖索引(INCLUDE)只能靠 pg_get_indexdef 看完整定义,information_schema 看不全'
    - '标识列:serial/bigserial 与 GENERATED AS IDENTITY 都在 column_default 里表现为 nextval(...)——新增可空列安全,但改既有标识列是高风险'
    - '分区表 relkind=p,分区键在 pg_partitioned_table;ALTER 分区表影响面含所有子分区,必须当 full'
    - 'enum 是独立对象(pg_type + pg_enum):增 enum 值=ALTER TYPE ADD VALUE(PG12+ 事务内不能,需额外注意);删/改 enum 值需重写数据,极高风险'
  high_risk_pg_specific:
    - 'ALTER TYPE (enum) ADD/RENAME/REMOVE VALUE —— 删/改值需重写依赖列,不可逆'
    - 'ALTER TABLE ATTACH/DETACH PARTITION —— 影响查询路由与数据归属'
    - 'DROP TYPE —— 连带所有用该类型的列失效'
    - '改列 TYPE(如 varchar→int)需 USING 转换,失败即全表受阻'
```
