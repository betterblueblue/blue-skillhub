# 5 分钟上手（QUICKSTART）

面向第一次使用 Blue SkillHub 的工程师：装到哪、怎么触发、第一个例子能看到什么、校验失败了怎么办。走完整个流程约 5 分钟。

## 0. 前提

- AI 客户端：Claude Code 或 Codex（其他客户端的验证程度见[环境兼容说明](docs/environment-compatibility.md)）
- Python 3（校验脚本需要，`python --version` 确认）
- 已克隆本仓库，以下命令在仓库根目录执行

## 1. 装到哪

Claude Code 用户（Codex 用户把 `.claude\skills` 换成 `.codex\skills`）：

```powershell
# 升级重装时必须先删旧目录再复制：Copy-Item 对已存在的目标目录会把新版嵌套进去，不会覆盖
"pathfinder","impact" |
  ForEach-Object { Remove-Item "$env:USERPROFILE\.claude\skills\$_" -Recurse -Force -ErrorAction Ignore }

Copy-Item "skills\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder" -Recurse -Force
Copy-Item "skills\impact" "$env:USERPROFILE\.claude\skills\impact" -Recurse -Force
```

重启客户端后，输入 `/pathfinder` 或 `/impact` 能被识别即装好。0→1 新产品链路（intent 六件套）和其他组件的安装见[安装与验证清单](docs/install-and-verify-checklist.md)。

## 2. 第一个例子：只读摸清一个陌生项目

在目标项目里说：

```text
/pathfinder
这个项目我刚接手，先帮我只读摸底。
```

跑完你会得到：

- `change-impact/_project-map.md`——项目地图：技术栈、模块、入口、数据模型、运行命令、风险区域，每条结论标 `【已核实: 证据】` 或 `【推断: 待验证】`
- `change-impact/_project-map/facts/` 下两份 JSON——脚本产出的可复验基础事实

地图写入前会自动运行校验脚本 `pf_validate.py`（11 项检查），不通过不会写入。

## 3. 第二个例子：改代码前先查影响

```text
/impact
我想删除 sys_user.remark 字段，先做影响分析，不要直接改代码。
```

它会查清调用方、接口、数据库和测试的影响，按风险给出 light（简单改动）或 full（高风险改动）的分析文档。**进入任何写操作前，它会停下来等你逐步授权：**

```text
确认 Step 2
```

只有 `确认 Step N` 算数——`继续`、`好的`、`全部确认` 都会被拒绝。这是设计行为，不是 bug。

## 4. FAIL 了怎么办

校验器报 FAIL **是门禁在正常工作**——它拦下了一个真实问题，不是工具坏了。处理方式：

1. 读第一条 FAIL 信息，它会写明缺什么（如 `V1: 行号引用不存在`、`V18: 缺少真实验证结果`）
2. 按提示补齐或修正，重跑同一条校验命令
3. 重复直到 `0 failed`；退出码非 0 时**不得**把产物当作完成

几种常见情况：

- **impact full 模式首跑**：`_active-state.md` 还没有真实校验结果，第一次加 `--bootstrap`，通过后再不带它复跑一次
- **写操作被 hook 拦下**（Claude Code 启用写前门禁时）：说明缺少当前对话的 `确认 Step N`，核对它列出的 Step 内容后回复确认再重试
- **脚本找不到**：命令里的 `skills/impact/scripts/...` 是相对本仓库的路径，装到别处时替换为实际安装路径
- **`python` 不可用**：确认 Python 3 在 PATH 里

绕过门禁（跳过校验、无视退出码、把 FAIL 说成通过）在这套工具里没有正当理由。如果你确认是校验器误报，把 FAIL 原文记录下来反馈。

## 5. 下一步

- 各 skill 完整说明：[pathfinder](skills/pathfinder/) · [impact](skills/impact/) · [intent 六件套](README.md#从零开始开发)
- 不同 AI 客户端的验证程度与边界：[环境兼容说明](docs/environment-compatibility.md)
- 场景速查表与完整路线：[README](README.md)
