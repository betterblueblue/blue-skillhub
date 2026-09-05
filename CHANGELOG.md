# Changelog

本仓库的技能以 Claude Code 插件形式发布，版本记录见下。

## 0.1.3 - 2026-09-05

阶段 3 单源化返工：

- `rules.md` 去掉「改进记录交互」节：用户交互话术按 `tests/test_skill_improvement_prompt.py` 契约回归内联（intent-anchor、pathfinder、impact 三处自包含），并补上 impact 历史缺失的"普通完成不询问"。
- 修复指针路径：`{_common 目录}` 占位符全部替换为可解析的 `../_common/rules.md`（`_common` 与每个技能目录同级，插件安装与手动复制两种形态下均成立），intent-verify 的 chain_validate 引用同步修正。
- 说人话与确认语义的正文瘦成主题指针，语义只在 `rules.md` 一处，不再双源。
- 回归：完整 CI 测试面九项全部通过（契约测试、353 项技能测试、三个校验器直跑、_common 单测、真实项目矩阵、eval 交付检查、run.sh 循环、模板同步 10/10、元数据校验）。

## 0.1.2 - 2026-09-05

- 新增共享规则文件 `skills/_common/rules.md`：跨技能重复规则的详细定义（面向用户表述、确认语义、验证声明、改进记录交互、档位升降）收进单一来源。
- 8 个 SKILL.md 去重（impact、pathfinder、intent-anchor / prd / design / issues / dev / verify）：正文保留一行自足摘要加指针，技能特有约束（如工单类型字段的写法、impact 产物双读者）原文保留。

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
