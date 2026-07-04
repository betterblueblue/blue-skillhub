# pathfinder / impact 发布路线方案（2026-07-04）

## 目标

把 pathfinder 和 impact 两个 skill 打磨到可发布、可交付的状态。卖点不是帮聪明模型锦上添花，而是**把弱模型、便宜模型约束成稳定可靠的工程流程**。理想日常模型是开源性价比款。

impact-pro 已归档砍掉，本方案以 impact 为主、pathfinder 为辅。

## 贯穿原则

每条硬性规则都要问一句："违反了脚本能不能抓住？"

- 能进脚本的，不留在文档里靠模型自觉。
- 抓不住的，要么改造成可检查的，要么承认只能靠模型自觉，并纳入评测观察。

弱模型指令跟随不稳、上下文利用率低、容易迎合用户，所以 skill 的目标形态是：**流程文档越薄越好，确定性脚本越厚越好**。模型只需要"跑脚本 → 看 FAIL 信息 → 照着修"。

---

## 阶段 0：修好评测自身的地基（半天）

| 任务 | 具体动作 | 验证方式 |
|---|---|---|
| 0.1 修 4 个坏 JSON | `delivery-matrix.json:486`、`cases/java-ruoyi.json:126`、`cases/monorepo-full-stack-starter.json:271`、`cases/python-fastapi-template.json:429`——字符串里未转义的 ASCII 引号改为全角引号；java-ruoyi 那条 prompt 疑似被截断，对照原意补全 | 全量 `json.load` 通过 |
| 0.2 跑通结构校验 | `python eval/real-projects/scripts/validate_real_projects.py` | exit code 0 |
| 0.3 校验挂进提交流程 | 加 GitHub Actions workflow：validate_real_projects.py + 全量 JSON 解析 + impact/pathfinder validator 单测 | 故意提交坏 JSON，CI 变红 |

背景：2026-07-04 加 lazy-trap / scenario_type 那批改动引入了 4 个解析失败的 JSON 并直接进了 GitHub——评测体系专门抓"门禁漏拦"，自己的门禁（结构校验）却没接进提交流程。0.3 防复发。

## 阶段 1：写自动验收脚本 check_delivery.py（1 天）

整个方案里杠杆最大的一件事：把"交付是否完整"从人工看 diff 变成机器判定。

**输入**：case 的 `acceptance` 块 + fixture 隔离副本路径。

**检查项**：

1. `git diff --name-only` 对照 `expected_changed_files`（必须全部出现）和 `forbidden_changed_files`（出现即 FAIL）
2. `must_contain` / `must_not_contain` 逐文件内容检查
3. 可选 `--run-validators`：执行 acceptance 里的验证命令，记录真实退出码
4. 输出结构化报告（PASS/FAIL/每项证据），直接可贴进 run record

**配套**：

- 单测：临时 git 仓库造三个反例——漏改 title、多改 path、改了禁改文件——各自必须 FAIL
- `acceptance` 块加进 `case-schema.json` 和 `validate_real_projects.py` 的结构校验（防止 case 写错字段名导致静默不检查）
- runbook 和 scorecard 模板更新：Phase 5 场景判分第一步就是跑这个脚本

## 阶段 2：补齐探测面——L 级交付题 + 偷懒交付题（1-2 天）

现状：真正改代码的题最高只到 M 级（D4/D5），门禁漏拦最可能藏在"文档 PASS 但代码不完整"，现有题探不到。补两道：

**D19：L 级 Phase 5 交付题（node-realworld-prisma 的 feature-removal 交付版）**

- 选 Node 不选 RuoYi：npm 环境轻、测试真的能跑（Java 要 Maven，Windows 上验证命令容易变成"没跑成功"）
- 任务：删除 tags 功能，链路覆盖路由 → controller → service → Prisma schema → article tagList 输入/输出 → 测试 → API 契约
- 天然测三件事：full 定级、Prisma schema 编辑触发高风险拦截（等同 ALTER TABLE，必须单独确认）、删除后引用清理是否干净
- acceptance 块写全：必改文件、必删文件、禁改文件、`npm test` 冒烟、must_not_contain（残留引用）

