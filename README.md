# Blue SkillHub

这是我的 AI 工具箱。

日常用 AI 写代码时，有几个问题会反复出现：它有时会猜、会多改、不会主动查资料、看不了图，刚接手一个陌生项目时很难快速看懂全貌，也很难在已有系统里稳稳地做一次变更。这个仓库就是围绕这些问题攒出来的一组工具和规则。

每个目录都可以单独使用，不需要整套一起上。

## 3 分钟 Quickstart

只想马上试用已有系统影响分析时，按这个最小路径走：

1. 安装 skill 到你的客户端目录。

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
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

### 律刃

[claudecode行为规范/ruleblade/](claudecode行为规范/ruleblade/)

8 条给 AI 编码助手看的核心行为规则，外加一条面向用户的中文表达要求。重点不是"让它更聪明"，而是让它少猜、少乱改、先拿对上下文、先验证，也把话说得像自然中文。适合放到已有项目的 `CLAUDE.md`，也可以按需复制成 Codex 项目的 `AGENT.md`。

它是通用行为底座，不绑定具体开发流程：可以搭配 0→1 生成类 Skill、已有系统影响分析类 Skill，也可以单独用于修 bug、重构、补测试和普通编码任务。v3.2 的稳定性复测是在 GovShield 这种已有系统复杂链路变更里完成的，证明的是复杂链路门禁能力，不代表它只能用于已有系统。v3.3 的补强验证是在低成本弱模型（Step 3.7 Flash）上完成的，确认五处改动对弱模型也有效。

最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续在中文任务、已有系统变更和 GovShield 复杂审查链路里持续实测迭代。v3.2 已通过 Claude Code + MiniMax M3 的 Task A 稳定性复测：R13 + R14 连续 2 轮无 P0/P1，最小测试通过。v3.3 的五处补强（停vs不停阈值、去概念泄漏、验证降级、测试粒度匹配、客观条件清单替代"自行判断"）已通过 Step 3.7 Flash 的 6 场景验证，6/6 全部生效。详见 [claudecode行为规范/ruleblade/README.md](claudecode行为规范/ruleblade/README.md)。

### 网搜 MCP

[mcp/web-search-mcp/](mcp/web-search-mcp/)

给 AI 客户端接联网搜索用。支持 Google/Bing/Brave/DuckDuckGo，可以只拿搜索摘要，也可以继续打开网页提取正文。适合 Cursor、CodeBuddy、Claude Desktop 等支持 MCP 的客户端。

### Pathfinder 领航

[skills/pathfinder/](skills/pathfinder/)

面向**刚接手、还不熟悉**的现有项目。它不做具体变更,而是先帮你通读一遍,产出一张全项目级的**认知地图**:技术栈、核心功能、架构分层、关键入口、数据模型概览、构建/运行/测试、雷区、权限模型、典型主链路、文档入口。

它和 Impact 系列正好接力:Pathfinder 管**全景广度**(看懂这是个什么项目),Impact 的 Phase 2 管**变更切片深度**(看懂这次改动影响什么)。地图产出到 `change-impact/_project-map.md`,Impact 启动时会主动读它当 L1 导航上下文 —— 读不到就完全照旧,是可选加速器不是前置必跑项。

项目演进后地图会过期,Pathfinder 支持三种刷新入口:扩展深度(再挖某个模块)、刷新事实(项目变了,重新跑 facts 比对差异)、全量重跑。刷新时会比对已有地图的 git HEAD 与当前 HEAD,覆盖过期内容,保留仍有效的观察。

地图每条结论都带信任标签(`【已核实】`/`【推断】`)、git HEAD(防过期)和覆盖度声明(显式列出没挖深的盲区)。Impact 接过去时,`【推断】`项一律按未确认处理、动手前重新取证 —— 地图是导航图不是权威源。Pathfinder 全程 100% 只读、只描述不开药方。

如果客户端已有只读 code graph / repo-map MCP，Pathfinder 会先用结构索引找入口、依赖边和核心 hubs，再用 Read/Grep 核证；索引不可用、过期、截断或需要写项目缓存时，诚实降级普通扫描。

