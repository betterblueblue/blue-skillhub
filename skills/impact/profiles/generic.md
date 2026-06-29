# Generic Profile

> 强备用 profile，适用于无法命中任何专属 profile 的项目。Level 1 核心能力。

## 基本信息

```yaml
name: generic
level: 1
matchers:
  files:
    - package.json
    - next.config.js
    - next.config.mjs
    - next.config.ts
    - nuxt.config.ts
    - nuxt.config.js
    - requirements.txt
    - pyproject.toml
    - go.mod
    - Cargo.toml
    - pom.xml
    - build.gradle
  dependencies: []
  directories:
    - src
    - app
    - pages
    - components
    - composables
    - server
    - api
    - controllers
    - services
    - models
    - repositories
    - migrations
    - tests
roles:
  - 通用应用
```

## discovery_globs

> 通过扫描目录结构自动推断项目布局。

```yaml
discovery_globs:
  service:
    - "**/*Service*.java"
    - "**/*service*.py"
    - "**/*service*.ts"
    - "**/*Service*.go"
    - "**/services/**/*.py"
    - "**/services/**/*.ts"
    - "**/service/**/*.go"
    - "**/composables/**/*.ts"
    - "**/app/composables/**/*.ts"
    - "**/app/utils/**/*.ts"
  data_access:
    - "**/*Mapper.xml"
    - "**/*Mapper.java"
    - "**/*Repository*.java"
    - "**/*Repository*.py"
    - "**/*Dao*.java"
    - "**/*Model*.py"
    - "**/models.py"
    - "**/schemas.py"
    - "**/*Model*.go"
    - "**/models.go"
    - "**/database.go"
    - "**/*DbContext.cs"
    - "**/*Context.cs"
    - "**/prisma/schema.prisma"
    - "**/prisma.config.ts"
    - "**/*.sql"
    - "**/migrations/**/*.sql"
  api:
    - "**/*Controller*.java"
    - "**/*Controller*.py"
    - "**/*Controller*.ts"
    - "**/*Handler*.go"
    - "**/routes/*.py"
    - "**/routes/*.ts"
    - "**/api/**/*.ts"
    - "**/src/app.ts"
    - "**/app/**/route.ts"
    - "**/app/**/page.tsx"
    - "**/app/**/layout.tsx"
    - "**/pages/api/**/*.ts"
    - "**/pages/api/**/*.js"
    - "**/server/api/**/*.ts"
    - "**/server/routes/**/*.ts"
    - "**/app/pages/**/*.vue"
    - "**/pages/**/*.vue"
    - "**/app/layouts/**/*.vue"
    - "**/middleware.ts"
    - "**/proxy.ts"
    - "**/src/index.ts"
    - "**/src/server.ts"
    - "**/src/main.ts"
    - "**/src/routes/**/*.tsx"
    - "**/src/routes/**/*.ts"
    - "**/endpoints/**/*.py"
    - "**/routers.go"
    - "**/*handler*.go"
    - "**/*Controller.cs"
    - "**/*Endpoint.cs"
    - "**/Program.cs"
  entity:
    - "**/*Entity.java"
    - "**/*DO.java"
    - "**/*Model*.py"
    - "**/*Schema*.py"
    - "**/models.py"
    - "**/schemas.py"
    - "**/prisma/schema.prisma"
    - "**/*model*.go"
    - "**/*entity*.go"
    - "**/models/*.go"
    - "**/entities/*.go"
    - "**/models.go"
    - "**/Entities/**/*.cs"
  dto:
    - "**/dto/*.java"
    - "**/vo/*.java"
    - "**/request/*.java"
    - "**/response/*.java"
    - "**/schemas/*.py"
    - "**/schemas/*.ts"
    - "**/src/types/**/*.ts"
    - "**/app/lib/definitions.ts"
    - "**/lib/definitions.ts"
    - "**/app/types/**/*.ts"
    - "**/types/**/*.ts"
    - "**/src/client/**/*.ts"
    - "**/*Request.cs"
    - "**/*Response.cs"
    - "**/*Dto.cs"
  config:
    - "**/application*.yml"
    - "**/application*.properties"
    - "**/*.yaml"
    - "**/*.yml"
    - "**/config*.py"
    - "**/settings.py"
    - "**/appsettings*.json"
    - "**/package.json"
    - "**/tsconfig*.json"
    - "**/vite.config.ts"
    - "**/next.config.*"
    - "**/nuxt.config.*"
    - "**/app.config.ts"
    - "**/app/app.config.ts"
    - "**/playwright.config.ts"
    - "**/prisma.config.ts"
    - "**/*.sln"
    - "**/*.csproj"
    - "**/Directory.Packages.props"
    - "**/go.mod"
  test:
    - "**/test/**/*.java"
    - "**/tests/**/*.py"
    - "**/*.test.ts"
    - "**/*.spec.ts"
    - "**/*.test.tsx"
    - "**/*.spec.tsx"
    - "**/*.test.vue"
    - "**/*.spec.vue"
    - "**/*_test.go"
    - "**/*Test.java"
    - "**/tests/**/*.cs"
    - "**/*Tests/**/*.cs"
  migration:
    - "**/*.sql"
    - "**/db/**/*.sql"
    - "**/migrations/**/*.sql"
    - "**/flyway/**/*.sql"
    - "**/liquibase/**/*.xml"
    - "**/alembic/**/*.py"
    - "**/db/migrate/**/*.rb"
    - "**/prisma/migrations/**/*"
    - "**/app/seed/route.ts"
    - "**/scripts/seed*.ts"
    - "**/Migrations/**/*.cs"
  ui:
    - "**/app/**/*.tsx"
    - "**/app/**/*.vue"
    - "**/components/**/*.tsx"
    - "**/components/**/*.vue"
    - "**/pages/**/*.tsx"
    - "**/pages/**/*.vue"
    - "**/src/**/*.tsx"
    - "**/src/**/*.vue"
    - "**/src/**/*.css"
    - "**/src/components/**/*"
```

