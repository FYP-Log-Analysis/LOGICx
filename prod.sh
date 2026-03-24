#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v python >/dev/null 2>&1; then
  echo "Error: python is not available in PATH."
  exit 1
fi

if ! command -v streamlit >/dev/null 2>&1; then
  echo "Error: streamlit is not available in PATH. Install dependencies first."
  exit 1
fi

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then
    kill "$API_PID" 2>/dev/null || true
  fi
  if [[ -n "${DASH_PID:-}" ]]; then
    kill "$DASH_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting API on http://localhost:4000"
python -m uvicorn api.main:app --host 0.0.0.0 --port 4000 &
API_PID=$!

echo "Starting dashboard on http://localhost:8501"
streamlit run dashboard/main.py --server.port 8501 --server.address 0.0.0.0 &
DASH_PID=$!

echo "Services started. Press Ctrl+C to stop."
wait "$API_PID" "$DASH_PID"
