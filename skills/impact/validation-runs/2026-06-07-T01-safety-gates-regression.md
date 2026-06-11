# T01 修复后安全门禁静态回归

- 测试日期：2026-06-07
- 测试人：Codex
- 测试方式：文档规则静态扫描 + 模板一致性检查
- 测试范围：`skills/impact`
- 目标：验证从 `impact-pro` 回迁的关键安全门禁已在 `impact` 中落地，且旧风险入口不再作为执行规则存在。
- 结论：通过。
- 失败等级：无 P0/P1。

## 回归项

| 检查项 | 期望 | 证据 | 结论 |
|--------|------|------|------|
| Step 编号确认 | Phase 5 必须使用 `确认 Step N / 跳过 Step N` | `SKILL.md` Phase 5；`README.md` 示例；`030-implementation.md` | 通过 |
| 模糊确认无效 | `yes/可以/继续/全部确认` 不得触发写操作 | `SKILL.md` 自动/确认边界；`README.md` 自动/确认边界 | 通过 |
| 判档时机 | Phase 2.5 只预判；Phase 3.5 正式判档 | `SKILL.md` Phase 2.5 / Phase 3.5 | 通过 |
| 苏格拉底多轮 | 每轮 <= 3 问，不是总共 3 问；P0/P1 未确认不得执行 | `SKILL.md` Phase 3 | 通过 |
| 简化不跳闸 | 用户可简化文档形式，但不能跳过安全闸 | `SKILL.md` Phase 3.5；`README.md` v3.1 | 通过 |
| 执行前门禁 | 写操作前必须完成 preflight | `templates/060-preflight.md`；`SKILL.md` Phase 5 | 通过 |
| 执行记录 | `090-execution-record.md` 使用完整模板追加记录 | `templates/090-execution-record.md`；`SKILL.md` 执行记录 | 通过 |
| light 模板 | light 不跳过安全闸 | `templates/040-light.md` | 通过 |
| 实施模板 | Step 需记录语义约定、验证方式和确认提示 | `templates/030-implementation.md` | 通过 |
| 验收标准 | 有轻量验收和一票否决项 | `VALIDATION.md` | 通过 |

## 执行命令

旧风险入口固定字符串扫描：

```powershell
rg -n -F "确认执行？" skills/impact/SKILL.md skills/impact/README.md skills/impact/templates skills/impact/VALIDATION.md
rg -n -F "立即降级" skills/impact/SKILL.md skills/impact/README.md skills/impact/templates skills/impact/VALIDATION.md
rg -n -F "纯执行" skills/impact/SKILL.md skills/impact/README.md skills/impact/templates skills/impact/VALIDATION.md
rg -n -F "Phase 2.5 判档 + 确认" skills/impact/SKILL.md skills/impact/README.md skills/impact/templates skills/impact/VALIDATION.md
```

结果：均无命中。

关键能力扫描：

```powershell
rg -n "确认 Step|phase5-preflight|execution-record|Phase 3.5|P0 必问|不是总问题数" skills/impact
```

结果：命中 `SKILL.md`、`README.md`、`VALIDATION.md`、`templates/060-preflight.md`、`templates/090-execution-record.md`、`templates/030-implementation.md`。

格式检查：

```powershell
git diff --check -- skills/impact
```

结果：通过，无尾随空白。

## 剩余边界

- T01 是静态规则回归，不等同于真实项目 Phase 5 写操作闭环。
- `impact` 仍定位为 Java / MyBatis / RuoYi 类项目的受监督影响分析与执行辅助，不宣称任意技术栈。
- 后续若要升级到生产级闭环证据，应选择 RuoYi 或等价 Java 项目执行一次低风险 Step 级确认演练。
