# 言镜（wordmirror）蒸馏 SOP（标准作业流程）

> 本文档是全部"LLM 手工环节"的唯一依据。任何 agent/人重新蒸馏时**必须**按此流程走，
> 产物结构、引用格式、数字口径才算合规。manifest.json 登记的每个产物都能在此找到生成方法。
>
> 版本 1.0 ｜ 2026-08-31 ｜ 从 2026-08-31 的实际蒸馏过程逆向固化

---

## 第 0 步 · 全量重提（脚本，无 LLM）

```bash
cd <skill 包目录>   # skill 装在哪就在哪跑，如 ~/.agents/skills/wordmirror
python engine/extract_all.py          # → data/corpus_all.jsonl（用户侧，10,798 条）
python engine/extract_ai.py           # → data/ai_messages.jsonl（AI 侧，48,868 条）
python engine/build_session_cards.py  # → data/sessions.jsonl（会话卡）
```

**去重（extract_all.py 尚未内置，手工执行）**：

```python
# 同一内容跨 agent 重复提交的，保留首见（按日期排序后）
import json, re
rows = [json.loads(l) for l in open('data/corpus_all.jsonl', encoding='utf-8')]
seen, out = set(), []
for r in sorted(rows, key=lambda x: x['date']):
    k = re.sub(r'\s+', '', r['msg'])[:150]
    if k in seen: continue
    seen.add(k); out.append(r)
with open('data/corpus_dedup.jsonl', 'w', encoding='utf-8') as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + '\n')
```

**入库自检**（三条过了才算数）：
- [ ] 行数合理（口径变化超过 ±30% 要先查是不是提取器坏了）
- [ ] 每行 date 落在已知时间范围（当前 2025-11-09 ~ 今天）
- [ ] 随机抽 10 条目视：是用户口吻，无 `<system-reminder>`、无 AGENTS.md 注入、无工具输出

## 第 1 步 · 数字底座（脚本，无 LLM）

统计口径**必须**用脚本算，禁止 LLM 凭感觉写数字：

```python
# 信号词频率 / 消息长度分布 / 分 agent 特征 / 月度主题 / 主题最后活跃日
# 统一输出到控制台，产物文档引用的每个数字都能在这里复现
```

（待固化：`engine/compute_stats.py`——P2 骨架任务，见文末 TODO）

## 第 2 步 · 画像蒸馏（LLM 环节，核心 SOP）

### 2.1 portrait.md（画像）

固定章节（顺序不可变）：

1. **一句话**——身份 + 阶段 + 特征，40 字内
2. **身份底座**——姓名/年龄/城市/背景/家庭，全部要语料有据
3. **主线表**——时间 | 主线 | 证据强度（目录名+消息量）
4. **当前状态表**——各条线（如求职 5 线）的状态和下一步
5. **工作风格**——每条格式：`风格名——原话（日期）`，**一条风格必须配一条原话**，无原证的直觉判断标注"（推断）"
6. **矛盾/摇摆**——诚实记录，含日期
7. **版本修正记录**——v1→v2 改了什么事实（有则写）

规则：
- **说人话（最高优先级）**：成文禁用发明术语——「语料指纹」「行为范式」「基因库」「光谱」「画像速写」这类比喻一律不写。检验法：这个说法用户自己嘴里出现过吗？没有就换成他会问的那句话（例：「项目基因库」→「这 15 个项目后来都怎么样了」）。此规则来自用户原话「你他妈能不能说人话啊」（35 次明示）
- 引用原话**必须带日期**；写不出日期的引用删掉
- 语料之外的事实（如 jobsearch 目录的文件）标注来源文件路径，与语料证据区分
- "推断"二字只能出现在明确标注处，正文禁止

### 2.2 habits.md（协作规则）

固定章节：
1. 怎么跟我说话（6 条规则，每条可追溯到语料证据）
2. 信号词表——**词 | 频率（脚本算出）| 含义**。频率必须来自第 1 步，禁止手写
3. 协作节奏
4. 技术背景速览

## 第 3 步 · 专题产物（LLM 环节，按需）

| 节 | 产物 | 数据输入 | 结构要求 |
|---|---|---|---|
| 3.1 | 02_我做过的关键决定 | 语料决策句式扫描（`我决定/先不/算了/选X`正则）+ 人工筛 | 每条决定：当时想法（原话+日期）→ 备选 → 后来怎样 |
| 3.2 | 03_我是怎么跟AI说话的 | compute_stats 的动词频率/长度分布 | 三种路数 + 教 AI 干活的原话 + 问得不好的地方（诚实） |
| 3.3 | 04_写给现在的我_九封信 | 月度素材（每月 top3 主题/开场/收尾，脚本提） | 每月一封，用那个月的口气写，**只用那个月的话** |
| 3.4 | 03_我说过要做的事_现在都怎么样了 | stalled_topics.json（最后活跃日） | 搁置（30 天+）/冷却（8-30）/等外部/收线 四档 |
| 3.5 | 05_这15个项目后来都怎么样了 | proj_genes_raw.json（top15 的起源/最长/近况） | 每个项目：时间+条数/怎么开始的/干成了什么/为什么停 |
| 3.6 | 06_我擅长什么不擅长什么 | "被问住"句式扫描 + 自信陈述扫描 | 真拿得出手的/能讲但要收着讲的/别往深了聊的，每级有原话日期 |
| 3.7 | 09_还原我的一天 | 指定日期的全量消息 | 按时段还原 + 那一天放在九个月里看 |

## 第 4 步 · HTML 产物（模板渲染）

数据 json → `templates/` 模板 → `engine/generate_html_pages.py` 渲染 → `products/html/`。
**禁止直接手编 products/html/ 下的文件**（样式改 templates，数据改 json）。
三套设计 token 的来源：awesome-design-md（linear.app / spotify / notion 三套 DESIGN.md）。

## 第 5 步 · 收尾（每次蒸馏必做）

```bash
python engine/self_check.py        # 14 项自检，全绿才继续（--web 连浏览器一起验）
git add -A
git commit -m "蒸馏 YYYY-MM-DD：语料 N 条→M 条，画像/产物更新点简述"
```

- 更新 manifest.json 的 rows 数字和 updated 日期
- 画像有事实修正时，在 portrait.md 版本修正记录里写清 v(n-1)→v(n) 差异

---

## 数字口径备忘（防两套真相复发）

**口径以 data/ 里的实际行数为准，不写死数字**——每次 `ds ingest` 都会因新对话而变化。
引用数字前先数一遍：`wc -l data/corpus_dedup.jsonl`。

| 口径 | 来源 | 2026-08-31 末值 |
|---|---|---|
| 用户原话（去重） | corpus_dedup.jsonl | 6,633（含当日增量） |
| 用户原话（未去重） | corpus_all.jsonl | ~9,900 |
| AI 回复 | ai_messages.jsonl | ~44,200 |
| 会话卡 | sessions.jsonl | 353 |
| agent 覆盖 | manifest.known_gaps | 8 个 |
| bro 频率 | stats_wordfreq.json | 清洗后口径（旧口径 1027 含转录注入，已废弃） |

## TODO（P2 骨架收尾）

- [ ] `engine/compute_stats.py`：把第 1 步的统计固化成脚本（信号词/长度/分agent/月度/搁置主题 一次出全）
- [ ] `engine/distill_materials.py`：把第 3 步的"素材提取"（决策句式/被问住句式/月度切片/项目基因）固化成脚本，LLM 只做最后的成文
- [ ] 去重步骤并入 extract_all.py
