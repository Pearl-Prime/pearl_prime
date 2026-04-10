# Exercise system audit — Phoenix Omega

**Project:** proj_state_convergence_20260328  
**Date:** 2026-04-10  
**Subsystem:** core_pipeline, teacher_mode  

## STARTUP_RECEIPT (authority reads)

- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PEARL_ARCHITECT_STATE.md`
- `docs/DOCS_INDEX.md` (minimum navigation)
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`, `ACTIVE_WORKSTREAMS.tsv`, `SUBSYSTEM_AUTHORITY_MAP.tsv`
- Rendering/assembly: `phoenix_v4/rendering/chapter_composer.py`, `phoenix_v4/exercises/component_assembler.py`, `phoenix_v4/exercises/practice_library_loader.py`, `scripts/run_pipeline.py` (registry vs atom branches), `phoenix_v4/planning/assembly_compiler.py`, `phoenix_v4/planning/registry_resolver.py`
- Standards: `SOURCE_OF_TRUTH/exercises_v4/aha_noticing_phoenix_standard.yaml` (~27 technique keys + `_default`), `integration_phoenix_standard.yaml` (subset of keys + `_default` added in this upgrade)
- Pearl Practice DIM system: `config/pearl_practice/exercise_dimensions.yaml` — **Option A**: keep separate from book/TTS prose (pause_s timing is for standalone audio); connection point = future TTS layer if pause markers are ever injected into book scripts.

## Four systems (as-operated before this work)

| System | Role | Book pipeline |
|--------|------|----------------|
| Registry `EXERCISE` sections | Topic-specific prose | **Section registry path:** `registry_resolver` → `to_prose()`; missing slots may call `get_exercise_for_chapter` (library_34). **Not** `chapter_composer`. |
| ab_tady_37 | Rich 5-component JSON | Loader hooks exist (`resolve_from_ab_tady_components`); not auto-wired from registry/atom IDs in this audit. |
| library_34 | 272 generic items in `SOURCE_OF_TRUTH/practice_library/inbox/*_PRODUCTION_READY.json` | Fallback in `chapter_composer` (empty EXERCISE) and in `registry_resolver` (empty section). |
| DIM1–DIM5 | Combinatorial audio | `scripts/pearl_practice/*` only; not book pipeline. |

**Composition engine:** `component_templates.yaml` (bridges/intro pools) + `template_composer.py` (Pearl Practice) — book path uses `config/pearl_practice/component_templates.yaml` for bridges/intros in `compose_exercise`; Phoenix aha/integration now preferred from `SOURCE_OF_TRUTH/exercises_v4/*_phoenix_standard.yaml`.

## Phase 1 — Verified state (pre-fix narrative)

- **exercises_v4 approved atoms:** 11 YAML files under `SOURCE_OF_TRUTH/exercises_v4/approved/`. All were `approval.status: candidate` with full `content` blocks (intro, guided_practice, aha_noticing, integration) — **not stubs** (`candidate/_stubs` is separate).
- **component_assembler** already loaded `aha_noticing_phoenix_standard.yaml` and `integration_phoenix_standard.yaml`; lookup was by `exercise_id`, which rarely matched technique keys (e.g. atom ids vs `cyclic_sighing`). **Gap:** needed deterministic `exercise_type` → standard-key pool.
- **exercise_context:** `AssemblyContext` existed but `compose_chapter_prose` / `book_renderer` did not pass arc signals; `run_pipeline` / `assembly_compiler` did not emit `exercise_context`. **Gap:** no `emotional_role_sequence` → `EmotionalState`, no repeat/session-close wiring at render.
- **Production paths:** Topics with `registry/{topic}.yaml` use **registry resolver** (not Stage 6 `render_book` atom plan). Atom-assembly books use `render_book` → `compose_chapter_prose`. Draft grief run with registry showed **EXERCISE FALLBACK** warnings when resolver had to pull library_34 for empty EXERCISE sections — confirms library is still a backstop, not removed.

## Phase 6 — Decision

- **Keep DIM1–DIM5 for Pearl Practice / standalone audio.** Book chapters use continuous prose; optional future: TTS pause markers from DIM — document only, no code change to DIM.

## ab_tady_37 migration

- **Deferred:** moving 39 JSON atoms into `SOURCE_OF_TRUTH/exercises_v4/approved/` would be a large content import; OUT_OF_SCOPE for “wiring only” unless explicitly requested. Runtime already supports `ab_tady_data` in `assemble_exercise_for_chapter` when wired upstream.

## Post-upgrade behavior (this PR)

- `compose_chapter_prose` builds `AssemblyContext` from `emotional_role`, `chapter_index`, `total_chapters`, `exercise_atom_id`, `topic_id`, `persona_id`, `exercise_repeat_index` when no explicit `exercise_context` is passed.
- `component_assembler` maps canonical `exercise_type` (or chapter-rotated type) → Phoenix standard key for aha/integration; bridge/intro still from `SOURCE_OF_TRUTH/exercises_v4` YAMLs.
- `practice_library_loader.compose_exercise` uses Phoenix aha/integration blocks (category → type → standard key); bridges/intros still from `component_templates.yaml`.
- `get_exercise_for_chapter` logs **WARNING** when library_34 is used (registry + composer paths).
- **Atom `render_book` path:** `budget.json` + `quality_summary.json` include `exercise_source` counts and `exercise_fallback_ratio`; **>50%** library_34 triggers `exercise_fallback_quality_warning` and `logger.warning`.
- **Registry render path:** still writes registry-shaped `quality_summary.json`; exercise telemetry for registry books remains a future enhancement (resolver would need to aggregate sources).

## Verification commands

```bash
PYTHONPATH=. python3 -m pytest tests/ -k "exercise or practice or component" -q
```

Atom book (bypass registry by using a topic **without** `registry/{topic}.yaml` if present in repo), then inspect `artifacts/rendered/.../budget.json` → `exercise_source`.

Registry book (e.g. grief): expect resolver warnings if EXERCISE sections are empty for some chapters; fix is registry content, not loader deletion.
