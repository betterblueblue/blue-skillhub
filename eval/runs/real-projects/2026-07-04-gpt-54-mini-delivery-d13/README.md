# 用户导出仅限管理员的影响分析

## 1. 变更意图

目标是把“用户列表导出”收紧为只有管理员可用。当前项目里，导出入口同时受前端按钮和后端权限注解控制；默认初始化数据又把 `system:user:export` 分给了普通角色，所以演示环境里普通用户也能看到并调用导出。

这里有一个需要先说清的口径问题：代码里的“管理员”不是单一概念。

- `ShiroUtils.isAdmin(Long userId)` 认的是 `userId == 1`【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-common\src\main\java\com\ruoyi\common\utils\ShiroUtils.java:78-90】
- `SysRole.isAdmin(Long roleId)` 认的是 `roleId == 1`【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-common\src\main\java\com\ruoyi\common\core\domain\entity\SysRole.java:79-85】
- 登录授权里，`UserRealm` 对 `user.isAdmin()` 直接放行到 `*:*:*`【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-framework\src\main\java\com\ruoyi\framework\shiro\realm\UserRealm.java:66-69】

所以这次需求有两种理解：

1. 只允许系统内置超级管理员账号导出，也就是 `userId == 1`
2. 只允许拥有管理员角色的用户导出，也就是按角色关系判断

现有代码更接近第一种，但产品文案写的是“管理员角色”，所以这里是本次分析里最重要的未确认点。

## 2. 覆盖范围

| 项目 | 现状 | 影响判断 |
|---|---|---|
| 数据产生点 | 用户列表导出走 `SysUserController.export`，内部复用 `userService.selectUserList(user)`【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\java\com\ruoyi\web\controller\system\SysUserController.java:82-89】【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-system\src\main\java\com\ruoyi\system\service\impl\SysUserServiceImpl.java:81-84】 | 直接相关 |
| 状态/字段定义 | 导出权限字符是 `system:user:export`；普通角色菜单初始化里已经包含 `1004` 用户导出【已核实: E:\agent\real-project-fixtures\java-ruoyi\sql\ry_20260319.sql:183-188】【已核实: E:\agent\real-project-fixtures\java-ruoyi\sql\ry_20260319.sql:272-273】 | 直接相关 |
| 持久化位置 | 权限菜单写在 `sys_menu`，角色-菜单关系写在 `sys_role_menu`，用户-角色关系写在 `sys_user_role`【已核实: E:\agent\real-project-fixtures\java-ruoyi\sql\ry_20260319.sql:279-373】 | 直接相关 |
| 对外接口 | `POST /system/user/export`，受 `@RequiresPermissions("system:user:export")` 保护【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\java\com\ruoyi\web\controller\system\SysUserController.java:82-85】 | 直接相关 |
| 前端展示 | `user.html` 上的“导出”按钮同样按 `shiro:hasPermission="system:user:export"` 控制【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\resources\templates\system\user\user.html:77】 | 直接相关 |
| 导出/报表 | 导出实现最终落到 `ExcelUtil.exportExcel`【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\java\com\ruoyi\web\controller\system\SysUserController.java:89】【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-common\src\main\java\com\ruoyi\common\utils\poi\ExcelUtil.java:539-580】 | 只需验证 |
| 测试入口 | 仓库里未找到 `src/test`、`*Test.java` 或 `*Tests.java` 的现成用户导出测试 | 暂缺 |
| 明确排除项 | 角色导出、岗位导出、字典导出、日志导出不在本次范围内，虽然它们也用了同类导出模式【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\java\com\ruoyi\web\controller\system\SysRoleController.java:72-79】【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\java\com\ruoyi\web\controller\system\SysPostController.java:55-62】 | 暂不纳入 |

## 3. 现状结论

1. 导出不是一个“隐式能力”，而是明确的权限点 `system:user:export`。
2. 页面按钮和后端接口都挂在这个权限点上，单改前端隐藏不够，直接调接口仍可能命中后端。
3. 默认初始化数据里，`普通角色` 已经被分配了 `1004 用户导出`，所以 demo 数据下普通用户能导出并不意外。
4. 导出的数据本身不是全表裸查，仍走用户列表查询和数据权限控制；这次改的是“谁能发起导出”，不是“导出内容长什么样”。

## 4. 需要同步判断的点

- 如果“管理员”指系统内置超级管理员账号，后端最好以 `ShiroUtils.isAdmin()` 为准。
- 如果“管理员”指某个角色成员，现有代码没有一条统一的角色级管理员判断，得先定清楚口径。
- 仅删除 `sys_menu` 里的 `1004` 不够稳，因为已有角色授权数据可能仍保留。
- 仅改前端按钮不够稳，因为后端导出接口还在。

## 5. 影响面排序

必须同步处理：

1. `SysUserController.export` 的后端访问控制。
2. `user.html` 的导出按钮展示。
3. 初始化数据里 `system:user:export` 的默认授权。

需要用户决策：

1. “管理员”到底按 `userId == 1` 还是按角色成员判断。
2. 现存非管理员角色里，是否要保留导出权限的历史数据。

只需验证：

1. 其他用户管理动作是否还保留原权限。
2. 导出文件格式和内容是否不变。

## 6. 建议的最小改法

如果按当前代码口径收紧，最小动作是：

1. 后端在 `POST /system/user/export` 再加一层管理员判断。
2. 前端按钮继续保留 `shiro:hasPermission`，但实际可见性会自然收窄。
3. 清理默认菜单授权里 `1004` 对非管理员角色的分配，避免初始化数据继续放开。

这组改法不会碰导出格式，也不会改用户列表查询逻辑本身。

## 7. 验证建议

- 用内置管理员账号访问用户列表，确认导出仍可用。
- 用普通用户账号访问同一路由，确认页面按钮不显示，手动 POST 也被拦。
- 回看 `sys_role_menu` 和现有角色授权，确认没有遗留的导出权限。

## 8. 已确认事实

- 项目是 Java Spring Boot + MyBatis 的多模块 RuoYi 工程，主配置和 MySQL 连接都在 `ruoyi-admin` 下【已核实: E:\agent\real-project-fixtures\java-ruoyi\pom.xml:107-111】【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\resources\application.yml:17-22】【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\resources\application-druid.yml:1-9】。
- 用户导出入口是 `SysUserController.export`，权限字符是 `system:user:export`【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\java\com\ruoyi\web\controller\system\SysUserController.java:82-89】。
- 页面按钮也是同一个权限字符【已核实: E:\agent\real-project-fixtures\java-ruoyi\ruoyi-admin\src\main\resources\templates\system\user\user.html:77】。
- 默认菜单数据已经包含 `用户导出`，并且普通角色 `2` 在初始化时拿到了这条权限【已核实: E:\agent\real-project-fixtures\java-ruoyi\sql\ry_20260319.sql:187】【已核实: E:\agent\real-project-fixtures\java-ruoyi\sql\ry_20260319.sql:272-273】。
- 当前仓库没有找到专门覆盖用户导出的测试文件。

## 9. 不采用的推断

- 不把“当前所有用户都能导出”直接等同于“后端没有权限控制”。事实是后端有控制，只是默认数据把权限分出去了。
- 不把 `role_key = 'admin'` 当成唯一管理员判断依据。代码里真正的管理员判断散在 `userId == 1` 和 `roleId == 1` 两套逻辑里。
- 不把其他模块的导出权限一起改掉。它们是同类实现，不是本次需求对象。

