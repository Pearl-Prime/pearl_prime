#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Pearl Star Job Queue V1 — Phase A install step 2: Procrastinate + venv
#
# Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §8 step 3, §4.2
# Handoff §5.2: venv at /opt/pearl-star/venv, schema pearl_star_queue.
#
# Creates the venv, installs Procrastinate (psycopg3, pinned 2.*), applies the
# Procrastinate schema into the pearl_star_queue schema, and deploys the queue
# Python sources (worker + watchdog + monitor + pscli + app.py) into PS_HOME.
#
# IDEMPOTENT + inline sudo (operator OR NOPASSWD agent). Authoring-only.
# Tier policy: Procrastinate = MIT, Postgres-backed, local. CLAUDE.md OK.
# ---------------------------------------------------------------------------
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"
REPO_ROOT="$(cd "${HERE}/../../.." && pwd)"   # scripts/pearl_star/install -> repo root

echo "=== [02] Procrastinate venv + schema ==="

# --- 1. python3 + venv module ----------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  ps_say "Installing python3 + venv"
  sudo apt-get update -qq && sudo apt-get install -y python3 python3-venv python3-pip
fi

# --- 2. venv at /opt/pearl-star/venv ---------------------------------------
if [ -x "${PS_PY}" ]; then
  ps_skip "venv exists at ${PS_VENV}"
else
  ps_say "Creating venv at ${PS_VENV}"
  sudo install -d -o "${PS_USER}" -g "${PS_GROUP}" -m 0755 "${PS_HOME}" 2>/dev/null \
    || sudo install -d -m 0755 "${PS_HOME}"
  sudo python3 -m venv "${PS_VENV}"
  sudo chown -R "${PS_USER}:${PS_GROUP}" "${PS_VENV}" 2>/dev/null || true
  ps_ok "venv created"
fi

# --- 3. install procrastinate (pinned) + deps ------------------------------
ps_say "Installing ${PS_PROCRASTINATE_PIN} (+ requests for ComfyUI HTTP)"
sudo "${PS_PIP}" install --upgrade pip >/dev/null
sudo "${PS_PIP}" install "${PS_PROCRASTINATE_PIN}" "requests>=2.31" >/dev/null
ps_ok "$("${PS_PY}" -c 'import procrastinate; print("procrastinate "+procrastinate.__version__)' 2>/dev/null || echo 'procrastinate installed')"

# --- 4. deploy queue python sources into PS_HOME ---------------------------
# These are the authored repo artifacts; copy them onto Pearl Star so systemd
# units can import them. Sources: scripts/pearl_star/{worker,bin}.
ps_say "Deploying queue python sources to ${PS_HOME}/app"
sudo install -d -m 0755 "${PS_HOME}/app"
sudo install -m 0644 "${REPO_ROOT}/scripts/pearl_star/worker/app.py"                  "${PS_HOME}/app/app.py"
sudo install -m 0644 "${REPO_ROOT}/scripts/pearl_star/worker/flux_schnell_worker.py"  "${PS_HOME}/app/flux_schnell_worker.py"
sudo install -m 0755 "${REPO_ROOT}/scripts/pearl_star/bin/watchdog.py"                "${PS_HOME}/app/watchdog.py"
sudo install -m 0755 "${REPO_ROOT}/scripts/pearl_star/bin/monitor.py"                 "${PS_HOME}/app/monitor.py"
sudo install -m 0755 "${REPO_ROOT}/scripts/pearl_star/bin/pscli"                      /usr/local/bin/pscli
sudo chown -R "${PS_USER}:${PS_GROUP}" "${PS_HOME}/app" 2>/dev/null || true
ps_ok "sources deployed; pscli -> /usr/local/bin/pscli"

# --- 5. apply procrastinate schema into pearl_star_queue schema ------------
# search_path was set on the role in 01_*.sh so tables land in pearl_star_queue.
export PROCRASTINATE_APP="app.app:app"
DSN="$(ps_dsn)"
if sudo -u postgres psql -d "${PS_PG_DB}" -tAc \
     "SELECT 1 FROM information_schema.tables WHERE table_schema='${PS_PG_SCHEMA}' AND table_name='procrastinate_jobs'" \
     | grep -q 1; then
  ps_skip "Procrastinate schema already applied in ${PS_PG_SCHEMA}"
else
  ps_say "Applying Procrastinate schema (procrastinate schema --apply)"
  sudo -u "${PS_USER}" env \
    PROCRASTINATE_APP="${PROCRASTINATE_APP}" \
    PS_QUEUE_DSN="${DSN}" \
    PYTHONPATH="${PS_HOME}" \
    "${PS_PY}" -m procrastinate --app "${PROCRASTINATE_APP}" schema --apply
  ps_ok "Procrastinate schema applied into ${PS_PG_SCHEMA}"
fi

ps_ok "Procrastinate ready: venv=${PS_VENV} schema=${PS_PG_SCHEMA} app=app.app:app"
echo "=== [02] done ==="
