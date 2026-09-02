# 言镜 · WordMirror 视觉设计系统（DESIGN.md v3.0）

> 本文档管"长什么样"。产品设计原则见根目录 DESIGN.md 与各 references/ 协议。
> v3.0 起，全站从"暖纸白 + 衬线 + 话印朱"改成"冷纸白 + 墨 + 单一青色"，方向是克制与编辑感。
> 给任何 AI agent 的用法：做言镜相关页面时先读本文档，token 照抄，不要发明新颜色。

---
version: 3.0
name: wordmirror-design
description: 言镜单一视觉体系。冷纸白 + 墨 + 单一青色强调，衬线编辑排版；全页只允许一处光谱渐变作为"折射"签名。
---

## 1. 视觉主题与气质

一面镜子照人，本质是光的反射。全站把"镜"落成一个动作：**光只折一次**——
除标题下那条光谱线外，全页不再出现任何渐变、霓虹、玻璃。其余都是 墨 + 纸 + 一个青色。

气质：冷静、编辑感、可信。像一个"个人年度报告"，而不是营销海报。

**零外联铁律**：所有产物是 file:// 双击可开的单文件。禁止 webfont CDN、禁止任何外部请求。字体靠系统字体栈优雅降级。

## 2. 颜色与角色

```yaml
colors:
  paper:         "#F7F8F7"   # 页面底：冷白，刻意不用暖奶油
  surface:       "#FFFFFF"   # 卡片、面板
  soft:          "#EEF1EF"   # 软底、药丸、进度底
  line:          "#E2E6E3"   # 1px 边线
  ink:           "#16181A"   # 标题、正文强
  body:          "#4A4E4B"   # 正文
  muted:         "#878C88"   # 次要、眉标
  accent:        "#0F766E"   # 青：镜面的冷光，全站唯一强调色
  accent-deep:   "#0B5F58"   # hover
  accent-soft:   "#E6F0EE"   # 青色淡底
```

### 光谱（签名，只此一处）

```yaml
spectrum: "linear-gradient(90deg, #F97316, #EC4899, #8B5CF6, #3B82F6)"
```

- 只允许出现在**页面大标题下的一条 180px × 3px 细线**（class `.refract`），代表"光折了一下"。
- 其余任何地方（卡片、数字、边框、按钮）**禁止使用光谱渐变**。

### 状态色（说 vs 做 / 照见状态）

```yaml
semantic:
  stalled:  "#C03E3A"   # 说了没下文：深红，不闪不加粗
  cooling:  "#BF8228"   # 放凉：琥珀
  waiting:  "#10B981"   # 在等外部（可选，少用）
  done:     "#0F766E"   # 办完：青（= accent，沉淀）
```

## 3. 字体

零 webfont，系统字体栈。

```yaml
type:
  display:  "'Songti SC','Noto Serif SC','Source Han Serif SC',SimSun,Georgia,serif"
            # 衬线：大标题、照见事实、引文、大数字。字重 600-700
  body:     "-apple-system,'SF Pro Display','PingFang SC','HarmonyOS Sans SC','MiSans','Segoe UI','Microsoft YaHei',sans-serif"
            # 正文与 UI
  mono:     "'JetBrains Mono','SF Mono',Consolas,'Cascadia Code',ui-monospace,monospace"
            # 日期、编号、眉标、计数
```

**字号层级：** display 44-84px（衬线 700）→ 区块标题 28px（衬线 700）→ 正文 16px →
辅助 14px → 眉标 12px（mono，字距 +3px）。大数字 34-56px 衬线 700，配一句人话注解，不许裸数字。

## 4. 核心组件

### 折射线 `.refract`（签名组件）

大标题下方一条 180px 宽、3px 高、圆角的光谱细线。全站唯一。读页 hero 出现一次。

### 照见卡 `.insight-card`

白底 + 1px 边线 + 4px 圆角。内容：mono 青色类型标签 + 衬线照见事实 +
青色左边线引文块（mono 日期 + 衬线原文）。

### 数字带 `.stats`

编辑式横条：上下 1px 边线，格子之间竖线分隔（不是卡片）。数字用衬线墨色，注解弱色。

### 引文块 `.quote`

左侧 3px 青色竖线 + mono 全日期眉标 + 衬线引文。"引用必须带日期"在排版层的执行。

### 说 vs 做条 `.gap-bar`

一条 8px 高圆角条，三段（办完青 / 放凉琥珀 / 没下文红），下方图例。落差一眼可见。

### 导航卡 `.nav-card`

白底 + 1px 边线 + 4px 圆角，mono 编号 + 衬线标题 + 一句说明。hover：边线变青、上浮 2px。

## 5. 布局

- 内容最大宽 1040px，居中，左右 40px 留白
- 区块间距 72px；间距基元 4px
- 大留白、克制；移动端卡片改单列

## 6. 规矩与禁区（Do & Don't）

**必须：** 引文必带全日期；状态只用语义色四档；每页落款"言镜 · 数据只存在你自己的电脑上"；
每页有顶部铭牌；行高 ≥1.6。

**文案说人话：** 用户看得见的每个字用大白话（「你说的话」「重复的只算一次」「照见」），
不出现「语料/画像/蒸馏/去重/语义索引/向量/脱敏」这类内部词。

**禁止：** 霓虹色、大投影、发光、玻璃拟态、极光底、整页渐变（渐变只允许 `.refract` 一处）；
卡片圆角 > 4px；纯黑 #000；日期省略成 "06-06"。

## 7. 给 agent 的快速提示词

> 做言镜产物页面：读本文件。冷纸白 #F7F8F7 底 + 墨 #16181A 正文 + 单一青色 #0F766E 强调；
> 衬线做标题/引文/大数字，mono 做日期/眉标。全页只在标题下放一条 180px 光谱细线（.refract），
> 其余地方禁用渐变、玻璃、霓虹。状态色 stalled深红/cooling琥珀/done青。零外部请求，系统字体栈。
> 落款"言镜 · 数据只存在你自己的电脑上"。文案说人话。改样式先改本文档再动模板。

## 8. 现状

- 六页产物（index/01 我是谁/03 说过要做的事/05 照见/10 时间弧线/月报）由 scripts/render.py 渲染
- 照见页读 data/profile/insights.jsonl；说过要做的事读两层 promises.jsonl
- 改样式先改本文档再动模板，然后重跑 render.py
