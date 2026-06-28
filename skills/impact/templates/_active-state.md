# [变更名称] 活跃状态

> 跨会话恢复状态文件。这是一个检查点，不构成任何写操作授权。
> 它永远不能替代当前对话中的 `确认 Step N`。

## 状态头

- 更新时间：[真实系统时间]
- skill：impact
- 目标项目根目录：
  - 绝对路径：[如 E:\projects\ruoyi-vue]
  - 判定方式：[git-rev-parse / user-specified / pom-dot-xml / build-dot-gradle / package-dot-json / inferred-from-cwd / other]
  - 验证时间：[真实系统时间 ISO 8601]
- 需求目录：`change-impact/[需求名称]/`
- 当前阶段：[Phase 4 / Phase 5 / 阻塞 / 完成]
- 模式：[light / full]
- 执行方式：[auto / manual]  — 当前会话是 agent 自主执行还是人类逐步确认
- 并发锁：[none / locked_by_[agent_id]]  — 多 agent 不能同时操作同一需求目录
- 当前 Git HEAD：[HEAD / 非 Git / Git 不可用]
- Git 审计状态：[clean / dirty / non-git / unavailable]
- 是否需要确认：[true / false]
- 待执行 Step：[Step N / none]
- 上次提示 Step：[Step N / none]
- 上次确认 Step：[Step N / none]
- 上次完成 Step：[Step N / none]
- V1-only 计数：[N]

## 当前意图

- 用户目标：[用户原始变更意图摘要]
- 当前假设：[当前假设]
- 成功标准：[可验证完成标准]
- 更简单方案：[更简单方案 / 不适用]

## 文档状态

| 文档 | 状态 | 备注 |
| --- | --- | --- |
| 000-context-pack.md | 缺失 / 草稿 / 已确认 | |
| 010-requirements.md | 缺失 / 草稿 / 已确认 / 不适用 | |
| 020-design.md | 缺失 / 草稿 / 已确认 / 不适用 | |
| 030-implementation.md | 缺失 / 草稿 / 已确认 / 不适用 | |
| 040-light.md | 缺失 / 草稿 / 已确认 / 不适用 | |
| 060-preflight.md | 缺失 / 草稿 / 通过 / 阻塞 | |
| 090-execution-record.md | 缺失 / 活跃 | |

## Step 台账

| Step | 状态 | 写入对象 | 确认 | 验证等级 | 备注 |
| --- | --- | --- | --- | --- | --- |
| Step N | 计划 / 待确认 / 已确认 / 成功 / 失败 / 跳过 | [文件/表/配置] | [需要 / 已确认 / 跳过] | [V0-V3] | |

## 恢复检查

恢复任何写操作前：

- [ ] 重新读本文件
- [ ] 重新读 030-implementation.md 或 040-light.md
- [ ] 如有 060-preflight.md 则重新读
- [ ] 检查当前 git 状态 / 目标文件状态
- [ ] 复述待执行 Step 和写入对象
- [ ] 要求当前对话中新的 `确认 Step N`

## 待确认项

> 代码可推断项已由 Agent 自行查证（见 context-pack §7），此处只保留业务需决策项。

- [业务决策项 / 风险 / 用户决策]

## 最近验证

- 命令：`[命令]`
- 结果：[通过 / 失败 / 跳过]
- 验证等级：[V0 / V1 / V2 / V3]
- 跳过原因：[原因 / 不适用]

## 恢复备注

- [恢复时读到的冲突、不一致、阻塞项、下一步安全动作]
