<!-- version: 1.0, last_updated: 2026-06-15, skill_commit: <TODO> -->
# 通用栈探测:清单文件 → 栈 / 构建 / 测试映射

> 本文件是栈无关的轻量探测表。Pathfinder 不依赖 impact-pro 的 profiles,自带这张通用映射。
> 用途:Phase 2 读清单文件,识别语言/框架/构建工具/测试入口,填地图【2】技术栈和【8】构建运行测试。
> **接缝**:以后若要栈专属深挖,可在此挂接 impact-pro 的 `profiles/<stack>.md`;当前通用版不引入该依赖。

## 探测原则

- **以清单文件为准**(`package.json` 等),命中即【已核实】。
- 命令字段(构建/测试/启动)优先从清单的 scripts / 配置里**读出来**,不凭框架惯例硬写。
- 找不到清单 → 按扩展名 + 目录启发式推断,标【推断】+ 置信低。
- **不执行**任何构建/测试命令——只**记录**命令是什么(Pathfinder 只读)。

## 清单文件 → 技术栈映射

| 清单文件 | 语言/生态 | 进一步看 | 构建/测试命令来源 |
|----------|-----------|----------|--------------------|
| `package.json` | Node.js / 前端 | `dependencies`(react/vue/next/express/nest…)、`scripts` | `scripts` 字段 |
| `pom.xml` | Java (Maven) | `<dependencies>`(spring-boot/mybatis…) | `./mvnw` / `mvn` |
| `build.gradle(.kts)` | Java/Kotlin (Gradle) | plugins、dependencies | `./gradlew` / `gradle` |
| `go.mod` | Go | `require`(gin/echo/gorm…) | `go build` / `go test` |
| `requirements.txt` | Python (pip) | 包名(django/flask/fastapi…) | 见 README / Makefile |
| `pyproject.toml` | Python (poetry/pdm/uv) | `[tool.poetry]`/deps | `poetry`/`pdm`/`uv` + 脚本 |
| `*.csproj` / `*.sln` | .NET / C# | PackageReference(EFCore/AspNetCore…) | `dotnet build`/`test` |
| `Gemfile` | Ruby | gem(rails/sinatra…) | `bundle` / `rake` |
| `composer.json` | PHP | require(laravel/symfony…) | composer scripts |
| `Cargo.toml` | Rust | dependencies(actix/axum…) | `cargo build`/`test` |
| `pubspec.yaml` | Dart / Flutter | dependencies | `flutter`/`dart` |

## DB 类型探测(只读)

| 来源 | 看什么 |
|------|--------|
| `docker-compose.yml` | service image(mysql/postgres/mongo/redis…) |
| 数据源配置 | `application.yml`/`.env`/`settings.py` 里 jdbc/连接串前缀(**脱敏密码**) |
| ORM 依赖 | mybatis/jpa/gorm/prisma/sqlalchemy/efcore → 反推 DB 家族 |
| migration 目录 | `migrations/`/`db/migrate`/alembic/flyway → 有版本化 schema |

> 连接串密码一律脱敏 `***`,只记键名和路径。

## monorepo / 多栈

- 找根 `package.json` 的 `workspaces` / `pnpm-workspace.yaml` / `lerna.json` / `nx.json` / `turbo.json` / Go `go.work` / `apps`+`packages` 结构。
- 为每个子项目分别探测栈,列出目录边界,**不压成单栈**。
- 地图【2】技术栈分子项目小节呈现。

## 找不到清单时的启发式(标【推断】+ 置信低)

| 信号 | 推断 |
|------|------|
| 大量 `.py` + `manage.py` | Python(可能 Django) |
| 大量 `.go` 无 go.mod | Go(可能 GOPATH 旧项目) |
| 大量 `.java` + `WEB-INF` | Java Web(可能旧 Servlet) |
| `index.html` + `.js`/`.ts` 无 package.json | 纯静态前端 |

启发式结论必须显式标"置信低,无清单佐证",并列入【13】未覆盖项建议用户补充。

## 维护注意

- 新生态出现时加一行映射即可,不改 Phase 2 主流程。
- 本表只做"识别 + 记录命令",绝不执行命令(只读硬性规则)。
