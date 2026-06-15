# impact write gate hook

Optional Claude Code `PreToolUse` hook for impact / impact-pro Phase 5.

It adds a settings-layer check before write tools run:

1. A project is protected only when its root contains `.impact-protected`.
2. `Write`, `Edit`, `MultiEdit`, `NotebookEdit`, and write-like `Bash` commands
   under that root require the latest real user message in the current transcript
   to start with `确认 Step N`.
3. The confirmation is consumed once per protected root. A second write requires
   another explicit `确认 Step N`.

## Enable

Merge `impact-write-gate.settings.example.json` into `.claude/settings.json` or
`.claude/settings.local.json`. The repository default settings are not modified
automatically.

Then place an empty `.impact-protected` file at the target project root you want
to guard.

## Cross-platform commands

The JSON example calls Python directly:

```json
"command": "python .claude/hooks/impact-write-gate.py"
```

If a wrapper is preferred:

- Windows PowerShell: `powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/impact-write-gate.ps1`
- Bash/macOS/Linux: `bash .claude/hooks/impact-write-gate.sh`

## State and limits

- One-time confirmation state is stored in `~/.claude/impact-write-gate/`.
- Override with `IMPACT_WRITE_GATE_STATE_DIR=/path/to/state`.
- Temporarily bypass with `IMPACT_WRITE_GATE_DISABLE=1` in the Claude Code
  process environment.
- The Bash check is heuristic. It catches common write-like commands, but it is
  not a sandbox. Keep DB read-only accounts and settings deny rules for hard
  boundaries.
