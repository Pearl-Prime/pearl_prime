#!/usr/bin/env bash
# Provision pearl-prime-content R2 + publish marketing feed (no Cloudflare dashboard).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

BUCKET="${PEARL_PRIME_CONTENT_R2_BUCKET:-pearl-prime-content}"
BRAND="${1:-stillness_press}"
LOCALE="${2:-en_US}"

echo "=== Pearl_Int GHL feed R2 (API token only) ==="
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py 2>/dev/null || true)"

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" || -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]]; then
  echo "ERROR: Missing CLOUDFLARE_API_TOKEN or CLOUDFLARE_ACCOUNT_ID in Keychain."
  exit 1
fi

WR="npx --yes wrangler@4"

echo "--- wrangler whoami ---"
$WR whoami

echo "--- create bucket ${BUCKET} ---"
if $WR r2 bucket list 2>/dev/null | grep -q "^${BUCKET}$"; then
  echo "bucket already exists"
else
  $WR r2 bucket create "${BUCKET}"
fi

echo "--- public r2.dev URL ---"
set +e
$WR r2 bucket dev-url enable "${BUCKET}" 2>/dev/null
CDN_BASE="$($WR r2 bucket dev-url get "${BUCKET}" 2>/dev/null | grep -Eo 'https://pub-[a-f0-9]+\.r2\.dev' | tail -1)"
set -e

if [[ -z "${CDN_BASE}" || ! "${CDN_BASE}" =~ ^https://pub-[a-f0-9]+\.r2\.dev$ ]]; then
  echo "ERROR: could not resolve pub-*.r2.dev CDN URL for bucket ${BUCKET}" >&2
  echo "Check CLOUDFLARE_API_TOKEN has Account → R2 → Edit permissions." >&2
  exit 1
fi

if [[ -n "${CDN_BASE}" ]]; then
  echo "CDN base: ${CDN_BASE}"
  security add-generic-password -s phoenix-omega -a PEARL_PRIME_CONTENT_CDN_URL -w "${CDN_BASE}" -U 2>/dev/null || true
  security add-generic-password -s phoenix-omega -a PEARL_PRIME_CONTENT_R2_BUCKET -w "${BUCKET}" -U 2>/dev/null || true
else
  echo "WARN: no r2.dev URL yet; set PEARL_PRIME_CONTENT_CDN_URL manually after enable"
fi

python3 scripts/marketing/build_funnel_book_url_index.py
PYTHONPATH=. python3 scripts/marketing/build_marketing_feed.py --brand-id "${BRAND}" --locale "${LOCALE}"

FEED_DIR="$(ls -td "artifacts/marketing_feed/${BRAND}/${LOCALE}/"*/ | head -1)"
FEED="${FEED_DIR}marketing_feed.json"
WEEK="$(basename "${FEED_DIR%/}")"
OBJ_KEY="pearl-prime-content/${BRAND}/${LOCALE}/${WEEK}/marketing_feed.json"

echo "--- upload ${FEED} ---"
$WR r2 object put "${BUCKET}/${OBJ_KEY}" --file "${FEED}" --content-type application/json --remote

if [[ -n "${CDN_BASE}" ]]; then
  PUBLIC="${CDN_BASE}/${OBJ_KEY}"
  echo ""
  echo "============================================================"
  echo "GHL admin feed URL:"
  echo "  ${PUBLIC}"
  echo ""
  echo "GitHub secrets (optional, for weekly CI):"
  echo "  gh secret set PEARL_PRIME_CONTENT_R2_BUCKET -b '${BUCKET}'"
  echo "  gh secret set PEARL_PRIME_CONTENT_CDN_URL -b '${CDN_BASE}'"
  echo "============================================================"
fi
