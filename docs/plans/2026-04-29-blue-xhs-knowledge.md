# blue-xhs-knowledge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the blue-xhs-knowledge skill — a Xiaohongshu carousel knowledge card generator that takes a single Chinese concept word and produces multi-card carousel images + Xiaohongshu copy.

**Architecture:** Dual-layer design — narrative roles (cover/definition/scenario/depth/conclusion) and visual styles (ethereal/grounded/semantic/emphasis) are independent decisions by Claude. 4 prompt templates inspired by blue-word-poster's philosophies but redesigned for knowledge card format with information hierarchy. Python script reuses core API logic from word-poster-generate.py but adapted for carousel batch semantics.

**Tech Stack:** Claude Code skill (SKILL.md), Python 3 (requests, pathlib), GPT-image-2 via GRS/Yunwu providers

---

### Task 1: Create directory structure

**Files:**
- Create: `blue-xhs-knowledge/` (directory)
- Create: `blue-xhs-knowledge/references/` (directory)
- Create: `blue-xhs-knowledge/scripts/` (directory)
- Create: `blue-xhs-knowledge/output/` (directory)

**Step 1: Create directories**

```bash
mkdir -p "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references"
mkdir -p "D:/PyProject/blue-skillhub/blue-xhs-knowledge/scripts"
mkdir -p "D:/PyProject/blue-skillhub/blue-xhs-knowledge/output"
```

**Step 2: Verify structure**

```bash
ls -R "D:/PyProject/blue-skillhub/blue-xhs-knowledge/"
```

Expected: directories for references, scripts, output exist

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/
git commit -m "feat: scaffold blue-xhs-knowledge skill directory structure"
```

---

### Task 2: Create concept archive

**Files:**
- Create: `blue-xhs-knowledge/output/concept-archive.md`

**Step 1: Write initial archive file**

Create `D:\PyProject\blue-skillhub\blue-xhs-knowledge\output\concept-archive.md`:

```markdown
# 概念存档

| 批次 | 概念 | 卡片数 | 风格分配 | 日期 |
|------|------|--------|----------|------|
```

**Step 2: Verify file exists and has correct header**

```bash
cat "D:/PyProject/blue-skillhub/blue-xhs-knowledge/output/concept-archive.md"
```

Expected: file with header row and column names matching spec

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/output/concept-archive.md
git commit -m "feat: add initial concept archive for xhs-knowledge"
```

---

### Task 3: Write Ethereal (空灵) prompt template

**Files:**
- Create: `blue-xhs-knowledge/references/prompt-ethereal.md`

**Step 1: Write the prompt-ethereal.md template**

This template is based on `blue-word-poster/references/prompt-float.md` but redesigned for Xiaohongshu knowledge card format. Key changes from original float template:

1. Opening declares narrative role (`{{卡片叙事角色}}`) and carousel position (`{{卡片序号}}/{{总卡片数}}`)
2. "画面构成" section adds knowledge card information hierarchy — title vs subtitle vs annotation must have distinct visual weight
3. Typography rules add title/subtitle/annotation visual weight distinction
4. New placeholder `{{副标题或注释}}` for supplementary info layer
5. Retains the core philosophy: no ground/platform surface, elements float freely, poetic composition, large whitespace

The template body must follow the same structure as the originals (philosophy → composition → execution → user input). Template body text is immutable — only `{{...}}` placeholders are filled.

Write the full content to `D:\PyProject\blue-skillhub\blue-xhs-knowledge\references\prompt-ethereal.md`. The content should be:

