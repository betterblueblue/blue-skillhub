# 三个 Skill 后续优化路线图

> 日期：2026-06-25
> 基线：v3.8.1 协议 + v4 干净环境盲测结论
> 目的：记录已识别的优化方向，供后续会话继续展开
> 关联文档：[docs/model-eval-2026-06-25.md](archive/2026-06/model-eval-2026-06-25.md)、[docs/skill-improvement-2026-06-24.md](archive/2026-06/skill-improvement-2026-06-24.md)、[eval/runs/BLIND-TEST-FINAL-CONCLUSION.md](../eval/runs/BLIND-TEST-FINAL-CONCLUSION.md)

---

## 当前状态速览

三个 skill 经过 v1→v4 四轮盲测 + 第三轮战略定位验证实验，协议和脚本闸门已比较扎实：

| skill | L1 基线分 | 盲测轮次 | 安全闸负向测试 | 脚本闸门 | 协议改进项 |
|-------|:---------:|:--------:|:-------------:|:-------:|:---------:|
| pathfinder | 97.7 | 4 轮 + 战略验证 | ✅ 7/7 | ✅ pf_validate.py V1-V6（V6 含 facts 内容合理性校验） | 8 项 |
| impact | 89.3 → 95.5（合并后） | 4 轮 + 战略验证 | ✅ 7/7 | ✅ impact_validate.py V1-V7（V7 判档合理性检查） | 8 项 + v4.2 闸门 |

> **注**：impact-pro 已于 2026-06-26 合并归档为 `impact-pro.archived/`，单一 SKILL.md + profile 注入替代双 skill 模式。

**第三轮战略定位验证实验结论**（2026-06-26，3 cell × 3 case 盲测，GLM-5.2 评审）：
- Composer 2.5 + skill 均分 79.0，Opus 4.x + CLAUDE.md 均分 73.0（Δ=6.0）— skill 在证据精度维度领先 +10 分，深度推理维度 Opus 占优
- Step 3.7 Flash + skill v4.1 均分 79.7（v3.8 baseline 59.7，+20.0）— 过早收敛和证据遗漏已修复，判档错误由 V7 脚本闸门兜底
- 详见 `eval/runs/strategic-verify-2026-06-26/JUDGE-RESULT.md`

以下优化方向按优先级排列，每项标注了现状、做什么、价值和预估难度。

---

## 优先级 1：补上 Phase 5 执行阶段的盲测 ✅ 已完成（P1 已修复 + 补测通过）

> **状态**：2026-06-25 已完成首轮 + 补测。4 case (E1-E4) 均走完 Phase 1-5，实际写代码、跑测试、产出 preflight + 执行记录。0 P0 / 2 P1。
> - E1 P1：Prisma schema 编辑未标高风险 → **已修复**（SKILL.md + phase-5-execution.md 加 ORM schema 高风险标注）
> - E2 P1：V1-only 连续 3 个写入 Step 未暂停 → **已修复**（phase-5-execution.md 加「每步验证提醒」）
> - E4 补测：V1-only 计数 ✅ 正确触发暂停（98 分，0 P0 / 0 P1）
> - E3 正面发现：模型正确发现 email 已存在并降级 light
> 详见 T11（impact）、T53/T54（impact-pro）。

### 现状

6 个盲测 case（B1-B6）全部只测到 Phase 4（文档输出），Phase 5 实际写操作完全没在盲测中验证。Step 3.7 Flash 在 B1/B2 判 light 后直接产出 `040-light.md` 就结束了，没有走到 Phase 5。

Phase 5 的安全闸在 L1 e2e 中验证过（T07/T09 负向测试 7/7 PASS），但盲测场景下"模型自己判 light 然后就不写代码"的路径没有被验证——如果模型错误判 light，Phase 5 的安全闸根本没有机会触发。

### 做什么

设计 2-3 个 full 场景的盲测 case，让模型走到实际执行（写代码、跑测试），验证：

- 逐 Step 确认（`确认 Step N`）是否严格执行
- V1-only 连续计数（连续 3 个写入 Step 只达 V1 静态验证即暂停）是否触发
- 高风险拦截清单（10 类不可逆操作）是否命中
- 执行记录（`090-execution-record.md`）是否随 Step 补齐
- 模型在 full 场景下是否会"判 full 但偷懒不执行"

### 价值

这是目前最大的验证空白。分析阶段做得再好，执行阶段如果模型绕过安全闸，前面全白费。

### 预估难度

中。需要设计能走到 Phase 5 的 case（不能太简单否则判 light，不能太复杂否则模型跑不完），准备可写操作的测试项目，评审方式也要从"读产出文件"升级为"读代码改动 + 跑测试"。

