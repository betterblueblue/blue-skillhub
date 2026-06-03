# Blue SkillHub

> 个人 AI 技能库 —— 存放自用的 Claude Code Skill 与项目级行为准则

## 目录结构

```
.
├── ruleblade/          # 律刃 —— AI 编码行为准则
│   ├── CLAUDE.md       # 可直接用于 Claude Code 的项目级行为准则
│   └── README.md       # 律刃的迭代历程与设计文档
├── web-search-mcp/     # 网搜 MCP —— 基于 MCP 协议的网页搜索服务器
│   ├── dist/           # 编译产物
│   ├── package.json
│   ├── README.md       # 使用说明与配置文档
│   └── web-search-mcp修复记录.md  # 修复与调优记录
├── vl-vision/          # VL Vision —— 通用 VL 识图工具
│   ├── providers/      # VL 模型适配器（硅基流动等）
│   ├── vl_vision.py    # 主入口
│   ├── config.py       # 配置管理
│   ├── SKILL.md        # Skill 说明与 Prompt 模板
│   └── README.md       # 使用文档
└── README.md           # 本文件
```

## 项目说明

这个仓库是我个人的 AI 技能与工具集合，主要包含：

- **ruleblade/** —— 经过实验验证的 AI 编码行为准则（律刃 v3），用于指导 Claude Code 等 AI 助手在编码任务中的精准行为
- **web-search-mcp/** —— 基于 [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp) 改造优化的 MCP 网页搜索服务器（v0.3.2），新增 Google 搜索、代理支持、中文搜索优化等，适用于 CodeBuddy / Cursor / Claude Desktop 等客户端
- **vl-vision/** —— 通用 VL 识图工具，调用外部视觉语言模型 API，让不具备视觉能力的 LLM 也能识图。10 个预置 prompt 模板 + 自定义 prompt，支持 CLI 和 Agent 双模式调用

## 使用方式

将 `ruleblade/CLAUDE.md` 复制到你的项目根目录，Claude Code 会自动读取并遵循其中的行为准则。

## 关于律刃

律刃是一套经过 A/B 实验淬炼的 7 条中文祈使句规则，核心设计原则：

- **实验验证**：每条规则都有可归因的实验证据，不是拍脑袋
- **写法优先**：祈使句 > 描述句，短指令 > 长解释
- **ROI 甜点**：7 条规则是边际效益最优点
- **分级适用**：按任务规模决定检查哪些规则

详见 [`ruleblade/README.md`](ruleblade/README.md)。
