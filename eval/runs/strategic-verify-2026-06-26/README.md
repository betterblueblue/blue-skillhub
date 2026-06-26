# 战略定位验证实验 — 2026-06-26

> 目标：回答两个问题
> 1. **P0**：Composer 2.5 + CLAUDE.md + skill 的分析质量是否接近 Opus + CLAUDE.md（仅行为准则）？
> 2. **P1**：v4.1 协议是否修复了弱模型（Step 3.7 Flash）在 V6/V7 中暴露的问题？

---

## 一、实验设计

### 1.1 三个 Cell

| Cell | 模型 | 条件 | Prompt 文件 |
|------|------|------|------------|
| P0-A | Composer 2.5 | CLAUDE.md + /impact skill（v4.1 合并版） | PROMPT-P0A-composer-skill.md |
| P0-B | Opus 4.x | CLAUDE.md 仅行为准则（不加载任何 skill） | PROMPT-P0B-opus-noskill.md |
| P1 | Step 3.7 Flash | CLAUDE.md + /impact skill（v4.1 合并版） | PROMPT-P1-step-skill.md |

三个 cell 可以并行执行（分析阶段不修改源代码，各自写入独立输出目录）。

### 1.2 测试 Case（复用 V7 模糊 prompt）

| Case | 项目 | 技术栈 | 预期档位 | 模糊 prompt |
|------|------|--------|---------|------------|
| B1' | test-projects/ruoyi-vue | Java/Spring | full | "我们系统一个账号能同时在好几个地方登录，这不太安全，能不能加个限制，就让它只能在一个地方登录" |
| B2' | test-projects/prisma-express-ts | Node/Express | light | "API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧" |
| B3' | test-projects/prisma-express-ts | Node/Express | full | "注册的时候不是有发验证邮件吗，但是不验证好像也能用，这样不行吧" |

选择 V7 case 的原因：
- V7 已有全部 3 个模型 × 2 条件的 baseline 数据，可直接对比
- 模糊 prompt 是 skill 增益最大的场景（V7 增益 +12.1 vs V6 增益 +2）
- 覆盖 Java 和 Node 两个技术栈、full 和 light 两种档位

### 1.3 关键约定

- **只做分析**：所有 cell 只做影响分析 + 文档输出，不进入 Phase 5 执行（不修改源代码）
- **自问自答模式**：skill 组不等待人工回答，自行做合理假设并标注 `[假设]`
- **盲测评审**：GLM-5.2 评审时不知道产出来自哪个 cell、哪个模型
- **三个 cell 使用同一份测试项目源码**（只读），各自写入独立输出目录

### 1.4 输出路径

| Cell | 输出路径 |
|------|---------|
| P0-A | `test-projects/<project>/change-impact/p0a-composer-skill/<case-id>/` |
| P0-B | `test-projects/<project>/change-impact/p0b-opus-noskill/<case-id>/` |
| P1 | `test-projects/<project>/change-impact/p1-step-skill/<case-id>/` |

---

## 二、执行方式

### 2.1 启动三个 Cell（并行）

1. **P0-A**：在 Claude Code 中打开 `e:\agent\blue-skillhub`，选择 Composer 2.5，复制 `PROMPT-P0A-composer-skill.md` 中 `---` 之后的内容发送
2. **P0-B**：在 Claude Code 中打开 `e:\agent\blue-skillhub`，选择 Opus，复制 `PROMPT-P0B-opus-noskill.md` 中 `---` 之后的内容发送
3. **P1**：在 Claude Code 中打开 `e:\agent\blue-skillhub`，选择 Step 3.7 Flash，复制 `PROMPT-P1-step-skill.md` 中 `---` 之后的内容发送

三个 cell 在不同会话中并行运行，互不干扰。

### 2.2 评审（三个 cell 全部完成后）

将 `JUDGE-PROMPT.md` 的内容发给 GLM-5.2，逐 case 评审 9 份产出（3 cell × 3 case）。

---

## 三、判定标准

### 3.1 P0：战略定位是否达成

```
判定条件：|P0-A 均分 - P0-B 均分| ≤ 5 分
```

| 结果 | 含义 |
|------|------|
| Δ ≤ 5 | ✅ 战略定位达成——Composer + skill 达到了 Opus + CLAUDE.md 的水平 |
| 5 < Δ ≤ 10 | ⚠️ 接近但有差距——需分析差距在哪些维度 |
| Δ > 10 | ❌ 未达成——skill 的外置补偿不足以弥补模型能力差 |

### 3.2 P1：v4.1 是否修复弱模型问题

| 对比 | V7 C6 baseline（v3.8） | 判定 |
|------|:---:|------|
| P1 均分 | 59.7 | P1 > 65 → v4.1 有效 |
| B2' 判档 | Full ❌（应为 Light） | P1 B2' 判 Light → 修复 |
| B3' passport.ts | ❌ 遗漏 | P1 B3' 包含 → 修复 |
| B2'/B3' 过早收敛 | 各只 1 Step | P1 Step 数 > 2 → 修复 |

### 3.3 V7 baseline 数据（用于对比）

| Cell | 模型 | 条件 | B1' | B2' | B3' | 均分 |
|------|------|------|:---:|:---:|:---:|:---:|
| V7-C3 | Composer 2.5 | noskill | 70 | 72 | 71 | 71.0 |
| V7-C4 | Composer 2.5 | skill v3.8 | 84 | 83 | 84 | 83.7 |
| V7-C5 | Step 3.7 Flash | noskill | 49 | 53 | 44 | 48.7 |
| V7-C6 | Step 3.7 Flash | skill v3.8 | 75 | 57 | 47 | 59.7 |

---

## 四、产物归档

```
eval/runs/strategic-verify-2026-06-26/
├── README.md                          # 本文件
├── PROMPT-P0A-composer-skill.md       # Cell A prompt
├── PROMPT-P0B-opus-noskill.md         # Cell B prompt
├── PROMPT-P1-step-skill.md            # P1 prompt
├── JUDGE-PROMPT.md                    # 评审 prompt
├── scorecards/                        # GLM-5.2 评分卡
│   ├── P0A-B1.scorecard.json
│   ├── P0A-B2.scorecard.json
│   ├── ...
│   └── _summary.md                    # 评审总结
└── conclusion.md                      # 最终结论（评审后填写）
```
