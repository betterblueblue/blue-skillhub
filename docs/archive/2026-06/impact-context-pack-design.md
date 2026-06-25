# impact / impact-pro 上下文包能力设计复盘

> 这份文档用于复盘 `impact` / `impact-pro` 新增“上下文包”能力的完整过程。它重点回答：为什么提出这个需求、讨论中发现了什么问题、参考了哪些资料、最终怎么设计、实现后效果如何。

## 1. 一句话概括

我们把 `impact` / `impact-pro` 从“会做影响分析的 Skill”，升级成了“能指挥 agent 用固定方法拿到刚好够用、刚好相关、可解释上下文的影响分析 Skill”。

这次升级的核心不是让 agent 多读文件，而是让 agent 知道：

- 先读什么；
- 后读什么；
- 哪些内容真的相关；
- 哪些内容看过但不该继续带入；
- 什么时候该停止扩大上下文；
- 如何把上下文整理成后续 agent 可以接手的产物。

最终落地为 `Context Pack / 上下文包` 协议。

这里和 `RuleBlade` 的分工是分层的：`RuleBlade` 是通用编码行为底座，可用于 0→1 新系统开发、已有系统变更、重构、修 bug 和测试补充；`Context Pack` 是 `impact` / `impact-pro` 面向现有系统影响分析时的上下文收敛协议，负责把真实代码、schema、接口、配置和测试证据整理成后续 agent 能接手的变更上下文。

## 2. 为什么会提出这个需求

最初 `impact` / `impact-pro` 已经具备比较完整的影响分析流程：识别技术栈、发现代码和 schema、苏格拉底式澄清、light/full 判档、文档输出、执行前检查和逐 Step 确认。

但在反复测试和讨论中，我们发现一个更底层的问题：agent 做复杂代码变更时，失败往往不是因为“不会写代码”，而是因为上下文拿得不对。

常见问题包括：

| 问题 | 表现 | 后果 |
|------|------|------|
| 上下文过少 | 只读了一个文件或一个搜索结果 | 漏掉真实入口、配置、权限、测试或数据结构 |
| 上下文过多 | 把大量搜索结果、无关文件全塞进对话 | token 浪费，重点被噪音淹没 |
| 上下文不可解释 | 只说“我看了这些文件”，没说为什么相关 | 后续 agent 或人工复核很难接手 |
| 排除项缺失 | 看过但无关的文件没有记录 | 后续反复搜索同一批无关文件 |
| 判档过早 | 没完成上下文发现就决定 light/full | 高风险 DB/API/权限变更可能被误判为 light |
| profile 依赖临场发挥 | 多栈项目只靠 glob 推导上下文顺序 | 不同 agent 执行结果不稳定 |

所以这个需求本质上是：让 agent 在真正设计和写代码前，先拥有一套稳定的上下文获取协议。

## 3. 讨论过程中形成的关键判断

### 3.1 不是复制 ACE，而是吸收它的上下文思想

我们讨论过 Augment Code / ACE 为什么体验强。结论不是“模型更神”，而是它的上下文系统更强：它能更快找到相关代码、理解跨文件关系、减少无效搜索。

但我们也明确了边界：

- Augment 的 Context Engine 是产品级私有能力，包含语义索引、关系理解、多源索引、压缩等能力；
- 我们不依赖它的 key，也不复制私有实现；
- 我们要做的是一个本地可解释协议，让任何 agent 都能按规则拿到相对稳定的上下文包。

换句话说，我们不是做一个“低配搜索引擎”，而是做一个“上下文选择和交付规范”。

### 3.2 上下文不是越多越好

这次升级的核心价值是“刚好够用”：

- enough：足够支撑判档、设计、验证和回滚；
- relevant：只保留与本次变更相关的代码、schema、接口、配置和测试；
- explainable：每个纳入项都有理由，每个排除项也有理由。

如果 agent 不知道什么时候停止，它就会继续读更多文件；如果 agent 不记录为什么排除，它就会在后面重复走弯路。

### 3.3 light/full 判档不能发生在上下文包之前

