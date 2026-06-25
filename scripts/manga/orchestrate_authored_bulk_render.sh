#!/usr/bin/env bash
# Pearl Star: render all authored manga panel_prompts via queue.
# Run ON Pearl Star (nohup-friendly). Requires queue worker deploy first:
#   bash scripts/pearl_star/install/expose_queue_env_for_operator.sh
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${REPO_ROOT}"

REF="${BULK_GIT_REF:-origin/agent/manga-queue-health-fix-20260624}"
LOG_DIR="${REPO_ROOT}/artifacts/manga/bulk_logs"
mkdir -p "${LOG_DIR}"
LOG="${LOG_DIR}/authored_bulk_$(date -u +%Y%m%dT%H%M%SZ).log"

echo "=== authored bulk render @ ${REF} ===" | tee -a "${LOG}"
git fetch origin agent/manga-queue-health-fix-20260624 2>&1 | tee -a "${LOG}" || true
git checkout "${REF}" -- \
  scripts/manga/render_all_authored_panels.py \
  scripts/manga/queue_panel_renders.py \
  scripts/manga/pearl_star_t2i_enqueue.py \
  scripts/manga/defer_panel_job_cli.py \
  scripts/pearl_star/worker/flux_schnell_worker.py \
  scripts/pearl_star/worker/flux_dev_manga_worker.py \
  scripts/pearl_star/worker/app.py \
  2>&1 | tee -a "${LOG}" || git checkout FETCH_HEAD -- scripts/manga/render_all_authored_panels.py 2>&1 | tee -a "${LOG}"

if ! systemctl is-active --quiet procrastinate-worker; then
  echo "WARN: procrastinate-worker not active — run expose_queue_env_for_operator.sh" | tee -a "${LOG}"
fi

USE_QUEUE=1
if ! grep -q "stall_warn_at_s=STALL_WARN_S" /opt/pearl-star/app/flux_dev_manga_worker.py 2>/dev/null; then
  echo "WARN: deployed worker missing manga stall thresholds — using direct ComfyUI (run expose_queue_env_for_operator.sh for queue mode)" | tee -a "${LOG}"
  USE_QUEUE=0
fi

set -a
# shellcheck disable=SC1091
. "${REPO_ROOT}/.pearl_star_queue.env"
set +a

python3 scripts/manga/render_all_authored_panels.py --report-only 2>&1 | tee -a "${LOG}"

echo "=== starting render (queue=${USE_QUEUE}) ===" | tee -a "${LOG}"
if [ "${USE_QUEUE}" = "1" ]; then
  python3 scripts/manga/render_all_authored_panels.py --via-queue 2>&1 | tee -a "${LOG}"
else
  python3 scripts/manga/render_all_authored_panels.py 2>&1 | tee -a "${LOG}"
fi
echo "=== done ===" | tee -a "${LOG}"
