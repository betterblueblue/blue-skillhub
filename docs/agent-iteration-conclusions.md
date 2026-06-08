# 面向后续 Agent 的迭代结论

本文档给后续继续迭代 Blue SkillHub 的 agent 使用。重点不是复述 Not ACE benchmark，而是把测试事实转化为对本仓库核心资产的迭代判断：

- `claudecode行为规范/ruleblade/CLAUDE.md`
- `skills/impact/`
- `skills/impact-pro/`
- `skills/vl-vision/`

## 总结论

本仓库的核心方向是正确的：不要试图让模型“凭聪明”完成已有系统变更，而要用规则和 skill 把 agent 固定在 **上下文先行、证据化影响分析、边界文件验证、逐步确认、最小修改** 的轨道上。

Not ACE benchmark 进一步证明了一点：

> 更强的上下文入口可以提升 agent 表现，但不能替代规则、验证和边界扫描。这个仓库里的 RuleBlade、ImpactRadar、ImpactRadar Pro 应继续扮演“流程约束与证据门禁”的角色。

## 已被测试事实支持的设计

### 1. `CLAUDE.md` 的“上下文先行”是核心规则，不是装饰

`CLAUDE.md` 第 2 条要求 agent 在实现前确认项目入口、模块边界、注册点、生成物、测试入口，并对复杂链路先输出覆盖表。

这条规则被 Not ACE benchmark 强化支持。

测试事实：

- 在 `go-story-origin` 任务中，关键文件不只包括 `articles/models.go`、`articles/validators.go`、`articles/serializers.go`、`articles/routers.go`，还包括 `hello.go`。
- `hello.go` 是 Go Gin RealWorld 样本项目的入口和 GORM AutoMigrate 边界。
- MiniMax M3（下文简称 M3）+ `rg` 原始 r1 漏掉 `hello.go`，P0 recall 0.800，overall recall 0.833。
- M3 + Not ACE 三轮都命中 `hello.go`，P0/overall recall 均为 1.000。
- GLM-5.1 + `rg` 和 GLM-5.1 + Not ACE 在 Go 复跑中都 3/3 命中 `hello.go`，说明强模型可以靠常规工具补上，但成本差异显著。

对仓库迭代的结论：

- `CLAUDE.md` 里的“注册点、生成物、测试入口、边界文件”要求必须保留。
- 后续不要把上下文规则简化成“找到业务文件即可”。
- 对 DB/API/权限/状态机/生成物/测试这类变更，必须继续要求覆盖表。
- 可以进一步把“结构边界文件”写得更明确，例如：入口文件、migration/AutoMigrate、路由注册、generated client、权限注册、测试 fixture。

### 2. RuleBlade 不是模型能力的重复，而是模型波动的稳定器

`CLAUDE.md` 的价值不是让强模型更会写代码，而是减少不同模型和不同运行路径下的波动。

测试事实：

- M3 + `rg` 在同一 Go 语义任务上 3 次运行表现不完全稳定：`hello.go` 命中 2/3。
- M3 + Not ACE 在同一任务上 `hello.go` 命中 3/3，P0/overall recall 都为 1.000。
- Kimi K2.6 + `rg` 在 pilot 中优于 Kimi + Not ACE，说明“加语义工具”并不必然提升表现。
- GLM-5 + Not ACE 没有正收益，GLM-5.1 + Not ACE 有明显正收益，说明收益依赖模型和 harness。

对仓库迭代的结论：

- RuleBlade 不应绑定某一个模型或某一个工具。
- 规则要继续保持模型无关：要求证据、引用、边界、验证，而不是假设某个模型或 MCP 总是可靠。
- 后续可以增加“工具结果必须二次验证”的表述：Not ACE、搜索 MCP、DB MCP 都只能提供候选证据，不能直接当最终结论。

### 3. `impact` 的 Java/RuoYi 专项定位是合理的

`skills/impact/` 面向 Java/Spring/MyBatis/RuoYi，强调 schema、Controller、Service、Mapper、XML、权限、前端、测试等链路。

Not ACE agent benchmark 中的 `ruoyi-permission-chain` 任务证明了 RuoYi 权限链路非常容易漏边界。

测试事实：

- Kimi K2.6 + `rg` 和 Kimi K2.6 + Not ACE 在 RuoYi 任务上都漏了 `SysPermissionService.java`、`UserDetailsServiceImpl.java`、`PermissionContextHolder.java` 等 expected 文件。
- GLM-5 + Not ACE 在 RuoYi 任务中也漏了 `PermissionContextHolder.java`，overall recall 下降到 0.636。
- RuoYi 权限链路涉及后端权限字符串、`@PreAuthorize`、权限加载、数据范围、前端 route metadata、Vuex permissions、`v-hasPermi`。

对仓库迭代的结论：

