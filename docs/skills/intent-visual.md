# IntentVisual（视觉规范生成）

> 为"没有设计素材 + 有用户界面"的项目生成视觉规范 `visual-design.md` 和验收基线 `visual-baseline.html`，登记进 `INTENT.md` 第 12 节，激活链路既有的视觉验收门禁。

运行：`/intent-visual`（手动触发）｜技能本体：[skills/intent-visual/](../../skills/intent-visual/)

## 它做什么

- 生成两份产物：视觉规范文档 + 一个可以直接打开的基线 HTML 页面。
- 基线登记进 INTENT.md 第 12 节后，下游门禁自动激活：intent-issues 要求工单验收标准对照设计文件、intent-dev 要求 UI 证据、intent-verify 要求真实截图与基线比对。
- 风格来源三选一：常备参考池（vercel / notion / stripe / apple 四个拉开距离的方向）、常备方向样张、用户实测提取。
- 参考文件是第三方对公开网站的分析，不是官方设计系统：产物区分实测值与推断值，专有字体换系统字体栈，不使用品牌 Logo 与商标。

## 什么时候用

- 项目没有设计稿，但用户对界面风格有要求，且希望在验收时"风格"是可以判定的。
- 已有设计素材时不需要：素材直接由 intent-anchor 登记为 UI 验收基线。
- 前置条件：INTENT.md、PRD、architecture.md、design.md 四者齐且通过校验。

## 常见问题

**"要某某风格"怎么变成可验收的？**
风格被拆成可判定的条目（配色、间距、字体栈、布局模式）写进规范，基线页面作为对照物；验收时拿真实截图和基线比。

**会泄露或侵权吗？**
参考文件只进上下文按 pin commit 取用；产物不使用专有字体和品牌标识。

**轻量档会省掉基线页吗？**
不会。`visual-baseline.html` 是验收对照物，任何档位都必须产出。

## 用对了是什么样子

- `INTENT.md` 第 12 节新增了素材记录行，重跑 `intent_validate.py` 通过。
- 基线页能在浏览器打开，风格条目和规范文档一一对应。
- 到 intent-verify 阶段，截图能和基线页逐条比对出"像不像"。
