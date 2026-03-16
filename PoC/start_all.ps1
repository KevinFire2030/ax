param(
  [int]$LandingPort = 7999,
  [string]$StateFile = ".poc_processes.json"
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

function Find-DirByTag {
  param(
    [Parameter(Mandatory=$true)][string]$Parent,
    [Parameter(Mandatory=$true)][string]$Tag
  )
  $d = Get-ChildItem -LiteralPath $Parent -Directory | Where-Object { $_.Name -like "*$Tag*" } | Select-Object -First 1
  if (-not $d) { throw "Cannot find directory under '$Parent' with tag '$Tag'" }
  return $d.FullName
}

$postDir = Find-DirByTag -Parent $root -Tag '(post-detection)'
$prevDir = Find-DirByTag -Parent $root -Tag '(prevention)'

$keywordDir = Join-Path $postDir 'keyword-based'
$contextDir = Join-Path $postDir 'context-based'
$externalDir = Join-Path $prevDir 'external'
$internalDir = Join-Path $prevDir 'internal'

Write-Host "[PoC] Starting 4 demo servers..." -ForegroundColor Cyan

$procs = @()

function Start-PoCProcess {
  param(
    [Parameter(Mandatory=$true)][string]$Name,
    [Parameter(Mandatory=$true)][string]$WorkingDirectory,
    [Parameter(Mandatory=$true)][string]$Command
  )
  $p = Start-Process powershell.exe -WorkingDirectory $WorkingDirectory -ArgumentList @(
    "-NoExit",
    "-Command",
    $Command
  ) -PassThru

  $procs += [pscustomobject]@{
    name = $Name
    pid = $p.Id
    startedAt = (Get-Date).ToString("s")
    cwd = $WorkingDirectory
    command = $Command
  }
}

# 1) post-detection keyword-based (8000)
Start-PoCProcess -Name "post_keyword" -WorkingDirectory $keywordDir -Command ".\\run_web.ps1"

# 2) post-detection context-based (8010)
Start-PoCProcess -Name "post_context" -WorkingDirectory $contextDir -Command ".\\run_web.ps1"

# 3) prevention external (8020)
Start-PoCProcess -Name "pre_external" -WorkingDirectory $externalDir -Command "`$env:PORT='8020'; .\\run_server.ps1"

# 4) prevention internal (8030)
Start-PoCProcess -Name "pre_internal" -WorkingDirectory $internalDir -Command "`$env:PORT='8030'; .\\run_server.ps1"

# Landing page server (simple static)
Start-PoCProcess -Name "landing" -WorkingDirectory $root -Command "python -m http.server $LandingPort"

# Persist state for stop_all.ps1
try {
  $json = $procs | ConvertTo-Json -Depth 4
  Set-Content -LiteralPath (Join-Path $root $StateFile) -Value $json -Encoding UTF8
} catch {
  Write-Host "[PoC] Warning: failed to write state file: $StateFile" -ForegroundColor Yellow
}

Write-Host "[Landing] http://127.0.0.1:$LandingPort/index.html" -ForegroundColor Green
Write-Host "[PoC] State: $StateFile" -ForegroundColor DarkGray
