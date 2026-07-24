# PRD - 团队进度助手

## Problem Statement

跨天使用 AI 编码助手的开发者在每次换会话后都要重新解释做到哪里，进度信息在会话切换中丢失。

## Solution

在会话结束前自动生成交接记录，包含任务、进度、阻塞和下一步。新会话读取记录后能准确继续工作。交接记录绝对不能丢。

## User Stories

1. As a 开发者, I want 在会话结束前自动生成包含任务进度和阻塞的交接记录, so that 新会话能准确继续工作 [C01]

## Implementation Decisions

- 交接记录格式：Markdown，包含任务列表、当前进度、阻塞项和下一步
- 存储位置：项目根目录的 handoff/ 目录

### Design Standards

无设计标准素材。

### Terminology Constraints

无术语约束。

### Security Requirements

| 要求 ID | 安全要求 | 对应能力 |
|---|---|---|
| SF01 | 交接记录不包含敏感信息（密码、token 等） | C01 |

## Acceptance Criteria

### P01: 生成并查看交接记录

对应 User Stories: Story 1

- **Given** 当前会话有 3 个进行中的任务和 1 个阻塞项
- **When** 触发生成交接记录
- **Then** 记录文件存在
- **And** 记录包含任务列表
- **And** 记录包含进度和阻塞项
- **And** 记录包含下一步
- **And** 记录不包含敏感信息 [SF01]

## Testing Decisions

- 测试交接记录生成逻辑：输入任务状态，输出格式正确的记录
- 测试新会话读取记录后能恢复进度

## Out of Scope

- 自动归档旧记录：推迟，第一版先验证交接内容是否有用
- 自动发送通知：放弃，不连接外部聊天工具

## Intent Verification

### 保留能力覆盖

| 能力 ID | 保留能力 | PRD 中的位置 | 状态 |
|---|---|---|---|
| C01 | 生成交接记录 | User Story 1, Implementation Decisions | 已体现 |

### 不可妥协项核对

| 能力 ID | 不可妥协项 | PRD 是否支持 | 证据 |
|---|---|---|---|
| C01 | 没有交接记录就无法解决跨会话丢失问题 | 支持 | User Story 1 和 Solution 明确要求生成记录 |

### 新增能力

无。
