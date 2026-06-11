# T04: Claude Code + MiniMax M3 真实 /impact 复测

日期：2026-06-08

## 目的

验证本轮针对真实使用案例补强的 `impact` 规则是否有效，并检查是否引入新的问题。

覆盖能力：

- 长期目标模式
- 源系统到目标系统对齐
- 接口返回检查清单
- V0-V3 验证等级
- 非 Git 项目降级保护
- 阻塞恢复安全闸
- Step 范围一致
- 验证命令必须来自项目证据

## 环境

- Agent：Claude Code CLI 2.1.167
- 模型：当前 Claude Code 配置的 MiniMax M3
- 触发方式：真实 Claude Code Skill 调用，命令 `/impact`
- 测试目录：`E:\agent\impact-m3-skill-test`
- 结果文件：
  - `E:\agent\impact-m3-skill-test\results\T1-real-slash-impact-long-parity.txt`
  - `E:\agent\impact-m3-skill-test\results\T1R-real-slash-impact-long-parity-after-fix.txt`
  - `E:\agent\impact-m3-skill-test\results\T3-real-slash-impact-blocked-recovery.txt`
  - `E:\agent\impact-m3-skill-test\results\T3R-real-slash-impact-blocked-recovery-after-fix.txt`
  - `E:\agent\impact-m3-skill-test\results\T4-real-slash-impact-step-scope-consistency.txt`
  - `E:\agent\impact-m3-skill-test\results\T5-real-slash-impact-write-closure.txt`
  - `E:\agent\impact-m3-skill-test\results\T5R-real-slash-impact-write-closure-after-fix.txt`

## 样本

非 Git 隔离项目：

- 源实现：`parity-source/app/chat.py`
- 目标实现：`parity-target/src/main/java/demo/chat/ChatOrchestrator.java`
- 进度文档：`parity-target/GT rag变更内容.md`

任务模拟：根据进度文档继续把 Python chat payload 行为迁移/对齐到 Java。

## 结果

| 场景 | 预期 | 结果 |
|------|------|------|
| T1 长期对齐任务 | 触发长期目标模式，产出可信来源/目标实现/对齐语义/差距证据 | 通过 |
| T1 接口返回字段新增 | 消费者/OpenAPI/generated client 不明时，不得正式建议 light | 首轮失败，T1R 修复后通过 |
| T1 验证等级 | 只读静态对照应标 V1，运行时未执行单独说明 | 首轮失败，T1R 修复后通过 |
| T1 非 Git 降级 | 说明无法 git 审计，要求 before/after、hash、备份或用户接受风险 | 通过 |
| T3 阻塞恢复 | 延迟确认后先复核；只读测试中应写“确认有效但本轮不执行” | 首轮表述含混，T3R 修复后通过 |
| T4 Step 范围一致 | 前文写不新增方法时，后文不得新增 helper；确需 helper 必须纳入 Step | 修复后通过 |
| T5 写操作闭环 | 隔离副本中执行写操作后，必须有备份、验证等级、执行记录 | 首轮失败，T5R 修复后通过 |

## 发现并修复的问题

1. **消费者不明仍建议 light**
   - 现象：T1 首轮在外部消费者不明时仍建议 light。
   - 修复：在 `SKILL.md` 中新增硬规则：不得一边写消费者/generated client/OpenAPI/SDK/持久化快照未确认，一边正式建议 light。

2. **只读静态分析被写成 V0**
   - 现象：T1 首轮已经做了字段对照，但当前最高验证等级写 V0。
   - 修复：新增说明：只读分析本身可达到 V1；未执行写操作应单独写“实施状态未执行”。

3. **阻塞恢复表述冲突**
   - 现象：T3 首轮同时写“无需重新确认”和“继续等待确认”。
   - 修复：新增说明：恢复检查通过且最新确认匹配时，写“确认有效但本轮不执行”；不得同时等待同一个确认。

4. **Step 范围前后不一致**
   - 现象：T1R 前文写不新增方法，后文计划新增 `getNested` helper。
   - 修复：新增 Step 范围一致规则；T4 复测通过。

5. **验证命令缺少项目证据**
   - 现象：T3R/T4 示例中出现 `mvn` 编译命令，但 fixture 没有 `pom.xml` 或 `mvnw`。
   - 修复：新增规则：验证命令必须来自真实项目入口；找不到时写 V2/V3 不可用，不得套用占位命令。

6. **写操作后没有执行记录却声称闭环完成**
   - 现象：T5 首轮在隔离副本中完成代码写入和备份，但没有创建 `090-execution-record.md`，仍声称“写操作闭环完成”。
   - 修复：新增规则：执行记录是 Phase 5 闭环的一部分；没有执行记录时只能写“执行记录未写，闭环未完成”。
   - 复测：T5R 通过，实际创建 `change-impact/T5R-rank-field/090-execution-record.md`，并记录非 Git 降级、hash、备份、V1、V2/V3 不可用。

## 剩余风险

- MiniMax M3 在长输出中仍可能夹带英文括注，如 `source of truth`。当前核心模板已改为中文“可信来源”，但模型偶发英文括注属于 P3 表达问题。
- 真实写操作闭环已用隔离副本做最小闭环验证；未覆盖复杂多文件/多 Step 写操作。

## 结论

本轮优化对 `impact` 有效：长期目标、跨系统对齐、接口返回检查、验证等级、非 Git 降级、阻塞恢复和最小写操作闭环均能在真实 `/impact` + MiniMax M3 下触发。

首次复测暴露的 6 个新问题已回补到 `SKILL.md` 与 `VALIDATION.md`。当前结论为：**只读分析、执行前安全门禁和最小写操作闭环通过；复杂多文件执行闭环需后续单独复测。**
