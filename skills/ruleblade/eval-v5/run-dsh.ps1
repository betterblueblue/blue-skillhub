<#
.SYNOPSIS
  用 dsh headless 批量跑律刃 v5 场景（DeepSeek 一侧）。

.DESCRIPTION
  每个变体用一个隔离的 DSH_HOME（目录名不含变体信息），规则文件放在该 home 的 AGENTS.md，
  对应你平时 ~/.dsh/AGENTS.md 的全局位置；你自己的 ~/.dsh/AGENTS.md 不会被读到，也不会被改动。
  沙盒放在中性路径下，每个沙盒是独立 git 仓库，dsh 的项目根发现会停在沙盒里。

.EXAMPLE
  .\run-dsh.ps1 -Scenarios S2 -Variants full -Reps 1          # 先跑一个冒烟
  .\run-dsh.ps1                                                # 默认：全部 dsh 场景 × none/v4/full × 3 次
  .\run-dsh.ps1 -Round 20261026-2100 -Resume                   # 中断后继续
#>
param(
    [string]$Round = (Get-Date -Format 'yyyyMMdd-HHmm'),
    [string[]]$Variants = @('none', 'v4', 'full'),
    [string[]]$Scenarios = @(),
    [int]$Reps = 3,
    [int]$TimeoutSec = 900,
    [string]$ResultsRoot = 'E:\agent\ruleblade-eval',
    # dsh 的 Windows shell 沙盒要给工作区加 ACL，在 E:\agent 下会报 SetNamedSecurityInfoW (Win32 5)，放在用户目录下正常
    [string]$SandboxRoot = (Join-Path $env:USERPROFILE 'rbw'),
    [string[]]$Patch = @(),
    [switch]$Resume
)

. (Join-Path $PSScriptRoot 'lib.ps1')

$cfg = Read-Scenarios
$selected = @($cfg.scenarios | Where-Object { $_.platforms -contains 'dsh' -and ($Scenarios.Count -eq 0 -or $Scenarios -contains $_.id) })
if ($selected.Count -eq 0) { throw '没有匹配的场景。' }
foreach ($v in $Variants) { [void](Get-RuleFile $v) }

$roundDir = Join-Path $ResultsRoot "$Round\dsh"
New-Item -ItemType Directory -Force $roundDir | Out-Null
$nodeExe = (Get-Command node -ErrorAction Stop).Source
$dshBin = Join-Path $env:APPDATA 'npm\node_modules\@deepseek-ai\dsh\lib\bin.js'
if (-not (Test-Path -LiteralPath $dshBin)) { throw "找不到 dsh 入口：$dshBin" }

# ---------- 隔离的 DSH_HOME ----------
$srcHome = Join-Path $env:USERPROFILE '.dsh'
$homesRoot = Join-Path $env:USERPROFILE '.dshx'
$agentsEmpty = Join-Path $homesRoot '_agents'
New-Item -ItemType Directory -Force $agentsEmpty | Out-Null
$allVariants = @($cfg.variants.PSObject.Properties.Name)

function Initialize-DshHome([string]$Variant) {
    $letter = [char](97 + [array]::IndexOf($allVariants, $Variant))
    $h = Join-Path $homesRoot $letter
    if (-not (Test-Path -LiteralPath $h)) {
        New-Item -ItemType Directory -Force $h | Out-Null
        foreach ($d in 'profiles', 'dsh-runtimes', 'cache', 'llm-deepseek', '.agent-presets', 'router-standard', 'super-injector') {
            $s = Join-Path $srcHome $d
            if (Test-Path -LiteralPath $s) { New-Item -ItemType Junction -Path (Join-Path $h $d) -Target $s | Out-Null }
        }
        # 密钥类文件用硬链接，脚本不读取内容
        foreach ($f in '.env', '.credentials.yaml', '.anonymous-user-id', 'settings.yaml.imported') {
            $s = Join-Path $srcHome $f
            if (Test-Path -LiteralPath $s) { New-Item -ItemType HardLink -Path (Join-Path $h $f) -Target $s | Out-Null }
        }
        foreach ($d in 'sessions', 'storages', 'attachments') { New-Item -ItemType Directory -Force (Join-Path $h $d) | Out-Null }
    }
    $agents = Join-Path $h 'AGENTS.md'
    $rule = Get-RuleFile $Variant
    if ($rule) { Copy-Item -LiteralPath $rule -Destination $agents -Force }
    elseif (Test-Path -LiteralPath $agents) { Remove-Item -LiteralPath $agents -Force }
    return $h
}

