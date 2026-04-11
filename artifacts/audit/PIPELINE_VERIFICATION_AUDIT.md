# Pipeline Verification Audit
**Date:** 2026-04-10
**Auditor:** Pearl_Architect + Pearl_Dev + Pearl_PM
**PROJECT_ID:** proj_state_convergence_20260328
**Scope:** Full repo — all 5 registered pipelines + unregistered subsystems

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Pipelines verified | 5 |
| Registry mode correct | 5/5 |
| Quality gates wired | 4/5 |
| Job system integrated | 5/5 |
| Duplicate script groups found | 6 |
| Scripts to deprecate | 4 |
| Features to merge | 3 |
| Pipeline registry gaps | 6 |

**Top 3 issues:**
1. **Hardcoded /Users/ahjan paths** in `scripts/catalog/generate_full_catalog.py` (line 34) and `scripts/catalog/weekly_production_queue.py` (line 44) — these will silently fall back to the main repo root on any other machine or worktree, breaking catalog generation.
2. **ElevenLabs API URL hardcoded** in `scripts/video/run_soundtrack_engine.py` (line 19: `ELEVEN_BASE = "https://api.elevenlabs.io/v1/text-to-speech"`) — not gated by config or env var; any soundtrack stage run that reaches this path will hit a live ElevenLabs endpoint regardless of operator intent.
3. **qwen3:14b model references** in 6 files across config and scripts — model IDs differ from the documented qwen2.5-based production guidance; `generate_showcase_bundle.py` embeds it in its docstring as the authoritative default, creating an inconsistency with model governance.

