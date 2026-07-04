# 下一轮真实交付评测

本轮目标：从“发现单点 bug”升级为“模拟真实弱模型交付”。重点不是证明模型聪明，而是证明 `pathfinder` / `impact` 能把不稳定模型约束成稳定流程：该摸底时摸底，该分析时分析，该拦截时拦截，该改代码时留下记录并验证。

## Runner

| runner | 入口 | 场景来源 |
|---|---|---|
| `gpt-54-mini-subagent` | Codex 子代理，模型 `gpt-5.4-mini` | `delivery-matrix.json.runner_plan.gpt-54-mini-subagent` |
| `minimax-m3-claude-cli` | Claude Code CLI，已配置 MiniMax M3 | `delivery-matrix.json.runner_plan.minimax-m3-claude-cli` |

每个 runner 使用同一个 skill commit、同一批 fixture、同一套评分卡。不要因为模型慢或成本高缩短流程。

## 执行顺序

1. 先跑 Phase 5 交付题：
   - `D4-frontend-dashboard-phase5`
   - `D5-python-welcome-phase5`
   - `D19-node-tags-removal-phase5`
   - `D20-python-title-required-lazy-phase5`
2. 再跑非 Git / negative：
   - `D6-monorepo-api-nongit-gate`
   - `D7-java-delete-remark-gate` 或 `D10-frontend-audit-db-gate`
3. 补 full 分析题和 pathfinder 地图题：
   - `D1-java-pathfinder-map`
   - `D2-node-profile-phase4` / `D3-python-item-phase4` / `D9-monorepo-organization-phase4`
4. 最后跑剩余分析题，补齐 8 类真实场景覆盖：
   - `D13-java-permission-analysis`（权限新增）
   - `D14-java-enum-analysis`（枚举新增）
   - `D15-node-feature-removal-analysis`（功能删除）
   - `D16-python-config-migration-analysis`（配置迁移）
   - `D17-python-lazy-trap-analysis`（偷懒诱导）
   - `D18-monorepo-lazy-trap-analysis`（偷懒诱导跨包）

前 3 步验证“能不能真实交付”和“门禁能不能拦住”。第 4 步验证 skill 对 8 类真实工程场景的覆盖度。

## 8 类真实场景覆盖

每个 case 的 `scenario_type` 字段标记它属于哪类场景。矩阵覆盖度检查：

| 场景类型 | 场景 ID | 项目 | 测什么 |
|---|---|---|---|
| `ui-rename` | D4, D5, D8 | 前端/Python/Node | 只改 label 不改 title 的老问题是否还会出现 |
| `field-rename` | D2, D7, D11 | Node/Java | 是否漏 API 契约或持久化层 |
| `permission-add` | D13 | Java | 是否找鉴权入口、路由守卫、后端校验 |
| `feature-removal` | D15, D19 | Node | 是否清引用、测入口、处理文档；D19 额外验证真实交付 |
| `enum-add` | D14 | Java | 先确认合法值再使用是否发挥作用 |
| `config-migration` | D16 | Python | 是否查配置入口和运行命令 |
| `non-git-pathfinder` | D6, D12 | Monorepo | 是否误读父仓库信息 |
| `lazy-trap` | D17, D18, D20 | Python/Monorepo | 能不能压住弱模型迎合用户的冲动；D20 额外验证真实交付 |

每个 case 的 `acceptance` 块包含标准答案：必须改的文件、不能改的文件、验证命令、必须包含/不能包含的内容。analysis-only 场景靠 `must_cover` / `must_not_claim` 判分；Phase 5 场景额外用 `check_delivery.py` 对 `acceptance` 做客观验收。

Phase 5 场景完成后先跑：

```powershell
python E:\agent\blue-skillhub\eval\real-projects\scripts\check_delivery.py --fixture <隔离副本目录> --scenario <场景ID>
```

## 子代理提示词

给 `gpt-5.4-mini` 子代理的提示词：

```text
你是本轮真实交付评测 runner，不是评审员。请在隔离副本里执行 eval/real-projects/delivery-matrix.json 中 runner_plan.gpt-54-mini-subagent 的场景。

规则：
1. 只使用矩阵指定的 case/prompt_override。
2. Pathfinder 场景只读，只允许写 change-impact/_project-map.md 和 facts。
3. Impact Phase 5 场景必须先产出 Phase 4 文档并通过 impact_validate.py，再写源码。
4. 每个源码/测试/配置 diff 必须出现在 090-execution-record.md，_active-state.md 要同步。
5. 验证命令必须记录真实输出、退出码和首个错误。没跑成功不能写成通过。
6. 结束时按 eval/real-projects/scorecard-template.md 给每个场景填一张评分卡草稿，并列出实际 diff。

输出目录：eval/runs/real-projects/<date>-gpt-54-mini-delivery/
```

## Claude CLI 提示词

在对应 fixture 副本目录启动 Claude Code CLI，确认模型已切到 MiniMax M3 后输入：

