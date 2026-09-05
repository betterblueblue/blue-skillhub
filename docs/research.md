# 研究与实验记录

本页收编原 README「研究与实验记录」一节，面向维护和改进这套 Skill 的人；普通使用不需要读这里。

## Not ACE 上下文检索探索

2026 年 6 月，项目针对 [Not ACE](https://not-ace.ame.rip/) 做了一轮上下文检索实验。这部分内容不是可安装的 Skill，而是律刃和 ImpactRadar 的研究资料，完整记录保存在 [docs/not-ace-exploration/](not-ace-exploration/)。

这轮实验的结论是：Not ACE 不能代替 `rg`，更适合先按语义找出可能相关的上下文，再回到源码核实。

在这轮测试中，它让 MiniMax M3 的表现更稳定，也减少了 GLM-5.1 的耗时和费用；但在 Kimi K2.6、GLM-5 和 DeepSeek V4 系列上没有得到稳定收益。DeepSeek V4 Pro 和 Flash 通过硅基流动接入，因此结果不能代表官方渠道的模型表现。

## 其他研究和测试记录

- [ImpactRadar 真实案例复盘](archive/2026-06/impact-real-case-study.md)：长会话和多步骤变更中发现的问题。
- [MiniMax M3 复测计划](archive/2026-06/impact-m3-next-regression-plan.md)：下一轮回归测试的范围和方法。
- [多会话写入授权测试方案](archive/2026-06/impact-multisession-write-gate-test-plan.md)：检查中断和恢复后是否仍需重新授权。
- [律刃与 ImpactRadar 边界检查](archive/2026-06/release-positioning-check-2026-06-08.md)：核对两者的职责是否冲突或遗漏。
- [Not ACE 多模型测试](archive/2026-06/not-ace-benchmark-research.md)：记录不同模型使用 Not ACE 时的表现。
- [三项核心 Skill 的改进依据](archive/2026-06/agent-iteration-conclusions.md)：从测试结果中整理出的后续调整方向。
- [ImpactRadar 回归测试约定](skill-eval/regression.md)：修改 Skill 后如何复测。
- [历史测试材料](archive/2026-06/benchmarks/)：2026-06-09 之前的写入授权测试和模型能力测试，现已归档。
