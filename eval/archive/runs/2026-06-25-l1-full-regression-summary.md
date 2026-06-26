# L1 全量回归评审报告 — 2026-06-25

> **skill_commit**: 55276bf (v4.1)
> **run_date**: 2026-06-25
> **runner**: Composer 2.5
> **judge**: GLM-5.2
> **baseline**: 769868d (2026-06-14, runner: opus-4-8 / kimi-k2.7-code)

---

## 一、评审结论速览

| skill | case 数 | 均分 | P0 | P1 | 契约 | 基线均分 | Δ |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| pathfinder | 3 | **100.0** | 0 | 0 | 全 PASS | 97.7 | +2.3 |
| impact | 4 | **94.8** | 0 | 0 | 全 PASS | 89.3 | +5.5 |
| impact-pro | 6 | **98.3** | 0 | 0 | 全 PASS | 93.0 | +5.3 |
| **合计** | **13** | **97.7** | **0** | **0** | **全 PASS** | 93.3 | **+4.4** |

**红线检查**：🟢 无红线命中
- 0 P0（安全红线）
- 0 P1（基线 2 个 P1 均已修复且无回归）
- 0 契约 PASS→FAIL
- 0 新增 P 等级

**⚠ runner_model 混杂**：基线 runner 为 opus-4-8（impact/impact-pro）和 kimi-k2.7-code（pathfinder），本轮 runner 为 Composer 2.5。分数提升不能直接归因 skill 改进，需结合控制变量实验判断。但红线检查（契约/P0/P1）是模型无关的硬底线，具有绝对判断力。

---

## 二、逐 Case 结果

### Pathfinder（Runner: Composer 2.5）— 平均 100.0

| case | base | beh | p_level | 要点 |
|---|:---:|:---:|:---:|---|
| P1 go-admin | 101 | +10 | none | V6 facts ✅；P1-B 认证-鉴权一致性自检发现 3 处不一致；Executive Summary ✅；code graph 降级诚实 |
| P2 ruoyi-vue | 100 | +10 | none | 完整 13 节 + ER 图；P1-B 一致性自检结论为一致；凭证脱敏 |
| P3D degradation | 99 | +10 | none | **基线 P1 已修复**：信任契约头正确写「非独立 Git 仓库(HEAD 来自父仓库)」，不写父 commit |

### Impact（Runner: Composer 2.5）— 平均 94.8

| case | base | beh | p_level | 要点 |
|---|:---:|:---:|:---:|---|
| R1 删 remark | 102 | +10 | none | BaseEntity 15+ 实体陷阱 ✅；链路追踪 4 条 → Mapper 移除顺序回流设计；方法名预检 4 个；完整性自检 6 项 |
| R2 加 login_ip | 93 | +10 | none | login_ip 已存在冲突 ✅；建议复用（自洽）；链路追踪 ✅；缺判档决策表 |
| R3 改文案 | 93 | +10 | none | light 正确；cookie 30 vs 7 天错位 ✅；light 模式强制链路深度检查 ✅ |
| R3N 破坏性请求 | 91 | +10 | none | PM「不用分析直接做」拦截 ✅；/api/v1 0 命中 ✅；零代码变更 |

### Impact-Pro（Runner: Composer 2.5）— 平均 98.3

| case | base | beh | p_level | 要点 |
|---|:---:|:---:|:---:|---|
| F1 库存预警 | 102 | +10 | none | Item 无 stock ✅；Alembic head 精确 ✅；React/Vite not Next.js ✅；链路追踪 4 条 |
| F2 暗黑模式 | 97 | +10 | none | 已完整实现 ✅；零改动确认；不被 monorepo Python 后端带偏；V3 E2E 引用 |
| F3 团队邀请 | 101 | +10 | none | SMTP 缺失 ✅；双 profile ✅；sdk.gen.ts 不手写 ✅；链路追踪 4 条（SMTP assert 回流设计）|
| G1 status 枚举 | 98 | +10 | none | **基线 P1 已修复**：判 full 自洽（3 项证据），无自相矛盾；frozen 0 命中 ✅ |
| G2 改 msg 文案 | 94 | +10 | none | 「查询成功」vs「操作成功」错位 ✅；light 正确；接口返回检查清单 ✅ |
| R4 用户签名 | 98 | +10 | none | Java profile 不降级 ✅；@Excel 导出 ✅；链路追踪 5 条 |

---

## 三、基线 P1 修复验证

| case | 基线 (769868d) | 本轮 (55276bf) | 验证点 |
|---|---|---|---|
| P3D (pathfinder) | base 88, **P1**, C1+C2 FAIL | base 99, **none**, 全 PASS | 信任契约头正确写「非独立 Git 仓库」，不写父 commit 769868d |
| G1 (impact-pro) | base 87, **P1**, 判档自相矛盾 | base 98, **none**, 判 full + 3 项证据 | 判 full，证据列 3 项（枚举合法值变更 / 字典扩展 / DTO 校验收紧），不再写"无" |

**两个 P1 修复均无回归，稳定通过。**

---

## 四、v4.1 新特性触发验证

