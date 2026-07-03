# D6 Non-Git Pathfinder Comparison

本次对比覆盖 `D6-monorepo-api-nongit-gate`：只复制 monorepo 的 `apps/api` 子目录，没有 `.git`，要求 Pathfinder 生成降级项目地图，不得读取或编造父仓库 Git 信息。

## 结论

| runner | 最终状态 | 关键表现 | 证据 |
|---|---|---|---|
| `gpt-54-mini-subagent` | `UNVERIFIED` | facts 正确，但没有完成 `_project-map.md` 和 README | `git.json` 为非 Git null/空；地图缺失 |
| `minimax-m3-claude-cli` | `GATE-RECOVERED` | 完成地图和归档；首次 Mermaid V5 失败后修复 | `pf_validate.py` 最终 `8 passed / 0 failed / 0 warnings` |
| `gpt-54-mini-subagent` 最小模板复跑 | `GATE-RECOVERED / PASS` | 发现 fixture 旧 `change-impact` 污染，清理后从 facts、`--stdin` gate 到最终地图完整跑完 | `pf_validate.py` 最终 `8 passed / 0 failed / 0 warnings` |

## 共同通过点

两个 runner 的 `facts/git.json` 都正确：

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

这说明 `pf_git.py` 的非 Git 保护在真实 runner 里生效：没有把同级或父目录其它 fixture 的 Git 信息混进来。

## 模型差异

`gpt-5.4-mini` 首轮能正确跑 facts，但在需要组织完整地图草稿、stdin 校验、落盘和归档时没有收敛。2026-07-04 最小模板复跑后，它可以从干净副本完成地图：首次 `--stdin` 被 V5 Mermaid 一致性拦住，补正文说明后最终通过。因此 D6 对它的结论从“能力未证明”更新为“短模板 + gate 可以拉回完成态”。

MiniMax M3 能完成完整地图，且地图里明确写出 `apps/web`、`packages/shared`、`packages/db`、`packages/auth`、root scripts 等缺失会限制判断。不过它首次触发 Pathfinder V5 Mermaid 检查，修 Mermaid 节点后才通过，所以按本轮统一口径记为 `GATE-RECOVERED`，不是首次 PASS。

## 证据入口

- `eval/runs/real-projects/2026-07-03-gpt-54-mini-delivery-d6/README.md`
- `eval/runs/real-projects/2026-07-03-minimax-m3-delivery-d6/README.md`
- `eval/runs/real-projects/2026-07-04-gpt-54-mini-delivery-d6-minimal/README.md`

## 下一步

D6 的复跑暴露出一个评测设置问题：真实 fixture 里可能已经有旧 `change-impact`。后续所有 isolated/non-git 副本，除非专门测试恢复或旧地图刷新，都要先清理副本内旧 `change-impact`，再开始评测。
