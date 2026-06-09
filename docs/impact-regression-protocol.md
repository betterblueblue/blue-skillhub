# Impact Skills 优化后回归复测协议

> 目的：每次 `impact` / `impact-pro` 完成规则、模板、profile、adapter 或 README 的重要优化后，都按同一套协议自动补做相关复测，避免只改文档、不验证真实行为。

## 适用范围

本协议适用于：

- `skills/impact/SKILL.md`
- `skills/impact/templates/*.md`
- `skills/impact/VALIDATION.md`
- `skills/impact-pro/SKILL.md`
- `skills/impact-pro/templates/*.md`
- `skills/impact-pro/profiles/*.md`
- `skills/impact-pro/db-adapters/*.md`
- `skills/impact-pro/VALIDATION.md`
- 两个 skill 的 README、验证索引和验收记录

纯错别字、链接修正、排版调整等不改变行为边界的修改，可以只跑 RG0 文档一致性检查。

## 核心原则

1. **优化后必须复测**：新增或修改一条规则，就至少覆盖它直接影响的场景。
2. **按风险分层，不每次全量**：小改跑最小回归包；安全门禁、判档、写操作或 profile 变化必须跑扩展包。
3. **真实 agent 复测保留为关键闸门**：涉及弱模型、长会话、Step 确认、写操作闭环、负向场景时，必须补真实 Claude Code / MiniMax M3 或等价真实 agent 对话记录。
4. **自动只读，写操作隔离**：复测可以自动做只读检查；任何写入测试项目的动作必须在隔离副本或临时 fixture 中执行。
5. **结果必须归档**：每轮复测必须写入对应 `validation-runs/`，并更新 `INDEX.md`。

## 触发矩阵

| 修改类型 | 必跑复测 | 可选复测 | 通过标准 |
|----------|----------|----------|----------|
| README / 描述 / 致谢 | RG0 文档一致性检查 | 无 | 无矛盾定位、无旧版本结论、链接有效 |
| light/full 判档规则 | RG1 判档回归 | RG3 真实 agent 复测 | 简单场景不过度 full，高风险场景不得 light |
| 苏格拉底提问规则 | RG1 提问回归 | RG3 真实 agent 复测 | 每轮不超过 3 问，但可多轮收敛；问题来自证据 |
| Context Pack / 引用检查 | RG1 上下文回归 | RG2 多栈回归 | L1/L2/L3、相关性、引用分级、排除项完整 |
| 接口返回检查清单 | RG1 响应契约回归 | RG3 M3 复测 | 新增字段可 light；删除/重命名/消费者不明必须 full 或补证据 |
| V0-V3 验证等级 | RG1 验证等级回归 | RG3 M3 复测 | 静态检查为 V1；不可把未运行写成 V2/V3 |
| Step 确认 / 阻塞恢复 | RG1 门禁回归 | RG3 长会话复测 | 模糊确认无效；延迟确认后先复核 Step 和文件状态 |
| Phase 5 / 写操作闭环 | RG2 执行闭环回归 | RG3 真实写操作复测；涉及多会话/长目标/写入目标边界时按 `docs/impact-multisession-write-gate-test-plan.md` 执行 | 有 preflight、确认、执行记录、验证等级、回滚方式；写入对象位于目标项目根目录内 |
| `impact-pro` profile 修改 | RG2 对应栈 full + light | RG3 弱模型复测 | profile 命中正确；generic 降级诚实；验证命令来自项目证据 |
| DB adapter 修改 | RG2 DB 场景回归 | RG3 生产级复验 | 无 DB 权限时降级；不得编造表结构、索引或影响行数 |

## 回归包定义

### RG0：文档一致性检查

每次修改后都必须执行：

```powershell
git diff --check
rg -n "T01-T45|T01-T46|真实写操作闭环待后续|response contract checklist|证据账本|evidence ledger" README.md skills/impact skills/impact-pro docs --glob "!docs/impact-regression-protocol.md"
```

检查项：

- 根 README、skill README、VALIDATION 和 validation index 的结论一致。
- 不出现旧版本验收范围，例如已经有 T47 但仍写 T45 为最新。
- 不出现生硬或未统一的术语。
- 新验证记录已加入对应 `validation-runs/INDEX.md`。

### RG1：规则定向回归

当优化影响规则或模板时执行。至少覆盖：

- `impact`：长期目标、接口返回检查、V0-V3、非 Git 降级、阻塞恢复、Step 范围一致、验证命令证据。
- `impact-pro`：Node/Express 响应字段删除、profile 识别、full 判档、消费者/OpenAPI/generated client 未确认处理、V1/V3 区分。

