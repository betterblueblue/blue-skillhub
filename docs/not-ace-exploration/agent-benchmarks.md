# Agent Benchmarks

V3/V3.1 的目标从“检索结果是否命中文件”升级为“agent 在真实任务里是否能做出完整、低幻觉、可执行的影响分析”。

实验限制：

- 不写代码，只产出影响分析和修改方案。
- 每组每任务先跑 1 次，作为 pilot。
- 允许常规 coding agent 工具：`rg`、文件读取、`git`、必要的目录探测。
- Not ACE 组额外允许通过 MCP 使用 Not ACE。

## V3: Claude Code + Minimax M3

分组：

| Group | Model / Tools | Purpose |
| --- | --- | --- |
| A | Claude Code + Minimax M3 + 常规工具 | 中等模型强基线。 |
| B | Claude Code + Minimax M3 + Not ACE + 常规工具 | 测 Not ACE 对 M3 的上下文发现增益。 |
| C | Codex + 常规工具 | 强模型参考上限。 |

任务：

| Task | Focus |
| --- | --- |
| `fastapi-item-source` | FastAPI + React 字段流转影响分析。 |
| `ruoyi-permission-chain` | RuoYi 权限字符串到前端按钮权限链路。 |
| `go-story-origin` | Go 任务中的产品语言入口、模型、迁移和接口链路。 |

主要结果：

| Group | P0 Recall | Overall Recall | Quality | Avg Time | Cost |
| --- | ---: | ---: | ---: | ---: | ---: |
| M3 + `rg` | 0.933 | 0.884 | 13/15 | 197.788s | $2.098848 |
| M3 + Not ACE | 1.000 | 0.939 | 15/15 | 240.077s | $2.250654 |
| Codex + `rg` | 1.000 | 1.000 | 15/15 | N/A | N/A |

关键观察：

- M3 + `rg` 在 Go 任务中漏掉 P0 文件 `hello.go`。
- M3 + `rg` 误把 AutoMigrate 链路归因到 `common/database.go`。
- M3 + Not ACE 找到了更完整的链路，最终影响分析更接近高级 agent。
- Not ACE 对 M3 的主要价值是降低第一步找错方向的概率，而不是减少耗时。

V3 结论：

Not ACE 对 M3 是稳定性增强。它能提升 P0 recall、overall recall 和分析完整度，但不是效率增强器；复杂链路中仍需要 `rg` 补注册点、测试、generated client、migration 等边界。

## V3.1: Claude Code + GLM-5.1

分组：

| Group | Model / Tools | Purpose |
| --- | --- | --- |
| E | Claude Code + GLM-5.1 + 常规工具 | 测 GLM baseline。 |
| F | Claude Code + GLM-5.1 + Not ACE + 常规工具 | 测 Not ACE 对 GLM 的边际收益。 |

主要结果：

| Group | P0 Recall | Overall Recall | Quality | Avg Time | Cost | Turns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GLM + `rg` | 1.000 | 0.939 | 15/15 | 651.339s | $8.286750 | 44 |
| GLM + Not ACE | 1.000 | 0.970 | 15/15 | 330.634s | $5.037745 | 55 |

关键观察：

- GLM baseline 本身已经强于 M3 baseline。
- Not ACE 没有显著改变 P0 recall，因为 GLM baseline 已经达到 1.000。
- Not ACE 明显降低平均耗时和成本，但 turns 增加，说明它可能改变了探索路径，而不是简单减少工具调用。

V3.1 结论：

Not ACE 对不同模型的收益形态不同。对 M3，它主要提升稳定性和完整度；对 GLM-5.1，它更像效率和成本优化器；对 Codex 这类强模型，预期边际收益更小，后续可作为 D 组补测。

## V3.2: Claude Code + Kimi K2.6

分组：

| Group | Model / Tools | Purpose |
| --- | --- | --- |
| G | Claude Code + Kimi K2.6 + 常规工具 | 测 Kimi baseline。 |
| H | Claude Code + Kimi K2.6 + Not ACE + 常规工具 | 测 Not ACE 对 Kimi 的边际收益。 |

主要结果：

