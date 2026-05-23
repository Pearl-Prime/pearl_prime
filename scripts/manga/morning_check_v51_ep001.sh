#!/usr/bin/env bash
#
# Morning check for V5.1 ep_001 overnight dispatch on Pearl Star.
# Per OPD-141 operator review protocol (2026-05-22):
#   1. rsync results from Pearl Star → local Mac
#   2. count composites + identify any failures from the run log
#   3. run validator suite, get class-A failure distribution
#   4. if <5 panels failed validators → open Finder for §11 visual review
#   5. if ≥5 panels failed → surface the failure distribution BEFORE opening images
#      so operator sees the pattern before doing per-panel review
#
# Run from the repo root on the operator's Mac after waking up:
#   bash scripts/manga/morning_check_v51_ep001.sh
#
# Exit codes:
#   0  — ≥31/35 composites + <5 validator failures (ready for §11 review)
#   1  — <31/35 composites OR ≥5 validator failures (triage before review)
#   2  — dispatch not finished yet (compute still running on Pearl Star)
#
# Per V5.1 catalog rollout plan §Milestone-A acceptance gate + operator 4-question
# review criteria (2026-05-22):
#   - Are ≥31/35 composites visually shippable?  (operator visual)
#   - Does Mira read as the same character across all 35 panels?  (operator visual)
#   - Does the iyashikei aesthetic hold (negative space, palette, emotional register)?  (operator visual)
#   - Are the 4-5 architectural gap panels (ELS + pet) clearly explainable gaps rather
#     than pipeline failures?  (operator visual — script flags those panels explicitly)

set -uo pipefail  # NOT -e: we want to report failures, not bail on them

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
cd "$REPO_ROOT" || exit 1

SERIES="stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
EP="ep_001"
LOCAL_COMPOSED="artifacts/manga/${SERIES}/composed_v51_qwen/${EP}"
LOCAL_LAYERS="artifacts/manga/${SERIES}/panels_v51_2stage/${EP}"
PS_HOST="pearl_star"
PS_ROOT="~/v51_dispatch"

echo "═══════════════════════════════════════════════════════════════════"
echo "  V5.1 ep_001 morning check — $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# 1. Check Pearl Star dispatch state
echo "→ Step 1: Pearl Star dispatch state"
DRIVER_STATUS=$(ssh -o ConnectTimeout=10 "$PS_HOST" "pgrep -af 'dispatch.py' | head -2" 2>&1)
if echo "$DRIVER_STATUS" | grep -q 'dispatch.py'; then
    echo "  ⚠  Dispatch driver STILL RUNNING:"
    echo "$DRIVER_STATUS" | sed 's/^/    /'
    REMOTE_DONE=$(ssh "$PS_HOST" "ls $PS_ROOT/composed/ 2>/dev/null | wc -l" 2>/dev/null)
    echo "  ⚠  Composites on Pearl Star so far: ${REMOTE_DONE}/35"
    echo ""
    echo "  Dispatch not yet finished. Wait for completion or check progress with:"
    echo "    ssh $PS_HOST 'tail -10 ~/v51_dispatch/_run_log.txt'"
    exit 2
fi
echo "  ✓ dispatch driver no longer running on Pearl Star (run complete)"
echo ""

# 2. Rsync results from Pearl Star
echo "→ Step 2: rsync composites + per-panel layers from Pearl Star"
mkdir -p "$LOCAL_COMPOSED" "$LOCAL_LAYERS"
rsync -avq pearl_star:~/v51_dispatch/composed/ "$LOCAL_COMPOSED/" 2>&1 | tail -3
rsync -avq pearl_star:~/v51_dispatch/outputs/ "$LOCAL_LAYERS/" 2>&1 | tail -3
ssh "$PS_HOST" "cat ~/v51_dispatch/_run_summary.json 2>/dev/null" > "$LOCAL_LAYERS/_run_summary.json"
echo "  ✓ rsync complete"
echo ""

