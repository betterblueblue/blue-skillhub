# web-search-mcp

> 给 AI 客户端用的网页搜索 MCP 服务，基于 [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp) 改造。

它负责把“联网搜索”接到 Cursor、CodeBuddy、Claude Desktop 等支持 MCP 的客户端里。支持 Google/Bing/Brave/DuckDuckGo，多结果摘要、完整网页内容提取，以及本地代理访问。

## 与原项目的主要差异

| 改动项 | 说明 |
|--------|------|
| **新增 Google 搜索引擎** | 原项目仅支持 Bing / Brave / DuckDuckGo，现新增 Google 搜索并设为首选引擎 |
| **搜索引擎优先级调整** | `Google → Bing → Brave → DuckDuckGo`，Google 中文搜索质量远优于原默认的 Bing |
| **Playwright 代理支持** | 修复了 Playwright 不读取环境变量代理的问题，在 `chromium.launch()` 中显式传入 `proxy` 参数 |
| **统一使用 Chromium** | 将 Brave 搜索从 Firefox 改为 Chromium，避免未安装 Firefox Playwright 浏览器导致的报错 |
| **多引擎逻辑修复** | 修复了多引擎模式下有效结果被丢弃的 bug（`bestResults` 在循环结束后未被检查） |
| **默认运行参数** | 入口处设置常用默认值，即使 MCP 客户端没有正确传递 `env` 也能启动 |
| **中文搜索优化** | Google 搜索默认 locale `zh-CN`、timezone `Asia/Shanghai`，优化中文搜索体验 |
| **上下文爆炸防护** | 防止搜索结果撑爆 AI 上下文窗口：每条结果 6000 字符截断、全局 40000 字符上限、60 秒防重复搜索、句子边界感知截断 |
| **语义安全截断** | `smartTruncate` 在句子/段落/词边界处截断，不会在句中或词中硬切；保留 HTML 段落/标题结构而非压成无结构文本 |
| **网页结构保留** | `parseContent` 按 h1-h6/p/li/blockquote 等语义元素提取内容，保留标题标记和段落换行，而不是用 `.text()` 全部压成无结构文本 |

## 功能概览

提供 3 个 MCP 工具：

### 1. `full-web-search`

搜索网页，并继续打开靠前的结果提取正文。适合需要详细资料时使用。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | — | 搜索查询语句（必填） |
| `limit` | number | 3 | 返回结果数量（1-5，硬上限 5） |
| `includeContent` | boolean | true | 是否获取完整页面内容（内容会自动截断） |
| `maxContentLength` | number | 6000 | 每个结果内容的最大字符数（硬上限 8000） |

**安全机制**：
- 60 秒内相同查询自动拦截，防止重复搜索浪费上下文
- 全局输出硬上限 40000 字符，超出部分截断并提示省略数量
- 内容截断使用 `smartTruncate`，在句子边界处截断而非硬切

### 2. `get-web-search-summaries`

只返回搜索结果标题、摘要和链接，不继续打开网页。适合先快速看一眼有哪些结果。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | — | 搜索查询语句（必填） |
| `limit` | number | 3 | 返回结果数量（1-5，硬上限 5） |

### 3. `get-single-web-page-content`

直接读取指定 URL 的正文内容，不先搜索。适合 `full-web-search` 返回信息不够时深入查看某个页面。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | — | 目标网页 URL（必填） |
| `maxContentLength` | number | 6000 | 内容最大字符数（硬上限 10000） |

## 快速开始

### 前置要求

- Node.js >= 18
- 如需代理访问 Google，请准备 HTTP 代理服务（默认 `localhost:7890`）

### 当前仓库路径

本仓库当前的 MCP 入口文件是：

```text
E:\agent\blue-skillhub\mcp\web-search-mcp\dist\index.js
```

如果仓库不在这个位置，请把 MCP 客户端配置里的 `args` 改成你本机的绝对路径。

> 当前目录以 `dist/` 产物运行，没有随仓库提供 `src/` 和 `tsconfig.json`。因此安装使用时不需要执行 `npm run build`；如需二次开发，需要先补回源码构建链。

### 安装依赖

在配置 MCP 客户端之前，先在项目目录下执行这两条命令：

```powershell
cd E:\agent\blue-skillhub\mcp\web-search-mcp

# 第一步：安装 npm 依赖
npm install

# 第二步：安装 Playwright Chromium 浏览器
npx playwright install chromium
```

> 跳过 `npm install` 会导致服务启动时报缺依赖；跳过 `npx playwright install chromium`，搜索时通常会因为浏览器不存在而返回 0 结果。

### 启动验证

在配置 MCP 客户端前，可以先手动验证入口是否能启动：

```powershell
cd E:\agent\blue-skillhub\mcp\web-search-mcp
node .\dist\index.js
```

看到下面两行就说明入口能启动：

```text
Web Search MCP Server started
Waiting for MCP messages...
```

验证完成后按 `Ctrl+C` 退出，再配置到 MCP 客户端。

### MCP 客户端配置

在 MCP 客户端（如 CodeBuddy、Cursor、Claude Desktop）的配置文件中添加：

**CodeBuddy** (`~/.codebuddy/mcp.json`)：

```json
{
  "mcpServers": {
    "web-search-mcp": {
      "command": "node",
      "args": ["E:\\agent\\blue-skillhub\\mcp\\web-search-mcp\\dist\\index.js"],
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

**Cursor / Claude Desktop**：配置格式类似，重点是 `args` 必须指向本机真实存在的 `dist/index.js`。

### 配置后验证

1. 重启 MCP 客户端。
2. 在客户端里确认出现 `full-web-search`、`get-web-search-summaries`、`get-single-web-page-content` 这 3 个工具。
3. 让 AI 调用 `get-web-search-summaries` 搜一个简单关键词，例如 `MCP protocol`。
4. 如果返回 0 结果，优先检查代理地址、`npx playwright install chromium` 是否执行过，以及客户端是否正确传入 `env`。

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
| `MAX_CONTENT_LENGTH` | `6000` | 内容提取的默认字符上限（硬上限 10000，超出自动 cap） |

## 搜索引擎

| 引擎 | 方式 | 优先级 | 状态 |
|------|------|--------|------|
| Google | Playwright Chromium | 1（首选） | 正常 |
| Bing | Playwright Chromium | 2 | CSS 选择器待更新，可能解析失败 |
| Brave | Playwright Chromium | 3 | 正常 |
| DuckDuckGo | Axios（无浏览器） | 4（备用选择） | 正常 |

## 项目结构

```
web-search-mcp/
├── dist/
│   ├── index.js                      # MCP 服务入口，注册工具并设置默认运行参数
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
