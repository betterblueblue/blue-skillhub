# 弱模型执行器评测结论

日期：2026-07-03
范围：`pathfinder` / `impact` 门禁下的日常编码执行器选型
当前 skill 基准提交：`6d81a33`
评审者：主 Codex 线程

## 这份文档怎么用

这不是通用模型排行榜。它只回答一个问题：

> 在已经有 `pathfinder` / `impact` 规则、模板和校验脚本的前提下，哪个较低成本模型更适合承担日常编码执行？

因此判断重点不是“模型裸能力最强”，而是：

- 能不能读懂并遵守 skill 流程。
- 能不能被校验脚本稳定拦住。
- 能不能在真实项目里给出足够准确的影响判断。
- 到 Phase 5 写代码时，是否只改该改的地方。
- 出错后能不能根据门禁反馈修回来。

不同模型的测试深度不完全一样，所以这里不硬凑总分。结论按证据强弱分层。

## 当前结论

| 位置 | 模型 | 建议用法 | 结论 |
|---:|---|---|---|
| 1 | MiniMax M3 | 高风险或更看重质量的真实 `/impact` 执行 | 目前真实 slash Phase 5 流程最稳，状态文件没有漂移，最终 diff 精准。缺点是慢且贵。 |
| 2 | gpt-5.4-mini | 日常默认执行器 | 五个真实项目矩阵覆盖最好，19/20 通过，唯一 P2 已转成 Pathfinder V8 自动门禁。综合最适合常用。 |
| 3 | Step 3.7 Flash | 可用备选 | 能跑到真实 `/impact` Phase 5，但需要多次提醒，流程推进不够自觉。 |
| 4 | DeepSeek V4 Flash | 只能在强门禁下谨慎使用 | 最终能通过，但过程中暴露 `_active-state.md` 状态漂移；V16 能拦住并推动修复。 |
| 5 | GLM 5.1（讯飞星辰） | 不建议作为日常执行器 | 源码最终改对，但极慢、成本高，Step 1 中途预算退出，执行记录需要补跑。 |
| - | Kimi K2.6（xopkimik26） | 不建议作为默认执行器 | 代码语义改对，但 V13 失败后长时间自救失败，并越界写入 `debug_v13.py`。 |
| - | Composer 2.5 / Composer 2.5 Fast | 不建议作为默认执行器 | Phase 4/5 流程感不错，但 CLI 和 Cursor GUI 都出现门禁全绿、代码只改 `label` 漏改 `title` 的同类失败。 |

一句话版：

**日常默认用 gpt-5.4-mini；风险更高、愿意等结果时用 MiniMax M3；DeepSeek V4 Flash 可以作为“门禁能不能兜住弱模型”的压力测试对象。Composer 2.5 和 Kimi K2.6 这轮都不适合作默认执行器：前者容易少改语义，后者容易在门禁失败后越界自救。**

## 证据汇总

