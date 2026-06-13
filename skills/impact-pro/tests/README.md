# impact-pro skill — tests/

两套测试，覆盖从"scenario 结构合法性"到"skill 真行为端到端"全链路。

## v1 静态校验（L0，冒烟）

```bash
bash skills/impact-pro/tests/run.sh
```

校验项：
1. JSON schema 完整性（id/title/skill/stack/fixture/query/expected）
2. fixture 项目存在 + commit 哈希匹配
3. `iron_rules_triggered` 中的铁律在 SKILL.md 铁律区存在
4. `references_loaded` 中的文件存在
5. `phase_3_5_classification` 是 light 或 full
6. `files_to_inspect` 中的文件存在 + 含必须字符串
7. **共享契约存在性**（新增）：检查 `docs/skill-eval/contracts.md` 中的共享契约在 impact-pro/SKILL.md 铁律区都存在

> **定位**：每次改动必跑，免费、确定性、零主观。全绿才允许进入 L1。

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
| S3 | impact-pro | go-admin | 加头像上传接口（OSS + 缩略图 + 权限） | ❌ FAIL | ✅ PASS 9/9 |

### S3 修复项（7 项）

1. Upload 签名 `interface{}` → `context.Context` + `*AvatarUploadReq`
2. `mime.ExtensionsByType` 空切片保护
3. 加 magic-byte 二次校验（`ValidateImageMagicBytes`）
4. 硬编码路径 → `config.ExtConfig.Upload.AvatarDir`
5. InsetAvatar 501 stub → 恢复原始实现（铁律 #2）
6. BR-006 降级逻辑：缩略图生成失败 → thumbPath=origPath, 不报错
7. 清理路径测试：新建 `failStore` mock 验证 cleanup

## 统一测评体系

impact-pro 已接入三层防漂移测评体系，详见 [docs/skill-eval/](../../../docs/skill-eval/)：

| 层 | 入口 | 说明 |
|---|---|---|
| L0 静态 | `bash skills/impact-pro/tests/run.sh` | 就是上面的 v1 |
| L1 行为契约 | `bash eval/run-l1.sh impact-pro` | 6 个标准化 case，覆盖 Java/Go/FastAPI/React 四栈 |
| L2 人审深度 | 人工 | 主观维度抽样 |

基线 diff：`bash eval/diff-baseline.sh impact-pro`

## 测试产物位置

```
tests/
├── run.sh               # L0 入口
├── lib/validate.sh      # 校验函数库（含共享契约检查）
├── scenarios/           # 静态场景 JSON（v1，git 追踪）
│   └── go-gin-gorm/
│       ├── 001-modify-user-status-enum.json
│       └── 002-change-api-msg-text.json
└── e2e/                 # e2e 产出（gitignore，本地保留）
    ├── scenarios/
    │   └── 003-add-avatar-upload/
    ├── workdirs/
    │   └── 003-add-avatar-upload/
    └── prompts/
```

## 当前 fixtures

| 项目 | URL | Commit | 用途 |
|------|-----|--------|------|
| go-admin | https://github.com/go-admin-team/go-admin | b83eef8670b09533213cdd29635e01842704ddd8 | impact-pro S3 场景 |

## 设计背景

回应 gpt5.5pro 评审 P0 #3「缺可重复自动化验收」。

- v1（静态/L0）回应"有没有"
- v2（e2e/L1-L2）回应"够不够"
- 共享契约检查回应"改一处会不会漂移到另两处"

完整设计见 `docs/skill-scenarios-design-2026-06-12.md`，测评体系设计见 `docs/plans/2026-06-13-skill-eval-system-design.md`。
