#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.wordpress.local"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE. Run scripts/integrations/setup_wordpress_local.sh first." >&2
  exit 1
fi

source "$ENV_FILE"

: "${WORDPRESS_SITE_URL:?Missing WORDPRESS_SITE_URL in $ENV_FILE}"
: "${WORDPRESS_USERNAME:?Missing WORDPRESS_USERNAME in $ENV_FILE}"
: "${WORDPRESS_KEYCHAIN_SERVICE:?Missing WORDPRESS_KEYCHAIN_SERVICE in $ENV_FILE}"

WORDPRESS_APP_PASSWORD="$(security find-generic-password -a "$WORDPRESS_USERNAME" -s "$WORDPRESS_KEYCHAIN_SERVICE" -w)"
export WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD

python3 "${ROOT_DIR}/scripts/pearl_news_post_to_wp.py" \
  --title "Phoenix Omega WordPress connection test" \
  --content "<p>Local dry-run connection check.</p>" \
  --dry-run
