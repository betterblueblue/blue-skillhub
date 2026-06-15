# Frontend / Next.js Profile

> Level 1 — 在 `vercel/next-learn/dashboard/final-example` 上完成首轮静态验收。适用于 Next.js App Router / Pages Router 项目，覆盖 Server Components、Client Components、Route Handlers、Server Actions、NextAuth、缓存刷新和前端 UI 状态。

## 基本信息

```yaml
name: frontend-nextjs
level: 1
matchers:
  files:
    - package.json
    - next.config.js
    - next.config.mjs
    - next.config.ts
    - middleware.ts
    - proxy.ts
    - app/layout.tsx
    - pages/_app.tsx
  dependencies:
    - next
    - react
    - react-dom
    - next-auth
    - "@auth/core"
    - "@vercel/postgres"
    - postgres
    - prisma
    - zod
  directories:
    - app
    - pages
    - components
    - lib
    - public
    - styles
roles:
  - Next.js 应用
  - 前端 UI/交互层
  - 服务端渲染/API 边界
  - BFF/Server Actions 项目
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/app/lib/**/*.ts"
    - "**/app/lib/**/*.tsx"
    - "**/lib/**/*.ts"
    - "**/lib/**/*.tsx"
    - "**/server/**/*.ts"
    - "**/services/**/*.ts"
    - "**/app/**/actions.ts"
    - "**/app/**/actions.tsx"
    - "**/actions.ts"
    - "**/auth.ts"
    - "**/auth.config.ts"
  data_access:
    - "**/app/lib/data.ts"
    - "**/app/lib/db.ts"
    - "**/lib/data.ts"
    - "**/lib/db.ts"
    - "**/lib/prisma.ts"
    - "**/prisma/schema.prisma"
    - "**/drizzle.config.*"
    - "**/src/db/**/*.ts"
    - "**/app/**/route.ts"
  api:
    - "**/app/**/route.ts"
    - "**/app/**/route.tsx"
    - "**/pages/api/**/*.ts"
    - "**/pages/api/**/*.js"
    - "**/app/**/page.tsx"
    - "**/app/**/layout.tsx"
    - "**/app/**/loading.tsx"
    - "**/app/**/error.tsx"
    - "**/middleware.ts"
    - "**/proxy.ts"
    - "**/next.config.*"
  entity:
    - "**/app/lib/definitions.ts"
    - "**/app/lib/types.ts"
    - "**/lib/definitions.ts"
    - "**/lib/types.ts"
    - "**/types/**/*.ts"
    - "**/src/types/**/*.ts"
    - "**/prisma/schema.prisma"
  dto:
    - "**/app/lib/definitions.ts"
    - "**/lib/definitions.ts"
    - "**/types/**/*.ts"
    - "**/app/**/*schema*.ts"
    - "**/lib/**/*schema*.ts"
    - "**/app/**/*validation*.ts"
    - "**/lib/**/*validation*.ts"
  config:
    - "**/package.json"
    - "**/next.config.js"
    - "**/next.config.mjs"
    - "**/next.config.ts"
    - "**/tsconfig*.json"
    - "**/tailwind.config.*"
    - "**/postcss.config.*"
    - "**/playwright.config.*"
    - "**/vitest.config.*"
    - "**/.env.example"
    - "**/.env.local.example"
    - "**/auth.config.ts"
  test:
    - "**/__tests__/**/*.{ts,tsx,js,jsx}"
    - "**/*.test.ts"
    - "**/*.test.tsx"
    - "**/*.spec.ts"
    - "**/*.spec.tsx"
    - "**/tests/**/*.ts"
    - "**/tests/**/*.tsx"
    - "**/e2e/**/*.ts"
  migration:
    - "**/prisma/migrations/**/*"
    - "**/drizzle/**/*.sql"
    - "**/migrations/**/*.sql"
    - "**/app/**/seed/route.ts"
    - "**/app/seed/route.ts"
    - "**/seed.ts"
    - "**/scripts/seed*.ts"
  ui:
    - "**/app/**/*.tsx"
    - "**/components/**/*.tsx"
    - "**/src/components/**/*.tsx"
    - "**/app/ui/**/*.tsx"
    - "**/styles/**/*.css"
    - "**/app/**/*.css"
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "package.json"
    - "next.config.*"
    - "tsconfig*.json"
    - "middleware.ts"
    - "proxy.ts"
  entrypoints:
    - "**/app/**/page.tsx"
    - "**/app/**/layout.tsx"
    - "**/app/**/route.ts"
    - "**/pages/api/**/*.ts"
    - "**/pages/api/**/*.js"
    - "**/middleware.ts"
    - "**/proxy.ts"
  data_models:
    - "**/app/lib/definitions.ts"
    - "**/app/lib/types.ts"
    - "**/lib/definitions.ts"
    - "**/lib/types.ts"
    - "**/types/**/*.ts"
    - "**/prisma/schema.prisma"
    - "**/prisma/migrations/**/*"
    - "**/drizzle/**/*.sql"
  dependency_paths:
    - "**/app/lib/**/*.ts"
    - "**/app/lib/**/*.tsx"
    - "**/lib/**/*.ts"
    - "**/lib/**/*.tsx"
    - "**/server/**/*.ts"
    - "**/services/**/*.ts"
    - "**/app/**/actions.ts"
    - "**/app/**/actions.tsx"
    - "**/auth.ts"
    - "**/auth.config.ts"
  tests:
    - "**/__tests__/**/*.{ts,tsx,js,jsx}"
    - "**/*.test.ts"
    - "**/*.test.tsx"
    - "**/*.spec.ts"
    - "**/*.spec.tsx"
    - "**/tests/**/*.ts"
    - "**/tests/**/*.tsx"
    - "**/e2e/**/*.ts"
  configs:
    - "**/package.json"
    - "**/next.config.*"
    - "**/tsconfig*.json"
    - "**/tailwind.config.*"
    - "**/postcss.config.*"
    - "**/playwright.config.*"
    - "**/vitest.config.*"
    - "**/.env.example"
    - "**/.env.local.example"
    - "**/auth.config.ts"
  exclude_patterns:
    - "**/node_modules/**"
    - "**/.next/**"
    - "**/out/**"
    - "**/coverage/**"
```

