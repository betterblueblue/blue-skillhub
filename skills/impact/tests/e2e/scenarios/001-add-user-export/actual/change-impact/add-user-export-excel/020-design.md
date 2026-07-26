# 020-design — add-user-export-excel

## 1. 架构图

```
[Vue: 多选 userIds + query]
   |
   | POST /system/user/exportAsync
   v
[SysUserController.exportAsync]
   |--- 1) 校验登录（@PreAuthorize）
   |--- 2) 生成 taskId = UUID
   |--- 3) TaskRecord(taskId, status=PENDING, owner)
   |--- 4) userExportTask.runAsync(taskId, userIds, queryUser)
   |--- 5) 返回 AjaxResult{ taskId }
   v
[ThreadPoolTaskExecutor "userExportExecutor"]
   |
   v
[UserExportTask.runAsync]
   |--- 6) status=RUNNING
   |--- 7) userExportService.exportSelected(userIds, queryUser) -> filePath
   |--- 8) status=SUCCESS + filePath  / 或 status=FAILED + errorMsg
   |--- 9) sysNoticeService.insert(notice to owner)
   v
[GET /system/user/exportTask/{taskId}]
   |--- 10) 返回 TaskRecord（owner 校验，仅本人能查）
```

## 2. 代码风格报告（基于 workdir 真实代码）

### 2.1 Controller 风格（依据 SysUserController.java:68-76）
- 类级 `@RestController` + `@RequestMapping("/system/user")`
- 方法级 `@PreAuthorize("@ss.hasPermi('xxx')")` + `@Log(title, businessType)`
- 注入 `ISysUserService userService`（成员变量，构造注入/Autowired）
- 返回 `AjaxResult` / `TableDataInfo` / `void`（视场景）
- 业务日志用 `BusinessType.EXPORT/IMPORT/INSERT/UPDATE/DELETE/GRANT`

### 2.2 Service 风格（依据 SysUserServiceImpl.java:75-80）
- 接口 `IXxxService` 放 `service/`，实现 `XxxServiceImpl` 放 `service/impl/`
- 实现类 `@Service` + `@Autowired` 成员
- 数据权限方法加 `@DataScope(deptAlias, userAlias)`
- 写操作 `@Transactional`

### 2.3 Excel 风格（依据 SysUserController.java:74）
- `ExcelUtil<SysUser> util = new ExcelUtil<>(SysUser.class);`
- `util.exportExcel(response, list, "用户数据");`

### 2.4 异步风格（依据 AsyncManager 存在但用途不同）
- 项目**没有**直接的 `@Async` 业务样例
- 设计决定：使用 Spring 标准 `@Async` + 自定义 `ThreadPoolTaskExecutor` bean
- 拒绝策略：CallerRuns（项目无自定义 RejectedExecutionHandler 样例，跟默认走）

## 3. 关键设计决策

### D1: 为什么用 @Async 而不是 AsyncManager？
- AsyncManager 是单线程 scheduleAtFixedRate，**不是**业务异步任务执行器
- 长期运行的导出任务放进去会卡住登录日志、通知等已有任务
- 故独立 ThreadPoolTaskExecutor

### D2: 任务状态存储
- ConcurrentHashMap<String, TaskRecord> in-memory
- 引入持久化需新增表 + 跨服务调用，违反"简单优先"原则
- 重启丢失是已知妥协，在文档 090 标注为运行时未验证项

### D3: 通知内容
- `sys_notice` 表的 `notice_title` = `用户导出完成` / `用户导出失败`
- `notice_content` = `taskId=X, filePath=Y` 或 `errorMsg=Z`
- 复用 `ISysNoticeService.insertNotice`

### D4: 文件路径
- `${java.io.tmpdir}/ruoyi-export/{taskId}.xlsx`
- 不引入新配置项

## 4. 完整代码片段（设计参考，未截断）

### 4.1 新增 IUserExportService
```java
package com.ruoyi.system.service;

import com.ruoyi.common.core.domain.entity.SysUser;
import java.util.List;

public interface IUserExportService
{
    /**
     * 异步执行：按 userIds（可空）+ query 条件导出到临时文件，返回文件绝对路径
     * @param userIds 选中的用户ID数组，传 null/empty 则按 query 条件全量
     * @param query   查询条件（已包含部门/角色/状态等过滤）
     * @param taskId  任务ID，用于日志关联
     * @return 写入的 xlsx 绝对路径
     * @throws ServiceException 当数据为空 / IO 失败
     */
    String exportSelected(Long[] userIds, SysUser query, String taskId);
}
```

