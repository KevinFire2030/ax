$ErrorActionPreference = 'Stop'

if (-not (Test-Path .venv)) {
  python -m venv .venv
}

.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt

if (-not (Test-Path .env)) {
  Copy-Item .env.template .env
}

.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8070 --reload
