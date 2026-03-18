$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path .\.venv)) {
  python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r .\requirements.txt

if (-not (Test-Path .\.env)) {
  Write-Host "Missing .env. Copy .env.template -> .env and fill values." -ForegroundColor Yellow
  exit 1
}

Write-Host "\nTry:" -ForegroundColor Cyan
Write-Host "  python gauss_quickcheck.py models" -ForegroundColor Cyan
Write-Host "  python gauss_quickcheck.py chat" -ForegroundColor Cyan
