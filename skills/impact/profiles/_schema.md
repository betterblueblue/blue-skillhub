# Profile 统一接口定义

> 所有 profile 必须符合此 schema。Level 标注验收标准。

## 字段说明

```yaml
name: string          # 唯一标识，如 java-spring-mybatis
level: 1 | 2 | 3      # 成熟度等级（见下）
matchers:             # 技术栈检测规则（依赖优先于文件名）
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
  entity: []          # 数据实体/领域模型文件
  dto: []             # DTO/VO/Request/Response 文件
  ui: []              # 前端 UI 组件/页面文件
context_discovery:    # Context Pack 构建顺序；旧 profile 未填写时从 discovery_globs 推导
  project_map: []     # 项目地图：根配置、包管理、启动/测试命令、目录边界
  entrypoints: []     # 入口：route/controller/page/handler/command/job
  data_models: []     # 数据结构：schema/model/entity/dto/type/migration
  dependency_paths: [] # 依赖路径：service/repository/client/store/composable
  tests: []           # 测试入口：unit/integration/e2e/api
  configs: []         # 配置/权限：env/config/feature flag/permission
  exclude_patterns: [] # 排除项：dist/build/vendor/generated/cache 等
  high_frequency_pattern_check: string # 引用计数异常大时的验证策略提示
style_axes:           # 风格观察轴（结论需运行时从代码确认）
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

## Context Pack 规则

`context_discovery` 用来指导 agent 先找什么、后找什么，目标是拿到“刚好够用、刚好相关、可解释”的项目背景。

- 新 profile 应填写 `context_discovery`。
- 老 profile 若未填写，按 `discovery_globs` 推导：`api → entrypoints`，`entity/dto/migration/data_access → data_models`，`service/data_access → dependency_paths`，`test → tests`，`config → configs`。
- 每个候选文件或对象都必须标注相关性：3 直接修改候选，2 影响判断候选，1 背景参考，0 暂不纳入范围。
- Context Pack 必须记录排除项，避免把无关文件带入后续分析。
- 未完成 Context Pack 前，不得正式 light/full 定级。

## Level 定义

| Level | 含义 | 验收标准 |
|-------|------|---------|
| 1 | 基础覆盖 | 新技术栈先用 `generic` 完成首轮备用分析；随后在至少 1 个真实项目完成 full + light 双变更验收；能识别栈、找到主文件、给出来自项目证据的候选命令、说明发现方式、有 limitations；验收记录写入 `validation-runs/` |
| 2 | 深度覆盖 | 在至少 2 个真实项目或 1 个生产级项目中完成复验；积累了稳定风格轴、验证规则、失败前置条件和常见误判限制 |
| 3 | 成熟稳定 | 经多个生产级项目验证，limitations 已充分覆盖；full/light、负向、运行时验证和执行检查点均有通过证据 |

## Profile 晋级协议

新增或升级专属 profile 时，必须按顺序执行：

1. **generic 备用**：先用 `profiles/generic.md` 完成只读发现，记录命中证据和局限。
2. **候选 profile**：新增 profile 文件时，只写已验证的 matcher、glob、命令和限制；未知项写入 `notes.limitations`。
3. **双变更验收**：至少在一个真实项目完成 full + light 两类变更验收，记录技术栈规则选择证据、Context Pack、定级证据和验证方案。
4. **运行时验证**：能执行的 build/test/lint/typecheck 必须实际运行；无法运行时记录环境限制，不得写成已通过。
5. **记录归档**：新增 `validation-runs/Txx` 记录，并在 `README.md` / `VALIDATION.md` 更新 Level 说明。

禁止事项：

- 不能只因文件名或依赖命中就把新栈标成 Level 1。
- 不能把 generic 备用结果描述成专属 profile 已验证。
- 不能写未验证的命令、glob、目录结构或风格结论。
- 不能用 demo 项目的单一 happy path 覆盖生产级限制说明。

## matchers 打分规则

```
依赖命中: +3 分
文件命中: +1 分
目录命中: +1 分

最高分 profile 被选中。
无命中 → 加载 generic.md
```

## 写入规范

- 每个轴的值是「通常长什么样」的**提示**，明确标注「结论需运行时从代码确认」
- 不写未验证的 glob/command，验证前写进 `notes.limitations`
- 迁移文件（migration）glob 必须覆盖：SQL 脚本、Flyway、Liquibase、迁移工具配置
- 新增或升级 profile 时必须补充 `context_discovery`；暂时无法验证的条目写入 `notes.limitations`
