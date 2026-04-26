# Manga Pipeline Audit — Phase 1 Synthesis

**Date:** 2026-04-26
**Author:** Pearl_Architect (synthesis) + Pearl_Research (parallel reads, 5 subagents) + Pearl_PM (catalog planning)
**Scope:** READ-only audit across `artifacts/research/manga_*` + `artifacts/research/webtoon_*` + `artifacts/research/strategic_audit/` + `docs/MANGA_*` + `docs/research/manga_craft/` + `specs/AI_MANGA_PIPELINE_SUMMARY.md` + `specs/manga_*` + `specs/MANGA_*` + `schemas/manga/` + `phoenix_v4/manga/` + `scripts/manga/` + `config/source_of_truth/manga_*` + `config/manga/` + `artifacts/manga/`
**Branch:** `agent/pearl-architect-manga-audit-20260426` from `origin/main` HEAD `0795235689`
**Deliverable status:** Phase 1 complete — recommendations land in §7 for operator approval before any execution work begins

---

## §1 — Executive summary

The Phoenix Omega manga pipeline is **operationally live for one episode in one locale** (`stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying` ep_001 — 38 PNG pages + 35 vertical webtoon strips rendered 2026-04-26 06:11–06:29). The end-to-end pipeline (chapter script → panel prompts → ComfyUI render → bubble render → webtoon compose) is validated by that single episode. Everything else in the catalog is configured but not produced.

