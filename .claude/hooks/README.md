# Impact 写入前检查 Hook

这是 ImpactRadar 推荐使用的 `PreToolUse` Hook。它会在 Claude Code 执行写操作前检查用户授权，补上文档校验脚本无法提供的实时保护。

## 工作方式

1. 只有项目根目录存在 `.impact-protected` 时，Hook 才会保护该项目。
2. 在受保护项目中调用 `Write`、`Edit`、`MultiEdit`、`NotebookEdit` 或可能写入文件的 `Bash` 命令前，当前会话中最后一条真实用户消息必须以 `确认 Step N` 开头。
3. 每次确认在同一个项目根目录下只能放行一次写操作。再次写入时，需要用户重新确认。
4. 写入源码、测试、配置或 schema 时，还必须找到对应的 `change-impact/<需求目录>/_active-state.md`。其中记录的待执行步骤要与本次确认一致，Phase 4 文档和 `060-preflight.md` 必须存在，最近一次校验结果中的失败数必须为 0。

写入 `change-impact/` 内的分析文档时，不要求源码写入所需的 Phase 4 完成状态和 `060-preflight.md`；但仍需遵守 ImpactRadar 自身的文档写入确认规则。Hook 放行某项操作，不代表 Skill 流程中的其他条件都已满足。

## 启用方法

把 `impact-write-gate.settings.example.json` 中的配置合并到 `.claude/settings.json` 或 `.claude/settings.local.json`。仓库不会自动修改这两个文件。

然后在需要保护的目标项目根目录创建一个空文件：

```text
.impact-protected
```

建议启用这个 Hook，是因为 V18、V20 等校验只能检查写入后的文档记录，无法证明工具执行前最后一条用户消息究竟是什么。Hook 会读取当前会话记录，并在写操作发生前完成这项检查。

## 跨平台命令

示例配置直接调用 Python：

```json
"command": "python .claude/hooks/impact-write-gate.py"
```

也可以通过包装脚本调用：

- Windows PowerShell：`powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/impact-write-gate.ps1`
- Bash / macOS / Linux：`bash .claude/hooks/impact-write-gate.sh`

## 状态与限制

- 一次性确认状态保存在 `~/.claude/impact-write-gate/`。
- 可以用 `IMPACT_WRITE_GATE_STATE_DIR=/path/to/state` 更改保存位置。
- 在 Claude Code 进程环境中设置 `IMPACT_WRITE_GATE_DISABLE=1` 可以临时关闭 Hook。
- 对 `Bash` 的判断基于常见命令特征，不是完整沙箱。数据库仍应使用只读账号，必要时还要配置 settings deny 规则。
- Hook 只保护带有 `.impact-protected` 的项目，不会自动覆盖其他工作区。

## 验证

在 Blue SkillHub 根目录运行：

```powershell
python -m unittest eval.real-projects.tests.test_impact_write_gate
```

测试会模拟 Claude Code 的 `PreToolUse` 事件，覆盖两类情况：没有最新的 `确认 Step N` 就尝试写入；虽然收到步骤确认，但 Phase 4 文档或执行前检查尚未完成就尝试修改源码。
