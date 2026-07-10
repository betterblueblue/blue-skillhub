# Web Search MCP

> 为支持 MCP 的 AI 客户端提供网页搜索，基于 [mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp) 修改。

Cursor、CodeBuddy 和 Claude Desktop 等客户端可以通过它搜索 Google、Bing、Brave 和 DuckDuckGo。既可以只获取标题和摘要，也可以继续打开结果页提取正文；需要时还可以通过本地 HTTP 代理访问。

## 与原项目的主要差异

| 改动项 | 说明 |
|--------|------|
| **新增 Google 搜索引擎** | 原项目仅支持 Bing、Brave 和 DuckDuckGo；当前版本增加 Google，并将它设为首选 |
| **调整搜索引擎顺序** | 当前顺序为 `Google → Bing → Brave → DuckDuckGo`，更适合本项目以中文为主的搜索任务 |
| **Playwright 代理支持** | 修复了 Playwright 不读取环境变量代理的问题，在 `chromium.launch()` 中显式传入 `proxy` 参数 |
| **统一使用 Chromium** | 将 Brave 搜索从 Firefox 改为 Chromium，避免未安装 Firefox Playwright 浏览器导致的报错 |
| **修复多引擎结果选择** | 修复多引擎模式下可能丢弃有效结果的问题（循环结束后没有检查 `bestResults`） |
| **默认运行参数** | 入口处设置常用默认值，即使 MCP 客户端没有正确传递 `env` 也能启动 |
| **中文搜索优化** | Google 搜索默认 locale `zh-CN`、timezone `Asia/Shanghai`，优化中文搜索体验 |
| **限制输出长度** | 每条结果默认最多 6000 个字符，全部结果合计最多 40000 个字符；60 秒内不重复执行相同搜索 |
| **按内容边界截断** | `smartTruncate` 优先在段落、句子或单词边界截断，尽量保留完整语义 |
| **网页结构保留** | `parseContent` 按 h1-h6/p/li/blockquote 等语义元素提取内容，保留标题标记和段落换行，而不是用 `.text()` 全部压成无结构文本 |

## 功能概览

提供 3 个 MCP 工具：

### 1. `full-web-search`

搜索网页，并继续打开靠前的结果提取正文。适合需要详细资料时使用。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | 无 | 搜索查询语句（必填） |
| `limit` | number | 3 | 返回结果数量（1-5，硬上限 5） |
| `includeContent` | boolean | true | 是否获取完整页面内容（内容会自动截断） |
| `maxContentLength` | number | 6000 | 每个结果内容的最大字符数（硬上限 8000） |

**输出限制**：

- 60 秒内不会重复执行相同查询。
- 全部结果合计最多返回 40000 个字符，超出部分会截断并说明省略数量。
- `smartTruncate` 会优先在句子边界截断内容。

### 2. `get-web-search-summaries`

只返回搜索结果标题、摘要和链接，不继续打开网页。适合先快速看一眼有哪些结果。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | 无 | 搜索查询语句（必填） |
| `limit` | number | 3 | 返回结果数量（1-5，硬上限 5） |

### 3. `get-single-web-page-content`

直接读取指定 URL 的正文内容，不先搜索。适合 `full-web-search` 返回信息不够时深入查看某个页面。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | 无 | 目标网页 URL（必填） |
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

> 当前仓库只提供已经构建好的 `dist/`，没有包含 `src/` 和 `tsconfig.json`。直接安装使用时无需运行 `npm run build`；如需修改源码并重新构建，需要先恢复原项目的源码和 TypeScript 配置。

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
| `FORCE_MULTI_ENGINE_SEARCH` | 无 | 设为 `true` 启用多引擎模式 |
| `DEFAULT_NUM_RESULTS` | 无 | 每次搜索默认返回结果数 |
| `SEARCH_TIMEOUT` | 无 | 单个引擎超时时间（毫秒） |
| `MAX_CONTENT_LENGTH` | `6000` | 内容提取的默认字符数，最大不能超过 10000 |

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

- 原项目：[mrkrsl/web-search-mcp](https://github.com/mrkrsl/web-search-mcp)，作者 Mark Russell
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Playwright](https://playwright.dev/)

## License

MIT
