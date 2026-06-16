# 跨平台执行说明

> 适用范围：bash / Git-Bash / PowerShell / Windows cmd。SKILL.md 正文默认用跨平台友好的写法，平台差异细节集中在此。

## 时间戳命令

执行记录的 `## [YYYY-MM-DD HH:MM:SS] Step N: ...` 时间戳必须来自真实系统命令输出，**不得由模型自行编写**：

| 环境 | 命令 |
|------|------|
| bash / Git-Bash (Linux/macOS) | `date "+%Y-%m-%d %H:%M:%S"` |
| PowerShell (Windows) | `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` |
| Windows cmd | `echo %date% %time%`（格式不可控，**不推荐**） |

跨平台脚本场景：用环境探测分支，或要求用户在 `~/.bashrc` / PowerShell profile 中预置 `now()` 函数。

## 路径分隔符

**所有文档、命令、模板中的路径统一使用正斜杠 `/`**（Anthropic 官方明确要求）：

- ✅ `references/phase-5-execution.md`
- ❌ `references\phase-5-execution.md`

无论操作系统都按 `/` 写，工具层（Read/Write/Bash）会按运行平台正确解析。

## shell 元字符

模板和示例中的命令默认用 bash 风格。PowerShell 用户需自行转换：

| bash | PowerShell |
|------|------------|
| `2>/dev/null` | `2>$null` |
| `$(command)` | `$(command)`（同义） |
| `export FOO=bar` | `$env:FOO = "bar"` |
| `grep -rn "x" .` | `Get-ChildItem -Recurse \| Select-String "x"` |
| `head -n 5` | `Get-Content -TotalCount 5` |
| `wc -l` | `(Get-Content file \| Measure-Object -Line).Lines` |
| `mkdir -p` | `New-Item -ItemType Directory -Force` |
| `rm -rf` | `Remove-Item -Recurse -Force` |
| `~` (home) | `$env:USERPROFILE` |
| 反引号 `` ` `` 命令替换 | `$(...)`（PowerShell 不支持反引号） |

**SKILL.md 内的所有命令示例**默认假设用户有 bash/Git-Bash 可用；纯 Windows 用户看到时知道需自行转换。

## 行尾符

仓库文件统一 LF。Windows 用户的 Git 客户端默认 `core.autocrlf=true` 会把 LF 改为 CRLF，可能导致：
- shell 脚本第一行 `#!/bin/bash` 因 `\r` 报错
- grep / awk 在 CRLF 文件上行为差异

建议在仓库根目录设置 `.gitattributes`：

```
* text=auto eol=lf
```

## 工具假设

模板中的命令基于以下假设，用户环境不满足时**必须先调整命令再执行**，不得直接套用：

- **Maven 项目**：`./mvnw`（推荐）或 `mvn`
- **Gradle 项目**：`./gradlew`（推荐）或 `gradle`
- **Node 项目**：`npm` / `pnpm` / `yarn`（按 lockfile 选）
- **Go 项目**：`go`（模块模式默认开启）
- **Python 项目**：`python`（Windows 上常是 `python` 而非 `python3`）

找不到 `pom.xml`/`package.json`/`go.mod` 等真实入口时，**不得写"mvn test""npm test"等占位命令**，写"V2/V3 不可用/需补证据"。

## 维护注意

- 跨平台差异是**易变**信息，新平台/新工具出现时及时补一行。
- 不下沉到 references 的平台差异（如 `Read` / `Write` 工具本身）由 Claude Code 平台处理，不在此文档。
