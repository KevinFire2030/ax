$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (Test-Path .\requirements.txt) {
  python -m pip install -r .\requirements.txt | Out-Null
}

if (!(Test-Path .\.env)) {
  if (Test-Path .\create_env.ps1) {
    Write-Host "Missing .env. Running create_env.ps1..." -ForegroundColor Yellow
    .\create_env.ps1
    exit 1
  }
  if (Test-Path .\.env.template) {
    Copy-Item .\.env.template .\.env
    Write-Host "Created .env from .env.template. Please edit .env and set OPENAI_API_KEY." -ForegroundColor Yellow
    notepad .\.env
    Write-Host "After saving .env, run this script again." -ForegroundColor Yellow
    exit 1
  }
  Write-Host "Missing .env and .env.template" -ForegroundColor Red
  exit 1
}

if (-not $env:PORT) { $env:PORT = "8030" }
python .\internal_ui_server.py
