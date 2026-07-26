# 用户列表导出 Excel（选中用户 + 异步任务）Context Pack

> 生成时间：2026-06-29 14:43:14  |  版本：1.0  |  生成者：impact skill + claude
>
> 导航：**000-context-pack.md** → [010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

> 目标：给后续 agent 一个小而准、可解释的上下文入口。只放本次变更真正需要的证据；看过但暂不相关的内容也要说明原因。

## 1. 变更意图

- 用户原话：用户列表页要能导出 Excel，把选中的用户导出到 Excel，包含所有字段。要权限控制（仅 'system:user:export' 权限的能用），数据量大用异步任务处理。
- 当前假设：在用户列表页接入"选中用户异步导出"，复用已有后端 `/system/user/exportAsync` 接口，前端 `handleExport` 改为传选中 `userIds` 调异步接口并轮询任务状态下载文件。
- 已识别技术栈：Java / Spring Boot / MyBatis（Maven 多模块 RuoYi-Vue），前端 Vue2 + Element UI
- 已加载技术栈规则：`profiles/java-spring-mybatis.md`，DB adapter `db-adapters/mysql.md`
- 任务规模：中
- 成功标准：用户在列表页勾选若干用户后点导出，前端调异步接口提交任务，任务完成后能下载含所选用户全部字段的 Excel；仅有 system:user:export 权限的能操作。
- 长期目标模式：否
- 总目标 / 当前 Step / Backlog（如适用）：不适用
- 项目地图状态：无地图

## 2. 源系统到目标系统对齐（如适用）

不适用。本次不是对齐外部源系统，而是接入项目内已实现的后端能力到前端。

## 3. 分层上下文

| 层级 | 内容 | 结论 |
|------|------|------|
| L1 项目地图 | RuoYi-Vue 多模块 Maven 项目（ruoyi-admin/ruoyi-system/ruoyi-framework/ruoyi-common/ruoyi-ui），Java 17 + Spring Boot + MyBatis + MySQL，前端 Vue2 + Element UI | 技术栈确认，构建命令 `mvn clean package -DskipTests`，测试 `mvn test` |
| L2 变更邻域 | 后端导出链路已完整：SysUserController（export + exportAsync + exportTask）、UserExportTask（状态机）、UserExportTaskLauncher（@Async 入口）、UserExportServiceImpl（导出逻辑）、AsyncConfig（线程池）、SysUser 实体（@Excel 注解）；前端 index.vue handleExport 仍走同步 /export，未传 userIds | 后端完整，前端缺口在 handleExport 未接入异步 + 选中 |
| L3 精准证据 | SysUserController.java:79-105（同步+异步导出接口）、index.vue:452-456（handleExport 走同步）、index.vue:359-363（handleSelectionChange 已收集 this.ids）、UserExportTaskLauncher.java:44-70（@Async runAsync）、AsyncConfig.java:18-32（userExportExecutor 线程池） | 前端已有 ids 收集，handleExport 未用 |

## 4. 相关文件和对象

| 文件/对象 | 类型 | 相关性 | 为什么相关 | 证据 |
|-----------|------|--------|------------|------|
| `ruoyi-ui/src/views/system/user/index.vue` | ui | 3 直接修改候选 | handleExport 需改为调异步接口 + 传选中 userIds + 轮询任务状态下载 | `index.vue:452-456` 走同步 `/system/user/export`，未传 `this.ids` |
| `ruoyi-ui/src/api/system/user.js` | ui | 3 直接修改候选 | 需新增 exportAsync / exportTask 查询的 API 封装方法 | `user.js` 当前无 export 相关方法（同步导出走全局 `this.download`） |
| `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java` | entrypoint | 2 影响判断候选 | 后端 exportAsync/exportTask 已实现，确认接口契约供前端对接 | `SysUserController.java:92-105` exportAsync 接收 userIds + 返回 taskId |
| `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/UserExportTask.java` | service | 2 影响判断候选 | 任务状态机 PENDING→RUNNING→SUCCESS/FAILED，前端轮询依据 | `UserExportTask.java:24-27` Status 枚举 |
| `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/UserExportTaskLauncher.java` | service | 1 背景参考 | @Async 入口，跨 Bean 调用走代理，理解异步执行机制 | `UserExportTaskLauncher.java:44` @Async("userExportExecutor") |
| `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/UserExportServiceImpl.java` | service | 1 背景参考 | 导出逻辑：userIds 筛选 + ExcelUtil 写文件到 downloadPath | `UserExportServiceImpl.java:35-65` exportSelected |
| `ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java` | model | 1 背景参考 | @Excel 注解定义导出字段，确认"所有字段"覆盖范围 | `SysUser.java:28-75` 字段注解 |
| `ruoyi-framework/src/main/java/com/ruoyi/framework/config/AsyncConfig.java` | config | 1 背景参考 | userExportExecutor 线程池配置 | `AsyncConfig.java:18-32` corePoolSize=2 maxPoolSize=4 |
| `ruoyi-system/src/test/java/com/ruoyi/system/service/impl/UserExportTaskLauncherTest.java` | test | 2 影响判断候选 | 已有测试覆盖状态机 + 异步 + @Async 注解回归 | `UserExportTaskLauncherTest.java:62-174` |

相关性说明：

- 3：本次大概率要改。
- 2：不一定改，但影响设计、定级或验证。
- 1：只用于理解风格、约定或背景。
- 0：看过但排除，写入"暂不纳入范围"。

## 5. 关键上下文

### 入口

- `POST /system/user/export`：同步导出（按 query 条件全量，不支持选中）— `SysUserController.java:79-85`
- `POST /system/user/exportAsync`：异步导出，接收 `userIds`（可选）+ `SysUser query`，返回 `{taskId, status}` — `SysUserController.java:92-105`
- `GET /system/user/exportTask/{taskId}`：任务状态查询，返回 `{taskId, status, filePath, errorMsg}` — `SysUserController.java:110-125`

### 数据结构

- `SysUser` 实体含 `@Excel` 注解字段：userId、deptId、userName、nickName、email、phonenumber、sex、status、loginIp、loginDate + `@Excels` 部门（deptName、leader）— `SysUser.java:28-85`
- password 字段无 @Excel 注解，不导出 — `SysUser.java:59`
- `UserExportTask.TaskRecord`：taskId、owner、status(volatile)、filePath(volatile)、errorMsg(volatile) — `UserExportTask.java:29-43`
- `UserExportTask.Status`：PENDING / RUNNING / SUCCESS / FAILED — `UserExportTask.java:24-27`

### 依赖路径

- Controller → UserExportTask.submit（创建任务记录）→ UserExportTaskLauncher.runAsync（@Async 跨 Bean 走代理）→ UserExportServiceImpl.exportSelected（userIds 筛选 + ExcelUtil 写文件）→ SysNotice 通知 — `SysUserController.java:97-100`
- `selectUserList` 带 `@DataScope(deptAlias="d", userAlias="u")` 数据权限 — `SysUserServiceImpl.java:76-77`

### 配置和权限

- 权限标识：`system:user:export`，已注册在 sys_menu（menuId=1004）— `sql/ry_20260417.sql:193`
- 前端权限指令：`v-hasPermi="['system:user:export']"` 已绑定导出按钮 — `index.vue:41`
- 线程池：`userExportExecutor`，corePoolSize=2 / maxPoolSize=4 / queueCapacity=50 / CallerRunsPolicy — `AsyncConfig.java:18-32`
- 文件下载路径：`D:/ruoyi/uploadPath/download/`（来自 `ruoyi.profile`）— `application.yml:10`、`RuoYiConfig.java:110-113`

### 测试

- `UserExportTaskTest.java`：状态机 submit/get 单测 — `UserExportTaskTest.java:33-66`
- `UserExportTaskLauncherTest.java`：runAsync 成功/失败/unknownTaskId + @Async 注解回归 + 跨线程完成 — `UserExportTaskLauncherTest.java:62-174`
- `UserExportServiceImplTest.java`：exportSelected userIds 筛选 + 空数据异常 — `UserExportServiceImplTest.java:44-100`
- 当前可达到的验证等级：V1（静态确认：读代码 + grep 引用 + 人工推演关键路径；未跑 mvn test）

### 风格规范

- `_style-rules.md` 状态：无
- `_project-map.md`【14】：无
- 风格分歧检测：不涉及（无风格规范文件，退回 profile style_axes + 运行时现采）
- 渐进积累：本轮无新增

### 关键链路追踪

| 链路类型 | 入口 | 追踪路径 | 发现的二级影响 |
|---------|------|---------|--------------|
| 错误处理链 | exportAsync 提交后 service 抛异常 | UserExportTaskLauncher.runAsync catch → status=FAILED + errorMsg + 失败通知 | 前端轮询到 FAILED 需展示 errorMsg，不能只显示"失败" |
| 中间件管线 | @PreAuthorize("@ss.hasPermi('system:user:export')") | Spring Security AOP 拦截 → 无权限返回 403 | 前端调 exportAsync 无权限时收到 403，需提示用户无权限而非静默失败 |
| 数据流路径 | 前端 handleExport 传 userIds | this.ids → POST body userIds → UserExportServiceImpl 筛选 → ExcelUtil 写 xlsx → filePath 返回 | 异步任务文件落在服务器 downloadPath，前端需通过 filePath 或单独下载接口取回；当前 exportTask 返回 filePath 但无文件下载接口 |
| 配置依赖 | ruoyi.profile = D:/ruoyi/uploadPath | RuoYiConfig.getDownloadPath() → 写文件路径 | 生产环境路径可能与开发不同，filePath 是服务器绝对路径，前端不能直接用 |

> 追踪发现：exportTask 接口返回 `filePath`（服务器绝对路径），但**没有提供根据 taskId 下载文件的接口**。前端轮询到 SUCCESS 后，需要下载文件的途径。这是潜在缺口，但当前同步 `/export` 接口是直接流式响应下载，异步导出的文件下载方式需确认。

## 6. 引用检查结果

| 分类 | 文件/对象 | 影响 | 处理方式 |
|------|-----------|------|----------|
| 必须同步修改 | `ruoyi-ui/src/views/system/user/index.vue` handleExport | 未接入异步 + 选中 userIds，不勾选也能导全部但走同步，选中后导不出选中项 | 纳入实施 Step 1：改 handleExport 调异步接口传 this.ids + 轮询 |
| 必须同步修改 | `ruoyi-ui/src/api/system/user.js` | 缺 exportAsync / exportTask 的 API 封装方法 | 纳入实施 Step 1：新增 API 方法 |
| 只需验证 | 异步导出文件下载方式 | exportTask 返回服务器 filePath，前端用末尾文件名调 RuoYi 内置 `/common/download` 下载 | 验证项：`CommonController.java:45-60` 已提供通用下载接口 |
| 只需验证 | `SysUserController.java` exportAsync/exportTask | 后端已实现，逻辑不变 | 验证项：接口契约与前端调用一致 |
| 暂不纳入 | `UserExportTask.java` / `UserExportTaskLauncher.java` / `UserExportServiceImpl.java` / `AsyncConfig.java` | 后端异步链路已完整实现且有测试，本次只做前端接入 | 排除原因：后端无需改动，已有单测覆盖 |

> 找不到引用时写"未找到引用"，不得写成"无影响"。

## 7. 已确认事实

- 后端 `/system/user/exportAsync` 已实现，接收 `userIds`（Long[] 可选）+ `SysUser query`，返回 `{taskId, status}` — 来源：`SysUserController.java:92-105`
- 后端 `/system/user/exportTask/{taskId}` 已实现，返回 `{taskId, status, filePath, errorMsg}` — 来源：`SysUserController.java:110-125`
- `system:user:export` 权限已注册（menuId=1004）且已绑定到 export/exportAsync/exportTask 三个接口 — 来源：`sql/ry_20260417.sql:193`、`SysUserController.java:78,91,110`
- 异步执行走 `UserExportTaskLauncher.runAsync`（@Async("userExportExecutor")），跨 Bean 调用走 Spring 代理，已修复 self-invocation bug — 来源：`UserExportTaskLauncher.java:44`、`SysUserController.java:100`
- 导出字段覆盖：userId/deptId/userName/nickName/email/phonenumber/sex/status/loginIp/loginDate + 部门 deptName/leader；password 不导出 — 来源：`SysUser.java:28-85`
- `selectUserList` 带 `@DataScope` 数据权限，导出受数据权限约束 — 来源：`SysUserServiceImpl.java:76-77`
- 前端 `handleSelectionChange` 已收集 `this.ids`（选中用户 userId 数组）— 来源：`index.vue:359-363`
- 前端 `handleExport` 当前走同步 `this.download('system/user/export', {...this.queryParams})`，未传 this.ids — 来源：`index.vue:452-456`
- 前端导出按钮已绑定 `v-hasPermi="['system:user:export']"` — 来源：`index.vue:41`
- 异步任务文件落在 `RuoYiConfig.getDownloadPath()`（`D:/ruoyi/uploadPath/download/`）— 来源：`UserExportServiceImpl.java:62`、`RuoYiConfig.java:110-113`
- exportTask 返回的 filePath 是服务器绝对路径（如 `D:/ruoyi/uploadPath/download/xxx.xlsx`）— 来源：`UserExportServiceImpl.java:62-64`、`SysUserController.java:122`

## 8. 待确认问题

> Phase 3 Step 3.0 不确定项分类后，代码可推断项已自行查证并写入 §7「已确认事实」，此处只保留业务需决策项。

### 代码推断项（已自行查证，无需用户确认）

- 前端已有 `this.ids` 收集选中用户 — 代码推断：`index.vue:359-363` — 依据：handleSelectionChange 将 selection.map 为 userId 存入 this.ids
- 后端 exportAsync 接收 userIds 参数名 — 代码推断：`SysUserController.java:94` — 依据：`@RequestParam(value = "userIds", required = false) Long[] userIds`
- 任务状态枚举值 — 代码推断：`UserExportTask.java:24-27` — 依据：`enum Status { PENDING, RUNNING, SUCCESS, FAILED }`
- 线程池拒绝策略为 CallerRunsPolicy（队列满时调用线程执行）— 代码推断：`AsyncConfig.java:27` — 依据：`setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy())`
- 异步导出文件下载方式 — 代码推断：`CommonController.java:45-60` — 依据：RuoYi 内置 `GET /common/download?fileName=xxx&delete=false`，从 `RuoYiConfig.getDownloadPath() + fileName` 读取文件流式下载；exportTask 返回的 filePath 末尾文件名可直接作为 fileName 参数传入

### 待用户确认项（业务决策）

无。所有不确定项均已通过代码推断消化。

## 9. 暂不纳入范围

| 文件/对象 | 排除原因 |
|-----------|----------|
| `UserExportTask.java` | 后端状态机已完整实现且有单测，本次只做前端接入 |
| `UserExportTaskLauncher.java` | @Async 入口已实现且有单测，无需改动 |
| `UserExportServiceImpl.java` | 导出逻辑（userIds 筛选 + 写文件）已实现且有单测 |
| `AsyncConfig.java` | 线程池配置已就绪，无需调整 |
| `SysUser.java` | @Excel 注解字段已定义，导出字段覆盖完整 |
| 后端三个测试文件 | 已覆盖状态机/异步/导出逻辑，本次前端改动不破坏后端测试 |
| 数据库 schema | 无 schema 变更，sys_menu 已有 system:user:export 权限记录 |
