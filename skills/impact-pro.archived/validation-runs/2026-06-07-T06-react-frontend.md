# T06 full-stack-fastapi-template/frontend - 设置页主题偏好

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：React / Vite / TanStack Router / Playwright
- 项目路径：`E:\agent\impact-pro-validation-work\full-stack-fastapi-template\frontend`
- Commit：`38302d7492dbd158ed6cf499a6dd0bab6ad17141`
- 变更意图：在用户设置页调整主题偏好行为，保存到本地设置并刷新/重新登录后保持。
- 使用档位：light
- 命中 profile：`generic`
- 最终评分：76
- 失败等级：P2

## 实际发现

### 技术栈检测

可识别证据：

- `package.json` 存在。
- 依赖包含 `react`、`vite`、`@tanstack/react-router`、`@playwright/test`、`next-themes`。
- `package.json` scripts 包含 `build`、`lint`、`test`。

当前 `impact-pro` 无前端专属 profile，因此加载 `generic`。

### 上下文发现

真实关键文件：

- `src/main.tsx`
- `src/components/theme-provider.tsx`
- `src/components/Common/Appearance.tsx`
- `src/routes/_layout/settings.tsx`
- `tests/user-settings.spec.ts`
- `src/index.css`

当前 `generic` glob 可发现：

- `tests/user-settings.spec.ts`

当前 `generic` 默认不覆盖：

- `**/*.tsx`
- `src/routes/**/*.tsx`
- `src/components/**/*.tsx`
- `src/index.css`

关键证据：

- `ThemeProvider` 使用 `localStorage.getItem(storageKey)` 初始化主题。
- `setTheme()` 写入 `localStorage`。
- `main.tsx` 使用 `ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme"`。
- `user-settings.spec.ts` 已覆盖主题切换和会话保持。

### 风险追问

应追问：

1. 是否保留 `dark` 默认值，还是改为 `system`？
2. 非法 localStorage 值如何处理？
3. 主题切换是否仅本地保存，还是要同步用户服务端设置？
4. 是否需要覆盖刷新、重新登录、系统主题变化三种场景？

### 定级

应判定 light。

理由：

- 不涉及 DB。
- 不涉及后端 API。
- 主要影响前端状态、本地存储和 E2E 测试。

但如果要求服务端同步用户偏好，应升级为 full。

## 评分

| 维度 | 分值 | 得分 | 说明 |
|------|------|------|------|
| 技术栈检测与 profile 选择 | 15 | 12 | 识别 package，但无前端 profile |
| 上下文发现 | 20 | 10 | 能找到测试，漏核心 TSX 组件 |
| 风险识别与追问 | 20 | 15 | 风险清楚，但证据发现不足 |
| light/full 定级 | 10 | 9 | light 合理 |
| 文档质量 | 15 | 11 | 不应生成 DB 章节，模板需更前端化 |
| 执行安全 | 10 | 10 | 写操作确认规则存在 |
| 验证设计 | 10 | 9 | Playwright 用例形态正确 |

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P2 | generic 不覆盖 TSX 组件 | `theme-provider.tsx`、`settings.tsx` 未匹配 | 新增前端 profile |
| P2 | generic 模板偏后端/DB | 无 DB 项目仍需人工删数据库章节 | 模板按维度动态裁剪 |
| P3 | 无 CSS/theme 风格轴 | `index.css` 包含 `.dark` 和主题变量 | profile 增加 theme/style 发现 |

## 结论

仅可辅助分析。前端项目需要专属 profile 后再进入稳定使用。
