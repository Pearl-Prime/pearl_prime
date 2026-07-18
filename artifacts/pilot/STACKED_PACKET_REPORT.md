# Section stacking results — loader wiring + multi-layer composition

**Project:** proj_state_convergence_20260328  
**Subsystem:** core_pipeline  
**Pilot run:** `PYTHONPATH=. python3 scripts/pilot/run_legacy_template_packet_pilot.py --topic anxiety --persona gen_z_professionals --teacher ahjan --exercise-journeys --output-dir artifacts/pilot/stacked_packet/anxiety/`

## Phase 1 — Root cause (diagnosed)

| Check | Result |
|--------|--------|
| Index path for `v2_somatic` | `template_expand2/_extracted/qaudiobook_template_v2_somatic/sections_somatic_v2` — correct |
| On-disk section dirs | `section_01_hook`, …, `section_06_teacherdoctrine`, … (prefix `section_NN_` — loader already matched via `_resolve_somatic_v2_section_path`) |
| YAML body key | `content:` (block scalar) — `_yaml_body` already reads `content` |
| `load_legacy_section('v2_somatic', ch, sec)` for all 120 cells | **120/120** return prose (>20 chars) in this workspace |
| Why production saw **2/120** legacy hits | **Pilot defaulted to `--legacy-library v4_therapeutic`**, whose extracted tree only has **two** section YAMLs per `legacy_template_index.yaml`. The somatic grid was never consulted. |

**Additional hardening:** `_maybe_descend_sections_somatic_v2()` descends from the zip wrapper into `sections_somatic_v2/` when the index points at `qaudiobook_template_v2_somatic/` without the inner segment.

## Loader fix

- **Before:** Operators ran the pilot with the default `v4_therapeutic` library → 2 legacy hits; somatic grid idle.  
- **After:** Pilot default library is **`v2_somatic`**; wrapper descent supports a mis-pointed index path.  
- **Measured:** `v2_somatic` continues to resolve **120/120** section files when the tree is present.

## Stacking results (anxiety / standard_book / this pilot)

| Metric | Before (typical: v4 default + single-layer selection) | After (stacked pilot) | Notes |
|--------|------------------------------------------------------|------------------------|--------|
| Packet total words | ~8,500 class (thin legacy + enrichment only) | **14,397** | From `word_budget.json` → `packet_total_words` |
| Enriched book words (pre-packet) | 8,452 | 8,452 | Unchanged — stacking happens at compose time |
| Sections in audit | 102 | 102 | **Not** 120: `standard_book` beatmap here uses **4 base slots/chapter** (HOOK, SCENE, REFLECTION, INTEGRATION) + depth-appended slots; legacy YAML maps by **slot ordinal** (1–4), not the full 10-section somatic grid |
| Avg words/section | ~84 (historical reports) | **141** | Depth-only rows pull average down vs 450 six-hour target |
| Legacy in packets | 2 (v4 path) | **51** | One legacy slice per **beatmap** slot where `slot_idx < len(bm_ch.slots)`; depth-only rows have no template row |
| Teacher + registry | Teacher replaced registry in slot | **27** packets with `teacher_atom`; registry text supplied via `peek_registry_content_for_beatmap_slot` into enrichment layer | |
| Depth | Via enrichment split only | **51** with `depth_module` in `sources_used` | Appended depth slots |
| Under beatmap `target_words` | (prior) high | **75 / 102** | Targets still ambitious vs available source depth for this format |
| Gap to 54,000 | Large | **~39,600 words short** | Needs more slots per chapter (e.g. six-hour format), Pearl_Writer expansion, and/or using somatic sections 5–10 once beatmap carries them |

**Source frequency (section_packet_audit.json):**  
`legacy_template`: 51, `depth_module`: 51, `enrichment`: 49, `teacher_atom`: 27, `journey_intro:awareness`: 3.

## Per-section-type notes (qualitative)

For this run, base slots are only four types per chapter; somatic section types 5–10 are unused until the beatmap includes matching slots. Template + registry + teacher stacking **does** add words, but **standard_book** does not mirror the 10-section somatic filenames 1:1 beyond the first *N* slots.

## Quality check — chapter 1 read-aloud

Read `artifacts/pilot/stacked_packet/anxiety/book.txt` chapter 1: the somatic hook opens with coherent body-first prose; later blocks introduce **phone/scene**, then **teacher doctrine** (e.g. desire/teaching lines), then **Elena** narrative, then reflection and exercise framing. **Transitions are audible** — useful content, but not yet a single unified voice. Placeholders such as `[STORY_INJECTION_POINT]` / `[EXERCISE_INJECTION_POINT]` remain and should be handled in the delivery renderer or upstream content.

## What still closes the gap to 54k

1. **Beatmap density:** Move to a format with **10 sections/chapter** (or otherwise align beatmap to the somatic grid) so all 120 YAML slices participate.  
2. **Pearl_Writer / expansion:** Stacking alone reached **~14.4k** packet words here — strong lift, still far from 54k.  
3. **Thin types:** Depth-only packets and low `target_words` slots keep averages below 450.

## Production readiness

**Partial.** Loader + composer + pilot now exercise **v2_somatic** and **multi-layer stacking** deterministically. Replacing registry-as-default for full six-hour books still requires **format alignment** (10 slots), **placeholder cleanup**, and **expansion** to hit duration targets.

## Tests

Focused: `tests/test_legacy_template_loader.py`, `tests/test_section_packet_composer.py`, `tests/test_enrichment_select.py::test_peek_registry_for_beatmap_slot_non_empty_under_teacher` — **21 passed** in the verification run.
