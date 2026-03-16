param(
  [string]$StateFile = ".poc_processes.json",
  [int[]]$Ports = @(7999,8000,8010,8020,8030)
)

$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$statePath = Join-Path $root $StateFile

function Kill-PidTree {
  param([int]$ProcId)

  # Best-effort: kill children first (Windows)
  try {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcId" -ErrorAction SilentlyContinue
    foreach ($c in ($children | Where-Object { $_ -and $_.ProcessId })) {
      Kill-PidTree -ProcId ([int]$c.ProcessId)
    }
  } catch {}

  try {
    $proc = Get-Process -Id $ProcId -ErrorAction SilentlyContinue
    if ($proc) {
      Write-Host "  - Killing PID $ProcId ($($proc.ProcessName))" -ForegroundColor Yellow
      Stop-Process -Id $ProcId -Force -ErrorAction SilentlyContinue
    }
  } catch {}
}

function Get-PidsListeningOnPort {
  param([int]$Port)
  $lines = netstat -ano | Select-String -Pattern (":$Port\s")
  $pids = @()
  foreach ($ln in $lines) {
    $parts = ($ln.ToString() -split "\s+") | Where-Object { $_ -ne "" }
    if ($parts.Length -ge 5) {
      $procId = $parts[-1]
      if ($procId -match '^\d+$') { $pids += [int]$procId }
    }
  }
  $pids | Sort-Object -Unique
}

Write-Host "[PoC] Stopping demo servers..." -ForegroundColor Cyan

# 1) Prefer killing tracked processes (closes the spawned terminal windows too)
if (Test-Path -LiteralPath $statePath) {
  try {
    $items = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    Write-Host "[PoC] Using state file: $StateFile" -ForegroundColor DarkGray

    foreach ($it in $items) {
      if ($it.pid -and ($it.pid -as [int])) {
        Write-Host "- $($it.name)" -ForegroundColor Cyan
        Kill-PidTree -ProcId ([int]$it.pid)
      }
    }

    Remove-Item -LiteralPath $statePath -Force -ErrorAction SilentlyContinue
  } catch {
    Write-Host "[PoC] Warning: failed to read/parse state file. Fallback to port-based kill." -ForegroundColor Yellow
  }
} else {
  Write-Host "[PoC] No state file ($StateFile). Fallback to port-based kill." -ForegroundColor DarkGray
}

# 2) Fallback: kill by ports
Write-Host "[PoC] Fallback stop by ports: $($Ports -join ', ')" -ForegroundColor DarkGray
foreach ($p in $Ports) {
  $pids = Get-PidsListeningOnPort -Port $p
  if (-not $pids -or $pids.Count -eq 0) {
    continue
  }

  foreach ($procId in $pids) {
    Kill-PidTree -ProcId $procId
  }
}

Write-Host "[PoC] Done." -ForegroundColor Green
