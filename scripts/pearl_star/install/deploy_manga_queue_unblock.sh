#!/usr/bin/env bash
# Deploy manga queue-unblock fix on Pearl Star (POST-CJK — requires free GPU).
#
# STAGE: commit + back-port only (run from laptop).
# DEPLOY: after CJK data lane completes per OPD-20260629-003 Order A:
#   ssh -t pearl_star 'cd ~/phoenix_omega && bash scripts/pearl_star/install/deploy_manga_queue_unblock.sh'
#
# Ref: OPD-20260629-003; manga QA dispatch-bug diagnosis 2026-06-29.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${REPO_ROOT}"

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"

DEPLOY="${1:-}"
if [[ "${DEPLOY}" != "--deploy" ]]; then
  echo "STAGE-ONLY mode (no GPU, no service restarts)."
  echo "Re-run on Pearl Star after CJK frees GPU:"
  echo "  bash scripts/pearl_star/install/deploy_manga_queue_unblock.sh --deploy"
  exit 0
fi

echo "=== [deploy] manga queue-unblock (OPD-20260629-003) ==="

# --- 1. pearl-star-owned manga output root ---------------------------------
sudo install -d -o "${PS_USER}" -g "${PS_GROUP}" -m 0755 "${PS_MANGA_OUT_ROOT:-/var/lib/pearl-star/manga_out}"

# --- 2. sync workers + lock module (install kit back-port) -----------------
bash "${HERE}/expose_queue_env_for_operator.sh"

# --- 3. zombie reset (stale doing → failed, not todo) ----------------------
set -a && . "${REPO_ROOT}/.pearl_star_queue.env" && set +a
"${PS_PY}" "${HERE}/reset_zombie_procrastinate_jobs.py" --stale-minutes 30 --queue t2i

# --- 4. kill stale waiters (Jun-25 bulk + ep_010 queue_panel_renders) -----
for pat in "queue_panel_renders.py.*ep_010" "warrior_then_stillness"; do
  pids="$(pgrep -f "${pat}" 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "killing stale: ${pat} → ${pids}"
    kill ${pids} 2>/dev/null || true
  fi
done

# --- 5. release manga GPU lane + resume t2i dispatch -----------------------
pscli gpu-release 2>/dev/null || true
pscli resume 2>/dev/null || true
sudo systemctl restart procrastinate-worker
sleep 3
systemctl is-active procrastinate-worker

# --- 6. operator-visible symlink (optional; idempotent) --------------------
MANGA_OUT="${PS_MANGA_OUT_ROOT:-/var/lib/pearl-star/manga_out}"
LINK="${REPO_ROOT}/artifacts/manga/pearl_star_out"
ln -sfn "${MANGA_OUT}" "${LINK}"
echo "symlink: ${LINK} → ${MANGA_OUT}"

echo
echo "=== deploy complete — run single-panel smoke next (GPU required) ==="
echo "  pscli gpu-acquire manga"
echo "  python3 scripts/manga/queue_panel_renders.py --via-queue \\"
echo "    --panel-prompts artifacts/manga/panel_prompts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.panel_prompts.json \\"
echo "    --output-dir artifacts/manga/panels/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001/ \\"
echo "    --only-panel ep001_035 --skip-existing"
echo "  pscli gpu-release"
