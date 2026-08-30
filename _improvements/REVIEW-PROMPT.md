# 复盘引导词(REVIEW PROMPT)

> **使用方式**:一个项目的意图链路(intent-anchor → … → intent-verify / intent-adversarial)完整跑完之后,新开一个会话(或回到原会话),把下方引导线之间的内容完整粘贴进去。这个会话负责执行全循环的「回流 + 再优化」两段。

---

## 复盘会话引导词(复制以下全部内容)

上一个项目刚跑完意图链路。现在执行 Skill 体系的复盘与回流,步骤如下:

**1. 验证回流**:读 `blue-skillhub/_improvements/verification-cards.md`(6 张验证任务卡)。如果项目会话已按 VALIDATION-PROMPT 执行了各卡验证,汇总其结果;否则现在补验——按各卡步骤对项目实测(不是只看文档),重点:

- 卡 1(anchor):INTENT 第 17 节是否产出、行数与源材料页数一致、CC 表是否与用户确认
- 卡 2(issues):真值追溯表是否存在、V13 是否 PASS、抽查 3 行映射内容
- 卡 4(adversarial):六类攻击是否全覆盖、SF/CC 逐条关联、并发是否真并发、对"防御成功"用例抽验攻击构造真实性
- 卡 5(verify):页面走查是否逐页真点、缺陷闭环是否走完(FIX-* → 修复 → 定向复验)
- 卡 7(impact):高风险请求是否被拦(write-gate/确认制)、090 回归验证是否按 R2-IMP1 记录(V25)
- 卡 8(pathfinder):只读边界是否守住、Script Gate 是否拦缺 facts、可信度抽验

**2. 系统测试(若项目尚未跑过)**:按项目形态执行安全审计(越权矩阵/业务逻辑攻击/暴力破解)与性能测试(数据放大→基准→并发压测+一致性断言),方法论底稿见 `blue-skillhub/_improvements/README.md` 资产表;发现的缺陷走 FIX-* 工单 → 修复 → 定向复验。

**3. 新问题复盘**:把本次暴露的 SKILL/校验器自身问题登记为 backlog(新建 `YYYY-MM-DD-<项目>-backlog.md` 或追加已有文件),每条带实测证据,按归因三分类(校验器缺口 / SKILL 指引不够 / Agent 违反指引)标注。

**4. 状态更新**:更新 `blue-skillhub/_improvements/STATUS.md`——新问题以 `R{轮次}-{编号}` 登记;历史条目按验证结果流转(fixed → verified;复发 → regressed);追加归因分布趋势一行。

**5. 优化执行**:按归因直接修复——校验器缺口和 Agent 违反 → 下沉校验器规则(P0,改 `_common/*.py` 或各 skill `scripts/*.py`,并在对应 tests/ 补正反例);SKILL 指引不够 → 改 SKILL/模板/底稿(P1)。修复引用 git commit hash。

**纪律**:修复后必须回归(跑对应校验器的既有测试 + 新用例);验证报告与 backlog 的结论要有实测证据,不接受"应该没问题"。

---

## 复盘会话结束的标志

- `verifications/` 新增本项目验证报告,STATUS.md 已更新(含归因趋势行)
- 新问题已登记 backlog,已修复项引用了 commit hash
- 全部校验器测试通过;若本轮改了校验器,用下个项目(或历史项目)回归验证了拦截行为
