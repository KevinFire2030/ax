#!/usr/bin/env bash
set -euo pipefail

# Stops processes started by start_all.sh (best-effort).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"

kill_if_pidfile() {
  local name="$1"
  local pidfile="$LOG_DIR/${name}.pid"
  if [[ -f "$pidfile" ]]; then
    local pid
    pid=$(cat "$pidfile" 2>/dev/null || true)
    if [[ -n "${pid:-}" ]]; then
      if kill -0 "$pid" 2>/dev/null; then
        echo "Killing $name (PID $pid)"
        kill "$pid" 2>/dev/null || true
        # give it a moment
        sleep 0.5
        kill -9 "$pid" 2>/dev/null || true
      else
        echo "$name: PID $pid not running (stale pidfile)"
      fi
    fi
    rm -f "$pidfile"
  else
    echo "$name: no pidfile"
  fi
}

echo "[PoC] Stopping servers (logs dir: $LOG_DIR)"

kill_if_pidfile landing
kill_if_pidfile post_keyword
kill_if_pidfile post_context
kill_if_pidfile pre_external
kill_if_pidfile pre_internal

echo "[PoC] Done"
