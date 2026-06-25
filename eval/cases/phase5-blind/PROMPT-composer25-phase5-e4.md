# E4 V1-only 计数专项盲测 Prompt（Composer 2.5）

> 复制下面 `---` 之后的内容发给 Composer 2.5 执行。

---

你接下来要完成 1 个测试任务，使用 `/impact-pro` skill，**走完整 Phase 1-5 流程，包括实际执行阶段**。

**测试项目路径**（本 cell 专属副本，你会在第一步复制）：
- 源项目：`test-projects/static-frontend`
- 工作目录：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/`

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
5. **尝试运行 build/test 命令**：用 Bash 工具尝试运行项目证据发现的 build/test 命令。如果环境不支持（缺 Docker/DB/Java 等），如实标注 V1 并说明原因，不得假装通过。
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

**关键前置步骤**：任务开始前，你必须先 Read 对应 skill 的 `SKILL.md` 文件，确保你使用的是最新版协议。读完 SKILL.md 后，如果其中提到某 Phase 的完整规则在 `references/` 下，也请 Read 对应的 references 文件。

---

## 准备步骤：复制测试项目

在开始任务前，先复制测试项目到本 cell 专属目录：

```bash
CELL_DIR="eval/runs/phase5-blind-2026-06-25/cell-C1"
mkdir -p "$CELL_DIR/test-projects"
cp -r test-projects/static-frontend "$CELL_DIR/test-projects/"
```

---

## 任务（E4）— impact-pro 分析并执行：给首页加用户反馈表单

先 Read `skills/impact-pro/SKILL.md`（及 references/），然后运行 `/impact-pro`，处理以下需求：

项目路径：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/static-frontend`
输出到：`eval/runs/phase5-blind-2026-06-25/cell-C1/test-projects/static-frontend/change-impact/E4/`

用户原话："首页底部能不能加个用户反馈表单，就是填个姓名、邮箱和留言，点提交就行"

**要求**：走完 Phase 1-5，实际修改 index.html、style.css 和 JS 文件，尝试运行项目证据发现的 build/test 命令（如果有的话），产出 `060-preflight.md` 和 `090-execution-record.md`。如果项目没有构建系统（无 package.json / 无 Makefile 等），如实标注 V1 并维护 V1-only 计数。

---

## 归档步骤

任务完成后，列出 `change-impact/` 目录下的文件清单，以及实际修改的源代码文件清单（`git diff --stat`），作为总结。

```bash
CELL_DIR="eval/runs/phase5-blind-2026-06-25/cell-C1"

echo "=== E4 产出文件 ==="
find "$CELL_DIR/test-projects/static-frontend/change-impact/E4/" -type f

echo "=== E4 源码改动 ==="
cd "$CELL_DIR/test-projects/static-frontend" && git diff --stat
```
