---
name: intent-visual
description: 读取 INTENT.md、PRD、architecture.md 和 design.md，为无设计素材但需要用户界面的项目生成视觉规范 visual-design.md 和验收基线 visual-baseline.html，并登记进 INTENT.md 第 12 节激活下游既有视觉门禁。支持参考池推荐、常备方向样张、实测提取三种风格来源。适用于 intent-design 完成后、intent-issues 之前；已有设计素材或无界面的项目不使用本 skill。
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, WebFetch
---

# Intent-Visual

## 目标

为"无设计素材 + 有用户界面"的项目生成视觉规范 `visual-design.md` 和验收基线 `visual-baseline.html`，登记进 `INTENT.md` 第 12 节后，激活链路既有的视觉验收通道——intent-issues 的 V6（工单验收标准须"对照"设计文件）、intent-dev 的 UI 证据要求、intent-verify 的 V3（路径证据须附真实截图/Playwright 产物，与基线页比对）。这些门禁是既有机制，本 skill 只负责补上"第 12 节没有素材行"这个缺口，不改动下游。

本 skill 只负责视觉规范的产生与登记：

- 不做需求澄清、不写 PRD、不做技术设计、不拆工单、不写业务代码。
- 对 `INTENT.md` 的唯一合法写入是第 12 节新增一行素材记录；写入后必须重跑 `intent_validate.py`。
- 校验器只查结构；"风格是否符合用户期望"由 Phase 2 的样张确认和 intent-verify 的截图比对保证。

## 前置条件

1. 必须存在通过 `intent_validate.py` 校验的 `INTENT.md`。
2. 必须存在通过 `prd_validate.py` 校验的 `PRD`。
3. 必须存在通过 `design_validate.py` 校验的 `architecture.md` 和 `design.md`。
4. 四者缺一不可。

## 轻量档

INTENT.md 第 2 节标注轻量档时：

- `visual-design.md` 各表允许只留一行，章节不可缺，`visual_validate.py` 照常运行。
- `visual-baseline.html` 仍须产出——它是验收对照物，不随档位省略。
- Phase 2 的来源选择与 Phase 5 的确认合并：草稿开头列出输入路径与所选来源，用户一次确认同时覆盖。
- 发现目标实际需要完整品牌体系（多端、暗色模式、组件库）时，触发升档单向规则：停下来告知用户升为标准档。只允许轻量升标准。

## 参考文件取用

- **常备参考**：`references/` 下 4 份（vercel / notion / stripe / apple），按"风格空间拉开距离的方向"选取，保持上游原样存储。来源、pin commit 与完整品牌索引见 `references/README.md`。
- **按需取用**：用户指名未 vendored 的品牌时，按 `references/README.md` 记录的 pin commit 拼 raw URL 只取那一份；取回的文件只进上下文，不落盘。**禁止使用浮动分支名取用**——上游结构会变，产物来源必须可复现。
- **如实定位**：参考文件是第三方对公开网站的分析，不是官方设计系统。提取结果是近似值，产物必须区分实测值与推断值；专有字体换系统字体栈，品牌 Logo 与商标不使用。

## 工作流程

### Phase 1：前置检查与分支判定

1. 确认 intent.md、prd.md、architecture.md、design.md 路径，读取全文。
2. 运行 `intent_validate.py`、`prd_validate.py`、`design_validate.py`，任一 FAIL 则停止。
3. 分支判定，**结果必须告知用户**，不静默跳过也不静默生成：
   - PRD 能力表没有用户可操作的界面（纯 CLI / 本地工具）→ 告知无需视觉规范，结束。
   - INTENT 第 12 节已有素材行 → 告知已有设计标准、下游门禁已激活，本 skill 不运行，直接交接 intent-issues。
   - 无素材但有界面 → 继续 Phase 2。
4. 从 intent.md 路径推导链路目录，产物写入同目录的 `visual-design.md` 和 `visual-baseline.html`。不创建目录、不写文件。
5. 如果 `visual-design.md` 已存在（跨会话恢复），读取现有内容，复述当前进度。

