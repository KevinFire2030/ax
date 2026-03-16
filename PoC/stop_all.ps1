param(
  [string]$StateFile = ".poc_processes.json",
  [int[]]$Ports = @(7999,8000,8010,8020,8030)
)

$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$statePath = Join-Path $root $StateFile

function Kill-PidTree {
  param([int]$Pid)

  # Best-effort: kill children first (Windows)
  try {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$Pid" -ErrorAction SilentlyContinue
    foreach ($c in ($children | Where-Object { $_ -and $_.ProcessId })) {
      Kill-PidTree -Pid ([int]$c.ProcessId)
    }
  } catch {}

  try {
    $proc = Get-Process -Id $Pid -ErrorAction SilentlyContinue
    if ($proc) {
      Write-Host "  - Killing PID $Pid ($($proc.ProcessName))" -ForegroundColor Yellow
      Stop-Process -Id $Pid -Force -ErrorAction SilentlyContinue
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
      $pid = $parts[-1]
      if ($pid -match '^\d+$') { $pids += [int]$pid }
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
        Kill-PidTree -Pid ([int]$it.pid)
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

  foreach ($pid in $pids) {
    Kill-PidTree -Pid $pid
  }
}

Write-Host "[PoC] Done." -ForegroundColor Green
