# Frontend / React / Vite Profile

> Level 1 — 在 `fastapi/full-stack-fastapi-template/frontend` 上完成首轮验收。适用于 React + Vite + TypeScript 前端项目，兼容 TanStack Router、Playwright/Vitest。

## 基本信息

```yaml
name: frontend-react-vite
level: 1
matchers:
  files:
    - package.json
    - vite.config.ts
    - tsconfig.json
  dependencies:
    - react
    - vite
    - "@vitejs/plugin-react"
    - "@vitejs/plugin-react-swc"
    - "@playwright/test"
    - vitest
  directories:
    - src
    - src/components
    - src/routes
    - tests
roles:
  - 前端单页应用
  - UI/交互层
  - E2E 测试项目
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/src/hooks/**/*.ts"
    - "**/src/hooks/**/*.tsx"
    - "**/src/lib/**/*.ts"
    - "**/src/utils.ts"
    - "**/src/utils/**/*.ts"
  data_access:
    - "**/src/client/**/*.ts"
    - "**/src/api/**/*.ts"
    - "**/src/services/**/*.ts"
  api:
    - "**/src/routes/**/*.tsx"
    - "**/src/routes/**/*.ts"
    - "**/src/main.tsx"
    - "**/src/App.tsx"
    - "**/src/router*.ts"
    - "**/src/routeTree*.ts"
  entity:
    - "**/src/types/**/*.ts"
    - "**/src/client/types*.ts"
    - "**/src/client/schemas*.ts"
  dto:
    - "**/src/client/**/*.ts"
    - "**/src/types/**/*.ts"
  config:
    - "**/package.json"
    - "**/vite.config.ts"
    - "**/tsconfig*.json"
    - "**/playwright.config.ts"
    - "**/vitest.config.ts"
    - "**/biome.json"
    - "**/src/index.css"
  test:
    - "**/tests/**/*.spec.ts"
    - "**/tests/**/*.test.ts"
    - "**/src/**/*.test.ts"
    - "**/src/**/*.test.tsx"
    - "**/src/**/*.spec.ts"
    - "**/src/**/*.spec.tsx"
  migration: []
  ui:
    - "**/src/components/**/*.tsx"
    - "**/src/routes/**/*.tsx"
    - "**/src/**/*.tsx"
    - "**/src/**/*.css"
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "package.json"
    - "vite.config.ts"
    - "tsconfig*.json"
    - "playwright.config.ts"
    - "vitest.config.ts"
  entrypoints:
    - "**/src/main.tsx"
    - "**/src/App.tsx"
    - "**/src/routes/**/*.tsx"
    - "**/src/routes/**/*.ts"
    - "**/src/router*.ts"
    - "**/src/routeTree*.ts"
  data_models:
    - "**/src/types/**/*.ts"
    - "**/src/client/types*.ts"
    - "**/src/client/schemas*.ts"
    - "**/src/client/**/*.ts"
  dependency_paths:
    - "**/src/hooks/**/*.ts"
    - "**/src/hooks/**/*.tsx"
    - "**/src/lib/**/*.ts"
    - "**/src/utils.ts"
    - "**/src/utils/**/*.ts"
    - "**/src/api/**/*.ts"
    - "**/src/services/**/*.ts"
  tests:
    - "**/tests/**/*.spec.ts"
    - "**/tests/**/*.test.ts"
    - "**/src/**/*.test.ts"
    - "**/src/**/*.test.tsx"
    - "**/src/**/*.spec.ts"
    - "**/src/**/*.spec.tsx"
  configs:
    - "**/package.json"
    - "**/vite.config.ts"
    - "**/tsconfig*.json"
    - "**/playwright.config.ts"
    - "**/vitest.config.ts"
    - "**/biome.json"
    - "**/src/index.css"
  exclude_patterns:
    - "**/node_modules/**"
    - "**/dist/**"
    - "**/build/**"
    - "**/coverage/**"
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## style_axes

> 下列是观察方向，结论必须运行时从项目文件现采。

| 轴 | 观察方向 |
|----|----------|
| naming | 组件 PascalCase、hook useXxx、测试描述文案 |
| layering | routes/components/hooks/lib/client 的目录边界 |
| orm | 不适用；前端项目不得生成 DB 变更结论 |
| transaction | 不适用；关注本地状态、server mutation、缓存失效 |
| exception | 表单校验、toast、ErrorBoundary、API error handling |
| logging | console、错误上报、devtools 使用 |
| api_response | generated client/types、React Query mutation/query 结构 |
| dependency_injection | Provider 结构，如 ThemeProvider、QueryClientProvider、RouterProvider |
| ui_state | localStorage/sessionStorage、URL state、React state、context |
| styling | CSS/Tailwind/theme class、dark mode、设计系统组件 |

## commands

```yaml
commands:
  build: npm run build
  test: npm test
  dev: npm run dev
  lint: npm run lint
```

## db_introspection

```yaml
db_introspection:
  orm: 不适用
  migration_tool: 不适用
  schema_source: 不适用；如涉及 generated API client，只读 `src/client/**`
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "localStorage|sessionStorage"
      files: "**/src/**/*.tsx"
      desc: "本地状态持久化"
    - pattern: "Provider"
      files: "**/src/**/*.tsx"
      desc: "全局 Provider 注入"
    - pattern: "getByTestId|getByRole"
      files: "**/tests/**/*.spec.ts"
      desc: "Playwright 选择器风格"
    - pattern: "dark|theme"
      files: "**/src/**/*.{tsx,css}"
      desc: "主题样式和切换逻辑"
  file_patterns:
    - "**/src/**/*.tsx"
    - "**/src/**/*.ts"
    - "**/src/**/*.css"
    - "**/tests/**/*.spec.ts"
```

## notes

```yaml
notes:
  limitations:
    - 仅在 React/Vite 样本上验收，Vue/Nuxt/Next.js 需要新增或扩展 profile
    - 不处理后端 schema；一旦涉及 API 契约变更，应同时加载后端 profile
    - 不直接判断视觉质量，需要结合截图/E2E 或人工验收
  edge_cases:
    - generated client 不应手改，应追踪 OpenAPI 源头
    - 主题、认证、路由通常在 Provider 或 root route 中，不能只读页面组件
    - 前端-only 变更不得生成 SQL/DB 回滚方案
```
