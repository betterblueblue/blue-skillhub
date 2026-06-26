# Frontend / Nuxt / Vue Profile

> Level 1 — 在 `nuxt-ui-templates/dashboard` 上完成首轮静态验收。适用于 Nuxt 3/4 + Vue 3 项目，覆盖 pages/layouts/components/composables/server API、Nuxt UI、VueUse、Zod 表单校验和 SSR/CSR 组件边界。

## 基本信息

```yaml
name: frontend-nuxt-vue
level: 1
matchers:
  files:
    - package.json
    - nuxt.config.ts
    - nuxt.config.js
    - app.vue
    - app/app.vue
    - app.config.ts
    - app/app.config.ts
  dependencies:
    - nuxt
    - vue
    - "@nuxt/ui"
    - "@vueuse/core"
    - "@vueuse/nuxt"
    - zod
    - pinia
    - vitest
    - "@nuxt/test-utils"
  directories:
    - app
    - app/pages
    - app/components
    - app/composables
    - app/layouts
    - server
    - server/api
    - pages
    - components
    - composables
roles:
  - Nuxt 应用
  - Vue 前端 UI/交互层
  - Nitro server API / BFF
  - SSR/CSR 混合项目
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/app/composables/**/*.ts"
    - "**/composables/**/*.ts"
    - "**/app/utils/**/*.ts"
    - "**/utils/**/*.ts"
    - "**/stores/**/*.ts"
    - "**/app/stores/**/*.ts"
    - "**/server/utils/**/*.ts"
  data_access:
    - "**/server/**/*.ts"
    - "**/server/api/**/*.ts"
    - "**/server/routes/**/*.ts"
    - "**/server/plugins/**/*.ts"
    - "**/prisma/schema.prisma"
    - "**/drizzle.config.*"
  api:
    - "**/server/api/**/*.ts"
    - "**/server/routes/**/*.ts"
    - "**/app/pages/**/*.vue"
    - "**/pages/**/*.vue"
    - "**/app/layouts/**/*.vue"
    - "**/layouts/**/*.vue"
    - "**/app/error.vue"
    - "**/error.vue"
  entity:
    - "**/app/types/**/*.ts"
    - "**/types/**/*.ts"
    - "**/server/types/**/*.ts"
    - "**/prisma/schema.prisma"
  dto:
    - "**/app/types/**/*.ts"
    - "**/types/**/*.ts"
    - "**/interfaces/**/*.ts"
    - "**/*.d.ts"
    - "**/app/**/*schema*.ts"
    - "**/server/**/*schema*.ts"
  config:
    - "**/package.json"
    - "**/nuxt.config.*"
    - "**/app.config.ts"
    - "**/app/app.config.ts"
    - "**/tsconfig*.json"
    - "**/eslint.config.*"
    - "**/vitest.config.*"
    - "**/playwright.config.*"
    - "**/.env.example"
    - "**/pnpm-workspace.yaml"
  test:
    - "**/__tests__/**/*.{ts,vue}"
    - "**/*.test.ts"
    - "**/*.spec.ts"
    - "**/*.test.vue"
    - "**/*.spec.vue"
    - "**/tests/**/*.ts"
    - "**/e2e/**/*.ts"
  migration:
    - "**/prisma/migrations/**/*"
    - "**/drizzle/**/*.sql"
    - "**/migrations/**/*.sql"
    - "**/server/database/**/*.sql"
  ui:
    - "**/app/**/*.vue"
    - "**/components/**/*.vue"
    - "**/pages/**/*.vue"
    - "**/layouts/**/*.vue"
    - "**/app/assets/**/*.css"
    - "**/assets/**/*.css"
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "package.json"
    - "nuxt.config.*"
    - "app.config.ts"
    - "app/app.config.ts"
    - "tsconfig*.json"
    - "pnpm-workspace.yaml"
  entrypoints:
    - "**/server/api/**/*.ts"
    - "**/server/routes/**/*.ts"
    - "**/app/pages/**/*.vue"
    - "**/pages/**/*.vue"
    - "**/app/layouts/**/*.vue"
    - "**/layouts/**/*.vue"
    - "**/app/error.vue"
    - "**/error.vue"
  data_models:
    - "**/app/types/**/*.ts"
    - "**/types/**/*.ts"
    - "**/server/types/**/*.ts"
    - "**/prisma/schema.prisma"
    - "**/prisma/migrations/**/*"
    - "**/drizzle/**/*.sql"
    - "**/migrations/**/*.sql"
  dependency_paths:
    - "**/app/composables/**/*.ts"
    - "**/composables/**/*.ts"
    - "**/app/utils/**/*.ts"
    - "**/utils/**/*.ts"
    - "**/stores/**/*.ts"
    - "**/app/stores/**/*.ts"
    - "**/server/utils/**/*.ts"
    - "**/server/**/*.ts"
  tests:
    - "**/__tests__/**/*.{ts,vue}"
    - "**/*.test.ts"
    - "**/*.spec.ts"
    - "**/*.test.vue"
    - "**/*.spec.vue"
    - "**/tests/**/*.ts"
    - "**/e2e/**/*.ts"
  configs:
    - "**/package.json"
    - "**/nuxt.config.*"
    - "**/app.config.ts"
    - "**/app/app.config.ts"
    - "**/tsconfig*.json"
    - "**/eslint.config.*"
    - "**/vitest.config.*"
    - "**/playwright.config.*"
    - "**/.env.example"
    - "**/pnpm-workspace.yaml"
  exclude_patterns:
    - "**/node_modules/**"
    - "**/.nuxt/**"
    - "**/.output/**"
    - "**/dist/**"
    - "**/coverage/**"
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## style_axes

> 下列是观察方向，结论必须运行时从项目文件现采。

| 轴 | 观察方向 |
|----|----------|
| naming | Vue SFC PascalCase、composable useXxx、server API 文件路径、页面路由命名 |
| layering | app/pages、components、composables、types、server/api、layouts 的边界 |
| orm | Prisma/Drizzle/server DB 工具；纯 mock API 时必须标注无 DB 证据 |
| transaction | server API 写入、store/composable 状态变更、SSR 数据获取时序 |
| exception | error.vue、try/catch、Zod 校验、Nuxt UI 表单错误、API status |
| logging | console、Nuxt/Nitro 日志、错误上报 |
| api_response | eventHandler/defineEventHandler 返回值、useFetch/useAsyncData 数据形态 |
| dependency_injection | provide/inject、Nuxt plugin、app.config、useAppConfig、modules |
| state | ref/reactive/computed、useState、Pinia、VueUse shared composable、URL query |
| rendering_boundary | `.server.vue`、`.client.vue`、SSR 数据获取、hydration 风险 |
| styling | Nuxt UI、Tailwind、CSS variables、app/assets/css |

## commands

```yaml
commands:
  build: npm run build
  test: npm test
  dev: npm run dev
  lint: npm run lint