```markdown
你要生成的不是普通知识卡片插画，也不是把一个词语放大后贴在画面上的字效卡片，而是一张"基于概念含义自动构建视觉隐喻"的高级知识卡片——它是小红书图文轮播组中的一张。

这张卡片必须让人一眼就感受到这个概念"为什么是这样被表达的"，而不是只看到漂亮画面却无法理解含义。画面要做到"文字本身就是主题，图像是对文字的深化表达，二者共同组成一个完整的视觉句子"。

当前卡片身份：这是轮播组中的第 {{卡片序号}} 张（共 {{总卡片数}} 张），叙事角色为 {{卡片叙事角色}}（如封面/定义/场景/深度/结论）。

一、先理解概念，再生成画面
在动手生成之前，先智能分析用户输入内容，包括但不限于：
1. 这个概念最核心的字面含义是什么。
2. 这个概念在情绪上偏向温柔、冷峻、危险、孤独、浪漫、压迫、希望、纯真、欲望、秩序、冲突、疏离、自由、沉默、毁灭、重生等哪种倾向。
3. 这个概念是否具有双关、反差、张力、隐喻、悖论、社会性、哲学性或情感深度。
4. 这个概念最适合被转译成哪一种视觉逻辑：人物关系、物体关系、动作关系、空间关系、对比关系、象征关系、冲突关系、秩序关系、荒诞关系、诗意关系等。
5. 如果这个概念较抽象，不要直接做空洞抽象图案，而要找到能够承载其含义的具体视觉载体。
6. 如果这个概念较具体，也不要只做字面插图，而要通过构图、尺度、关系、反差与氛围，让它变得更有思想和记忆点。

二、空灵风格核心规则
这是空灵版（Ethereal）知识卡片模板，源自悬浮风格的设计哲学，核心特征：

1. **无地面、无基座、无承载面**——画面中不应出现明确的横向承载结构（如地面、舞台、台基、地平线、平台）。所有元素自由漂浮、悬浮或嵌入文字本体。
2. **构图轻盈、留白充裕**——画面呼吸感强，信息密度低，不是塞满的版面。留白是设计的一部分，不是空。
3. **诗意感优先**——元素不是"站上去的"，而是"浮在那里的"、"飘进来的"、"渗透出来的"。画面应有轻盈、飘渺、空气感。
4. **文字与元素的漂浮关系**——元素可以浮在文字旁边、嵌入文字内部、从文字缝隙中生长出来、围绕文字漂浮。但不应有"落地"感。

三、知识卡片信息层次
作为知识卡片（而非纯词语海报），这张图需要承载信息层次：

1. **第一层：核心文字**——用户输入的概念词必须是画面主视觉，大而醒目，占据画面重要区域。这是最强势的视觉层级。
2. **第二层：副标题或注释**——如果有副标题/注释内容，它以轻量方式存在：可以沿着文字边缘排布、像低声补充的注解、像一条气息停留在局部。它不是独立的信息栏，而是融入意境的补充。
3. **第三层：视觉隐喻**——漂浮的图像元素与文字咬合，共同组成概念的视觉表达。
4. **第四层：极少量辅助信息**——如编号、署名等，仅在非常相关时增强艺术感。

信息层次之间的视觉权重必须有明确区分：
- 核心文字：最大、最醒目、最强势
- 副标题/注释：明显小于核心文字，视觉权重约为核心文字的1/3
- 视觉隐喻元素：与核心文字形成咬合关系，但不抢夺视觉主导
- 辅助信息：极小、克制、仅做点缀

四、画面构图逻辑
整体画面必须极简、明确、有概念感，构图要干净而有力量。

1. 大字作为画面的核心骨架。用户输入的概念文字应成为画面中的主视觉文字主体，通常以大尺寸出现，占据画面重要区域，具有强识别性与视觉压迫感。
2. 图像元素不是随意摆放，而是要与文字产生关系。它们可以漂浮在字旁、嵌入字中、与字形成互动、从字缝隙中生长、在视觉上与字构成对照。
3. 整体元素数量要克制。通常控制在少量关键主体之内。宁可少而准，也不要多而散。
4. 画面要有明确主次关系：文字是第一视觉层，图像叙事是第二视觉层，副标题是第三视觉层。
5. 留白要聪明，不是空，而是让画面更有呼吸感、更有判断力、更有设计感。
6. 构图应尽量轻盈、飘渺、好读，并具备"知识卡片感"——不是海报截图，而是适合在小红书轮播中被逐张阅读的信息载体。

五、轮播连贯性
这张卡片是轮播组中的一张（第 {{卡片序号}} 张 / 共 {{总卡片数}} 张）。

1. 如果这是封面卡（第1张），应制造悬念引子，让人想左滑看下一张。不要在封面把概念完全说透。
2. 如果这是结论卡（最后一张），应形成意象收束，与封面形成呼应闭环。
3. 如果是中间的解读卡，应承接前卡、铺垫后卡，形成阅读流动感。
4. 同组轮播的卡片之间应有视觉气质的连续性——配色倾向、排版逻辑、文字风格应有一致的底层系统，但每张卡的视觉焦点可以不同。

六、视觉风格要求
整体风格为高级图形艺术知识卡片，具有拼贴感、丝网印刷感、石版印刷感或版画式质感。

风格要求：
1. 具有强烈平面设计感。
2. 画面应有干净统一的色彩逻辑，颜色数量不宜过多。
3. 可使用高饱和主背景色配合大面积浅色文字，形成强对比。
4. 质感可带有细微颗粒、纸张纹理、印刷噪点、轻微做旧感，但整体仍需清爽、利落、高级。
5. 人物或物体细节要清楚，但整体仍然服从平面卡片的统一调性。
6. 不要做成廉价模板，不要出现低级拼贴感，不要做成广告页，不要做成普通电商排版。

七、文字排版逻辑
1. 核心文字必须作为画面主标题，大且醒目。字形清晰、完整、可识别。
2. 副标题或注释如果有内容，必须以明显小于核心文字的方式呈现，视觉权重约为核心文字的1/3。它不是第二个标题，而是补充信息。
3. 可以在画面克制位置加入少量辅助短句或编号，但必须非常简洁且自然。
4. 所有文字都要像从画面中漂浮出来一样，不能像后期随便贴上去。

八、成图目标
最终生成的知识卡片必须满足以下结果：
1. 一眼看上去极简、轻盈、空灵、完整、有高级感。
2. 能让人快速感受到这个概念的情绪和内涵。
3. 图与字之间存在强关联，形成聪明、准确、耐看的视觉表达。
4. 既有平面设计的理性控制，也有艺术表达的情绪力度。
5. 作为轮播组中的一张，与前后卡片形成阅读节奏。
6. 信息层次清晰：核心文字一眼可见，副标题自然读取，视觉隐喻引发联想。
7. 不能只是"把概念画出来"，而是要"把概念的精神状态视觉化"，并且用空灵、漂浮、轻盈的方式。

九、执行原则
1. 不要机械重复固定模板，要根据概念智能变化。
2. 整体保持极简、概念化、强排版、强识别度的统一品质。
3. 构图要轻盈，画面要克制，表达要巧妙。
4. 不要过度解释，不要加入多余元素，不要让画面显得拥挤。
5. 任何视觉元素都必须服务于概念表达，不能为了好看而偏离主题。

请基于以上原则，生成这张知识卡片。

用户输入内容：
核心文字 / 概念词：{{核心文字}}
文字语言：{{文字语言}}
副标题或注释：{{副标题或注释}}
卡片叙事角色：{{卡片叙事角色}}
卡片序号：{{卡片序号}}
总卡片数：{{总卡片数}}
可选补充语境：{{可选补充语境}}
可选情绪倾向：{{可选情绪倾向}}
可选禁用元素：{{可选禁用元素}}
是否允许辅助文字：{{是否允许辅助文字}}
辅助文字如允许，必须与主题的关系说明：{{辅助文字关系说明}}
```

