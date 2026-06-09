param(
  [Parameter(Mandatory = $true)]
  [string]$RunPath,

  [switch]$Json,
  [string]$OutPath = ""
)

$ErrorActionPreference = "Stop"

function Get-RecordFiles([string]$Path) {
  if (-not (Test-Path $Path)) {
    throw "Run path not found: $Path"
  }

  $item = Get-Item $Path
  if ($item.PSIsContainer) {
    return @(Get-ChildItem -Path $Path -Recurse -File -Filter "*.json")
  }

  return @($item)
}

function Get-NumberAverage($Values) {
  $numbers = @(
    $Values |
      Where-Object { $null -ne $_ -and -not ($_ -is [string] -and $_ -eq "") } |
      ForEach-Object { [double]$_ }
  )

  if ($numbers.Count -eq 0) {
    return $null
  }

  return [math]::Round((($numbers | Measure-Object -Average).Average), 3)
}

function Get-NumberSum($Values) {
  $numbers = @(
    $Values |
      Where-Object { $null -ne $_ -and -not ($_ -is [string] -and $_ -eq "") } |
      ForEach-Object { [double]$_ }
  )

  if ($numbers.Count -eq 0) {
    return 0
  }

  return [math]::Round((($numbers | Measure-Object -Sum).Sum), 6)
}

function Get-Rate([int]$Count, [int]$Total) {
  if ($Total -eq 0) {
    return 0
  }

  return [math]::Round($Count / $Total, 3)
}

function Get-Decision($Summary) {
  if ($Summary.run_count -eq 0) {
    return "hold"
  }

  if ($Summary.completed_rate -eq 0) {
    return "reject"
  }

  if ($Summary.provider_error_rate -ge 0.5 -or $Summary.timeout_rate -ge 0.5) {
    return "hold"
  }

  if ($null -ne $Summary.avg_p0_recall -and
      $Summary.avg_p0_recall -ge 0.85 -and
      ($null -eq $Summary.avg_quality_total -or $Summary.avg_quality_total -ge 12) -and
      $Summary.provider_error_rate -eq 0 -and
      $Summary.timeout_rate -eq 0) {
    return "enter"
  }

  if ($null -ne $Summary.avg_p0_recall -and $Summary.avg_p0_recall -lt 0.6) {
    return "reject"
  }

  return "hold"
}

function Format-Cell($Value) {
  if ($null -eq $Value) {
    return "-"
  }

  return [string]$Value
}

$records = @()
foreach ($file in Get-RecordFiles $RunPath) {
  $raw = Get-Content $file.FullName -Raw | ConvertFrom-Json

  # Skip task files or other JSON artifacts that are not run score records.
  if (-not ($raw.PSObject.Properties.Name -contains "run_id") -or
      -not ($raw.PSObject.Properties.Name -contains "model") -or
      -not ($raw.PSObject.Properties.Name -contains "status")) {
    continue
  }

  $records += $raw
}

$summaries = @()
$groups = $records | Group-Object {
  "{0}|{1}|{2}" -f $_.model, $_.agent_framework, $_.tool_group
}

foreach ($group in $groups) {
  $parts = $group.Name -split "\|", 3
  $items = @($group.Group)
  $runCount = $items.Count
  $completedCount = @($items | Where-Object { $_.status -eq "completed" }).Count
  $timeoutCount = @($items | Where-Object { $_.status -eq "timeout" }).Count
  $providerErrorCount = @($items | Where-Object { $_.status -eq "provider_error" }).Count
  $toolErrorRuns = @($items | Where-Object {
    $toolErrors = 0
    if ($_.PSObject.Properties.Name -contains "tool_errors" -and $null -ne $_.tool_errors) {
      $toolErrors = [int]$_.tool_errors
    }

    $_.status -eq "tool_error" -or $toolErrors -gt 0
  }).Count

  $summary = [pscustomobject]@{
    model = $parts[0]
    agent_framework = $parts[1]
    tool_group = $parts[2]
    run_count = $runCount
    completed_rate = Get-Rate $completedCount $runCount
    timeout_rate = Get-Rate $timeoutCount $runCount
    provider_error_rate = Get-Rate $providerErrorCount $runCount
    tool_error_run_rate = Get-Rate $toolErrorRuns $runCount
    avg_p0_recall = Get-NumberAverage ($items | ForEach-Object { $_.p0_recall })
    avg_overall_recall = Get-NumberAverage ($items | ForEach-Object { $_.overall_recall })
    avg_quality_total = Get-NumberAverage ($items | ForEach-Object { $_.quality_total })
    avg_duration_seconds = Get-NumberAverage ($items | ForEach-Object { $_.duration_seconds })
    total_cost_usd = Get-NumberSum ($items | ForEach-Object { $_.cost_usd })
    total_input_tokens = [int](Get-NumberSum ($items | ForEach-Object { $_.input_tokens }))
    total_output_tokens = [int](Get-NumberSum ($items | ForEach-Object { $_.output_tokens }))
  }

  $summary | Add-Member -NotePropertyName decision -NotePropertyValue (Get-Decision $summary)
  $summaries += $summary
}

if ($Json) {
  $content = $summaries | ConvertTo-Json -Depth 6
} else {
  $lines = @()
  $lines += "| Model | Agent | Tools | Runs | Completed | Avg P0 Recall | Avg Overall Recall | Avg Quality / 15 | Avg Time | Total Cost | Provider Errors | Tool Error Runs | Decision |"
  $lines += "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"
  foreach ($item in $summaries | Sort-Object model, tool_group) {
    $totalCost = "$" + ([math]::Round($item.total_cost_usd, 6))
    $lines += "| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8}s | {9} | {10} | {11} | {12} |" -f `
      (Format-Cell $item.model),
      (Format-Cell $item.agent_framework),
      (Format-Cell $item.tool_group),
      $item.run_count,
      $item.completed_rate,
      (Format-Cell $item.avg_p0_recall),
      (Format-Cell $item.avg_overall_recall),
      (Format-Cell $item.avg_quality_total),
      (Format-Cell $item.avg_duration_seconds),
      $totalCost,
      $item.provider_error_rate,
      $item.tool_error_run_rate,
      $item.decision
  }

  $content = $lines -join [Environment]::NewLine
}

if (-not [string]::IsNullOrWhiteSpace($OutPath)) {
  Set-Content -Path $OutPath -Value $content -Encoding UTF8
}

$content