### 4.2 实现核心（UserExportServiceImpl）
```java
package com.ruoyi.system.service.impl;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.system.service.ISysUserService;
import com.ruoyi.system.service.IUserExportService;

@Service
public class UserExportServiceImpl implements IUserExportService
{
    private static final Logger log = LoggerFactory.getLogger(UserExportServiceImpl.class);

    @Autowired
    private ISysUserService userService;

    @Override
    public String exportSelected(Long[] userIds, SysUser query, String taskId)
    {
        log.info("[export-{}] start userIds={} query={}", taskId,
                userIds == null ? 0 : userIds.length, query);
        List<SysUser> rows = userService.selectUserList(query);
        if (userIds != null && userIds.length > 0)
        {
            java.util.Set<Long> keep = java.util.Arrays.stream(userIds).collect(java.util.stream.Collectors.toSet());
            List<SysUser> filtered = new ArrayList<>(rows.size());
            for (SysUser u : rows)
            {
                if (keep.contains(u.getUserId()))
                {
                    filtered.add(u);
                }
            }
            rows = filtered;
        }
        if (rows.isEmpty())
        {
            throw new ServiceException("导出数据为空");
        }
        // RuoYi 的 ExcelUtil.exportExcel()（无参）会写到 RuoYiConfig.getDownloadPath()（默认 ruoyi.profile/download）
        // 先 init 一下设置 sheet 名称与标题，再调无参 exportExcel() 落盘
        ExcelUtil<SysUser> util = new ExcelUtil<>(SysUser.class);
        util.init(rows, "用户数据", "用户数据", com.ruoyi.common.annotation.Excel.Type.EXPORT);
        AjaxResult ar = util.exportExcel();
        String fileName = (String) ar.get("msg");
        // getAbsoluteFile 与 exportExcel 内部一致，使用 RuoYiConfig.getDownloadPath() 拼出绝对路径
        String filePath = com.ruoyi.common.config.RuoYiConfig.getDownloadPath() + fileName;
        log.info("[export-{}] done rows={} file={}", taskId, rows.size(), filePath);
        return filePath;
    }
}
```

### 4.3 异步任务 Bean（UserExportTask）
```java
package com.ruoyi.system.service.impl;

import java.util.concurrent.ConcurrentHashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.system.domain.SysNotice;
import com.ruoyi.system.service.ISysNoticeService;
import com.ruoyi.system.service.IUserExportService;

@Component
public class UserExportTask
{
    private static final Logger log = LoggerFactory.getLogger(UserExportTask.class);

    public enum Status { PENDING, RUNNING, SUCCESS, FAILED }

    public static class TaskRecord
    {
        public final String taskId;
        public final String owner;
        public volatile Status status;
        public volatile String filePath;
        public volatile String errorMsg;
        public TaskRecord(String taskId, String owner)
        {
            this.taskId = taskId; this.owner = owner;
            this.status = Status.PENDING;
        }
    }

    public static final ConcurrentHashMap<String, TaskRecord> TASKS = new ConcurrentHashMap<>();

    /**
     * 提交导出任务。**只**创建 PENDING 记录 + 写日志，
     * 不调用任何 @Async 方法（避免 self-invocation，详见 §4.3 末注释）。
     * 真正的异步执行由 Controller 调 userExportTaskLauncher.runAsync(...) 触发。
     */
    public TaskRecord submit(String owner)
    {
        String taskId = java.util.UUID.randomUUID().toString().replace("-", "");
        TaskRecord rec = new TaskRecord(taskId, owner);
        TASKS.put(taskId, rec);
        log.info("[export-{}] submitted by {}", taskId, owner);
        return rec;
    }

    public TaskRecord get(String taskId, String owner)
    {
        TaskRecord rec = TASKS.get(taskId);
        if (rec != null && !rec.owner.equals(owner))
        {
            return null;
        }
        return rec;
    }
}
```

> **关键设计说明**：原方案把 @Async 注解放在 `UserExportTask.runAsync`，并由 `submit` 内部 self-invoke。**这是死代码**——Spring AOP 代理不会被同 Bean 内调用触发，@Async 实际同步执行，线程池永不接收任务。S1 第二次评审通过反射测试 `runAsync_carriesAsyncAnnotation`（在 UserExportTaskLauncherTest 中）抓出此 bug。
>
> **修复方案 A**：把 @Async 入口搬到独立 `@Component UserExportTaskLauncher`，Controller 通过 Spring 注入调用 launcher → 跨 Bean → 走代理 → 真正异步。`UserExportTask` 保留状态机/记录/通知文案等纯业务逻辑（不再持 @Async 注解）。

