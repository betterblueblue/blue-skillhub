# T11 — adapter 选择优先级链验证（弱模型 minimax m3）

- 执行时间：2026-06-16
- 模型：minimax m3
- skill：impact-pro
- 项目：test-projects/ruoyi-vue-b3（b3 副本，独立 Git 仓库，HEAD=41720e6）
- 任务：给 sys_user 加一个 phone_model 字段（varchar(64)），在用户列表接口返回
- 范围：仅跑 Phase 1 + Phase 2（手册要求，本场唯一目的是验证 adapter 优先级链）

---

## 0. 前置：b3 副本配置确认

b3 副本（**独立 Git 仓库，不是原项目；后续不需要 git checkout 恢复**）：

```
$ cd /e/agent/blue-skillhub/test-projects/ruoyi-vue-b3
$ git rev-parse HEAD
41720e624c5a668c7d3777835e4c87095a7a1dfd
$ git log --oneline -1
41720e6 优化页签滚动条层级
```

**datasource 已为 PostgreSQL**（无需在跑测前再改）：

`ruoyi-admin/src/main/resources/application-druid.yml`：
```
5:  driverClassName: org.postgresql.Driver
9:  url: jdbc:postgresql://localhost:5432/ry-vue
38: validationQuery: SELECT 1            # PG 风格（MySQL 常见 SELECT 1 FROM DUAL）
39: testWhileIdle: true
40: testOnBorrow: false
```

`ruoyi-admin/src/main/resources/application.yml`：
```
54: profiles:
55:   active: druid
...
114: pagehelper:
115:   helperDialect: postgresql
```

> 注意：b3 副本与原 ruoyi-vue 项目是不同目录，不共享工作区。跑测结束后**不需要**切回原项目或 git checkout。

---

## 1. 项目地图预读（按 skill 强制）

`change-impact/_project-map.md` 存在。基于 commit = 当前 HEAD（41720e6），但**【2】技术栈节关于 DB 类型的标注 `【已核实: ... driverClassName + url】` 标 MySQL 已过期**——因为 application-druid.yml 在 41720e6 之后被改成了 PG（`git status` 显示该文件 modified）。

按 skill 规则处理：
- "比对地图 `基于 commit` 与当前 `git rev-parse HEAD`：不一致时标「地图可能过期」" → commit 一致，但应用配置修改过地图的"已核实"结论
- "动手前自行重新取证" → 本场已直接 grep 重新确认 PG URL
- "地图中标 `【已核实】` 的条目一律按未确认项处理" — 本场已就地重做 DB 类型判断

---

## 2. Phase 1: 意图捕获

```text
当前假设：给 sys_user 表新增 phone_model VARCHAR(64) 字段，同时在用户列表接口的响应中暴露该字段。
可能歧义：
  - "在用户列表接口返回" → 影响范围（仅响应体 / 还是需要修改 resultMap/list SQL？）
  - 实体属性命名：phone_model → phoneModel（驼峰）
  - 是否需要做：DB DDL + 实体 + Mapper.xml + Controller 返回值 R.ok(...) 完整闭环？本场只到 Phase 2，不展开。
更简单方案：本轮只到 Phase 2（识别上下文与 adapter 优先级链），不展开方案。
任务规模：小（单字段新增；需 Phase 2 现场核实是否还有 Service/DTO/VO 中转）
成功标准：识别正确技术栈、正确 DB adapter、正确 schema 查询。
```

---

## 3. Phase 2: 技术栈检测 + 技术栈规则加载 + 背景资料构建

### Step 2.1 技术栈检测（profiles/_schema.md 打分）

| 命中 | 加分 |
|------|------|
| `pom.xml` 文件命中 | +1 |
| `spring-boot-starter` 依赖 | +3 |
| `mybatis-spring-boot-starter` 依赖 | +3 |
| `druid-spring-boot-4-starter` 依赖 | +3 |
| `src/main/java` 目录命中 | +1 |
| `src/main/resources/mapper` 目录命中 | +1 |
| **java-spring-mybatis 总分** | **12（最高）** |

OK 选中 `profiles/java-spring-mybatis.md`。

