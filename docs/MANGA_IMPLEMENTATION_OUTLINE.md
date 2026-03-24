# Manga Implementation Outline

**Purpose:** High-level implementation map for the AI Manga Dharma system.
Use this as the operational bridge between the spec suite and real code.

**Authority:** [specs/AI_MANGA_PIPELINE_SUMMARY.md](/Users/ahjan/phoenix_omega/specs/AI_MANGA_PIPELINE_SUMMARY.md)

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
- **LLM + chapter writer (replay):** `phoenix_v4.manga.llm.client` (`ReplayLLMClient`, `from_json_file`), `phoenix_v4.manga.chapter.writer.write_chapter_script_pair` (prompt `phoenix_v4/manga/prompts/chapter_writer_prompt.txt`, replay fixtures under `tests/fixtures/manga/replay/`), deterministic stub `writer_stub.build_chapter_script_pair_from_handoff` — `tests/test_manga_chapter_writer.py`, `tests/test_manga_writer_stub.py`
- config-backed style archetypes
- config-backed panel layouts
- seed teaching-library atoms for prompt override testing
- a deterministic visual prompt compiler in `phoenix_v4.manga`
- focused tests
- a `panel_prompts.json` manifest compiler for free Colab and future render backends
- a retrieval-first manga asset resolver so existing visuals are reused before new images are requested

## What Pearl_GitHub Should Remember

- manga implementation starts from the summary doc, not from isolated partial specs
- the safe branching pattern is a clean `agent/*` branch from `origin/main`
- the first implementation slice is intentionally small and contract-first
- use the free Colab notebook for near-term rendering and seed-bank growth
- wire ComfyUI only after the reuse/contracts layer is stable and batch rendering is actually needed
- rendering/orchestration should follow only after deterministic contracts and tests are in place
