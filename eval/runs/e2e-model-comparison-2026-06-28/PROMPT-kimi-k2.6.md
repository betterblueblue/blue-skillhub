# 端到端验证：Pathfinder 摸底 → Impact 变更分析（Kimi K2.6）

> 复制 `---` 之后的内容发给模型执行。
> 目标：验证 Pathfinder 和 Impact 的端到端协作质量。

---

你接下来要完成 3 个任务，按顺序逐个执行。

**工作目录**：`e:\agent\blue-skillhub`

**测试项目路径**（只读，不修改源代码）：`test-projects/realworld-express-prisma-kimi-k2.6`

这是一个 RealWorld (Conduit) API 规范的 Express + Prisma + TypeScript 实现，包含用户认证（JWT）、文章 CRUD、评论、关注、标签等功能。

## 关键前置步骤（必做，不可跳过）

**不要使用已安装的 skill 副本（可能过期）。必须从仓库目录读取最新版 skill 文件。**

**不要使用 `/pathfinder` 或 `/impact` 斜杠命令。** 斜杠命令会触发 IDE 自动加载 `~/.claude/skills/` 下的已安装版本，可能过期且不受你控制。你必须手动 Read 以下文件，并严格按照其中的流程手动执行。

任务开始前，你必须依次 Read 以下文件（以仓库目录为准）：

### Pathfinder skill 文件（任务 1 用）
1. `skills/pathfinder/SKILL.md` — 主文件
2. `skills/pathfinder/references/phase-1-sizing.md` — Phase 1 体量测量
3. `skills/pathfinder/references/phase-2-explore-domains.md` — Phase 2 并行专探
4. `skills/pathfinder/references/phase-3-depth-fill.md` — Phase 3 深挖 + Phase 5 扩展
5. `skills/pathfinder/references/stack-detection.md` — 栈探测
6. `skills/pathfinder/references/handoff-contract.md` — 与 impact 协作
7. `skills/pathfinder/references/cross-platform-notes.md` — 跨平台
8. `skills/pathfinder/references/review-checklist.md` — review checklist
9. `skills/pathfinder/templates/project-map.md` — 地图模板
10. `skills/pathfinder/code-graph-adapters/generic-mcp.md` — 代码图适配器（若可用）

### Pathfinder 脚本（Phase 1.5 + Phase 4 闸门用）
- `skills/pathfinder/scripts/pf_scan.py` — Phase 1.5 项目扫描
- `skills/pathfinder/scripts/pf_git.py` — Phase 1.5 Git 元数据
- `skills/pathfinder/scripts/pf_validate.py` — Phase 4 Script Gate 闸门

### Impact skill 文件（任务 2、3 用）
1. `skills/impact/SKILL.md` — 主文件
2. `skills/impact/references/phase-1-intent.md` — Phase 1
3. `skills/impact/references/phase-2-context-discovery.md` — Phase 2
4. `skills/impact/references/phase-2.5-risk-triage.md` — Phase 2.5
5. `skills/impact/references/phases-detail.md` — Phase 3 & 3.5（含 Step 3.0 不确定项分类）
6. `skills/impact/references/phase-4-output.md` — Phase 4
7. `skills/impact/references/phase-5-execution.md` — Phase 5
8. `skills/impact/references/dimensions.md` — 19 维度
9. `skills/impact/references/cross-platform-notes.md` — 跨平台
10. `skills/impact/profiles/node-express-prisma.md` — Node/Express/Prisma 技术栈规则
11. `skills/impact/db-adapters/postgresql.md` — PostgreSQL 适配器
12. `skills/impact/templates/000-context-pack.md` — Context Pack 模板
13. `skills/impact/templates/040-light.md` — light 模式模板
14. `skills/impact/templates/010-requirements.md` — 需求文档模板
15. `skills/impact/templates/020-design.md` — 设计文档模板
16. `skills/impact/templates/030-implementation.md` — 实施文档模板
17. `skills/impact/templates/060-preflight.md` — 执行前检查模板
18. `skills/impact/templates/_active-state.md` — 状态文件模板
19. `skills/impact/templates/_style-rules.md` — 风格规则模板
20. `skills/impact/code-graph-adapters/generic-mcp.md` — 代码图适配器（若可用）

**重要**：以上文件全部从仓库目录 `skills/` 读取，不要从 `~/.claude/skills/` 读取。仓库是 source of truth。

---

## 任务 1：Pathfinder 摸底

按照上方 Read 的 `skills/pathfinder/SKILL.md` 中定义的流程，对 `test-projects/realworld-express-prisma-kimi-k2.6` 做项目认知地图。

输出路径：`test-projects/realworld-express-prisma-kimi-k2.6/change-impact/_project-map.md`

### 关键要求

