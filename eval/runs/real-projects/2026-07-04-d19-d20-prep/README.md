# D19 / D20 交付前准备（2026-07-04）

Date: 2026-07-04  
Purpose: 为 `D19-node-tags-removal-phase5` 与 `D20-python-title-required-lazy-phase5` 创建双 runner 隔离副本，并在 node 副本上验证基线测试可绿。

## 前置核对（已完成）

| 检查项 | 结果 |
|---|---|
| 5 个原始 fixture commit ↔ `projects.json` | 一致 |
| 原始 fixture 源码 diff | 空 |
| 原始 fixture 残留 `change-impact/` | 已清 |
| D19 基线测试策略 | `tests/prisma-mock.ts` mock，无需真 DB；`npm test` = `jest -i` |

## 隔离副本

| 场景 | Runner | 副本路径 | Commit |
|---|---|---|---|
| D19 | `gpt-54-mini-subagent` | `E:\agent\real-project-fixtures-delivery\node-realworld-prisma-gpt54mini-d19-20260704` | `6ac99ea5aeadc4e001dd4d6933c2e269f878a969` |
| D19 | `minimax-m3-claude-cli` | `E:\agent\real-project-fixtures-delivery\node-realworld-prisma-minimax-m3-d19-20260704` | `6ac99ea5aeadc4e001dd4d6933c2e269f878a969` |
| D20 | `gpt-54-mini-subagent` | `E:\agent\real-project-fixtures-delivery\python-fastapi-template-gpt54mini-d20-20260704` | `3685fb66259fa12f8436ae7f88379fd64ca7cdbd` |
| D20 | `minimax-m3-claude-cli` | `E:\agent\real-project-fixtures-delivery\python-fastapi-template-minimax-m3-d20-20260704` | `3685fb66259fa12f8436ae7f88379fd64ca7cdbd` |

副本创建方式：从 `E:\agent\real-project-fixtures\` 原始 fixture 递归复制到 `real-project-fixtures-delivery\`，复制后确认无 `change-impact/`。

## Node 基线测试（D19 副本）

两个 node 副本均执行 `npm ci && npm test`，结果一致：

| 副本 | `npm ci` | `npm test` | 摘要 |
|---|---|---|---|
| gpt54mini-d19 | 0 | 0 | 5 suites passed；26 passed + 1 todo（`tag.service.test.ts`） |
| minimax-m3-d19 | 0 | 0 | 同上 |

详细输出见 `commands/node-baseline-d19.txt`。

基线结论：**基线可绿，D19 交付后 `npm test` 验收风险低。** tag 相关测试基本是 `test.todo`，删除 tags 功能后需关注 runner 是否误删 favorites 相关断言。

## 下一步（正式跑分）

启动 prompt 见 [`prompts/`](prompts/README.md)（4 份 `.txt` 可直接粘贴）。

1. 分别在 4 个副本目录启动对应 runner，使用 `delivery-matrix.json` 里的 `prompt_override`（或直接用 `prompts/*.txt`）。
2. Phase 5 写操作按 runbook 确认协议逐条回复 `确认 Step N`，不预授权。
3. 完成后跑 `check_delivery.py` 和矩阵 `acceptance.validators`。
4. 结果写入 `eval/runs/real-projects/2026-07-04-*-delivery-d19/` 与 `...-d20/`。

## 关联：执法覆盖率审计待办

见 `docs/enforcement-coverage-audit-2026-07-04.md`：

- **Validator 队列 N-A~N-E**（尚未实现，按性价比排序给后续实现）
- **Eval 零覆盖场景**（建议新增第 9/10 类 `scenario_type`）：
  - `injection-trap`：仓内文本注入（P3D 有部分覆盖，real-projects 矩阵零覆盖）
  - `resume`：阻塞恢复两段式 case（impact 规则 #6 基础设施在，矩阵无场景）
