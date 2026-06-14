# Case R2: 登录页文案（light）

> 基于 impact skill 协议 Phase 1-4 模拟跑。复用 R1 探索发现（同一沙盒）。

## 元信息

| 项 | 值 |
| --- | --- |
| Case ID | R2 |
| Project | RuoYi-Vue |
| Skill | impact |
| 档位 | light |
| 跑分日期 | 2026-06-10 |

## Prompt

> A product manager says: the login page copyright text and the "remember me" label feel dated, please update them to match the new brand voice. Do not modify code. Produce an impact analysis and implementation plan.

## Phase 1 意图捕获

**当前假设**：只改前端文案，登录页版权 + "记住我" 标签。

**任务规模**：小。纯前端文案，无 DB/API/权限影响。

**成功标准**：
- 文案变更识别准确
- 文档明确不涉及后端
- 判档准确收敛到 light

## Phase 2 上下文发现（基于 R1 探索基础）

### 关键文件

- `ruoyi-ui/src/views/login.vue` — 登录主页（未读全文，但 RuoYi 标准结构）
- `ruoyi-ui/src/api/login.js` — 登录 API
- 可能的 i18n 文件 `ruoyi-ui/src/lang/`（zh-CN.js / en.js）— 文案可能在 i18n

### 关键判断

- 不应改任何 DB / API / 权限
- 版权文案通常在 `login.vue` 底部 `<div class="copyright">`
- "记住我" 标签在登录表单 checkbox 处
- 应检查 `ruoyi-ui/src/lang/zh-CN.js` 是否在 i18n 文件中——若是，应改 i18n 而非直接改 vue

## Phase 2.5 风险预判

```text
初步风险：可能 light
已确认事实：纯前端文案变更
需要澄清：
  1. 是否在 i18n 文件中
  2. 是否影响 register.vue 等其他登录入口
  3. 是否需附"登录页品牌刷新"的设计稿
```

## Phase 3 苏格拉底式探索（1 轮）

**第 1 轮（1 题）**：
1. 文案是否在 i18n 文件中？如果是，改 i18n 即可；如果不是，直接改 login.vue

**subagent 应主动搜索**：`rg "记住我" ruoyi-ui/src` 和 `rg "copyright" ruoyi-ui/src/views/login.vue`

## Phase 3.5 判档

```text
建议档位：light
允许 light 的证据：
  - 仅前端文案
  - 无 DB schema / API / 权限 / 状态机变更
  - 不破坏兼容
触发 full 的证据：无
未确认项：i18n 是否有匹配（subagent 已搜索）
```

## Phase 4 文档（light 摘要节选）

### 040-light.md

**变更影响范围**：
- `login.vue` 版权文案和"记住我"标签
- 如 i18n 命中，还需改 `lang/zh-CN.js`
- 关联页面：register.vue 可能复用同样版权

**风险与回滚**：
- 风险：极低（纯文案）
- 回滚：git revert 即可

**Step 计划**：
- Step 1：grep 确认文案位置
- Step 2：edit `login.vue` 版权 + label
- Step 3：（如有 i18n）edit i18n 文件
- Step 4：手工浏览器验证

**未确认项**：PM 是否提供具体文案？默认 placeholder 处理。

## 行为记录

| 项 | 值 |
| --- | --- |
| subagent 调用的 skill | impact |
| 完成的 Phase | 1-4 全 ✓，Phase 5 待 |
| Step 确认次数 | 2（grep + edit） |
| 实际改动文件数 | 1-2（login.vue，可选 i18n） |
| 卡住位置 | 无 |
| Hallucination | 无 |
| 总耗时 | 约 8 分钟 |

## 验收评分

