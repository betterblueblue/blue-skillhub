---
name: blue-xhs-knowledge-design
description: Design spec for the blue-xhs-knowledge skill - a Xiaohongshu knowledge carousel card generator inspired by blue-word-poster
type: project
---

# blue-xhs-knowledge Skill Design

## Overview

A Claude Code skill that generates Xiaohongshu (小红书/RED) carousel knowledge cards from a single Chinese word/concept. The skill visualizes philosophical/psychological concepts as multi-card carousel posts, with each card carrying a narrative role and a visual style independently assigned by Claude.

Inspired by blue-word-poster's 4 visual style philosophies, redesigned for Xiaohongshu's knowledge card format and audience.

**Why**: blue-word-poster generates single poster images for Douyin; this new skill adapts the concept visualization approach for Xiaohongshu's carousel format, which requires multi-card storytelling with information hierarchy.

**How to apply**: When building this skill, follow the dual-layer design principle — narrative roles and visual styles are independent decisions. Do not hardcode card count or style-to-role mappings.

## Skill Metadata

- **name**: `blue-xhs-knowledge`
- **version**: 1.0.0
- **user_invocable**: true
- **trigger phrases**: '知识卡片', '小红书', 'xhs', '图文知识', '概念可视化', 'knowledge card'

## Workflow (6 Steps)

1. **Archive check** — Read `output/concept-archive.md`. Reject any concept that has been previously published. Same deduplication logic as blue-word-poster.

2. **Concept interpretation & narrative planning** — Claude analyzes the input concept's emotional quality and complexity, then decides:
   - Card count (3-6, flexible based on concept complexity)
   - Narrative role for each card (cover/definition/scenario/depth/conclusion etc.)
   - Visual style for each card (ethereal/grounded/semantic/emphasis)
   - Narrative roles and visual styles are **not** fixed-binded — Claude matches them based on concept temperament
   - Simple concepts → 3 cards (cover + definition + conclusion)
   - Complex concepts → 5-6 cards (cover + definition + scenario + depth + conclusion, or double-depth)

3. **Generate prompt files** — Read the 4 template files from `references/`, fill `{{...}}` placeholders, write to `output/batch-{NNN}/`. Filename format: `prompt-{style}-{concept}-{sequence}.txt`

4. **Call script to generate images** — Run `python scripts/xhs-knowledge-generate.py output/batch-{NNN}/`

5. **Append to archive** — Write concept + style assignments + card count + batch number + date to `output/concept-archive.md`

6. **Generate Xiaohongshu copy** — Write `xhs-copy.md` with title, body text, hashtags, and cover recommendation

## Red Line Rules

- Template body text is immutable — only `{{...}}` placeholders are filled
- Concepts cannot repeat (archive check)
- Within one carousel group, visual styles should not repeat (if card count > 4, reuse is allowed but adjacent cards must avoid same style)
- Copy must not use AI tone words (赋能, 无缝, 释放, 震撼心灵, etc.)
- Copy must not use "golden-quote" style endings ("人生就是...", "所以记住...")
- Copy must not reference images ("这张图告诉我们...") — speak the knowledge directly
- Tone: like a friend sharing a discovery, not a teacher lecturing

## 4 Visual Styles (Redesigned)

All styles are based on blue-word-poster's design philosophies but redesigned for Xiaohongshu knowledge card format. Key shift: from "pure word visualization" (poster-style, word is the entire subject) to "knowledge card visualization" (card-style, needs to carry information hierarchy: title > subtitle > annotation).

### Ethereal (空灵)

**Source**: float (no ground / no base surface)

**Concept**: Large whitespace, elements float freely or embed into characters, poetic composition. No ground/platform surface.

**Best for**: Cover cards (suspense hook) and conclusion cards (imagery closure).

**Difference from original**: Original is pure word visualization; new version must support **information hierarchy** — allows subtitles, brief annotations as lightweight text auxiliary.

### Grounded (实证)

**Source**: stage (with ground / base surface / platform)

**Concept**: Stable base surface, elements land and root, information has a "landing surface". Explicit ground/stage/platform surface.

**Best for**: Definition cards (concept grounded explanation) and scenario cards (life examples).

**Difference from original**: New version emphasizes **information landing feel** — definitions/data/facts should visually have a "bearing surface", not float in air.

### Semantic (语义)

**Source**: deep (deep semantic analysis, multi-layer)

**Concept**: Multi-layered overlay, rich metaphor, semantic chain visualization. Most systematic semantic analysis mechanism.

**Best for**: Depth cards (multi-dimensional expansion of concept, causal chains, layered progression).

**Difference from original**: New version adds **structured semantic chain** — not just free metaphor overlay, allows ordered logical progression (起→承→转→合).

### Emphasis (强调)

**Source**: deep-bold (deep semantic + bold formatting on key statements)

**Concept**: Core arguments bolded/highlighted/enlarged, strong visual impact, key points instantly distinguishable.

**Best for**: Core argument cards and conclusion cards (golden closure).

**Difference from original**: New version strengthens **information hierarchy contrast** — not just bold typography, needs visual "title-level > subtitle-level > annotation-level" clear hierarchy.

## Prompt Template Design

Each template retains the original's visual philosophy core but is rewritten for knowledge card format. Changes:

1. **Narrative role declaration**: Template opening declares what role this card plays (cover/definition/scenario/depth/conclusion), telling GPT-image-2 the card's position in the carousel narrative.

2. **Information hierarchy requirement**: "画面构成" section adds knowledge card info-layer requirements — title vs subtitle vs annotation must have distinct visual weight.

