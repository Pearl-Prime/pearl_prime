#!/usr/bin/env bash
set -euo pipefail
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
export PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1
: "${DASHSCOPE_FREE_QUOTA_API_KEY:?FREE_KEY missing after Keychain load}"
PROOF=artifacts/qa/manga_video_pose_bank_pilot_2026-07-24
PYTHONPATH=. python3 scripts/manga/video_bank/run_capture_burn.py \
  --manifest "${PROOF}/capture_manifest.json" \
  --proof-root "$PROOF" \
  --preflight-only \
  --max-seconds 85
