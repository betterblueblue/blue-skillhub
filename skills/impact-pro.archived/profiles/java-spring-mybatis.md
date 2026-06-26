# Java / Spring / MyBatis Profile

> Level 2 — 从 RuoYi-Vue 等真实项目迁移，积累了深度规则。

## 基本信息

```yaml
name: java-spring-mybatis
level: 2
matchers:
  files:
    - pom.xml
  dependencies:
    - spring-boot-starter
    - mybatis-spring-boot-starter
    - druid-spring-boot-starter
  directories:
    - src/main/java
    - src/main/resources/mapper
roles:
  - 后端服务
  - REST API
  - 管理后台
```

## discovery_globs

```yaml
discovery_globs:
  service:
    - "**/*Service*.java"
    - "**/*ServiceImpl*.java"
  data_access:
    - "**/*Mapper.xml"
    - "**/*Mapper.java"
    - "**/*Dao.java"
    - "**/*Repository*.java"
  api:
    - "**/*Controller*.java"
    - "**/*RestController*.java"
  entity:
    - "**/*Entity.java"
    - "**/*DO.java"
    - "**/domain/*.java"
    - "**/entity/*.java"
  dto:
    - "**/dto/*.java"
    - "**/vo/*.java"
    - "**/request/*.java"
    - "**/response/*.java"
  config:
    - "**/application*.yml"
    - "**/application*.properties"
    - "**/application-druid*.yml"
    - "**/*Config*.java"
  test:
    - "**/test/**/*.java"
    - "**/*Test.java"
    - "**/*Tests.java"
  migration:
    - "**/*.sql"
    - "**/db/**/*.sql"
    - "**/sql/**/*.sql"
    - "**/migrations/**/*.sql"
    - "**/flyway/**/*.sql"
    - "**/liquibase/**/*.xml"
  ui: []  # 纯后端栈，无前端 UI 层
```

## context_discovery

```yaml
context_discovery:
  project_map:
    - "pom.xml"
    - "**/application*.yml"
    - "**/application*.properties"
  entrypoints:
    - "**/*Controller*.java"
    - "**/*RestController*.java"
  data_models:
    - "**/*Entity.java"
    - "**/*DO.java"
    - "**/domain/*.java"
    - "**/entity/*.java"
    - "**/dto/*.java"
    - "**/vo/*.java"
    - "**/*Mapper.xml"
    - "**/*.sql"
  dependency_paths:
    - "**/*Service*.java"
    - "**/*ServiceImpl*.java"
    - "**/*Mapper.java"
    - "**/*Dao.java"
    - "**/*Repository*.java"
  tests:
    - "**/test/**/*.java"
    - "**/*Test.java"
    - "**/*Tests.java"
  configs:
    - "**/application*.yml"
    - "**/application*.properties"
    - "**/*Config*.java"
  exclude_patterns:
    - "**/target/**"
    - "**/generated/**"
  high_frequency_pattern_check: "引用计数异常大时先验证依赖是否真实存在"
```

## style_axes

> 结论需运行时从代码现采，下列为常见模式提示。

| 轴 | 常见模式 | 说明 |
|----|---------|------|
| naming | ServiceImpl/Controller/Mapper/XML驼峰，Mapper XML用下划线 | 列名→属性用驼峰映射 |
| layering | Controller → Service → Mapper(Dao) → XML | 部分项目无ServiceImpl直接写Service |
| orm | MyBatis XML + 注解混用，resultMap显式映射 | XML管理复杂查询，注解管简单CRUD |
| transaction | @Transactional加在ServiceImpl方法上 | 类级别@Transactional表示所有方法开启事务 |
| exception | 自定义业务异常 BusinessException，ControllerAdvice统一处理 | 错误码枚举+全局异常处理 |
| logging | Slf4j + {} 占位符，private static final Logger | Lombok @Slf4j 可选 |
| api_response | R 统一包装 {code, msg, data}，AjaxResponse | 分页用 PageUtils 或自定义 Page |
| dependency_injection | @Autowired字段注入为主，部分constructor | Lombok @RequiredArgsConstructor 可选 |
| entity | 字段注解@Column或无注解(MyBatis自动映射)，无@Getter/@Setter则手写getter/setter | Lombok可选 |

## commands

```yaml
commands:
  build: mvn clean package -DskipTests
  test: mvn test
  dev: mvn spring-boot:run
  lint: mvn checkstyle:check
```

## db_introspection

```yaml
db_introspection:
  orm: MyBatis
  migration_tool: 手写SQL脚本
  schema_source: 默认 db-adapters/mysql.md（SQL 只在 adapter 一处维护），运行时 DB 类型探测可覆盖（如探测到 PostgreSQL 则切到 db-adapters/postgresql.md）
```

## validation_strategy

```yaml
validation_strategy:
  grep_patterns:
    - pattern: "@Transactional"
      files: "**/*Service*.java"
      desc: "事务注解位置"
    - pattern: "private static final Logger"
      files: "**/*Service*.java"
      desc: "日志声明方式"
    - pattern: "resultType|resultMap"
      files: "**/*Mapper.xml"
      desc: "MyBatis返回类型声明"
    - pattern: "R\\.ok\\(|R\\.error\\("
      files: "**/*Controller*.java"
      desc: "统一响应包装"
  file_patterns:
    - "**/*Service*.java"
    - "**/*Controller*.java"
    - "**/*Mapper.xml"
    - "**/application*.yml"
```

## notes

```yaml
notes:
  limitations:
    - 不自动发现 MyBatis-Plus 特有逻辑（需升级profile）
    - 不自动发现 Spring Security 配置细节
    - 枚举类位置需人工确认
  edge_cases:
    - 多数据源项目：discovery_globs 会命中所有，优先按模块目录隔离
    - Mapper XML和Mapper接口分离：XML在resources/mapper，需同时读接口和XML
    - Service和ServiceImpl分离：先读Service接口再读Impl
    - 微服务模块项目：module名做前缀隔离，避免同名类混淆
```