通过标准：

- 相关规则能在输出中明确触发。
- 未确认项写成“不确定/需确认”，不得编造。
- 只读分析可写 V1，但不得写成 V2/V3。
- 没有 `确认 Step N` 不得执行写操作。

### RG2：扩展场景回归

当修改 profile、adapter、Phase 5 或跨 skill 共用规则时执行。至少选择受影响最大的 2-3 类场景：

- Java/RuoYi 或 Java/MyBatis full + light。
- Node/Express/Prisma full + light。
- FastAPI/SQLModel full + light。
- Go/Gin/GORM full + light。
- React/Vite、Next.js 或 Nuxt/Vue 前端 light/full 判档。
- monorepo 主/辅 profile 边界。
- DB 无权限、破坏性请求、证据不足等负向场景。

通过标准：

- 平均分不低于 85。
- 无未修复 P0/P1。
- 涉及写操作时必须在隔离副本完成 preflight、Step 确认、执行记录和验证等级。

### RG3：真实 agent / 弱模型复测

出现下列任一情况必须执行：

- 优化目标就是修复真实 agent 对话中暴露的问题。
- 涉及 MiniMax M3、GLM、Kimi 等相对弱模型稳定性。
- 涉及长会话、上下文压缩、blocked 恢复、延迟确认。
- 涉及写操作闭环、测试失败修复、DDL/DML、配置变更。
- 涉及写入目标边界、多会话授权一致性或连续 V1-only 写入，按 [impact-multisession-write-gate-test-plan.md](impact-multisession-write-gate-test-plan.md) 补独立 subagent 复测。
- 涉及负向场景：破坏性请求、证据不足、非目标技术栈误判。

推荐做法：

- 将当前 repo skill 复制到真实客户端 skill 目录。
- 在隔离 fixture 或隔离项目副本中触发 `/impact` 或 `/impact-pro`。
- 记录完整对话输出、命令、模型、版本、测试目录和结论。
- 不把外部项目代码写入本仓库，只归档复测摘要和可公开的 fixture 说明。

通过标准：

- 真实 agent 没有绕过 Step 级确认。
- 真实 agent 没有把未知证据写成已确认。
- 真实 agent 能触发本次优化所要求的规则。
- 若首次失败，必须记录失败原因、修复项和复测结果。

## 复测记录格式

每次复测新增一份文件：

```text
skills/{impact|impact-pro}/validation-runs/YYYY-MM-DD-Txx-短名称.md
```

内容模板：

```markdown
# Txx: [复测名称]

日期：

## 触发原因

- 本轮优化了什么：
- 为什么需要复测：

## 环境

- Agent：
- 模型：
- 触发方式：
- 测试目录：
- 结果文件：

## 用例

| 场景 | 预期 | 实际 | 结论 |
|------|------|------|------|

## 发现的问题

1. 问题：
   - 影响：
   - 修复：
   - 复测：

## 结论

- 通过 / 有条件通过 / 不通过
- P0/P1：
- 后续风险：
```

写完后必须更新：

- `skills/impact/validation-runs/INDEX.md` 或 `skills/impact-pro/validation-runs/INDEX.md`
- 对应 `VALIDATION.md` 的当前结论或当前改进建议
- 如果影响用户理解，再更新 README

## 自动化边界

这里的“自动复测”不是指 agent 可以无人监督写生产项目，而是指：

- 只读检查、文档一致性扫描、静态规则检查可以在优化后自动执行。
- 真实 agent 对话复测可以由当前 agent 主动委派或启动，但必须使用隔离 fixture。
- 写操作、DDL/DML、配置变更、测试修复仍然必须遵守 `确认 Step N`，即使发生在测试项目中也要记录确认来源。
- 如果没有 Claude Code、Docker、Java、Node、数据库等运行环境，记录为环境限制，不得把未运行写成通过。

## 后续优化时的默认动作

以后只要出现“优化 impact / impact-pro / 规则 / 模板 / profile / adapter”的任务，执行 agent 应默认做以下动作：

1. 判断修改类型，选择 RG0-RG3 回归包。
2. 修改前记录预期影响面。
3. 修改后自动跑 RG0。
4. 按触发矩阵补 RG1/RG2/RG3。
5. 写入 validation record 并更新 index。
6. 在最终回复里说明：跑了哪些复测、哪些没跑、原因是什么、是否有 P0/P1。
