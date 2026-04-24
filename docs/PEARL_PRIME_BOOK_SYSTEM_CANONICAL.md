# Pearl Prime Book System — Canonical Contract

**Date:** 2026-04-24
**Authority:** post-PR-604 spine pipeline, with forward references to open PRs #605, #608, and #610
**Status:** DRAFT — cleanup-phase baseline; will be finalized when legacy paths are removed

This document is the single source of truth for the Pearl Prime book generation
system. Any re-introduction of v2 / v3 / template_expand* / pipeline-mode=registry
code requires an explicit ADR that updates this doc.

---

## 1. One pipeline path

All book generation MUST flow through:

```
scripts/run_pipeline.py --pipeline-mode spine ...
```

Anything else (registry mode, template_expand legacy, pilot pipelines) is
legacy and scheduled for deletion in the phased cleanup tracked by
`artifacts/cleanup/pearl_prime_deletion_manifest_2026-04-24.md`.

Pilot script `scripts/pilot/run_spine_pipeline.py` is a standalone minimal
harness and is KEPT as a reference implementation for debugging spine
enrichment in isolation. It may NOT be used for production output.

## 2. Structural format

- **12 chapters** per book
- **10 sections** per chapter
- **5 variants** per section (selected deterministically by seed)

Section types include `SCENE`, `DEPTH`, `TEACHER`, etc. (authoritative list
lives in the format registry; see §6). SCENE slots live at section indices
**(2, 5, 9)** — this is `SCENE_SECTION_INDICES` in `phoenix_v4/planning/story_planner.py`.

## 3. Book phases and story arcs

A book has four narrative phases, each covering three chapters:

| Phase    | Default chapters | Arc beats scheduled                        |
|----------|------------------|--------------------------------------------|
| HARDSHIP | 1–3              | recognition → mechanism_proof → turning    |
| HELP     | 4–6              | recognition → mechanism_proof → turning    |
| HEALING  | 7–9              | recognition → mechanism_proof → turning    |
| HOPE     | 10–12            | recognition → mechanism_proof → **embodiment** (phase-final chapter) |

`build_story_schedule()` selects N_PER_PHASE character journeys per phase,
each covering all four arc positions across the SCENE slots of one chapter.

## 4. Atom stacking

Every book slot is resolved against these atom banks:

| Layer      | Symbol | Source                                              |
|------------|--------|-----------------------------------------------------|
| Persona    | 👤     | `config/atoms/persona/...` (per-persona voice)      |
| Teacher    | 🎓     | `config/atoms/teacher/...` (doctrine, reflections)  |
| Registry   | 📋     | `config/content_banks/registry/...` (structural)    |
| Story      | 📖     | `story_atoms/{persona}/anchored/{topic}/...`        |
| Exercise   | 📚     | `config/exercises/...` (practice library)           |

Under `additive_enrichment=True` the spine pipeline layers all four sources
per slot: **persona first → registry always → teacher third → story where scheduled**.
Practice library is injected by the exercise journey planner.

## 5. Required features (cleanup must not regress any of these)

The following features landed on main and must survive legacy deletion. Any
cleanup PR that breaks one of these has to revert.

