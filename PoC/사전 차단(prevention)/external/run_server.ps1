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
  Write-Host "Missing .env. Create it and set OPENAI_API_KEY." -ForegroundColor Yellow
  exit 1
}

python .\detection_agent_webhook.py
