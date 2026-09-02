# 更新协议 · "重新提取 / 你的情况过期了"

> 触发场景：用户要求数据更新（新对话没进来）、你的情况过期了、换了机器要初始化。
> 原则：重复跑不会重复入库（按消息内容去掉重复的），放心执行。

## 一条命令

```bash
python <skill目录>/scripts/wm.py ingest
```

它会串联：提取（你的话+AI 的话）→ 去掉重复的 → 拼对话记录 → 统计 → 整理素材 → 挖照见候选 → 生成网页。全程在你自己电脑上。

## 就一条命令

更新数据就 `python scripts/wm.py ingest` 一条，它会自己串联：提取你说的话 → 去掉重复的 → 拼对话记录 → 统计 → 整理素材 → 挖照见候选 → 生成网页。中间那几步不用你分开跑。

（提取存档是三件"AI 干不了的活"之一，所以留成命令；查旧话、看数据这些你自己读文件就行，不用命令。）

## 注意

1. **首次跑要花的时间和你说过的话有多少成正比**（话多的话约几分钟）；以后只补新的，很快
2. 跑完报告里的"量级提示"（<500 条=了解得还比较粗）要转告用户，管理预期
3. **你的情况文件（portrait.md / habits.md）不自动重写**——你说过的话更新后，按 `references/SOP_蒸馏流程.md` 重新整理才更新
4. **报告页（决定 / 反复提 / 总让 AI 干什么 / AI 怎么看我）也不是自动的**——ingest 只产候选素材，这 4 份内容要按 `references/distill-report-protocol.md` 由 Agent 读语料写 MD，脚本只渲染
4. **照见候选不自动定稿**：ingest 会产出 `data/materials_insights.json`（照见候选），但**不会**自动写 `data/profile/insights.jsonl`——你要按 `references/mirror-protocol.md` 筛一遍、改话术、定稿追加写进去；不定稿，开工的照见永远不会点破
5. 更新完建议跑 `python scripts/wm.py check`（自检），全绿才算完成
6. 探测不到某 agent → 正常（报告"没找到，跳过"），不是错误；新 agent 支持要改 `scripts/detect_agents.py` 的表
7. **DeepSeek Harness（dsh）提取需要 zstandard**（解压 zstd）：`pip install zstandard`；没装时该 agent 自动跳过并提示，不影响其他 agent
