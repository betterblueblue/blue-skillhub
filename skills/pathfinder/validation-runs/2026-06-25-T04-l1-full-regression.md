# T04 — L1 全量回归（v4.1, Composer 2.5, 2026-06-25）

- 测试日期：2026-06-25
- runner_model：Composer 2.5
- judge：GLM-5.2
- skill_commit：55276bf（v4.1）
- baseline：769868d（2026-06-14, runner: kimi-k2.7-code）

## 触发原因

- v4.1 协议改进完成后，需 L1 全量回归验证 pathfinder 既有能力无回归。
- 验证 P3D 基线 P1（信任契约头写父 commit）修复无回归。
- 验证 code graph MCP 降级处理（当前会话 code graph inactive，降级为 Read/Grep/Glob 扫描）。

## 环境

- Agent / 模型：Composer 2.5（批量执行模式，agent 自行模拟用户回答）
- 触发方式：L1 回归 prompt 批量执行
- 测试目录：`test-projects/<fixture>/change-impact/l1-full-regression-composer25/<case-id>/`
- 评审产物：`eval/runs/2026-06-25-pathfinder@55276bf/*.scorecard.json`
- 汇总报告：`eval/runs/2026-06-25-l1-full-regression-summary.md`
- 注意：当前会话 code graph MCP inactive（无索引），Phase 2 降级为 Read/Grep/Glob 扫描，地图中如实标注 `status: unavailable`

## 用例

| case | 项目 | base | beh | p_level | 脚本闸门 | 要点 |
|------|------|:----:|:---:|:-------:|:-------:|------|
| P1 | go-admin | 101 | +10 | none | 6 PASS / 0 FAIL | V6 facts ✅；P1-B 认证-鉴权一致性自检发现 3 处不一致；Executive Summary ✅；code graph 降级诚实 |
| P2 | ruoyi-vue | 100 | +10 | none | 6 PASS / 0 FAIL | 完整 13 节 + ER 图；P1-B 一致性自检结论为一致；凭证脱敏 |
| P3D | degradation-trap | 99 | +10 | none | 6 PASS / 0 FAIL | **基线 P1 已修复**：信任契约头正确写「非独立 Git 仓库(HEAD 来自父仓库)」，不写父 commit |

**均分：100.0** | **P0：0** | **P1：0** | **契约：全 PASS** | **脚本闸门（pf_validate.py）：6 PASS / 0 FAIL（×3）**

## 基线 P1 修复验证

| case | 基线 (769868d) | 本轮 (55276bf) | 验证点 |
|------|---------------|----------------|--------|
| P3D | base 88, **P1**, C1+C2 FAIL | base 99, **none**, 全 PASS | 信任契约头正确写「非独立 Git 仓库(HEAD 来自父仓库)」，不写父 commit 769868d |

**P1 修复无回归，稳定通过。**

## 基线 diff 红线检查

| 检查项 | 结果 |
|--------|------|
| 契约 PASS → FAIL | 0 例（3/3 全 PASS） |
| p_level 新增 P0/P1 | 0 例（基线 1 个 P1 已修复，无新增） |
| base 分下降 | 0 例（所有 case 均高于基线） |

**⚠ runner_model 混杂**：基线 runner 为 kimi-k2.7-code，本轮为 Composer 2.5。分数提升不能直接归因 skill 改进，但红线检查（契约/P0/P1）是模型无关的硬底线。

## 关键发现

1. **code graph 降级处理正确**：3 个 case 均诚实标注 `status: unavailable`，降级为 Read/Grep/Glob 扫描，不影响地图质量。pf_validate.py 仍 6 PASS / 0 FAIL。
2. **P1-B 认证-鉴权一致性自检有效**：P1（go-admin）发现 3 处不一致并如实记录；P2（ruoyi-vue）结论为一致。
3. **凭证脱敏**：P2 中数据库密码等凭证正确脱敏为 `***`。
4. **P3D 信任契约修复稳定**：基线 P1（信任契约头写父 commit 769868d）在 v4.1 下正确写「非独立 Git 仓库(HEAD 来自父仓库)」。

## 结论

- **通过**
- P0/P1：0 / 0
- 基线 P1（P3D 信任契约头）修复无回归
- pf_validate.py 在 3 个 case 上均 6 PASS / 0 FAIL，脚本闸门有效
- code graph 降级处理正确，不影响地图质量
- 后续风险：runner_model 不一致（kimi → composer），不建议直接将本轮分数作为新基线
