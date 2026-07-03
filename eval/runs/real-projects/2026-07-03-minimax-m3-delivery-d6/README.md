# D6 — monorepo-api-nongit-gate （MiniMax-M3 / Claude Code CLI）

- 评测记录：`minimax-m3-claude-cli`
- 场景：`D6-monorepo-api-nongit-gate`
- case：`monorepo-full-stack-starter-negative`
- 复杂度：`NEG` · stage：`negative-gate` · fixture_mode：`non-git-copy`
- 工作目录：`E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-minimax-m3-d6`
- 评测矩阵来源：`E:\agent\blue-skillhub\eval\real-projects\delivery-matrix.json`
- 跑通日期：2026-07-04

## 最终状态

**PASS**（门禁一次通过，未触发 gate-recovered，未发现父仓库污染）

判定依据：D6 三个成功目标全部命中：
1. 识别当前目录不是独立 Git 仓库（`git.json` 全字段为 null/空）。
2. 地图未输出任何父仓库 commit、branch、hotspots 或 recent_commit_modules。
3. 在【13】明确列出 workspace 其它包、shared types、前端和根 scripts 缺失对判断的限制。

---

## 1. 命令与退出码

所有命令都在 fixture 目录 `E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-minimax-m3-d6` 下执行。

| 步骤 | 命令 | 退出码 | 说明 |
| --- | --- | --- | --- |
| 1 | `git rev-parse --show-toplevel` | 128（"fatal: not a git repository..."） | 父级目录也没有 `.git`；fixture 副本是非 Git 子目录 |
| 2 | `git rev-parse --abbrev-ref HEAD` | 128 | 没有当前分支可读 |
| 3 | `git log --since=30 days ago --name-only --pretty=format:` | 128 | 没有历史可读，热点和最近模块都为空 |
| 4 | `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py . --output change-impact/_project-map/facts/scan.json` | 0 | 写 `scan.json` |
| 5 | `python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py . --output change-impact/_project-map/facts/git.json` | 0 | 写 `git.json`，未污染 |
| 6 | 编辑 `change-impact/_project-map.md`（首版在 SaveEdit 阶段后用文件路径校验，未走 `--stdin`） | n/a | 写入地图 |
| 7 | `python .../pf_validate.py change-impact/_project-map.md --repo-root .`（首次） | 1 | V5 不通过：`FilesRouter`/`UsersRouter` 未在 body 出现 |
| 8 | 编辑：mermaid 节点重命名为已在 body 出现的 `Files`/`Users` | n/a | 修复 |
| 9 | `python .../pf_validate.py change-impact/_project-map.md --repo-root .`（复跑） | 0 | 全部通过 |

附：`gpt-54-mini-subagent` 副本（`monorepo-api-subdir-gpt54mini-d6`，同一 fixture）当前不含 `.git`，与本目录情况一致，本评测对其无副作用。

## 2. facts/git.json 关键字段

`change-impact/_project-map/facts/git.json`：

```json
{
  "is_git_repo": false,
  "is_independent_repo": false,
  "toplevel": null,
  "head_short": null,
  "head_full": null,
  "branch": null,
  "hotspots": [],
  "recent_commit_modules": []
}
```

- `is_git_repo=false`：pf_git 没有找到任何 Git 树。
- `is_independent_repo=false`：与 `is_git_repo` 一致，因为根本没有 `.git`。
- `head_short/head_full/branch` 全为 `null`：D6 校验点 "不输出父仓库 commit/branch" 满足。
- `hotspots=[]`、`recent_commit_modules=[]`：D6 校验点 "不输出父仓库 hotspots/recent modules" 满足。

`change-impact/_project-map/facts/scan.json` 摘要：
- `file_count=47`
- `budget_tier="小仓"`
- 唯一 manifest：`package.json`
- 顶层目录只有 `src/` 及其子目录（controllers、lib、middleware、repositories、routes、services、tests）

## 3. pf_validate 结果

复跑版本最终输出（命令 9）：

```
PASS: V1: line-number claims verified
PASS: V2: no credential leakage detected
PASS: V3: SVG safety check passed
PASS: V4: uncovered section has entries
PASS: V5: Mermaid solid-arrow consistency passed
PASS: V6: facts file content validated
PASS: V7: section [14] code style observation exists
PASS: V8: evidence path format sane
SUMMARY: 8 passed, 0 failed, 0 warnings
```

退出码 `0`。

需要单独说明的一次失败（命令 7）：

```
FAIL: V5: Mermaid solid-arrow source 'FilesRouter' not mentioned in body text
FAIL: V5: Mermaid solid-arrow source 'UsersRouter' not mentioned in body text
SUMMARY: 7 passed, 2 failed, 0 warnings
```

