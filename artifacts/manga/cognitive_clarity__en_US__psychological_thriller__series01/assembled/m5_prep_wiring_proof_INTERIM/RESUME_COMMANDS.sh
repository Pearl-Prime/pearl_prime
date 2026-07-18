#!/usr/bin/env bash
# M5-prep Pearl Star resume — cognitive_clarity__en_US__psychological_thriller__series01
# WIRING PROOF used INTERIM stand-ins. This script enqueues REAL bank layers.
#
# GPU envelope: Q-MANGA-03 / OPD-20260704-007 — LOW priority, ~2–4 GPU-h pilot.
# This series estimate: ~6 images × ~20s ≈ 0.03 GPU-h (within envelope if
# batched with other pilots under the 2–4h cap; CJK atom lane always preempts).
#
# RAP: queue-first via pscli. Never call ComfyUI directly.
# Pearl Star was UNREACHABLE at M5-prep authoring (no pscli / box down).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "Preflight: Pearl Star queue must be RUNNING"
# ssh ahjan108@100.92.68.74 '… pscli status'   # enable when box is up

BANK="artifacts/manga/cognitive_clarity__en_US__psychological_thriller__series01/image_bank"
mkdir -p "$BANK/L0" "$BANK/L2" "$BANK/L3"

# Example enqueue (1 image per job — RAP). Expand from bank_contracts/*.yaml.
# PYTHONPATH=. python3 -c "
# from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job
# enqueue_panel_job(task='t2i_qwen_image', prompt='<from scene_inventory>',
#                   width=1080, height=1920, priority='LOW',
#                   out_path='$BANK/L0/<scene_id>.png')
# "

echo "After REAL layers land: re-run assemble_from_bank.py with provenance: REAL"
echo "  PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \\
echo "    --manifest artifacts/manga/cognitive_clarity__en_US__psychological_thriller__series01/assembly_manifests/<real_manifest>.yaml \\
echo "    --out-dir artifacts/manga/cognitive_clarity__en_US__psychological_thriller__series01/assembled/<real_name>/ --strip --bubbles"
