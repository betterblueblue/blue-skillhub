# 030 — 实施文档 (Implementation)

> 需求：email-required-validation
> 关联：`020-design.md`

---

## 2.1 自检

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 所有必须修改的文件已列出 | ✅ | 7 改 + 4 新 = 11 个 |
| 每个 Step 有明确的写入对象 | ✅ | |
| DDL/DML Step 单独列出 | ✅ | 回填 SQL 在 050-validation/ |
| 测试 Step 有明确的验证方式 | ✅ | |

> 如果存在 ❌ 缺失项，必须补充对应 Step 或在"未确认项"中说明原因。不得跳过此自检直接提交。

## 2.2 设计到实施的对照

<!-- 填写指引：020 设计文档中每个 Dxx 至少对应一个 Step。030 不得引用不存在的 Dxx。
  每个写业务内容的 Step 必须引用至少一个 Dxx。
  纯 validator、只读检查等流程步骤可写"流程步骤，不改业务对象"。 -->

| 设计项（来自 020） | 对应 Step | 覆盖状态 |
|---|---|---|
| D01 | Step 1 | ✅ 已覆盖 |
| D02 | Step 2 | ✅ 已覆盖 |
| D03 | Step 3, Step 5 | ✅ 已覆盖 |
| D04 | Step 3, Step 5 | ✅ 已覆盖 |
| D05 | Step 3 | ✅ 已覆盖 |
| D06 | Step 3 | ✅ 已覆盖 |

> 如果 020 中有 Dxx 在此表无对应 Step，必须补充 Step 或在"未确认项"中说明原因。

## 3. 执行步骤

### Step 1: 修改 SysUser.java 加校验注解

- **设计项**：D01
- **维度**：代码
- **文件**：`ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java`
- **操作**：
  ```java
  // getter 上加注解（与 userName getter 模式一致）
  @NotBlank(message = "邮箱不能为空")
  @Email(message = "邮箱格式不正确")
  @Size(min = 0, max = 50, message = "邮箱长度不能超过50个字符")
  public String getEmail()
  ```
- **确认类型**：改代码

### Step 2: 修改前端校验规则

- **设计项**：D02
- **维度**：前端
- **文件**：`ruoyi-ui/src/views/system/user/index.vue`
- **操作**：
  ```javascript
  email: [
      { required: true, message: "请输入邮箱地址", trigger: "blur" },
      { type: "email", message: "请输入正确的邮箱地址", trigger: ["blur", "change"] }
  ]
  ```
- **确认类型**：改代码

### Step 3: 新增回填 Mapper + Service

- **设计项**：D03、D04、D05、D06
- **维度**：代码
- **文件**：
  - `ruoyi-system/src/main/java/com/ruoyi/system/mapper/SysUserMapper.java`
  - `ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml`
  - `ruoyi-system/src/main/java/com/ruoyi/system/service/ISysUserService.java`
  - `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java`
- **操作**：新增 `countEmptyEmailUsers` / `batchBackfillEmptyEmail` / `backfillEmptyEmails` 方法和 XML
- **确认类型**：改代码

### Step 4: 新增测试

- **设计项**：D01
- **维度**：测试
- **文件**：
  - `ruoyi-system/src/test/java/com/ruoyi/system/SysUserEmailValidationTest.java`
  - `ruoyi-system/src/test/java/com/ruoyi/system/service/impl/SysUserBackfillServiceTest.java`
- **操作**：新增 Bean Validation 测试和 Service 测试
- **确认类型**：写文件

### Step 5: 运行回填脚本

- **设计项**：D03、D04
- **维度**：DML
- **文件**：`050-validation/001-backfill-empty-emails.sql`
- **操作**：执行回填 SQL
- **确认类型**：DML
