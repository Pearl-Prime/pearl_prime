#!/usr/bin/env bash
# Research Pipeline Entry Point
# Runs all research layers sequentially per RESEARCH_CITATION_GAP_DEV_SPEC section 3.
# Requires: Ollama running with qwen3:14b (or set OLLAMA_MODEL).
# Usage:
#   bash scripts/research/run_pipeline.sh [--dry-run] [--layers layer1,layer2,...] [--paste path/to/raw.txt]
#
# Dependency order (per spec section 7):
#   1. feed ingest (fetch_feeds.py)
#   2. psychology, pain_points, event_impact (layers 1-3, can run in parallel)
#   3. narrative, platform, linguistic (layers 4-6, depend on 1-3)
#   4. semantic_trend (depends on linguistic)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUNNER="$SCRIPT_DIR/run_research.py"
FETCH="$SCRIPT_DIR/fetch_feeds.py"
RAW_DIR="$REPO_ROOT/artifacts/research/raw"

DRY_RUN=""
PASTE_ARG=""
LAYERS="all"
DATE_STEM="$(date +%Y-%m-%d)"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --dry-run             Validate prompt files without calling LLM
  --layers LAYERS       Comma-separated layer list (default: all)
                        Available: psychology,pain_points,event_impact,
                                   narrative,platform,linguistic,semantic_trend
  --paste PATH          Path to raw feed data for paste input
  --output-stem STEM    Date stem for output files (default: today)
  -h, --help            Show this help

Examples:
  $(basename "$0") --dry-run
  $(basename "$0") --layers psychology,pain_points --paste artifacts/research/raw/2026-03-31/feed.xml
  $(basename "$0") --layers all
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN="--dry-run"; shift ;;
        --layers) LAYERS="$2"; shift 2 ;;
        --paste) PASTE_ARG="--paste $2"; shift 2 ;;
        --output-stem) DATE_STEM="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# Layer order respects dependency graph
ALL_LAYERS_ORDERED=(psychology pain_points event_impact narrative platform linguistic semantic_trend)

if [[ "$LAYERS" == "all" ]]; then
    SELECTED_LAYERS=("${ALL_LAYERS_ORDERED[@]}")
else
    IFS=',' read -ra SELECTED_LAYERS <<< "$LAYERS"
fi

echo "=== Research Pipeline ==="
echo "Date stem: $DATE_STEM"
echo "Layers:    ${SELECTED_LAYERS[*]}"
echo "Dry run:   ${DRY_RUN:-no}"
echo "Paste:     ${PASTE_ARG:-none}"
echo ""

# Step 0: Check if raw feed data exists; offer to fetch if not
RAW_TODAY="$RAW_DIR/$DATE_STEM"
if [[ ! -d "$RAW_TODAY" || -z "$(ls -A "$RAW_TODAY" 2>/dev/null | grep -v '.gitkeep')" ]]; then
    echo "[WARN] No raw feed data found at $RAW_TODAY"
    if [[ -z "$DRY_RUN" && -z "$PASTE_ARG" ]]; then
        echo "[INFO] Running feed ingest first..."
        PYTHONPATH="$REPO_ROOT" python3 "$FETCH" || echo "[WARN] Feed ingest returned non-zero; continuing..."
    fi
fi

# Step 1: Run each layer
PASS=0
FAIL=0
SKIP=0

for layer in "${SELECTED_LAYERS[@]}"; do
    echo ""
    echo "--- Layer: $layer ---"

    CMD=(python3 "$RUNNER" --prompt-id "$layer" --output-stem "$DATE_STEM")
    [[ -n "$DRY_RUN" ]] && CMD+=($DRY_RUN)
    [[ -n "$PASTE_ARG" ]] && CMD+=($PASTE_ARG)

    PYTHONPATH="$REPO_ROOT" "${CMD[@]}" && {
        echo "[OK] $layer completed"
        ((PASS++))
    } || {
        echo "[FAIL] $layer failed (exit $?)"
        ((FAIL++))
    }
done

echo ""
echo "=== Pipeline Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Total:  ${#SELECTED_LAYERS[@]}"

if [[ $FAIL -gt 0 ]]; then
    echo "[WARN] $FAIL layer(s) failed. Check output above."
    exit 1
fi

echo "[OK] All layers completed successfully."
