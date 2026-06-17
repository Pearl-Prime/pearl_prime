#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Pearl Star Job Queue V1 — Phase A install step 3: ComfyUI-Persistent-Queue
#
# Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §8 step 4, §4.4
# Installs the ComfyUI-Persistent-Queue custom_node (reboot-resume for
# ComfyUI's in-process queue — belt-and-suspenders with the durable
# Postgres work-list). Pinned commit per spec §14 (stale-extension risk).
#
# IDEMPOTENT + inline sudo. Restarts comfyui.service so the node loads.
# Authoring-only artifact: do NOT execute here.
# Tier policy: ComfyUI + custom node are free + local. CLAUDE.md OK.
# ---------------------------------------------------------------------------
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"

echo "=== [03] ComfyUI-Persistent-Queue custom_node ==="

NODE_DIR="${PS_COMFY_CUSTOM_NODES}/ComfyUI-Persistent-Queue"

if [ ! -d "${PS_COMFY_CUSTOM_NODES}" ]; then
  echo "  [pearl-star] ERROR: ComfyUI custom_nodes dir not found at ${PS_COMFY_CUSTOM_NODES}" >&2
  echo "  Set PS_COMFY_HOME to the real ComfyUI checkout and re-run." >&2
  echo "  (dispatcher convention: ~/phoenix_server/ComfyUI)" >&2
  exit 2
fi

# --- 1. clone or update at pinned ref --------------------------------------
if [ -d "${NODE_DIR}/.git" ]; then
  ps_skip "custom_node present at ${NODE_DIR} (fetching + checking out pin)"
  sudo git -C "${NODE_DIR}" fetch --quiet origin
else
  ps_say "Cloning ComfyUI-Persistent-Queue into ${NODE_DIR}"
  sudo git clone --quiet "${PS_CPQ_REPO}" "${NODE_DIR}"
fi
ps_say "Checking out pin: ${PS_CPQ_PIN}"
sudo git -C "${NODE_DIR}" checkout --quiet "${PS_CPQ_PIN}"
RESOLVED="$(sudo git -C "${NODE_DIR}" rev-parse --short HEAD)"
ps_ok "ComfyUI-Persistent-Queue at ${RESOLVED}"

# --- 2. install node python requirements (if any) into ComfyUI's env -------
if [ -f "${NODE_DIR}/requirements.txt" ]; then
  ps_say "Installing custom_node requirements (best-effort; ComfyUI venv)"
  # ComfyUI typically runs from its own venv; try common locations, non-fatal.
  if [ -x "${PS_COMFY_HOME}/venv/bin/pip" ]; then
    sudo "${PS_COMFY_HOME}/venv/bin/pip" install -r "${NODE_DIR}/requirements.txt" >/dev/null || \
      ps_say "WARN: requirements install non-zero; review manually"
  else
    ps_say "WARN: ComfyUI venv pip not found at ${PS_COMFY_HOME}/venv — install requirements manually"
  fi
fi

# --- 3. restart comfyui so the node loads ----------------------------------
if systemctl list-unit-files 2>/dev/null | grep -q '^comfyui\.service'; then
  ps_say "Restarting comfyui.service to load the custom_node"
  sudo systemctl restart comfyui.service
  sleep 3
else
  ps_say "WARN: comfyui.service not installed yet — install it (see RUNBOOK step for systemd) then: sudo systemctl restart comfyui"
fi

# --- 4. verify ComfyUI answers + node is loadable --------------------------
ps_say "Verifying ComfyUI reachable at ${PS_COMFY_URL}"
if curl -fsS "${PS_COMFY_URL}/system_stats" >/dev/null 2>&1; then
  ps_ok "ComfyUI reachable; Persistent-Queue node installed at ${RESOLVED}"
else
  echo "  [pearl-star] WARN: ComfyUI not answering on ${PS_COMFY_URL} yet." >&2
  echo "  Start it (comfyui.service) and confirm the node appears in the log." >&2
fi

echo "=== [03] done ==="
