# Exploration Timeline

## V1: 初始检索对照

目标是验证 Not ACE 是否不是“噱头”。对照组不是弱化的手工搜索，而是会使用 `rg` 的普通 coding agent 基线。

关键设计：

- 对比 Not ACE `search_context` 与 `rg` exact/semantic query。
- 样本覆盖 Go 与 FastAPI 类项目。
- 指标包括 recall、P@10、MRR。

关键发现：

- Not ACE 在自然语言 / 产品语言入口上有优势。
- `rg` 在 exact symbol 已知时仍然非常强。
- FastAPI semantic case 出现 Not ACE 自动索引失败，暴露产品可靠性风险。

## V2: 强化检索 benchmark

V1 后认为样本太少、`rg` baseline 过弱，于是升级为 V2。

关键设计：

- `rg` baseline 允许最多 3 轮搜索。
- expected files 分为 P0 / P1 / P2。
- 增加 hybrid 组：Not ACE 语义召回后再用 `rg` 验证。
- 增加增量索引探针。

关键发现：

- `rg` 的强基线表现非常硬，尤其是 P0 recall。
- Not ACE 单独使用不够稳定。
- hybrid 组 recall 最好，但更慢、噪声也更高。
- 增量索引探针能在约 1.145 秒发现新增临时文件。

## V3: Agent benchmark

V2 之后，实验重点从“能不能搜到文件”升级为“真实 agent 能不能做出更完整的影响分析”。

关键设计：

- A 组：Claude Code + Minimax M3 + 常规工具。
- B 组：Claude Code + Minimax M3 + Not ACE + 常规工具。
- C 组：Codex + 常规工具，作为强模型参考上限。
- 每组每任务先跑 1 次，作为 V3 pilot。
- 限制不写代码，只做影响分析和修改方案，避免污染样本项目。

关键发现：

- M3 + Not ACE 在 P0 recall、overall recall 和分析质量上优于 M3 + `rg`。
- M3 + `rg` 在 Go 任务中漏掉关键入口 `hello.go`，并误判了 AutoMigrate 链路。
- Not ACE 对 M3 更像稳定性增强，不是效率增强。

## V3.1: GLM-5.1 扩展

用户进一步提出是否测试 Claude Code + GLM-5.1。因为本地 Claude Code 已配置，继续用同一套任务框架扩展。

关键设计：

- E 组：Claude Code + GLM-5.1 + 常规工具。
- F 组：Claude Code + GLM-5.1 + Not ACE + 常规工具。

关键发现：

- GLM-5.1 baseline 强于 M3 baseline。
- Not ACE 对 GLM-5.1 的主要收益不再是 P0 recall，而是时间和成本下降。
- 强模型 / 强 baseline 会吞掉一部分 Not ACE 的召回增益，但仍可能获得探索成本收益。

## V3.2: Kimi K2.6 扩展

用户切换 Claude Code 到 Kimi K2.6 后，继续沿用 V3 的三条任务补测。

关键设计：

- G 组：Claude Code + Kimi K2.6 + 常规工具。
- H 组：Claude Code + Kimi K2.6 + Not ACE + 常规工具。

关键发现：

- Kimi K2.6 + `rg` 在本轮 pilot 中整体优于 Kimi K2.6 + Not ACE。
- Kimi + `rg` 在 FastAPI 与 Go 任务上 expected-file recall 都达到 1.0。
- Kimi + Not ACE 在 Go 任务中漏掉 `hello.go`，在 FastAPI 任务中漏掉部分 generated schema / test 边界。
- Not ACE 没有给 Kimi 带来 M3 那种稳定性收益，也没有带来 GLM 那种成本/时间收益。

## V3.3: DeepSeek V4 Pro 探针

用户重新配置 Claude Code 到硅基流动平台的 DeepSeek V4 Pro 后，尝试沿用 V3 任务框架。

关键发现：

- 第一次误配为 `deepseek-ai/DeepSeek-V4-Flash`，结果废弃。
- 重新配置后确认实际模型为 `deepseek-ai/DeepSeek-V4-Pro`。
- DeepSeek V4 Pro + `rg` 组无法正常评分：FastAPI/RuoYi 返回 success 但 final result 为空；Go 返回了 Claude Code system reminder / skill 文本，而不是影响分析。
- DeepSeek V4 Pro + Not ACE 组连续两条任务 15 分钟超时，debug 显示反复工具调用，没有收敛到 final answer。