function Get-DefaultModel([string]$DshHome) {
    $old = $env:DSH_HOME
    try {
        $env:DSH_HOME = $DshHome
        $patchArgs = @(); foreach ($p in $Patch) { $patchArgs += @('--patch', $p) }
        $dump = & $nodeExe $dshBin --profile headless @patchArgs --dump-config 2>$null | Out-String
        $m = [regex]::Match($dump, 'id: agent-default-model[\s\S]*?model:\s*(\S+)')
        if ($m.Success) { return $m.Groups[1].Value } else { return 'unknown' }
    }
    finally { $env:DSH_HOME = $old }
}

function Invoke-DshTurn {
    param([string]$Cwd, [string]$Task, [string]$SessionId, [string]$DshHome, [string]$EventsPath, [string]$StderrPath)
    $psi = [System.Diagnostics.ProcessStartInfo]::new($nodeExe)
    $psi.ArgumentList.Add($dshBin)
    $psi.ArgumentList.Add('--profile'); $psi.ArgumentList.Add('headless')
    foreach ($p in $Patch) { $psi.ArgumentList.Add('--patch'); $psi.ArgumentList.Add($p) }
    $psi.ArgumentList.Add('--json')
    if ($SessionId) { $psi.ArgumentList.Add('--session-id'); $psi.ArgumentList.Add($SessionId) }
    $psi.ArgumentList.Add('-')
    $psi.WorkingDirectory = $Cwd
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = $Script:Utf8NoBom
    $psi.StandardErrorEncoding = $Script:Utf8NoBom
    $psi.Environment['DSH_HOME'] = $DshHome
    $psi.Environment['DSH_AGENTS_HOME'] = $agentsEmpty
    $proc = [System.Diagnostics.Process]::new()
    $proc.StartInfo = $psi
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    [void]$proc.Start()
    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()
    $writer = [System.IO.StreamWriter]::new($proc.StandardInput.BaseStream, $Script:Utf8NoBom)
    $writer.Write($Task)
    $writer.Close()
    $timedOut = -not $proc.WaitForExit($TimeoutSec * 1000)
    if ($timedOut) { try { $proc.Kill($true) } catch { }; $proc.WaitForExit() }
    $sw.Stop()
    Write-Utf8 $EventsPath $outTask.Result
    Write-Utf8 $StderrPath $errTask.Result
    return [pscustomobject]@{ ExitCode = $(if ($timedOut) { -1 } else { $proc.ExitCode }); TimedOut = $timedOut; Seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1) }
}

function Get-TurnStats([string]$EventsPath) {
    $s = [ordered]@{ session_id = $null; steps = 0; tool_calls = 0; input_tokens = 0; output_tokens = 0; cache_read_tokens = 0; end_reason = $null; final = '' }
    foreach ($line in [System.IO.File]::ReadAllLines($EventsPath, $Script:Utf8NoBom)) {
        if (-not $line.Trim()) { continue }
        try { $e = $line | ConvertFrom-Json } catch { continue }
        switch ($e.type) {
            'session' { $s.session_id = $e.sessionId }
            'tool_call' { $s.tool_calls++ }
            'final' { $s.final = [string]$e.text }
            'status' {
                if ($e.phase -eq 'step_end') {
                    $s.steps++
                    if ($e.usage) {
                        $s.input_tokens += [int64]$e.usage.inputTokens
                        $s.output_tokens += [int64]$e.usage.outputTokens
                        $s.cache_read_tokens += [int64]$e.usage.cacheReadTokens
                    }
                }
                elseif ($e.phase -eq 'turn_end') { $s.end_reason = $e.reason.kind }
            }
        }
    }
    return $s
}

# ---------- 计划：按 次数 → 场景 → 打乱的变体 交错执行 ----------
$plan = [System.Collections.Generic.List[object]]::new()
$rng = [System.Random]::new(20261026)
for ($r = 1; $r -le $Reps; $r++) {
    foreach ($sc in $selected) {
        foreach ($v in ($Variants | Sort-Object { $rng.Next() })) { $plan.Add([pscustomobject]@{ Scenario = $sc; Variant = $v; Rep = $r }) }
    }
}

