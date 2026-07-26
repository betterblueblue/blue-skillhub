# 环境兼容说明

> 说明 Pathfinder 与 ImpactRadar 在不同 AI 客户端下的已验证程度和边界。依据：真实项目评测记录（`eval/real-projects/`）、逃逸清单（`eval/real-projects/escape-ledger.md`）与评测手册（`eval/real-projects/runbook.md`）。

## 结论表

| 运行环境 | 已验证程度 | 写前门禁（impact-write-gate hook） | 建议用途 |
|---|---|---|---|
| Claude Code（交互式） | 评测主环境，验证最充分 | 可用，推荐启用（复制 hooks + 根目录放 `.impact-protected`） | 全流程，含 Phase 5 实施 |
| Claude Code CLI（无人值守 / headless） | 有正式评测数据（`minimax-m3-claude-cli` runner） | hook 依赖"最新用户消息为 `确认 Step N`"，无人值守时确认协议须由编排层扮演 | 分析类场景；实施类须编排层严格执行确认协议 |
| Codex 子代理（无人值守） | 有正式评测数据（`gpt-54-mini-subagent`、`composer-25fast-subagent`），**裸跑不受写前 hook 保护** | 不可用——hook 是 Claude Code 机制 | 分析类场景可用；**Phase 5 实施不得裸跑**，评测中此类 runner 标记为 `subagent-unattended-stress-only`，仅作压力测试 |
| 其他 MCP 客户端（Cursor 等） | 本仓库评测未覆盖其交互式运行 | 不可用 | skill 文档与流程兼容，但验证程度未知；重要变更前先用小任务试用 |

## 关键边界（如实披露）

1. **Codex 裸跑无写前 hook**：只能靠事后 `check_delivery` 归因，不能在工具执行前拦截未授权写入。这是逃逸清单记录的已知边界，属于环境属性，不是待修缺陷。
2. **hook 不是沙箱**：数据库写入的真正防线是只读账号、settings deny 和外部权限控制。
3. **确认协议是双层约束**：skill 文字要求 `确认 Step N`（所有环境生效）；hook 把它补强为工具执行前检查（仅 Claude Code）。
4. **评测结论只代表当时的模型版本与场景**：各 runner 的逐场景表现见 `eval/real-projects/model-support-matrix.md`，不构成长期模型排名。
