# Blue SkillHub 安装与验证 Checklist

> 目的：让别人能按步骤把规则、Skill 和 MCP 真正装起来，而不是只看理念介绍。

## 0. 先确认仓库绝对路径

本文示例使用：

```text
E:\agent\blue-skillhub
```

如果你的仓库不在这个位置，所有示例里的 `E:\agent\blue-skillhub` 都要替换成你本机的绝对路径。

PowerShell 可用下面命令确认：

```powershell
Resolve-Path .
```

## 1. 安装 RuleBlade

适用：Claude Code / Codex / 其他支持项目规则文件的 agent。

复制到 Claude Code 项目：

```powershell
Copy-Item "E:\agent\blue-skillhub\claudecode行为规范\ruleblade\CLAUDE.md" "你的项目根目录\CLAUDE.md"
```

复制到 Codex 项目：

```powershell
Copy-Item "E:\agent\blue-skillhub\claudecode行为规范\ruleblade\CLAUDE.md" "你的项目根目录\AGENT.md"
```

验证：

1. 在目标项目启动 agent。
2. 让 agent 简述当前项目规则。
3. 应能看到“先思考再编码、简单优先、精准修改、上下文先行、写操作确认”等规则。

## 2. 安装 Pathfinder / Impact Skills

### Codex

复制到 Codex skills 目录：

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.codex\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.codex\skills\impact" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact-pro" "$env:USERPROFILE\.codex\skills\impact-pro" -Recurse -Force
```

重启 Codex 后验证：

```text
/pathfinder
/impact
/impact-pro
```

`/pathfinder` 能进入陌生项目摸底流程，`/impact` / `/impact-pro` 能进入变更意图捕获流程即可。

### Claude Code

复制到 Claude skills 目录：

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact-pro" "$env:USERPROFILE\.claude\skills\impact-pro" -Recurse -Force
```

验证：

```powershell
claude --print -- "/pathfinder 只做测试：请说明 pathfinder 的适用范围，不要写文件"
claude --print -- "/impact 只做测试：请说明 impact 的适用范围，不要写文件"
claude --print -- "/impact-pro 只做测试：请说明 impact-pro 的适用范围，不要写文件"
```

预期：

- `/pathfinder` 应说明它面向陌生现有项目的只读认知地图。
- `/impact` 应说明它面向 Java/Spring/MyBatis/RuoYi 类现有系统。
- `/impact-pro` 应说明它面向已验证 profile 覆盖范围内的多栈现有系统。
- `/impact` 和 `/impact-pro` 都应强调写操作必须 `确认 Step N`。

