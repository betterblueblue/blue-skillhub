---
name: blue-xhs-knowledge
description: "小红书知识卡片生成器。传入1个概念词语，智能规划叙事结构（封面/定义/场景/深度/结论等），每张卡片独立分配视觉风格（空灵/实证/语义/强调），生成3-6张轮播卡片图，概念存档防重复，同时输出小红书发布文案。Use when user says '知识卡片', '小红书', 'xhs', '图文知识', '概念可视化', 'knowledge card'."
user_invocable: true
version: "1.0.0"
---

# 知识卡片

把概念的精神状态视觉化，不是插图化。

## 这不是什么

- 不是字效卡片——把概念放大贴上去不是设计
- 不是普通知识插画——画面必须和概念咬合，不是概念 + 图的拼凑
- 不是模板堆砌——每个概念都有专属的叙事逻辑和视觉逻辑
- 不是文案配图——文字本身就是画面的骨架

## 四种 Prompt 模板

| 模板 | 特点 | 适用场景 |
|------|------|----------|
| **空灵版** (`prompt-ethereal.md`) | 无承载面，元素自由漂浮，大留白，诗意构图 | 封面（悬念引子）、结论（意象收束） |
| **实证版** (`prompt-grounded.md`) | 有承载面（地面/舞台/平台），信息落地，画面稳定 | 定义页（概念落地）、场景页（生活实例） |
| **语义版** (`prompt-semantic.md`) | 多层次叠加，语义链可视化，结构化递进 | 深度解读页（概念多维展开） |
| **强调版** (`prompt-emphasis.md`) | 同语义版，关键论点加粗/高亮，信息层级对比强烈 | 核心论点页、结论页 |

## 执行流程

### Step 1：存档检查

1. Read `output/concept-archive.md`
2. 检查用户输入的概念是否在存档范围以内
3. 如有重复概念 → 提醒用户："概念 '{重复概念}' 已在存档中（batch-{NNN}），请替换为新概念"
4. 新概念 → 继续

如果 concept-archive.md 不存在，说明是首次使用，自动创建。

### Step 2：概念解读与叙事规划

Claude 分析概念，决定轮播组的叙事结构和视觉分配：

- **卡片数量**：3-6张，根据概念复杂度灵活决定
- **叙事角色**：每张卡片的叙事功能（封面/定义/场景/深度/结论等）
- **视觉风格**：每张卡片的视觉模板（空灵/实证/语义/强调）
- **叙事角色和视觉风格是独立的**——Claude 根据概念的气质将二者匹配

典型规划：

| 概念复杂度 | 卡片数 | 叙事结构 | 风格分配示例 |
|------------|--------|----------|-------------|
| 简单概念 | 3张 | 封面 + 定义 + 结论 | 空灵 / 实证 / 空灵 |
| 中等概念 | 4张 | 封面 + 定义 + 场景 + 结论 | 空灵 / 实证 / 实证 / 强调 |
| 复杂概念 | 5-6张 | 封面 + 定义 + 场景 + 深度 + 结论 | 空灵 / 实证 / 实证 / 语义 / 强调 |

铁律：同一轮播组内，视觉风格尽量不重复（卡片数 > 4 时允许复用，但相邻卡片避免同风格）。

### Step 3：生成 prompt 文件

1. 确定批次号：扫描 output/batch-* 目录，取最大号 +1（首次为 batch-001）
2. 创建批次目录：`mkdir -p output/batch-{NNN}/`
3. Read 对应的 prompt 模板文件
4. 每张卡片生成1个 prompt 文件，文件名格式：`prompt-{style}-{concept}-{sequence}.txt`

示例（5张卡片，概念"锚定效应"）：

| 序号 | 叙事角色 | 视觉风格 | 模板文件 | 输出文件名 |
|------|----------|----------|----------|-----------|
| 1 | 封面 | 空灵 | prompt-ethereal.md | prompt-ethereal-锚定效应-01.txt |
| 2 | 定义 | 实证 | prompt-grounded.md | prompt-grounded-锚定效应-02.txt |
| 3 | 场景 | 实证 | prompt-grounded.md | prompt-grounded-锚定效应-03.txt |
| 4 | 深度 | 语义 | prompt-semantic.md | prompt-semantic-锚定效应-04.txt |
| 5 | 结论 | 强调 | prompt-emphasis.md | prompt-emphasis-锚定效应-05.txt |

