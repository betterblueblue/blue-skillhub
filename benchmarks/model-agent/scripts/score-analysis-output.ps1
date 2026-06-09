param(
  [Parameter(Mandatory = $true)]
  [string]$TaskPath,

  [Parameter(Mandatory = $true)]
  [string]$OutputPath,

  [string]$RunId = "",
  [string]$Model = "unknown",
  [string]$AgentFramework = "unknown",
  [string]$ToolGroup = "normal-tools",
  [string]$Status = "completed",
  [double]$DurationSeconds = 0,
  [double]$CostUsd = 0,
  [int]$InputTokens = 0,
  [int]$OutputTokens = 0,
  [int]$ToolCalls = 0,
  [int]$ToolErrors = 0,
  [int]$SearchCalls = 0,
  [int]$FileReads = 0,
  [int]$AnalysisQuality = -1,
  [int]$PlanCorrectness = -1,
  [int]$VerificationCoverage = -1,
  [int]$BoundaryAwareness = -1,
  [int]$HallucinationControl = -1
)

$ErrorActionPreference = "Stop"

function Normalize-Text([string]$Text) {
  return ($Text -replace "\\", "/").ToLowerInvariant()
}

function Test-ExpectedHit([string]$NormalizedOutput, [string]$ExpectedPath) {
  $path = Normalize-Text $ExpectedPath
  if ($NormalizedOutput.Contains($path)) {
    return $true
  }

  $parts = @($path -split "/")
  if ($parts.Count -eq 0) {
    return $false
  }

  $leaf = $parts[-1]
  if (-not $NormalizedOutput.Contains($leaf)) {
    return $false
  }

  # Accept compressed mentions such as `prisma/.../link.prisma`
  # when both the first path segment and leaf filename appear.
  $root = $parts[0]
  if ($NormalizedOutput.Contains($root) -and $NormalizedOutput.Contains($leaf)) {
    return $true
  }

  return $false
}

if (-not (Test-Path $TaskPath)) {
  throw "Task file not found: $TaskPath"
}
if (-not (Test-Path $OutputPath)) {
  throw "Output file not found: $OutputPath"
}

$task = Get-Content $TaskPath -Raw | ConvertFrom-Json
$output = Normalize-Text (Get-Content $OutputPath -Raw)

if ([string]::IsNullOrWhiteSpace($RunId)) {
  $RunId = "{0}-{1}-{2}" -f (Get-Date -Format "yyyyMMdd-HHmmss"), $Model, $task.id
}

$expected = @($task.expected_files)
$p0 = @($expected | Where-Object { $_.tier -eq "P0" })

$hits = @()
$misses = @()
$p0Hits = @()
$p0Misses = @()
$boundaryHits = @{}
$boundaryMisses = @{}

foreach ($item in $expected) {
  $hit = Test-ExpectedHit $output $item.path
  $boundary = if ($item.boundary_type) { [string]$item.boundary_type } else { "unspecified" }

  if ($hit) {
    $hits += $item
    if ($item.tier -eq "P0") {
      $p0Hits += $item
    }
    if (-not $boundaryHits.ContainsKey($boundary)) {
      $boundaryHits[$boundary] = 0
    }
    $boundaryHits[$boundary] += 1
  } else {
    $misses += $item
    if ($item.tier -eq "P0") {
      $p0Misses += $item
    }
    if (-not $boundaryMisses.ContainsKey($boundary)) {
      $boundaryMisses[$boundary] = 0
    }
    $boundaryMisses[$boundary] += 1
  }
}

$p0Recall = if ($p0.Count -gt 0) { [math]::Round($p0Hits.Count / $p0.Count, 3) } else { $null }
$overallRecall = if ($expected.Count -gt 0) { [math]::Round($hits.Count / $expected.Count, 3) } else { $null }
$manualValues = @(
  $AnalysisQuality,
  $PlanCorrectness,
  $VerificationCoverage,
  $BoundaryAwareness,
  $HallucinationControl
)
$hasManualScores = @($manualValues | Where-Object { $_ -ge 0 }).Count -gt 0
$qualityTotal = if ($hasManualScores) {
  @($manualValues | ForEach-Object { if ($_ -ge 0) { $_ } else { 0 } } | Measure-Object -Sum).Sum
} else {
  $null
}

[pscustomobject]@{
  run_id = $RunId
  scored_at = (Get-Date).ToString("o")
  task_id = $task.id
  project = $task.project
  repo_url = $task.repo_url
  commit = $task.commit
  mode = $task.mode
  model = $Model
  agent_framework = $AgentFramework
  tool_group = $ToolGroup
  status = $Status
  p0_recall = $p0Recall
  overall_recall = $overallRecall
  expected_count = $expected.Count
  hit_count = $hits.Count
  p0_expected_count = $p0.Count
  p0_hit_count = $p0Hits.Count
  misses = @($misses | ForEach-Object {
    [pscustomobject]@{
      path = $_.path
      tier = $_.tier
      reason = $_.reason
      boundary_type = $_.boundary_type
    }
  })
  p0_misses = @($p0Misses | ForEach-Object {
    [pscustomobject]@{
      path = $_.path
      reason = $_.reason
      boundary_type = $_.boundary_type
    }
  })
  boundary_hits = $boundaryHits
  boundary_misses = $boundaryMisses
  manual_scores = [pscustomobject]@{
    analysis_quality = if ($AnalysisQuality -ge 0) { $AnalysisQuality } else { $null }
    plan_correctness = if ($PlanCorrectness -ge 0) { $PlanCorrectness } else { $null }
    verification_coverage = if ($VerificationCoverage -ge 0) { $VerificationCoverage } else { $null }
    boundary_awareness = if ($BoundaryAwareness -ge 0) { $BoundaryAwareness } else { $null }
    hallucination_control = if ($HallucinationControl -ge 0) { $HallucinationControl } else { $null }
  }
  quality_total = $qualityTotal
  duration_seconds = $DurationSeconds
  cost_usd = $CostUsd
  input_tokens = $InputTokens
  output_tokens = $OutputTokens
  tool_calls = $ToolCalls
  tool_errors = $ToolErrors
  search_calls = $SearchCalls
  file_reads = $FileReads
  output_path = $OutputPath
} | ConvertTo-Json -Depth 10
