# Not ACE 是不是有用？一次围绕国产模型与语义上下文检索的 Coding Agent 基准测试

今天（2026年6月8日），我围绕 Not ACE 做了一轮小型基准测试（benchmark）。最初的问题很简单：

> Not ACE 这种语义上下文工具，真的能提升编码 agent（coding agent）的上下文发现能力吗？

但测到后面，问题变得更具体：

> 当模型能力不同、工具链不同、任务类型不同的时候，Not ACE 的收益到底体现在哪里？

测完以后，我觉得它不是一句“有用”或“没用”能概括的。更准确地说：

> Not ACE 不是 `rg` 的替代品，而是一个语义上下文入口。它在不同模型上帮上的忙不一样：对 MiniMax M3（下文简称 M3）更像是在补稳定性，对 GLM-5.1 更像是在省时间、省成本；但在这轮测试里，Kimi K2.6、GLM-5、DeepSeek V4 系列没有跑出稳定收益。

注：本文里的 `rg` 指 [ripgrep](https://github.com/BurntSushi/ripgrep)，一个常见的命令行全文搜索工具，可以理解成更快、更现代的 `grep`。Codex、Claude Code 这类编码 agent 在阅读代码库时经常会用它做符号搜索、关键词搜索和路径定位。

这里可以先用几个例子理解。

MiniMax M3 的问题不是完全不会找，而是有时会漏掉关键边界。比如 Go 语义任务里，M3 + `rg` 三轮有两轮能找到完整链路，但有一轮漏了 `hello.go`。这个文件不是普通背景文件，而是项目入口和 GORM AutoMigrate 的边界。GORM 是 Go 生态常用的 ORM 库，AutoMigrate 是它根据 Go model 自动创建或更新数据库表结构的能力；漏掉这个文件，影响分析就会少掉“新增字段是否进入数据库迁移链路”这一层判断。M3 + Not ACE 三轮都命中了 `hello.go`，P0 recall 也从 0.933 提升到 1.000。所以我说它是在补稳定性：不是把一个完全不会做的模型变成会做，而是让它更少在开头找偏方向，也更少漏掉这种关键入口文件。

GLM-5.1 的情况不一样。它本身已经能稳定找到完整上下文，在同一个 Go 任务里，两组都是 P0/overall recall 满分。但接入 Not ACE 后，平均耗时从 424.303s 降到 199.295s，总成本从 $6.212890 降到 $4.467345。也就是说，Not ACE 没有明显改变“能不能找全”，改变的是“要花多少时间和成本才能找全”。所以它更像是在提效率、降成本。

Kimi K2.6 和 GLM-5 暂时没有看到类似帮助。Kimi + Not ACE 在 Go 任务里反而漏了 `hello.go`；GLM-5 + Not ACE 的 overall recall 低于 `rg` 组，耗时和成本也更高。DeepSeek V4 系列主要是跑测试时不够顺，比如空 result、system reminder 泄露、Not ACE 大结果触发 API 400，因此这轮不能拿它来评价 Not ACE 本身。需要特别说明的是，本轮 DeepSeek V4 Pro / Flash 通过硅基流动平台接入，不代表 DeepSeek 官方模型在官方服务或其他接入方式下的真实能力。

## 背景：为什么要测 Not ACE

现在的编码 agent 并不缺搜索工具。Codex、Claude Code 这类工具本来就会大量使用 `rg`、文件读取、`git`、框架约定等方式找上下文。

所以如果要证明 Not ACE 有价值，不能把它和“瞎找”比较。一个公平的基线（baseline）应该是：

> Not ACE vs 会用 `rg` 的普通编码 agent。

这也是这轮测试的基本出发点。

## 实验设计

实验分成两类。

第一类是检索型基准测试，只看能不能找到预期文件（expected files）。

第二类是 agent 任务型基准测试，不只看检索结果，而是让 agent 做真实影响分析：

- 能不能找到 P0 关键文件
- 会不会漏结构边界
- 是否读太多无关文件
- 最终分析是否完整
- 是否出现臆测
- 耗时、成本、交互轮次（turns）如何变化

重点任务之一是 Go Gin RealWorld 项目的 `go-story-origin`：

> “发布的 stories/articles 要记录来源 channel，并且 feed/detail 响应要暴露它。”

这个任务故意用产品语言描述，不直接说代码符号。

在这个任务里，关键文件包括：

- `articles/models.go`
- `articles/validators.go`
- `articles/serializers.go`
- `articles/routers.go`
- `articles/unit_test.go`
- `hello.go`

其中 `hello.go` 特别重要。它是 Go 项目的入口和 GORM AutoMigrate 边界。这里的 AutoMigrate 可以理解成“应用启动时根据 model 同步数据库表结构”的迁移入口。一个 agent 如果只找到文章模块，但漏掉 `hello.go`，说明它没有追到完整变更链路。

## 先说总结果

这轮测试后，我对 Not ACE 的判断是：

> 它不是完整的上下文引擎（Context Engine），更不是 `rg` 替代品。它更像一个语义召回入口，适合帮助 agent 从产品语言快速进入候选上下文，然后再用 `rg`、文件阅读和框架约定做验证。

不同模型上的表现差异很明显。

| 模型组合 | Not ACE 主要效果 |
| --- | --- |
| MiniMax M3 + Not ACE | 提升稳定性，减少漏 P0 文件 |
| GLM-5.1 + Not ACE | 召回率不变，但耗时和成本明显下降 |
| Kimi K2.6 + Not ACE | 这轮没有看到明显帮助 |
| GLM-5 + Not ACE | 这轮没有看到明显帮助 |
| DeepSeek V4 Pro / Flash | 当前 Claude Code 测试框架（harness）下不稳定，这轮不打分；本轮通过硅基流动平台接入，不代表官方模型真实能力 |

后面表格里会反复出现几个指标，先简单解释一下：

- P0 召回率（P0 Recall）：必须命中的关键文件覆盖比例。
- 整体召回率（Overall Recall）：所有预期文件（expected files）的覆盖比例。
- 分析质量（Quality）：人工评分的最终影响分析质量，满分通常为 15。
- 平均耗时（Avg Duration / Avg Time）：单次任务平均完成时间。
- 成本（Cost / Total Cost）：Claude Code 返回的模型调用成本。
- `hello.go` 命中：Go 任务中是否找到入口和 AutoMigrate 边界文件。

## MiniMax M3：Not ACE 主要是在补稳定性

M3 这组最能看出 Not ACE 的“兜底”作用。

在 `go-story-origin` 任务上做了 3 次复跑：

| 组 | 平均 P0 召回率（Avg P0 Recall） | 平均整体召回率（Avg Overall Recall） | `hello.go` 命中 | 平均耗时（Avg Duration） | 总成本（Total Cost） |
| --- | ---: | ---: | ---: | ---: | ---: |
| M3 + `rg` | 0.933 | 0.944 | 2/3 | 200.906s | $2.116285 |
| M3 + Not ACE | 1.000 | 1.000 | 3/3 | 202.841s | $1.943893 |

这个结果说明，Not ACE 没有明显让 M3 更快，但让它更不容易漏关键文件。

M3 + `rg` 后两轮也能找到完整链路，但第一轮漏了 `hello.go`。而 M3 + Not ACE 三轮都命中。

所以在 M3 上，我更愿意这样概括：

> Not ACE 对 M3 的主要价值不是提速，而是减少“第一步找错方向”或漏掉结构边界的情况。

## GLM-5.1：Not ACE 更像是在省时间、省成本

GLM-5.1 的情况不一样。

在同一个 Go 语义任务上，GLM-5.1 + `rg` 本身已经很强，3 次都能找到完整上下文。但 Not ACE 仍然让它跑得更快、更便宜：

| 组 | 平均 P0 召回率（Avg P0 Recall） | 平均整体召回率（Avg Overall Recall） | `hello.go` 命中 | 平均耗时（Avg Duration） | 总成本（Total Cost） |
| --- | ---: | ---: | ---: | ---: | ---: |
| GLM-5.1 + `rg` | 1.000 | 1.000 | 3/3 | 424.303s | $6.212890 |
| GLM-5.1 + Not ACE | 1.000 | 1.000 | 3/3 | 199.295s | $4.467345 |

这组很关键。

因为它说明 Not ACE 没有提升召回率，双方本来都是满分。但它让 GLM-5.1 用更少时间、更低成本找到同样完整的上下文。

所以在 GLM-5.1 上，我会这样概括：

> Not ACE 对 GLM-5.1 的价值主要不是“多找到了什么”，而是“更快、更便宜地找全了”。

## Kimi K2.6：这轮没有帮上忙

Kimi K2.6 的结果比较反直觉。

| 组 | 平均 P0 召回率（Avg P0 Recall） | 平均整体召回率（Avg Overall Recall） | 分析质量（Quality） | 平均耗时（Avg Time） | 成本（Cost） |
| --- | ---: | ---: | ---: | ---: | ---: |
| Kimi K2.6 + `rg` | 0.833 | 0.818 | 14.667/15 | 152.335s | $7.250610 |
| Kimi K2.6 + Not ACE | 0.767 | 0.672 | 14.000/15 | 170.404s | $8.511360 |

这轮里，Kimi + `rg` 反而更好。

尤其在 Go 任务中，Kimi + `rg` 找到了 `hello.go`，而 Kimi + Not ACE 漏了它。

一个可能解释是：Kimi 本身会做较强的宽搜索，Not ACE 的语义结果反而让它过早收窄，漏掉结构边界。

因此 Kimi 这轮不能证明 Not ACE 有帮助。

## GLM-5：不如 GLM-5.1

GLM-5 也跑了同样对照。

| 组 | P0 召回率（P0 Recall） | 整体召回率（Overall Recall） | 分析质量（Quality） | 平均耗时（Avg Time） | 成本（Cost） |
| --- | ---: | ---: | ---: | ---: | ---: |
| GLM-5 + `rg` | 0.850 | 0.853 | 14.333/15 | 139.806s | $5.142750 |
| GLM-5 + Not ACE | 0.850 | 0.793 | 14.667/15 | 177.013s | $6.545355 |

GLM-5 + Not ACE 的叙述质量略好，但召回率更低，耗时和成本更高。Go 任务里两组都漏了 `hello.go`。

所以 GLM 系里，目前更值得继续测的是 GLM-5.1，而不是 GLM-5。

## DeepSeek V4：这轮主要卡在调用链

DeepSeek V4 Pro 和 V4 Flash 都试了，但这轮不适合和其他模型放在一起比较。

DeepSeek V4 Pro 的问题是：

- JSON `result` 为空
- 输出 Claude Code system reminder / skill 文本
- Not ACE 组长时间不收敛

DeepSeek V4 Flash 比 Pro 好一点，`stream-json` 简单任务能跑，甚至能识别 `hello.go`。但直接调用 Not ACE MCP 时，Not ACE 返回了 116KB 的大结果，下一轮 API 400。

所以 DeepSeek 这轮测到的不是 Not ACE 的能力，更像是在提醒我们：

> 当前 Claude Code + DeepSeek V4 系列 + MCP 大结果这条链路还不够稳，应该先把调用方式调顺，再做正式对照。

## 关键发现：Not ACE 不替代 `rg`

这轮基准测试反复证明了一件事：

> `rg` 在 exact symbol 场景仍然非常强。

如果你已经知道要找 `ArticleModel`、`hasPermi`、`ItemCreate`，那 `rg` 很直接、很稳定、很便宜。

Not ACE 的优势更多出现在：

- 用户说的是产品语言
- 需求没有给出代码符号
- agent 容易第一步找错方向
- 模型能力中等，需要语义入口辅助
- 目标是减少探索成本，而不是完全替代验证

最佳工作流不是：

> Not ACE 替代 `rg`

而是：

> Not ACE 先做语义召回，`rg` 再验证引用、注册点、边界文件、测试入口。

## 小结

如果只用一句话总结：

> Not ACE 是一个有价值的语义上下文入口，但不是完整的上下文引擎（Context Engine）。

更具体一点：

1. 对 M3，Not ACE 提升稳定性。
2. 对 GLM-5.1，Not ACE 主要是省时间、省成本。
3. 对 Kimi K2.6、GLM-5，这轮没有看到稳定帮助。
4. 对 DeepSeek V4，这轮主要问题是 Claude Code 这条调用链还不够稳。
5. `rg` 仍然是 exact symbol 和验证阶段的强基线。
6. 最合理的实践方式是 Not ACE + `rg` 混合检索。

## 我会怎么用它

如果是我实际使用 Not ACE，我不会让它独立承担全部上下文发现。

我会把它放在第一步：

> “先帮我从产品语言找到可能相关的模块和链路。”

然后立刻接 `rg`：

> “验证这些文件的引用关系、注册点、测试入口和迁移边界。”

也就是说，Not ACE 负责先把可能相关的地方找出来，`rg` 负责继续确认引用、入口和边界有没有漏。

## 后续值得做的实验

这轮已经足够说明 Not ACE 不是噱头，但还不能当作定论。下一步更值得做的是：

- 对 GLM-5.1 + Not ACE 做更多任务复跑
- 把任务扩展到权限链路、状态机、异步任务、generated client
- 记录搜索调用次数（Search Calls）、文件读取次数（File Reads）、Not ACE 调用次数（Not ACE Calls）
- 控制 Not ACE 返回大小，避免大结果把不够稳定的调用链打崩
- 设计更强的混合策略：Not ACE top-N 语义召回 + 强制边界扫描（mandatory boundary scan）

目前最值得继续深入的方向是：

> GLM-5.1 + Not ACE 作为国产强模型 + 语义上下文入口的组合，是否能稳定接近强模型编码 agent 的上下文发现能力。