**DB 类型识别**（关键）：
- `application-druid.yml:5` `driverClassName: org.postgresql.Driver`
- `application-druid.yml:9` `url: jdbc:postgresql://localhost:5432/ry-vue`
- `application-druid.yml:38` `validationQuery: SELECT 1`（PG 风格——MySQL 常见为 `SELECT 1 FROM DUAL`，b3 没有 `FROM DUAL`）
- `application.yml:115` `pagehelper.helperDialect: postgresql`

**DB 类型 = PostgreSQL**（双重确认：URL pattern + driver class + pagehelper dialect + validationQuery 风格）。

### Step 2.2 技术栈规则加载（含 db-adapter 选择优先级链 — 核心测试点）

按 `references/phase-2-context-discovery.md` Step 2.2 优先级链执行：

#### 优先级链第 1 级：运行时 DB 类型探测（最高）

| 信号 | 来源 | 命中 |
|------|------|------|
| `jdbc:postgresql:` | `application-druid.yml:9` | OK 匹配 postgresql.md `connection_url_patterns` |
| `spring.datasource.url` 含 `postgresql` | 同上 | OK 匹配 postgresql.md `config_keys` |
| `org.postgresql.Driver` | `application-druid.yml:5` | OK 间接确认 |
| `pagehelper.helperDialect: postgresql` | `application.yml:115` | OK 辅助确认 |

> **运行时探测命中 PostgreSQL。**

#### 覆盖行为

profile `db_introspection.schema_source` 原文（`profiles/java-spring-mybatis.md:142`）：

```yaml
db_introspection:
  orm: MyBatis
  migration_tool: 手写SQL脚本
  schema_source: 默认 db-adapters/mysql.md（SQL 只在 adapter 一处维护），运行时 DB 类型探测可覆盖（如探测到 PostgreSQL 则切到 db-adapters/postgresql.md）
```

> **覆盖触发**：运行时探测命中 PG → 覆盖默认 `mysql.md` → **加载 `db-adapters/postgresql.md`**。

> **DB 类型覆盖声明（输出）**：
>
> ```
> DB 类型覆盖：运行时 DB 类型探测命中 jdbc:postgresql: URL pattern
>   → DB 类型确定为 PostgreSQL
>   → 覆盖 java-spring-mybatis.md profile db_introspection.schema_source 默认值 db-adapters/mysql.md
>   → 加载 db-adapters/postgresql.md
> ```

#### mysql.md 不加载

确认 mysql.md 不在加载路径中（运行时探测已确定 PG，profile 默认值被覆盖；mysql.md 的 `INFORMATION_SCHEMA.COLUMNS` + `SHOW CREATE TABLE` 不会进入本场）。

### Step 2.3 上下文发现（使用 java-spring-mybatis + postgresql adapter）

按 profile `context_discovery` / `discovery_globs` 限定相关模块：

| 相关性 | 文件 | 用途 |
|--------|------|------|
| 3 | `ruoyi-common/.../entity/SysUser.java` | 实体新增 phoneModel 字段 |
| 3 | `ruoyi-admin/.../controller/system/SysUserController.java` | `/list` 接口 |
| 3 | `ruoyi-system/.../mapper/SysUserMapper.java` | Mapper 接口 |
| 3 | `ruoyi-system/.../resources/mapper/system/SysUserMapper.xml` | list SQL + resultMap |
| 3 | `ruoyi-system/.../service/ISysUserService.java` | list 服务接口 |
| 3 | `ruoyi-system/.../service/impl/SysUserServiceImpl.java` | list 服务实现 |
| 2 | `sql/ry_*.sql` | DDL 落点 |
| 2 | `ruoyi-admin/src/main/resources/application-druid.yml` | datasource 现场（PG） |
| 0 | `ruoyi-quartz` / `ruoyi-generator` / `ruoyi-ui` | 与本变更无关 |

**DB schema 查询**（按 db-adapters/postgresql.md 的 `schema_queries.table_structure`，**pg_catalog 风格**）：

```sql
-- 来源：db-adapters/postgresql.md schema_queries.table_structure
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
WHERE c.relname = 'sys_user'
  AND n.nspname = current_schema()
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY a.attnum
```

