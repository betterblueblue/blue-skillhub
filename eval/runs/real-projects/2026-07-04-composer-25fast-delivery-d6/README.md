# D6 — 非 Git monorepo 子目录 Pathfinder（Composer 2.5 Fast）

## 结论

**PASS**。识别当前目录为非独立 Git 仓库；地图头部写「非 Git,以扫描时间为准」；未引用父仓库 commit/branch/hotspots；明确 `@repo/auth`/`@repo/db`/`@repo/shared` 等 workspace 包不在副本内、限制完整运行与 schema 判断。

## Validator

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures\monorepo-api-subdir-d6-composer\api\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures\monorepo-api-subdir-d6-composer\api
```

- 退出码：`0`
- 摘要：`10 passed, 0 failed, 0 warnings`
- 首次 `--stdin` 校验曾 V5 失败（Mermaid 节点未在正文提及），修正后通过

## 运行信息

| 项 | 值 |
|---|---|
| 场景 ID | D6-monorepo-api-nongit-gate |
| Case ID | monorepo-full-stack-starter-negative |
| Runner | composer-25fast-subagent |
| 模型 | Composer 2.5 Fast |
| fixture | `E:\agent\real-project-fixtures\monorepo-api-subdir-d6-composer\api` |
| Git | 非 Git（`git.json`: `is_git_repo: false`） |
| 运行日期 | 2026-07-04 |

## 产物

- `E:\agent\real-project-fixtures\monorepo-api-subdir-d6-composer\api\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures\monorepo-api-subdir-d6-composer\api\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures\monorepo-api-subdir-d6-composer\api\change-impact\_project-map\facts\git.json`

## 关键发现

1. **非 Git 纪律**：`pf_git.py` 产出 `is_git_repo: false`；地图【0】基于 commit 为「非 Git,以扫描时间为准」。
2. **monorepo 子包边界**：`@repo/api` 依赖 `workspace:*` 的 auth/db/shared/config，副本内无法独立 install/run；【13】列为未深入项。
3. **技术栈**：Express 5 + TypeScript + Prisma（经 `@repo/db`）+ Better Auth + S3/MinIO + 可选 Redis 限流；小仓 ~47 文件。
4. **架构**：经典 routes → controllers → services → repositories 分层；`/api/auth/*` 由 `@repo/auth` 挂载。
5. **风险**：S3 默认弱凭证键、用户 DELETE 无 owner 校验、脱离 workspace 不可运行。

## D6 success_target 对照

| 目标 | 结果 |
|---|---|
| 识别非独立 Git 仓库 | ✅ `git.json` + 地图头部 |
| 不输出父仓库 Git 信息 | ✅ head/branch/hotspots 均为 null/空 |
| 明确 shared/前端/根 scripts 缺失限制判断 | ✅ 【2】【7】【8】【13】多处声明 workspace 包不在副本 |

## Facts 摘要

- `scan.json`: `file_count: 47`, `budget_tier: 小仓`
- `git.json`: `is_git_repo: false`, `is_independent_repo: false`
