---
name: ask-blue
description: 用户问“该用哪个技能”“从哪开始”时，按想拿到的结果指路：写提示词、定项目目标、摸底仓库、修改系统或交接任务。普通任务不必套用技能。
disable-model-invocation: true
allowed-tools: Read
---

# Ask Blue

本仓库的技能分成两条主线加一组外围工具。用户说不清要用什么时，按下面的处境表指路。

## 两条主线

**从零做新项目（intent-chain 八件套）**，顺序固定，前一步的产出是后一步的输入：

1. `/intent-anchor`：把模糊想法追问成 `INTENT.md`（目标、能力取舍、不可妥协项、验收路径）。
2. `/intent-prd`：意图 → PRD。
3. `/intent-design`：PRD → `architecture.md` + `design.md`。
4. `/intent-visual`：仅 UI 项目且没有设计素材时，生成视觉规范和验收基线。
5. `/intent-issues`：按垂直切片拆工单，验收路径全覆盖检查。
6. `/intent-dev`：逐工单 TDD 开发，真实运行证据才能标 done。
7. `/intent-adversarial`：安全攻击实测 + 并发断言 + 性能压测，缺陷闭环。
8. `/intent-verify`：端到端验收 + 漂移核对，链级校验通过才算走完。

**改已有系统**：

1. 项目完全不熟 → `/pathfinder` 只读摸底出项目地图（可选，不跑也行）。
2. `/impact`：影响分析 + 受监督实施，写操作逐项确认。

## 处境 → 入口

| 用户的情况 | 指到 | 之后 |
|---|---|---|
| 想把随口说的需求或已有提示词整理成给另一个 Agent 的指令 | `/prompt-refiner` | 复制提示词给目标 Agent，不走项目链路 |
| 有个项目想法，还没想清为谁做、哪些能力要保留 | `/intent-anchor` | 确认目标和取舍，写入 `intent.md`，供后续 PRD 和开发使用 |
| 只要当前 Agent 根据现有材料直接给结果，例如整理一批客服反馈 | 直接交代任务 | 不必先写提示词或做意图锚定 |
| 已有明确 PRD/规格，要从零实现 | 从 `/intent-issues` 或 `/intent-design` 接入（需补齐上游文件） | intent-chain 后半段 |
| 刚接手陌生仓库，不知道是什么 | `/pathfinder` | 有改动需求时进 `/impact` |
| 熟悉项目，要加功能/修 bug/重构 | `/impact` | 完成后独立验收 |
| UI 项目没有设计稿但要求界面风格 | `/intent-visual` | 登记后由下游门禁验收 |
| 工单开发完，交付前 | `/intent-adversarial` → `/intent-verify` | 缺陷回 `/intent-dev` 修 |
| 把行为规则装进项目 | `/ruleblade` | 装一次长期生效 |

## 不随插件分发的部分

仓库（github.com/betterblueblue/blue-skillhub）里还有：

- `prompt/`：开发卡住、需求变更对账、跨会话交接、独立验收、提交前整理等场景的即贴即用 Prompt。
- `whydump`：Java OOM 排查 utility。
- `eval/`：测评体系与历史跑批记录。

插件用户需要这些时，去仓库取。第三方工具（diagnosing-bugs 等）的入口见仓库 README 的场景表。

## 指路原则

- `/prompt-refiner` 和 `/intent-anchor` 独立使用，不按需求大小排序。只有交付物不清楚时才问：“你想拿到给另一个 Agent 的指令、留给开发的项目决策，还是这件事的结果？”
- 用户的处境落在两条主线之间时（比如"在已有系统上加一个大功能"），先问清"从零建还是改现有"，再选主线；不要替用户猜。
- 指路时给一句话理由（为什么是这个而不是相邻的），并说明用完之后下一步去哪。
