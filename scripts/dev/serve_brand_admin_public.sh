#!/usr/bin/env bash
# Serve brand-wizard-app/public (onboarding PNG deck, gallery, registry).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PORT="${1:-8899}"
cd "${ROOT}/brand-wizard-app/public"
echo "http://127.0.0.1:${PORT}/onboarding/presentation.html"
echo "http://127.0.0.1:${PORT}/lane_examples_gallery.html"
exec python3 -m http.server "${PORT}" --bind 127.0.0.1