**Step 2: Verify file content**

```bash
wc -l "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-ethereal.md"
```

Expected: ~130+ lines, all placeholders present

**Step 3: Verify placeholders**

```bash
grep -c '{{' "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-ethereal.md"
```

Expected: 11 placeholder occurrences ({{核心文字}}, {{文字语言}}, {{副标题或注释}}, {{卡片叙事角色}}, {{卡片序号}}, {{总卡片数}}, {{可选补充语境}}, {{可选情绪倾向}}, {{可选禁用元素}}, {{是否允许辅助文字}}, {{辅助文字关系说明}})

**Step 4: Commit**

```bash
git add blue-xhs-knowledge/references/prompt-ethereal.md
git commit -m "feat: add ethereal (空灵) prompt template for xhs-knowledge"
```

---

### Task 4: Write Grounded (实证) prompt template

**Files:**
- Create: `blue-xhs-knowledge/references/prompt-grounded.md`

**Step 1: Write the prompt-grounded.md template**

Based on `blue-word-poster/references/prompt-stage.md` but redesigned for knowledge card format. Key changes from original stage template:

1. Opening declares narrative role and carousel position
2. Adds information hierarchy section (title > subtitle > annotation visual weight)
3. Emphasizes "information landing feel" — definitions/data/facts should visually have a "bearing surface"
4. Adds carousel continuity section
5. Retains core philosophy: must have ground/base/platform surface, elements land and root, theatrical/stable composition

