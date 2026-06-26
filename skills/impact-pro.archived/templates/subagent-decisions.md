# Subagent 决策矩阵 — [变更名称]

> 模板用途：subagent 在 Phase 5 自治模式下，每 Step 必须填写本表。
> 本表是 subagent 的**预决策建议**，不替代人类 `确认 Step N`。subagent 只能建议 execute / pause-and-wait / flag-high-risk，**任何写操作（Edit/Write/DDL/DML/配置变更/测试修复）的执行必须由人类在当前对话中显式 `确认 Step N` 后**方可执行。flag-high-risk 仅限 eval 沙盒（subagent-as-user 协议）中继续只读分析；**生产会话中 flag-high-risk 后必须暂停等待人类**。
> 参考 SKILL.md "高风险 Step 识别清单"。

---

## 上下文快照

- 加载的 profile：
- profile 选择依据（matchers 命中项）：
- 加载的 db-adapter：
- db-adapter 选择依据（运行时探测 / profile 默认 / 兜底）：
- 栈检测确认状态：[已确认 / 用户覆盖 / 降级 generic]

---

## 决策矩阵汇总（必填）

| Step | DECIDE | 高风险清单命中 | 决策依据（1 行） |
| --- | --- | --- | --- |
| 0 | request-human-confirm / flag-and-pause / HUMAN-OVERRIDE-REQUIRED | [如命中写条目，否则写"无"] | [理由] |
| 1 | [同上] | | |
| 2 | [同上] | | |
| ... | | | |

---

## Step N: [操作名称]

### RESTATE
- **目标**：[文件 / 表 / 函数 / 行号]
- **影响范围**：[哪些文件 / API consumer / DB row 受影响]
- **回滚方式**：[精确反向命令]
- **验证方式**：[命令 + 期望结果]

### DECIDE
- **结论**：[request-human-confirm / pause-and-wait / flag-high-risk（仅 eval 沙盒可继续只读分析，生产会话必须暂停）]
- **依据**：
  - 高风险清单检查：
    - DROP TABLE / DROP COLUMN：PASS（不涉及）
    - DELETE FROM 无 WHERE：PASS
    - 删旧接口 / 删旧 Controller 类：PASS
    - 删除文件 without backup：PASS
    - 修改 status / enum / 错误码 / 权限标识：PASS
    - 任何不可逆操作：PASS
  - 其他依据：[如有，写出]

### RECORD
- 写入 090-execution-record.md 的 [HH:MM:SS] Step N 段
- 实际执行：[改了哪些文件 / 跑了哪些命令]
- 验证结果：[V1/V2/V3 通过 / 失败 / 受限]

---

## 决策偏离说明（如有）

如果实际执行**与 implementation.md 计划有偏离**（如用手写 migration 替代 autogenerate），必须在此段显式说明：

- **偏离内容**：[简述]
- **偏离原因**：[为什么]
- **影响**：[正面 / 负面 / 中性]

---

## 收尾

- 实际执行 Steps：[N/N]
- 暂停 Steps：[N/N]
- 拒绝 Steps（需人类）：[N/N]
- 总 Token 消耗：[N]
- 总工具调用：[N]
