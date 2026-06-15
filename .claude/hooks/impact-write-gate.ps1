$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "impact-write-gate.py"
$stdin = [Console]::In.ReadToEnd()

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
  $stdin | & $python.Source $scriptPath
  exit $LASTEXITCODE
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  $stdin | & $py.Source -3 $scriptPath
  exit $LASTEXITCODE
}

Write-Error "python or py was not found; cannot run impact-write-gate"
exit 2
