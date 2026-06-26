# T20 nuxt-ui-templates/dashboard - 用户菜单主题文案调整

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Nuxt 4 / Vue 3 / Nuxt UI / VueUse
- 项目路径：`E:\agent\impact-pro-validation-work\nuxt-dashboard`
- 变更意图：调整用户菜单里的 `Theme` / `Appearance` 文案或默认主题展示文案，不改主题切换逻辑。
- 使用档位：light
- 命中 profile：`frontend-nuxt-vue`
- 最终评分：92
- 失败等级：无

## 实际发现

关键文件：

- `app/components/UserMenu.vue`：用户菜单、Theme/Appearance 分组、`useColorMode()`、`useAppConfig()`、颜色选择。
- `app/app.config.ts`：默认 `primary` / `neutral` 颜色。
- `app/app.vue`：根据 `colorMode.value` 计算页面背景 meta color。
- `app/pages/settings/index.vue`：设置页 profile 文案和 toast 风格证据。

## 验收判断

应判定 light。

理由：

- 只改菜单 label，不改 `colorMode.preference`、`appConfig.ui.colors`、Nuxt config 或 server API。
- 不涉及 DB、Nitro server API、持久化 schema。
- 需要检查文案是否影响可访问名称和测试选择器。

## 风险追问

1. 是否只改用户菜单文案，还是设置页标题也同步？
2. 新文案是否影响已有 E2E 通过 role/name 查找按钮？
3. 是否需要多语言资源，还是模板硬编码即可？

## 验证方案

- `pnpm run typecheck`。
- `pnpm run lint`。
- UI 检查：用户菜单展开后新文案可见；Light/Dark 切换仍更新 `colorMode.preference`。
- 回归：颜色选择仍写入 `appConfig.ui.colors`。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | 文案可能是测试可访问名称 | `label: 'Theme'`、`label: 'Appearance'` | 验证中用 role/name 的测试需同步 |

## 结论

通过（light）。该用例补充 Nuxt/Vue 样本第二变更，验证 profile 能隔离 UI 文案与主题状态逻辑。
