---
name: ruleblade
description: 安装或升级律刃行为规则。按用户需要的检查细度选择完整版或精简版，保留项目里已有的其他规则。
disable-model-invocation: true
allowed-tools: Read, Write, Edit
---

# 律刃 RuleBlade

律刃 v5.0 有两种写法，不按模型名称自动分档：

| 文件 | 什么时候选 | 内容 |
|---|---|---|
| [CLAUDE.full.md](CLAUDE.full.md) 完整版 | 需要明确检查动作、自查上限，或没有偏好 | 9 条规则加中文表达要求 |
| [CLAUDE.lite.md](CLAUDE.lite.md) 精简版 | 团队已有执行习惯，只想保留原则和停手条件 | 6 段原则加中文表达要求 |

规则正文只在这两个文件里，本文件只负责安装，不复述规则内容。v4.0 已退役，存档在 `archive/CLAUDE.v4.0.md`，不要再安装它。

> **文件位置**：`CLAUDE.full.md`、`CLAUDE.lite.md` 在本技能目录 `${CLAUDE_SKILL_DIR}` 下，不在当前项目里。这个路径没被替换成实际目录时（别的客户端），用本 SKILL.md 所在目录的绝对路径。

## 安装步骤

1. **确定用哪一份。** 用户指定哪份就用哪份；否则按上表推荐，没有偏好时推荐完整版，在写入确认时一并说明。
2. **确定写到哪个文件。**
   - Claude Code → 项目根目录的 `CLAUDE.md`
   - Codex、DeepSeek Harness（dsh）→ 项目根目录的 `AGENTS.md`
   - 用户想对所有项目生效时，也可以写全局文件：Claude Code 是 `~/.claude/CLAUDE.md`，dsh 是 `~/.dsh/AGENTS.md`，Codex 是 `~/.codex/AGENTS.md`。
3. **读取选中的规则文件，征得用户同意后写入。**
4. **目标文件已经存在时，不要直接覆盖。**
   - 里面已经有旧版律刃（标题含"律刃 RuleBlade"，或者开头是"# CLAUDE.md"加"行为准则，减少常见的 LLM 编码错误"）：告诉用户现在是哪个版本，问要不要把旧版那一段换成新版，文件里的其他内容保留。
   - 里面没有律刃：把新版作为一节追加到末尾，或者请用户自己合并。冲突的地方由用户决定。
5. **写完告诉用户**：装的是哪一份、写在哪个文件里。仅更换模型不需要重装。

## 两份的依据

两份都在 DeepSeek V4.1 Flash 上测过：同批场景都是 39/39，v4.0 为 29/39，不放规则为 30/39。精简版在这批任务多用约 29% 的输出 token。没有 Opus 5.5、GPT-6 Astra 的对照结果，不据此推荐型号。详见 [TASK_V5_VERIFY.md](TASK_V5_VERIFY.md)。

## 与其他技能的关系

- 律刃约束通用的编码行为；IntentAnchor、Pathfinder、ImpactRadar 等技能负责各自的需求澄清、项目摸底或影响分析流程。两者可以配合，也可以单独使用。
- 规则偏向"不动无关的东西"，不是"多检查几遍"。完整版按影响面分档：生成型任务自查最多 2 轮，高风险变更才要求先查清影响范围、出覆盖表。
