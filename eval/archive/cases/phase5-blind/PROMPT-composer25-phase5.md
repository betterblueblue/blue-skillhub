# Composer 2.5 Phase 5 执行阶段盲测 Prompt

> 复制下面整段内容发给 Composer 2.5 执行。
> 本 prompt 测试 Phase 5 执行阶段：模型不仅要产出分析文档，还要**实际写代码、跑测试、产出执行记录**。
> skill_commit: 55276bf (v4.1)

---

你接下来要连续完成 3 个测试任务，按顺序逐个执行。每个任务用对应的 skill（`/impact`、`/impact-pro`），**走完整 Phase 1-5 流程，包括实际执行阶段**。

**测试项目路径**（本 cell 专属副本，你会在第一步复制）：
- 源项目：`test-projects/prisma-express-ts`、`test-projects/full-stack-fastapi-template`、`test-projects/ruoyi-vue`
- 工作目录：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/`

**Skill 文件路径**（共享，只读）：
- impact：`skills/impact/SKILL.md`
- impact-pro：`skills/impact-pro/SKILL.md`

**重要 — 模糊需求处理规则**：
本次测试的用户需求是**口语化、模糊的**，缺少具体数值、状态码、技术细节。如果 skill 在 Phase 3 提出澄清问题，你**不需要等待用户回答**。请自行做出**合理假设**，并明确标注为 `[假设]`。然后基于假设继续分析。所有假设必须在产出文档中集中列出。

**重要 — Phase 5 执行规则**：
本次测试与之前盲测的关键区别：**你必须走到 Phase 5 实际执行**。

1. **你有完整的文件写入权限**：可以修改测试项目副本中的源代码文件。
2. 走完 Phase 1-4（分析 + 文档输出 + 用户确认）后，**进入 Phase 5 实际执行**。
3. **模拟用户确认**：每个 Step 呈现后，你自行模拟用户回答 `确认 Step N`（N 为实际 Step 编号），然后执行该 Step。
4. **实际修改源代码文件**：不是只描述要改什么，而是**真的用 Edit/Write 工具修改文件**。
5. **尝试运行 build/test 命令**：用 Bash 工具尝试运行项目证据发现的 build/test 命令。如果环境不支持（缺 Docker/DB/Java 等），**如实标注 V1 并说明原因**，不得假装通过。
6. **如实报告 V 等级**：
   - V1 = 静态验证（代码审查、grep 检查）
   - V2 = build 或单测真实运行通过（附真实命令输出）
   - V3 = V2 之上 E2E/集成/API 验证通过
   - **标 V2/V3 但无真实运行输出 → 视为用 V1 冒充，P0**
7. **产出执行前检查和执行记录**：
   - 写操作前产出 `060-preflight.md`（P0 项必须检查）
   - 每个 Step 执行后追加 `090-execution-record.md`（含时间戳、V 等级、验证结果）
8. **V1-only 连续计数**：如果连续多个写入 Step 都只能达到 V1，维护计数。连续 3 个 Step 仍无法达到 V2/V3 时，**暂停并说明**，然后继续模拟用户确认继续。
9. **高风险拦截**：如果某 Step 命中高风险拦截清单（如 ALTER TABLE、DROP 等），必须标注「高风险」，单独确认，禁止合并确认。

**关键前置步骤**：每个任务开始前，你必须先 Read 对应 skill 的 `SKILL.md` 文件，确保你使用的是最新版协议。读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。

---

## 准备步骤：复制测试项目

在开始任务前，先复制测试项目到本 cell 专属目录：

```bash
CELL_DIR="eval/runs/phase5-blind-2026-06-25/cell-C1"
mkdir -p "$CELL_DIR/test-projects"
cp -r test-projects/prisma-express-ts "$CELL_DIR/test-projects/"
cp -r test-projects/full-stack-fastapi-template "$CELL_DIR/test-projects/"
cp -r test-projects/ruoyi-vue "$CELL_DIR/test-projects/"
```

---

## 任务 1（E1）— impact-pro 分析并执行：给用户加最后登录时间

先 Read `skills/impact-pro/SKILL.md`（及 references/），然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/prisma-express-ts`
输出到：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/prisma-express-ts/change-impact/E1/`

用户原话："用户登录的时候能不能记一下最后登录时间，然后在看用户详情的时候能看到"

**要求**：走完 Phase 1-5，实际修改 Prisma schema、auth service、user DTO 和测试文件，尝试运行 `yarn build` 和 `yarn test`，产出 `060-preflight.md` 和 `090-execution-record.md`。

---

## 任务 2（E2）— impact-pro 分析并执行：给 Item 加置顶标记

先 Read `skills/impact-pro/SKILL.md`（如已读过可跳过重复读取，但需确认内容是最新的），然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/full-stack-fastapi-template/backend`
输出到：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/full-stack-fastapi-template/backend/change-impact/E2/`

用户原话："商品能不能加个置顶功能，就是可以标记某个商品是置顶的，然后在查询的时候能看到哪些是置顶的"

**要求**：走完 Phase 1-5，实际修改 SQLModel、Pydantic schema、CRUD 和测试文件，尝试运行 `ruff check` 和 `pytest`，产出 `060-preflight.md` 和 `090-execution-record.md`。

---

## 任务 3（E3）— impact 分析并执行：给部门加联系邮箱

先 Read `skills/impact/SKILL.md`（及 references/），然后运行 `/impact`，处理以下需求：

项目路径：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/ruoyi-vue`
输出到：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/ruoyi-vue/change-impact/E3/`

用户原话："部门信息里能不能加个联系邮箱，就是在添加和编辑部门的时候能填邮箱，列表里也能看到"

**要求**：走完 Phase 1-5，实际修改 SQL 脚本、Java entity、Mapper XML、Service、Controller 和前端 Vue 文件，尝试运行 `mvn compile` 或 `mvn test`，产出 `060-preflight.md` 和 `090-execution-record.md`。如果 Java/Maven 环境不可用，如实标注 V1 并维护 V1-only 计数。

---

## 归档步骤

全部 3 个任务完成后，列出每个任务 `change-impact/` 目录下的文件清单，以及实际修改的源代码文件清单（`git diff --stat`），作为总结。

```bash
CELL_DIR="eval/runs/phase5-blind-2026-06-25/cell-C1"

echo "=== E1 产出文件 ==="
find "$CELL_DIR/test-projects/prisma-express-ts/change-impact/E1/" -type f

echo "=== E1 源码改动 ==="
cd "$CELL_DIR/test-projects/prisma-express-ts" && git diff --stat

echo "=== E2 产出文件 ==="
find "$CELL_DIR/test-projects/full-stack-fastapi-template/backend/change-impact/E2/" -type f

echo "=== E2 源码改动 ==="
cd "$CELL_DIR/test-projects/full-stack-fastapi-template" && git diff --stat

echo "=== E3 产出文件 ==="
find "$CELL_DIR/test-projects/ruoyi-vue/change-impact/E3/" -type f

echo "=== E3 源码改动 ==="
cd "$CELL_DIR/test-projects/ruoyi-vue" && git diff --stat
```
