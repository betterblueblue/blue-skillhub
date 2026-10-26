<#
.SYNOPSIS
  在 Kiro 里手动跑律刃 v5 场景（Opus 5.5 一侧）的准备和收集脚本。

.DESCRIPTION
  -Prepare  生成沙盒（规则放在 .kiro/steering/ruleblade.md）和执行清单。
  （不带开关）打开下一个待跑的沙盒，并把这一轮的提示词复制到剪贴板。
  -Collect  你在 Kiro 里复制助手的最终回复后运行：保存回复、记录改动；
            有下一轮就把下一轮提示词放进剪贴板，没有就标记完成。
  -Status   查看进度。

.EXAMPLE
  .\kiro-run.ps1 -Prepare -Round k1026                 # 默认 v4 和 lite 两个变体，各 1 次
  .\kiro-run.ps1 -Round k1026                          # 打开下一个
  .\kiro-run.ps1 -Round k1026 -Collect                 # 复制回复后收集
#>
param(
    [Parameter(Mandatory)] [string]$Round,
    [switch]$Prepare,
    [switch]$Collect,
    [switch]$Status,
    [string[]]$Variants = @('v4', 'lite'),
    [string[]]$Scenarios = @(),
    [int]$Reps = 1,
    [string]$ResultsRoot = 'E:\agent\ruleblade-eval',
    [string]$SandboxRoot = (Join-Path $env:USERPROFILE 'rbw')
)

. (Join-Path $PSScriptRoot 'lib.ps1')

$roundDir = Join-Path $ResultsRoot "$Round\kiro"
$indexPath = Join-Path $roundDir 'runs.json'
$kiroCmd = Join-Path $env:LOCALAPPDATA 'Programs\Kiro\bin\kiro.cmd'

function Read-Index { Get-Content -Raw -Encoding UTF8 $indexPath | ConvertFrom-Json }
function Save-Index($idx) { Save-Json $indexPath $idx }

if ($Prepare) {
    if (Test-Path -LiteralPath $indexPath) { throw "轮次已存在：$indexPath" }
    $cfg = Read-Scenarios
    $selected = @($cfg.scenarios | Where-Object { $_.platforms -contains 'kiro' -and ($Scenarios.Count -eq 0 -or $Scenarios -contains $_.id) })
    if ($selected.Count -eq 0) { throw '没有匹配的场景。' }
    $items = foreach ($r in 1..$Reps) { foreach ($sc in $selected) { foreach ($v in $Variants) { [pscustomobject]@{ sc = $sc; v = $v; r = $r; rule = (Get-RuleFile $v) } } } }
    $rng = [System.Random]::new(1026)
    $items = @($items | Sort-Object { $rng.Next() })
    New-Item -ItemType Directory -Force $roundDir | Out-Null
    $runs = @()
    $n = 0
    foreach ($it in $items) {
        $n++
        $id = Get-NeutralName $n 'k'
        $runDir = Join-Path $roundDir "$($it.v)\$($it.sc.id)\r$($it.r)"
        New-Item -ItemType Directory -Force $runDir | Out-Null
        $sandbox = Join-Path $SandboxRoot "$Round-$id\$($it.sc.project)"
        $baseTree = New-Sandbox -Scenario $it.sc -SandboxDir $sandbox -SteeringRuleFile $it.rule
        Write-Utf8 (Join-Path $runDir 'base.tree') $baseTree
        for ($t = 1; $t -le $it.sc.turns.Count; $t++) { Write-Utf8 (Join-Path $runDir "turn$t.prompt.txt") ([string]$it.sc.turns[$t - 1]) }
        Save-Json (Join-Path $runDir 'meta.json') ([ordered]@{ platform = 'kiro'; round = $Round; variant = $it.v; scenario = $it.sc.id; rep = $it.r; model = 'claude-opus-5.5 (Kiro，手动选择)'; sandbox = $sandbox; id = $id; turns = @(); done = $false })
        $runs += [ordered]@{ id = $id; run_dir = $runDir; sandbox = $sandbox; scenario = $it.sc.id; turns = $it.sc.turns.Count; collected = 0; done = $false }
    }
    Save-Index ([ordered]@{ round = $Round; active = $null; runs = $runs })
    $lines = @("# Kiro 执行清单：$Round", '', '每个沙盒开一个新的 Kiro 窗口，模型选 Claude Opus 5.5，Autopilot，新建 Vibe 会话。', '', '| # | 编号 | 场景 | 轮数 | 沙盒 |', '|---|---|---|---|---|')
    $k = 0
    foreach ($run in $runs) { $k++; $lines += "| $k | $($run.id) | $($run.scenario) | $($run.turns) | ``$($run.sandbox)`` |" }
    $lines += @('', '## 每个沙盒的提示词', '', '照原文发送，不要补充说明。助手提问时不要回答，直接复制回复并 -Collect。')
    foreach ($run in $runs) {
        $lines += @('', "### $($run.id)（$($run.scenario)，$($run.turns) 轮）", '', "沙盒：``$($run.sandbox)``")
        for ($t = 1; $t -le $run.turns; $t++) {
            $p = Get-Content -Raw -Encoding UTF8 (Join-Path $run.run_dir "turn$t.prompt.txt")
            $label = if ($t -eq 1) { '第 1 轮' } else { "第 $t 轮（第 $($t - 1) 轮收集后，在同一个对话里发送）" }
            $lines += @('', "${label}：", '', '```text', $p.Trim(), '```')
        }
    }
    Write-Utf8 (Join-Path $roundDir 'CHECKLIST.md') ($lines -join "`n")
    Write-Host "已生成 $($runs.Count) 个沙盒。清单：$(Join-Path $roundDir 'CHECKLIST.md')"
    Write-Host "开始：.\kiro-run.ps1 -Round $Round"
    return
}

