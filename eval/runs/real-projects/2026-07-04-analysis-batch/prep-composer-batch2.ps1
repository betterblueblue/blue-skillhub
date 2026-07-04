# Composer 2.5 Fast 补覆盖面批次一键准备（D2/D3/D4/D5/D6/D7/D10/D14/D18）
# 运行方式：在 PowerShell 里执行 .\prep-composer-batch2.ps1

$fixtures = "E:\agent\real-project-fixtures"

function Ensure-GitClone {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Destination)) {
        git clone --quiet $Source $Destination
        Write-Host "  创建干净 Git 副本: $Destination"
    } else {
        Write-Host "  已存在，保留: $Destination"
    }

    git -C $Destination status --short --branch --untracked-files=all
}

# 1. 清理所有 read-only-original fixture 的 change-impact
Write-Host "=== 清理 read-only fixture ===" -ForegroundColor Cyan
$cleanTargets = @(
    "$fixtures\java-ruoyi",
    "$fixtures\node-realworld-prisma",
    "$fixtures\python-fastapi-template",
    "$fixtures\frontend-react-dashboard",
    "$fixtures\monorepo-full-stack-starter"
)
foreach ($t in $cleanTargets) {
    $ci = Join-Path $t "change-impact"
    if (Test-Path $ci) {
        Remove-Item $ci -Recurse -Force
        Write-Host "  清理: $ci"
    }
}

# 2. D4 隔离副本（frontend-react-dashboard delivery 场景）
$d4Copy = "$fixtures\frontend-react-dashboard-d4-composer"
if (Test-Path $d4Copy) { Remove-Item $d4Copy -Recurse -Force }
Copy-Item "$fixtures\frontend-react-dashboard" $d4Copy -Recurse
$ci = Join-Path $d4Copy "change-impact"
if (Test-Path $ci) { Remove-Item $ci -Recurse -Force }
Write-Host "  创建 D4 副本: $d4Copy"

# 3. D5 隔离副本（python-fastapi-template delivery 场景）
$d5Copy = "$fixtures\python-fastapi-template-d5-composer"
if (Test-Path $d5Copy) { Remove-Item $d5Copy -Recurse -Force }
Copy-Item "$fixtures\python-fastapi-template" $d5Copy -Recurse
$ci = Join-Path $d5Copy "change-impact"
if (Test-Path $ci) { Remove-Item $ci -Recurse -Force }
Write-Host "  创建 D5 副本: $d5Copy"

# 4. D6 非 Git 子目录副本（monorepo apps/api only, no .git）
$d6Copy = "$fixtures\monorepo-api-subdir-d6-composer"
if (Test-Path $d6Copy) { Remove-Item $d6Copy -Recurse -Force }
New-Item -ItemType Directory -Path $d6Copy -Force | Out-Null
Copy-Item "$fixtures\monorepo-full-stack-starter\apps\api" "$d6Copy\api" -Recurse
# 确保没有 .git
$gitDir = Join-Path $d6Copy ".git"
if (Test-Path $gitDir) { Remove-Item $gitDir -Recurse -Force }
Write-Host "  创建 D6 非 Git 子目录副本: $d6Copy"

# 5. D14/D18 专用干净副本
# 这些场景必须用独立副本，不能复用原始 java-ruoyi / monorepo-full-stack-starter。
Ensure-GitClone "$fixtures\java-ruoyi" "$fixtures\java-ruoyi-d14-composer-20260704-223205"
Ensure-GitClone "$fixtures\monorepo-full-stack-starter" "$fixtures\monorepo-full-stack-starter-d18-composer-20260704-223205"

Write-Host ""
Write-Host "=== 全部就绪 ===" -ForegroundColor Green
Write-Host "按顺序在 Cursor Composer 2.5 Fast 里跑以下 9 个场景。"
Write-Host "每个场景：开新会话 -> 设工作目录 -> 贴 prompt -> 跑完 -> 开下一个"
Write-Host ""
Write-Host "场景清单见: eval/runs/real-projects/2026-07-04-analysis-batch/COMPOSER-CHECKLIST-2.md"