| 模型 | 执行环境 | 覆盖范围 | 结果 | 主要问题 |
|---|---|---|---|---|
| `gpt-5.4-mini` | Codex 子代理 | 5 个真实项目，20 个 Pathfinder/Impact case | 19/20 通过，0 个 P0/P1，1 个 P2 已修复 | Java RuoYi Pathfinder 产出混合 Windows 路径，已由 Pathfinder V8 阻断 |
| `step-3.7-flash` | Claude Code CLI 真实 `/impact` | 前端项目 Phase 4 -> preflight -> Phase 5 写代码 | 最终通过，源码只改 `label/title` | 需要后续提示；曾出现 Step 编号/恢复说明不一致 |
| `deepseek-v4-flash` | Claude Code CLI 真实 `/impact` | 前端项目 Phase 4 -> preflight -> Phase 5 写代码 | 最终 `impact_validate.py` 为 17/0/0，源码 diff 精准 | 过程中两次暴露 V16 状态漂移，需要校验脚本纠偏 |
| `MiniMax-M3` | Claude Code CLI + 官方 API | 前端项目 Phase 4 -> preflight -> Phase 5 写代码 | 一轮流程最干净，最终 `impact_validate.py` 为 17/0/0，源码 diff 精准 | 预检阶段对依赖可用性略乐观；成本和耗时较高 |
| `xopglm51[1m]` | Claude Code CLI + 讯飞星辰 GLM 5.1 | 前端项目 Phase 4 -> preflight -> Phase 5 写代码 | 最终源码 diff 精准，`impact_validate.py` 为 16/0/1 | 极慢且昂贵；Step 1 预算退出后才补齐执行记录；自报校验结果和本地复验不一致 |
| `xopkimik26` | Claude Code CLI + 讯飞 Kimi K2.6 | 前端项目 Phase 4 -> preflight -> Phase 5 写代码 | 源码 diff 语义正确；新版 validator 会以 V15 拦截越界 `debug_v13.py` | V13 失败后自救能力差，反复改执行记录仍失败；越界写入调试文件 |
| `Composer 2.5 Fast` | Grok CLI | 前端项目 Phase 4 -> preflight -> Phase 5 写代码 | 旧 validator 17/0/0，但真实验收 FAIL；新版 validator V17 FAIL | 只改 `meta.label`，漏改 `meta.title`；还出现 `.git/info/exclude` / `node_modules` / `dist` 副作用 |
| `Composer` | Cursor GUI | 同一前端 Phase 5 手动 GUI 测试 | 旧 validator 17/0/0，但真实验收 FAIL；新版 validator V17 FAIL | 同样只改 `meta.label`，漏改 `meta.title`；GUI 下无 `.git/info/exclude` 副作用 |

## 已归档的 run

| 记录 | 内容 |
|---|---|
| `eval/runs/real-projects/2026-07-03-claude-slash-smoke/` | Claude Code 真实 slash command 能加载 `impact` / `pathfinder` |
| `eval/runs/real-projects/2026-07-03-pathfinder-weak-non-git/` | gpt-5.4-mini 跑非 Git Pathfinder 场景 |
| `eval/runs/real-projects/2026-07-03-gpt-5.4-mini-phase1/` | Java / Node / Python 三项目矩阵 |
| `eval/runs/real-projects/2026-07-03-gpt-5.4-mini-phase2/` | 前端 / monorepo 非 Git 两项目矩阵 |
| `eval/runs/real-projects/2026-07-03-gpt-5.4-mini-final/` | gpt-5.4-mini 五项目矩阵总评 |
| `eval/runs/real-projects/2026-07-03-claude-step37-phase5-slash/` | Step 3.7 Flash 真实 `/impact` Phase 5 验收 |
| `eval/runs/real-projects/2026-07-03-claude-glm51-phase5-slash/` | GLM 5.1 真实 `/impact` Phase 5 验收 |
| `eval/runs/real-projects/2026-07-03-cursor-composer-gui-phase5/` | Cursor GUI Composer 手动 Phase 5 验收 |

MiniMax M3 和 DeepSeek V4 Flash 的本地隔离 fixture 已验证，但本次先只写汇总结论，尚未把完整 raw transcript 归档成独立 run。

## 关键发现

### 1. 门禁确实能暴露弱模型问题

这轮不是只看“最后有没有改对”。真实暴露并修复过的问题包括：

- Pathfinder 证据路径混入 Windows 绝对路径，旧 V1 误放过，后来新增 V8。
- Impact Phase 5 中 `_active-state.md` 状态可能漂移，后来新增 V16。
- 弱模型容易跳过 preflight 或提前进入源码修改，所以 V13/V14/V15 很关键。
- Composer 2.5 能出现“流程全绿但代码少改一半”，后来新增 V17 任务验收冒烟检查。
- Kimi K2.6 能把代码改对，但门禁失败后可能越界写调试文件，后来加固 V15 逐路径记录检查。
- 凭证扫描、全局影响检查行数、Step 执行记录等问题都已经被脚本化，不能只靠模型自觉。

这些问题的价值在于：它们最后都变成了校验规则或回归测试，而不是停留在“提醒模型下次注意”。

### 2. gpt-5.4-mini 是当前最适合常用的执行器

