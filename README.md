# Blue SkillHub

这是我的 AI 工具箱。

日常用 AI 写代码时，有几个问题会反复出现：它有时会猜、会多改、不会主动查资料、看不了图，刚接手一个陌生项目时很难快速看懂全貌，也很难在已有系统里稳稳地做一次变更。这个仓库就是围绕这些问题攒出来的一组工具和规则。

每个目录都可以单独使用，不需要整套一起上。

## 里面有什么

### 律刃

[claudecode行为规范/ruleblade/](claudecode行为规范/ruleblade/)

8 条给 AI 编码助手看的核心行为规则，外加一条面向用户的中文表达要求。重点不是“让它更聪明”，而是让它少猜、少乱改、先拿对上下文、先验证，也把话说得像自然中文。适合放到已有项目的 `CLAUDE.md`，也可以按需复制成 Codex 项目的 `AGENT.md`。

它是通用行为底座，不绑定具体开发流程：可以搭配 0→1 生成类 Skill、已有系统影响分析类 Skill，也可以单独用于修 bug、重构、补测试和普通编码任务。v3.2 的稳定性复测是在 GovShield 这种已有系统复杂链路变更里完成的，证明的是复杂链路门禁能力，不代表它只能用于已有系统。

最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续在中文任务、已有系统变更和 GovShield 复杂审查链路里持续实测迭代。目前 v3.2 已通过 Claude Code + MiniMax M3 的 Task A 稳定性复测：R13 + R14 连续 2 轮无 P0/P1，最小测试通过。

### 网搜 MCP

[mcp/web-search-mcp/](mcp/web-search-mcp/)

给 AI 客户端接联网搜索用。支持 Google/Bing/Brave/DuckDuckGo，可以只拿搜索摘要，也可以继续打开网页提取正文。适合 Cursor、CodeBuddy、Claude Desktop 等支持 MCP 的客户端。

### Pathfinder 领航

[skills/pathfinder/](skills/pathfinder/)

面向**刚接手、还不熟悉**的现有项目。它不做具体变更,而是先帮你通读一遍,产出一张全项目级的**认知地图**:技术栈、核心功能、架构分层、关键入口、数据模型概览、构建/运行/测试、雷区、权限模型、典型主链路、文档入口。

它和 Impact 系列正好接力:Pathfinder 管**全景广度**(看懂这是个什么项目),Impact 的 Phase 2 管**变更切片深度**(看懂这次改动影响什么)。地图产出到 `change-impact/_project-map.md`,Impact 启动时会主动读它当 L1 导航上下文 —— 读不到就完全照旧,是可选加速器不是前置必跑项。

地图每条结论都带信任标签(`【已核实】`/`【推断】`)、git HEAD(防过期)和覆盖度声明(显式列出没挖深的盲区)。Impact 接过去时,`【推断】`项一律按未确认处理、动手前重新取证 —— 地图是导航图不是权威源。Pathfinder 全程 100% 只读、只描述不开药方。

如果说律刃管 AI 的**脑子**、Impact 管 AI 的**手**,那 Pathfinder 管的是 AI 的**眼睛** —— 先看懂,才谈得上动手。设计复盘见 [docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md](docs/archive/2026-06/2026-06-13-pathfinder-skill-design.md)。

### ImpactRadar

[skills/impact/](skills/impact/)

面向 Java/Spring/MyBatis/RuoYi 类现有系统。它不是从 0 到 1 生成新项目，而是帮你在已有代码、表结构、接口和业务约束里，做一次功能迭代、新功能接入、字段/API/权限/配置变更或重构。

它可以搭配律刃使用：律刃约束 agent 的通用编码行为，ImpactRadar 负责 Java/RuoYi 现有系统的影响分析流程。

v3.4 之后补了长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 项目降级保护、阻塞恢复安全闸和多会话写授权一致性，适合迁移、对齐、重构等多 Step 变更。Claude Code + MiniMax M3 真实 `/impact` 复测已经走完 S1-S7 回归，模糊确认、历史确认、延迟确认、非 Git + V1-only、Health/API 响应字段变化都不能绕过 `确认 Step N`。