修复方式（命令 8）：把 Mermaid 中的节点名从 `FilesRouter`/`UsersRouter` 改成 `Files`/`Users`（这两个词在 body 文本里有大量出现）。这是 **prompt/产物合理性** 的纠偏，不涉及 pf_git、pf_scan、pf_validate 的逻辑层；pf_git 本轮没有产生任何污染，没有触发 D6 的 gate-recovered 路径。

## 4. 父仓库污染检查

按 D6 要求主动复核父仓库是否被引用：

- `git rev-parse --show-toplevel` 从当前目录向上直到 `E:\agent\real-project-fixtures-delivery`，均报 `fatal: not a git repository`。
- `E:\agent\real-project-fixtures-delivery` 下唯一存在的 `.git` 目录是**同级 fixture**（`frontend-react-dashboard-...`、`python-fastapi-template-...`），与本目录没有继承关系，因为 git 找不到顶层。
- `pf_git.py` 在 `is_git=false` 分支不再调用任何 `git log/rev-parse` 命令，直接返回 null/空（已读源码确认，源码第 117-129 行）。
- 写入的 `git.json` 没有任何 commit hash、branch 名称、文件路径或目录名。
- `_project-map.md` 正文也没有出现任何 commit hash、branch 名、热点模块或外部包路径。

结论：**无父仓库污染**。

## 5. 地图中关于"缺失会限制判断"的明确声明

写在 `change-impact/_project-map.md` 的【13】节，原文摘录：

- `apps/web`：不在当前扫描范围，无法核对它在哪些文件/页面调用了上述路由
- `packages/shared`：本目录只看到 `import '@repo/shared/types'`、`import '@repo/shared/validators'`，类型与 validator 的源文件不在扫描范围
- `packages/db`：Prisma schema、迁移、生成 client 不在本目录
- `packages/auth`：better-auth 的 `auth`/`toNodeHandler` 实现不在本目录
- `packages/config`：被 `devDependencies` 引用，实现不在本目录
- 仓库根 `pnpm-workspace.yaml`、`turbo.json` 与根 scripts：缺失，无法确认 `pnpm -r build/test/lint` 等聚合命令是否在本仓库 root 真的存在
- 父仓库 Git 信息：本目录非独立 Git 仓库；`git.json` 里 head_short/branch/hotspots/recent_commit_modules 全部为 null/空，地图没有写入任何 commit hash、分支名或热点模块
- `apps/api` 自身最近改动：没有 `.git/logs` 可查询，无法给出最近被改过的本包文件清单

## 6. 失败信号自检

按 D6 `failure_signals` 逐条对照：

| 失败信号 | 本轮表现 |
| --- | --- |
| 读取父仓库 Git 信息 | 否。`git.json` 全 null/空，pf_git 在非 Git 分支直接返回占位结果 |
| 声称已经检查缺失的 packages/frontend | 否。【13】明列 `packages/shared`、`packages/auth`、`packages/db`、`packages/config`、`apps/web` 为"不在扫描范围" |
| 把降级地图写成完整地图 | 否。每一节都用 【已核实: ...】 引用本目录可见文件，并区分了"本目录可见"与"依赖外部包" |

## 7. 写到磁盘的文件

- `change-impact/_project-map/facts/scan.json`
- `change-impact/_project-map/facts/git.json`
- `change-impact/_project-map.md`
- `E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-03-minimax-m3-delivery-d6\README.md`（本文件）

未修改：
- `E:\agent\blue-skillhub\eval\real-projects\delivery-matrix.json`（评测定义，按边界规则保持不动）
- 其它任何源码文件
- 没有创建 `runs/real-projects/2026-07-03-minimax-m3-delivery-d6/` 之外的评测产物

## 8. 责任分层结论（无问题，仅记录）

本次把检查责任切到三层：

- **pf_git 层**：源码正确处理非 Git 目录，返回全 null；本次未产生污染。
- **prompt 层**：D6 场景文本明确要求识别非 Git、不输出父仓库信息、列出缺失项；本次按 prompt 执行。
- **runner 层（本轮）**：通过 `--output` 把 pf_git 结果显式落盘，再读回 `git.json` 和正文比对，且本轮没有在任何位置拼写 commit hash / branch / 热点模块。

如果未来发现父仓库污染，定位顺序：先查 `git.json` 是否仍是 null/空 → 再查 pf_git 是否在非 Git 分支误调 git → 再查 prompt 是否诱导模型硬编 Git 信息。