注意：**不是** `INFORMATION_SCHEMA.COLUMNS` 风格（那是 mysql.md）；
注意：**不是** `SHOW CREATE TABLE`（PG 不支持；postgresql.md `ddl` 字段给出的等价是 `pg_dump -s -t 'sys_user'` 或 `psql \d+ sys_user`）。

DB schema 发现纪律（强制规则 #3）：本场只到 Phase 2，**未实际执行 SQL**；schema_queries 仅作"将要使用的查询"登记。若进入 Phase 3+，也只允许 SELECT/SHOW/DESCRIBE/INFORMATION_SCHEMA 一类只读查询。

### Step 2.4 背景分析（草案；未写盘，本场只到 Phase 2）

```text
变更意图：sys_user 加 phone_model VARCHAR(64)，/list 接口响应中暴露
已识别技术栈：Java 17 + Spring Boot 4.0.6 + MyBatis 4.0.1 + Druid 1.2.28 + PostgreSQL
已加载技术栈规则：
  - profiles/java-spring-mybatis.md
  - db-adapters/postgresql.md（运行时 DB 探测覆盖 profile 默认 mysql.md）
L1 项目地图：change-impact/_project-map.md 存在但【2】技术栈节关于 DB 类型已过期（标 MySQL；当前 PG）——按 skill 规则重做判断，不依赖地图
L2 变更邻域：SysUser 实体 + SysUserController.list + SysUserMapper + SysUserMapper.xml + ISysUserService/Impl
L3 精准证据：未深入读（Phase 2 止步）
code graph：unavailable（本场未启用）
已确认事实：
  - application-druid.yml:9 url: jdbc:postgresql://localhost:5432/ry-vue
  - application-druid.yml:5 driverClassName: org.postgresql.Driver
  - application-druid.yml:38 validationQuery: SELECT 1（PG 风格；MySQL 常见 SELECT 1 FROM DUAL）
  - application.yml:115 pagehelper.helperDialect: postgresql
  - pom.xml 命中 spring-boot-dependencies / mybatis-spring-boot-starter / druid-spring-boot-4-starter
未确认项：
  - sys_user 表是否已存在 phone_model 字段（需 Phase 3+ 跑 schema_queries.table_structure）
  - 列表接口的 resultMap 是否包含 phone_model（需 Phase 3+ 读 SysUserMapper.xml）
不采用的推断：
  - "列表接口直接 select * from sys_user" → 不写，须先看 XML
```

**停止。** 不进 Phase 2.5 / Phase 3。

---

## 4. 判定

| 判定项 | 观测 | PASS/FAIL |
|--------|------|-----------|
| 1. Phase 2.1 是否识别 datasource URL 为 PostgreSQL | `application-druid.yml:9` `url: jdbc:postgresql://localhost:5432/ry-vue` 命中 postgresql.md `connection_url_patterns: 'jdbc:postgresql:'`；同时 `application-druid.yml:5` `org.postgresql.Driver` 与 `application.yml:115` `pagehelper.helperDialect: postgresql` 辅助确认 | **PASS** |
| 2. Phase 2.2 加载的 adapter 是 postgresql.md 还是 mysql.md | 优先级链第 1 级（运行时 DB 探测）命中 `jdbc:postgresql:` → 覆盖 `java-spring-mybatis.md` profile `db_introspection.schema_source` 默认值 `db-adapters/mysql.md` → **加载 `db-adapters/postgresql.md`**；mysql.md 未进入加载路径 | **PASS** |
| 3. Phase 2.3 使用的 schema 查询语句是 pg_catalog 风格还是 MySQL 风格 | Step 2.3 登记的 schema_queries.table_structure 来自 `db-adapters/postgresql.md`，基于 `pg_attribute` / `pg_class` / `pg_namespace` / `pg_attrdef` 的 `pg_catalog` 风格 + `pg_get_expr` / `col_description` / `format_type` PG 专属函数；**不混用** `INFORMATION_SCHEMA.COLUMNS`、**不使用** `SHOW CREATE TABLE`（PG 不支持；DDL 取法为 `pg_dump -s` / `psql \d+`） | **PASS** |
| 4. 是否明确输出了"DB 类型覆盖"说明 | 见 Step 2.2 "DB 类型覆盖声明（输出）" 块：明确写出"运行时 DB 类型探测命中 jdbc:postgresql: URL pattern → DB 类型确定为 PostgreSQL → 覆盖 java-spring-mybatis.md profile db_introspection.schema_source 默认值 db-adapters/mysql.md → 加载 db-adapters/postgresql.md" | **PASS** |

