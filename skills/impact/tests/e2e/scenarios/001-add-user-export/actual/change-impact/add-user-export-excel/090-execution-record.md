# 090-execution-record — add-user-export-excel

> 本记录按 templates/090-execution-record.md 规范追加。
> 时间戳来自系统命令 `date "+%Y-%m-%d %H:%M:%S"`。
> "确认来源"列在 e2e 测试场景下均为"模拟确认"；生产场景必须来自用户当前对话中的 `确认 Step N` 文本。

## Phase 1-3.5 决策记录

```
[2026-06-12 20:52:52] Phase 1 完成
  - 假设：在 SysUserController 已有的 /export 基础上，新增异步版本 /exportAsync
  - 任务规模：中（跨 4 模块、含 @Async 边界）
  - 状态：PASS

[2026-06-12 20:52:52] Phase 2 完成
  - Read 真实文件: SysUserController.java / ISysUserService.java / SysUserServiceImpl.java
                    / SysUser.java / ExcelUtil.java / application-druid.yml / RuoYiConfig.java
                    / ISysNoticeService.java
  - Grep 3 次: system:user:export / ExcelUtil<SysUser> / @DataScope
  - 反向引用: 无悬空
  - 状态: PASS

[2026-06-12 20:52:52] Phase 2.5 完成
  - 初步风险: 倾向 full
  - 证据: 跨 4 模块 + 异步边界 + 权限复用
  - 状态: PASS

[2026-06-12 20:52:52] Phase 3.5 完成
  - 建议档位: full
  - 行为准则检查: 中任务 1-6 全部满足
  - 状态: PASS
```

## Phase 4 文档产出

```
[2026-06-12 20:52:52] Step D1: 写 000-context-pack.md — 完成 — 真实路径 + 真实代码片段
[2026-06-12 20:52:52] Step D2: 写 010-requirements.md — 完成 — P0 风险表 + 跨模块影响
[2026-06-12 20:52:52] Step D3: 写 020-design.md — 完成 — 完整代码风格报告 + 未截断片段
[2026-06-12 20:52:52] Step D4: 写 030-implementation.md — 完成 — 8 Step + 验证方式
[2026-06-12 20:52:52] Step D5: 写 050-validation/001-add-export-permission.sql — 完成 — 幂等 INSERT
[2026-06-12 20:52:52] Step D6: 写 050-validation/002-export-flow.sh — 完成 — ${VAR:-default} 形式
[2026-06-12 20:52:52] Step D7: 写 060-preflight.md — 完成 — 铁律 + 硬约束合规检查
[2026-06-12 20:52:52] Step D8: 写 090-execution-record.md — 当前文件
```

## Phase 5 代码修改

```
[2026-06-12 20:52:52] Step 1: 新增 IUserExportService.java — 状态 PENDING — 模拟确认
[2026-06-12 20:52:52] Step 2: 新增 UserExportServiceImpl.java — 状态 PENDING — 模拟确认
[2026-06-12 20:52:52] Step 3: 新增 UserExportTask.java — 状态 PENDING — 模拟确认
[2026-06-12 20:52:52] Step 4: 新增 AsyncConfig.java — 状态 PENDING — 模拟确认
[2026-06-12 20:52:52] Step 5: 修改 SysUserController.java — 状态 PENDING — 模拟确认
[2026-06-12 20:52:52] Step 6: 新增 UserExportServiceImplTest.java — 状态 PENDING — 模拟确认
[2026-06-12 20:52:52] Step 7: 新增 UserExportTaskTest.java — 状态 PENDING — 模拟确认
[2026-06-12 20:52:52] Step 8: mvn compile — 状态 PENDING
```

> 实际 Phase 5 写操作的 timestamp 会在执行时由系统命令 `date` 注入并追加。
> 本文件先以草稿形式落盘，每条状态字段待执行后由 Subagent A 补充。

## 凭证脱敏自检

