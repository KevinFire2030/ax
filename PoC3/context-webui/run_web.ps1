param(
  [string]$SampleXlsx = "",
  [int]$Port = 8000,
  [string]$Host = "0.0.0.0"
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path .\.venv)) {
  python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path .\.env)) {
  Write-Host "Missing .env. Copy .env.template -> .env and fill values." -ForegroundColor Yellow
  exit 1
}

if ($SampleXlsx -ne "") {
  # override SAMPLE_XLSX_PATH for this run
  $env:SAMPLE_XLSX_PATH = $SampleXlsx
}

Write-Host "[WEB] http://$Host:$Port" -ForegroundColor Green
python -m uvicorn web_app:app --host $Host --port $Port
