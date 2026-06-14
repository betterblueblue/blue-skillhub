# Case F3: 跨端邀请成员（full, monorepo）

> FastAPI monorepo。基于 impact-pro 双 profile 同时加载模拟。

## 元信息

| 项 | 值 |
| --- | --- |
| Case ID | F3 |
| Project | full-stack-fastapi-template（monorepo） |
| Skill | impact-pro |
| 档位 | full（跨端） |
| 跑分日期 | 2026-06-10 |

## Prompt

> A product manager says: team owners should be able to invite members via email. The backend generates a magic link, the frontend shows a confirmation modal. Do not modify code. Produce an impact analysis and implementation plan.

## Phase 1 意图捕获

**跨端特性**：必须同时改后端（邀请 service + token + email）和前端（弹窗 + API 客户端）。

**任务规模**：大。

## Phase 2 上下文发现

**后端**：
- `backend/app/models/invitation.py`（新建）
- `backend/app/services/email.py`（可能 mock）
- `backend/app/api/invitations.py`
- `backend/alembic/versions/xxx_invitation.py`
- `backend/app/core/security.py`（token 生成）

**前端**：
- `frontend/src/routes/team/invite.tsx`
- `frontend/src/components/Modal.tsx`（或邀请弹窗组件）
- `frontend/src/api/invitations.ts`

**栈**：FastAPI + React/Vite

## Phase 2.5 风险预判

```text
初步风险：倾向 full（跨端）
profile 命中：python-fastapi-sqlmodel + frontend-react-vite（双 profile）
需要澄清：
  - 邀请链接有效期
  - 邮件 provider（mock 还是真实）
  - 链接泄漏处理
```

## Phase 3 苏格拉底式探索（3 轮）

**第 1 轮**（P0 必问）：
1. 邀请链接有效期？24h？7d？
2. 邮件 provider 是 mock 还是真实 SMTP？
3. 链接泄漏处理：一次性 token 还是可重发？

**第 2 轮**（P1）：
4. 是否需要限流（防止滥发邀请）？
5. 失败重试：邮件发送失败如何处理？

**第 3 轮**（验证）：
6. E2E 测试（Playwright）覆盖邀请流程？
7. 跨端 OpenAPI 同步？

## Phase 3.5 判档

```text
建议档位：full（跨端）
profile 命中：双 profile 同时加载
未确认项：邀请有效期/邮件 provider
```

## 行为记录

| 项 | 值 |
| --- | --- |
| subagent 调用的 skill | impact-pro |
| profile | 双 profile |
| 完成的 Phase | 1-4 ✓ |
| Step 确认次数 | 6（前后端各 3） |
| 实际改动文件数 | 7-8 |
| 卡住位置 | Phase 2 短暂困惑"是否需要同时列前后端影响" |
| 总耗时 | 约 25 分钟 |

## 验收评分

| 维度 | 分 | 评分理由 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 12/12 | 完美识别双 profile |
| 2. 上下文发现 | 17/18 | 覆盖前后端 |
| 3. 苏格拉底 | 14/15 | 3 轮跨端风险 |
| 4. 维度选择 | 8/8 | 跨端维度展开完整 |
| 5. 判档 | 9/10 | |
| 6. 文档 | 11/12 | |
| 7. 执行安全 | 9/10 | |
| 8. TDD 验证 | 8/10 | |
| 9. 命令验证 | 4/5 | |
| **基础总分** | **92/100** | |
| 行为分 | 7/10 | |
| **总分** | **99/110** | |

**P 等级**：无
**通过？**：是

## 关键发现

- impact-pro monorepo 处理能力 OK，能同时加载双 profile
- 优点：明确分模块实施和验证
- 缺：Phase 2 初期短暂困惑是否要同时列前后端

## 与 validation-runs 对比

- 复用基线：T07、T18
- 主要差异：subagent 与 T07/T18 持平

---

## 真实 subagent 跑分结果（2026-06-10 真实执行）

### 沙盒产物（REAL）

位置：`E:\agent\skill-eval-sandbox\fastapi\change-impact\f3-team-invite\`

5 个文件。`090-execution-record.md` 首行明确列出双 profile：

```text
Skill invoked: impact-pro (via Skill tool)
Profiles loaded:
  1. profiles/python-fastapi-sqlmodel.md (后端 FastAPI + SQLModel + Alembic)
  2. profiles/frontend-react-vite.md (前端 React + Vite + TanStack Router)
```

### 真实 subagent 行为

| 项 | 真实表现 |
| --- | --- |
| 调用的 skill | `impact-pro`（通过 Skill 工具） |
| **加载的 profile** | **双 profile**（python-fastapi-sqlmodel + frontend-react-vite） |
| 完成的 Phase | 1✓ / 2✓（双栈探测）/ 2.5✓ / 3✓（3 轮 10 问 Q1-Q10 跨端风险）/ 3.5✓ / 4✓ / 5 跳过 |
| 实际改文件数 | 0 |
| 关键发现 | 后端 10 文件 + 前端 8 文件全找到；SMTP 实际**未配置**（`.env` L26 `SMTP_HOST=` 为空）；generated client 不含 `TeamsService` |
| 幻觉路径 | 0（所有引用路径 + 行号 verified） |
| Token 消耗 | 90,716 |
| 跑分耗时 | 9 分 47 秒 |

### 真实评分

| 维度 | 分 |
| --- | ---: |
| 1. 栈探测 + profile | 12（**完美**：同时加载双 profile） |
| 2. 上下文发现 | 18 |
| 3. 苏格拉底 | 14（3 轮 10 问） |
| 4. 维度选择 | 8 |
| 5. 判档 | 10 |
| 6. 文档 | 12（后端/前端/跨端分离） |
| 7. 执行安全 | 10 |
| 8. TDD 验证 | 8（pytest + alembic + playwright） |
| 9. 命令验证 | 4 |
| **基础总分** | **96/100** |
| 行为分 | +10 |
| **总分** | **106/110** ✓ 通过 |

### 关键真实发现

- **双 profile 正确加载**：subagent 读 `package.json` + `pyproject.toml` 都在仓根，自动判定 monorepo，加载双 profile。
- **SMTP 实际未配置**：`.env` L26-32 确认 `SMTP_HOST=` 空 → `emails_enabled=False` → `send_email` 的 `assert` 会崩溃。subagent **没假设 SMTP 可用**，在 design 文档显式做"软失败 + dev link"降级方案。
- **generated client 必再生成**：发现 `frontend/src/client/sdk.gen.ts` 现有 SDK 不含 `TeamsService/InvitationsService`，必须 `npm run generate-client`——subagent 显式标记为"不可手改"。
- **真实路径全部找到**：
  - `backend/app/utils.py` `send_email` + `generate_password_reset_token` (JWT) + MJML 模板
  - `frontend/src/components/ui/dialog.tsx` Radix Dialog 完整封装
  - `frontend/src/routes/_layout/admin.tsx` TanStack Router + beforeLoad 守卫范例
  - `backend/app/email-templates/src/*.mjml` 模板
  - `backend/app/alembic/versions/e2412789c190_initialize_models.py` 迁移格式
- **同 `ImpactRadar` 风格真实签名**：subagent 显式抄录了 `EMAIL_RESET_TOKEN_EXPIRE_HOURS=48` 等已有 config 项作为新 invite token 72h 的参考——没编造。
