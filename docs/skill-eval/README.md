# Skill 测评体系

这里是 Pathfinder 和 ImpactRadar 共享测评资料的入口。IntentAnchor 目前使用独立的校验脚本行为测试，并由 CI 运行，不参与这里的 L1/L2 模型测评。

## 三层模型

| 层 | 测什么 | 怎么跑 | 成本 | 触发 |
|---|---|---|---|---|
| L0 静态检查 | 强制规则、文件引用、共享约定和测试项目版本 | `bash skills/<skill>/tests/run.sh` | 无模型费用 | 每次改动 |
| L1 行为测试 | 让另一个 AI 扮演用户执行用例，再按客观条件评分 | 见 `eval/` | 低成本模型 | 发布前或定期 |
| L2 人工抽查 | 提问质量、文档可读性和项目地图质量 | 人工检查，可选多模型复核 | 较高 | 重要版本或 L1 出现明显下降 |

## 快速决策树

1. **修改了 `SKILL.md`、强制规则、模板、Profile 或评分规则？**
   先跑 L0，再按 [回归触发矩阵](regression.md) 选择需要复跑的 L1 用例。

2. **准备发布新版本？**
   运行 L0、完整 L1 和 L2 抽查，再和上一版基线比较。

3. **只想确认没改坏？**
   先跑 L0。L0 只能证明静态规则和脚本没有明显回归，不能代替真实任务测试。

4. **测 Pathfinder？**
   除 L0 外，使用 [Pathfinder 评分规则](rubric-pathfinder.md)。

## 关联文档

- [共享约定](contracts.md)：Pathfinder 和 ImpactRadar 都要遵守的规则，L0 会据此检查。
- [ImpactRadar 评分规则](rubric-impact.md)：指向 `VALIDATION.md` 中的 9 个评分维度。
- [Pathfinder 评分规则](rubric-pathfinder.md)：Pathfinder 使用的 9 个评分维度。
- [经验进入核心规则的条件](rule-promotion.md)：说明真实使用经验满足什么条件后，才能修改核心规则或门禁。
- [回归触发矩阵](regression.md)：说明不同改动需要复跑哪些测试。
- [真实项目回归测试](../../eval/real-projects/)：可重复运行的 Java、Node.js、Python、前端和 monorepo 用例。
- [当前基线](../../eval/baselines/)：保存用于版本比较的评分数据。

## 完整复验说明

[REVALIDATION.md](REVALIDATION.md) 说明了 L0/L1/L2 的完整运行方式、控制变量方法、模型差异处理、自动评分工具，以及 Pathfinder 和 ImpactRadar 各自的复验清单。

L1 的执行和部分评分依赖模型，因此结果一定会有波动。比较两次运行前，先确认评分卡中的 `runner_model` 是否一致；需要判断某次 Skill 修改是否真正有效时，应让同一个模型运行对照组，并用 `eval/scripts/analyze_control.py` 比较。
