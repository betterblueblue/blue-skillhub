# d12-composer-25fast Pathfinder 评测记录

目标：在 `E:\agent\real-project-fixtures\monorepo-full-stack-starter`（Git 根目录）只读生成项目地图，再在删除 `.git` 的副本 `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer` 重跑一次，并比较两次差异。

允许修改的文件：

- `E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\git.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map\facts\git.json`

参考地图：`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-gpt54mini-nongit\change-impact\_project-map.md`

Skill hub 脚本：`E:\agent\blue-skillhub\skills\pathfinder\scripts\`

## 实际命令

### 1) Git 根目录

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py E:\agent\real-project-fixtures\monorepo-full-stack-starter --output E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\scan.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py E:\agent\real-project-fixtures\monorepo-full-stack-starter --output E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map\facts\git.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter
```

退出码：

- `pf_scan.py` = `0`
- `pf_git.py` = `0`
- `pf_validate.py` 第一次 = `0`（头部换行修正后复验仍为 `0`）

关键输出摘要：

- `pf_scan.py`：`file_count: 152`，`budget_tier: 小仓`，`dir_tree` 覆盖 `apps/`、`packages/`、`scripts/`
- `pf_git.py`：`is_git_repo: true`，`is_independent_repo: true`，`head_short: 21fbd77`，`toplevel: E:/agent/real-project-fixtures/monorepo-full-stack-starter`
- `pf_validate.py`：`SUMMARY: 10 passed, 0 failed, 0 warnings`

### 2) 删除 `.git` 的副本

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer --output E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map\facts\scan.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer --output E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map\facts\git.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer
```

退出码：

- `pf_scan.py` = `0`
- `pf_git.py` = `0`
- `pf_validate.py` = `0`

关键输出摘要：

- `pf_scan.py`：与 Git 根目录一致，`file_count: 152`，`budget_tier: 小仓`
- `pf_git.py`：`is_git_repo: false`，`is_independent_repo: false`，`toplevel: null`，`head_short/head_full/branch: null`
- `pf_validate.py`：`SUMMARY: 10 passed, 0 failed, 0 warnings`

## 两次差异

### 事实层（facts）

| 字段 | Git 根目录 | 非 Git 副本 |
|------|-----------|------------|
| `scan.json` file_count | 152 | 152（一致） |
| `scan.json` budget_tier | 小仓 | 小仓（一致） |
| `git.json` is_git_repo | true | false |
| `git.json` head_short | 21fbd77 | null |
| `git.json` toplevel | E:/agent/real-project-fixtures/monorepo-full-stack-starter | null |
| `git.json` hotspots | [] | [] |

无 Git 时必须降级的信息：HEAD commit、branch、toplevel、hotspots、recent_commit_modules。`pf_scan.py` 输出不受影响。

### 地图头部

| 字段 | Git 根目录 | 非 Git 副本 |
|------|-----------|------------|
| 开头说明 | 标准 Pathfinder 说明，不提删除 `.git` | 额外说明「当前副本已删除 `.git`，因此头部按非 Git 处理」 |
| 生成时间 | 2026-07-04 18:14:17 +08:00 | 2026-07-04 18:14:18 +08:00 |
| 基于 commit | **21fbd77**（真实 HEAD） | **非 Git,以扫描时间为准** |

### 结构内容

两份 `_project-map.md` 的 workspace 边界、shared types、API、Prisma、前端、风险点、【14】代码风格观察等 15 个核心节内容一致；差异仅在头部 Git 归属与开头说明。

## 生成结果

- Git 根目录项目地图：`E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md`
- 非 Git 副本项目地图：`E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map.md`

## 判分方复核

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-full-stack-starter-d12-composer
```

两条命令退出码均为 `0`，摘要均为 `SUMMARY: 10 passed, 0 failed, 0 warnings`。非 Git 副本的 `facts/git.json` 为 `is_git_repo=false`，且 `head_short/head_full/branch/hotspots/recent_commit_modules` 均为空，未发现父仓库 Git 信息污染。