- `impact` 继续保留 Java/RuoYi 专项规则，不应完全并入通用规则。
- RuoYi profile 应继续强调权限字符串、`PermissionContextHolder`、`DataScopeAspect`、前端 `v-hasPermi`、Vuex permissions、router metadata。
- 对权限类任务，必须强制“后端授权 + 数据范围 + 前端可见性”三段覆盖，不能只看 controller 注解或按钮 directive。

### 4. `impact-pro` 的 profile 化设计被多栈测试支持

`skills/impact-pro/` 把通用流程和技术栈 profile 分开，支持 Go、FastAPI、React、Next.js、Nuxt、.NET、Node/Prisma 等。

Not ACE benchmark 说明，不同技术栈的关键边界完全不同，靠单一通用搜索规则不够。

测试事实：

- Go 任务的关键边界是 `hello.go` 的 AutoMigrate。
- FastAPI + React 任务的关键链路包括 `backend/app/models.py`、`backend/app/api/routes/items.py`、前端 Add/Edit form、table columns、generated client、schema、tests。
- RuoYi 任务的关键链路包括后端权限服务、数据范围、前端权限 directive、route/store/getters。
- GLM-5.1 + Not ACE 在 Go 任务中能保持 3/3 full recall 并降低平均耗时；但 GLM-5、Kimi、DeepSeek 的表现不同，说明 profile 规则仍应作为稳定兜底。

对仓库迭代的结论：

- `impact-pro` 的 profile 机制应继续增强，不要退回单一 generic 规则。
- Go profile 应明确要求扫描入口/migration 边界，例如 `main.go`、`hello.go`、`AutoMigrate`、migration 目录。
- FastAPI/React profile 应明确要求 generated client/schema、form/table、backend tests、frontend tests。
- 权限链路应考虑独立 profile 或在 Java/RuoYi profile 中加强。

### 5. Context Pack 是值得继续做的能力

`impact` 和 `impact-pro` 都已经有 `context-pack.md` 模板。Not ACE benchmark 证明语义入口有价值，但也暴露了原始工具结果过大和模型适配不稳的问题。

测试事实：

- DeepSeek V4 Flash 会调用 Not ACE MCP，但 Not ACE 返回 116.5KB 大结果后，下一轮 API 400。
- DeepSeek V4 Flash 在 `stream-json` 简单任务中可用，但直接吃 Not ACE 大结果不稳定。
- 本轮 DeepSeek V4 Pro / Flash 通过硅基流动平台接入，不能代表 DeepSeek 官方模型在官方服务或其他接入方式下的真实能力。
- GLM-5.1 + Not ACE 在 Go 复跑中保持 1.000 recall，并把平均耗时从 424.303s 降到 199.295s。
- M3 + Not ACE 在 Go 复跑中把 `hello.go` 命中从 2/3 提升到 3/3。

对仓库迭代的结论：

- Context Pack 不应只是“搜索结果堆叠”，而应是压缩后的证据包。
- Context Pack 应包含：候选文件、相关性等级、为什么纳入、必须验证的边界、明确排除项。
- 对弱 harness 或国产模型，尤其要限制工具结果大小。
- 可以考虑给 `impact-pro` 增加“语义召回结果压缩协议”：Not ACE/search MCP top-N 先压缩，再交给 agent 做影响分析。

### 6. `vl-vision` 方向与仓库主线兼容，但应保持工具型定位

`skills/vl-vision/` 解决的是纯文本 agent 看不了图的问题，提供 OCR、布局分析、UI 截图还原、报错截图分析等能力。

这次 Not ACE benchmark 不是视觉任务，不能直接证明 `vl-vision` 的效果。但它支持一个共同设计原则：

> 外部工具负责补齐模型缺口，RuleBlade/Skill 负责把工具结果转成可验证证据，而不是让模型直接信任工具输出。

对仓库迭代的结论：

- `vl-vision` 应保持“获取视觉证据”的工具定位。
- 视觉结果应像 Not ACE 结果一样进入证据包，而不是直接变成最终事实。
- 对 UI 变更类任务，`vl-vision` 可以和 `impact-pro` frontend profile 联动：截图 OCR/layout → 影响分析 → 验证计划。

## 后续迭代建议

### A. 强化 RuleBlade 的边界文件清单

建议在 `CLAUDE.md` 的“上下文先行”中增加更明确的边界示例：

- 入口文件：`main.go`、`hello.go`、`app.py`、`Program.cs`
- migration：Alembic、Prisma migration、GORM AutoMigrate、EF Core migration
- 路由注册：router、controller mapping、frontend route
- generated artifacts：OpenAPI client、schemas、SDK、types
- 权限注册：permission string、route metadata、directive、data scope
- 测试入口：unit test、fixture、E2E spec、Postman collection

依据：

- `go-story-origin` 中 `hello.go` 是区分普通业务文件召回和完整链路召回的关键 P0。
- FastAPI case 中 generated client/schema 和 tests 是多组模型容易漏的 P1/P2 边界。

