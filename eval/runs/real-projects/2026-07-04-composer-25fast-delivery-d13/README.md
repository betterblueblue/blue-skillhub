# D13 — java-ruoyi 用户导出权限收紧（Composer 2.5 Fast）

**场景 ID：** D13-java-permission-analysis  
**Fixture：** `E:\agent\real-project-fixtures\java-ruoyi`  
**模式：** full，analysis-only（无代码变更）  
**需求目录：** `change-impact/user_export_permission/`  
**验证：** `impact_validate.py --mode full` → **26 passed, 0 failed, 0 warnings**

## 用户原话

> 现在所有用户都能导出用户列表，需要改成只有管理员角色才能导出。先不要写代码，只做完整影响分析。

## 核心结论

**问题不在“缺少权限控制”，而在默认 DB 授权过宽。**

RuoYi 用户导出链路四层均已就位：

| 层级 | 位置 | 权限字符 | 现状 |
|------|------|----------|------|
| 后端 Shiro | `SysUserController.export` | `system:user:export` | `@RequiresPermissions` 已存在 |
| 前端 Thymeleaf | `user.html` 导出按钮 | `system:user:export` | `shiro:hasPermission` 已存在 |
| 菜单定义 | `sys_menu` menu_id=1004 | `system:user:export` | 已定义 |
| 角色映射 | `sys_role_menu` | role 2 → menu 1004 | **根因：普通角色默认拥有导出** |

种子数据 `insert into sys_role_menu values ('2', '1004')` 使演示用户 `ry`（普通角色）拥有导出权限，表现为“所有用户都能导出”。

## 关键发现

1. **后端必须校验，不能仅隐藏按钮** — `@RequiresPermissions` + Shiro AOP 已在 `POST /system/user/export` 生效；收回 DB 授权后，直接 POST 也会被拒绝。
2. **管理员 bypass** — `user_id=1` 在 `UserRealm` 获 `*:*:*`，不依赖 `sys_role_menu` 是否含 1004。
3. **“管理员”口径歧义** — `ShiroUtils.isAdmin()` 认 `userId==1`，与用户文案“管理员角色”可能不一致；待业务确认（见 010-requirements §2.5）。
4. **推荐最小改法** — 删除种子 SQL 及运行库中 role 2 对 menu 1004 的映射；Controller 与模板**验证不变**即可。
5. **禁止方案** — 仅隐藏前端按钮（不安全，直接 POST 仍可导出）。

## 覆盖范围（must_cover 对照）

- ✅ Shiro `@RequiresPermissions` on export Controller method
- ✅ Thymeleaf `shiro:hasPermission` on export button
- ✅ 角色-权限映射 in DB/SQL (`sys_menu` / `sys_role_menu` / `SysMenuMapper.selectPermsByUserId`)
- ✅ 前后端必须同时校验（现有代码已双层；实施时禁止只改 UI）
- ✅ Shiro 配置（`AuthorizationAttributeSourceAdvisor`、`UserRealm` 授权链）

## 建议 Phase 5 步骤（未执行）

1. 修改 `sql/ry_20260319.sql` — 移除 `(2, 1004)` 种子行  
2. 运行库 DML — `DELETE FROM sys_role_menu WHERE menu_id=1004 AND role_id=2`  
3. 验证 Controller / user.html 权限绑定不变  
4. 清 Shiro 授权缓存或重登  
5. 手工验收：admin 可导出，ry 不可  

详见 `change-impact/user_export_permission/030-implementation.md`。

## 产出文件

| 文件 | 说明 |
|------|------|
| `000-context-pack.md` | 上下文、证据、覆盖缺口 |
| `010-requirements.md` | 业务需求与验收标准 |
| `020-design.md` | 设计方案、19 维全局影响检查 |
| `030-implementation.md` | 判档决策表、实施 Step、API 方法验证 |
| `_active-state.md` | Phase 4 状态与 validator 结果 |

## Validator 摘要

```
SUMMARY: 26 passed, 0 failed, 0 warnings
Exit code: 0
```

命令：

```bash
python E:/agent/blue-skillhub/skills/impact/scripts/impact_validate.py \
  E:/agent/real-project-fixtures/java-ruoyi/change-impact/user_export_permission \
  --mode full \
  --repo-root E:/agent/real-project-fixtures/java-ruoyi \
  --seed 42
```
