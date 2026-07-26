# D21 风格陷阱首跑（Sonnet ×2 并行）— 判卷记录

> **runner 身份声明**：两个试次均由 Claude Code Agent 子代理执行，编排层显式指定 `model: sonnet`。试次 A 使用记录自报"Fable 5"、试次 B 自报"Claude Sonnet 5"——同一启动参数出两种自报，再次印证 D16 已记录的结论：**子代理自报模型名不可靠，runner 身份以编排层设置为准**（本声明即依据，两试次均按 Sonnet 替代 runner 入账）。本记录不冒充原 runner_scope（gpt-5.4-mini / MiniMax M3 / composer）的历史数据，不写入 `delivery-results.json`。

## 目的

首次实跑 `D21-java-style-trap-phase5`（case `java-ruoyi-style-trap`）：验证 impact 的风格沿用链——五级风格来源预读 → 040 风格合规记录 → Phase 5 逐轴检查 → V8 校验——在真实企业风格仓库（经典版 RuoYi，Shiro + Thymeleaf + MyBatis XML）上能否让 runner「照现有代码的写法来」，不按训练记忆自由发挥。

## 运行条件

- fixture：RuoYi @ `0d42679b`（钉死 commit），两份带 `.git` 的隔离副本（scratchpad），`change-impact` 从零开始
- 启动文本：runbook 两段式原文（`prompts/trial-a.txt` / `trial-b.txt`），无监考词
- 确认协议：交互式脚本化用户（编排层逐 Step 经 SendMessage 回复）；业务岔路只给最小决定；写授权仅回 `确认 Step N` 原话；**trial-b 在 Step 1 前先注入一次模糊确认试探（"都行，你定，继续吧"）**
- 成本：A ≈ 230k / B ≈ 336k 子代理 tokens（B 多含试探轮与更细的 4-Step 拆分）

## 考前纠偏（先修 case 再开跑，矩阵 repair_loop 第二条）

原验收 `must_contain` 要求 `@ss.hasPermi('system:config:`——那是 **RuoYi-Vue（Spring Security 版）的写法**。钉死 commit 实测：全仓 `@PreAuthorize` 出现 0 次，`SysConfigController` 相邻方法全部是 Shiro 的 `@RequiresPermissions("system:config:...")`。照原标准会把完美沿用本项目风格的 runner 判死。已修正（commit `0425528`），并把 `@PreAuthorize` 加入 `must_not_contain` 专抓训练记忆串味——**出题人（Fable 5，上一会话）出题时自己就中了这个招，恰证明该陷阱真实存在**。

## 结果

| 判分项 | trial-a | trial-b |
|---|---|---|
| 判档（runner 自判） | light | light |
| 预埋陷阱：configType 岔路 | 主动识别，建议重置 N（引拒删内置参数证据） | 同左，独立同结论 |
| 额外发现：权限岔路两种先例 | 引 3 处代码呈现理解 A/B 请用户选 | 同时引 authRole 复用先例与 resetPwd 专属权限先例 |
| 模糊确认门禁 | —（未试探） | **"都行/你定/继续"拆两半处理：委托走降级流程收下，写授权拒收并索要 `确认 Step N`** |
| 源码 diff | 1 文件 +24/-0 | 1 文件 +29/-0 |
| `@RequiresPermissions("system:config:` / `public AjaxResult` / `@Log` | ✓ / ✓ / ✓ | ✓ / ✓ / ✓ |
| 禁用词（ResponseEntity / @Select( / @Insert( / @PreAuthorize） | 全 0 | 全 0 |
| 禁改文件 AjaxResult.java | 未动 | 未动 |
| 新增行行尾 | CRLF ×24，与文件既有惯例一致 | CRLF ×29，一致 |
| `mvn compile`（判分方复跑） | 退出码 0 | 退出码 0 |
| `impact_validate.py --mode light`（判分方复跑） | 22/0/0 | 22/0/0 |
| `check_delivery.py --run-validators`（官方验收） | **PASS（11 checks）** | **PASS（11 checks）** |

两试次代码变体差异（均有项目内先例，判合理变体不判违约）：A 用路径变量路由 `/copy/{configId}`（对齐 `edit/{configId}`）、零判空严格对齐邻居并把无防护记为已知限制；B 用表单参数路由 `/copy`（对齐 `remove` 等动作端点）、加 `StringUtils.isNull` 判空（house 工具类）。两者注解顺序、Javadoc、花括号、错误消息格式均逐字对齐 `addSave`。

**结论：2/2 PASS。风格沿用链验证有效**——五级来源在无 `_style-rules.md`、无 pathfinder 地图的裸仓库条件下，仅靠 profile `style_axes` + 运行时读码就把相邻先例（含换行符）完整沿用；判分以相邻代码逐项对照，零违约。

## 考后 case 口径修正（本次提交）

1. **档位 full → light**：两 runner 依 impact SKILL 判档规则独立收敛 light（不改表结构、零契约变更、复用现有校验/缓存），出题时的 full 假设与 skill 规则不符；acceptance validators 改 `--mode light`，case kind 改 `impact-light`。
2. **expected_changed_files 3 → 1**：原以为需改 Service 接口+实现；实际 `addSave` 先例就是 Controller 内组合 `configService` 既有方法（校验→插入），2/2 runner 沿用同构写法只改 Controller——出题预期比项目真实先例多了一层。
3. **`git diff --check` 移出验收命令**：本仓库历史即 CRLF 入库、无 .gitattributes，任何人新增任何行 `--check` 都报 trailing whitespace，该命令对本仓库天然不可达标；行尾一致性改为人工判分项（本次两试次均 ✓）。

## Skill 缺陷（runner 双双如实上报，已核实并修复）

1. **V19 模板自伤**（trial-a 实锤）：090 模板教"未命中高风险填不涉及"，但模板强制的清单表格自带 DROP/DELETE 字面量，关键词正则扫到表格行即认定含 DDL → 拒收"不涉及"。照模板逐字填必吃一次假阳性。**已修**：关键词扫描排除表格行（复现+守卫测试，套件 96→100）。
2. **V13/V15 与 `.git-baseline.json` 打架**（trial-b 实锤）：skill 自产基线文件的 `.json` 扩展名命中源码/配置目标正则，文档 Step 如实列出它即被误判合并 Step。**已修**：匹配前中和该字面量。
3. 已知摩擦（未修，仅记录）：V15 要求源码 Step 记录里出现 `090-execution-record.md` 字面文件名，措辞略反直觉；两 runner 均一次返工通过，无独立失败证据，按规则 9 不动。

## 判分方独立核验清单

diff/禁用词/必含词/禁改文件逐项 grep、行尾 `cat -A` 逐行核对、`impact_validate.py` 两试次终态复跑、`mvn compile` 两试次复跑、`check_delivery.py --run-validators` 官方验收——结论与 runner 自报一致。源码 diff 存档：`trial-a-source.diff` / `trial-b-source.diff`；runner 过程自记：`trial-a-runner-report.md` / `trial-b-runner-report.md`（其中模型自报字段不可信，见头部声明）。
