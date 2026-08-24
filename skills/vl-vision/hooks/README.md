# 识图门禁 hook — 使用说明

> 配套 vl-vision 的 PreToolUse hook,把「识图必须走 vl-vision」这条规则变成硬门禁,
> 不再依赖模型自觉。

## 它解决什么问题

全局规则 CLAUDE.md 第 0 条要求:识图必须走 vl-vision,禁止用模型自身能力直接"看"图。
但规则只是文字,执行靠模型记性。弱模型(如 deepseek-v4-flash)看到图片时本能走
`Read` 工具,把图片直接塞给主模型——而这类模型不支持 vision,API 立即报
`400 当前模型不支持该能力:vision`,会话卡死、反复死循环。

本 hook 在 `Read` 工具执行前拦截:目标是图片文件、且当前模型不支持 vision 时,
当场阻断,并把引导语(改用 `vl_vision.py`)作为反馈送回模型上下文,让它转去调
vl-vision。vl-vision 自己走 Bash/Python,不受本 hook 影响。

## 文件位置

```
skills/vl-vision/
├── SKILL.md                    # Skill 入口文档(内有本 hook 的指引)
├── vl_vision.py
└── hooks/
    ├── block-image-read.py     # PreToolUse hook:拦 Read 工具读图片文件
    ├── block-image-attachment.py  # UserPromptSubmit hook:拦用户直接粘贴图片
    ├── vision_blacklist.json   # 纯文本模型黑名单(当前含 deepseek 系列)
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
   (随 skill 一起部署;`vision_blacklist.json` 漏拷也不怕,脚本有内置兜底关键词能拦 deepseek)
2. 在全局 `C:\Users\blue\.claude\settings.json` 的 `hooks` 字段挂载两个 hook:
   - `PreToolUse`(matcher=Read)→ 拦工具读图片
   - `UserPromptSubmit` → 拦用户直接粘贴图片(`[Image #N]`,不走 Read 工具)
3. **重启会话生效**——Claude Code 启动时才加载 hooks,改完配置当前会话不会自动生效。

### 完整配置示例(ccswitch / deepseek)

用 ccswitch 管理时,把下面整段写进全局 `~/.claude/settings.json`
(替换 `sk-xxx` 为真实 key)。深色底是相对你的 ccswitch 模板做的关键改动:

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

> 相比旧的 ccswitch 模板改了三处:
> 1. **env 里删掉 `CLAUDE_MODEL_SUPPORTS_VISION`**——设为 `0` 会把所有模型(含多模态)强制拦掉,是坑。黑名单自动判断,不需要它。
> 2. **加 `UserPromptSubmit` hook**——只挂 PreToolUse 只拦 Read 图片,直接粘图还会 400。
> 3. **env 加 `STEP_API_KEY`**——vl-vision 识图要调 stepfun API,没这个 key 识别会失败。

**换多模态模型(claude/gemini/gpt)**:这份配置不用改——黑名单不命中,默认放行。
只有换新的纯文本模型时,才把它加进 `vision_blacklist.json` 的 `keywords`。

## 判断逻辑(换模型怎么处理)

**设计原则:默认放行,只拦纯文本模型。** 正常多模态模型直接走 Claude Code
默认机制(能看图就自己看),只有确认是纯文本模型(如 deepseek)才拦,引导改用
vl-vision。这样换新模型不会被误拦。

```
① 环境变量 CLAUDE_MODEL_SUPPORTS_VISION
     =1 / true / yes / on   → 放行(强制)
     =0 / false / no / off  → 阻断(强制,一般不设)
② 未设开关 → 按模型名黑名单兜底(见 `vision_blacklist.json` 的 `keywords`,
     当前只含 deepseek 系列纯文本:deepseek-v4/v3/r1/chat/reasoner)
     → 命中黑名单 → 阻断;不命中 → 默认放行
③ 读不到模型名 → 默认放行(不误伤正常多模态)
```

- **换任何主流多模态模型**(claude / gemini / gpt / 通义 / 豆包 / Kimi 等)
  → **自动放行,零改动**——它们不在黑名单,默认就走正常机制。
- **换纯文本模型**(deepseek 之外的新文本模型)→ 把它加进 `vision_blacklist.json`
  的 `keywords`,重启会话即拦;不加就默认放行(会 400,自己负责)。
- **想让纯文本模型临时看图** → 设环境变量 `CLAUDE_MODEL_SUPPORTS_VISION=1` 放行。

## 参数:`CLAUDE_MODEL_SUPPORTS_VISION`

手动控制门禁放行/阻断的环境变量,优先级高于黑名单。**一般不设置**——默认放行
多模态、只拦黑名单纯文本,绝大多数情况不用管它。

| 值 | 行为 | 典型场景 |
|----|------|----------|
| `1` / `true` / `yes` / `on` | 强制放行 | 纯文本模型临时想直接看图(会 400) |
| `0` / `false` / `no` / `off` | 强制阻断 | 想强制某模型一律走 vl-vision(一般不设) |
| 不设置 | 按黑名单判断 | 默认;正常多模态直接放行 |

**设置方式(任选其一)**:

```bash
# ① 系统环境变量(对所有会话生效,改完重启终端)
# Windows:setx CLAUDE_MODEL_SUPPORTS_VISION 1
#   macOS/Linux: export CLAUDE_MODEL_SUPPORTS_VISION=1

# ② 全局 settings.json 的 env 段(随 Claude Code 一起加载,推荐)
```

```json
{
  "env": {
    "CLAUDE_MODEL_SUPPORTS_VISION": "1"
  }
}
```

**生效时机**:修改后重启 Claude Code 会话才生效(和 hooks 加载时机一致)。
**误拦时解除**:如果模型其实支持看图却被拦,按上面设 `1` 重启即可;引导信息里也会提示这条。

## 手动测试

给 hook 喂 JSON 事件模拟 PreToolUse 入参,检查退出码:

```bash
# 1. 不支持 vision 的模型 + 读图片 → 应 exit 2(阻断)
export ANTHROPIC_MODEL="deepseek-v4-flash-0731"
echo '{"tool_name":"Read","tool_input":{"file_path":"C:/x/a.png"}}' \
  | python block-image-read.py; echo "exit=$?"

# 2. 同模型 + 显式开关=1 → 应 exit 0(放行,模拟"换了多模态")
export CLAUDE_MODEL_SUPPORTS_VISION=1
echo '{"tool_name":"Read","tool_input":{"file_path":"C:/x/a.png"}}' \
  | python block-image-read.py; echo "exit=$?"
unset CLAUDE_MODEL_SUPPORTS_VISION

# 3. 多模态模型(如 claude-sonnet-5,不在黑名单)→ 应 exit 0(放行)
export ANTHROPIC_MODEL="claude-sonnet-5"
echo '{"tool_name":"Read","tool_input":{"file_path":"C:/x/a.png"}}' \
  | python block-image-read.py; echo "exit=$?"

# 4. 读文本文件 / 非 Read 工具 → 应 exit 0(放行)
echo '{"tool_name":"Read","tool_input":{"file_path":"C:/x/main.py"}}' \
  | python block-image-read.py; echo "exit=$?"
```

## 卸载

1. 从 `settings.json` 删掉 `hooks` 块(或整段 `PreToolUse` 条目)。
2. 删除 `C:\Users\blue\.claude\skills\vl-vision\hooks\`(仓库源可留着)。
3. 重启会话。

## 边界与已知限制

- 拦两条通道:
  1. **`Read` 工具读图片文件** → `PreToolUse` hook(`block-image-read.py`)
  2. **用户直接把图片粘贴进对话**(显示为 `[Image #N]`)→ `UserPromptSubmit`
     hook(`block-image-attachment.py`)——这条不走 Read 工具,PreToolUse 拦不到,
     图片会直接塞进主模型触发 400,所以单独拦。
- hook 判断依赖 `ANTHROPIC_MODEL` 环境变量;读不到时按"不支持"处理(安全优先),
  可能误拦,用上面的显式开关解除。
- hook 自身出错时放行(解析失败返回 0),不会因为门禁坏了卡住整个工作流。
- 若未来出现别的渠道把图片塞进主模型(如某个 MCP 截图工具直传),需要另加拦截。