如果 Claude Code 已配置只读 code graph / repo-map MCP，`/pathfinder`、`/impact` 和 `/impact-pro` 会按各自规则自动探测使用；没有配置也应诚实降级到 Read/Grep，不影响基本流程。Cursor 用户可按 [§4 安装 Codegraph MCP](#4-安装-codegraph-mcp可选) 配置；若 MCP 已连接但没有工具，见 [README FAQ：Codegraph MCP](../README.md#codegraph-mcp-显示已连接但没有工具no-tools)。

### 可选：启用 Claude Code 写前门禁 Hook

适用：希望把 `确认 Step N` 从 prompt 纪律补强为工具执行前检查的 Claude Code 项目。

复制 hook 到目标项目：

```powershell
New-Item "你的项目根目录\.claude" -ItemType Directory -Force
Copy-Item "E:\agent\blue-skillhub\.claude\hooks" "你的项目根目录\.claude\hooks" -Recurse -Force
```

把 `E:\agent\blue-skillhub\.claude\hooks\impact-write-gate.settings.example.json` 的 `PreToolUse` 配置合并到目标项目的 `.claude/settings.json` 或 `.claude/settings.local.json`，然后在目标项目根目录放一个空文件：

```powershell
New-Item "你的项目根目录\.impact-protected" -ItemType File
```

预期：受保护根目录内的 `Write` / `Edit` / `MultiEdit` / 写类 `Bash` 需要当前对话最新用户消息以 `确认 Step N` 开头才放行一次。这个 hook 不是沙箱，DB 仍必须使用只读账号。

## 3. 安装 Web Search MCP

进入 MCP 目录：

```powershell
cd E:\agent\blue-skillhub\mcp\web-search-mcp
npm install
npx playwright install chromium
```

手动启动验证：

```powershell
node .\dist\index.js
```

看到下面输出后按 `Ctrl+C` 退出：

```text
Web Search MCP Server started
Waiting for MCP messages...
```

MCP JSON 示例：

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

如果仓库路径不同，只改 `args` 中的绝对路径。

验证：

1. 重启 MCP 客户端。
2. 确认出现 `full-web-search`、`get-web-search-summaries`、`get-single-web-page-content`。
3. 让 agent 搜索一个普通关键词，例如 `MCP protocol`。

## 4. 安装 Codegraph MCP（可选）

适用：Cursor 等支持 MCP 的客户端；给 Pathfinder / Impact / Impact-Pro 提供只读结构索引（入口、依赖边、callers 等）。不是前置必装项，未配置时会降级到 Read/Grep。

### 4.1 建索引

在**要打开的工作区根目录**执行（只需一次）：

```powershell
cd E:\agent\blue-skillhub
codegraph init
```

确认出现 `.codegraph/` 目录（含 `codegraph.db` 等）。

### 4.2 项目级 MCP 配置（推荐）

不要在全局 `%USERPROFILE%\.cursor\mcp.json` 里裸跑 `codegraph serve --mcp`——Cursor 不一定传 workspace cwd，容易 **已连接但没有工具**。详见 [README FAQ：Codegraph MCP](../README.md#codegraph-mcp-显示已连接但没有工具no-tools)。

本仓库已带好 wrapper，在**项目根** `.cursor/mcp.json` 中配置（路径改成你的绝对路径）：

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "E:/agent/blue-skillhub/.cursor/codegraph-mcp.cmd",
      "args": []
    }
  }
}
```

wrapper 内容见 `.cursor/codegraph-mcp.cmd`，核心是 `codegraph serve --mcp --path "<项目根>"`。

建议把全局 `~/.cursor/mcp.json` 里的 codegraph 条目清掉，只保留项目级配置，避免冲突。

### 4.3 验证

1. 重载 MCP（Cursor 设置里刷新 codegraph，或重启 Cursor）。
2. 确认出现 4 个工具：`codegraph_search`、`codegraph_callers`、`codegraph_node`、`codegraph_explore`。
3. 新开 Agent 会话，跑 `/pathfinder` 只读摸底；地图【0】结构索引辅助应能标 `used`（而非长期 `degraded`）。

仍无工具时，按 [README FAQ 排查表](../README.md#codegraph-mcp-显示已连接但没有工具no-tools) 逐项检查。

## 5. 安装 VL Vision

安装依赖：

```powershell
pip install requests
```

查看模板：

```powershell
python E:\agent\blue-skillhub\skills\vl-vision\vl_vision.py --list-templates
```

配置 key 后测试：

```powershell
$env:SILICONFLOW_API_KEY="sk-your-key"
python E:\agent\blue-skillhub\skills\vl-vision\vl_vision.py path\to\image.png
```

## 6. 常见踩坑

| 问题 | 处理 |
|------|------|
| Codegraph MCP 已连接但没有工具 | 不要用全局裸 `serve --mcp`；改用项目级 wrapper + `--path`，见 [下文排障](#codegraph-mcp-显示已连接但没有工具no-tools) 与 [§4](#4-安装-codegraph-mcp可选) |
| MCP JSON 里还是旧路径 | 把 `args` 改成当前仓库的绝对路径 |
| `/impact` 不生效 | 确认 skill 复制到了正确客户端目录，并重启客户端 |
| `/pathfinder` 不生效 | 确认 skill 复制到了正确客户端目录，并重启客户端 |
| Claude Code `--print` 不识别 `/impact` | prompt 前加 `--`，例如 `claude --print -- "/impact ..."` |
| 运行 MCP 缺 Chromium | 执行 `npx playwright install chromium` |
| agent 想直接写文件 | 必须要求它等待 `确认 Step N` |
| 中断后说“继续”就想写 | 先读 `_active-state.md`、实施文档、preflight 和执行记录，复核磁盘状态后重新要求 `确认 Step N` |

### Codegraph MCP 显示已连接，但没有工具（No tools）

**现象**

- Cursor 设置里 `codegraph` MCP 开关是绿的，状态像“已连接”
- 展开后却是 **No tools**，或只有连接信息、看不到 `codegraph_search` / `codegraph_explore` 等
- Agent 侧仍提示 workspace 未索引、结构索引不可用
- 本地其实已有 `.codegraph/codegraph.db`，CLI 查询正常

**原因**

`codegraph serve --mcp` 需要知道**项目根目录**才能找到 `.codegraph/` 索引。若在全局 `~/.cursor/mcp.json`（Windows：`%USERPROFILE%\.cursor\mcp.json`）里只写：

```json
"codegraph": { "command": "codegraph", "args": ["serve", "--mcp"] }
```

Cursor 的 Shared MCP **不一定**会把当前 workspace 的工作目录传给子进程。codegraph 启动时找不到 `.codegraph/`，就会注册 **0 个工具**，界面仍可能显示“已连接”。

**解决办法（推荐：项目级 wrapper）**

1. **先建索引**（目标仓库根目录，只需一次）：

```powershell
cd E:\agent\blue-skillhub
codegraph init
```

2. **清空或移除全局 codegraph 配置**，避免和项目配置冲突。全局文件里 `mcpServers` 留空即可：

```json
{ "mcpServers": {} }
```

3. **在项目根 `.cursor/mcp.json` 里指向 wrapper**（本仓库已带好，可直接参考）：

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "E:/agent/blue-skillhub/.cursor/codegraph-mcp.cmd",
      "args": []
    }
  }
}
```