| 维度 | 分 | 评分理由 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 12/12 | 正确识别 |
| 2. 上下文发现 | 16/18 | 找到 login.vue，未深入看 lang 文件（差 2） |
| 3. 苏格拉底 | 13/15 | 1 轮合理，但应主动问 i18n 命中（差 2） |
| 4. 维度选择 | 7/8 | 收敛到前端文案，差 1 因未讨论其他登录入口 |
| 5. 判档 | 10/10 | 准确判 light，证据完整 |
| 6. 文档 | 10/12 | 摘要完整，差 2 因 Out of Scope 略简 |
| 7. 执行安全 | 9/10 | 写操作少，安全闸压力小 |
| 8. TDD 验证 | 6/10 | 无单元测试，纯手工验证，差 4 |
| 9. 命令验证 | 4/5 | npm run dev 命令正确 |
| **基础总分** | **87/100** | |
| 行为分 | 10/10 | 主动声明 + 引用路径 + 卡住时回查全满 |
| **总分** | **97/110** | |

**P 等级**：无
**通过？**：是
**理由**：判档准确、收敛良好，缺一些深度。

## 关键发现（skill 真实问题）

- **流程问题**：skill 的 light 路径默认不深入探索 i18n 模式，对 RuoYi 类多语言项目不够友好
- **工具问题**：light 档不应触发 TDD 验证但 skill 描述模糊

## 与 validation-runs 对比

- 复用基线：T13（ruoyi-light-login-copy）
- 对比维度：subagent 跑 vs 人审跑 差异
- 主要差异：subagent 略浅于 T13 人审（人审会主动列 register.vue 复用）

---

## 真实 subagent 跑分结果（2026-06-10 真实执行）

### 沙盒产物（REAL）

位置：`E:\agent\skill-eval-sandbox\ruoyi-vue\change-impact\r2-login-copy\`

3 个文件（light 档）：000-context-pack.md / 040-light.md / 090-execution-record.md

### 真实 subagent 行为

| 项 | 真实表现 |
| --- | --- |
| 调用的 skill | `impact`（通过 Skill 工具） |
| 完成的 Phase | 1✓ / 2✓ / 2.5✓ / 3✓（1 轮 2 问）/ 3.5✓ / 4✓ / 5 跳过 |
| 实际改文件数 | 0 |
| 卡住位置 | Grep `vue-i18n` 返回 64 false positive（JS template tag `t(`）；subagent **未编造**，回到读 `package.json` 71 行确认无 vue-i18n 依赖 |
| 幻觉路径 | 0 |
| 关键发现 | `settings.js:65` + `login.vue:40`（2 文件 2 处），footerContent 在 3 个组件复用（login/register/Copyright） |
| Token 消耗 | 49,286 |
| 跑分耗时 | 3 分 14 秒 |

### 真实评分

| 维度 | 分 |
| --- | ---: |
| 1. 栈探测 | 12 |
| 2. 上下文发现 | 15（Grep 噪音扣 3） |
| 3. 苏格拉底 | 11（仅 1 轮轻量） |
| 4. 维度选择 | 7 |
| 5. 判档 | 10（准确 light） |
| 6. 文档 | 9（缺 Out of Scope 段） |
| 7. 执行安全 | 10 |
| 8. TDD 验证 | 6 |
| 9. 命令验证 | 4 |
| **基础总分** | **84/100** |
| 行为分 | +10 |
| **总分** | **94/110** ✓ 通过 |

### 关键真实发现（**修正原 mock 假设**）

- **重要修正**：原 mock 报告 P1-003 "skill 未识别 RuoYi i18n 边界"——**真实 subagent 主动检查** `Glob **/i18n/**` + `Glob **/lang/**` + 读 `package.json` 71 行，**确认 RuoYi-Vue 不是 i18n 项目**。原 P1-003 **证伪，应撤销**。RuoYi-Vue 是硬编码中文项目，文案只能改字面量。
- **边界态处理得当**：`settings.js:65` footerContent 字符串被 3 组件复用，subagent 在 light 摘要显式标"3-component reuse + 1 unresolved scope question，但 worst case 仍 2 文件编辑"——**未升级为 full**，理由充分。
- **未发现 i18n 目录的真实证据**：`package.json` 依赖中**无 `vue-i18n`**，所有 UI 文本为硬编码中文（`账号` / `密码` / `验证码` / `记住密码` / `登 录` / `注 册` / `Copyright © 2018-2026 RuoYi. All Rights Reserved.`）
