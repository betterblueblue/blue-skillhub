param(
    [string]$SourceRepo = "E:\agent\govshield",
    [string]$WorkRoot = "E:\agent\ruleblade-context-test",
    [string]$RuleFile = "E:\agent\blue-skillhub\claudecode行为规范\ruleblade\CLAUDE.md",
    [string]$RoundName = "",
    [string]$ModelLabel = "claude-m3"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RoundName)) {
    $RoundName = "task-a-stability-" + (Get-Date -Format "yyyy-MM-dd-HHmmss") + "-$ModelLabel"
}

$RoundDir = Join-Path $WorkRoot $RoundName
$ProjectDir = Join-Path $RoundDir "v32-stable\govshield"
$Phase1Task = Join-Path $RoundDir "phase1-analysis-task.md"
$Phase2Task = Join-Path $RoundDir "phase2-implementation-task.md"
$Phase1Output = Join-Path $RoundDir "v32-stable-phase1-output.txt"
$Phase2Output = Join-Path $RoundDir "v32-stable-phase2-output.txt"
$StatusAfterPhase1 = Join-Path $RoundDir "status-after-phase1.txt"
$StatusAfterPhase2 = Join-Path $RoundDir "status-after-phase2.txt"
$DiffStat = Join-Path $RoundDir "v32-stable-phase2.diffstat"
$DiffFile = Join-Path $RoundDir "v32-stable-phase2.diff"
$MavenOutput = Join-Path $RoundDir "maven-minimal-test-output.txt"
$MavenAllOutput = Join-Path $RoundDir "maven-all-test-output.txt"
$FrontendNodeOutput = Join-Path $RoundDir "frontend-node-test-output.txt"
$SurefireSummary = Join-Path $RoundDir "surefire-summary.txt"

if (Test-Path $RoundDir) {
    throw "Round directory already exists: $RoundDir"
}

New-Item -ItemType Directory -Force $RoundDir | Out-Null
New-Item -ItemType Directory -Force (Split-Path -Parent $ProjectDir) | Out-Null

git clone --local $SourceRepo $ProjectDir
Copy-Item -LiteralPath $RuleFile -Destination (Join-Path $ProjectDir "CLAUDE.md") -Force

$phase1Prompt = @'
# RuleBlade Task A Phase 1: Analysis Only

你正在隔离副本中工作，不要访问或修改 `E:\agent\govshield` 原始项目。

本阶段只做影响分析和覆盖表，**禁止修改任何文件**，不要执行写操作，不要提交 git commit。

## 产品变更

现在审查链路里，风险项可以被人工确认或撤销。产品希望把“风险统计”的口径改得更符合人工复核后的状态：

当某个风险项被人工撤销 `DISMISSED` 后，它仍然必须保留在风险详情和决策历史里，不能删除、不能丢审计留痕；但它不应该继续计入“有效风险统计”。

有效风险定义：

- `reviewDecision !== 'DISMISSED'`
- `CONFIRMED` 计入有效风险
- 未复核 `NULL/空` 计入有效风险
- `DISMISSED` 不计入有效风险

## 你需要输出

请基于真实代码搜索和阅读，输出一份影响分析。必须包含：

1. 当前审查链路地图：上传/审查生成/结果保存/结果查询/人工决策/首页近期审查/前端结果页/导出。
2. 字段和状态定义：`riskCount`、`highRiskCount`、`reviewDecision`、`CONFIRMED`、`DISMISSED`、未复核分别在哪里定义或使用。
3. 覆盖表：
   - 数据产生点
   - 状态/字段定义
   - 持久化位置
   - 对外接口
   - 前端展示
   - 导出/报表
   - 测试入口
   - 明确排除项
4. 你建议修改的文件和理由。
5. 你明确不建议修改的文件/模块和理由。
6. 验收标准：如何判断实现正确。
7. 最小测试策略：应该补哪些测试，应该运行什么命令。
8. 风险点：比如统计口径不一致、N+1 查询、误删撤销风险、只改前端或只改后端。

注意：只分析，不改代码。最后请汇报你执行了哪些搜索/阅读命令。
'@

$phase2Prompt = @'
# RuleBlade Task A Phase 2: Implement

你正在隔离副本中工作，不要访问或修改 `E:\agent\govshield` 原始项目；不要提交 git commit。

上一阶段你已经做过影响分析。本阶段请基于你的分析实现变更。

## 产品变更

当风险项被人工撤销 `DISMISSED` 后，它仍然必须保留在风险详情和决策历史里，不能删除、不能丢审计留痕；但它不应该继续计入“有效风险统计”。

有效风险定义：

- `reviewDecision !== 'DISMISSED'`
- `CONFIRMED` 计入有效风险
- 未复核 `NULL/空` 计入有效风险
- `DISMISSED` 不计入有效风险

## 产品确认

有效高/中/低风险数按原 `riskLevel` 字段分桶，但先排除 `reviewDecision === 'DISMISSED'` 的风险项。`CONFIRMED` 和 `NULL/空` 均计入。

## 实现要求

