#!/usr/bin/env bash
set -euo pipefail

# Best-effort starter for Linux/macOS.
# Starts 4 servers in background and a static landing page.

LANDING_PORT=${LANDING_PORT:-7999}
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"

ensure_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    echo "[PoC] ERROR: directory not found: $dir" >&2
    exit 1
  fi
}

start_uvicorn() {
  local dir="$1"; local app="$2"; local port="$3"; local name="$4"
  ensure_dir "$dir"
  (
    cd "$dir"
    python3 -m venv .venv >/dev/null 2>&1 || true
    # shellcheck disable=SC1091
    source .venv/bin/activate
    python -m pip install -r requirements.txt >/dev/null
    nohup python -m uvicorn "$app" --host 127.0.0.1 --port "$port" >"$LOG_DIR/${name}.log" 2>&1 &
    echo $! >"$LOG_DIR/${name}.pid"
  )
}

start_py() {
  local dir="$1"; local script="$2"; local port="$3"; local name="$4"
  ensure_dir "$dir"
  (
    cd "$dir"
    python3 -m venv .venv >/dev/null 2>&1 || true
    # shellcheck disable=SC1091
    source .venv/bin/activate
    python -m pip install -r requirements.txt >/dev/null
    PORT="$port" nohup python "$script" >"$LOG_DIR/${name}.log" 2>&1 &
    echo $! >"$LOG_DIR/${name}.pid"
  )
}

echo "[PoC] Starting servers... logs: $LOG_DIR"

# post-detection keyword-based
start_uvicorn "$ROOT_DIR/사후 탐지(post-detection)/keyword-based" "web_app:app" 8000 "post_keyword"

# post-detection context-based
start_uvicorn "$ROOT_DIR/사후 탐지(post-detection)/context-based" "web_app:app" 8010 "post_context"

# prevention external
start_py "$ROOT_DIR/사전 차단(prevention)/external" "detection_agent_webhook.py" 8020 "pre_external"

# prevention internal
start_py "$ROOT_DIR/사전 차단(prevention)/internal" "internal_ui_server.py" 8030 "pre_internal"

# landing
(
  cd "$ROOT_DIR"
  nohup python3 -m http.server "$LANDING_PORT" >"$LOG_DIR/landing.log" 2>&1 &
  echo $! >"$LOG_DIR/landing.pid"
)

echo "[Landing] http://127.0.0.1:${LANDING_PORT}/index.html"

echo "[PoC] PIDs:" 
for f in "$LOG_DIR"/*.pid; do
  [[ -f "$f" ]] || continue
  echo "- $(basename "$f" .pid): $(cat "$f")"
done

echo "[PoC] Logs: $LOG_DIR (tail -f <name>.log)"
