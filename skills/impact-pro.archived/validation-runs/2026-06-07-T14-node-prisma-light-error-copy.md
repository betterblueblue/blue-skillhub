# T14 prisma-examples/testing-express - 重复用户错误文案调整

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Node.js / TypeScript / Express / Prisma
- 项目路径：`E:\agent\impact-pro-validation-work\prisma-examples\orm\testing-express`
- 变更意图：将重复邮箱创建用户时的错误文案从 `User already exists!` 调整为更明确的提示。
- 使用档位：light
- 命中 profile：`node-express-prisma`
- 最终评分：90
- 失败等级：无

## 实际发现

关键文件：

- `src/app.ts`：`POST /user` 捕获 Prisma create 错误后返回 `409` 和 `{ error: 'User already exists!' }`。
- `tests/user.test.ts`：重复创建用户测试断言状态码 `409` 和错误文案。
- `package.json`：`test` 命令为 Jest + Supertest。
- `prisma/schema.prisma`：用户唯一性约束来源，但本变更不需要改 schema。

## 验收判断

应判定 light。

理由：

- 不新增字段、不改唯一约束、不改 Prisma migration。
- 只改 API 错误响应文案和对应测试断言。
- 需要提醒 API 消费者可能依赖精确错误文案，但不是 schema/API 结构破坏。

## 风险追问

1. 是否有前端或外部客户端依赖原始错误文案？
2. 是否只改 message，还是要引入稳定错误码？
3. 是否需要保持英文，还是支持本地化？

## 验证方案

- `pnpm/npm test` 或项目实际包管理器执行 Jest。
- 正向：首次创建用户仍返回 200。
- 错误：重复邮箱仍返回 409，新错误文案准确。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | 错误文案可能是外部契约 | `tests/user.test.ts` 断言精确字符串 | 文档标注 API 消费者兼容风险 |

## 结论

通过（light）。该用例补充 Node/Prisma 样本第二变更，验证 profile 能区分“Prisma schema 证据需要只读确认”和“无需迁移的 API 文案调整”。