之前我们已经讨论过：light/full 应该由 agent 基于证据先行建议，用户复核确认；用户可以升档或要求简化输出，但不能把已触发 full 的高风险变更降成跳过安全闸的 light。

这次进一步明确：正式判档必须发生在 `Context Pack` 和苏格拉底式澄清之后。

原因很简单：如果上下文还没收敛，agent 并不知道这个变更是否涉及 DB schema、API 契约、权限、状态机、缓存、消息队列或跨端联动。过早判档就是猜。

### 3.4 三个问题不是总上限，而是每轮上限

我们还讨论过苏格拉底式提问为什么不能永远只问 3 个问题。

最终规则是：

- 每轮最多 3 个问题，避免用户疲劳；
- light 通常 0-1 轮；
- full 通常 1-3 轮；
- 高风险场景最多 5 轮；
- 超过后不继续消耗用户耐心，而是输出“已确认 / 未确认 / 建议默认 / 必须用户拍板”。

这个原则和上下文包配合起来，形成一个平衡：只读操作自动收集证据，真正需要业务判断时再用少量问题问用户。

## 4. 查阅和参考的资料

这次参考的资料分为两类：外部产品资料和仓库内已有验证资料。

### 4.1 外部资料

主要参考 Augment Code 公开资料中关于 Context Engine / Context Engine MCP 的描述：

