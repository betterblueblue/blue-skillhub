# Impact / Pathfinder 分支审查 Backlog

> 复盘日期:2026-08-30
> 来源:租衣摄影项目复盘后的延伸审查——intent 链路(0→1 路径)修复 20 项后,用同一副眼镜(五层框架:执行断层/真值锚定/验证深度/缺陷闭环/结构)审视已有系统迭代分支的 impact + pathfinder。
> 审查方式:通读两个 SKILL 全文、impact_validate.py(V1-V10,3207 行)、impact-write-gate.py hook、pathfinder 硬性规则与 Script Gate;参考租衣项目实战教训(超卖/越权/页面走查逃逸)。

## 先说正面(与 intent 链路改进前的对照)

impact/pathfinder 的机制成熟度整体**高于** intent 链路改进前,本轮 intent 侧修复的多个问题在这里**已经有对应物**。特别值得肯定的三点:① impact 的写操作门禁是**确认制 + 消费制**(`确认 Step N` 一次性消费,模糊确认/合并确认全部无效),比 intent 链路的文字规则硬;② pathfinder 的 FACTS 层用**脚本产出确定性事实**(scan.json/git.json),真值锚定方式比 intent 链路的纯 Agent 产物先进;③ 两个 skill 都有「改进记录提示」——自我改进意识在源头就存在,只是没有接入统一回流载体(见 R2-IMP2)。

**没有** intent 链路那种「verify 从未运行却呈现完成」的问题——impact 的完成被 Step 确认制和校验器锁住。

| intent 链路本轮修复的 | impact/pathfinder 的既有对应物 |
|---|---|
| 校验器硬拦 | impact_validate.py(V1-V10,3207 行,含凭证脱敏/行号抽查/判档一致性)、pf_validate.py(Script Gate)、write-gate hook(opt-in,`.impact-protected` 标记 + `确认 Step N` 消费制) |
| 门禁制 | Phase 4/5 分步门禁(强制规则 11)、高风险拦截清单(强制规则 2)、写入前置检查(规则 8/9) |
| 锚定 | 苏格拉底问题格式强制(规则 13:带依据的选择题)、FACTS 确定性事实层(pathfinder Phase 1.5)、可信度强制标注 |
| 验证声明规范 | 规则 14「验证声明必须附原始输出」、收尾使用记录(含「门禁是否拦住」「值得沉淀的改进」字段) |

**没有** intent 链路那种「verify 从未运行却呈现完成」的问题——impact 的完成被 Step 确认制和校验器锁住。

## 缺口(2 项)

### - [x] R2-IMP1 impact 执行后缺「风险驱动的对抗回归」门禁
- **证据**:impact Phase 5 的验证方式由每个 Step 自行定义(「验证方式」字段);SKILL 全文无「安全回归」「并发一致性」概念。租衣实战教训:库存原子化超卖正是"已有系统迭代改下单逻辑"引入的缺陷类型——若有人用 impact 迭代下单/支付/权限类代码,Step 验证大概率写"跑既有单测",并发一致性与安全回归不在默认视野。intent 链路本轮已新增 intent-adversarial 环节,但只挂在 0→1 交付前,**迭代路径改完代码后没有对应的对抗回归关卡**——两条路径在这里不对称。
- **影响**:高风险 Step(权限/支付/库存/数据迁移)执行后,引入的并发竞态与安全回归无机制保证被发现。
- **修复落点(修订 v2,原方案"复用 intent-adversarial 全套模板"过重,弃)**:impact SKILL Phase 5 增加「风险分级定向回归」规则——**按改动命中类型选回归维度,不全跑**:
  - **基线(所有写类 Step)**:项目已有测试全过 + 改动行为有对应测试(软件开发基本功,一句话规则)
  - **定向(命中高风险清单才加)**:改权限/角色/enum → 越权抽测(双身份横向矩阵抽 2-3 条);改支付/库存/名额等并发资源 → 并发一致性断言(超卖=0、重复提交拒绝,几行脚本而非全套流程);改 API 契约/公共导出 → 消费者清单逐个验证;涉及数据迁移 → 数据校验+回滚演练
  - **全套(罕见)**:仅系统级大改(新认证体系/新支付通道)才值得跑完整 adversarial 流程
  - 落地形式:高风险拦截清单(强制规则 2)旁加一张「回归维度镜像表」;090-execution-record.md 增加回归结果字段。CC 断言用例可参考 intent-adversarial 的写法,但不要求全套流程
- 状态:- [ ] 待办

