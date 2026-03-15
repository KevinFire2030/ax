param(
  [Parameter(Mandatory=$true)][string]$InputXlsx = ".\sample_data_raw.xlsx",
  [string]$AgentUrl = "http://127.0.0.1:8000/check"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (Test-Path .\requirements.txt) {
  python -m pip install -r .\requirements.txt | Out-Null
}

$env:PYTHONIOENCODING="utf-8"
python .\cpcex_hook_simulator.py $InputXlsx $AgentUrl
