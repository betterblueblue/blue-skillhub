# ADR-004 _common 为什么随插件分发但不进插件 skills 数组

日期：2026-09-05　状态：已采纳

## 决定

`skills/_common/`（共享校验器、markdown_parser、chain_validate、rules.md）随插件整体分发，但**不列进 plugin.json 的 skills 数组**——它没有 SKILL.md，不是技能，是技能们共享的基础设施。

## 为什么

- 插件把整个仓库作为安装单元，`_common` 天然随行；各技能按"兄弟目录"定位它（校验器内部用 `Path(__file__).parent.parent.parent / "_common"`，SKILL.md 里写 `../_common/rules.md`），插件安装和手动复制两种形态下相对路径都成立。
- 列进 skills 数组反而会让客户端把它当一个技能加载，报"缺 SKILL.md"或在技能列表里出现一个无意义的条目。

## 约束（改代码前必读）

- `_common` 的目录名和位置**不能改**：它是所有技能的兄弟锚点。
- 新增共享校验器放这里；技能专属校验器放各自 `scripts/`。
- 交互话术不进 `_common`（见 ADR-001）。
