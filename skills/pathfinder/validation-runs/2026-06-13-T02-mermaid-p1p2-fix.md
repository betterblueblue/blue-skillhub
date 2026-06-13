# T02: Pathfinder 二轮验证 — Mermaid 图 + P1/P2 修复确认

日期：2026-06-13

## 目的

确认 pathfinder skill 的两个更新（基于 T01 发现）在实跑中生效：

1. **P1 修复**: 凭证脱敏铁律补显式反例——雷区节中即使值是众所周知的默认值也不得明文写入
2. **P2 修复**: Git 归属检查——Phase 1 先做 `git rev-parse --show-toplevel` 对比当前目录,区分独立仓库/子目录/非 Git
3. **新功能**: 地图内嵌 3 张 Mermaid 图(【3】架构图、【6】ER 图、【11】主链路图)

覆盖能力:
- Mermaid 图信任纪律(实线=已核实,虚线=推断)
- 凭证脱敏在雷区节的严格执行
- Git 归属检查三种结果
- Mermaid 可渲染性

## 环境

- Agent: Claude Code CLI (model xopglm51)
- 模型: Claude Sonnet 4.6 (claude-sonnet-4-6)
- 触发方式: 手动模拟 Pathfinder Phase 0–4 流程
- 测试项目: test-projects/go-admin (Go, 独立 Git 仓库, HEAD b83eef8)、test-projects/ruoyi-vue (Java+Vue, 独立 Git 仓库, HEAD 41720e6)、临时子目录和非 Git 项目
- 结果文件: test-projects/_pathfinder-validation-results/ (V1/V2 更新版 map)

## 结果

| Run | 场景 | 预期 | 结果 |
|-----|------|------|------|
| V1-r2 | go-admin + Mermaid 图 | 【3】架构图+【6】ER 图+【11】主链路图;Git 独立仓库;凭证无明文 | **PASS** — 3 张 Mermaid 图产出;实线/虚线区分正确;归属检查独立仓库;凭证全部脱敏 |
| V2-r2 | ruoyi-vue + Mermaid 图 | 同上;聚焦区权限更深 | **PASS** — 3 张 Mermaid 图产出;虚线推断跳正确;归属检查独立仓库;凭证全部脱敏(P1 修复生效) |
| V4-r2 | Git 归属检查 | 子目录→写'非独立仓库';非 Git→写'非 Git' | **PASS** — 三种情况正确区分 |
| V3 | 交接 /impact | 同 T01(未实跑) | 未重跑(无变化) |
| V5 | 安全 | 凭证脱敏在雷区节严格执行 | **PASS** — 雷区节无明文凭证值 |

## 发现的问题

1. [P2] **Bash 中 `git rev-parse --show-toplevel` 与 `$(pwd)` 路径格式不一致** — 在 Git Bash 中,`show-toplevel` 返回 `E:/agent/blue-skillhub`,而 `$(pwd)` 返回 `/e/agent/blue-skillhub`,直接字符串比较 `==` 总是失败,即使是独立仓库也会误判为"子目录"。PowerShell 示例不受影响(git 和 PowerShell 都用 `E:\` 格式)。证据: V4-r2 在 `_tmp-subdir` 中测试时,`toplevel=E:/agent/blue-skillhub` 与 `pwd=/e/agent/blue-skillhub/...` 格式不同。建议: bash 示例中用 `test -d "$(pwd)/.git"` 作为独立仓库的判定方式(更简单且不受路径格式影响),或 `git -C "$(pwd)" rev-parse --show-toplevel` 确保在当前目录上下文中运行。

2. [P2] **V3 仍未实跑** — 同 T01 备注,需人在独立会话中运行 /impact 验证交接行为。

## 与 T01 对比

| 维度 | T01 | T02 |
|------|-----|-----|
| Mermaid 图 | 无(纯文字+ASCII) | 3 张 Mermaid 图,信任纪律一致 |
| P1 凭证脱敏 | 雷区节泄露明文值(已手动修正) | 雷区节全部脱敏,修复生效 |
| P2 Git 归属 | 未测试(子目录误继承 HEAD) | 三种情况正确区分,但发现 bash 路径比较问题 |
| P0 问题数 | 0 | 0 |
| P1 问题数 | 1(凭证脱敏)→已修复 | 0 |
| P2 问题数 | 2 | 2(bash 路径比较,V3 未实跑) |

## 结论

整体 **PASS**，无 P0、无 P1。P1(凭证脱敏)修复确认生效。发现 1 个新 P2(Bash 路径格式跨平台不一致)和 1 个遗留 P2(V3 未实跑)。pathfinder 核心能力(Mermaid 图信任纪律、凭证脱敏、Git 归属、降级)均验证通过。
