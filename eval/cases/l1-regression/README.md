# L1 定向回归说明

> Skill 协议改进后的定向回归，验证三条改进链路没破坏现有能力。
> 跑分模型：Composer 2.5 / Step 3.7 Flash
> 评审模型：GLM-5.2

## 为什么需要这套回归

`docs/archive/2026-06/skill-improvement-2026-06-24.md` 实施了 5 个改进项（P1-A/P1-B/I1-A/I2-A/IP1-A），改了 pathfinder/impact 两个 skill 的协议。需要回归测试确认改进没破坏既有能力。

## 和盲测（blind/）的区别

| | 盲测（blind/） | L1 回归（本目录） |
|---|---|---|
| case 来源 | B1-B6，真实开发场景，不预设答案 | L1 case 中的 P1/R1/F1，有 expected 答案 |
| 用途 | 验证 5 个改进项是否修复了盲测暴露的问题（有改进前后对比） | 验证改进没破坏既有能力（无改进前后同模型对比） |
| 能否说"分数下降" | 能——同模型改进前后跑同 case | 不能——基线是 kimi/opus，不是这两个模型 |
| 评审标准 | JUDGE-RUBRIC.md | L1 case 的 expected 字段（must_hit_files、iron_rules、trap_for） |

**L1 回归是盲测的补充**：盲测是主验证（干净的前后对比），L1 回归确认改进没破坏盲测没覆盖的 case 类型。L1 回归分数不要和 `eval/baselines/` 里的基线直接比——基线 runner 是 kimi/opus，不是 Composer/Step。

## Case 选择和覆盖链路

从 L1 全部 13 个 case 中选 3 个，每个对应一条改进链路：

| Case | skill | 对应改进 | 为什么选这个 case |
|------|-------|---------|------------------|
| P1 | pathfinder | P1-A + P1-B | go-admin 是独立 Git 仓库 + 有 DB，能触发 P1-A 的 facts 校验；有 casbin + JWT auth 流程，能触发 P1-B 的认证-鉴权字段一致性自检 |
| R1 | impact | I1-A + I2-A | full 模式，会生成 `030-implementation.md`，能触发 I1-A 方法名存在性验证 + I2-A 被调方法异常行为确认 |
| F1 | impact | IP1-A | full 模式，有 context-pack 的"暂不纳入范围"环节，能触发 IP1-A 用户场景覆盖验证 |

## 执行方式

和盲测一样：每个模型复制对应 prompt，粘贴发给模型即可。

| 模型 | prompt 文件 | 产出目录前缀 |
|------|------------|-------------|
| Composer 2.5 | `PROMPT-composer25-regression.md` | `l1-regression-composer25/` |
| Step 3.7 Flash | `PROMPT-step37flash-regression.md` | `l1-regression-step37flash/` |

## 跑完后

把两个 `l1-regression-<model>/` 目录的产出位置告诉我，我（GLM-5.2）按 L1 case 的 `expected` 字段逐条核实：

- `must_hit_files`：预期命中的文件是否找到
- `iron_rules_must_hold`：预期守住的铁律是否守住
- `forbidden_claims`：预期不出现的错误论断是否出现
- `trap_for`：预设的坑是否踩中

产出评分卡写入 `eval/runs/l1-regression-<date>-<model>/`。

## 评审重点（对应改进项）

除了 L1 case 原有的 expected 检查，额外关注改进项是否触发：

| Case | 额外检查 |
|------|---------|
| P1 | Script Gate 输出是否含 V6；facts/scan.json 和 git.json 内容是否合理；【10】权限模型节是否做了认证-鉴权字段一致性自检 |
| R1 | `030-implementation.md` 中的方法名是否经 grep 验证存在；对已有方法的调用是否确认了异常行为 |
| F1 | context-pack 的"暂不纳入范围"是否做了用户场景覆盖验证；排除文件是否附 trace 证据 |

## 目录结构

```
eval/cases/l1-regression/
├── README.md                          # 本文件
├── PROMPT-composer25-regression.md    # Composer 2.5 一键执行 prompt
└── PROMPT-step37flash-regression.md   # Step 3.7 Flash 一键执行 prompt
```

L1 case 原始定义在 `eval/cases/{pathfinder,impact}/`，本目录只放批量执行的 prompt。