## context_discovery

> generic 只负责兜底分析，不把命中结果描述成专属技术栈已验证。

```yaml
context_discovery:
  project_map:
    - "package.json"
    - "pom.xml"
    - "build.gradle"
    - "pyproject.toml"
    - "requirements.txt"
    - "go.mod"
    - "Cargo.toml"
    - "*.sln"
    - "*.csproj"
    - "Dockerfile"
    - "docker-compose*.yml"
  entrypoints:
    - "**/*Controller*.java"
    - "**/*Controller*.py"
    - "**/*Controller*.ts"
    - "**/*Controller.cs"
    - "**/*Endpoint.cs"
    - "**/*Handler*.go"
    - "**/routes/**/*"
    - "**/api/**/*"
    - "**/app/**/route.ts"
    - "**/app/**/page.tsx"
    - "**/pages/api/**/*"
    - "**/server/api/**/*"
    - "**/Program.cs"
    - "**/main.go"
  data_models:
    - "**/*Entity.java"
    - "**/*DO.java"
    - "**/models.py"
    - "**/schemas.py"
    - "**/models.go"
    - "**/Entities/**/*.cs"
    - "**/*DbContext.cs"
    - "**/prisma/schema.prisma"
    - "**/*.sql"
    - "**/migrations/**/*"
  dependency_paths:
    - "**/*Service*.*"
    - "**/*Repository*.*"
    - "**/*Mapper*.*"
    - "**/*Dao*.*"
    - "**/services/**/*"
    - "**/repositories/**/*"
    - "**/composables/**/*"
    - "**/stores/**/*"
  tests:
    - "**/test/**/*"
    - "**/tests/**/*"
    - "**/*.test.*"
    - "**/*.spec.*"
    - "**/*_test.go"
    - "**/*Tests/**/*.cs"
  configs:
    - "**/application*.yml"
    - "**/application*.properties"
    - "**/*.yaml"
    - "**/*.yml"
    - "**/config*.*"
    - "**/settings.py"
    - "**/appsettings*.json"
    - "**/package.json"
    - "**/tsconfig*.json"
    - "**/vite.config.*"
    - "**/next.config.*"
    - "**/nuxt.config.*"
    - "**/go.mod"
  exclude_patterns:
    - "**/node_modules/**"
    - "**/dist/**"
    - "**/build/**"
    - "**/.next/**"
    - "**/.nuxt/**"
    - "**/.output/**"
    - "**/target/**"
    - "**/vendor/**"
    - "**/bin/**"
    - "**/obj/**"
    - "**/generated/**"
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## 目录结构发现流程

```
1. 扫描根目录 → 列出所有一级子目录
2. 识别常见模式 → 提出候选 discovery_globs
3. 回显用户确认 → 用户可调整
4. 不确定项 → 标注 limitations
```

### 常见目录模式

| 模式 | 推断含义 | 候选 glob |
|------|---------|---------|
| src/main/java | Java | `**/*Service*.java`, `**/*Controller*.java` |
| src/main/resources/mapper | MyBatis | `**/*Mapper.xml` |
| app/ | Python/Go | `**/*service*.py`, `**/*Handler*.go` |
| go.mod | Go | `**/models.go`, `**/routers.go`, `**/*_test.go` |
| *.sln / *.csproj | .NET | `**/*DbContext.cs`, `**/*Controller.cs`, `**/*Endpoint.cs` |
| server/ | Node.js/TS | `**/*Controller*.ts`, `**/routes/*.ts` |
| controllers/ | Python/TS | `**/controllers/**` |
| services/ | 通用 | `**/services/**` |
| models/ | Python | `**/*Model*.py` |
| prisma/ | Prisma | `**/prisma/schema.prisma`, `**/prisma.config.ts` |
| app/ + next.config.* | Next.js App Router | `**/app/**/page.tsx`, `**/app/**/route.ts`, `**/app/lib/**/*.ts` |
| pages/api/ | Next.js Pages API | `**/pages/api/**/*.ts`, `**/pages/api/**/*.js` |
| app/ + nuxt.config.* | Nuxt 4 / Vue | `**/app/pages/**/*.vue`, `**/app/components/**/*.vue`, `**/server/api/**/*.ts` |
| pages/ + nuxt.config.* | Nuxt 3 / Vue | `**/pages/**/*.vue`, `**/components/**/*.vue`, `**/composables/**/*.ts` |
| src/routes/ | 前端/Node 路由 | `**/src/routes/**/*.tsx`, `**/src/routes/**/*.ts` |
| src/components/ | 前端组件 | `**/src/**/*.tsx`, `**/src/components/**/*` |
| repositories/ | 多语言 | `**/*Repository*.java`, `**/*Repository*.py` |
| migrations/ | DB迁移 | `**/migrations/**/*.sql` |

## style_axes

> generic profile 不预置风格结论，只提供观察方向。

```yaml
style_axes:
  naming: ""        # 结论需运行时从代码确认：扫描目标文件识别命名规范
  layering: ""      # 结论需运行时从代码确认：识别典型分层目录
  orm: ""          # 结论需运行时从代码确认：检查是否有 ORM 目录/配置
  transaction: ""  # 结论需运行时从代码确认：检查是否有事务相关关键字
  exception: ""     # 结论需运行时从代码确认：检查异常处理模式
  logging: ""       # 结论需运行时从代码确认：检查日志框架引用
  api_response: ""  # 结论需运行时从代码确认：检查 API 响应包装模式
  dependency_injection: "" # 结论需运行时从代码确认：检查 DI 关键字
