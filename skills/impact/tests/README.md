# impact skill — tests/

两套测试，覆盖从"scenario 结构合法性"到"skill 真行为端到端"全链路。

## v1 静态校验（L0，冒烟）

```bash
bash skills/impact/tests/run.sh
```

校验项：
1. JSON schema 完整性（id/title/skill/stack/fixture/query/expected）
2. fixture 项目存在 + commit 哈希匹配
3. `iron_rules_triggered` 中的铁律在 SKILL.md 铁律区存在
4. `references_loaded` 中的文件存在
5. `phase_3_5_classification` 是 light 或 full
6. `files_to_inspect` 中的文件存在 + 含必须字符串
7. **共享契约存在性**（新增）：检查 `docs/skill-eval/contracts.md` 中的共享契约在 impact/SKILL.md 铁律区都存在，防止改一处另两处漂移

> **定位**：每次改动必跑，免费、确定性、零主观。全绿才允许进入 L1。

`scenarios/` 同时含**负向门禁场景**（`negative/neg-001|004|006`，对应铁律 #1 模糊/预授权、#4 越界写、#6 恢复须重确认），验证 skill 对越界请求的拒绝行为，实跑见 [validation-runs/2026-06-14-T07-negative-iron-rule-gates.md](../validation-runs/2026-06-14-T07-negative-iron-rule-gates.md)（T07，3/3 PASS）。

## v2 e2e 真行为测试（L1/L2，回归）

`e2e/` 目录下完整端到端：Subagent A 真跑 skill + 真改代码 + 真写 change-impact 文档，Subagent B 做 9 维评审。

### 跑法

```bash
cd e2e

# 准备 workdir（从 test-projects/ 克隆 fixture）
./run-helper.sh setup <scenario.json>

# 看 git diff
./run-helper.sh diff <scenario.json>

# 清理 workdir（actual/ 保留供审查）
./run-helper.sh cleanup <scenario.json>
```

Subagent A/B 由主 Claude 在对话中驱动（需要 LLM，不能纯 bash 化）。

### 已完成的 E2E 场景

| # | Skill | 项目 | 场景 | 首次评审 | 修复后 |
|---|-------|------|------|----------|--------|
| S1 | impact | RuoYi-Vue | 删 sys_user.remark（高风险 DROP COLUMN） | — | ✅ PASS 7/7 |
| S2 | impact | RuoYi-Vue | 加 last_login_ip（DB schema 变更） | — | ✅ PASS 9/9 |
| S3 | impact-pro | go-admin | 加头像上传接口（OSS + 缩略图 + 权限） | ❌ FAIL | ✅ PASS 9/9 |

### S3 发现的价值

真实项目测试暴露了 3 个 mock 永远找不到的语义问题：
- **BaseEntity 共享**：remark 是基类字段，删 remark 影响 7 个 entity + 11 个 Vue 页
- **login_ip 重复**：已有 login_ip，新增 last_login_ip 会语义重复
- **frozen 不存在**：go-admin 的 user.status 没有 frozen 值，"删 frozen"是空操作

## 统一测评体系

impact 已接入三层防漂移测评体系，详见 [docs/skill-eval/](../../../docs/skill-eval/)：

| 层 | 入口 | 说明 |
|---|---|---|
| L0 静态 | `bash skills/impact/tests/run.sh` | 就是上面的 v1 |
| L1 行为契约 | `bash eval/run-l1.sh impact` | 4 个标准化 case（R1/R2/R3/R3N），subagent 扮用户端到端跑分 |
| L2 人审深度 | 人工 | 主观维度抽样 |

基线 diff：`bash eval/diff-baseline.sh impact`

## 测试产物位置

```
tests/
├── run.sh               # L0 入口
├── lib/validate.sh      # 校验函数库（含共享契约检查）
├── scenarios/           # 静态场景 JSON（v1，git 追踪）
│   ├── java-spring-mybatis/
│   │   ├── 001-delete-sys-user-remark.json
│   │   ├── 002-add-last-login-ip.json
│   │   └── 003-change-login-remember-me.json
│   └── negative/        # 负向门禁场景（铁律 #1/#4/#6，见 T07）
│       ├── neg-001-vague-authorization.json
│       ├── neg-004-write-outside-target-root.json
│       └── neg-006-resume-without-reconfirm.json
└── e2e/                 # e2e 产出（gitignore，本地保留）
    ├── scenarios/
    ├── workdirs/
    └── prompts/
```

## 设计背景

回应 gpt5.5pro 评审 P0 #3「缺可重复自动化验收」。

- v1（静态/L0）回应"有没有"
- v2（e2e/L1-L2）回应"够不够"
- 共享契约检查回应"改一处会不会漂移到另两处"

完整设计见 `docs/archive/2026-06/skill-scenarios-design-2026-06-12.md`，测评体系设计见 `docs/archive/2026-06/2026-06-13-skill-eval-system-design.md`。
