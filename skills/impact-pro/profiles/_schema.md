# Profile 统一接口定义

> 所有 profile 必须符合此 schema。Level 标注验收标准。

## 字段说明

```yaml
name: string          # 唯一标识，如 java-spring-mybatis
level: 1 | 2 | 3      # 成熟度等级（见下）
matchers:             # 栈探测规则（依赖优先于文件名）
  files: []           # 文件名命中（如 pom.xml）
  dependencies: []    # 依赖命中（如 spring-boot-starter）
  directories: []     # 目录命中
roles: []             # 此栈的典型角色（如后端/API服务）
discovery_globs:      # 上下文发现用的 glob 模式
  service: []         # 业务逻辑层文件
  data_access: []     # 数据访问层文件
  api: []             # API/Controller 层文件
  config: []          # 配置文件
  test: []            # 测试文件
  migration: []        # 迁移/Schema 文件
style_axes:           # 风格观察轴（结论需运行时现采）
  naming: string      # 命名规范提示
  layering: string    # 分层模式提示
  orm: string         # ORM 方式提示
  transaction: string # 事务处理提示
  exception: string    # 异常处理提示
  logging: string     # 日志框架提示
  api_response: string # API 响应格式提示
  dependency_injection: string # DI 方式提示
commands:             # 构建/测试/启动命令
  build: string
  test: string
  dev: string
  lint: string
db_introspection:     # 数据库自省方式
  orm: string         # ORM 名称
  migration_tool: string # 迁移工具名称
  schema_source: string # Schema 发现来源
validation_strategy:  # 风格合规检查策略
  grep_patterns: []   # grep 检查项
  file_patterns: []   # 需检查风格的文件模式
notes:
  limitations: []     # 已知局限
  edge_cases: []     # 边缘场景
```

## Level 定义

| Level | 含义 | 验收标准 |
|-------|------|---------|
| 1 | 基础覆盖 | 能识别栈、能找到主文件、能给候选命令、能说明发现方式、有 limitations |
| 2 | 深度覆盖 | 在真实变更中积累了风格轴和验证规则 |
| 3 | 成熟稳定 | 经多个真实项目验证，limitations 已充分覆盖 |

## matchers 打分规则

```
依赖命中: +3 分
文件命中: +1 分
目录命中: +1 分

最高分 profile 被选中。
无命中 → 加载 generic.md
```

## 写入规范

- 每个轴的值是「通常长什么样」的**提示**，明确标注「结论需运行时现采」
- 不写未验证的 glob/command，验证前写进 `notes.limitations`
- 迁移文件（migration）glob 必须覆盖：SQL 脚本、Flyway、Liquibase、迁移工具配置
