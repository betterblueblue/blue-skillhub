# 030-implementation — add-user-export-excel

## 1. 实施步骤（按依赖排序）

### Step 1: 新增 IUserExportService 接口
- 文件：`ruoyi-system/src/main/java/com/ruoyi/system/service/IUserExportService.java`
- 操作：Write（new file）
- 验证：`javac -d /tmp/out ruoyi-system/src/main/java/com/ruoyi/system/service/IUserExportService.java` 退出码 0
- 回滚：rm 文件即可
- 用户确认：低风险（pure addition, no runtime impact），可自动

### Step 2: 新增 UserExportServiceImpl
- 文件：`ruoyi-system/src/main/java/com/ruoyi/system/service/impl/UserExportServiceImpl.java`
- 操作：Write（new file）
- 验证：同上 javac
- 回滚：rm 文件
- 用户确认：低风险

### Step 3: 新增 UserExportTask（含 @Async）
- 文件：`ruoyi-system/src/main/java/com/ruoyi/system/service/impl/UserExportTask.java`
- 操作：Write（new file）
- 验证：javac
- 回滚：rm 文件
- 用户确认：中风险（异步语义 + 通知副作用），本次**模拟用户已确认**

### Step 4: 新增 AsyncConfig
- 文件：`ruoyi-framework/src/main/java/com/ruoyi/framework/config/AsyncConfig.java`
- 操作：Write（new file）
- 验证：javac
- 回滚：rm 文件
- 用户确认：低风险（新增 bean）

### Step 5: 修改 SysUserController
- 文件：`ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java`
- 操作：Edit（新增 2 方法 + 注入 UserExportTask + import）
- 验证：javac + mvn compile
- 回滚：git checkout
- 用户确认：中风险（接口契约新增）— 模拟用户已确认

### Step 6: 新增单元测试 — UserExportServiceImplTest
- 文件：`ruoyi-system/src/test/java/com/ruoyi/system/service/impl/UserExportServiceImplTest.java`
- 操作：Write（new file）
- 验证：mvn -pl ruoyi-system -Dtest=UserExportServiceImplTest test PASS
- 回滚：rm 文件
- 用户确认：低风险

### Step 7: 新增单元测试 — UserExportTaskTest
- 文件：`ruoyi-system/src/test/java/com/ruoyi/system/service/impl/UserExportTaskTest.java`
- 操作：Write（new file）
- 验证：mvn test
- 回滚：rm 文件
- 用户确认：低风险

### Step 8: mvn compile 全模块
- 命令：`cd workdir && mvn -q -DskipTests -pl '!ruoyi-ui' compile`
- 验证：退出码 0
- 失败处理：定位到具体类，修语法

## 2. 验证方式

| 验证项 | 命令 | 期望 |
|--------|------|------|
| 编译 | `mvn -q -DskipTests compile` | exit 0 |
| 单元测试 | `mvn -q -pl ruoyi-system -Dtest='UserExport*Test' test` | exit 0 |
| 静态检查 | `grep -rn "TODO\|<your\|<file path>" change-impact/ workdir/` | 无匹配 |
| 凭证脱敏 | `grep -rn "admin123\|password.*=.*['\"]" change-impact/` | 无匹配 |
| 权限绑定 | `grep -n "system:user:export" SysUserController.java` | 含 exportAsync 行 |

## 3. 环境降级路径

- 缺 `@EnableAsync` 注解 → 补到 AsyncConfig 类级注解
- 项目主类已有 `@EnableAsync` 扫描 → 移除 AsyncConfig 类级 `@EnableAsync`
- ExcelUtil 缺 `exportExcel(List, String, String)` 重载 → 改用 `exportExcel(HttpServletResponse, List, String)` 写临时 HttpServletResponse 包装
- SysNoticeService API 不存在 → 改用 ISysNoticeService.insertNotice

## 4. 风险标记

- **Step 3/5/6/7** — 中风险（涉及异步语义、接口契约、测试覆盖），但都是"新增/扩展"，不属于铁律 #2 高危拦截清单（DROP/DELETE/GRANT/ALTER/不可逆）
- 无 DROP / 无 ALTER / 无 GRANT / 无 schema 变更 / 无删除接口
- 权限 system:user:export **已存在**，不需新增 menu 记录 → 不写 DDL

## 5. 凭证脱敏承诺

- 所有文档中 password / secret / token 出现处为 `***` 或 `$PASSWORD` 变量引用
- 任何 shell 脚本中 token 使用 `${TOKEN:-default-token-for-test}` 形式
- 任何 SQL 脚本无凭证
