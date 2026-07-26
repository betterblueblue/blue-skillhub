# 060-preflight — 执行前检查

## 1. 仓库状态
- workdir: `E:\agent\blue-skillhub\skills\impact\tests\e2e\workdirs\001-add-user-export`
- 当前分支: `master`
- 与 origin/master 一致（fixture 拷贝，无外部状态）

## 2. 基线验证
- [x] `mvn -q -DskipTests -pl '!ruoyi-ui' compile` 退出码 0（在改 workdir 之前）
- [x] 项目结构完整（8 模块）
- [x] 权限 system:user:export 在 sql/ry_20260417.sql:193 已存在

## 3. Step 确认（按 030-implementation.md）
| Step | 描述 | 风险 | 用户确认 |
|------|------|------|----------|
| 1 | 新增 IUserExportService.java | 低 | 模拟确认（pure addition） |
| 2 | 新增 UserExportServiceImpl.java | 低 | 模拟确认 |
| 3 | 新增 UserExportTask.java（@Async） | 中 | 模拟确认（异步语义+通知） |
| 4 | 新增 AsyncConfig.java | 低 | 模拟确认 |
| 5 | 修改 SysUserController.java（+2 端点） | 中 | 模拟确认（接口契约） |
| 6 | 新增 UserExportServiceImplTest.java | 低 | 模拟确认 |
| 7 | 新增 UserExportTaskTest.java | 低 | 模拟确认 |
| 8 | mvn compile 全模块 | — | 验证动作 |

## 4. 铁律合规
- 铁律 #1（最高确认法）：本 e2e 测试场景下，使用"模拟用户确认"标注；非测试场景必须真实确认。
- 铁律 #2（高风险拦截清单）：本变更无 DROP / ALTER / GRANT / 删接口 — 不命中拦截
- 铁律 #3（DB 只读纪律）：SQL 脚本不直接执行，仅作为 DDL 交付物提交评审
- 铁律 #4（写入目标边界）：所有文件落在 workdir 内部；change-impact 文档在 actual/ 子目录
- 铁律 #7（凭证脱敏）：详见每份文档，所有 password/secret/token 字面量替换为 `***` 或 `${VAR:-default}`
- 铁律 #5（破坏性请求保护）：不适用 — 本次是新增/扩展
- 铁律 #6（阻塞恢复）：不适用 — 无阻塞

## 5. 硬约束合规（来自加固 prompt 1.5）
- **A. 凭证脱敏**：所有文档中 password/secret 出现处为 `***` 或 `${VAR:-default}`；执行报告同此规则
- **B. 单元测试**：UserExportServiceImplTest + UserExportTaskTest（状态机 + async 边界）；覆盖核心路径 + 1 异常路径
- **C. 可执行性**：002-export-flow.sh 使用 `${VAR:-default}` 形式，无 `XXXXX` / `TO_BE_FILLED` / `<your-token>` 占位

## 6. 回滚方式
- workdir 修改通过 `git checkout -- <file>` 回滚
- 新文件通过 `rm` 即可
- change-impact 文档在 actual/，不影响 workdir 主仓

## 7. 执行记录路径
- 实际记录追加到 090-execution-record.md
- 每条记录格式：`[YYYY-MM-DD HH:MM:SS] Step N: <name> - <status> - <user-confirm> - <verify>`

## 8. 运行时未验证项（已记录在 090）
- HTTP 真实调用未执行（需要启动 ruoyi-admin + DB）
- ExcelUtil.exportExcel(List, String, String) 重载是否在当前 pom 版本存在（需在 mvn compile 后确认）
- SysNoticeService.insertNotice 真实方法签名（基于 RuoYi 标准 API 推断，需实际验证）