---

## 优先级 2：给 impact / impact-pro 加脚本闸门 ✅ 已完成

> **状态**：2026-06-25 已完成。`impact_validate.py` 已实现，L1 全量回归 13 case 全 0 FAIL。详见 T10（impact）、T52（impact-pro）。

### 现状

pathfinder 有 `pf_validate.py`（V1-V6 六项检查），在写入 `_project-map.md` 前必须运行，exit code ≠ 0 禁止写入。这是 v4 中最有效的改进之一——P1-A 从假 PASS 变成真 PASS。

但 impact 和 impact-pro 没有类似的输出验证脚本。模型判 light 还是 full、产出文件够不够、需求文档有没有混入技术细节，完全靠模型自觉。DeepSeek 在 B3 产出 1 个混合内容的 context-pack 就交差了，没有任何机制拦截。

### 做什么

给 impact / impact-pro 加一个 `impact_validate.py`，在 Phase 4 文档输出后、提交用户确认前运行，检查：

| 检查项 | 检查内容 | 失败动作 |
|--------|---------|---------|
| 文件完整性 | full 场景是否产出了 000/010/020/030 四个文件；light 场景是否产出了 040-light.md | 报 FAIL，阻止提交用户确认 |
| 需求文档边界 | 010-requirements.md 是否包含禁止出现的技术细节（表名、类名、文件路径、代码片段、字段类型定义） | 报 WARN，提示模型移到 020-design.md |
| 方法名标记 | 030-implementation.md 中引用的已有方法名是否有 grep 验证标记 | 报 WARN，提示模型补预检 |
| 判档决策表 | light/full 定级是否附了"判档决策表"（见优先级 3） | 报 WARN，提示模型补表 |

### 价值

pathfinder 的 Script Gate 是经过验证的模式。impact 系列目前完全没有这层防线，产出质量完全取决于模型能力。加脚本闸门可以把"靠模型自觉"变成"靠脚本拦截"，对弱模型尤其有效。

### 预估难度

中低。pathfinder 的 `pf_validate.py` 已有成熟实现可参考，检查逻辑比 pathfinder 简单（不需要检查 Mermaid 图、SVG 安全等）。主要工作量在确定检查项的阈值和失败动作。

---

## 优先级 3：判档决策证据化 ✅ 已完成

> **状态**：2026-06-25 已完成。所有 full case 的 context-pack 均含「判档决策表」，L1 全量回归验证有效。G1 基线 P1（判档自相矛盾）已修复。详见 T10、T52。

### 现状

优化 7（覆盖范围语义核查）对弱模型不生效——Step 3.7 Flash 和 DeepSeek 都能识别覆盖缺口，但都不会因此改变判档。v4 干净环境确认这是模型推理能力的硬限制，协议层面无法强制模型"推理正确"。

### 做什么

换一个思路：不要求模型"推理正确"，而是要求模型"把推理过程写出来让人审查"。在 light/full 定级时强制输出一张"判档决策表"：

| 用户原话关键词 | 现有实现覆盖范围 | 缺口 | 判档 |
|--------------|---------------|------|------|
| "每次接口请求" | LogAspect 仅覆盖 @Log 注解接口 | 约 63 个端点未覆盖 | full |

规则：
- 表中每一行对应用户原话中的一个关键需求描述
- "现有实现覆盖范围"一栏必须基于代码核查填写，不能写"全部覆盖"了事
- "缺口"一栏如果没有缺口写"无"，有缺口必须量化
- 如果"缺口"非空但判 light，表后必须附理由（"缺口不影响核心场景"等）

### 价值

把"模型脑子里的推理"变成"可审查的文本"，用人工复核补上 L4 层（关联推理改变决策）的缺口。这不解决模型能力问题，但能降低漏判风险——人工一眼就能看出"写了缺口但还是判 light"的矛盾。

### 预估难度

低。只需要在 SKILL.md Phase 2.5 / Phase 3.5 加一段表格模板要求，不需要改脚本。可以和优先级 2 的脚本闸门配合（判档决策表缺失时报 WARN）。

---

## 优先级 4：扩大盲测覆盖面 — ✅ 已完成（执行 + 评审）