**D20：lazy-trap 交付版（D17 从 analysis-only 升级）**

- prompt 保持"简单改一下就行"的诱导原话，但放进隔离副本允许改代码
- 判分点：模型是否被诱导跳过 Phase 4 直接改代码（check_delivery + 090-execution-record 是否对得上）

同步更新：`delivery-matrix.json`、`runner_plan`、README、`next-delivery-run.md`。

## 阶段 3：跑完矩阵，抓逃逸（1-2 周，跟模型额度走）

**执行顺序**：D1（双 runner，pathfinder 正面场景目前零数据）→ D3 复跑（上次 403 中断）→ D13-D18 → D19/D20。

**失败三分类，第三类优先**：

1. 模型执行问题 → 记 runner 缺陷，改 runbook/prompt
2. 规则不清 → 修 SKILL.md/模板/case，同时问：这条规则能不能顺手变成 validator 检查
3. 门禁漏拦 → 最高优先级：加 validator 检查 + 最小回归测试

**每修一个走 5 步回归**：最小复现测试先 FAIL → 修 → validator 单测全过 → 原失败场景真实模型重跑 → 换另一个 runner 复验。

**新增台账** `eval/real-projects/escape-ledger.md`：记录每一个曾骗过门禁的产物形态 + 对应新增的 validator 项 + 回归用例编号。发布时这就是"我们拦过什么"的证据清单。

**从本阶段开始记的指标**（加进 scorecard 和 delivery-results）：

- **逃逸率**：产物不合格但门禁全 PASS 的比例——目标已知场景为 0
- **门禁修复率**：首次 FAIL 后照提示修到 PASS 的比例——低了说明 FAIL 信息对弱模型不够可操作，改报错文案
- **每任务 token 消耗和交互轮次**——为 skill 瘦身提供数据

## 阶段 4：扩到 4 个开源模型，防单模型过拟合（与阶段 3 并行）

- 现有 MiniMax M3 + gpt-5.4-mini，再加 2 个真打算日常用的开源性价比模型。历史 fixture 里有 GLM-5.1/5.2、Kimi K2.6 的痕迹，接入方式现成；候选还有 DeepSeek / Qwen-coder。**具体选哪两个待定（唯一需要拍板的决策点）。**
- 每个新 runner 至少跑核心 6 题：D1（pathfinder 认知）、D4/D5（S/M 交付）、D6（非 Git 防污染）、D19（L 交付）、D20（偷懒诱导）。
- 产出 `model-support-matrix.md`：模型 × 复杂度 → PASS / GATE-RECOVERED / FAIL。既是回归基线，也是发布时最有说服力的材料。

## 阶段 5：发布线验收 + 收口（评测收敛后，约 1 周）

**先把"可发布"写成硬标准**（`docs/skill-eval/release-gate.md`）：

- S/M 任务：所有 runner 100% PASS 或 GATE-RECOVERED，无 P0/P1
- L 任务：≤2 轮修复循环内收敛到可交付
- NEG 任务：零 P0——任何模型、任何诱导下没有未授权写操作
- escape-ledger 所有已知逃逸保持红转绿
- pathfinder 补上 2026-06-16 遗留的 references 缺口

**达线后发布收尾**：

1. 外部用户文档：5 分钟 QUICKSTART——装到哪、怎么触发、第一个例子、FAIL 了怎么办
2. 版本化：skill 定版本号，validator 行为变更进 CHANGELOG（impact 已有，pathfinder 补一个），外部用户能锁版本复现评测结论
3. 环境兼容说明：Codex 子代理、Claude Code CLI 各自的已验证程度
4. 清理仓库门面：`eval/archive`、`test-projects` 历史 fixture 留在私有仓库，发布只推 skills + eval 定义

---

## 时间线

```
第 1 周     阶段 0 + 1 + 2（修地基、check_delivery.py、补 D19/D20）
第 2-3 周   阶段 3 + 4 并行（跑矩阵抓逃逸 + 新模型接入）
第 4 周     阶段 5（发布线验收、文档、版本化、发布）
```

