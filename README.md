# Blue SkillHub

> 个人 AI 工具箱 —— 规则约束、联网搜索、视觉识别、变更分析，补齐 AI 的短板

## 这是什么

日常使用 AI 编码助手时，总会遇到几类反复出现的能力缺口：行为不可控、无法联网、不能看图、变更无章法。这个仓库就是我针对这些问题的个人解决方案，每个子目录独立可用。

## 目录结构

```
blue-skillhub/
├── claudecode行为规范/  🎯 律刃 —— AI 编码行为准则（7 条实验验证的祈使句规则）
│   └── ruleblade/
├── mcp/                 🔍 网搜 —— MCP 网页搜索服务器（Google 首选 + 中文优化）
│   └── web-search-mcp/
└── skills/              🧩 Skill 合集
    ├── impact/          📡 ImpactRadar —— 变更影响分析（Java/Spring/MyBatis，light/full 两档）
    ├── impact-pro/      📡 ImpactRadar Pro —— 通用变更影响分析（多语言/多栈，自动探测技术栈）
    └── vl-vision/       👁️ 识图 —— 通用 VL 识图工具（突破纯文本 LLM 的视觉限制）
```

| 目录 | 一句话 | 详请 |
|------|--------|------|
| [**claudecode行为规范/ruleblade/**](claudecode行为规范/ruleblade/) | 7 条实验验证的 AI 编码行为准则 | 约束 AI 编码行为，精准可控、不画蛇添足 |
| [**mcp/web-search-mcp/**](mcp/web-search-mcp/) | MCP 网页搜索服务器 | Google 首选 + 中文优化，赋予 AI 联网搜索能力 |
| [**skills/impact/**](skills/impact/) | 变更影响分析 Skill | Java/Spring/MyBatis 专属，19 维度 × light/full 两档，三文档逐级确认 |
| [**skills/impact-pro/**](skills/impact-pro/) | 通用变更影响分析 Skill | 多语言/多栈通用，自动探测技术栈并加载 profile，DB adapter 系统 |
| [**skills/vl-vision/**](skills/vl-vision/) | 通用 VL 识图工具 | 10 个预置模板 + 自定义 prompt，突破纯文本 LLM 的视觉限制 |

## 快速使用

- **规则** → 将 `claudecode行为规范/ruleblade/CLAUDE.md` 复制到项目根目录，Claude Code 自动生效
- **搜索** → 在 MCP 客户端配置 `mcp/web-search-mcp/dist/index.js`，详见 [mcp/web-search-mcp/README.md](mcp/web-search-mcp/README.md)
- **识图** → `python skills/vl-vision/vl_vision.py <图片路径>`，详见 [skills/vl-vision/README.md](skills/vl-vision/README.md)
- **影响分析（Java 栈）** → 安装 impact skill，对 AI 说"我想改一下"即可触发，详见 [skills/impact/README.md](skills/impact/README.md)
- **影响分析（通用栈）** → 安装 impact-pro skill，适用于 Node/Python/Go/.NET 等项目，详见 [skills/impact-pro/README.md](skills/impact-pro/README.md)

## 5 分钟安装验证

把仓库克隆到本地后，先按下面顺序跑一遍，确认每个工具真的可用。

### 1. 律刃规则

复制规则文件到目标项目根目录：

```powershell
Copy-Item "claudecode行为规范/ruleblade/CLAUDE.md" "你的项目路径/CLAUDE.md"
```

验证方式：在目标项目里启动 Claude Code，确认它能读取根目录的 `CLAUDE.md`。

### 2. 网搜 MCP

进入 MCP 目录并安装运行依赖：

```powershell
cd mcp/web-search-mcp
npm install
npx playwright install chromium
node ./dist/index.js
```

看到 `Web Search MCP Server started` 和 `Waiting for MCP messages...` 即表示服务入口正常。

MCP 客户端配置时，`args` 必须写本机绝对路径，例如当前仓库位置对应：

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

更多代理、搜索引擎和环境变量配置见 [mcp/web-search-mcp/README.md](mcp/web-search-mcp/README.md)。

### 3. VL 识图

先安装依赖并检查模板列表：

```powershell
pip install requests
python skills/vl-vision/vl_vision.py --list-templates
```

再配置 `SILICONFLOW_API_KEY` 后跑一张图片：

```powershell
$env:SILICONFLOW_API_KEY="sk-your-key"
python skills/vl-vision/vl_vision.py path/to/image.png
```

### 4. Impact Skills

把对应 skill 目录安装到你的 AI 客户端技能目录：

```text
skills/impact
skills/impact-pro
```

验证方式：在客户端中触发 `/impact` 或 `/impact-pro`，能进入变更意图捕获流程即可。
