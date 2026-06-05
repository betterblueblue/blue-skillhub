# Blue SkillHub

> 个人 AI 工具箱 —— 规则、搜索、视觉、影响分析，补齐 AI 的短板

## 这是什么

日常使用 AI 编码助手时，总会遇到几类反复出现的能力缺口：行为不可控、搜不了网、看不了图、变更无章法。这个仓库就是我针对这些问题的个人解决方案，每个子目录独立可用。

## 目录结构

```
blue-skillhub/
├── ruleblade/          🎯 律刃 —— AI 编码行为准则（7 条实验验证的祈使句规则）
├── web-search-mcp/     🔍 网搜 —— MCP 网页搜索服务器（Google 首选 + 中文优化）
├── vl-vision/          👁️ 识图 —— 通用 VL 识图工具（让纯文本 LLM 也能看图）
├── impact/             📡 ImpactRadar —— 苏格拉底式需求澄清与变更实施（19 维度 × 三文档）
└── mcps/               🔌 MCP 服务器配置集（Playwright、Sequential Thinking 等）
```

| 目录 | 一句话 | 详请 |
|------|--------|------|
| [**ruleblade/**](ruleblade/) | 7 条实验验证的 AI 编码行为准则 | 让 AI 编码时听话、精准、不画蛇添足 |
| [**web-search-mcp/**](web-search-mcp/) | MCP 网页搜索服务器 | 让 AI 能搜网，Google 首选 + 中文优化 |
| [**vl-vision/**](vl-vision/) | 通用 VL 识图工具 | 让纯文本 LLM 也能看图，10 个预置模板 + 自定义 prompt |
| [**impact/**](impact/) | 苏格拉底式需求澄清与变更实施 Skill | 19 维度灵活覆盖，需求→设计→实施三文档逐级确认，逐操作执行 |
| [**mcps/**](mcps/) | MCP 服务器配置集 | Playwright 浏览器自动化、Sequential Thinking 等预置配置 |

## 快速使用

- **规则** → 将 `ruleblade/CLAUDE.md` 复制到项目根目录，Claude Code 自动生效
- **搜索** → 在 MCP 客户端配置 `web-search-mcp/dist/index.js`，详见 [web-search-mcp/README.md](web-search-mcp/README.md)
- **识图** → `python vl-vision/vl_vision.py <图片路径>`，详见 [vl-vision/README.md](vl-vision/README.md)
- **影响分析** → 安装 impact skill，对 AI 说"我想改一下"即可触发，详见 [impact/README.md](impact/README.md)
- **MCP 配置** → 将 `mcps/` 下对应目录的 JSON 复制到 MCP 客户端配置中