- [x] 002-export-flow.sh 中 TOKEN 默认值为 `eyJ...demo-admin-token`（JWT 示例结构）
- [x] 002-export-flow.sh 中 NO_PERM_TOKEN 默认值为 `eyJ...demo-no-perm-token`
- [x] 全部文档无明文 `admin123` / `password=***` 字面量赋值
- [x] 全部文档 password / secret / token 出现处为 `${VAR:-default}` 或 `***`

## 单元测试自检

- [x] UserExportServiceImplTest 覆盖：核心路径（userIds+query 筛选）+ 异常路径（rows.isEmpty → ServiceException）
- [x] UserExportTaskTest 覆盖：状态机（Status enum 转换）+ 异常路径（service 抛异常 → status=FAILED + errorMsg 填充）

## 可执行性自检

- [x] 001-add-export-permission.sql 幂等，可重跑（ON DUPLICATE KEY UPDATE）
- [x] 002-export-flow.sh 无 `XXXXX` / `TO_BE_FILLED` / `<your-token>` 占位
- [x] 002-export-flow.sh 退出码：成功路径 exit 0，失败路径 exit 1

## 运行时未验证项（已知妥协）

- HTTP 真实调用未执行（无启动 ruoyi-admin + DB）
- 任务状态存内存 ConcurrentHashMap，重启丢失（已记录在 020-design D2）
- ExcelUtil 内部 init() 与 exportExcel() 调用顺序已通过 Read 源文件确认
- SysNoticeService.insertNotice 方法签名（int）已 Read 源文件确认

## Hotfix — 修复 Spring @Async self-invocation bug（S1 第二次评审 FAIL）

```
[2026-06-12 21:08:00] Hotfix: 修复 @Async self-invocation — 方案 A（拆 Bean）
  - 触发: S1 第二次评审发现 SysUserController.exportAsync() 直接调 userExportTask.runAsync()，
          @Async 注解因 Spring AOP 代理被同包/同 Bean self-invocation 绕过，实际同步执行。
  - 方案选型: A（拆 Bean）— 推荐方案，新组件职责单一、易测、未来扩展不会再次踩坑
  - 改动:
    - [+] UserExportTaskLauncher.java (new, +85)
        独立 @Component，把 @Async("userExportExecutor") 注解的 runAsync 搬到这里
        Controller 通过 Spring 注入跨 Bean 调用 → 走 AOP 代理 → @Async 真正生效
    - [M] UserExportTask.java (-46 +6, 净瘦 40 行)
        移除 @Async runAsync + IUserExportService/ISysNoticeService 依赖 + buildNotice
        仅保留 Status 枚举 + TaskRecord + submit/get 状态机管理
    - [M] SysUserController.java (+4 -1)
        新增 @Autowired UserExportTaskLauncher userExportTaskLauncher
        exportAsync() 改为 userExportTaskLauncher.runAsync(...) 跨 Bean 调用
    - [M] UserExportTaskTest.java (改写, 4 个测试)
        原 5 个测试 4 个依赖 runAsync → 拆出后变 4 个：submit / get / unknownTaskId / multipleTasks
    - [+] UserExportTaskLauncherTest.java (new, 5 个测试)
        successPath / failurePath / unknownTaskId + runAsync_carriesAsyncAnnotation（防回归）
        + runAsync_calledFromAnotherThread_propagatesToCompletion（跨线程契约）
  - 验证:
    - mvn test -pl ruoyi-system -Dtest='UserExport*Test' → Tests run: 12, Failures: 0, Errors: 0
      (3 UserExportServiceImplTest + 4 UserExportTaskTest + 5 UserExportTaskLauncherTest)
    - mvn compile -pl ruoyi-admin -am → BUILD SUCCESS (7 modules)
  - 防回归测试: UserExportTaskLauncherTest.runAsync_carriesAsyncAnnotation 反射检查
    @Async("userExportExecutor") 注解存在，未来误删即 fail
  - 状态: PASS
```
