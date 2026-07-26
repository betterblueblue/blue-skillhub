# 000-context-pack — add-user-export-excel

> 需求：在 SysUserController 的 /export 之外，新增一个异步版本 /exportAsync，
> 支持按 userIds 数组（前端多选框）+ 已有查询条件筛选，把选中的用户导出为 Excel。
> 保留原 /export 同步路径。异步任务使用 @Async + ThreadPoolTaskExecutor，
> 完成后通过 SysNotice 通知当前用户。

---

## 1. 现有代码引用（Read 自 workdir，绝对路径）

| # | 路径 | 行 | 关键片段 |
|---|------|----|---------|
| C1 | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java` | 68-76 | 现有同步 export：`@PreAuthorize("@ss.hasPermi('system:user:export')") @PostMapping("/export") public void export(...)` |
| C2 | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java` | 1-29 | import：`HttpServletResponse / ExcelUtil / SysUser / SecurityUtils / PreAuthorize` |
| C3 | `ruoyi-system/src/main/java/com/ruoyi/system/service/ISysUserService.java` | 20, 216 | 接口：`selectUserList(SysUser)` / `importUser(...)`（无 export 方法） |
| C4 | `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java` | 75-80 | `selectUserList` 走 `@DataScope(deptAlias = "d", userAlias = "u")` + `userMapper.selectUserList(user)` |
| C5 | `ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml` | — | `selectUserList` 是 XML 实现，参数 `user` 包含所有条件字段 |
| C6 | `ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java` | 28-95 | `@Excel(name=...)` 注解字段：userId/deptId/userName/nickName/email/phonenumber/sex/status/loginIp/loginDate/dept.leader/dept.deptName |
| C7 | `ruoyi-framework/src/main/java/com/ruoyi/framework/manager/AsyncManager.java` | — | 已有 AsyncManager：单线程 scheduleAtFixedRate 风格（用于登录日志），不适合长任务 |
| C8 | `sql/ry_20260417.sql` | 193 | 已有菜单：`insert into sys_menu values('1004', '用户导出', '100', '5', '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:export', '#', 'admin', sysdate(), '', null, '')` |
| C9 | `ruoyi-admin/src/main/resources/application-druid.yml` | 11 | `password: password`（master 库）— 项目自带默认占位，本文档不复制其字面量 |
| C10 | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java` | 78-88 | 现有 /importData 走 `ExcelUtil<SysUser>.importExcel` —— 确认项目用 EasyExcel 包装类 |

## 2. 关键代码片段（未截断，复制自源文件）

### C1 — 现有同步 export
```java
@Log(title = "用户管理", businessType = BusinessType.EXPORT)
@PreAuthorize("@ss.hasPermi('system:user:export')")
@PostMapping("/export")
public void export(HttpServletResponse response, SysUser user)
{
    List<SysUser> list = userService.selectUserList(user);
    ExcelUtil<SysUser> util = new ExcelUtil<SysUser>(SysUser.class);
    util.exportExcel(response, list, "用户数据");
}
```

### C4 — 现有 selectUserList
```java
@Override
@DataScope(deptAlias = "d", userAlias = "u")
public List<SysUser> selectUserList(SysUser user)
{
    return userMapper.selectUserList(user);
}
```

### C6 — SysUser @Excel 字段（节选）
```java
@Excel(name = "用户序号", type = Type.EXPORT, cellType = ColumnType.NUMERIC, prompt = "用户编号")
private Long userId;

@Excel(name = "部门编号", type = Type.IMPORT)
private Long deptId;

@Excel(name = "登录名称")
private String userName;

@Excel(name = "用户名称")
private String nickName;
```

## 3. 风格基线（基于以上证据）

| 维度 | 现状 | 复用策略 |
|------|------|---------|
| Controller 注解 | `@PreAuthorize` + `@Log` + `@PostMapping` | 新增 /exportAsync 复用同模板 |
| 权限标识 | 字符串字面量 `'system:user:export'` | 复用同串，不引入新标识 |
| Excel 工具 | `com.ruoyi.common.utils.poi.ExcelUtil` | 复用同 util，不引入 EasyExcel 直接调用 |
| Service 命名 | `ISysUserService` + `SysUserServiceImpl` | 新增 `IUserExportService` 独立 Service（按职责拆） |
| Mapper 调用 | `userMapper.selectUserList(user)` | 复用，不新增 XML |
| 数据权限 | `@DataScope(deptAlias, userAlias)` 注解在 Service 方法 | 新查询路径必须保留 |
| 异步执行 | 已有 `AsyncManager` 走定时线程 | 不复用（不适配），改用 `@Async` + 自定义 ThreadPoolTaskExecutor |
| 通知方式 | 项目无 SysNotice 调用样例 | 通过 ISysNoticeService.insert 直接落库 |

## 4. 反向引用检查（Grep 3 次）

```
rg "system:user:export" -- 已锁定 sql/ry_20260417.sql:193 + Controller:69
rg "ExcelUtil<SysUser>" -- 已锁定 Controller:74/83/93
rg "@DataScope" -- 已锁定 SysUserServiceImpl:76/89/102
```

无悬空引用、无孤岛。

## 5. 风险摘要（衔接 Phase 2.5）

- P0: 异步端点必须 200ms 内返回 taskId（不能同步阻塞）
- P0: 失败路径必须有结构化错误 + SysNotice
- P1: SysUser 未标 @Excel 的字段（avatar/password/delFlag/pwdUpdateDate）默认不导出
- P1: 线程池需配置独立 name + 拒绝策略（CallerRuns 兜底）
- P2: 文件落地路径用 java.io.tmpdir（不写死）

## 6. 输出文件策略

- 新文件：`IUserExportService.java` / `UserExportServiceImpl.java` / `UserExportTask.java` / `UserExportTaskTest.java`
- 修改文件：`SysUserController.java`（新增端点 + 注入 Service）
- 复用文件：`ISysUserService.selectUserList`（无改动）
- SQL：不新增（权限已存在 menu_id=1004）