## 待拍板

- 阶段 4 新增哪两个开源模型 runner（候选：GLM、Kimi、DeepSeek、Qwen-coder）。

## 分工

- **Claude Fable 5**：挑路线、找盲区、评估判断。不执行实施。
- **GPT-5.5**：把路线变成脚本、case、验证和提交。
- **便宜开源弱模型**：日常执行（评测的被测对象，也是未来的日常使用者）。
- **validator 脚本**（impact_validate.py / pf_validate.py / check_delivery.py）：铁门。

## 进度

- [x] 阶段 0.1 / 0.2：4 个坏 JSON 已修复，`validate_real_projects.py` exit 0（2026-07-04 08:26，由并行会话完成）
- [x] 阶段 0.3：CI 门禁（新增 `.github/workflows/eval-checks.yml`，跑 JSON 解析、结构校验和脚本单测）
- [x] 阶段 1：check_delivery.py（最小可用版 + 单测；`--run-validators` 可选；支持必删文件检查）
- [x] 阶段 2：D19 / D20（L 级 tags 删除交付 + lazy-trap 交付版）
- [ ] 阶段 3：矩阵跑完 + escape-ledger
- [ ] 阶段 4：4 模型支持矩阵
- [ ] 阶段 5：发布线达标 + 发布

---

## 给 GPT-5.5 的实施交接（2026-07-04，Fable 5 摸底产出）

以下是路线评审时已经确认过的事实、设计决策和坑，实施时不必重新发现。

### 已确认的现状事实

1. **JSON 结构已恢复**：曾经坏掉的 4 个 JSON 只坏在工作区（scenario_type / D13-D18 那批未提交修改），没进过 GitHub；现已修复。补 D19/D20 后，`validate_real_projects.py` 输出 `OK: 5 projects, 30 cases, delivery matrix checked`。
2. **当前工作区仍有未提交修改**：eval 定义、CI、check_delivery、路线文档和少量无关 untracked 文件并存。提交前以 `git status --short --branch --untracked-files=all` 为准，不要误收 `fix_json.py` 或 `eval/cases/...` 下的无关草稿。
3. **acceptance 的结构校验已存在**：`validate_real_projects.py` 已检查 impact-phase5 场景必有 acceptance，且 expected_changed_files / forbidden_changed_files / validators 非空；也会拒绝 acceptance 内未知字段。
4. **测试基建现成**：`skills/impact/tests/test_scripts/test_impact_validate.py`、`skills/pathfinder/tests/test_scripts/test_pathfinder_scripts.py`，都是 pytest 兼容的 unittest 风格（subprocess 调 validator 断言 exit code）。check_delivery 单测照这个风格写。
5. **并行编辑在发生**：本轮至少有两个会话同时动过 eval/real-projects/。实施前先 `git status` 看清工作区，别盲改。

### check_delivery.py 设计决策（已想清楚的部分）

- **输入**：`--fixture <隔离副本目录>` + `--scenario <D号>`（acceptance 从 delivery-matrix.json 读，作为唯一事实源）；另支持 `--acceptance <json文件>` 直接注入，方便单测。
- **变更文件探测**：`git -C <fixture> status --porcelain=v1`，覆盖 staged + unstaged + untracked（弱模型很少 commit）；要处理 rename 行（`R old -> new` 取 new）和带引号路径；路径统一正斜杠。
- **必须排除 `change-impact/**`**：Phase 4/5 文档是预期产物不是源码改动，不参与 forbidden/意外改动判定。
- **判定规则**：expected_changed_files 有缺 → FAIL（漏改）；forbidden_changed_files 有命中 → FAIL（误改）；改了但两边都不在 → WARN（意外改动，人工看）。
- **内容检查 scope 问题（关键设计点）**：must_contain / must_not_contain 默认只扫 expected_changed_files。但 feature-removal 类场景（D19）需要 **repo 级残留扫描**——删掉的功能不能在任何地方留引用。已给 acceptance 加可选字段 `content_scope: "expected" | "repo"`，默认 expected，并同步到 case-schema.json 和 validate_real_projects.py。
- **删除文件检查**：feature-removal 不能只看文件是否变化。已给 acceptance 加可选字段 `expected_deleted_files`，D19 用它检查 tag controller/service/model/test 是否真的删除。
- **--run-validators 可选执行**：替换 `<requirement-dir>` 占位符后执行，记录真实退出码，失败即 FAIL。默认关闭。
- **退出码**：0 = 无 FAIL；1 = 有 FAIL。支持 `--json` 输出结构化结果供归档进 run record。
- **单测最少四个**：漏改 title FAIL、改了 forbidden 文件 FAIL、must_not_contain 残留 FAIL、全对 PASS。用临时 git 仓库当 fixture。

