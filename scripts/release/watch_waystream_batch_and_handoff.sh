#!/usr/bin/env bash
# Poll batch_waystream_epubs until exit, then run finish_waystream_handoff.py.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
LOG="artifacts/waystream/logs/watch_handoff.log"
mkdir -p artifacts/waystream/logs
exec >>"$LOG" 2>&1
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] watch_waystream_batch_and_handoff start"

BATCH_PID="${1:-}"
if [[ -n "$BATCH_PID" ]]; then
  while kill -0 "$BATCH_PID" 2>/dev/null; do
    N="$(find artifacts/weekly_packages/way_stream_sanctuary -name '*.epub' 2>/dev/null | wc -l | tr -d ' ')"
    echo "[$(date -u +%H:%M:%SZ)] batch pid=$BATCH_PID epubs_on_disk=$N"
    sleep 120
  done
  echo "[$(date -u +%H:%M:%SZ)] batch pid=$BATCH_PID exited"
else
  echo "no batch pid — waiting for any batch_waystream_epubs.py to finish"
  while pgrep -f 'batch_waystream_epubs.py' >/dev/null 2>&1; do
    N="$(find artifacts/weekly_packages/way_stream_sanctuary -name '*.epub' 2>/dev/null | wc -l | tr -d ' ')"
    echo "[$(date -u +%H:%M:%SZ)] batch running epubs_on_disk=$N"
    sleep 120
  done
fi

eval "$(python3 scripts/ci/load_integration_env_from_keychain.py 2>/dev/null)" || true
export PYTHONPATH=.
python3 scripts/release/finish_waystream_handoff.py
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] watch_waystream_batch_and_handoff done"
