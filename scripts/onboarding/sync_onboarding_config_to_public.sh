#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="${ROOT}/brand-wizard-app/public/onboarding"
mkdir -p "${DEST}"
cp "${ROOT}/config/onboarding"/*.json "${DEST}/"
echo "Synced config/onboarding/*.json -> brand-wizard-app/public/onboarding/"
