param(
  [Parameter(Mandatory=$true)][string]$InputXlsx
)

$ErrorActionPreference = "Stop"

# Move to script folder
Set-Location -LiteralPath $PSScriptRoot

# Install deps (best-effort)
if (Test-Path .\requirements.txt) {
  python -m pip install -r .\requirements.txt | Out-Null
}

# Create .env from template if missing
if (!(Test-Path .\.env)) {
  if (Test-Path .\.env.template) {
    Copy-Item .\.env.template .\.env
    Write-Host "Created .env from .env.template. Please edit .env and set OPENAI_API_KEY." -ForegroundColor Yellow
    notepad .\.env
    Write-Host "After saving .env, run this script again." -ForegroundColor Yellow
    exit 1
  } else {
    Write-Host "Missing .env and .env.template" -ForegroundColor Red
    exit 1
  }
}

# Run
python .\context-based_detection.py $InputXlsx
