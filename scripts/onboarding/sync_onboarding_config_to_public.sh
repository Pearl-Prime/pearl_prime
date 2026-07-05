#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="${ROOT}/brand-wizard-app/public/onboarding"
PUBLIC="${ROOT}/brand-wizard-app/public"
mkdir -p "${DEST}"
shopt -s nullglob
onboarding_json=("${ROOT}/config/onboarding"/*.json)
if ((${#onboarding_json[@]})); then
  cp "${onboarding_json[@]}" "${DEST}/"
  echo "Synced config/onboarding/*.json -> brand-wizard-app/public/onboarding/"
else
  echo "warn: no config/onboarding/*.json (skip)" >&2
fi

# Static onboarding/prez spine (repo root) → public root so Cloudflare Pages serves real HTML
# (not SPA index.html fallback).
SPINE_HTML=(
  market_lane_matrix.html
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

# Weekly OS: repo-root brand_admin_weekly_os.html is canonical logic; transform paths for Pages dist.
WEEKLY_OS_SRC="${ROOT}/brand_admin_weekly_os.html"
WEEKLY_OS_DEST="${PUBLIC}/brand_admin_weekly_os.html"
if [[ -f "${WEEKLY_OS_SRC}" ]]; then
  sed \
    -e 's|brand-wizard-app/public/assets/|assets/|g' \
    -e "s|JSON_BASE='brand-wizard-app/public/'|JSON_BASE=''|g" \
    -e 's|brand-wizard-app/public/brand_handoff_dashboard.html|brand_handoff_dashboard.html|g' \
    "${WEEKLY_OS_SRC}" > "${WEEKLY_OS_DEST}"
  echo "Synced brand_admin_weekly_os.html -> brand-wizard-app/public/ (Pages-safe paths)"
else
  echo "warn: missing brand_admin_weekly_os.html (skip)" >&2
fi

# Pearl Prime pitch deck (docs/) → public root so brand-admin-onboarding-bu2.pages.dev serves them
DOCS_HTML=(
  pearl_prime_v6-3.html
  pearl_prime_v6-3-ja.html
  pearl_prime_v6-3-zh.html
  pearl_prime_v6-3-tw.html
)
for f in "${DOCS_HTML[@]}"; do
  src="${ROOT}/docs/${f}"
  if [[ -f "${src}" ]]; then
    cp "${src}" "${PUBLIC}/${f}"
  else
    echo "warn: missing docs/${f} (skip)" >&2
  fi
done
echo "Synced docs/ pitch deck HTML -> brand-wizard-app/public/"
# Onboarding MP3 benchmarks (TTS): committed under brand-wizard-app/public/onboarding/audio/
# Regenerate: python3 scripts/onboarding/generate_voice_benchmark_audio.py
