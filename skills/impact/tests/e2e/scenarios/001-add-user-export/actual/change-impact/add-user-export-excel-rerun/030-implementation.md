# 用户列表导出 Excel（选中用户 + 异步任务）实施文档

> 生成时间：2026-06-29 14:43:14  |  版本：1.0  |  生成者：impact skill + claude
>
> 导航：[010-requirements.md](010-requirements.md) → [020-design.md](020-design.md) → **030-implementation.md** → [060-preflight.md](060-preflight.md) → [090-execution-record.md](090-execution-record.md) | [_active-state.md](_active-state.md)

## 1. 实施顺序

1. 先在 `ruoyi-ui/src/api/system/user.js` 新增两个 API 封装方法（提交异步导出 + 查询任务状态），为页面调用提供基础。
2. 再改造 `ruoyi-ui/src/views/system/user/index.vue` 的 handleExport，调用新 API 传选中 userIds，轮询任务状态，成功后下载文件。

顺序原因：页面方法依赖 API 方法，API 方法必须先就位。

## 2. 前置检查清单

- [x] 分析依据中的待确认问题已处理，或明确接受风险（所有不确定项已代码推断消化）
- [x] 当前假设、歧义和成功标准已确认
- [x] 精准修改边界已确认，不包含无关重构/格式化（仅前端两文件）
- [x] status/enum/常量/错误码/权限/配置键等语义约定已找到原定义（任务状态枚举 `UserExportTask.java:24-27`、权限标识 `SysUserController.java:78`）
- [ ] 依赖服务状态确认（如涉及）— 不涉及外部依赖
- [ ] 数据库备份状态确认（如涉及 DB）— 不涉及 DB
- [ ] 锁策略/停机窗口确认（如涉及 DB/批量任务）— 不涉及
- [x] 回滚方案准备完毕（前端改动可单独回滚）
- [x] `_active-state.md` 已创建或将在本需求目录首次写入时创建
- [ ] 破坏性操作已单独确认（如涉及 DROP/DELETE/RENAME/接口删除）— 不涉及破坏性操作

## 2.1 改动完整性自检（提交确认前必做）

| 验收标准（来自 010） | 对应 Step | 覆盖状态 |
|---------------------|----------|---------|
| 勾选用户后点导出，提交异步任务并提示已提交 | Step 2（handleExport 调 exportUserAsync + $modal 提示） | ✅ |
| 任务完成后能下载 Excel，含所选用户全部字段 | Step 2（轮询到 SUCCESS 后 this.download 下载文件） | ✅ |
| 未勾选时按查询条件导出全部 | Step 2（this.ids 为空时传空数组，后端按 query 全量） | ✅ |
| 任务失败时看到失败原因 | Step 2（轮询到 FAILED 时 $modal.msgError 展示 errorMsg） | ✅ |
| 无权限者看不到按钮也调不了接口 | 已就绪（按钮 v-hasPermi + 接口 @PreAuthorize，无需改动） | ✅ 已就绪 |
| 导出进行中列表页可正常操作 | Step 2（异步提交后不阻塞，轮询用 setTimeout 不卡 UI） | ✅ |

## 2.2 判档决策表

> Phase 3.5 定级证据：full 模式。现状核查为"部分实现"——后端异步导出完整，前端未接入异步+选中。