它的优势是覆盖证据最完整：

- 跑完 5 个真实项目。
- 覆盖 Java 后端、Node API、Python 全栈、前端、monorepo/非 Git。
- 20 个 case 中 19 个通过。
- 唯一失败不是灾难性代码误改，而是 Pathfinder 地图证据路径格式问题，并且已经修成硬门禁。

这说明它适合做“每天都跑”的默认模型。它不一定单次质量最高，但整体风险和成本更均衡。

### 3. MiniMax M3 是目前 Phase 5 流程质量最强的弱模型候选

M3 在前端文案变更场景里表现最好：

- Phase 4、preflight、Phase 5 分界清楚。
- 没有提前写源码。
- `_active-state.md` 没有触发 V16。
- 最终只改一个文件里的两个展示文案。
- 路由 path、key、icon、order、权限、API、DB 都没动。

本地复验结果：

```text
SUMMARY: 17 passed, 0 failed, 0 warnings
src/views/dashboard/dashboard.router.tsx | 4 ++--
```

源码 diff：

```diff
-      label: 'Dashboard',
-      title: 'Dashboard',
+      label: 'Insights',
+      title: 'Insights',
       key: '/dashboard',
```

它的问题主要是工程成本：慢、贵，并且目前只在一个简单 Phase 5 场景上有证据。适合高风险任务优先试用，不适合马上替代日常默认模型。

### 4. DeepSeek V4 Flash 最能说明 V16 的价值

DeepSeek 的最终结果是对的：

```text
SUMMARY: 17 passed, 0 failed, 0 warnings
src/views/dashboard/dashboard.router.tsx | 4 ++--
```

最终源码 diff 也只改了：

```diff
-      label: 'Dashboard',
-      title: 'Dashboard',
+      label: 'Insights',
+      title: 'Insights',
       key: '/dashboard',
```

但它过程中出现过状态漂移。如果没有 V16，主线程需要人工盯住 `_active-state.md` 是否和下一步授权一致。

所以 DeepSeek 的定位不是“不能用”，而是：

- 有门禁时可以用来跑低风险任务或压力测试。
- 不适合直接作为默认日常执行器。
- 如果要用，必须坚持 `impact_validate.py` 每一步都跑，不要相信模型自己的完成声明。

### 5. Step 3.7 Flash 能跑通，但更像备选

Step 3.7 Flash 的正面结果是：真实 `/impact` 能跑到 Phase 5，最后源码修改也正确。

它的问题是过程不够顺：

- 第一次容易停在 fast-track 分类后，需要提醒继续产 Phase 4 文档。
- preflight 和 source write 的顺序需要主线程明确压住。
- 曾暴露 Step 编号和恢复说明不一致。

它适合做备选模型，也适合作为“弱模型能不能被规则扶起来”的测试对象；但从日常体验看，不如 gpt-5.4-mini 和 M3。

### 6. GLM 5.1 质量能过，但执行成本过高

讯飞星辰通道的 GLM 5.1 实际模型标识是 `xopglm51[1m]`。它最终完成了同一个前端 Phase 5 场景，源码 diff 正确：

```diff
-      label: 'Dashboard',
-      title: 'Dashboard',
+      label: 'Insights',
+      title: 'Insights',
       key: '/dashboard',
```

但过程问题比较明显：

- Phase 4 约 12 分 41 秒，成本约 6.79 美元。
- preflight 约 6 分 48 秒，成本约 7.50 美元。
- Step 1 第一次在源码已改后撞到预算上限，未生成 `090-execution-record.md`。
- 追加收尾又撞一次预算，但最终补出了执行记录。
- 本地最终校验是 `16 passed, 0 failed, 1 warning`，warning 为 V4 判档表缺失。
- `_active-state.md` 里有过期的 Git 审计描述，且自报校验结果和主线程本地复验不一致。

它的主要问题不是代码改错，而是慢、贵、容易在“源码已改但记录未补齐”的中间状态停住。这个行为暴露的 V15 缺口已经修复：Git 仓库中如果源码/测试/配置已有 diff，但缺少 `090-execution-record.md` 或记录里没有源码写入 Step，validator 现在会直接 FAIL。