if (-not (Test-Path -LiteralPath $indexPath)) { throw "找不到轮次 $Round，先运行 -Prepare。" }
$idx = Read-Index

if ($Status) {
    $done = @($idx.runs | Where-Object done).Count
    Write-Host "进度：$done / $($idx.runs.Count)   当前：$($idx.active)"
    $idx.runs | Where-Object { -not $_.done } | Select-Object -First 5 | ForEach-Object { Write-Host "  待跑 $($_.id) $($_.scenario)（已收集 $($_.collected)/$($_.turns) 轮）" }
    return
}

if ($Collect) {
    if (-not $idx.active) { throw '当前没有进行中的沙盒。先不带开关运行一次。' }
    $run = $idx.runs | Where-Object { $_.id -eq $idx.active }
    $turn = [int]$run.collected + 1
    $reply = Get-Clipboard -Raw
    $prompt = Get-Content -Raw -Encoding UTF8 (Join-Path $run.run_dir "turn$turn.prompt.txt")
    if ([string]::IsNullOrWhiteSpace($reply)) { throw '剪贴板是空的。请在 Kiro 里点助手最终回复的复制按钮后再运行。' }
    if ($reply.Trim() -eq $prompt.Trim()) { throw '剪贴板里还是提示词，不是助手的回复。' }
    $baseTree = (Get-Content -Raw (Join-Path $run.run_dir 'base.tree')).Trim()
    Write-Utf8 (Join-Path $run.run_dir "turn$turn.reply.md") $reply
    [void](Save-TurnSnapshot -RunDir $run.run_dir -Turn $turn -SandboxDir $run.sandbox -BaseTree $baseTree)
    $metaPath = Join-Path $run.run_dir 'meta.json'
    $meta = Get-Content -Raw -Encoding UTF8 $metaPath | ConvertFrom-Json
    $meta.turns = @($meta.turns) + @([ordered]@{ turn = $turn; collected_at = (Get-Date).ToString('s') })
    $run.collected = $turn
    if ($turn -ge $run.turns) {
        $run.done = $true; $meta.done = $true; $idx.active = $null
        Save-Json $metaPath $meta; Save-Index $idx
        $left = @($idx.runs | Where-Object { -not $_.done }).Count
        Write-Host "$($run.id) 完成，剩余 $left 个。关掉这个 Kiro 窗口，再运行 .\kiro-run.ps1 -Round $Round 开下一个。"
    }
    else {
        Save-Json $metaPath $meta; Save-Index $idx
        $next = Get-Content -Raw -Encoding UTF8 (Join-Path $run.run_dir "turn$($turn + 1).prompt.txt")
        Set-Clipboard -Value $next
        Write-Host "已收集第 $turn 轮。第 $($turn + 1) 轮提示词已复制到剪贴板，在同一个对话里发送：$next"
    }
    return
}

# 打开下一个
if ($idx.active) {
    $run = $idx.runs | Where-Object { $_.id -eq $idx.active }
    Write-Host "$($run.id) 还没收集完（已收集 $($run.collected)/$($run.turns) 轮）。复制回复后运行 -Collect。"
    return
}
$run = $idx.runs | Where-Object { -not $_.done } | Select-Object -First 1
if (-not $run) { Write-Host "全部完成。下一步：python `"$PSScriptRoot\check.py`" score `"$(Join-Path $ResultsRoot $Round)`""; return }
$idx.active = $run.id
Save-Index $idx
$prompt = Get-Content -Raw -Encoding UTF8 (Join-Path $run.run_dir 'turn1.prompt.txt')
Set-Clipboard -Value $prompt
if (Test-Path -LiteralPath $kiroCmd) { Start-Process -FilePath $kiroCmd -ArgumentList @('--new-window', "`"$($run.sandbox)`"") -WindowStyle Hidden }
else { Write-Host "找不到 kiro.cmd，请手动在 Kiro 里打开：$($run.sandbox)" }
Write-Host "已打开 $($run.id)（$($run.turns) 轮）：$($run.sandbox)"
Write-Host "1. 新窗口里确认模型是 Claude Opus 5.5、Autopilot，新建对话"
Write-Host "2. 粘贴提示词发送（已在剪贴板）：$prompt"
Write-Host "3. 跑完后复制助手的最终回复（助手提问也不要回答），运行：.\kiro-run.ps1 -Round $Round -Collect"