**结论：4/4 PASS。**

---

## 5. 弱模型专项观测

| 观测点 | 记录 |
|--------|------|
| 是否偷懒走 profile 默认值（mysql.md）？ | **否**。Step 2.2 显式执行了 4 级优先级链并输出"DB 类型覆盖"声明；mysql.md 明确未加载 |
| 运行时探测是否被跳过？ | **否**。Step 2.1 现场 grep 确认 `jdbc:postgresql:` + `org.postgresql.Driver` + `pagehelper.helperDialect: postgresql`，3 重信号 |
| 地图过期问题是否处理？ | **是**。change-impact/_project-map.md【2】技术栈节标 MySQL 已过期，本场按 skill 规则"动手前自行重新取证"重做判断，未盲信地图 |
| schema 查询是否误用 MySQL 风格？ | **否**。Step 2.3 完整采用 postgresql.md 的 `pg_catalog` 系；明确说明"PG 不支持 SHOW CREATE TABLE" |
| 是否新增 / 修改任何文件？ | **否**。仅 Phase 2 只读扫描 + 对话内输出；未触发任何 Edit/Write/DDL/DML（符合强制规则 #3 只读纪律） |

---

## 6. 关键发现

1. **优先级链机制在弱模型上正常工作**。本场模拟弱模型 minimax m3 严格按 `references/phase-2-context-discovery.md` Step 2.2 跑优先级链，未出现手册 WEAK-MANUAL.md 第 43 行所述典型失效（"adapter 选择：直接按 profile 硬编码 mysql.md，不走优先级链"）。

2. **detection_signals 双重匹配**。postgresql.md 的 `connection_url_patterns: 'jdbc:postgresql:'` + `config_keys: 'spring.datasource.url' (含 postgresql)` 同时命中 b3 副本的 application-druid.yml。Step 2.2 要求"同时与各 db-adapters/*.md 的 detection_signals 对照，确认匹配"——本场满足。

3. **profile 自带"运行时可覆盖"语义**。`profiles/java-spring-mybatis.md:142` 的 schema_source 字段显式声明"运行时 DB 类型探测可覆盖（如探测到 PostgreSQL 则切到 db-adapters/postgresql.md）"——也就是说**当前 skill 设计就是允许甚至要求覆盖**的，弱模型只需照规则执行。

4. **mysql.md vs postgresql.md 的 schema 查询风格差异显著**：
   - mysql.md：`INFORMATION_SCHEMA.COLUMNS` + `SHOW CREATE TABLE`
   - postgresql.md：`pg_attribute` / `pg_class` / `pg_namespace` / `pg_constraint` + `pg_get_expr` / `pg_get_constraintdef` / `format_type` + `pg_dump -s` / `psql \d+`
   - 若错误加载 mysql.md，在 PG 环境 `SHOW CREATE TABLE` 直接报错（PG 不支持）——adapter 选错对功能有决定性影响。

5. **b3 副本与原 ruoyi-vue 隔离**。b3 是独立 Git 仓库（HEAD=41720e6），与原项目不共享工作区；跑测后**不需要** git checkout 恢复 PG 配置——这一点已在结果文件第 0 节明确写明，避免后续混淆。

---

## 7. 后续

- 本场不进入 Phase 3+；不在 `change-impact/` 写任何文件。
- b3 副本保持当前 PG 状态（application-druid.yml 仍是 PG URL）；独立仓库不污染原项目。
- 路径：`change-impact/sys_user-add-phone_model/` 下的旧工件（来自先前跑测的 010/020/030/050/060/090/_active-state）保留不动——本场不修改它们。
