# web-search-mcp 修复与调优记录

> 日期：2026-06-03（初版） / 2026-06-10（上下文爆炸修复）
> MCP 版本：v0.3.2
> 路径：`E:\agent\blue-skillhub\mcp\web-search-mcp\`

---

## 一、Bug 修复（2026-06-03）

### Bug 1：MCP 配置缺少服务器名称 key

**现象**：CodeBuddy 无法识别 web-search-mcp 服务器

**原因**：`~/.codebuddy/mcp.json` 中 `mcpServers` 下直接写了 `command`、`args` 等字段，缺少服务器名称 key 包裹

**修复前**：
```json
{
  "mcpServers": {
    "command": "node",
    "args": ["E:\\agent\\mcp\\web-search-mcp-v0.3.2\\dist\\index.js"],
    "env": { ... }
  }
}
```

**修复后**：
```json
{
  "mcpServers": {
    "web-search-mcp": {
      "command": "node",
      "args": ["E:\\agent\\mcp\\web-search-mcp-v0.3.2\\dist\\index.js"],
      "env": { ... }
    }
  }
}
```

**文件**：`c:\Users\blue\.codebuddy\mcp.json`

---

### Bug 2：Playwright 未配置代理

**现象**：浏览器能启动但搜索返回 0 结果，`Search engine: None`

**原因**：虽然 `mcp.json` 的 `env` 中配置了 `HTTP_PROXY`/`HTTPS_PROXY`，但 Playwright **不会自动读取环境变量**，需要在 `chromium.launch()` 或 `browser.newContext()` 中显式传入 `proxy` 参数

**修复**：在以下 3 处 `launch` 调用中添加代理配置

1. `dist/search-engine.js` — Brave 搜索的浏览器启动
2. `dist/search-engine.js` — Bing 搜索的浏览器启动
3. `dist/browser-pool.js` — 浏览器池的启动

**修改内容**：
```javascript
// 修改前
browser = await chromium.launch({
    headless: process.env.BROWSER_HEADLESS !== 'false',
    args: [...],
});

// 修改后
const _proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || process.env.http_proxy;
browser = await chromium.launch({
    headless: process.env.BROWSER_HEADLESS !== 'false',
    proxy: _proxy ? { server: _proxy } : undefined,
    args: [...],
});
```

---

### Bug 3：Firefox Playwright 浏览器未安装

**现象**：Brave 搜索硬编码使用 `firefox`，但系统未安装 Firefox 的 Playwright 浏览器

**原因**：`search-engine.js` 中 `tryBrowserBraveSearch` 直接 `import('playwright').firefox`，而 `C:\Users\blue\AppData\Local\ms-playwright\firefox-1522` 不存在

**修复**：将 Brave 搜索的浏览器从 `firefox` 改为 `chromium`

```javascript
// 修改前
const { firefox } = await import('playwright');
browser = await firefox.launch({...});