如果说律刃管 AI 的**脑子**、Impact 管 AI 的**手**,那 Pathfinder 管的是 AI 的**眼睛** —— 先看懂,才谈得上动手。设计复盘见 [docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md](docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md)。

### ImpactRadar

[skills/impact/](skills/impact/)

面向多技术栈现有系统（Java/Spring/MyBatis、Node/Express/Prisma、Python/FastAPI、Go/Gin/GORM、前端框架等）。它不是从 0 到 1 生成新项目，而是帮你在已有代码、表结构、接口和业务约束里，做一次功能迭代、新功能接入、字段/API/权限/配置变更或重构。技术栈专属规则位于 `profiles/`，Phase 2 自动探测并按需加载。

它可以搭配律刃使用：律刃约束 agent 的通用编码行为，ImpactRadar 负责多技术栈现有系统的影响分析流程。

v3.4 之后补了长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 项目降级保护、阻塞恢复安全闸和多会话写授权一致性，适合迁移、对齐、重构等多 Step 变更。最新新增**风格契约**（`change-impact/_style-rules.md`）：用户把团队强制/建议规则写进去，Impact 在分析和校验时会读取并检查代码是否符合。优先级链为：契约文件 > 地图观察 > Profile 提示 > 运行时现采；规则在实际变更中发现并追加，不要求预先写全。Claude Code + MiniMax M3 真实 `/impact` 复测已经走完 S1-S7 回归，模糊确认、历史确认、延迟确认、非 Git + V1-only、Health/API 响应字段变化都不能绕过 `确认 Step N`。

经过 V1-V10 共 10 轮盲测（3 个模型 × 6 个真实场景 × 有/无 skill 对照 = 100+ 份产出），skill 的核心价值可以归纳为：把模糊需求变成显式假设（V7 验证）、苏格拉底式提问不替用户拍板（V9 人工交互 8 项 `[假设]` 100% 转为用户确认）、结构化保障（回滚方案、验证步骤、方法名预检始终做到）、防御性检查（refreshToken TTL 同步等独有发现）、安全闸（逐步确认、写入边界、高风险拦截，弱模型也绕不过）。当前版本 v4.1，最新改进包括多轮触发条件（链路追踪发现的副作用风险必须回流 Phase 3 追问）和链路追踪发现回流，V10 单 case 验证总分 92→96。详细数据见 [skills/impact/README.md](skills/impact/README.md)。

当前还接入了可选 code graph MCP 作为结构化定义/引用候选入口，以及 `change-impact/{需求名称}/_active-state.md` 作为跨会话恢复检查点。`_active-state.md` 只记录 pending Step、文档状态和未确认项，不授权源码/SQL/配置/测试写入，也不能替代当前对话里的 `确认 Step N`。Claude Code 可选启用 `.claude/hooks/impact-write-gate.*`，把 Step 确认补强成工具执行前检查。

### VL 识图

[skills/vl-vision/](skills/vl-vision/)

一个通用图片理解小工具。给它图片和模板，它会调用视觉模型返回结构化分析。适合让纯文本 AI 补上“看图”能力。

### 统一测评体系

[docs/skill-eval/](docs/skill-eval/) + [eval/](eval/)

两个 skill 共用的防漂移测评体系。核心思路：**不新建测评方法，而是把已有的强资产收敛成能定期复跑、自动检测负向漂移的活体系。**

三层金字塔：

| 层 | 测什么 | 怎么跑 | 成本 |
|---|---|---|---|
| L0 静态自洽 | 铁律存在、引用完整、共享契约、fixture 锁定、风格规则校验 | `bash skills/<skill>/tests/run.sh` | 免费 |
| L1 行为契约 | subagent 扮用户跑 case，客观维度自动判 + 安全闸 | `bash eval/run-l1.sh <skill>` | 便宜模型 |
| L2 人审深度 | 主观维度（苏格拉底质量、文档/地图可读性）抽样 | 人工 + 可选多模型评委 | 贵 |

