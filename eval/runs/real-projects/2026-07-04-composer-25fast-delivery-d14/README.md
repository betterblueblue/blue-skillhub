# D14 — LOCKED 用户状态影响分析（Composer 2.5 Fast）

## 结论

判定为 **full**。用户 `status` 需从二态扩展为三态（含 LOCKED），必须同步覆盖：枚举定义、登录拦截、后台用户页展示/筛选/改状态、字典翻译、Excel 导出、i18n 文案；并与现有「密码输错临时锁定」机制区分语义。

## Validator

```powershell
python E:\agent\blue-skillhub\skills\impact\scripts\impact_validate.py E:\agent\real-project-fixtures\java-ruoyi-d14-composer-20260704-223205\change-impact\locked-user --mode full --repo-root E:\agent\real-project-fixtures\java-ruoyi-d14-composer-20260704-223205
```

- 退出码：`0`
- 摘要：`26 passed, 0 failed, 1 warnings`（V2：010-requirements 含技术细节 — 可接受）

## 运行信息

| 项 | 值 |
|---|---|
| 场景 ID | D14-java-enum-analysis |
| Case ID | java-ruoyi-impact-enum |
| Runner | composer-25fast-subagent |
| 模型 | Composer 2.5 Fast |
| fixture | `E:\agent\real-project-fixtures\java-ruoyi-d14-composer-20260704-223205` |
| 运行日期 | 2026-07-04 |

## 产物

- `E:\agent\real-project-fixtures\java-ruoyi-d14-composer-20260704-223205\change-impact\locked-user\`
  - `000-context-pack.md`
  - `010-requirements.md`（含判档决策表）
  - `020-design.md`（§6 全局影响检查 19 行）
  - `030-implementation.md`（§3.2 API 方法验证）
  - `_active-state.md`

## 关键发现

1. **现状语义**：`sys_user.status` 仅 0/1（`sql/ry_20260319.sql:54`）；`UserStatus` 有 OK/DISABLE/DELETED，其中 `DELETED("2")` 用于 `del_flag` 而非 status（`SysLoginService.java:113`）。
2. **登录链路**：仅 `status == DISABLE("1")` 拦截（`SysLoginService.java:119`）→ `UserBlockedException` → Shiro `LockedAccountException`（`UserRealm.java:118`）。不加 LOCKED 分支则锁定无效。
3. **UI 二值化**：列表 `user.html` 为 0/1 开关（L258-277）；详情 `view.html` 硬编码「正常/停用」（L59）；编辑/新增为 checkbox。
4. **字典共用风险**：`sys_normal_disable` 仅 0/1，且被部门/角色/岗位等多模块复用 — 直接加「锁定」会波及其他页面；建议新建 `sys_user_status`。
5. **导出**：`SysUser` Excel 注解 `readConverterExp = "0=正常,1=停用"`（L73）须扩展。
6. **已在线会话**：`OnlineSessionFilter` 不复查账号 status — 锁定默认只阻止新登录，不踢已有 session。
7. **命名冲突**：系统另有密码重试锁定（`user.password.retry.limit.exceed`）与 IP 黑名单 — LOCKED 文案需区分。

## 已确认业务决策（2026-07-04）

用户确认「按默认建议全走」：

| 项 | 确认结果 |
|---|---|
| LOCKED 编码 | `"3"` |
| 字典策略 | 新建 `sys_user_status`（0/1/3），不扩展 `sys_normal_disable` |
| 登录提示 | DISABLE → `user.blocked`；LOCKED → 新增 `user.locked` |
| 已在线用户 | 不强制下线，仅拦新登录 |
| 管理操作 | 用户管理页三态（可手动设 LOCKED） |

## 必须同步修改（实施阶段）

| 优先级 | 文件 | 变更 |
|--------|------|------|
| P0 | `UserStatus.java` | 增加 `LOCKED` |
| P0 | `SysLoginService.java` | LOCKED 登录拦截 |
| P0 | `user.html` / `view.html` / `edit.html` / `add.html` | 三态 UI |
| P1 | `SysUser.java` | Excel readConverterExp |
| P1 | 字典 DML + `messages.properties` | 展示与提示 |
| P2 | `UserConstants.java`、可选 `changeStatus` 白名单 | 常量与校验 |

## Out of Scope

- 密码输错临时锁定（`SysPasswordService`）
- 角色/部门/岗位 status
- 在线会话 `OnlineStatus`
- 强制踢已登录 session（除非用户确认纳入）

## Git 状态

- fixture 源码：无改动（仅新增 `change-impact/locked-user/` 文档）