| 用户原话关键词 | 现有实现覆盖范围 | 缺口 | 判档依据 |
|--------------|---------------|------|---------|
| "导出 Excel" | 同步 /export 已实现（`SysUserController.java:79-85`），异步 /exportAsync 已实现（`SysUserController.java:92-105`） `【已核实: SysUserController.java:79-105】` | 前端 handleExport 走同步未接异步 | full（前端接入异步+跨前后端） |
| "选中的用户" | 前端 handleSelectionChange 已收集 this.ids（`index.vue:359-363`），后端 exportAsync 已支持 userIds 参数（`SysUserController.java:94`） `【已核实: index.vue:359-363, SysUserController.java:94】` | 前端 handleExport 未传 this.ids | full（需改前端传参+轮询） |
| "包含所有字段" | SysUser @Excel 注解已标记全部导出字段（`SysUser.java:28-85`），password 不导出 `【已核实: SysUser.java:28-85】` | 无 | full（沿用已有字段覆盖，无需改） |
| "权限控制 system:user:export" | 权限已注册（`sql/ry_20260417.sql:193`），三接口已绑 @PreAuthorize（`SysUserController.java:78,91,110`），前端按钮已绑 v-hasPermi（`index.vue:41`） `【已核实: sql/ry_20260417.sql:193, SysUserController.java:78,91,110】` | 无 | full（权限链路已完整，无需改） |
| "异步任务处理" | UserExportTask 状态机（`UserExportTask.java:20-69`）、UserExportTaskLauncher @Async（`UserExportTaskLauncher.java:44`）、AsyncConfig 线程池（`AsyncConfig.java:18-32`）均已实现 `【已核实: UserExportTask.java:20-69, UserExportTaskLauncher.java:44, AsyncConfig.java:18-32】` | 前端未轮询任务状态 | full（前端需加轮询逻辑） |

触发 full 的证据：
1. 跨模块（前端 ruoyi-ui + 后端 ruoyi-admin/ruoyi-system）联动
2. 涉及权限校验（system:user:export）
3. 涉及异步任务（线程池 + 状态机）
4. 前端需新增轮询逻辑（非纯展示层）

未确认项：无（全部代码推断消化）。

## 3. 执行步骤

### Step 1: 新增前端异步导出 API 方法

- **维度**：代码/接口
- **文件**：`ruoyi-ui/src/api/system/user.js`
- **风格约束**（来自 profile 的 `style_axes`，运行时从项目文件现采）：
  - api_response API 方法用 `export function` + `request`，GET 用 params、POST 用 data（参考 `ruoyi-ui/src/api/system/user.js:5-11` listUser）
  - naming 方法名驼峰，注释用 `//` 单行中文说明（参考 `ruoyi-ui/src/api/system/user.js:4` `// 查询用户列表`）
- **操作**：
  ```javascript
  // 在 ruoyi-ui/src/api/system/user.js 末尾（deptTreeSelect 方法之后）新增：

  // 提交用户异步导出任务
  export function exportUserAsync(query) {
    return request({
      url: '/system/user/exportAsync',
      method: 'post',
      params: query
    })
  }

  // 查询用户导出任务状态
  export function getUserExportTask(taskId) {
    return request({
      url: '/system/user/exportTask/' + taskId,
      method: 'get'
    })
  }
  ```
- **影响范围**：仅新增两个导出方法，不影响 user.js 现有方法
- **回滚方式**：删除新增的两个方法
- **语义约定（status/enum/常量/错误码/权限名/配置键）**：不涉及新增语义约定；任务状态枚举 PENDING/RUNNING/SUCCESS/FAILED 引用原定义（`UserExportTask.java:24-27`）
- **验证方式**：静态确认（grep 验证方法存在 + 接口路径与后端一致）
- **确认类型**：写文件

### Step 2: 改造 handleExport 接入异步导出

- **维度**：代码/前端
- **文件**：`ruoyi-ui/src/views/system/user/index.vue`
- **风格约束**（来自 profile 的 `style_axes`，运行时从项目文件现采）：
  - layering 页面 methods 中定义操作方法，用 import 引入 API（参考 `index.vue:178` import { listUser, ... }）
  - naming 方法名驼峰，注释 `/** xxx */`（参考 `index.vue:451` `/** 导出按钮操作 */`）
  - api_response 用 this.$modal 做提示（参考 `index.vue:448` this.$modal.msgSuccess）
