# Changelog

本仓库的技能以 Claude Code 插件形式发布，版本记录见下。

## 0.1.7 - 2026-09-05

第二档借鉴落地：

- intent-issues 新增**决策工单**：拆工单时遇到"要拍板而非写代码"的前置问题（如押金支付形态），立 `[D-xx]` 决策工单（类型「需拍板」，必需段落：决策问题/选项/状态/决议去向）；实现工单可依赖未拍板决策使其显式挡路；拍板决议回写 design.md。issues_validate 新增 V14（状态必须为「待拍板」或含用户确认的「已拍板」）与 V2 类型感知（决策工单按决策段落校验）。
- impact 的 phase-5 新增**人工执行脚本格式框架**：交给人工在生产环境执行的 DDL/DML 脚本自带影响预告、回滚提示、输对象名确认门（不收 y）、分步进度与收尾摘要。
- 新增 `docs/adr/` 四篇决策备忘：交互话术为什么内联、历史清理为什么用 filter-repo、轻量档为什么只升不降、_common 为什么随插件分发但不列为技能。

## 0.1.6 - 2026-09-05

借鉴 Skills for Real Engineers（Matt Pocock）的三处方法论，全部为技能文档级改动，不涉及校验器：

- intent-design 新增**假设表岔路（体验验证）**：标"无依据"的假设若要亲手体验才能拍板，主动建议做一次性小样让用户体验后再定；小样是弃子、不进交付。内置降级：未安装任何原型技能时按规则现场做即可。
- intent-design 新增 `references/deep-module.md`（普通话版深模块判据）：学多少得多少、删除测试、浅转发层识别，供「模块与边界」自查。
- intent-dev 新增**测试入口清单**：写测试前先列出功能对外的入口（验收路径入口 + 公开方法）并给用户确认，测试只从入口进、不调内部私有方法——内部重构不再牵连测试。

## 0.1.5 - 2026-09-05

- README 重构：679 行减到 386 行。删除技能详介（由 docs/skills/ 承接）与 18 行长场景表（由 ask-blue 与 6 行短表承接）；「快速验证」合并进安装与验证清单（含中断恢复对话示例）；「研究与实验记录」移至 docs/research.md。开场门面（GIF、全景图）、3 分钟上手、链路图、三核心分工表、"谁更需要严格门禁"、复盘回流原样保留。
- 修复安装与验证清单中一个从未生效的锚点（原指向 README FAQ 列表项，改为指向清单内部同名小节）。

## 0.1.4 - 2026-09-05

- 路由技能 `blue-hub` 更名为 `ask-blue`（目录、frontmatter、文档页、插件清单同步更名）。

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
