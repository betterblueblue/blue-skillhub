# 010 — 需求分析 (Requirements)

> 需求：modify-user-create-flow-email-required
> 需求来源：用户对话 `002-modify-user-create-flow.json` user_query 字段
> 判档：full（DB schema 兼容 + 存量数据回填 + 跨模块 + 铁律 #2/#3）

---

## 1. 业务目标

将 `sys_user.email` 提升为**强必填 + 邮箱格式合法**的字段，并完成**存量数据**的回填工作（与新增校验策略一致），最终让 email 在所有用户场景中保持格式可用、不空。

---

## 2. 范围（In / Out of Scope）

### 2.1 In Scope

| 模块 | 行为 |
| --- | --- |
| 后端 Entity | `SysUser.email` getter 加 `@NotBlank`，保留现有 `@Email` + `@Size` |
| 后端 Controller | `SysUserController.add/edit` 通过现有 `@Validated` 链路自动触发（无需改代码） |
| 后端 Service | `SysUserServiceImpl.importUser` 经 `BeanValidators.validateWithException` 自动受益 |
| 前端 | `ruoyi-ui/.../user/index.vue` 中 `rules.email` 增 `required: true` + 自定义 message |
| 存量数据 | 生成 `050-validation/001-backfill-empty-emails.sql`（含 COUNT 预检 + 批量回填），**不直接执行** |
| 验证 | `050-validation/002-validate-email-regex.sh` 跑 `@Email` 注解的冒烟脚本（curl + JSON），不直接对生产 |
| 测试 | 新增 `SysUserEmailValidationTest` 覆盖必填 + 格式 + 异常路径 |

### 2.2 Out of Scope（不顺便做）

- **不**改 `sys_user.email` 的 DDL（如 `NOT NULL` / `UNIQUE`）—— 破坏兼容、需重写所有依赖 default '' 的老脚本
- **不**改 `checkEmailUnique` 的 Mapper SQL —— 沿用现状
- **不**改 `updateUser` / `insertUser` 逻辑 —— Bean Validation 自动覆盖
- **不**改前端 `profile/`（个人中心）邮箱编辑入口（保持兼容，本期统一由 admin 入口管）
- **不**新增 `sys_user_email_audit` 之类审计表

---

## 3. 用户故事 / 验收标准

### US-1 后端强制 email 必填

- **Given** 调用 `POST /system/user`，body 中 `email=""` 或缺省
- **When** Bean Validation 校验
- **Then** HTTP 400，body 含 `email: 邮箱不能为空`

### US-2 后端强制 email 格式

- **Given** `email="not-an-email"`
- **Then** HTTP 400，body 含 `email: 邮箱格式不正确`

### US-3 前端必填拦截

- **Given** 用户在"添加用户"对话框中不填 email 直接点确定
- **Then** Element UI 提示 `请输入邮箱地址`（红字）

### US-4 前端格式拦截

- **Given** `email="abc@"`
- **Then** Element UI 提示 `请输入正确的邮箱地址`

### US-5 存量数据回填（**非运行时执行**）

- **Given** `SELECT COUNT(*) FROM sys_user WHERE email IS NULL OR email = ''` 返回 N
- **When** DBA 在维护窗口跑 `050-validation/001-backfill-empty-emails.sql`
- **Then** N 行 email 更新为 `'unknown@local'`，脚本末尾再跑一次 COUNT 验证 = 0

---

## 4. 风险等级 + 触发铁律

| Step | 风险 | 铁律 | 拦截动作 |
| --- | --- | --- | --- |
| 改 Entity SysUser.java 加 `@NotBlank` | 中（API 契约收紧） | #5（破坏性请求保护）—— 不算破坏 | `@Validated` 已就绪，Bean Validation 报错返回 400 而非 500 |
| 改前端 `rules.email` 加 `required` | 低 | 无 | 沿用 Element UI 模式 |
| 写 `001-backfill-empty-emails.sql` | **高** | #2（数据回填）+ #3（DDL/DML 默认生成脚本不直接执行） | 脚本落 `050-validation/`，不直跑；含 COUNT 预检 + 事务 + 日志 |
| 新增 Mapper method `countEmptyEmailUsers` / `batchBackfillEmptyEmail` | 中 | #2（new mapper method） | 配 JUnit 5 + Mockito 测试 |
| 新增 JUnit 测试 `SysUserEmailValidationTest` | 低 | #6（行为准则）测试 | 覆盖核心 + 异常路径 |

### 4.1 行为准则检查（中任务必检 1-6）

1. 先思考，再编码：✅ 本文档 + context-pack 已罗列假设
2. 简单优先：✅ 不引入新依赖、不加 helper、不做推测性扩展
3. 精准修改：✅ 改动清单限定在 4 个文件 + 1 个新测试 + 1 个新 SQL
4. 目标驱动：✅ 每个 Step 配验证方式（JUnit / curl / SQL COUNT）
5. 改前确认语义约定：✅ 沿用 `@Email`、不引入自定义 regex
6. 测试策略匹配风险：✅ Service / Mapper method / Validator 都配测试

---

## 5. 兼容性 / 回滚

| 维度 | 兼容策略 | 回滚 |
| --- | --- | --- |
| 旧前端用户 | 新 `required` 规则**仅**影响新提交；浏览器缓存刷新后生效 | 删除 `required: true` 一行 |
| 旧 API 客户端 | 调用 `POST /system/user` 漏传 email 会被 400 拒绝（**破坏性**） | 移除 getter 上的 `@NotBlank`（保留 `@Email`） |
| 存量 email='' 的行 | 必填化**不**强制 DDL 改 NOT NULL，老行仍可 SELECT/EXPORT | — |
| 存量回填 'unknown@local' | 写入后**不**通过 `@Email`（无 TLD）但属内部数据，不暴露在新增校验路径 | UPDATE 回原值或 '' |

---

## 6. 跨模块影响

| 模块 | 变更点 | 风险 |
| --- | --- | --- |
| `ruoyi-common` | `SysUser.java` getter 加 `@NotBlank` | 中（API 契约收紧） |
| `ruoyi-admin` | `SysUserController.java` —— **不改**（沿用 `@Validated`） | 低 |
| `ruoyi-system` | `SysUserMapper.java` + `SysUserMapper.xml` 新增 2 个 method；`SysUserServiceImpl` 新增 `backfillEmptyEmails` 方法 | 中（new mapper method 触发铁律 #2 配套测试） |
| `ruoyi-system` | 新增 `src/test/java/.../SysUserEmailValidationTest.java` | 低 |
| `ruoyi-ui` | `views/system/user/index.vue` `rules.email` 加 `required: true` | 低 |
| `sql/` | 落 `actual/change-impact/.../050-validation/001-backfill-empty-emails.sql`（不落仓库 `sql/`，避免 fixture 漂移） | 高（铁律 #3） |

---

## 7. 升降档规则

- **降 light 条件**（仅当用户明确说"先只改前端"）：不降。**铁律 #2 已触发**，必须保留 SQL 脚本（哪怕不跑）。
- **升 full 条件**（已满足）：DB schema（评估不 DDL）+ 存量数据 + 跨模块 + 铁律 #2/#3。

---

## 8. 未确认项 / 待 Phase 3 收敛

1. 是否需要把 `email` 长度上限从 50 改 100？—— 默认不改
2. 是否需要 `email` `UNIQUE` 索引？—— 已有 `checkEmailUnique` 业务层校验，应用层足够
3. 回填脚本是否要分批（避免长事务）？—— 默认不分批（DBA 决策），但脚本注释给提示
