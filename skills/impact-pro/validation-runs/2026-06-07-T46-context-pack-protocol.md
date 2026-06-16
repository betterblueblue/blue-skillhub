# T46 Context Pack 协议回归

## 目标

验证 `impact-pro` 是否能参考 Context Engine / ACE 一类思路，把多栈项目的上下文发现固化成可执行、可解释、可移交的 Context Pack 协议。

这里不复刻外部产品能力，也不依赖第三方 key；只把“刚好够用、刚好相关”的上下文选择方法落到 Skill 规则、profile schema、模板和验收标准中。

## 检查范围

- `SKILL.md`
- `README.md`
- `VALIDATION.md`
- `profiles/_schema.md`
- `profiles/_template.md`
- `templates/000-context-pack.md`
- `templates/010-requirements.md`
- `templates/020-design.md`
- `templates/040-light.md`
- `templates/060-preflight.md`

## 验收项

| 检查项 | 预期 | 结果 |
|--------|------|------|
| 通用内核 | Phase 2 明确包含技术栈检测、profile 加载和 Context Pack 构建 | 通过 |
| profile 指引 | `_schema.md` / `_template.md` 提供 `context_discovery` 字段 | 通过 |
| 内置 profile | bundled profiles 均显式提供 `context_discovery`，无需临场推导 | 通过 |
| 旧 profile 兼容 | 外部或历史 profile 缺少 `context_discovery` 时，从 `discovery_globs` 推导 | 通过 |
| 分层探索 | L1 项目地图、L2 变更邻域、L3 精准证据逐层收敛 | 通过 |
| 相关性分级 | 候选文件/对象必须标注 3/2/1/0，并说明用途 | 通过 |
| 上下文预算 | 限制读取数量和片段大小，超出预算先问最多 3 个收敛问题 | 通过 |
| 排除记录 | 看过但不相关的文件必须记录排除原因 | 通过 |
| 定级时机 | Context Pack 和苏格拉底澄清完成后才正式 light/full 定级 | 通过 |
| 写入门禁 | `000-context-pack.md` 先在对话输出草案，写入文件仍需用户确认 | 通过 |
| 文档串联 | requirements/design/light/preflight 都能引用 Context Pack 摘要 | 通过 |

## 结论

通过。`impact-pro` 现在不仅要求“发现上下文”，还要求 agent 解释上下文为什么被纳入、为什么被排除、哪些事实已确认、哪些问题仍需用户拍板。

这能帮助其他 agent 模仿 ACE 的核心收益：不是拿最多上下文，而是拿对当前变更刚好够用的上下文，并且保留可审计的选择理由。

补强项：内置 `generic`、Java、Node、Python、Go、.NET、React、Next.js、Nuxt/Vue profile 已全部补充显式 `context_discovery`，新旧 profile 仍保留 schema 级兼容规则。