// 修改后
const { chromium } = await import('playwright');
browser = await chromium.launch({...});
```

**文件**：`dist/search-engine.js` 第 108 行

同时将 `dist/browser-pool.js` 默认 `BROWSER_TYPES` 从 `'chromium,firefox'` 改为 `'chromium'`

---

### Bug 4：环境变量未传递到 MCP 进程

**现象**：MCP 服务器日志显示 `types=chromium,firefox`，但配置中设的是 `BROWSER_TYPES: "chromium"`

**原因**：CodeBuddy 可能未正确将 `mcp.json` 中的 `env` 字段传递给 MCP 子进程

**修复**：在 `dist/index.js` 入口处硬编码默认环境变量

```javascript
// 在文件顶部添加
process.env.BROWSER_TYPES = process.env.BROWSER_TYPES || 'chromium';
process.env.BROWSER_HEADLESS = process.env.BROWSER_HEADLESS || 'true';
process.env.HTTP_PROXY = process.env.HTTP_PROXY || 'http://localhost:7890';
process.env.HTTPS_PROXY = process.env.HTTPS_PROXY || 'http://localhost:7890';
process.env.http_proxy = process.env.http_proxy || 'http://localhost:7890';
process.env.https_proxy = process.env.https_proxy || 'http://localhost:7890';
```

**文件**：`dist/index.js` 第 2-8 行

---

### Bug 5：搜索引擎逻辑 bug — 多引擎模式下丢弃有效结果

**现象**：Brave 搜索成功返回 3 条结果（质量分 1.0），但最终返回 `engine: None, results: 0`

**原因**：当 `FORCE_MULTI_ENGINE_SEARCH=true` 时，代码会尝试所有引擎。如果最后一个引擎（DuckDuckGo）返回 0 结果，`results.length > 0` 判断不通过，跳过了 `bestResults` 的返回逻辑，直接走到循环外的 "All approaches failed"

**代码流程分析**：
1. Bing 返回 0 结果 → 跳过
2. Brave 返回 3 结果，质量 1.0 → 记入 `bestResults`，但因 `forceMultiEngine=true` 继续尝试
3. DuckDuckGo 返回 0 结果 → `results.length > 0` 为 false，不进入处理分支
4. 循环结束 → 走到 `"All approaches failed, returning empty results"`

**修复**：在循环结束后、返回空结果前，检查 `bestResults` 是否有值

```javascript
// 修改前
console.log(`[SearchEngine] All approaches failed, returning empty results`);
return { results: [], engine: 'None' };

// 修改后
if (bestResults.length > 0) {
    console.log(`[SearchEngine] Using best results from ${bestEngine} (quality: ${bestQuality.toFixed(2)})`);
    return { results: bestResults, engine: bestEngine };
}
console.log(`[SearchEngine] All approaches failed, returning empty results`);
return { results: [], engine: 'None' };
```

**文件**：`dist/search-engine.js` 约第 85-90 行

---

### Bug 6：Bing 搜索解析失败

**现象**：Bing 页面加载成功（HTML 129609 字符），但 `.b_algo`、`.b_result`、`.b_card` 选择器均匹配 0 个结果

**原因**：Bing 页面结构可能更新，CSS 选择器已不匹配当前页面

**状态**：未修复。Brave 和 Google 搜索可作为替代，Bing 解析器需后续根据最新页面结构更新选择器

---

## 二、功能增强（2026-06-03）

### 新增 Google 搜索引擎

**文件**：`dist/search-engine.js`

**新增方法**：

1. `tryBrowserGoogleSearch(query, numResults, timeout)` — Google 搜索入口（含 2 次重试）
2. `tryBrowserGoogleSearchInternal(browser, query, numResults, timeout)` — Google 搜索内部实现
3. `parseGoogleResults(html, maxResults)` — Google 搜索结果解析

**特性**：
- 使用 Chromium 浏览器 + 代理
- locale 设为 `zh-CN`，timezoneId 设为 `Asia/Shanghai`，优化中文搜索体验
- 支持多种 Google 页面 CSS 选择器（`#search .g`、`.Gx5Zad`、`.tF2Cxc` 等）
- URL 直接访问 `https://www.google.com/search?q=...&hl=zh-CN`

---

## 三、搜索引擎优先级调整（2026-06-03）

### 调整前

```
Browser Bing → Browser Brave → Axios DuckDuckGo
```

### 调整后（初始添加 Google）

```
Browser Bing → Browser Google → Browser Brave → Axios DuckDuckGo
```

### 最终调整（Google 置首）

```
Browser Google → Browser Bing → Browser Brave → Axios DuckDuckGo
```

**调整原因**：
- Google 中文搜索结果质量远优于 Bing
- Bing 当前存在解析失败问题（Bug 6）
- Brave 作为备用表现稳定
- DuckDuckGo 作为最后兜底

---

## 四、完整 MCP 配置示例

以下为 `~/.codebuddy/mcp.json` 的完整配置，供参考：

