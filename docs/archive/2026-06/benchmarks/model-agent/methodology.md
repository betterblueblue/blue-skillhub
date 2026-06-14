# Methodology

## 目标

这个 benchmark 的目标是形成可复跑、可扩展、可解释的模型能力评测体系。

评测对象不是裸模型，而是：

```text
模型 + agent 框架 + 工具集合 + 项目上下文
```

因此结论必须写成：

```text
Claude Code + GLM-5.1 + normal tools 在这组任务中表现如何
```

而不是：

```text
GLM-5.1 一定比某模型强
```

## Phase 0: Sanity

每个模型进入正式任务前必须先过最小闸门。

| Check | 目的 | 失败处理 |
| --- | --- | --- |
| one-line prompt | 确认模型能返回普通答案 | 标记 provider_error，不进入能力评分 |
| JSON output | 确认 agent runner 能解析结果 | 修 runner / output format |
| read file | 确认文件读取工具可用 | 修权限或工具配置 |
| `rg` search | 确认常规搜索可用 | 修 PATH / embedded rg |
| no-edit compliance | 确认 analysis-only 不写文件 | 记录 policy failure |

Sanity 失败不代表模型弱，只代表当前接入不可评分。

## Phase 1: Screening

第一批项目建议选真实但可控的 SaaS 项目，例如 Papermark。

目标：

- 看模型是否能从产品语言找到代码入口。
- 看它会不会漏 Prisma schema、migration、generated client、tests、权限链路。
- 看成本、耗时和工具使用是否可控。
- 找到值得进入第二批的模型。

建议任务类型：

| 类型 | 例子 | 重点边界 |
| --- | --- | --- |
| 字段流转 | 分享链接增加来源渠道字段 | Prisma、API、UI、analytics、tests |
| 权限链路 | data room 成员访问文档权限 | auth、team membership、viewer path |
| analytics | 访问统计新增 referrer category | event schema、Tinybird、UI chart |
| notification | 新增通知偏好 | DB、settings UI、email sending |

第一批不追求终局结论，只筛掉明显不适合的模型，保留失误模式。

第一批结束后只能写：

```text
这个模型组合在 Papermark analysis-only 筛选任务里表现出某种倾向。
```

不能写：

```text
这个模型组合已经被证明是最强 coding agent。
```

## Phase 2: Validation

第二批只让晋级模型进入更复杂项目，例如 Documenso。

目标：

- 看第一批表现是否能迁移到复杂 workflow。
- 测状态机、审计日志、模板、签名流程、权限组合。
- 保持 analysis-only，避免执行成本暴涨。

推荐任务：

| 类型 | 例子 |
| --- | --- |
| 状态机 | 新增 `reminded` 签名状态会影响哪些地方 |
| 权限/审计 | 团队成员下载文档时权限和 audit log 如何串联 |

## Phase 3: Execution

第三批只给最终候选模型真改代码。

目标：

- 验证模型能否把影响分析转成最小正确 patch。
- 验证测试选择、自我修复和回归控制。

建议只跑：

```text
1-2 个模型 × 1-2 个任务 × 1 轮
```

真执行任务必须使用隔离 worktree 或 disposable clone。

## 证据等级

为了避免把 pilot 讲成最终结论，每个结论都要标证据等级。

| Level | 名称 | 说明 |
| --- | --- | --- |
| L0 | Harness 可用 | 模型能跑通 sanity，但还没有任务证据 |
| L1 | Screening 信号 | 在第一批项目里看到召回、工具、成本、稳定性倾向 |
| L2 | Cross-project 复核 | 进入第二批并在另一个复杂项目上保持同类表现 |
| L3 | Execution 证明 | 真改代码、跑验证、能处理失败和回归 |

默认只把 L2 以后称为“较稳定结论”。L1 更适合写成“候选模型画像”。

## 公平性控制

每个对比组必须尽量保持这些条件一致：

- 同一个项目 commit。
- 同一个 task JSON 和 system prompt。
- 同一轮次尽量使用同样的时间上限。
- 每次 run 使用新会话，避免上下文污染。
- 不让被测模型给自己打人工分。
- 失败状态和能力分分开统计。
- 如果修改 expected files 口径，受影响任务需要整体重跑或明确标注不可横向比较。

Not ACE / MCP 组要在 prompt 里明确触发条件。只“配置了 MCP”不等于 agent 一定会主动调用。

## 成本控制

默认使用漏斗，而不是全排列：

1. 所有候选模型先过 Phase 0 sanity。
2. Phase 1 每个模型每个任务跑 1 轮。
3. 只有争议项复跑 1 轮。
4. 只有 `enter` 或强 `hold` 模型进入 Phase 2。
5. 只有 Phase 2 仍然有优势的模型进入 Phase 3。

停止继续评测的常见条件：

- 连续 provider error 或 timeout。
- 两个任务都漏 P0。
- 明显编造不存在文件、表、API。
- 成本超过同批中位数 2 倍，且召回/质量没有明显优势。
- 工具调用不可控，无法稳定复现。

## 任务设计规则

每个任务必须包含：

- `prompt`: 用户自然语言需求，尽量不用准确代码符号。
- `expected_files`: P0/P1/P2 文件列表。
- `reason`: 每个 expected file 为什么重要。
- `must_notice`: 必须识别的架构事实。
- `forbidden_claims`: 不允许编造的结论。
- `mode`: `analysis_only` 或 `execution`。
- `allowed_tools`: 允许工具集合。
- `disallowed_actions`: 禁止行为，例如写文件、跑安装、联网。

P0 / P1 / P2 含义：

| Tier | 含义 |
| --- | --- |
| P0 | 漏掉会导致方案不完整或方向错误 |
| P1 | 漏掉会降低实现/验证质量 |
| P2 | 背景文件，帮助提高完整度 |

## 失败分类

每次 run 必须记录状态。

| Status | 含义 | 是否进入能力评分 |
| --- | --- | --- |
| `completed` | 正常产出 final answer | 是 |
| `timeout` | 超过时间限制 | 否，计入稳定性 |
| `provider_error` | 网关 / API / 模型服务错误 | 否，计入接入稳定性 |
| `tool_error` | 工具调用参数错误或工具崩溃 | 视情况，通常计入工具稳定性 |
| `invalid_output` | 无法解析、空 result、非目标格式 | 否，计入输出稳定性 |
| `policy_or_permission_block` | 权限或安全限制导致无法执行 | 否，单独标注 |

## 晋级规则

进入第二批建议满足：

- 平均 P0 Recall >= 0.85。
- 人工 Quality >= 12/15。
- 至少一个复杂任务中 Boundary Awareness >= 3/3。
- 没有连续两个 `timeout` / `provider_error`。
- 成本不超过同批中位数 2 倍，除非召回明显更强。

淘汰或暂停：

- 最小 prompt 失败。
- 两个任务都漏 P0。
- 连续超时。
- 明显编造不存在文件 / 表 / API。
- 高成本但召回不高。

## 结论写法

禁止写：

```text
模型 A 比模型 B 强。
```

推荐写：

```text
在 Papermark analysis-only 任务中，模型 A 的 P0 recall 更高，但成本更高；模型 B 输出更短、更便宜，但更容易漏 generated schema。
```

结论必须保留：

- 项目范围
- 工具范围
- 任务模式
- 轮次
- 接入方式
- 失败状态
