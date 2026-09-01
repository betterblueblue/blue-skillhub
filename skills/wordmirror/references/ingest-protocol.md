# 更新协议 · "重新提取 / 画像过期了"

> 触发场景：用户要求数据更新（新对话没进来）、画像过期、换了机器要初始化。
> 原则：ingest 是幂等的——重复跑不会重复入库（按消息内容去重），放心执行。

## 一条命令

```bash
python <skill目录>/scripts/ds.py ingest
```

它会串联：提取（用户话+AI话）→ 去重 → 会话卡 → 数字底座 → 素材 → 渲染产物页。全程本地。

## 分步（只想跑某一步时）

| 命令 | 作用 |
|---|---|
| `python scripts/ds.py init` | 只探测本机有哪些 agent 存档（不写任何东西） |
| `python scripts/ds.py ingest` | 全链路更新 |
| `python scripts/ds.py ask "词"` | 快速检索（验证数据活着） |
| `python scripts/ds.py where` | 显示数据目录和语料条数 |

## 注意

1. **首次跑耗时与语料量成正比**（重度用户约几分钟）；增量跑很快
2. 跑完报告里的"量级提示"（<500 条=画像会很薄）要转告用户，管理预期
3. **画像文件（portrait.md / habits.md）不自动重写**——语料更新后，按 `engine/SOP_蒸馏流程.md` 重新蒸馏才换版（SOP 在数据仓库的 engine/ 下，若只有 skill 包则提示用户去原仓库跑）
4. 更新完建议跑 `python scripts/ds.py check`（自检），全绿才算完成
5. 探测不到某 agent → 正常（报告"没找到，跳过"），不是错误；新 agent 支持要改 `engine/detect_agents.py` 的表
