# Skill 文档契约矩阵

> 本文件是仓库内所有 Skill 的权威总入口（单份事实来源）。用于回答「有哪些 Skill、什么时候用、怎么触发、允许写什么、产什么、有没有校验器」。
>
> 修改一个 Skill 时，同步核对本矩阵是否仍与 `skills/<name>/SKILL.md` 一致。
>
> 审计日期：2026-09-05（初始为只读审计生成）。随后按本矩阵统一了 frontmatter：当时的 `SKILL.md` 都显式声明了 `disable-model-invocation`，并新增「写入边界」小节（与本矩阵同一次提交 e6affdb）。
>
> 2026-10-26：移除 vl-vision（主流模型已能直接看图）。
>
> 2026-11-01：对照当前各 `SKILL.md` 复核：补上 ask-blue、ruleblade 两行（矩阵现为 15 行：14 个入库技能加自用的 blue-interview），更正 refs 数、wordmirror 的字段与写入范围、链路几行的备注；impact 去掉任意 SQL 预批准；pathfinder / impact 的写入边界写明改进记录的例外。

## 分类

| 分类 | Skill |
|---|---|
| **链路**（Intent 主链，8 个） | intent-anchor · intent-prd · intent-design · intent-visual（条件）· intent-issues · intent-dev · intent-adversarial · intent-verify |
| **既有**（已有系统，2 个） | pathfinder · impact |
| **入口与规则**（2 个） | ask-blue（路由）· ruleblade（律刃安装） |
| **工具**（utility，1 个） | whydump |
| **独立**（个人画像，1 个） | wordmirror |
| **自用**（面试辅导，1 个，不提交 Git） | blue-interview |

链路顺序：

```text
intent-anchor → intent-prd → intent-design → intent-visual（仅 UI 项目、无设计素材时）
→ intent-issues → intent-dev → intent-adversarial → intent-verify
```

## 调用方式字段说明

