#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Pearl Star Job Queue V1 — Smoke A1: flux-schnell book-cover dispatch
#
# Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §13 criterion 5 (operator CLI);
#       handoff §5.3 A1.
# PASS condition (handoff §5.3): job dispatched via the queue -> ComfyUI
# executes -> an output file lands in /var/lib/pearl-star/output/ ->
# `pscli status` shows the job COMPLETED -> all within 60 s wall-clock.
#
# Run ON Pearl Star (ssh pearl_star), AFTER 01-04 + systemd units are live.
# Read-only on the repo; talks to the running queue. No sudo needed.
# Tier: free + local (Procrastinate enqueue + ComfyUI flux-schnell). CLAUDE.md OK.
# ---------------------------------------------------------------------------
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../install/00_config.sh
. "${HERE}/../install/00_config.sh"
EVID="${PS_EVIDENCE_DIR:-/tmp/pearl_star_phase_a_evidence}"; mkdir -p "${EVID}"

echo "=== Smoke A1: flux-schnell book-cover dispatch (pass = COMPLETED + output file < 60 s) ==="
START=$(date +%s)

# --- 1. enqueue one t2i_flux_schnell job via Procrastinate -----------------
export PROCRASTINATE_APP=app.app:app
export PYTHONPATH="${PS_HOME}/app"
ENQ_OUT=$("${PS_PY}" - <<'PY'
import os, sys
sys.path.insert(0, os.environ["PYTHONPATH"])
from app import app
with app.open():
    job_id = app.tasks["t2i_flux_schnell"].defer(
        prompt="serene mountain temple at dawn, soft light, book cover composition, no text",
        negative="lowres, blurry",
        job_label="A1_book_cover",
    )
print(job_id)
PY
)
echo "  enqueued job_id=${ENQ_OUT}"
echo "A1 enqueue job_id=${ENQ_OUT} at $(date -u +%FT%TZ)" >> "${EVID}/A1_smoke_evidence.txt"

# --- 2. wait for an output file to land (<= 60 s) --------------------------
DEADLINE=$((START + 60))
LANDED=""
while [ "$(date +%s)" -lt "${DEADLINE}" ]; do
  NEW=$(find "${PS_OUTPUT_DIR}" -type f -newermt "@${START}" 2>/dev/null | head -1 || true)
  if [ -n "${NEW}" ]; then LANDED="${NEW}"; break; fi
  sleep 2
done

# --- 3. confirm via pscli status -------------------------------------------
echo "  --- pscli status ---"
pscli status | tee -a "${EVID}/A1_smoke_evidence.txt"
ELAPSED=$(( $(date +%s) - START ))

if [ -n "${LANDED}" ]; then
  echo "  PASS: output landed -> ${LANDED} (in ${ELAPSED}s)"
  echo "A1 PASS output=${LANDED} elapsed=${ELAPSED}s" >> "${EVID}/A1_smoke_evidence.txt"
  ls -la "${LANDED}" | tee -a "${EVID}/A1_smoke_evidence.txt"
  exit 0
else
  echo "  FAIL: no output file in ${PS_OUTPUT_DIR} within 60 s (elapsed ${ELAPSED}s)" >&2
  echo "A1 FAIL no-output elapsed=${ELAPSED}s" >> "${EVID}/A1_smoke_evidence.txt"
  echo "  Debug: check ComfyUI reachable (${PS_COMFY_URL}/system_stats), worker log:" >&2
  echo "         journalctl -u procrastinate-worker -n 50" >&2
  exit 1
fi
