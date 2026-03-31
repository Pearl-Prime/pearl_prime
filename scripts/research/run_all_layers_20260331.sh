#!/usr/bin/env bash
# Run two-pass Qwen3 research for all wired layers with fixed artifact stems.
# Requires: Ollama + Qwen3 (see scripts/research/README.md).
# Usage:
#   PASTE=artifacts/research/raw/2026-03-31/some_feed.txt bash scripts/research/run_all_layers_20260331.sh
#   STEM=2026-03-31 PASTE=path/to/raw.txt bash scripts/research/run_all_layers_20260331.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STEM="${STEM:-2026-03-31}"
RUNNER=(python3 "$ROOT/scripts/research/run_research.py" --output-stem "$STEM")
[[ -n "${PASTE:-}" ]] && RUNNER+=(--paste "$PASTE")

for id in psychology pain_points event_impact narrative platform linguistic semantic_trend; do
  echo "=== $id ===" >&2
  "${RUNNER[@]}" --prompt-id "$id"
done
