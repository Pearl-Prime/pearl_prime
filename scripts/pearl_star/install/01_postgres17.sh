#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Pearl Star Job Queue V1 — Phase A install step 1: PostgreSQL 17 broker
#
# Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §8 step 1-2, §4.2, §4.5
# Installs Postgres 17, creates the queue role + database, and sets
# synchronous_commit=on (spec §4.5 — ACID durability, reboot-resume).
#
# IDEMPOTENT: re-running is safe — every step checks state first.
# Uses `sudo` inline so it works run interactively by the OPERATOR or by a
# NOPASSWD execution agent. Authoring-only artifact: do NOT execute here.
#
# Tier policy: free + local (Postgres = MIT-ish PostgreSQL license). CLAUDE.md OK.
# ---------------------------------------------------------------------------
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=00_config.sh
. "${HERE}/00_config.sh"

echo "=== [01] PostgreSQL ${PS_PG_VERSION} broker install ==="

# --- 1. apt repo + package -------------------------------------------------
if command -v psql >/dev/null 2>&1 && psql --version 2>/dev/null | grep -q " ${PS_PG_VERSION}\."; then
  ps_skip "postgresql-${PS_PG_VERSION} already installed ($(psql --version))"
else
  ps_say "Adding PGDG apt repository (Ubuntu 24.04 ships 16 by default; spec wants 17)"
  if [ ! -f /etc/apt/sources.list.d/pgdg.list ]; then
    sudo install -d /usr/share/postgresql-common/pgdg
    sudo curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc
    # shellcheck disable=SC1091
    . /etc/os-release
    echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" \
      | sudo tee /etc/apt/sources.list.d/pgdg.list >/dev/null
  fi
  ps_say "apt-get update + install postgresql-${PS_PG_VERSION} postgresql-contrib-${PS_PG_VERSION}"
  sudo apt-get update -qq
  sudo apt-get install -y "postgresql-${PS_PG_VERSION}" "postgresql-contrib-${PS_PG_VERSION}"
  ps_ok "postgresql-${PS_PG_VERSION} installed"
fi

# --- 2. ensure cluster + service enabled -----------------------------------
ps_say "Enabling + starting postgresql@${PS_PG_VERSION}-main"
sudo systemctl enable --now "postgresql@${PS_PG_VERSION}-main" 2>/dev/null \
  || sudo systemctl enable --now postgresql
# Wait for the socket to accept connections (idempotent poll, max ~30s).
for _ in $(seq 1 30); do
  if sudo -u postgres psql -tAc 'SELECT 1' >/dev/null 2>&1; then break; fi
  sleep 1
done

# --- 3. queue login role ---------------------------------------------------
if [ ! -r "${PS_PG_PWFILE}" ]; then
  ps_say "Generating queue DB password -> ${PS_PG_PWFILE} (0600)"
  sudo install -d -o "${PS_USER}" -g "${PS_GROUP}" -m 0750 "$(dirname "${PS_PG_PWFILE}")" 2>/dev/null || true
  umask 077
  openssl rand -base64 24 | sudo tee "${PS_PG_PWFILE}" >/dev/null
  sudo chmod 0600 "${PS_PG_PWFILE}"
  sudo chown "${PS_USER}:${PS_GROUP}" "${PS_PG_PWFILE}" 2>/dev/null || true
else
  ps_skip "queue DB password file already present (${PS_PG_PWFILE})"
fi
QUEUE_PW="$(sudo cat "${PS_PG_PWFILE}")"

if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${PS_PG_ROLE}'" | grep -q 1; then
  ps_skip "role ${PS_PG_ROLE} exists (updating password to match pwfile)"
  sudo -u postgres psql -c "ALTER ROLE ${PS_PG_ROLE} WITH LOGIN PASSWORD '${QUEUE_PW}';" >/dev/null
else
  ps_say "Creating login role ${PS_PG_ROLE}"
  sudo -u postgres psql -c "CREATE ROLE ${PS_PG_ROLE} WITH LOGIN PASSWORD '${QUEUE_PW}';" >/dev/null
  ps_ok "role ${PS_PG_ROLE} created"
fi

# --- 4. queue database -----------------------------------------------------
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${PS_PG_DB}'" | grep -q 1; then
  ps_skip "database ${PS_PG_DB} exists"
else
  ps_say "Creating database ${PS_PG_DB} owned by ${PS_PG_ROLE}"
  sudo -u postgres createdb -O "${PS_PG_ROLE}" "${PS_PG_DB}"
  ps_ok "database ${PS_PG_DB} created"
fi

# --- 5. dedicated schema (handoff §5.2 — schema pearl_star_queue) ----------
ps_say "Ensuring schema ${PS_PG_SCHEMA} (owner ${PS_PG_ROLE})"
sudo -u postgres psql -d "${PS_PG_DB}" \
  -c "CREATE SCHEMA IF NOT EXISTS ${PS_PG_SCHEMA} AUTHORIZATION ${PS_PG_ROLE};" >/dev/null
# Make the role default to this schema so Procrastinate's tables land there.
sudo -u postgres psql -d "${PS_PG_DB}" \
  -c "ALTER ROLE ${PS_PG_ROLE} IN DATABASE ${PS_PG_DB} SET search_path TO ${PS_PG_SCHEMA}, public;" >/dev/null

# --- 6. durability: synchronous_commit=on (spec §4.5) ----------------------
ps_say "Setting synchronous_commit=on (spec §4.5 ACID durability)"
sudo -u postgres psql -c "ALTER SYSTEM SET synchronous_commit = 'on';" >/dev/null
sudo -u postgres psql -c "SELECT pg_reload_conf();" >/dev/null

ps_ok "PostgreSQL ${PS_PG_VERSION} broker ready: db=${PS_PG_DB} role=${PS_PG_ROLE} schema=${PS_PG_SCHEMA} on ${PS_PG_HOST}:${PS_PG_PORT}"
echo "    Connection (psycopg3): postgresql://${PS_PG_ROLE}:***@${PS_PG_HOST}:${PS_PG_PORT}/${PS_PG_DB}"
echo "=== [01] done ==="