输出：分支判定结果和产物候选路径。

### Phase 2：确定风格来源（用户菜单）

入口只问一次"视觉参考从哪来"，选项按推荐顺序展示，四个选项映射 INTENT 的决策来源契约：

- **A 推荐实例网站（默认建议）**：按 INTENT 第 1 节的产品定位和受众，从 `references/README.md` 的品牌索引中挑 2-3 个风格拉开距离的候选，每个附一句"为什么适合你项目"的说明。用户确认一个后：已 vendored 的读本地文件，未 vendored 的按 pin commit 远程取用。决策来源记"用户明确确认"。
- **B 常备方向样张**：从 4 份常备参考各抽核心值，渲染一张极小样张（标题 + 正文 + 按钮 + 卡片，一页并排或多个小文件），用 Playwright 截图给用户看；环境没有浏览器时把样张 HTML 交给用户自己打开。用户看图选。决策来源记"用户明确确认"。
- **C 用户自报指名**：用户说"像某某站 / 某某产品"。池内品牌按 pin commit 取用；池外网站实测提取（WebFetch 拉 HTML/CSS，或 Playwright 打开后读 computed style），区分实测值与推断值。决策来源记"用户明确确认"。
- **D 授权模型决定**：用户明确说"你定"，从参考池选一个并说明理由。决策来源记"用户授权模型决定"。

分支可换道：A 的候选都不满意 → 转 B 看方向样张或转 C 自报；B 的样张都不合意 → 转 A/C；实测提取失败（登录墙、动态渲染拿不到值）→ 回 A 换候选，或请用户提供截图素材。

样张是一次性候选素材：截图和临时 HTML 留在对话或临时目录，**不写入链路目录**。

输出：选定来源、提取方式、决策来源。

### Phase 3：蒸馏生成 visual-design.md

按 `templates/visual-design.md` 的骨架生成草稿，四步：

1. **取**：按用户要求从来源抽段落；混合要求（如"Stripe 的配色 + Notion 的排版"）从多份各取，来源节分别登记。
2. **换**：专有字体换系统字体栈；品牌 Logo、商标、品牌文案不使用。
3. **裁**：与项目无关的部分整节拿掉，或在「明确不采用」记一行。
4. **出**：按模板章节填具体值。

硬约束：

- 只写具体值（hex 色值、px、字体栈、毫秒），不写形容词——形容词无法验收。
- 模板表格的列名与列数是校验契约，不得改动。
- 「明确不采用」逐条列出，不得为空或只写"无"——负面清单和正面清单一样防漂移。
- 「来源与替代」记录来源 URL / commit / 提取方式 / 日期，区分实测值与推断值，替代方案逐条写明。
- 探索已有代码库时发现与 INTENT.md 或 PRD 冲突的信息，停下来告知用户，不要自行改写原意。

输出：`visual-design.md` 完整草稿。

### Phase 4：生成 visual-baseline.html

按 `templates/visual-baseline.html` 渲染：

- 样式变量逐项来自 `visual-design.md` 第 2-5 节，不在本文件里发明规范之外的新样式。
- 渲染替代后的真实字体栈——用户接下来确认的是真实长相，不是想象。

输出：`visual-baseline.html` 完整草稿（与规范一同展示）。

### Phase 5：确认与写入

1. 在回复中展示两份产物的完整内容。
2. 用户回复"确认"即构成全文确认；"继续""嗯""可以"不算。
3. 写入链路目录，运行：

   ```bash
   python "{intent-visual skill 目录}/scripts/visual_validate.py" "{目标项目根目录}/intent-chain/{链路目录}/visual-design.md"
   ```

4. 修复结构问题后重新运行。若修复改变了色板、字体、组件值等实质内容，之前的全文确认立即失效，必须重新展示并确认。

输出：通过结构校验的 `visual-design.md` 和 `visual-baseline.html`。

### Phase 6：登记与交接

