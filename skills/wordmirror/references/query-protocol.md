# 检索协议 · "我之前说过什么"

> 触发场景：用户问自己的历史观点、决定、口头禅、某话题的想法、哪些事没下文。
> 核心原则：**回答里的每一句"我说过 X"都要有日期**，查不到就直说查不到。

## 1. 找数据目录

先读 `references/data-locations.md` 定位本机的 data 目录。默认顺序：
`~/.wordmirror/data/` → 本 skill 上一级的 `../../data/`。

## 2. 检索什么文件

| 想查什么 | 用哪个文件 | 说明 |
|---|---|---|
| 我说过的话（主力） | `data/corpus_dedup.jsonl` | 每行一条：`{agent, date, proj, sid, msg}` |
| 我后来补充确认的事实 | `data/user_writebacks.jsonl` | 口头确认但没在对话里的 |
| 某次对话的来龙去脉 | `data/sessions.jsonl` | 会话卡：我问了什么 + AI 结论 |
| AI 当时回了什么 | `data/ai_messages.jsonl` | 量大，按 sid 关联再查 |

## 3. 检索方法（从简到繁）

**第一层：关键词 grep**（80% 的问题这就够了）

```bash
grep "关键词" <data目录>/corpus_dedup.jsonl
# 多词分别 grep 再取交集；中文直接搜
```

**第二层：时间过滤**（"上个月""7 月的时候"）

```bash
grep '"date": "2026-07' <data目录>/corpus_dedup.jsonl
```

**第三层：主题定位**（"我备考那会儿"）

先按项目目录名 grep proj 字段（如"备考""jobsearch"），再在结果里搜关键词。

**第四层：跑脚本**（复杂问题，比如"我说过要做但没下文的事"）

```bash
python <skill目录>/scripts/ds.py ask "关键词"
# 或全量统计：python <skill目录>/scripts/ds.py ingest 后看 data/stalled_topics.json
```

## 4. 回答格式（给用户看的）

- 先给结论，再给原话引文（带日期和当时的 agent/项目）
- 同一件事前后说法变了 → 两个都摆出来，标注日期，别替用户判断哪个对
- 只有孤证 → 说明"就找到这一条"
- 什么都没搜到 → 直说没找到，不编。这是硬规则

## 5. 典型问法对照

| 用户问 | 实际检索 |
|---|---|
| "我上个月纠结的事后来怎么样了" | 当月语料搜"纠结/犹豫/要不要" → 追踪后续日期同话题 |
| "我对 RAG 的观点是什么" | grep "RAG/向量/检索" → 按时间排，展示观点演化 |
| "我说过要做但没下文的事" | data/stalled_topics.json（按 gap 天数排） |
| "我说话有什么口头禅" | data/stats_wordfreq.json（脚本算好的频率表） |
| "把我 7 月 7 号那天干的事还原出来" | grep '"date": "2026-07-07' → 按会话分组复述 |
