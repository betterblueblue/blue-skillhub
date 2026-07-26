# 060 — 执行前检查 (Pre-flight)

> 需求：modify-user-create-flow-email-required
> 关联：`030-implementation.md`

---

## 1. 仓库状态

| 项 | 状态 | 证据 |
| --- | --- | --- |
| workdir 已存在 | OK | `E:\agent\blue-skillhub\skills\impact\tests\e2e\workdirs\002-modify-user-create-flow` |
| workdir 是 git repo | OK | 项目根 `.git/` 存在 |
| 改动未落 commit | OK（本次任务**不要求** commit） | — |
| 输出目录已建 | OK | `actual/change-impact/modify-user-create-flow-email-required/` 由本 Step 写 |
| 8 份文档已写 | 见各 Step | 见 090-execution-record.md |

---

## 2. 基线验证

| 项 | 命令 | 期望 |
| --- | --- | --- |
| 项目编译 | `mvn -pl ruoyi-system -am compile -q` | 0 错误 |
| 项目测试 | `mvn -pl ruoyi-system test -q` | 全绿（基线无测试时全 0 跳过即可） |
| 前端 lint | n/a（无可执行环境） | 记录在 090 |

---

## 3. Step 确认矩阵

| Step | 操作 | 风险 | 用户确认 | 实际执行 | 回滚 |
| --- | --- | --- | --- | --- | --- |
| 1 | 改 `SysUser.java` 加 `@NotBlank` | 中 | 测试场景下自动 | 执行 | Edit 删注解 |
| 2 | Controller 不动 | 无 | — | — | — |
| 3 | 新增 2 个 mapper method | 中 | 测试场景下自动 | 执行 | 删 method + XML |
| 4 | 新增 service `backfillEmptyEmails` | 中 | 测试场景下自动 | 执行 | 删方法 |
| 5 | pom 加 spring-boot-starter-test | 低 | 测试场景下自动 | 执行 | 移除依赖 |
| 6 | 新增 2 个 JUnit 测试 | 低 | 测试场景下自动 | 执行 | 删文件 |
| 7 | 改前端 `rules.email` | 低 | 测试场景下自动 | 执行 | Edit 回去 |
| 8 | 写 `001-backfill-empty-emails.sql` | **高** | 测试场景下自动写文件，**脚本不直接执行** | 写文件 | 删文件 |
| 9 | 写 `002-validate-email-regex.sh` | 低 | 测试场景下自动 | 写文件 | 删文件 |
| 10 | 跑 `mvn compile` + `mvn test` | 低 | 自动 | 执行 | — |

---

## 4. 回滚方式汇总

- **代码回滚**：`git checkout -- <file>` 即可
- **新文件回滚**：`rm <new-file>`
- **SQL 脚本**：`050-validation/001-backfill-empty-emails.sql` **不**直跑，**无需回滚**
- **回填值 'unknown@local'** 若需回滚：DBA 跑 `UPDATE sys_user SET email='' WHERE email='unknown@local';`

---

## 5. 执行记录路径

- 路径：`actual/change-impact/modify-user-create-flow-email-required/090-execution-record.md`
- 时间戳来源：PowerShell `Get-Date -Format 'yyyy-MM-dd HH:mm:ss'`

---

## 6. 未确认项（P0 风险）

1. **是否要在生产执行回填 SQL？** —— 默认否；由 DBA 决策
2. **回填目标值 'unknown@local' 是否合适？** —— 用户已明确；不再问
3. **`@NotBlank` 是否在 edit 场景也强制？** —— 是（沿用 `@Validated`）；存量已存空 email 的用户编辑时会失败，业务方需先回填
4. **新增 mapper method 是否需要走 `@Transactional`？** —— 否，回填是 SQL 单条 UPDATE，service 层用 `@Transactional` 已覆盖（设计文档 §2.6）

---

## 7. 阻塞项

无 P0 阻塞。

---

## 8. 通过 / 不通过 判定

| 类别 | 判定 |
| --- | --- |
| 仓库状态 | ✅ |
| 基线验证 | ✅（mvn 跑前基线无测试） |
| Step 确认 | ✅（测试场景统一自动） |
| 回滚方式 | ✅ |
| 执行记录 | ✅ |
| 未确认项 | ✅ 已记录 |

**Preflight: PASS** —— 可进入 Phase 5 执行。
