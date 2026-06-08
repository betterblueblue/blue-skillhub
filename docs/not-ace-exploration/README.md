# Not ACE Exploration

这个目录记录一次围绕 [Not ACE](https://not-ace.ame.rip/) 的上下文检索与 coding agent benchmark 探索。

核心问题不是“Not ACE 能不能替代 `rg`”，而是：

- 它是否能在自然语言 / 产品语言描述下更快找到上下文入口。
- 它对中等能力模型，例如 Claude Code + Minimax M3，是否能提升真实任务中的上下文发现稳定性。
- 它和常规工具链，尤其是 `rg` / `git` / framework verification，应该如何组合。

## 目录

- [timeline.md](timeline.md): 本轮探索时间线与关键决策。
- [retrieval-benchmarks.md](retrieval-benchmarks.md): V1/V2 检索型 benchmark 设计、结果与结论。
- [agent-benchmarks.md](agent-benchmarks.md): V3/V3.1 agent 型 benchmark 设计、结果与结论。
- [next-steps.md](next-steps.md): 下一轮实验建议。

## 安全边界

本目录只保存可复盘的实验设计、指标和结论，不保存：

- Not ACE API Token。
- Claude / Codex 原始 debug log。
- 大体量样本仓库副本。
- 可能包含命令行参数、环境变量或账号信息的 transcript 原文。

原始实验工作区位于本机 `E:\agent\not-ace-benchmark`。如需继续实验，应优先在该目录复制、清洗和评分，再把稳定结论同步回本目录。

## 一句话结论

Not ACE 更像一个有价值的语义上下文入口，而不是完整替代 `rg` 的 Context Engine。它对 exact symbol 场景提升有限，但在产品语言、语义入口和较弱模型的第一步定向上有明显价值；最佳用法是 Not ACE 先召回候选链路，`rg` / `git` / 框架约定再验证注册点、边界文件和测试入口。
