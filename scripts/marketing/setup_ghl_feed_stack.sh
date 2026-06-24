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

# Verify 15-topic feed coverage (E1 + E5 per topic)
PYTHONPATH=. python3 - "$BRAND" "$LOCALE" <<'PY'
import json
import sys
from collections import defaultdict
from pathlib import Path

brand, locale = sys.argv[1], sys.argv[2]
feed_path = sorted(Path("artifacts/marketing_feed").glob(f"{brand}/{locale}/*/marketing_feed.json"))[-1]
feed = json.loads(feed_path.read_text())
by_topic = defaultdict(set)
for item in feed["items"]:
    by_topic[item["topic"]].add(item["email_slot"])
topics = sorted(by_topic)
e1 = sum(1 for t in topics if "e1" in by_topic[t])
e5 = sum(1 for t in topics if "e5" in by_topic[t])
print(f"feed: {feed_path} · topics={len(topics)} · items={len(feed['items'])} · e1={e1} · e5={e5}")
if len(topics) != 15 or e1 != 15 or e5 != 15:
    print("ERROR: expected 15 topics with E1 and E5 each", file=sys.stderr)
    sys.exit(1)
PY

python3 scripts/marketing/publish_marketing_feed_r2.py --brand-id "$BRAND" --locale "$LOCALE" --dry-run

echo ""
echo "Feed URL shape (paste to GHL admin after R2 + CDN live):"
echo "  \${PEARL_PRIME_CONTENT_CDN_URL}/pearl-prime-content/${BRAND}/${LOCALE}/<week>/marketing_feed.json"
echo ""
echo "Webhook: run ./scripts/freebies/setup_ghl_webhook.sh '<url>' when GHL admin returns URL"
echo "═══ done ═══"
