# Manga Pipeline Onboarding

**Purpose:** Get new developers and agents running the manga pipeline end-to-end.
**Authority:** `specs/AI_MANGA_PIPELINE_SUMMARY.md` (chapter pipeline), `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (catalog/portfolio governance), `docs/MANGA_IMPLEMENTATION_OUTLINE.md`
**Render authority (current):** `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (V5.1 Qwen-Image-Layered — AUTHORITY 2026-05-20, supersedes V4 L0+L2) + `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md` (rollout/milestones) + `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md`. Any render guidance below that predates 2026-05-20 reflects V4 — defer to the V5 docs.
**Catalog / fan-out:** Layer 1 planning is banked (444/444, PR #1355) — verify, do not rebuild. Execution: [docs/GLOBAL_CATALOG_FANOUT_EXECUTION_PLAN.md](./GLOBAL_CATALOG_FANOUT_EXECUTION_PLAN.md).
**Last updated:** 2026-05-29 (SSOT counts + V5.1 + entry-point routing); Phase 2X.6 catalog base 2026-04-26.

---

## CLI entry points (read this before picking a script)

| Goal | Doc | Primary entry |
|------|-----|----------------|
| Registry job + ITE stages | [MANGA_PIPELINE_COMPLETE_GUIDE.md](./MANGA_PIPELINE_COMPLETE_GUIDE.md) | `scripts/pipeline/create_job.py` → `run_chapter_production.py` |
| Smoke / weekly / full book export | [MANGA_PRODUCTION_PIPELINE.md](./MANGA_PRODUCTION_PIPELINE.md) | `scripts/run_manga_pipeline.py`, `scripts/weekly_manga_rollout.py` |
| Chapter DAG + series setup (this doc) | here | `scripts/manga/run_manga_chapter.py`, `run_series_setup.py` |
| V5.1 panel render (Pearl Star) | [docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md](./specs/MANGA_V5_LAYERED_ARCHITECTURE.md) | `scripts/manga/render_v5_episode.py` + rollout plan |

---

## Phase 2X.4 Catalog Reconciliation (2026-04-26)

The catalog/portfolio side of this pipeline was reconciled in Phase 2X. Read `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` for the full set of decisions (D-1..D-20). Quick map for what changed and where it lives:

| Concern | Where it lives | Notes |
|---|---|---|
| Strategic genre allow-list | `docs/GENRE_PORTFOLIO_PLAN.md` (CANONICAL) | 15 strategic shells — drives series_plan `genre.enum` |
| Per-locale catalog plans | `docs/CJK_CATALOG_PLAN.md`, `docs/US_CATALOG_PLAN.md` (CANONICAL) | Locale-specific format mix + platform routing |
| Mode strategy (mode definitions) | `docs/MANGA_MODE_STRATEGY.md` (CANONICAL) | Migrated from docx; 9 tables / 68 rows of mode rules |
| Brand portfolio (37 brands) | `config/manga/canonical_brand_list.yaml` + `docs/GENRE_PORTFOLIO_PLAN.md` | 37 manga-canon brands (Path X; not `config/brand_registry.yaml`) |
| Catalog plan generator | `scripts/manga/generate_catalog_plan_from_strategic.py` | Brand-metadata × pure-market-share weighting (4-leg) |
| Catalog plan output (auto-gen) | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | **AUTO-GENERATED — do NOT hand-edit.** Re-run the generator after editing strategic-tier inputs. |
| Series plan YAMLs | `config/source_of_truth/manga_series_plans/{locale}/` | **1,350** YAMLs across 5 locales (EXECUTED #696/#727; pre-exec projection was 1,410) |
| Book plan YAMLs | `config/source_of_truth/manga_book_plans/{series_id}/ep_NN.yaml` | **18,900** YAMLs (one per book/episode) |
| Series titles at plan stage | `title` / `localized_titles` in series_plan YAMLs | **1,349/1,350 = `TBD`** (expected); filled during generation, not a planning gap |
| Series plan generator | `scripts/manga/generate_series_plans_from_catalog.py` | Consumes catalog plan + format_routing.yaml |
| Atomic regen entry | `scripts/manga/run_2x4_atomic_regen.py` | PRESERVE map honors production-active series |

### New schema fields (series_plan v2.1.0)

`schemas/manga/series_plan.schema.json` v2.1.0 added:

- **`genre.enum`** — extended from 10 → 23 entries (10 legacy + 13 strategic). Strategic shells include `dark_fantasy`, `psychological_thriller`, `supernatural_mystery`, `sci_fi_cyberpunk`, `mecha`, `action_battle`, `sports_competition`, `workplace_drama`, `historical_period`, `cultivation_martial`. Add a new genre by editing this enum + adding a craft bible to `docs/research/manga_craft/{genre}.md` + adding pacing rows to `config/manga/manga_pacing_by_genre.yaml`.
- **`demographic`** — `kodomo|shonen|shojo|seinen|josei|general`
- **`locale_origin`** — `jp|kr|tw|cn|us` (origin convention for the genre, separate from the runtime locale)
- **`distribution_status`** — `distributed|gray_zone_disclosed|hold_pending_market_clearance` (D-18 + D-19)
- **`teacher_id`** — now nullable (brand wins; teacher is a body attribute per OQ-3 disposition)
- **`target_platforms.minItems`** — relaxed from 1 → 0 to support `hold_pending_market_clearance` (ko_KR per D-18)
- **`connector_lane.enum`** — added `gray_zone_with_disclosure`, `hold_pending_market_clearance`

### 5-locale matrix (D-18, D-19)

| Locale | Master format | Distribution status |
|---|---|---|
| en_US | dual path: bw_page_manga (manga aisle) OR direct_self_help_illustrated (mainstream) | `distributed` |
| ja_JP | bw_page_manga | `distributed` |
| zh_TW | bw_page_manga (hybrid) | `distributed` |
| zh_CN | color_vertical_webtoon | `gray_zone_disclosed` (push to Bilibili/Kuaikan/Tencent with full AI-disclosure metadata; R-zh_CN-distribution=HIGH per PRC Generative AI Service Measures 2023) |
| ko_KR | color_vertical_webtoon | `hold_pending_market_clearance` (rendered now, distribution paused; `target_platforms` intentionally empty) |

### Craft bibles (per-genre)

`docs/research/manga_craft/` — one bible per strategic genre. The 9 added in Phase 2X.3:
`dark_fantasy.md`, `psychological_thriller.md`, `supernatural_mystery.md`, `sci_fi_cyberpunk.md`, `workplace_drama.md`, `action_battle.md`, `sports_competition.md`, `historical_period.md`, `mecha.md`. Use these when authoring panel prompts, pacing decisions, and lettering profiles for a strategic-shell genre.

### Brand vs teacher (OQ-3 resolution)

- **Brand is the catalog allocation unit** (37 brands; live SSOT = **1,350** series plans across 5 locales).
- **Teacher is a body attribute** carried in `teacher_id` (nullable). A brand can have multiple authors/teachers attached at the body level; series identity is brand-first.
- **Anti-homogeneity** is now enforced via the per-brand %-allocation in `GENRE_PORTFOLIO_PLAN.md`, not via a separate brand-DNA enforcement layer (`MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` was reframed in Phase 2X.5 to point at the strategic plan rather than implement its own mechanism).

### Archived specs (Phase 2X.5)

`specs/archive/DEFERRED_2026_04_26.md` indexes specs that had zero code references and were deferred (not deleted): `MANGA_MODE_SYSTEM_SPEC.md` and `MANGA_AUTHOR_SYSTEM_SPEC.md`. See that index for reactivation criteria.

---

## Quick Start

The manga pipeline has two modes: **Series Setup** (run once per series) and **Chapter Production** (run per chapter). Both are exercised from the CLI scripts in `scripts/manga/`.

### Prerequisites

```bash
pip install -r requirements.txt          # core deps (PyYAML, jsonschema)
pip install -r requirements-test.txt     # adds Pillow for page composition + test deps
```

### 1. Validate Schemas

Confirm all manga JSON schemas load and cross-reference correctly:

```bash
python -m pytest tests/test_manga_schemas.py tests/test_manga_schema_refs.py -v
```

### 2. Run Series Setup

Series setup creates the frozen identity, genre blueprint, story architecture, and asset registry for a new series. It uses replay fixtures for deterministic offline runs.

```bash
python scripts/manga/run_series_setup.py \
  --workspace /tmp/manga_demo \
  --replay-dir tests/fixtures/manga/series_replay
```

This writes validated artifacts under `/tmp/manga_demo/series/`:
- `style_bible.json`
- `lettering_style_bible.json`
- `genre_blueprint.json`
- `story_architecture_internal.json`
- `story_architecture_handoff.json`
- `asset_registry.json`

### 3. Run a Chapter (Full DAG)

The chapter runner executes the full DAG: transmission split, writer, visual prompts, image gen, lettering, layout, QC, and series memory merge.

```bash
python scripts/manga/run_manga_chapter.py \
  --workspace /tmp/manga_demo \
  --image-backend fixture-replay \
  --replay-dir tests/fixtures/manga/replay
```

Resume from a specific stage with `--from-stage` / `--to-stage`:

```bash
python scripts/manga/run_manga_chapter.py \
  --workspace /tmp/manga_demo \
  --from-stage chapter_visual \
  --to-stage chapter_qc
```

Stage IDs (in execution order):
1. `transmission_split` -- Verify story architecture handoff
2. `chapter_writer` -- Chapter script (writer handoff)
3. `chapter_visual` -- Panel prompts
4. `chapter_image_gen` -- Panel images manifest
5. `chapter_lettering` -- Lettering spec
6. `chapter_layout` -- Page composites
7. `chapter_qc` -- QC revision queue
8. `series_memory_merge` -- Merge series memory

### 4. Run ITE (Implicit Therapeutic Engine) Pipeline

The ITE pipeline enriches chapter artifacts with breath pacing, color arc, gutter therapy, and fractal compliance data. It runs as part of the chapter DAG but can also be invoked standalone:

```bash
# Panel breath annotation
python scripts/manga/ite_panel_breath.py --chapter /tmp/manga_demo/chapter_script_writer_handoff.json

# Color arc
python scripts/manga/ite_color_arc.py --chapter /tmp/manga_demo/chapter_script_writer_handoff.json

# Gutter therapy
python scripts/manga/ite_gutter_therapy.py --chapter /tmp/manga_demo/chapter_script_writer_handoff.json

# Fractal compliance check
python scripts/manga/ite_fractal_check.py --chapter /tmp/manga_demo/chapter_script_writer_handoff.json

# Full ITE QC (all gates T-01 through T-20)
python scripts/manga/ite_qc.py --chapter /tmp/manga_demo/chapter_script_writer_handoff.json
```

### 5. Validate Any Manga JSON Artifact

```bash
python scripts/manga/validate_manga_json.py \
  --schema panel_prompts \
  --file /tmp/manga_demo/panel_prompts.json
```

Available schema stems: `panel_prompts`, `chapter_script_writer_handoff`, `chapter_script_internal_record`, `lettering_spec`, `revision_queue`, `series_memory`, `series_memory_update`, `genre_blueprint`, `story_architecture_handoff`, `story_architecture_internal`, `style_bible`, `panel_images_manifest`, `stage_manifest`, `chapter_request`, and more. Full list in `schemas/manga/`.

---

## Architecture Overview

### Directory Map

```
phoenix_v4/manga/                     # Python package (kernel)
  __init__.py                         # Public API: compile_visual_prompt, resolve_panel_asset, etc.
  config.py                           # Style archetype + panel layout loader
  visual_prompt_compiler.py           # Deterministic prompt assembly
  panel_prompt_manifest.py            # Batch prompt compiler
  asset_resolver.py                   # Retrieval-first manga image reuse
  ite_pipeline.py                     # ITE: breath, color arc, gutter, fractal, ITE QC
  image_backend.py                    # Noop + fixture-replay image backends
  transmission.py                     # Transmission splitter (internal -> handoff)
  chapter/
    writer.py                         # Chapter writer (LLM or replay)
    writer_stub.py                    # Deterministic writer stub
    visual_from_script.py             # chapter_script -> panel_prompts
    lettering_from_script.py          # chapter_script -> lettering_spec
    page_compose.py                   # Pillow-based page compositor
    chapter_production.py             # Orchestrates writer->visual->lettering->layout
  series/
    visual_identity.py                # Style bible + anchor panels
    genre.py                          # Genre blueprint builder
    story_architect.py                # Story architecture + beat sheet
    series_asset_registry.py          # Asset registry builder
    emit.py                           # Series artifact bundle emitter
  qc/
    gate_registry.py                  # Load config/manga/gate_registry.yaml
    chapter_qc.py                     # Build revision_queue for a chapter
    ite_scorer.py                     # ITE heuristic scorer (4 dimensions + composite)
  memory/
    series_memory_merge.py            # Apply updates, build snapshots
  runner/
    chapter_runner.py                 # Resumable chapter DAG
    dag_order.py                      # Stage execution order
    stage_manifest_io.py              # Per-stage manifest read/write
    revision_policy.py                # Revision loop policy
  models/
    validation.py                     # jsonschema loading + validation
    paths.py                          # Canonical artifact filenames
    stage_ids.py                      # Locked stage ID strings
    leakage.py                        # Transmission leakage checks
    workspace_layout.py               # Multi-chapter workspace resolution
  llm/
    client.py                         # ReplayLLMClient for deterministic tests
  sdf/
    stub.py                           # SDF training stub (future ComfyUI)
  prompts/
    chapter_writer_prompt.txt         # System prompt for chapter writer LLM

config/manga/                         # YAML configs
  gate_registry.yaml                  # QC gate definitions (runner gates)
  manga_gates.yaml                    # Visual prompt + silence gates
  ite_config.yaml                     # ITE parameters (breath, color, gutter, fractal, stealth)
  genre_ite_profiles.yaml             # Per-genre ITE overrides (10 genres)
  style_archetypes.yaml               # Visual style tokens
  panel_layouts.yaml                  # Panel layout grid definitions
  page_and_layout_enums.yaml          # Enum stubs for page/panel types
  sabido_roles.yaml                   # Character transmission constraints
  asset_selection_priority.yaml       # Asset resolver priority rules
  workspace_layout.yaml               # Multi-chapter workspace config
  teaching_library/atoms/seed_atoms.yaml  # Seed teaching atoms

schemas/manga/                        # JSON Schema (Draft 2020-12)
  manga_common.schema.json            # Shared definitions ($defs)
  panel_prompts.schema.json
  chapter_script_writer_handoff.schema.json
  chapter_script_internal_record.schema.json
  lettering_spec.schema.json
  revision_queue.schema.json
  series_memory.schema.json
  series_memory_update.schema.json
  series_memory_snapshot.schema.json
  genre_blueprint.schema.json
  story_architecture_handoff.schema.json
  story_architecture_internal.schema.json
  style_bible.schema.json
  lettering_style_bible.schema.json
  character_model_sheets.schema.json
  asset_registry.schema.json
  anchor_panels.schema.json
  motif_evolution_map.schema.json
  panel_images_manifest.schema.json
  stage_manifest.schema.json
  chapter_request.schema.json

scripts/manga/                        # CLI entry points
  run_series_setup.py                 # Series setup (one-shot)
  run_manga_chapter.py                # Full chapter DAG runner
  run_chapter_production.py           # Chapter production (writer->layout)
  run_chapter_visual.py               # Visual prompt compilation only
  run_prompt_compiler.py              # Single prompt compilation
  run_asset_resolver.py               # Asset resolution
  validate_manga_json.py              # Validate any manga JSON against schema
  ite_panel_breath.py                 # ITE breath annotation
  ite_color_arc.py                    # ITE color arc
  ite_gutter_therapy.py               # ITE gutter therapy
  ite_fractal_check.py                # ITE fractal compliance
  ite_qc.py                           # ITE full QC (T-01..T-20)

tests/                                # Test suite
  test_manga_schemas.py               # Schema loading + fixture validation
  test_manga_schema_refs.py           # Cross-schema $ref resolution
  test_manga_transmission.py          # Transmission splitter
  test_manga_series_setup.py          # Series setup end-to-end
  test_manga_chapter_writer.py        # Chapter writer (replay)
  test_manga_writer_stub.py           # Writer stub deterministic output
  test_manga_chapter_visual.py        # Visual prompt compilation
  test_manga_lettering_from_script.py # Lettering spec builder
  test_manga_chapter_production_integration.py  # Full chapter production
  test_manga_chapter_runner_e2e_replay.py       # Full DAG end-to-end
  test_manga_runner_revision_features.py        # Revision loop features
  test_manga_asset_resolver.py        # Asset resolver
  test_manga_visual_prompt_compiler.py # Visual prompt compiler
  fixtures/manga/                     # Replay fixtures for offline tests

specs/                                # Specifications
  AI_MANGA_PIPELINE_SUMMARY.md        # Master spec (7 agents, artifacts, data flow)
  MANGA_MODE_SYSTEM_SPEC.md           # System-level spec (EI, SDF, ComfyUI)
  MANGA_CHAPTER_WRITER_SPEC.md        # Chapter writer agent spec
  MANGA_GENRE_AGENT_SPEC.md           # Genre agent spec
  MANGA_STORY_ARCHITECT_SPEC.md       # Story architect spec
  MANGA_LAYOUT_AGENT_SPEC.md          # Layout agent spec
  MANGA_TEACHING_LIBRARY_SPEC.md      # Teaching library spec
  MANGA_SERIES_BIBLE_SPEC.md          # Series bible spec
  MANGA_TEXT_RENDERING_SPEC.md        # Text rendering spec
  MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md   # Brand DNA / anti-spam
  MANGA_PRODUCTION_PIPELINE_SPEC.md   # Production pipeline spec
```

### Pipeline Data Flow

```
Series Setup (once):
  Director brief -> Visual Identity Agent -> Genre Agent -> Story Architect
  Outputs: style_bible, genre_blueprint, story_architecture, asset_registry

Chapter Production (per chapter):
  story_architecture_handoff
    -> Transmission Splitter (strips carrier annotations)
    -> Chapter Writer (clean beat -> chapter_script)
    -> Visual Agent (chapter_script -> panel_prompts)
    -> Image Generation (panel_prompts -> panel_images)
    -> Lettering Agent (chapter_script + composition_notes -> lettering_spec)
    -> Layout Agent (panel_images + lettering_spec -> final_page_composite)
    -> QC Agent (all outputs -> revision_queue + series_memory_update)
    -> Series Memory Merge (updates series_memory.json)

ITE Enrichment (per chapter, integrated into DAG):
  chapter_script -> breath annotation -> gutter therapy -> color arc -> fractal check -> ITE QC
```

### Gate Registry

Two gate config files exist:

1. **`config/manga/gate_registry.yaml`** -- Runner-level gates checked by the chapter DAG:
   - `MANGA_GATE_IMAGES_ALL_OK` (chapter_image_gen)
   - `MANGA_GATE_LETTERING_SILENCE` (chapter_lettering)
   - `MANGA_GATE_LAYOUT_PAGES` (chapter_layout)
   - `MANGA_GATE_STORY_HANDOFF` (transmission_split)

2. **`config/manga/manga_gates.yaml`** -- Visual prompt and silence gates:
   - `MANGA.PROMPT.STRUCTURE` (BLOCKER)
   - `MANGA.PROMPT.TOKEN_BUDGET` (MAJOR)
   - `MANGA.TEACHING.PANEL_EXPRESSION` (MAJOR)
   - `MANGA.SILENCE.STRUCTURE` (BLOCKER)

3. **ITE QC gates** (in code, `phoenix_v4/manga/ite_pipeline.py`):
   - T-01 through T-20, covering breath, gutter, stealth, color, fractal, soundtrack, Sabido roles

### Key Design Principles

1. **Transmission integrity:** Creative agents never see teaching metadata. The Transmission Splitter strips carrier annotations from writer handoffs. QC sees everything.

2. **Contract-first:** All inter-agent communication is through versioned JSON artifacts validated against `schemas/manga/*.schema.json`. No implicit state passing.

3. **Retrieval before render:** The asset resolver checks existing image banks before requesting new image generation, keeping costs low.

4. **Deterministic testing:** Replay fixtures and stub backends allow the full pipeline to run without LLM calls or image generation.

5. **ITE stealth:** The Implicit Therapeutic Engine works through visual/structural means (breath pacing, color temperature, gutter spacing, fractal backgrounds) without any therapeutic vocabulary appearing in reader-facing content.

---

## Common Tasks

### Adding a New Genre

1. Add genre profile to `config/manga/genre_ite_profiles.yaml`
2. Add genre hiding places to `config/manga/genres/{genre_id}.json` (if Story Architect needs them)
3. Add any genre-specific color overrides to `config/manga/ite_config.yaml` under `color_arc.genre_overrides`
4. Run `python -m pytest tests/test_manga_series_setup.py -v` to verify

### Adding a New QC Gate

1. Add gate definition to `config/manga/gate_registry.yaml` (runner gates) or `config/manga/manga_gates.yaml` (visual/silence gates)
2. Implement check in `phoenix_v4/manga/qc/chapter_qc.py`
3. Add test case in `tests/test_manga_chapter_runner_e2e_replay.py`

### Adding a New Teaching Atom

1. Add atom YAML to `config/manga/teaching_library/atoms/`
2. Ensure atom has `panel_expression` field for visual prompt override
3. Run `python scripts/manga/validate_manga_json.py` on any affected artifacts

### Running the Full Test Suite

```bash
python -m pytest tests/test_manga_*.py -v
```

---

## Spec Cross-Reference

| Component | Spec | Code | Config |
|-----------|------|------|--------|
| Visual Identity | `specs/AI_MANGA_PIPELINE_SUMMARY.md` (Agent 00) | `phoenix_v4/manga/series/visual_identity.py` | `config/manga/style_archetypes.yaml` |
| Genre Agent | `specs/MANGA_GENRE_AGENT_SPEC.md` | `phoenix_v4/manga/series/genre.py` | `config/manga/genre_ite_profiles.yaml` |
| Story Architect | `specs/MANGA_STORY_ARCHITECT_SPEC.md` | `phoenix_v4/manga/series/story_architect.py` | -- |
| Chapter Writer | `specs/MANGA_CHAPTER_WRITER_SPEC.md` | `phoenix_v4/manga/chapter/writer.py` | -- |
| Visual Agent | `specs/AI_MANGA_PIPELINE_SUMMARY.md` (Agent 04a) | `phoenix_v4/manga/chapter/visual_from_script.py` | `config/manga/panel_layouts.yaml` |
| Lettering Agent | `specs/AI_MANGA_PIPELINE_SUMMARY.md` (Agent 04b) | `phoenix_v4/manga/chapter/lettering_from_script.py` | -- |
| Layout Agent | `specs/MANGA_LAYOUT_AGENT_SPEC.md` | `phoenix_v4/manga/chapter/page_compose.py` | `config/manga/page_and_layout_enums.yaml` |
| QC Agent | `specs/AI_MANGA_PIPELINE_SUMMARY.md` (Agent 06) | `phoenix_v4/manga/qc/chapter_qc.py` | `config/manga/gate_registry.yaml` |
| ITE | `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md` | `phoenix_v4/manga/ite_pipeline.py` | `config/manga/ite_config.yaml` |
| Transmission | `specs/AI_MANGA_PIPELINE_SUMMARY.md` (Splitter) | `phoenix_v4/manga/transmission.py` | -- |
| Series Memory | `specs/AI_MANGA_PIPELINE_SUMMARY.md` (Memory) | `phoenix_v4/manga/memory/series_memory_merge.py` | -- |
| Asset Resolver | `docs/MANGA_IMPLEMENTATION_OUTLINE.md` (Slice 2a) | `phoenix_v4/manga/asset_resolver.py` | `config/manga/asset_selection_priority.yaml` |
| Sabido Roles | ITE spec section 9 | (checked by ITE QC) | `config/manga/sabido_roles.yaml` |
