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
scripts/run_pipeline.py --pipeline-mode spine ... <!-- CI-ALLOWLIST: legacy-registry-ok — prose-only non-executed reference -->
```

Anything else (registry mode, template_expand legacy, pilot pipelines) is
legacy and scheduled for deletion in the phased cleanup tracked by
`artifacts/cleanup/pearl_prime_deletion_manifest_2026-04-24.md`.

Pilot script `scripts/debug/run_spine_pipeline.py` is a standalone minimal
harness and is KEPT as a reference implementation for debugging spine
enrichment in isolation. It may NOT be used for production output.

### 1.1 — Code default (resolved 2026-07-10)

`--pipeline-mode` argparse default in `scripts/run_pipeline.py` is **`spine`** <!-- CI-ALLOWLIST: legacy-registry-ok — prose-only non-executed reference -->
(COHESIVE-FLOW-PATH-DEFAULT-SPINE-01). Omitted flag → canonical path.

Legacy `--pipeline-mode registry` remains for explicit legacy QA only and is
**blocked** for `--render-book` under `--quality-profile production|flagship`
unless `--allow-legacy-registry` is passed.

## 2. Structural format

- **chapter count is per-runtime-format** — see `config/format_selection/format_registry.yaml` for the canonical value. As of 2026-05-18:
  - `standard_book` → **10 chapters** (`chapter_count_default: 10`; the most consequential default per AUTO-PLAN-SSOT-01-AMENDMENT Group B)
  - `extended_book_2h` → 14 chapters (works at 12 when paired with a 12-chapter F006 arc per `phoenix_v4/planning/format_selector.py:263-277`)
  - `deep_book_6h` → 16 chapters (per `chapter_count_default`)
  - 12-chapter arcs (F006 "Nervous System Ladder" et al.) remain valid for `extended_book_2h` and any format whose `compatible_structural_formats` includes F006
- **10 sections** per chapter
- **≥ 3 variants** per section (target 5 where authored; minimum 3 per TEMPLATE-UNIVERSAL-01 + SPEC-739-THRESHOLD-01; selected deterministically by seed)

**No "12 chapters per book" canonical claim.** Prior drafts of this doc said 12; that was drift against the registry. The registry is the SSOT for `chapter_count_default` per format. See cap entry AUTO-PLAN-SSOT-01-AMENDMENT in `docs/PEARL_ARCHITECT_STATE.md` for the reconciliation history.

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

All seven run in `scripts/run_pipeline.py` under `--pipeline-mode spine`. <!-- CI-ALLOWLIST: legacy-registry-ok — prose-only non-executed reference -->

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
  --exercise-journeys \
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
- `scripts/run_pipeline.py` (spine branch — canonical; registry branch legacy) <!-- CI-ALLOWLIST: legacy-registry-ok — prose-only non-executed reference -->
- `scripts/debug/run_spine_pipeline.py` (debug harness only)
- `scripts/publish/build_epub.py` (operator packaging entry; wraps release backend)
- `config/format_selection/format_registry.yaml`
- `config/source_of_truth/master_arcs/**`

## 10. What replaces what

| Legacy                                     | Replacement                                        |
|--------------------------------------------|----------------------------------------------------|
| `template_expand/`, `template_expand2/`    | `phoenix_v4/planning/*` + `config/content_banks/`  |
| `pipeline-mode=registry` fast path         | `pipeline-mode=spine` (default since 2026-07-10)   |
| `scripts/pilot/run_legacy_template_packet_pilot.py` | `scripts/run_pipeline.py --pipeline-mode spine`  <!-- CI-ALLOWLIST: legacy-registry-ok — prose-only non-executed reference --> |
| `scripts/pilot/run_spine_pipeline.py`      | `scripts/debug/run_spine_pipeline.py` (debug only) |
| `phoenix_v4/planning/legacy_template_loader.py` | (removed in Phase C or D)                      |
| Ad-hoc freeze_settings.yaml (never landed) | `config/format_selection/format_registry.yaml`     |

## 11. Script roles (operator-facing)

| Path | Role |
|------|------|
| `scripts/run_pipeline.py --pipeline-mode spine` | **Production book build** (default mode)  <!-- CI-ALLOWLIST: legacy-registry-ok — prose-only non-executed reference --> |
| `scripts/publish/build_epub.py` | **Production packaging** (EPUB from rendered `.txt`) |
| `scripts/release/build_epub.py` | Packaging backend (called by publish wrapper) |
| `scripts/render_plan_to_txt.py` | QA-only plan→txt render |
| `scripts/generate_full_catalog.py` | Catalog wrapper (routes to spine) |
| `scripts/run_max_quality_catalog.py` | QA batch wrapper (routes to spine+production chord) |
| `scripts/debug/run_spine_pipeline.py` | Debug spine harness (NOT production) |
| `scripts/experimental/compose_cohesive_chapter_from_plan.py` | Experimental chapter composer (NOT production) |
| `--pipeline-mode registry` | Legacy fast-path (blocked for production renders) |

## 12. Operator quick reference (2026-07-10)

Build a real book:

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic <topic> --persona <persona> --arc <arc.yaml> \
  --pipeline-mode spine \
  --quality-profile production --exercise-journeys \
  --render-book --render-dir <out_dir> --out <out_dir>/plan.json
```

(`--pipeline-mode spine` is the default; keep it explicit in production docs so the chord gate stays green.)

Package it:

```bash
python3 scripts/publish/build_epub.py --input <book.txt> ... --output <book.epub>
```

## 13. Cleanup status

| Phase | Scope                                         | Status         | Merge SHA |
|-------|-----------------------------------------------|----------------|-----------|
| A     | Stale docs + references                       | pending review | —         |
| B     | Unreferenced legacy scripts                   | pending review | —         |
| C     | Legacy loader + pilot packet script           | pending review | —         |
| D     | `template_expand/`, `template_expand2/`       | pending review | —         |
| E     | `pipeline-mode=registry` branch of run_pipeline.py | pending review | —     <!-- CI-ALLOWLIST: legacy-registry-ok — prose-only non-executed reference --> |
| F     | Final consolidation + shim removal            | pending review | —         |

This table is updated after each phase merges. Only when every row is filled
in AND no legacy references exist (verification commands in Step 8 of the
cleanup playbook) does this doc move from DRAFT to FINAL.