| Group | P0 Recall | Overall Recall | Quality | Avg Time | Cost | Turns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Kimi K2.6 + `rg` | 0.833 | 0.818 | 14.667/15 | 152.335s | $7.250610 | 61 |
| Kimi K2.6 + Not ACE | 0.767 | 0.672 | 14.000/15 | 170.404s | $8.511360 | 44 |

关键观察：

- Kimi K2.6 + `rg` 在本轮 pilot 中比 Kimi K2.6 + Not ACE 更好：recall 更高、质量分更高、耗时更短、成本更低。
- FastAPI 任务中，Kimi + Not ACE P0 recall 满分，但漏掉 `frontend/src/client/schemas.gen.ts`、`backend/tests/api/routes/test_items.py`、`backend/tests/utils/item.py`。
- RuoYi 任务中，两组都漏掉 `SysPermissionService.java`、`UserDetailsServiceImpl.java`、`PermissionContextHolder.java` 等 expected 文件，说明 Kimi 倾向于写出完整叙述，但不一定稳定列出评分所需的具体链路文件。
- Go 任务中，Kimi + `rg` 命中全部 expected files；Kimi + Not ACE 漏掉 P0 文件 `hello.go`。

V3.2 结论：

这轮不支持“Not ACE 能增强 Kimi K2.6”的结论。更合理的解读是：Kimi K2.6 本身会做较强的宽搜索，Not ACE 在部分任务上可能过早收窄上下文，导致边界文件漏召回。这个结论仍需要重复运行验证，尤其是 `go-story-origin`。

## V3.3: Claude Code + DeepSeek V4 Pro

DeepSeek V4 Pro 这一轮作为探针运行，不纳入正常 scoring table。本轮通过硅基流动平台接入，不代表 DeepSeek 官方模型在官方服务或其他接入方式下的真实能力。

分组：

| Group | Model / Tools | Outcome |
| --- | --- | --- |
| I | Claude Code + DeepSeek V4 Pro + 常规工具 | 无法正常评分。 |
| J | Claude Code + DeepSeek V4 Pro + Not ACE + 常规工具 | 连续超时，无法正常评分。 |

模型校验：

- 首次试跑实际模型为 `deepseek-ai/DeepSeek-V4-Flash`，结果废弃。
- 重新配置后确认实际模型为 `deepseek-ai/DeepSeek-V4-Pro`。

主要结果：

| Group | Task | Result |
| --- | --- | --- |
| DeepSeek V4 Pro + `rg` | `fastapi-item-source` | Claude JSON 返回 success，但 `result` 为空。 |
| DeepSeek V4 Pro + `rg` | `ruoyi-permission-chain` | Claude JSON 返回 success，但 `result` 为空。 |
| DeepSeek V4 Pro + `rg` | `go-story-origin` | 输出 Claude Code system reminder / skill 文本，而非影响分析。 |
| DeepSeek V4 Pro + Not ACE | `fastapi-item-source` | 15 分钟超时，反复工具调用，未收敛。 |
| DeepSeek V4 Pro + Not ACE | `ruoyi-permission-chain` | 15 分钟超时，反复工具调用，未收敛。 |

V3.3 结论：

这轮不能评价 Not ACE 对 DeepSeek V4 Pro 的增益，因为普通 `rg` baseline 自身就没有产出有效 final artifact。更合理的判断是：当前 Claude Code benchmark harness 下，DeepSeek V4 Pro 的适配稳定性不足。下一步应先做一个最小 sanity check，确认 `--output-format json` 能稳定把用户答案写入 `result`，再重跑 benchmark。

## V3.4: Claude Code + DeepSeek V4 Flash Sanity

DeepSeek V4 Flash 来自同一硅基流动平台，这轮只做 harness sanity，不进入正式 scoring table；同样不代表 DeepSeek 官方模型在官方服务或其他接入方式下的真实能力。

主要结果：

| Check | Result |
| --- | --- |
| Minimal JSON answer | 模型确认为 `deepseek-ai/DeepSeek-V4-Flash`，但 JSON `result` 为空。 |
| Plain text sentinel | 能返回文本，但 `BENCHMARK_READY` 变成 `BENCHMARK_READYY`。 |
| Stream JSON simple answer | 通过，能在 `result` 中返回中文短句。 |
| Stream JSON repo sanity | 通过，能识别 Go 项目入口 `hello.go`。 |
| Direct Not ACE MCP | 失败。模型会调用 `mcp__not-ace__search_context`，但 Not ACE 返回 116.5KB 大结果后，下一轮 API 400。 |
| Compressed Not ACE context injection | 失败，返回空 result。 |

