# Model Agent Benchmark

这个目录用于持续评测不同模型接入 coding agent 框架后的真实工程能力。

它不评“模型智商”，而评：

> 一个模型在 Claude Code / Codex 这类 agent 工具链里，能不能稳定找到上下文、正确使用工具、形成影响分析、执行修改并完成验证闭环。

当前体系从 Not ACE 探索得到，但不绑定 Not ACE。它可以同时比较：

- 模型 + 常规工具，例如 `rg`、文件读取、git
- 模型 + 语义检索 MCP，例如 Not ACE
- 强模型 / 中等模型 / 低成本模型
- analysis-only 任务和真改代码任务

## 目录结构

```text
benchmarks/model-agent/
├── README.md
├── methodology.md
├── rubric.md
├── run-result-schema.json
├── runbook.md
├── task-schema.json
├── prompts/
│   └── analysis-only-system.md
├── runs/
│   └── README.md
├── scripts/
│   ├── score-analysis-output.ps1
│   ├── summarize-runs.ps1
│   ├── validate-run-result.ps1
│   └── validate-task.ps1
├── tasks/
│   └── papermark/
│       ├── dataroom-notification-preference.json
│       ├── dataroom-permission-chain.json
│       └── link-source-analytics.json
└── templates/
    ├── manual-review.template.md
    ├── model-scorecard.template.md
    ├── run-report.template.md
    └── task.analysis-only.template.json
```

## 评测分层

| Phase | 名称 | 目的 | 是否改代码 |
| --- | --- | --- | --- |
| 0 | Sanity | 排除接入失败、JSON 输出失败、工具不可用 | 否 |
| 1 | Screening | 在真实 SaaS 项目里筛模型、看失误模式 | 否 |
| 2 | Validation | 只让晋级模型进入复杂 workflow 项目复核 | 否 |
| 3 | Execution | 只让最终候选真改代码并跑测试 | 是 |

推荐项目节奏：

| 批次 | 项目类型 | 候选项目 | 目的 |
| --- | --- | --- | --- |
| 第一批 | Next.js / Prisma SaaS | Papermark | 字段流转、权限、analytics、generated、UI、tests |
| 第二批 | 复杂 workflow | Documenso | 状态机、签名流程、审计、模板、权限 |
| 第三批 | 大型压力或非 TS 栈 | Dub / Go / Java / Python 项目 | 泛化、长上下文、真执行 |

## 漏斗式运行

不要全模型、全项目、全任务铺开跑。成本会失控，噪声也会变大。

推荐规模：

| 批次 | 模型数 | 任务数 | 轮次 | 用途 |
| --- | ---: | ---: | ---: | --- |
| 第一批 | 4-6 | 3-4 | 1 轮，争议项复跑 | 筛选 |
| 第二批 | 2-3 | 2 | 1 轮 | 复核 |
| 第三批 | 1-2 | 1-2 | 1 轮 | 真改代码验证 |

进入第二批的建议门槛：

- P0 Recall >= 0.85
- Quality >= 12/15
- 没有连续 provider / harness 失败
- 至少一个复杂任务边界命中表现好
- 成本没有超过同批中位数 2 倍，除非它的召回明显更强

## 输出不要只做排行榜

最终结果应输出模型画像，而不是单一总分：

| 维度 | 例子 |
| --- | --- |
| 上下文召回 | 强 / 中 / 弱 |
| 语义入口 | 强 / 中 / 弱 |
| 工具调用稳定性 | 稳 / 偶发错 / 不可用 |
| 边界意识 | migration / generated / tests / auth |
| 输出质量 | 分析型强 / 执行型强 / 啰嗦 |
| 成本效率 | 高成本 / 中等 / 便宜 |
| 适合用途 | 主力 agent / 辅助分析 / 低成本批处理 / 不建议 |

## 使用流程

1. 为目标项目写任务文件，参考 [templates/task.analysis-only.template.json](templates/task.analysis-only.template.json)。
2. 用 [prompts/analysis-only-system.md](prompts/analysis-only-system.md) 作为 analysis-only 任务系统提示。
3. 按 [runbook.md](runbook.md) 固定项目 commit、工具组、输出目录和复跑规则。
4. 用 [scripts/score-analysis-output.ps1](scripts/score-analysis-output.ps1) 生成单次 run 的 score JSON。
5. 用 [templates/manual-review.template.md](templates/manual-review.template.md) 记录人工 15 分和扣分依据。
6. 用 [scripts/summarize-runs.ps1](scripts/summarize-runs.ps1) 汇总一批 run。
7. 用 [templates/run-report.template.md](templates/run-report.template.md) 和 [templates/model-scorecard.template.md](templates/model-scorecard.template.md) 形成报告和模型画像。
8. 根据 [methodology.md](methodology.md) 的晋级规则决定是否进入下一批。

## 基础命令

校验任务文件：

```powershell
.\benchmarks\model-agent\scripts\validate-task.ps1 `
  -TaskPath .\benchmarks\model-agent\tasks\papermark\link-source-analytics.json
```

对某次 analysis-only 输出做机器评分：

```powershell
.\benchmarks\model-agent\scripts\score-analysis-output.ps1 `
  -TaskPath .\benchmarks\model-agent\tasks\papermark\link-source-analytics.json `
  -OutputPath E:\agent\model-agent-benchmark\outputs\MODEL-link-source-analytics.md `
  -Model "GLM-5.1" `
  -AgentFramework "Claude Code" `
  -ToolGroup "normal-tools" `
  -Status completed `
  -DurationSeconds 120.5 `
  -CostUsd 1.2345
```

脚本只负责机器可判定部分，例如 P0 Recall、Overall Recall、misses、boundary hits。人工质量分仍按 [rubric.md](rubric.md) 记录。

汇总一批 score JSON：

```powershell
.\benchmarks\model-agent\scripts\summarize-runs.ps1 `
  -RunPath .\benchmarks\model-agent\runs\20260609-papermark-phase1\scored
```

校验单个 score JSON：

```powershell
.\benchmarks\model-agent\scripts\validate-run-result.ps1 `
  -RunResultPath .\benchmarks\model-agent\runs\20260609-papermark-phase1\scored\glm-5.1-normal-papermark-link-source-analytics-r1.score.json
```

`runs/` 默认忽略本地输出。需要长期保存的研究结论，建议整理成 `docs/` 下的报告，而不是直接提交原始日志。

## 第一批任务包

当前内置 Papermark 第一批任务：

| Task | 目的 |
| --- | --- |
| `papermark-link-source-analytics` | 测 link/source 字段流转、analytics ingestion、analytics UI、Prisma/migration 边界 |
| `papermark-dataroom-permission-chain` | 测 data room 权限链路、后端 API、group permissions、前端可见性 |
| `papermark-dataroom-notification-preference` | 测 notification preference、settings UI、API、async email job、validation/migration |

这些任务 pinned 到 Papermark commit `cd374a9aa8639e46c8490e39dc4c2fcaf4092caa`。第一次正式跑完后，应根据真实模型输出和人工复核微调 P1/P2，而不是改动 P0 口径来迁就模型。

## 关键原则

MCP 本身只是工具，不会主动调用——触发条件必须写进 prompt / `CLAUDE.md` / skill。`rg` 是强基线，不应拿 Not ACE 和”瞎找”对比。每个 expected file 必须有 `reason`，否则 P0/P1/P2 口径会漂移。provider error、timeout、invalid output 不算模型能力分，但计入稳定性。真改代码只给进入最终阶段的模型做。第一批只能形成候选画像和失误模式，跨项目稳定结论至少需要第二批复核。