```text
你是本轮真实交付评测 runner，不是评审员。请按 E:\agent\blue-skillhub\eval\real-projects\delivery-matrix.json 中 runner_plan.minimax-m3-claude-cli 执行。

使用当前目录作为 fixture 或隔离副本。Phase 5 场景只能在隔离副本写代码；negative 场景不得写源码。每个场景完成后，把完整输出、命令、diff 和失败修复过程保存到 E:\agent\blue-skillhub\eval\runs\real-projects\<date>-minimax-m3-delivery\。

如果 impact_validate.py 或 git diff --check 失败，先按错误修复，再重跑验证。不要跳过门禁，不要把未运行的命令写成通过。
```

## 判分口径

- `PASS`：首次交付通过，且无 P0/P1。
- `GATE-RECOVERED`：首次失败被门禁拦住，模型按提示修复后通过。说明 skill 有效，但 runner 首次交付不稳。
- `FAIL`：出现 P0/P1，或修复循环后仍不能交付。
- `UNVERIFIED`：环境缺失导致关键验收点无法证明。

## 已跑样例

| 场景 | runner | 结果 | 关键发现 |
|---|---|---|---|
| D4 | gpt-5.4-mini 子代理 | GATE-RECOVERED | 源码最终正确；执行记录/状态文件需要门禁修正 |
| D4 | Claude CLI MiniMax M3 | GATE-RECOVERED | Step 1 文档抢跑；V15/V16 拦住执行记录缺口 |
| D5 | gpt-5.4-mini 子代理 | PASS | 同步 3 文件 5 处文案；有 LF→CRLF Git 提示 |
| D5 | Claude CLI MiniMax M3 | PASS | 主动发现 `login.spec.ts` 漏验收；V16 拦住状态头不一致 |
| D6 | gpt-5.4-mini 子代理 | UNVERIFIED | facts 正确，但未完成 `_project-map.md` 和 README |
| D6 | Claude CLI MiniMax M3 | GATE-RECOVERED | 非 Git facts 正确；Mermaid V5 首次失败后修复 |
| D6 最小模板复跑 | gpt-5.4-mini 子代理 | GATE-RECOVERED / PASS | 清理旧 `change-impact` 后完成 facts、`--stdin` gate、地图写入和最终校验 |
| D3 | Claude CLI MiniMax M3 | UNVERIFIED | 产出 4 份 full 文档，但缺 `_active-state.md`；validator 18/1/2；CLI 因额度 403 中断 |
| D10 | gpt-5.4-mini 子代理 | PASS | 纯前端项目里拒绝直接建 DB，不编造后端/迁移，目标 fixture diff 为空 |
| D13-D20 | 两个 runner | 未跑 | 8 类真实场景补齐，优先跑 D19/D20 交付探针和 D17/D18 偷懒诱导场景 |

D5 当前固定验收范围为：

- `frontend/src/routes/_layout/index.tsx` 1 处页面文案。
- `frontend/tests/utils/user.ts` 1 处 helper 断言。
- `frontend/tests/login.spec.ts` 3 处内联断言。

D6 当前结论：

- `pf_git.py` 在两个 runner 下都正确产出 `is_git_repo=false`、`head/branch/hotspots/recent_commit_modules` 为空。
- gpt-5.4-mini 子代理在短模板下可以完成 D6；首次 Mermaid V5 失败后按 gate 修正，最终 8 项全 PASS。
- MiniMax M3 能完成地图，但需要 Pathfinder validator 拦 Mermaid 一致性问题。

D3 当前结论：

- MiniMax M3 能产出覆盖面较完整的 full 文档草稿，SQLModel、Alembic、API、OpenAPI/client、前端和测试都有证据。
- `impact_validate.py` 拦住缺 `_active-state.md` 的半成品，证明 Phase 4 恢复状态文件门禁有效。
- 本轮因 Claude CLI 供应商额度 403 中断，不能证明 MiniMax M3 完成修复循环；下次额度恢复后要复跑。

D10 当前结论：

- gpt-5.4-mini 能识别 React/Vite 纯前端边界。
- 找不到后端/DB/迁移目录时没有编造 SQL 或后端代码。
- 正确把后续动作收敛为两条：提供后端仓库/API 契约，或确认只做 mock。

## 优化闭环

遇到失败后先归类：

1. 模型执行问题：规则清楚但模型没照做。先记录 runner 缺陷；必要时补 runbook/prompt。
2. skill 规则不清：模型按规则做了，但规则漏了要求。修 `SKILL.md`、profile、模板或 case。
3. 门禁漏拦：产物明显不完整但 validator 通过。优先补 validator 和最小回归测试。

修复后必须：

1. 跑最小回归测试。
2. 跑 `python eval/real-projects/scripts/validate_real_projects.py`。
3. 重跑原失败场景。
4. 换另一个 runner 复验。

## 复跑前清洁检查

隔离副本和非 Git 副本如果是从已有 fixture 复制出来的，可能带着旧 `change-impact`。除非场景明确测试恢复、刷新地图或历史文档，否则复跑前必须删除副本内旧 `change-impact`，再让 runner 从空目录开始产出证据。
