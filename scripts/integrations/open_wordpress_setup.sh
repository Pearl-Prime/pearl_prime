#!/bin/zsh
set -euo pipefail

SITE_URL="${1:-}"

if [[ -z "$SITE_URL" && -f "$(cd "$(dirname "$0")/../.." && pwd)/.env.wordpress.local" ]]; then
  source "$(cd "$(dirname "$0")/../.." && pwd)/.env.wordpress.local"
  SITE_URL="${WORDPRESS_SITE_URL:-}"
fi

if [[ -z "$SITE_URL" ]]; then
  echo "Usage: $0 https://your-site.example" >&2
  exit 1
fi

SITE_URL="${SITE_URL%/}"
SITE_URL="${SITE_URL%/wp-admin}"

open "${SITE_URL}/wp-admin/profile.php"
open "https://github.com/Ahjan108/phoenix_omega_v4.8/settings/secrets/actions"

echo "Opened WordPress profile page and phoenix_omega_v4.8 GitHub Actions secrets page."