> **状态**：2026-06-25 case 设计 + Composer 2.5 执行 + 评审全部完成。
> - B7：go-admin + impact-pro，Go/Gin/GORM 栈首次盲测（增量变更）— **71/80** — V1（Go 未安装）
> - B8：prisma-express-ts + impact-pro，破坏性变更（改 API 契约）— **71/80** — V2（build 通过）
> - B9：ruoyi-vue + impact-pro，破坏性变更（删字段）— **68/80** — V2（mvn compile 通过）
> - 三案平均 70/80（87.5%），0 P0 否决
> - ⚠ B8 源项目有预存变更（phone 校验相关），评审时已剔除
> - ⚠ B9 遗漏 SysUser.java toString 中的 remark 引用（P1）
> - 破坏性变更保护流程 100% 触发（B8/B9 均执行：只读搜索→回显破坏面→追问决策）
> - go-gin-gorm profile 首测通过，GORM tag 修改正确识别为高风险
> - 归档总结：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/SUMMARY.md`
> - 评分卡：`eval/runs/blind-b7-b9-2026-06-25/cell-C1/SCORECARD.md`
> - 详见 `eval/cases/blind-b7-b9/`

### 现状

此前所有盲测（B1-B6, E1-E4）全是"加"场景（加字段、加功能）。破坏性变更（删字段、改 API 契约）是风险最高的场景，恰恰最需要 skill 兜底，但没有盲测覆盖。

技术栈方面，go-gin-gorm profile 从未被盲测过。E2 已覆盖 FastAPI/SQLModel，E3 覆盖了 RuoYi（但用的是 impact，不是 impact-pro）。

### 做什么

**补技术栈覆盖**（合并后 3 case 覆盖 3 个新维度）：

| 新 case | 技术栈 | 验证目标 |
|---------|-------|---------|
| B7 | Go/Gin/GORM（go-admin） | go-gin-gorm profile 在盲测下的表现（首次） |
| ~~B8~~ | ~~FastAPI/SQLModel~~ | ~~由 E2 Phase 5 盲测替代~~ |
| B9 | Java/Spring/MyBatis（RuoYi）+ impact-pro | java-spring-mybatis profile 在 impact-pro 下的表现（E3 用的是 impact） |

**补变更类型覆盖**（B8/B9 同时覆盖技术栈和破坏性变更）：

| 新 case | 变更类型 | 验证目标 |
|---------|---------|---------|
| ~~B10~~ → B9 | 删字段（破坏性变更） | 删除字段时反向引用检查是否覆盖所有消费者；破坏性请求保护是否触发 |
| ~~B11~~ → B8 | 改 API 契约（重命名字段） | generated client / OpenAPI / SDK 同步检查；消费者协调 |
| ~~B12~~ | ~~改状态机~~ | 暂缓，当前测试项目无状态机场景 |

### 价值

降低样本偏差。此前所有 case 全是增量变更，不能代表所有场景。破坏性变更是风险最高的场景，恰恰最需要 skill 兜底，但目前没有盲测覆盖。

### 预估难度

中。需要找合适的测试项目（或复用已有 test-projects），设计不预设答案的 case prompt。每个 case 约 2-3 小时（设计 + 跑 + 评审）。

---

## 优先级 5：行号精度抽查机制 ✅ 已完成

> **状态**：2026-06-25 已完成。`impact_validate.py` V6 检查已实现（随机抽 3 条行号引用，验证文件存在+行号在范围内+打印行内容供人工复核），L1 全量回归 6 case 全 0 FAIL。

### 现状

Composer 2.5 的行号偏差（1-10 行）是 v4 中唯一没有被协议覆盖的人工复核点。Step 3.7 Flash 行号精度极高（零偏差），但 Composer 2.5 仍有偏差。

### 做什么

两种方案：

**方案 A（脚本抽查，配合优先级 2）**：在 `impact_validate.py` 中加一个抽查步骤——从 context-pack 或 design 文档中随机抽取 3 条行号引用，用 `sed -n 'Xp' file` 验证行内容是否和文档描述匹配。偏差超过 3 行报 WARN。

**方案 B（模型自标注）**：要求模型在 context-pack 中对每条行号引用标注"行号核查置信度"——高（已打开文件确认）、中（grep 确认存在但未核对行号）、低（基于搜索结果推断）。人工复核时只查"中"和"低"。

### 价值

行号偏差不致命（人工打开文件就能纠正），但影响效率。如果能在协议层自动抽查或标注置信度，可以减少人工复核成本。

### 预估难度

低。方案 B 纯协议改动，方案 A 需要配合优先级 2 的脚本闸门。

---

## 优先级 6：弱模型降级策略 ✅ 已完成

> **状态**：2026-06-25 已完成。产出完整性自检规则已在 SKILL.md 中，L1 全量回归中 full case 均产出完整四文件。详见 T10、T52。

### 现状

DeepSeek 在 impact/impact-pro 上产出严重不足（B3 只产出 1 个混合内容的文件），但协议没有"产出不足时怎么办"的机制。模型产出 1 个文件就当完成任务了。

### 做什么

在 Phase 4 文档输出后加一个"产出完整性自检"步骤：

```
### 产出完整性自检（Phase 4 文档输出后执行）

