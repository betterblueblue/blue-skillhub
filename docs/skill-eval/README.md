# Skill 测评体系

> 唯一入口：无论测哪个 skill、改了什么、想跑哪层，从这里开始。

## 三层模型

| 层 | 测什么 | 怎么跑 | 成本 | 触发 |
|---|---|---|---|---|
| L0 静态自洽 | 铁律存在、引用完整、共享契约、fixture 锁定 | `bash skills/<skill>/tests/run.sh` | 免费 | 每次改动必跑 |
| L1 行为契约 | subagent 扮用户跑 case，客观维度自动判 + 安全闸 | 见 eval/ 目录 | 便宜模型 | release 前 / 定期 |
| L2 人审深度 | 主观维度（苏格拉底质量、文档/地图可读性） | 人工 + 可选多模型评委 | 贵 | 里程碑 / 红线命中 |

## 快速决策树

1. **改了 SKILL.md / 铁律 / 模板 / profile / rubric？**
   → 跑 L0（必）+ 按触发矩阵选 L1 子集（见 regression.md）

2. **要 release 一个新版本？**
   → L0 + L1 全量 + L2 抽样 + 和上一基线 diff（见 baselines/）

3. **只想确认没改坏？**
   → 只跑 L0，全绿即安全

4. **测 Pathfinder？**
   → L0 + Pathfinder 专属 rubric（见 rubric-pathfinder.md）

## 关联文档

- [共享契约清单](contracts.md) — 三 skill 都要守的契约，L0 据此检查
- [impact/impact-pro rubric](rubric-impact.md) — 指向 VALIDATION.md 的 9 维
- [Pathfinder rubric](rubric-pathfinder.md) — Pathfinder 专属 9 维
- [回归触发矩阵](regression.md) — 改了什么 → 跑哪些复测
- [基线与红线规则](../../eval/baselines/) — 防漂移硬机制

## 模型方差与控制变量法

L1 由模型执行 + 模型判分,**方差不可消灭**(非确定性系统)。所以 diff 工具链这样对齐:

- **评分卡记双模型**:`runner_model`(执行 skill 产出的) + `judge`(打分的),见 `eval/schemas/scorecard-schema.json`。两者任一不一致或为 `unknown`,跨 run 的分数差**不能直接归 skill**。
- **diff 自动预警混杂**:`eval/diff-baseline.sh`(<skill>) 报红线(契约 PASS→FAIL / p_level 退化) + runner_model 混杂预警。支持 `diff-baseline.sh <skill> <run_a> <run_b>` 直接对比两个 run(控制变量实验用)。
- **控制变量实验**:要回答"分数变化是 skill 漂移还是模型方差",保持 runner_model 不变,只改 skill 版本,各 cell 跑 ≥2 次取均值。脚本 `eval/scripts/analyze_control.py <scorecards_dir>` 聚合两 cell 均值/方差/维度,按"信号比 = |Δ|/σ_内"裁决。

> 详见 `eval/scripts/diff_baseline.py` / `analyze_control.py` 的 docstring。设计依据:2026-06-14 对 GLM-5.1 方差分析的独立审查(结论:方差不可消灭,但分层 + 控制变量能让对比"够用")。