1. 征得用户同意后，在 INTENT.md 第 12 节表格末尾登记一行（只新增这一行，不改动其他内容）：

   ```markdown
   | D{序号} | 生成的视觉规范 | intent-chain/{链路目录}/visual-design.md | 全部页面，对照 visual-baseline.html | {用户确认原话} |
   ```

2. 重跑 `intent_validate.py` 确认 INTENT.md 仍通过校验（V10 检查设计标准行）。
3. 交接 intent-issues：第 12 节已有素材行后，`issues_validate.py` 的 V6 会要求涉及界面的工单在验收标准中写"对照 visual-design.md 结构一致"；intent-dev 对照基线页实现；intent-verify 的 V3 会要求路径证据附真实截图并与基线页比对。这些全是既有机制，本 skill 不做任何改动。

## 强制规则

1. **四件套必须存在且通过校验**：不通过则不进入视觉设计。
2. **分支判定结果必须告知用户**：无界面或已有素材时不产出文件，不静默跳过。
3. **来源必须经 Phase 2 菜单由用户选择或明确授权**：不代替用户拍板视觉方向；决策来源遵循 INTENT 决策契约（用户明确确认 / 用户授权模型决定）。
4. **远程取用必须用 pin 的 commit**：见 `references/README.md`；禁止浮动分支名，产物来源必须可复现。
5. **只写具体值，不写形容词**：hex、px、字体栈、毫秒；模板表格列名与列数不得改动。
6. **「明确不采用」不得为空**：「来源与替代」必须含 URL / commit / 原创 声明之一和日期，并区分实测值与推断值。
7. **专有字体与品牌资产必须处理**：字体换系统字体栈，Logo 与商标不使用，全部记录在来源与替代节。
8. **样张等候选素材不写入链路目录**：链路目录只放最终产物。
9. **先确认再写文件**：展示完整草稿，用户回复"确认"即构成全文确认；"继续""嗯""可以"不算。
10. **结构校验必须通过**：写入后运行 `visual_validate.py`，实质内容修改后确认失效、重新确认。
11. **登记后必须重跑 intent_validate.py**：D 行使用用户确认原话；除第 12 节新增一行外不得改动 INTENT.md 其他内容。
12. **按模板写入**：写入前必须先读取 `templates/visual-design.md` 和 `templates/visual-baseline.html`，模板是完整格式契约。
13. **上游已答不重问**：用户已在 INTENT.md 或上游链路文档中明确记录的信息直接引用；仅当发现现状与记录冲突时才向用户确认。
14. **对用户说人话**：面向用户的汇报、提问和确认请求不用链路内部黑话；确认请求必须让用户看得懂再确认。括注解释过的领域词若尚未收录进 INTENT 术语表，提醒用户回 intent-anchor 补登记。

## visual-design.md 必需章节

1. 概览
2. 色板
3. 字体与字号阶梯
4. 间距与圆角
5. 组件样式
6. 布局与响应式
7. 动效
8. 明确不采用
9. 来源与替代

## 文件存放

最终文件放在目标项目根目录：

```text
intent-chain/{链路目录}/visual-design.md
intent-chain/{链路目录}/visual-baseline.html
```

- 链路目录由 intent-anchor 创建，两份产物写入同一目录。
- 同一产品的修订覆盖原文件。

## 能力边界

Intent-Visual 能够：

- 三种来源的风格取证与蒸馏：参考池推荐、常备方向样张、实测提取。
- 让用户通过真实样张按视觉做选择，而不是用风格词汇描述。
- 生成可验收的规范与基线页，登记后激活既有下游门禁，不改动任何下游校验器。

Intent-Visual 做不到：

- 保证达到参考品牌的水准——专有字体替代、动效与排版工艺有实际损失；产出定位是"风格参考"，不是"品牌还原"。
- 像素级自动比对（第一版不做）：风格相符 = 页面截图与基线页并排 + 人工确认；token 偏差算缺陷，气质差距由用户裁决。
- 替代 intent-verify 的路径验收；替代 intent-dev 写页面。
