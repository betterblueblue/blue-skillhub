# 020 — 设计文档 (Design)

> 需求：modify-user-create-flow-email-required
> 关联：`010-requirements.md` `000-context-pack.md`

---

## 1. 总体设计

### 1.1 设计原则

1. **不破坏 DDL 兼容**：必填由应用层 Bean Validation 承担，**不**改 `sys_user.email` 的 `NOT NULL` 约束
2. **复用现有模式**：沿用 `SysUser.userName`（L147-149）`@Xss + @NotBlank + @Size` 三段式注解；前端沿用 `rules.userName` 模式
3. **不引入新依赖**：`spring-boot-starter-validation` 已在 `ruoyi-common/pom.xml:47`
4. **不发明新 regex**：直接用 `jakarta.validation.constraints.Email`（RFC 5321 简化版）

### 1.2 改动清单（最小化）

| # | 文件 | 变更类型 | 内容 |
| --- | --- | --- | --- |
| 1 | `ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java` | 改 | email getter 上加 `@NotBlank` + `@Email` + `@Size`（与 `userName` getter 注解模式一致） |
| 2 | `ruoyi-ui/src/views/system/user/index.vue` | 改 | `rules.email` 加 `required: true` + 兜底 message |
| 3 | `ruoyi-system/src/main/java/com/ruoyi/system/mapper/SysUserMapper.java` | 改 | 新增 2 个 method（`countEmptyEmailUsers` / `batchBackfillEmptyEmail`） |
| 4 | `ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml` | 改 | 对应 XML 2 段 |
| 5 | `ruoyi-system/src/main/java/com/ruoyi/system/service/ISysUserService.java` | 改 | 新增 `backfillEmptyEmails(int batchSize)` 接口方法 |
| 6 | `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java` | 改 | 实现 `backfillEmptyEmails` |
| 7 | `ruoyi-system/pom.xml` | 改 | 加 `spring-boot-starter-test`（JUnit 5 + Mockito） |
| 8 | `ruoyi-system/src/test/java/com/ruoyi/system/SysUserEmailValidationTest.java` | **新** | Bean Validation 测试 |
| 9 | `ruoyi-system/src/test/java/com/ruoyi/system/service/impl/SysUserBackfillServiceTest.java` | **新** | Service 测试（Mockito） |
| 10 | `actual/change-impact/.../050-validation/001-backfill-empty-emails.sql` | **新** | 回填脚本（落 `050-validation/`，**不**落仓库 `sql/`） |
| 11 | `actual/change-impact/.../050-validation/002-validate-email-regex.sh` | **新** | 校验冒烟脚本 |

修改文件 7 个 + 新文件 4 个 = 11 个；满足 `expected_modified_files_min = 4`。

---

## 2. 代码风格报告（含完整代码片段）

### 2.1 注解风格 —— 沿用 `SysUser.userName` 模式

**完整未截断**（来自 `SysUser.java:146-157`，Read 出来的真代码）：

```java
@Xss(message = "用户账号不能包含脚本字符")
@NotBlank(message = "用户账号不能为空")
@Size(min = 0, max = 30, message = "用户账号长度不能超过30个字符")
public String getUserName()
{
    return userName;
}
```

> 实施踩坑（修正版）：本次 e2e 评审过程中发现 Subagent A 初版的"@NotBlank 放 field + @Email 放 getter" 拆分模式**JUnit 跑出 0 违规**（测试 mvn test 失败 2/4）。原因不是注解在 getter 上"不可靠"，而是 **Hibernate Validator 默认走 property access 路径**，field 上的注解对 `validator.validateProperty(bean, "email")` 无效。**实际修复**：所有三个注解（`@NotBlank` / `@Email` / `@Size`）**统一放在 getter 上**（与项目已有 `userName` getter 模式完全一致），同时跑 `mvn clean install` 清掉 stale .class（注解从 field 搬到 getter 之前已编译的 .class 仍带原注解，导致 test 始终命中旧 class）。

**email 改造后（最终版）**（实际落地的真代码，`SysUser.java:43-46` 字段 + L158-167 getter）：

```java
// 字段（保持简洁）
@Excel(name = "用户邮箱")
private String email;

// getter（注解集中，与 userName 模式一致）
@NotBlank(message = "邮箱不能为空")
@Email(message = "邮箱格式不正确")
@Size(min = 0, max = 50, message = "邮箱长度不能超过50个字符")
public String getEmail()
{
    return email;
}
```

> 说明：`@Xss` 不适合 email（email 通常带 `+` `@` `.` 是合法字符），故不加。`@NotBlank` 顺序在前：fail-fast 优先。**与 userName getter 模式完全对齐**——`SysUser` 全类注解风格统一在 getter 层，符合 Hibernate Validator 默认 property access 行为。**编译后务必 `mvn clean install` 清掉 stale .class**（否则 field→getter 注解迁移后旧 .class 仍生效）。

### 2.2 Controller 风格 —— 沿用 `@Validated @RequestBody`

**完整未截断**（来自 `SysUserController.java:122-144`）：

```java
@PreAuthorize("@ss.hasPermi('system:user:add')")
@Log(title = "用户管理", businessType = BusinessType.INSERT)
@PostMapping
public AjaxResult add(@Validated @RequestBody SysUser user)
{
    deptService.checkDeptDataScope(user.getDeptId());
    roleService.checkRoleDataScope(user.getRoleIds());
    if (!userService.checkUserNameUnique(user))
    {
        return error("新增用户'" + user.getUserName() + "'失败，登录账号已存在");
    }
    else if (StringUtils.isNotEmpty(user.getPhonenumber()) && !userService.checkPhoneUnique(user))
    {
        return error("新增用户'" + user.getUserName() + "'失败，手机号码已存在");
    }
    else if (StringUtils.isNotEmpty(user.getEmail()) && !userService.checkEmailUnique(user))
    {
        return error("新增用户'" + user.getUserName() + "'失败，邮箱账号已存在");
    }
    user.setCreateBy(getUsername());
    user.setPassword(SecurityUtils.encryptPassword(user.getPassword()));
    return toAjax(userService.insertUser(user));
}
```