4. **wrapper 负责解析项目根并传入 `--path`**（`.cursor/codegraph-mcp.cmd`）：

```bat
@echo off
setlocal
set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
codegraph serve --mcp --path "%ROOT%"
```

路径请改成你本机仓库的绝对路径；Linux/macOS 可写等价的 `.sh` wrapper，核心仍是 `codegraph serve --mcp --path "<项目根>"`。

5. **重载 MCP**（Cursor 设置里刷新 codegraph，或重启 Cursor）。

**如何确认生效**

- MCP 面板里 codegraph 应列出 4 个工具：`codegraph_search`、`codegraph_callers`、`codegraph_node`、`codegraph_explore`
- 新开 Agent 会话后，Pathfinder / Impact 的结构索引辅助应能标为 `used`，而不是长期 `degraded`

**仍不行的排查顺序**

| 检查项 | 说明 |
|--------|------|
| `.codegraph/` 是否在**打开的工作区根** | 用 File → Open Folder 打开的目录应与 `codegraph init` 一致 |
| wrapper 里的 `--path` | 必须指向含 `.codegraph/` 的那一层，不是子目录 |
| 全局 vs 项目 MCP 重复配置 | 只保留项目级 wrapper，全局不要再用裸 `serve --mcp` |
| `codegraph` 是否在 PATH | 终端能执行 `codegraph --version` |

Pathfinder / Impact 在 MCP 不可用时会退回到 Read/Grep，不影响基本流程；修好 MCP 后主要是结构发现和 blast radius 更快、更准。

## 7. 最小验收

安装完成后，至少确认：

- RuleBlade 能被目标项目读取。
- `/pathfinder` 能触发，且只说明只读摸底范围。
- `/impact` 和 `/impact-pro` 能触发。
- Web Search MCP 服务能手动启动；MCP 客户端能看到 3 个 web-search 工具。
- （可选）Codegraph MCP 客户端能看到 4 个 codegraph 工具。
- `impact` / `impact-pro` 在只分析测试中不会写文件，并明确 `_active-state.md` 不能替代 `确认 Step N`。