- **操作**：
  ```javascript
  // 1. 修改 ruoyi-ui/src/views/system/user/index.vue 第 178 行 import，新增 exportUserAsync, getUserExportTask：
  import { listUser, getUser, delUser, addUser, updateUser, resetUserPwd, changeUserStatus, deptTreeSelect, exportUserAsync, getUserExportTask } from "@/api/system/user"

  // 2. 替换 handleExport 方法（原 index.vue:452-456）：
  /** 导出按钮操作 */
  handleExport() {
    const userIds = this.ids
    const queryParams = { ...this.queryParams, userIds: userIds }
    this.$modal.confirm('是否确认导出选中的用户数据？未选中则按当前条件导出全部。').then(() => {
      return exportUserAsync(queryParams)
    }).then(res => {
      const taskId = res.taskId
      this.$modal.msgSuccess("导出任务已提交，正在后台处理...")
      this.pollExportTask(taskId)
    }).catch(() => {})
  },
  /** 轮询异步导出任务状态 */
  pollExportTask(taskId) {
    const maxRetry = 60
    let retry = 0
    const poll = () => {
      retry++
      if (retry > maxRetry) {
        this.$modal.msgError("导出任务超时，请稍后在任务列表查看")
        return
      }
      getUserExportTask(taskId).then(res => {
        if (res.status === 'SUCCESS') {
          const filePath = res.filePath || ''
          const fileName = filePath.substring(filePath.lastIndexOf('/') + 1)
          this.download('common/download', { fileName: fileName, delete: false }, fileName)
        } else if (res.status === 'FAILED') {
          this.$modal.msgError("导出失败：" + (res.errorMsg || '未知错误'))
        } else {
          setTimeout(poll, 2000)
        }
      }).catch(() => {
        this.$modal.msgError("查询导出任务状态失败")
      })
    }
    setTimeout(poll, 2000)
  },
  ```
- **影响范围**：仅 handleExport 方法改造 + 新增 pollExportTask 方法 + import 行增加两个方法，不影响 index.vue 其他逻辑
- **回滚方式**：将 handleExport 恢复为原始同步版本，删除 pollExportTask，移除 import 中的两个方法
- **语义约定（status/enum/常量/错误码/权限名/配置键）**：任务状态值 SUCCESS/FAILED 引用原定义（`UserExportTask.java:25-26` Status 枚举）；userIds 参数名引用后端 @RequestParam 定义（`SysUserController.java:94`）
- **验证方式**：静态确认（grep 验证方法调用 + 人工推演轮询逻辑）；集成验证需启动前后端（本次验证任务不执行）
- **确认类型**：写文件

## 3.2 API 方法验证（⚠️ 强制必做 — 缺此节 impact_validate.py V3 FAIL 阻止提交）

> 对照 §3 执行步骤中引用的所有**已有代码库方法**，验证其存在性和异常行为。
> **新增方法**（本次变更新定义的）不在此表，但在备注中标注"新增"。

| 方法名 | 来源文件 | grep 验证 | 异常行为 | 验证标注 |
|--------|---------|----------|---------|---------|
| `this.download(` | `ruoyi-ui/src/utils/request.js:127` | ✅ 存在 `【已核实: ruoyi-ui/src/utils/request.js:127】` | 不抛异常，失败时 catch 内 Message.error 提示 | 已确认 |
| `this.$modal.msgSuccess(` | 全局挂载（`ruoyi-ui/src/main.js` 挂载 $modal） | ✅ 存在 `【已核实: ruoyi-ui/src/views/system/user/index.vue:448】` 同文件已用 | 不抛异常，仅弹提示 | 已确认 |
| `this.$modal.msgError(` | 全局挂载 | ✅ 存在 `【已核实: ruoyi-ui/src/views/system/user/index.vue:448】` 同类 $modal 方法已用 | 不抛异常，仅弹提示 | 已确认 |
| `this.$modal.confirm(` | 全局挂载 | ✅ 存在 `【已核实: ruoyi-ui/src/views/system/user/index.vue:444】` handleDelete 已用 | 返回 Promise，用户取消时 reject（走 catch） | 已确认 |
| `exportUserAsync(` | — | 新增，本次定义（Step 1） | — | 新增 |
| `getUserExportTask(` | — | 新增，本次定义（Step 1） | — | 新增 |
| `pollExportTask(` | — | 新增，本次定义（Step 2） | — | 新增 |

> **填写说明**：
> - this.download：grep 验证 `ruoyi-ui/src/utils/request.js:127` 定义 `export function download`，`main.js:47` 挂载 `Vue.prototype.download = download`，页面用 `this.download` 调用
> - this.$modal：项目全局挂载，index.vue 同文件 handleDelete（:444, :448）已使用 msgSuccess/confirm，异常行为为 Promise reject 走 catch
> - 新增方法（exportUserAsync/getUserExportTask/pollExportTask）本次定义，不在已有方法验证范围