# 3. Count composites
N_COMPOSITES=$(ls "$LOCAL_COMPOSED"/*.png 2>/dev/null | wc -l | tr -d ' ')
echo "→ Step 3: composite count"
echo "  composites on disk: $N_COMPOSITES / 35"
if [ "$N_COMPOSITES" -lt 31 ]; then
    echo "  ✗ Below §11 acceptance threshold of ≥31/35"
    SHIP_GATE_FAIL=1
else
    echo "  ✓ Meets count threshold (≥31/35 needed for §11)"
fi
echo ""

# 4. Identify panels that failed from run summary
echo "→ Step 4: panels that failed dispatch (from Pearl Star run summary)"
if [ -f "$LOCAL_LAYERS/_run_summary.json" ]; then
    python3 -c "
import json, sys
try:
    d = json.load(open('$LOCAL_LAYERS/_run_summary.json'))
    fails = [p for p in d.get('panels', []) if p.get('outcome') == 'fail']
    if fails:
        print(f'  ✗ {len(fails)} panels failed dispatch:')
        for f in fails:
            print(f\"    - {f['panel_id']}: {f.get('reason','?')}\")
    else:
        print('  ✓ 0 dispatch failures')
except Exception as e:
    print(f'  (could not parse run_summary: {e})')
"
else
    echo "  (run_summary.json not yet on Pearl Star; skipping)"
fi
echo ""

# 5. Validator suite — V4 class-A gates on each composite
echo "→ Step 5: validator suite (V4 class-A gates per panel)"
PYTHONPATH=. python3 - <<'PYEOF'
import json
import sys
from pathlib import Path
sys.path.insert(0, "scripts/manga")
try:
    import render_v4_episode as v4
    import render_v5_episode as v5
    import validate_layer as vl
except Exception as e:
    print(f"  could not import validator: {e}")
    sys.exit(0)

REPO = Path.cwd()
SERIES = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
EP = "ep_001"
composed = REPO / f"artifacts/manga/{SERIES}/composed_v51_qwen/{EP}"
configs = v4.load_configs("stillness_en_01")
panel_states = v4.load_panel_states(SERIES, EP)
state_by_id = {p["panel_id"]: p for p in panel_states}

results = []
for png in sorted(composed.glob("*.png")):
    pid = png.stem
    panel = state_by_id.get(pid)
    if not panel:
        results.append((pid, "?", "no_continuity_state", []))
        continue
    try:
        bundle, layer_type, sz, arch_ctx = v5.compile_v5_full_panel_prompt(panel, configs)
        arch_meta = (configs["panel_templates"].get("archetypes", {}) or {}).get(panel.get("archetype"), {}) or {}
        # validate_composite is in render_v5_episode.py; use it via the layer file
        # Quick path: instantiate LayerValidationInput
        vi = vl.LayerValidationInput(
            image_path=png,
            layer_type=layer_type,
            safe_zone_row=sz,
            archetype_ctx=arch_ctx,
            archetype_meta=arch_meta,
        )
        report = vl.validate_layer(vi)
        class_a_fails = [r["check_id"] for r in report
                        if (r.get("severity") == "FAIL" and not r.get("passed") and not r.get("skipped"))]
        results.append((pid, panel.get("archetype"), "OK" if not class_a_fails else "FAIL", class_a_fails))
    except Exception as e:
        results.append((pid, panel.get("archetype"), f"ERR: {e}", []))

print(f"  validated {len(results)} composites")
fails = [r for r in results if r[2] != "OK"]
if not fails:
    print("  ✓ 0 class-A failures across all composites")
else:
    print(f"  ✗ {len(fails)} composites failed class-A gates:")
    by_check = {}
    for pid, arch, status, checks in fails:
        print(f"    - {pid} ({arch}): {status} {checks}")
        for c in checks:
            by_check[c] = by_check.get(c, 0) + 1
    if by_check:
        print(f"\n  Failure distribution by check:")
        for c, n in sorted(by_check.items(), key=lambda x: -x[1]):
            print(f"    {n:>3} × {c}")
    # Exit nonzero if ≥5 failures (operator's diagnostic threshold)
    if len(fails) >= 5:
        sys.exit(2)
PYEOF
VAL_EXIT=$?
echo ""

# 6. Operator's 4-question §11 review criteria
echo "→ Step 6: §11 review checklist (operator visual)"
cat <<'CHECKLIST'
  When you open the Finder window:
    ☐ 1. Are ≥31/35 composites visually shippable?
    ☐ 2. Does Mira read as the same character across all 35 panels?
    ☐ 3. Does the iyashikei aesthetic hold (negative space, palette, emotional register)?
    ☐ 4. Are the 4-5 architectural gap panels (ELS + pet) clearly explainable gaps
         rather than pipeline failures?

  If yes to all four → accept; trigger Milestone C Step 0 (extract beatsheet
  from ep_001's 35 YAMLs before generator code).

  If anything looks wrong → note panel + archetype; triage before proceeding.
CHECKLIST
echo ""

# 7. Open Finder if pass; otherwise warn first
if [ "${SHIP_GATE_FAIL:-0}" = "1" ] || [ "$VAL_EXIT" = "2" ]; then
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  ⚠  TRIAGE NEEDED before §11 review."
    echo "  See above:  composite count = $N_COMPOSITES/35  |  validator exit = $VAL_EXIT"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "  Opening Finder anyway so you can see what landed, but read the"
    echo "  failure distribution above FIRST before forming a visual verdict."
    open "$LOCAL_COMPOSED/"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════════"
echo "  ✓ Dispatch complete, count OK, validators OK."
echo "  Opening Finder for §11 review."
echo "═══════════════════════════════════════════════════════════════════"
open "$LOCAL_COMPOSED/"
exit 0
