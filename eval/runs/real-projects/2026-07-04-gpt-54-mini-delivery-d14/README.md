# LOCKED 用户状态影响分析

需求：现有用户状态只有“正常 / 停用”，需要新增 `LOCKED` 状态，锁定后不能登录。  
当前只做影响分析，不改代码。

## 判分方复核

Overall status: **FAIL**

内容分析质量可用，但本场景是 `impact-phase4` / `phase4-docs`，需要在 fixture 内产出标准 Phase 4 full 文档。实际运行只写了本归档 README，没有创建 `change-impact/locked-user/000-context-pack.md`、`010-requirements.md`、`020-design.md`、`030-implementation.md`、`_active-state.md`，也没有运行 `impact_validate.py`。

独立复跑：

```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py `
  --fixture E:\agent\real-project-fixtures\java-ruoyi-d14-gpt54mini-20260704-221627 `
  --scenario D14-java-enum-analysis `
  --run-record eval\runs\real-projects\2026-07-04-gpt-54-mini-delivery-d14\README.md `
  --requirement-dir change-impact\locked-user `
  --json
```

结果：`FAIL`，`phase4-artifacts` 缺 5 个 full 模式必需文档；`analysis-source-diff` 为 PASS，说明没有源码改动。

## 结论

这是一个 **full 级** 变更，不适合按轻量改动处理。

原因很直接：

- 涉及用户状态枚举和常量定义
- 涉及登录认证分支
- 涉及后台用户管理页的状态展示、筛选和修改
- 涉及国际化提示文案
- 涉及字典数据 `sys_normal_disable`
- 还和系统里已有的“密码输错锁定”概念撞名，容易混淆

## 现状

代码里，用户状态目前是三段语义，但只有两种“可登录”态：

- `SysUser.status` 只有“0 正常 / 1 停用”
- `UserStatus` 枚举只有 `OK / DISABLE / DELETED`
- 登录时只要 `status == '1'` 就会抛 `UserBlockedException`，最终变成 Shiro 的 `LockedAccountException`
- 后台页面把“用户状态”做成了 `sys_normal_disable` 字典和 0/1 开关

同时，项目里已经有另一套“锁定”语义：

- 密码输错次数超限会走 `UserPasswordRetryLimitExceedException`
- 黑名单 IP 会走 `BlackListException`

所以这次新增 `LOCKED`，不能只当成一个文案或一个取值改动看。

## 覆盖表

| 维度 | 现状 | 影响文件 / 位置 | 结论 |
|---|---|---|---|
| 数据产生点 | 用户新增、编辑、改状态、导入时都能写 `status` | [`SysUserController.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java:142), [`SysUserServiceImpl.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java:221), [`SysUserMapper.xml`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml:177) | 必须同步看 |
| 状态/字段定义 | `SysUser.status` 只有 0/1 语义，`UserStatus` 里已有 `DELETED="2"` | [`SysUser.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java:72), [`UserStatus.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-common/src/main/java/com/ruoyi/common/enums/UserStatus.java:10), [`UserConstants.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-common/src/main/java/com/ruoyi/common/constant/UserConstants.java:16) | 必须同步看 |
| 持久化位置 | `sys_user.status` 是 `char(1)`，目前默认值是 `0` | [`sql/ry_20260319.sql`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/sql/ry_20260319.sql:54) | 结构上未必要改表，但要确认取值 |
| 对外接口 | 登录失败提示、用户状态修改接口、用户列表过滤 | [`SysLoginService.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-framework/src/main/java/com/ruoyi/framework/shiro/service/SysLoginService.java:113), [`SysLoginController.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysLoginController.java:68), [`SysUserController.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java:324) | 必须同步看 |
| 前端展示 | 列表页、详情页、新增/编辑页都只认识 0/1 | [`user.html`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-admin/src/main/resources/templates/system/user/user.html:44), [`view.html`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-admin/src/main/resources/templates/system/user/view.html:59), [`add.html`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-admin/src/main/resources/templates/system/user/add.html:93), [`edit.html`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-admin/src/main/resources/templates/system/user/edit.html:72) | 必须同步看 |
| 导出 / 报表 | 用户状态的 Excel 注解仍是 0/1 | [`SysUser.java`](E:/agent/real-project-fixtures/java-ruoyi-d14-gpt54mini-20260704-221627/ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java:72) | 必须同步看 |
| 测试入口 | 仓库里没找到直接覆盖这条链路的测试 | `rg` 未找到 `*Test.java` 中的用户状态/登录测试 | 需要补测试 |
| 明确排除项 | 角色、部门、岗位状态不是这次的主链路 | `SysRole*`、`SysDept*`、`SysPost*` 只作为背景引用 | 暂不纳入 |

## 影响链路

### 1. 登录链路

现在的登录判断是：

1. 查用户
2. 看 `del_flag`
3. 看 `status`
4. `status == '1'` 就直接拒绝登录

也就是说，`LOCKED` 一旦加入，登录判断一定要多一个分支，否则“锁定后不能登录”不会生效。  
而且目前用户停用和“登录锁定”已经共用 `UserBlockedException` / `LockedAccountException` 这套异常语义，新增 `LOCKED` 后，提示文案也要分清是“账号状态锁定”还是“密码错误锁定”。

### 2. 后台用户管理页

当前后台是二值状态：

- 列表页状态列只做了开关图标
- 新增 / 编辑页都是一个 checkbox
- 详情页直接用 `status == '0' ? '正常' : '停用'`
- 列表筛选下拉框来自 `sys_normal_disable`

所以如果 `LOCKED` 要让管理员可见、可筛选、可切换，前端至少要一起改：

- 列表页状态列要能显示第三种状态
- 详情页要能显示 `LOCKED`
- 新增 / 编辑页要能设置 `LOCKED`
- 列表筛选要能按 `LOCKED` 查

如果不打算让管理员手动设成 `LOCKED`，那也至少要说明这个状态由谁写入、在哪个接口写入。现在代码里没有这个入口。

### 3. 字典数据

`sys_normal_disable` 现在只有：

- `0 = 正常`
- `1 = 停用`

它不只是用户页在用，项目里还有很多地方复用这套字典。  
所以这里有一个很重要的分叉：

- 直接把 `LOCKED` 加进 `sys_normal_disable`，会把这个“两态开关”变成三态，其他共用页面也会跟着变
- 新建一个更贴近用户状态的新字典类型，可以把影响收窄，但要改用户页绑定的字典来源

这不是代码能替你拍板的地方，得先定业务口径。

### 4. 持久化和 SQL

从表结构看，`sys_user.status` 是 `char(1)`，所以**单看字段长度**，新增一个单字符状态不一定要改表。  
但这不代表没影响：

- 默认值还是 `0`
- 现有种子数据只有 `0`
- 现有 SQL 和页面都假设只有 `0/1`

如果 `LOCKED` 要进入初始化脚本、演示数据或后续迁移脚本，就得补数据变更。这个更像字典/初始化数据调整，不是表结构调整。

### 5. 国际化与错误提示

当前国际化里已经有：

- `user.blocked=用户已封禁，请联系管理员`
- `user.password.delete=对不起，您的账号已被删除`

如果新增 `LOCKED`，要决定：

- 继续复用 `user.blocked`
- 还是新增一个专门的 key，例如“账号已锁定”

这会影响登录失败时用户看到的提示，也会影响后续排障时能不能一眼区分“账号被管理员锁定”和“密码输错触发的临时锁定”。

## 需要确认的点

1. `LOCKED` 的编码值要用什么。现在代码里没有这个值，`status` 虽然是 `char(1)`，但 `UserStatus` 里已经占了 `2 = 删除` 的语义，不能直接想当然。
2. `LOCKED` 是不是要让管理员在用户管理页手动设置。现在页面只有 0/1 开关，没有第三种入口。
3. `sys_normal_disable` 要不要继续复用。这个字典已经被很多页面共用，改它会把影响带到别处。
4. 登录提示要不要区分“停用”和“锁定”。现在两者都可能落到 `user.blocked` 一类提示里。

## 测试建议

这条链路不能只看页面，至少要补这些验证：

- 登录时 `status=LOCKED` 的拒绝分支
- 用户管理页对 `LOCKED` 的展示和筛选
- `changeStatus` 或新增接口对 `LOCKED` 的写入
- 字典显示和导出文案

当前仓库里没找到现成的用户状态/登录测试用例，所以这块最好补一组直接命中的测试。

## 排除项

这次先不纳入：

- 角色、部门、岗位的状态字段
- 在线会话状态
- 密码输错次数锁定那条逻辑本身

它们和“用户账号状态 LOCKED”有关联，但不是这次需求的主改动点。
