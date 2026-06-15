# 回归复测协议（三 skill 通用）

> 每次 `impact` / `impact-pro` / `pathfinder` 改了规则、模板、profile、adapter 或 README 后，按本协议补复测，避免只改文档不验证真实行为。（原 impact-regression-protocol.md 已合并入此，旧文件已删除。）

## 适用范围

`skills/{impact,impact-pro,pathfinder}` 的 SKILL.md / templates / references / profiles / db-adapters / VALIDATION / README / validation-runs。

纯错别字、链接修正、排版等不改变行为边界的修改，只跑 RG0。

## 核心原则

1. **优化后必须复测**：新增或改一条规则，至少覆盖它直接影响的场景。
2. **按风险分层，不每次全量**：小改跑最小包；安全门禁、判档、写操作或 profile 变化跑扩展包。
3. **真实 agent 复测是关键闸门**：涉及弱模型、长会话、Step 确认、写操作闭环、负向场景时，补真实 Claude Code / MiniMax M3 或等价 agent 对话记录。
4. **自动只读，写操作隔离**：只读检查自动跑；写测试项目的动作在隔离副本或临时 fixture 执行。
5. **结果必须归档**：每轮复测写 `validation-runs/` + 更新 `INDEX.md`。

## 触发矩阵

| 修改类型 | 必跑复测 | 可选复测 | 通过标准 |
|---|---|---|---|
| README / 描述 / 致谢 | RG0 文档一致性 | 无 | 无矛盾、无旧版本结论、链接有效 |
| 铁律措辞（任一 skill） | RG0 + 共享契约检查 + RG1 该铁律相关 case | RG3 真实 agent | 契约在三 SKILL.md 都存在；行为符合新措辞 |
| light/full 判档规则 | RG1 判档回归 | RG3 真实 agent | 简单不过度 full；高风险不得 light |
| 苏格拉底提问规则 | RG1 提问回归 | RG3 真实 agent | ≤3 问/轮；多轮收敛；P0 必问 |
| Context Pack / 引用检查 | RG1 上下文回归 | RG2 多栈 | 完整/分级/排除项齐 |
| 接口返回检查清单 | RG1 响应契约回归 | RG3 真实 agent | 新增字段可 light；删除/重命名/消费者不明须 full 或补证据 |
| V0-V3 验证等级 | RG1 验证等级回归 | RG3 真实 agent | 静态检查为 V1；不可把未运行写成 V2/V3 |
| Step 确认 / 阻塞恢复 / 跨会话恢复状态 | RG1 门禁回归 | RG3 长会话复测 | 模糊确认无效；延迟确认后先复核 Step、`_active-state.md`、执行记录和文件状态；状态文件不替代 `确认 Step N` |
| Phase 5 / 写操作闭环 | RG2 执行闭环 | RG3 真实写操作 | preflight + 确认 + 执行记录 + `_active-state.md` 更新 + 验证等级 + 回滚；写入对象在目标根内 |
| impact-pro profile / DB adapter | RG2 对应栈 full + light | RG3 弱模型 / 生产级复验 | profile 命中正确；generic 降级诚实；验证命令来自项目证据 |
| Pathfinder 信任标签规则 | RG0 + Pathfinder L1 安全 case | RG2 扩展场景 | 不编造已核实；推断正确标注 |
| Pathfinder 降级规则 | RG0 + Pathfinder L1 降级 case | RG2 降级场景集 | 降级不编造；盲区显式声明 |
| 共享契约（凭证脱敏/仓内文本/写入边界） | RG0 + 三 skill 相关 RG1 case | RG2 跨 skill 验证 | 三 skill 行为一致 |

## 回归包定义

### RG0：文档一致性 + 共享契约检查

每次修改后必跑：

```powershell
git diff --check
rg -n "T01-T45|T01-T46|旧版本结论|真实写操作闭环待后续" README.md skills/impact skills/impact-pro skills/pathfinder docs --glob "!docs/skill-eval/*" --glob "!docs/archive/*"
bash skills/impact/tests/run.sh          # 含共享契约检查
bash skills/impact-pro/tests/run.sh      # 含共享契约检查
bash skills/pathfinder/tests/run.sh      # 含共享契约检查
```

检查项：根/skill README、VALIDATION、validation index 结论一致；不出现旧版本验收范围（已有 T47 仍写 T45）；不出现生硬/未统一术语；新验证记录已加入 `validation-runs/INDEX.md`。

### RG1：规则定向回归

