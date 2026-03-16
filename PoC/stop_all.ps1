param(
  [int[]]$Ports = @(7999,8000,8010,8020,8030)
)

$ErrorActionPreference = 'Continue'

function Get-PidsListeningOnPort {
  param([int]$Port)
  $lines = netstat -ano | Select-String -Pattern (":$Port\s")
  $pids = @()
  foreach ($ln in $lines) {
    $parts = ($ln.ToString() -split "\s+") | Where-Object { $_ -ne "" }
    # netstat format: Proto LocalAddress ForeignAddress State PID
    if ($parts.Length -ge 5) {
      $pid = $parts[-1]
      if ($pid -match '^\d+$') { $pids += [int]$pid }
    }
  }
  $pids | Sort-Object -Unique
}

Write-Host "[PoC] Stopping servers by ports: $($Ports -join ', ')" -ForegroundColor Cyan

foreach ($p in $Ports) {
  $pids = Get-PidsListeningOnPort -Port $p
  if (-not $pids -or $pids.Count -eq 0) {
    Write-Host "- Port $p: no listener" -ForegroundColor DarkGray
    continue
  }

  foreach ($pid in $pids) {
    try {
      $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
      $name = if ($proc) { $proc.ProcessName } else { "<unknown>" }
      Write-Host "- Killing PID $pid ($name) on port $p" -ForegroundColor Yellow
      taskkill /PID $pid /F | Out-Null
    } catch {
      Write-Host "  ! Failed to kill PID $pid on port $p: $_" -ForegroundColor Red
    }
  }
}

Write-Host "[PoC] Done. (터미널 창은 남아있을 수 있어요. 필요하면 창만 닫아주세요.)" -ForegroundColor Green