```json
{
  "mcpServers": {
    "web-search-mcp": {
      "command": "node",
      "args": [
        "E:\\agent\\blue-skillhub\\mcp\\web-search-mcp\\dist\\index.js"
      ],
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

**字段说明**：

| 字段 | 说明 |
|------|------|
| `command` | 固定为 `node`，用于启动 MCP 服务器 |
| `args` | 指向编译后的入口文件 `dist/index.js`（绝对路径） |
| `BROWSER_TYPES` | 浏览器类型，仅 `chromium`（已修复 Bug 3，不要加 `firefox`） |
| `BROWSER_HEADLESS` | 是否无头模式，`true` 为后台运行不弹窗 |
| `HTTP_PROXY` / `HTTPS_PROXY` | 代理地址（大小写各一份，确保兼容） |
| `http_proxy` / `https_proxy` | 同上，小写形式（部分库只读小写） |
| `FORCE_MULTI_ENGINE_SEARCH` | 设为 `true` 启用多引擎模式，会依次尝试 Google → Bing → Brave → DuckDuckGo |
| `DEFAULT_NUM_RESULTS` | 每次搜索默认返回的结果数量 |
| `SEARCH_TIMEOUT` | 单个搜索引擎的超时时间（毫秒） |

**注意事项**：

1. **代理必配**：Playwright 不会自动读取系统代理，必须在 `env` 中显式设置（Bug 2 已在代码层面修复代理传递，但 `env` 中仍需提供地址）
2. **路径使用双反斜杠**：Windows 下 JSON 中的 `\` 需转义为 `\\`
3. **环境变量兜底**：即使 `env` 未正确传递，`dist/index.js` 入口处已硬编码默认值（Bug 4 修复），但建议仍然在配置中显式声明
4. **多 MCP 服务器**：如需同时配置多个 MCP 服务器，在 `mcpServers` 下添加新的 key 即可：

```json
{
  "mcpServers": {
    "web-search-mcp": {
      "command": "node",
      "args": ["E:\\agent\\blue-skillhub\\mcp\\web-search-mcp\\dist\\index.js"],
      "env": { "..." : "..." }
    },
    "another-mcp-server": {
      "command": "npx",
      "args": ["-y", "some-other-mcp-server"],
      "env": {}
    }
  }
}
```

---

## 五、上下文爆炸防护（2026-06-10）

### 背景

使用 Claude Code 通过第三方中转接口（如 Coding Plan）调用 `full-web-search` 时，MCP 输出可达 **500KB+ / 条 × 5 条 = 2.5MB+** 原文塞进上下文，导致：

1. Claude Code "Cogitated for 3m 25s"，憋很久处理巨量上下文
2. 中转网关吃不住，返回 `empty or malformed response (HTTP 200)`
3. 同一搜索请求被重复执行
4. 网页内容大量重复（火山方舟页面同一用户评价重复 4 次、FAQ 重复 3 次）

**根因**：`full-web-search` 默认 `includeContent=true`、`maxContentLength=500KB`、`limit=5`，无截断、无上限、无去重。

---

### Bug 7：内容提取无截断，500KB/条塞爆上下文

**现象**：单次搜索输出超 10 万字符，中转接口返回空响应

**修复**：三层截断体系

| 层级 | 参数 | 原值 | 修复后 |
|------|------|------|--------|
| 单条结果 | `maxContentLength` 默认/硬上限 | 500000 / 无 | **6000 / 8000** |
| 全局输出 | `MAX_TOTAL_OUTPUT` | 无 | **40000** |
| 单页抓取 | `get-single-web-page-content` 上限 | 无 | **10000** |
| 环境变量 | `MAX_CONTENT_LENGTH` | 无硬上限 | **10000 cap** |

**文件**：`dist/index.js`、`dist/enhanced-content-extractor.js`、`dist/content-extractor.js`、`dist/utils.js`

---

### Bug 8：搜索结果数无上限

**现象**：`limit` 默认 5、可设到 10，5 条全文 = 巨量上下文

**修复**：`limit` 默认改为 3，硬上限 5

| 工具 | 原默认 / 上限 | 修复后 |
|------|--------------|--------|
| `full-web-search` | 5 / 10 | **3 / 5** |
| `get-web-search-summaries` | 5 / 10 | **3 / 5** |
| `handleWebSearch` 内部 | 5 | **3** |

**文件**：`dist/index.js`（schema 定义 + validateAndConvertArgs + handleWebSearch + summaries handler）

---

### Bug 9：同一查询被重复执行

**现象**：崩溃日志中同一个 `full-web-search` 查询被 Claude Code 连续调用两次，输出翻倍

**修复**：60 秒防重复搜索机制

```javascript
// 新增 recentSearches Map
this.recentSearches = new Map(); // query → timestamp

