你现在负责对一个已经完成的开发任务进行独立验收。本轮只做验收，不修改源码、配置或文档。可以运行不会改变业务数据或外部系统的常规检查和测试；可能产生危险副作用的命令不要执行。

## 工作区

- 项目绝对路径：`e:\agent\blue-skillhub`
- 当前分支：`master`
- 任务基线：`HEAD`（commit `b333c8a`，`docs(ruleblade): add section 9 - prevent over-optimization and review expansion`）。该 commit 是 intent-anchor 改动前最后一个提交，改动均未提交，处于工作区未暂存状态。
- 工作区状态（`git status --short`）：

  ```
   D eval/runs/real-projects/2026-07-04-minimax-m3-delivery-d19r2/README.md
   M skills/intent-anchor/SKILL.md
   M skills/intent-anchor/references/semantic-audit.md
   M skills/intent-anchor/scripts/intent_validate.py
   M skills/intent-anchor/templates/INTENT.md
   M skills/intent-anchor/templates/stage-gate-check.md
   M skills/intent-anchor/tests/fixtures/valid-intent.md
   M skills/intent-anchor/tests/test_intent_validate.py
  ?? HANDOFF.md
  ?? blue-interview-log/
  ?? docs/blue-interview-validation-report-2026-07-13.md
  ?? docs/plans/
  ```

  属于本任务的未提交改动：`skills/intent-anchor/` 下 7 个文件（均标记为 `M`）。

  明确不属于本任务的用户原有改动：
  - `D eval/runs/real-projects/2026-07-04-minimax-m3-delivery-d19r2/README.md`（删除，任务前已存在）
  - `?? HANDOFF.md`、`?? blue-interview-log/`、`?? docs/blue-interview-validation-report-2026-07-13.md`、`?? docs/plans/`（均为未跟踪文件，任务前已存在）

  另外存在两份运行态副本，用户已明确声明不修改：
  - `C:\Users\blue\.claude\skills\intent-anchor\`——从 GitHub 拉取的运行态，本次任务中已被还原到 HEAD 版本（即改动前的原始状态）。
  - `C:\Users\blue\.codex\skills\intent-anchor\`——同样是从 GitHub 拉取的运行态，本次任务未触碰。

## 原始需求

用户原话（转录文件中按时间顺序整理）：

1. 第一条消息："你先看看这个执行记录 E:\agent\EnterpriseMatchHub\app\2026-07-24-084004-command-messageintent-anchorcommand-message.txt"

2. 用户在 EnterpriseMatchHub 项目中使用 intent-anchor → to-prd → to-issues 三个 skill 链路后，发现实现结果存在以下质量问题（用户原话整理）：
   - "意图：方向对，缺「UI 以原型为准」硬约束"
   - "PRD：功能对，黑话多，缺原型验收章"
   - "Issues：竖切对后端友好，验收没绑 prototype → 最大流程漏洞"
   - "实现：按「能测通」交付，不按「像产品」交付 → 最大质量责任"
   - "质量不高 = 流程门禁缺原型 + 我实现时以 API/测试为 KPI，而不是以你给的页面为 KPI"
   - "金刚区"等行业黑话原样进入文档和界面文案，普通人看不懂
   - "FRANCHISE 1 TRANSFER 2 COOP 3 AIC 4 LEGAL 显示未中文名称啊 不然看不懂"

3. 用户提出的可执行改进方向（原话）：
   - "每条前端相关 issue 验收必须写：对照 prototype/screens/xxx.html，结构一致"
   - "Done 定义：功能通 且 UI 过原型，缺一不可"
   - "文案规则：界面/提示只用大白话；黑话只留在开发文档"

4. 用户确认的 skill 改造范围（原话）："intent-anchor to-prd to-issues 我主要用了这三个skill intent-anchor是我们这个项目里的 可以改造 另外两个是别人的 不好直接改 后续如何避免这些问题？"

5. 用户确认的改造方案（原话）："一、intent-anchor 改造（3 处） 二、to-prd / to-issues 绕行方案 选方案 A吧"

6. 用户纠正改错位置（原话）："妈滴屁 你是不是改歪了啊 要改的skill在这里 这才是源码 E:\agent\blue-skillhub\skills\intent-anchor .claude和.codex下面的是从github直接拉取的 属于运行态 不用修改"

## 后续确认

1. **改造范围**：只改 `e:\agent\blue-skillhub\skills\intent-anchor`（源码），不修改 `.claude` 和 `.codex` 下的运行态副本。
2. **方案 A**：to-prd / to-issues 不直接修改，通过 intent-anchor 的 Phase 4 交接 prompt 注入设计标准和术语要求，让下游 skill 继承约束。
3. **intent-anchor 改造 3 处**：
   - 改动 1：识别设计标准——Phase 2 新增步骤，检查项目目录中是否存在原型/设计稿，有则请用户确认作为 UI 验收基线，记录到 INTENT.md 新增的第 12 节。
   - 改动 2：标记术语——Phase 2 新增步骤，审查能力描述中的行业黑话，给出人话翻译和界面文案，记录到 INTENT.md 新增的第 13 节。
   - 改动 3：增强交接 prompt——Phase 4 的交接 prompt 中增加设计标准和术语的约束条款，传递给下游 skill。
4. **明确排除**：不修改 to-prd 和 to-issues 的代码；不修改 `.claude` 和 `.codex` 下的运行态副本。

## 实现会话的完成说明（待核实）

实现会话声称完成了以下内容：

1. 在源码位置 `e:\agent\blue-skillhub\skills\intent-anchor` 修改了 7 个文件：
   - `SKILL.md`：Phase 2 加第 7、8 步（识别设计标准、标记术语），Phase 2.5 表格加 S6/S7 行并更新描述文字从 S1-S5 改为 S1-S7，强制规则第 4 条同步修改，Phase 4 交接 prompt 加设计标准和术语要求，必需章节列表加第 12、13 节。
   - `templates/INTENT.md`：加第 12 节（设计标准）和第 13 节（术语表）。
   - `references/semantic-audit.md`：加 S6（设计标准审查）和 S7（术语标记审查），执行要求从 S1-S5 改为 S1-S7。
   - `templates/stage-gate-check.md`：brainstorm/PRD、任务拆分、开发完成三个阶段各加设计标准和术语检查项。
   - `scripts/intent_validate.py`：REQUIRED_SECTIONS 加第 12、13 节，V2 PASS 消息改为"全部 13 个章节存在"，V9 审查范围扩展到 S1-S7，新增 V10（设计标准校验）和 V11（术语表校验）。
   - `tests/fixtures/valid-intent.md`：加第 12、13 节和 S6/S7 复核记录。
   - `tests/test_intent_validate.py`：期望检查数从 9 改为 11，S5 后面加 S6/S7，新增 `TestDesignStandards` 和 `TestTerminology` 两个测试类。

2. 声称的验证结果：
   - 源码位置：`python -m pytest skills/intent-anchor/tests/test_intent_validate.py -v` → 27 passed，退出码 0。
   - `.claude` 运行态还原后：19 passed，退出码 0。

3. 声称还原了 `.claude` 下 7 个运行态文件到 HEAD 版本（使用 `git show HEAD:` 覆盖）。

4. 声称修复了中文引号导致的 SyntaxError（`intent_validate.py` 中 Python 字符串包含中文引号 `"` `"` 导致语法错误）。

## 验收要求

1. 重新读取原始需求和后续确认，逐项列出验收项。

2. 查看当前 git status、实际 diff 和相关文件；改动已经提交时比较相关 commit 或基线与当前状态。不要直接采信上述完成说明。

3. 对修改过的函数、字段、接口、配置和公开行为反查调用方、引用方、注册点、生成物与测试；找不到引用时明确写"未找到"。

4. 检查是否存在漏改、误改、只改一半、无关改动，或者覆盖用户原有改动的情况。

5. 检查测试是否真正覆盖本次需求。能安全判断时，确认测试在旧错误仍存在时会失败；无法验证时如实说明。

6. 重新运行必要的验证命令，记录实际命令、退出码和关键结果。不要引用实现会话的结果代替复验。

7. 测试全部通过也不能直接判定完成；必须回到原始需求逐项核对。

### 具体验收检查点

以下是实现会话声称完成但需要独立核实的关键点：

- **C1**：`SKILL.md` Phase 2 是否新增了"识别设计标准"步骤，要求检查项目目录中的原型/设计素材并请用户确认。
- **C2**：`SKILL.md` Phase 2 是否新增了"标记术语"步骤，要求审查能力描述中的行业黑话并给出人话翻译和界面文案。
- **C3**：`SKILL.md` Phase 2.5 表格是否包含 S6（设计标准）和 S7（术语标记）两行，描述文字是否从 S1-S5 更新为 S1-S7。
- **C4**：`SKILL.md` 强制规则第 4 条是否从 S1-S5 更新为 S1-S7。
- **C5**：`SKILL.md` Phase 4 交接 prompt 是否包含设计标准约束（PRD 列出设计文件路径、工单 Acceptance criteria 包含对照设计文件、Done 定义包含 UI 对照）和术语约束（界面使用人话翻译、原始术语只允许在开发文档中）。
- **C6**：`SKILL.md` 必需章节列表是否包含第 12（设计标准）和第 13（术语表）节。
- **C7**：`templates/INTENT.md` 是否新增第 12 节（设计标准表格，含设计素材 ID、类型、路径、验收范围、用户确认）和第 13 节（术语表表格，含原始术语、人话翻译、用于界面的文案、出现在能力 ID）。
- **C8**：`references/semantic-audit.md` 是否新增 S6（设计标准）和 S7（术语标记）的完整规则定义，包括有素材/无素材和有术语/无术语两种情况的处理方式，以及执行要求从 S1-S5 更新为 S1-S7。
- **C9**：`templates/stage-gate-check.md` 是否在 brainstorm/PRD、任务拆分、开发完成三个阶段各增加了设计标准和术语的检查项。
- **C10**：`scripts/intent_validate.py` 的 REQUIRED_SECTIONS 是否包含"## 12. 设计标准"和"## 13. 术语表"，V2 PASS 消息是否更新为"全部 13 个章节存在"。
- **C11**：`scripts/intent_validate.py` 的 audit_headings 是否包含"S6 设计标准"和"S7 术语标记"，V9 PASS 消息是否更新为"S1-S7"。
- **C12**：`scripts/intent_validate.py` 是否新增 V10（设计标准校验：有素材时检查 5 列完整且无占位符，无素材时检查用户确认"没有"）和 V11（术语表校验：有术语时检查 4 列完整且无占位符，无术语时检查"无术语需要翻译"）。
- **C13**：`tests/fixtures/valid-intent.md` 是否新增第 12、13 节和 S6/S7 复核记录，且 fixture 能通过所有校验。
- **C14**：`tests/test_intent_validate.py` 期望检查数是否从 9 更新为 11，是否新增 `TestDesignStandards` 和 `TestTerminology` 测试类，测试是否覆盖缺失章节、缺用户确认、占位符、缺翻译/界面文案等失败场景。
- **C15**：`.claude\skills\intent-anchor\` 下的 7 个文件是否已还原到 HEAD 版本（即不包含本次改动）。
- **C16**：`intent_validate.py` docstring 中 V2 描述是否仍写"11 个必需章节齐全"（与实际检查 13 个章节不一致——这是一个已知的文档遗漏）。
- **C17**：`intent_validate.py` 的 `git diff HEAD`（不带 `--ignore-all-space`）是否显示全文件重写（527 行删除、603 行新增），而 `--ignore-all-space` 显示实际只有 79 行新增、3 行删除——确认是否有不必要的空白噪音。

### 运行验证命令

在 `e:\agent\blue-skillhub` 下运行：

```
python -m pytest skills/intent-anchor/tests/test_intent_validate.py -v
```

确认退出码和测试数量。

在 `C:\Users\blue\.claude\skills\intent-anchor` 下运行：

```
python -m pytest tests/test_intent_validate.py -v
```

确认 `.claude` 运行态是否已还原到改动前状态（预期 19 passed，而非 27 passed）。

## 输出要求

- 总结论只能是 PASS、FAIL 或证据不足。
- 每项原始需求都要给出结论和具体文件、代码位置或命令证据。
- 单独列出漏改、误改、无关改动、未验证内容和剩余风险；没有也要明确写"未发现"。
- 如果原始需求不足以判断是否完成，不得给出 PASS。缺少任务基线时，说明哪些改动无法确认归属；只有它确实妨碍验收时才判定为证据不足。
- 本轮不要修复发现的问题。先提交验收报告，等待用户决定下一步。
