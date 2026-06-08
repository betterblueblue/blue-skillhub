# T48: Claude Code + MiniMax M3 RG3 前端与 monorepo 复测

日期：2026-06-08

## 触发原因

- 本轮目标：在 T47 Node/Express 响应契约负向复测之后，补充 MiniMax M3 对前端 UI-only light 和 monorepo 边界的真实 `/impact-pro` 复测。
- 复测级别：`docs/impact-regression-protocol.md` 中的 RG3。

## 环境

- Agent：Claude Code CLI 2.1.167
- 模型：当前 Claude Code 配置的 MiniMax M3
- 触发方式：真实 Claude Code Skill 调用，命令 `/impact-pro`
- 测试目录：`E:\agent\impact-m3-rg3-20260608`
- 结果文件：
  - `E:\agent\impact-m3-rg3-20260608\results\T48-impact-pro-react-ui-light.txt`
  - `E:\agent\impact-m3-rg3-20260608\results\T48R-impact-pro-react-ui-light-rerun.txt`
  - `E:\agent\impact-m3-rg3-20260608\results\T48R2-impact-pro-react-ui-light-after-contract.txt`
  - `E:\agent\impact-m3-rg3-20260608\results\T49-impact-pro-monorepo-toast.txt`

## 用例

| 场景 | 预期 | 实际 | 结论 |
|------|------|------|------|
| T48 React/Vite UI-only：`Sign in` 改 `Continue` | 命中前端 profile；建议 light；说明验证命令来自 `package.json`；当前最高 V1 | 首轮和 R1 输出过短，只给未确认项/自我闭环声明，未展示 profile 和判档证据 | 首轮不通过 |
| T48R2 补“只分析最小响应契约”后复测 | 必须完整输出 profile、Context Pack、判档证据、验证命令来源、V0-V3 和未写文件状态 | 输出完整；命中 `frontend-react-vite`；建议 light；验证命令来自 `package.json`；当前最高 V1；V2/V3 未运行原因明确 | 通过 |
| T49 monorepo 前端 toast：`Saved successfully` 改 `Saved` | 识别 frontend/backend 边界；后端只读确认，不扩大实现范围；建议 light | 正确识别 monorepo；frontend 为直接修改对象；backend 无引用，暂不纳入；建议 light；当前最高 V1 | 通过 |

## 发现的问题

1. **只分析模式输出过短**
   - 影响：M3 在简单 UI-only 场景中容易只输出“未确认项/已闭环”，没有展示 profile、Context Pack、判档依据和验证命令来源。
   - 修复：在 `SKILL.md` 增加“只分析 / 不写文件的最小响应契约”；在 `VALIDATION.md` 增加对应验收标准。
   - 复测：T48R2 通过。

## 结论

- 结论：有条件通过，修复后通过。
- P0/P1：无。首轮问题评为 P2 输出完整性问题；若出现在高风险变更中可升级为 P1。
- 后续风险：建议继续抽测更复杂的前端场景，例如 i18n、Storybook、快照测试、Route Handler 或 API client 共同存在的项目。