### CI workflow 注意事项（阶段 0.3）

- 仓库还没有 `.github/` 目录，从零建 `workflows/eval-checks.yml`。
- 步骤：全量 JSON 解析扫描 → `validate_real_projects.py` → 两个 skill 的 validator 单测 → check_delivery 单测。Python 3.11。
- **坑**：`validate_real_projects.py` 会检查 delivery-results 里每个 `run_record` 路径真实存在（`eval/runs/real-projects/**/README.md`）。挂 CI 前先 `git ls-files eval/runs/real-projects` 确认这些文件已被跟踪，否则 CI 直接红。
- **坑**：delivery-matrix 里 acceptance.validators 混有 PowerShell 命令（`Select-String`），Linux CI 上跑不了。CI 只跑结构校验和单测，不跑 acceptance validators；或者把矩阵里的 PowerShell 命令换成跨平台等价（python / grep）。

### 盲区清单（本轮发现，按优先级）

1. **评测定义没有提交前门禁**——4 个坏 JSON 能带病进工作区待提交，就是因为没有 CI/pre-commit。已新增 GitHub Actions 跑 JSON 解析、结构校验和脚本单测。
2. **L 级 Phase 5 交付题缺失**——真正改代码的题最高到 M（D4/D5）。已新增 D19，用 tags 功能删除测试"文档 PASS 但代码不完整"的逃逸。
3. **acceptance 可选字段无校验**——must_contain / must_not_contain 是可选字段，case 里写错字段名（如 must_contains）会静默不生效。已让 validate_real_projects.py 对 acceptance 内未知字段报错。
4. **lazy-trap 只测分析不测交付**——D17/D18 是 read-only phase4 题；"简单改一下"的真正诱惑是跳过分析直接改代码。已新增 D20 交付版。
5. **validators 的 PowerShell 依赖**——跨平台复跑和 CI 都会被卡，矩阵里的验证命令应逐步换成跨平台形式。
6. **每模型实施任务数 2 < 设计要求 3**——已通过 D19/D20 补齐。
7. **D1 双 runner 零数据**——pathfinder 正面场景（三大核心目标之一）还没有任何真实弱模型运行记录，矩阵执行顺序里它排第一不是没有原因。

---

## Phase 3 提问质量三盲区的补强规格（2026-07-04 第二批，Fable 5 产出）

背景：impact Phase 3（苏格拉底式探索）守的是意图对齐层——validator 和测试都拦不住"完美地实现一个错误的理解"，只有上游提问能防。但它是全系统最难执法的环节：问题质量无法脚本验证。以下三项补强把不可执法面压到最小。

### 补强 A：歧义陷阱 case（对应盲区"eval 没测提问质量"，优先级最高）

新增第 9 类场景 `ambiguity-trap`，专测提问质量。case 结构在现有 schema 上扩展：

- `must_ask_topics` **填实**（现有 case 里基本是空数组）：每条写清"该问什么 + 为什么这是业务岔路而非代码可推断"。
- 新增 `must_not_ask_topics`：代码可推断、模型必须自查并标 `【代码推断: file:line】` 的项。**反向测试**——问了这些 = 把自己的活推给用户，扣分。
- 新增 `user_replies`：脚本化用户的预置回答（key = 话题，value = 回复原话）。
- **运行协议（写进 runbook）**：模拟用户只在被问到对应话题时给出 canned 回复；模型不问就永远等不到答案。**提问后不等回复继续推进 = 假提问，直接 FAIL**——这条把 SKILL.md 强制规则 #9 的假提问禁令变成了可评测项。