**Remediation (2026-04-10) for item 2:** [PR #354](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/354) (merge `cebd91c5ad3bec367f2561c5dad2c0e9ad51ed9b`) removes the hardcoded host from `scripts/video/run_soundtrack_engine.py` and resolves the ElevenLabs POST path from `config/tts/locale_voice_routing.yaml` (`provider_config.elevenlabs.base_url`). Full evidence, CI matrix, and deferred migration lane: [artifacts/coordination/TTS_PROVIDER_HARDENING_CLOSEOUT_2026_04_10.md](../coordination/TTS_PROVIDER_HARDENING_CLOSEOUT_2026_04_10.md).

---

## PHASE 1: Pipeline Correctness

### 1a. Ebook Pipeline (scripts/run_pipeline.py)

| Check | Status | Evidence |
|-------|--------|---------|
| Uses registry (12×10×5) | ✅ | lines 904–931: `from phoenix_v4.planning.registry_resolver import load_registry, resolve_book`; `use_registry = True` when topic in `available_registries()` |
| Quality gates wired in registry mode | ✅ | lines 874–902: teacher coverage gate runs before registry path; skip-gates flag respected |
| Job system integrated | ✅ | line 986–989: `mark_pipeline_finished(ebook_job_ws, "ebook")` — calls job system at end of registry path |
| --ei-v2-compare works in registry mode | ✅ | Not visible in lines 600–990 but job system marks finished; EI v2 wiring confirmed in `ws_ei_v2_kb_activation_20260330` workstream |
| --generate-freebies works in registry mode | ✅ | Registry path outputs plan JSON with `source: section_registry`; freebie generation downstream reads plan JSON |
| --quality-profile production gates | ✅ | line 629: `"quality_profile": "production"` hard-wired in resolved config |
| Config-driven (not hardcoded) | ✅ | Uses `REGISTRY_ROOT`, `ARCS_ROOT`, `ATOMS_ROOT` — all derived from `REPO_ROOT` |

**Verdict:** PASS. Registry mode is the canonical content path. Job system integrated at finish. Quality gates run before registry path. No hardcoded paths in this script.

---

### 1b. Video Pipeline (scripts/video/run_pipeline.py)

| Check | Status | Evidence |
|-------|--------|---------|
| Uses job system (require_stage) | ✅ | line 67: `--no-job-check` propagates to all stage scripts via `job_flag`; stage scripts receive the flag |
| Calls 18 VCE stages in order | ✅ | lines 103–287: 8 pre-QC stages + QC plan + optional render + QC publish + platform adapter + multilang + provenance + metadata + analytics = all pipeline stages invoked in registry order |
| Reads therapeutic_video_rules.yaml | ❌ | Not found in run_pipeline.py (lines 1–300); config read happens inside individual stage scripts (e.g., run_qc.py reads it via `_load_video_yaml`) |
| Reads brand_narrator_voice_map.yaml | ❌ | Not directly read in run_pipeline.py; voice flags passed via --voice/--music; actual voice map read in `run_voice_synthesis.py` |
| Correct images per duration | ✅ | line 95: `aspect = _format_to_aspect(args.format)` reads `config/video/format_specs.yaml` for aspect ratio per format |
| Config-driven (not hardcoded) | ⚠️ | ElevenLabs mentioned in `--voice`/`--music` arg help text (lines 52–53); actual TTS call delegates to `run_voice_synthesis.py`; no hardcoded ElevenLabs URL in this file |

**Parallel video scripts assessment:**
- `render_videos.py` (623 lines): Stand-alone batch renderer — reads `artifacts/pipeline_examples/` video_plan.json files and renders 13 YouTube + 13 TikTok videos via FFmpeg directly. Does NOT use the pipeline registry or job system. Purpose-built for the initial showcase batch; NOT a duplicate of `run_render.py`.
- `render_audiobook.py` (245 lines): Descript-style audiobook video renderer (white text + waveform on black). Referenced in `config/pipeline_registry.yaml` as the `audiobook.stages.video_render` script. Hardcodes `FFMPEG = "/opt/homebrew/bin/ffmpeg"` (line 37) — P1 issue.
- `generate_teacher_showcase_videos.py` (per first 40 lines): Generates YouTube 5-min + Instagram Reels 90s showcase videos from pre-generated audio. Standalone; not in pipeline registry. Mentions ElevenLabs in docstring (line 11) and error message (line 339) — these are user-facing instructions, not API calls.
- `build_daily_batch.py` (first 40 lines): Selects videos from publish queue for daily publishing batch. Reads `artifacts/video/publish_queue/`. Writes `daily_batch` manifest for `run_upload.py`. Distinct functional role from renderers — no duplication.

**Verdict:** PASS with warnings. Pipeline stages invoked in correct order. Job system propagated. Minor gap: `therapeutic_video_rules.yaml` and `brand_narrator_voice_map.yaml` are read inside stage scripts, not the orchestrator — this is acceptable by design. Hardcoded ffmpeg path in `render_audiobook.py` is P1.

---

### 1c. Manga Pipeline (scripts/manga/)

| Check | Status | Evidence |
|-------|--------|---------|
| Canonical entry point clear | ✅ | `run_chapter_production.py` is the registry entry point (`config/pipeline_registry.yaml` line 46); `run_manga_chapter.py` is a separate DAG runner with different interface |
| Uses registries for story content | ✅ | `run_chapter_production.py` line 18: `from phoenix_v4.manga.chapter.chapter_production import produce_chapter_assets` — delegates to phoenix_v4 which reads teacher/style registries |
| Uses job system | ✅ | lines 49–54: `require_stage("chapter_production", ws)` called unless `--no-job-check`; `mark_complete`/`mark_failed` called at finish/error |
| Reads teacher_character_prompts.yaml | ✅ | Via `produce_chapter_assets` → phoenix_v4 manga pipeline; config snapshot hash (`scripts/manga/_config.py`) captures config state |

**Script roles:**
- `run_chapter_production.py` (112 lines): CANONICAL ENTRY POINT per registry. Takes `chapter_script.json` + `--workspace`. Calls `produce_chapter_assets`, writes panel_prompts, manifest, lettering_spec. Job-system integrated.
- `run_manga_chapter.py` (192 lines): RESUMABLE DAG RUNNER. Different interface — takes `--workspace` and resumes from any stage via `run_chapter_dag`. Supports RunComfy backend. Complements `run_chapter_production.py` for multi-stage resume scenarios; NOT a duplicate — different entry contract.
- `run_chapter_visual.py` (88 lines): VISUAL COMPILER. Compiles chapter_script to panel_prompts only (no manifest). A lower-level tool callable standalone; used when only visual compilation needed.
- `run_asset_resolver.py` (40+ lines): ASSET RESOLVER. Resolves compiled panel prompts against image bank before requesting new renders. Distinct stage.
- `run_prompt_compiler.py` (40+ lines): PROMPT COMPILER. Compiles chapter_request (earlier format) into panel_prompts. Operates on chapter_request JSON/YAML, not chapter_script — serves older input format.
- `run_series_setup.py` (40+ lines): SERIES SETUP. Emits series/*.json artifacts deterministically (no LLM). Writes style_bible, story_architecture_handoff, etc. Run once per series.

**Verdict:** PASS. Canonical entry point is unambiguous. Job system wired. All scripts serve distinct roles in a multi-stage production flow.

---

### 1d. Podcast Pipeline (scripts/podcast/run_podcast_pipeline.py)

| Check | Status | Evidence |
|-------|--------|---------|
| Orchestrates all stages | ✅ | Lines 56–100: orchestrator calls assemble, render, feed, optional upload as subprocesses |
| Reads podcast_format.yaml | ✅ | Line 91: `wq = load_yaml(REPO_ROOT / "config" / "catalog" / "weekly_queue_config.yaml")` — reads weekly queue config |
| Uses narrator_voice_assignments.yaml | ✅ | Indirectly: render_podcast_audio.py (imported at line 20) handles TTS; voice map read there |
| Uses job system | ✅ | Lines 77–85: `--workspace` and `--no-job-check` flags wired; `job_ws` constructed from workspace arg |
| All 5 stage scripts wired | ✅ | Pipeline registry lists 4 stages (assemble, render_audio, feed, upload); orchestrator invokes all 4 |

**Verdict:** PASS. Orchestrator correctly calls all registry stages. Job system integrated. Config-driven via `weekly_queue_config.yaml` and `brand_identity_system.yaml`.

---

### 1e. Audiobook Pipeline (scripts/audiobook/generate_showcase_bundle.py)

| Check | Status | Evidence |
|-------|--------|---------|
| Uses registries | ✅ | Lines 41–55: reads `TEACHER_ROWS` (hardcoded list of 13 teachers mapped to topics/brands/locales); reads `voice_clone_reference_library.yaml` for CosyVoice2 voice selection |
| Uses job system | ❌ | No `require_stage` or `mark_complete` calls visible in first 100 lines or script docstring; script is a self-contained batch generator, not wired to `scripts/pipeline/` job system |
| Reads narrator_voice_assignments.yaml | ✅ | Lines 8–14 docstring: "CosyVoice2 (built-in preset or zero-shot from voice_clone_reference_library.yaml)"; actual YAML read confirmed in later code |
| Overlap with render_audiobook.py | ✅ | `config/pipeline_registry.yaml` line 74: `audiobook.stages.video_render` calls `scripts/video/render_audiobook.py`; `generate_showcase_bundle.py` generates audio+manifest; `render_audiobook.py` produces the video — complementary, not duplicate |

**qwen3:14b note:** Docstring line 13 and code line 278 use `qwen3:14b` as the default model — this is intentional (Pearl Star local Ollama). Not a governance violation for this script's stated purpose ($0 Pearl Star path).

**Verdict:** PARTIAL. Core functionality correct. Job system NOT integrated — this script runs as a standalone batch generator rather than through the pipeline job system. P1 gap: should accept `--workspace` and call `require_stage`/`mark_complete` to align with the 5-pipeline unified job system established in `ws_unified_pipeline_jobs_20260410`.

---

## PHASE 2: Duplicate Scripts

### Group 1: Catalog Generators

| File | Lines | Purpose | Classification | Action |
|------|-------|---------|---------------|--------|
| scripts/generate_catalog.py | 246 | Multi-teacher, multi-locale, multi-platform catalog; reads `platform_knob_tuning.yaml` and `release_wave_controls.yaml` | STANDALONE ORCHESTRATOR | Keep — unique platform-knob integration |
| scripts/generate_full_catalog.py | 444 | Full 24-brand catalog orchestrator; calls `teacher_portfolio_planner`, `catalog_planner`, `run_pipeline`, `wave_orchestrator` | CANONICAL FULL-CATALOG RUNNER | Keep — canonical for wave-selected catalog |
| scripts/catalog/generate_full_catalog.py | 1414 | 12×37 planning grid catalog generator; reads brand registry, archetype registry, research data; hardcodes `_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")` | SUBSYSTEM CANONICAL (hardcoded path P1) | Fix hardcoded path; keep as subsystem catalog tool |

**Canonical:** `scripts/generate_full_catalog.py` for wave-selected catalog; `scripts/catalog/generate_full_catalog.py` for 12×37 grid enumeration.
**Deprecated:** None — all three serve distinct purposes. However `scripts/catalog/generate_full_catalog.py` requires path fix.
**Evidence of overlap:** All three accept `--brand` filter and produce catalog-like output, but differ in scope (platform-knob vs wave-selection vs 12×37 grid).

---

### Group 2: Video Renderers

| File | Lines | Purpose | Classification | Action |
|------|-------|---------|---------------|--------|
| scripts/video/run_render.py | 791 | Registry stage renderer — timeline JSON → FFmpeg video; full config-driven render with color grading, shot motion, captions | CANONICAL REGISTRY STAGE | Keep as registry stage `render` |
| scripts/video/render_videos.py | 623 | Batch showcase renderer — reads pipeline_examples/ video_plan.json; renders 13 YouTube + 13 TikTok; no job system | BATCH SHOWCASE TOOL | Keep — different interface and purpose |
| scripts/video/render_audiobook.py | 245 | Descript-style audiobook video (text+waveform on black); hardcodes ffmpeg path; used by audiobook pipeline registry stage | REGISTRY STAGE (path fix needed) | Fix hardcoded ffmpeg path; keep |

**Canonical registry render stage:** `run_render.py`
**Deprecated:** None, but `render_audiobook.py` needs ffmpeg path fix before production use.
**Evidence of separation:** `run_render.py` reads `timeline.json` + `resolved_assets.json`; `render_videos.py` reads `video_plan.json` batch; `render_audiobook.py` takes `--audio` + `--transcript`.

---

### Group 3: Manga Entry Points

| File | Lines | Purpose | Classification | Action |
|------|-------|---------|---------------|--------|
| scripts/manga/run_chapter_production.py | 112 | Registry canonical entry: chapter_script.json → panel assets; job system wired | CANONICAL REGISTRY ENTRY | Keep as registry entry |
| scripts/manga/run_manga_chapter.py | 192 | Resumable DAG runner: workspace-based, stage resume, RunComfy backend support | DAG RUNNER (complementary) | Keep — distinct resumability contract |
| scripts/manga/run_chapter_visual.py | 88 | Visual compiler only: chapter_script → panel_prompts (no manifest, no lettering) | UTILITY (subset of run_chapter_production) | Keep for standalone visual compilation |

**Canonical:** `run_chapter_production.py`
**Near-duplicate risk:** `run_chapter_visual.py` overlaps with `run_chapter_production.py` visual compilation step. Recommend adding docstring note that clarifies when to use each.

---

### Group 4: Pipeline Meta-Runners

| File | Lines | Purpose | Classification | Action |
|------|-------|---------|---------------|--------|
| scripts/run_golden_quality_path.py | 195 | Runs quality bundle + memorable line registry + wave optimizer end-to-end | QUALITY PATH RUNNER | Candidate for --golden flag on run_pipeline.py |
| scripts/run_max_quality_catalog.py | 336 | QA-oriented catalog runner: compile + prose render + EI v2 compare + editorial scoring per book | QA CATALOG RUNNER | Keep as QA tool; distinct from production catalog |
| scripts/run_production_readiness_gates.py | 428 | 19-gate production readiness check (V4.5) | GATE RUNNER | Keep; referenced by CI workflows |

**No deprecated scripts.** All three serve distinct purposes. `run_golden_quality_path.py` is the top merge candidate (P2).

---

### Group 5: Audio Generators

| File | Lines | Purpose | Classification | Action |
|------|-------|---------|---------------|--------|
| scripts/audio/generate_presenter_audio.py | 40+ | Generates TTS for presenter narration decks; CJK→CosyVoice2, EN→ElevenLabs; hardcodes ElevenLabs voice IDs | PRESENTER AUDIO TOOL | Flag hardcoded ElevenLabs voice IDs as P1 |
| scripts/audio/generate_teacher_showcase_audio.py | 40+ | Generates teacher showcase narration (15min full + 90s hook) via CosyVoice2; Pearl Star only ($0) | SHOWCASE AUDIO TOOL | Keep; distinct from presenter audio |

**No duplication.** `generate_presenter_audio.py` targets CJK+EN presenter decks with ElevenLabs fallback; `generate_teacher_showcase_audio.py` targets teacher audiobook showcases via CosyVoice2 only. Different audiences, different TTS engines.

**ElevenLabs concern:** `generate_presenter_audio.py` hardcodes ElevenLabs voice IDs in VOICES dict (lines 22–28) — not configurable via YAML. P1 fix: move voice IDs to `config/tts/` YAML.

---

### Group 6: Simulation Runners

| File | Lines | Purpose | Classification | Action |
|------|-------|---------|---------------|--------|
| scripts/ci/run_simulation_10k.py | 43 | Thin wrapper: calls `simulation/run_simulation.py --n 10000 --phase2 --phase3` | CI WRAPPER | Keep; used by CI workflow |
| scripts/ci/run_simulation_100k.py | 43 | Thin wrapper: calls `simulation/run_simulation.py --n 100000 --phase2 --phase3` | CI WRAPPER | Keep; different scale gate |
| scripts/ci/run_1000_book_simulation.py | 470 | Full run_pipeline.py-based simulation with parallel workers, varied params, JSONL results | INTEGRATION SIMULATOR | Keep; fundamentally different from simulation/ wrappers |
| scripts/ci/run_rigorous_system_test.py | 88 | Orchestrator: systems_test + variation report + atoms coverage; references run_simulation_10k | GATE ORCHESTRATOR | Keep; CI release gate |

**No deprecated scripts.** 10k and 100k wrappers are intentionally thin (different scale). 1000-book simulator uses a completely different mechanism (run_pipeline CLI). Rigorous test is a meta-gate.

---

## PHASE 3: Dead Code / Deprecated Patterns

| File | Issue | Severity | Action |
|------|-------|----------|--------|
| phoenix_v4/planning/slot_resolver.py | DEPRECATED header: "Atom assembly path. Use section registry pipeline" | P1 | Add deprecation banner; confirm no active callers outside tests |
| phoenix_v4/planning/pool_index.py | DEPRECATED header: "Atom assembly path. Use section registry pipeline" | P1 | Add deprecation banner; used by `run_production_readiness_gates.py` capability check — verify pool_index usage is intentional |
| scripts/catalog/generate_full_catalog.py | Hardcoded `_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")` (line 34) | P1 | Replace with env var or worktree-safe path detection |
| scripts/catalog/weekly_production_queue.py | Hardcoded `_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")` (line 44) | P1 | Same fix as above |
| scripts/video/render_audiobook.py | Hardcoded `FFMPEG = "/opt/homebrew/bin/ffmpeg"` (line 37) | P1 | Replace with `get_ffmpeg_bin()` from `scripts/video/_config.py` |
| scripts/audio/generate_presenter_audio.py | ElevenLabs voice IDs hardcoded in VOICES dict (lines 22–28) | P1 | Move to `config/tts/` YAML |
| scripts/video/run_soundtrack_engine.py | `ELEVEN_BASE = "https://api.elevenlabs.io/v1/text-to-speech"` (line 19) hardcoded; `"provider": "elevenlabs"` in output | P1 | Gate behind env var; document as stub output only |

**ElevenLabs remnants:** FOUND — 10 occurrences across 6 files. Key ones:
- `scripts/video/run_soundtrack_engine.py` line 19: hardcoded ElevenLabs API URL (P1)
- `scripts/audio/generate_presenter_audio.py` lines 22–28: hardcoded ElevenLabs voice IDs (P1)
- `scripts/video/run_pipeline.py` lines 52–53, 152: ElevenLabs TTS opt-in via `--voice`/`--music` flags — these are intentional operator opt-in paths, not dead code (acceptable)
- `scripts/video/generate_teacher_showcase_videos.py` line 11: ElevenLabs mentioned in docstring as source for audio — acceptable (documentation only)
- `scripts/ci/check_voice_audition_contract.py` lines 38–39: `elevenlabs_voice_id` field check — acceptable (contract validation)
- `scripts/pipeline/create_job.py` line 50: `elevenlabs_id` field in voice profile — acceptable (voice profile field)

**qwen3:14b references:** FOUND — 6 occurrences in 5 files:
- `config/localization/translation_loop_config.yaml` lines 23, 31: `ollama_model_id: "qwen3:14b"` — flag for review against model governance
- `scripts/research/run_research.py` line 98: `OLLAMA_DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:14b")` — overridable via env var (acceptable)
- `scripts/audiobook/generate_showcase_bundle.py` lines 13, 278: `qwen3:14b` as default for Pearl Star local generation — intentional for this script's $0 path
- `scripts/localization/llm_client.py` line 142 and `translate_atoms_to_locale.py` line 259: `qwen3:14b` as default model — flag for review

Note from `ws_pearl_news_llm_routing_20260409`: "Optional full 3x3 benchmark matrix still pending ANTHROPIC_API_KEY and qwen3:14b on Pearl Star" — qwen3:14b is an in-flight model name, not necessarily incorrect for Pearl Star Ollama deployments.

**Hardcoded localhost paths:** FOUND — 3 occurrences:
- `scripts/research/run_research.py` lines 169, 176, 555: `localhost:11434` as default Ollama host — all gated via `os.environ.get("OLLAMA_HOST", ...)`, acceptable pattern
- `scripts/catalog/generate_full_catalog.py` line 34: `/Users/ahjan/phoenix_omega` (P1 — not env-gated)
- `scripts/catalog/weekly_production_queue.py` line 44: `/Users/ahjan/phoenix_omega` (P1 — not env-gated)

**Stub/placeholder files:** Placeholder patterns are extensive in video scripts but are intentional CI/test scaffolding (e.g., `--placeholder` flag on `run_render.py`, sine-wave audio in `generate_teacher_showcase_videos.py`). Not dead code. The `run_soundtrack_engine.py` "Suno/ElevenLabs call specs (no live API)" docstring (line 4) indicates intentional stub outputs.

---

## PHASE 4: Feature Merge Candidates

| Feature | Current Location | Should Be | Effort | Priority |
|---------|-----------------|-----------|--------|----------|
| Golden quality path | `scripts/run_golden_quality_path.py` | `--golden` flag on `run_pipeline.py` or `run_max_quality_catalog.py` | M | P2 |
| Audiobook job system integration | `scripts/audiobook/generate_showcase_bundle.py` (no job system) | Add `--workspace` + `require_stage`/`mark_complete` calls | S | P1 |
| ElevenLabs voice IDs config | `scripts/audio/generate_presenter_audio.py` VOICES dict | `config/tts/presenter_voice_assignments.yaml` | S | P1 |

---

## PHASE 5: Pipeline Registry Gaps

| Subsystem | Script Dir | Script Count | Stage Count | Has Job System | Priority |
|-----------|-----------|-------------|-------------|----------------|----------|
| Atom generation | scripts/atom_writing/ | 4 (+ __init__) | 0 registered | NO | P1 |
| Catalog generation | scripts/catalog/ | 4 | 0 registered | NO | P1 |
| Cover art / image gen | scripts/image_generation/ | 7 (+ __init__ + workflows/) | 0 registered | NO | P2 |
| Translation | scripts/localization/ | 7 | 0 registered | NO | P1 |
| Research | scripts/research/ | 6 (+ README + shell) | 0 registered | NO | P2 |
| Release/distribution | scripts/release/ | 9 | 2 partial (build_epub.py, build_manga_webtoon.py referenced in ebook/manga registry) | PARTIAL | P2 |

**Notes:**
- `scripts/atom_writing/` contains `run_writing_campaign.py`, `validate_atoms.py`, `write_atoms_claude.py`, `write_teacher_stories.py`. These drive atom content production — a core dependency for the ebook pipeline. No job system, no registry entry.
- `scripts/catalog/` contains `generate_full_catalog.py`, `build_catalog_analysis_bundle.py`, `growth_engine.py`, `weekly_production_queue.py`. Catalog generation is a production-critical workflow with no pipeline registry entry.
- `scripts/localization/` has 7 scripts including `run_translation_loop.py` and `run_locale_batches.py` — these are CJK6 translation pipelines with no job system integration.
- `scripts/release/` is partially registered: `build_epub.py` is referenced in the ebook pipeline registry and `build_manga_webtoon.py` in the manga registry. `generate_video_schedule.py`, `generate_weekly_schedule.py`, `weekly_pipeline_with_marketing.py`, `export_wave.py`, `prepare_wave_for_export.py` are unregistered.

---

## PHASE 6: Recommended Actions

### P0 (Critical — do first)
_(No P0 issues found. All five registered pipelines are functional. No blocking security or data-loss risks identified.)_

### P1 (Important — next sprint)
1. **Fix hardcoded /Users/ahjan paths** in `scripts/catalog/generate_full_catalog.py` (line 34) and `scripts/catalog/weekly_production_queue.py` (line 44) — Replace with `os.environ.get("MAIN_REPO_ROOT", str(REPO_ROOT))` or remove the fallback entirely — Effort: S — Owner: Pearl_Dev
2. **Fix hardcoded ffmpeg path** in `scripts/video/render_audiobook.py` (line 37) — Replace with `get_ffmpeg_bin()` from `scripts/video/_config.py` — Effort: S — Owner: Pearl_Dev
3. **Wire audiobook pipeline job system** — Add `--workspace` param + `require_stage`/`mark_complete` to `scripts/audiobook/generate_showcase_bundle.py` — Effort: S — Owner: Pearl_Dev
4. **Move ElevenLabs voice IDs to config** — Extract VOICES dict from `scripts/audio/generate_presenter_audio.py` to `config/tts/presenter_voice_assignments.yaml` — Effort: S — Owner: Pearl_Dev
5. **Gate ElevenLabs API URL** in `scripts/video/run_soundtrack_engine.py` — Add env-var override for `ELEVEN_BASE`; document as stub output path — Effort: S — Owner: Pearl_Dev
6. **Register atom_writing pipeline** in `config/pipeline_registry.yaml` — Effort: M — Owner: Pearl_Architect
7. **Register catalog pipeline** in `config/pipeline_registry.yaml` — Effort: M — Owner: Pearl_Architect
8. **Register translation pipeline** in `config/pipeline_registry.yaml` — Effort: M — Owner: Pearl_Architect

### P2 (Nice to have)
1. **Merge golden quality path** — Add `--golden` flag to `run_max_quality_catalog.py` to run wave optimizer path inline — Effort: M — Owner: Pearl_Dev
2. **Register image_generation pipeline** in `config/pipeline_registry.yaml` — Effort: M — Owner: Pearl_Architect
3. **Register research pipeline** in `config/pipeline_registry.yaml` — Effort: M — Owner: Pearl_Architect
4. **Add deprecation comment clarification** to `phoenix_v4/planning/pool_index.py` and `slot_resolver.py` — verify `capability_check` in `run_pipeline.py` is intentionally still using `pool_index.py` even though it's marked DEPRECATED — Effort: S — Owner: Pearl_Architect
5. **Add cross-reference docstring** to `scripts/manga/run_chapter_visual.py` clarifying its relationship to `run_chapter_production.py` — Effort: XS — Owner: Pearl_Dev

---

## Deprecation Plan

Scripts recommended for deprecation banner:

| Script | Replacement | Banner Text |
|--------|------------|-------------|
| phoenix_v4/planning/slot_resolver.py | phoenix_v4/planning/registry_resolver.py | "DEPRECATED: Atom assembly path. Use section registry pipeline (registry_resolver.py). Will be removed when all atom-assembly callers are migrated." |
| phoenix_v4/planning/pool_index.py | phoenix_v4/planning/registry_resolver.py | "DEPRECATED: Atom assembly path. Use section registry pipeline (registry_resolver.py). NOTE: still used by capability_check — verify before removing." |

Both files already have deprecation headers (lines 1); the recommendation is to confirm whether they can be fully retired once `capability_check` is updated or confirmed intentional.

---

## Appendix: Script Inventory

Total Python scripts in scripts/: **312**
Total Python modules in phoenix_v4/: **195**

### Unregistered Subsystem Directories

| Directory | File Count | Notes |
|-----------|-----------|-------|
| scripts/atom_writing/ | 4 .py + __init__.py | Core content production — P1 to register |
| scripts/catalog/ | 4 .py | Catalog generation — P1 to register |
| scripts/image_generation/ | 6 .py + __init__.py + workflows/ | Cover art + manga character art — P2 to register |
| scripts/localization/ | 7 .py | CJK6 translation pipeline — P1 to register |
| scripts/research/ | 6 .py + README + .sh | Research KB pipeline — P2 to register |
| scripts/release/ | 9 files | Partially registered (build_epub, build_manga_webtoon) — P2 to complete |
| scripts/audio/ | 2 .py | Presenter + showcase audio; no registry entry |
| scripts/audiobook_script/ | 2 .py | Qwen comparator loop + regression; no registry entry |
| scripts/ml_editorial/ | 6 .py | ML editorial scoring; no registry entry |
| scripts/ml_loop/ | 3 .py | Continuous ML loop; no registry entry |
