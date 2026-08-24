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
    ├── block-image-read.py     # 本 hook(脚本本体)
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
2. 在全局 `C:\Users\blue\.claude\settings.json` 的 `hooks` 字段挂载(只加这个字段,别动别的):

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Read",
           "hooks": [
             {
               "type": "command",
               "command": "python C:/Users/blue/.claude/skills/vl-vision/hooks/block-image-read.py"
             }
           ]
         }
       ]
     }
   }
   ```

3. **重启会话生效**——Claude Code 启动时才加载 hooks,改完配置当前会话不会自动生效。

## 判断逻辑(换模型怎么处理)

hook 按以下顺序决定放行还是阻断:

```
① 环境变量 CLAUDE_MODEL_SUPPORTS_VISION
     =1 / true / yes / on   → 放行
     =0 / false / no / off  → 强制阻断(即使白名单命中)
② 未设开关 → 按模型名白名单兜底(见 `vision_whitelist.json` 的 `keywords`,
     2026-08 收敛为「只覆盖主流 API 厂商多模态」:Anthropic(claude) / Google(gemini) /
     OpenAI(gpt-4o·4.1·4.5·5) / 智谱(glm-4v·5v) / 通义(qwen-vl) / 豆包(doubao-vision·
     seed) / Kimi / 阶跃(step-3) / 百度(ernie-vl) / 腾讯(hunyuan-vision)。不含
     论文/开源模型(如 llava、internvl)——代理网关不提供,留着只会误导)
     → 命中放行
③ 都拿不准 → 阻断(安全优先),引导改用 vl-vision
```

- **换主流多模态模型**(名字在白名单里)→ 自动放行,零改动。
- **换多模态模型但名字不在白名单**(本地部署的开源 VLM、代理自定义名等)
  → 设环境变量 `CLAUDE_MODEL_SUPPORTS_VISION=1` 后重启会话即可放行,不用改脚本。
  开关值可以放在 `settings.json` 的 `env` 里,或系统环境变量。
- **想强制一律走 vl-vision** → 设 `CLAUDE_MODEL_SUPPORTS_VISION=0`。

## 参数:`CLAUDE_MODEL_SUPPORTS_VISION`

手动控制门禁放行/阻断的环境变量,优先级高于模型名白名单。**不设置就用模型名白名单自动判断**,所以不是必须项——它存在的意义是:你换了一个白名单外的多模态模型(或想强制走 vl-vision)时,不需要改脚本,设一个变量就搞定。

| 值 | 行为 | 典型场景 |
|----|------|----------|
| `1` / `true` / `yes` / `on` | 放行,允许直接 Read 图片 | 换了多模态模型,名字不在白名单 |
| `0` / `false` / `no` / `off` | 强制阻断,一律走 vl-vision | 想确保任何图片都不经主模型"亲眼看" |
| 不设置 | 用模型名白名单兜底判断 | 默认;换白名单内的模型时无需关心 |

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

# 3. 白名单模型(如 claude-sonnet-5)→ 应 exit 0(放行)
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
