# ImpactRadar 测试说明

这里包含确定性的 L0 检查，以及需要模型参与的历史端到端测试说明。

## L0 静态检查

```bash
bash skills/impact/tests/run.sh
```

`run.sh` 会完成三组检查：

1. 检查 `skills/impact/templates/` 中的必需模板是否存在且不为空。
2. 运行 `test_scripts/test_impact_validate.py`，检查风格规则、Phase 4/5 分步、执行前检查、状态一致性和确认记录等校验行为。
3. 校验 10 个场景 JSON：3 个 RuoYi-Vue 正向场景和 7 个负向场景，包括字段删除、字段新增、模糊授权、越界写入、数据库只读、破坏性请求、恢复后重新确认和凭证脱敏。

L0 不调用模型，结果可以重复验证。全部通过后，再决定是否运行需要模型参与的 L1 或真实项目测试。

早期 3 个负向场景的真实运行记录见 [T07](../validation-runs/2026-06-14-T07-negative-iron-rule-gates.md)。

## 历史端到端测试

`e2e/` 用于让执行模型在隔离项目中运行 Skill、修改代码并生成 `change-impact/` 文档，再由另一个模型或人工按 9 个维度复核。相关工作目录默认不纳入 Git。

已完成的历史场景：

| # | Skill | 项目 | 场景 | 首次评审 | 修复后 |
|---|-------|------|------|----------|--------|
| S1 | ImpactRadar | RuoYi-Vue | 删除 sys_user.remark（高风险 DROP COLUMN） | 未单独评分 | PASS 7/7 |
| S2 | ImpactRadar | RuoYi-Vue | 增加 last_login_ip（DB schema 变更） | 未单独评分 | PASS 9/9 |
| S3 | ImpactRadar（当时名为 `impact-pro`） | go-admin | 增加头像上传接口（OSS + 缩略图 + 权限） | FAIL | PASS 9/9 |

### S3 发现的价值

真实项目测试发现了仅靠模拟数据难以暴露的三类问题：

- **BaseEntity 共享**：remark 是基类字段，删 remark 影响 7 个 entity + 11 个 Vue 页
- **login_ip 重复**：已有 login_ip，新增 last_login_ip 会语义重复
- **frozen 不存在**：go-admin 的 user.status 没有 frozen 值，"删 frozen"是空操作

## 与统一测评体系的关系

ImpactRadar 已接入三层测评体系，用于发现修改后出现的质量下降。详细说明见 [docs/skill-eval/](../../../docs/skill-eval/)：

| 层 | 入口 | 说明 |
|---|---|---|
| L0 静态检查 | `bash skills/impact/tests/run.sh` | 模板、校验脚本和场景 JSON |
| L1 行为测试 | `bash eval/run-l1.sh impact` | 当前 `eval/cases/impact/` 下的 16 个用例 |
| L2 人工抽查 | 人工 | 提问质量、文档可读性等主观维度 |

与基线比较：`bash eval/diff-baseline.sh impact`

## 测试产物位置

```
tests/
├── run.sh               # L0 入口
├── lib/validate.sh      # 场景与共享约定检查
├── test_scripts/
│   └── test_impact_validate.py  # impact_validate.py 行为测试
├── scenarios/           # L0 场景 JSON
│   ├── java-spring-mybatis/
│   │   ├── 001-delete-sys-user-remark.json
│   │   ├── 002-add-last-login-ip.json
│   │   └── 003-change-login-remember-me.json
│   └── negative/        # neg-001 至 neg-007
└── e2e/                 # 本地端到端测试工作区，默认不提交
```

## 设计背景

这套测试最初用于补上“缺少可重复自动验收”的问题：

- L0 确认规则、模板和脚本是否完整。
- L1/L2 确认模型实际执行时是否遵守规则，以及文档质量是否足够。
- 共享约定检查避免 Pathfinder 与 ImpactRadar 对同一条安全规则写出不同要求。

完整设计见 `docs/archive/2026-06/skill-scenarios-design-2026-06-12.md`，测评体系设计见 `docs/archive/2026-06/2026-06-13-skill-eval-system-design.md`。