**State of the manga pipeline today:**
- **Schemas:** v3.0.0 (`text_by_locale` multimarket-aware) is live on main. Schemas in `schemas/manga/` are well-organized and consumed by `phoenix_v4/manga/models/validation.py`.
- **Code:** 66 files / ~11,821 lines in `phoenix_v4/manga/`, ~30 LIVE modules. Recent PR cadence (#642–#678 over April) is healthy. No abandonment detected.
- **Specs:** 23 spec docs / 21,759 lines split across two cohorts: Apr 11 architecture suite (LIVE) and Apr 24 task-specific gates suite (mostly PARTIAL or ASPIRATIONAL).
- **Config:** 132 series plans + 716 book plans + 365 manga profiles generated from `MANGA_FULL_CATALOG_PLAN.md`. Coverage 4 locales × Ahjan strand only. 11 of 12 teachers have zero series plans yet.
- **Production:** ep_001 shipped to `artifacts/manga/`. ep_002 chapter script authored 2026-04-25 but no panel_prompts, no renders. PR #678 lettering fix is **open, not yet merged** — that is the active blocker.

**Top 5 strengths:**
1. **Transmission integrity chain is live and testable.** `chapter_runner.py` orchestrates a resumable DAG (writer_stub → visual_from_script_v3 → image_backend → lettering_from_script → bubble_render → page_compose → webtoon_compose → chapter_qc → series_memory_merge). This is the durable backbone.
2. **Schema v3 + locale_resolver give us 4-locale routing for free.** Once a chapter script is written + translated, all four locales render through the same code path.
3. **Research corpus is unusually deep.** Cover design (5 docs, ~600KB), dialogue systems (3 docs), strategic audit (3 docs), genre style bibles (10 craft files), webtoon technical reference, AI policy blocker matrix. We are *not* under-researched.
4. **Catalog plan is fully tabulated.** `MANGA_FULL_CATALOG_PLAN.md` defines 168 Ahjan series × 4 locales + 11 other teacher strands. Generators (`generate_series_plans_from_catalog.py`, `generate_book_plans_from_series.py`) are deterministic and re-runnable.
5. **AI policy is mapped.** ALLOWED platforms (KDP, Comic C'moA, GlobalComix), GREY platforms (WEBTOON Canvas, Bookwalker, Pixiv Comic), and BLOCKED platforms (Tapas, Shueisha/MangaPlus, Viz, Yen Press) are catalogued. No upload code targets blocked platforms.

**Top 5 gaps:**
1. **QC gate runner is not wired into chapter_runner.** `chapter_qc.build_revision_queue_for_chapter()` exists but is not invoked on every render. Gates are defined; they are not executed automatically. This is the largest active risk to catalog scaling.
2. **PR #678 lettering fix is open and unmerged.** It unblocks bubble rendering for v3-schema scripts. Without it, ep_002 cannot be rendered.
3. **Cover pipeline is largely aspirational.** Five Apr 24 cover specs (uniqueness engine, regulatory compliance, full assembly, pipeline integration, flux workflows) define an ambitious cover production engine; only minimal code references exist. Cover quality is currently best-effort, not gated.
4. **Eleven of twelve teachers have no series plans.** The Apr 13 catalog plan describes 12 teachers; only Ahjan's 168 series are generated. The remaining 11 teachers' plans, profiles, and character LoRAs are not staged.
5. **Chapter script production is throughput-bound.** Only 2 chapter scripts exist (ep_001 + ep_002 of one series). Catalog plan calls for ~14 chapters × 132 series × 4 locales = ~7,392 chapter scripts (Ahjan strand alone). Authoring is currently manual.

**The big decision the operator needs to make:**

**Do we ship before we scale?** Two paths converge on May:
- **Path A — Ship ep_001 to readers first.** Merge PR #678. Render ep_002. Push both to KDP and WEBTOON Canvas (en_US first; ja_JP/zh_TW/zh_CN as translation lands). Use real reader signal to inform §7 priorities. *Pro:* Validates the system end-to-end with public feedback. *Con:* Defers the gate runner + cover pipeline + mass scripting work.
- **Path B — Wire the gate runner + cover pipeline before scaling.** Treat the audit prune list (§4) and gate runner (§7 Sprint 2B) as blockers before any catalog ramp. *Pro:* Avoids producing 100+ chapters without QC enforcement. *Con:* Pushes first reader contact further out.

These are not mutually exclusive (Path A is one ep_001 unblock + a Canvas upload script; Path B is structural), but the operator needs to call the order. The audit recommends **Path A on the en_US ep_001/ep_002 lane in parallel with Path B on the gate runner** — see §7 for the integrated sprint sequence.

---

## §2 — Inventory

The five subagent reads cover the corpora separately. Tables below are summarized; the per-corpus subagent reports remain in transcript for full per-file detail.

### §2.1 — Research corpus (`artifacts/research/`)

Per-corpus tables; verdicts: **KEEP** (governs future work), **KEEP-NICHE** (still useful, narrow scope), **REDUNDANT** (superseded), **OUTDATED** (date stamped, obsolete), **UNREAD** (subagent A hit token limits).

| File | Lines | Date | Verdict | Why |
|------|------|------|---------|-----|
| `manga_genre_writing_styles_2026_04_04.md` | ~1300 | 2026-04-04 | KEEP | 10-genre playbook with pacing metrics (shōnen 30–80 wpp; seinen 40–120 wpp; shōjo 50–130 wpp). Direct input to Chapter Writer. |
| `webtoon_therapeutic_scroll_craft_2026-04-25.md` | ~600 | 2026-04-25 | KEEP | Form-as-substrate thesis. Latest. Polyvagal-grounded scroll cadence. |
| `webtoon_technical_reference_2026-04-25.md` | ~500 | 2026-04-25 | KEEP | 800×1280px JPEG spec + 2× supersample. Bridge to `webtoon_compose.py`. |
| `webtoon_master_reference_2026-04-25.md` | ~800 | 2026-04-25 | KEEP | Canon webtoon reference. Cross-cutting decisions: schema v3.0.0, FONT_REGISTRY rebuild CJK-first, SVG vector bubbles, vertical-strip composer, Scroll Therapeutic Test gate. **Hard signal:** WEBTOON Canvas has no public upload API and is TOS-grey for AI content. |
| `webtoon_japan_market_rakuten_ai_2026-04-25.md` | ~400 | 2026-04-25 | KEEP | LINE Manga Indies + Piccoma + Bookwalker breakdown for ja_JP. Dual-format strategy guidance. |
| `webtoon_compositing_lettering_2026-04-25.md` | ~400 | 2026-04-25 | KEEP | Direct input to `webtoon_compose.py` and `lettering_from_script.py`. |
| `manga_vs_webtoon_economics_2026-04-25.md` | ~300 | 2026-04-25 | KEEP | Webtoon CAGR 28–34%; B&W Japan revenue dominance; Piccoma ¥105B annual. Justifies 55–65% color-vertical allocation. |
| `manga_vs_webtoon_decision_matrix_2026-04-25.yaml` | (yaml) | 2026-04-25 | KEEP-CANON | **Definitive 5-locale format allocation.** 58% color vertical webtoon / 24% B&W page / 14% color page / 4% self-help. Includes ko_KR as 5th locale (operator scope is 4 — **see §8 OQ-1**). |
| `MANGA_CATALOG_GAP_ANALYSIS.md` | ~300 | 2026-04-* | KEEP | System-layer gap analysis. Recommends taxonomy expansion, anti-homogeneity tracking, female-reader grammar. |
| `MANGA_READER_PROMISES.md` | ~200 | 2026-04-* | KEEP-NICHE | Reader-promise contracts per genre. |
| `MANGA_QA_RUBRIC.md` | ~300 | 2026-04-* | KEEP | QA scoring rubric. Should govern the §7 gate-runner implementation. |
| `INTEGRATION_LOG.md` | ~200 | 2026-04-* | KEEP-NICHE | Integration touchpoints log. |
| `ai_policy_blocker_audit_2026-04-25.md` | ~400 | 2026-04-25 | KEEP-CANON | Platform-by-platform AI-content posture: ALLOWED (KDP, Comic C'moA, GlobalComix), GREY (WEBTOON Canvas, Bookwalker, Pixiv Comic), BLOCKED (Tapas, Shueisha/MangaPlus, Viz, Yen Press). Source of truth for upload-target gating. |
| `manga_cover_design/01_japan_by_genre.md` | 1831 | 2026-04-26 | KEEP-CANON | UNREAD by subagent A (token limits). Headings indicate per-genre cover layout templates, color palette recipes, typography pairings, character pose libraries, anti-pattern lists. **Direct input to FLUX/ComfyUI cover generation.** |
| `manga_cover_design/02_japan_publisher_house_styles.md` | 855 | 2026-04-26 | KEEP-CANON | UNREAD. 8 major Japanese publishers (Shūeisha, Kodansha, …). Visual identity at thumbnail scale, logo design, title typography, spine/back cover. |
| `manga_cover_design/03_global_markets.md` | 1377 | 2026-04-26 | KEEP-CANON | UNREAD. Non-Japan markets including Taiwan/HK (zh_TW), Mainland China (zh_CN). Direct input to multi-locale cover variants. |
| `manga_cover_design/04_typography_system.md` | 1851 | 2026-04-26 | KEEP-CANON | UNREAD. Full Japanese display + title font categories (fude, mincho, gothic, modern display). Vertical/horizontal stacking. Furigana on covers. |
| `manga_cover_design/09_bestseller_cover_analysis.md` | 1993 | 2026-04-26 | KEEP-CANON | UNREAD. Cross-market bestseller cover pattern decomposition. Oricon 2024–2025 sample. |
| `manga_dialogue_system/01_visual_dialogue_systems.md` | 620 | 2026-04-26 | KEEP-CANON | UNREAD. Per-genre bubble shapes, tail styles, typography conventions, text direction, SFX, caption boxes, spatial rules. **Direct input to `bubble_render.py`.** |
| `manga_dialogue_system/02_dialogue_vocabulary_patterns.md` | 667 | 2026-04-26 | KEEP-CANON | UNREAD. 11-genre speech register analysis (shōnen, shōjo, seinen, josei, kodomomuke, isekai, horror, sports, slice-of-life/iyashikei, BL/GL, mecha). |
| `manga_dialogue_system/03_programmatic_lettering_approaches.md` | 1103 | 2026-04-26 | KEEP-CANON | UNREAD. Professional tools (Clip Studio, InDesign), open-source (Panel Cleaner, Manga-OCR, BalloonTranslator, OpenCV, WebtoonKit), academic approaches. **Should inform any future automation of the lettering pipeline.** |
| `manga_quality_bar/01_iyashikei_craft_study.md` | 501 | 2026-04-26 | KEEP-CANON | UNREAD. Series analyses (Yotsuba&!, Barakamon, March Comes In Like a Lion, Mushishi, Flying Witch, Non Non Biyori, Hidamari Sketch, A Bride's Story). 5 defining craft moves of iyashikei. |
| `manga_quality_bar/02_studio_workflow_gap_analysis.md` | 538 | 2026-04-26 | KEEP-CANON | UNREAD. Compares professional manga studio pipeline (9 stages) with Phoenix Omega current pipeline. **Likely the single best diagnostic for what we're missing.** |
| `strategic_audit/01_global_manga_market_map.md` | 333 | 2026-04-18 | KEEP | Japan domestic market + US market maps. Platform dominance + bestseller patterns. Inputs for §6 catalog plan. |
| `strategic_audit/02_bestseller_pattern_decomposition.md` | 397 | 2026-04-18 | KEEP | Iyashikei + essay manga commercial pipeline. Flagship example: My Lesbian Experience with Loneliness. |
| `strategic_audit/06_competitive_landscape.md` | 325 | 2026-04-18 | KEEP-NICHE | "Manga Guide to X" (No Starch Press). Korean healing manhwa (Naver/Kakao). AI-assisted manga competitors. |

**Research corpus totals:** ~13–17 single files + 4 subdirs (13 files) = ~26–30 files. Total estimated lines ~25,000.

**Audit limitation surfaced:** Subagent A returned with the 4 subdirs (13 files, ~600KB) **unread** due to its token budget. Headings + line counts have been captured by direct inspection; full content remains to be parsed. **None of these subdirs are prune candidates** — all are recent (2026-04-26 mtime) and reference future implementation work. They land as KEEP-CANON in the inventory and feed §7 sprints 2E (cover pipeline) and 2H (bubble render).

### §2.2 — Docs corpus (`docs/MANGA_*` + `docs/research/manga_craft/` + `docs/sessions/` + `docs/manga_tech_notes.txt` + `docs/deep_research_manga_*.txt`)

| File | Lines | Date | Verdict | Why |
|------|------|------|---------|-----|
| `docs/MANGA_PIPELINE_COMPLETE_GUIDE.md` | 59 | 2026-04-26 | KEEP-CANON | Operator quick reference + entry points. |
| `docs/MANGA_FONT_REGISTRY.md` | 109 | 2026-04-26 | KEEP-CANON | CJK font infra + FONT_REGISTRY v2 authority. |
| `docs/MANGA_GTM_PLAN.md` | 229 | 2026-04-26 | KEEP-CANON | 3-region tier strategy. EI v2 quality gates (therapeutic ≥0.60, safety ≥0.95). Year 1 targets: 50 titles / 8 platforms / 6 markets / $120K–$240K. |
| `docs/MANGA_CJK_SHAPING.md` | 140 | 2026-04-26 | KEEP-CANON | HarfBuzz Phase 2A live; Phase 2B integration pending; Phase 2C vertical CJK B&W pages. |
| `docs/MANGA_CATALOG_VOLUME_AND_ASSETS_HANDOFF_2026_04_17.md` | 186 | 2026-04-26 | KEEP-CANON | Inventory + gaps + next-actions. **Lettering gap surfaced here first** (Apr 17). |
| `docs/MANGA_PIPELINE_ONBOARDING.md` | 341 | 2026-04-26 | KEEP-CANON | Developer onboarding. Architecture diagram. Schema cross-reference. T-01..T-20 ITE QC gate registry. Quick-start with fixture-replay. |
| `docs/MANGA_IMPLEMENTATION_OUTLINE.md` | 171 | 2026-04-26 | KEEP-CANON | Operational bridge. Phase 0–1 chapter artifact contracts + transmission splitter. |
| `docs/sessions/SESSION_HANDOFF_2026-04-25.md` | 607 | 2026-04-26 | KEEP-CANON | **The runbook.** 26 PRs merged. 10-min operator activation path. 14-item explicit backlog. Risk register snapshot (R-1 WEBTOON-API HIGH; R-3 Pillow-CJK MED; R-11 dashboard-UI HIGH). |
| `docs/research/manga_craft/index.md` | 46 | 2026-04-26 | KEEP-CANON | Genre style bible navigation. References 10 craft lanes. |
| `docs/research/manga_craft/iyashikei_minimalism.md` | 86 | 2026-04-26 | KEEP-CANON | Genre bible. Panel scaffolding (7 fields). Failure modes. Per-volume shape. |
| `docs/research/manga_craft/shojo_romance.md` | 83 | 2026-04-26 | KEEP-CANON | Panel scaffolding (8 fields). Failure modes. 48-vol shape. |
| `docs/research/manga_craft/<other 8 craft bibles>` | (unread) | 2026-04-26 | KEEP-CANON | BL, graphic_novel, josei, kodomomuke, seinen_psychological, shonen_encouragement, webtoon_vertical_drama, webtoon_vertical_romance — index references all 10. Subagent B read 2 in detail; remaining 8 should follow same panel-scaffolding pattern. |
| `docs/manga_tech_notes.txt` | 2053+ | 2026-04-26 | KEEP-CANON | Agent architecture. ComfyUI design. Long-running design diary. |
| `docs/deep_research_manga_deepseek.txt` | 20345+ | 2026-04-26 | KEEP-CANON | Market intelligence corpus. Gen Z 15–45s hook; Gen Alpha 8–15s rapid visual; 8 style archetypes; 90-day exec roadmap. |
| `docs/MANGA_MODE_STRATEGY.docx` | (binary) | various | UNCLASSIFIED | Binary docx. Not opened in this audit. **See §8 OQ-7** for whether to migrate to Markdown. |

**Docs corpus totals:** ~14 markdown + 2 text + 1 docx = ~17 files. Total estimated lines ~26,000+ (deep_research_manga_deepseek alone is 20K+).

**Subagent B verdict:** Zero docs marked REDUNDANT or OUTDATED. All 13 read-in-full are KEEP-CANON. Strategic layering by audience (operator / developer / architect / market researcher / craft-lane practitioner) is intentional, not duplicative. **The docs tree does not need pruning.**

**Catalog plan reference at `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md`** (19,383 bytes, 2026-04-26): tabulates 12 teachers × 4 locales × 18–24 series each. Headings: "Locations & Languages", "Teachers (12)", "CATALOG BY TEACHER × LOCATION" (sections 1–12), "GRAND TOTAL", "Genre Distribution by Teacher Tradition", "Production Pipeline Per Title". This file lives in `artifacts/`, not `docs/`, but is the source of truth for §6.

### §2.3 — Specs corpus (`specs/`)

23 spec docs / 21,759 lines. Two timestamp cohorts.

**Cohort 1 — Apr 11 architecture suite (11 files, ~6,950 lines):**

| File | Lines | Status | Code refs | Verdict |
|------|------|--------|-----------|---------|
| `AI_MANGA_PIPELINE_SUMMARY.md` | 354 | LIVE | 2 | **CANONIZE** — master reference. Transmission integrity chain. 7-agent + 2 cross-cutting. |
| `MANGA_PRODUCTION_PIPELINE_SPEC.md` | 1412 | PARTIAL | 1 | KEEP — operational envelope. Cost model is aspirational; orchestration partial. |
| `MANGA_MODE_SYSTEM_SPEC.md` | 1415 | ASPIRATIONAL | **0** | **PRUNE** (§4 candidate). Mode enforcement already distributed across agent specs. Zero callers. |
| `MANGA_GENRE_AGENT_SPEC.md` | 546 | LIVE | 3 | KEEP — referenced in story_architect; genre_blueprint generation implemented. |
| `MANGA_CHAPTER_WRITER_SPEC.md` | 854 | LIVE | 5 | **CANONIZE** — core agent. Producing chapter_script.json across all series. |
| `MANGA_STORY_ARCHITECT_SPEC.md` | 841 | LIVE | 4 | KEEP — Transmission Splitter live. Fix 1–4 patches integrated. |
| `MANGA_SERIES_BIBLE_SPEC.md` | 816 | PARTIAL | 2 | KEEP — series structure formula live; TikTok clip extraction aspirational. |
| `MANGA_TEACHING_LIBRARY_SPEC.md` | 594 | LIVE | 4 | **CANONIZE** — wisdom atom source. 20+ seed atoms. Core IP. |
| `MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` | 603 | ASPIRATIONAL | **0** | **PRUNE** (§4 candidate). 30-brand fingerprint matrix. No anti-spam engine implemented. |
| `MANGA_TEXT_RENDERING_SPEC.md` | 1330 | PARTIAL | 2 | KEEP — basic rendering live; clarity_mode/authentic_mode toggle is spec-only (default authentic). |
| `MANGA_LAYOUT_AGENT_SPEC.md` | 910 | LIVE | 6 | KEEP — layout compositing live. Page type enums implemented. Webtoon fallback verified. |

**Cohort 2 — Apr 24 task-specific gates suite (12 files, ~7,500+ lines):**

| File | Lines | Status | Code refs | Verdict |
|------|------|--------|-----------|---------|
| `MANGA_AUTHOR_SYSTEM_SPEC.md` | 672 | ASPIRATIONAL | **0** | **PRUNE** (§4 candidate). Collaborative editing UI/API. Not core pipeline. |
| `manga_visual_quality_gates.md` | 914 | PARTIAL | 1 | **CANONIZE** — MQG-02 (silence density) live; MQG-01, MQG-03..08 are spec-ready, not wired. **§7 Sprint 2C target.** |
| `manga_speech_atom_taxonomy.md` | 434 | LIVE | 5 | **CANONIZE** — selection engine live. Cooldown + forbidden_after enforced. Matrix validated. |
| `manga_ei_v2_dialogue_gates.md` | 906 | ASPIRATIONAL | **0** | KEEP — MDLG-01..05 fully specified, zero integration. **§7 Sprint 2D target** (do not prune; this is implementation-ready). |
| `manga_cover_uniqueness_engine.md` | 1345 | ASPIRATIONAL | 1 | KEEP — minimal `covers/__init__.py` reference. No fingerprint hashing or diversity scoring yet. **Defer pending §6 cover pivot decision.** |
| `manga_cover_regulatory_compliance.md` | 928 | ASPIRATIONAL | 0 | KEEP — no moderation engine. Manual editorial review currently. Defer. |
| `manga_cover_full_assembly.md` | 1114 | ASPIRATIONAL | 0 | KEEP — full assembly pipeline not implemented. Basic cover generation exists but does not follow spec. Defer. |
| `manga_cover_pipeline_integration.md` | 1055 | ASPIRATIONAL | 0 | KEEP — workflow described; actual implementation is linear with no gates. Defer. |
| `manga_cover_flux_workflows.md` | 1326 | PARTIAL | 2 | KEEP — FLUX calls live; per-style tuning minimal. Latency targets unmonitored. |
| `manga_name_thumbnail_stage.md` | 560 | PARTIAL | 2 | KEEP — Name Stage exists; MQG gates partially wired; cost optimization manual. |
| `manga_character_setting_consistency.md` | 786 | LIVE | 3 | KEEP — `series_memory.json` is the implementation. QC Agent updates it. Continuity checks active. |
| `manga_bubble_rendering_engine.md` | 1175 | PARTIAL | 1 | KEEP — bubble rendering live; OCR purity check documented but rarely runs (manual trigger). |

**Schemas (`schemas/manga/`):** 27 JSON Schema files. Core LIVE schemas: `manga_common.schema.json`, `series_plan.schema.json` (v2.0.0, Apr 25), `book_plan.schema.json` (v2.0.0, Apr 25), `lettering_spec.schema.json` (v3.0.0 with `silence_confirmed`, Apr 25), `series_memory.schema.json`, `panel_prompts.schema.json`, `anchor_panels.schema.json`, `story_architecture_internal.schema.json`, `chapter_request.schema.json`, `genre_blueprint.schema.json`. **No prune candidates** — all are referenced in code or tests.

### §2.4 — Code modules (`phoenix_v4/manga/`, `scripts/manga/`)

`phoenix_v4/manga/` — 66 files / ~11,821 lines.

| Path | Lines | Status | Notes |
|------|------|--------|-------|
| `runner/chapter_runner.py` | 586 | **LIVE** | Resumable chapter DAG. Entry called by `scripts/manga/run_manga_chapter.py`. |
| `chapter/chapter_production.py` | 136 | **LIVE** | Chapter workflow: prompts → lettering → bubble → pages. |
| `chapter/visual_from_script_v3.py` | 252 | **LIVE** | FLUX panel_prompts compiler. PR #655. ep_001 ready. |
| `chapter/lettering_from_script.py` | 222 | **LIVE** (PR #678 fix in flight) | v3-schema-aware. **PR #678 OPEN, not merged.** Required for ep_002. |
| `chapter/bubble_render.py` | 282 | **LIVE** | Speech bubble rendering. PR #648 locale_resolver integration. |
| `chapter/cjk_text_shaper.py` | 145 | **LIVE** | HarfBuzz + Pillow fallback. Phase 2A. PR #654. |
| `chapter/webtoon_compose.py` | 198 | **LIVE** | Vertical-strip composer. PR #650. **Verify wiring** (subagent D recommended). |
| `chapter/page_compose.py` | 156 | **LIVE** | Final page PNG composition. |
| `chapter/locale_resolver.py` | 89 | **LIVE** | Multi-locale text resolution. |
| `qc/chapter_qc.py` | 252 | **LIVE-but-NOT-WIRED** | Gates defined; **`build_revision_queue_for_chapter()` not invoked from chapter_runner**. **§7 Sprint 2B target.** |
| `qc/gate_registry.py` | 54 | LIVE | Loads `manga_gates.yaml`. |
| `qc/pacing_gates.py` + `restraint_gate.py` + `yearning_gate.py` | ~200 total | LIVE | MDLG-09b audit remediation. PRs #524, similar. |
| `chapter/writer_stub.py` | 165 | **STUB** (intentional) | Deterministic mapper. No LLM writer. **§7 Sprint 2I target** (replace with Claude SDK call when LLM Tier 1 is approved). |
| `sdf/stub.py` | 28 | **ORPHAN** | **PRUNE** (§4 candidate). Never imported. Returns empty dict. |
| `chapter/visual_from_script.py` (v2) | 198 | LEGACY-LIVE | Still imported by `lettering_from_script` for v2 compat. **Keep until ep_001 v2 → v3 migration complete.** |
| `ite_pipeline.py` | 156 | LIVE | ITE scoring (color arc, gutter, breath, fractal). |
| `image_backend.py` | 187 | LIVE | Panel image manifest (replay/noop modes). |
| `translation/translators.py` | 134 | LIVE | Tier-2 Qwen `text_by_locale` auto-fill. PR #652. |
| `series/story_architect.py` | 189 | LIVE | Series narrative strategy from profiles. |
| `covers/{cover_assembler,cover_generator,cover_selector}.py` | ~280 total | LIVE | Cover subsystem. Stub-level. |
| `models/{validation,paths,stage_ids,workspace_layout}.py` | ~150 total | LIVE | Validation + path infrastructure. |
| `panel_prompt_manifest.py`, `asset_resolver.py`, `transmission.py` | ~180 total | LIVE | Artifact registration + transmission. |

`scripts/manga/` — execution layer.

| Path | Status | Notes |
|------|--------|-------|
| `run_manga_chapter.py` | **LIVE** entry | Resumable chapter DAG. CI invokes via `.github/workflows/manga-pipeline.yml`. |
| `build_panel_prompts.py` | **LIVE** entry | v3 chapter_script → panel_prompts.json. |
| `render_ep001_panels_local_comfy.py` | **LIVE** entry (NEW 2026-04-26) | Local ComfyUI HTTP API fallback. Used to render ep_001. |
| `generate_series_plans_from_catalog.py` | LIVE entry | Generated 132 series plan YAMLs. PR #643. |
| `generate_book_plans_from_series.py` | LIVE entry | Generated 716 book plan YAMLs. PR #646. |
| `translate_chapter_script.py` | LIVE entry | Multi-locale translation. PR #652. |
| `check_font_registry.py` | LIVE entry | CJK font registry validation. PR #647. |
| `migrate_lettering_v2_to_v3.py` | ACTIVE | One-shot migration. Will be ARCHIVED after migration completes. |
| `validate_catalog_plan.py` | LIVE | Catalog bounds + homogeneity checks. CI gate. |
| `ite_qc.py` | LIVE | ITE gates test runner. Manual debugging. |
| `build_manga_catalog.py` | LIVE | Catalog rebuild with schema v2. |
| `validate_manga_series_catalog_bounds.py` | LIVE | Helper for `validate_catalog_plan`. |
| `install_manga_fonts.sh` | LIVE | CJK font acquisition (macOS / Linux / apt). |
| `manga_asset_estimator.py` | LIVE | Asset cost calculator. |
| `stilness_press_image_bank.py` | LIVE | Brand-specific image bank (840 assets, 9 topics). |
| `forensic_quality_sprint.py` | LIVE-niche | Artifact teardown debugging. |
| `smoke_post_publish.py` | LIVE | Post-publish artifact verification. |
| `r2_manga_release.py` | LIVE | Cloudflare R2 release staging. |
| `run_chapter_production.py` | **ARCHIVED-CANDIDATE** | **PRUNE** (§4 candidate). Legacy wrapper. Subsumed by `run_manga_chapter.py`. |
| `run_chapter_visual.py` | **ARCHIVED-CANDIDATE** | **PRUNE** (§4 candidate). Isolated test driver. |
| `run_asset_resolver.py` | **ARCHIVED-CANDIDATE** | **PRUNE** (§4 candidate). Isolated test driver. |
| `run_prompt_compiler.py` | **ARCHIVED-CANDIDATE** | **PRUNE** (§4 candidate) (if exists; subagent D flagged). |
| `run_series_setup.py` | **ARCHIVED-CANDIDATE** | **PRUNE** (§4 candidate). Subsumed by chapter_runner. |
| `manga_character_sheet_stub.py` | STUB (50 lines, placeholder) | **PRUNE-OR-IMPLEMENT** (§4 candidate, low priority). |
| `manga_series_pitch.py` | STUB (50 lines, placeholder) | **PRUNE-OR-IMPLEMENT** (§4 candidate, low priority). |

### §2.5 — Config + catalog state

| Path | Files | Notes |
|------|------|-------|
| `config/source_of_truth/manga_series_plans/` | **132** YAMLs | en_US: 42, ja_JP: 42, zh_TW: 24, zh_CN: 24. All Ahjan strand. Apr 25. |
| `config/source_of_truth/manga_book_plans/` | **716** YAMLs (in 48+ subdirs) | Episode breakdowns. zh_TW + zh_CN largely populated; en_US + ja_JP partially. |
| `config/source_of_truth/manga_profiles/` | **365** YAMLs across 40 profile families | EI character-author profiles + teaching cores + character archetypes. |
| `config/source_of_truth/manga_story_strategies/` | 4 files | shōnen, seinen, shōjo, combinatorial_index. |
| `config/source_of_truth/manga_cover_layers/` | 1 brand (Stillness Press only) | **Gap:** 11 brands stubbed. |
| `config/source_of_truth/manga_speech_atoms/` | schema only, **no atoms populated** | **Gap:** CJK6 translation pipeline not signaled here. |
| `config/source_of_truth/manga_series_examples/` | 1 example (`the_garden_at_tidecalm.yaml`) | Minimal. |
| `config/manga/` | 18 operational YAMLs | gate_registry, manga_gates, brand_illustration_styles, genre_ite_profiles, manga_taxonomy, panel_layouts, format_routing, brand_lora_plans, sabido_roles, teacher_character_prompts, japan_dual_track_config, korea_webtoon_config, asset_selection_priority, manga_pacing_by_genre, vertical_scroll_webtoon, bw_page_rtl, color_page, self_help_illustrated. |

**Production artifacts (`artifacts/manga/`):**

| Path | Status |
|------|--------|
| `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | 19,383 bytes. The catalog source-of-truth doc. |
| `artifacts/manga/chapter_scripts/` | **2 scripts** for 1 series. ep_001 (15.6 KB, 2026-04-26) + ep_002 (21 KB, 2026-04-25). All `the_alarm_is_lying`. |
| `artifacts/manga/panel_prompts/` | **1 panel_prompts.json** (ep_001 only). ep_002 not generated. |
| `artifacts/manga/ep_001/` | **38 PNG pages** (ep001_001..ep001_038). 2026-04-26 06:11–06:13. ~30 MB. |
| `artifacts/manga/ep_001_strips_en_US/` | **35 vertical webtoon strips** (JPG). 2026-04-26 06:10. |
| `artifacts/manga/ep_001_bubbled_en_US/` | 18 dirs (bubble layer). |
| `artifacts/manga/ep_001_composed_input/` | 37 dirs (composition inputs). |
| `artifacts/manga/anxiety_series/` | 18 dirs (older test outputs — possibly archive candidate, see §4). |
| `artifacts/manga/stillness_press_qa_run/` | QA artifacts from 2026-04-24. |

**Coordination state (`coordination/`):** **Directory does not exist** in this branch. CLAUDE.md mentions `coordination/projects.tsv` and `coordination/workstreams.tsv`; subagent E confirmed they are not in the repo tree. **See §8 OQ-2** for whether to surface this as missing infrastructure or whether the coordination layer lives elsewhere.

**Counts summary:**
- Research files: ~26–30 (13+ in subdirs alone)
- Docs files (manga-scoped): ~17
- Specs: 23
- Schemas: 27
- Code modules in `phoenix_v4/manga/`: 66 files
- Code scripts in `scripts/manga/`: ~24+
- Config YAMLs (manga_*): 132 series + 716 book + 365 profiles + 18 manga config + 1 cover_layers + others = **1,222+ files**
- Artifact directories under `artifacts/manga/`: ~10 top-level

---

## §3 — Best-of (what to keep + elevate)

The 5 subagents converged on a small set of artifacts that should govern future work. The audit recommends elevating these to canonical-anchor status. Future PRs that contradict any of these without explicit approval should be governance-blocked.

### §3.1 — Top 10 most valuable artifacts across all corpora

1. **`docs/sessions/SESSION_HANDOFF_2026-04-25.md`** — *Single source of truth for production status.* 26 PRs merged, 10-min activation path, 14-item backlog, risk register. Bridges all other docs into actionable state. **Use as the operator runbook for every catalog cycle.**
2. **`specs/AI_MANGA_PIPELINE_SUMMARY.md`** — *System architecture canon.* Transmission integrity chain. 7 agents + 2 cross-cutting systems. **No downstream spec, code, or PR may contradict this without explicit governance approval.**
3. **`artifacts/research/manga_vs_webtoon_decision_matrix_2026-04-25.yaml`** — *Definitive 5-locale format allocation.* Drives format routing (`config/manga/format_routing.yaml`) and platform targeting per locale.
4. **`artifacts/research/webtoon_master_reference_2026-04-25.md`** — *Canon webtoon reference.* The cross-cutting decisions (schema v3, FONT_REGISTRY rebuild, SVG vector bubbles, vertical-strip composer, Scroll Therapeutic Test gate) all trace to this doc.
5. **`artifacts/research/ai_policy_blocker_audit_2026-04-25.md`** — *Platform AI-content posture matrix.* Dictates which platforms we may publish to and which we must not. Do not push to BLOCKED platforms; wrap GREY platforms in disclosure.
6. **`artifacts/manga/MANGA_FULL_CATALOG_PLAN.md`** — *Catalog source-of-truth.* 12 teachers × 4 locales × 18–24 series. Driver of `generate_series_plans_from_catalog.py`.
7. **`docs/MANGA_PIPELINE_ONBOARDING.md`** — *Developer onboarding canon.* Schema cross-reference. Gate registry. Quick-start with fixture-replay.
8. **`docs/research/manga_craft/index.md`** + **10 craft bibles** — *Genre style bibles.* Per-genre panel scaffolding (6–9 fields per panel). Direct input to LLM prompt compilation. Iyashikei and shōjo are read in detail; the other 8 follow the same pattern.
9. **`specs/MANGA_CHAPTER_WRITER_SPEC.md`** + **`specs/MANGA_TEACHING_LIBRARY_SPEC.md`** + **`specs/manga_speech_atom_taxonomy.md`** — *The transmission triangle.* Wisdom atoms (Teaching Library) + atom selection (Speech Atom Taxonomy) + dialogue generation (Chapter Writer). Together they govern every word that ends up in a bubble.
10. **`phoenix_v4/manga/runner/chapter_runner.py`** — *The pipeline backbone.* 586 lines, resumable DAG, all stages dispatched here. Any new stage or gate must integrate with this runner.

### §3.2 — Canonical anchors (the 3–5 specs/docs that govern everything else)

The audit recommends these five be tagged **CANONICAL** in `docs/DOCS_INDEX.md` (a future PR — out of scope for this audit):

1. **`specs/AI_MANGA_PIPELINE_SUMMARY.md`** — pipeline architecture
2. **`docs/sessions/SESSION_HANDOFF_2026-04-25.md`** — production runbook
3. **`artifacts/manga/MANGA_FULL_CATALOG_PLAN.md`** — catalog scope
4. **`artifacts/research/manga_vs_webtoon_decision_matrix_2026-04-25.yaml`** — format allocation
5. **`artifacts/research/ai_policy_blocker_audit_2026-04-25.md`** — platform posture

These five together tell a new contributor: *what we're building, what we've built, what we'll build next, what shape it takes, and where we may publish.*

---

## §4 — Prune list (DRAFT — operator approves before deletion in Phase 2)

**Total proposed for deletion: 11 files. Below the 30-file segmentation threshold; one PR is sufficient. Below the 50-file CLAUDE.md mass-deletion threshold; no special owner sign-off needed.**

The list separates **safe** (zero callers, fully superseded) from **requires-verify** (needs an additional grep before delete) from **contentious** (operator should weigh in).

### §4.1 — Safe to delete (zero callers, fully superseded)

| # | Path | Lines | Last touched | Why prune | Risk |
|---|------|------|--------------|-----------|------|
| 1 | `phoenix_v4/manga/sdf/stub.py` | 28 | 2026-04-11 | Returns empty dict. Never imported. SDF conditioning is unimplemented and not on roadmap. | SAFE |
| 2 | `scripts/manga/run_chapter_production.py` | 94 | 2026-04-11 | Legacy wrapper. Subsumed by `run_manga_chapter.py` (the unified entry). All functionality moved to `chapter_runner`. | SAFE |
| 3 | `scripts/manga/run_chapter_visual.py` | (~70) | 2026-04-11 | Isolated module test driver. Subsumed by `run_manga_chapter.py`. | SAFE |
| 4 | `scripts/manga/run_asset_resolver.py` | (~70) | 2026-04-11 | Isolated module test driver. Subsumed by `run_manga_chapter.py`. | SAFE |
| 5 | `scripts/manga/run_series_setup.py` | (~70) | 2026-04-11 | Isolated module test driver. Subsumed by `run_manga_chapter.py`. | SAFE |

### §4.2 — Requires verify before delete (likely orphaned, want one more grep)

| # | Path | Lines | Last touched | Why prune | Verify before delete |
|---|------|------|--------------|-----------|----------------------|
| 6 | `scripts/manga/run_prompt_compiler.py` (if exists) | (~70) | 2026-04-11 | Subagent D flagged. Confirm existence with `ls scripts/manga/run_prompt_compiler.py`. | SAFE-once-verified |
| 7 | `scripts/manga/manga_character_sheet_stub.py` | ~50 | 2026-04-24 | Placeholder. No business logic. | Confirm no script imports it before delete. |
| 8 | `scripts/manga/manga_series_pitch.py` | ~50 | 2026-04-24 | Placeholder. No business logic. | Same — confirm no imports. |

### §4.3 — Contentious (operator should weigh in)

| # | Path | Lines | Why this is contentious |
|---|------|------|-------------------------|
| 9 | `specs/MANGA_MODE_SYSTEM_SPEC.md` | 1415 | Subagent C flagged: zero code refs; mode enforcement is already distributed across agent specs. **But the spec is 1,415 lines of design thinking that may inform future mode-switching work.** Operator should choose: (a) prune outright, (b) move to `specs/archive/`, (c) keep but tag DEFERRED in DOCS_INDEX. |
| 10 | `specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` | 603 | Same. Zero code refs; no anti-spam engine. Same a/b/c choice. Anti-homogeneity tracking is recommended in `MANGA_CATALOG_GAP_ANALYSIS.md` — this spec partially overlaps that recommendation. |
| 11 | `specs/MANGA_AUTHOR_SYSTEM_SPEC.md` | 672 | Same. Zero code refs; collaborative editing UI/API not core pipeline. Apr 13 mtime (newer than other Cohort 1 specs). Could move to roadmap rather than prune. |

### §4.4 — Aggregate

- **Files proposed for deletion:** 11
- **Lines proposed for deletion:** ~3,400 (mostly the 3 contentious specs)
- **Bytes:** roughly 90–100 KB
- **Mass-deletion threshold check:** 11 ≤ 50 (CLAUDE.md owner-approval threshold). **No special sign-off needed.**
- **Segmentation:** Single PR per CLAUDE.md guidance. If operator chooses option (a) "prune outright" for §4.3, all 11 fit in one PR.
- **Suggested PR title:** `chore(manga): prune Phase 2A — 11 orphan/superseded files (audit 2026-04-26)`

### §4.5 — Files explicitly NOT pruned (defended)

These were considered and kept; documented so future audits don't re-litigate.

- **`phoenix_v4/manga/chapter/visual_from_script.py` (v2)** — superseded by v3 but still imported by `lettering_from_script` for v2 compat. **Keep until ep_001 + ep_002 fully migrate to v3 schema.** Re-evaluate after PR #678 lands.
- **`phoenix_v4/manga/chapter/writer_stub.py`** — intentional deterministic stub. Not orphan; called by `chapter_runner`. Its replacement (live LLM writer via Claude SDK) is §7 Sprint 2I; until then, the stub is load-bearing.
- **`scripts/manga/migrate_lettering_v2_to_v3.py`** — one-shot migration. ARCHIVED-after-use, but not yet used. Keep until migration completes.
- **All Cohort 2 cover specs** (`manga_cover_uniqueness_engine`, `manga_cover_regulatory_compliance`, `manga_cover_full_assembly`, `manga_cover_pipeline_integration`) — aspirational, but represent ~5 PRs of design thinking that should be implemented in §7 Sprint 2E if operator approves the cover pivot. Do not prune.
- **`manga_ei_v2_dialogue_gates.md`** — aspirational, but implementation-ready. §7 Sprint 2D target. Do not prune.
- **All 5 unread cover-design research files (`artifacts/research/manga_cover_design/0[1-9]_*.md`)** — recent (2026-04-26), high content density, future implementation references. Do not prune.

---

## §5 — Audit-vs-shipped (per-spec/plan reality check)

Per-spec reconciliation between what was called for and what is actually live on `origin/main` HEAD `0795235689`. Format: `spec/plan | called for | shipped | shipped-via | gap`.

### §5.1 — Cohort 1 (Apr 11 architecture suite)

| Spec | Called for | Shipped | Shipped via | Gap |
|------|-----------|---------|-------------|-----|
| `AI_MANGA_PIPELINE_SUMMARY.md` | 7 agents + 2 cross-cutting (Story Architect, Genre Agent, Series Bible, Chapter Writer, Layout Agent, Lettering Agent, QC Agent + Transmission Splitter + Teaching Library) | 6 of 7 agents implemented; both cross-cutting systems | `phoenix_v4/manga/{series,chapter,qc,runner}/` + `transmission.py` | **Live writer agent** is stubbed (`writer_stub.py` is deterministic, no LLM). All other agents are functional. |
| `MANGA_PRODUCTION_PIPELINE_SPEC.md` | Batch orchestration; cloud GPU scaling (RunPod/Vast.ai); 12-week timeline; cost model | Local/Pearl-Star ComfyUI render path; deterministic chapter DAG | `chapter_runner.py` + `render_ep001_panels_local_comfy.py` (Pearl Star fallback) | **Cloud GPU scaling not implemented.** Single-node Pearl Star ComfyUI is sufficient for current throughput; cloud burst is a §7 Phase 4 target if catalog scale demands it. |
| `MANGA_GENRE_AGENT_SPEC.md` | 6-step workflow; villain design from protagonist shadow; 10 international genres | Genre blueprint generation in story_architect | `phoenix_v4/manga/series/story_architect.py` + `config/manga/genre_ite_profiles.yaml` | Mostly shipped. Villain-from-shadow logic is implicit; spec could be retired or kept as design reference. |
| `MANGA_CHAPTER_WRITER_SPEC.md` | Panel-by-panel script generation; silent page protocol; field classification | `writer_stub.py` deterministic mapper produces v3 chapter scripts | `chapter/writer_stub.py` → `chapter_script.json` | **Live LLM writer not integrated.** Stub maps handoff → panels deterministically. Quality is bounded by handoff content. §7 Sprint 2I. |
| `MANGA_STORY_ARCHITECT_SPEC.md` | Beat sheet expansion; Transmission Splitter dual-view; silence_map allocation; cadence adapter | All four cross-cutting capabilities in code | `series/story_architect.py` + `transmission.py` | None. Live. |
| `MANGA_SERIES_BIBLE_SPEC.md` | Per-series reference; 19-page COMPRESSION→MA→CHOICE→TONGLEN→AFTER formula; motif library; TikTok clip spines | Series structure in code; per-series YAMLs in config | `config/source_of_truth/manga_series_examples/` + `chapter_runner` | **TikTok clip spine extraction not implemented.** Aspirational. §7 Phase 4. |
| `MANGA_TEACHING_LIBRARY_SPEC.md` | Wisdom atom taxonomy; 20+ seed atoms; deployment rules | Atoms loaded; deployment rules enforced | (atom files in config) | Live. |
| `MANGA_LAYOUT_AGENT_SPEC.md` | Page composition; RTL/LTR/webtoon direction; page type handling; text z-ordering | Layout compositing live | `chapter/page_compose.py` + `chapter/webtoon_compose.py` | None. Live. |
| `MANGA_TEXT_RENDERING_SPEC.md` | clarity_mode vs manga_authentic_mode; SFX multilingual rendering | Basic rendering; default authentic_mode | `chapter/bubble_render.py` + `cjk_text_shaper.py` | **clarity_mode toggle not implemented.** Defer; not critical. |
| `MANGA_MODE_SYSTEM_SPEC.md` | Mode system for shōnen/seinen/shōjo/isekai/horror | Distributed across agent specs (no central mode-switching code) | (none) | **No code refs.** §4 prune candidate. |
| `MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` | 30-brand fingerprint matrix; anti-spam scoring | (none) | (none) | **No code refs.** §4 prune candidate. |

### §5.2 — Cohort 2 (Apr 24 task-specific gates suite)

| Spec | Called for | Shipped | Shipped via | Gap |
|------|-----------|---------|-------------|-----|
| `manga_visual_quality_gates.md` | MQG-01..08 (visual rhythm, silence density, establishing shot, reading flow, emotional arc, page-turn payoff, char presence, bubble count) | MQG-02 (silence density) live; rest spec-ready | `qc/pacing_gates.py` (MQG-02 audit remediation MDLG-09b) | **MQG-01, MQG-03..08 not wired.** §7 Sprint 2C. |
| `manga_speech_atom_taxonomy.md` | Atom dimensions; anti-repetition; deterministic selection | Selection engine live; cooldown + forbidden_after enforced | `phoenix_v4/manga/<atom_selector>` + atom config | Live. |
| `manga_ei_v2_dialogue_gates.md` | MDLG-01..05 (engagement, somatic precision, word economy, uniqueness, EI cohesion) | (none) | (none) | **Zero integration.** Spec is implementation-ready. §7 Sprint 2D. |
| `manga_cover_uniqueness_engine.md` | Cover fingerprint hashing; diversity scoring; batch validation | Minimal `covers/__init__.py` reference | (none) | **Aspirational.** §7 Sprint 2E. |
| `manga_cover_regulatory_compliance.md` | Age rating; content moderation; banned imagery; regional rules | (none) | (none) | **Aspirational.** §7 Sprint 2E. |
| `manga_cover_full_assembly.md` | Cover composition; layout rules; safe-area constraints | Basic cover generation (no spec compliance) | `covers/cover_assembler.py` | **Aspirational.** §7 Sprint 2E. |
| `manga_cover_pipeline_integration.md` | End-to-end cover workflow with gates | Linear pipeline, no gates | `covers/` | **Aspirational.** §7 Sprint 2E. |
| `manga_cover_flux_workflows.md` | FLUX integration; per-style configurations; latency targets | FLUX calls live; minimal per-style tuning | `covers/cover_generator.py` | Per-style tuning incomplete. §7 Sprint 2E. |
| `manga_name_thumbnail_stage.md` | Name Stage workflow; layout candidates; MQG execution | Name Stage exists; MQG partially wired | `chapter_runner` + `qc/` | Cost optimization manual. §7 Sprint 2C. |
| `manga_character_setting_consistency.md` | Character state continuity; outfit tracking; injury persistence; setting memory | `series_memory.json` is the implementation | `chapter_runner` + `series_memory.schema.json` | Live. |
| `manga_bubble_rendering_engine.md` | Bubble shape mapping; SFX rendering; font substitution; OCR purity | Bubble rendering live; OCR rare (manual) | `chapter/bubble_render.py` | OCR purity not auto-run. §7 Sprint 2C subsumes. |
| `MANGA_AUTHOR_SYSTEM_SPEC.md` | Collaborative editing UI/API | (none) | (none) | **Zero refs.** §4 prune candidate. |

### §5.3 — `docs/MANGA_QUALITY_GAP_PLAN.md` 7-sprint reconciliation

The Apr 17 quality-gap plan called for sprints 0/A/B/C/D/E. Reconciliation:

| Sprint | Called for | Shipped via PR(s) | Status |
|--------|-----------|-------------------|--------|
| Sprint 0 | Phase 0 schema (format / panel_layout_template / target_platforms) | PR #632 | DONE |
| Sprint A | Catalog rebuild + schema v2 | PR #642, #643, #646 | DONE (132 series + 716 book plans) |
| Sprint B | FONT_REGISTRY rebuild + CJK shaping | PR #647 + PR #654 (Phase 2A) | DONE Phase 2A; **Phase 2B integration pending** (§7 Sprint 2H) |
| Sprint C | Visual quality gates (MQG-01..08) | PR #524 (audit remediation; MDLG-09b) | **PARTIAL — only MQG-02 wired** (§7 Sprint 2C) |
| Sprint D | EI v2 dialogue gates (MDLG-01..05) | (none) | **NOT STARTED** (§7 Sprint 2D) |
| Sprint E | Cover pipeline | PR-level: covers/ stubs only | **NOT STARTED** (§7 Sprint 2E) |

**4 of 7 sprints DONE, 1 PARTIAL, 2 NOT STARTED.**

### §5.4 — WEBTOON Canvas vs PDF/print pivot

Subagents A, B, C all surface the same answer: **architecture is digital/webtoon-forward**. PDF/print is a post-QC export format, not a primary gate concern.

- `MANGA_GTM_PLAN.md` lists Webtoon vertical scroll first; Q3 2026 Asia-Pacific launch.
- `SESSION_HANDOFF_2026-04-25.md` explicitly calls "Build WEBTOON Canvas submission `python3 scripts/publish/webtoon_canvas_upload.py`" as the final ship step.
- `manga_visual_quality_gates.md` MQG-06 (page-turn payoff) is skipped for `reading_direction: webtoon`.
- `MANGA_LAYOUT_AGENT_SPEC.md` supports RTL / LTR / vertical scroll; layout agent is direction-aware.

**No contradiction in the corpus.** The pivot is settled. PDF export is a flag (`--export-pdf`) on `run_manga_chapter`, not a gated output.

The remaining open question (R-1 in the risk register, also surfaced by subagent A): **WEBTOON Canvas has no public upload API and is TOS-grey for AI content.** Workarounds (headless Playwright + DOM-diff CI) are in the 14-item backlog (item 4). **See §8 OQ-3.**

### §5.5 — ep_002 production status (the most actionable gap)

Per subagent E + verification:

- `artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_002.yaml` — **exists**, 21 KB, 2026-04-25.
- `artifacts/manga/panel_prompts/.../ep_002.panel_prompts.json` — **does not exist**.
- `artifacts/manga/ep_002/` — **does not exist**.

**Root cause:** PR #678 (`fix(manga): lettering_from_script v3-schema awareness — unblocks bubble rendering`) is **OPEN, not merged**. Until it lands, the v3-schema chapter scripts cannot be lettered, which means the render-and-letter loop cannot complete for ep_002.

**This is the single highest-leverage merge in the entire backlog.** Once #678 lands, ep_002 becomes a 30-minute pipeline run.

---

## §6 — Full-catalog plan for 4 locales (en_US, ja_JP, zh_TW, zh_CN)

The Apr 13 `MANGA_FULL_CATALOG_PLAN.md` defines 12 teachers × 4 locales × 18–24 series each. Total scope ranges from 576 series (low end, 12 × 4 × 12) to ~1,152 series (high end, 12 × 4 × 24). This section refines that into a phased, capacity-aware production plan.

### §6.1 — Per-locale targets and format mix (4-locale scope)

Format mix derives from `manga_vs_webtoon_decision_matrix_2026-04-25.yaml` (5-locale; we drop ko_KR per operator scope — see §8 OQ-1). Genre weighting derives from `docs/research/manga_craft/index.md` and `manga_genre_writing_styles_2026_04_04.md`.

| Locale | Primary platforms | Format mix (color-vertical / B&W-page / color-page / self-help) | Genre weighting |
|--------|-------------------|--------------------------------------------------------------|-----------------|
| **en_US** | KDP Comics + WEBTOON Canvas | 60% / 20% / 15% / 5% | Broad: iyashikei (cozy), seinen (psychological), webtoon-vertical-romance, somatic/healing genres. Low-mecha. |
| **ja_JP** | KDP + LINE Manga Indies (dual-format) | 40% / 45% / 13% / 2% | Iyashikei + josei + seinen-philosophical (contemplative bias). B&W-page weighting reflects domestic market. |
| **zh_TW** | KDP + Bilibili + Kuaikan (multi-platform) | 50% / 40% / 7% / 3% | Cultivation/xianxia bias, plus seinen + webtoon-vertical-romance. |
| **zh_CN** | Contingent on partnership (BLOCKED until secured — see §8 OQ-4) | 70% / 10% / 18% / 2% | Cultivation/xianxia primary; webtoon-vertical-romance secondary. |

**Mecha genre note:** Subagent A and `docs/research/manga_craft/index.md` both note mecha as a known gap. Mecha is not in the current 10 craft bibles. **See §8 OQ-5** for whether to add a mecha craft bible (Year 2 candidate) or stay focused on therapeutic/iyashikei lanes.

### §6.2 — Per-series production scope

From `MANGA_FULL_CATALOG_PLAN.md` and ep_001 evidence:

- **Per series:** ~14 chapters (catalog plan target)
- **Per chapter:** ~32–35 panels (ep_001 = 35 FLUX prompts; ep_002 = 32 panels)
- **Per panel:** ~30 seconds render time on Pearl Star ComfyUI (ep_001 wall-clock evidence: 38 PNG pages in ~2 minutes for the bulk render = ~30s/page)
- **Per chapter wall-clock:** ~30 minutes pipeline time (script → panel prompts → render → bubble → compose → QC)

**Per-series production cost:** ~14 chapters × 30 min = **~7 wall-clock hours per series, single-locale.** Multi-locale fan-out is mostly translation + composing, not full re-render — assume **~10 wall-clock hours per series, fully localized 4 locales.**

### §6.3 — Total scope (4-locale × Ahjan strand only)

The Ahjan strand is the only strand with series plans staged. Total Ahjan scope:

| | Series count | Chapters target | Wall-clock |
|-|--------------|-----------------|-----------|
| Ahjan main (Buddhist Contemporary) | 24 series × 4 locales = 96 | 96 × 14 = **1,344 chapters** | 1,344 × 30 min = **672 hours** ≈ 28 days continuous |
| Ahjan forest simplicity (Stillness Press) | 18 series × 4 locales = 72 | 72 × 14 = **1,008 chapters** | 1,008 × 30 min = **504 hours** ≈ 21 days continuous |
| **Ahjan total** | **168** | **2,352** | **1,176 hours ≈ 49 days continuous** |

This is **theoretical wall-clock at single-pipeline throughput**, assuming no pauses, perfect translations, no re-runs. Real-world adjustment factor 2–4× for revisions, QA cycles, and translator review yields **~100–200 calendar days for the Ahjan strand at 1 pipeline lane**.

### §6.4 — Total scope if all 12 teachers are filled

12 teachers × Ahjan-equivalent scope = ~12 × 168 = **~2,016 series**, **~28,224 chapters**. At 30 min/chapter wall-clock, that's **~14,112 hours ≈ 588 days continuous**. **Real-world: 3–5 years at 1 pipeline lane.** Far above any single-year capacity.

**STOP rule check (§6 of execution flow): "Catalog plan total scope >5,000 chapters → STOP, surface as scope question."** ✅ Triggered. Catalog must be phased.

### §6.5 — Recommended phasing

**Phase 3.1 — en_US Ahjan main strand (Year 1, validate the full-catalog assumption)**
- 24 series × 1 locale × 14 chapters = **336 chapters**
- Wall-clock: ~168 hours ≈ 7 days continuous = ~1 calendar month at 4 hours/day pipeline lane
- Ship cadence: 1 series ep_001 per week × 24 weeks → all 24 series have ep_001 live by month 6
- Then ep_002, ep_003... rolling weekly
- **Operator goal:** by Year 1 end, all 24 en_US Ahjan main series have at least ep_001..ep_005 live

**Phase 3.2 — 4-locale Ahjan main strand (Year 1–2)**
- 24 series × 4 locales × 14 chapters = **1,344 chapters**
- Wall-clock: ~672 hours ≈ 28 days continuous; calendar: ~6 months with translation review
- Translation pipeline (Tier 2 Qwen) runs in parallel; doesn't bottleneck render
- **Operator goal:** by end of Year 2, all 96 series have ep_001..ep_007 in all 4 locales

**Phase 3.3 — Ahjan forest simplicity (Year 2–3)**
- 18 series × 4 locales × 14 chapters = **1,008 chapters**
- Same cadence as 3.2

**Phase 3.4 — Other 11 teachers (Year 3–4+)**
- Sequence by priority: pick top 3 teachers to expand based on Year 1 Ahjan reader signal
- Per-teacher series plan generation = 1 PR each (re-run `generate_series_plans_from_catalog.py` after catalog plan extension)
- Year 3: 3 additional teachers; Year 4: 4 more; Year 5+: remaining 4

### §6.6 — Gating dependencies per locale

| Locale | Translation | LoRA | Profiles | Master arc | Bubble fonts | AI policy |
|--------|------------|------|----------|------------|--------------|-----------|
| en_US | Native | None needed | 24 series × 1 author = Hana Tidecalm + others | Stillness Press uses anxiety/burnout/grief — covered | ✅ FONT_REGISTRY v2 | KDP ALLOWED + Canvas GREY |
| ja_JP | Tier-2 Qwen pending review by ja_JP-fluent reviewer | Optional (per-character LoRA) | 24 series × authors with Japanese names | midlife_women known gap (subagent A) | ✅ FONT_REGISTRY v2 (Source Han Sans) | KDP ALLOWED + LINE Manga Indies pending |
| zh_TW | Tier-2 Qwen + Traditional Chinese reviewer | Optional | 24 series × Mandarin-name authors | Same midlife_women gap | ✅ LXGW WenKai | KDP ALLOWED + Bilibili/Kuaikan TBD |
| zh_CN | Tier-2 Qwen + Simplified Chinese reviewer | Optional | 24 series × Mandarin-name authors | Same midlife_women gap | ✅ LXGW WenKai | BLOCKED — no AI-policy-compliant platform with public upload (see §8 OQ-4) |

**The midlife_women master arc gap** is surfaced by subagent A (research corpus) — the catalog plan covers anxiety, burnout, depression, grief, imposter_syndrome, financial_anxiety, social_anxiety, sleep_anxiety, self_worth, boundaries, compassion_fatigue, courage, somatic_healing, overthinking, but does **not** explicitly cover the midlife_women demographic arc. **See §8 OQ-6** for whether to add it as a 15th topic for the Ahjan strand.

### §6.7 — Realistic Year 1 target

If the operator picks **Path A (ship first)**:
- **Q2 2026 (May–July):** Merge PR #678. Render ep_002. Ship ep_001 + ep_002 to KDP en_US (and Canvas if §8 OQ-3 resolved).
- **Q3 2026 (Aug–Oct):** ep_001 for 6 more en_US Ahjan main series. Translation pipeline stress-tested on `the_alarm_is_lying` ja_JP/zh_TW/zh_CN.
- **Q4 2026 (Nov–Dec):** ep_001 for all 24 en_US Ahjan main series. 1 full series (`the_alarm_is_lying`) shipped 14 chapters in 4 locales.

If the operator picks **Path B (build gates first)**:
- **Q2 2026:** §7 Sprints 2A–2D (prune + gate runner + MQG + MDLG). No new chapter shipping.
- **Q3 2026:** §7 Sprints 2E–2I. Maybe 1 new chapter shipped.
- **Q4 2026:** Catalog ramp begins; 6–8 chapters shipped.

**Audit recommendation:** Path A on the en_US ep_001/ep_002 lane (parallel to Path B on gate runner). See §7 for the integrated sequence.

### §6.8 — Cost-per-locale rough estimate

Pearl Star is on-prem; compute is sunk cost. Translation (Tier-2 Qwen on Pearl Star, banned-paid-LLM-API) is also sunk cost. Cost per chapter in **operator time** is the binding constraint:
- ~30 min wall-clock pipeline
- ~10 min operator review per chapter (QA artifact spot-check, on average)
- = **~40 min per chapter per locale**

For Phase 3.1 (336 chapters): 336 × 40 min = **224 hours of operator review** ≈ 28 days at 8h/day. **Across Year 1, that's ~2.5 hours/day of review.** Sustainable solo.

For Phase 3.2 (1,344 chapters): 4× larger. **Translation reviewer + en_US reviewer + per-locale fluency reviewer needed.** Single-operator capacity is exceeded.

---

## §7 — Recommended sprint sequence (Phase 2+)

For each gap surfaced in §5, this section recommends the next workstream to open + estimated work + dependencies. Sequence respects: prune-first (Phase 2A), then gate-runner (Phase 2B), then per-locale catalog ship (Phase 3+).

**No workstream is opened by this audit.** The operator approves §7 before any workstream is created.

### §7.1 — Phase 2A — Pruning (1 PR)

| Sprint | Owner | Scope | Hours | Dependencies | PR title |
|--------|-------|-------|------|--------------|---------|
| 2A | Pearl_GitHub (or Pearl_Architect) | Delete the 11 §4 files + minor archive moves | 2–4 | Operator approval of §4 list | `chore(manga): prune Phase 2A — 11 orphan/superseded files (audit 2026-04-26)` |

**Acceptance:** push_guard passes; preflight passes; governance APPROVED; CI green; no test breakage.

### §7.2 — Phase 2B — QC gate runner integration (1 PR, HIGH priority)

| Sprint | Owner | Scope | Hours | Dependencies |
|--------|-------|-------|------|--------------|
| 2B | Pearl_Dev | Wire `chapter_qc.build_revision_queue_for_chapter()` into `chapter_runner.py` post-CHAPTER_LAYOUT stage. Fail chapter if revision queue is non-empty (configurable per gate severity). | 4–8 | None | 

**Acceptance:** ep_001 re-run executes QC gates; revision queue is generated; failures emit clear diagnostics. Add `tests/test_manga_chapter_qc_runner_integration.py`.

**Why HIGH priority:** Without this, every chapter shipped is shipped without programmatic QC. As catalog scales, manual review becomes the bottleneck.

### §7.3 — Phase 2C — MQG-01, MQG-03..08 wiring (3 PRs, MEDIUM priority)

| Sprint | Owner | Scope | Hours | PRs |
|--------|-------|-------|------|-----|
| 2C.1 | Pearl_Dev | MQG-01 (visual rhythm) + MQG-03 (establishing shot) | 4–6 | 1 PR |
| 2C.2 | Pearl_Dev | MQG-04 (reading flow) + MQG-05 (emotional arc) | 4–6 | 1 PR |
| 2C.3 | Pearl_Dev | MQG-06 (page-turn payoff, skip for webtoon) + MQG-07 (char presence) + MQG-08 (bubble count) | 4–6 | 1 PR |

**Dependency:** §7.2 must land first (gate runner is the host).

**Acceptance:** Each gate has unit test + integration test (called via `chapter_qc.build_revision_queue_for_chapter`). Tests pass on `ep_001` fixture.

### §7.4 — Phase 2D — MDLG-01..05 dialogue gates (1–2 PRs, MEDIUM priority)

| Sprint | Owner | Scope | Hours | PRs |
|--------|-------|-------|------|-----|
| 2D | Pearl_Dev | MDLG-01..05 (engagement, somatic precision, word economy, uniqueness, EI cohesion) per `manga_ei_v2_dialogue_gates.md` spec. Wire into `qc/` and `gate_registry.yaml`. | 12–20 | 1–2 PRs |

**Dependency:** §7.2 must land first.

**Acceptance:** All 5 gates run on `ep_001` script; revision queue populated when dialogue fails. `tests/test_manga_dialogue_gates.py` extended.

### §7.5 — Phase 2E — Cover pipeline gates (3–5 PRs, DEFERRED until operator decision)

The cover pipeline has 5 ASPIRATIONAL specs (uniqueness, regulatory, full assembly, pipeline integration, flux workflows). Total spec line count: ~5,768 lines. Total implementation effort: substantial.

| Sprint | Owner | Scope | Hours |
|--------|-------|-------|------|
| 2E.1 | Pearl_Dev | Cover gate execution timing decision (see §8 OQ-7): pre-FLUX or post-FLUX. Update `manga_cover_pipeline_integration.md`. | 2 |
| 2E.2 | Pearl_Dev | Cover uniqueness fingerprint hashing (per `manga_cover_uniqueness_engine.md` §3) | 8–12 |
| 2E.3 | Pearl_Dev | Cover regulatory compliance scan (per `manga_cover_regulatory_compliance.md`) | 12–16 |
| 2E.4 | Pearl_Dev | Cover full assembly pipeline (per `manga_cover_full_assembly.md`) | 16–24 |
| 2E.5 | Pearl_Dev | Cover pipeline integration (per `manga_cover_pipeline_integration.md`) | 8–12 |

**Dependency:** §7.2 (gate runner). §8 OQ-7 (timing decision).

**Audit note:** This is a substantial Year 1 commitment. **Recommend deferring 2E.2–2E.5 until §8 OQ-8 — "do we ship cover-as-thumbnail or cover-as-art" — is answered.** If we ship cover-as-thumbnail (small, low-stakes), basic FLUX is enough. Cover-as-art (large, marketing-grade) needs the full pipeline.

### §7.6 — Phase 2F — bubble_render → cjk_text_shaper Phase 2B (1 PR, LOW-effort HIGH-leverage)

| Sprint | Owner | Scope | Hours |
|--------|-------|-------|------|
| 2F | Pearl_Dev | 10-line edit per `SESSION_HANDOFF_2026-04-25.md` backlog item 7. Wire `cjk_text_shaper.shape()` into `bubble_render` for CJK bubbles. | 0.5–1 |

**Dependency:** None. Independent of §7.2.

**Acceptance:** ja_JP / zh_TW / zh_CN bubble rendering uses HarfBuzz path when uharfbuzz is installed; falls back to Pillow when not.

### §7.7 — Phase 2G — queue_panel_renders.py (Pearl Star ComfyUI submitter, 1 PR)

| Sprint | Owner | Scope | Hours |
|--------|-------|-------|------|
| 2G | Pearl_Dev | Per `SESSION_HANDOFF_2026-04-25.md` backlog item 1. ComfyUI HTTP queue submitter for Pearl Star. ~45 min PR per session. | 0.75 |

**Dependency:** None. Pearl Star marker installed (operator step).

**Acceptance:** Run `python3 scripts/manga/queue_panel_renders.py --series the_alarm_is_lying --episode ep_002 --locale en_US` and queue is populated; renders produce panels.

### §7.8 — Phase 2H — Furigana + page_compose vertical CJK (Phase 2C, 2 PRs, DEFERRED)

| Sprint | Owner | Scope | Hours |
|--------|-------|-------|------|
| 2H.1 | Pearl_Dev | Phase 2C — page_compose vertical CJK for B&W ja_JP page format | 8–12 |
| 2H.2 | Pearl_Dev | Phase 3 — furigana renderer for ja_JP | 12–24 |

**Dependency:** §7.6.

**Audit note:** Defer until ja_JP catalog ramp begins (Phase 3.2).

### §7.9 — Phase 2I — Live LLM writer integration (1–2 PRs, OPERATOR-PRESENT-ONLY)

`writer_stub.py` is intentionally deterministic. The full pipeline calls for a Claude-driven writer (per CLAUDE.md LLM Tier Policy: Tier 1 for prose generation, operator-present). Implementation:

| Sprint | Owner | Scope | Hours |
|--------|-------|-------|------|
| 2I | Pearl_Dev (operator-present) | Replace `writer_stub.py` callsite in `chapter_runner` with `writer_anthropic.py` (Claude SDK call via skills/claude-api). Tier 1 operator-present only. Cache prompts. | 12–24 |

**Dependency:** §7.2 (gate runner verifies output quality). §8 OQ-9 (commit to Tier-1 writer).

**Audit note:** This is the most controversial sprint. CLAUDE.md says Tier 1 is for "operator-present" tasks. A live LLM writer in `chapter_runner` could fire under operator-absent CI conditions. **Either (a) gate the writer behind a flag that's only on locally + operator presence, or (b) keep `writer_stub.py` and treat catalog scripts as the place for Tier-1 hand-authoring.** Operator must call which.

### §7.10 — Phase 2J — Speech atom population for CJK6 (1–4 PRs, MEDIUM)

| Sprint | Owner | Scope | Hours |
|--------|-------|-------|------|
| 2J.1 | Pearl_Dev (Tier-2 Qwen translation) | Generate ja_JP atom set from existing en_US atom matrix | 4–8 |
| 2J.2 | Pearl_Dev (Tier-2 Qwen translation) | Generate zh_TW atom set | 4–8 |
| 2J.3 | Pearl_Dev (Tier-2 Qwen translation) | Generate zh_CN atom set | 4–8 |
| 2J.4 | Pearl_Dev | Atom validation + integration tests across all 4 locales | 4–8 |

**Dependency:** None.

**Acceptance:** `config/source_of_truth/manga_speech_atoms/` populated for all 4 locales. `tests/test_speech_atom_taxonomy.py` validates locale coverage.

### §7.11 — Phase 2K — Cover layers + LoRAs for 11 brands (11 PRs, deferred to Year 2)

11 brands without cover_layer specs. Each is 1 PR (~2 hours) to scaffold the Stillness-Press-equivalent. **Recommend deferring** until Year 2 / Phase 3.4 begins, since 11 of 12 teachers also lack series plans.

### §7.12 — Phase 2L — Series plans for remaining 11 teachers (1 PR per teacher, deferred to Year 2)

Each teacher = 1 catalog plan section + `generate_series_plans_from_catalog.py` re-run. Each = 1 PR (~2 hours). **Recommend deferring** to Year 2 / Phase 3.4 priority order based on Year 1 Ahjan reader signal.

### §7.13 — Phase 2M — Ship ep_001 to readers (the actual launch sequence)

This is the operator's critical-path "Path A" sequence. Per `SESSION_HANDOFF_2026-04-25.md`:

| Step | Owner | Action | Time |
|------|-------|--------|------|
| 2M.1 | Operator | Add R2 secrets at GitHub Codespaces | 5 min |
| 2M.2 | Operator | SSH Pearl Star, install marker | 2 min |
| 2M.3 | Operator | Install CJK fonts, validate | 5 min |
| 2M.4 | Operator | Replace mock translations: `python3 scripts/manga/translate_chapter_script.py --force` | <5 min |
| 2M.5 | Pearl_Dev | Land §7.7 (queue_panel_renders.py) | 45 min |
| 2M.6 | Operator | Render ep_001 panels via §7.7 | 20–30 min |
| 2M.7 | Operator | r2_sync push; bubble_render; webtoon_compose | 5 min |
| 2M.8 | Operator | Build WEBTOON Canvas submission package | 5 min |
| 2M.9 | Operator | Submit to KDP + Canvas (manual upload, see §8 OQ-3) | varies |

**Plus PR #678 must merge first** for ep_002 to follow.

### §7.14 — Phase 2N — Render ep_002 (the lettering-fix unblock)

| Sprint | Owner | Scope | Hours |
|--------|-------|-------|------|
| 2N.1 | Pearl_GitHub | Merge PR #678 (lettering_from_script v3-schema awareness) | 0.25 |
| 2N.2 | Pearl_Dev | Generate ep_002 panel_prompts via `build_panel_prompts.py` | 0.5 |
| 2N.3 | Operator | Render ep_002 via Pearl Star ComfyUI | 0.5 |
| 2N.4 | Operator | Bubble + webtoon compose | 0.25 |

**Total:** ~1.5 hours operator time post-PR-merge.

### §7.15 — Critical-path sequence (audit-recommended order)

```
WEEK 1:
  - Operator approves §4 prune list → §7.1 lands (Phase 2A)
  - Operator approves §7.2 → Pearl_Dev lands gate-runner integration (Phase 2B)
  - Operator approves §7.6 → Pearl_Dev lands bubble-render Phase 2B (Phase 2F)
  - Operator approves §7.7 → Pearl_Dev lands queue_panel_renders.py (Phase 2G)
  - Operator merges PR #678 (Phase 2N.1)

WEEK 2:
  - Phase 2N.2–2N.4: ep_002 renders, ships
  - Phase 2M.1–2M.9: ep_001 ships to readers (KDP en_US first; Canvas if §8 OQ-3 resolved)
  - §7.10 Phase 2J.1: ja_JP speech atom generation begins (parallel)

WEEKS 3–6:
  - Phase 2C (MQG-01, 03..08): 3 PRs, 1/week
  - Phase 2D (MDLG-01..05): 1–2 PRs
  - First 2–3 additional en_US Ahjan main series ep_001 ships (Phase 3.1)

WEEKS 7–12:
  - Phase 2J.2–2J.4 (CJK speech atoms)
  - Phase 3.1 ramps: 6–10 series with ep_001 by week 12
  - First ja_JP localized chapter ships (validate Phase 3.2 readiness)

WEEKS 13–26 (Q3 2026):
  - Phase 3.1 continues
  - Phase 3.2 begins (4-locale Ahjan main)
  - §7.5 (cover pipeline) begins if §8 OQ-8 resolved

WEEKS 27–52 (Q4 2026):
  - Phase 3.1 completes (24 en_US Ahjan main series with ep_001..ep_005 each)
  - Phase 3.2 partial (~6 series in 4 locales)
  - §7.9 (live LLM writer) decision and possibly land
```

### §7.16 — Estimated hours summary

| Phase | Hours (low) | Hours (high) | Calendar weeks |
|-------|-------------|--------------|----------------|
| 2A (prune) | 2 | 4 | <1 |
| 2B (gate runner) | 4 | 8 | <1 |
| 2C (MQG) | 12 | 18 | 3 |
| 2D (MDLG) | 12 | 20 | 2 |
| 2E (cover) — DEFERRED | 46 | 64 | 6–8 |
| 2F (bubble Phase 2B) | 0.5 | 1 | <1 |
| 2G (queue_panel_renders) | 0.75 | 0.75 | <1 |
| 2H (Phase 2C/3 CJK) — DEFERRED | 20 | 36 | 4 |
| 2I (live writer) — POLICY DECISION | 12 | 24 | 2 |
| 2J (CJK atoms) | 16 | 32 | 4 |
| 2K (cover layers, 11 brands) — DEFERRED | 22 | 44 | 4 |
| 2L (series plans, 11 teachers) — DEFERRED | 22 | 44 | 4 |
| 2M (ship ep_001) | <1 hr operator | 1 | <1 |
| 2N (ship ep_002) | 1.5 | 1.5 | <1 |
| **Phase 2 total (excluding deferred)** | **62** | **109** | **12 weeks** |
| **Phase 2 + 3.1 first half (ship 12 ep_001s)** | +60 | +120 | +12 weeks |

**Year 1 envelope: ~120–230 hours of Pearl_Dev/operator engineering, plus ongoing per-chapter operator review.** Achievable solo if focused.

---

## §8 — Open questions for operator

Each question is tagged with the §-reference where it surfaced. Operator picks an answer; that answer drives Phase 2/3 sequencing.

### OQ-1 — Is ko_KR a 5th locale?
- **Surfaced:** §2.1, §6.1
- **Context:** `manga_vs_webtoon_decision_matrix_2026-04-25.yaml` defines 5 locales including ko_KR. Operator scope for this audit is 4 (en_US, ja_JP, zh_TW, zh_CN).
- **Why it matters:** ko_KR is WEBTOON Canvas native (170M MAU). Skipping it leaves the largest webtoon audience on the table. But Korea AI Act enforcement is "post-Jan 2027" per `SESSION_HANDOFF_2026-04-25.md` risk register — by the time Phase 3.2 ships, Korea may be the riskiest locale.
- **Audit recommendation:** Stay 4-locale through end of 2026. Re-evaluate ko_KR in Q1 2027 once AI Act enforcement posture is clear.

### OQ-2 — Where does the coordination layer live?
- **Surfaced:** §2.5
- **Context:** `CLAUDE.md` references `coordination/projects.tsv` and `coordination/workstreams.tsv` for project + workstream tracking, but `coordination/` directory does not exist in the repo.
- **Why it matters:** Without coordination TSVs, project state lives in artifact mtimes + commit history, which is brittle. Audit found `proj_manga_first_ship_20260425` referenced but no canonical state file.
- **Audit recommendation:** Either (a) bootstrap `coordination/` with the projects.tsv + workstreams.tsv per CLAUDE.md, or (b) clarify that coordination lives elsewhere (Notion / external) and update CLAUDE.md to point there.

### OQ-3 — How do we ship to WEBTOON Canvas given no public API?
- **Surfaced:** §5.4, §6.6
- **Context:** WEBTOON Canvas has no public upload API. `webtoon_master_reference_2026-04-25.md` and the risk register R-1 (HIGH) note TOS-grey for AI content. `SESSION_HANDOFF_2026-04-25.md` 14-item backlog item 4 calls for "WEBTOON headless connector + DOM-diff runbook."
- **Why it matters:** Path A (ship ep_001) requires either (a) manual upload to Canvas, (b) headless Playwright automation, or (c) skip Canvas and ship KDP-only.
- **Audit recommendation:** **Manual upload for ep_001 + ep_002.** Once volume justifies, build headless connector (3+ PRs per backlog item 4). Until then, treat Canvas as a manual operator step.

### OQ-4 — zh_CN platform partnership status
- **Surfaced:** §6.1, §6.6
- **Context:** zh_CN is BLOCKED in `manga_vs_webtoon_decision_matrix_2026-04-25.yaml` (contingent on partnership). No AI-policy-compliant zh_CN platform with public upload exists.
- **Why it matters:** Phase 3.2 (4-locale Ahjan main) blocks on zh_CN distribution. If no partnership materializes, we ship 3-locale only or shelve zh_CN until clarity.
- **Audit recommendation:** **Generate zh_CN content (translation pipeline is sunk cost) but do not commit to a release date.** Hold zh_CN renders in `artifacts/manga/` for future distribution opportunity.

### OQ-5 — Add mecha craft bible?
- **Surfaced:** §6.1, §3.1
- **Context:** `docs/research/manga_craft/index.md` references 10 craft lanes (BL, graphic_novel, iyashikei, josei, kodomomuke, seinen_psychological, shojo_romance, shonen_encouragement, webtoon_vertical_drama, webtoon_vertical_romance). Mecha is absent.
- **Why it matters:** Therapeutic/iyashikei/healing focus is the current strategic core. Mecha would be a major thematic expansion. Subagent A flagged the gap.
- **Audit recommendation:** **Defer mecha to Year 2+** unless one of the 11 not-yet-staged teachers brings a mecha lane (e.g., master_feung's tradition).

### OQ-6 — Add midlife_women master arc topic?
- **Surfaced:** §6.6
- **Context:** Subagent A flagged midlife_women as a missing master arc. Current Ahjan topic list (anxiety, burnout, depression, grief, imposter_syndrome, financial_anxiety, social_anxiety, sleep_anxiety, self_worth, boundaries, compassion_fatigue, courage, somatic_healing, overthinking) covers many demographics but lacks an explicitly midlife-women framing.
- **Why it matters:** Iyashikei + josei readership is heavily skewed midlife-women per `manga_vs_webtoon_decision_matrix` and `strategic_audit/`. We may be under-serving the largest reader demographic.
- **Audit recommendation:** **Add 1 series in en_US Ahjan main strand** as a Phase 3.1 experiment. If reader signal is positive, add 4-locale fan-out in Phase 3.2.

### OQ-7 — Cover gate execution timing (pre-FLUX or post-FLUX)?
- **Surfaced:** Subagent C contradiction analysis, §5.2
- **Context:** Panel-level MQG gates run pre-FLUX (structural). Cover uniqueness/regulatory gates are post-rendered (visual content). Specs are silent on whether cover gates block FLUX or run only QC.
- **Why it matters:** Pre-FLUX gates save compute (don't render covers that fail uniqueness). Post-FLUX gates are structurally simpler (you have the image already). Decision drives §7.5 implementation order.
- **Audit recommendation:** **Hybrid.** Cover uniqueness fingerprint hashing runs post-FLUX (you need the image). Cover regulatory compliance has a pre-FLUX prompt-side check (banned-imagery prompt filter) and a post-FLUX visual moderation check.

### OQ-8 — Cover-as-thumbnail vs cover-as-art commitment?
- **Surfaced:** §7.5
- **Context:** Cover pipeline has 5 ASPIRATIONAL specs totaling ~5,768 lines. Implementation effort: ~46–64 hours (Sprint 2E.1–2E.5).
- **Why it matters:** If we're shipping covers as small thumbnails on KDP and Canvas, basic FLUX is enough. If covers are marketing assets that drive discoverability, the full pipeline (uniqueness + regulatory + assembly + integration) is justified.
- **Audit recommendation:** **Cover-as-thumbnail for Phase 3.1.** Reassess after Year 1 reader signal. If covers prove to be the discoverability bottleneck, build the full pipeline in Year 2.

### OQ-9 — Live LLM writer integration: do we go Tier 1?
- **Surfaced:** §7.9
- **Context:** `writer_stub.py` is deterministic. CLAUDE.md says Tier 1 (Claude Code) is for "operator-present" prose generation. A live writer in `chapter_runner` could fire under operator-absent CI conditions, which violates Tier 1 intent.
- **Why it matters:** Without a live writer, every chapter script must be Tier-1 hand-authored (operator-present, ~2 hours per chapter). With a live writer, chapter scripts can be drafted in CI and operator-reviewed (~10 min per chapter). 12× throughput delta.
- **Audit recommendation:** **Keep `writer_stub.py` for v3 catalog scripts** (chapter scripts are creative work — operator-present anyway). Add a separate `writer_anthropic.py` for *non-script* assist (e.g., cover copy, blurbs, marketing) where automated drafts are reviewed before publication. This honors Tier 1 intent.

### OQ-10 — How aggressive should the prune be?
- **Surfaced:** §4.3
- **Context:** §4.3 contentious specs (MODE_SYSTEM, BRAND_DNA, AUTHOR_SYSTEM) have zero code refs but contain ~2,700 lines of design thinking.
- **Why it matters:** Prune-outright loses the design thinking. Move-to-archive keeps it but flags as deferred. Keep-tag-deferred preserves indexability.
- **Audit recommendation:** **Move to `specs/archive/` with a `DEFERRED_2026_04_26.md` index file**. Preserves the design work; signals deferred status; doesn't clutter the live `specs/` tree.

### OQ-11 — Should `MANGA_MODE_STRATEGY.docx` migrate to Markdown?
- **Surfaced:** §2.2
- **Context:** The docx is the only binary in the manga docs corpus. Subagent B did not read it.
- **Why it matters:** Binary docs are not auditable, not searchable, and not versionable in git. If this docx contains canonical mode-strategy content, it should be in Markdown.
- **Audit recommendation:** **Convert to Markdown in Phase 2A or shortly after.** If the content is duplicative of `MANGA_MODE_SYSTEM_SPEC.md` (a §4 prune candidate), the docx may also be prunable.

### OQ-12 — Workflow for executing the audit?
- **Surfaced:** Procedural
- **Context:** This audit deliverable proposes 11 prunes (§4), 13 sprints (§7), 4 catalog phases (§6), 12 open questions (§8). Operator review path is not yet sequenced.
- **Audit recommendation:** **3-pass operator review:** (a) read §1 + §8 first (fastest decision surface); (b) approve/reject/amend §4 + §7 critical-path (next 24 hours of work); (c) commit to §6 catalog phasing (Year 1–4 envelope).

---

## §9 — Audit limitations and caveats

- Subagent A returned with the 4 research subdirs (`manga_quality_bar`, `manga_dialogue_system`, `manga_cover_design`, `strategic_audit`) **partially unread** due to its token budget. Headings + line counts + dates have been captured by direct inspection (per-subdir line counts in §2.1), but the full content of those 13 files (~600 KB) has not been indexed in detail. **Recommendation:** when §7.5 (cover pipeline) opens, the cover-design research subdirs should be fully read by the implementing agent before code work begins.
- Subagent E reported `coordination/` does not exist; verified in §2.5. If coordination state is canonical elsewhere, this audit underrepresents it.
- The `MANGA_MODE_STRATEGY.docx` was not opened (binary). See §8 OQ-11.
- ep_002 panel_prompts and renders do not exist; subagent E + verification confirmed. PR #678 unblocks.
- Code calls were not exhaustively grep-validated for orphan status — subagent D's "ORPHAN" verdicts are based on import-graph signals, not exhaustive callsite enumeration. The §4 prune list reflects "high confidence" candidates; before any deletion, run a final `grep -r '<basename>' phoenix_v4/ scripts/ tests/ .github/` per file.
- The 716 book_plans count differs from subagent E's earlier estimate of "48 dirs (480+ eps)" — verified count via `find` is 716. Subagent E undercounted; `find config/source_of_truth/manga_book_plans -type f -name '*.yaml' | wc -l` returns 716.
- `gen_series_plans_from_catalog.py` and `generate_book_plans_from_series.py` are deterministic; re-running them does not destroy state, but it does re-emit the YAMLs. Don't re-run during Phase 2 unless catalog plan itself changes.
- Cost figures in §6.8 are operator-time estimates. Actual translation review time per chapter may vary 2–4× by locale fluency requirements.

---

## §10 — Closing note

This audit is a navigation/decision artifact, not a spec. It introduces **no new governing specs** and modifies **no code, config, or coordination state**. It proposes (a) a prune list of 11 files in §4, (b) a sprint sequence of 13 phases in §7, (c) a 4-phase catalog plan in §6, and (d) 12 open questions in §8. Each requires explicit operator approval before execution.

**The manga lane stays in current state** (ep_001 live; ep_002 content authored but PR #678 not merged) until the operator picks the next move from §7.

The next step is operator review of this document. Phase 2+ is gated on that review.
