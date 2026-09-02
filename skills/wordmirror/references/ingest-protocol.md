# 更新协议 · "重新提取 / 你的情况过期了"

> 触发场景：用户要求数据更新、你的情况过期了、换机器要初始化。
> 原则：**你（Agent）按下面 8 步逐步执行**，每步一个脚本，顺序不能乱（去重必须排在统计/素材之前，否则数字会虚高）。重复跑不会重复入库（按内容去重）。

## 8 步（每步跑完、看到产物再往下）

| 步 | 命令 | 干什么 | 产物 |
|---|---|---|---|
| 1 | `python scripts/detect_agents.py` | 探测哪些 agent 有存档 | 报告（哪个能采、哪个跳过） |
| 2 | `python scripts/extract_all.py` | 提取你说的话 | `data/corpus_all.jsonl` |
| 3 | `python scripts/extract_ai.py` | 提取 AI 的回复 | `data/ai_messages.jsonl` |
| 4 | `python scripts/dedup.py` | 去重 | `data/corpus_dedup.jsonl` |
| 5 | `python scripts/build_session_cards.py` | 拼会话卡 | `data/sessions.jsonl` |
| 6 | `python scripts/compute_stats.py` | 词频/长度/分 agent 特征 | `data/stats_*.json` |
| 7 | `python scripts/distill_materials.py` 和 `distill_insights.py` | 挖素材 + 照见候选 | `data/materials_*.json` |
| 8 | `python scripts/render.py all` | 出全 10 页 HTML | `products/html/` |

> 数据根目录经环境变量 `WORD_MIRROR_HOME` 指定；脚本自己会找到 `~/.wordmirror` 或绑定位置（见 `data-locations.md`）。

## 注意

1. 首次跑的时间和你话量成正比（话多约几分钟）；以后只补新的，快。
2. 每步看脚本输出：会打印产物条数；条数比上次暴跌（>30%）要怀疑提取器坏了，别闷头往下跑。
3. **portrait.md / habits.md 不自动重写**——更新后按 `references/SOP_蒸馏流程.md` 重新整理。
4. **报告页（决定/反复/任务/AI看/各AI样子/这几个月）不自动写**——按 `references/distill-report-protocol.md` 由你读语料写 6 份 MD。
5. **照见候选不自动定稿**——按 `references/mirror-protocol.md` 筛一遍写 `insights.jsonl`。
6. 更新完跑 `python scripts/self_check.py` 自检，全绿才算完。
7. 探测不到某 agent 是正常（报告"没找到，跳过"）；新 agent 改 `scripts/detect_agents.py` 的表。
8. DeepSeek Harness（dsh）提取需要 zstandard（`pip install zstandard`）；没装自动跳过并提示。
