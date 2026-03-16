param(
  [int]$LandingPort = 7999
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Host "[PoC] Starting 4 demo servers..." -ForegroundColor Cyan

# 1) post-detection keyword-based (8000)
Start-Process powershell -WorkingDirectory "$root\사후 탐지(post-detection)\keyword-based" -ArgumentList @(
  "-NoExit",
  "-Command",
  ".\run_web.ps1"
)

# 2) post-detection context-based (8010)
Start-Process powershell -WorkingDirectory "$root\사후 탐지(post-detection)\context-based" -ArgumentList @(
  "-NoExit",
  "-Command",
  ".\run_web.ps1"
)

# 3) prevention external (8020)
Start-Process powershell -WorkingDirectory "$root\사전 차단(prevention)\external" -ArgumentList @(
  "-NoExit",
  "-Command",
  "$env:PORT='8020'; .\run_server.ps1"
)

# 4) prevention internal (8030)
Start-Process powershell -WorkingDirectory "$root\사전 차단(prevention)\internal" -ArgumentList @(
  "-NoExit",
  "-Command",
  "$env:PORT='8030'; .\run_server.ps1"
)

# Landing page server (simple static)
Start-Process powershell -WorkingDirectory "$root" -ArgumentList @(
  "-NoExit",
  "-Command",
  "python -m http.server $LandingPort"
)

Write-Host "[Landing] http://127.0.0.1:$LandingPort (serving PoC/index.html)" -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:$LandingPort/index.html" -ForegroundColor Green
