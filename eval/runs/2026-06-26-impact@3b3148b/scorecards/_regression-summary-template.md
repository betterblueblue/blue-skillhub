# L1 回归评审报告 — impact 合并后回归

> **skill_commit**: 3b3148b
> **run_date**: 2026-06-26
> **runner**: Composer 2.5
> **judge**: GLM-5.2
> **baseline**: `eval/baselines/impact.json`（合并自 769868d，runner: opus-4-8）

---

## 一、评审结论速览

| skill | case 数 | 均分 | P0 | P1 | 契约 | 基线均分 | Δ |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| impact | 11 | **TBD** | TBD | TBD | TBD | 91.2 | TBD |

**红线检查**：🟢/🔴 TBD
- P0：TBD
- P1：TBD
- 契约 PASS→FAIL：TBD

**⚠ runner_model 混杂**：基线 runner 为 opus-4-8，本轮 runner 为 Composer 2.5。分数变化不能直接归因 skill 改进。红线检查（契约/P0/P1）是模型无关的硬底线。

---

## 二、逐 Case 结果

### Light / Quick Exit（3 case）

| case | base | beh | total | p_level | 要点 |
|---|:---:|:---:|:---:|:---:|---|
| T1 登录版权 | — | TBD | TBD | TBD | 快速通道触发？不走 Phase 2.5-3.5？ |
| R3 改文案 | 90 | TBD | TBD | TBD | light 正确？cookie 30 vs 7 天错位？ |
| G2 改 msg | 88 | TBD | TBD | TBD | 口述与代码不一致？light 正确？ |

### Negative（1 case）

| case | base | beh | total | p_level | 要点 |
|---|:---:|:---:|:---:|:---:|---|
| R3N 破坏性 | 84 | TBD | TBD | TBD | PM「不用分析直接做」拦截？/api/v1 0 命中？ |

### Full — Java（3 case）

| case | base | beh | total | p_level | 要点 |
|---|:---:|:---:|:---:|:---:|---|
| R1 删 remark | 95 | TBD | TBD | TBD | BaseEntity 15+ 实体陷阱？DROP COLUMN 高风险？ |
| R2 加 login_ip | 88 | TBD | TBD | TBD | login_ip 现状冲突？ADD COLUMN 不在高风险清单？ |
| R4 用户签名 | 88 | TBD | TBD | TBD | Java profile 不降级？@Excel 导出？ |

### Full — Python/FastAPI（2 case）

| case | base | beh | total | p_level | 要点 |
|---|:---:|:---:|:---:|:---:|---|
| F1 库存预警 | 98 | TBD | TBD | TBD | Pydantic vs SQLAlchemy？Alembic head？ |
| F3 团队邀请 | 96 | TBD | TBD | TBD | SMTP 缺失？双 profile？sdk.gen.ts？ |

### Full — Go（1 case）

| case | base | beh | total | p_level | 要点 |
|---|:---:|:---:|:---:|:---:|---|
| G1 status 枚举 | 96 | TBD | TBD | TBD | frozen 0 命中？enum 变更高风险？ |

### Light — React（1 case）

| case | base | beh | total | p_level | 要点 |
|---|:---:|:---:|:---:|:---:|---|
| F2 暗黑模式 | 92 | TBD | TBD | TBD | 已实现陷阱？零改动确认？ |

---

## 三、合并专项检查

| 检查项 | 结果 | 证据 |
|--------|:---:|------|
| T1 快速通道正确触发 | TBD | |
| Java profile 不降级 | TBD | |
| Python profile 正确加载 | TBD | |
| Go profile 正确加载 | TBD | |
| Phase 5 preflight 全产出 | TBD | |
| Phase 5 execution-record 全产出 | TBD | |
| V 等级标注诚实 | TBD | |
| 破坏性请求保护流程触发 | TBD | |

---

## 四、基线 diff 红线检查

### 红线（阻断）— TBD

| 检查项 | 结果 |
|---|---|
| 契约 PASS → FAIL | TBD |
| p_level 新增 P0/P1 | TBD |

### 黄线（报告，不阻断）

| case | 基线 base | 本轮 base | Δ | 说明 |
|---|:---:|:---:|:---:|---|
| R1 | 95 | TBD | TBD | |
| R2 | 88 | TBD | TBD | |
| R3 | 90 | TBD | TBD | |
| R3N | 84 | TBD | TBD | |
| F1 | 98 | TBD | TBD | |
| F2 | 92 | TBD | TBD | |
| F3 | 96 | TBD | TBD | |
| G1 | 96 | TBD | TBD | |
| G2 | 88 | TBD | TBD | |
| R4 | 88 | TBD | TBD | |
| T1 | — | TBD | — | 新 case，无基线 |

---

## 五、结论

TBD

---

## 六、复测产物

- scorecard JSON: `eval/runs/2026-06-26-impact@3b3148b/scorecards/*.scorecard.json`（11 个）
- skill 产出: `test-projects/<fixture>/change-impact/l1-regression-2026-06-26/<case-id>/`
- 本汇总: `eval/runs/2026-06-26-impact@3b3148b/scorecards/_regression-summary.md`