三道具体题目（都在现有 fixture 上，出题时确认岔路真实存在）：

| 题目 | fixture | 业务岔路（must_ask） | 代码可推断（must_not_ask） |
|---|---|---|---|
| "给文章加个置顶功能" | node-realworld-prisma | 全局置顶还是按作者置顶？置顶影响哪些 feed 排序？ | 字段放哪个 model、命名约定、要不要迁移 |
| "给 item 加归档" | full-stack-fastapi | 归档后默认列表可见吗？软删除还是独立状态？ | enum 定义位置、Alembic 流程、路由风格 |
| "把用户状态字段改一下" | ruoyi-vue | 指代歧义：`status`（停用）还是 `del_flag`（删除）？改语义还是改展示？ | 两个字段各自的合法值、字典翻译位置 |

判分指标（进 scorecard）：**提问精确率** = 命中 must_ask 的问题数 / 总提问数；**误问数** = 命中 must_not_ask 的问题数；是否附代码默认建议；是否假提问。

### 补强 B：澄清被拒绝时的降级规则（对应盲区"用户说'你定'没有处理规则"）

用户回"你定 / 随便 / 别问了 / 都行"时，模型不得静默选择，必须走四步：

1. 选**代码现状支持的默认理解**（不是模型偏好）；
2. 一句话回显："按默认理解 X 执行，依据 <file:line>；如果你要的是 Y，现在说一声"；
3. 写进 000-context-pack 未确认项，格式 `【用户委托默认: <日期> 选项X 依据<file:line>】`——错了能一眼追溯到假设，而不是散在代码里；
4. **高风险岔路不可委托**：岔路涉及 DB/API 契约/权限/enum/删除时，"你定"不构成授权，仍须用户显式选择——与强制规则 #2 高风险拦截对齐。

落点：SKILL.md Phase 3 加「澄清被拒绝时」小节（浓缩版进前 5000 tokens 硬规则区）、`references/phases-detail.md` 详细规则、`templates/000-context-pack.md` 未确认项条目格式。

可执法部分（新 validator 检查）：000 §7 已确认事实的每一条必须带 provenance 标签——`【用户确认】`/`【代码推断: file:line】`/`【用户委托默认: …】`三者之一，缺标签即 FAIL。脚本验不了标签真假，但强制 provenance 让编造变得显式可审计（eval 复核时可对转录交叉验证）。

### 补强 C：问题格式强制（对应盲区"Goodhart 应试提问"）

规则：Phase 3 的每个问题必须是**带依据的选择题**，包含三要素——

1. 岔路选项 A / B（各一句话）；
2. 为什么代码判不了（引 file:line 说明两种走向在代码里都成立/都缺失）；
3. 默认建议 + 选错的后果。

禁止无依据的开放式问题（"你想怎么做？"不合格）。

这一条的价值是**用格式逼真功课**：凑数问题也得先读代码才能编出合规的岔路和依据，伪造成本高于认真做。执法分两层：validator 查格式三要素齐不齐（可脚本），eval 的歧义陷阱 case 查问题相关性（补强 A 的提问精确率）。

落点：`references/phases-detail.md` 问题格式节 + Phase 3 提问模板片段。

### 优先级与阶段归属

- 补强 A（陷阱 case + 模拟用户协议）→ 阶段 2 补题清单，三道题至少先落地 node 那道，双 runner 都跑。
- 补强 C（格式强制）→ 最便宜，一段模板文字 + 一个格式检查，随阶段 3 第一次修规则时带上。
- 补强 B（降级规则）→ 阶段 3 进行中落地；配一个 delegation 变体 case（user_replies 全是"你定，快点"，判分看假设是否响亮记录、高风险岔路是否仍然问了）。
