# Blue SkillHub

这是我的 AI 工具箱。

日常用 AI 写代码时，有几个问题会反复出现：它有时会猜、会多改、不会主动查资料、看不了图，也很难在已有系统里稳稳地做一次变更。这个仓库就是围绕这些问题攒出来的一组工具和规则。

每个目录都可以单独使用，不需要整套一起上。

## 里面有什么

### 律刃

[claudecode行为规范/ruleblade/](claudecode行为规范/ruleblade/)

8 条给 AI 编码助手看的行为规则。重点不是“让它更聪明”，而是让它少猜、少乱改、先拿对上下文、先验证。适合放到已有项目的 `CLAUDE.md`，也可以按需复制成 Codex 项目的 `AGENT.md`。

它是通用行为底座，不绑定具体开发流程：可以搭配 0→1 生成类 Skill、已有系统影响分析类 Skill，也可以单独用于修 bug、重构、补测试和普通编码任务。v3.2 的稳定性复测是在 GovShield 这种已有系统复杂链路变更里完成的，证明的是复杂链路门禁能力，不代表它只能用于已有系统。

最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续在中文任务、已有系统变更和 GovShield 复杂审查链路里持续实测迭代。目前 v3.2 已通过 Claude Code + MiniMax M3 的 Task A 稳定性复测：R13 + R14 连续 2 轮无 P0/P1，最小测试通过。

### 网搜 MCP

[mcp/web-search-mcp/](mcp/web-search-mcp/)

给 AI 客户端接联网搜索用。支持 Google/Bing/Brave/DuckDuckGo，可以只拿搜索摘要，也可以继续打开网页提取正文。适合 Cursor、CodeBuddy、Claude Desktop 等支持 MCP 的客户端。

### ImpactRadar

[skills/impact/](skills/impact/)

面向 Java/Spring/MyBatis/RuoYi 类现有系统。它不是从 0 到 1 生成新项目，而是帮你在已有代码、表结构、接口和业务约束里，做一次功能迭代、新功能接入、字段/API/权限/配置变更或重构。

它可以搭配律刃使用：律刃约束 agent 的通用编码行为，ImpactRadar 负责 Java/RuoYi 现有系统的影响分析流程。

近期根据真实使用案例补强了长期目标模式、接口返回检查清单、V0-V3 验证等级、非 Git 项目降级保护和阻塞恢复安全闸，适合迁移、对齐、重构等多 Step 变更。补强后已用 Claude Code + MiniMax M3 通过真实 `/impact` 复测，覆盖长期对齐、阻塞恢复、Step 范围一致和最小写操作闭环。

### ImpactRadar Pro

[skills/impact-pro/](skills/impact-pro/)

`impact` 的多栈版本。面向已验证技术栈规则覆盖范围内的现有系统，未知栈会先用通用规则扫描，不直接冒充“已完整支持”。适合 Node、Python、Go、.NET、前端项目等多栈项目里的变更影响分析。

它也可以搭配律刃使用：律刃提供通用行为约束，ImpactRadar Pro 提供多栈 profile 化的影响分析流程。

近期同步补强了跨系统对齐规则、接口返回检查清单、验证等级、非 Git 降级和阻塞恢复安全闸，避免多栈迁移或长会话执行时把静态验证、旧授权和当前文件状态混在一起。补强后已用 Claude Code + MiniMax M3 通过真实 `/impact-pro` 复测，验证 Node/Express 响应字段删除能正确判定 full。

上下文包能力的设计复盘见 [docs/impact-context-pack-design.md](docs/impact-context-pack-design.md)，里面记录了需求来源、方案取舍和实现效果。

### VL 识图

[skills/vl-vision/](skills/vl-vision/)

一个通用图片理解小工具。给它图片和模板，它会调用视觉模型返回结构化分析。适合让纯文本 AI 补上“看图”能力。

## 研究与实验记录

### Not ACE 上下文检索探索

这部分记录今天（2026年6月8日）围绕 [Not ACE](https://not-ace.ame.rip/) 做的一轮上下文检索实验。它不是仓库里的可安装 skill，而是一次用来反推 RuleBlade、ImpactRadar、ImpactRadar Pro 后续该怎么迭代的研究材料。

可以先读这三份：

- [docs/impact-regression-protocol.md](docs/impact-regression-protocol.md)：ImpactRadar / ImpactRadar Pro 优化后的回归复测协议，规定什么时候跑 RG0-RG3、什么时候必须真实 agent 复测。
- [docs/not-ace-benchmark-research.md](docs/not-ace-benchmark-research.md)：研究性博客文章，解释 Not ACE 在 MiniMax M3、GLM-5.1、Kimi K2.6、GLM-5、DeepSeek V4 系列上的不同表现。
- [docs/not-ace-exploration/](docs/not-ace-exploration/)：完整实验记录，包括 V1/V2 检索测试、V3 agent 任务测试、模型复跑、DeepSeek 调用链问题和下一轮计划。
- [docs/agent-iteration-conclusions.md](docs/agent-iteration-conclusions.md)：给后续 agent 迭代看的结论，把测试事实映射到 RuleBlade、ImpactRadar、ImpactRadar Pro 和 VL Vision 的优化方向。

这轮实验的核心判断是：Not ACE 不是 `rg` 的替代品，而是语义上下文入口。它对 MiniMax M3 更像是在补稳定性，对 GLM-5.1 更像是在省时间、省成本；但在 Kimi K2.6、GLM-5、DeepSeek V4 系列上，这轮没有跑出稳定收益。DeepSeek V4 Pro / Flash 通过硅基流动平台接入，不代表 DeepSeek 官方模型真实能力。

## 致谢

律刃最初版参考了 multica-ai/andrej-karpathy-skills 的 [CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)，后续是在真实中文编码任务和复杂链路测试里一轮轮收紧出来的。

“改代码前先反查调用方和引用方，查到后再分级处理”来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提出的 issue。这个建议已经同步进 RuleBlade、ImpactRadar 和 ImpactRadar Pro，用来减少只改当前文件却漏掉接口、生成物、测试或注册点的风险。

ImpactRadar 近期关于长期目标、阻塞恢复、接口返回检查和验证等级的补强，也来自 [hxd-ggsddu](https://github.com/hxd-ggsddu) 提供的真实使用案例。这个案例暴露了长会话、多 Step 迁移、非 Git 项目、延迟确认和弱模型执行时更容易出现的边界问题。

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

### 4. 安装 Impact Skills

把需要的 skill 目录复制到你的 AI 客户端 skills 目录，例如 Codex 的 `$CODEX_HOME/skills`：

```text
skills/impact
skills/impact-pro
```

触发 `/impact` 或 `/impact-pro`，能进入变更意图捕获流程即可。

几个边界要记住：

- `impact` 面向 Java/Spring/MyBatis/RuoYi 类现有系统。
- `impact-pro` 面向已验证技术栈规则覆盖范围内的多栈现有系统。
- 写文件、改代码、DDL/DML、配置变更、删除、测试修复，都必须由用户明确回复 `确认 Step N`。
- 不能用 `yes`、`继续`、`全部确认` 代替 Step 级确认。

## 目录速览

```text
blue-skillhub/
├── claudecode行为规范/
│   └── ruleblade/
├── docs/
│   ├── not-ace-exploration/
│   ├── agent-iteration-conclusions.md
│   ├── impact-regression-protocol.md
│   └── not-ace-benchmark-research.md
├── mcp/
│   └── web-search-mcp/
└── skills/
    ├── impact/
    ├── impact-pro/
    └── vl-vision/
```
