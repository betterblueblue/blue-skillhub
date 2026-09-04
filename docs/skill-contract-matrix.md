# Skill 文档契约矩阵

> 本文件是仓库内所有 Skill 的权威总入口（单份事实来源）。用于回答「有哪些 Skill、什么时候用、怎么触发、允许写什么、产什么、有没有校验器」。
>
> 修改一个 Skill 时，同步核对本矩阵是否仍与 `skills/<name>/SKILL.md` 一致。
>
> 审计日期：2026-09-05（初始为只读审计生成）。随后已按本矩阵落地 frontmatter 统一：14 个 `SKILL.md` 均已显式声明 `disable-model-invocation` 并新增「写入边界」小节（尚未提交 Git）。

## 分类

| 分类 | Skill |
|---|---|
| **链路**（Intent 主链，8 个） | intent-anchor · intent-prd · intent-design · intent-visual（条件）· intent-issues · intent-dev · intent-adversarial · intent-verify |
| **既有**（已有系统，2 个） | pathfinder · impact |
| **工具**（utility，2 个） | vl-vision · whydump |
| **独立**（个人画像，1 个） | wordmirror |
| **自用**（面试辅导，1 个，不提交 Git） | blue-interview |

链路顺序：

```text
intent-anchor → intent-prd → intent-design → intent-visual（仅 UI 项目、无设计素材时）
→ intent-issues → intent-dev → intent-adversarial → intent-verify
```

## 调用方式字段说明

`disable-model-invocation` 决定 Skill 是模型可自动发现还是仅用户显式 `/skill-name` 触发（语义见 `writing-for-agents/SKILL-MECHANICS.md`）：

- **省略或 `false`** = 模型可自动触发；`description` 常驻上下文，作为模型侧触发指针。
- **`true`** = 仅用户手动触发；`description` 面向人，需压成一行摘要，去掉触发词表。

当前状态：**14 个 Skill 均已显式声明该字段**（链路 8 个 `true`；impact / pathfinder / vl-vision / whydump / wordmirror / blue-interview 为 `false`），不再依赖隐式默认。

## 契约矩阵

图例：写入边界为「允许写什么」。✓ = 是；— = 无 / 不适用。

### 链路（8）

| Skill | 触发 | 输入 | 输出 | 写入边界 | refs | 校验器 | 备注 / 冲突 |
|---|---|---|---|---|---|---|---|
| intent-anchor | 意图模糊 / 要求锚定 | 用户想法 | `INTENT.md` | `INTENT.md` | 3 | `intent_validate` | 允许联网（WebSearch/WebFetch）；写入确认未显式统一 |
| intent-prd | anchor 后 | `INTENT.md` | PRD | PRD 文档 | 0 | `prd_validate` | 描述写「PRD」，链路用 `prd.md`，命名需统一 |
| intent-design | prd 后 | `INTENT.md` + PRD | `architecture.md` / `design.md` | 两文档 | 0 | `design_validate` | 正文与 README 细节可能不一致 |
| intent-visual | design 后、UI 且无素材 | INTENT/PRD/arch/design + 参考 | `visual-design.md` + `visual-baseline.html`；回写 INTENT 第 12 节 | 上述文件（含回写 INTENT，已声明） | 5（含 refs/README） | `visual_validate` | 链中唯一用 Edit 回写 INTENT；写入范围已声明 |
| intent-issues | design 后、dev 前 | INTENT/PRD/arch/design | `issues.md` / 工单 | 工单文档 | 0 | `issues_validate` | 轻量档例外只在 README 体现 |
| intent-dev | issues 后 | INTENT/PRD/issues/arch/design | 源码 + 测试 + `dev-record` | 业务代码 / 测试 / 记录 | 0 | `dev_validate` | 授权确认不如 impact 明确；adversarial 插在 dev 与 verify 之间 |
| intent-adversarial | dev 后、verify 前 | INTENT/issues/dev-record/arch | 攻击/压测/并发证据 + `FIX-*` 工单 | `FIX-*` 工单 / 报告（已声明，仅限被测系统） | 0 | `adversarial_validate` | 写 FIX-* 工单已声明；allowed 无 Edit、靠 Write |
| intent-verify | 全部工单完成后 | INTENT/PRD/issues/dev-record/arch/design | 验收记录 / 证据 / 缺陷结论 | 验收文档 | 0 | `verify_validate` | 未列 Edit（Write 够用，需说明） |

