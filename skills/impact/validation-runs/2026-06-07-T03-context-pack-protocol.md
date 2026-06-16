# T03 项目背景协议回归

## 目标

验证 `impact` 是否能把"上下文发现"升级成可交给后续 agent 使用的项目背景，而不是把搜索结果一次性堆给模型。

## 检查范围

- `SKILL.md`
- `README.md`
- `VALIDATION.md`
- `templates/000-context-pack.md`
- `templates/010-requirements.md`
- `templates/020-design.md`
- `templates/040-light.md`
- `templates/060-preflight.md`

## 验收项

| 检查项 | 预期 | 结果 |
|--------|------|------|
| Phase 2 产物 | Phase 2 必须先输出项目背景草案 | 通过 |
| 分层探索 | 包含 L1 项目地图、L2 变更邻域、L3 精准证据 | 通过 |
| 相关性分级 | 文件、表、接口、配置项可标注 3/2/1/0 | 通过 |
| 上下文预算 | 限制 L1/L2/L3 读取规模，超出后先追问收敛 | 通过 |
| 排除记录 | 看过但无关的对象写入"暂不纳入范围" | 通过 |
| 定级时机 | 未完成项目背景前不得正式 light/full 定级 | 通过 |
| 写安全闸 | `000-context-pack.md` 仍属于文档写入，必须等用户确认 | 通过 |
| 下游模板引用 | full/light/preflight 模板能引用项目背景摘要 | 通过 |

## 结论

通过。`impact` 现在要求 agent 先构建小而准、可解释的项目背景，再进入风险预判、苏格拉底式澄清和正式定级。

该机制适合 Java/Spring/MyBatis/RuoYi 类现有系统，目标是减少上下文过载、漏读关键文件和凭空补全表结构/API 的问题。
