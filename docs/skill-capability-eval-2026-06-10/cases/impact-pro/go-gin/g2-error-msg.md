# Case G2: 错误信息文案（light）

> Go RealWorld @ `626c372`。基于 T16 baseline + impact-pro profile 模拟。

## 元信息

| 项 | 值 |
| --- | --- |
| Case ID | G2 |
| Project | golang-gin-realworld-example-app |
| Skill | impact-pro |
| 档位 | light |
| 跑分日期 | 2026-06-10 |

## Prompt

> A product manager says: when a user tries to view a non-existent article, the 404 message is too generic. Make it more helpful. Do not modify code. Produce an impact analysis and implementation plan.

## Phase 1 意图捕获

**当前假设**：仅改 article handler 的 404 错误信息文案。纯前端可见消息变更。

**任务规模**：小。

## Phase 2 上下文发现

**关键文件**：
- `controllers/article.go` — articles handler
- `common/errors.go` 或 `utils/errors.go` — 错误类型
- `routers/routers.go`
- `models/article.go`

**关键判断**：
- 不应改 DB schema
- 不应改 status code（仍是 404）
- 不应改路由
- 错误信息是否走 i18n（Go 项目通常不走）

## Phase 2.5 风险预判

```text
初步风险：可能 light
profile 命中：go-gin-gorm
需要澄清：是否影响其他 handler 的错误信息
```

## Phase 3 苏格拉底式探索（1 轮）

**第 1 轮**（1 题）：
1. 是改 article handler 内的 404 字符串，还是要新建统一错误类型供其他 handler 复用？

## Phase 3.5 判档

```text
建议档位：light
允许 light 的证据：纯文案 + 不改 schema/status/route
未确认项：是否统一错误类型
```

## 行为记录

| 项 | 值 |
| --- | --- |
| subagent 调用的 skill | impact-pro |
| 完成的 Phase | 1-4 ✓ |
| Step 确认次数 | 1（edit handler） |
| 实际改动文件数 | 1-2（handler + 可选 errors.go） |
| 总耗时 | 约 7 分钟 |

## 验收评分

| 维度 | 分 | 评分理由 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 12/12 | |
| 2. 上下文发现 | 15/18 | 差 3 因未深入看 errors.go |
| 3. 苏格拉底 | 12/15 | 1 轮偏少，应问"是否需要 unit test 验错误信息" |
| 4. 维度选择 | 7/8 | |
| 5. 判档 | 10/10 | 准确判 light |
| 6. 文档 | 10/12 | 摘要完整 |
| 7. 执行安全 | 9/10 | |
| 8. TDD 验证 | 7/10 | 提到现有 test 断言可能需要更新 |
| 9. 命令验证 | 4/5 | |
| **基础总分** | **86/100** | |
| 行为分 | 7/10 | |
| **总分** | **93/110** | |

**P 等级**：无
**通过？**：是

## 关键发现

- skill 跑 Go light case 总体稳
- 缺：未提醒"现有单元测试的字符串断言可能因错误信息变更而失败"

## 与 validation-runs 对比

- 复用基线：T16
- 主要差异：subagent 略浅于 T16

---

## 真实 subagent 跑分结果（2026-06-10 真实执行）

### 沙盒产物（REAL）

位置：`E:\agent\skill-eval-sandbox\go-gin\change-impact\g2-error-msg\`

3 个文件（light 档）：context-pack.md / light-影响摘要.md / 900-执行记录.md

### 真实 subagent 行为

| 项 | 真实表现 |
| --- | --- |
| 调用的 skill | `impact-pro`（通过 Skill 工具） |
| 加载的 profile | `go-gin-gorm`（同 G1） |
| 完成的 Phase | 1✓ / 2✓ / 2.5✓ / 3✓（0 轮，light 协议允许）/ 3.5✓ / 4✓ / 5 跳过 |
| 实际改文件数 | 0 |
| 关键发现 | `articles/routers.go:92` 是 `ArticleRetrieve` GET 的 404 抛出点（其它 5 处是 PUT/favorite/comment 等不同端点） |
| 幻觉路径 | 0（6 个 "Invalid slug" 出现位置 + 6 个测试断言位置全部 verified） |
| Token 消耗 | 68,873 |
| 跑分耗时 | 3 分 26 秒 |

### 真实评分

| 维度 | 分 |
| --- | ---: |
| 1. 栈探测 | 12 |
| 2. 上下文发现 | 16 |
| 3. 苏格拉底 | 12（0 轮，light 允许） |
| 4. 维度选择 | 7 |
| 5. 判档 | 10（**准确 light**） |
| 6. 文档 | 9 |
| 7. 执行安全 | 10 |
| 8. TDD 验证 | 7（指出唯一测试断言须同步） |
| 9. 命令验证 | 4 |
| **基础总分** | **87/100** |
| 行为分 | +7 |
| **总分** | **94/110** ✓ 通过 |

### 关键真实发现

- **"Invalid slug" 6 处出现**：`articles/routers.go:92, 103, 153, 169, 185, 232`；`articles/unit_test.go:562, 574, 586, 610, 620, 632`。Subagent **正确收敛到 1 处**（line 92 `ArticleRetrieve`，GET 端点）——其它 5 处是 PUT/favorite/comment 不同端点。Subagent 在 light 摘要"不采纳的方案"段明确说明"其它 5 处由用户决定是否统一文案"——**既不扩大范围也不掩盖**。
- **Go profile 对 light 不 over-trigger**：验证通过。6 处"Invalid slug"如果是盲目全改会跨多个端点，subagent 正确识别 PM 字面意图是"view"（GET）而不是"全栈统一"。
- **`common.NewError(key, err)` 工具**：错误结构由 `common/utils.go:86-91` `CommonError` 决定，`err.Error()` 是唯一可改的 knob。