## 选型建议

### 日常小改动

优先：`gpt-5.4-mini`

理由：五项目矩阵证据最完整，成本和稳定性更均衡。适合常见 light 变更、Pathfinder 摸底、Impact 分析和低风险代码修改。

### 风险更高的已有系统变更

优先：`MiniMax-M3`

理由：当前真实 `/impact` Phase 5 流程质量最好。适合更看重流程稳定、写入边界和文档一致性的任务。

### 预算敏感或备选执行

可选：`step-3.7-flash`

理由：能完成，但需要更明确的提示和主线程监督。

### 压力测试门禁

可选：`deepseek-v4-flash`

理由：它能暴露状态漂移这类真实问题，适合检验门禁是否足够硬。不建议作为默认执行器。

### 不建议默认使用

暂不推荐：`xopglm51[1m]`

理由：最终源码可以改对，但完成同一个小型 Phase 5 任务的耗时和成本都偏高，而且需要额外收尾才能补齐执行记录。它适合偶尔做对照实验，不适合日常小步快跑。

暂不推荐：`Composer 2.5 / Composer 2.5 Fast`

理由：流程遵守不错，但真实代码验收失败。CLI 和 Cursor GUI 两条链路都只改了 `meta.label`，漏掉同对象 `meta.title`，旧 validator 全绿但用户验收不通过。v5.6 的 V17 已能拦住这个失败产物，但模型本身不适合默认托管日常写入。

暂不推荐：`xopkimik26`

理由：代码语义能做对，但门禁失败后的自救行为不稳。它没有定位到 V13 误伤点，反复改执行记录后越界写入 `debug_v13.py`。v5.6 的 V15 已能拦住这类未记录源码类 diff，但模型不适合默认执行器。

## 评分口径

后续如果要把结论数字化，建议不要只打一个总分，而是拆成五项：

| 维度 | 含义 |
|---|---|
| 流程遵守 | 是否按 Pathfinder / Impact 阶段执行，是否提前写文件 |
| 门禁通过 | `pf_validate.py` / `impact_validate.py` 是否通过，失败后能否修正 |
| 代码准确性 | 最终 diff 是否只改需求范围内的内容 |
| 证据可靠性 | 是否编造路径、行号、接口、DB、权限或测试结论 |
| 自主推进 | 是否需要主线程频繁提醒继续下一步 |

其中 `代码准确性` 和 `门禁通过` 权重应最高。弱模型只要最后代码越界，再会写文档也不能算好。

## 仍然不能证明的事

- M3 / DeepSeek / Step 的 Phase 5 样本目前都是前端文案修改，还没有覆盖 DB/API/权限/测试联动写入。
- GLM 5.1 这轮同样只覆盖前端文案修改，不能代表复杂 full 变更能力。
- 前端 fixture 没有安装 `node_modules`，所以 `npm run lint` / `npm run build` 只能证明环境缺依赖，不能证明构建通过。
- Codex Desktop 的真实 slash dispatcher 本轮没有直接工具可测；已证明的是 Claude Code CLI 的真实 slash command。
- Kimi K2.6 已有 xopkimik26 Phase 5 样本，但只覆盖前端文案修改；复杂 full 变更能力仍未验证。

## 下一步建议

1. 把 MiniMax M3 和 DeepSeek V4 Flash 的完整执行记录各自归档成独立 run。
2. 给 M3 跑一个中等复杂度任务：前端展示文案 + 对应测试更新。
3. 再给 M3 / gpt-5.4-mini 各跑一个后端 API 响应字段变更，但不动 DB。
4. 最后再测一个真正 full 变更：DB schema + API + 前端 + 测试，确认弱模型在复杂链路下不会只改表面代码。

当前最稳妥的使用策略是：

> gpt-5.4-mini 负责日常默认执行；MiniMax M3 负责更重要的写入任务；DeepSeek V4 Flash 和 Step 3.7 Flash 继续作为门禁压力测试与备选执行器；GLM 5.1 暂时只作为对照样本。
