# Blue SkillHub

> 个人 AI 工具箱 —— 规则、搜索、视觉，三件套补齐 AI 的短板

## 这是什么

日常使用 AI 编码助手时，总会遇到几类反复出现的能力缺口：行为不可控、搜不了网、看不了图。这个仓库就是我针对这三类问题的个人解决方案，每个子目录独立可用。

## 目录结构

```
blue-skillhub/
├── ruleblade/          🎯 律刃 —— AI 编码行为准则（7 条实验验证的祈使句规则）
├── web-search-mcp/     🔍 网搜 —— MCP 网页搜索服务器（Google 首选 + 中文优化）
└── vl-vision/          👁️ 识图 —— 通用 VL 识图工具（让纯文本 LLM 也能看图）
```

| 目录 | 一句话 | 详请 |
|------|--------|------|
| [**ruleblade/**](ruleblade/) | 7 条实验验证的 AI 编码行为准则 | 让 AI 编码时听话、精准、不画蛇添足 |
| [**web-search-mcp/**](web-search-mcp/) | MCP 网页搜索服务器 | 让 AI 能搜网，Google 首选 + 中文优化 |
| [**vl-vision/**](vl-vision/) | 通用 VL 识图工具 | 让纯文本 LLM 也能看图，10 个预置模板 + 自定义 prompt |

## 快速使用

- **规则** → 将 `ruleblade/CLAUDE.md` 复制到项目根目录，Claude Code 自动生效
- **搜索** → 在 MCP 客户端配置 `web-search-mcp/dist/index.js`，详见 [web-search-mcp/README.md](web-search-mcp/README.md)
- **识图** → `python vl-vision/vl_vision.py <图片路径>`，详见 [vl-vision/README.md](vl-vision/README.md)
