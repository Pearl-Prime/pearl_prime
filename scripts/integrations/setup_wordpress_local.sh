#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.wordpress.local"
KEYCHAIN_SERVICE="phoenix-omega-wordpress"

prompt_if_empty() {
  local value="$1"
  local label="$2"
  if [[ -n "$value" ]]; then
    printf '%s' "$value"
    return 0
  fi
  printf "%s: " "$label" >&2
  IFS= read -r value
  printf '%s' "$value"
}

normalize_site_url() {
  local url="$1"
  url="${url%/}"
  url="${url%/wp-admin}"
  if [[ "$url" != http://* && "$url" != https://* ]]; then
    url="https://${url}"
  fi
  printf '%s' "$url"
}

SITE_URL="${1:-${WORDPRESS_SITE_URL:-}}"
USERNAME="${2:-${WORDPRESS_USERNAME:-}}"
APP_PASSWORD="${3:-${WORDPRESS_APP_PASSWORD:-}}"

SITE_URL="$(prompt_if_empty "$SITE_URL" "WordPress site URL")"
USERNAME="$(prompt_if_empty "$USERNAME" "WordPress username")"
if [[ -z "$APP_PASSWORD" ]]; then
  printf "WordPress application password: " >&2
  stty -echo
  IFS= read -r APP_PASSWORD
  stty echo
  printf "\n" >&2
fi

SITE_URL="$(normalize_site_url "$SITE_URL")"

security add-generic-password \
  -U \
  -a "$USERNAME" \
  -s "$KEYCHAIN_SERVICE" \
  -w "$APP_PASSWORD" >/dev/null

cat > "$ENV_FILE" <<EOF
WORDPRESS_SITE_URL="$SITE_URL"
WORDPRESS_USERNAME="$USERNAME"
WORDPRESS_KEYCHAIN_SERVICE="$KEYCHAIN_SERVICE"
EOF

printf "Saved site/user to %s and stored the app password in macOS Keychain service '%s'.\n" "$ENV_FILE" "$KEYCHAIN_SERVICE"
printf "Next steps:\n"
printf "  1. Run: %s/scripts/integrations/open_wordpress_setup.sh %s\n" "$ROOT_DIR" "$SITE_URL"
printf "  2. Test: %s/scripts/integrations/test_wordpress_local.sh\n" "$ROOT_DIR"
