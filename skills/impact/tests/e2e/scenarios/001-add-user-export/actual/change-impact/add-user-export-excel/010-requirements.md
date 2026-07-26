# 010-requirements — add-user-export-excel

## 1. 业务目标

为"用户管理"列表页提供**异步导出**能力：
- 前端勾选若干行 → 提交 userIds + 查询条件
- 后端立即返回 `taskId`（200ms 内）
- 后端线程池执行 Excel 生成 → 写入临时文件 → 通过站内通知告知当前用户下载入口
- 同步 `/export` 端点保留，作为少量数据快速导出路径

## 2. 范围

### In-Scope
- 新增 `POST /system/user/exportAsync`（含 `system:user:export` 权限校验）
- 新增 `GET /system/user/exportTask/{taskId}`（任务状态查询）
- 新增 `IUserExportService` + `UserExportServiceImpl`（业务封装）
- 新增 `UserExportTask`（@Component 持有 @Async 方法）
- 新增 ThreadPoolTaskExecutor bean 配置
- 新增 SysUser 字段导出配置（仅限已 @Excel 标注字段，不补 avatar/password）
- 单元测试：`UserExportServiceImplTest` + `UserExportTaskTest`

### Out-of-Scope
- Quartz 持久化任务（用户未要求可恢复）
- 文件存储到 OSS/MinIO（项目未集成）
- Excel 样式/合并单元格定制（与原 /export 行为一致）
- 大文件分片下载（项目无相关基础设施）
- 多语言/i18n 通知文案变更
- 前端 Vue 组件改动（仅在文档中给出调用样例，不改 workdir Vue 文件）

## 3. P0 风险与决策

| ID | 风险 | 决策 |
|----|------|------|
| R1 | 异步任务长时间占用线程 | 独立 ThreadPoolTaskExecutor（core=2, max=4, queue=50, CallerRuns 拒绝） |
| R2 | 任务状态查询 vs 通知链路 | 任务状态存内存 ConcurrentHashMap<taskId, TaskRecord>（重启丢失，符合"短期异步"语义） |
| R3 | 权限校验必须前置 | 复用 `@PreAuthorize("@ss.hasPermi('system:user:export')")`，无权限 403 |
| R4 | 数据权限 | Service 内部复用 `ISysUserService.selectUserList` 走 `@DataScope` |
| R5 | 失败异常吞掉 | 异常路径必须有：log.error + SysNotice(失败) + TaskRecord.status=FAILED |
| R6 | 凭证脱敏 | 文档中所有 password/secret 占位为 `***`（铁律 #7 强化，硬约束 A） |

## 4. 跨模块影响

| 模块 | 变更类型 | 详情 |
|------|---------|------|
| ruoyi-admin | 修改 | SysUserController.java +2 方法（exportAsync, getExportTask） |
| ruoyi-system | 新增 | service/export/IUserExportService.java + Impl + Task |
| ruoyi-framework | 修改 | 增加 AsyncConfig 注册 ThreadPoolTaskExecutor |
| ruoyi-system | 新增测试 | src/test/java/.../UserExportServiceImplTest.java + UserExportTaskTest.java |
| sql | 不变更 | 权限 system:user:export 已存在（menu_id=1004） |

## 5. 升降档规则

- 触发 full 的原因：跨 4 模块 + 异步边界 + 权限复用 + 必配测试
- 不允许降档为 light 的原因：异步边界（铁律硬约束 B）必须有 JUnit 覆盖
- 若用户后续要求"持久化任务状态"或"OSS 存储"，仍属 full，需补新文档

## 6. 成功标准

1. `mvn compile` 在 workdir 全模块 PASS
2. `GET /system/user/exportAsync` 在无权限 token 下返回 403
3. 任务成功执行后 `GET /system/user/exportTask/{taskId}` 返回 status=SUCCESS + filePath
4. 任务失败时 status=FAILED + errorMsg 包含 ServiceException 原文
5. JUnit 5 + Mockito 覆盖：成功路径 1 + 异常路径 1（ServiceException + RuntimeException 各一）
6. 文档与代码中无明文 password / secret 字面量
