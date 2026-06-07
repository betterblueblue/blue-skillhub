# Blue SkillHub

这是我的 AI 工具箱。

日常用 AI 写代码时，有几个问题会反复出现：它有时会猜、会多改、不会主动查资料、看不了图，也很难在已有系统里稳稳地做一次变更。这个仓库就是围绕这些问题攒出来的一组工具和规则。

每个目录都可以单独使用，不需要整套一起上。

## 里面有什么

### 律刃

[claudecode行为规范/ruleblade/](claudecode行为规范/ruleblade/)

7 条给 AI 编码助手看的行为规则。重点不是“让它更聪明”，而是让它少猜、少乱改、先验证。适合放到已有项目的 `CLAUDE.md` 里，给 Claude Code 这类编码助手做行为约束。

### 网搜 MCP

[mcp/web-search-mcp/](mcp/web-search-mcp/)

给 AI 客户端接联网搜索用。支持 Google/Bing/Brave/DuckDuckGo，可以只拿搜索摘要，也可以继续打开网页提取正文。适合 Cursor、CodeBuddy、Claude Desktop 等支持 MCP 的客户端。

### ImpactRadar

[skills/impact/](skills/impact/)

面向 Java/Spring/MyBatis/RuoYi 类现有系统。它不是从 0 到 1 生成新项目，而是帮你在已有代码、表结构、接口和业务约束里，做一次功能迭代、新功能接入、字段/API/权限/配置变更或重构。

### ImpactRadar Pro

[skills/impact-pro/](skills/impact-pro/)

`impact` 的多栈版本。面向已验证技术栈规则覆盖范围内的现有系统，未知栈会先用通用规则扫描，不直接冒充“已完整支持”。适合 Node、Python、Go、.NET、前端项目等多栈项目里的变更影响分析。

上下文包能力的设计复盘见 [docs/impact-context-pack-design.md](docs/impact-context-pack-design.md)，里面记录了需求来源、方案取舍和实现效果。

### VL 识图

[skills/vl-vision/](skills/vl-vision/)

一个通用图片理解小工具。给它图片和模板，它会调用视觉模型返回结构化分析。适合让纯文本 AI 补上“看图”能力。

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
├── mcp/
│   └── web-search-mcp/
└── skills/
    ├── impact/
    ├── impact-pro/
    └── vl-vision/
```