1. 审查结果详情接口、首页近期审查接口、前端结果页风险统计、导出 Markdown/JSON 中，风险数量和高风险数量应使用“有效风险”口径。
2. 如果同一结果里还有中/低风险统计，必须说明并保持口径一致，不能同一页面总数用有效口径、中低风险仍用原始口径。
3. 风险详情列表仍然展示已撤销风险，并继续展示人工处理状态与决策历史，不要把撤销风险从列表里过滤掉。
4. 不要修改规则审查、Agent 审查、风险生成、DDL/schema、接口地址、路由或无关页面。
5. 补充能覆盖有效风险口径的测试。
6. 运行能覆盖你改动的最小测试；如果完整测试无法运行，说明原因。

完成后请汇报：

- 修改了哪些文件
- `CONFIRMED`、`DISMISSED`、未复核三种状态的统计口径
- 如何保证撤销风险仍留痕且仍在详情列表可见
- 看过但排除的模块
- 执行了哪些验证命令及结果
- 如果验证失败，必须给出实际命令、退出码、首个错误和下一步修复判断
- `git diff --stat` 和关键 diff 摘要
'@

Set-Content -LiteralPath $Phase1Task -Value $phase1Prompt -Encoding UTF8
Set-Content -LiteralPath $Phase2Task -Value $phase2Prompt -Encoding UTF8

Push-Location $ProjectDir
try {
    Write-Host "Round directory: $RoundDir"
    Write-Host "Project directory: $ProjectDir"
    Write-Host "Running Phase 1..."

    & claude -p --permission-mode bypassPermissions $phase1Prompt *> $Phase1Output
    $phase1Exit = $LASTEXITCODE
    git status --short | Set-Content -LiteralPath $StatusAfterPhase1 -Encoding UTF8

    if ($phase1Exit -ne 0) {
        Write-Host "Phase 1 failed with exit code $phase1Exit. See: $Phase1Output"
        exit $phase1Exit
    }

    $unexpectedPhase1 = git status --short | Where-Object { $_ -ne " M CLAUDE.md" }
    if ($unexpectedPhase1) {
        Write-Host "Phase 1 wrote files unexpectedly. See: $StatusAfterPhase1"
        exit 20
    }

    Write-Host "Running Phase 2..."
    & claude -p --permission-mode bypassPermissions $phase2Prompt *> $Phase2Output
    $phase2Exit = $LASTEXITCODE
    git status --short | Set-Content -LiteralPath $StatusAfterPhase2 -Encoding UTF8
    git status --short --untracked-files=all | Set-Content -LiteralPath (Join-Path $RoundDir "status-after-phase2-all.txt") -Encoding UTF8
    git diff --stat | Set-Content -LiteralPath $DiffStat -Encoding UTF8
    git diff | Set-Content -LiteralPath $DiffFile -Encoding UTF8

    if ($phase2Exit -ne 0) {
        Write-Host "Phase 2 failed with exit code $phase2Exit. Diff was still captured."
        exit $phase2Exit
    }

    Write-Host "Running minimal Maven tests..."
    & mvn -pl govshield-test -am "-Dtest=ReviewServiceTest,ComplianceControllerTest" "-Dsurefire.failIfNoSpecifiedTests=false" test *> $MavenOutput
    $mavenExit = $LASTEXITCODE

    if ($mavenExit -ne 0) {
        Write-Host "Minimal Maven test failed with exit code $mavenExit. See: $MavenOutput"
        exit $mavenExit
    }

    Write-Host "Running all govshield-test Maven tests..."
    & mvn -pl govshield-test -am test *> $MavenAllOutput
    $mavenAllExit = $LASTEXITCODE

    if ($mavenAllExit -ne 0) {
        Write-Host "All govshield-test Maven tests failed with exit code $mavenAllExit. See: $MavenAllOutput"
        exit $mavenAllExit
    }

    $frontendDir = Join-Path $ProjectDir "govshield-frontend"
    if (Test-Path (Join-Path $frontendDir "src\utils")) {
        $frontendTests = Get-ChildItem -LiteralPath (Join-Path $frontendDir "src\utils") -Filter "*.test.js" -ErrorAction SilentlyContinue
        if ($frontendTests.Count -gt 0) {
            Push-Location $frontendDir
            try {
                Write-Host "Running frontend node tests..."
                & node --test "src/utils/*.test.js" *> $FrontendNodeOutput
                $frontendExit = $LASTEXITCODE
                if ($frontendExit -ne 0) {
                    Write-Host "Frontend node tests failed with exit code $frontendExit. See: $FrontendNodeOutput"
                    exit $frontendExit
                }
            }
            finally {
                Pop-Location
            }
        }
    }

    $reportDir = Join-Path $ProjectDir "govshield-test\target\surefire-reports"
    if (Test-Path $reportDir) {
        $files = Get-ChildItem -LiteralPath $reportDir -Filter "TEST-*.xml"
        $tests = 0
        $failures = 0
        $errors = 0
        $skipped = 0
        foreach ($file in $files) {
            [xml]$xml = Get-Content -LiteralPath $file.FullName
            $suite = $xml.testsuite
            $tests += [int]$suite.tests
            $failures += [int]$suite.failures
            $errors += [int]$suite.errors
            $skipped += [int]$suite.skipped
        }
        "files=$($files.Count) tests=$tests failures=$failures errors=$errors skipped=$skipped" |
            Set-Content -LiteralPath $SurefireSummary -Encoding UTF8
    }

    Write-Host "Task A stability run finished. Review artifacts in: $RoundDir"
}
finally {
    Pop-Location
}
