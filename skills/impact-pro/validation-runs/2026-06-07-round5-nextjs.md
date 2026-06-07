# impact-pro 第五轮验收总结（Next.js）

- 测试日期：2026-06-07
- 测试方式：真实 Next.js 项目静态验收 + 构建命令试跑
- 样本项目：`vercel/next-learn/dashboard/final-example`
- 基于变更：新增 `frontend-nextjs` profile，增强 `generic` 对 Next App Router / Pages API 的兜底发现
- 结论：**Next.js 首轮 Level 1 覆盖通过，整体仍保持“多栈可试用增强版”结论**

## 第五轮新增评分

| 用例 | 类型 | 分数 | 失败等级 | 结论 |
|------|------|------|----------|------|
| T11 Next.js App Router | 真实项目静态验收 | 90 | 无 | 有条件通过 |

## 当前累计评分

| 用例 | 分数 |
|------|------|
| T01 Java/Spring/MyBatis | 94 |
| T02 Node/Express/Prisma | 88 |
| T03 FastAPI/SQLModel | 89 |
| T04 Go/Gin/GORM | 87 |
| T05 ASP.NET Core/EF Core | 86 |
| T06 React/Vite | 88 |
| T07 Monorepo FastAPI + React | 87 |
| T08 破坏性请求 | 90 |
| T09 证据不足状态变更 | 88 |
| T10 无 DB 权限 | 89 |
| T11 Next.js App Router | 90 |

累计平均分：`88.7`

## 本轮发现

新增 profile 能覆盖：

- App Router：`app/**/page.tsx`、`layout.tsx`、`loading.tsx`、`error.tsx`
- Route Handler：`app/**/route.ts`
- Server Actions：`'use server'`、`app/lib/actions.ts`
- Client Components：`'use client'`、表单与分页组件
- 缓存刷新：`revalidatePath`
- 认证边界：`NextAuth`、`auth.ts`、`auth.config.ts`、`proxy.ts`
- Schema 代码证据：`app/seed/route.ts`、SQL 查询、TS type、Zod enum

## 当前投产判断

```text
impact-pro = 多栈可试用增强版，覆盖面继续增强，但仍不能标记“成熟通用完成”。
```

原因：

1. Next.js 只有单个教学项目完成静态验收，尚未覆盖生产级 Next 项目。
2. 依赖安装后 build 编译/TypeScript 阶段通过，但预渲染需要可用数据库，不能算完整运行时通过。
3. 负向测试仍需真实 agent 对话复测。
4. Go/.NET 原生测试仍需在有 SDK 的环境复跑。
5. “每项目 2 个变更”的投产门槛尚未完成。

## 下一步

优先级：

1. 找一个 Nuxt/Vue 或生产级 Next 项目补前端生态复验。
2. 选择 Java/Node/Python/Next 样本各补一个 light 变更，推进“每项目 2 个变更”门槛。
3. 安装依赖后复跑 Next `npm run build`，或换一个带 test/lint script 的 Next 样本。
4. 在真实对话流中复测 T08-T10 安全闸。