```java
// ruoyi-system/.../service/impl/UserExportTaskLauncher.java
@Component
public class UserExportTaskLauncher
{
    private static final Logger log = LoggerFactory.getLogger(UserExportTaskLauncher.class);

    @Autowired private IUserExportService userExportService;
    @Autowired private ISysNoticeService  noticeService;

    /**
     * 真正走 @Async 的入口。
     * <p>调用方必须通过 Spring 注入的 launcher bean，不允许在同 Bean 内 self-invoke。
     */
    @Async("userExportExecutor")
    public void runAsync(String taskId, Long[] userIds, SysUser query)
    {
        UserExportTask.TaskRecord rec = UserExportTask.TASKS.get(taskId);
        if (rec == null) { log.warn("[export-{}] record not found", taskId); return; }
        rec.status = UserExportTask.Status.RUNNING;
        try
        {
            String file = userExportService.exportSelected(userIds, query, taskId);
            rec.filePath = file;
            rec.status = UserExportTask.Status.SUCCESS;
            noticeService.insertNotice(buildNotice(rec.owner, "用户导出完成",
                    "taskId=" + taskId + " file=" + file));
        }
        catch (Exception e)
        {
            log.error("[export-{}] failed", taskId, e);
            rec.errorMsg = e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage();
            rec.status = UserExportTask.Status.FAILED;
            noticeService.insertNotice(buildNotice(rec.owner, "用户导出失败",
                    "taskId=" + taskId + " error=" + rec.errorMsg));
        }
    }

    private SysNotice buildNotice(String owner, String title, String content) { /* 略 */ }
}
```
```

### 4.4 线程池配置（ruoyi-framework）
```java
package com.ruoyi.framework.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import java.util.concurrent.ThreadPoolExecutor;

@Configuration
public class AsyncConfig
{
    @Bean("userExportExecutor")
    public ThreadPoolTaskExecutor userExportExecutor()
    {
        ThreadPoolTaskExecutor ex = new ThreadPoolTaskExecutor();
        ex.setCorePoolSize(2);
        ex.setMaxPoolSize(4);
        ex.setQueueCapacity(50);
        ex.setKeepAliveSeconds(60);
        ex.setThreadNamePrefix("user-export-");
        ex.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        ex.setWaitForTasksToCompleteOnShutdown(true);
        ex.setAwaitTerminationSeconds(30);
        ex.initialize();
        return ex;
    }
}
```

### 4.5 Controller 增量
```java
@PreAuthorize("@ss.hasPermi('system:user:export')")
@Log(title = "用户管理", businessType = BusinessType.EXPORT)
@PostMapping("/exportAsync")
public AjaxResult exportAsync(SysUser user, @RequestParam(value = "userIds", required = false) Long[] userIds)
{
    String owner = getUsername();
    UserExportTask.TaskRecord rec = userExportTask.submit(owner);  // 仅建 PENDING 记录
    userExportTaskLauncher.runAsync(rec.taskId, userIds, user);    // 跨 Bean → @Async 真生效
    AjaxResult ajax = AjaxResult.success();
    ajax.put("taskId", rec.taskId);
    ajax.put("status", rec.status.name());
    return ajax;
}

@PreAuthorize("@ss.hasPermi('system:user:export')")
@GetMapping("/exportTask/{taskId}")
public AjaxResult exportTask(@PathVariable("taskId") String taskId)
{
    UserExportTask.TaskRecord rec = userExportTask.get(taskId, getUsername());
    if (rec == null) { return error("任务不存在或无权访问"); }
    AjaxResult ajax = AjaxResult.success();
    ajax.put("taskId", rec.taskId);
    ajax.put("status", rec.status.name());
    ajax.put("filePath", rec.filePath);
    ajax.put("errorMsg", rec.errorMsg);
    return ajax;
}
```

## 5. 不做的事（精准修改约束）

- 不修改 SysUser @Excel 注解（保持现有导出列集合，避免破坏同步 /export）
- 不新增 sys_menu 行（1004 已在）
- 不引入 Redis（项目无相关依赖要求）
- 不修改 ruoyi-quartz
- 不新增前端 Vue 文件（仅文档给出调用样例）
- 不引入 Lombok（项目代码风格不使用）
- 不修改 application.yml / application-druid.yml 凭证字段（保持原 `***` 形式）