$homes = @{}
foreach ($v in $Variants) { $homes[$v] = Initialize-DshHome $v }
$model = Get-DefaultModel $homes[$Variants[0]]
Write-Host "轮次：$Round   模型：$model   计划：$($plan.Count) 次运行"
Save-Json (Join-Path $roundDir "round-$($Variants -join '-').json") ([ordered]@{ round = $Round; platform = 'dsh'; model = $model; variants = $Variants; reps = $Reps; patch = $Patch; scenarios = @($selected.id); created = (Get-Date).ToString('s') })

$i = 0
foreach ($item in $plan) {
    $i++
    $sc = $item.Scenario; $v = $item.Variant; $r = $item.Rep
    $runDir = Join-Path $roundDir "$v\$($sc.id)\r$r"
    $metaPath = Join-Path $runDir 'meta.json'
    if ($Resume -and (Test-Path -LiteralPath $metaPath)) {
        $old = Get-Content -Raw -Encoding UTF8 $metaPath | ConvertFrom-Json
        if ($old.done) { continue }
    }
    if (Test-Path -LiteralPath $runDir) { Remove-Item -LiteralPath $runDir -Recurse -Force }
    New-Item -ItemType Directory -Force $runDir | Out-Null

    $hash = [System.BitConverter]::ToString([System.Security.Cryptography.SHA1]::HashData([System.Text.Encoding]::UTF8.GetBytes("$Round|$v|$($sc.id)|$r"))).Replace('-', '').Substring(0, 8).ToLower()
    $sandbox = Join-Path $SandboxRoot "$hash\$($sc.project)"
    $baseTree = New-Sandbox -Scenario $sc -SandboxDir $sandbox
    Write-Utf8 (Join-Path $runDir 'base.tree') $baseTree

    $meta = [ordered]@{ platform = 'dsh'; round = $Round; variant = $v; scenario = $sc.id; rep = $r; model = $model; sandbox = $sandbox; dsh_home = $homes[$v]; started = (Get-Date).ToString('s'); turns = @(); done = $false }
    Save-Json $metaPath $meta
    Write-Host ("[{0}/{1}] {2} {3} r{4} ..." -f $i, $plan.Count, $sc.id, $v, $r) -NoNewline

    $sessionId = $null
    $failed = $false
    for ($t = 1; $t -le $sc.turns.Count; $t++) {
        $task = [string]$sc.turns[$t - 1]
        Write-Utf8 (Join-Path $runDir "turn$t.prompt.txt") $task
        $ev = Join-Path $runDir "turn$t.events.jsonl"
        $res = Invoke-DshTurn -Cwd $sandbox -Task $task -SessionId $sessionId -DshHome $homes[$v] -EventsPath $ev -StderrPath (Join-Path $runDir "turn$t.stderr.txt")
        $stats = Get-TurnStats $ev
        Write-Utf8 (Join-Path $runDir "turn$t.reply.md") $stats.final
        [void](Save-TurnSnapshot -RunDir $runDir -Turn $t -SandboxDir $sandbox -BaseTree $baseTree)
        if (-not $sessionId) { $sessionId = $stats.session_id }
        $turnMeta = [ordered]@{ turn = $t; exit_code = $res.ExitCode; timed_out = $res.TimedOut; seconds = $res.Seconds }
        foreach ($k in $stats.Keys) { if ($k -ne 'final') { $turnMeta[$k] = $stats[$k] } }
        $meta.turns += $turnMeta
        Save-Json $metaPath $meta
        if ($res.ExitCode -ne 0 -or -not $sessionId) { $failed = $true; break }
    }
    $meta.done = -not $failed
    $meta.finished = (Get-Date).ToString('s')
    Save-Json $metaPath $meta
    $last = $meta.turns[-1]
    Write-Host (" {0}  {1}s  steps={2}" -f $(if ($failed) { "失败(exit=$($last.exit_code))" } else { 'ok' }), $last.seconds, $last.steps)
}

Write-Host "完成。结果目录：$roundDir"
Write-Host "下一步：python `"$PSScriptRoot\check.py`" score `"$(Join-Path $ResultsRoot $Round)`""
