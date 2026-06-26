# T13 RuoYi-Vue - 登录页版权/提示文案调整

- 测试日期：2026-06-07
- 测试人：Codex
- 项目栈：Java / Spring Boot / MyBatis / Vue 2 / Element UI
- 项目路径：`E:\agent\impact-pro-validation-work\RuoYi-Vue`
- 变更意图：调整登录页底部版权文案和登录按钮加载文案，不改认证逻辑。
- 使用档位：light
- 命中 profile：`java-spring-mybatis` + 前端 Vue 目录辅助发现
- 最终评分：91
- 失败等级：无

## 实际发现

关键文件：

- `ruoyi-ui/src/views/login.vue`：登录标题、账号/密码/验证码占位、按钮文案、`footerContent` 渲染、登录提交逻辑。
- `ruoyi-ui/src/settings.js`：`footerContent`、`footerVisible`、布局和主题配置。
- `ruoyi-ui/package.json`：前端构建和 lint 命令来源。

## 验收判断

应判定 light。

理由：

- 不涉及 Java Controller/Service/Mapper。
- 不涉及 DB schema、SQL、权限、验证码接口或认证流程。
- 只涉及前端静态文案和配置读取。

## 风险追问

1. 新版权文案是否需要按环境或品牌动态区分？
2. 是否需要同步浏览器标题或侧边栏品牌名？
3. 登录按钮加载文案是否需要保持中文/英文 i18n 一致？

## 验证方案

- 前端 lint/build。
- 手动或 E2E 检查登录页 footer、按钮 loading 文案、验证码刷新仍可用。
- 错误用例：登录失败后 loading 恢复，验证码仍按原逻辑刷新。

## 问题清单

| 等级 | 问题 | 证据 | 修复建议 |
|------|------|------|----------|
| P3 | Vue 前端不是 `java-spring-mybatis` 主体 | `ruoyi-ui/src/views/login.vue` | RuoYi 项目命中 Java profile 后，前端目录需作为辅助上下文 |

## 结论

通过（light）。该用例补充 RuoYi 样本的第二变更，验证 `impact-pro` 能在 Java 项目中识别前端-only light 变更，不误生成 Mapper/XML/SQL 计划。