`disable-model-invocation` 决定 Skill 是模型可自动发现还是仅用户显式 `/skill-name` 触发（语义见 [Claude Code 技能文档](https://code.claude.com/docs/en/skills)）：

- **省略或 `false`** = 模型可自动触发；`description` 常驻上下文，作为模型侧触发指针。
- **`true`** = 仅用户手动触发；`description` 面向人，需压成一行摘要，去掉触发词表。

当前状态：14 个 Skill 显式声明了该字段：`true` 10 个（链路 8 个 + ask-blue + ruleblade），`false` 4 个（impact / pathfinder / whydump / blue-interview）。wordmirror 的 frontmatter 没写这个字段（等同 `false`，模型可自动触发），是 4f60df2 入口瘦身时去掉的。

## 契约矩阵

图例：写入边界为「允许写什么」。✓ = 是；— = 无 / 不适用。

### 链路（8）

| Skill | 触发 | 输入 | 输出 | 写入边界 | refs | 校验器 | 备注 / 冲突 |
|---|---|---|---|---|---|---|---|
| intent-anchor | 意图模糊 / 要求锚定 | 用户想法 | `intent-chain/{链路目录}/intent.md` | 同左（校验器只认这个路径） | 3 | `intent_validate` | 允许联网（WebSearch/WebFetch）；写入确认按 `_common/rules.md`「确认语义」 |
| intent-prd | anchor 后 | `INTENT.md` | `prd.md` | `prd.md` | 0 | `prd_validate` | description 仍只写「PRD」，正文和写入边界已统一为 `prd.md` |
| intent-design | prd 后 | `INTENT.md` + PRD | `architecture.md` / `design.md` | 两文档 | 1 | `design_validate` | refs 为 `deep-module.md`（设计模块前必读）；正文与 README 细节可能不一致 |
| intent-visual | design 后、UI 且无素材 | INTENT/PRD/arch/design + 参考 | `visual-design.md` + `visual-baseline.html`；回写 INTENT 第 12 节 | 上述文件（含回写 INTENT，已声明） | 5（含 refs/README） | `visual_validate` | 链中唯一用 Edit 回写 INTENT；写入范围已声明 |
| intent-issues | design 后、dev 前 | INTENT/PRD/arch/design | `issues.md` / 工单 | 工单文档；决策工单拍板后回写 architecture.md 第 7 节的假设行或 design.md 对应能力节（改前 / 改后给用户确认） | 0 | `issues_validate` | 轻量档单工单直行写在 SKILL.md「轻量档」节；回写用 Edit |
| intent-dev | issues 后 | INTENT/PRD/issues/arch/design | 源码 + 测试 + `dev-record` | 业务代码 / 测试 / 记录；开发中拍板的决策工单：更新 issues.md 里的状态，并按 intent-issues 规则回写设计文档 | 0 | `dev_validate` | 授权确认不如 impact 明确；完成后先交 adversarial 再交 verify；决策工单不进 dev-record |
| intent-adversarial | dev 后、verify 前 | INTENT/issues/dev-record/arch | 攻击/压测/并发证据 + `FIX-*` 工单 | `FIX-*` 工单 / 报告；只打用户确认过的非生产目标 | 0 | `adversarial_validate` | 写 FIX-* 工单已声明；allowed 无 Edit、靠 Write |
| intent-verify | 全部工单完成、adversarial 通过后 | INTENT/PRD/issues/dev-record/arch/design/adversarial-record | 验收记录 / 证据 / 缺陷结论 | 验收文档；改进回流需用户同意并确认路径 | 0 | `verify_validate` | 未列 Edit（Write 够用，需说明）；性能/安全/并发引用 adversarial-record |

### 既有（2）

| Skill | 触发 | 输入 | 输出 | 写入边界 | refs | 校验器 | 备注 / 冲突 |
|---|---|---|---|---|---|---|---|
| impact | `/impact`、影响分析、改字段删表 | 现有代码 / 需求 / 地图 / DB | `change-impact/` 多阶段文档 + 代码实施 | 必须 `确认 Step N`；DB 写默认走外部脚本 | 10 | `impact_validate` | 任意 SQL 工具（`execute_sql` / `query`）2026-11-01 移出 allowed-tools，调用时客户端会问用户；写保护靠 prompt/hook。改进记录只在用户明确要求保存、确认路径后写，写入边界和强制规则 4 已写明这个例外 |
| pathfinder | `/pathfinder`、摸底、领航 | 源码 / 配置 / DB | `change-impact/_project-map.md` + `facts/*.json` | **仅地图 / facts；源码只读（已声明）** | 8 | `pf_validate` | 「项目源码只读」已由「写入边界」明示；allowed 仍含 Write/Edit 属预批准。改进记录同 impact，写入边界和硬性规则 2 已写明这个例外 |

### 入口与规则（2）

| Skill | 触发 | 输入 | 输出 | 写入边界 | refs | 校验器 | 备注 / 冲突 |
|---|---|---|---|---|---|---|---|
| ask-blue | 用户手动 `/ask-blue` | 用户的处境描述 | 指到对应技能和先后顺序（只在对话里） | 不写文件（allowed-tools 只有 Read）；没有「写入边界」节 | 0 | — | 只有 SKILL.md，没有 README；设为 `true`，description 却带触发词，和上面「`true` 去掉触发词表」的约定不一致 |
| ruleblade | 用户手动 `/ruleblade` | 用户主要用的模型 | 把 `CLAUDE.full.md` 或 `CLAUDE.lite.md` 写进项目根 `CLAUDE.md`（Codex、dsh 写 `AGENTS.md`），或用户选的全局文件 | 征得同意后写；目标文件已存在时不直接覆盖；没有「写入边界」节 | 0 | — | description 带触发词，同 ask-blue |

### 工具 / 独立 / 自用（3）

| Skill | 触发 | 输入 | 输出 | 写入边界 | refs | 校验器 | 备注 / 冲突 |
|---|---|---|---|---|---|---|---|
| whydump | OOM / 堆爆 | histo / GC 日志 | 取证结论 / 建议（写入已声明：确认路径、改参数先确认） | 已声明 | 0 | 无（仅 test） | `pwsh` 与别处工具命名不一致（环境映射）；显式 `disable-model-invocation: false` |
| wordmirror | 「我之前说过 / 记住 / 更新画像」 | 本地话语 / 档案 | 检索答案 / 画像 / 报告 | 全局数据目录（`WORD_MIRROR_HOME` → `~/.wordmirror/bind.json` → `~/.wordmirror/`）和项目层 `.wordmirror/`；写在 SKILL.md「数据在哪」节，没有单独的「写入边界」节 | 15 | `check_quotes` / `self_check` | 本地数据，不上传；隐私依赖协议约束；frontmatter 没写 `disable-model-invocation` |
| blue-interview | 面试 / 简历 / JD / 复盘（**自用，不提交 Git**） | 经历 / JD / 仓库 / 转写 | 回答 / 简历 / profile / 档案 | 已声明（profile / 训练档案 / 简历写入确认的训练目录） | 10 | `extended_validate` 等 | 写入边界已声明；无 README、工具声明过宽仍保留 |

## 横切发现

1. **references 分层不统一**：有 refs 的 7 个（impact 10 / wordmirror 15 / blue-interview 10 / pathfinder 8 / intent-visual 5 / intent-anchor 3 / intent-design 1）；无 refs 的 8 个（intent-prd / issues / dev / adversarial / verify / whydump / ask-blue / ruleblade）。链路中 anchor、design、visual 有 references，其余 5 个全靠正文承担。
2. **调用方式**：14 个显式声明（`true` 10 个，`false` 4 个）；wordmirror 没写，等同 `false`。
3. **工具声明与行为的边界已逐项声明，残余风险仍在**（`allowed-tools` 是预批准不是白名单，真正的写保护依赖确认 / hook / DB 权限）：
   - `pathfinder`：源码只读已声明；allowed 仍含 Write/Edit，仅地图/facts 可写（改进记录的例外见上表）。
   - `intent-adversarial`：写 `FIX-*` 工单已声明；allowed 无 Edit，靠 Write。
   - `intent-verify`：只写验收记录、不改源码；改进回流要用户同意并确认路径，已声明。
   - `impact`：DB 写保护依赖 prompt/hook + `确认 Step N`；任意 SQL 工具已移出 allowed，调用时客户端会问用户。
4. **根 README 技能清单**：入库技能都已列出（whydump、wordmirror 在安装说明和仓库结构里）；只缺自用的 blue-interview，合理。
5. **没有技能 README 的**：blue-interview（自用，合理）和 ask-blue（只有 SKILL.md）。
6. **`skills/_common` 不是技能**，随插件分发（见 ADR-004）：共享规则 `rules.md`，以及链路各校验器引用的共享模块（`chain_validate` / `markdown_parser` / `issue_types` / `defect_status` / `d5_check` / `term_check`）。

## 维护约定

- 本矩阵是权威来源；`SKILL.md`、各 README、校验器、根 README 不得与它冲突。
- 新增 / 删除 / 改触发 / 改写入边界的 Skill，先改本矩阵，再同步 `SKILL.md` 与根 README。
- blue-interview 为自用，**不纳入 Git 提交范围**；本矩阵保留其信息供维护参考。