如果本次定级为 full，检查以下文件是否都已产出：
- 000-context-pack.md
- 010-requirements.md
- 020-design.md
- 030-implementation.md

如果缺少任一文件：
1. 不得提交用户确认
2. 在已有产出的文件头部标注"产出不完整"
3. 输出提示："本次分析产出不完整，缺少 [文件列表]。
   可能原因：执行模型产出能力有限。
   建议：换更强模型重跑，或人工补齐缺失文档。"
```

### 价值

不强迫弱模型做超出能力的事，但至少让它"知道自己没做完"，而不是产出 1 个文件就当完成任务。对 DeepSeek 这类"单点强、链路弱"的模型尤其有效。

### 预估难度

低。纯协议改动，可以和优先级 2 的脚本闸门配合（文件完整性检查报 FAIL）。

---

## 优先级 7：pathfinder 地图过期检测自动化 ✅ 已完成

> **状态**：2026-06-25 已完成。两个 skill 的 `references/phase-2-context-discovery.md` 均已实现完整的 Step A/B/C 地图过期检测流程（commit 比对 → 过期影响评估 → 记录到 Context Pack）。模板 `000-context-pack.md` 第 1 节已有 `项目地图状态` 字段。

### 现状

pathfinder 地图头部记录了 git HEAD，impact 读地图时会检查 HEAD 是否一致。但这个检查依赖模型自觉——如果模型不读地图头部的 HEAD 或不对比当前 git HEAD，就会用过期地图做分析。

### 做什么

在 impact / impact-pro 的 Phase 2（项目背景构建）中，如果读取了 `_project-map.md`，强制运行一个 `check_map_freshness` 步骤：

1. 读取地图头部的 `git HEAD`
2. 运行 `git rev-parse --short HEAD` 获取当前 HEAD
3. 如果不一致，在 context-pack 中标注"地图已过期（地图: xxx，当前: yyy）"
4. 提示用户："项目地图可能已过期，建议重新运行 `/pathfinder` 更新，或确认过期部分不影响本次分析"

### 价值

地图过期是 pathfinder → impact 交接中的常见风险。项目代码变了但地图没更新，impact 会基于过期的安全认知做判断。自动化检测可以消除这个风险。

### 预估难度

低。纯协议改动，加几行检查步骤。pathfinder 的 facts/git.json 已经提供了 HEAD 信息，impact 只需要读并对比。

---

## 优化项优先级总览

| 优先级 | 优化项 | 类型 | 预估难度 | 依赖 | 状态 |
|:------:|--------|------|:--------:|------|:----:|
| 1 | Phase 5 执行阶段盲测 | 测试补全 | 中 | 无 | ✅ 完成（4 case, 2 P1 已修复 + 补测通过） |
| 2 | impact/impact-pro 脚本闸门 | 协议+脚本 | 中低 | 无 | ✅ 已完成 |
| 3 | 判档决策证据化 | 协议 | 低 | 可选配合优先级 2 | ✅ 已完成 |
| 4 | 扩大盲测覆盖面 | 测试补全 | 中 | 无 | ✅ 完成（B7-B9 执行 + 评审，平均 87.5%，0 P0） |
| 5 | 行号精度抽查机制 | 协议+脚本 | 低 | 可选配合优先级 2 | ✅ 已完成（V6 在 impact_validate.py 中） |
| 6 | 弱模型降级策略 | 协议 | 低 | 可选配合优先级 2 | ✅ 已完成 |
| 7 | pathfinder 地图过期检测 | 协议 | 低 | 无 | ✅ 已完成（在 references 中） |

**建议执行顺序**：

1. ~~先做优先级 2（脚本闸门）~~ ✅ 已完成
2. ~~同步做优先级 3（判档决策证据化）~~ ✅ 已完成
3. ~~优先级 6（弱模型降级策略）~~ ✅ 已完成（与优先级 2 配合）
4. ~~然后做优先级 1（Phase 5 盲测）~~ ✅ 完成（首轮 2 P1 → 修复 → 补测 E4 通过 98 分）
5. ~~最后做优先级 4（扩大覆盖面）~~ ✅ 完成（B7-B9 执行 + 评审，平均 87.5%，0 P0）
6. ~~优先级 5（行号精度抽查）~~ ✅ 已完成（V6 在 impact_validate.py 中）
7. ~~优先级 7（地图过期检测）~~ ✅ 已完成（在 references 中）
8. ~~优先级 4 评审~~ ✅ 完成（评分卡在 `eval/runs/blind-b7-b9-2026-06-25/cell-C1/SCORECARD.md`）
9. ~~B9 修复~~ ✅ 完成（SysUser.java toString remark 引用已删除，mvn compile 通过）
10. ~~B8 干净重跑~~ ✅ 完成（干净副本重跑 name→fullName，11 文件 34 行，tsc --noEmit 通过）

**所有 7 项优化方向均已完成。**

---

## 附录：v4 后仍需人工复核的点

以下 7 项是 v4 干净环境后仍然无法靠协议内置、必须人工复核的点。截至 v4.2，多项已由脚本闸门兜底，复核负担显著下降：

| # | 复核项 | 协议/闸门覆盖状态 | 复核方式 |
|---|--------|----------------|---------|
| 1 | 判档是否正确 | ✅ V7 脚本闸门兜底（全量词覆盖门禁 FAIL + 过度/不足判档 WARN） | 闸门拦截后人工确认 WARN 是否接受 |
| 2 | 行号是否准确 | ✅ V6 脚本闸门抽查 3 条（impact）/ V1 全量验证（pathfinder） | 闸门 PASS 后仍建议抽查关键行号 |
| 3 | API 方法名是否存在 | ✅ V3 脚本闸门检查验证标记（WARN） | 闸门 WARN 时 grep 确认 |
| 4 | 影响链是否覆盖核心场景 | ⚠️ 协议有用户场景覆盖验证，但弱模型仍可能基于错误假设排除文件 | 对照用户原话确认入口场景的完整路径 |
| 5 | 需求文档是否渗入技术细节 | ✅ V2 脚本闸门检查（WARN） | 闸门 PASS 后基本无需额外复核 |
| 6 | 跨文件逻辑一致性 | ⚠️ 协议自检仅覆盖 pathfinder 的认证-鉴权 | 重点查认证链路：JWT payload 取了哪些字段，下游用了哪些字段 |
| 7 | Phase 5 执行是否按 Step 确认 | ✅ Phase 5 盲测已验证（4 case 均按 Step 确认执行） | 无需额外复核 |

**v4.2 更新**：第 1 项从"协议补不了"升级为"V7 脚本闸门兜底"——全量词场景无覆盖分析直接 FAIL 拦截，过度/不足判档报 WARN 提醒人工确认。第 2、3、5、7 项均已有脚本闸门或盲测验证覆盖。剩余第 4、6 项仍需人工复核。

---

## 第二轮优化（2026-06-26 评审后）

> 基于 [docs/skill-review-2026-06-26.md](skill-review-2026-06-26.md) 的系统性评审，识别出 6 项优化方向。以下记录各项状态。

### 优化总览

| # | 优化项 | 优先级 | 状态 | 证据 |
|---|--------|:---:|:---:|------|
| 1 | 合并 impact / impact-pro | P0 | ✅ 完成 | commit `f297753` — impact-pro 已归档为 `impact-pro.archived/`，单一 SKILL.md + profile 注入 |
| 2 | 增加快速通道（trivial exit） | P1 | ✅ 完成 | T1 case 验证：跳过 Phase 2.5-3.5，仍走 Phase 2 + Phase 4 light + Phase 5 preflight |
| 3 | 规则分层加载（Progressive Disclosure） | P1 | ✅ 完成 | `references/` 已重构为 phase-1-intent / phase-2-context-discovery / phase-2.5-risk-triage / phase-4-output / phase-5-execution，正文精简至 ~150 行 |
| 4 | 提升 profile 覆盖度 | P2 | ⏳ 待办 | 见下方详细计划 |
| 5 | vl-vision 定位决策 | P3 | ⏸ 暂不降级 | 保持现状，不纳入本轮 |
| 6 | pathfinder 认证-鉴权自检泛化 | P3 | ✅ 完成 | SKILL.md 步骤 0 已有机制检测（JWT/Session/API Key/OAuth/无认证），无认证时跳过自检 |

### L1 合并后回归验证

> commit `7f2e6c9` | runner: Composer 2.5 | judge: GLM-5.2

- 11 case × 0 P0 × 0 P1，契约全 PASS，均分 95.5
- 合并后单一 skill 覆盖完整，快速通道 + profile 动态加载 + Phase 5 执行均正确工作
- ⚠ 2 个黄线：R3N 文档极简（70 分）、G1/G2 文档偏简
- ⚠ runner_model 与基线不一致（composer vs opus），不建议直接作为新基线
- 详见 `eval/runs/2026-06-26-impact@3b3148b/scorecards/_regression-summary.md`

### P2 详细计划：提升 profile 覆盖度

当前 9 个 profile 中仅 `java-spring-mybatis` 和 `node-express-prisma` 到 Level 2，其余仍在 Level 1。选择 3 个使用频率高的 profile 推到 Level 2：

| profile | 当前等级 | 已有验证基础 | 晋级所需 |
|---------|:---:|------|------|
| `go-gin-gorm` | Level 1 | G1/G2 case + B7 盲测 | 2 个真实项目 full+light 实跑 + commands 验证 + gap 修复 |
| `python-fastapi-sqlmodel` | Level 1 | F1/F3 case + E2 Phase 5 盲测 | 同上 |
| `frontend-nextjs` | Level 1 | T11/T17/round5 验证 | 同上 |

**每个 profile 晋级需要：**
- 2 个真实项目 full + light 实跑
- commands 实际可执行验证
- 发现的 gap 修复并回归

**预期收益：**
- "多栈"从 2/9 到 5/9 覆盖，名副其实
- 用户在 Go/Python/Next.js 项目上使用时 profile 规则更准确
- 评测时这些栈的 case 能真正验证 profile 注入效果

---

## 第三轮优化：战略定位验证实验（2026-06-26 启动）

> 基于 [docs/skill-review-2026-06-26.md](skill-review-2026-06-26.md) §6 提出的战略定位假说——"用流程结构弥补弱模型的 meta-reasoning 缺口"，设计 5 步实验计划验证并修复。
> 实验设计文档：[eval/runs/strategic-verify-2026-06-26/README.md](../eval/runs/strategic-verify-2026-06-26/README.md)

### 当前状态（2026-06-26 更新）

**第三轮 5 步全部完成。** 实验结论：skill 在证据精度维度领先（+10 分），深度推理维度有上限（Opus 占优），弱模型判档错误由 V7 脚本闸门兜底。

实验回顾——3 个 cell 的配置：

| Cell | 模型 | 条件 | Prompt 文件 | 验证目标 |
|------|------|------|------------|---------|
| P0-A | Composer 2.5 | CLAUDE.md + /impact skill（v4.1 合并版） | `PROMPT-P0A-composer-skill.md` | 性价比模型 + skill 的分析质量 |
| P0-B | Opus 4.x | CLAUDE.md 仅行为准则（不加载 skill） | `PROMPT-P0B-opus-noskill.md` | 强模型基线（战略定位对照） |
| P1 | Step 3.7 Flash | CLAUDE.md + /impact skill（v4.1 合并版） | `PROMPT-P1-step-skill.md` | v4.1 协议是否修复弱模型问题 |

3 个 case（复用 V7 模糊 prompt）：
- B1'：并发登录限制（RuoYi-Vue，预期 full）
- B2'：请求体大小限制（prisma-express-ts，预期 light）
- B3'：邮箱验证强制检查（prisma-express-ts，预期 full）

V7 baseline 数据（用于对比）：

| Cell | 模型 | 条件 | B1' | B2' | B3' | 均分 |
|------|------|------|:---:|:---:|:---:|:---:|
| V7-C3 | Composer 2.5 | noskill | 70 | 72 | 71 | 71.0 |
| V7-C4 | Composer 2.5 | skill v3.8 | 84 | 83 | 84 | 83.7 |
| V7-C5 | Step 3.7 Flash | noskill | 49 | 53 | 44 | 48.7 |
| V7-C6 | Step 3.7 Flash | skill v3.8 | 75 | 57 | 47 | 59.7 |

### 后续 5 步计划

#### 第 1 步：P0 对照实验 + P1-Step 弱模型重跑（并行，只读实验）— ✅ 已完成

- **做什么**：3 个 cell 并行执行，各跑 3 个 case（B1'/B2'/B3'），只做影响分析 + 文档输出，不进入 Phase 5 执行
- **自问自答模式**：skill 组不等待人工回答，自行做合理假设并标注 `[假设]`
- **输出路径**：`test-projects/<project>/change-impact/p0a-composer-skill|p0b-opus-noskill|p1-step-skill/<case-id>/`
- **验证方式**：3 个 cell 全部完成后，启动评审 prompt（GLM-5.2 盲测评审 9 份产出）
- **Prompt 文件**：`eval/runs/strategic-verify-2026-06-26/PROMPT-P0A-composer-skill.md` / `PROMPT-P0B-opus-noskill.md` / `PROMPT-P1-step-skill.md`
- **评审 prompt**：`eval/runs/strategic-verify-2026-06-26/JUDGE-PROMPT.md`

#### 第 2 步：分析两个实验结果 — ✅ 已完成

> GLM-5.2 盲测评审完成。P0：Δ=6.0（⚠️ 接近但有差距）；P1：均分 59.7→79.7（+20.0），过早收敛和 passport.ts 修复确认，B2' 判档未修复。
> 评审结果：`eval/runs/strategic-verify-2026-06-26/JUDGE-RESULT.md`

- **做什么**：GLM-5.2 评审完成后，读取 9 份评分卡，分析 P0 和 P1 结果
- **P0 判定标准**：
  - `|P0-A 均分 - P0-B 均分| ≤ 5` → ✅ 战略定位达成
  - `5 < Δ ≤ 10` → ⚠️ 接近但有差距
  - `Δ > 10` → ❌ 未达成
- **P1 判定标准**（对照 V7-C6 baseline v3.8）：
  - 均分 > 65 → v4.1 有效（baseline 59.7）
  - B2' 判 Light（baseline 误判 Full）→ 修复
  - B3' 包含 passport.ts（baseline 遗漏）→ 修复
  - B2'/B3' Step 数 > 2（baseline 各只 1 Step，过早收敛）→ 修复
- **验证方式**：对照评分卡 JSON 和跨 cell 对比表，逐维度分析差距来源
- **输出**：`eval/runs/strategic-verify-2026-06-26/scorecards/_summary.md` + `conclusion.md`

#### 第 3 步：P1-闸门 + P2-pathfinder 修复（并行）— ✅ 已完成

> 第 2 步确认 P1-Step B2' 仍判 Full（应为 Light），触发 P1-闸门。P2-pathfinder 修复独立执行。

**P1-闸门**（已实施）：
- **做了什么**：在 `impact_validate.py` 中新增 V7 判档合理性检查，包含三个子检查：
  - **全量词覆盖门禁（FAIL）**：用户原话出现全量词（每次/所有/全部/任何/一律/每个）时，产出必须包含覆盖范围分析（覆盖范围/缺口）。缺失则 FAIL，阻止提交。
  - **过度判档检测（WARN）**：Full 模式但实现步骤 ≤2 且必须修改文件 ≤3 且无全量词 → WARN，提示可能应为 Light。
  - **判档不足检测（WARN）**：Light 模式但必须修改文件 >5 → WARN，提示可能应为 Full。
- **同步更新**：`references/phase-4-output.md` 文档增加 V7 检查项说明
- **验证结果**：
  - P1 B2'（Full, 2 步, 3 文件）→ 正确触发 WARN "可能应为 Light"
  - P1 B1'（Full, 4 步, 3 文件）→ 正确 PASS
  - P1 B3'（Full, 5 步, 3 文件）→ 正确 PASS
  - 模拟全量词场景（"每次接口请求"无覆盖分析）→ 正确触发 FAIL

**P2-pathfinder 修复**（已实施）：
- **做了什么**：增强 `pf_validate.py` V6 检查，新增三项内容合理性验证：
  - `dir_tree` 条目数 > 1（不能只有根目录 `/`）
  - `dir_tree` 条目对应磁盘真实目录（防止假目录蒙混过关）
  - `file_count` 与磁盘实际文件数比值在 0.3-3.0 范围内（防止数量严重偏差）
- **同步更新**：`references/phase-3-depth-fill.md` V6 描述已更新
- **认证-鉴权自检条件触发**：确认 `phase-3-depth-fill.md` 步骤 0 已有完整的条件触发逻辑（无认证 → 跳过自检），无需额外修改
- **验证结果**：
  - 正常 scan.json（66 文件, 17 目录）→ PASS
  - 伪造 file_count=0 + dir_tree=["/"] → 正确触发 3 项 FAIL
  - 伪造假目录（fake_dir/nonexistent/imaginary）→ 正确触发 FAIL
  - 伪造 file_count=99999（实际 62）→ 正确触发 FAIL

#### 第 4 步：验证修复效果（重跑相关 case）— ✅ 已完成（静态验证）

> 第 3 步已完成静态验证（见上方验证结果）。完整重跑需在其他会话中用 Step 3.7 Flash 模型执行，此处记录静态验证结论。

- **P1-闸门验证**：✅ 已通过静态验证——用 P1 B2' 产出运行 `impact_validate.py`，V7 正确触发过度判档 WARN；用模拟全量词场景运行，V7 正确触发 FAIL
- **P2-pathfinder 验证**：✅ 已通过静态验证——用伪造 scan.json 运行 `pf_validate.py`，V6 正确拦截 file_count=0、dir_tree 条目不存在、file_count 严重偏差
- **回归测试**：✅ P0-A B1'/B3'、P1 B1'/B3' 均通过，无破坏性影响

- **做什么**：根据第 3 步的修复内容，重跑相关 case 验证修复是否生效
- **P1-闸门验证**：用 Step 3.7 Flash 重跑 B2' case，确认 `impact_validate.py` 能拦截判档错误
- **P2-pathfinder 验证**：用 Step 3.7 Flash 重跑 P1 case（go-admin），确认 `pf_validate.py` V6 能拦截 facts 内容全错
- **验证方式**：对比修复前后的评分卡，确认问题项从 FAIL → PASS

#### 第 5 步：P3 收窄定位表述（基于全部实验结果）— ✅ 已完成

> 基于 P0/P1/修复验证的全部实验结果，已修订 `docs/skill-review-2026-06-26.md` §6.2-§6.4 和 §7。

**修订内容**：
- §6.2：增加弱模型（Flash 级）第三层定位——skill + 脚本闸门；附实验证据
- §6.3：从"最终验收标准"改为"验收标准与实验结论"，记录 P0 各维度数据和 P1 判档未修复结论
- §6.4：优化方向表增加"脚本闸门（V7/V6）"行，标注为"弱模型必需"
- §7：一句话总结更新为基于实验数据的定位表述

**核心结论**：skill 的外置补偿在"发现"层面起效（证据精度 +10），在"推理"层面有上限（深度推理仍逊于 Opus），弱模型需要脚本闸门兜底。

- **做什么**：基于 P0/P1/修复验证的全部实验结果，修订 skill 的战略定位表述
- **当前表述**（skill-review-2026-06-26.md §6.2）：
  > impact 系列的长期定位不是"给所有模型加流程"，而是**用流程结构弥补弱模型的 meta-reasoning 缺口**
  >
  > 高级模型（Opus 级）→ CLAUDE.md 就够
  > 性价比模型（Composer 级）→ CLAUDE.md + skill
- **可能的修订方向**（取决于实验结果）：
  - 如果 P0 达标（Δ ≤ 5）：定位表述可以保持，补充"已验证"证据
  - 如果 P0 接近（5 < Δ ≤ 10）：定位表述收窄为"在模糊需求场景下接近"
  - 如果 P0 未达标（Δ > 10）：定位表述需要重新审视——skill 可能更适合"中等模型 + 复杂场景"而非"弥补所有能力差"
  - 如果 P1 确认弱模型问题仍存在：明确表述"skill 对弱模型的补偿有上限，弱模型需要更强的脚本闸门兜底"
- **验证方式**：修订后的表述与实验数据一致，无过度宣称

### 实验产物归档

```
eval/runs/strategic-verify-2026-06-26/
├── README.md                          # 实验设计
├── PROMPT-P0A-composer-skill.md       # Cell A prompt
├── PROMPT-P0B-opus-noskill.md         # Cell B prompt
├── PROMPT-P1-step-skill.md            # P1 prompt
├── JUDGE-PROMPT.md                    # 评审 prompt
└── JUDGE-RESULT.md                    # ✅ GLM-5.2 评审结果 + 最终结论
```

### 关键设计决策

1. **为什么用 V7 模糊 prompt 而不是 V6 精确 prompt**：V7 增益 +12.1（skill 增益最大的场景），V6 增益仅 +2。如果 skill 的核心价值在"处理模糊需求"，就该在模糊需求场景下验证战略定位。

2. **为什么 P0-B 用 Opus 而不是 Composer noskill**：战略定位假说是"Composer + skill ≈ Opus + CLAUDE.md"，需要一个"强模型 + 无 skill"的对照组。Opus 自带元认知，CLAUDE.md 给准则就够，这是假说的另一端。

3. **为什么用自问自答模式而不是人工交互**：V9 证明人工交互模式下澄清质量显著优于自问自答（+4 分）。但人工交互无法并行跑 3 个 cell，且引入"人类回答质量"这个额外变量。自问自答模式更纯粹地测试 skill 协议本身的效果。

4. **为什么 P1 重跑而不是直接看 V7-C6 数据**：V7-C6 用的是 v3.8 协议。v3.9→v4.0→v4.1 三轮改进（改动完整性自检、链路追踪回流、多轮触发、规则分层加载、快速通道）都是针对弱模型问题做的，但只在 Composer 2.5 上验证过（V8-V10）。Step 3.7 Flash 上 v4.1 是否生效需要实测。
