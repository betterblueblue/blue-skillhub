# Blue SkillHub

给用开源模型在现有系统上做有风险变更的人，配的工头和安检门。

开源模型已经便宜到人人用得起，也强到"能干活"，但还没强到"可托付"。这个仓库里的核心是两个 skill —— **ImpactRadar**（变更影响分析 + 门禁执行）和 **Pathfinder**（项目摸底 + 防幻觉）—— 不负责让弱模型变聪明，负责让它犯的错响亮、可修复，而不是安静地混进你的代码库。

核心思路：规则写在 prompt 里，模型可以忘、可以绕、可以迎合你；写进脚本里，exit code 不讲情面。这两个 skill 把资深工程师的变更纪律做成了机器可执行的门禁——模型可以偷懒，门禁不会。

每个目录都可以单独使用，不需要整套一起上。

## 项目定位

这套 skill 面向**已有项目的需求迭代**，不面向 0→1 新系统生成。它处理的是存量代码里的真实风险：字段/API/权限/配置变化会不会漏引用、破坏兼容、影响数据、绕过测试，或者在恢复会话时把旧确认当成新授权。

它也不是默认把所有需求都做重。简单需求走 light/快速通道，只保留最小影响分析、执行前检查和 Step 确认；复杂需求或高风险变更才触发 full 模式，输出更完整的需求、设计、实施和验证文档。

目标模型是**性价比高但不够稳的开源模型**。这些模型能写代码，但容易跳步骤、漏上下文、提前宣布完成。Pathfinder 和 ImpactRadar 的价值，是用项目地图、澄清问题、模板、执行记录和脚本门禁，把弱模型和强模型之间的执行差距尽量缩小。

对用户也尽量友好：你不需要会写复杂 prompt，也不需要先把需求拆成工程任务。模糊需求会先被 skill 通过代码取证和少量澄清问题收敛成低歧义、可执行、可验证的指令；真正要写文件或改代码时，再用 `确认 Step N` 明确授权。

每次 Pathfinder / Impact 收尾时，agent 会在最终回复里自动追加一段简短使用记录，记录模型、模式、验证结果、门禁是否拦住、最终结果和值得沉淀的问题。它默认只出现在对话里，不自动写文件；后续如果要沉淀成日志文件，再单独确认保存规则。

## 3 分钟 Quickstart

只想马上试用已有系统影响分析时，按这个最小路径走：

1. 安装 skill 到你的客户端目录。

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\intent-anchor" "$env:USERPROFILE\.claude\skills\intent-anchor" -Recurse -Force
```

Codex 用户把 `.claude\skills` 换成 `.codex\skills` 即可。完整安装路径见 [docs/install-and-verify-checklist.md](docs/install-and-verify-checklist.md)。

2. 在目标项目里先摸底，再做变更。

```text
/pathfinder
这个项目我刚接手，先帮我只读摸底。

