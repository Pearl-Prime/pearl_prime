#!/usr/bin/env bash
# orchestrate_ja_jp_stillness_full_render.sh — top-level Pearl Star autonomous orchestrator.
#
# Chains Phase 0 (ja_JP source gen) → Phase 1 (smoke + auto-validate) → Phase 2 (bulk).
# Hourly: refresh + sync the operator dashboard to R2.
#
# Designed to run on Pearl Star in nohup mode (tmux is not installed and sudo
# is gated; use `nohup … & disown` from the operator's SSH session, then close
# the laptop — see docs/runbooks/JA_JP_STILLNESS_PEARL_STAR_BULK_RUNBOOK.md).
#
# Resumable: each phase has a sentinel under artifacts/manga/sentinels/; a
# re-invocation skips already-completed phases. Inside Phase 2, sentinels are
# per-chapter, so a mid-bulk interruption only re-runs the in-flight chapter.

set -uo pipefail  # NOT -e — phase wrappers handle their own failure paths.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

LOG_DIR="$REPO_ROOT/artifacts/manga/bulk_logs"
mkdir -p "$LOG_DIR"

SENTINEL_DIR="$REPO_ROOT/artifacts/manga/sentinels"
mkdir -p "$SENTINEL_DIR"

# Load Keychain env on Pearl Star — actually only meaningful on the operator's
# laptop. On Pearl Star the env should come from ~/.config/rclone + ~/.config/gh.
# We try the loader but ignore failures.
if [ -f "$REPO_ROOT/scripts/ci/load_integration_env_from_keychain.py" ]; then
    if command -v security >/dev/null 2>&1; then
        eval "$(python3 "$REPO_ROOT/scripts/ci/load_integration_env_from_keychain.py" 2>/dev/null)" || true
    fi
fi

# Make user-local installed tools (gh, rclone) on Pearl Star visible.
export PATH="$HOME/.local/bin:$PATH"

# Defaults — overridable via env at the `nohup ... &` invocation.
SERIES="${SERIES:-stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying}"
SKIP_R2="${SKIP_R2:-0}"
SKIP_COMMIT="${SKIP_COMMIT:-0}"
DRY_RUN="${DRY_RUN:-0}"
DASHBOARD_INTERVAL_SECONDS="${DASHBOARD_INTERVAL_SECONDS:-3600}"

# Translation model — Pearl Star Ollama defaults to qwen2.5:7b which is NOT
# loaded. The actually-loaded model is qwen2.5:14b. Default here so Phase 0
# actually translates instead of silently failing with HTTP 404.
export QWEN_MODEL="${QWEN_MODEL:-qwen2.5:14b}"

phase_log() {
    local phase="$1"
    echo "=========================================="
    echo "=== $phase @ $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
    echo "=========================================="
}

run_phase0() {
    phase_log "PHASE 0 — ja_JP source translation"
    local args=()
    [ "$DRY_RUN" = "1" ] && args+=(--dry-run)
    python3 scripts/manga/ja_jp_phase0_source_gen.py "${args[@]}"
}

run_phase1() {
    phase_log "PHASE 1 — smoke render + auto-validate"
    local args=()
    [ "$DRY_RUN" = "1" ] && args+=(--dry-run)
    [ "$SKIP_R2" = "1" ] && args+=(--skip-r2)
    [ "$SKIP_COMMIT" = "1" ] && args+=(--skip-commit)
    args+=(--series "$SERIES")
    python3 scripts/manga/ja_jp_phase1_smoke.py "${args[@]}"
}

run_phase2() {
    phase_log "PHASE 2 — bulk render"
    local args=()
    [ "$DRY_RUN" = "1" ] && args+=(--dry-run)
    [ "$SKIP_R2" = "1" ] && args+=(--skip-r2)
    [ "$SKIP_COMMIT" = "1" ] && args+=(--skip-commit)
    python3 scripts/manga/ja_jp_phase2_bulk.py "${args[@]}"
}

refresh_dashboard() {
    local args=()
    [ "$SKIP_R2" = "1" ] && args+=(--no-upload)
    python3 scripts/manga/bulk_status_dashboard.py "${args[@]}" 2>&1 | sed 's/^/  [dashboard] /'
}

dashboard_loop() {
    # Background loop — refreshes the dashboard every $DASHBOARD_INTERVAL_SECONDS.
    while true; do
        refresh_dashboard || true
        sleep "$DASHBOARD_INTERVAL_SECONDS"
    done
}

# Start the dashboard background loop (only if R2 sync is wanted).
if [ "$SKIP_R2" != "1" ]; then
    dashboard_loop &
    DASH_PID=$!
    trap 'kill $DASH_PID 2>/dev/null; wait $DASH_PID 2>/dev/null' EXIT
fi

# --- PHASE 0 ---
P0_SENTINEL="$SENTINEL_DIR/ja_jp_phase0_complete.flag"
if [ -f "$P0_SENTINEL" ]; then
    echo "[$(date -u +%H:%M:%S)] Phase 0 sentinel exists; skipping."
else
    run_phase0 || { echo "Phase 0 FAILED; orchestrator halting."; exit 1; }
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$P0_SENTINEL"
fi

# --- PHASE 1 ---
SMOKE_OK="$SENTINEL_DIR/SMOKE_OK_ja_jp_stillness.flag"
SMOKE_FAIL="$SENTINEL_DIR/SMOKE_FAILED.flag"
if [ -f "$SMOKE_OK" ]; then
    echo "[$(date -u +%H:%M:%S)] Smoke already validated; skipping Phase 1."
elif [ -f "$SMOKE_FAIL" ]; then
    echo "[$(date -u +%H:%M:%S)] Smoke FAILED previously; manual review required. Exiting."
    refresh_dashboard
    exit 1
else
    run_phase1
    P1_RC=$?
    if [ $P1_RC -ne 0 ]; then
        echo "Phase 1 smoke FAILED (rc=$P1_RC); orchestrator halting (sentinel left for operator)."
        refresh_dashboard
        exit 1
    fi
fi

# --- PHASE 2 ---
BULK_COMPLETE="$SENTINEL_DIR/BULK_COMPLETE_ja_jp_stillness.flag"
if [ -f "$BULK_COMPLETE" ]; then
    echo "[$(date -u +%H:%M:%S)] Bulk already complete; skipping Phase 2."
else
    run_phase2 || { echo "Phase 2 FAILED; orchestrator halting (per-chapter sentinels preserved)."; refresh_dashboard; exit 1; }
fi

# --- PHASE 3 — book assembler (cover + scroll + PDF + R2 sync per series) ---
echo "=========================================="
echo "=== PHASE 3 — book assembly @ $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "=========================================="
P3_ARGS=()
[ "$SKIP_R2" = "1" ] && P3_ARGS+=(--skip-r2)
python3 scripts/manga/ja_jp_phase3_assemble.py "${P3_ARGS[@]}" || echo "Phase 3 returned non-zero (per-series BOOK_COMPLETE sentinels preserved)"

refresh_dashboard
echo "=========================================="
echo "=== ORCHESTRATOR COMPLETE @ $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "=========================================="
