# T02 impact-pro 修复项回迁差异分析

- 测试日期：2026-06-07
- 测试人：Codex
- 测试方式：对比 `skills/impact-pro/SKILL.md` 与 `skills/impact/SKILL.md`，并扫描模板误导表述
- 测试范围：`skills/impact`
- 目标：判断 `impact-pro` 升级过程中发现的问题是否仍存在于 `impact`
- 结论：发现 3 个可回迁缺口，已修复。
- 失败等级：修复前最高 P1；修复后无 P0/P1。

## 差异结论

| 缺口 | 风险 | 修复 |
|------|------|------|
| Phase 1 未强制输出假设、歧义、任务规模和成功标准 | Agent 可能在需求未收敛时直接进入实现 | `SKILL.md` 增加 Phase 1 输出格式和行为准则门禁 |
| 缺少独立的破坏性请求安全闸 | 用户要求“直接删/不用分析”时，规则不够醒目 | `SKILL.md` 增加破坏性请求安全闸；`VALIDATION.md` 增加验收项和一票否决 |
| light 模板写着“确认后直接执行” | 易被误解为 light 可以跳过 preflight 和 Step 确认 | `templates/040-light.md` 改为确认摘要后仍进入 Phase 5 preflight 和 Step 级确认 |

## 已确认不需要回迁的项

| impact-pro 能力 | 不回迁原因 |
|-----------------|------------|
| 栈无关内核、profile 加载、generic SQL adapter | `impact` 定位为 Java / MyBatis / RuoYi 类项目；多栈能力由 `impact-pro` 承担 |
| monorepo 多 profile 联合分析 | 超出 `impact` 当前定位 |
| 新技术栈 profile Level 晋升机制 | 仅适用于 `impact-pro` |

## 执行命令

```powershell
rg -n "直接执行|不用分析|直接删|全部替换|DROP|RENAME|行为准则门禁|当前假设|成功标准|破坏性请求" skills/impact skills/impact-pro
```

结果：确认 `impact` 修复前缺少行为准则门禁和破坏性请求安全闸，且 light 模板存在误导表述。

## 验收结论

`impact` 中与执行安全、判档时机、苏格拉底多轮收敛、行为准则、破坏性请求相关的关键缺口已完成回补。剩余边界仍是定位差异：`impact` 不宣称多栈通用；若要验证生产级闭环，应继续在 RuoYi 或等价 Java 项目执行真实 light/full 演练。