1. **Phase 1.5 FACTS 层（必做）**：Phase 1 完成后，必须运行两个脚本产出 facts JSON：
   ```bash
   python skills/pathfinder/scripts/pf_scan.py test-projects/realworld-express-prisma-kimi-k2.6 --output test-projects/realworld-express-prisma-kimi-k2.6/change-impact/_project-map/facts/scan.json
   python skills/pathfinder/scripts/pf_git.py test-projects/realworld-express-prisma-kimi-k2.6 --output test-projects/realworld-express-prisma-kimi-k2.6/change-impact/_project-map/facts/git.json
   ```
   脚本执行失败时停下来排查，不能跳过。

2. **核心 15 节（【0】～【14】）**：地图必须包含全部 15 个核心节，包括：
   - 【0】基本信息 → 【13】没挖深的部分
   - **【14】代码风格观察（默认产出，不可跳过）**——含 naming / layering / orm / transaction / exception / logging / api_response / DI 等观察轴
   - Executive Summary（给人看的第一屏）

3. **Script Gate（必做）**：写入 `_project-map.md` 前必须运行闸门脚本：
   ```bash
   python skills/pathfinder/scripts/pf_validate.py test-projects/realworld-express-prisma-kimi-k2.6/change-impact/_project-map.md --repo-root test-projects/realworld-express-prisma-kimi-k2.6
   ```
   exit code ≠ 0 时逐条修正后重新运行，直到 exit code = 0 才能写入。

4. **三张 Mermaid 图**：【3】架构/模块图、【6】数据模型 ER 图、【11】典型主流程图

5. **认证-鉴权字段一致性自检**：填完【10】后必须读源码比对认证链路和鉴权链路的字段一致性

6. 不要修改任何源代码文件

---

## 任务 2：Impact 分析 — 请求体大小限制（light）

按照上方 Read 的 `skills/impact/SKILL.md` 中定义的流程，处理以下需求：

项目路径：`test-projects/realworld-express-prisma-kimi-k2.6`
输出到：`test-projects/realworld-express-prisma-kimi-k2.6/change-impact/e2e/C1/`

用户原话："API 请求体没有限制，有人传了个超大的东西服务器差点挂了，加个限制吧"

### 关键要求

1. **只做影响分析和文档输出，不修改源代码，不进入 Phase 5 执行**
2. 如果 Phase 3 提出澄清问题，你**不需要等待用户回答**。请自行做出**合理假设**，并明确标注为 `[假设]`。例如："[假设] 限制大小为 1MB"
3. 所有假设必须在产出文档中集中列出
4. **Phase 3 Step 3.0 不确定项分类**：每个不确定项先判断是"代码可推断"还是"业务需决策"。代码可推断的自行查证标注 `【代码推断: file:line】`，不问用户；只有业务需决策项才做假设
5. **Phase 2 拉取 L1 上下文**：如果任务 1 产出了 `_project-map.md`，Phase 2 必须读取它作为 L1 项目地图
6. **Phase 2 预读风格规范**：读取 `_project-map.md`【14】代码风格观察（若存在）

---

## 任务 3：Impact 分析 — 强制邮箱验证（full）

按照上方 Read 的 `skills/impact/SKILL.md` 中定义的流程，处理以下需求：

项目路径：`test-projects/realworld-express-prisma-kimi-k2.6`
输出到：`test-projects/realworld-express-prisma-kimi-k2.6/change-impact/e2e/C2/`

用户原话："注册的时候不需要验证邮箱就能直接用，这样不行吧"

### 关键要求

1. **只做影响分析和文档输出，不修改源代码，不进入 Phase 5 执行**
2. 如果 Phase 3 提出澄清问题，你**不需要等待用户回答**。请自行做出**合理假设**，并明确标注为 `[假设]`
3. 所有假设必须在产出文档中集中列出
4. **Phase 3 Step 3.0 不确定项分类**：同任务 2 要求
5. **Phase 2 拉取 L1 上下文**：同任务 2 要求
6. **full 模式产出三文档**：010-requirements.md + 020-design.md + 030-implementation.md + 000-context-pack.md
7. 这个变更涉及多层：Prisma schema 变更、注册流程改动、登录校验、新增验证端点、邮件发送工具、auth 中间件改动——分析必须覆盖这些层面

---

## 全部完成后

列出所有产出文件清单作为总结：

```bash
echo "=== Pathfinder 产出 ==="
dir /s /b test-projects\realworld-express-prisma-kimi-k2.6\change-impact\_project-map.md
dir /s /b test-projects\realworld-express-prisma-kimi-k2.6\change-impact\_project-map\facts\

echo "=== Impact C1 产出 ==="
dir /s /b test-projects\realworld-express-prisma-kimi-k2.6\change-impact\e2e\C1\

echo "=== Impact C2 产出 ==="
dir /s /b test-projects\realworld-express-prisma-kimi-k2.6\change-impact\e2e\C2\
```