关键观察：

- Flash 比 Pro 更有希望，因为 simple stream-json 路径能工作。
- 但它仍不能直接进入 Not ACE agent benchmark。
- 最大问题不是完全不会用 Not ACE，而是 Not ACE MCP 返回过大 tool result 后，Claude Code + Flash 的下一轮调用不稳定。
- Not ACE 的 Go 任务 top results 语义上有用，包含 `articles/models.go`、`articles/routers.go`、`articles/serializers.go`、`articles/validators.go`、测试文件，但漏掉 `hello.go`。

V3.4 结论：

DeepSeek V4 Flash 可以继续研究，但当前要换测试方法：使用 `stream-json`，避免让模型直接吃 Not ACE MCP 原始大结果，改为外部预检索 + 极小 context pack + 文件选择任务。它现在不适合直接跑完整 V3 agent benchmark。

## V3.5: Claude Code + GLM-5

GLM-5 这一轮进入正式 scoring table。

分组：

| Group | Model / Tools | Purpose |
| --- | --- | --- |
| K | Claude Code + GLM-5 + 常规工具 | 测 GLM-5 baseline。 |
| L | Claude Code + GLM-5 + Not ACE + 常规工具 | 测 Not ACE 对 GLM-5 的边际收益。 |

主要结果：

| Group | P0 Recall | Overall Recall | Quality | Avg Time | Cost | Turns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GLM-5 + `rg` | 0.850 | 0.853 | 14.333/15 | 139.806s | $5.142750 | 62 |
| GLM-5 + Not ACE | 0.850 | 0.793 | 14.667/15 | 177.013s | $6.545355 | 65 |

逐任务观察：

| Task | GLM-5 + `rg` | GLM-5 + Not ACE |
| --- | --- | --- |
| `fastapi-item-source` | P0 1.000，overall 0.909，漏 `schemas.gen.ts`。 | P0 1.000，overall 0.909，漏 `backend/tests/utils/item.py`。 |
| `ruoyi-permission-chain` | P0 0.750，overall 0.818，漏 `UserDetailsServiceImpl.java` 和 `SysRoleController.java`。 | P0 0.750，overall 0.636，漏 `UserDetailsServiceImpl.java`、`SysUserController.java`、`getters.js`、`PermissionContextHolder.java`。 |
| `go-story-origin` | P0 0.800，overall 0.833，漏 `hello.go`。 | P0 0.800，overall 0.833，漏 `hello.go`。 |

V3.5 结论：

这轮不支持“Not ACE 能增强 GLM-5”的结论。Not ACE 组最终叙述质量略高，但没有提升 P0 recall，overall recall 下降，并且耗时和成本都更高。与 GLM-5.1 相比，GLM-5 对 Not ACE 的利用效果明显更弱。

## V3.6: GLM-5.1 Go Repeat

这轮只复跑 `go-story-origin`，因为它最能观察产品语言入口、结构边界和 `hello.go` 迁移入口是否被找到。

分组：

| Group | Runs |
| --- | --- |
| GLM-5.1 + `rg` | r1, r2b, r3b |
| GLM-5.1 + Not ACE | r1, r2, r3 |

逐轮结果：

| Group | Run | P0 Recall | Overall Recall | `hello.go` | Duration | Cost | Turns |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| GLM-5.1 + `rg` | r1 | 1.000 | 1.000 | yes | 549.200s | $2.380870 | 12 |
| GLM-5.1 + `rg` | r2b | 1.000 | 1.000 | yes | 323.922s | $1.752275 | 9 |
| GLM-5.1 + `rg` | r3b | 1.000 | 1.000 | yes | 399.788s | $2.079745 | 9 |
| GLM-5.1 + Not ACE | r1 | 1.000 | 1.000 | yes | 223.904s | $1.662400 | 19 |
| GLM-5.1 + Not ACE | r2 | 1.000 | 1.000 | yes | 173.118s | $1.049940 | 13 |
| GLM-5.1 + Not ACE | r3 | 1.000 | 1.000 | yes | 200.862s | $1.755005 | 20 |

