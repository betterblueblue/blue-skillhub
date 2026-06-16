# T47: Claude Code + MiniMax M3 真实 /impact-pro 响应契约负向复测

日期：2026-06-08

## 目的

验证 `impact-pro` 在多栈项目中是否能正确处理 API 响应字段删除，尤其是：

- 不误判为 Java
- 正确识别 Node/Express
- 删除响应字段必须 full
- 消费者/OpenAPI/generated client 不明时不得 light
- 区分 V1 静态验证与 V3 运行时验证

## 环境

- Agent：Claude Code CLI 2.1.167
- 模型：当前 Claude Code 配置的 MiniMax M3
- 触发方式：真实 Claude Code Skill 调用，命令 `/impact-pro`
- 测试目录：`E:\agent\impact-m3-skill-test\node-api`
- 结果文件：`E:\agent\impact-m3-skill-test\results\T2-real-slash-impact-pro-node-delete-response.txt`

## 样本

Node fixture：

- `package.json`：含 `express` 依赖与 `node --test`
- `src/invoice.js`：`getInvoice` 返回 `{ id, amount, status, legacyCode }`
- `README.md`：声明 `GET /invoice` 返回 `legacyCode`

任务：删除 `GET /invoice` 的响应字段 `legacyCode`。

## 结果

| 检查项 | 预期 | 实际 |
|--------|------|------|
| 技术栈识别 | Node/Express，不得套 Java | 通过 |
| profile 选择 | Express 命中，Prisma 降级为未使用，generic 备用方案 | 通过 |
| 定级 | 删除响应字段必须 full | 通过 |
| 消费者不明 | 不得写“无影响”，必须写证据不足/待确认 | 通过 |
| 接口返回检查清单 | 列字段变化、消费者、文档、OpenAPI/SDK、验证项 | 通过 |
| 验证等级 | 静态搜索达到 V1，V3 未运行 | 通过 |
| Step 确认 | 只给待确认 Step，不写文件 | 通过 |

## 观察

MiniMax M3 在该场景表现稳定：没有把 Node 项目套用 Java/Spring/MyBatis，也没有把字段删除误判成 light。

它正确识别了：

- `src/invoice.js` 是响应构造点。
- `README.md` 是契约证据。
- 仓内没有 OpenAPI/SDK 不代表无影响，只能写“未确认/证据不足”。
- 当前最高验证等级是 V1，V3 需要真实 HTTP 请求。

## 结论

`impact-pro` 针对响应字段删除这一负向场景通过真实 `/impact-pro` + MiniMax M3 复测。该场景没有发现新的 P0/P1 问题。
