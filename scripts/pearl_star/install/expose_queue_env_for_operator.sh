#!/usr/bin/env bash
# One-time operator step: repair queue.env DSN + sync workers + operator-readable env copy.
# Requires interactive sudo on Pearl Star (see RUNBOOK.md §B for temporary NOPASSWD option).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"
REPO_ROOT="$(cd "${HERE}/../../.." && pwd)"
WORKER_SRC="${REPO_ROOT}/scripts/pearl_star/worker"
PS_APP="${PS_HOME}/app"

echo "=== expose queue env + worker sync for SSH enqueue ==="

sudo install -d -m 0750 /etc/pearl-star
# ps_dsn must run as root (reads /opt/pearl-star/.pgpass_queue) — never expand $(ps_dsn) in ahjan108 shell.
sudo env HERE="${HERE}" PS_GROUP="${PS_GROUP}" bash <<'EOSUDO'
set -euo pipefail
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"
DSN="$(ps_dsn)"
cat > /etc/pearl-star/queue.env <<EOF
PS_QUEUE_DSN=${DSN}
PS_PG_SCHEMA=${PS_PG_SCHEMA}
PS_COMFY_URL=${PS_COMFY_URL}
PS_OUTPUT_DIR=${PS_OUTPUT_DIR}
PS_LIB_DIR=${PS_LIB_DIR}
PS_LOG_DIR=${PS_LOG_DIR}
PS_DLQ_DIR=${PS_DLQ_DIR}
PS_ALERT_DIR=${PS_ALERT_DIR}
PS_HEARTBEAT_DIR=${PS_HEARTBEAT_DIR}
PS_HEARTBEAT_FORENSIC=${PS_HEARTBEAT_FORENSIC}
PS_HEARTBEAT_INTERVAL_S=${PS_HEARTBEAT_INTERVAL_S}
PS_WATCHDOG_TICK_S=${PS_WATCHDOG_TICK_S}
PS_HEARTBEAT_SILENCE_KILL_S=${PS_HEARTBEAT_SILENCE_KILL_S}
PS_SIGTERM_GRACE_S=${PS_SIGTERM_GRACE_S}
PS_COMFY_OUTPUT=${PS_COMFY_HOME}/output
EOF
chmod 0640 /etc/pearl-star/queue.env
chgrp "${PS_GROUP}" /etc/pearl-star/queue.env
EOSUDO

USER_HOME="${HOME:-/home/${SUDO_USER:-ahjan108}}"
OP_ENV="${USER_HOME}/phoenix_omega/.pearl_star_queue.env"
echo "copying queue env → ${OP_ENV}"
sudo cp /etc/pearl-star/queue.env "${OP_ENV}"
sudo chown "$(whoami):$(id -gn)" "${OP_ENV}"
chmod 600 "${OP_ENV}"

echo "syncing worker modules → ${PS_APP}"
sudo install -d -m 0755 "${PS_APP}"
for f in app.py flux_schnell_worker.py flux_dev_manga_worker.py qwen_manga_worker.py; do
  sudo install -m 0644 "${WORKER_SRC}/${f}" "${PS_APP}/${f}"
done
for f in watchdog.py monitor.py; do
  sudo install -m 0755 "${REPO_ROOT}/scripts/pearl_star/bin/${f}" "${PS_APP}/${f}"
done
sudo install -m 0755 "${REPO_ROOT}/scripts/pearl_star/bin/pscli" /usr/local/bin/pscli
sudo chown -R "${PS_USER}:${PS_GROUP}" "${PS_APP}"

echo "restarting queue services"
sudo systemctl restart pearl-star-monitor procrastinate-worker
sleep 3
sudo systemctl is-active procrastinate-worker pearl-star-monitor pearl-star-watchdog

set -a && . "${OP_ENV}" && set +a
"${PS_PY}" "${REPO_ROOT}/scripts/pearl_star/bin/pscli" status

echo "=== done — operator copy at ${OP_ENV} ==="
