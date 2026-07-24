#!/usr/bin/env bash
# Lane A — CJK6 educators/anxiety cloud translate on Singapore Model Studio free quota.
# Operator-present only. Hard-stops on Arrearage / FreeTierOnly (cloud script).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
unset OLLAMA_HOST
# Keychain often points QWEN_BASE_URL at Pearl Star :11434 — must not win.
unset QWEN_BASE_URL
export PHOENIX_TRANSLATION_ALLOW_CLOUD=1
export PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY=1
export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# Burn order: soon-expiring free SKUs first (DOC dates from recon).
MODELS=(
  "qwen3.5-plus-2026-04-20"
  "qwen3.6-27b"
  "deepseek-v4-flash"
  "qwen3.7-plus"
)
LOCALES=(ja-JP ko-KR zh-CN zh-HK zh-SG zh-TW)
PERSONA="${PERSONA:-educators}"
TOPIC="${TOPIC:-anxiety}"
BUDGET="${BUDGET_CAP_USD:-2}"
LOG_DIR="artifacts/coordination/heartbeats"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/cjk6_free_tier_translate_$(date -u +%Y%m%dT%H%M%SZ).log"

pick_model() {
  local m
  for m in "${MODELS[@]}"; do
    echo "$m"
    return 0
  done
}

MODEL="${DASHSCOPE_MODEL:-$(pick_model)}"
export DASHSCOPE_MODEL="$MODEL"
echo "Lane A start model=$MODEL persona=$PERSONA topic=$TOPIC" | tee -a "$LOG"

for loc in "${LOCALES[@]}"; do
  echo "=== locale=$loc model=$DASHSCOPE_MODEL ===" | tee -a "$LOG"
  set +e
  PYTHONPATH=. python3 scripts/translate_atoms_all_locales_cloud.py \
    --locale "$loc" --persona "$PERSONA" --topic "$TOPIC" \
    --dashscope-only --resume --budget-cap-usd "$BUDGET" 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  set -e
  if grep -qE 'FREE_TIER_HARD_STOP|Arrearage|FreeTierOnly' "$LOG"; then
    echo "HARD STOP free-tier/arrearage — aborting remaining locales" | tee -a "$LOG"
    exit 1
  fi
  if [[ $rc -ne 0 ]]; then
    # Rotate model once on generic failure, then continue
    for m in "${MODELS[@]}"; do
      if [[ "$m" != "$DASHSCOPE_MODEL" ]]; then
        export DASHSCOPE_MODEL="$m"
        echo "rotating model -> $DASHSCOPE_MODEL" | tee -a "$LOG"
        break
      fi
    done
  fi
done

echo "Lane A finished log=$LOG" | tee -a "$LOG"