### ImpactRadar Pro

[skills/impact-pro/](skills/impact-pro/)

`impact` 的多栈版本。面向已验证技术栈规则覆盖范围内的现有系统，未知栈会先用通用规则扫描，不直接冒充”已完整支持”。适合 Node、Python、Go、.NET、前端项目等多栈项目里的变更影响分析。

它也可以搭配律刃使用：律刃提供通用行为约束，ImpactRadar Pro 提供多栈 profile 化的影响分析流程。

`impact-pro` 同样补了跨系统对齐规则、接口返回检查清单、验证等级、非 Git 降级、阻塞恢复安全闸和多会话写授权一致性。真实 `/impact-pro` 复测里，Node/Express 响应字段删除能正确判定 full，无 `确认 Step N` 时也不会写文件。

上下文包能力的设计复盘见 [docs/impact-context-pack-design.md](docs/impact-context-pack-design.md)，里面记录了需求来源、方案取舍和实现效果。

### VL 识图

[skills/vl-vision/](skills/vl-vision/)

一个通用图片理解小工具。给它图片和模板，它会调用视觉模型返回结构化分析。适合让纯文本 AI 补上“看图”能力。

### 统一测评体系

[docs/skill-eval/](docs/skill-eval/) + [eval/](eval/)

三个 skill 共用的防漂移测评体系。核心思路：**不新建测评方法，而是把已有的强资产收敛成能定期复跑、自动检测负向漂移的活体系。**

三层金字塔：

| 层 | 测什么 | 怎么跑 | 成本 |
|---|---|---|---|
| L0 静态自洽 | 铁律存在、引用完整、共享契约、fixture 锁定 | `bash skills/<skill>/tests/run.sh` | 免费 |
| L1 行为契约 | subagent 扮用户跑 case，客观维度自动判 + 安全闸 | `bash eval/run-l1.sh <skill>` | 便宜模型 |
| L2 人审深度 | 主观维度（苏格拉底质量、文档/地图可读性）抽样 | 人工 + 可选多模型评委 | 贵 |

防漂移的关键机制是**基线评分卡时间序列 + 红线 diff**：每次改 skill 后跑 L1，产出评分卡，和上一基线逐 case 对比；任何契约从 PASS→FAIL、维度掉档≥3 分、新增 P0/P1 = 红线阻断，不许发布。详细设计见 [docs/archive/2026-06/2026-06-13-skill-eval-system-design.md](docs/archive/2026-06/2026-06-13-skill-eval-system-design.md)，实施手册见 [docs/archive/2026-06/2026-06-13-skill-eval-system-runbook.md](docs/archive/2026-06/2026-06-13-skill-eval-system-runbook.md)。

## 研究与实验记录

### Not ACE 上下文检索探索

