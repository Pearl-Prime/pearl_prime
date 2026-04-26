#!/usr/bin/env bash
# US Manga Lead-Series Rollout — 13 brands × 1 lead pick each
# Generated: 2026-04-23
#
# Each block runs ONE brand's lead manga through the full pipeline:
#   1. Image bank gate check (must have N panel PNGs at image_bank/{brand}/{topic}/)
#   2. run_manga_pipeline → script + render via Pearl Star (Ollama)
#   3. R2 upload to {brand}/manga/{date}/
#   4. Brand digest fragment for brand_admin handoff
#
# PRECONDITIONS — fail fast if any of these are not green:
#   • Pearl Star online: curl -s http://pearlstar.local:11434/api/tags > /dev/null
#   • Ollama models loaded: gemma3:27b for English, qwen3:32b for CJK6
#   • Image banks populated: see panel-count column in PITCHES.md
#   • R2 credentials in env: R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
#   • LLM tier policy: NO paid LLM API keys in env (script enforces)
#
# USAGE:
#   ./ROLLOUT_COMMANDS.sh                    # dry-run all 13 (default safe mode)
#   ./ROLLOUT_COMMANDS.sh --execute          # actually run them
#   ./ROLLOUT_COMMANDS.sh --brand stillness_press --execute   # one brand

set -euo pipefail

cd "$(dirname "$0")/../.."   # repo root

DRY_RUN="--dry-run"
ONLY_BRAND=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute) DRY_RUN="" ; shift ;;
    --brand) ONLY_BRAND="$2" ; shift 2 ;;
    *) echo "unknown arg: $1" ; exit 2 ;;
  esac
done

# ── Preflight ──
echo "── Preflight ──"
if ! curl -sf -m 3 http://pearlstar.local:11434/api/tags > /dev/null 2>&1; then
  if ! curl -sf -m 3 http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "ERROR: Pearl Star (Ollama) is not reachable on pearlstar.local:11434 or localhost:11434"
    echo "       Start Ollama on Pearl Star or override with PEARLSTAR_URL env var, then re-run."
    [[ -z "$DRY_RUN" ]] && exit 1
    echo "       (continuing in dry-run mode — commands will be printed but not executed)"
  fi
fi

if [[ -n "${ANTHROPIC_API_KEY:-}${OPENAI_API_KEY:-}${DASHSCOPE_API_KEY:-}" ]]; then
  echo "ERROR: paid LLM API key set in env. Manga lane is Tier 2 — Pearl Star only."
  echo "       Unset these before running."
  exit 1
fi

DATE=$(date +%Y-%m-%d)
mkdir -p "artifacts/manga_us_lead_picks/runs/${DATE}"
RUNLOG="artifacts/manga_us_lead_picks/runs/${DATE}/runlog.txt"
: > "$RUNLOG"
echo "Run log: $RUNLOG"
echo

# ── 13 lead picks · brand,topic_id,genre,demo ──
# topic_id is what run_manga_pipeline expects — pull from each series's brand profile
read -r -d '' PICKS <<'EOF' || true
body_memory|grief|josei|josei
bright_presence_tw|nondual|seinen|seinen
cognitive_clarity|attention|shonen|shonen
devotion_path|opening|shonen|shonen
digital_ground|voice|shojo|shojo
heart_balance|catharsis|josei|josei
qi_foundation|cultivation|seinen|seinen
relational_calm|belonging|josei|josei
sleep_restoration|night_healing|josei|josei
solar_return|fire|shonen|shonen
somatic_wisdom|grief|josei|josei
stillness_press|anxiety_overwhelm|josei|josei
warrior_calm|cultivation|shonen|shonen
EOF

# ── Run each pick ──
i=0
while IFS='|' read -r BRAND TOPIC GENRE DEMO; do
  [[ -z "$BRAND" ]] && continue
  i=$((i+1))
  if [[ -n "$ONLY_BRAND" && "$BRAND" != "$ONLY_BRAND" ]]; then continue; fi

  BANK_DIR="image_bank/${BRAND}/${TOPIC}"
  N_PNG=0
  if [[ -d "$BANK_DIR" ]]; then
    N_PNG=$(find "$BANK_DIR" -maxdepth 1 -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
  fi

  echo "── [${i}/13] ${BRAND} | ${TOPIC} | ${GENRE} ──"
  echo "    image bank: ${BANK_DIR} (${N_PNG} PNGs)"

  if [[ "$N_PNG" -lt 8 ]]; then
    echo "    SKIP — image bank has fewer than 8 PNGs (gate threshold). Populate first via:"
    echo "    PYTHONPATH=. python3 scripts/image_generation/manga_teacher_batch.py \\"
    echo "      --brand ${BRAND} --topic ${TOPIC} --count 12"
    echo "" | tee -a "$RUNLOG"
    continue
  fi

  CMD="PYTHONPATH=. python3 scripts/run_manga_pipeline.py \\
      --brand ${BRAND} \\
      --topic ${TOPIC} \\
      --genre ${GENRE} \\
      --persona gen_z_professionals \\
      --render-book \\
      --output-dir artifacts/manga_us_lead_picks/runs/${DATE}/${BRAND} \\
      ${DRY_RUN}"

  echo "    CMD: ${CMD}" | tee -a "$RUNLOG"
  if [[ -z "$DRY_RUN" ]]; then
    eval "$CMD" 2>&1 | tee -a "$RUNLOG"

    # R2 upload
    PYTHONPATH=. python3 -c "
from scripts.manga.r2_manga_release import upload_manga_release_dir
upload_manga_release_dir('artifacts/manga_us_lead_picks/runs/${DATE}/${BRAND}', '${BRAND}/manga/${DATE}/')
" 2>&1 | tee -a "$RUNLOG"
  fi
  echo
done <<< "$PICKS"

echo "── Done ──"
echo "Mode: $([[ -z "$DRY_RUN" ]] && echo EXECUTE || echo DRY-RUN)"
echo "Log:  $RUNLOG"