### B. 给 `impact-pro` 增加“语义召回压缩”步骤

建议在 Phase 2 增加可选步骤：

```text
如果有 Not ACE / semantic search MCP：
1. 先作为 L2 候选召回，不直接当事实。
2. 只保留 top-N 文件路径、score、一句话原因。
3. 对每个候选用 rg/read 验证真实引用。
4. 补做 mandatory boundary scan。
5. 写入 context-pack，而不是把原始大结果塞进上下文。
```

依据：

- GLM-5.1 + Not ACE 在 Go 复跑中显著降低耗时和成本。
- DeepSeek V4 Flash 被 Not ACE 116.5KB 大结果触发 API 400。
- Kimi/GLM-5 说明语义召回可能过早收窄，必须强制 boundary scan。

### C. 为 M3 类中等模型增加“结构边界强制核查”

建议对 `impact-pro` 的中高风险任务增加一条 gate：

```text
如果模型或工具链属于中等能力组合，且任务涉及 DB/API/序列化/测试：
必须显式核查入口/迁移/注册/测试边界。
未找到要写“未找到”，不能跳过。
```

依据：

- M3 + `rg` 在 Go r1 漏 `hello.go`。
- M3 + Not ACE 3/3 命中 `hello.go`，说明语义入口可缓解，但规则仍应兜底。

### D. 区分“稳定性收益”和“效率收益”

后续验证文档不要只写“效果更好”，要区分收益类型：

| 收益类型 | 观察指标 |
| --- | --- |
| 稳定性收益 | P0 recall、关键边界命中率、hallucination 降低 |
| 效率收益 | elapsed、cost、file reads、search calls |
| 质量收益 | analysis quality、plan correctness、verification coverage |

依据：

- M3 + Not ACE：主要是稳定性收益。
- GLM-5.1 + Not ACE：主要是效率/成本收益。
- Kimi/GLM-5：未显示正收益。

### E. 不要把 Not ACE 写成硬依赖

本仓库不应假设用户一定有 Not ACE。

合理策略：

- 有 Not ACE：作为 semantic entry 使用。
- 无 Not ACE：使用 `rg` / `git grep` / 文件结构 / profile 规则。
- Not ACE 返回过大或失败：降级为常规工具，标注工具失败。

依据：

- DeepSeek V4 Flash + Not ACE 大结果失败。
- `rg` 在 exact symbol 和验证阶段仍然非常强。
- GLM-5.1 + `rg` 本身也能达到 full recall，只是更慢更贵。

## 给后续 Agent 的执行准则

后续修改本仓库时，请遵守以下结论：

1. 不要削弱 `CLAUDE.md` 的上下文先行、边界扫描、精准修改和验证要求。
2. 不要把 `impact` 和 `impact-pro` 简化成普通搜索模板；它们的价值在证据化流程和确认门禁。
3. 不要把 Not ACE 或任何 semantic search 当作事实源；它只能提供候选上下文。
4. 修改 `impact-pro` profile 时，要用真实测试任务证明该 profile 能找到结构边界。
5. 对 Go profile，必须保留入口/migration/AutoMigrate 边界扫描。
6. 对 FastAPI/React profile，必须保留 generated client/schema/form/table/test 链路。
7. 对 RuoYi/权限任务，必须覆盖后端权限、数据范围、前端权限可见性。
8. 对视觉任务，`vl-vision` 输出必须作为证据输入，而不是未经验证的最终事实。

## 当前最值得继续做的功能

优先级从高到低：

1. 在 `impact-pro` 中加入 semantic context pack 压缩协议。
2. 强化 Go profile 的 entrypoint/migration boundary scan。
3. 强化 FastAPI/React profile 的 generated client/schema/test scan。
4. 强化 Java/RuoYi 权限链路 profile，尤其 `PermissionContextHolder` 和 data scope。
5. 设计一个统一的 context-pack scorecard：P0/P1/P2 recall、boundary hits、noise、elapsed、cost。
6. 让 `vl-vision` 的截图分析结果能进入 context-pack 模板。

## 事实来源

本结论引用以下本仓库文档和外部实验结果：

- `docs/not-ace-exploration/agent-benchmarks.md`
- `docs/not-ace-exploration/timeline.md`
- `docs/not-ace-benchmark-research.md`
- `E:\agent\not-ace-benchmark\v3-agent-benchmark\v3.6-glm51-go-repeat-report.md`
- `E:\agent\not-ace-benchmark\v3-agent-benchmark\v3.7-m3-go-repeat-report.md`
- `E:\agent\not-ace-benchmark\v3-agent-benchmark\v3.2-kimi26-report.md`
- `E:\agent\not-ace-benchmark\v3-agent-benchmark\v3.5-glm5-report.md`
- `E:\agent\not-ace-benchmark\v3-agent-benchmark\v3.4-deepseek-v4-flash-sanity.md`
