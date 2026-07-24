# Issues - 团队进度助手

<!--
  本文件由 intent-issues skill 生成。
  前置文件：intent-anchor/valid-intent.md 和 prd/valid-prd.md
  生成日期：2026-07-24
-->

---

## Issue 1: 生成交接记录功能

- **类型**：AFK

### What to build

在会话结束前触发生成交接记录，记录包含任务、进度、阻塞和下一步。新会话读取记录后能恢复进度。

### Acceptance criteria

**[P01] 正常生成交接记录**
- Given: 当前会话有 3 个进行中的任务和 1 个阻塞项
- When: 触发生成交接记录
- [ ] Then: 记录文件存在
- [ ] And: 记录包含任务列表
- [ ] And: 记录包含进度和阻塞项
- [ ] And: 记录包含下一步
- [ ] And: 记录不包含敏感信息 [SF01]

### Blocked by

None - can start immediately

### User stories covered

- Story 1 [C01]

---

## Coverage Verification

### 验收路径覆盖

| 路径 ID | 验收路径 | 覆盖工单 | 状态 |
|---|---|---|---|
| P01 | 生成并查看交接记录 | Issue 1 | 已覆盖 |

### 保留能力覆盖

| 能力 ID | 保留能力 | 覆盖工单 | 状态 |
|---|---|---|---|
| C01 | 生成交接记录 | Issue 1 | 已覆盖 |

### 新增能力

无。
