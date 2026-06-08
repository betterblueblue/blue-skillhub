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

## 2. 安装 Impact Skills

### Codex

复制到 Codex skills 目录：

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.codex\skills\impact" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact-pro" "$env:USERPROFILE\.codex\skills\impact-pro" -Recurse -Force
```

重启 Codex 后验证：

```text
/impact
/impact-pro
```

能进入变更意图捕获流程即可。

### Claude Code

复制到 Claude skills 目录：

```powershell
Copy-Item "E:\agent\blue-skillhub\skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
Copy-Item "E:\agent\blue-skillhub\skills\impact-pro" "$env:USERPROFILE\.claude\skills\impact-pro" -Recurse -Force
```

验证：

```powershell
claude --print -- "/impact 只做测试：请说明 impact 的适用范围，不要写文件"
claude --print -- "/impact-pro 只做测试：请说明 impact-pro 的适用范围，不要写文件"
```

预期：

- `/impact` 应说明它面向 Java/Spring/MyBatis/RuoYi 类现有系统。
- `/impact-pro` 应说明它面向已验证 profile 覆盖范围内的多栈现有系统。
- 两者都应强调写操作必须 `确认 Step N`。

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
| Claude Code `--print` 不识别 `/impact` | prompt 前加 `--`，例如 `claude --print -- "/impact ..."` |
| 运行 MCP 缺 Chromium | 执行 `npx playwright install chromium` |
| agent 想直接写文件 | 必须要求它等待 `确认 Step N` |

## 6. 最小验收

安装完成后，至少确认：

- RuleBlade 能被目标项目读取。
- `/impact` 和 `/impact-pro` 能触发。
- MCP 服务能手动启动。
- MCP 客户端能看到 3 个工具。
- `impact` / `impact-pro` 在只分析测试中不会写文件。
