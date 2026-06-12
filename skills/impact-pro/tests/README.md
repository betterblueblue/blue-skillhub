# impact-pro skill — tests/scenarios/

回应 gpt5.5pro 评审 P0 #3「缺可重复自动化验收」。

## 设计

与 `skills/impact/tests/` 同构：每个 scenario JSON 是一个可重放的回归场景。

## 跑法

```bash
cd skills/impact-pro/tests
./run.sh
```

**当前能力（v1，静态层）**：
- 校验每个 scenario JSON 格式
- 校验 fixture 存在 + commit 哈希匹配
- 校验 SKILL.md 中含期望的 iron rule
- 校验 references 实际存在
- 校验 fixture 中"必须存在"的文件/字符串
- 校验 scenario 中 `expected.iron_rules_triggered` 至少 1 条

**未来能力（v2，LLM 集成层）**：
- 调用 Claude API 跑 skill，对比实际输出 vs `expected.phase_3_5_classification`

## 目录结构

```
skills/impact-pro/tests/
├── README.md
├── scenarios/
│   └── go-gin-gorm/
│       ├── 001-*.json
│       └── ...
├── fixtures/
│   └── README.md
├── run.sh
└── lib/
    └── validate.sh
```

## 当前 fixtures

| 项目 | URL | Commit | 用途 |
|------|-----|--------|------|
| go-admin | https://github.com/go-admin-team/go-admin | b83eef8670b09533213cdd29635e01842704ddd8 | impact-pro 2 个场景 |

## 编写新场景

参考 `scenarios/go-gin-gorm/001-*.json`。特别注意：

- impact-pro 的 profile 加载需 `discovery_globs` 真的命中，scenario 可加 `trap_for` 描述
- 多栈 / 未知栈场景应加 scenario 验证 `generic.md` 兜底
- db-adapter 选择（generic-sql vs mysql）应在 trap 中标注