- [Augment Context Engine MCP 官方产品页](https://www.augmentcode.com/product/context-engine-mcp/)：强调语义代码搜索、减少无效 grep、减少 token、让 agent 更快拿到相关信息。
- [Augment Context Engine MCP 文档](https://docs.augmentcode.com/context-services/mcp/overview)：强调语义理解、跨文件关系、代码以外的上下文、智能筛选和压缩。
- [Augment Context Engine MCP 发布文章](https://www.augmentcode.com/blog/context-engine-mcp-now-live)：介绍把 Context Engine 通过 MCP 接给 Claude Code、Cursor、Codex 等工具，并强调上下文架构对 agent 质量的影响。
- [Augment Blog](https://www.augmentcode.com/blog)：用于观察它们对 AI-native 工程、agent 系统和上下文能力的整体叙述方式。

我们从这些资料中抽取了几个可落地的思想：

| 外部思想 | 本项目落地方式 |
|----------|----------------|
| 语义相关性比纯 grep 更重要 | 用相关性 3/2/1/0 强制 agent 解释为什么相关 |
| agent 不应浪费时间探索无关路径 | 加入上下文预算和排除项记录 |
| 跨文件关系很关键 | L2 变更邻域要求找入口、模型、依赖路径、配置和测试 |
| 上下文需要压缩而不是堆叠 | L3 精准证据限制深入文件数量和片段大小 |
| 多源上下文有价值 | 上下文包覆盖代码、schema、API、配置、权限、测试和命令 |

### 4.2 仓库内资料

本项目已有大量验证和规则文件，也成为这次设计的依据：

- `skills/impact/SKILL.md`
- `skills/impact-pro/SKILL.md`
- `skills/impact/VALIDATION.md`
- `skills/impact-pro/VALIDATION.md`
- `skills/impact-pro/profiles/_schema.md`
- `skills/impact-pro/profiles/*.md`
- `skills/impact-pro/validation-runs/`
- `skills/impact/validation-runs/`

其中 `impact-pro` 已经积累了多栈验证记录，包括 Java/RuoYi、Node/Prisma、FastAPI、Go/Gin/GORM、.NET/EF Core、React/Vite、Next.js、Nuxt/Vue、monorepo 和负向场景。上下文包协议是在这些测试暴露出的真实问题上抽象出来的，而不是凭空设计。

## 5. 最终决定怎么干

最终方案是给两个 Skill 都加入 `Context Pack / 上下文包`，并把它作为 Phase 2 的必需产物。

### 5.1 新流程

升级后的主流程变成：

```text
Phase 1 意图捕获
   → Phase 2 上下文包构建
   → Phase 2.5 初步风险预判
   → Phase 3 苏格拉底式探索
   → Phase 3.5 正式 light/full 判档
   → Phase 4 文档输出
   → Phase 5 执行与验证
```

关键变化是：Phase 2 不再只是“上下文发现”，而是必须产出一个结构化上下文包草案。

### 5.2 三层探索模型

上下文包采用三层结构：

| 层级 | 目标 | 例子 |
|------|------|------|
| L1 项目地图 | 先搞清项目和模块边界 | 技术栈、根配置、启动命令、测试命令、主要目录 |
| L2 变更邻域 | 找到围绕本次变更的相关对象 | API 入口、Controller、Service、Model、Mapper、schema、UI、测试 |
| L3 精准证据 | 只深入阅读真正影响设计的片段 | 状态机、权限校验、事务边界、DTO 字段、迁移脚本、测试断言 |

这套模型解决的是“从哪里开始”和“什么时候深入”的问题。

### 5.3 相关性分级

每个候选文件、表、接口或配置项都必须打分：

| 分值 | 含义 | 用途 |
|------|------|------|
| 3 | 直接修改候选 | 本次大概率要改 |
| 2 | 影响判断候选 | 不一定改，但影响设计、判档或验证 |
| 1 | 背景参考 | 只用于理解风格、约定或历史模式 |
| 0 | 暂不纳入范围 | 看过但与本次无关，必须说明排除原因 |

这个设计让上下文包不是文件清单，而是经过筛选的上下文交付物。

### 5.4 上下文预算

为避免 agent 无限扩张读取范围，默认预算是：

- L1 项目地图：最多 10 个文件或命令输出摘要；
- L2 变更邻域：最多 15 个候选文件/对象；
- L3 精准证据：最多深入阅读 6 个文件或关键片段；
- 每个证据片段控制在 80 行以内。

超过预算时，不继续盲目扩大读取范围，而是先问用户最多 3 个收敛问题。

### 5.5 先对话草案，确认后再写文件

上下文包虽然是必需产物，但它仍然遵守写操作门禁：

- Phase 2 结束前，先在对话中输出上下文包草案；
- 只有进入 Phase 4 且用户确认写文档后，才写入 `change-impact/{需求名称}/000-context-pack.md`；
- `060-preflight.md` 中也加入上下文包确认项。

这保证了“上下文包强制存在”和“写文件必须确认”不冲突。

## 6. impact 和 impact-pro 的差异

### 6.1 impact

`impact` 面向 Java/Spring/MyBatis/RuoYi 类现有系统。

它的上下文包更偏 Java 后端和管理系统变更：

- Controller；
- Service / ServiceImpl；
- Mapper / Mapper XML；
- Entity / DTO / VO；
- application 配置；
- SQL / migration；
- Java 测试；
- DB schema 和 MCP 数据库能力探测。

对应实现：

- `skills/impact/SKILL.md`
- `skills/impact/templates/000-context-pack.md`
- `skills/impact/VALIDATION.md`
- `skills/impact/validation-runs/2026-06-07-T03-context-pack-protocol.md`

### 6.2 impact-pro

`impact-pro` 是多栈通用版本。

它的关键不是把所有栈写死在一个巨大 prompt 里，而是：

- 通用内核不预设技术栈；
- Phase 2 先探测技术栈；
- 按需加载 `profiles/` 中的技术栈规则；
- 每个内置 profile 都显式提供 `context_discovery`；
- 未知栈先走 `generic` 兜底；
- 新栈必须经过真实项目验收后才能升级 profile Level。

对应实现：

- `skills/impact-pro/SKILL.md`
- `skills/impact-pro/templates/000-context-pack.md`
- `skills/impact-pro/profiles/_schema.md`
- `skills/impact-pro/profiles/_template.md`
- `skills/impact-pro/profiles/*.md`
- `skills/impact-pro/VALIDATION.md`
- `skills/impact-pro/validation-runs/2026-06-07-T46-context-pack-protocol.md`

## 7. 具体实现了什么

### 7.1 新增上下文包模板

新增文件：

- `skills/impact/templates/000-context-pack.md`
- `skills/impact-pro/templates/000-context-pack.md`

模板包含：

- 变更意图；
- 当前假设；
- 技术栈和 profile；
- L1/L2/L3 分层上下文；
- 相关文件和对象；
- 相关性分级；
- 接口、数据结构、配置、权限、测试；
- 已确认事实；
- 待确认问题；
- 暂不纳入范围；
- 上下文预算。

### 7.2 修改 Skill 主流程

两个 `SKILL.md` 都加入了：

- Phase 2 上下文包构建；
- Phase 2 结束前必须输出上下文包草案；
- 未完成上下文包前不得正式 light/full 判档；
- 超出上下文预算时先问收敛问题；
- 写入 `000-context-pack.md` 前必须用户确认。

### 7.3 修改 full / light 文档模板

为了让上下文包不是孤立文件，还把它接进了后续文档：

- full 需求文档增加上下文包摘要；
- full 设计文档增加上下文包摘要；
- light 摘要增加上下文包摘要；
- phase5 preflight 增加上下文包确认项。

这保证了上下文包会贯穿“需求 → 设计 → 实施 → 执行”。

### 7.4 给 profile 增加 context_discovery

`impact-pro` 的 profile schema 新增：

```yaml
context_discovery:
  project_map: []
  entrypoints: []
  data_models: []
  dependency_paths: []
  tests: []
  configs: []
  exclude_patterns: []
```

并且 9 个内置 profile 已全部显式补充：

- `generic`
- `java-spring-mybatis`
- `node-express-prisma`
- `python-fastapi-sqlmodel`
- `go-gin-gorm`
- `dotnet-aspnet-efcore`
- `frontend-react-vite`
- `frontend-nextjs`
- `frontend-nuxt-vue`

这样 agent 面对不同技术栈时，不需要临场猜测“先看什么”，而是按 profile 明确顺序收敛上下文。

### 7.5 更新验收标准

验收文档新增或强化：

- 上下文包必须包含 L1/L2/L3；
- 必须包含相关性 3/2/1/0；
- 必须包含已确认事实、待确认问题、暂不纳入范围和预算；
- 高风险变更没有上下文包可判 P0/P1；
- 未完成上下文包就正式判档属于失败；
- 内置 profile 必须显式提供 `context_discovery`。

## 8. 实现后的效果

### 8.1 agent 的行为更稳定

升级前，agent 可能这样做：

```text
搜索关键词 → 打开几个文件 → 根据感觉判断影响面 → 开始写设计
```

升级后，agent 必须这样做：

```text
L1 项目地图
→ L2 变更邻域
→ L3 精准证据
→ 标注相关性 3/2/1/0
→ 写清纳入和排除原因
→ 输出上下文包草案
→ 再进入风险预判和澄清
```

这把“靠经验探索”变成了“按协议探索”。

### 8.2 后续 agent 更容易接手

上下文包不是写给当前 agent 自己看的，而是写给后续执行者看的。

后续 agent 可以直接看到：

- 本次变更真正相关的文件有哪些；
- 哪些文件只是背景参考；
- 哪些文件已经排除；
- 哪些事实已经确认；
- 哪些问题还不能猜；
- 验证入口在哪里；
- 上下文预算用了多少。

这减少了线程切换、模型切换、subagent 接力时的上下文损耗。

### 8.3 更能防止臆测

上下文包强制区分：

- 已确认事实；
- 待确认问题；
- 不采用的推断；
- 暂不纳入范围。

这会压制 LLM 常见问题：找不到证据时编造接口、表结构、字段含义、测试命令或项目风格。

### 8.4 更适合多栈项目

`impact-pro` 最容易出问题的地方是多技术栈上下文差异巨大：

- Java 要看 Controller / Service / Mapper / XML；
- Prisma 要看 schema.prisma / migrations / routes / tests；
- FastAPI 要看 routes / SQLModel / Alembic / deps；
- Go 要看 routers / models / serializers / database；
- .NET 要看 Program / Controller / DbContext / Entity / Migration；
- React/Vite 要看 routes / components / generated client / tests；
- Next.js 要区分 Server Component、Client Component、Route Handler、Server Action；
- Nuxt/Vue 要区分 pages、components、composables、server API、SSR/CSR 边界。

显式 `context_discovery` 让不同栈有自己的上下文入口顺序，而不是统一用一个粗糙规则扫全仓。

## 9. 验证方式和证据

### 9.1 提交记录

本次上下文包能力主要由两次提交落地：

```text
fda6459 补充影响分析上下文包协议
2d0f6ae 显式补充各技术栈上下文发现顺序
```

### 9.2 静态验证

已执行过的验证包括：

```powershell
git diff --check -- skills/impact skills/impact-pro
```

用于检查 Markdown / YAML / 空白格式没有明显错误。

还验证了两个 `SKILL.md` 的 YAML front matter 能解析，避免再次出现 YAML 块语法错误。

### 9.3 profile YAML 验证

对 `skills/impact-pro/profiles/*.md` 中的 `context_discovery` 做了解析检查，确认 9 个内置 profile 都包含：

- `project_map`
- `entrypoints`
- `data_models`
- `dependency_paths`
- `tests`
- `configs`
- `exclude_patterns`

验证结论：

```text
all bundled profiles context_discovery OK: 9
```

### 9.4 目标审计

最后按目标逐项审计：

| 目标要求 | 当前证据 | 结论 |
|----------|----------|------|
| impact 有固定上下文方法 | `skills/impact/SKILL.md` Phase 2 + `templates/000-context-pack.md` | 达到 |
| impact-pro 有固定上下文方法 | `skills/impact-pro/SKILL.md` Phase 2 + `templates/000-context-pack.md` | 达到 |
| 上下文刚好够用 | L1/L2/L3 + 上下文预算 | 达到 |
| 上下文刚好相关 | 相关性 3/2/1/0 + 暂不纳入范围 | 达到 |
| 上下文可解释 | 为什么相关、已确认事实、待确认问题、排除原因 | 达到 |
| 多栈能稳定执行 | 9 个内置 profile 显式 `context_discovery` | 达到 |
| 不跳过安全闸 | 未完成上下文包前不得正式判档；写入需确认 | 达到 |

## 10. 这个设计和普通 RAG / grep 的区别

| 方案 | 特点 | 局限 |
|------|------|------|
| grep | 快，精确匹配文本 | 不知道业务相关性，不会解释为什么相关 |
| 普通 RAG | 能召回语义相关片段 | 容易缺少项目结构、写操作门禁和工程流程约束 |
| 全仓扫描 | 看起来全面 | token 成本高，噪音多，容易淹没重点 |
| Context Pack | 分层收敛、预算控制、相关性解释、可交接 | 需要 agent 严格执行协议；语义召回能力仍取决于工具 |

因此，Context Pack 更像是“工程化上下文选择协议”，不是单一检索工具。

## 11. 后续还能怎么增强

这次已经达成可用版本，但后续还可以继续演进：

| 方向 | 说明 |
|------|------|
| 自动评分 | 对上下文包质量打分，比如覆盖度、相关性、排除项完整度 |
| 真实对话复测 | 用 subagent 跑更多真实需求，验证上下文包是否真的减少误判 |
| profile Level 绑定 | profile 晋级时强制附带 Context Pack 样例 |
| 运行时证据增强 | 把测试结果、构建结果、DB introspection 结果更结构化地接入上下文包 |
| 可视化 | 把 L1/L2/L3 和相关性分级画成影响图 |
| 自动裁剪 | 当上下文超预算时，自动给出“保留/丢弃/需用户确认”的裁剪建议 |

## 12. 最终结论

这次新增的上下文包能力，让 `impact` / `impact-pro` 从“能做影响分析”进一步升级为“能治理 agent 获取上下文的方式”。

它解决的是 AI coding agent 落地中的一个关键问题：复杂变更前，agent 到底应该看哪些文件、相信哪些证据、排除哪些噪音、何时停止探索、如何让下一个 agent 接手。

这不是简单写 prompt，而是围绕 LLM 工程化缺陷，设计了一套可执行、可验证、可交接的上下文协议。