这部分记录 2026 年 6 月 8 日围绕 [Not ACE](https://not-ace.ame.rip/) 做的一轮上下文检索实验。它不是仓库里的可安装 skill，而是一次用来反推 RuleBlade、ImpactRadar、ImpactRadar Pro 后续该怎么迭代的研究材料。

可以先读这些：

- [docs/install-and-verify-checklist.md](docs/install-and-verify-checklist.md)：安装和验证 checklist，说明复制到哪里、MCP JSON 用哪个绝对路径、Skill 怎么验证。
- [docs/impact-real-case-study.md](docs/impact-real-case-study.md)：ImpactRadar 真实使用案例的匿名复盘，记录它暴露了哪些长会话和多 Step 边界。
- [docs/archive/2026-06/impact-m3-next-regression-plan.md](docs/archive/2026-06/impact-m3-next-regression-plan.md)：下一轮 MiniMax M3 复测计划，限定后续要测的高价值场景。
- [docs/archive/2026-06/impact-multisession-write-gate-test-plan.md](docs/archive/2026-06/impact-multisession-write-gate-test-plan.md)：多会话写授权一致性验收方案，覆盖旧授权、延迟确认、非 Git 降级、V1-only 暂停和写入目标边界。
- [docs/skill-eval/regression.md](docs/skill-eval/regression.md)：ImpactRadar / ImpactRadar Pro 优化后的回归复测协议，规定什么时候跑 RG0-RG3、什么时候必须真实 agent 复测。
- [docs/archive/2026-06/release-positioning-check-2026-06-08.md](docs/archive/2026-06/release-positioning-check-2026-06-08.md)：阶段性 release 定位自查，确认 RuleBlade、ImpactRadar、ImpactRadar Pro 的边界是否自洽。
- [docs/not-ace-benchmark-research.md](docs/not-ace-benchmark-research.md)：研究性博客文章，解释 Not ACE 在 MiniMax M3、GLM-5.1、Kimi K2.6、GLM-5、DeepSeek V4 系列上的不同表现。
- [docs/not-ace-exploration/](docs/not-ace-exploration/)：完整实验记录，包括 V1/V2 检索测试、V3 agent 任务测试、模型复跑、DeepSeek 调用链问题和下一轮计划。
- [docs/archive/2026-06/agent-iteration-conclusions.md](docs/archive/2026-06/agent-iteration-conclusions.md)：给后续 agent 迭代看的结论，把测试事实映射到 RuleBlade、ImpactRadar、ImpactRadar Pro 和 VL Vision 的优化方向。
- [benchmarks/（已归档）](docs/archive/2026-06/benchmarks/)：写授权回归夹具（impact-write-gate）+ 模型 agent 能力评测体系（model-agent）。2026-06-09 后无活动，暂停保留历史；not-ace 研究见上。

这轮实验的核心判断是：Not ACE 不是 `rg` 的替代品，而是语义上下文入口。它对 MiniMax M3 更像是在补稳定性，对 GLM-5.1 更像是在省时间、省成本；但在 Kimi K2.6、GLM-5、DeepSeek V4 系列上，这轮没有跑出稳定收益。DeepSeek V4 Pro / Flash 通过硅基流动平台接入，不代表 DeepSeek 官方模型真实能力。

## 致谢

律刃最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续是在真实中文编码任务和复杂链路测试里一轮轮收紧出来的。

“改代码前先反查调用方和引用方，查到后再分级处理”来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提出的 issue。这个建议已经同步进 RuleBlade、ImpactRadar 和 ImpactRadar Pro，用来减少只改当前文件却漏掉接口、生成物、测试或注册点的风险。

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
Copy-Item "E:\agent\blue-skillhub\skills\impact-pro" "$env:USERPROFILE\.codex\skills\impact-pro" -Recurse -Force
```

Claude Code：

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact-pro" "$env:USERPROFILE\.claude\skills\impact-pro" -Recurse -Force
```

重启客户端后触发 `/pathfinder`(陌生项目摸底)、`/impact` 或 `/impact-pro`(变更影响分析),能进入对应流程即可。完整安装和验证 checklist 见 [docs/install-and-verify-checklist.md](docs/install-and-verify-checklist.md)。

几个边界要记住：

- `pathfinder` 面向刚接手的陌生项目,产全项目认知地图,100% 只读、只描述不开药方。
- `impact` 面向 Java/Spring/MyBatis/RuoYi 类现有系统。
- `impact-pro` 面向已验证技术栈规则覆盖范围内的多栈现有系统。
- 写文件、改代码、DDL/DML、配置变更、删除、测试修复,都必须由用户明确回复 `确认 Step N`。
- 不能用 `yes`、`继续`、`全部确认` 代替 Step 级确认。

## 目录速览

```text
blue-skillhub/
├── claudecode行为规范/
│   └── ruleblade/
├── docs/
│   ├── skill-eval/          # 统一测评体系入口(含 REVALIDATION.md 复验体系)
│   ├── not-ace-exploration/
│   ├── archive/2026-06/     # 历史文档归档(含已迁出的 benchmarks/)
│   ├── impact-context-pack-design.md
│   ├── impact-real-case-study.md
│   ├── install-and-verify-checklist.md
│   └── not-ace-benchmark-research.md
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
    ├── impact-pro/
    └── vl-vision/
```
