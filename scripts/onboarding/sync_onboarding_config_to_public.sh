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
# Consolidated to 7 pages — see plan audit.
# Only market_lane_matrix still lives at repo root.
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

# Pearl Prime pitch deck (docs/) → public root so brand-admin-onboarding.pages.dev serves them
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
