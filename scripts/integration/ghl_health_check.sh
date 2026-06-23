#!/usr/bin/env bash
# Pearl_Int — GHL integration health (no secret values printed).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

echo "═══ Pearl_Int GHL Health Check ═══"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

check_var() {
  local name="$1"
  local val="${!name:-}"
  if [[ -n "$val" ]]; then
    echo "OK  $name is set (len=${#val})"
    return 0
  fi
  echo "MISS $name"
  return 1
}

eval "$(python3 scripts/ci/load_integration_env_from_keychain.py 2>/dev/null || true)"

missing=0
for v in PHOENIX_GHL_FUNNEL_WEBHOOK GHL_API_KEY GHL_LOCATION_ID GHL_CONTACTS_URL; do
  check_var "$v" || missing=$((missing + 1))
done

LOCAL="$REPO/config/local/ghl_funnel_webhook.url"
if [[ -f "$LOCAL" ]] && [[ -s "$LOCAL" ]]; then
  echo "OK  local webhook file present ($(wc -c <"$LOCAL" | tr -d ' ') bytes)"
else
  echo "MISS local webhook file ($LOCAL)"
fi

echo "--- smoke (no live POST unless webhook set) ---"
python3 scripts/freebies/inject_ghl_webhook.py || true
python3 scripts/freebies/verify_ghl_webhook_push.py || true

echo "═══ done (missing required vars: $missing) ═══"
exit 0
