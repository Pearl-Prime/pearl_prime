#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Pearl Star Job Queue V1 — Phase A install step 4: user + directories
#
# Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §5.1 (heartbeat dirs), §5.4 (alerts),
#       §14 (backup dir). Handoff §5.2 (system user + dirs).
#
# Creates the pearl-star system user/group and every runtime directory:
#   /opt/pearl-star, /var/log/pearl-star, /var/lib/pearl-star{,/output,/dlq},
#   /run/pearl-star/heartbeat (tmpfs via tmpfiles.d), /var/backups/postgres.
#
# IDEMPOTENT + inline sudo. Authoring-only artifact: do NOT execute here.
# ---------------------------------------------------------------------------
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"

echo "=== [04] system user + runtime directories ==="

# --- 1. system group + user ------------------------------------------------
if getent group "${PS_GROUP}" >/dev/null 2>&1; then
  ps_skip "group ${PS_GROUP} exists"
else
  ps_say "Creating system group ${PS_GROUP}"
  sudo groupadd --system "${PS_GROUP}"
fi
if id "${PS_USER}" >/dev/null 2>&1; then
  ps_skip "user ${PS_USER} exists"
else
  ps_say "Creating system user ${PS_USER} (home ${PS_HOME}, nologin)"
  sudo useradd --system --gid "${PS_GROUP}" --home-dir "${PS_HOME}" \
    --shell /usr/sbin/nologin --comment "Pearl Star Job Queue" "${PS_USER}"
fi

# --- 2. persistent directories ---------------------------------------------
mk() {  # mk <path> <mode>
  if [ -d "$1" ]; then ps_skip "dir $1"; else ps_say "mkdir $1 ($2)"; fi
  sudo install -d -o "${PS_USER}" -g "${PS_GROUP}" -m "$2" "$1"
}
mk "${PS_HOME}"            0755
mk "${PS_LOG_DIR}"         0755
mk "${PS_HEARTBEAT_FORENSIC}" 0755   # /var/log/pearl-star/heartbeat (60s flush, spec §5.1)
mk "${PS_LIB_DIR}"         0755
mk "${PS_OUTPUT_DIR}"      0755      # A1 output lands here (handoff §5.3)
mk "${PS_DLQ_DIR}"         0750      # dead-letter (handoff §5.2)
mk "${PS_ALERT_DIR}"       0755      # operator alert drops (spec §5.4)

# --- 3. backup dir (spec §14 — nightly pg_dump + R2 mirror) ----------------
ps_say "Backup dir ${PS_BACKUP_DIR} (spec §14 single-NVMe mitigation)"
sudo install -d -o postgres -g postgres -m 0750 "${PS_BACKUP_DIR}" 2>/dev/null \
  || sudo install -d -m 0750 "${PS_BACKUP_DIR}"

# --- 4. tmpfs heartbeat dir via tmpfiles.d (survives reboot recreation) ----
# /run is tmpfs; recreate the heartbeat tree on every boot (spec §5.1).
TMPFILES=/etc/tmpfiles.d/pearl-star.conf
ps_say "Installing tmpfiles.d rule -> ${PS_HEARTBEAT_DIR} (tmpfs, recreated on boot)"
sudo tee "${TMPFILES}" >/dev/null <<EOF
# Pearl Star Job Queue — recreate tmpfs runtime dirs on boot (spec §5.1)
d ${PS_RUN_DIR} 0755 ${PS_USER} ${PS_GROUP} -
d ${PS_HEARTBEAT_DIR} 0755 ${PS_USER} ${PS_GROUP} -
EOF
sudo systemd-tmpfiles --create "${TMPFILES}"
ps_ok "heartbeat tmpfs dir ready: ${PS_HEARTBEAT_DIR}"

echo
ps_ok "directories provisioned. Layout:"
printf '    %s\n' \
  "${PS_HOME}            (venv + app/)" \
  "${PS_LOG_DIR}         (worker/watchdog/monitor logs + heartbeat forensics)" \
  "${PS_OUTPUT_DIR}      (A1 smoke output)" \
  "${PS_DLQ_DIR}         (dead-letter queue)" \
  "${PS_ALERT_DIR}       (operator alert JSONL drops)" \
  "${PS_HEARTBEAT_DIR}   (tmpfs heartbeats)" \
  "${PS_BACKUP_DIR}      (nightly pg_dump)"
echo "=== [04] done ==="