```

命令必须以 `package.json` scripts 为准；Nuxt 项目常见 `typecheck` 应作为验证候选，存在 `typecheck` script 时优先执行 `npm run typecheck` 或对应包管理器命令。

## db_introspection

```yaml
db_introspection:
  orm: Prisma/Drizzle/Nitro storage/自定义 server DB，运行时从依赖和 server 代码确认
  migration_tool: Prisma migrations / Drizzle / SQL scripts，运行时确认
  schema_source: 优先 migration/schema；其次 server API mock/types；纯前端或 mock 数据不得声称已确认 DB
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "useFetch|useAsyncData"
      files: "**/*.{vue,ts}"
      desc: "Nuxt 数据获取"
    - pattern: "eventHandler|defineEventHandler"
      files: "**/server/**/*.ts"
      desc: "Nitro server API"
    - pattern: "ref\\(|reactive|useState|computed"
      files: "**/*.{vue,ts}"
      desc: "Vue 状态管理"
    - pattern: "z\\.object|safeParse|parse\\("
      files: "**/*.{vue,ts}"
      desc: "表单/API 校验"
    - pattern: "useAppConfig|appConfig|defineNuxtConfig"
      files: "**/*.{vue,ts}"
      desc: "Nuxt 配置和主题"
    - pattern: "\\.server\\.vue|\\.client\\.vue"
      files: "**/*.vue"
      desc: "SSR/CSR 组件边界"
  file_patterns:
    - "**/app/**/*.vue"
    - "**/app/**/*.ts"
    - "**/server/**/*.ts"
    - "**/nuxt.config.*"
    - "**/app.config.ts"
```

## notes

```yaml
notes:
  limitations:
    - 仅在 Nuxt UI Dashboard 样本完成首轮静态验收，尚未覆盖生产级 Nuxt 后端写入和数据库迁移
    - Nuxt 项目可能只有 mock server API；无 DB/migration 时必须标注 schema 不适用或未确认
    - `.server.vue` / `.client.vue` 边界影响 hydration，实施前必须列出受影响组件类型
    - `npm run lint`、`npm run typecheck` 等必须安装依赖后才可判定结果
  edge_cases:
    - Nuxt 4 可能使用 `app/` 目录，Nuxt 3/旧项目可能直接使用 `pages/`、`components/`
    - 前端-only 设置项可判 light；涉及 server API、持久化、权限或通知发送时应升级 full
    - 使用 Nuxt UI / app.config 主题时，视觉变更需检查全局配置和组件局部覆盖
```
