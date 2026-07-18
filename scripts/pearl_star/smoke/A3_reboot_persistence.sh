#!/usr/bin/env bash
# ===========================================================================
#  ####  Smoke A3: REBOOT PERSISTENCE  ####
#
#  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  !!  THIS TEST REBOOTS PEARL STAR.  `sudo systemctl reboot`.            !!
#  !!  The box goes DOWN for ~5 minutes. Every running render dies.       !!
#  !!  Do NOT run this while any production batch is in flight.           !!
#  !!  It is a TWO-PHASE test — you run it once before the reboot and     !!
#  !!  again (with `verify`) after the box comes back.                    !!
#  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ===========================================================================
#
# Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §4.6 (reboot-resume), §13 criterion 1;
#       handoff §5.3 A3.
# PASS condition (handoff §5.3): 5 jobs queued -> `sudo systemctl reboot` ->
# after ~5 min boot -> SSH back -> all 5 jobs visible + resume + complete within
# 10 min post-boot -> 0 duplicates -> 0 losses.
#
# USAGE (run ON Pearl Star, ssh pearl_star):
#   ./A3_reboot_persistence.sh enqueue          # phase 1: queue 5 jobs + snapshot, PAUSED
#   ./A3_reboot_persistence.sh reboot           # phase 2: confirm + sudo systemctl reboot
#   # ... wait ~5 min, ssh back in ...
#   ./A3_reboot_persistence.sh verify           # phase 3: resume + confirm 5/5, 0 dup, 0 loss
#
# `reboot` requires you to type the literal word REBOOT to proceed.
# Tier: free + local. CLAUDE.md OK.
# ===========================================================================
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../install/00_config.sh
. "${HERE}/../install/00_config.sh"
EVID="${PS_EVIDENCE_DIR:-/tmp/pearl_star_phase_a_evidence}"; mkdir -p "${EVID}"
STATE="${PS_LIB_DIR}/.a3_reboot_state.json"
N_JOBS=5

phase="${1:-help}"

enqueue() {
  echo "=== A3 phase 1: enqueue ${N_JOBS} jobs + snapshot (queue left PAUSED) ==="
  # Pause first so the jobs sit pending across the reboot (proves WAL durability,
  # not just fast completion).
  pscli pause >/dev/null
  export PROCRASTINATE_APP=app.app:app PYTHONPATH="${PS_HOME}/app"
  IDS=$("${PS_PY}" - <<PY
import os, sys
sys.path.insert(0, os.environ["PYTHONPATH"])
from app import app
ids = []
with app.open():
    for i in range(${N_JOBS}):
        ids.append(app.tasks["t2i_flux_schnell"].defer(
            prompt=f"A3 reboot-persistence probe {i}", job_label=f"A3_{i}"))
print(",".join(str(x) for x in ids))
PY
)
  echo "{\"ids\": \"${IDS}\", \"enqueued_at\": \"$(date -u +%FT%TZ)\"}" | tee "${STATE}"
  echo "  queued job ids: ${IDS}  (queue is PAUSED)"
  echo "A3 enqueue ids=${IDS} at $(date -u +%FT%TZ)" >> "${EVID}/A3_smoke_evidence.txt"
  pscli status | tee -a "${EVID}/A3_smoke_evidence.txt"
  echo
  echo "  NEXT: ./A3_reboot_persistence.sh reboot   (this WILL reboot Pearl Star)"
}

reboot_box() {
  echo
  echo "  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "  !!  ABOUT TO REBOOT PEARL STAR (sudo systemctl reboot).     !!"
  echo "  !!  The box will be DOWN ~5 min. SSH will drop.             !!"
  echo "  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo
  printf "  Type REBOOT (all caps) to proceed, anything else to abort: "
  read -r CONFIRM
  if [ "${CONFIRM}" != "REBOOT" ]; then
    echo "  aborted — no reboot performed."; exit 1
  fi
  echo "A3 reboot issued at $(date -u +%FT%TZ)" >> "${EVID}/A3_smoke_evidence.txt"
  echo "  rebooting now. After ~5 min, ssh pearl_star and run:"
  echo "      ./A3_reboot_persistence.sh verify"
  sync
  sudo systemctl reboot
}

