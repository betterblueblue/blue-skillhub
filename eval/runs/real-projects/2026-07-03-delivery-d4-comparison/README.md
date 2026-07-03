# D4 Phase 5 Delivery Comparison

本次对比只覆盖 `D4-frontend-dashboard-phase5`：把 React dashboard 侧边栏显示文案从 `Dashboard` 改成 `Insights`。这是一个安全、可回滚、但能暴露“半截改动”和“执行记录不完整”的 Phase 5 小场景。

## 结论

| runner | 最终状态 | 首次问题 | 门禁作用 | 最终验收 |
|---|---|---|---|---|
| `gpt-54-mini-subagent` | `GATE-RECOVERED` | 执行记录/状态文件曾出现一致性问题 | `impact_validate.py` 拦住后修复 | `18 passed / 0 failed / 0 warnings` |
| `minimax-m3-claude-cli` | `GATE-RECOVERED` | Step 1 未确认就写 Phase 4 文档；Step 5 首次 V15/V16 FAIL | Step 确认追认违规；V15/V16 拦住不完整记录 | `18 passed / 0 failed / 0 warnings` |

这说明 D4 不再只是测“能不能发现 label/title 半截改动”，而是在测真实交付链路：

- Phase 4 文档是否完整。
- Phase 5 是否先 preflight 再改源码。
- 源码 diff 是否只改期望文件。
- `090-execution-record.md` 与 `_active-state.md` 是否覆盖源码写入。
- validator 是否能把不完整交付拦住，并让弱模型修到通过。

## 关键发现

1. **V17 有效覆盖任务验收冒烟检查。**
   两个 runner 最终都同时修改了 `label` 和 `title`，没有复现旧的“只改 label”问题。

2. **V15/V16 暴露了真实交付问题。**
   两个 runner 都不是靠一次完美交付通过，而是经历了执行记录或状态文件修复。这个结果证明 Phase 5 门禁在真实 runner 中有价值。

3. **MiniMax M3 有 Step 纪律问题。**
   M3 在收到 `确认 Step 1` 前写入 Phase 4 文档。虽然后续被追认并如实记录，但最终判定不能算首次 PASS，只能算 `GATE-RECOVERED`。

4. **gpt-5.4-mini 的确认纪律更好，但执行流畅性一般。**
   它能在写文件前等待确认，Phase 4 也是 `18 passed / 0 failed / 0 warnings`；但中途需要主控追问才继续汇报下一步。

## 证据入口

- `eval/runs/real-projects/2026-07-03-gpt-54-mini-delivery-d4/README.md`
- `eval/runs/real-projects/2026-07-03-minimax-m3-delivery-d4/README.md`

## 下一步

继续跑 `D5-python-welcome-phase5`。D5 比 D4 多一个测试同步要求：不仅要改页面文案，还要同步 Playwright helper 中的断言。它能进一步验证弱模型是否会只改源码、漏测试。
