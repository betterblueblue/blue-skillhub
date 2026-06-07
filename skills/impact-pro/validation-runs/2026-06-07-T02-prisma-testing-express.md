# T02 prisma-examples/testing-express - 用户显示名/取消原因类字段

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Node.js / TypeScript / Express / Prisma / PostgreSQL
- 项目路径：`E:\agent\impact-pro-validation-work\prisma-examples\orm\testing-express`
- Commit：`663c23ca1a6c6f03d2ad0c67868020b560a172e4`
- 变更意图：给实体增加一个业务字段，并在创建接口和查询接口返回。
- 使用档位：full
- 命中 profile：`generic`
- 最终评分：66
- 失败等级：P1

## 实际发现

### 栈探测

可识别证据：

- `package.json` 存在。
- 依赖包含 `express`、`@prisma/client`、`prisma`、`@prisma/adapter-pg`。
- 存在 `prisma/schema.prisma` 和 `prisma.config.ts`。

当前 `impact-pro` 没有 Node/Express/Prisma 专属 profile，因此会加载 `generic`。

### 上下文发现

真实关键文件：

- `package.json`
- `prisma/schema.prisma`
- `prisma.config.ts`
- `src/app.ts`
- `src/index.ts`
- `tests/user.test.ts`

但当前 `generic` glob 实测只能稳定命中：

- `tests/user.test.ts`

当前 `generic` 没有命中：

- `prisma/schema.prisma`
- `prisma.config.ts`
- `src/app.ts`
- `src/index.ts`

关键证据：

- `prisma/schema.prisma` 定义 `User` 模型：`id`、`name`、`email @unique`。
- `src/app.ts` 定义 `GET /user` 和 `POST /user`。
- `tests/user.test.ts` 覆盖成功创建、重复 email 409、用户列表返回。

### 风险追问

如果上下文能被正确发现，应追问：

1. 新字段是否必填，默认值如何处理？
2. 是否需要修改 Prisma migration？
3. `POST /user` 是否接收该字段，`GET /user` 是否返回？
4. 是否需要错误用例覆盖空值、过长、重复或格式错误？

但由于当前 glob 漏掉 schema 和 API 入口，`impact-pro` 很可能无法基于证据提出这些问题。

### 判档

正确判档应为 full。

理由：

- Prisma schema 变更。
- Express API 输入/输出变更。
- 测试用例需要同步更新。

当前规则在证据不足情况下可能误判 light，这是 P1 风险。

## 评分

| 维度 | 分值 | 得分 | 说明 |
|------|------|------|------|
| 栈探测与 profile 选择 | 15 | 12 | 能识别 package，但无专属 profile |
| 上下文发现 | 20 | 7 | 漏掉 schema 和 API 入口 |
| 风险识别与追问 | 20 | 10 | 规则有方向，但缺证据支撑 |
| light/full 判档 | 10 | 7 | 理论可判 full，实际证据不足 |
| 文档质量 | 15 | 10 | 可写草案，但关键文件不可靠 |
| 执行安全 | 10 | 10 | 写操作确认规则存在 |
| 验证设计 | 10 | 10 | 现有测试明显，可补 API 用例 |

合计：66。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P1 | generic 漏掉 Prisma schema | `prisma/schema.prisma` 不在 discovery_globs | 新增 `node-express-prisma` profile |
| P1 | generic 漏掉 Express API 入口 | `src/app.ts` 不匹配 `**/api/**/*.ts` 或 `**/routes/*.ts` | 增加 `src/app.ts`、`src/server.ts`、`src/index.ts`、`src/routes/**/*.ts` |
| P2 | migration 发现不支持 Prisma | `prisma.config.ts` 声明 migration path | 增加 Prisma config 和 migrations glob |

## 结论

不通过。当前 `impact-pro` 不能可靠用于 Node/Express/Prisma 项目。
