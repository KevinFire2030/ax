$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (Test-Path .\.env) {
  Write-Host ".env already exists." -ForegroundColor Yellow
  exit 0
}

if (!(Test-Path .\.env.template)) {
  Write-Host "Missing .env.template" -ForegroundColor Red
  exit 1
}

Copy-Item .\.env.template .\.env
Write-Host "Created .env from .env.template. Please set OPENAI_API_KEY." -ForegroundColor Yellow
notepad .\.env