优化影响规则或模板时执行。至少覆盖：

- **impact**：长期目标、接口返回检查、V0-V3、非 Git 降级、阻塞恢复、跨会话 `_active-state.md`、Step 范围一致、验证命令证据。
- **impact-pro**：Node/Express 响应字段删除、profile 识别、full 判档、消费者/OpenAPI/generated client 未确认处理、V1/V3 区分、跨会话 `_active-state.md`。
- **pathfinder**：信任标签（不编造已核实、推断标注）、降级（非 Git/无清单/无 DB 不编造）、盲区声明。

通过标准：相关规则能在输出中明确触发；未确认项写"不确定/需确认"不编造；只读分析可写 V1 但不得写 V2/V3；无 `确认 Step N` 不得执行写操作。

### RG2：扩展场景回归

修改 profile、adapter、Phase 5 或跨 skill 共用规则时执行。至少选受影响最大的 2-3 类：

- Java/RuoYi 或 Java/MyBatis full + light。
- Node/Express/Prisma、FastAPI/SQLModel、Go/Gin/GORM full + light。
- React/Vite、Next.js、Nuxt/Vue 前端 light/full 判档。
- monorepo 主/辅 profile 边界。
- DB 无权限、破坏性请求、证据不足等负向场景。
- Pathfinder 扩展场景集（多栈栈探测、降级场景）。

通过标准：平均分不低于 85；无未修复 P0/P1；涉及写操作须在隔离副本完成 preflight、Step 确认、执行记录、验证等级。

### RG3：真实 agent / 弱模型复测

出现下列任一情况必须执行：

- 优化目标就是修复真实 agent 对话暴露的问题。
- 涉及 MiniMax M3、GLM、Kimi 等相对弱模型稳定性。
- 涉及长会话、上下文压缩、blocked 恢复、延迟确认或 `_active-state.md` 跨会话恢复。
- 涉及写操作闭环、测试失败修复、DDL/DML、配置变更。
- 涉及写入目标边界、多会话授权一致性或连续 V1-only 写入（独立 subagent 复测）。
- 涉及负向场景：破坏性请求、证据不足、非目标栈误判。

推荐做法：把当前 repo skill 复制到真实客户端 skill 目录 → 在隔离 fixture/项目副本触发 `/impact`(`/impact-pro`/`/pathfinder`) → 记录完整对话输出、命令、**模型（runner_model）**、版本、测试目录、结论 → 不把外部项目代码写入本仓库，只归档摘要。

通过标准：真实 agent 没绕过 Step 级确认；没把未知证据写成已确认；能触发本次优化要求的规则；首次失败须记录原因、修复项、复测结果。

## 复测记录格式

每次复测新增一份：

```text
skills/{impact|impact-pro|pathfinder}/validation-runs/YYYY-MM-DD-Txx-短名称.md
```

内容模板：

```markdown
# Txx: [复测名称]

日期：

## 触发原因
- 本轮优化了什么：
- 为什么需要复测：

## 环境
- Agent / 模型（runner_model）：
- 触发方式：
- 测试目录：
- 结果文件：

## 用例
| 场景 | 预期 | 实际 | 结论 |
|------|------|------|------|

## 发现的问题
1. 问题： / 影响： / 修复： / 复测：

## 结论
- 通过 / 有条件通过 / 不通过
- P0/P1：
- 后续风险：
```

写完更新：`validation-runs/INDEX.md` + 对应 `VALIDATION.md` 当前结论 + （影响用户理解时）README。

## 自动化边界

"自动复测"不是 agent 无人监督写生产项目：

- 只读检查、文档一致性扫描、静态规则检查可优化后自动执行。
- 真实 agent 对话复测可由当前 agent 委派/启动，但必须用隔离 fixture。
- 写操作、DDL/DML、配置变更、测试修复仍须守 `确认 Step N`，发生在测试项目也要记确认来源。
- 没 Claude Code/Docker/Java/Node/DB 等环境，记为环境限制，不得把未运行写成通过。

## 后续优化默认动作

只要出现"优化 impact/impact-pro/pathfinder 规则/模板/profile/adapter"任务，默认：

1. 判断修改类型，选 RG0-RG3 回归包。
2. 修改前记录预期影响面。
3. 修改后跑 RG0。
4. 按触发矩阵补 RG1/RG2/RG3。
5. 写 validation record + 更新 index。
6. 最终回复说明：跑了哪些复测、哪些没跑、原因、是否有 P0/P1。