汇总：

| Group | Avg P0 Recall | Avg Overall Recall | `hello.go` Hits | Avg Duration | Total Cost | Total Turns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GLM-5.1 + `rg` | 1.000 | 1.000 | 3/3 | 424.303s | $6.212890 | 30 |
| GLM-5.1 + Not ACE | 1.000 | 1.000 | 3/3 | 199.295s | $4.467345 | 52 |

V3.6 结论：

GLM-5.1 + Not ACE 在 Go 语义任务上形成了更强证据：它没有进一步提升 recall，因为两组都已满分；它的价值体现在用更低耗时和更低成本达到同样完整的上下文覆盖。Not ACE 组 turns 更多，说明它不是简单减少交互次数，而是改变探索路径，让 GLM-5.1 更快进入正确上下文。

## V3.7: M3 Go Repeat

这轮复跑同一个 `go-story-origin` 任务，观察 M3 是否能稳定命中 `hello.go`。

分组：

| Group | Runs |
| --- | --- |
| M3 + `rg` | r1, r2, r3 |
| M3 + Not ACE | r1, r2, r3 |

逐轮结果：

| Group | Run | P0 Recall | Overall Recall | `hello.go` | Duration | Cost | Turns |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| M3 + `rg` | r1 | 0.800 | 0.833 | no | 143.124s | $0.588600 | 13 |
| M3 + `rg` | r2 | 1.000 | 1.000 | yes | 216.553s | $0.618846 | 14 |
| M3 + `rg` | r3 | 1.000 | 1.000 | yes | 243.041s | $0.908839 | 15 |
| M3 + Not ACE | r1 | 1.000 | 1.000 | yes | 219.924s | $0.608266 | 34 |
| M3 + Not ACE | r2 | 1.000 | 1.000 | yes | 179.101s | $0.648287 | 18 |
| M3 + Not ACE | r3 | 1.000 | 1.000 | yes | 209.499s | $0.687341 | 28 |

汇总：

| Group | Avg P0 Recall | Avg Overall Recall | `hello.go` Hits | Avg Duration | Total Cost | Total Turns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M3 + `rg` | 0.933 | 0.944 | 2/3 | 200.906s | $2.116285 | 42 |
| M3 + Not ACE | 1.000 | 1.000 | 3/3 | 202.841s | $1.943893 | 80 |

V3.7 结论：

M3 + Not ACE 的收益主要是稳定性，不是速度。它让 M3 在 3 次运行中都命中 `hello.go`，并保持 P0/overall recall 满分；`rg` 组新增两轮补上了，但原始 r1 漏掉 `hello.go`，说明常规工具对 M3 来说有更高的路径波动。

## 当前综合判断

| Scenario | Judgment |
| --- | --- |
| Exact symbol 已知 | `rg` 优先，Not ACE 提升有限。 |
| 产品语言 / 自然语言入口 | Not ACE 有明显价值。 |
| 中等能力模型 | Not ACE 能减少漏 P0 和误判链路。 |
| 强 baseline 模型 | Not ACE 可能更多体现在探索成本，而不是 recall。 |
| Kimi K2.6 pilot | 当前结果更支持 Kimi + `rg`，Not ACE 未显示正收益。 |
| DeepSeek V4 Pro probe | 当前不可评分，优先排查 Claude Code harness 适配。 |
| DeepSeek V4 Flash sanity | simple stream-json 可用，但 Not ACE MCP 大结果会触发不稳定。 |
| GLM-5 pilot | 可评分，但 Not ACE 未显示正收益；GLM-5.1 更值得继续。 |
| GLM-5.1 repeat | 在 Go 语义任务上，Not ACE 保持满分 recall，同时显著降低耗时和成本。 |
| M3 repeat | 在 Go 语义任务上，Not ACE 稳定提升 recall 一致性，尤其是 `hello.go`。 |
| 复杂链路任务 | Not ACE 找入口，`rg` 和框架约定做验证。 |
