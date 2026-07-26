# 用户列表导出 Excel（选中用户 + 异步任务）设计文档

> 生成时间：2026-06-29 14:43:14  |  版本：1.0  |  生成者：impact skill + claude
>
> 导航：[010-requirements.md](010-requirements.md) → **020-design.md** → [030-implementation.md](030-implementation.md) → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

## 1. 设计概览

本次变更把用户列表页的导出按钮从同步导出改为接入已有的异步导出流程。前端 `handleExport` 改为调用 `POST /system/user/exportAsync`，传入勾选的用户编号数组（`this.ids`）和当前查询条件，拿到任务编号后轮询 `GET /system/user/exportTask/{taskId}`，任务成功后通过 RuoYi 内置的 `GET /common/download` 接口下载生成的 Excel 文件。

核心决策有三点：第一，复用后端已完整实现的异步导出链路（任务状态机 + 专用线程池 + 数据权限），后端零改动；第二，前端新增两个 API 封装方法（提交异步导出、查询任务状态），保持与现有 API 文件风格一致；第三，文件下载复用 RuoYi 内置通用下载接口，避免新增后端接口。这样改动范围收敛在前端两个文件，风险可控。

## 2. 分析依据

| 类型 | 证据来源 | 已确认事实 / 未确认项 |
|------|----------|----------------------|
| 已确认 | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java:92-105` | 异步导出接口已实现，接收 userIds + query，返回 taskId + status |
| 已确认 | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java:110-125` | 任务状态查询接口已实现，返回 taskId + status + filePath + errorMsg |
| 已确认 | `ruoyi-admin/src/main/java/com/ruoyi/web/controller/common/CommonController.java:45-60` | RuoYi 内置通用下载接口 `GET /common/download?fileName=xxx&delete=false`，从 downloadPath 读取文件 |
| 已确认 | `ruoyi-ui/src/views/system/user/index.vue:359-363` | 前端 handleSelectionChange 已收集 this.ids（选中用户编号数组） |
| 已确认 | `ruoyi-ui/src/views/system/user/index.vue:452-456` | 当前 handleExport 走同步 this.download，未传 this.ids |
| 已确认 | `ruoyi-system/src/main/java/com/ruoyi/system/service/impl/UserExportTask.java:24-27` | 任务状态枚举 PENDING/RUNNING/SUCCESS/FAILED |
| 未确认 | 无 | 所有不确定项已通过代码推断消化 |
| 不采用的推断 | 不新增后端文件下载接口 | exportTask 返回的 filePath 含服务器绝对路径，但末尾文件名可直接传给内置 /common/download，无需新接口 |

> Context Pack 摘要见 `change-impact/add-user-export-excel-rerun/000-context-pack.md`，不在本文档重复。

## 3. 变更明细

### 代码

| 对象 | 当前逻辑 | 变更操作 | 目标逻辑 | 影响说明 |
|------|----------|----------|----------|----------|
| `ruoyi-ui/src/api/system/user.js` | 无导出相关 API 方法（同步导出走全局 this.download） | 新增 | 新增 `exportUserAsync`（提交异步导出）和 `getUserExportTask`（查询任务状态）两个方法 | 前端 API 层新增两个方法，不影响现有方法 |
| `ruoyi-ui/src/views/system/user/index.vue` handleExport | 调 `this.download('system/user/export', {...this.queryParams})` 同步导出 | 修改 | 改为调 exportUserAsync 传 this.ids + queryParams，轮询任务状态，成功后用 this.download 下载文件 | 导出按钮行为从同步改为异步轮询 |

### 接口/契约

| 对象 | 当前定义 | 变更操作 | 目标定义 | 影响说明 |
|------|----------|----------|----------|----------|
| `POST /system/user/exportAsync` | 已存在，前端未调用 | 前端接入 | 前端 handleExport 调用此接口 | 接口契约不变，只是新增调用方 |
| `GET /system/user/exportTask/{taskId}` | 已存在，前端未调用 | 前端接入 | 前端轮询此接口 | 接口契约不变 |
| `GET /common/download` | 已存在（通用下载） | 前端接入 | 任务成功后用此接口下载文件 | 接口契约不变 |

## 4. 代码风格报告

项目前端使用 Vue2 + Element UI，API 方法统一封装在 `src/api/system/user.js` 中，每个方法用 `export function` 导出，内部调用 `request`（来自 `@/utils/request`），参数通过 `params`（GET）或 `data`（POST）传递。列表页 `index.vue` 在 `methods` 中定义操作方法，通过 `import` 引入 API 方法，用 `this.$modal` 做消息提示，用 `this.download` 做文件下载（全局挂载在 `Vue.prototype`）。

