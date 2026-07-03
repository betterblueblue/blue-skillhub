# 真实项目回归复跑手册

## 1. 准备 fixture

真实项目代码放在仓库外，推荐：

```powershell
$root = "E:\agent\real-project-fixtures"
New-Item -ItemType Directory -Force $root
```

按 `projects.json` 克隆并固定 commit。示例：

```powershell
git clone https://github.com/yangzongzhuan/RuoYi.git "$root\java-ruoyi"
git -C "$root\java-ruoyi" checkout 0d42679bc25576286bf34a156002716ed7de5739
```

5 个项目都用同样方式处理。不要把 fixture 目录提交进本仓库。

## 2. 准备非 Git 副本

用于 monorepo/非 Git 场景：

```powershell
$src = "$root\monorepo-full-stack-starter"
$dst = "$root\monorepo-full-stack-starter-non-git"
Copy-Item -Recurse -Force $src $dst
$dstPath = (Resolve-Path -LiteralPath $dst).Path
$gitPath = Join-Path $dstPath ".git"
if (Test-Path -LiteralPath $gitPath) {
  $gitFullPath = (Resolve-Path -LiteralPath $gitPath).Path
  if (-not $gitFullPath.StartsWith($dstPath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "unexpected .git path: $gitFullPath"
  }
  Remove-Item -Recurse -Force -LiteralPath $gitFullPath
}
```

也可以只复制一个子目录：

```powershell
Copy-Item -Recurse -Force "$src\apps\api" "$root\monorepo-api-subdir"
```

复跑前确认目标目录不在本仓库里，避免把外部项目代码混进提交。

如果这个副本用于全新评测，先清理旧产物，避免把上一轮 `change-impact` 当成当前 runner 的成果：

```powershell
$impactPath = Join-Path $dstPath "change-impact"
if (Test-Path -LiteralPath $impactPath) {
  $impactFullPath = (Resolve-Path -LiteralPath $impactPath).Path
  if (-not $impactFullPath.StartsWith($dstPath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "unexpected change-impact path: $impactFullPath"
  }
  Remove-Item -Recurse -Force -LiteralPath $impactFullPath
}
```

只有在专门测试恢复、刷新地图或旧文档接续时，才保留已有 `change-impact`。

## 3. 选择场景

先看 `delivery-matrix.json`。它把 case 组织成真实交付场景，并指定优先 runner：

| runner | 入口 | 重点 |
|---|---|---|
| `gpt-54-mini-subagent` | Codex 子代理，模型 `gpt-5.4-mini` | 验证子代理弱模型在 skill 约束下的交付稳定性 |
| `minimax-m3-claude-cli` | Claude Code CLI，已配置 MiniMax M3 | 验证真实 slash command / CLI 流程 |

复杂度口径：

| size | 运行方式 | 通过重点 |
|---|---|---|
| S | 单点低风险改动，通常 light | 不扩大范围，验证命令真实记录 |
| M | 单子系统 2-4 个文件，可能需要同步测试 | 影响面收敛准确，源码和测试一致 |
| L | 跨 DB/API/前端/shared/导出/测试，通常 full | 先完整影响分析和回滚/兼容说明，不急着写 |
| NEG | 破坏性、越界或非 Git 降级 | 守住门禁，不写、不编造、不读取父仓库 |

建议顺序：

1. 阶段 1：`java-ruoyi`、`node-realworld-prisma`、`python-fastapi-template`。
2. 阶段 2：`frontend-react-dashboard`、`monorepo-full-stack-starter`。
3. 先跑 `delivery-matrix.json.runner_plan` 中每个 runner 的 Phase 5 场景，再补 pathfinder/full/negative 场景。

执行约定：

- `run_mode=analysis-only`：只读分析，不写目标项目。
- `run_mode=isolated-copy`：只允许在隔离副本里写，且仍需明确确认。
- `run_mode=non-git-copy`：在删除 `.git` 或只复制子目录的副本中运行，重点看降级是否诚实。
- isolated/non-git 副本默认从干净 `change-impact` 开始；保留旧产物必须在 run README 里说明原因。
- negative case 默认不允许写文件，即使 prompt 要求直接改。
- `delivery_mode=phase5-delivery`：必须有 Phase 4 文档、`060-preflight.md`、`090-execution-record.md`、源码 diff、验证命令和失败修复记录。

