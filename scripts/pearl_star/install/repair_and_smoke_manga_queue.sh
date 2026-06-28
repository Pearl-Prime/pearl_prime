#!/usr/bin/env bash
# Pearl Star: repair queue.env + deploy workers + one-panel manga queue smoke.
# Run ON Pearl Star with interactive sudo:
#   ssh -t pearl_star 'cd ~/phoenix_omega && bash scripts/pearl_star/install/repair_and_smoke_manga_queue.sh'
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

REF="${SMOKE_GIT_REF:-origin/agent/manga-queue-health-fix-20260624}"
echo "=== sparse checkout queue-fix files @ ${REF} ==="
git fetch origin agent/manga-queue-health-fix-20260624 2>/dev/null || true
for p in \
  scripts/manga/queue_panel_renders.py \
  scripts/manga/pearl_star_t2i_enqueue.py \
  scripts/manga/defer_panel_job_cli.py \
  scripts/pearl_star/worker/app.py \
  scripts/pearl_star/worker/flux_schnell_worker.py \
  scripts/pearl_star/worker/flux_dev_manga_worker.py \
  scripts/pearl_star/worker/qwen_manga_worker.py \
  scripts/pearl_star/bin/pscli \
  scripts/pearl_star/install/expose_queue_env_for_operator.sh
do
  git checkout "${REF}" -- "${p}"
done

bash scripts/pearl_star/install/expose_queue_env_for_operator.sh

HERE="$(cd scripts/pearl_star/install && pwd)"
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"
OP_ENV="${REPO_ROOT}/.pearl_star_queue.env"

echo "=== worker health ==="
if ! systemctl is-active --quiet procrastinate-worker; then
  echo "FAIL: procrastinate-worker not active (check journalctl -u procrastinate-worker -n 30)" >&2
  exit 1
fi
if ! pgrep -f "procrastinate.*worker.*t2i" >/dev/null; then
  echo "FAIL: no procrastinate t2i worker process (crash-loop? journalctl -u procrastinate-worker -n 30)" >&2
  exit 1
fi

set -a && . "${OP_ENV}" && set +a
echo "=== clearing stale t2i jobs (concurrency=1 blocks smoke) ==="
"${PS_PY}" "${HERE}/reset_zombie_procrastinate_jobs.py" --stale-minutes 30 --queue t2i

SMOKE_PANEL="${SMOKE_PANEL:-ep001_035}"
OUT="artifacts/manga/panels/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001/${SMOKE_PANEL}.png"
echo "=== one-panel queue smoke (${SMOKE_PANEL}) ==="
curl -sf -m 8 http://127.0.0.1:8188/system_stats >/dev/null || {
  echo "FAIL: ComfyUI not reachable on :8188" >&2
  exit 1
}

if [ -f "${OUT}" ]; then
  mv -f "${OUT}" "${OUT}.pre_smoke.bak"
  echo "backed up existing ${OUT} → ${OUT}.pre_smoke.bak"
fi

python3 scripts/manga/queue_panel_renders.py \
  --via-queue \
  --panel-prompts artifacts/manga/panel_prompts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.panel_prompts.json \
  --output-dir artifacts/manga/panels/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001/ \
  --only-panel "${SMOKE_PANEL}"

OUT="artifacts/manga/panels/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001/${SMOKE_PANEL}.png"
if [ ! -s "${OUT}" ]; then
  echo "FAIL: smoke output missing: ${OUT}" >&2
  exit 1
fi
MTIME="$(stat -c %Y "${OUT}" 2>/dev/null || stat -f %m "${OUT}")"
NOW="$(date +%s)"
AGE=$((NOW - MTIME))
if [ "${AGE}" -gt 600 ]; then
  echo "FAIL: ${OUT} mtime is ${AGE}s old — smoke skipped existing file or worker did not render" >&2
  exit 1
fi
echo "SMOKE OK: ${OUT} ($(stat -c%s "${OUT}" 2>/dev/null || stat -f %z "${OUT}") bytes, fresh)"
"${PS_PY}" "${REPO_ROOT}/scripts/pearl_star/bin/pscli" list --workload t2i --limit 5
