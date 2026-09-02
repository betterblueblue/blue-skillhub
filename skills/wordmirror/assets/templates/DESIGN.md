# 言镜 · WordMirror 视觉设计系统（DESIGN.md v5.0 · Duna 式）

> 本文档管"长什么样"。产品设计原则见根目录 DESIGN.md 与各 references/ 协议。
> v3.0 建立冷纸白编辑感；v4.0 解决层次感（四档色阶、章节编号、表面投影）；
> v5.0 整体换血为 **Duna 式暖白风格**（参照 duna.com 实测提取，官方 DESIGN.md 为付费内容未采用）：
> 暖白画布 + 暖墨文字 + 茄紫点睛 + 柠檬信号色 + 晨景 hero + 大圆角柔影卡片。
> 给任何 AI agent 的用法：做言镜相关页面时先读本文档，token 照抄，不要发明新颜色。

---
version: 5.0
name: wordmirror-design
description: 言镜单一视觉体系（Duna 式）。暖白画布 + 暖墨 + 茄紫强调 + 柠檬信号；开场是纯 CSS 晨景渐变 hero，正文是暖白阅读带；大圆角 + 柔影；全页只允许一条光谱细线作为"折射"签名。
---

## 1. 视觉主题与气质

参照对象 Duna（duna.com，业务 onboarding 平台）的气质：**开朗、暖、可信的现代 SaaS 编辑感**——
巨大紧凑的墨色标题、暖白画布、大量留白、大圆角卡片，开场用一个暖色"天空"而不是黑幕。
言镜保留自己的签名：标题下一条光谱细线（光只折一次），hero 里的晨光是这条线的放大版舞台。

气质：暖、明亮、“个人年度报告”，不是营销海报也不是终端。

**零外联铁律**：所有产物是 file:// 双击可开的单文件。禁止 webfont CDN、禁止任何外部请求。
唯一允许的位图是 hero 晨景画：由生图脚本（gpt-image-2）预先生成，
存为 `assets/templates/hero-dawn.jpg`（≈150KB JPEG），render.py 渲染时以 base64 内嵌进每页
（模板占位符 `__HERO_IMG__`）。画不存在时模板自动落回纯 CSS 晨光渐变，产物始终零外联。
换画只换这张 jpg 后重跑 render.py。

## 2. 颜色与角色

```yaml
colors:
  paper:         "#FDFCFA"   # 页面底：暖白（微暖，不冷不奶油过头）
  surface:       "#FFFFFF"   # 卡片、面板（纯白浮在暖白上）
  soft:          "#F3F1EB"   # 软底、色带、进度底（骨白）
  line:          "#E7E3D9"   # 1px 边线（暖灰）
  ink:           "#221C15"   # 标题、引文、大数字（暖近黑）
  body:          "#4C463D"   # 正文（暖深灰）
  muted:         "#8B8579"   # 次要、眉标
  muted-soft:    "#B5AFA2"   # 最弱注解、置底内容
  accent:        "#42217A"   # 茄紫：全站唯一强调色（Duna 标题的深茄紫 #1B0624 提亮到可读档）
  accent-deep:   "#2C1157"   # hover、强调标题
  accent-soft:   "#F2EBFA"   # 茄紫淡底（"当下"章节渐变的起点色）
  lime:          "#AEEC1D"   # 柠檬信号色（Duna 的 pop）：只准做 logo 圆点等微元素，禁止做文字色
```

### 光谱（签名，只此一处）

```yaml
spectrum: "linear-gradient(90deg, #F59E0B, #EC4899, #8B5CF6, #3B82F6)"
```

- 只允许出现在**页面大标题下的一条 180px × 3px 细线**（class `.refract`）。
- hero 里的 `.refract` 允许带暖色柔光 box-shadow（晨光感），其余任何地方禁止渐变。

### 晨景 hero（签名开场，只此一处渐变区）

hero 是"暖色油画天空"：三层 CSS 渐变叠加（右上日光 radial + 左下霞光 radial +
自上而下 peach → 骨白 → 暖白的线性淡出），底部用 `clip-path` 多边形压一层
低透明度"远山"剪影。墨色大标题压在淡出的晨光上。除 hero 外全页禁用大面积渐变。

### 状态色（说 vs 做 / 提醒状态）

```yaml
semantic:
  stalled:  "#C4473F"   # 说了没下文：深红
  cooling:  "#C08519"   # 放凉：暖琥珀
  waiting:  "#3E9B63"   # 在等外部（少用）
  done:     "#7CA30D"   # 办完：橄榄绿（柠檬色的可读档）
```

## 3. 字体

v5 起 display 从衬线改为**无衬线大标题**（Duna 是 grotesque，衬线是旧刊物路线的遗产）。

```yaml
type:
  display:  "'Segoe UI','SF Pro Display','PingFang SC','HarmonyOS Sans SC','MiSans','Microsoft YaHei',sans-serif"
            # 标题、引文、大数字。字重 700，字距收紧（-0.3 ~ -0.5px）
  body:     "-apple-system,'SF Pro Display','PingFang SC','HarmonyOS Sans SC','MiSans','Segoe UI','Microsoft YaHei',sans-serif"
  mono:     "'JetBrains Mono','SF Mono',Consolas,'Cascadia Code',ui-monospace,monospace"
```

