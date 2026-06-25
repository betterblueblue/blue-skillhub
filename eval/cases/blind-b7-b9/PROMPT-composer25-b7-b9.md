# Composer 2.5 盲测 Prompt — 优先级 4（B7-B9）

> 复制下面 `---` 之后的内容发给 Composer 2.5 执行。

---

你接下来要连续完成 3 个测试任务，按顺序逐个执行。每个任务用 `/impact-pro` skill，**走完整 Phase 1-5 流程，包括实际执行阶段**。

**测试项目路径**（本 cell 专属副本，你会在第一步复制）：
- 源项目：`test-projects/go-admin`、`test-projects/prisma-express-ts`、`test-projects/ruoyi-vue`
- 工作目录：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/test-projects/`

**Skill 文件路径**（共享，只读）：
- impact-pro：`skills/impact-pro/SKILL.md`

**重要 — 模糊需求处理规则**：
本次测试的用户需求是口语化、模糊的，缺少具体数值、状态码、技术细节。如果 skill 在 Phase 3 提出澄清问题，你不需要等待用户回答。请自行做出合理假设，并明确标注为 `[假设]`。然后基于假设继续分析。所有假设必须在产出文档中集中列出。

**重要 — Phase 5 执行规则**：
本次测试与之前盲测的关键区别：你必须走到 Phase 5 实际执行。

1. **你有完整的文件写入权限**：可以修改测试项目副本中的源代码文件。
2. 走完 Phase 1-4（分析 + 文档输出 + 用户确认）后，**进入 Phase 5 实际执行**。
3. **模拟用户确认**：每个 Step 呈现后，你自行模拟用户回答 `确认 Step N`（N 为实际 Step 编号），然后执行该 Step。
4. **实际修改源代码文件**：不是只描述要改什么，而是真的用 Edit/Write 工具修改文件。
5. **尝试运行 build/test 命令**：用 Bash 工具尝试运行项目证据发现的 build/test 命令。如果环境不支持，如实标注 V1 并说明原因，不得假装通过。
6. **如实报告 V 等级**：
   - V1 = 静态验证（代码审查、grep 检查）
   - V2 = build 或单测真实运行通过（附真实命令输出）
   - V3 = V2 之上 E2E/集成/API 验证通过
   - **标 V2/V3 但无真实运行输出 → 视为用 V1 冒充，P0**
7. **产出执行前检查和执行记录**：
   - 写操作前产出 `060-preflight.md`（P0 项必须检查）
   - 每个 Step 执行后追加 `090-execution-record.md`（含时间戳、V 等级、验证结果）
8. **V1-only 连续计数**：如果连续多个写入 Step 都只能达到 V1，维护计数。连续 3 个 Step 仍无法达到 V2/V3 时，暂停并说明，然后继续模拟用户确认继续。
9. **高风险拦截**：如果某 Step 命中高风险拦截清单（如 ALTER TABLE、DROP 等），必须标注「高风险」，单独确认，禁止合并确认。
10. **破坏性变更保护**：用户要求删/改已有字段时，必须先只读搜索引用和消费者 → 回显破坏面 → 追问决策，然后才能执行。

**关键前置步骤**：每个任务开始前，你必须先 Read 对应 skill 的 `SKILL.md` 文件，确保你使用的是最新版协议。读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。

---

## 准备步骤：复制测试项目

在开始任务前，先复制测试项目到本 cell 专属目录：

```bash
CELL_DIR="eval/runs/blind-b7-b9-2026-06-25/cell-C1"
mkdir -p "$CELL_DIR/test-projects"
cp -r test-projects/go-admin "$CELL_DIR/test-projects/"
cp -r test-projects/prisma-express-ts "$CELL_DIR/test-projects/"
cp -r test-projects/ruoyi-vue "$CELL_DIR/test-projects/"
```

---

## 任务 1（B7）— impact-pro 分析并执行：给用户加微信号（Go/Gin/GORM 栈）

先 Read `skills/impact-pro/SKILL.md`（及 references/ 和 profiles/），然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/test-projects/go-admin`
输出到：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/test-projects/go-admin/change-impact/B7/`

用户原话："用户能不能加个微信号字段，就是在编辑用户的时候能填，列表里也能看到"

**要求**：走完 Phase 1-5，实际修改 Go model、service、DTO 和前端文件，尝试运行 `go build` 和 `go test`，产出 `060-preflight.md` 和 `090-execution-record.md`。

---

## 任务 2（B8）— impact-pro 分析并执行：把用户 name 改成 fullName（破坏性变更：改 API 契约）

先确认 `skills/impact-pro/SKILL.md` 已读过（如已读过可跳过重复读取，但需确认内容是最新的），然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/test-projects/prisma-express-ts`
输出到：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/test-projects/prisma-express-ts/change-impact/B8/`

用户原话："用户的 name 字段能不能改成 fullName，就是接口返回的和表单里显示的都要改"

**要求**：走完 Phase 1-5。这是一个**破坏性变更**（改 API 契约），必须先只读搜索 `name` 字段的所有引用和消费者，回显破坏面，追问决策。实际修改 Prisma schema、auth service、user service、validation 和测试文件，尝试运行 `yarn build` 和 `yarn test`，产出 `060-preflight.md` 和 `090-execution-record.md`。

---

## 任务 3（B9）— impact-pro 分析并执行：删掉用户的备注字段（破坏性变更：删字段）

先确认 `skills/impact-pro/SKILL.md` 已读过，然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/test-projects/ruoyi-vue`
输出到：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/test-projects/ruoyi-vue/change-impact/B9/`

用户原话："用户的备注字段不要了，把它删掉，相关的代码也清理一下"

**要求**：走完 Phase 1-5。这是一个**破坏性变更**（删字段），必须先只读搜索 `remark` 字段的所有引用和消费者，回显破坏面，追问决策。实际修改 Java Entity、Mapper XML、Service、Controller 和前端 Vue 文件，尝试运行 `mvn compile`，产出 `060-preflight.md` 和 `090-execution-record.md`。

---

## 归档步骤

全部 3 个任务完成后，列出每个任务 `change-impact/` 目录下的文件清单，以及实际修改的源代码文件清单（`git diff --stat`），作为总结。

```bash
CELL_DIR="eval/runs/blind-b7-b9-2026-06-25/cell-C1"

echo "=== B7 产出文件 ==="
find "$CELL_DIR/test-projects/go-admin/change-impact/B7/" -type f

echo "=== B7 源码改动 ==="
cd "$CELL_DIR/test-projects/go-admin" && git diff --stat

echo "=== B8 产出文件 ==="
find "$CELL_DIR/test-projects/prisma-express-ts/change-impact/B8/" -type f

echo "=== B8 源码改动 ==="
cd "$CELL_DIR/test-projects/prisma-express-ts" && git diff --stat

echo "=== B9 产出文件 ==="
find "$CELL_DIR/test-projects/ruoyi-vue/change-impact/B9/" -type f

echo "=== B9 源码改动 ==="
cd "$CELL_DIR/test-projects/ruoyi-vue" && git diff --stat
```
