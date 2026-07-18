# shellcheck shell=bash
# ---------------------------------------------------------------------------
# Pearl Star Job Queue V1 — Phase A shared install config
#
# SOURCE this file from every install/smoke script:  . "$(dirname "$0")/00_config.sh"
# It centralizes every path, port, user, and version so the kit has ONE
# source of truth. Edit here, not in the individual scripts.
#
# Spec: docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md (§4, §5, §8)
# Tier policy: CLAUDE.md — all Tier-2 (free + local). No paid LLM API.
# ---------------------------------------------------------------------------
set -euo pipefail

# --- identity --------------------------------------------------------------
PS_USER="${PS_USER:-pearl-star}"          # dedicated system user that owns the queue
PS_GROUP="${PS_GROUP:-pearl-star}"

# --- postgres --------------------------------------------------------------
PS_PG_VERSION="${PS_PG_VERSION:-17}"      # spec §8 step 1 — Ubuntu 24.04 canonical
PS_PG_DB="${PS_PG_DB:-pearl_star_queue}"  # spec §4.2 — database name
PS_PG_ROLE="${PS_PG_ROLE:-pearl_star}"    # login role for the queue
PS_PG_SCHEMA="${PS_PG_SCHEMA:-pearl_star_queue}"  # handoff §5.2 — schema name
PS_PG_HOST="${PS_PG_HOST:-127.0.0.1}"     # spec §2 constraint 4 — localhost only
PS_PG_PORT="${PS_PG_PORT:-5432}"
# Password is generated on first install and stored 0600 at PS_PG_PWFILE.
# NEVER commit a real password. The installer writes one if absent.
PS_PG_PWFILE="${PS_PG_PWFILE:-/opt/pearl-star/.pgpass_queue}"

# Procrastinate connection string (psycopg3). Built at runtime from the above.
ps_dsn() {
  local pw=""
  if [ -r "${PS_PG_PWFILE}" ]; then pw="$(cat "${PS_PG_PWFILE}")"; fi
  printf 'postgresql://%s:%s@%s:%s/%s' \
    "${PS_PG_ROLE}" "${pw}" "${PS_PG_HOST}" "${PS_PG_PORT}" "${PS_PG_DB}"
}

# --- python venv -----------------------------------------------------------
PS_HOME="${PS_HOME:-/opt/pearl-star}"             # handoff §5.2
PS_VENV="${PS_VENV:-/opt/pearl-star/venv}"        # handoff §5.2 — Procrastinate venv
PS_PY="${PS_PY:-${PS_VENV}/bin/python}"
PS_PIP="${PS_PIP:-${PS_VENV}/bin/pip}"
# Pinned per spec §14 risk register (Procrastinate breaking-API risk).
PS_PROCRASTINATE_PIN="${PS_PROCRASTINATE_PIN:-procrastinate[psycopg]==2.*}"

# --- comfyui ---------------------------------------------------------------
# Endpoint convention from scripts/image_generation/dispatchers/pearl_star_dispatcher.py
PS_COMFY_URL="${PS_COMFY_URL:-http://127.0.0.1:8188}"
PS_COMFY_HOME="${PS_COMFY_HOME:-/home/${SUDO_USER:-ahjan108}/phoenix_server/ComfyUI}"
PS_COMFY_CUSTOM_NODES="${PS_COMFY_CUSTOM_NODES:-${PS_COMFY_HOME}/custom_nodes}"
# Pinned commit for ComfyUI-Persistent-Queue per spec §14 (stale-extension risk).
# Operator: confirm/refresh this SHA against upstream before running 03_*.sh.
PS_CPQ_REPO="${PS_CPQ_REPO:-https://github.com/Hangover3832/ComfyUI-Persistent-Queue.git}"
PS_CPQ_PIN="${PS_CPQ_PIN:-main}"   # <-- replace with a pinned SHA after operator review

# --- other service ports (informational; not installed in Phase A) ---------
PS_OLLAMA_URL="${PS_OLLAMA_URL:-http://127.0.0.1:11434}"     # spec §3.3 / §4.1
PS_COSYVOICE_URL="${PS_COSYVOICE_URL:-http://127.0.0.1:9880}" # spec §3.2 / §4.1

# --- queue runtime dirs (created by 04_directories.sh) ---------------------
PS_LOG_DIR="${PS_LOG_DIR:-/var/log/pearl-star}"
PS_LIB_DIR="${PS_LIB_DIR:-/var/lib/pearl-star}"
PS_OUTPUT_DIR="${PS_OUTPUT_DIR:-/var/lib/pearl-star/output}"     # handoff §5.3 A1
PS_MANGA_OUT_ROOT="${PS_MANGA_OUT_ROOT:-/var/lib/pearl-star/manga_out}"  # t2i panel PNG land (pearl-star owned)
PS_DLQ_DIR="${PS_DLQ_DIR:-/var/lib/pearl-star/dlq}"              # handoff §5.2 dead-letter
PS_RUN_DIR="${PS_RUN_DIR:-/run/pearl-star}"                      # tmpfs heartbeats
PS_HEARTBEAT_DIR="${PS_HEARTBEAT_DIR:-/run/pearl-star/heartbeat}"           # spec §5.1 (tmpfs)
PS_HEARTBEAT_FORENSIC="${PS_HEARTBEAT_FORENSIC:-/var/log/pearl-star/heartbeat}"  # spec §5.1 (60s flush)
PS_BACKUP_DIR="${PS_BACKUP_DIR:-/var/backups/postgres}"         # spec §14 nightly pg_dump

# --- watchdog tunables (spec §5.1 / §5.2 — Q-PSQ-WATCHDOG-INTERVAL-01) ------
PS_HEARTBEAT_INTERVAL_S="${PS_HEARTBEAT_INTERVAL_S:-30}"   # worker emit cadence
PS_HEARTBEAT_FLUSH_S="${PS_HEARTBEAT_FLUSH_S:-60}"         # tmpfs->forensic flush cadence
PS_WATCHDOG_TICK_S="${PS_WATCHDOG_TICK_S:-60}"            # watchdog poll cadence
PS_HEARTBEAT_SILENCE_KILL_S="${PS_HEARTBEAT_SILENCE_KILL_S:-90}"  # silent>90s => CRASHED
PS_SIGTERM_GRACE_S="${PS_SIGTERM_GRACE_S:-10}"           # SIGTERM->SIGKILL grace (spec §5.2)
PS_STALL_WARN_MULT="${PS_STALL_WARN_MULT:-2}"            # 2x expected => STALL_WARN
PS_STALL_KILL_MULT="${PS_STALL_KILL_MULT:-3}"            # 3x expected => STALL_KILL

# --- repo bin location (where pscli/watchdog/monitor are deployed FROM) -----
# These are the in-repo authored sources; the runbook copies them onto Pearl Star.
PS_REPO_BIN="${PS_REPO_BIN:-scripts/pearl_star/bin}"

# --- alert drop dir (repo-relative on the producer side; spec §5.4) --------
PS_ALERT_DIR="${PS_ALERT_DIR:-/var/lib/pearl-star/operator_alerts}"

# Helper: idempotent "say what you do" echo.
ps_say() { printf '  [pearl-star] %s\n' "$*"; }
ps_ok()  { printf '  [pearl-star] OK: %s\n' "$*"; }
ps_skip(){ printf '  [pearl-star] SKIP (already done): %s\n' "$*"; }
