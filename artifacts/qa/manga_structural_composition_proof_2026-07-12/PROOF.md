# Structural Composition MVP — EXECUTED-REAL proof packet

**Date:** 2026-07-12  
**Branch:** `agent/manga-structural-composition-mvp`  
**Proof root:** `artifacts/qa/manga_structural_composition_proof_2026-07-12/`  
**Acceptance layer:** **EXECUTED-REAL** (byte-verified real bank / assembled panels + support overlays from shared resolved transform path)  
**Not claimed:** PROVEN-AT-BAR · 100% · lettering v2 on assembler · assembler `--structural-plan` consume

---

## What this proves

| Run | Template | Real asset(s) | Result |
|-----|----------|---------------|--------|
| `seated_table_stillness_ep001_016` | `seated_table_scene` | stillness assembled `ep001_016.png` (2,633,608 B) | PASS + overlay |
| `standing_room_stillness_ep001_013` | `standing_room_scene` | stillness assembled `ep001_013.png` (2,125,334 B) | PASS + overlay |
| `seated_table_mecha_cockpit` | `seated_table_scene` | mecha bank `L0_cockpit_interior` + `L2_seated_cockpit` | PASS + overlay |
| `standing_room_mecha_threshold` | `standing_room_scene` | mecha bank `L0_hangar_pre_dawn` + `L2_threshold_stand` | PASS + overlay |
| `floating_control_stillness_ep001_008` | `seated_table_scene` | stillness `ep001_008.png` (floating checklist case) | **CONTACT_FAIL** (expected) |

Machine summary: `PROOF_SUMMARY.json`  
Asset digests: `asset_fingerprints/ASSET_FINGERPRINTS.json`

All PASS overlays assert `same_resolved_transform_path: true` (contact validation and overlay share `ResolvedTransform` from the plan envelope).

---

## Honesty notes

1. **Sparse worktree:** `artifacts/manga/.../v4_render_cache` L2 sources are declared in the stillness panel manifest but are **not checked out** here. Proof uses **materialized LFS** assembled panels under `artifacts/qa/.../stillness_ep001_postmerge_honest/panels/` and mecha bank layers under `.../mecha_layered_packet_v1/bank/`.
2. **Assembler `--structural-plan`:** **EXPLICITLY DEFERRED** this lane. Plans/overlays were produced via `plan_panel_layout.py` + `validate_scene_assembly_visual.py`, not by rewiring `assemble_from_bank.py`.
3. **Lettering:** assembler remains on `bubble_render` v1 — unchanged.
4. **Horizon law:** universal horizon-ratio G3 **not** re-canonized.
5. **ep001_016 panel-type vs structural template:** archetype `sparse_establishing_wide` bridges to standing in config; this proof uses `seated_table_scene` because the accepted panel shows a **tiny seated figure** with seat/table contact (checklist). Bridge taxonomy is not collapsed.
6. **Not PROVEN-AT-BAR.**

---

## Reproduce

```bash
# Materialize LFS bank/panel bytes if still pointers:
git lfs checkout -- \
  artifacts/qa/manga_reading_packets_2026-07-10/mecha_layered_packet_v1/bank/*.png \
  artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/panels/ep001_008.png \
  artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/panels/ep001_013.png \
  artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/panels/ep001_016.png

PYTHONPATH=scripts/manga python3 scripts/manga/plan_panel_layout.py \
  --bundle artifacts/qa/manga_structural_composition_proof_2026-07-12/bundles/seated_table_stillness_ep001_016_bundle.json \
  --emit-overlay \
  --candidate-root /tmp/structural_proof_seated
```

---

## Deferred / remaining

- Optional assembler `--structural-plan` consume path (left deferred).
- Push/PR of structural branch (see closeout for exact remote status).
- Blind / PROVEN-AT-BAR (out of scope).
