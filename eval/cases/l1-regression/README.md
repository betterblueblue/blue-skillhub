# L1 专项回归记录

这个目录记录 2026-06-24 至 2026-06-28 期间的几轮专项回归。它是历史批次说明，不是当前 L1 的统一入口；当前用例定义在 `eval/cases/impact/` 和 `eval/cases/pathfinder/`，运行方法见 [Skill 测评体系](../../../docs/skill-eval/)。

## 为什么需要这套回归

[2026-06-24 改进记录](../../../docs/archive/2026-06/skill-improvement-2026-06-24.md) 包含 P1-A、P1-B、I1-A、I2-A 和 IP1-A 共 5 项修改，涉及 Pathfinder 与 ImpactRadar。专项回归用于确认这些修改没有破坏原有能力。

## 和盲测（blind/）的区别

| | 盲测（blind/） | L1 回归（本目录） |
|---|---|---|
| 用例来源 | B1-B6，真实开发场景，不预设答案 | L1 中的 P1/R1/F1，带有 `expected` 验收条件 |
| 用途 | 验证 5 个改进项是否修复了盲测暴露的问题（有改进前后对比） | 验证改进没破坏既有能力（无改进前后同模型对比） |
| 能否判断分数变化 | 可以，同一个模型在修改前后运行相同用例 | 不可以，历史基线使用 kimi/opus，与本批模型不同 |
| 评分依据 | `JUDGE-RUBRIC.md` | 用例的 `expected` 字段 |

L1 专项回归是盲测的补充。盲测负责比较修改前后的变化，专项回归负责检查其他类型的用例是否仍然正常。由于执行模型不同，这批分数不能直接和 `eval/baselines/` 中的 kimi/opus 基线比较。

## 用例选择与改进对应关系

首批测试从当时的 13 个 L1 用例中选择 3 个，每个对应一组改进：

| 用例 | Skill | 对应改进 | 选择原因 |
|------|-------|---------|------------------|
| P1 | pathfinder | P1-A + P1-B | go-admin 是独立 Git 仓库 + 有 DB，能触发 P1-A 的 facts 校验；有 casbin + JWT auth 流程，能触发 P1-B 的认证-鉴权字段一致性自检 |
| R1 | impact | I1-A + I2-A | full 模式，会生成 `030-implementation.md`，能触发 I1-A 方法名存在性验证 + I2-A 被调方法异常行为确认 |
| F1 | impact | IP1-A | full 模式，有 context-pack 的"暂不纳入范围"环节，能触发 IP1-A 用户场景覆盖验证 |

## 评分方法

每次运行都按 L1 用例中的 `expected` 字段逐项检查：

- `must_hit_files`：预期命中的文件是否找到
- `iron_rules_must_hold`：要求遵守的强制规则是否全部满足
- `forbidden_claims`：预期不出现的错误论断是否出现
- `trap_for`：预设的坑是否踩中

评分卡写入 `eval/runs/l1-regression-<date>-<model>/`。评审模型与执行模型应分开记录，避免把执行结果和评审意见混在一起。

## 评审重点（对应改进项）

除了 L1 case 原有的 expected 检查，额外关注改进项是否触发：

| Case | 额外检查 |
|------|---------|
| P1 | Script Gate 输出是否含 V6；facts/scan.json 和 git.json 内容是否合理；【10】权限模型节是否做了认证-鉴权字段一致性自检 |
| R1 | `030-implementation.md` 中的方法名是否经 grep 验证存在；对已有方法的调用是否确认了异常行为 |
| F1 | context-pack 的"暂不纳入范围"是否做了用户场景覆盖验证；排除文件是否附 trace 证据 |

## Impact 合并后全量回归（2026-06-26）

`impact-pro` 合并到 ImpactRadar 后，当时的 11 个用例统一使用 `/impact`，并完整运行 Phase 1-5。

| 模型 | Prompt 文件 | 产出目录前缀 | 运行记录目录 |
|------|------------|-------------|---------|
| Composer 2.5 | `PROMPT-composer25-merge-regression.md` | `l1-regression-2026-06-26/` | `eval/runs/2026-06-26-impact@3b3148b/` |

评审模型：GLM-5.2。详细方案见 `eval/runs/2026-06-26-impact@3b3148b/README.md`。

## 风格规则与 Pathfinder 刷新测试（2026-06-28）

这一批新增 S1 和 P4 两个 L1 用例：

| 用例 | Skill | 测试目标 | 准备要求 |
|------|-------|---------|-----------|
| S1 | impact | 风格契约：用户要求 `System.out.println`，但 `_style-rules.md` 有 grep 强制规则禁用 | 运行前在项目 `change-impact/` 下创建 `_style-rules.md`（1 条 grep 强制规则 + 2 条建议规则） |
| P4 | pathfinder | 扩展深度刷新：已有地图后再挖 casbin 权限模块 | 先运行 P1 生成初始地图，再运行 P4 的 prompt |

### S1 额外检查

- context-pack 的 `### 风格规范` 段是否填写了 `_style-rules.md` 状态
- skill 是否警告 `System.out` 违反强制规则
- V8 校验器是否通过（契约存在且 grep 可执行）
- 产出代码是否避免了 `System.out`（改用 Slf4j）

### P4 额外检查

- 刷新是否保留了初始地图中仍有效的观察
- casbin 模块分析是否带 `【已核实】` 标签
- git HEAD 是否与初始地图一致或更新（如有新 commit）
- 地图 `【13】没挖深的部分` 是否更新（casbin 已扩展）

## 目录结构

```text
eval/cases/l1-regression/
├── README.md
└── PROMPT-composer25-merge-regression.md  # 2026-06-26 合并后回归 Prompt
```

早期的模型专用 Prompt 已不在本目录。当前仓库有 16 个 ImpactRadar 用例和 6 个 Pathfinder 用例，均以 `eval/cases/{impact,pathfinder}/*.json` 为准。