> ⚠️ §3 执行步骤写完后，已填写上方 §3.2 API 方法验证表。

## 4. 回滚方案

### 逐步骤回滚

- Step 2 回滚：将 `index.vue` 的 handleExport 恢复为原始同步版本（`this.download('system/user/export', {...this.queryParams}, ...)`），删除 pollExportTask 方法，从 import 移除 exportUserAsync 和 getUserExportTask。
- Step 1 回滚：删除 `user.js` 末尾新增的 exportUserAsync 和 getUserExportTask 两个方法。

### 组合回滚顺序

```
全部回滚时：
  1. 先回滚 Step 2（页面改造，依赖 Step 1 的 API 方法）
  2. 再回滚 Step 1（API 方法）
Step 2 单独失败时：回滚 Step 2，Step 1 保留（API 方法未被调用无副作用）
```

## 5. 验证步骤

### 正向用例（功能正常）
- [ ] 勾选 2 个用户后点导出 → 提示"任务已提交" → 轮询 → 下载到 Excel，内容为这 2 个用户
- [ ] 不勾选任何用户点导出 → 提示"任务已提交" → 下载到 Excel，内容为当前查询条件全部用户
- [ ] 导出进行中点击查询/翻页 → 正常响应不卡顿

### 错误用例（异常边界）
- [ ] 无 system:user:export 权限的用户访问 → 看不到导出按钮；直接调接口返回 403
- [ ] 导出空数据（查询条件无匹配） → 任务状态 FAILED，提示"导出数据为空"
- [ ] 轮询超过 60 次（约 2 分钟）仍未完成 → 提示"导出任务超时"
- [ ] 查询任务状态接口异常 → 提示"查询导出任务状态失败"

### 其他验证
- [ ] API 兼容性验证：同步 /export 接口仍可用，异步接口契约不变
- [ ] 数据一致性验证：导出数据受 @DataScope 约束，非超管只能导出可见范围用户

## 6. E2E / 验证脚本

脚本路径：`change-impact/add-user-export-excel-rerun/050-validation/`

- `001_export_async_api_check.sh`：curl 脚本，验证 exportAsync 提交 + exportTask 轮询 + common/download 下载三个接口的契约
- `002_export_async_select_users.sql`：SQL 验证脚本，验证选中用户导出数据正确性（对比导出行数与选中用户数）

脚本内容见 050-validation/ 目录下对应文件。

## 7. 实施时间线

| 步骤 | 预计耗时 | 里程碑 |
|------|---------|--------|
| Step 1 新增 API 方法 | 5 分钟 | user.js 新增两方法 |
| Step 2 改造 handleExport | 15 分钟 | 异步导出 + 轮询 + 下载打通 |
| 集成验证 | 20 分钟 | 前后端联调通过 |

## 8. 跨会话恢复状态

状态文件写入 `change-impact/add-user-export-excel-rerun/_active-state.md`，格式参照 `templates/_active-state.md`。它只记录当前 Phase、pending Step、文档确认状态、验证等级、未确认项和恢复检查结果，不构成任何写操作授权。

恢复时必须先读 `_active-state.md`、本实施文档、`060-preflight.md` 和 `090-execution-record.md`，再复核磁盘状态并重新要求当前对话中的 `确认 Step N`。

## 9. 环境备选路径

如果实际执行时**部分验证命令不可用**（如前端环境缺失）：

| 计划验证 | 环境缺失场景 | 备选方案 |
| --- | --- | --- |
| 前端联调（npm run dev + 手动操作） | 前端环境未就绪 | 静态确认：grep 验证 API 方法 + 人工推演轮询逻辑 |
| 后端接口契约验证 | 后端未启动 | 静态确认：读 SysUserController.java 确认接口签名与前端调用一致 |
| `mvn test` | Java 环境缺失 | 本次验证任务不执行 Phase 5，标注 V1 静态确认 |

**备选方案已在风险预判时识别并写入本文档**，避免"事后才发现环境受限"。
