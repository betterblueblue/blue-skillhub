# Case F2: 前端深色模式（light）

> FastAPI template 前端。基于 impact-pro frontend-react-vite profile 模拟。

## 元信息

| 项 | 值 |
| --- | --- |
| Case ID | F2 |
| Project | full-stack-fastapi-template（前端） |
| Skill | impact-pro |
| 档位 | light |
| 跑分日期 | 2026-06-10 |

## Prompt

> A product manager says: add a dark mode toggle in user settings, save the preference locally, and have it persist across refreshes. Do not modify code. Produce an impact analysis and implementation plan.

## Phase 1 意图捕获

**当前假设**：纯前端，settings 页面加开关，存 localStorage，刷新后保持。

**任务规模**：小。关键验证判档能正确收敛到 light，不被后端 Python 栈带偏。

## Phase 2 上下文发现

**关键文件**：
- `frontend/src/routes/settings/appearance.tsx` 或类似
- `frontend/src/stores/userSettings.ts`（Zustand/Redux）
- `frontend/src/hooks/useLocalStorage.ts`
- `frontend/src/index.css` 或主题 CSS 变量

**栈**：React + Vite + TypeScript + Chakra UI / Tailwind / shadcn

## Phase 2.5 风险预判

```text
初步风险：可能 light
profile 命中：frontend-react-vite
需要澄清：现有主题方案、CSS 变量还是 class 切换
```

## Phase 3 苏格拉底式探索（1 轮）

1. 项目是否已有 dark mode（用 `data-theme` attribute 还是 CSS variables）？
2. 是否需要跟随系统主题（prefers-color-scheme）？

## Phase 3.5 判档

```text
建议档位：light
允许 light 的证据：纯前端，localStorage 持久化
未确认项：现有主题方案
```

## 行为记录

| 项 | 值 |
| --- | --- |
| subagent 调用的 skill | impact-pro |
| profile | frontend-react-vite |
| 完成的 Phase | 1-4 ✓ |
| 总耗时 | 约 9 分钟 |

## 验收评分

| 维度 | 分 | 评分理由 |
| --- | ---: | --- |
| 1. 栈探测 + profile | 11/12 | 差 1 因未明确指出 Vite 工具链 |
| 2. 上下文发现 | 15/18 | |
| 3. 苏格拉底 | 13/15 | |
| 4. 维度选择 | 7/8 | |
| 5. 判档 | 10/10 | 准确判 light |
| 6. 文档 | 10/12 | |
| 7. 执行安全 | 9/10 | |
| 8. TDD 验证 | 7/10 | Vitest 命令正确 |
| 9. 命令验证 | 4/5 | |
| **基础总分** | **86/100** | |
| 行为分 | 7/10 | |
| **总分** | **93/110** | |

**P 等级**：无
**通过？**：是

## 关键发现

- profile frontend-react-vite 准确引导前端栈
- 优点：判 light 未受 monorepo 后端影响

---

## 真实 subagent 跑分结果（2026-06-10 真实执行）

### 沙盒产物（REAL）

位置：`E:\agent\skill-eval-sandbox\fastapi\frontend\change-impact\f2-dark-mode\`

3 个文件（light 档）：context-pack.md / light-影响摘要.md（写得最完整，12 段）/ 900-执行记录.md

### 真实 subagent 行为

| 项 | 真实表现 |
| --- | --- |
| 调用的 skill | `impact-pro`（通过 Skill 工具） |
| 加载的 profile | `frontend-react-vite`（Level 1） |
| 完成的 Phase | 1✓ / 2✓ / 2.5✓ / 3✓（1 轮 1 问）/ 3.5✓ / 4✓ / 5 跳过 |
| 实际改文件数 | 0（仅 frontend/ 目录；backend/ 未触碰） |
| 关键发现 | **dark mode 已完全实现**——`ThemeProvider` + `localStorage("vite-ui-theme")` + `<Appearance />` + 3 个 E2E |
| 幻觉路径 | 0 |
| Token 消耗 | 57,806 |
| 跑分耗时 | 3 分 41 秒 |

### 真实评分

| 维度 | 分 |
| --- | ---: |
| 1. 栈探测 + profile | 12 |
| 2. 上下文发现 | 18（**完美**：5 文件全找） |
| 3. 苏格拉底 | 13 |
| 4. 维度选择 | 8 |
| 5. 判档 | 10（准确 light） |
| 6. 文档 | 11（最完整 light 摘要） |
| 7. 执行安全 | 10 |
| 8. TDD 验证 | 7 |
| 9. 命令验证 | 4 |
| **基础总分** | **93/100** |
| 行为分 | +10 |
| **总分** | **103/110** ✓ 通过 |

### 关键真实发现（**全场最大正向发现**）

- **Dark mode 已完整实现**：

  | 现状 | 证据 |
  | --- | --- |
  | `ThemeProvider`（light/dark/system 三态） | `src/components/theme-provider.tsx:9` |
  | `localStorage` 持久化 `vite-ui-theme` | `src/components/theme-provider.tsx:96` |
  | 启动时回读 + `prefers-color-scheme` | `src/components/theme-provider.tsx:38` |
  | 根挂载 | `src/main.tsx:45` |
  | UI 组件 `<Appearance />` + `<SidebarAppearance />` | `src/components/Common/Appearance.tsx` |
  | `.dark` / `:root` CSS 变量 | `src/index.css:44-111` |
  | E2E 覆盖（按钮可见 / 切换 / 跨登录持久化） | `tests/user-settings.spec.ts:205-256` |

  **PM 需求"加 dark mode"实际只是"在 `/settings` 页加 Appearance Tab"**——subagent 没有按 PM 字面意思"建新 dark mode"，而是建议"复用现有组件"。

- **死依赖发现**：`next-themes` 在 `package.json:40` 但**未导入**——subagent 显式标"不在本变更范围"，未自作主张清理。

- **没踩"monorepo trap"**：subagent 正确避免建议后端 / DB / API 改动，**front-end-only** 边界守得干净。

- **失败模式预防**：subagent 在最终报告里指出"less rigorous agent would have proposed building new theme infrastructure from scratch"——这是**反向激励 skill 的 evidence-based discovery**。

### 唯一缺口

`src/routes/_layout/settings.tsx` 当前的 Tabs 是 `My profile / Password / Danger zone`，**没有给 Appearance 留位置**。这是本次变更的**唯一修改点**。
