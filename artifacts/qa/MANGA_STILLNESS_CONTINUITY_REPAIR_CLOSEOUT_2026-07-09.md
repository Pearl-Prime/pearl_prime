# Stillness Continuity Repair — Closeout (2026-07-09)

**Taxonomy:** EXECUTED-REAL (35/35 assembly under HR-U16 + room-capable L2)  
**Lane:** Pearl_Dev stillness continuity repair  
**Acceptance layer:** EXECUTED-REAL — byte-verified assembly; not PROVEN-AT-BAR

## Problem

`ep_001_from_continuity.yaml` regenerated 35/35 but `assemble_from_bank.load_manifest` fail-closed on **HR-U16**: panels ep001_008–012 exceeded 6 consecutive abstract panels without `re_establish` on `full_render`/`partial_motif`. Room-capable gap renders (`L2_seated_kitchen_knees_up_v1`, `L2_full_figure_kitchen_standing_v1`) were on disk but not selected in the manifest.

## Fix seam (lowest truthful)

| Layer | Change |
|---|---|
| `scripts/manga/generate_assembly_manifest.py` | `_enforce_hr_u16_re_establish` patches first failure per abstract run → `re_establish` on kitchen L0 + seated knees-up L2; `_maybe_override_room_l2` / `_maybe_add_room_l2_on_establishing` wire full-figure L2 on kitchen establishing; insert/abstract L2 pool uses gap-render clean assets |
| L2 composition sidecars | Added `anchor` + `eye_y_px` to gap room-capable L2 sidecars (required for G3 horizon paste) |
| Manifest | `ep001_008` → `re_establish` / `shared_meal_table_medium` / `L2_seated_kitchen_knees_up_v1`; `ep001_013` → `L2_full_figure_kitchen_standing_v1` |

## Commands (verified)

```bash
PYTHONPATH=. python3 scripts/manga/generate_assembly_manifest.py \
  --series stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --profile stillness_en_01 \
  --episode ep_001 \
  --out artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml

PYTHONPATH=. python3 scripts/manga/validate_chapter_composition_grammar.py \
  artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml
# PASS

PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
  --manifest artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml \
  --out-dir artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/ep_001_from_continuity_final
# 35/35 PNGs
```

## HR-U16 outcome

| Panel | Before | After |
|---|---|---|
| ep001_008 | insert_object (abstract streak 7) | **re_establish** + kitchen L0 + `L2_seated_kitchen_knees_up_v1` |
| ep001_009–012 | HR-U16 FAIL | PASS (streak reset) |

Gate report ep001_008: G1/G2/G3/G4/G5 PASS, ops `G3_horizon_scale`, `G4_contact_shadow_under_L2`, `G5_occluder_BOOK`.

## Room-capable assets wired

| Asset | crop | Wired panel | bytes |
|---|---|---|---|
| `L2_seated_kitchen_knees_up_v1` | knees_up | ep001_008 re_establish | 1,270,030 |
| `L2_full_figure_kitchen_standing_v1` | full_figure | ep001_013 establishing | 1,245,446 |

Proof grid: `artifacts/qa/manga_room_capable_gap_review_2026-07-09.png`

## PROVENANCE

```
research:  artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md; artifacts/qa/MANGA_STILLNESS_GAP_RENDER_CLOSEOUT_2026-07-09.md
documents: docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md; manga_human_readability_rules_2026-07-09.json
builds_on: generate_assembly_manifest.generate; validate_chapter_composition_grammar; assemble_from_bank.load_manifest
inventory: EXTENDS generate_assembly_manifest (HR-U16 + room L2 selection); EXTENDS gap L2 sidecars (anchor metadata); UNCHANGED HR-U16 threshold
```

## Machine-readable tags

```
manga-stillness-continuity-fix=completed
manga-stillness-continuity-closeout=artifacts/qa/MANGA_STILLNESS_CONTINUITY_REPAIR_CLOSEOUT_2026-07-09.md
manga-stillness-continuity-manifest=artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml
manga-stillness-continuity-assembly=artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/ep_001_from_continuity_final
manga-stillness-room-assets-wired=L2_seated_kitchen_knees_up_v1@ep001_008,L2_full_figure_kitchen_standing_v1@ep001_013
manga-stillness-hr-u16=fixed
manga-stillness-continuity-next-action=Blind-judge room-capable panels; dispatch mecha/thriller gap renders (out of scope)
manga-stillness-continuity-blocker=none
```