**坑（保留 v4 教训）：** 中文没有可靠的系统衬线粗体（SimSun 是伪粗），
若某天要引文换衬线，兑底必须 Georgia + 雅黑，禁 SimSun 排在雅黑前。

**文字四档色阶（不变，层次感的根）：**

1. **墨色 ink**：标题、引文、大数字、strong
2. **导语档**：紧跟章节标题的第一段（CSS `h2 + p` 自动命中），17.5px
3. **正文档 body**：16px
4. **辅助档 muted + mono**：日期、眉标、注解小字

**字号层级：** hero display clamp(44px, 7vw, 88px)（700，行高 1.08，字距 -0.5px）→
章节标题 30px（700，上方 mono 茄紫编号）→ 导语 17.5px → 正文 16px → 辅助 14px →
眉标 12px mono 字距 +3px。大数字 34-56px 700，必配一句人话注解。

## 4. 核心组件

### 晨景 hero（见上）+ 铭牌

hero 内：顶栏（柠檬圆点 logo-dot + 言镜 wordmark + mono 副标）→ 眉标 → 巨大墨色标题 → 光谱线。

### 章节标题 h2（编号锚点）

CSS counter 自动编号：h2 上方一行 mono 茄紫编号（01、02…）。扫读先见编号再见标题。

### 表面层次

paper 暖白底 → soft 骨白色带（无影）→ surface 纯白卡：1px 暖灰边线 + 14px 圆角 +
柔影 `0 1px 2px rgba(34,28,21,.04), 0 10px 28px rgba(34,28,21,.06)`（token `--shadow-card`）。
hover 上浮 2px + 茄紫边线。**禁止大投影、禁止发光**（hero 光晕除外）。

### 茄紫出场纪律

茄紫只用于：章节编号、引文日期眉标、类型标签、引文左边线、链接、hover、承诺卡顶边、
"当下"章节的强调（accent-soft 渐变淡底）。不用于正文长句。柠檬绿只做 logo 圆点等微元素。

### 提醒卡 `.insight-card`

白底 + 1px 边线 + 14px 圆角。mono 茄紫类型标签 + 无衬线提醒事实 +
左边线引文块；主引文块用 accent-soft 茄紫淡底 10px 圆角。

### 数字带 `.stats`

编辑式横条：上下 1px 边线、竖线分格（不是卡片）。数字墨色无衬线，注解弱色。

### 引文块 `.quote`

左侧 3px 茄紫竖线 + mono 全日期眉标 + 无衬线引文墨色。"引用必须带日期"的排版执行。

### 说 vs 做条 `.gap-bar`

8px 高圆角条三段（done 橄榄 / cooling 琥珀 / stalled 红），下方图例。

### 导航卡 `.nav-card`

白底 + 边线 + 14px 圆角，mono 编号 + 无衬线标题 + 一句说明。hover：茄紫边线 + 上浮 + 柔影加深。

## 5. 布局

- 内容最大宽 1040px，居中，左右 40px 留白
- 区块间距 72px；间距基元 4px
- 大留白、开朗；移动端卡片改单列

## 6. 规矩与禁区（Do & Don't）

**必须：** 引文必带全日期；状态只用语义色四档；每页落款"言镜 · 数据只存在你自己的电脑上"；
每页有顶部铭牌；行高 ≥1.6；文案说人话（禁内部术语上页面）。

**禁止：** hero 以外的大面积渐变；发光、玻璃拟态、极光底、黑幕开场（v4 教训：太黑）；
纯黑 #000 文字；柠檬绿做文字色或大面积填充；日期省略成 “06-06”；
webfont / 运行时外部请求（晨景画只准 base64 内嵌，不准 `<img src="http…">`）。

## 7. 给 agent 的快速提示词

> 做言镜产物页面：读本文件。暖白 #FDFCFA 底 + 暖墨 #221C15 + 茄紫 #42217A 强调 + 柠檬 #AEEC1D 微信号；
> 开场是纯 CSS 晨景 hero（暖色天空 + 远山剪影 + 墨色大标题 + 一条光谱细线），正文落回暖白阅读带；
> 白卡 14px 圆角 + 柔影，hover 茄紫描边。文字四档色阶，章节标题带 mono 茄紫编号。
> 零外部请求，系统字体栈（display 无衬线，禁 SimSun）。状态色 stalled红/cooling琥珀/done橄榄。
> 落款"言镜 · 数据只存在你自己的电脑上"。改样式先改本文档再动模板。

## 8. 现状

- 九页产物（index/01 我是谁/02 我做过的重要决定/03 说过要做的事/04 该注意的事/05 我反复提的事/06 我在各 AI 里的样子/07 我总让 AI 干什么/08 AI 怎么看我/09 走过的这几个月/月报）由 scripts/render.py 渲染
- 提醒页读 data/profile/insights.jsonl；说过要做的事读两层 promises.jsonl
- 改样式先改本文档再动模板，然后重跑 render.py
- 2026-09-02：v5.0 Duna 式改版（用户指定参照 https://getdesign.md/design-md/duna，
  官方文档付费，风格从 duna.com 实测提取：暖白/暖墨/茄紫/柠檬/晨景/胶囊/大圆角）
- 2026-09-02：hero 升级为真实水粉画（用户拍板“要嵌图片”）：gpt-image-2 生成
  桃色晚霞 + 淡紫远山 + 湖面留白 + 草甸小花，压 149KB JPEG 内嵌，管线见第 1 节