防漂移的关键机制是**基线评分卡时间序列 + 红线 diff**：每次改 skill 后跑 L1，产出评分卡，和上一基线逐 case 对比；任何契约从 PASS→FAIL、维度掉档≥3 分、新增 P0/P1 = 红线阻断，不许发布。详细设计见 [docs/archive/2026-06/2026-06-13-skill-eval-system-design.md](docs/archive/2026-06/2026-06-13-skill-eval-system-design.md)，实施手册见 [docs/archive/2026-06/2026-06-13-skill-eval-system-runbook.md](docs/archive/2026-06/2026-06-13-skill-eval-system-runbook.md)。

## 研究与实验记录

### Not ACE 上下文检索探索

这部分记录 2026 年 6 月 8 日围绕 [Not ACE](https://not-ace.ame.rip/) 做的一轮上下文检索实验。它不是仓库里的可安装 skill，而是一次用来反推 RuleBlade、ImpactRadar 后续该怎么迭代的研究材料。

可以先读这些：

- [docs/install-and-verify-checklist.md](docs/install-and-verify-checklist.md)：安装和验证 checklist，说明复制到哪里、MCP JSON 用哪个绝对路径、Skill 怎么验证。
- [docs/archive/2026-06/impact-real-case-study.md](docs/archive/2026-06/impact-real-case-study.md)：ImpactRadar 真实使用案例的匿名复盘，记录它暴露了哪些长会话和多 Step 边界。
- [docs/archive/2026-06/impact-m3-next-regression-plan.md](docs/archive/2026-06/impact-m3-next-regression-plan.md)：下一轮 MiniMax M3 复测计划，限定后续要测的高价值场景。
- [docs/archive/2026-06/impact-multisession-write-gate-test-plan.md](docs/archive/2026-06/impact-multisession-write-gate-test-plan.md)：多会话写授权一致性验收方案，覆盖旧授权、延迟确认、非 Git 降级、V1-only 暂停和写入目标边界。
- [docs/skill-eval/regression.md](docs/skill-eval/regression.md)：ImpactRadar 优化后的回归复测协议，规定什么时候跑 RG0-RG3、什么时候必须真实 agent 复测。
- [docs/archive/2026-06/release-positioning-check-2026-06-08.md](docs/archive/2026-06/release-positioning-check-2026-06-08.md)：阶段性 release 定位自查，确认 RuleBlade、ImpactRadar 的边界是否自洽。
- [docs/archive/2026-06/not-ace-benchmark-research.md](docs/archive/2026-06/not-ace-benchmark-research.md)：研究性博客文章，解释 Not ACE 在 MiniMax M3、GLM-5.1、Kimi K2.6、GLM-5、DeepSeek V4 系列上的不同表现。
- [docs/not-ace-exploration/](docs/not-ace-exploration/)：完整实验记录，包括 V1/V2 检索测试、V3 agent 任务测试、模型复跑、DeepSeek 调用链问题和下一轮计划。
- [docs/archive/2026-06/agent-iteration-conclusions.md](docs/archive/2026-06/agent-iteration-conclusions.md)：给后续 agent 迭代看的结论，把测试事实映射到 RuleBlade、ImpactRadar 和 VL Vision 的优化方向。
- [benchmarks/（已归档）](docs/archive/2026-06/benchmarks/)：写授权回归夹具（impact-write-gate）+ 模型 agent 能力评测体系（model-agent）。2026-06-09 后无活动，暂停保留历史；not-ace 研究见上。

这轮实验的核心判断是：Not ACE 不是 `rg` 的替代品，而是语义上下文入口。它对 MiniMax M3 更像是在补稳定性，对 GLM-5.1 更像是在省时间、省成本；但在 Kimi K2.6、GLM-5、DeepSeek V4 系列上，这轮没有跑出稳定收益。DeepSeek V4 Pro / Flash 通过硅基流动平台接入，不代表 DeepSeek 官方模型真实能力。

## 致谢

律刃最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续是在真实中文编码任务和复杂链路测试里一轮轮收紧出来的。

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

把需要的 skill 目录复制到你的 AI 客户端 skills 目录。

Codex：

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.codex\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.codex\skills\impact" -Recurse -Force
```

Claude Code：

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
```

重启客户端后触发 `/pathfinder`(陌生项目摸底)、`/impact`(变更影响分析),能进入对应流程即可。完整安装和验证 checklist 见 [docs/install-and-verify-checklist.md](docs/install-and-verify-checklist.md)。

几个边界要记住：

- `pathfinder` 面向刚接手的陌生项目,产全项目认知地图,100% 只读、只描述不开药方。
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

### Codegraph MCP 显示已连接，但没有工具（No tools）

**现象**

- Cursor 设置里 `codegraph` MCP 开关是绿的，状态像“已连接”
- 展开后却是 **No tools**，或只有连接信息、看不到 `codegraph_search` / `codegraph_explore` 等
- Agent 侧仍提示 workspace 未索引、结构索引不可用
- 本地其实已有 `.codegraph/codegraph.db`，CLI 查询正常

**原因**

`codegraph serve --mcp` 需要知道**项目根目录**才能找到 `.codegraph/` 索引。若在全局 `~/.cursor/mcp.json`（Windows：`%USERPROFILE%\.cursor\mcp.json`）里只写：

```json
"codegraph": { "command": "codegraph", "args": ["serve", "--mcp"] }
```

Cursor 的 Shared MCP **不一定**会把当前 workspace 的工作目录传给子进程。codegraph 启动时找不到 `.codegraph/`，就会注册 **0 个工具**，界面仍可能显示“已连接”。

**解决办法（推荐：项目级 wrapper）**

1. **先建索引**（目标仓库根目录，只需一次）：

```powershell
cd E:\agent\blue-skillhub
codegraph init
```

2. **清空或移除全局 codegraph 配置**，避免和项目配置冲突。全局文件里 `mcpServers` 留空即可：

```json
{ "mcpServers": {} }
```

3. **在项目根 `.cursor/mcp.json` 里指向 wrapper**（本仓库已带好，可直接参考）：

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "E:/agent/blue-skillhub/.cursor/codegraph-mcp.cmd",
      "args": []
    }
  }
}
```

4. **wrapper 负责解析项目根并传入 `--path`**（`.cursor/codegraph-mcp.cmd`）：

```bat
@echo off
setlocal
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
codegraph serve --mcp --path "%ROOT%"
```

路径请改成你本机仓库的绝对路径；Linux/macOS 可写等价的 `.sh` wrapper，核心仍是 `codegraph serve --mcp --path "<项目根>"`。

5. **重载 MCP**（Cursor 设置里刷新 codegraph，或重启 Cursor）。

**如何确认生效**

- MCP 面板里 codegraph 应列出 4 个工具：`codegraph_search`、`codegraph_callers`、`codegraph_node`、`codegraph_explore`
- 新开 Agent 会话后，Pathfinder / Impact 的结构索引辅助应能标为 `used`，而不是长期 `degraded`

**仍不行的排查顺序**

| 检查项 | 说明 |
|--------|------|
| `.codegraph/` 是否在**打开的工作区根** | 用 File → Open Folder 打开的目录应与 `codegraph init` 一致 |
| wrapper 里的 `--path` | 必须指向含 `.codegraph/` 的那一层，不是子目录 |
| 全局 vs 项目 MCP 重复配置 | 只保留项目级 wrapper，全局不要再用裸 `serve --mcp` |
| `codegraph` 是否在 PATH | 终端能执行 `codegraph --version` |

Pathfinder / Impact 在 MCP 不可用时会诚实降级到 Read/Grep，不影响基本流程；修好 MCP 后主要是结构发现和 blast radius 更快、更准。

分步安装与验证见 [docs/install-and-verify-checklist.md §4](docs/install-and-verify-checklist.md#4-安装-codegraph-mcp可选)。

## 目录速览

```text
blue-skillhub/
├── .claude/
│   └── hooks/                # 可选 Claude Code 写前门禁 hook
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
    └── vl-vision/
```
