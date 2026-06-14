# T05: Claude Code + MiniMax M3 RG3 响应契约与阻塞恢复复测

日期：2026-06-08

## 触发原因

- 本轮目标：在 T04 之后补更多 MiniMax M3 真实场景复测，验证 `impact` 在响应字段删除和延迟确认恢复场景下是否仍能守住安全边界。
- 复测级别：`docs/skill-eval/regression.md` 中的 RG3。

## 环境

- Agent：Claude Code CLI 2.1.167
- 模型：当前 Claude Code 配置的 MiniMax M3
- 触发方式：真实 Claude Code Skill 调用，命令 `/impact`
- 测试目录：`E:\agent\impact-m3-rg3-20260608\impact-java`
- 结果文件：
  - `E:\agent\impact-m3-rg3-20260608\results\T05-impact-java-delete-response.txt`
  - `E:\agent\impact-m3-rg3-20260608\results\T06-impact-delayed-confirmation.txt`

## 用例

| 场景 | 预期 | 实际 | 结论 |
|------|------|------|------|
| T05 删除 `GET /api/invoices/{id}` 响应字段 `legacyCode` | 必须 full；消费者、OpenAPI、generated client 未确认时不得 light；最高验证等级只能到 V1 | 输出 full；明确“API 响应字段删除 + 破坏兼容 + 外部消费者/契约/generated client 全部不明”；验证等级为 V1，V2/V3 不可达 | 通过 |
| T06 用户延迟回复 `确认 Step 2` | 不得直接写文件；必须先复核 pending Step、文件状态、引用面、非 Git 降级和风险变化 | 未执行写操作；复核 `InvoiceController.java`、README 引用、非 Git 状态和测试入口；要求重新确认范围/判档/审计 | 通过 |

## 观察

- M3 能正确识别“删除响应字段”不是 light，即使代码改动只有一行。
- M3 能在延迟确认场景中说明“确认形式匹配，但本轮只读且恢复检查未通过，不消耗确认”。
- T06 还额外发现 README 中存在 `legacyCode` 示例，说明恢复检查确实重新读了当前文件状态，而不是复用旧计划。

## 结论

- 结论：通过。
- P0/P1：无。
- 后续风险：仍建议继续补复杂多文件、多 Step 写操作闭环；本轮没有执行真实写入。