后端使用 Spring Boot + MyBatis，Controller 方法用 `@PreAuthorize("@ss.hasPermi('xxx')")` 做权限校验，用 `@Log` 记录操作日志，返回 `AjaxResult` 统一包装。本次新增的前端 API 方法遵循现有 `user.js` 的 `export function` + `request` 模式，handleExport 改造遵循现有 methods 风格，不引入新的依赖或模式。

### 实施阶段风格约束

> 由当前技术栈规则的 `style_axes` 动态生成。参考背景资料中发现的实际代码，不使用预置标签。

| style_axes 轴名 | 从代码现采的约束内容 |
|-----------------|---------------------|
| api_response | 后端返回 AjaxResult 统一包装 {code, msg, data}，前端 request 拦截器自动处理 code（`user.js:1` import request） |
| layering | 前端 API 方法集中在 api/ 目录，页面 import 后调用（`index.vue:178` import { listUser, ... } from "@/api/system/user"） |
| logging | 后端用Slf4j + {} 占位符（`UserExportTaskLauncher.java:31,50,64`） |
| naming | 前端 API 方法驼峰命名（listUser/getUser），页面方法驼峰（handleExport/handleSelectionChange） |
| exception | 后端自定义 ServiceException + ControllerAdvice 统一处理（`UserExportServiceImpl.java:55` throw ServiceException） |

## 5. 替代方案与权衡

| 方案 | 思路 | 优点 | 缺点 | 风险 |
|------|------|------|------|------|
| A: 前端接入异步导出（本次选定） | handleExport 改调 exportAsync 传 userIds + 轮询 + 通用下载 | 复用全部已有后端能力，改动最小，支持选中 + 异步 | 前端需实现轮询逻辑 | 轮询间隔和超时需合理设置 |
| B: 保留同步导出，只加选中传参 | 把 this.ids 传给同步 /export 接口 | 改动更小 | 同步导出大数据量阻塞页面，不符合"异步任务处理"需求 | 违背用户明确要求的异步需求 |
| C: 后端新增流式异步下载接口 | 新增一个接口直接流式返回异步生成的文件 | 前端不用轮询 | 需改后端，违背"后端已就绪"现状，且无法支持任务状态可见 | 后端改动引入新风险 |
| → 选了 A，理由：复用已完整实现的后端异步链路，改动收敛在前端两文件，满足选中+异步+权限全部需求 |

## 6. 横切关注点

| # | 维度 | 是否涉及 | 检查要点 | 本变更的处理 |
|---|------|----------|----------|-------------|
| 1 | 权限校验 | ☑ | 新接口是否鉴权、现有权限是否需调整 | 三个导出接口已绑定 system:user:export 权限（`SysUserController.java:78,91,110`），前端按钮已绑 v-hasPermi（`index.vue:41`），无需新增权限 |
| 2 | 操作审计日志 | ☑ | 关键写操作是否记录审计日志 | exportAsync 已加 @Log(businessType=EXPORT)（`SysUserController.java:90`），异步导出自动记录审计 |
| 3 | 敏感数据脱敏 | ☑ | 返回值、日志、导出中的敏感字段是否脱敏 | 导出字段已排除 password（`SysUser.java:59` 无 @Excel 注解），loginIp 等字段按现有导出注解输出 |
| 4 | 缓存失效 | ☐ | 变更涉及的缓存键是否需要刷新/失效 | 不涉及缓存，导出是只读查询+文件生成 |
| 5 | 事务边界 | ☐ | 跨表/跨服务操作的事务一致性 | 不涉及，导出只读不写库 |
| 6 | 消息队列/事件 | ☐ | 是否产生或消费事件，Schema 是否变更 | 不涉及消息队列，异步走线程池非 MQ |
| 7 | 国际化 | ☐ | 是否涉及多语言文案 | 不涉及，前端提示文案沿用现有中文风格 |
| 8 | 并发控制 | ☑ | 是否需要乐观锁/悲观锁/分布式锁 | 任务记录用 ConcurrentHashMap + volatile（`UserExportTask.java:45,33-34`），线程池 CallerRunsPolicy 限流，无需额外锁 |
| 9 | 限流/熔断 | ☑ | 新接口或变更接口是否需要限流 | 线程池 queueCapacity=50 + CallerRunsPolicy 拒绝策略（`AsyncConfig.java:24,27`），队列满时降级为同步执行，天然限流 |
| 10 | 数据迁移 | ☐ | 存量数据是否需要转换、回填 | 不涉及，无 schema 变更 |
| 11 | 向后兼容 | ☑ | API/数据/配置变更是否破坏现有消费者 | 同步 /export 接口保留不动，新增的是前端调用方，后端契约不变，完全向后兼容 |
| 12 | 监控告警 | ☐ | 是否需要新增/调整监控指标和告警规则 | 不涉及，本次只接前端，后端已有日志 |
| 13 | 配置灰度 | ☐ | 配置变更是否需要灰度发布 | 不涉及配置变更 |
| 14 | 依赖服务可用性 | ☑ | 下游服务不可用时是否降级 | 异步任务失败时 status=FAILED + errorMsg + 失败通知（`UserExportTaskLauncher.java:62-68`），前端轮询到 FAILED 展示原因 |
| 15 | 性能影响 | ☑ | 是否引入 N+1 查询、全表扫描、大对象序列化 | 导出走 selectUserList 带 @DataScope（`SysUserServiceImpl.java:76`），无 N+1；大数据量异步处理不阻塞主线程 |
| 16 | 日志级别 | ☑ | 关键操作日志级别是否合理 | 任务提交/完成/失败均用 log.info/error（`UserExportTaskLauncher.java:50,64`、`UserExportTask.java:56`），级别合理 |
| 17 | 定时任务 | ☐ | 是否影响现有定时任务的执行 | 不涉及定时任务 |
| 18 | 数据一致性 | ☐ | 跨库/跨表数据是否需要最终一致性保障 | 不涉及，只读导出无一致性问题 |
| 19 | 回滚方案 | ☑ | 每项变更是否有独立回滚手段 | 前端改动可单独回滚 handleExport 和 user.js 新增方法，不影响后端 |

