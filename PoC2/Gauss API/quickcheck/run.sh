#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv >/dev/null 2>&1 || true
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

if [[ ! -f .env ]]; then
  echo "Missing .env. Copy .env.template -> .env and fill values." >&2
  exit 1
fi

echo "Try:"
echo "  python gauss_quickcheck.py models"
echo "  python gauss_quickcheck.py chat"
