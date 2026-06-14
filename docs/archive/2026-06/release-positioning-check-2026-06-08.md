# Release 定位自查：RuleBlade、ImpactRadar、ImpactRadar Pro

日期：2026-06-08

## 自查目的

这几轮连续优化后，规则、Skill、验证记录和研究文档都变多了。本文用于确认三件事：

1. 三者定位是否清楚。
2. 当前能力边界是否自洽。
3. 下一步是否应该继续加规则，还是先进入复测和安装落地阶段。

## 当前定位

### RuleBlade

定位：通用 AI 编码行为底座。

它不绑定具体任务类型，可以用于：

- 0→1 新系统开发
- 已有系统变更
- bug 修复
- 重构
- 补测试
- 搭配其他 0→1 Skill
- 搭配 `impact` / `impact-pro`

它解决的是 agent 的通用行为问题：少猜、少乱改、先拿上下文、先验证、写操作前确认。

### ImpactRadar

定位：Java/Spring/MyBatis/RuoYi 类现有系统的变更影响分析和受监督执行 Skill。

它不是从 0 到 1 生成新系统的工具，而是在已有系统里做：

- 功能迭代
- 新功能接入
- 字段/API/权限/配置变更
- 重构
- 迁移或对齐任务中的单 Step

它的核心价值是把模糊需求变成证据化影响分析、light/full 判档、可执行 Step、验证方案和执行记录。

### ImpactRadar Pro

定位：多栈已验证 profile 覆盖范围内的现有系统变更影响分析 Skill。

它不宣称覆盖任意技术栈。未知栈先用 generic 兜底，只有通过真实项目 full + light 验收后，才能升级专属 profile。

它解决的是多栈项目中更复杂的上下文发现问题：

- 技术栈识别
- profile 加载
- monorepo 主/辅边界
- DB adapter 降级
- 前端/后端/API/DB/生成物/测试之间的影响分级

## 当前已完成的关键补强

- Context Pack：L1/L2/L3 分层上下文。
- 引用检查分级：必须同步修改 / 需要用户决策 / 只需验证 / 暂不纳入。
- 长期目标模式：维护总目标、当前 Step、Backlog、阻塞项和未验证项。
- 源系统到目标系统对齐：记录可信来源、目标实现、对齐语义和差距证据。
- 接口返回检查清单：避免响应字段变化被轻率判 light。
- V0-V3 验证等级：静态检查、构建测试、运行路径分开说。
- 非 Git 降级保护：无 Git 时必须有替代审计和回滚说明。
- 阻塞恢复安全闸：延迟确认后先复核当前状态。
- 只分析最小响应契约：不写文件也必须展示证据、判档和验证等级。
- RG0-RG3 回归复测协议：后续优化后按风险选择复测包。

## 当前验证证据

### RuleBlade

- v3.2 已通过 Claude Code + MiniMax M3 的 Task A 稳定性复测。
- README 中仍说明：这证明复杂链路门禁能力，不代表只能用于已有系统。

### ImpactRadar

- T04：长期对齐、接口返回字段判档、阻塞恢复、Step 范围一致、验证命令证据、最小写操作闭环。
- T05：响应字段删除判 full、延迟确认不直接执行。

当前结论：适合作为 Java/RuoYi 类项目的受监督影响分析与执行辅助。复杂多文件、多 Step 写操作闭环仍建议继续复测。

### ImpactRadar Pro

- T01-T48：多栈静态验收、前端运行时复测、负向对话复测、生产级项目复验、Step 编号确认、执行前检查、Go RealWorld 写操作闭环、最终复审、M3 RG3 补测。
- T47：Node/Express 删除响应字段。
- T48：React/Vite UI-only 和 monorepo 边界，并修复只分析输出过短问题。

当前结论：可以按“多栈常规项目可投入使用（已验证 profile 覆盖范围内，必须由用户确认后执行）”使用。

## 自洽性检查

| 检查项 | 结果 |
|--------|------|
| RuleBlade 是否被描述得过窄 | 通过；README 和 RuleBlade README 都说明可用于 0→1 和已有系统 |
| impact 是否突出“现有系统” | 通过；README 和 skill README 都明确不是 0→1 |
| impact-pro 是否避免“任意技术栈”宣称 | 通过；使用“已验证 profile 覆盖范围内” |
| Not ACE 是否被描述成可安装 Skill | 通过；README 明确它是研究材料，不是可安装 skill |
| M3 复测是否变成无边界全量测试 | 通过；已用下一轮计划限定高价值场景 |
| 安装路径是否仍有旧仓库路径 | 通过；MCP README 和根 README 使用当前仓库路径示例，并提醒替换本机绝对路径 |

## 暂停继续加规则

当前不建议继续立即增加新的行为规则。理由：

- 规则已经覆盖主要高风险边界。
- 新增规则会增加 Skill 阅读负担。
- 近期真实问题已经能通过 RG3 复测发现并定向修复。

下一阶段更应该做：

1. 按 `docs/install-and-verify-checklist.md` 验证用户能装起来。
2. 按 `docs/archive/2026-06/impact-m3-next-regression-plan.md` 做下一轮高价值 RG3。
3. 按 `docs/impact-regression-protocol.md` 保持“优化后必须复测”的节奏。

## Release 结论

当前文档和验证状态可以作为一个阶段性 release：

```text
RuleBlade = 通用 AI 编码行为底座。
ImpactRadar = Java/RuoYi 类现有系统影响分析与受监督执行 Skill。
ImpactRadar Pro = 多栈已验证 profile 覆盖范围内的现有系统影响分析与受监督执行 Skill。
```

当前最重要的下一步不是继续扩功能，而是让安装、验证、复测和定位说明都能被外部用户顺利读懂并执行。
