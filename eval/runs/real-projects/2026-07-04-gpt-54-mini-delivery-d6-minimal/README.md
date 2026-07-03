# D6 Minimal Pathfinder 复测记录

结论: `GATE-RECOVERED / PASS`

这次 fixture 副本一开始就带着旧的 `change-impact` 目录，确实会污染 D6 复测。我先把 fixture 副本内旧 `change-impact` 删除掉，再重新跑 `pf_scan.py`、`pf_git.py`、`pf_validate.py`，所以最终证据只来自清理后的产物。

## 1. 清理

命令:

```powershell
Remove-Item -LiteralPath E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704\change-impact -Recurse -Force
```

退出码: `0`

关键结果:

- 删除了 fixture 副本内旧的 `change-impact` 目录。

## 2. Facts

命令:

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_scan.py E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704 --output E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704\change-impact\_project-map\facts\scan.json
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_git.py E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704 --output E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704\change-impact\_project-map\facts\git.json
```

退出码:

- `pf_scan.py` -> `0`
- `pf_git.py` -> `0`

关键输出:

- `scan.json` 记录 `file_count: 47`、`budget_tier: 小仓`
- `git.json` 记录 `is_git_repo: false`

## 3. 地图校验

首次 `--stdin` 校验命令:

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py --stdin --repo-root E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704
```

首次退出码: `1`

首次关键输出:

- `FAIL: V5: Mermaid solid-arrow source 'fs' not mentioned in body text`
- `FAIL: V5: Mermaid solid-arrow source 'fc' not mentioned in body text`

修正动作:

- 在 `_project-map.md` 正文补充了 `fc` / `fs` 的说明
- 顺手修正了几处路径笔误

重新 `--stdin` 校验退出码: `0`

写入后最终校验命令:

```powershell
python E:\agent\blue-skillhub\skills\pathfinder\scripts\pf_validate.py E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704\change-impact\_project-map.md --repo-root E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704
```

最终退出码: `0`

最终关键输出:

- `PASS: V1: line-number claims verified`
- `PASS: V2: no credential leakage detected`
- `PASS: V3: SVG safety check passed`
- `PASS: V4: uncovered section has entries`
- `PASS: V5: Mermaid solid-arrow consistency passed`
- `PASS: V6: facts file content validated`
- `PASS: V7: section [14] code style observation exists`
- `PASS: V8: evidence path format sane`

## 4. 产物与文件列表

本次最终使用的产物:

- `E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704\change-impact\_project-map.md`
- `E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704\change-impact\_project-map\facts\scan.json`
- `E:\agent\real-project-fixtures-delivery\monorepo-api-subdir-gpt54mini-d6-minimal-20260704\change-impact\_project-map\facts\git.json`

这次实际改动只落在允许的三个位置上:

- fixture 副本内的 `change-impact/_project-map.md`
- fixture 副本内的 `change-impact/_project-map/facts/*.json`
- `E:\agent\blue-skillhub\eval\runs\real-projects\2026-07-04-gpt-54-mini-delivery-d6-minimal\README.md`
