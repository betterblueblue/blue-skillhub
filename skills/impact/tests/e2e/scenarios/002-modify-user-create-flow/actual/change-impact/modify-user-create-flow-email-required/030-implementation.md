# 030 — 实施计划 (Implementation)

> 需求：modify-user-create-flow-email-required
> 关联：`010-requirements.md` `020-design.md` `060-preflight.md`

---

## 1. Step 清单

> 注：测试场景下**所有** Step 都是"在 fixture 副本上执行"。高风险 Step（`回填 SQL`）按 skill 规则**只生成脚本不直接执行**。

### Step 1 [低] Entity 加 `@NotBlank`（**不**改 DDL）

- **维度**：API 契约 / Bean Validation
- **操作**：Edit `SysUser.java` email getter 上加 `@NotBlank(message = "邮箱不能为空")`
- **影响范围**：`@Validated @RequestBody SysUser` 的所有入参（add/edit）
- **回滚**：移除该注解即可
- **语义约定**：沿用 `@Email`（RFC 5321 简化版）+ `@NotBlank`（Jakarta 标准）
- **验证**：`mvn compile` + `mvn test` 中 `SysUserEmailValidationTest`

### Step 2 [低] Controller 不动

- **维度**：无需修改
- **验证**：`mvn compile` 仍通过

### Step 3 [中] Mapper 接口 + XML 新增 2 个 method

- **维度**：MyBatis Mapper（铁律 #2 触发：new mapper method）
- **操作**：
  - `SysUserMapper.java` 加 `countEmptyEmailUsers()` 和 `batchBackfillEmptyEmail(String defaultEmail)`
  - `SysUserMapper.xml` 加对应 `<select>` + `<update>`
- **影响范围**：仅本 Mapper namespace
- **回滚**：删除新增 method
- **语义约定**：动态 SQL 沿用现有 `<if>` 风格（Mapper.xml L183-194）
- **验证**：`mvn compile` + JUnit `SysUserBackfillServiceTest`

### Step 4 [中] Service 接口 + 实现新增 `backfillEmptyEmails`

- **维度**：Service（铁律 #2 触发：new Service method）
- **操作**：
  - `ISysUserService.java` 加接口方法
  - `SysUserServiceImpl.java` 实现，委派给 mapper
- **影响范围**：仅本 Service
- **回滚**：删除方法
- **验证**：`mvn test` 中 `SysUserBackfillServiceTest` 覆盖正常路径 + 异常路径（默认值空时抛 ServiceException）

### Step 5 [中] ruoyi-system/pom.xml 加 spring-boot-starter-test

- **维度**：依赖
- **操作**：`<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>`
- **验证**：`mvn test-compile` 通过

### Step 6 [高] 写 JUnit 测试（铁律 #6 行为准则）

- **维度**：测试
- **操作**：在 `ruoyi-system/src/test/java/.../system/` 下新建 2 个测试类
  - `SysUserEmailValidationTest`：构造 `Validator`、对 SysUser bean 校验
  - `SysUserBackfillServiceTest`：Mockito mock mapper、调用 service、验证委派 + 异常路径
- **验证**：`mvn test -pl ruoyi-system`

### Step 7 [中] 前端 `rules.email` 改造

- **维度**：前端表单校验
- **操作**：Edit `index.vue` L253-259
- **验证**：手动 UI 验证（测试场景无法启 ruoyi-ui，记录在 090-execution-record.md）

### Step 8 [高 / 不可逆 / **不直接执行**] 写回填 SQL 脚本

- **维度**：DB DML（铁律 #2 / #3 触发）
- **操作**：Write `actual/change-impact/.../050-validation/001-backfill-empty-emails.sql`
  - 顶部 `SELECT COUNT(*)` 预检（落日志）
  - `START TRANSACTION;`
  - `UPDATE sys_user SET email='unknown@local' WHERE email IS NULL OR email='';`
  - 末尾 `SELECT COUNT(*)` 验证 = 0
  - `COMMIT;`
- **回滚**：`UPDATE sys_user SET email='' WHERE email='unknown@local';`
- **验证**：脚本**不**直跑；落 `050-validation/` 待 DBA 在维护窗口手动执行
- **预检**：脚本顶部有 `SELECT COUNT(*)` 报告预计影响行数（铁律 #2 预检要求）

### Step 9 [低] 写前端校验冒烟脚本

- **维度**：E2E 验证
- **操作**：Write `actual/change-impact/.../050-validation/002-validate-email-regex.sh`
  - 用 `${TOKEN:-test-token}` / `${BASE_URL:-http://localhost:8080}` 占位
  - 包含成功路径（合法 email）和失败路径（空 / 非法 email）
  - **不**对生产执行
- **验证**：脚本语法 `bash -n` 通过

### Step 10 [中] 跑 mvn compile + mvn test

- **维度**：CI 验证
- **操作**：`mvn -pl ruoyi-system -am compile` + `mvn -pl ruoyi-system test`
- **验证**：compile 0 错误，test 全绿
- **降级路径**：若 mvn 跑不通，单独验证 `javac` 编译失败原因（依赖缺失/语法错误）

---

## 2. 验证矩阵

| Step | 验证方式 | 通过标准 |
| --- | --- | --- |
| 1 | `mvn compile` | 0 错误 |
| 3 | `mvn compile` | 0 错误（MyBatis XML 解析无误） |
| 4 | JUnit `SysUserBackfillServiceTest` | 全绿 |
| 5 | `mvn test-compile` | 0 错误 |
| 6 | `mvn test` | JUnit 全绿，覆盖核心 + 异常 |
| 7 | UI 手动（无可执行环境） | 在 090 记录 |
| 8 | `bash -n` + COUNT 预检存在 | 语法 OK，SQL 含预检 |
| 9 | `bash -n 002-validate-email-regex.sh` | 语法 OK |
| 10 | `mvn -pl ruoyi-system test` | 编译 + 测试全绿 |

---

## 3. 风险拦截 / 不确定性

| 风险 | 应对 |
| --- | --- |
| Spring Boot 4.0.6 默认 surefire 跳过父 pom 未声明模块 | Spring Boot 4 BOM 自带 surefire 插件，可直接跑 `mvn test` |
| 测试用例缺 `src/test/java` 目录 | 本次 Step 6 新建目录 + 文件 |
| MyBatis XML 解析失败（语法错） | Linter 无法做；用 `mvn compile` 验证 |
| 配置文件 `application.yml` 含明文 password | **硬约束 A**：本任务不读 `application.yml` 入文档；若必须引用，**脱敏** |

---

## 4. 环境降级

| 环境 | 跑法 |
| --- | --- |
| 完整 Maven | `mvn -pl ruoyi-system -am test` |
| 仅编译 | `mvn -pl ruoyi-system -am compile` |
| 无 Maven | `cd ruoyi-system && javac -cp <classpath> src/main/java/.../SysUser.java`（**不推荐**，依赖复杂） |
| 无 Java 17 | 在文档中标注"需 Java 17"，不降级跑 |

---

## 5. 回滚策略

| Step | 回滚方式 |
| --- | --- |
| 1 | Edit 回去除 `@NotBlank` |
| 3 | 删除 mapper method + XML |
| 4 | 删除 service method |
| 5 | 移除 pom 依赖 |
| 6 | 删除测试文件 |
| 7 | Edit 回去 |
| 8 | 不直跑脚本，**无需回滚**（脚本可由 DBA 选择不执行） |
| 9 | 删除文件 |
| 10 | — |