3. **Carousel continuity hint**: Mentions "第X张 / 共Y张" to imply visual continuity across carousel group.

4. **Typography rules**: "排版规则" section adds title/subtitle/annotation visual weight distinction.

### Placeholder List

| Placeholder | Source | Purpose |
|---|---|---|
| `{{卡片叙事角色}}` | New | cover/definition/scenario/depth/conclusion |
| `{{卡片序号}}` | New | Position in carousel (1, 2, 3...) |
| `{{总卡片数}}` | New | Total cards in this carousel group |
| `{{核心文字}}` | Original | The concept word/phrase |
| `{{文字语言}}` | Original | Language of the text |
| `{{副标题或注释}}` | New | Supplementary information layer |
| `{{可选补充语境}}` | Original | Optional context |
| `{{可选情绪倾向}}` | Original | Optional emotional direction |
| `{{可选文化方向}}` | Original (deep/deep-bold) | Optional cultural direction |
| `{{可选禁用元素}}` | Original | Optional forbidden elements |
| `{{是否允许辅助文字}}` | Original | Whether auxiliary text is allowed |
| `{{辅助文字关系说明}}` | Original | Auxiliary text relationship description |

### Ethereal Template Placeholder

Uses `{{核心文字}}` (not `{{输入文字}}`), matching float template convention.

### Grounded Template Placeholder

Uses `{{核心文字}}` (not `{{输入文字}}`), matching stage template convention.

### Semantic & Emphasis Templates Placeholder

Use `{{核心文字}}` as main input (unified from original's `{{输入文字}}` for consistency). Retain `{{可选文化方向}}`.

## Xiaohongshu Copy Generation

**Output**: `output/batch-{NNN}/xhs-copy.md`

**Structure**:
```
## 📌 标题
(15 chars max, clickworthy but not clickbait)

## 正文
(2-4 paragraphs, 1-3 sentences each. Narrative aligns with carousel card logic:
cover hook → body expansion → conclusion echo. Max 300 chars)

## 标签
#concept-name #related-field #xhs-popular-tags (3-5 hashtags)

## 🖼 尒颂推荐封面
(Recommend which card to use as Xiaohongshu cover image)
```

**Red lines**:
- No AI tone (赋能, 无缝, 释放, 震撼心灵, 让我们一起, 助力)
- No golden-quote endings ("人生就是...", "所以记住...")
- No image references ("这张图告诉我们...") — speak knowledge directly
- Tone: friend sharing a discovery, not teacher lecturing
- Xiaohongshu-specific: shorter title (15 chars), # hashtags, "左滑看更多" carousel prompt

**Difference from blue-word-poster Douyin copy**: Douyin copy is video-script style; Xiaohongshu copy is image-text post reading style. Xiaohongshu title is shorter, hashtags use # format, body text must have clear correspondence with carousel images.

## Python Script

**File**: `scripts/xhs-knowledge-generate.py`

**Architecture**: Independent new script, reusing core API call logic from `word-poster-generate.py` (env loading, provider abstraction, submit+poll / sync patterns).

**Key differences from original script**:

| Aspect | Original | New |
|---|---|---|
| Filename parsing | `prompt-float-{word}.txt`, `prompt-deep-bold-{word}.txt` | `prompt-{style}-{concept}-{sequence}.txt` |
| Style mapping | float→悬浮, stage→舞台, deep→深度, deep-bold→深度强调 | ethereal→空灵, grounded→实证, semantic→语义, emphasis→强调 |
| Output naming | `{ChineseStyle}_{word}.png` | `{ChineseStyle}_{concept}_{sequence}.png` |
| Batch semantics | 4 images per batch (1 per style) | N images per batch (carousel group, variable count) |

**CLI usage**: `python scripts/xhs-knowledge-generate.py <output-dir> [-p provider]`

**Env file**: Shares the same `.env` file at project root (`D:\PyProject\blue-skillhub\.env`) with blue-word-poster.

## Output Directory Structure

```
output/batch-001/
  prompt-ethereal-锚定-01.txt
  prompt-grounded-锚定-02.txt
  prompt-semantic-锚定-03.txt
  prompt-emphasis-锚定-04.txt
  空灵_锚定_01.png
  实证_锚定_02.png
  语义_锚定_03.png
  强调_锚定_04.png
  xhs-copy.md
```

## Concept Archive

**File**: `output/concept-archive.md`

**Format**:
```
| 批次 | 概念 | 卡片数 | 风格分配 | 日期 |
| 001  | 锚定 | 4      | 空灵/实证/语义/强调 | 2026-04-29 |
```

## Skill File Structure

```
blue-xhs-knowledge/
  SKILL.md                     — Skill manifest and workflow definition
  README.md                     — Human-facing documentation
  references/
    prompt-ethereal.md          — Ethereal style prompt template
    prompt-grounded.md          — Grounded style prompt template
    prompt-semantic.md          — Semantic style prompt template
    prompt-emphasis.md          — Emphasis style prompt template
  scripts/
    xhs-knowledge-generate.py   — Image generation Python script
  output/
    concept-archive.md          — Concept deduplication archive
```

## Relationship to blue-word-poster

- **Shared**: Project root `.env`, image generation providers (GRS/Yunwu), GPT-image-2 model, concept visualization philosophy
- **Independent**: Prompt templates, Python script, archive file, output directory, Xiaohongshu copy format
- **Design principle**: blue-word-poster is for Douyin single-poster format; blue-xhs-knowledge is for Xiaohongshu carousel knowledge card format. Both use the same underlying visual philosophies but apply them differently based on platform needs.