/impact
我想删除 sys_user.remark 字段，先做影响分析，不要直接改代码。
```

`/impact` 支持多技术栈（Java/Spring/MyBatis、Node/Express/Prisma、Python/FastAPI、Go/Gin/GORM、前端框架等），Phase 2 自动探测技术栈并加载对应规则。如果已经知道项目结构，也可以跳过 `/pathfinder` 直接进 `/impact`。

3. 只在看到 Step 说明后确认写入。

```text
确认 Step 2
```

`继续`、`好的`、`全部确认` 都不算写入授权。Claude Code 用户可选启用 `.claude/hooks/impact-write-gate.*`，把这个规则补强到工具执行前。

## 里面有什么

### Prompt 工具箱

[prompt/](prompt/)

可以直接复制给 AI coding agent 的实用 Prompt，适合不需要完整 skill、但希望把常见协作要求说清楚的场景。目前收录[跨会话交接](prompt/session-handoff.md)、[卡住时重新梳理](prompt/stuck-reassessment.md)和[生成独立验收指令](prompt/independent-review-request.md)：分别用于保存跨会话上下文、停止无依据试错，以及把完整验收任务一次性交给新会话或其他 agent。

### 律刃

[claudecode行为规范/ruleblade/](claudecode行为规范/ruleblade/)

8 条给 AI 编码助手看的核心行为规则，外加一条面向用户的中文表达要求。重点不是"让它更聪明"，而是让它少猜、少乱改、先拿对上下文、先验证，也把话说得像自然中文。适合放到已有项目的 `CLAUDE.md`，也可以按需复制成 Codex 项目的 `AGENT.md`。

它是通用行为底座，不绑定具体开发流程：可以搭配 0→1 生成类 Skill、已有系统影响分析类 Skill，也可以单独用于修 bug、重构、补测试和普通编码任务。v3.2 的稳定性复测是在 GovShield 这种已有系统复杂流程变更里完成的，证明的是复杂流程检查能力，不代表它只能用于已有系统。v3.3 的补强验证是在低成本弱模型（Step 3.7 Flash）上完成的，确认五处改动对弱模型也有效。

最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续在中文任务、已有系统变更和 GovShield 复杂审查流程里持续实测迭代。v3.2 已通过 Claude Code + MiniMax M3 的 Task A 稳定性复测：R13 + R14 连续 2 轮无 P0/P1，最小测试通过。v3.3 的五处补强（停与不停阈值、去概念泄漏、验证等级调整、测试粒度匹配、客观条件清单替代"自行判断"）已通过 Step 3.7 Flash 的 6 场景验证，6/6 全部生效。详见 [claudecode行为规范/ruleblade/README.md](claudecode行为规范/ruleblade/README.md)。

### 网搜 MCP

[mcp/web-search-mcp/](mcp/web-search-mcp/)

给 AI 客户端接联网搜索用。支持 Google/Bing/Brave/DuckDuckGo，可以只拿搜索摘要，也可以继续打开网页提取正文。适合 Cursor、CodeBuddy、Claude Desktop 等支持 MCP 的客户端。

### Pathfinder 领航

[skills/pathfinder/](skills/pathfinder/)

**Impact 的导航输入。** 能做项目摸底的工具已经不少（codegraph MCP、IDE 代码库索引都在做），Pathfinder 真正独有的是防编造：每条结论强制标可信度标签（`【已核实: 证据】`/`【推断: 待验证】`）、非 Git 归属纪律、未覆盖项诚实声明。面向**刚接手、还不熟悉**的现有项目。它不做具体变更,而是先帮你通读一遍,产出一张全项目级的**认知地图**:技术栈、核心功能、架构分层、关键入口、数据模型概览、构建/运行/测试、风险区域、权限模型、典型主流程、文档入口。

它和 Impact 系列正好接力:Pathfinder 负责先看懂"这是个什么项目",Impact 的 Phase 2 负责深入分析"这次改动影响什么"。地图产出到 `change-impact/_project-map.md`,Impact 启动时会主动读它当 L1 导航上下文 —— 读不到就完全照旧,是可选的辅助工具,不是必须先跑的前置步骤。

项目演进后地图会过期,Pathfinder 支持三种刷新入口:继续深入某个模块、重新跑脚本比对项目变化、全量重跑。刷新时会比对已有地图的 git HEAD 与当前 HEAD,覆盖过期内容,保留仍有效的观察。

地图每条结论都带可信度标签(`【已核实】`/`【推断】`)、git HEAD(防过期)和覆盖度声明(显式列出没深入看的部分)。Impact 读取后,`【推断】`项一律按未确认处理、动手前重新取证 —— 地图只是导航参考,不是权威依据。Pathfinder 对项目本体只读、只描述不给修复建议；只写它自己管理的地图和 facts 文件。

如果客户端已有只读 code graph / repo-map MCP，Pathfinder 会先用结构索引找入口、依赖边和核心节点，再用 Read/Grep 核实；索引不可用、过期、截断或需要写项目缓存时，就退回到普通扫描。

律刃管判断、Impact 管改动、Pathfinder 管看懂项目 —— 先摸清项目再动手。设计复盘见 [docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md](docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md)。

### ImpactRadar

[skills/impact/](skills/impact/)

**核心产品。** 面向多技术栈现有系统（Java/Spring/MyBatis、Node/Express/Prisma、Python/FastAPI、Go/Gin/GORM、前端框架等）。它不是从 0 到 1 生成新项目，而是帮你在已有代码、表结构、接口和业务约束里，做一次功能迭代、新功能接入、字段/API/权限/配置变更或重构。22 项自动化门禁检查（V1-V22）确保弱模型犯的错尽量被拦住——D19 真实交付评测中，MiniMax M3 三次提前宣布"全部通过"，分别被三道不同门禁接住，最终修到可交付。技术栈专属规则位于 `profiles/`，Phase 2 自动探测并按需加载。

它可以搭配律刃使用：律刃约束 agent 的通用编码行为，ImpactRadar 负责多技术栈现有系统的影响分析流程。

v3.4 之后补了长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 项目保护、恢复后复核和多会话写授权一致性，适合迁移、对齐、重构等多 Step 变更。最新新增**风格规则文件**（`change-impact/_style-rules.md`）：用户把团队强制/建议规则写进去，Impact 在分析和校验时会读取并检查代码是否符合。优先级为：风格规则文件 > 地图观察 > Profile 提示 > 运行时采样；规则可以在实际变更中发现并追加，不要求预先写全。Claude Code + MiniMax M3 真实 `/impact` 复测已经走完 S1-S7 回归，模糊确认、历史确认、延迟确认、非 Git + V1-only、Health/API 响应字段变化都不能绕过 `确认 Step N`。

经过 V1-V10 共 10 轮盲测（3 个模型 × 6 个真实场景 × 有/无 skill 对照 = 100+ 份产出），skill 的核心价值可以归纳为：把模糊需求变成显式假设（V7 验证）、苏格拉底式提问不替用户拍板但自主推断代码事实（代码可推断项不问用户，业务决策项才问）、结构化保障（回滚方案、验证步骤、方法名预检始终做到）、防御性检查（refreshToken TTL 同步等独有发现）、安全检查（逐步确认、写入边界、高风险拦截，弱模型也绕不过）。当前版本 v5.8。2026-06-28 先做了一轮 5 模型端到端对比（Composer 2.5、Kimi K2.6、GLM-5.1、Step 3.7 Flash、GLM-5.2），选定 Composer 2.5 和 Step 3.7 Flash 作为性价比优化目标后，又做了 R1-R7 共 7 轮 Skill 模板优化验证（O1-O18 共 18 项优化措施），涵盖全局影响检查表 V10 脚本检查、Prisma ORM 异常行为参考、`_active-state.md` 存在性检查、§6/§3.2 标题防改名、弱引导下强制规则（context-pack 必产出、Phase 4 必跑验证脚本）、读路径 SQL 判 light 规则、脚本路径澄清、`_active-state.md` 模板结构强制、Phase 4/5 分步门禁 V13、源码写入前置检查门禁 V14、源码 Step 执行记录/状态文件门禁 V15（v5.6 起还会检查每个源码类 Git diff 是否被执行记录覆盖，v5.7 起 FAIL 文案包含具体修复步骤）、`_active-state.md` 状态一致性门禁 V16，以及任务验收冒烟检查 V17。2026-07-03 真实 Phase 5 复测发现 Composer 2.5 会出现“validator 全绿但代码少改一半”的情况，v5.6 已把 route meta `label/title` 半截改动转成脚本级 FAIL。v5.8 新增 Codex skill 元数据合规、Phase 4 写文档单独 Step 确认、收尾使用记录和 Pathfinder 地图消费记录 V22。`impact_validate.py` 现有 V1-V22 共 22 项自动化检查。详细数据见 [skills/impact/README.md](skills/impact/README.md)。

当前还接入了可选 code graph MCP 作为结构化定义/引用候选入口，以及 `change-impact/{需求名称}/_active-state.md` 作为跨会话恢复状态文件。`_active-state.md` 只记录 pending Step、文档状态和未确认项，不授权源码/SQL/配置/测试写入，也不能替代当前对话里的 `确认 Step N`。Claude Code 可选启用 `.claude/hooks/impact-write-gate.*`，把 Step 确认补强成工具执行前检查。

### IntentAnchor 意图锚定

[skills/intent-anchor/](skills/intent-anchor/)

**开发之前的意图保险栓。** Pathfinder 管看懂项目、Impact 管控执行，IntentAnchor 管的是更前面一步——你还没写 PRD、还没拆 issue 的时候，把模糊意图变成一份结构化的 INTENT.md，防止后续阶段（brainstorm → PRD → issue → 开发）偏离原始意图。

核心方法论是**三重锚定**：不问用户“你要什么”（人答不了抽象问题），而是问三个具体的——“有没有类似的东西？指给我看”（类比锚定）、“你现在怎么解决？最烦什么？”（反面锚定）、“假设做好了，你第一次打开它会先干什么？”（场景锚定）。至少完成 2/3 种，合并能力清单交用户标记。

它还做了**语义自检**（S1-S5）：不只检查文件格式，还要求 agent 重读源系统文件对比能力清单有没有遗漏、每条“保留”项有没有用户确认、三重锚定是不是真的做了。每步必须产出中间结果表格，不能一句话带过。产出后跑 `intent_validate.py`（9 项检查）校验完整性。

跟 Impact 的分工：IntentAnchor 防的是“规划偏离意图”（开发前），Impact 防的是“执行偏离规格”（开发中）。两者参考了相同的设计理念但独立运作，不需要配合使用。

这个 skill 诞生于一次失败复盘：用户走了一条看起来很规范的工作流（聊需求 → brainstorm → to-prd → to-issues → goal），每个环节执行质量都很高，但最后做出来的东西跟想要的不是一个东西——意图在阶段传递中逐级蒸发了。详细设计见 [skills/intent-anchor/README.md](skills/intent-anchor/README.md)。

### VL 识图

[skills/vl-vision/](skills/vl-vision/)

一个通用图片理解小工具。给它图片和模板，它会调用视觉模型返回结构化分析。适合让纯文本 AI 补上“看图”能力。

### 统一测评体系

[docs/skill-eval/](docs/skill-eval/) + [eval/](eval/)

两个 skill 共用的回归测评体系，用来防止质量退步。核心思路：**不新建测评方法，而是把已有的高质量测试用例整理成一套能定期复跑、自动发现质量下降的体系。**

三层金字塔：

| 层 | 测什么 | 怎么跑 | 成本 |
|---|---|---|---|
| L0 静态自洽 | 铁律存在、引用完整、共享契约、fixture 锁定、风格规则校验 | `bash skills/<skill>/tests/run.sh` | 免费 |
| L1 行为契约 | subagent 扮用户跑 case，客观维度自动评分 + 安全检查 | `bash eval/run-l1.sh <skill>` | 便宜模型 |
| L2 人审深度 | 主观维度（苏格拉底质量、文档/地图可读性）抽样 | 人工 + 可选多模型评委 | 贵 |

防止质量悄悄退步的关键机制是**基线评分卡 + 红线对比**：每次改 skill 后跑 L1，产出评分卡，和上一基线逐 case 对比；只要出现契约从 PASS→FAIL、维度掉档≥3 分或新增 P0/P1，就算红线，不能发布。详细设计见 [docs/archive/2026-06/2026-06-13-skill-eval-system-design.md](docs/archive/2026-06/2026-06-13-skill-eval-system-design.md)，实施手册见 [docs/archive/2026-06/2026-06-13-skill-eval-system-runbook.md](docs/archive/2026-06/2026-06-13-skill-eval-system-runbook.md)。

真实项目评测见 [eval/real-projects/](eval/real-projects/)。这里固定了 5 类项目（Java 后端、Node API、Python 全栈、前端、monorepo/非 Git），并新增真实交付矩阵：让弱模型在隔离副本里跑 Pathfinder、Impact Phase 4、Impact Phase 5、negative gate，记录 diff、验证命令、执行记录和失败修复循环。目标不是证明模型不会犯错，而是证明门禁能把错误拦住，并把模型拉回可交付状态。

已记录 10 种逃逸形态（E-001 到 E-010），全部有对应的 validator 检查或明确标注的边界。逃逸台账是"我们拦过什么"的证据清单，详见 [逃逸台账](eval/real-projects/escape-ledger.md)。评测手册见 [runbook.md](eval/real-projects/runbook.md)，其中明确：判分时以独立复跑 validator 的结果为准，不以 runner README 自报结果为准；每个 runner 每次运行使用物理隔离的 fixture 副本。

后续优化项统一记录在 [docs/skill-iteration-backlog.md](docs/skill-iteration-backlog.md)：P0 已落地项、等待真实日志再处理的 P1、产品化阶段再做的 P2 都放在那里，方便后续 agent 接着迭代。

基于 56 条已跑结果的跨模型对比，**Composer 2.5 Fast 是本套 skill 最推荐的主力弱模型**（22 条结果：9 PASS、7 GATE-RECOVERED、3 PASS-WARN、2 FAIL、1 UNVERIFIED）。GPT-5.4-mini（6 FAIL）和 MiniMax M3（2 FAIL）分别适合分析场景和简单分析，交付场景有风险。详细数据和结论见 [docs/handoff-summary-2026-07-04.md](docs/handoff-summary-2026-07-04.md)。

## 研究与实验记录

### Not ACE 上下文检索探索

2026 年 6 月围绕 [Not ACE](https://not-ace.ame.rip/) 做的一轮上下文检索实验，不是可安装 skill，而是用来判断 RuleBlade、ImpactRadar 后续怎么迭代的研究材料。完整记录在 [docs/not-ace-exploration/](docs/not-ace-exploration/)。

核心判断：Not ACE 不是 `rg` 的替代品，而是语义上下文入口。它对 MiniMax M3 更像在补稳定性，对 GLM-5.1 更像在省时间、省成本；但在 Kimi K2.6、GLM-5、DeepSeek V4 系列上这轮没跑出稳定收益。DeepSeek V4 Pro / Flash 经硅基流动平台接入，不代表 DeepSeek 官方模型真实能力。

相关文档（均在 `docs/` 下）：

- [archive/2026-06/impact-real-case-study.md](docs/archive/2026-06/impact-real-case-study.md) — ImpactRadar 真实使用案例复盘，暴露的长会话和多 Step 边界
- [archive/2026-06/impact-m3-next-regression-plan.md](docs/archive/2026-06/impact-m3-next-regression-plan.md) — 下一轮 MiniMax M3 复测计划
- [archive/2026-06/impact-multisession-write-gate-test-plan.md](docs/archive/2026-06/impact-multisession-write-gate-test-plan.md) — 多会话写授权一致性验收方案
- [archive/2026-06/release-positioning-check-2026-06-08.md](docs/archive/2026-06/release-positioning-check-2026-06-08.md) — RuleBlade、ImpactRadar 边界自洽性自查
- [archive/2026-06/not-ace-benchmark-research.md](docs/archive/2026-06/not-ace-benchmark-research.md) — Not ACE 在多个模型上的表现研究
- [archive/2026-06/agent-iteration-conclusions.md](docs/archive/2026-06/agent-iteration-conclusions.md) — 测试事实映射到三个 skill 的优化方向
- [skill-eval/regression.md](docs/skill-eval/regression.md) — ImpactRadar 优化后回归复测协议
- [archive/2026-06/benchmarks/](docs/archive/2026-06/benchmarks/) — 写授权回归夹具 + 模型 agent 能力评测（2026-06-09 后无活动，保留历史）

## 致谢

律刃最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续是在真实中文编码任务和复杂流程测试里一轮轮收紧出来的。

“改代码前先反查调用方和引用方，查到后再分级处理”来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提出的 issue。这个建议已经同步进 RuleBlade 和 ImpactRadar，用来减少只改当前文件却漏掉接口、生成物、测试或注册点的风险。

ImpactRadar 近期关于长期目标、阻塞恢复、接口返回检查、验证等级、多会话写授权、写入目标边界和连续 V1-only 暂停的补强，也来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提供的真实使用案例。这个案例暴露了长会话、多 Step 迁移、非 Git 项目、延迟确认和弱模型执行时更容易出现的边界问题。

## 快速验证

把仓库克隆到本地后，可以按下面几步确认工具能跑起来。

### 1. 使用律刃规则

把规则文件复制到目标项目根目录：

```powershell
Copy-Item "claudecode行为规范/ruleblade/CLAUDE.md" "你的项目路径/CLAUDE.md"
```

然后在目标项目里启动 Claude Code，确认它能读取根目录的 `CLAUDE.md`。

### 2. 启动网搜 MCP

先安装依赖和浏览器：

```powershell
cd mcp/web-search-mcp
npm install
npx playwright install chromium
node ./dist/index.js
```

看到下面两行，说明入口能启动：

```text
Web Search MCP Server started
Waiting for MCP messages...
```

配置 MCP 客户端时，`args` 要写本机绝对路径。例如当前仓库位置对应：

```json
{
  "mcpServers": {
    "web-search-mcp": {
      "command": "node",
      "args": ["E:\\agent\\blue-skillhub\\mcp\\web-search-mcp\\dist\\index.js"]
    }
  }
}
```

代理、搜索引擎和环境变量配置见 [mcp/web-search-mcp/README.md](mcp/web-search-mcp/README.md)。

### 3. 运行 VL 识图

先看可用模板：

```powershell
pip install requests
python skills/vl-vision/vl_vision.py --list-templates
```

配置 `SILICONFLOW_API_KEY` 后测试一张图片：

```powershell
$env:SILICONFLOW_API_KEY="sk-your-key"
python skills/vl-vision/vl_vision.py path/to/image.png
```

### 4. 安装 Pathfinder / Impact Skills

安装命令见上文 [3 分钟 Quickstart](#3-分钟-quickstart)，这里只补充使用时的关键边界。

几个边界要记住：

- `pathfinder` 面向刚接手的陌生项目,产全项目认知地图,项目本体只读、只描述不给修复建议；只写它自己管理的地图和 facts 文件。
- `impact` 面向多技术栈现有系统（Java/Spring/MyBatis、Node/Express/Prisma、Python/FastAPI、Go/Gin/GORM、前端框架等），Phase 2 自动探测技术栈并加载对应规则。
- 写文件、改代码、DDL/DML、配置变更、删除、测试修复,都必须由用户明确回复 `确认 Step N`。
- 不能用 `yes`、`继续`、`全部确认` 代替 Step 级确认。
- 中断后恢复时，`_active-state.md` 只能帮助复述 pending Step 和核验磁盘状态，不能当成授权。

恢复/确认的真实交互应长这样：

```text
用户：继续
Agent：我先读取 change-impact/删除用户备注/_active-state.md、030-implementation.md、
060-preflight.md 和 090-execution-record.md，并复核当前 Git/磁盘状态。
当前 pending_step 是 Step 2，但“继续”不是授权。Step 2 将修改
E:\project\ruoyi-system\src\main\resources\mapper\system\SysUserMapper.xml，
回滚方式是恢复该文件的字段映射，验证方式是 mapper 引用检查 + 对应测试。
请回复：确认 Step 2

