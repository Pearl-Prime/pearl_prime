# Stillness ep_001 — honest post-merge bank-assembly packet

**Date:** 2026-07-11  
**Workstream:** `ws_stillness_gap_rerender_and_honest_packet_20260711`  
**Proof kind:** bank assembly via `assemble_from_bank.py` (NOT `composed_v4_qwen`)  
**Acceptance layer:** EXECUTED-REAL (byte-verified 35-panel bank path + blob-gate PASS gap L2s). Not PROVEN-AT-BAR.

## Paths

- Assembly: `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/ep_001_from_continuity_final`
- Manifest: `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml`
- Gaps: `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_bank_gaps.json` (panels_complete=35/35, layers_missing=0)
- Reader: `index.html`

## Gap L2 rerender evidence

Pearl Star jobs 589–592 (`t2i_qwen_image`, white-backdrop cutout prompts) → rembg `isnet-general-use` → `bank_layer_blob_gate` PASS.


| Asset | bytes | blob-gate | small_edge |
|-------|------:|-----------|------------|
| L2_clean_bust_calm_v2_alpha.png | 1345063 | PASS | 8.78 |
| L2_hands_wrapping_cup_clean_v2_alpha.png | 2341149 | PASS | 10.27 |
| L2_seated_kitchen_knees_up_v1_alpha.png | 1410848 | PASS | 11.64 |
| L2_full_figure_kitchen_standing_v1_alpha.png | 738380 | PASS | 8.10 |


## Room-capable bindings

- `ep001_008` → `L2_seated_kitchen_knees_up_v1_alpha.png` (room_capable: true)
- `ep001_013` → `L2_full_figure_kitchen_standing_v1_alpha.png` (room_capable: true)

## Verification

- Panel count: 35 / 35 real PNG >50KB
- Chapter grammar / HR-U16: PASS (no FAIL findings)
- HTML reader resolves `panels/*.png`, contact sheet, room proof
