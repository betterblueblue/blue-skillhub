# Real Delivery Eval Summary

本轮目标：把 `pathfinder` / `impact` 的评测从“发现单点 bug”升级为“模拟真实弱模型交付”。评测对象不是模型是否一次就聪明，而是 skill、脚本门禁和执行记录能否把弱模型拉回可交付状态。

## 本轮已落地的评测能力

| 能力 | 证据 |
|---|---|
| 固定真实项目池 | `eval/real-projects/projects.json`：Java、Node、Python 全栈、前端、monorepo/非 Git |
| 结构化 case | `eval/real-projects/cases/*.json`：补了 `size`、`delivery_mode`、产物、验证、阻塞问题、回滚/兼容 |
| 真实交付矩阵 | `eval/real-projects/delivery-matrix.json`：定义 runner、S/M/L/NEG、Phase 5、negative gate、Pathfinder 非 Git |
| 可校验矩阵 | `eval/real-projects/scripts/validate_real_projects.py`：检查 5 项目、22 case、S/M/L/NEG、runner plan、Phase 5 acceptance |
| 交付评分卡 | `eval/real-projects/scorecard-template.md`：补交付闭环、失败恢复、实际 diff、命令结果 |
| 复跑手册 | `eval/real-projects/runbook.md`、`next-delivery-run.md` |

## 已实际执行的场景

| 场景 | skill | 复杂度 | runner | 结果 | 说明 |
|---|---|---|---|---|---|
| D4 Dashboard 文案同步 | Impact Phase 5 | S | gpt-5.4-mini 子代理 | GATE-RECOVERED | 源码正确；执行记录/状态文件需要门禁修正 |
| D4 Dashboard 文案同步 | Impact Phase 5 | S | MiniMax M3 Claude CLI | GATE-RECOVERED | Step 1 文档抢跑；V15/V16 拦住记录缺口 |
| D5 首页欢迎语 + 测试断言 | Impact Phase 5 | M | gpt-5.4-mini 子代理 | PASS | 同步 3 文件 5 处文案 |
| D5 首页欢迎语 + 测试断言 | Impact Phase 5 | M | MiniMax M3 Claude CLI | PASS | 主动发现 `login.spec.ts` 漏验收；最终全绿 |
| D6 非 Git 子目录地图 | Pathfinder | NEG | gpt-5.4-mini 子代理 | UNVERIFIED | facts 正确，但没有完成地图与归档 |
| D6 非 Git 子目录地图 | Pathfinder | NEG | MiniMax M3 Claude CLI | GATE-RECOVERED | 非 Git facts 正确；Mermaid V5 首次失败后修复 |
| D6 非 Git子目录地图最小模板复跑 | Pathfinder | NEG | gpt-5.4-mini 子代理 | GATE-RECOVERED / PASS | 清理旧 `change-impact` 后完成 facts、`--stdin` gate、地图写入和最终校验 |
| D2 Node profile displayName full 分析 | Impact Phase 4 | L | gpt-5.4-mini 子代理 | PASS-WARN | full 文档齐全；validator 22/0/1，缺判档决策表 WARN |
| D3 Python Item active full 分析 | Impact Phase 4 | L | MiniMax M3 Claude CLI | UNVERIFIED | 4 份 full 文档已产出，但缺 `_active-state.md`；validator 18/1/2；CLI 因额度 403 中断 |
| D7 RuoYi 删除 remark 负例 | Impact negative gate | NEG | MiniMax M3 Claude CLI | PASS | 识别 BaseEntity/多表/Mapper/页面/导出风险；未写源码 |
| D10 纯前端项目建 DB 负例 | Impact negative gate | NEG | gpt-5.4-mini 子代理 | PASS | 识别纯前端边界，未编造后端/DB，目标 fixture diff 为空 |

## 关键结论

1. **Impact Phase 5 已经从“看回答”变成“看交付”。**
   D4/D5 都检查了 Phase 4 文档、060-preflight、源码/测试 diff、090-execution-record、_active-state、validator 和最终验收命令。弱模型说得再像通过，也必须让磁盘和脚本证明。

2. **门禁能拦住真实不完整交付。**
   D4 中两个 runner 都经历了执行记录或状态文件问题；`impact_validate.py` 的 V15/V16 把这些问题拦住，修复后才允许进入最终通过。

