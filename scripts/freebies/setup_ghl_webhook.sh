#!/usr/bin/env bash
# Provision GHL inbound webhook for freebie lead capture (operator-only).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

ENV_NAME="PHOENIX_GHL_FUNNEL_WEBHOOK"
LOCAL_FILE="$REPO/config/local/ghl_funnel_webhook.url"

if [[ "${1:-}" == "" ]]; then
  echo "Usage: $0 <inbound-webhook-url>"
  echo "  Or: echo '<url>' > config/local/ghl_funnel_webhook.url"
  echo "See config/local/ghl_funnel_webhook.url.example and funnel/burnout_reset/GHL_HANDBOFF.md"
  exit 1
fi

URL="$1"
mkdir -p "$(dirname "$LOCAL_FILE")"
printf '%s\n' "$URL" > "$LOCAL_FILE"
chmod 600 "$LOCAL_FILE"

security add-generic-password -s phoenix-omega -a "$ENV_NAME" -w "$URL" -U 2>/dev/null || \
  security add-generic-password -s phoenix-omega -a "$ENV_NAME" -w "$URL"

eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
export PHOENIX_GHL_FUNNEL_WEBHOOK="$URL"

python3 scripts/freebies/inject_ghl_webhook.py --require-env
python3 scripts/freebies/verify_ghl_webhook_push.py
echo "GHL webhook provisioned and injected into all funnel landing pages (see config/freebies/ghl_funnel_capture.yaml)."