### 既有（2）

| Skill | 触发 | 输入 | 输出 | 写入边界 | refs | 校验器 | 备注 / 冲突 |
|---|---|---|---|---|---|---|---|
| impact | `/impact`、影响分析、改字段删表 | 现有代码 / 需求 / 地图 / DB | `change-impact/` 多阶段文档 + 代码实施 | 必须 `确认 Step N`；DB 写默认走外部脚本 | 10 | `impact_validate` | allowed 含任意 SQL 工具但文字限「只读发现」；写保护靠 prompt/hook |
| pathfinder | `/pathfinder`、摸底、领航 | 源码 / 配置 / DB | `change-impact/_project-map.md` + `facts/*.json` | **仅地图 / facts；源码只读（已声明）** | 8 | `pf_validate` | 「项目源码只读」已由「写入边界」明示；allowed 仍含 Write/Edit 属预批准 |

### 工具 / 独立 / 自用（4）

| Skill | 触发 | 输入 | 输出 | 写入边界 | refs | 校验器 | 备注 / 冲突 |
|---|---|---|---|---|---|---|---|
| vl-vision | 识图 / OCR | 图片 | 结构化识图结果 | — | 0 | — | 调外部视觉 API 但未列网络工具；README 有 hooks 门禁；**显式 `disable-model-invocation: false`** |
| whydump | OOM / 堆爆 | histo / GC 日志 | 取证结论 / 建议（写入已声明：确认路径、改参数先确认） | 已声明 | 0 | 无（仅 test） | `pwsh` 与别处工具命名不一致（环境映射）；显式 `disable-model-invocation: false` |
| wordmirror | 「我之前说过 / 记住 / 更新画像」 | 本地话语 / 档案 | 检索答案 / 画像 / 报告 | `~/.wordmirror` 数据（已声明：本地路径 + 用户确认） | 13 | `check_quotes` / `self_check` | 写入范围已声明（本地数据，不上传）；隐私依赖协议约束 |
| blue-interview | 面试 / 简历 / JD / 复盘（**自用，不提交 Git**） | 经历 / JD / 仓库 / 转写 | 回答 / 简历 / profile / 档案 | 已声明（profile / 训练档案 / 简历写入确认的训练目录） | 10 | `extended_validate` 等 | 写入边界已声明；无 README、工具声明过宽仍保留 |

## 横切发现

1. **references 分层不统一**：有 refs 的 6 个（impact 10 / wordmirror 13 / blue-interview 10 / pathfinder 8 / intent-visual 5 / intent-anchor 3）；无 refs 的 8 个（intent-design / dev / issues / prd / verify / adversarial / vl-vision / whydump）。链路中仅 anchor 与 visual 有 references，其余 6 个全靠正文承担。
2. **调用方式已统一**：14 个全部显式声明；链路 8 个 `true`，impact / pathfinder / vl-vision / whydump / wordmirror / blue-interview 为 `false`。
3. **工具声明与行为的边界已逐项声明，残余风险仍在**（`allowed-tools` 是预批准不是白名单，真正的写保护依赖确认 / hook / DB 权限）：
   - `pathfinder`：源码只读已声明；allowed 仍含 Write/Edit，仅地图/facts 可写。
   - `intent-adversarial`：写 `FIX-*` 工单已声明；allowed 无 Edit，靠 Write。
   - `intent-verify`：只写验收记录、不改源码，已声明。
   - `impact`：DB 写保护依赖 prompt/hook + `确认 Step N`，allowed 仍含任意 SQL 工具。
4. **根 README 技能清单不完整**：遗漏 blue-interview、whydump、wordmirror。
5. **唯一无 Skill README 的是 blue-interview**（自用属性，合理）。

## 维护约定

- 本矩阵是权威来源；`SKILL.md`、各 README、校验器、根 README 不得与它冲突。
- 新增 / 删除 / 改触发 / 改写入边界的 Skill，先改本矩阵，再同步 `SKILL.md` 与根 README。
- blue-interview 为自用，**不纳入 Git 提交范围**；本矩阵保留其信息供维护参考。
