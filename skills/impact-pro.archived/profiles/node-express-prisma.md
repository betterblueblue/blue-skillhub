# Node / Express / Prisma Profile

> Level 2 — 在 prisma-express-ts（分层架构 + Prisma 4 + Express 4）和 postgis-express（单文件 + Prisma 7 + Express 5 + PostGIS）上完成生产级验收（T51）。适用于 Node.js/TypeScript + Express/Fastify + Prisma ORM 项目。

## 基本信息

```yaml
name: node-express-prisma
level: 2
matchers:
  files:
    - package.json
    - prisma/schema.prisma
    - prisma.config.ts
  dependencies:
    - express
    - fastify
    - prisma
    - "@prisma/client"
    - "@prisma/adapter-pg"
  directories:
    - src
    - prisma
    - tests
roles:
  - Node.js API 服务
  - REST API
  - Prisma ORM 后端
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/*service*.ts"
    - "**/*Service*.ts"
    - "**/services/**/*.ts"
    - "**/src/services/**/*.ts"
  data_access:
    - "**/prisma/schema.prisma"
    - "**/prisma.config.ts"
    - "**/prisma/**/*.prisma"
    - "**/prisma/seed.ts"
    - "**/src/**/*repository*.ts"
    - "**/src/**/*Repository*.ts"
  api:
    - "**/src/app.ts"
    - "**/src/index.ts"
    - "**/src/server.ts"
    - "**/src/main.ts"
    - "**/src/routes/**/*.ts"
    - "**/src/controllers/**/*.ts"
    - "**/src/**/*Controller*.ts"
  entity:
    - "**/prisma/schema.prisma"
    - "**/src/**/*.model.ts"
    - "**/src/**/*Model*.ts"
  dto:
    - "**/src/**/*.dto.ts"
    - "**/src/**/*Dto*.ts"
    - "**/src/**/*.schema.ts"
    - "**/src/**/*Schema*.ts"
    - "**/src/validations/**/*.ts"
    - "**/src/**/*validation*.ts"
  config:
    - "**/package.json"
    - "**/tsconfig.json"
    - "**/prisma.config.ts"
    - "**/.env.example"
    - "**/docker-compose*.yml"
    - "**/jest.config.*"
    - "**/vitest.config.*"
  test:
    - "**/tests/**/*.ts"
    - "**/*.test.ts"
    - "**/*.spec.ts"
  migration:
    - "**/prisma/migrations/**/*"
    - "**/prisma/schema.prisma"
  ui: []  # 纯后端栈，无前端 UI 层
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "package.json"
    - "tsconfig.json"
    - "prisma.config.ts"
  entrypoints:
    - "**/src/app.ts"
    - "**/src/index.ts"
    - "**/src/server.ts"
    - "**/src/main.ts"
    - "**/src/routes/**/*.ts"
    - "**/src/controllers/**/*.ts"
  data_models:
    - "**/prisma/schema.prisma"
    - "**/prisma/migrations/**/*"
    - "**/src/**/*.model.ts"
    - "**/src/**/*.dto.ts"
    - "**/src/**/*.schema.ts"
  dependency_paths:
    - "**/*service*.ts"
    - "**/*Service*.ts"
    - "**/services/**/*.ts"
    - "**/src/**/*repository*.ts"
    - "**/src/**/*Repository*.ts"
  tests:
    - "**/tests/**/*.ts"
    - "**/*.test.ts"
    - "**/*.spec.ts"
  configs:
    - "**/package.json"
    - "**/tsconfig.json"
    - "**/prisma.config.ts"
    - "**/.env.example"
    - "**/docker-compose*.yml"
    - "**/jest.config.*"
    - "**/vitest.config.*"
  exclude_patterns:
    - "**/node_modules/**"
    - "**/dist/**"
    - "**/build/**"
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## style_axes

> 下列是观察方向，结论必须运行时从项目文件现采。

| 轴 | 观察方向 |
|----|----------|
| naming | 路由路径、模型字段、Prisma model、测试命名是否使用 camelCase |
| layering | 是否单文件 Express app，或 routes/controller/service/repository 分层 |
| orm | Prisma schema、PrismaClient 初始化、adapter、migration 路径 |
| transaction | 是否使用 `prisma.$transaction` 或单次 ORM 调用 |
| exception | Express/Fastify 错误响应状态码和 body 格式 |
| logging | 是否有 logger/morgan/pino/winston 或 console 输出 |
| api_response | REST 返回裸对象、数组，还是统一 envelope |
| dependency_injection | PrismaClient 是否单例导出、通过 context 注入或直接 import |

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
  orm: Prisma
  migration_tool: Prisma Migrate
  schema_source: 见 prisma/schema.prisma（代码级 schema 发现路径）；默认 db-adapter 由 Prisma provider 决定（sqlite → generic-sql.md / postgresql → postgresql.md / mysql → mysql.md），运行时 DB 类型探测可覆盖
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "model "
      files: "**/prisma/schema.prisma"
      desc: "Prisma model 定义"
    - pattern: "new PrismaClient"
      files: "**/src/**/*.ts"
      desc: "PrismaClient 初始化方式"
    - pattern: "(app|router)\\.(get|post|put|patch|delete)"
      files: "**/src/**/*.ts"
      desc: "Express 路由定义（app.xxx 和 router.xxx）"
    - pattern: "request\\("
      files: "**/tests/**/*.ts"
      desc: "Supertest API 测试"
  file_patterns:
    - "**/prisma/schema.prisma"
    - "**/src/**/*.ts"
    - "**/tests/**/*.ts"
```

## notes

```yaml
notes:
  limitations:
    - 仅在 Express + Prisma 样本上验收，Fastify/NestJS 需要二次验证
    - Prisma 7 的 `prisma-client` generator 与旧版 `prisma-client-js` 需运行时识别
    - 无数据库连接时不能确认行数、索引实际状态，只能读取 schema.prisma
  edge_cases:
    - 单文件 Express app：API、service、data_access 可能都在 `src/app.ts` 或 `src/server.ts`
    - monorepo：需先定位包含 `prisma/schema.prisma` 的子项目目录
    - 使用 Zod/class-validator 时，DTO/校验 schema 可能不在 Prisma schema 中
    - `Unsupported` 类型（PostGIS/JSONB 等）：Prisma Client 方法不可用，需 `$queryRaw` 操作
```