## style_axes

> 下列是观察方向，结论必须运行时从项目文件现采。

| 轴 | 观察方向 |
|----|----------|
| naming | App Router 目录命名、页面/布局文件约定、组件 PascalCase、hook useXxx |
| layering | app/pages/components/lib/server/db/auth 的边界；Server Action 与 Client Component 分工 |
| orm | Prisma/Drizzle/postgres/@vercel/postgres/原生 SQL；无 ORM 时必须标注 schema 来源 |
| transaction | Server Action、Route Handler、SQL transaction、缓存刷新与 redirect 的顺序 |
| exception | error.tsx、not-found.tsx、Zod safeParse、NextAuth/AuthError、Route Handler status |
| logging | console.error、错误上报、Next.js runtime 日志 |
| api_response | Route Handler `Response.json`、Server Action state、Pages API handler response |
| dependency_injection | Provider、SessionProvider、ThemeProvider、auth 配置、middleware/proxy |
| cache | `revalidatePath`、`revalidateTag`、`fetch` cache、`unstable_noStore`、Suspense/loading |
| rendering_boundary | Server Component / Client Component / Server Action / Route Handler 边界 |
| styling | Tailwind、CSS Modules、global.css、设计系统组件 |

## commands

```yaml
commands:
  build: npm run build
  test: npm test
  dev: npm run dev
  lint: npm run lint
```

命令需以 `package.json` scripts 为准；缺少 `test` 或 `lint` script 时必须标注为未确认，不得编造。Next.js `build` 可能在预渲染阶段执行 Server Component 数据读取，涉及 DB/外部服务时必须先列出 `POSTGRES_URL`、API key、mock 策略等前置条件。

## db_introspection

```yaml
db_introspection:
  orm: Prisma/Drizzle/postgres/@vercel/postgres/原生 SQL，运行时从依赖和代码确认
  migration_tool: Prisma migrations / Drizzle / SQL scripts / seed route，运行时确认
  schema_source: 优先 migration/schema 文件；其次 seed 脚本和 SQL 查询；无 DB 直连时只标注代码证据
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "'use client'|\"use client\""
      files: "**/app/**/*.tsx"
      desc: "Client Component 边界"
    - pattern: "'use server'|\"use server\""
      files: "**/app/**/*.{ts,tsx}"
      desc: "Server Action 边界"
    - pattern: "revalidatePath|revalidateTag|unstable_noStore|cache:"
      files: "**/app/**/*.{ts,tsx}"
      desc: "缓存与刷新策略"
    - pattern: "Response\\.json|NextResponse|pages/api"
      files: "**/*.{ts,tsx,js,jsx}"
      desc: "API/Route Handler 响应"
    - pattern: "safeParse|z\\.object|z\\.enum"
      files: "**/*.{ts,tsx}"
      desc: "表单/API 校验"
    - pattern: "NextAuth|auth\\(|middleware|proxy"
      files: "**/*.{ts,tsx}"
      desc: "认证和路由保护"
  file_patterns:
    - "**/app/**/*.{ts,tsx}"
    - "**/pages/**/*.{ts,tsx,js,jsx}"
    - "**/components/**/*.{ts,tsx}"
    - "**/lib/**/*.ts"
    - "**/middleware.ts"
    - "**/proxy.ts"
    - "**/next.config.*"
```

## notes

```yaml
notes:
  limitations:
    - 仅在 Next Learn 样本完成首轮静态验收，尚未在生产级 Next monorepo 复验
    - Next 项目可能是纯前端，也可能含 BFF/Server Actions/DB；不得因命中 frontend profile 就跳过服务端风险
    - 无 migration 文件时，只能从 seed 脚本和 SQL 查询推断 schema，必须标注为未确认
    - `npm test`、`npm run lint` 等命令必须以实际 scripts 为准；缺失时不可输出为已验证命令
    - `next build` 编译通过但预渲染失败时，应拆分记录编译/类型检查结果和运行时依赖失败原因；补齐 DB/外部服务后必须复跑并记录最终结果
    - 使用 `postgres(..., { ssl: 'require' })` 的项目，本地 Docker 复验需提供 SSL Postgres 或等价连接能力，不能用普通非 SSL Postgres 误判失败
    - Server Component/Client Component 边界容易被误改，实施前必须列出受影响文件的运行边界
  edge_cases:
    - 同仓多个 Next 示例或多 app workspace 时，先定位变更所在 package，再选择上下文根目录
    - Pages Router 与 App Router 混用时同时扫描 `pages/api` 与 `app/**/route.ts`
    - 涉及认证、缓存、DB 写入、redirect 的 Server Action 默认倾向 full
    - 仅 UI 文案/样式变更可判 light，但不得生成 DB/SQL 细节
```
