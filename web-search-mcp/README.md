# web-search-mcp (优化版 v0.3.2)

> 基于 [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp) 改造优化而来

一个基于 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 的网页搜索服务器，支持多搜索引擎、全文内容提取、代理访问等功能。适用于 Cursor、CodeBuddy、Claude Desktop 等支持 MCP 协议的 AI 客户端。

## 与原项目的主要差异

| 改动项 | 说明 |
|--------|------|
| **新增 Google 搜索引擎** | 原项目仅支持 Bing / Brave / DuckDuckGo，现新增 Google 搜索并设为首选引擎 |
| **搜索引擎优先级调整** | `Google → Bing → Brave → DuckDuckGo`，Google 中文搜索质量远优于原默认的 Bing |
| **Playwright 代理支持** | 修复了 Playwright 不读取环境变量代理的问题，在 `chromium.launch()` 中显式传入 `proxy` 参数 |
| **统一使用 Chromium** | 将 Brave 搜索从 Firefox 改为 Chromium，避免未安装 Firefox Playwright 浏览器导致的报错 |
| **多引擎逻辑修复** | 修复了多引擎模式下有效结果被丢弃的 bug（`bestResults` 在循环结束后未被检查） |
| **环境变量兜底** | 入口处硬编码默认环境变量，即使 MCP 客户端未正确传递 `env` 也能正常工作 |
| **中文搜索优化** | Google 搜索默认 locale `zh-CN`、timezone `Asia/Shanghai`，优化中文搜索体验 |
| **智能模型适配** | 自动检测 LLM 模型类型，为 Llama 等弱模型限制内容长度，为 Qwen/Deepseek 等强壮模型放开限制 |

## 功能概览

提供 3 个 MCP 工具：

### 1. `full-web-search`

搜索网页并从顶部结果中获取完整页面内容。最全面的搜索工具。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | — | 搜索查询语句（必填） |
| `limit` | number | 5 | 返回结果数量（1-10） |
| `includeContent` | boolean | true | 是否获取完整页面内容 |
| `maxContentLength` | number | — | 每个结果内容的最大字符数（0 = 无限制） |

### 2. `get-web-search-summaries`

搜索网页并仅返回摘要/描述，不跟踪链接提取全文。轻量替代方案。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | — | 搜索查询语句（必填） |
| `limit` | number | 5 | 返回结果数量（1-10） |

### 3. `get-single-web-page-content`

从指定 URL 提取单个网页的完整内容，无需执行搜索。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | — | 目标网页 URL（必填） |
| `maxContentLength` | number | — | 内容最大字符数（0 = 无限制） |

## 快速开始

### 前置要求

- Node.js >= 18
- 如需代理访问 Google，请准备 HTTP 代理服务（默认 `localhost:7890`）

### 安装

```bash
# 克隆本项目
git clone https://github.com/mrkrsl/web-search-mcp.git
cd web-search-mcp

# 安装依赖
npm install

# 构建（如有 src 目录）
npm run build
```

### 安装依赖

在配置 MCP 客户端之前，**必须先在项目目录下执行以下两条命令**：

```bash
# 第一步：安装所有 npm 依赖（最关键！）
npm install

# 第二步：安装 Playwright Chromium 浏览器（搜索功能依赖此浏览器）
npx playwright install chromium
```

> 如果跳过 `npm install`，MCP 服务器启动时会因缺少依赖报错；  
> 如果跳过 `npx playwright install chromium`，搜索功能将无法启动浏览器，返回 0 结果。

### MCP 客户端配置

在 MCP 客户端（如 CodeBuddy、Cursor、Claude Desktop）的配置文件中添加：

**CodeBuddy** (`~/.codebuddy/mcp.json`)：

```json
{
  "mcpServers": {
    "web-search-mcp": {
      "command": "node",
      "args": ["E:\\agent\\mcp\\web-search-mcp-v0.3.2\\dist\\index.js"],
      "env": {
        "BROWSER_TYPES": "chromium",
        "BROWSER_HEADLESS": "true",
        "HTTP_PROXY": "http://localhost:7890",
        "HTTPS_PROXY": "http://localhost:7890",
        "http_proxy": "http://localhost:7890",
        "https_proxy": "http://localhost:7890",
        "FORCE_MULTI_ENGINE_SEARCH": "true",
        "DEFAULT_NUM_RESULTS": "10",
        "SEARCH_TIMEOUT": "30000"
      }
    }
  }
}
```

**Cursor / Claude Desktop**（配置路径和格式类似，请参照对应客户端文档）

### 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BROWSER_TYPES` | `chromium` | Playwright 浏览器类型，**请勿添加 firefox** |
| `BROWSER_HEADLESS` | `true` | 无头模式，`false` 可弹出浏览器窗口用于调试 |
| `HTTP_PROXY` | `http://localhost:7890` | HTTP 代理地址 |
| `HTTPS_PROXY` | `http://localhost:7890` | HTTPS 代理地址 |
| `http_proxy` | `http://localhost:7890` | 小写形式（兼容部分库） |
| `https_proxy` | `http://localhost:7890` | 小写形式（兼容部分库） |
| `FORCE_MULTI_ENGINE_SEARCH` | — | 设为 `true` 启用多引擎模式 |
| `DEFAULT_NUM_RESULTS` | — | 每次搜索默认返回结果数 |
| `SEARCH_TIMEOUT` | — | 单个引擎超时时间（毫秒） |

## 搜索引擎

| 引擎 | 方式 | 优先级 | 状态 |
|------|------|--------|------|
| Google | Playwright Chromium | 1（首选） | 正常 |
| Bing | Playwright Chromium | 2 | CSS 选择器待更新，可能解析失败 |
| Brave | Playwright Chromium | 3 | 正常 |
| DuckDuckGo | Axios（无浏览器） | 4（兜底） | 正常 |

## 项目结构

```
web-search-mcp-v0.3.2/
├── dist/
│   ├── index.js                      # MCP 服务器入口，注册工具与环境变量兜底
│   ├── search-engine.js              # 搜索引擎实现（Google/Bing/Brave/DuckDuckGo）
│   ├── enhanced-content-extractor.js # 增强内容提取器
│   ├── content-extractor.js          # 基础内容提取器
│   ├── browser-pool.js               # 浏览器连接池管理
│   ├── rate-limiter.js               # 请求速率限制
│   ├── utils.js                      # 工具函数
│   └── types.js                      # 类型定义
├── package.json
├── README.md
└── web-search-mcp修复记录.md          # 详细修复与调优记录
```

## 致谢

- 原项目：[mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp) by Mark Russell
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Playwright](https://playwright.dev/)

## License

MIT