// 在 full-web-search handler 中
const normalizedQuery = args.query.toLowerCase().trim().replace(/\s+/g, ' ');
const now = Date.now();
const lastSearchTime = this.recentSearches.get(normalizedQuery);
if (lastSearchTime && (now - lastSearchTime) < 60000) {
    return { content: [{ type: 'text', text: 'Search for "..." was already performed recently.' }] };
}
this.recentSearches.set(normalizedQuery, now);
// 自动清理 120 秒前的缓存
```

**文件**：`dist/index.js`

---

### Bug 10：`cleanText` 用 `\s+` 把换行压成空格，摧毁段落结构 🔴

**现象**：`parseContent` 刚输出的结构化文本（带 `\n` 段落分隔），被 `cleanText` 的 `.replace(/\s+/g, ' ')` 一行压扁成无结构大段落。后续 `smartTruncate` 的"找换行"层永远命中不了。

**修复**：只压缩水平空白，保留 `\n`

```javascript
// 修改前
.replace(/\s+/g, ' ')           // 换行也被压成空格
.replace(/\n\s*\n/g, '\n')      // 段落分隔被消除

// 修改后
.replace(/[ \t]+/g, ' ')        // 只压缩空格和 tab，保留 \n
.replace(/\n{3,}/g, '\n\n')     // 3+ 连续换行压成 2 个（保留段落分隔）
```

**文件**：`dist/utils.js`

---

### Bug 11：`parseContent` 标题和段落不按文档顺序 🔴

**现象**：先 `find('h1,h2,...')` 遍历所有标题，再 `find('p,li,...')` 遍历所有段落。输出时标题全堆前面、段落全堆后面，结构完全脱节。

```
## 产品介绍        ← 所有标题先输出
## 套餐详情
方舟 Coding Plan…  ← 所有段落后输出
Lite 套餐 ¥49/月…
```

**修复**：合并为单次遍历，按文档顺序提取；跳过含嵌套块元素的父元素避免重复

```javascript
// 修改前：两次独立遍历
$mainElement.find('h1, h2, h3, h4, h5, h6').each(...)
$mainElement.find('p, li, td, th, blockquote, pre, dd, dt').each(...)

// 修改后：单次遍历，文档顺序
$mainElement.find('h1, h2, h3, h4, h5, h6, p, li, blockquote, pre, dd, dt').each(function () {
    // 按标签类型区分 heading / paragraph
    // 跳过含嵌套块元素的父元素（避免 p>ul 导致文本重复）
})
```

**文件**：`dist/enhanced-content-extractor.js` 的 `parseContent` 方法

---

### Bug 12：`forEach` 里用 `return` 代替 `break`，输出多个截断提示 🔴

**现象**：全局输出截断逻辑用了 `result.results.forEach(...)` + `return`，但 `forEach` 的 `return` 等于 `continue` 不是 `break`。超限时每个剩余迭代都会拼接一个 `[Output truncated...]` 字符串。

**修复**：改为 `for...of` + 真正的 `break`

```javascript
// 修改前
result.results.forEach((searchResult, idx) => {
    if (responseText.length >= MAX_TOTAL_OUTPUT) {
        responseText += `[Output truncated...]`;
        return;  // ← 这是 continue，不是 break！
    }
    ...
});

// 修改后
for (let idx = 0; idx < result.results.length; idx++) {
    const searchResult = result.results[idx];
    if (responseText.length >= MAX_TOTAL_OUTPUT) {
        responseText += `[Output truncated: ${omitted} result(s) omitted.]`;
        break;  // ← 真正的 break
    }
    ...
}
```

**文件**：`dist/index.js`

---

### Bug 13：`cleanTextContent` 过度删除英文词 🟡

**现象**：正则 `image|img|photo|picture|gallery|slideshow|carousel` 会把正文里出现的这些词全部删掉，如 "The image quality is great" → "The quality is great"。正则 `cookie|privacy|terms` 会把讨论隐私政策的文章内容删空。

**修复**：删除这些过度正则，只保留 base64 数据和完整 UI 短语

```javascript
// 修改前
text = text.replace(/image|img|photo|picture|gallery|slideshow|carousel/gi, '');
text = text.replace(/cookie|privacy|terms|conditions|disclaimer|legal|copyright|all rights reserved/gi, '');

