#!/usr/bin/env bash
# Dev/operator — build + validate GHL marketing feed (dry-run publish).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

BRAND="${1:-stillness_press}"
LOCALE="${2:-en_US}"

echo "═══ GHL feed stack (build + validate) ═══"
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py 2>/dev/null || true)"

python3 scripts/marketing/build_funnel_book_url_index.py --check || \
  python3 scripts/marketing/build_funnel_book_url_index.py

PYTHONPATH=. python3 scripts/marketing/build_marketing_feed.py --brand-id "$BRAND" --locale "$LOCALE"
PYTHONPATH=. python3 -m phoenix_v4.qa.validate_marketing_feed --sample-feed
python3 scripts/marketing/publish_marketing_feed_r2.py --brand-id "$BRAND" --locale "$LOCALE" --dry-run

echo ""
echo "Feed URL shape (paste to GHL admin after R2 + CDN live):"
echo "  \${PEARL_PRIME_CONTENT_CDN_URL}/pearl-prime-content/${BRAND}/${LOCALE}/<week>/marketing_feed.json"
echo ""
echo "Webhook: run ./scripts/freebies/setup_ghl_webhook.sh '<url>' when GHL admin returns URL"
echo "═══ done ═══"
