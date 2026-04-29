---
name: blue-word-poster
description: "词语视觉化海报生成器。传入4个词语，每个智能分配到一种风格（悬浮/舞台/深度/深度强调），9:16比例，词语存档防重复，同时输出抖音推广文案。Use when user says '海报', 'poster', '视觉化', '词语海报', '生成海报', 'word poster'."
user_invocable: true
version: "2.0.0"
---

# 词语海报

把词语的精神状态视觉化，不是插图化。

## 这不是什么

- 不是字效海报——把字放大贴上去不是设计
- 不是普通插画——画面必须和字咬合，不是字 + 图的拼凑
- 不是模板堆砌——每个词都有专属的视觉逻辑
- 不是文案配图——文字本身就是画面的骨架

## 四种 Prompt 模板

| 模板 | 特点 | 适用场景 |
|------|------|----------|
| **悬浮版** (`prompt-float.md`) | 无承载面，元素自由漂浮/嵌入，构图轻盈 | 诗意、抽象、自由类词语 |
| **舞台版** (`prompt-stage.md`) | 有承载面（地面/舞台/平台），画面稳定戏剧 | 命运、冲突、人物关系类词语 |
| **深度版** (`prompt-deep.md`) | 语义分析更系统，新增文化方向字段 | 需要深度理解的复杂词语 |
| **深度强调版** (`prompt-deep-bold.md`) | 同深度版，正文带 **加粗** 格式 | 同上，偏好视觉强调 |

## 执行流程

### Step 1：存档检查

1. Read `output/word-archive.md`
2. 检查用户输入的4个词是否都在存档范围以外
3. 如有重复词 → 提醒用户："词语 '{重复词}' 已在存档中（batch-{NNN}），请替换为新词"
4. 全部新词 → 继续

如果 word-archive.md 不存在，说明是首次使用，自动创建。

### Step 2：智能分配风格

Claude 根据每个词语的情绪气质，分配最适合的风格：
- 诗意、抽象、轻盈类 → 悬浮版
- 命运、冲突、人物关系、戏剧类 → 舞台版
- 需深度语义分析、文化典故类 → 深度版
- 同上但偏好视觉强调 → 深度强调版

铁律：每种风格每批次只用1次，4个词各不相同。

### Step 3：生成 4 个 prompt 文件

1. 确定批次号：扫描 output/batch-* 目录，取最大号 +1（首次为 batch-001）
2. 创建批次目录：`mkdir -p output/batch-{NNN}/`
3. Read 对应的 prompt 模板文件
4. 每个词只生成1个 prompt 文件：

| 词语 | 分配风格 | 模板文件 | 输出文件名 |
|------|----------|----------|-----------|
| {词语1} | 悬浮 | prompt-float.md | prompt-float-{词语1}.txt |
| {词语2} | 舞台 | prompt-stage.md | prompt-stage-{词语2}.txt |
| {词语3} | 深度 | prompt-deep.md | prompt-deep-{词语3}.txt |
| {词语4} | 深度强调 | prompt-deep-bold.md | prompt-deep-bold-{词语4}.txt |

拼接规则：将模板中的 {{...}} 占位符替换为实际值。prompt 正文（占位符以上的部分）一字不改。

### Step 4：调脚本生图

```bash
python scripts/word-poster-generate.py output/batch-{NNN}/            # 默认 GRS
python scripts/word-poster-generate.py output/batch-{NNN}/ -p yunwu    # 用 Yunwu
```

脚本会读取 4 个 prompt 文件，逐一生成 9:16 图片并下载。

等待脚本完成后，确认 4 张 PNG 文件已生成。

### Step 5：追加存档

将本次4个词写入 `output/word-archive.md`，追加到表格末尾：

```
| {词语1} | 悬浮 | batch-{NNN} | {日期} |
| {词语2} | 舞台 | batch-{NNN} | {日期} |
| {词语3} | 深度 | batch-{NNN} | {日期} |
| {词语4} | 深度强调 | batch-{NNN} | {日期} |
```

日期获取：`date +%Y-%m-%d`

如果是首次（word-archive.md 不存在），先创建文件头和表头。

### Step 6：生成抖音推广文案

根据4个词语的含义和海报视觉概念，生成统一抖音推广文案，保存到 `output/batch-{NNN}/douyin-copy.md`。

文案结构：

```markdown
# 词语海报 — batch-{NNN}

## 词语一览
- {词语1}（悬浮版）
- {词语2}（舞台版）
- {词语3}（深度版）
- {词语4}（深度强调版）

## 标题
（15字以内，有钩子感）

## 正文
（2-3句，口语化，串联4个词的核心感受）

## 标签
#话题1 #话题2 #话题3 #话题4 #话题5

## 配图指引
推荐封面图：{从4张中选1，说明理由}
```

文案写作红线：
- 禁止 AI 腔（赋能/无缝/释放/震撼心灵）
- 禁止金句感（不要像朋友圈鸡汤）
- 口语检验：你会这样跟朋友说吗？不会 → 改

## 输入格式

```
/词语海报 孤独 自由 沉默 矛盾
```

必须输入4个词语。少于4个时提醒用户补足。

或自然语言触发："帮我做四个词语的海报"、"生成孤独自由沉默矛盾的海报"

## 输出清单

output/batch-{NNN}/ 目录下：
- `prompt-float-{词语1}.txt` — 悬浮版 prompt
- `prompt-stage-{词语2}.txt` — 舞台版 prompt
- `prompt-deep-{词语3}.txt` — 深度版 prompt
- `prompt-deep-bold-{词语4}.txt` — 深度强调版 prompt
- `悬浮_{词语1}.png` — 悬浮版海报
- `舞台_{词语2}.png` — 舞台版海报
- `深度_{词语3}.png` — 深度版海报
- `深度强调_{词语4}.png` — 深度强调版海报
- `douyin-copy.md` — 抖音推广文案

output/word-archive.md — 词语存档（追加4行）

## 文件引用

- `references/prompt-float.md` — 悬浮版 prompt 模板
- `references/prompt-stage.md` — 舞台版 prompt 模板
- `references/prompt-deep.md` — 深度版 prompt 模板
- `references/prompt-deep-bold.md` — 深度强调版 prompt 模板
- `scripts/word-poster-generate.py` — 生图脚本
- `output/word-archive.md` — 词语存档

## 红线

1. prompt 正文不可修改——拼接时只填入 {{...}} 占位符
2. 9:16 比例固定
3. 必须输入 4 个词语
4. 词语不可与存档重复
5. 每种风格每批次只用 1 次
6. 文案 md 格式（不是 org）
7. 文案禁止 AI 腔、禁止金句感