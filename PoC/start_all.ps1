param(
  [int]$LandingPort = 7999
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

function Find-DirByTag {
  param(
    [Parameter(Mandatory=$true)][string]$Parent,
    [Parameter(Mandatory=$true)][string]$Tag
  )
  $d = Get-ChildItem -LiteralPath $Parent -Directory | Where-Object { $_.Name -like "*$Tag*" } | Select-Object -First 1
  if (-not $d) {
    throw "Cannot find directory under '$Parent' with tag '$Tag'"
  }
  return $d.FullName
}

$postDir = Find-DirByTag -Parent $root -Tag '(post-detection)'
$prevDir = Find-DirByTag -Parent $root -Tag '(prevention)'

$keywordDir = Join-Path $postDir 'keyword-based'
$contextDir = Join-Path $postDir 'context-based'
$externalDir = Join-Path $prevDir 'external'
$internalDir = Join-Path $prevDir 'internal'

Write-Host "[PoC] Starting 4 demo servers..." -ForegroundColor Cyan

# 1) post-detection keyword-based (8000)
Start-Process powershell -WorkingDirectory $keywordDir -ArgumentList @(
  "-NoExit",
  "-Command",
  ".\\run_web.ps1"
)

# 2) post-detection context-based (8010)
Start-Process powershell -WorkingDirectory $contextDir -ArgumentList @(
  "-NoExit",
  "-Command",
  ".\\run_web.ps1"
)

# 3) prevention external (8020)
Start-Process powershell -WorkingDirectory $externalDir -ArgumentList @(
  "-NoExit",
  "-Command",
  "$env:PORT='8020'; .\\run_server.ps1"
)

# 4) prevention internal (8030)
Start-Process powershell -WorkingDirectory $internalDir -ArgumentList @(
  "-NoExit",
  "-Command",
  "$env:PORT='8030'; .\\run_server.ps1"
)

# Landing page server (simple static)
Start-Process powershell -WorkingDirectory $root -ArgumentList @(
  "-NoExit",
  "-Command",
  "python -m http.server $LandingPort"
)

Write-Host "[Landing] http://127.0.0.1:$LandingPort/index.html" -ForegroundColor Green