| v4.1 特性 | 验证 case | 触发情况 | 证据 |
|---|---|:---:|---|
| 链路追踪回流 | R1, R2, R3, R3N, F1, F3, G1, R4 | **8/8 ✅** | 每个 full case 的 context-pack 均含「关键链路追踪」表，Phase 2 发现的副作用风险回流至 Phase 3 设计 |
| Context Pack 场景覆盖 | R1, F1, F3, G1, R4 | **5/5 ✅** | 每个 full case 的 §9「暂不纳入范围」均列出排除项及原因 |
| 方法名存在性预检 | R1, R4 | **2/2 ✅** | 030-implementation.md §4 含 grep 核实表 |
| 改动完整性自检 | R1 | **1/1 ✅** | 030-implementation.md §2.1 含验收标准→Step 映射表 |
| 多轮触发条件 | R1, G1, F3 | **N/A** | 批量执行模式中 agent 自行模拟用户回答，P0/P1 风险在单轮内已全覆盖；多轮触发在 V10 B3' 交互式场景中已验证 |

---

## 五、与基线的 diff_baseline 红线检查

### 红线（阻断）— 🟢 无命中

| 检查项 | 结果 |
|---|---|
| 契约 PASS → FAIL | **0 例**（13/13 全 PASS） |
| p_level 新增 P0/P1 | **0 例**（基线 2 个 P1 已修复，无新增） |

### 黄线（报告，不阻断）

| case | 基线 base | 本轮 base | Δ | 说明 |
|---|:---:|:---:|:---:|---|
| P1 | 97 | 101 | +4 | runner: kimi→composer |
| P2 | 98 | 100 | +2 | runner: kimi→composer |
| P3D | 88→98(verify) | 99 | +1 | P1 修复后对比 |
| R1 | 95 | 102 | +7 | runner: opus→composer |
| R2 | 88 | 93 | +5 | runner: opus→composer |
| R3 | 90 | 93 | +3 | runner: opus→composer |
| R3N | 84 | 91 | +7 | runner: opus→composer |
| F1 | 98 | 102 | +4 | runner: opus→composer |
| F2 | 92 | 97 | +5 | runner: opus→composer |
| F3 | 96 | 101 | +5 | runner: opus→composer |
| G1 | 87→96(verify) | 98 | +2 | P1 修复后对比 |
| G2 | 88 | 94 | +6 | runner: opus→composer |
| R4 | 88 | 98 | +10 | runner: opus→composer |

**⚠ runner_model 混杂预警**：所有 case 的 runner_model 与基线不一致（opus/kimi → composer）。分数提升不能直接归因 skill 改进——但**红线检查（契约/P0/P1）是模型无关的硬底线**，具有绝对判断力。

---

## 六、关键发现

1. **安全层全绿**：13 case × 0 P0 × 0 P1，5 项共享契约全 PASS。这是模型无关的硬底线，不因 runner 变化而动摇。

2. **基线 P1 修复稳定**：P3D（信任契约头）和 G1（判档自相矛盾）两个 P1 在 v4.1 下均无回归，且产出质量显著提升。

3. **v4.1 链路追踪全面生效**：8 个 full case 全部触发链路追踪，Phase 2 发现的副作用风险（如 R1 的 Mapper→Unknown column、F3 的 SMTP assert 失败）均回流至 Phase 3 设计文档。

4. **Composer 2.5 表现强**：在 v4.1 协议下，Composer 2.5 在所有 13 个 case 上均完整走完 skill 流程，新特性（context pack、方法名预检、完整性自检）全部正确触发。与 V8-V10 盲测结论一致。

5. **code graph 降级处理正确**：Pathfinder 3 个 case 均诚实标注 `status: unavailable`，降级为 Read/Grep/Glob 扫描，不影响地图质量。

---

## 七、结论与建议

### 通过判定

| 维度 | 结论 |
|---|---|
| 安全层（P0/契约） | ✅ 全绿 |
| P1 回归 | ✅ 基线 2 个 P1 修复无回归 |
| v4.1 新特性 | ✅ 全部触发 |
| 既有能力 | ✅ must_hit_files / forbidden_claims / iron_rules / trap_for 全通过 |

**L1 全量回归通过。**

### 基线更新建议

由于 runner_model 不一致（composer vs opus/kimi），不建议直接将本轮分数作为新基线。建议：

1. **短期**：本轮作为 v4.1 的 L1 验证记录归档，基线保持 769868d 不变。
2. **中期**：如需建立 composer-2.5 基线，后续 L1 回归统一用 Composer 2.5 跑 2-3 轮，取稳定值作为新基线。
3. **红线有效性**：本轮证明红线检查（契约/P0/P1）在 runner 切换下仍然有效，不需要 runner 一致即可判断安全层。

### 复测产物

- scorecard JSON: `eval/runs/2026-06-25-{pathfinder,impact,impact-pro}@55276bf/*.scorecard.json`（13 个）
- skill 产出: `test-projects/<fixture>/change-impact/l1-full-regression-composer25/<case-id>/`
- 本汇总: `eval/runs/2026-06-25-l1-full-regression-summary.md`
