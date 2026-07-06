# Composition Grammar Pilot — Findings (2026-07-07)

**Branch:** `agent/manga-composition-pilot-20260707`  
**Spec authority:** PR #4688 / `MANGA_COMPOSITION_GRAMMAR_SPEC.md` v1.0.0  
**Layer reached:** EXECUTED-REAL (byte-verified pilot outputs; not PROVEN-AT-BAR)

## What worked

1. **G1 legality matrix is implementable as pure lookups.** The control panel (`waist_up × full_render`) deterministically FAILs G1; the grammar strip routes waist-up to `defocus_derived` instead — the exact fix the spec predicts for the "floating half-person" defect.

2. **G3 horizon-ratio scaling runs on real April assets** with hand-annotated `composition_meta` (~3 sidecars, ~1–2 min/asset). P1 (`establishing`) places `L2_3210c57437fb` (thigh_up, diegetic pair) at the `seat_at_table` anchor with figure height within ±15% of `expected_figure_h_pct`.

3. **§8 derived backgrounds are zero-GPU PIL ops.** `defocus` (P2) and `tone_gradient` (P4) produce legal abstract stages without re-rendering.

4. **G4 contact shadow + G5 occluder BOOK layer** compose deterministically on P1. Even a weak two-ellipse shadow beats the control's zero-grounding paste.

5. **G6 defringe** (1px alpha MinFilter) integrates cleanly before every cutout paste.

6. **Minimal metadata suffices.** Three sidecars drove the full 4-panel strip:
   - `L0_2b9283d4c387.composition.json` (kitchen plate + anchor slot + occluder crop)
   - `L2_3210c57437fb_alpha.composition.json` (thigh_up establishing pose + diegetic_pair)
   - `front_portrait_seated_calm_cutout.composition.json` (waist_up dialogue register)

## What failed / gaps exposed

1. **Contact shadow timing.** Current pilot applies G4 *after* L2 paste via a whole-canvas multiply composite. It works visually but can bleed into the subject's lower edge. Production patch should render shadow on an intermediate layer *under* L2 (z between L0 and L2).

2. **Dialogue-bust placement is metadata-light.** P2/P4 use a hardcoded VN bottom-anchor (`82%` frame, `48%` height) rather than slot metadata. Acceptable for pilot; production should add an abstract-stage anchor slot or derive from `eye_y_px` alignment.

3. **G3 tolerance is sensitive to anchor annotation.** `anchor.y_px` and `expected_figure_h_pct` must be co-calibrated; wrong seat line fails G3 at ±15%. Hand-annotation is fine at pilot scale; bank scale may need a one-time calibration script.

4. **No manifest integration yet.** Pilot bypasses `assemble_from_bank.py` and YAML manifests. Gates and ops live in standalone `composition_grammar.py`.

## Grammar proven with minimal changes?

**Yes.** The spec architecture holds. No compositor rewrite required — a surgical patch to `assemble_from_bank.py` plus schema/sidecar additions is sufficient.

## Recommended next patch set (exact scope)

| # | File | Change |
|---|------|--------|
| 1 | `scripts/manga/composition_grammar.py` | Promote from pilot module → imported library (already written) |
| 2 | `scripts/manga/assemble_from_bank.py` | When `composition_meta` sidecar exists on L0+L2: run G1/G2/G8 pre-flight; if FAIL → raise; if PASS → `horizon_scale_paste` + G4/G5/G6 instead of `composite_layer` |
| 3 | `scripts/manga/assemble_from_bank.py` | Support manifest `derivation:` block on L0 layers (`defocus`, `tone_gradient`, `void`) per spec §7–§8 |
| 4 | `scripts/manga/assemble_from_bank.py` | Support `anchor_slot` + `grounding:` manifest fields (additive; `bbox_pct` remains fallback with WARN `bbox_legacy`) |
| 5 | `schemas/manga/composition_meta.schema.json` | Merge (already added in pilot) |
| 6 | `schemas/manga/assembly_manifest.schema.json` | Add optional `shot_type`, `anchor_slot`, `grounding`, `derivation` properties |
| 7 | `scripts/manga/tests/test_composition_grammar.py` | Gate unit tests (G1 matrix, G3 math, control fail case) |
| 8 | Bank annotation | Roll sidecars to remaining L0/L2 assets (5 L0 + 19 L2 per spec §9) |

**Explicitly NOT in next patch:** chapter-level §6.2 validator, full `iyashikei.yaml` shot_type column, G7 depth attenuation, ML horizon detection.

## Pilot artifacts

```
artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/
  assembled/composition_grammar_pilot/
    p1_establishing.png          (2.2 MB)
    p2_dialogue_bust.png         (1.1 MB)
    p3_insert_object.png         (1.5 MB)
    p4_reaction_emotion.png      (524 KB)
    control_illegal_waist_on_room.png (2.1 MB)
    composition_grammar_pilot_strip.jpg (760 KB)
    composition_grammar_control_strip.jpg (275 KB)
    gate_report.json
    FINDINGS.md (this file)
```

Regenerate:

```bash
PYTHONPATH=. python3 scripts/manga/run_composition_grammar_pilot.py
```
