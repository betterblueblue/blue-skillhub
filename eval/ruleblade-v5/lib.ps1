# 律刃 v5 评测共用函数。由 run-dsh.ps1 / prepare-kiro.ps1 / collect-kiro.ps1 点源加载。
$ErrorActionPreference = 'Stop'

$Script:EvalDir = $PSScriptRoot
$Script:RuleDir = (Resolve-Path (Join-Path $PSScriptRoot '..\..\skills\ruleblade')).Path
$Script:Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Read-Scenarios {
    Get-Content -Raw -Encoding UTF8 (Join-Path $Script:EvalDir 'scenarios.json') | ConvertFrom-Json
}

function Get-RuleFile([string]$Variant) {
    $cfg = Read-Scenarios
    $prop = $cfg.variants.PSObject.Properties[$Variant]
    if (-not $prop) { throw "未知变体：$Variant（可选：$($cfg.variants.PSObject.Properties.Name -join ', ')）" }
    if ($null -eq $prop.Value) { return $null }
    $path = Join-Path $Script:RuleDir $prop.Value
    if (-not (Test-Path -LiteralPath $path)) { throw "规则文件不存在：$path" }
    return $path
}

function Write-Utf8([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, $Script:Utf8NoBom)
}

function Invoke-Git([string]$Repo, [string[]]$GitArgs) {
    $out = & git -C $Repo -c core.autocrlf=false -c core.safecrlf=false -c core.quotepath=false @GitArgs 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git $($GitArgs -join ' ') 失败：$out" }
    return $out
}

# 用 fixture 建一个独立 git 仓库。返回基线 tree hash。
function New-Sandbox {
    param(
        [Parameter(Mandatory)] $Scenario,
        [Parameter(Mandatory)] [string]$SandboxDir,
        [string]$SteeringRuleFile
    )
    $fixture = Join-Path $Script:EvalDir "fixtures\$($Scenario.fixture)"
    if (Test-Path -LiteralPath $SandboxDir) { Remove-Item -LiteralPath $SandboxDir -Recurse -Force }
    New-Item -ItemType Directory -Force $SandboxDir | Out-Null
    Copy-Item -Path (Join-Path $fixture 'base\*') -Destination $SandboxDir -Recurse -Force
    Get-ChildItem -LiteralPath (Join-Path $fixture 'base') -Force -Filter '.*' -File |
        ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $SandboxDir -Force }
    if ($SteeringRuleFile) {
        $steer = Join-Path $SandboxDir '.kiro\steering'
        New-Item -ItemType Directory -Force $steer | Out-Null
        Copy-Item -LiteralPath $SteeringRuleFile -Destination (Join-Path $steer 'ruleblade.md') -Force
    }
    Invoke-Git $SandboxDir @('init', '-q') | Out-Null
    Invoke-Git $SandboxDir @('config', 'core.autocrlf', 'false') | Out-Null
    Invoke-Git $SandboxDir @('add', '-A') | Out-Null
    Invoke-Git $SandboxDir @('-c', 'user.name=dev', '-c', 'user.email=dev@example.com', 'commit', '-q', '-m', 'init') | Out-Null
    $head = Join-Path $fixture 'head'
    if (Test-Path -LiteralPath $head) {
        Copy-Item -Path (Join-Path $head '*') -Destination $SandboxDir -Recurse -Force
        $msg = if ($Scenario.head_message) { $Scenario.head_message } else { 'update' }
        Invoke-Git $SandboxDir @('add', '-A') | Out-Null
        Invoke-Git $SandboxDir @('-c', 'user.name=dev', '-c', 'user.email=dev@example.com', 'commit', '-q', '-m', $msg) | Out-Null
    }
    return (Invoke-Git $SandboxDir @('rev-parse', 'HEAD^{tree}')).Trim()
}

# 把工作区当前状态（含未跟踪文件）写成 tree 对象，不改 HEAD 和工作区。
function Get-TreeSnapshot([string]$SandboxDir) {
    $tmpIndex = Join-Path ([System.IO.Path]::GetTempPath()) ("rb-index-" + [guid]::NewGuid().ToString('N'))
    $old = $env:GIT_INDEX_FILE
    try {
        $env:GIT_INDEX_FILE = $tmpIndex
        Invoke-Git $SandboxDir @('add', '-A', '--', '.', ':(exclude).kiro') | Out-Null
        $steer = Join-Path $SandboxDir '.kiro'
        if (Test-Path -LiteralPath $steer) { Invoke-Git $SandboxDir @('add', '-A', '-f', '--', '.kiro/steering') | Out-Null }
        return (Invoke-Git $SandboxDir @('write-tree')).Trim()
    }
    finally {
        $env:GIT_INDEX_FILE = $old
        Remove-Item -LiteralPath $tmpIndex -Force -ErrorAction SilentlyContinue
    }
}

function Save-TurnSnapshot {
    param([string]$RunDir, [int]$Turn, [string]$SandboxDir, [string]$BaseTree)
    $tree = Get-TreeSnapshot $SandboxDir
    Write-Utf8 (Join-Path $RunDir "turn$Turn.tree") $tree
    $diff = Invoke-Git $SandboxDir @('diff', '--no-color', '--find-renames', $BaseTree, $tree)
    Write-Utf8 (Join-Path $RunDir "turn$Turn.diff") (($diff | Out-String))
    return $tree
}

function Get-NeutralName([int]$Index, [string]$Prefix) {
    return ('{0}{1:d3}' -f $Prefix, $Index)
}

function Save-Json([string]$Path, $Object) {
    Write-Utf8 $Path ($Object | ConvertTo-Json -Depth 10)
}