// 修改后：只删 base64 数据和完整 UI 短语
text = text.replace(/data:image\/[^;]+;base64,[A-Za-z0-9+/=]+/g, '');
text = text.replace(/\b(click to enlarge|click for full size|view larger|download image)\b/gi, '');
text = text.replace(/\b(accept all cookies|cookie settings|privacy policy|terms of service|all rights reserved)\b/gi, '');
```

**文件**：`dist/enhanced-content-extractor.js` 的 `cleanTextContent` 方法

---

### 新增功能：`smartTruncate` 句子边界感知截断

替代所有 `substring(0, N)` 硬切，在句子/段落/词边界处截断：

```
优先级：句号(。！？.!?) > 段落换行(\n) > 空格(不断词) > 硬切(兜底)
约束：边界必须在 maxLength × 0.6 之后才采用（避免丢太多内容）
```

**覆盖范围**：所有截断点统一使用

| 截断点 | 原方式 | 修复后 |
|--------|--------|--------|
| `utils.cleanText` | `substring` 硬切 | `smartTruncate` |
| `index.js` 输出截断 | `substring` 硬切 | `smartTruncate` |
| `index.js` 单页截断 | `substring` 硬切 | `smartTruncate` |
| `extractor` axios 层 | `substring` 硬切 | `smartTruncate` |

截断标注改为 `~6000 characters`（波浪号表示语义截断），并显示原文长度如 `Original: 45678 characters`。

**文件**：`dist/utils.js`（新增 `smartTruncate` 函数）、`dist/index.js`、`dist/enhanced-content-extractor.js`（导入并使用）

---

### 修复后参数对照表

| 参数 | 原始值 | 修复后 |
|------|--------|--------|
| `full-web-search` limit 默认/上限 | 5 / 10 | **3 / 5** |
| `full-web-search` includeContent 默认 | true | true（保持不变，搜索就是要看内容） |
| `maxContentLength` 默认/硬上限 | 500000 / 无 | **6000 / 8000** |
| 全局输出硬上限 `MAX_TOTAL_OUTPUT` | 无 | **40000** |
| 单页抓取 `maxContentLength` 上限 | 无 | **10000** |
| `MAX_CONTENT_LENGTH` 环境变量上限 | 无 | **10000** |
| `cleanText` maxLength 默认 | 10000 | **6000** |
| `get-web-search-summaries` limit 默认 | 5 | **3** |

---

## 六、修改文件清单（全量）

| 文件 | 修改内容 |
|------|---------|
| `c:\Users\blue\.codebuddy\mcp.json` | 添加服务器名称 key `web-search-mcp` |
| `dist/index.js` | 入口硬编码环境变量；限制参数默认值与硬上限；全局输出截断；防重复搜索；`forEach`→`for...of`；导入 `smartTruncate` |
| `dist/search-engine.js` | 添加 proxy 参数、修复多引擎逻辑 bug、新增 Google 搜索引擎、调整优先级 |
| `dist/browser-pool.js` | 添加 proxy 参数、默认 `BROWSER_TYPES` 改为 `chromium` |
| `dist/enhanced-content-extractor.js` | `MAX_CONTENT_LENGTH` 默认 6000 + 10000 硬上限；`parseContent` 按文档顺序提取并保留段落结构；`cleanTextContent` 删除过度正则；导入 `smartTruncate` 替换硬切 |
| `dist/content-extractor.js` | `MAX_CONTENT_LENGTH` 默认 6000 + 10000 硬上限 |
| `dist/utils.js` | 新增 `smartTruncate` 句子边界感知截断函数；`cleanText` 保留换行、使用 `smartTruncate`；默认 maxLength 改为 6000 |

---