The grounded template is the longest and most detailed of the simpler templates (like stage was longer than float), because it needs to specify how knowledge information (definitions, facts, data) should be presented with "landing feel" — they should rest on surfaces, not float.

Write the full content to `D:\PyProject\blue-skillhub\blue-xhs-knowledge\references\prompt-grounded.md`. Content should follow the same section structure as prompt-ethereal.md but with grounded-specific rules:

- Section 二 "实证风格核心规则" replaces 空灵 rules with:
  - Must have ground/base/platform surface
  - Elements must land, root, stand on the surface
  - Information has a "landing surface" — facts, definitions visually rest on bearing surfaces
  - Theatrical, stable, grounded composition

- Section 三 "知识卡片信息层次" same structure but emphasis on:
  - Core text can rest ON the ground surface or stand as a wall/structure above it
  - Subtitle/annotation rests on bearing surfaces (a shelf, a label strip, a ground-level annotation band)
  - Visual metaphors involve grounded relationships (standing, placing, stacking)

- Section 五 "轮播连贯性" same as ethereal

- All other sections adapted with grounded-style specifics

Placeholders same as ethereal template:
{{核心文字}}, {{文字语言}}, {{副标题或注释}}, {{卡片叙事角色}}, {{卡片序号}}, {{总卡片数}}, {{可选补充语境}}, {{可选情绪倾向}}, {{可选禁用元素}}, {{是否允许辅助文字}}, {{辅助文字关系说明}}

**Step 2: Verify file and placeholders**

```bash
wc -l "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-grounded.md"
grep -c '{{' "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-grounded.md"
```

Expected: ~150+ lines, 11 placeholder occurrences

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/references/prompt-grounded.md
git commit -m "feat: add grounded (实证) prompt template for xhs-knowledge"
```

---

### Task 5: Write Semantic (语义) prompt template

**Files:**
- Create: `blue-xhs-knowledge/references/prompt-semantic.md`

**Step 1: Write the prompt-semantic.md template**

Based on `blue-word-poster/references/prompt-deep.md` but redesigned for knowledge card format. This is the most detailed template (like deep was the most detailed original). Key changes from original deep template:

1. Opening declares narrative role and carousel position
2. Adds "structured semantic chain" — allows ordered logical progression (起→承→转→合), not just free metaphor overlay
3. Adds information hierarchy section with emphasis on multi-layer semantic rendering
4. Adds carousel continuity section
5. Retains core philosophy: multi-layered overlay, rich metaphor, semantic chain visualization, systematic semantic analysis
6. Includes {{可选文化方向}} placeholder (like the original deep template)

The semantic template should be the longest (~200+ lines) because it inherits deep's extensive semantic analysis mechanism and adds the knowledge card adaptations.

Placeholders (12 total, including {{可选文化方向}}):
{{核心文字}}, {{文字语言}}, {{副标题或注释}}, {{卡片叙事角色}}, {{卡片序号}}, {{总卡片数}}, {{可选补充语境}}, {{可选情绪倾向}}, {{可选文化方向}}, {{可选禁用元素}}, {{是否允许辅助文字}}, {{辅助文字关系说明}}

**Step 2: Verify file and placeholders**

```bash
wc -l "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-semantic.md"
grep -c '{{' "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-semantic.md"
```

Expected: ~200+ lines, 12 placeholder occurrences

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/references/prompt-semantic.md
git commit -m "feat: add semantic (语义) prompt template for xhs-knowledge"
```

---

### Task 6: Write Emphasis (强调) prompt template

**Files:**
- Create: `blue-xhs-knowledge/references/prompt-emphasis.md`

**Step 1: Write the prompt-emphasis.md template**

Based on `blue-word-poster/references/prompt-deep-bold.md` but redesigned for knowledge card format. Key differences from prompt-semantic.md:

1. Same content as semantic template but with **bold** Markdown formatting on key statements throughout (like deep-bold vs deep)
2. Strengthened information hierarchy contrast — not just bold typography, needs visual "title-level > subtitle-level > annotation-level" clear hierarchy
3. Core arguments are bolded/highlighted/enlarged, strong visual impact, key points instantly distinguishable
4. Includes {{可选文化方向}} placeholder (like semantic)

The emphasis template content should be identical to the semantic template's content, but with **bold** formatting applied to key statements. This is for cases where the image model may better parse emphasized formatting.

Placeholders (12 total, same as semantic):
{{核心文字}}, {{文字语言}}, {{副标题或注释}}, {{卡片叙事角色}}, {{卡片序号}}, {{总卡片数}}, {{可选补充语境}}, {{可选情绪倾向}}, {{可选文化方向}}, {{可选禁用元素}}, {{是否允许辅助文字}}, {{辅助文字关系说明}}

**Step 2: Verify file and placeholders**

```bash
wc -l "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-emphasis.md"
grep -c '{{' "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-emphasis.md"
grep -c '**' "D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-emphasis.md"
```

Expected: ~200+ lines, 12 placeholder occurrences, multiple bold formatting marks

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/references/prompt-emphasis.md
git commit -m "feat: add emphasis (强调) prompt template for xhs-knowledge"
```

---

### Task 7: Write Python image generation script

**Files:**
- Create: `blue-xhs-knowledge/scripts/xhs-knowledge-generate.py`

**Step 1: Write the script**

Based on `blue-word-poster/scripts/word-poster-generate.py` (~300 lines) but adapted for carousel batch semantics. Key changes:

| Aspect | Original | New |
|---|---|---|
| ENV_PATH | `D:\MyPythonProject\image\.env` | `D:\PyProject\blue-skillhub\.env` (project root) |
| Filename parsing | `prompt-float-{word}`, `prompt-deep-bold-{word}` | `prompt-{style}-{concept}-{sequence}` (e.g. `prompt-ethereal-锚定-01`) |
| STYLE_MAP | float→悬浮, stage→舞台, deep→深度, deep-bold→深度强调 | ethereal→空灵, grounded→实证, semantic→语义, emphasis→强调 |
| Output naming | `{ChineseStyle}_{word}.png` | `{ChineseStyle}_{concept}_{sequence}.png` |
| GRS_ASPECT_RATIO | `"9:16"` | `"3:4"` (from .env: GRS_ASPECT_RATIO=3:4) |
| YUNWU_SIZE | `"1024x1792"` | `"1024x1536"` (from .env: YUNWU_SIZE=1024x1536) |
| Interactive fallback | Scan word dirs | Scan batch dirs |
| batch semantics | 4 images per batch (1 per style) | N images per batch (carousel group, variable count) |

The script must:
1. Load `.env` from project root (`D:\PyProject\blue-skillhub\.env`)
2. Parse prompt filenames: `prompt-{style}-{concept}-{sequence}.txt` → extract style, concept, sequence
3. Map styles to Chinese prefixes using STYLE_MAP
4. Generate output filenames: `{ChineseStyle}_{concept}_{sequence}.png`
5. Support both GRS (async submit+poll) and Yunwu (sync) providers
6. Accept `<output-dir>` and optional `-p provider` CLI args
7. Handle variable number of prompt files per batch (not fixed to 4)

**Step 2: Verify script parses correctly**

```bash
python -c "import ast; ast.parse(open('D:/PyProject/blue-skillhub/blue-xhs-knowledge/scripts/xhs-knowledge-generate.py').read())"
```

Expected: no syntax errors

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/scripts/xhs-knowledge-generate.py
git commit -m "feat: add xhs-knowledge image generation script"
```

---

### Task 8: Write SKILL.md manifest

**Files:**
- Create: `blue-xhs-knowledge/SKILL.md`

**Step 1: Write SKILL.md**

The SKILL.md is the skill manifest and workflow definition. It must follow the exact same format as `blue-word-poster/SKILL.md`:

- YAML frontmatter with name, description, user_invocable, version
- Body with 6-step workflow (archive check → concept interpretation & narrative planning → generate prompt files → call script → append archive → generate Xiaohongshu copy)
- Red line rules
- Input format specification
- Output checklist
- File references

Key differences from blue-word-poster SKILL.md:

1. **Step 2** is "概念解读与叙事规划" not "智能分配风格" — Claude decides BOTH narrative role AND visual style per card, not just style per word
2. **Card count is flexible** (3-6) based on concept complexity, not fixed to 4
3. **Each card has both narrative role and visual style** — independent assignment
4. **Step 3 filename format**: `prompt-{style}-{concept}-{sequence}.txt` not `prompt-{style}-{word}.txt`
5. **Step 5 archive format**: concept + card count + style assignments + batch + date, not word + style + batch + date
6. **Step 6 is Xiaohongshu copy not Douyin copy**
7. **Input is single word**, not 4 words

**Step 2: Verify frontmatter**

```bash
head -10 "D:/PyProject/blue-skillhub/blue-xhs-knowledge/SKILL.md"
```

Expected: YAML frontmatter with name=blue-xhs-knowledge, version=1.0.0, user_invocable=true

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/SKILL.md
git commit -m "feat: add SKILL.md manifest for blue-xhs-knowledge"
```

---

### Task 9: Write README.md

**Files:**
- Create: `blue-xhs-knowledge/README.md`

**Step 1: Write README.md**

Human-facing documentation. Should include:
- Skill description (what it does)
- Version history (1.0.0 initial)
- 4 visual styles overview table
- Workflow summary
- Usage examples (trigger phrases)
- Output structure description
- Relationship to blue-word-poster

Follow the same documentation style as `blue-word-poster/README.md`.

**Step 2: Verify file**

```bash
wc -l "D:/PyProject/blue-skillhub/blue-xhs-knowledge/README.md"
```

Expected: ~40-60 lines

**Step 3: Commit**

```bash
git add blue-xhs-knowledge/README.md
git commit -m "feat: add README.md for blue-xhs-knowledge"
```

---

### Task 10: Add .gitignore

**Files:**
- Create: `.gitignore` (project root)

**Step 1: Write .gitignore**

The project has no .gitignore yet. Need to:
- Ignore `.env` (contains API keys)
- Ignore `.superpowers/` (brainstorming artifacts)
- Ignore generated output content in `*/output/batch-*/` (images, prompts) but keep archive files

```gitignore
# Secrets
.env

# Brainstorming artifacts
.superpowers/

# Generated images and prompts (keep archive files)
blue-word-poster/output/batch-*/*.png
blue-word-poster/output/batch-*/*.txt
blue-xhs-knowledge/output/batch-*/*.png
blue-xhs-knowledge/output/batch-*/*.txt
blue-xhs-knowledge/output/batch-*/*.md
```

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "feat: add .gitignore for secrets and generated artifacts"
```

---

### Task 11: Final verification

**Step 1: Verify complete skill structure**

```bash
ls -R "D:/PyProject/blue-skillhub/blue-xhs-knowledge/"
```

Expected:
```
blue-xhs-knowledge/
  SKILL.md
  README.md
  references/
    prompt-ethereal.md
    prompt-grounded.md
    prompt-semantic.md
    prompt-emphasis.md
  scripts/
    xhs-knowledge-generate.py
  output/
    concept-archive.md
```

**Step 2: Verify SKILL.md references match actual files**

Check that SKILL.md references `references/prompt-ethereal.md`, `references/prompt-grounded.md`, `references/prompt-semantic.md`, `references/prompt-emphasis.md`, `scripts/xhs-knowledge-generate.py`, `output/concept-archive.md` — and all these files exist.

**Step 3: Verify Python script can at least parse without errors**

```bash
python "D:/PyProject/blue-skillhub/blue-xhs-knowledge/scripts/xhs-knowledge-generate.py" --help
```

Expected: argparse help output showing `-p` provider option and `word_dir` argument

**Step 4: Verify all 4 templates have correct placeholder counts**

```bash
for f in ethereal grounded semantic emphasis; do
  echo "$f: $(grep -c '{{' D:/PyProject/blue-skillhub/blue-xhs-knowledge/references/prompt-${f}.md) placeholders"
done
```

Expected:
- ethereal: 11 placeholders
- grounded: 11 placeholders
- semantic: 12 placeholders (includes {{可选文化方向}})
- emphasis: 12 placeholders (includes {{可选文化方向}})