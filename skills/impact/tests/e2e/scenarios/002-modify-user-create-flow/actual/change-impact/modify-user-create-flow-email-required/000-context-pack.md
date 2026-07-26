# 000 — 上下文包 (Context Pack)

> 需求：modify-user-create-flow-email-required
> 范围：用户创建/编辑流程的 email 必填 + 格式校验 + 存量 email 回填
> 工作目录：`E:\agent\blue-skillhub\skills\impact\tests\e2e\workdirs\002-modify-user-create-flow`
> Skill: impact / Java-Spring-MyBatis / RuoYi-Vue v3.9.2

---

## 1. 仓库与项目形态（证据化）

| 项 | 证据 | 路径 / 行号 |
| --- | --- | --- |
| 项目根 | `pom.xml:3.9.2` | `E:\agent\blue-skillhub\skills\impact\tests\e2e\workdirs\002-modify-user-create-flow\pom.xml` |
| Spring Boot 版本 | `<spring-boot.version>4.0.6</spring-boot.version>` | `pom.xml:18` |
| Java 版本 | `<java.version>17</java.version>` | `pom.xml:17` |
| 子模块 | ruoyi-admin / ruoyi-common / ruoyi-framework / ruoyi-generator / ruoyi-quartz / ruoyi-system | 仓库根目录 |
| 校验依赖 | `spring-boot-starter-validation` 已在 `ruoyi-common` 引入 | `ruoyi-common\pom.xml:47` |
| 测试依赖 | **未引入** spring-boot-starter-test，需在 `ruoyi-system/pom.xml` 中新增 | `ruoyi-system\pom.xml:18-26`（确认无 test 依赖） |
| 已有 sys_user 表 DDL | `email varchar(50) default ''` | `sql\ry_20260417.sql:48` |
| 已有 sys_user 种子数据 | admin / ry 共 2 行，email 非空 | `sql\ry_20260417.sql:69-70` |

---

## 2. 关键代码现状（已 Read）

### 2.1 `SysUser` Entity（`ruoyi-common/.../entity/SysUser.java`）

- L5 `import jakarta.validation.constraints.*` — **校验注解已可用**
- L43-45 `email` 字段已带 `@Excel(name = "用户邮箱")`
- L159-164 getter 上有 `@Email(message = "邮箱格式不正确")` + `@Size(min = 0, max = 50, ...)`
- **缺**：`@NotBlank(message = "邮箱不能为空")`（当前未拦截空 email）
- L150 已有 `userName` 的 `@NotBlank` 模式（`@Xss + @NotBlank + @Size`），**email 必填应复用同模式**

```java
// SysUser.java:159-164 现状
@Email(message = "邮箱格式不正确")
@Size(min = 0, max = 50, message = "邮箱长度不能超过50个字符")
public String getEmail()
{
    return email;
}
```

### 2.2 Controller（`ruoyi-admin/.../controller/system/SysUserController.java`）

- L122-144 `add()` 方法已用 `@Validated @RequestBody SysUser user` — **Bean Validation 链路已就绪**
- L149-172 `edit()` 同上
- L137-140、166-169 已用 `userService.checkEmailUnique(user)` 做唯一性校验（不会因本次改动破坏现有路径）

### 2.3 Service（`ruoyi-system/.../service/impl/SysUserServiceImpl.java`）

- L500-564 `importUser()` L518、L529 调用 `BeanValidators.validateWithException(validator, user)` — **导入路径也走 Bean Validation**，回填后导入路径会受益
- L209-218 `checkEmailUnique` 不依赖 email 是否必填，与本次正交

### 2.4 Mapper XML（`ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml`）

- L142-144 `checkEmailUnique` 当前是 `where email = #{email} and del_flag = '0'` — **空 email 也会被查出"已存在"**，本次修后空 email 走"必填"路径，不再到达 mapper
- L146-178 `insertUser` 已是 `dynamic columns`，不会强制写入 email
- **新增** mapper method：`countEmptyEmailUsers` + `batchBackfillEmptyEmail` 是合理扩展

### 2.5 前端（`ruoyi-ui/src/views/system/user/index.vue`）

