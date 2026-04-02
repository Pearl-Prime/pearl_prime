#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="${ROOT}/brand-wizard-app/public/onboarding"
PUBLIC="${ROOT}/brand-wizard-app/public"
mkdir -p "${DEST}"
cp "${ROOT}/config/onboarding"/*.json "${DEST}/"
echo "Synced config/onboarding/*.json -> brand-wizard-app/public/onboarding/"

# Static onboarding/prez spine (repo root) → public root so Cloudflare Pages serves real HTML
# (not SPA index.html fallback).
SPINE_HTML=(
  brand_onboarding_hub.html
  brand_admin_master_onboarding.html
  brand_admin_weekly_os.html
  market_lane_matrix.html
  lane_examples_gallery.html
  us_brand_admin_v32_briefing.html
  jp_brand_admin_v32_briefing.html
)
for f in "${SPINE_HTML[@]}"; do
  src="${ROOT}/${f}"
  if [[ -f "${src}" ]]; then
    cp "${src}" "${PUBLIC}/${f}"
  else
    echo "warn: missing ${f} (skip)" >&2
  fi
done
echo "Synced onboarding spine HTML -> brand-wizard-app/public/"
