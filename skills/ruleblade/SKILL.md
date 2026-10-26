---
name: ruleblade
description: 把律刃行为规则装进当前项目：按用户主要使用的模型，把完整版（CLAUDE.full.md）或精简版（CLAUDE.lite.md）写入项目根的 CLAUDE.md（Codex、DeepSeek Harness 写入 AGENTS.md）。当用户要求安装或升级律刃、ruleblade、行为规范，或希望约束 AI 的编码行为时使用。
disable-model-invocation: true
allowed-tools: Read, Write, Edit
---

# 律刃 RuleBlade

律刃是一组写给 AI 编码助手的通用行为规则，当前版本 v5.0，按模型能力分成两份：

| 文件 | 给哪类模型 | 内容 |
|---|---|---|
| [CLAUDE.full.md](CLAUDE.full.md) 完整版 | DeepSeek V4.1 Flash、GLM、Kimi、MiMo、Haiku 等非旗舰模型；拿不准时也用这份 | 9 条规则加中文表达要求，检查动作和自查次数上限写得具体 |
| [CLAUDE.lite.md](CLAUDE.lite.md) 精简版 | Claude Opus 5.5、GPT-6 Astra 这一档旗舰模型 | 6 段原则，删掉了强模型默认会做的检查，写明哪些情况才停下来 |

规则正文只在这两个文件里，本文件只负责安装，不复述规则内容。v4.0 已退役，存档在 `archive/CLAUDE.v4.0.md`，不要再安装它。

## 安装步骤

1. **确定用哪一份。** 问用户在这个项目里主要用哪个模型；用户已经说过就不用再问。
   - Opus 5.5、GPT-6 Astra 或同一档的旗舰模型 → `CLAUDE.lite.md`
   - 其他模型、几个模型混用、或者用户说不清 → `CLAUDE.full.md`
2. **确定写到哪个文件。**
   - Claude Code → 项目根目录的 `CLAUDE.md`
   - Codex、DeepSeek Harness（dsh）→ 项目根目录的 `AGENTS.md`
   - 用户想对所有项目生效时，也可以写全局文件：Claude Code 是 `~/.claude/CLAUDE.md`，dsh 是 `~/.dsh/AGENTS.md`，Codex 是 `~/.codex/AGENTS.md`。
3. **读取选中的规则文件，征得用户同意后写入。**
4. **目标文件已经存在时，不要直接覆盖。**
   - 里面已经有旧版律刃（标题含"律刃 RuleBlade"，或者开头是"# CLAUDE.md"加"行为准则，减少常见的 LLM 编码错误"）：告诉用户现在是哪个版本，问要不要把旧版那一段换成新版，文件里的其他内容保留。
   - 里面没有律刃：把新版作为一节追加到末尾，或者请用户自己合并。冲突的地方由用户决定。
5. **写完告诉用户**：装的是哪一份、写在哪个文件里；以后主力模型换了档，要换成另一份。

## 两份的依据

两份都在 DeepSeek V4.1 Flash 上测过：12 个场景各跑 3 次，都是 39/39。v4.0 是 29/39，不放规则是 30/39。精简版在 DeepSeek 上的输出 token 比完整版多约 29%，主要多在生成型任务上反复检查，所以非旗舰模型用完整版。精简版还没在 Opus 5.5、GPT-6 Astra 上实测。详细记录见 [TASK_V5_VERIFY.md](TASK_V5_VERIFY.md)。

## 与其他技能的关系

- 律刃约束通用的编码行为；IntentAnchor、Pathfinder、ImpactRadar 等技能负责各自的需求澄清、项目摸底或影响分析流程。两者可以配合，也可以单独使用。
- 规则偏向"不动无关的东西"，不是"多检查几遍"。完整版按影响面分档：生成型任务自查最多 2 轮，高风险变更才要求先查清影响范围、出覆盖表。