```

### 风格确认步骤

1. 从 Phase 2 发现的目标文件中取 ≤ 6 个代表性文件
2. 扫描每个文件提取风格特征
3. 将发现填入 style_axes 的对应轴
4. 标注「未确认」项

## commands

> 常见构建/测试命令，提供候选供用户确认。

```yaml
commands:
  build: ""   # 需按项目实际填充，如 mvn / npm run build / python setup.py
  test: ""   # mvn test / pytest / npm test / go test
  dev: ""    # npm run dev / python manage.py runserver / mvn spring-boot:run
  lint: ""   # eslint / flake8 / golangci-lint
```

### 常见命令推断规则

| 文件 | 推断命令 |
|------|---------|
| pom.xml | `mvn clean package -DskipTests` |
| package.json | `npm run build` |
| requirements.txt | `pip install -r requirements.txt` |
| go.mod | `go build` |
| Cargo.toml | `cargo build` |

## db_introspection

```yaml
db_introspection:
  orm: ""         # 需从项目配置/代码中识别
  migration_tool: ""  # 检查 migrations/ 目录、Flyway、Liquibase、Alembic
  schema_source: generic-sql.md  # 回退到 generic-sql adapter
```

## validation_strategy

> generic 不预置具体检查项，提供框架供调整。

```yaml
validation_strategy:
  grep_patterns:
    - pattern: ""  # 待按项目确认
      files: ""    # 待按项目确认
      desc: ""     # 待按项目确认
  file_patterns:
    - ""          # 待按项目确认
```

## notes

```yaml
notes:
  limitations:
    - 不预置任何栈的风格结论，结论需运行时从代码确认
    - discovery_globs 候选可能不准确，依赖用户确认调整
    - commands 为猜测值，必须用户确认
    - 无 DB 直连时回退为代码扫描，schema 信息受限
    - 找不到 schema/API/model/test 时必须在文档中标注为未确认项，不得判定为已覆盖
  edge_cases:
    - 单文件项目：目录扫描可能无法推断项目结构
    - 混合栈项目（前后端同仓）：按变更维度选主 profile，辅助 profile 提供额外候选
    - 新项目（无历史代码）：风格确认为空，需用户明确风格要求
```
