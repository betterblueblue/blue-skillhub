param(
  [Parameter(Mandatory = $true)]
  [string]$RunResultPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $RunResultPath)) {
  throw "Run result file not found: $RunResultPath"
}

$result = Get-Content $RunResultPath -Raw | ConvertFrom-Json
$required = @(
  "run_id",
  "task_id",
  "project",
  "mode",
  "model",
  "agent_framework",
  "tool_group",
  "status"
)

$errors = @()
foreach ($field in $required) {
  if (-not ($result.PSObject.Properties.Name -contains $field)) {
    $errors += "Missing required field: $field"
  }
}

if ($result.mode -and ($result.mode -notin @("sanity", "analysis_only", "execution"))) {
  $errors += "Invalid mode: $($result.mode)"
}

$validStatuses = @(
  "completed",
  "timeout",
  "provider_error",
  "tool_error",
  "invalid_output",
  "policy_or_permission_block"
)
if ($result.status -and ($result.status -notin $validStatuses)) {
  $errors += "Invalid status: $($result.status)"
}

foreach ($field in @("p0_recall", "overall_recall")) {
  if ($result.PSObject.Properties.Name -contains $field -and $null -ne $result.$field) {
    $value = [double]$result.$field
    if ($value -lt 0 -or $value -gt 1) {
      $errors += "$field must be between 0 and 1"
    }
  }
}

if ($result.manual_scores) {
  foreach ($field in @("analysis_quality", "plan_correctness", "verification_coverage", "boundary_awareness", "hallucination_control")) {
    if ($result.manual_scores.PSObject.Properties.Name -contains $field -and $null -ne $result.manual_scores.$field) {
      $value = [int]$result.manual_scores.$field
      if ($value -lt 0 -or $value -gt 3) {
        $errors += "manual_scores.$field must be between 0 and 3"
      }
    }
  }
}

if ($errors.Count -gt 0) {
  [pscustomobject]@{
    valid = $false
    run_id = $result.run_id
    errors = $errors
  } | ConvertTo-Json -Depth 5
  exit 1
}

[pscustomobject]@{
  valid = $true
  run_id = $result.run_id
  task_id = $result.task_id
  model = $result.model
  status = $result.status
} | ConvertTo-Json -Depth 5
