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

如果 Claude Code 已配置只读 code graph / repo-map MCP，`/pathfinder`、`/impact` 和 `/impact-pro` 会按各自规则自动探测使用；没有配置也应诚实降级到 Read/Grep，不影响基本流程。

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

## 4. 安装 VL Vision

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

## 5. 常见踩坑

| 问题 | 处理 |
|------|------|
| MCP JSON 里还是旧路径 | 把 `args` 改成当前仓库的绝对路径 |
| `/impact` 不生效 | 确认 skill 复制到了正确客户端目录，并重启客户端 |
| `/pathfinder` 不生效 | 确认 skill 复制到了正确客户端目录，并重启客户端 |
| Claude Code `--print` 不识别 `/impact` | prompt 前加 `--`，例如 `claude --print -- "/impact ..."` |
| 运行 MCP 缺 Chromium | 执行 `npx playwright install chromium` |
| agent 想直接写文件 | 必须要求它等待 `确认 Step N` |
| 中断后说“继续”就想写 | 先读 `_active-state.md`、实施文档、preflight 和执行记录，复核磁盘状态后重新要求 `确认 Step N` |

## 6. 最小验收

安装完成后，至少确认：

- RuleBlade 能被目标项目读取。
- `/pathfinder` 能触发，且只说明只读摸底范围。
- `/impact` 和 `/impact-pro` 能触发。
- MCP 服务能手动启动。
- MCP 客户端能看到 3 个工具。
- `impact` / `impact-pro` 在只分析测试中不会写文件，并明确 `_active-state.md` 不能替代 `确认 Step N`。