## 7. 接口契约变更（如涉及 API）

| 接口 | 变更类型 | 旧契约 | 新契约 | 兼容性 |
|------|----------|--------|--------|--------|
| `POST /system/user/exportAsync` | 前端新增调用方 | 已存在但前端未调用 | 前端 handleExport 调用，传 userIds + query | 向后兼容 ✅（接口本身不变） |
| `GET /system/user/exportTask/{taskId}` | 前端新增调用方 | 已存在但前端未调用 | 前端轮询任务状态 | 向后兼容 ✅（接口本身不变） |
| `GET /common/download` | 前端新增调用方 | 已存在（通用下载） | 任务成功后下载文件 | 向后兼容 ✅（接口本身不变） |
| `POST /system/user/export` | 无变更 | 同步导出保留 | 保留作为后备 | 向后兼容 ✅ |

- **消费方影响**：仅前端用户列表页，无外部消费者
- **文档影响**：无后端接口文档变更，前端调用方新增

## 8. 设计原则约束

- **简单优先**：不添加用户未要求的功能，不做推测性设计。本次只接入已有异步导出，不新增后端接口、不加新字段、不改权限。
- **精准修改**：只改必须改的文件（前端 user.js 新增方法 + index.vue handleExport 改造），不"改进"相邻代码。
- **质量底线**：最小改动不等于最低质量，前端轮询需处理成功/失败/超时三种状态，达到项目同类功能质量标准。
- **语义约定**：任务状态枚举 PENDING/RUNNING/SUCCESS/FAILED 引用原定义（`UserExportTask.java:24-27`），权限标识 system:user:export 引用原定义（`sql/ry_20260417.sql:193`）。

### 行为准则检查

- 任务规模：中
- 适用规则：前 7 条规则
- 精准修改边界：仅 `ruoyi-ui/src/api/system/user.js`（新增两方法）+ `ruoyi-ui/src/views/system/user/index.vue`（改造 handleExport）
- 不做的事：不改后端、不改数据库、不改权限、不改其他前端文件
- 语义约定证据：任务状态枚举（`UserExportTask.java:24-27`）、权限标识（`SysUserController.java:78,91,110`）
- 测试策略依据：本次是前端 UI 层接入，属"纯 UI 展示层"范畴可说明不测理由；但 handleExport 涉及异步轮询逻辑，建议手动验收 + 集成验证

## 9. 数据迁移策略

- 存量数据如何转换：不涉及，无数据库变更。
- 是否需要历史快照：不涉及。
- 迁移脚本位置：不适用。

## 10. 向后兼容性评估

- API 变更是否破坏现有消费者：不破坏。同步导出接口 `/export` 保留不动，异步接口 `/exportAsync` 和任务查询接口 `/exportTask` 契约不变，只是前端新增调用。通用下载接口 `/common/download` 不变。
- 兼容方案（如有）：无需额外兼容方案，完全向后兼容。
