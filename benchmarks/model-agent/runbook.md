# Runbook

这份 runbook 用来保证每次评测都能复现。它关心的不是“怎么问得更聪明”，而是每个模型在同一套约束下怎么被公平比较。

## 1. 准备项目快照

每个 benchmark 项目必须固定 commit。

```powershell
git clone https://github.com/papermark/papermark E:\agent\model-agent-benchmark\repos\papermark
Set-Location E:\agent\model-agent-benchmark\repos\papermark
git checkout cd374a9aa8639e46c8490e39dc4c2fcaf4092caa
git rev-parse HEAD
```

任务文件里的 `project_root`、`repo_url`、`commit` 要和实际 checkout 对齐。

## 2. 跑 sanity

正式任务前先做最小检查：

- 模型能返回普通答案。
- agent 能读取文件。
- `rg` 能搜索。
- analysis-only 任务不会写文件。
- 如果要测试 Not ACE，确认 MCP 可见，并在 prompt 中明确要求“语义入口先用 Not ACE，再用 `rg` 验证”。

Sanity 失败只说明当前接入不可评分，不直接说明模型能力弱。

## 3. 统一运行方式

同一个任务至少保持这些条件一致：

- 同一项目 commit。
- 同一 task JSON。
- 同一 system prompt。
- 同一工具组定义。
- 每个 run 用新会话，避免前一个模型的上下文污染。
- analysis-only 阶段禁止写文件、装依赖、跑测试、跑 migration、联网。

工具组建议命名：

| Tool group | 含义 |
| --- | --- |
| `normal-tools` | `rg`、文件读取、目录列表、git |
| `not-ace` | 只额外接 Not ACE，仍允许 `rg` 验证 |
| `hybrid` | Not ACE、`rg`、框架专用工具都可用 |

## 4. 保存原始输出

建议命名：

```text
runs/
└── 20260609-papermark-phase1/
    ├── raw/
    │   └── glm-5.1-normal-papermark-link-source-analytics-r1.md
    ├── scored/
    │   └── glm-5.1-normal-papermark-link-source-analytics-r1.score.json
    └── summary.md
```

`raw/` 保存 agent final answer 和必要的人工记录。`scored/` 保存机器评分结果。成本、token、工具调用次数可以从 Claude Code / Codex 的统计或手工日志填入。

## 5. 机器评分

```powershell
.\benchmarks\model-agent\scripts\score-analysis-output.ps1 `
  -TaskPath .\benchmarks\model-agent\tasks\papermark\link-source-analytics.json `
  -OutputPath .\benchmarks\model-agent\runs\20260609-papermark-phase1\raw\glm-5.1-normal-papermark-link-source-analytics-r1.md `
  -RunId "20260609-glm51-normal-link-source-r1" `
  -Model "GLM-5.1" `
  -AgentFramework "Claude Code" `
  -ToolGroup "normal-tools" `
  -DurationSeconds 180 `
  -CostUsd 0.42 `
  -ToolCalls 12 `
  -SearchCalls 5 `
  -FileReads 7 `
  -AnalysisQuality 3 `
  -PlanCorrectness 3 `
  -VerificationCoverage 2 `
  -BoundaryAwareness 3 `
  -HallucinationControl 3 `
  > .\benchmarks\model-agent\runs\20260609-papermark-phase1\scored\glm-5.1-normal-papermark-link-source-analytics-r1.score.json
```

人工 15 分不要让被测模型自评。至少由人按 [rubric.md](rubric.md) 复核一次。

## 6. 汇总一批结果

```powershell
.\benchmarks\model-agent\scripts\summarize-runs.ps1 `
  -RunPath .\benchmarks\model-agent\runs\20260609-papermark-phase1\scored `
  -OutPath .\benchmarks\model-agent\runs\20260609-papermark-phase1\summary.md
```

需要给后续脚本消费时输出 JSON：

```powershell
.\benchmarks\model-agent\scripts\summarize-runs.ps1 `
  -RunPath .\benchmarks\model-agent\runs\20260609-papermark-phase1\scored `
  -Json
```

## 7. 晋级判断

第一批的目标是筛选，不是最终排名。

推荐处理：

- `enter`: 进入第二批复杂 workflow 任务。
- `hold`: 有价值但证据不足，争议任务复跑一次。
- `reject`: 暂停继续评测，除非接入方式或模型版本变化。

自动汇总脚本只给建议，不替代人工判断。最终结论必须同时看漏掉了哪些 P0 文件、是否编造、是否乱用工具、成本是否离谱。

## 8. 复跑原则

不要为了得到好看的分数无限复跑。

建议只在这些情况下复跑：

- 首轮 provider error、timeout、工具崩溃。
- 某个模型只差一个 P0，且输出质量明显接近门槛。
- 同一模型在同类任务表现波动很大，需要判断是否偶发。
- 任务本身 expected files 口径有问题，需要先修任务再整体重跑。