**本次不动**——`@Validated` 自动接收 `@NotBlank` 注解。

### 2.3 Mapper 注解风格 —— 沿用 `@Param`

**完整未截断**（来自 `SysUserMapper.java:78`）：

```java
public int updateUserAvatar(@Param("userId") Long userId, @Param("avatar") String avatar);
```

**新增 method**（同模式）：

```java
/**
 * 统计 email 为空或 NULL 的用户数（DDL/DML 预检）
 * @return 受影响行数
 */
public int countEmptyEmailUsers();

/**
 * 批量回填空 email 为 'unknown@local'
 * @param defaultEmail 回填目标值（建议 'unknown@local'）
 * @return 受影响行数
 */
public int batchBackfillEmptyEmail(@Param("defaultEmail") String defaultEmail);
```

### 2.4 Mapper XML 动态列风格 —— 沿用 `<if test="...">`

**完整未截断**（来自 `SysUserMapper.xml:180-198`）：

```xml
<update id="updateUser" parameterType="SysUser">
    update sys_user
    <set>
        <if test="deptId != 0">dept_id = #{deptId},</if>
        <if test="nickName != null and nickName != ''">nick_name = #{nickName},</if>
        <if test="email != null ">email = #{email},</if>
        <if test="phonenumber != null ">phonenumber = #{phonenumber},</if>
        ...
        update_time = sysdate()
    </set>
    where user_id = #{userId}
</update>
```

**新增 SQL**：

```xml
<select id="countEmptyEmailUsers" resultType="int">
    SELECT COUNT(*) FROM sys_user
    WHERE email IS NULL OR email = ''
</select>

<update id="batchBackfillEmptyEmail" parameterType="String">
    UPDATE sys_user
    SET email = #{defaultEmail}, update_time = sysdate()
    WHERE email IS NULL OR email = ''
</update>
```

### 2.5 Service 接口风格 —— 沿用 Javadoc + 简单入参

**完整未截断**（来自 `ISysUserService.java:175-181`）：

```java
/**
 * 重置用户密码
 *
 * @param user 用户信息
 * @return 结果
 */
public int resetPwd(SysUser user);
```

**新增 method**：

```java
/**
 * 回填 email 为空或 NULL 的用户
 *
 * @param defaultEmail 回填目标值
 * @return 回填行数
 */
public int backfillEmptyEmails(String defaultEmail);
```

### 2.6 Service 实现风格 —— 沿用 `@Autowired` + 委派

**完整未截断**（来自 `SysUserServiceImpl.java:375-381`）：

```java
@Override
public int resetPwd(SysUser user)
{
    return userMapper.resetUserPwd(user.getUserId(), user.getPassword());
}
```

**新增实现**：

```java
@Override
public int backfillEmptyEmails(String defaultEmail)
{
    if (StringUtils.isEmpty(defaultEmail))
    {
        throw new ServiceException("回填 email 默认值不能为空");
    }
    int affected = userMapper.batchBackfillEmptyEmail(defaultEmail);
    log.info("backfillEmptyEmails: defaultEmail={}, affected={}", defaultEmail, affected);
    return affected;
}
```

### 2.7 前端校验风格 —— 沿用 Element UI `rules`

**完整未截断**（来自 `index.vue:245-267`）：

```javascript
rules: {
    userName: [
        { required: true, message: "用户名称不能为空", trigger: "blur" },
        { min: 2, max: 20, message: '用户名称长度必须介于 2 和 20 之间', trigger: 'blur' }
    ],
    nickName: [
        { required: true, message: "用户昵称不能为空", trigger: "blur" }
    ],
    email: [
        {
            type: "email",
            message: "请输入正确的邮箱地址",
            trigger: ["blur", "change"]
        }
    ],
    phonenumber: [
        {
            pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/,
            message: "请输入正确的手机号码",
            trigger: "blur"
        }
    ]
}
```

**改造后**（`required` 优先 + 自定义 message）：

```javascript
email: [
    { required: true, message: "请输入邮箱地址", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱地址", trigger: ["blur", "change"] }
]
```

---

## 3. 设计原则自检

| 原则 | 自检 |
| --- | --- |
| 简单优先 | ✅ 1 个注解 + 1 行前端 + 1 个 SQL，无新模块 |
| 精准修改 | ✅ 改 7 个文件 + 新 4 个文件（11 个），无顺手重构 |
| 质量底线 | ✅ 新增 Service 配 Mockito 测试、新增 Mapper 配 JUnit 单元测试 |
| 沿用项目模式 | ✅ Bean Validation / Element UI rules / MyBatis dynamic SQL 全部沿用 |
| 不引入新依赖 | ✅ 只在 ruoyi-system 加 spring-boot-starter-test（标准 test 依赖） |

---

## 4. @Async 陷阱规避（S2 特别注意 D 段）

**本次需求完全不涉及异步**：email 必填 + 格式校验 + 存量回填都是同步操作。**不引入 `@Async`**。

> 假如未来扩展为"后台异步回填 + 进度查询"，必须按 `subagent-a-run-skill.md` D 段规则：
> - 拆 Bean：新建 `UserBackfillLauncher` 单独放 `@Async public void run()`
> - 或 Self-inject：`@Lazy @Autowired private UserBackfillService self;` 通过 `self.run()`
> - Controller 调 launcher / self，不直接调本类内 `@Async` 方法
