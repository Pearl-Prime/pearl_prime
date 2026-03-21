#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SOURCE_FILE="${1:-${ROOT_DIR}/docs/all_credentials.txt}"
SOURCE_META="${ROOT_DIR}/.integration_sources.local.yaml"

if [[ ! -f "$SOURCE_FILE" ]]; then
  printf "Credentials source not found: %s\n" "$SOURCE_FILE" >&2
  exit 1
fi

extract_export_value() {
  local key="$1"
  sed -n "s/^export ${key}=\"\\([^\"]*\\)\"/\\1/p" "$SOURCE_FILE" | head -n 1
}

WP_SITE_URL="$(extract_export_value "WORDPRESS_SITE_URL")"
WP_USERNAME="$(extract_export_value "WORDPRESS_USERNAME")"
WP_APP_PASSWORD="$(extract_export_value "WORDPRESS_APP_PASSWORD")"

WORDPRESS_IMPORTED=false
if [[ -n "$WP_SITE_URL" && -n "$WP_USERNAME" && -n "$WP_APP_PASSWORD" ]]; then
  /bin/zsh "${ROOT_DIR}/scripts/integrations/setup_wordpress_local.sh" \
    "$WP_SITE_URL" \
    "$WP_USERNAME" \
    "$WP_APP_PASSWORD"
  WORDPRESS_IMPORTED=true
fi

cat > "$SOURCE_META" <<EOF
credentials_source_path: "$SOURCE_FILE"
last_imported_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
wordpress_imported: ${WORDPRESS_IMPORTED}
manual_lookup_only_services:
  - line
  - whatsapp
  - wechat
  - messenger
  - imessage
safe_usage_rules:
  - "Use only service-matched credentials or app-specific tokens."
  - "Do not try random username/password combinations across services."
  - "If API tokens are missing, sign in manually and generate the required token, app password, or channel secret."
EOF

printf "Saved local integration source metadata to %s\n" "$SOURCE_META"
if [[ "$WORDPRESS_IMPORTED" == true ]]; then
  printf "Imported WordPress application-password settings from the local credentials source.\n"
else
  printf "No structured WordPress application-password block was found in %s.\n" "$SOURCE_FILE"
fi

printf "Messaging/login notes:\n"
printf "  - This importer does not guess or spray passwords across services.\n"
printf "  - For LINE/WhatsApp/Messenger/WeChat, use the local credentials file only as a human reference unless you have actual API tokens.\n"
printf "  - Run %s/scripts/integrations/setup_messaging_channels_local.sh for the token-based setup.\n" "$ROOT_DIR"
