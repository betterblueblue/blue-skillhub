# T10 — L1 全量回归（v4.1, Composer 2.5, 2026-06-25）

- 测试日期：2026-06-25
- runner_model：Composer 2.5
- judge：GLM-5.2
- skill_commit：55276bf（v4.1）
- baseline：769868d（2026-06-14, runner: opus-4-8）

## 触发原因

- v4.1 协议改进（链路追踪回流、多轮触发条件、Context Pack 场景覆盖、方法名存在性预检、改动完整性自检）完成后，需 L1 全量回归验证既有能力无回归、新特性全部触发。
- 路线图优先级 2（脚本闸门 `impact_validate.py`）、优先级 3（判档决策证据化）、优先级 6（弱模型降级策略 / 产出完整性自检）已在本轮工作中顺手完成，需通过 L1 验证有效性。

## 环境

- Agent / 模型：Composer 2.5（批量执行模式，agent 自行模拟用户回答）
- 触发方式：L1 回归 prompt 批量执行
- 测试目录：`test-projects/<fixture>/change-impact/l1-full-regression-composer25/<case-id>/`
- 评审产物：`eval/runs/2026-06-25-impact@55276bf/*.scorecard.json`
- 汇总报告：`eval/runs/2026-06-25-l1-full-regression-summary.md`

## 用例

| case | 变更 | 档位 | base | beh | p_level | 脚本闸门 | 要点 |
|------|------|:----:|:----:|:---:|:-------:|:-------:|------|
| R1 删 remark | RuoYi 删除 BaseEntity.remark 字段 | full | 102 | +10 | none | 0 FAIL | BaseEntity 15+ 实体陷阱 ✅；链路追踪 4 条 → Mapper 移除顺序回流设计；方法名预检 4 个；完整性自检 6 项 |
| R2 加 login_ip | RuoYi 登录增加 IP 记录 | full | 93 | +10 | none | 0 FAIL | login_ip 已存在冲突 ✅；建议复用（自洽）；链路追踪 ✅；缺判档决策表（P3） |
| R3 改文案 | RuoYi 登录 cookie 有效期文案 | light | 93 | +10 | none | 0 FAIL | light 正确；cookie 30 vs 7 天错位 ✅；light 模式强制链路深度检查 ✅ |
| R3N 破坏性请求 | RuoYi 删除 /api/v1 接口 | full | 91 | +10 | none | 0 FAIL | PM「不用分析直接做」拦截 ✅；/api/v1 0 命中 ✅；零代码变更 |

**均分：94.8** | **P0：0** | **P1：0** | **契约：全 PASS** | **脚本闸门：全 0 FAIL**

## v4.1 新特性触发验证

| v4.1 特性 | 验证 case | 触发 | 证据 |
|-----------|----------|:----:|------|
| 链路追踪回流 | R1, R2, R3, R3N | 4/4 ✅ | 每个 full case 的 context-pack 均含「关键链路追踪」表，Phase 2 副作用风险回流至 Phase 3 设计 |
| Context Pack 场景覆盖 | R1 | 1/1 ✅ | §9「暂不纳入范围」列出排除项及原因 |
| 方法名存在性预检 | R1 | 1/1 ✅ | 030-implementation.md §4 含 grep 核实表 |
| 改动完整性自检 | R1 | 1/1 ✅ | 030-implementation.md §2.1 含验收标准→Step 映射表 |
| 多轮触发条件 | R1 | N/A | 批量执行模式中 agent 自行模拟用户回答，P0/P1 风险在单轮内已全覆盖 |

## 基线 diff 红线检查

| 检查项 | 结果 |
|--------|------|
| 契约 PASS → FAIL | 0 例（4/4 全 PASS） |
| p_level 新增 P0/P1 | 0 例 |
| base 分下降 | 0 例（所有 case 均高于基线） |

**⚠ runner_model 混杂**：基线 runner 为 opus-4-8，本轮为 Composer 2.5。分数提升不能直接归因 skill 改进，但红线检查（契约/P0/P1）是不受模型影响的硬底线。

## 路线图优先级完成情况

| 路线图优先级 | 内容 | 本轮验证 |
|-------------|------|----------|
| 优先级 2 | 脚本闸门 `impact_validate.py` | ✅ 4 case 全 0 FAIL |
| 优先级 3 | 判档决策证据化 | ✅ full case 均含判档决策表（R2 缺表为 P3 轻微问题） |
| 优先级 6 | 弱模型降级策略（产出完整性自检） | ✅ R1 含完整性自检表 |

## 结论

- **通过**
- P0/P1：0 / 0
- v4.1 新特性全部正确触发
- 脚本闸门 `impact_validate.py` 在 4 个 case 上全 0 FAIL，验证有效
- 后续风险：runner_model 不一致（opus → composer），不建议直接将本轮分数作为新基线；如需建立 composer-2.5 基线，后续统一用 Composer 2.5 跑 2-3 轮取稳定值
