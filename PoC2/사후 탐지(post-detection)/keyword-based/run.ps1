param(
  [Parameter(Mandatory=$true)][string]$InputXlsx,
  [string]$KeywordFile = ".\detection_keywords.md"
)

$ErrorActionPreference = "Stop"

# Move to script folder
Set-Location -LiteralPath $PSScriptRoot

# Install deps (best-effort)
if (Test-Path .\requirements.txt) {
  python -m pip install -r .\requirements.txt | Out-Null
}

# Run
python .\keyword-based_detection.py $InputXlsx $KeywordFile