拼接规则：将模板中的 {{...}} 占位符替换为实际值。prompt 正文（占位符以上的部分）一字不改。

### Step 4：调脚本生图

```bash
python scripts/xhs-knowledge-generate.py output/batch-{NNN}/            # 默认 GRS
python scripts/xhs-knowledge-generate.py output/batch-{NNN}/ -p yunwu    # 用 Yunwu
```

脚本会读取所有 prompt 文件，逐一生成图片并下载。

等待脚本完成后，确认所有 PNG 文件已生成。

### Step 5：追加存档

将本次概念写入 `output/concept-archive.md`，追加到表格末尾：

```
| {批次} | {概念} | {卡片数} | {风格分配如: 空灵/实证/语义/强调} | {日期} |
```

示例：`| batch-001 | 锚定效应 | 5 | 空灵/实证/实证/语义/强调 | 2026-04-29 |`

日期获取：`date +%Y-%m-%d`

如果是首次（concept-archive.md 不存在），先创建文件头和表头。

### Step 6：生成小红书文案

根据概念含义和卡片叙事逻辑，生成小红书发布文案，保存到 `output/batch-{NNN}/xhs-copy.md`。

文案结构：

```markdown
## 📌 标题
(15字以内，吸引点击但不标题党)

## 正文
(2-4段，1-3句/段，叙事跟轮播组逻辑一致，不超过300字)

## 标签
#概念名 #相关领域 #热门标签 (3-5个)

## 🖼 尒颂推荐封面
(建议哪张卡片作为封面图)
```

文案红线：
- 禁止 AI 腔（赋能/无缝/释放/震撼心灵/让我们一起/助力）
- 禁止金句感（"人生就是..."）
- 禁止引用图片（"这张图告诉我们"）
- 口语检验：你会这样跟朋友说吗？不会 → 改

## 输入格式

```
/知识卡片 锚定
```

必须输入1个概念词语。

或自然语言触发："帮我做一个锚定效应的知识卡片"、"生成锚定的图文帖子"

## 输出清单

output/batch-{NNN}/ 目录下：
- `prompt-ethereal-{概念}-{序号}.txt` — 空灵版 prompt (如有)
- `prompt-grounded-{概念}-{序号}.txt` — 实证版 prompt (如有)
- `prompt-semantic-{概念}-{序号}.txt` — 语义版 prompt (如有)
- `prompt-emphasis-{概念}-{序号}.txt` — 强调版 prompt (如有)
- `空灵_{概念}_{序号}.png` — 空灵版卡片 (如有)
- `实证_{概念}_{序号}.png` — 实证版卡片 (如有)
- `语义_{概念}_{序号}.png` — 语义版卡片 (如有)
- `强调_{概念}_{序号}.png` — 强调版卡片 (如有)
- `xhs-copy.md` — 小红书发布文案

output/concept-archive.md — 概念存档（追加1行）

## 文件引用

- `references/prompt-ethereal.md` — 空灵版 prompt 模板
- `references/prompt-grounded.md` — 实证版 prompt 模板
- `references/prompt-semantic.md` — 语义版 prompt 模板
- `references/prompt-emphasis.md` — 强调版 prompt 模板
- `scripts/xhs-knowledge-generate.py` — 生图脚本
- `output/concept-archive.md` — 概念存档

## 红线

1. prompt 正文不可修改——拼接时只填入 {{...}} 占位符
2. 图片比例固定（按 .env 配置）
3. 必须输入 1 个概念词语
4. 概念不可与存档重复
5. 同一轮播组内，视觉风格尽量不重复（卡片数 > 4 时允许复用，但相邻卡片避免同风格）
6. 文案 md 格式（不是 org）
7. 文案禁止 AI 腔、禁止金句感、禁止引用图片