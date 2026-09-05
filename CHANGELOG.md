# Changelog

本仓库的技能以 Claude Code 插件形式发布，版本记录见下。

## 0.1.1 - 2026-09-05

- 新增 `blue-hub` 路由技能：不知道用哪个技能时，按处境指到对应入口和顺序。
- 新增 `docs/skills/` 技能文档页（12 页，固定四节：它做什么 / 什么时候用 / 常见问题 / 用对了是什么样子）。

## 0.1.0 - 2026-09-05

首次插件化发布。

- 新增 `.claude-plugin/` 插件清单（plugin.json + marketplace.json），插件内含：intent-chain 八件套（intent-anchor / intent-prd / intent-design / intent-visual / intent-issues / intent-dev / intent-adversarial / intent-verify）、impact、pathfinder、vl-vision、ruleblade。
- 律刃（ruleblade）从 `claudecode行为规范/` 移入 `skills/ruleblade/`，并补充 SKILL.md，使其可以随插件安装。
- 技能内的校验器调用路径统一改为"技能目录相对"写法，插件安装后可正常运行。
- impact 与 pathfinder 的改进回流在独立安装环境下优雅降级：`blue-skillhub/_improvements/` 不存在时跳过登记并提示用户。
- 共享校验器目录 `skills/_common/` 随插件分发，技能按"兄弟目录"定位它。
