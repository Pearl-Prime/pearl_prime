# Manga Implementation Outline

**Purpose:** High-level implementation map for the AI Manga Dharma system.
Use this as the operational bridge between the spec suite and real code.

**Authority:** [specs/AI_MANGA_PIPELINE_SUMMARY.md](/Users/ahjan/phoenix_omega/specs/AI_MANGA_PIPELINE_SUMMARY.md)

**Render (current):** [docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md](/Users/ahjan/phoenix_omega/docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md) (V5.1) + [docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md](/Users/ahjan/phoenix_omega/docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md) (scale milestones; continuity-state generator = non-negotiable unlock).

**Catalog SSOT (live):** `config/source_of_truth/manga_series_plans/` (**1,350** series, 5 locales) + `config/source_of_truth/manga_book_plans/` (**18,900** episodes). Phase 2X executed — see [specs/MANGA_CATALOG_RECONCILIATION_SPEC.md](/Users/ahjan/phoenix_omega/specs/MANGA_CATALOG_RECONCILIATION_SPEC.md). **Do not replan:** Layer 1 fan-out cells 444/444 (PR #1355); generate per [docs/GLOBAL_CATALOG_FANOUT_EXECUTION_PLAN.md](/Users/ahjan/phoenix_omega/docs/GLOBAL_CATALOG_FANOUT_EXECUTION_PLAN.md).

**CLI routing:** [docs/MANGA_PIPELINE_ONBOARDING.md](/Users/ahjan/phoenix_omega/docs/MANGA_PIPELINE_ONBOARDING.md) (chapter DAG) · [docs/MANGA_PRODUCTION_PIPELINE.md](/Users/ahjan/phoenix_omega/docs/MANGA_PRODUCTION_PIPELINE.md) (smoke/weekly) · [docs/MANGA_PIPELINE_COMPLETE_GUIDE.md](/Users/ahjan/phoenix_omega/docs/MANGA_PIPELINE_COMPLETE_GUIDE.md) (registry/ITE).

## Series catalog band (6–18)

`config/manga/manga_brand_series_plan.yaml` encodes **simultaneous** pacing via `active_series_target`, `max_active_series`, and `new_series_per_year` (**legacy 13/37 teacher-mode file** — do not use for 37-brand SSOT; use `config/manga/canonical_brand_list.yaml` + `config/source_of_truth/manga_series_plans/`). For long-run portfolio depth, `global_defaults.target_series_catalog_min` / `target_series_catalog_max` (owner band **6–18** series per teacher brand over planning horizons) document the approved range; `scripts/manga/validate_manga_series_catalog_bounds.py` checks that per-brand caps stay consistent with that ceiling.

## System Shape

The manga system is a two-mode pipeline:

1. `Series setup`
Creates the frozen identity and story architecture for a series.

2. `Chapter production`
Turns one chapter handoff into prompts, rendered panels, pages, QC, and memory updates.

The system is agent-shaped in the specs, but implementation should begin as deterministic modules with versioned artifacts. We should only introduce orchestration after the contracts are stable.

## Governing Principle

The manga system is not a generic image pipeline. Its core quality rule is transmission through felt story structure, not explicit teaching language. That means:

- upstream artifacts must carry transmission metadata cleanly
- writer-facing artifacts must strip carrier annotations
- downstream render steps must stay deterministic and style-locked
- QC must see more than creative agents see

## Operational Layers

### Layer 1: Config and contracts

This layer defines the stable inputs and artifact schemas:

- style archetypes
- panel layout defaults
- manga gate definitions
- teaching library atoms
- series profile config
- artifact shape for prompt compilation

### Layer 2: Deterministic compilers

This layer converts structured metadata into structured outputs:

- teaching atoms -> writer/story inputs
- chapter panels -> visual prompts
- chapter text -> lettering spec
- panel assets + lettering -> composed page plan

### Layer 3: Renderers and assemblers

This layer touches expensive or external systems:

- image generation backends
- page assembly
- PDF / EPUB / scroll export

### Layer 4: QC and memory

This layer enforces release truth:

- structural checks
- visual/style drift checks
- silence integrity
- continuity
- transmission leakage
- series memory updates

## Implementation Order

### Slice 1: Manga kernel

Start from [specs/AI_MANGA_PIPELINE_SUMMARY.md](/Users/ahjan/phoenix_omega/specs/AI_MANGA_PIPELINE_SUMMARY.md), not from scattered older docs.

Scope:

- add a real `phoenix_v4.manga` package
- move the notebook prompt compiler into tested code
- load style and panel rules from `config/manga/`
- support teaching-library `panel_expression` overrides
- emit a deterministic prompt artifact shape

This slice is the minimum code kernel because it matches the validated Colab prototype without prematurely committing to orchestration or backend rendering.

### Slice 2: Chapter artifact contracts

Next:

- define writer handoff schema
- define chapter script schema
- define `panel_prompts.json` contract formally
- add fixture-driven tests

### Slice 2a: Reuse before render

Before wiring a production renderer, add the retrieval-first layer:

- compile chapter panel requests into `panel_prompts.json`
- resolve reusable backgrounds, motifs, and prior panel assets from a manga image bank
- mark only unresolved panels for new generation
- keep the free Colab path usable for the unresolved set

This is the lowest-cost bridge between the validated Colab prototype and later ComfyUI production work.

### Slice 3: Render and assemble

Then:

- renderer wrapper
- page assembler
- provenance manifest writer
- local smoke path matching the Colab prototype

### Slice 4: QC and memory

Then:

- revision queue contract
- series memory update contract
- gate runner

## Current First Build Slice

This branch starts the kernel with:

- **Artifact contracts (Phase 0):** `schemas/manga/*.schema.json` (shared `manga_common`), `phoenix_v4.manga.models` (paths, stage IDs, jsonschema validation, handoff leakage checks), fixtures under `tests/fixtures/manga/`, tests `tests/test_manga_schemas.py` + `tests/test_manga_schema_refs.py`, CLI `scripts/manga/validate_manga_json.py`, layout enum stub `config/manga/page_and_layout_enums.yaml`
- **Transmission Splitter (PR2):** `phoenix_v4.manga.transmission.story_architecture_internal_to_handoff` per spec §5 — tests in `tests/test_manga_transmission.py`
- **Series setup (Chunk B):** `phoenix_v4.manga.series` — `visual_identity`, `genre`, `story_architect`, `series_asset_registry`, `emit` (`build_series_artifact_bundle`, `emit_series_setup`, `load_series_bundle_from_replay`); writes validated `series/style_bible.json`, `lettering_style_bible.json`, `genre_blueprint.json`, `story_architecture_internal.json`, `story_architecture_handoff.json`, `asset_registry.json`; CLI `scripts/manga/run_series_setup.py`; replay fixture `tests/fixtures/manga/series_replay/`; tests `tests/test_manga_series_setup.py`
- **LLM + chapter writer (replay):** `phoenix_v4.manga.llm.client` (`ReplayLLMClient`, `from_json_file`), `phoenix_v4.manga.chapter.writer.write_chapter_script_pair` (prompt `phoenix_v4/manga/prompts/chapter_writer_prompt.txt`, replay fixtures under `tests/fixtures/manga/replay/`), deterministic stub `writer_stub.build_chapter_script_pair_from_handoff` — `tests/test_manga_chapter_writer.py`, `tests/test_manga_writer_stub.py`
- **Visual path (chapter → prompts → manifest):** `phoenix_v4.manga.chapter.visual_from_script.compile_panel_prompts_from_chapter_script` maps `chapter_script_writer_handoff` → validated `panel_prompts` artifact; `phoenix_v4.manga.image_backend` provides `NoopImageBackend` and `FixtureReplayImageBackend` + `build_panel_images_manifest`; CLI `scripts/manga/run_chapter_visual.py`; tests `tests/test_manga_chapter_visual.py`
- **Chapter production (Chunk C+D):** `phoenix_v4.manga.chapter.lettering_from_script.build_lettering_spec_from_chapter_script`, `page_compose.compose_final_page_pngs` (Pillow; horizontal strips per page), `chapter_production.produce_chapter_assets` (validated `panel_prompts`, `panel_images_manifest`, `lettering_spec`, optional `final_page_composite/page_NNN.png`); CLI `scripts/manga/run_chapter_production.py`; tests `tests/test_manga_lettering_from_script.py`, `tests/test_manga_chapter_production_integration.py`; test dep `Pillow` in `requirements-test.txt`
- **QC + runner (Chunk E+F):** `config/manga/gate_registry.yaml`; `phoenix_v4.manga.qc` (`load_gate_registry`, `build_revision_queue_for_chapter`); `phoenix_v4.manga.memory` (`apply_series_memory_update`, snapshots); `phoenix_v4.manga.runner.run_chapter_dag` with `stages/*/stage_manifest.json` resume, `--from-stage` / `--to-stage` via CLI `scripts/manga/run_manga_chapter.py`; stage id `series_memory_merge`; tests `tests/test_manga_chapter_runner_e2e_replay.py`
- config-backed style archetypes
- config-backed panel layouts
- seed teaching-library atoms for prompt override testing
- a deterministic visual prompt compiler in `phoenix_v4.manga`
- focused tests
- a `panel_prompts.json` manifest compiler for free Colab and future render backends
- a retrieval-first manga asset resolver so existing visuals are reused before new images are requested

## Landmarks merged to `main` (implementation log)

Use this as the canonical “what shipped” timeline for the contract-first manga kernel. **Next branch:** always from current `origin/main` (as of last merge below).

| When (merge) | PR / focus | What landed |
|--------------|------------|-------------|
| 2026-03-24 | **#60** — Chunk E+F | `828c9a181e76819e24a57325b9f6cdc231d8b46d` — QC + resumable runner: `config/manga/gate_registry.yaml`, `phoenix_v4/manga/qc/`, `phoenix_v4/manga/memory/`, `phoenix_v4/manga/runner/` (`run_chapter_dag`, stage manifests under `stages/<stage_id>/`), `scripts/manga/run_manga_chapter.py` (`--from-stage` / `--to-stage`), stage id `series_memory_merge`, tests `tests/test_manga_chapter_runner_e2e_replay.py`. CI: Core tests, Release gates, EI V2, Change impact, governance, pearl-prime reported green before merge. |
| (prior) | **#59** — Chunk C+D | Chapter production: `lettering_from_script`, `page_compose` (Pillow), `chapter_production.produce_chapter_assets`, `scripts/manga/run_chapter_production.py`, `tests/test_manga_lettering_from_script.py`, `tests/test_manga_chapter_production_integration.py`, `Pillow` in `requirements-test.txt`. |
| (prior) | **#58** — Chunk B | Series setup: `phoenix_v4/manga/series/*`, `emit_series_setup`, `scripts/manga/run_series_setup.py`, `tests/test_manga_series_setup.py`, series replay fixture. |
| (prior) | **#57** | `scripts/git/push_guard.py`, `tests/test_push_guard.py`, `python3` alignment in `ps.txt` / `CLAUDE.md`. |
| (prior) | **#56** — Chunk A | Replay chapter writer: `phoenix_v4/manga/chapter/writer.py`, `ReplayLLMClient.from_json_file`, pair replay fixture, `tests/test_manga_chapter_writer.py`. |
| (prior) | Visual / Phase 0 | `visual_from_script`, `image_backend`, `run_chapter_visual`, schemas/models/transmission as documented above. |

**Deliberately not in this kernel yet:** live LLM calls inside the runner; ComfyUI / batch SD workers; SDF training and Comfy SDF nodes (those remain in **`specs/MANGA_MODE_SYSTEM_SPEC.md`** §6.7, not in `phoenix_v4` code).

**Local-only note:** an untracked `specs/MANGA_QC_AND_EBOOK_PIPELINE_SPEC.md` in some checkouts is unrelated to the merged PRs unless added intentionally.

## What Pearl_GitHub Should Remember

- manga implementation starts from the summary doc, not from isolated partial specs
- the safe branching pattern is a clean `agent/*` branch from `origin/main`
- the first implementation slice is intentionally small and contract-first
- use the free Colab notebook for near-term rendering and seed-bank growth
- wire ComfyUI only after the reuse/contracts layer is stable and batch rendering is actually needed
- rendering/orchestration should follow only after deterministic contracts and tests are in place
