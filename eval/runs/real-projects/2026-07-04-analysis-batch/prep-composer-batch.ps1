# Composer 2.5 Fast 分析题批次一键准备
# 运行方式：在 PowerShell 里执行 .\prep-composer-batch.ps1

$fixtures = "E:\agent\real-project-fixtures"

# 1. 清理所有 read-only-original fixture 的 change-impact
Write-Host "=== 清理 fixture ===" -ForegroundColor Cyan
$cleanTargets = @(
    "$fixtures\java-ruoyi",
    "$fixtures\node-realworld-prisma",
    "$fixtures\python-fastapi-template",
    "$fixtures\monorepo-full-stack-starter"
)
foreach ($t in $cleanTargets) {
    $ci = Join-Path $t "change-impact"
    if (Test-Path $ci) {
        Remove-Item $ci -Recurse -Force
        Write-Host "  清理: $ci"
    }
}

# 2. D9 隔离副本
$d9Copy = "$fixtures\monorepo-full-stack-starter-d9-composer"
if (Test-Path $d9Copy) { Remove-Item $d9Copy -Recurse -Force }
Copy-Item "$fixtures\monorepo-full-stack-starter" $d9Copy -Recurse
Write-Host "  创建 D9 副本: $d9Copy"

# 3. D12 隔离副本 + 删 .git
$d12Copy = "$fixtures\monorepo-full-stack-starter-d12-composer"
if (Test-Path $d12Copy) { Remove-Item $d12Copy -Recurse -Force }
Copy-Item "$fixtures\monorepo-full-stack-starter" $d12Copy -Recurse
Remove-Item "$d12Copy\.git" -Recurse -Force
Write-Host "  创建 D12 副本(无 .git): $d12Copy"

Write-Host ""
Write-Host "=== 全部就绪 ===" -ForegroundColor Green
Write-Host "按顺序在 Cursor Composer 2.5 Fast 里跑以下 8 个场景。"
Write-Host "每个场景：开新会话 -> 设工作目录 -> 贴 prompt -> 跑完 -> 开下一个"
Write-Host ""
Write-Host "场景清单见: eval/runs/real-projects/2026-07-04-analysis-batch/COMPOSER-CHECKLIST.md"