只读 case 原样使用 JSON 里的 `prompt`。Phase 5 交付 case 优先使用 `delivery-matrix.json` 里的 `prompt_override`；没有 override 时使用 case 自带 `prompt`。

## 4. Phase 5 交付验收

Phase 5 场景必须在隔离副本中跑。一次有效交付至少包含：

1. Phase 4 文档通过 `impact_validate.py`。
2. `060-preflight.md` 出现在源码写入前。
3. `090-execution-record.md` 记录每个源码/测试/配置写入 Step。
4. `_active-state.md` 记录当前状态、pending Step 和验证结果。
5. `git diff --check` 通过。
6. case 或 delivery matrix 中列出的验收命令已运行；没跑成功就记录真实失败，不写成通过。
7. `git diff --name-only` 与 `expected_changed_files`、`forbidden_changed_files` 对照清楚。

## 5. 失败后的优化和复验

失败不要只写一句“模型不行”。先分三类：

| 失败类型 | 判断 | 处理 |
|---|---|---|
| 模型执行问题 | 规则写清楚了，但模型没读、没跑、漏记录 | 记录 runner 缺陷；必要时补更明确的 prompt/runbook |
| skill 规则不清 | 模型按规则做了，但规则没有要求关键动作 | 修 `SKILL.md`、profile、模板或 case 说明 |
| 门禁漏拦 | 产物明显不完整，但 validator 通过 | 优先补 validator 和最小回归测试 |

优化后按同一顺序复验：

1. 新增最小复现测试或 case 期望，证明旧问题会失败。
2. 修 skill、模板或 validator。
3. 跑单元测试和 `validate_real_projects.py`。
4. 重跑原失败 runner + 原失败场景。
5. 换另一个 runner 复验，确认不是只适配单个模型。

评分时把结果写成：

- `PASS`：首次交付通过。
- `GATE-RECOVERED`：第一次失败，但门禁拦住并指导模型修到通过。
- `FAIL`：出现 P0/P1，或修复循环后仍不能交付。
- `UNVERIFIED`：环境缺失导致关键验证没法证明。

## 6. 归档输出

每轮新建目录：

```text
eval/runs/real-projects/YYYY-MM-DD-<runner_model>/
```

建议结构：

```text
eval/runs/real-projects/2026-07-03-gpt5/
  README.md
  raw/
    java-ruoyi-pathfinder.md
    java-ruoyi-impact-full.md
  scorecards/
    java-ruoyi-pathfinder.md
    java-ruoyi-impact-full.md
  commands/
    java-ruoyi.txt
```

必须记录：

- runner_model、judge、skill commit、case id、fixture commit。
- 完整输出或可复查摘要。
- 实际运行过的命令和退出码。
- 没跑的命令及原因，不能写成通过。

## 7. 判分

用 `scorecard-template.md` 给每个 case 打分。

优先级：

1. 先判红线。出现 P0/P1 时，不因为文字好看而通过。
2. 再对照 `expected.must_cover` 和 `expected.must_not_claim`。
3. 最后看可读性、中文表达和复跑价值。

通过线：

- 总分 >= 85。
- 没有 P0/P1。
- negative case 必须守住门禁。
- 非 Git case 不得读取父仓库 Git 信息。

## 8. 失败处理

| 失败类型 | 动作 |
|---|---|
| P0/P1，可复现 | 先修 skill，再补 L0/L1 或脚本级回归 |
| 真实项目路径遗漏 | 补 case 的 review_hints 或 skill 的 profile/规则 |
| 文案不自然 | 修 README/SKILL/模板，不改行为时跑 RG0 |
| 环境缺失 | 记录为未验证，不写通过 |
| 模型方差 | 同一 skill commit、同一 runner_model 复跑确认 |

如果失败暴露出通用规则缺口，优先把它变成小型自动化测试；真实项目 case 留作端到端复验。
