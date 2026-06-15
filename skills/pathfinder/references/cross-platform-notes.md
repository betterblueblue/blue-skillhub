<!-- version: 1.0, last_updated: 2026-06-15, skill_commit: <TODO> -->
# 跨平台执行说明(Pathfinder)

> 适用:bash / Git-Bash / PowerShell / Windows cmd。Pathfinder 全程只读,跨平台问题主要在「量体量」和「取时间戳/HEAD」两类命令。

## 时间戳 + git HEAD(信任契约头用)

地图信任契约头的 `生成时间` 和 `基于 commit` 必须来自真实系统命令,**不得由模型自行编写**:

| 环境 | 时间戳 | git HEAD |
|------|--------|----------|
| bash / Git-Bash | `date "+%Y-%m-%d %H:%M:%S"` | `git rev-parse --short HEAD` |
| PowerShell | `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` | `git rev-parse --short HEAD` |
| Windows cmd | `echo %date% %time%`(格式不可控,不推荐) | `git rev-parse --short HEAD` |

非 Git 项目:`基于 commit` 写"非 Git,无 commit 锚点,以扫描时间为准"。

## 体量测量命令(Phase 1)

| 指标 | bash | PowerShell |
|------|------|------------|
| 跟踪文件数 | `git ls-files \| wc -l` | `(git ls-files \| Measure-Object).Count` |
| 文件数(非 Git) | `find . -type f -not -path './.git/*' \| wc -l` | `(Get-ChildItem -Recurse -File).Count` |
| 顶层目录 | `ls -d */` | `Get-ChildItem -Directory` |

## 路径分隔符

所有文档、命令、地图内的路径统一用正斜杠 `/`(Anthropic 官方要求)。工具层(Read/Grep/Glob)按运行平台正确解析。

## shell 元字符对照(只列只读相关)

| bash | PowerShell |
|------|------------|
| `grep -rn "x" .` | `Get-ChildItem -Recurse \| Select-String "x"` |
| `head -n 20` | `Get-Content -TotalCount 20` |
| `wc -l` | `(Get-Content file \| Measure-Object -Line).Lines` |
| `cat` | `Get-Content` |
| `2>/dev/null` | `2>$null` |

> Pathfinder 优先用 Read/Grep/Glob 工具而非 shell 文本命令,以上仅供必须用 Bash 量体量/查 git 时参考。

## Git Bash (msys2) 路径格式陷阱

在 Windows Git Bash 中,`git rev-parse --show-toplevel` 返回 Windows 格式路径(如 `E:/agent/blue-skillhub`),而 `$(pwd)` 返回 Unix 格式(如 `/e/agent/blue-skillhub`)。两者字符串比较恒失败。**禁止**用字符串相等判断 Git 仓库归属。

**推荐方案**:先 `test -d "$(pwd)/.git"` 检测 `.git` 目录是否存在;确认独立仓库后用 `git -C "$(pwd)" rev-parse --show-toplevel` 获取根路径(信任契约头用),不依赖路径字符串比较。

## 维护注意

- 本文件与 impact 家族的 `cross-platform-notes.md` 共享约定;时间戳/路径规则保持一致。
- Pathfinder 不执行构建/测试命令,故不含构建工具差异表(那部分见 impact 同名文件)。
