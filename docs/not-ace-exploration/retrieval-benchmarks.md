# Retrieval Benchmarks

V1/V2 的目标是先把 Not ACE 放在一个公平的检索基线下看，而不是拿它和“瞎找上下文”比较。

## V1

对照：

| Group | Description |
| --- | --- |
| `rg` | 普通 coding agent 常用的全文搜索工具，覆盖 exact 和少量 semantic query。 |
| `not_ace` | Not ACE `search_context` 语义检索。 |

主要结果：

| Group | Recall | P@10 | MRR |
| --- | ---: | ---: | ---: |
| `rg` | 0.549 | 0.350 | 0.425 |
| `not_ace` | 0.644 | 0.607 | 0.625 |

关键 case：

| Case | Finding |
| --- | --- |
| `go-semantic` | `rg` 找到 0/6，Not ACE 找到 5/6，说明语义入口有效。 |
| `fastapi-exact` | 两边 recall 一样，但 Not ACE P@10 为 1.0，`rg` 为 0.7，说明 Not ACE 能减少部分噪声。 |
| `go-exact` | `rg` recall 1.0，Not ACE recall 0.833，说明 exact symbol 已知时不应替代 `rg`。 |
| `fastapi-semantic` | Not ACE 自动索引失败两次，是产品可靠性硬伤。 |

V1 结论：

Not ACE 能证明自己不是噱头，但还不能证明它是完整 Context Engine。它更适合作为语义入口，后续仍需 `rg` 验证边界文件、注册点和测试。

## V2

V2 强化了 baseline 和指标分层。

变化：

- `rg` 最多允许 3 轮搜索。
- expected files 分为 P0 / P1 / P2。
- 增加 hybrid：Not ACE 先语义召回，`rg` 再验证。
- 增加增量索引探针。

主要结果：

| Group | Avg P0 Recall | Avg Recall | Avg P@5 | Avg P@10 | Avg Noise@10 | Avg MRR | Avg Elapsed | Total Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rg` | 1.000 | 0.904 | 0.767 | 0.656 | 3.333 | 0.750 | 0.320s | 18 |
| `not_ace` | 0.708 | 0.619 | 0.600 | 0.569 | 4.167 | 0.917 | 7.950s | 6 |
| `hybrid` | 1.000 | 0.947 | 0.600 | 0.550 | 4.500 | 0.917 | 8.143s | 18 |

增量索引：

- 新增临时文件后，Not ACE 第一次探测即命中。
- 耗时约 1.145 秒。

V2 结论：

`rg` 是非常强的默认基线，尤其是 P0 recall。Not ACE 单独使用不够稳，但能提供好的语义入口；hybrid 组覆盖最完整，代价是更慢且候选噪声更高。比较合理的工作流是 Not ACE 先找可能链路，再用 `rg` / `git` / framework conventions 做验证。
