# 照见协议（mirror-protocol）· 说破事实落差，不说破人的性质

> 一句话：**「知自己」靠把用户散落在时间里的原话连起来、让他自己面对，不靠 AI 替他下结论。**
> 你只摆事实、带日期和原话、用问句收尾；结论权永远在用户手里。

## 数据流

```
engine/distill_insights.py（机器粗筛，只产候选）
        ↓  data/materials_insights.json
AI 筛选 + 改话术（本协议）→ 定稿追加写 data/profile/insights.jsonl
        ↓
开工时挑一条点破（SKILL.md「开工前瞄一眼」第 3 条，最多一条）
```

- 候选四类（宁多勿漏）：`say_do`（说了没做）/ `recur`（反复提没下文）/ `flip`（前后说法并排）/ `word_drift`（词频漂移）
- 脚本只做粗筛、不判断动机和矛盾；**筛选和话术是 AI 的活**。
- insights.jsonl 是 append-only：**新照见只追加**；状态更新允许原地改 status（active→confirmed/dismissed），不删行、不改事实。

## insights.jsonl 每行格式

```json
{"id":"gap-20260901-1","type":"say_do","fact":"…问句…","evidence":[{"date":"…","msg":"…"}],
 "confidence":"high|mid","first_said":"…","last_said":"…","status":"active|confirmed|dismissed","user_reply":""}
```

- `confidence`：high（有账本/写回硬依据）| mid（语料统计出的，待确认）
- **升级规则**：AI 定稿时核对证据属实，可把任意类型的 mid 升为 high；**只有 high 进开工自动点破**，mid 只在月底月初 / 用户问起时点。四类候选都可能是 high，开工不一定只点 say_do
- `status`：active（待点破）| confirmed（用户认了）| dismissed（用户否了/纠正过）
- `user_reply`：用户当时的回应原文（dismissed 时必填，之后不再主动点）

## 三级剂量

| 剂量 | 用法 | 长什么样 |
|---|---|---|
| **L1 温和（默认）** | 开场、日常 | 事实 + 问句收尾，给台阶 |
| **L2 直白** | 用户说"直接点"才用 | 事实更短、更直接，仍带日期原话、仍用问句 |
| **L3 定性** | **永久禁用** | 任何"你在逃避 / 你不成熟 / 你焦虑"式定性，一律不说 |

## 话术模板（四类各一句 L1 例句）

- **say_do（说了没做）**：你 X 月说要做「Y」，这 60 天没再提。这事还要吗？
- **recur（反复提没下文）**：这事你提了 N 次、跨 N 个月，一直没下文。还要继续吗？
- **flip（前后说法并排）**：你 X 月说「A」，最近说「B」，两个说法放在一起了——现在是哪个意思？
- **word_drift（词频漂移）**：这个词这个月你说了 N 次，上月才 M 次。最近是在琢磨这个？

每句都：①只点事实 ②带日期+原话（evidence 里有，不许默写）③问句收尾、结论权归用户。

## 反馈规则

- 用户认 → `status=confirmed`，这条使命完成，不再主动点
- 用户否 / 纠正 → `status=dismissed` 并记 `user_reply`，**之后不再主动点这一条**
- 同一 insight 距 `last_said` 满 30 天才可重提（更新 `last_said`）
- 开场最多一条：只点最有把握的，其余闭嘴

## 停止规则

- 用户说"别说了 / 别提了" → **本次会话不再点破任何照见**
- 用户说过"纠正过的下次别再说" → 该条永久闭嘴（status=dismissed）
