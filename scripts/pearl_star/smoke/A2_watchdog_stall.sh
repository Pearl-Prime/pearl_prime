#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Pearl Star Job Queue V1 — Smoke A2: watchdog stall detect + recover
#
# Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §13 criterion 2; §5.2; handoff §5.3 A2.
# PASS condition (handoff §5.3): inject FORCE_STALL=1 (`sleep 600`) -> watchdog
# logs STALL_WARN at 2x threshold -> SIGKILL at 3x -> queue requeues -> a
# second (real, non-stalled) attempt succeeds.
#
# Mechanics: the t2i worker honors env FORCE_STALL=1 by sleeping 600 s instead
# of dispatching (see worker/flux_schnell_worker.py). flux-schnell thresholds
# are warn=30 s / kill=60 s (spec §3.1), so the watchdog should WARN ~30 s and
# KILL ~60 s after the job starts. We then clear FORCE_STALL and confirm the
# retry produces a real output.
#
# Run ON Pearl Star, AFTER A1 passes. No sudo needed (uses systemctl --user? NO:
# it sets a drop-in env on the worker via `sudo systemctl edit` OR the operator
# exports FORCE_STALL in /etc/pearl-star/queue.env). This script uses the
# queue.env approach and asks for sudo ONLY to toggle that one env line.
# Tier: free + local. CLAUDE.md OK.
# ---------------------------------------------------------------------------
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../install/00_config.sh
. "${HERE}/../install/00_config.sh"
EVID="${PS_EVIDENCE_DIR:-/tmp/pearl_star_phase_a_evidence}"; mkdir -p "${EVID}"
ENVFILE=/etc/pearl-star/queue.env
WD_LOG="${PS_LOG_DIR}/watchdog.log"

echo "=== Smoke A2: watchdog stall detect + recover (warn 2x ~30s, kill 3x ~60s) ==="

# --- 1. turn on stall injection + restart worker ---------------------------
echo "  enabling FORCE_STALL=1 on the worker (sudo: one env line)"
sudo sed -i '/^FORCE_STALL=/d' "${ENVFILE}" 2>/dev/null || true
echo 'FORCE_STALL=1' | sudo tee -a "${ENVFILE}" >/dev/null
sudo systemctl restart procrastinate-worker
WATCH_START=$(date +%s)

# --- 2. enqueue a job that WILL stall --------------------------------------
export PROCRASTINATE_APP=app.app:app PYTHONPATH="${PS_HOME}/app"
JOB=$("${PS_PY}" - <<'PY'
import os, sys
sys.path.insert(0, os.environ["PYTHONPATH"])
from app import app
with app.open():
    print(app.tasks["t2i_flux_schnell"].defer(prompt="A2 stall probe", job_label="A2_stall"))
PY
)
echo "  enqueued stall job_id=${JOB} (will sleep 600s -> watchdog must kill it)"
echo "A2 stall job_id=${JOB} watch_start=$(date -u +%FT%TZ)" >> "${EVID}/A2_smoke_evidence.txt"

# --- 3. watch the watchdog log for STALL_WARN then STALL_KILL (<=100 s) -----
echo "  waiting for STALL_WARN (~30 s) then AUTO-KILL (~60 s) ..."
SAW_WARN=0; SAW_KILL=0; DEADLINE=$((WATCH_START + 120))
while [ "$(date +%s)" -lt "${DEADLINE}" ]; do
  if [ -f "${WD_LOG}" ]; then
    grep -q "STALL_WARN.*${JOB}" "${WD_LOG}" 2>/dev/null && SAW_WARN=1 || true
    grep -qE "AUTO-KILL.*reason=stall" "${WD_LOG}" 2>/dev/null && SAW_KILL=1 || true
  fi
  [ "${SAW_WARN}" = 1 ] && [ "${SAW_KILL}" = 1 ] && break
  sleep 3
done
echo "  STALL_WARN seen=${SAW_WARN}  AUTO-KILL seen=${SAW_KILL}"
{ echo "A2 STALL_WARN=${SAW_WARN} AUTO-KILL=${SAW_KILL}";
  echo "--- watchdog.log tail ---"; tail -20 "${WD_LOG}" 2>/dev/null; } >> "${EVID}/A2_smoke_evidence.txt"

# --- 4. clear injection so the RETRY runs for real -------------------------
echo "  clearing FORCE_STALL so the queue's retry produces a real output"
sudo sed -i '/^FORCE_STALL=/d' "${ENVFILE}"
sudo systemctl restart procrastinate-worker

# --- 5. confirm the retry completes (real output lands) --------------------
RETRY_START=$(date +%s); RETRY_DEADLINE=$((RETRY_START + 90)); LANDED=""
while [ "$(date +%s)" -lt "${RETRY_DEADLINE}" ]; do
  NEW=$(find "${PS_OUTPUT_DIR}" -type f -newermt "@${RETRY_START}" 2>/dev/null | head -1 || true)
  [ -n "${NEW}" ] && { LANDED="${NEW}"; break; }
  sleep 3
done
pscli status | tee -a "${EVID}/A2_smoke_evidence.txt"

if [ "${SAW_WARN}" = 1 ] && [ "${SAW_KILL}" = 1 ] && [ -n "${LANDED}" ]; then
  echo "  PASS: STALL_WARN + AUTO-KILL observed; retry produced ${LANDED}"
  echo "A2 PASS retry_output=${LANDED}" >> "${EVID}/A2_smoke_evidence.txt"
  exit 0
else
  echo "  FAIL: warn=${SAW_WARN} kill=${SAW_KILL} retry_output='${LANDED}'" >&2
  echo "A2 FAIL warn=${SAW_WARN} kill=${SAW_KILL} retry='${LANDED}'" >> "${EVID}/A2_smoke_evidence.txt"
  exit 1
fi