- L87 `<el-form ref="form" :model="form" :rules="rules" label-width="80px">`
- L107-109 邮箱 form-item 已声明 `prop="email"`
- L253-259 `rules.email` 当前只有 `{ type: "email", message: "...", trigger: [...] }` — **缺 `required: true`**
- L329-342 `reset()` 中 `form.email = undefined` — 保留

```javascript
// index.vue:253-259 现状
email: [
  {
    type: "email",
    message: "请输入正确的邮箱地址",
    trigger: ["blur", "change"]
  }
],
```

### 2.6 SQL DDL（`sql/ry_20260417.sql`）

- L42-64 `sys_user` 表创建
- L48 `email varchar(50) default '' comment '用户邮箱'`
- **本次不直接 DDL 改 NOT NULL**（破坏兼容：现存空 email 行 + 历史脚本依赖 default ''），必填由应用层注解承担
- L69-70 种子数据 email 已合法（`ry@163.com` / `ry@qq.com`），与本次兼容

---

## 3. 反向引用（Grep 结果）

| 查询 | 命中 | 评估 |
| --- | --- | --- |
| `setEmail\|getEmail` | SysUser.java 内 4 处、Mapper.xml 2 处 | 受影响 |
| `rules.email\|prop="email"` | index.vue L107-109, L253-259 | 必改 |
| `checkEmailUnique` | SysUserServiceImpl L209-218、Controller L137/166、Mapper.xml L142-144 | 行为不变，仅路径前置拦截 |
| `BeanValidators.validateWithException` | SysUserServiceImpl L518/529、admin/.../SysUserController L41/47 | 本次增加 `@NotBlank` 后会被自动触发，无需改调用方 |
| `insert into sys_user.*email` | ry_20260417.sql 2 行种子 | 不涉及 |

---

## 4. 维度选择（按需覆盖，不强制 19 维）

| 维度 | 是否覆盖 | 原因 |
| --- | --- | --- |
| DB schema | 是（仅评估，不 DDL） | 避免破坏兼容，必填交应用层 |
| 存量数据 | 是 | 铁律 #2 强触发 |
| 跨模块 | 是 | Entity + Controller + 前端 + Mapper + SQL |
| API 契约 | 是 | Controller 入参校验变化是契约层 |
| 权限 | 否 | 沿用 `@PreAuthorize("@ss.hasPermi('system:user:add')")` 不变 |
| 缓存 | 否 | email 不入缓存 |
| MQ / 异步 | 否 | 本次同步 |
| 状态机 / enum | 否 | 无 |
| 配置 | 否 | 无新增配置键 |
| 测试 | 是 | 必填，JUnit 5 + Mockito |

---

## 5. 关键决策（已落定 / 待 Phase 3 收敛）

- **沿用** `jakarta.validation.constraints.Email`（项目已有依赖），不引入新 regex 工具类（避免重复造轮子）
- **不**在 DDL 改 `NOT NULL`，破坏兼容；必填在应用层 `@NotBlank` 实现
- **回填脚本** 落 `050-validation/001-backfill-empty-emails.sql`，**不直接执行**（铁律 #3 + #2）
- **回填预检**：`SELECT COUNT(*) FROM sys_user WHERE email IS NULL OR email = ''` 必须在脚本中跑一次并落日志行
- **回填目标值** `unknown@local` 不符合 `@Email` 严格正则（无 TLD），因此**回填行不需要在应用层通过 `@Email` 校验**——回填走 SQL 而非新增接口

---

## 6. 仓内现有模式（Phase 5 改代码时遵循）

- Entity 注解：getter 上挂注解（参考 `SysUser.userName` L147-149）
- Controller 注解：`@Validated @RequestBody`（参考 `SysUserController.add` L125）
- Service 校验：调用 `BeanValidators.validateWithException(validator, user)`（参考 importUser L518）
- Mapper 动态列：`insertUser` / `updateUser` 都用 `<if test="x != null and x != ''">x,</if>`（参考 Mapper.xml L146-198）
- 前端校验：`el-form` 的 `rules` 数组结构（参考 index.vue L245-267）
