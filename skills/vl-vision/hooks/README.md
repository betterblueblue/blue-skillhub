# 识图门禁 hook — 使用说明

> 配套 vl-vision 的 hook,把「识图必须走 vl-vision」这条规则变成硬门禁,
> 不再依赖模型自觉。

## 它解决什么问题

纯文本模型(如 deepseek)不支持 vision,如果让它直接 Read 图片 / 用户直接粘图,
图片会塞进主模型,API 立即报 `400 当前模型不支持该能力:vision`,会话卡死、
反复死循环。本 hook 无条件拦截这两条通道,引导改用 vl-vision。

**设计原则:不做任何模型判断(没有黑名单/白名单/开关)。挂 hook 就拦,摘 hook 就放行。**

- 当前用纯文本模型(如 deepseek)→ 挂上 hook,图片被拦、走 vl-vision
- 当前用多模态模型(claude/gpt 等能看图)→ 摘掉 hook(或换配置),直接看图

## 文件位置

```
skills/vl-vision/
├── SKILL.md                    # Skill 入口文档(内有本 hook 的指引)
├── vl_vision.py
└── hooks/
    ├── block-image-read.py     # PreToolUse hook:拦 Read 工具读图片文件
    ├── block-image-attachment.py  # UserPromptSubmit hook:拦用户直接粘贴图片
    └── README.md               # 本文件(使用说明)
```

两份副本,职责不同:

| 位置 | 作用 |
|------|------|
| 仓库 `E:\agent\blue-skillhub\skills\vl-vision\hooks\` | 版本库源,随 skill 一起提交、改版 |
| 全局 `C:\Users\blue\.claude\skills\vl-vision\hooks\` | 运行时安装副本,settings.json 实际指向这里 |

改脚本先去改仓库源,再同步到全局副本(和这个 skill 其他文件的部署方式一致)。

## 安装

1. 把 `hooks/` 目录放到全局 skill 目录:
   `C:\Users\blue\.claude\skills\vl-vision\hooks\`
2. 在全局 `C:\Users\blue\.claude\settings.json` 的 `hooks` 字段挂载两个 hook:
   - `PreToolUse`(matcher=Read)→ 拦工具读图片
   - `UserPromptSubmit` → 拦用户直接粘贴图片(`[Image #N]`,不走 Read 工具)
3. **重启会话生效**——Claude Code 启动时才加载 hooks,改完配置当前会话不会自动生效。

### 完整配置示例(ccswitch / deepseek)

用 ccswitch 管理时,把下面整段写进全局 `~/.claude/settings.json`
(替换 `sk-xxx` 为真实 key):

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-xxxxxxxxxxxxxxxxxxxxxxxxx",
    "ANTHROPIC_BASE_URL": "http://118.24.52.21:8080",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "deepseek-v4-flash-0731[1M]",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME": "deepseek-v4-flash-0731",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash-0731",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME": "deepseek-v4-flash-0731",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-flash-0731[1M]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME": "deepseek-v4-flash-0731",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-flash-0731[1M]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "deepseek-v4-flash-0731",
    "ANTHROPIC_MODEL": "deepseek-v4-flash-0731[1M]",
    "CLAUDE_CODE_DISABLE_ATTACHMENTS": "1",
    "CLAUDE_CODE_EFFORT_LEVEL": "max",
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1",
    "STEP_API_KEY": "sk-your-stepfun-key"
  },
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "command": "python C:/Users/blue/.claude/skills/vl-vision/hooks/block-image-read.py",
            "type": "command"
          }
        ],
        "matcher": "Read"
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "command": "python C:/Users/blue/.claude/skills/vl-vision/hooks/block-image-attachment.py",
            "type": "command"
          }
        ]
      }
    ]
  },
  "includeCoAuthoredBy": false,
  "model": "opus",
  "skipDangerousModePermissionPrompt": true
}
```

> 要点:
> 1. **不需要任何 `CLAUDE_MODEL_SUPPORTS_VISION` / 黑名单 / 白名单**——hook 无条件拦,不做模型判断。
> 2. **必须挂两个 hook**——只挂 PreToolUse 只拦 Read 图片,直接粘图还会 400。
> 3. **`STEP_API_KEY` 必须有**——vl-vision 识图要调 stepfun API,没它识别失败。

**换多模态模型(claude/gpt 等能看图)**:摘掉 settings.json 里的两个 hook(或换一份不带 hooks 的 ccswitch 配置),直接看图,不用改任何脚本。

## 手动测试

给 hook 喂 JSON 事件模拟入参,检查退出码:

```bash
# 1. Read 图片 → 应 exit 2(无条件拦)
echo '{"tool_name":"Read","tool_input":{"file_path":"C:/x/a.png"}}' \
  | python block-image-read.py; echo "exit=$?"

# 2. 读文本文件 → 应 exit 0(放行)
echo '{"tool_name":"Read","tool_input":{"file_path":"C:/x/main.py"}}' \
  | python block-image-read.py; echo "exit=$?"

# 3. 粘图 → 应 exit 2(无条件拦)
echo '{"prompt":"[Image #1] 看看这个"}' \
  | python block-image-attachment.py; echo "exit=$?"

# 4. 无图文本 → 应 exit 0(放行)
echo '{"prompt":"读一下这个文件"}' \
  | python block-image-attachment.py; echo "exit=$?"
```

## 卸载

1. 从 `settings.json` 删掉 `hooks` 块(或整段 `PreToolUse` / `UserPromptSubmit` 条目)。
2. 删除 `C:\Users\blue\.claude\skills\vl-vision\hooks\`(仓库源可留着)。
3. 重启会话。

## 边界与已知限制

- 拦两条通道:
  1. **`Read` 工具读图片文件** → `PreToolUse` hook(`block-image-read.py`)
  2. **用户直接把图片粘贴进对话**(显示为 `[Image #N]`)→ `UserPromptSubmit`
     hook(`block-image-attachment.py`)——这条不走 Read 工具,PreToolUse 拦不到,
     图片会直接塞进主模型触发 400,所以单独拦。
- **无条件拦,不做模型判断**——挂上就拦所有模型的图片读取。要放行多模态模型,
  摘掉 hook,不是改脚本。
- hook 自身出错时放行(解析失败返回 0),不会因为门禁坏了卡住整个工作流。
- 若未来出现别的渠道把图片塞进主模型(如某个 MCP 截图工具直传),需要另加拦截。