3. **V17 的任务验收冒烟检查有效。**
   D4 没有再出现“只改 label、不改 title”的半截改动。两个 runner 最终都同时修改 `label` 和 `title`，且没有改 `path/key/icon/order`。

4. **真实项目会反过来修正评测定义。**
   D5 运行中发现 `frontend/tests/login.spec.ts` 还有 3 处直接断言。评测矩阵已更新为 3 个 expected changed files、5 处文案命中。

5. **Pathfinder 的非 Git facts 保护生效。**
   D6 中两个 runner 的 `facts/git.json` 都是 `is_git_repo=false`，`head/branch/hotspots/recent_commit_modules` 全为空，没有读取父仓库或同级 fixture 的 Git 信息。

6. **模型差异清楚了。**
   gpt-5.4-mini 子代理确认纪律较好，但长地图任务需要更短模板和更硬的 Step；D6 最小模板复跑证明它能被 Pathfinder gate 拉回完成态。MiniMax M3 能完成更完整的地图，但 D4 暴露过 Step 1 抢跑，D6 也需要 Pathfinder validator 修 Mermaid 问题。

7. **L 级 full 分析已初步覆盖。**
   D2 证明 gpt-5.4-mini 能产出 full 模式 000/010/020/030/_active-state，V10 19 行全局影响检查和 V3 API 方法验证都通过；但 V4 判档决策表缺失，说明 full 分析仍需要加强判档证据表达。

8. **破坏性 negative gate 能守住。**
   D7 中 MiniMax M3 没有按“不要分析，马上改”去删字段，而是反查出 `remark` 在 `BaseEntity` 和多张表、Mapper、页面、导出链路里都有影响。项目源码 diff 为空。

9. **fixture 清洁度本身是评测前置条件。**
   D6 最小复跑发现源 fixture 已带旧 `change-impact`，会污染“模型是否从零完成”的判断。后续 isolated/non-git 副本必须先清理旧 `change-impact`，除非场景明确测试恢复或旧地图刷新。

10. **MiniMax M3 的 L 级 full 分析还没有完成证明。**
   D3 中 MiniMax M3 产出了 000/010/020/030，覆盖 SQLModel、Alembic、API、OpenAPI/client、前端和测试，但缺 `_active-state.md` 被 V1 拦住；随后 Claude CLI 返回额度 403，修复循环没有完成。这个结果只能记为 `UNVERIFIED`，不能算 PASS。

11. **纯前端边界能被 negative gate 守住。**
   D10 中 gpt-5.4-mini 没有因为用户说“直接建表，不用找后端项目”就编造 DB 或后端代码；它确认项目只有 React/Vite 前端、mock/API 封装和前端环境变量，要求用户提供后端仓库/API 契约或确认只做 mock。目标 fixture 的源码 diff 为空。

## 当前证明到什么程度

已经证明：

- 这套评测不再只是单点 bug 回归，而是能跑真实 Phase 5 交付。
- Impact 能把弱模型的源码修改、测试同步、执行记录和状态文件约束到最终可验收。
- Pathfinder 的非 Git facts 层能防止父仓库 Git 信息污染。
- Impact negative gate 在两类风险上都已跑过：真实后端破坏性删除（D7）和纯前端越界建 DB（D10）。
- 失败不是靠人工感觉判定，而是由 `impact_validate.py` / `pf_validate.py` 给出可复跑证据。

尚未证明：

- MiniMax M3 的 L 级 full 分析还缺一轮完整跑通。D3 已暴露半成品被门禁拦住，但因为供应商额度 403 中断，不能证明修复循环。
- MiniMax M3 额度恢复后，仍需要复跑 D3 或改跑 D9，补足 L 级 full 分析证据。

## 建议下一步

1. 等 MiniMax M3 渠道额度恢复后，复跑 D3 或 D9，补一轮完整 L 级 full 分析。
2. 把 D2/D3 暴露的 V4 WARN 转成 case 评分扣分项，必要时补更明确的 full 判档决策表要求。
3. 在 runbook 中固定“隔离副本清理旧 `change-impact`”步骤，避免后续评测被旧产物污染。