- `build_story_schedule()` — phase-aware character journey planner
- `StorySchedule` — (chapter_index, section_index) → StoryAtomSlot mapping
- `BookSlotTracker` — book-level no-repeat + collision-family spread
- `resolve_injections()` — 4 injection markers + locale + mechanism tokens
- `EnrichedSlot.teacher_content` — teacher wrapper populated at depth pass
- Section packet audit (`section_packet_audit.json`)
- Registry peek on waterfall teacher wins (additive mode)
- Exercise journeys (`--exercise-journeys`)
- Format plan applied to spine (PR #605 derives runtime from output_format)
- Protagonist LoRA specs + character image pipeline (PR #610 — manga adjacent, book-agnostic)

## 6. Format registry (runtime format selection)

Runtime format drives target word bands and slot word budgets:

- **Registry:** `config/format_selection/format_registry.yaml`
- **Selector:** `phoenix_v4/planning/format_selector.py`
- **Duration planner:** `phoenix_v4/planning/duration_planner.py`
- **Output contract:** `phoenix_v4/planning/output_contract.py`
- **Spec loader:** `phoenix_v4/planning/beatmap_compile.py::load_format_spec`

Supported runtime formats for Prime books: `standard_book` (default),
plus those declared in the registry.

NOTE: The task brief referenced `config/freeze_settings.yaml` and
`phoenix_v4/planning/format_plan.py`. Neither exists in the current tree —
the equivalent responsibilities live in the files listed above. PR #605
("derive spine runtime from output_format") is still open; when it lands,
this section must be updated to reflect the freeze_settings wiring it
introduces (or amended if the shape differs).

## 7. Quality gates (must pass under this system)

- Chapter flow gate
- EI V2 composite ≥ 0.60
- ONTGP bestseller ≥ 0.55
- Scene anchor density cap (≤ 2 repeated > 3-word phrases)
- Book quality gate
- Transformation arc
- Memorable lines

All seven run in `scripts/run_pipeline.py` under `--pipeline-mode spine`.

## 8. CLI contract

Supported invocation (canonical):

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic <topic_id> \
  --persona <persona_id> \
  --arc <master_arc_yaml> \
  --pipeline-mode spine \
  --render-book --render-dir <out_dir> \
  --out <out_dir>/plan.json \
  --quality-profile production \
  --seed <seed>
```

Optional flags of record:
- `--runtime-format <name>` (defaults to `standard_book`)
- `--exercise-journeys`
- `--no-job-check --no-generate-freebies` (for fast iteration)

After cleanup completes, the `--pipeline-mode` flag may be removed entirely
(spine becomes implicit); that is tracked as Phase E in the deletion manifest.

## 9. Authority files

These files are the "kept" set. Cleanup PRs MUST NOT modify or delete them
without a superseding ADR:

- `phoenix_v4/planning/enrichment_select.py`
- `phoenix_v4/planning/story_planner.py`
- `phoenix_v4/planning/injection_resolver.py`
- `phoenix_v4/planning/beatmap_compile.py`
- `phoenix_v4/planning/knob_apply.py`
- `phoenix_v4/planning/format_selector.py`
- `phoenix_v4/planning/duration_planner.py`
- `phoenix_v4/planning/output_contract.py`
- `phoenix_v4/rendering/book_renderer.py`
- `phoenix_v4/rendering/chapter_composer.py`
- `scripts/run_pipeline.py` (spine branch only — registry branch slated for Phase E deletion)
- `scripts/pilot/run_spine_pipeline.py`
- `config/format_selection/format_registry.yaml`
- `config/source_of_truth/master_arcs/**`

## 10. What replaces what

| Legacy                                     | Replacement                                        |
|--------------------------------------------|----------------------------------------------------|
| `template_expand/`, `template_expand2/`    | `phoenix_v4/planning/*` + `config/content_banks/`  |
| `pipeline-mode=registry` fast path         | `pipeline-mode=spine` (will become default)        |
| `scripts/pilot/run_legacy_template_packet_pilot.py` | `scripts/pilot/run_spine_pipeline.py`    |
| `phoenix_v4/planning/legacy_template_loader.py` | (removed in Phase C or D)                      |
| Ad-hoc freeze_settings.yaml (never landed) | `config/format_selection/format_registry.yaml`     |

## 11. Cleanup status

| Phase | Scope                                         | Status         | Merge SHA |
|-------|-----------------------------------------------|----------------|-----------|
| A     | Stale docs + references                       | pending review | —         |
| B     | Unreferenced legacy scripts                   | pending review | —         |
| C     | Legacy loader + pilot packet script           | pending review | —         |
| D     | `template_expand/`, `template_expand2/`       | pending review | —         |
| E     | `pipeline-mode=registry` branch of run_pipeline.py | pending review | —    |
| F     | Final consolidation + shim removal            | pending review | —         |

This table is updated after each phase merges. Only when every row is filled
in AND no legacy references exist (verification commands in Step 8 of the
cleanup playbook) does this doc move from DRAFT to FINAL.
