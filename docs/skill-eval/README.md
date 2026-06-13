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