结论：

这轮不能用来评价 Not ACE 对 DeepSeek V4 Pro 的增益。更准确的结论是：当前 Claude Code benchmark harness 下，DeepSeek V4 Pro 适配稳定性不足，应先做最小 harness sanity check，再纳入主 benchmark。这里的 DeepSeek V4 Pro 来自硅基流动平台接入，不代表 DeepSeek 官方模型在官方服务或其他接入方式下的真实能力。

## V3.4: DeepSeek V4 Flash Sanity

用户切换到硅基流动平台的 DeepSeek V4 Flash 后，先做最小闸门测试。

关键发现：

- `--output-format json` 下，Flash 经常返回空 `result`。
- plain text 能输出，但精确 sentinel 不稳定，例如 `BENCHMARK_READY` 变成 `BENCHMARK_READYY`。
- `stream-json` 能拿到有效结果，并且 repo sanity 中能识别 Go 入口文件 `hello.go`。
- Flash 会调用 Not ACE MCP，但 Not ACE 返回 116.5KB 大结果后，下一轮 API 400。
- 将 Not ACE 结果压缩成小型候选文件列表再注入，Flash 仍出现空答。

结论：

DeepSeek V4 Flash 比 Pro 更有希望，但仍不适合直接跑完整 Not ACE agent benchmark。下一步如果继续测，应改为外部预检索、强压缩 context pack、只测文件选择，不直接让 Flash 吃 Not ACE MCP 原始大结果。

## V3.5: GLM-5 扩展

用户切换到 GLM-5 后，沿用 V3 三任务跑正式对照。

关键设计：

- K 组：Claude Code + GLM-5 + 常规工具。
- L 组：Claude Code + GLM-5 + Not ACE + 常规工具。

关键结果：

- GLM-5 + `rg`: P0 recall 0.850，overall recall 0.853，quality 14.333/15，平均 139.806 秒，总成本 $5.142750。
- GLM-5 + Not ACE: P0 recall 0.850，overall recall 0.793，quality 14.667/15，平均 177.013 秒，总成本 $6.545355。
- Go 任务中两组都漏掉 `hello.go`。
- RuoYi 任务中 Not ACE 组漏文件更多，尤其 `PermissionContextHolder.java`。

结论：

GLM-5 这一轮不显示 Not ACE 正收益。Not ACE 组最终叙述质量略高，但 recall 更低、耗时和成本更高。GLM-5.1 仍然是 GLM 系里更值得继续测 Not ACE 的候选。

## V3.6: GLM-5.1 Go 任务复跑

用户切回 GLM-5.1 后，对最关键的 `go-story-origin` 任务做纵向复跑。

关键设计：

- GLM-5.1 + `rg`: 使用原始 r1 加新增 r2b/r3b，共 3 次。
- GLM-5.1 + Not ACE: 使用原始 r1 加新增 r2/r3，共 3 次。
- 重点观察 `hello.go` 是否稳定命中，以及耗时/成本是否稳定改善。

关键结果：

- 两组 P0 recall 都是 1.000。
- 两组 overall recall 都是 1.000。
- 两组 `hello.go` 都是 3/3 命中。
- GLM-5.1 + `rg` 平均耗时 424.303 秒，总成本 $6.212890。
- GLM-5.1 + Not ACE 平均耗时 199.295 秒，总成本 $4.467345。

结论：

这轮复跑强化了 GLM-5.1 + Not ACE 的结论：Not ACE 在这个语义上下文任务里不是提升 recall，而是在保持完整 recall 的同时显著降低探索耗时和成本。

## V3.7: M3 Go 任务复跑

用户切换回 M3 后，对同一个 `go-story-origin` 任务做纵向复跑。

关键结果：

- M3 + `rg`: P0 recall 0.933，overall recall 0.944，`hello.go` 2/3 命中，平均耗时 200.906 秒，总成本 $2.116285。
- M3 + Not ACE: P0 recall 1.000，overall recall 1.000，`hello.go` 3/3 命中，平均耗时 202.841 秒，总成本 $1.943893。
- Not ACE 组 turns 更多：80 vs 42。

结论：

M3 上 Not ACE 的价值与 GLM-5.1 不同。GLM-5.1 是效率增强，M3 更像稳定性增强：Not ACE 让 M3 在语义产品语言任务中稳定命中 `hello.go` 这样的结构边界文件。
