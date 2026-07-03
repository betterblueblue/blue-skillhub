# D5 Phase 5 Delivery Comparison

本次对比覆盖 `D5-python-welcome-phase5`：把 FastAPI 全栈模板前端首页欢迎语改为 `Welcome back. Good to see you again.`，并同步所有直接断言该文案的前端测试。

## 场景修正

运行中发现原 D5 验收漏掉 `frontend/tests/login.spec.ts`。真实源码里旧欢迎语共有 5 处：

| 文件 | 命中数 |
|---|---:|
| `frontend/src/routes/_layout/index.tsx` | 1 |
| `frontend/tests/utils/user.ts` | 1 |
| `frontend/tests/login.spec.ts` | 3 |

因此已把 `delivery-matrix.json` 和 `python-fastapi-template.json` 更新为 3 个 expected changed files。这个发现本身就是 D5 的价值：真实交付题不能只靠预设答案，runner 的只读发现也会反过来修正评测场景。

## 结论

| runner | 最终状态 | 首次问题 | 门禁作用 | 最终验收 |
|---|---|---|---|---|
| `gpt-54-mini-subagent` | `PASS` | 需要主控追问才返回 Phase 4 状态；无越权写入 | Step 确认和 validator 全程约束住范围 | `18 passed / 0 failed / 0 warnings` |
| `minimax-m3-claude-cli` | `PASS` | Step 1 首次 V16 状态头不一致；报告里曾把 5 处命中写成 4 处 | V16 拦住状态不一致；主控纠正计数后继续 | `18 passed / 0 failed / 0 warnings` |

## 交付结果

两个 runner 最终都完成了：

- 修改 `frontend/src/routes/_layout/index.tsx` 1 处页面文案。
- 修改 `frontend/tests/utils/user.ts` 1 处 helper 断言。
- 修改 `frontend/tests/login.spec.ts` 3 处内联断言。
- 未修改 `backend/app/models.py`、`backend/app/api/routes/login.py`、`frontend/src/client/types.gen.ts`、`frontend/src/client/sdk.gen.ts`。
- `impact_validate.py --mode light` 最终均为 `18 passed / 0 failed / 0 warnings`。

## 模型差异

`gpt-5.4-mini` 的优点是确认纪律稳定，Phase 4 和最终验收都比较干净；缺点是中途需要主控追问状态，自动推进的流畅性一般。

MiniMax M3 的优点是会主动指出 `login.spec.ts` 这个验收缺口，并把用户修正后的范围写进后续文档；缺点是 Step 1 首次 `_active-state.md` 状态不一致，需要 validator 拦一下，且口头报告有一次计数错误。

## 证据入口

- `eval/runs/real-projects/2026-07-03-gpt-54-mini-delivery-d5/README.md`
- `eval/runs/real-projects/2026-07-03-minimax-m3-delivery-d5/README.md`

## 下一步

继续跑 negative / non-Git 场景，优先 `D6-monorepo-api-nongit-gate`。D4/D5 已经证明 Phase 5 小交付可以被门禁拉到最终可交付；下一步要验证 Pathfinder 非 Git 降级和越界拦截是否同样稳定。
