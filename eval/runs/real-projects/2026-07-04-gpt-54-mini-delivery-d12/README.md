# d12-gpt-54-mini Pathfinder 评测记录

目标：
在 `E:\agent\real-project-fixtures\monorepo-full-stack-starter` 先只读生成项目地图，再在删除 `.git` 的副本 `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit` 重跑一次，并比较两次差异。

允许修改的文件已控制在：
`E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md`
`E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\scan.json`
`E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\git.json`
`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map.md`
`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map\facts\scan.json`
`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map\facts\git.json`

## 实际命令

### 1) Git 根目录

```powershell
python 'C:\Users\blue\.codex\skills\pathfinder\scripts\pf_scan.py' 'E:\agent\real-project-fixtures\monorepo-full-stack-starter' --output 'E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\scan.json'
python 'C:\Users\blue\.codex\skills\pathfinder\scripts\pf_git.py' 'E:\agent\real-project-fixtures\monorepo-full-stack-starter' --output 'E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\git.json'
python 'C:\Users\blue\.codex\skills\pathfinder\scripts\pf_validate.py' 'E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md' --repo-root 'E:\agent\real-project-fixtures\monorepo-full-stack-starter'
```

退出码：
- `pf_scan.py` = `0`
- `pf_git.py` = `0`
- `pf_validate.py` 第一次 = `1`
- `pf_validate.py` 第二次 = `0`

关键输出摘要：
- `pf_scan.py`：`file_count: 152`，`budget_tier: 小仓`，`dir_tree` 覆盖 `apps/`、`packages/`、`scripts/`
- `pf_git.py`：`is_git_repo: true`，`is_independent_repo: true`，`head_short: 21fbd77`，`toplevel: E:/agent/real-project-fixtures/monorepo-full-stack-starter`
- `pf_validate.py` 首轮失败点：`V5: Mermaid solid-arrow source 'prismaClient' not mentioned in body text`
- 修正后复验：`8 passed, 0 failed, 0 warnings`

### 2) 删除 `.git` 的副本

```powershell
python 'C:\Users\blue\.codex\skills\pathfinder\scripts\pf_scan.py' 'E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit' --output 'E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map\facts\scan.json'
python 'C:\Users\blue\.codex\skills\pathfinder\scripts\pf_git.py' 'E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit' --output 'E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map\facts\git.json'
python 'C:\Users\blue\.codex\skills\pathfinder\scripts\pf_validate.py' 'E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map.md' --repo-root 'E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit'
```

退出码：
- `pf_scan.py` = `0`
- `pf_git.py` = `0`
- `pf_validate.py` 第一次 = `1`
- `pf_validate.py` 第二次 = `0`

关键输出摘要：
- `pf_scan.py`：和 Git 根目录一致，`file_count: 152`，`budget_tier: 小仓`
- `pf_git.py`：`is_git_repo: false`，`is_independent_repo: false`，`toplevel: null`，`head_short: null`，`head_full: null`
- `pf_validate.py` 首轮失败点：同样是 `V5: Mermaid solid-arrow source 'prismaClient' not mentioned in body text`
- 修正后复验：`8 passed, 0 failed, 0 warnings`

## 两次差异

### 事实层

- `pf_scan.py` 两次输出一致：`file_count 152`，`预算档位 小仓`，目录结构和清单文件一致。
- `pf_git.py` 差异明显：
  - Git 根目录版：识别为独立 Git 仓库，带 `head_short=21fbd77` 和 `toplevel`
  - 非 Git 副本版：`is_git_repo=false`，`head_short/head_full/toplevel/branch` 都降级为 `null`

### 地图头部

- Git 根目录版地图头部写的是 `基于 commit: 21fbd77`
- 非 Git 副本版地图头部写的是 `基于 commit: 非 Git,以扫描时间为准`

### 结构内容

- 两份 `_project-map.md` 的项目结构、workspace 边界、API、Prisma、shared types、前端、风险点、测试概况保持一致。
- 非 Git 副本版额外在开头说明当前副本已删除 `.git`，因此头部按非 Git 处理。

## 生成结果

- Git 根目录项目地图：`E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md`
- 非 Git 副本项目地图：`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map.md`

## 判分方复核

runner 首轮执行使用的是 `C:\Users\blue\.codex\skills\pathfinder\scripts\*.py`。判分方随后使用仓库内真实脚本独立复跑：

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit
```

两条命令退出码均为 `0`，摘要均为 `SUMMARY: 10 passed, 0 failed, 0 warnings`。非 Git 副本的 `facts/git.json` 为 `is_git_repo=false`，且 `head_short/head_full/branch/hotspots/recent_commit_modules` 均为空，未发现父仓库 Git 信息污染。
