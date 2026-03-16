param(
  [int]$Port = 8010
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path .\.venv)) {
  python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "\n[WEB] http://127.0.0.1:$Port" -ForegroundColor Green
python -m uvicorn web_app:app --host 127.0.0.1 --port $Port