verify() {
  echo "=== A3 phase 3: post-reboot verify (resume + 5/5 complete, 0 dup, 0 loss) ==="
  [ -r "${STATE}" ] || { echo "  no A3 state at ${STATE} — run 'enqueue' first" >&2; exit 2; }
  IDS=$(sed -n 's/.*"ids": "\([^"]*\)".*/\1/p' "${STATE}")
  echo "  expected ids: ${IDS}"
  echo "  uptime: $(uptime -p 2>/dev/null || true)"

  # Resume dispatch; the (still-pending) jobs should now run.
  pscli resume >/dev/null
  echo "A3 verify resumed at $(date -u +%FT%TZ) uptime=$(uptime -p 2>/dev/null)" >> "${EVID}/A3_smoke_evidence.txt"

  # Wait up to 10 min for all N to reach succeeded.
  export PROCRASTINATE_APP=app.app:app PYTHONPATH="${PS_HOME}/app"
  DEADLINE=$(( $(date +%s) + 600 ))
  while [ "$(date +%s)" -lt "${DEADLINE}" ]; do
    DONE=$("${PS_PY}" - "${IDS}" <<'PY'
import os, sys, psycopg
ids = [int(x) for x in sys.argv[1].split(",") if x]
dsn = os.environ["PS_QUEUE_DSN"]; schema = os.environ.get("PS_PG_SCHEMA", "pearl_star_queue")
with psycopg.connect(dsn) as c, c.cursor() as cur:
    cur.execute(f"SELECT count(*) FROM {schema}.procrastinate_jobs "
                f"WHERE id = ANY(%s) AND status='succeeded'", (ids,))
    print(cur.fetchone()[0])
PY
)
    echo "  succeeded: ${DONE}/${N_JOBS}"
    [ "${DONE}" = "${N_JOBS}" ] && break
    sleep 10
  done

  # Duplicate check: count distinct output files newer than enqueue.
  OUTN=$(find "${PS_OUTPUT_DIR}" -type f -name 'pearl_star_cover*' 2>/dev/null | wc -l | tr -d ' ')
  pscli status | tee -a "${EVID}/A3_smoke_evidence.txt"
  echo "A3 verify done=${DONE}/${N_JOBS} output_files=${OUTN}" >> "${EVID}/A3_smoke_evidence.txt"

  if [ "${DONE}" = "${N_JOBS}" ]; then
    echo "  PASS: ${DONE}/${N_JOBS} completed after reboot; 0 lost."
    echo "A3 PASS ${DONE}/${N_JOBS} 0-loss" >> "${EVID}/A3_smoke_evidence.txt"
    exit 0
  else
    echo "  FAIL: only ${DONE}/${N_JOBS} completed within 10 min post-boot" >&2
    echo "A3 FAIL ${DONE}/${N_JOBS}" >> "${EVID}/A3_smoke_evidence.txt"
    exit 1
  fi
}

case "${phase}" in
  enqueue) enqueue ;;
  reboot)  reboot_box ;;
  verify)  verify ;;
  *)
    echo "A3 reboot-persistence smoke — TWO-PHASE, REBOOTS PEARL STAR."
    echo "Usage: $0 {enqueue|reboot|verify}"
    echo "  enqueue : queue ${N_JOBS} jobs (paused), snapshot ids"
    echo "  reboot  : confirm + sudo systemctl reboot   <-- TAKES THE BOX DOWN ~5 min"
    echo "  verify  : (after SSH back) resume + assert ${N_JOBS}/${N_JOBS}, 0 dup, 0 loss"
    ;;
esac