### - [x] R2-IMP2 使用记录与改进沉淀未接入 _improvements 回流闭环
- **证据**:impact/pathfinder 的收尾使用记录「只输出在对话里,不默认写文件」;两者各有的「改进记录提示」节与 _improvements 的验证闭环(VALIDATION-PROMPT / REVIEW-PROMPT / STATUS / 验证卡)是**两套并行机制,互不引用**。verification-cards.md 的 6 张卡全部针对 intent 链路环节,impact/pathfinder 零覆盖。
- **影响**:两个 skill 的实战缺陷(「值得沉淀的改进」字段收集的东西)没有回流载体;_improvements 的归因趋势统计看不到这两个 skill 的健康度;下一个项目即便贴了 VALIDATION-PROMPT,也不会验证 impact/pathfinder 本身。
- **修复落点**:① impact/pathfinder SKILL 的「改进记录提示」节改为:沉淀项登记到 `blue-skillhub/_improvements/`(按归因三分类);② verification-cards.md 增加**卡 7(impact)**与**卡 8(pathfinder)**——卡 7 验证 Step 确认制/高风险拦截/write-gate 是否真实拦截(构造高风险请求实测)、卡 8 验证 Script Gate/可信度标注/只读边界(尝试让 Agent 写项目源码,应拒绝);③ REVIEW-PROMPT 补验清单同步增加两个 skill。
- 状态:- [ ] 待办

### 观察(不立条目)

- pathfinder 相对健全:只读边界 + Script Gate + 可信度强制 + 刷新机制,风险天然低于写操作链路;真值锚定(FACTS 脚本产出确定性事实)的设计甚至优于 intent 链路的纯 Agent 产物。
- impact_validate 的 V 系列聚焦文档阶段(000-030);执行阶段(060/090/_active-state)无校验——但 Phase 5 被逐步确认制和 write-gate 覆盖,校验需求低,暂不立条目。
- V5 凭证脱敏为 WARN 级(正则无法区分真实凭证与示例)——SKILL 已强制人工复核,可接受。

### 观察(不立条目)

- pathfinder 相对健全:只读边界 + Script Gate + 可信度强制 + 刷新机制,风险天然低于写操作链路;真值锚定(FACTS 脚本产出确定性事实)的设计甚至优于 intent 链路的纯 Agent 产物。
- impact_validate 的 V 系列聚焦文档阶段(000-030);执行阶段(060/090/_active-state)无校验——但 Phase 5 被逐步确认制和 write-gate 覆盖,校验需求低,暂不立条目。
- V5 凭证脱敏为 WARN 级(正则无法区分真实凭证与示例)——SKILL 已强制人工复核,可接受。
- **write-gate hook 是 opt-in 且绑定 Claude Code**:需项目根有 `.impact-protected` 标记 + 客户端支持 PreToolUse hook。非 Claude 客户端运行 impact 时,hook 不存在,写门禁只剩 SKILL 文字的逐步确认制——跨平台执行节建议明示这一边界。

## 结论

impact/pathfinder **没有** intent 链路那种程度的结构断层(门禁制、重型校验器、攻击拦截清单、消费制确认都已具备,部分设计优于 intent 侧),真实缺口只有 2 个:① 迭代路径改完代码后缺风险驱动的定向回归(R2-IMP1,超卖教训的镜像);② 使用记录与改进沉淀未接入统一回流闭环(R2-IMP2)。两项均为 P1,与 intent-adversarial 用例模板一起改性价比最高。

## 实施优先级

| 批次 | 内容 | 说明 |
|---|---|---|
| P1 | R2-IMP1 风险驱动回归门禁 | 超卖教训的镜像,建议与 intent-adversarial 用例模板一起改 |
| P1 | R2-IMP2 回流接入 + 卡 7/卡 8 | 与 _improvements 验证闭环打通 |

## 修复记录

### 2026-08-30 · R2-IMP1/R2-IMP2 完成

- **R2-IMP1**:`impact/SKILL.md` Phase 5 加「风险分级定向回归」(基线+定向维度,镜像高风险拦截清单);`templates/090-execution-record.md` 加「回归验证」节;`impact_validate.py` 新增 V25(缺基线记录 FAIL、写类 Step 缺节 WARN、高风险维度未记录 WARN)。
- **R2-IMP2**:impact/pathfinder 的「改进记录提示」改指 `_improvements`(归因三分类);验证卡补卡 7(impact)/卡 8(pathfinder);REVIEW-PROMPT 补验清单同步。
- **回归**:impact 全量 104 测试全过(含新增 V25 用例 4 项)+ pathfinder 35 项全过。