用户：确认 Step 2
Agent：现在执行 Step 2；执行后会更新 090-execution-record.md 和 _active-state.md。
```

## 常见问题（FAQ）

- **Codegraph MCP 显示已连接但没有工具（No tools）**：原因是全局裸 `serve --mcp` 找不到项目根的 `.codegraph/` 索引。完整排查步骤（项目级 wrapper、`--path` 传参、确认 4 个工具）见 [docs/install-and-verify-checklist.md §Codegraph 排障](docs/install-and-verify-checklist.md#codegraph-mcp-显示已连接但没有工具no-tools)。

  Pathfinder / Impact 在 MCP 不可用时会退回到 Read/Grep，不影响基本流程。

## 目录速览

```text
blue-skillhub/
├── .claude/
│   └── hooks/                # 可选 Claude Code 写前检查 hook
├── claudecode行为规范/
│   └── ruleblade/
├── docs/
│   ├── skill-eval/          # 统一测评体系入口(含 REVALIDATION.md 复验体系)
│   ├── not-ace-exploration/
│   ├── archive/2026-06/     # 历史文档归档(含已迁出的 benchmarks/)
│   ├── install-and-verify-checklist.md
│   ├── output-quality-review-2026-06-25.md
│   └── skill-optimization-roadmap-2026-06-25.md
├── eval/                     # 测评体系：case 定义 + 跑分历史 + 基线
│   ├── cases/<skill>/        # 可复跑用例定义（与跑分历史分离）
│   ├── runs/<date>-<skill>@<commit>/  # 评分卡时间序列(含 runner_model)
│   ├── baselines/<skill>.json         # 当前基线指针
│   ├── schemas/              # case + scorecard JSON schema
│   └── scripts/              # diff_baseline.py / analyze_control.py(控制变量裁决)
├── mcp/
│   └── web-search-mcp/
└── skills/
    ├── pathfinder/
    ├── impact/
    ├── intent-anchor/
    └── vl-vision/
```
