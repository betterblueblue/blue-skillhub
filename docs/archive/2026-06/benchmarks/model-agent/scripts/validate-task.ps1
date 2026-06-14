param(
  [Parameter(Mandatory = $true)]
  [string]$TaskPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $TaskPath)) {
  throw "Task file not found: $TaskPath"
}

$task = Get-Content $TaskPath -Raw | ConvertFrom-Json

$required = @(
  "id",
  "project",
  "project_root",
  "mode",
  "task_type",
  "prompt",
  "expected_files",
  "must_notice",
  "forbidden_claims",
  "allowed_tools",
  "disallowed_actions"
)

$errors = @()
foreach ($field in $required) {
  if (-not ($task.PSObject.Properties.Name -contains $field)) {
    $errors += "Missing required field: $field"
  }
}

if ($task.id -and ($task.id -notmatch "^[a-z0-9][a-z0-9-]*$")) {
  $errors += "Invalid id format: $($task.id)"
}

if ($task.mode -and ($task.mode -notin @("sanity", "analysis_only", "execution"))) {
  $errors += "Invalid mode: $($task.mode)"
}

$expected = @($task.expected_files)
if ($expected.Count -eq 0) {
  $errors += "expected_files must not be empty"
}

foreach ($item in $expected) {
  foreach ($field in @("path", "tier", "reason")) {
    if (-not ($item.PSObject.Properties.Name -contains $field)) {
      $errors += "Expected file entry missing $field"
    }
  }
  if ($item.tier -and ($item.tier -notin @("P0", "P1", "P2"))) {
    $errors += "Invalid tier for $($item.path): $($item.tier)"
  }
}

if ($errors.Count -gt 0) {
  [pscustomobject]@{
    valid = $false
    task_id = $task.id
    errors = $errors
  } | ConvertTo-Json -Depth 5
  exit 1
}

[pscustomobject]@{
  valid = $true
  task_id = $task.id
  expected_count = $expected.Count
  p0_count = @($expected | Where-Object { $_.tier -eq "P0" }).Count
} | ConvertTo-Json -Depth 5
