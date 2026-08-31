# Intent-Visual

> 把"要好看/要某某风格"变成一份可验收的视觉规范，让视觉要求进入链路门禁，而不是停留在对话里。

这是 intent-chain 链路的可选环节，位置在 intent-design 与 intent-issues 之间：

```text
intent-anchor → intent-prd → intent-design → intent-visual（仅 UI 项目）→ intent-issues → intent-dev → intent-adversarial → intent-verify
```

## 为什么需要它

链路原本有一条完整的视觉验收通道：INTENT.md 第 12 节的设计素材表（V10）→ 工单"对照设计文件"检查（V6）→ intent-verify 的截图门禁（V3）。但它有一个前提——项目里得先有设计素材（原型、设计稿、可点 HTML）。用户手里什么素材都没有、只说"要某某风格"时，第 12 节只能写"没有设计素材"，整条通道全部不适用，界面长相就退回模型临场发挥。

Intent-Visual 补的就是这个缺口：参考 [awesome-design-md](https://github.com/VoltAgent/awesome-design-md)（MIT）的方式把风格蒸馏成"只写具体值"的规范文件，生成配套的可视基线页，再登记进第 12 节——下游门禁原样点亮，一行校验器代码都不用改。

产物不叫 `DESIGN.md` 而叫 `visual-design.md`：Windows 文件名不区分大小写，链路目录里已有 intent-design 产出的 `design.md`，避免撞名。

## 快速开始

```text
/intent-visual
界面还没定风格，帮我先定一份视觉规范，后面照着做。
```

流程：分支判定 → 选风格来源（推荐实例网站 / 方向样张 / 你自己指名 / 我来定）→ 蒸馏成 `visual-design.md` → 生成 `visual-baseline.html` 样式画廊 → 你确认后写入并登记进 INTENT 第 12 节。

写入前运行 `visual_validate.py` 的 10 项结构检查（只写具体值、负面清单非空、来源可追溯、基线页存在等，见脚本头部注释）。

## 什么时候使用 / 不使用

使用（全部满足）：

- intent-design 已完成，四件前置文档通过各自校验器；
- 项目有用户界面；
- INTENT 第 12 节没有设计素材行。

不使用：

- 项目没有用户界面（纯 CLI / 本地工具）——直接进 intent-issues；
- 项目已有设计稿、原型或现成 DESIGN.md——把它登记进第 12 节即可，不需要本 skill；
- 用户不需要界面规范——明确拒绝即可，不产出文件。

## 参考文件

`references/` vendored 了 4 份常备参考（vercel / notion / stripe / apple，按风格方向选取），其余 70 个品牌按 pin commit 运行时按份取用，规则见 [references/README.md](references/README.md)。参考文件是第三方对公开网站的分析，不是官方设计系统；产出定位是"风格参考"，不是"品牌还原"。

## 下游怎么用

登记后无需任何配置：

- intent-issues：涉及界面的工单验收标准自动要求"对照 visual-design.md 结构一致"；
- intent-dev：对照 `visual-baseline.html` 实现；
- intent-verify：路径证据须附真实截图/Playwright 产物，与基线页并排比对。
