# Manga G1 Fix — Stillness demo_alarm_metaphor_6p (2026-07-08)

## Root cause

`demo_alarm_metaphor_6p_REAL_pilot.yaml` was hand-authored without the G1-aware L0 derivations that `generate_assembly_manifest.py` auto-emits for `ep_001_from_continuity.yaml`.

| panel | L2 sidecar `crop_class` | L0 sidecar `bg_class` | archetype | missing |
|-------|-------------------------|----------------------|-----------|---------|
| demo_p2_alarm_gaze | `waist_up` | `full_render` | character_quiet_face | `shot_type: reaction_emotion`, L0 `derivation: defocus` |
| demo_p4_watching_kettle | `waist_up` | `full_render` | shared_scene_medium | L0 `derivation: defocus` |
| demo_p5_noticing | `bust` | `full_render` | character_quiet_face | `shot_type: reaction_emotion`, L0 `derivation: defocus` |
| demo_p6_resolution | `bust` | `full_render` | character_at_table_medium | L0 `derivation: defocus` |

G1 matrix: `waist_up × full_render` and `bust × full_render` are **ILLEGAL** unless L0 is derived to `defocus_derived` (manifest `derivation.type: defocus`).

First failure observed: `demo_p2_alarm_gaze` — `ValueError: G1: waist_up × full_render is ILLEGAL (no diegetic pair)`.

## Fix

Smallest manifest-only fix — mirror `ep_001_from_continuity` patterns (no grammar rule or sidecar edits):

- Added `shot_type: reaction_emotion` + L0 `derivation: {type: defocus}` on `character_quiet_face` panels (p2, p5).
- Added L0 `derivation: {type: defocus}` (+ `shot_type: establishing` where applicable) on p4, p6.

File: `artifacts/manga/.../assembly_manifests/demo_alarm_metaphor_6p_REAL_pilot.yaml`

Test: `scripts/manga/tests/test_assemble_from_bank.py::test_demo_real_pilot_manifest_g1_legal`

## Rerun results

### demo_alarm_metaphor_6p_REAL_pilot → `assembled/demo_alarm_metaphor_6p_real/`

**CLEAN** — 6/6 panels, all grammar gates PASS.

```
demo_p1_therapist_memory.png  2,247,375 B
demo_p2_alarm_gaze.png        1,328,711 B  (G1 PASS: waist_up × defocus_derived)
demo_p3_kettle_macro.png      2,046,392 B
demo_p4_watching_kettle.png   1,448,542 B  (G1 PASS: waist_up × defocus_derived)
demo_p5_noticing.png          1,192,389 B  (G1 PASS: bust × defocus_derived)
demo_p6_resolution.png        1,246,375 B  (G1 PASS: bust × defocus_derived)
```

Log: `artifacts/qa/manga_g1_fix_demo_assembly_2026-07-08.log`  
Gate report: `assembled/demo_alarm_metaphor_6p_real/gate_report.json`

### ep_001_from_continuity (unchanged manifest)

**CLEAN** — 35/35 panels assembled to `/tmp/ep_001_g1_verify/` (repo disk full at 131 MiB free; prior in-repo run also blocked on disk, not G1).  
0 grammar gate failures in `gate_report.json`.

**Next blocker (byte gate, not G1):** `ep001_029` = **12,741 B** (`long_drop_decompression` / `tone_gradient` — no L2 layer; below 50 KB stub-as-done floor per M6-BLK-005).

## Machine summary

```
manga-g1-fix=<commit-sha>
manga-ep001-assembly=clean
manga-g1-evidence=artifacts/qa/manga_g1_fix_stillness_2026-07-08.md
manga-g1-next-action=Re-render ep001_029 long_drop panel above 50KB byte floor (M6-BLK-005)
manga-g1-blocker=none (G1); ep001_029 byte gate is next production blocker
```
