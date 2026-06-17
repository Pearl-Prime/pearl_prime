# Phoenix Omega — Repo Function Map

**Date:** 2026-06-17
**Author:** Pearl_Architect (total repo audit, read-only)
**Baseline:** `origin/main` @ `29c3fd76bc21f456953f7232df7272e436c4b474`
**Method:** Walked `docs/`, `specs/`, `scripts/`, `phoenix_v4/`, `config/`, `artifacts/coordination/`, `.github/workflows/` against origin/main. Verified currency against the 22-row `SUBSYSTEM_AUTHORITY_MAP.tsv`, `CANONICAL_ARTIFACTS_REGISTRY.tsv` (69 rows), `ACTIVE_WORKSTREAMS.tsv` (257 rows), `PEARL_ARCHITECT_STATE.md` (3,368 lines), open PRs (≈60), and the prior `SUBSYSTEM_HEALTH_AUDIT.md` (2026-06-09) + `artifacts/audit/q*` series (2026-04-29).

> **CURRENCY CAVEAT (read first):** Commit `30bd4dd6af` (2026-05-29) touched **57,017 files** — a mass re-import that reset `git log` last-commit dates for **468 of 518** tracked `.md` files to 2026-05-29. **`git log` recency is NOT a reliable staleness signal** for anything dated 2026-05-29. Staleness in this audit is judged by in-file content/headers, explicit SUPERSEDES markers, cross-references in the canonical authority set, and code/CI references — not commit dates. Files edited *after* 2026-05-29 are genuinely recent.

> **STATUS legend:** `done` = built + on main + wired/tested; `partial` = core on main but spec'd extensions or wiring incomplete; `needs-coding` = spec'd or known-broken, fix not on main; `not-started` = proposed/backlog only.

---

## Subsystem Roster (from SUBSYSTEM_AUTHORITY_MAP.tsv)

22 subsystems are governed. Below, each gets: what it does · authority docs · primary config/code entry points · STATUS + specific gaps.

---

### 1. core_pipeline — STATUS: partial
**What:** Arc-first book assembly engine: arc → chapter plan → atom selection → enrichment → section-packet composition → render. Gates every book ship.
**Authority:** `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` (sole architecture authority); `specs/PHOENIX_V4_5_WRITER_SPEC.md` (writer/content authority, v2 adds PIVOT/TAKEAWAY/THREAD/PERMISSION slots).
**Entry points:** `scripts/run_pipeline.py` (canonical CLI — `_run_spine_pipeline_mode` L648; `--pipeline-mode` default now **spine** per L1853); `phoenix_v4/planning/{catalog_planner,chapter_plan,story_planner,enrichment_select}.py`; `phoenix_v4/rendering/section_packet_composer.py`; `config/governance/system_registry.yaml`.
**Gaps:**
- `register_gate` and `ship_readiness` are **NOT wired into `run_pipeline.py`** on main (grep is empty) — they remain separate calls. PR #1536 (spine-default + register_gate wire + ship_readiness) is **OPEN, not merged**.
- Per Pearl Prime pilot (PR #1585) + memory: spine books PASS inline flow/craft/ei_v2 but **9/9 HARD_FAIL register+word-budget**; the frontier is COMPOSER scaffolding-repetition, not atom scarcity.
- Atom cohesion: atoms are slotted per-atom with **no adjacency model** → jarring/choppy books. Chunked A–F plan in flight (A schema + E audit dispatched; B/C/D/F gated).
- `deprecated/validators/` lists 5 permanently-removed validators (Arc-First §11) — structural-only discipline is enforced.

### 2. pearl_prime — STATUS: partial
**What:** Bestseller-grade book program on top of core_pipeline (hooks, aha, integration, thread, scene specificity, anti-generic, dwell-beat). The catalog $-maker (~800 high-confidence configs).
**Authority:** `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`; `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (canonical CLI = spine + production + `--exercise-journeys` per §570-577); `docs/PEARL_PRIME_RELEASE_CONTRACT.md`.
**Entry points (CANONICAL per registry):** `scripts/run_pipeline.py` (one path — do NOT fork); `scripts/pearl_prime_multilingual/`, `scripts/pearl_prime_en_us/`.
**Gaps:**
- ONE-PATH lockdown (`docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md`, 2026-06-09) phases 1–4 in flight (mechanical sweeps / runtime gates / craft gates child ws's open).
- Dwell-beat craft gate (sibling to G1–G6) spec'd in OVERLAY_SPEC but wiring ws (`ws_pearl_dev_dwell_beat_gate_wiring`) open.
- 1000-book build program: two active specs (`PEARL_PRIME_1000_BOOK_BUILD_PROGRAM_V1_SPEC.md` 2026-06-15, `PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM.md` 2026-06-14) — program-level, execution gated.
- Storefront launch (subsystem 19) is the downstream gate.

### 3. manga_pipeline — STATUS: partial
**What:** AI manga dharma pipeline. Multi-model: Qwen-Image (faces), FLUX (backgrounds), Animagine XL 4.0 (B&W panels), PuLID-FLUX-FaceNet (face-lock), ai-toolkit LoRA (named cast). Series bible → chapter script → visual-from-script → panel render → bubble → compose → cover.
**Authority:** `specs/AI_MANGA_PIPELINE_SUMMARY.md` (master); `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (V5.1 render authority, supersedes V4); `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (catalog governance); `docs/MANGA_IMPLEMENTATION_OUTLINE.md`.
**Entry points:** `scripts/manga/run_manga_chapter.py` (canonical DAG), `run_chapter_production.py`, `phoenix_v4/manga/runner/chapter_runner.py`, `phoenix_v4/manga/ite_pipeline.py`; `config/manga/gate_registry.yaml`; `schemas/manga/`. Catalog SSOT: `config/source_of_truth/manga_series_plans/{locale}/` (1,350 YAMLs × 5 locales) + `manga_book_plans/` (18,900).
**Gaps:**
- V2 multi-model: Phase A/B **CODE merged** (#925/926/928); per-character DATA filled (13 teacher 12-axis YAMLs, PR #1542 operator-review-pending). Phases C/D/E (register/genre LoRAs, anatomical, re-render smoke) ws's open.
- ep_002 V5.1 pose-library extension in flight; zh_TW/zh_CN blocked_lora + blocked_score follow-ups open.
- Cover-uniqueness + visual-QC specs (`specs/manga_cover_*`, `manga_visual_quality_gates.md`) are **ASPIRATIONAL, not production gates** (per DOCS_INDEX + `MANGA_PIPELINE_AUDIT_2026-04-26.md`); chapter QC runner not fully automatic.
- Weekly manga rollout active; locale 8→12 wire-without-regen sanctioned (PR #1369).

### 4. video_pipeline — STATUS: partial
**What:** Beat-driven narrative video + audiobook video; section-model frame selector (1 sec = 1 pic, REGULAR/MANGA mix); ffmpeg assembly.
**Authority:** `docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md` (+ run-pipeline-wiring follow-on); `docs/specs/PEARL_VIDEO_FRAME_SELECTOR_BEST_OF_V1_SPEC.md`; `docs/specs/PEARL_VIDEO_YT_STARSEED_AHJAN_UPDATE_V1_SPEC.md`; `docs/specs/TEACHER_MANGA_30S_VIDEO_V1_SPEC.md`.
**Entry points:** `scripts/video/build_frame_selector_v2.py` (on main); `config/video/{render_params,upload_config,audiobook_style,format_specs}.yaml`; `config/release_velocity/video_cadence.yaml`. Workflows: `video-daily-publish.yml`, `generate-video-bank.yml`.
**Gaps:**
- `scripts/video/assemble_mixed.py` (regular/manga-per-section assembler, generalizes the two v3_8 twins) is **NOT on main** — PR #1663 OPEN (do-not-merge). Export schema = builder↔assembler contract; manga JS keeps `.jpg` but renders are `.png` (gotcha).
- Best 3-stage video method (beat-author → AI-judge → human best-of) + seed-lock is **stranded local-only**; `build_daily_batch` is a publish-selector, not a builder.
- `ws_video_run_frame_judge_module_20260616` + several video ws's (washout fix, p0 upgrades, enhancement research) open.
- Teacher×manga 30s video V1 (12-13 deliverables) ws's open.

### 5. brand_admin — STATUS: partial
**What:** Operator-facing brand operations console. Phase 0–3 weekly OS; per-brand director screen with per-platform delivery cards.
**Authority:** `BRAND_ADMIN_CANONICAL_PACKAGE.md`; `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`; PEARL_ARCHITECT_STATE DASH-02.
**Entry points (CANONICAL):** `brand_admin_weekly_os.html` (operator-confirmed 2026-06-15; **rejected `brand_admin.html`**); Phase-3 → `public/brand_handoff_dashboard.html?brand=<id>` (single-brand "Brand Director Operations", PR #1618 merged/live); `brand-wizard-app/` (React) → CF Pages `brand-admin-onboarding`; brand resolution via `brand_admin_brands.json`; `server/routes/brand_onboarding.py`; `scripts/catalog/_active_brand_filter.py`.
**Gaps:**
- **`brand_admin.html` retirement (PR #1628) is still OPEN** — the file is still referenced by `_active_brand_filter.py`, `server/routes/brand_onboarding.py`, and `tests/test_brand_admin_public_api.py` on main. Do NOT delete until #1628 merges.
- Per-platform delivery + catalog data on the director screen is still **PLACEHOLDER**.
- Brand-admin v2 weekly cron wireup + per-platform download route + planned-volumes-per-brand backfill ws's open.

### 6. storefront — STATUS: partial (mockups + infra scaffold; not live)
**What:** Pearl Prime customer-facing storefront (Cloudflare Workers + D1). Catalog browse, product detail (book/audiobook/manga), cart, account library, reviews.
**Authority:** `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` (2026-06-06; **the only storefront spec** — no stale `specs/PEARL_PRIME_STOREFRONT_SPEC.md` exists, already cleaned).
**Entry points:** `storefront/` (wrangler.toml, package.json, `migrations/0001_init.sql`); `brand-wizard-app/public/storefront_mockups/` (16 HTML mockups + CSS + demo data); `config/storefront/{external_link_allowlist,sku_url_map}.yaml`; `.github/workflows/pearl-prime-storefront-deploy.yml`; `skills/pearl-int/references/storefront_resource_ids.md`.
**Gaps:** Phase A (UI mockups / framework research / CF wiring) ws's open; not a live store yet — mockups + DB init + deploy workflow exist, real catalog wiring pending.

### 7. naming (title engine) — STATUS: done (with versioned-dupe cruft)
**What:** Book/series title generation, scoring, dedupe, validation against marketing config.
**Authority:** `specs/TITLE_ENGINE_MARKETING_CONFIG_SPEC.md`.
**Entry points (CANONICAL):** `phoenix_v4/naming/` package (`generator.py`, `scorer.py`, `dedupe.py`, `validator.py`, `keyword_bank.py`, `cli.py`).
**Gaps:** Root-level `phoenix_title_engine_v4.py` is the legacy-but-still-imported engine (`tests/test_marketing_config_integration.py` imports it; `config/governance/system_registry.yaml` lists `phoenix_title_engine_v4.py` + glob `phoenix_title_engine*.py`). Root `phoenix_title_engine.py` and `_v3.py` are **superseded duplicates** (v4 is the live one). See DELETION_CANDIDATES.

### 8. catalog_planning — STATUS: done/partial
**What:** Generates which books/manga to create across brand × topic × persona × format × locale. Path X per-axis canon (24 archetypes × 13-14 lanes for book; 15-genre × 37-brand for manga).
**Authority:** `docs/GENRE_PORTFOLIO_PLAN.md`, `docs/CJK_CATALOG_PLAN.md`, `docs/US_CATALOG_PLAN.md`, `docs/specs/ANGLE_REGISTRY_SSOT_V2_SPEC.md` (supersedes V1); `specs/BRAND_REGISTRY_RECONCILIATION_37x14_SPEC.md`.
**Entry points:** `phoenix_v4/planning/catalog_planner.py`; `scripts/manga/generate_catalog_plan_from_strategic.py`; `scripts/catalog/build_catalog_analysis_bundle.py`; `config/catalog_planning/`; `config/source_of_truth/`.
**Gaps:** Brand registry 37→39×14 unification (PR #1604 do-not-merge); catalog generator v1.1 25-brand → 37-brand authoring ws's open; planned-volumes backfill open. No consolidated master catalog plan (closed-not-needed, MASTER-CATALOG-01).

### 9. pearl_news — STATUS: done (high-drift, anchored)
**What:** Daily news/article pipeline. EN via cloud (Groq) per hybrid cycle; CJK via Pearl Star (Qwen). Sidebar, pen-name author resolver, WP publish.
**Authority:** `docs/PEARL_NEWS_WRITER_SPEC.md` (2026-06-06); `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md`.
**Entry points (CANONICAL):** `pearl_news/pipeline/assemble_v52.py` (sidebar assembler — anchor PR #853 8070e81fd; EDIT in place, never fork v53); `pearl_news/pipeline/article_assembler.py`; `pearl_news/config/`, `pearl_news/prompts/`. Workflows: `pearl-news-daily.yml`, `pearl-news-assemble.yml`, `pearl-news-fill-qwen.yml`, `pearl-news-full-qa.yml`.
**Gaps:** Several open handoff/state PRs (#1429 supersedes #1293/#1373/#1425; #1512 V2 article-system handoff). Volunteer-digest pipeline + WP-plugin-drift-pull ws's open. Parallel test root `test_pearl_news/` may be superseded by `tests/` (see deletion candidates).

### 10. audiobook_pipeline — STATUS: partial
**What:** Fully-automated Qwen comparator loop → localized audiobook scripts; 5 hard + 4 scored gates; asyncio parallel; manual review queue in PhoenixControl. M4B + chapter markers.
**Authority:** `docs/AUDIOBOOK_OPS_MANUAL.md`; `docs/AUDIOBOOK_PIPELINE_SPEC.md`.
**Entry points:** `scripts/audiobook_script/run_comparator_loop.py`; `scripts/audiobook/`; `config/audiobook/`; `config/video/audiobook_style.yaml`. Workflow: `audiobook-regression.yml`.
**Gaps:** Brand-admin v2 audiobook axis (M4B + chapter markers × 37 brands) is the active execution lane (subsumes the ws). CosyVoice2 Pearl Star smoke pending. Duration labels are hand-set, not derived (150-WPM intent; needs DURATION_DERIVATION_SPEC application).

### 11. podcast_pipeline — STATUS: partial (proposed → building)
**What:** Weekly podcast cadence: assemble episode, render audio, generate RSS feed, ID3/loudness.
**Authority:** `docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md`; `pearl_news/research/podcast/`.
**Entry points:** `scripts/podcast/{assemble_podcast_episode,render_podcast_audio,generate_podcast_feed,render_simple_episode}.py`; `config/podcast/`; `config/integrations/podcast_credentials.yaml`. Workflow: `podcast-weekly.yml`.
**Gaps:** Marked `proposed` in authority map; brand-admin v2 podcast axis is the active lane. Spotify/Apple feed health + ID3/loudness hardening pending.

### 12. music_mode — STATUS: partial (V1 scaffold; V2 spec'd)
**What:** Music-brand content. Survey → song-kit → MusicGen render. Per-lane % allocation (lane_content_mix), first-person music wrapper. ~38 dormant music brands.
**Authority:** PEARL_ARCHITECT_STATE MUSIC-MODE-V1-01; `docs/specs/MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md`; `docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md`; `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md`; `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md`. SSOT: `SOURCE_OF_TRUTH/musician_banks/`.
**Entry points:** `phoenix_v4/musician/{survey_derivation}.py`, `lyric_mood_engine.py` (PR #1554 open); `scripts/music/` (build_music_index, export_musicgen_manifest, generate_book_companion_song, musicgen_colab, select_and_edit); `config/music/`.
**Gaps:** Many open PRs: #1580 (both-ways model + first-person wrapper, do-not-merge), #1561/#1560/#1554/#1547 (song-kit engine/orchestrator/Ahjan reference). Music-companions subsystem `proposed`. Live MusicGen route + first-real-artist seed pending. No music-file distribution (decided).

### 13. ei_v2 — STATUS: partial (scorer, not full engine)
**What:** Enlightened Intelligence quality layer. **Today = EMA-tuned weighted-sum editorial scorer** (45 recs/7+), with dimension gates, hybrid selector, learner, emotion-arc validator, cross-encoder reranker, domain embeddings, duration-fit, manga-dialogue gates.
**Authority:** `phoenix_v4/quality/ei_v2/`; `config/quality/ei_v2_config.yaml`.
**Entry points:** `phoenix_v4/quality/ei_v2/*` (config, dimension_gates, hybrid_selector, learner, llm_callback, emotion_arc_validator, cross_encoder_reranker, domain_embeddings, duration_fit, manga_dialogue_gates). Workflow: `ei-v2-gates.yml`.
**Gaps:** Vision's 4 stages PARTIAL/NOT-BUILT (no GA, not wired to planners). Strengthening design = PR #1516/#1517/#1578 (multi-objective T×E×fidelity fitness, spiritual-root synthesis CEG, Reader Council, retire EMA→qNEHVI BO + GA) — all OPEN. `EI_V2_REGISTRY_LEARNING_SPEC.md` referenced in agent_registry but learning-loop activation drifts.

### 14. teacher_mode — STATUS: partial
**What:** Teacher/pen-name authoring layer (one author = one consciousness moving through registers, NOT one grammatical person). Teacher banks, doctrine atoms, wrapper templates.
**Authority:** `docs/SYSTEMS_V4.md`; `specs/PHOENIX_V4_5_WRITER_SPEC.md`; `specs/TEACHER_MODE_*` suite; `TEACHER_MODE_INVARIANTS.md`. SSOT: `SOURCE_OF_TRUTH/teacher_banks/`; `config/authoring/pen_name_teacher_profiles.yaml`.
**Entry points:** `phoenix_v4/teacher/`; `phoenix_v4/rendering/teacher_wrapper.py` (`("","")`-on-incomplete safety). Workflows: `teacher-gates.yml`, `teacher-photo-drift-guard.yml`.
**Gaps:** HOOK P0/P1/P2 rewrite batches open; wrapper intro-variant diversification; ahjan teacher-bank framing re-author; teacher-doctrine overlay (PR #1539 — QUOTE retired per #915, roster residual). Atom coverage = teacher-bank overlay gap (QUOTE 0/15, TEACHER_DOCTRINE ahjan-only). Multiple overlapping teacher-mode specs (see DOCS_TIED_TO_FUNCTION for the canonical-vs-historical split).

### 15. translation (localization) — STATUS: partial
**What:** CJK6 atom translation (Qwen on Pearl Star); locale parity; quality contracts/golden regression.
**Authority:** `config/localization/quality_contracts/README.md`; `config/localization/locale_registry.yaml`.
**Entry points:** `scripts/localization/translate_atoms_to_locale.py`; `scripts/translate_atoms_all_locales_cloud.py`, `validate_translations.py`, `merge_translation_shards.py`, `check_golden_translation.py`. Workflows: `translate-atoms-qwen-matrix.yml`, `locale-gate.yml`, `generate-and-translate-atoms.yml`, `translate-bestseller-atoms.yml`.
**Gaps:** **Known bug:** `translate_atoms_to_locale.py` truncates atoms >8000 chars (drops `##` variants) across ALL CJK locales — likely contaminated prior sprints. Fix = chunk-per-variant + count guard, PR #1658 OPEN. Atom coverage ~85% ja-JP/zh-TW (Phase-A grid); CJK is voice/infra-gated.

### 16. integrations — STATUS: done (steady-state)
**What:** API/credential management; RunComfy, FLUX, ElevenLabs/CosyVoice, HF, messaging, podcast/storefront resource IDs.
**Authority:** `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` (2026-06-13); `skills/pearl-int/SKILL.md`.
**Entry points:** `scripts/ci/integration_env_registry.py`, `load_integration_env_from_keychain.py`, `check_integration_env.py`; `skills/pearl-int/references/`.
**Gaps:** RunComfy decommission Option-1 shipped (PR #1569: cap $25→$10, creds/cap/docs decommissioned, Keychain purged); full code rip-out + billing cancel **deferred** (`runcomfy_batch.py` is a shared lib with ~9 importers + 8 CI workflows + tests — deleting breaks manga + Core).

### 17. trend_feeds — STATUS: partial (on main + local-only acquisition)
**What:** RSS + SerpApi + Exploding Topics → scoring → BookSpec injection → MarketRouter boost.
**Authority:** `docs/TREND_FEED_INTEGRATION_STRATEGY.md`; `scripts/feeds/`.
**Entry points:** `config/trend_keywords/`; `scripts/feeds/budget_guard.py`. Workflow: `research_feeds_ingest.yml`.
**Gaps:** On main (PR #68): BookSpec `trend_heat_score` + MarketRouter trend elevation. **Still local-only:** acquisition layer (tier YAMLs, feed scripts) — treat as backlog until promoted.

### 18. recommendations — STATUS: not-started (backlog)
**What:** Catalog-facing recommender: which books to create next. Rules-based Phase 1.
**Authority:** `config/recommender/`; DOCS_INDEX Phoenix Recommender section.
**Entry points:** `config/recommender/{scoring_weights,constraints,hard_gates}.yaml` — but per DOCS_INDEX the `phoenix_recommender/` package and these configs are **"backlog reference; file not present"**.
**Gaps:** Entire package not built (Phase 1 rules-based scoring + hard gates). `ws_recommender_promotion` marked completed but DOCS_INDEX says package absent — verify. Lowest priority.

### 19. dashboard — STATUS: partial
**What:** Operator brand-admin v2 + onboarding hub + exec catalog dashboard.
**Authority:** PEARL_ARCHITECT_STATE DASH-02; `BRAND_ADMIN_CANONICAL_PACKAGE.md`.
**Entry points:** `brand_admin_weekly_os.html`, `brand-wizard-app/public/exec_catalog_dashboard.html`, `dashboard/`, root `dashboard.py` + `revenue_dashboard.jsx` (verify currency). Overlaps heavily with brand_admin (5).
**Gaps:** Brand-admin v2 navigate link; teacher_showcase media wiring; v2 axes_present field maintenance. Root `dashboard.py` / `revenue_dashboard.jsx` currency unclear (see deletion candidates — LOW confidence).

### 20. music_companions — STATUS: not-started (proposed)
**What:** Per-book companion music tracks via MusicGen queue.
**Authority:** `docs/specs/MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md` §6; PEARL_ARCHITECT_STATE MUSIC-MODE-V1-01-AMENDMENT-V2.
**Entry points (PROPOSED):** `artifacts/music_companions/`; `config/music/musicgen_config.yaml`; `scripts/music/musicgen_render_worker.py`.
**Gaps:** Queue integration proposed; MusicGen workload (`ws_pearl_int_pearl_star_phase_b_musicgen_workload`) open.

### 21. sangha_program — STATUS: not-started (proposed)
**What:** Sangha Karma Yoga volunteer program + level progression.
**Authority:** `docs/specs/SANGHA_KARMA_YOGA_PROGRAM_SPEC.md` + `_LEVEL_PROGRESSION_SPEC.md` (2026-06-12); PEARL_ARCHITECT_STATE SANGHA-KARMA-YOGA-V1-01.
**Entry points (PROPOSED):** `config/sangha_program/`; `artifacts/programs/sangha_karma_yoga_20260606/`.
**Gaps:** Config + volunteer roster proposed; recruitment-copy ws open. Sourced partly from `old_chat_specs/USLF_3_LA.txt`.

### 22. ite (manga in-the-engine pipeline) — STATUS: done (rolled into manga)
**What:** Manga gate runner / ITE pipeline.
**Authority:** `phoenix_v4/manga/ite_pipeline.py`; `config/manga/gate_registry.yaml`.
**Gaps:** F11 hardening + gate_registry maintenance (rolled into manga_pipeline ws's).

---

## Cross-cutting: devops / CI — STATUS: done (active, hot)
**What:** GitHub operations, governance gate, branch protection, push safety, LLM-policy enforcement.
**Authority:** `docs/GITHUB_OPERATIONS_FRAMEWORK.md`, `docs/GITHUB_GOVERNANCE.md` (2026-06-16), `docs/BRANCH_PROTECTION_REQUIREMENTS.md`, `CLAUDE.md`.
**Entry points:** `.github/workflows/` (**88 workflows**); `scripts/ci/`, `scripts/git/`; `config/governance/required_checks.yaml`. Required check on "Protect main" ruleset = **Verify governance** (+ atoms-parse-sweep promoted #1640).
**Notable:** `main` is ruleset-protected but **repo-admin has pull_request bypass** → operator self-merges aren't hard-gated; Core/Release aren't required checks and don't run on push-to-main → red won't block a merge (verify test health manually). `.claude/worktrees/**` is committed to origin/main (~110GB) → disk poison; phantom-deletion hazard documented.

---

## Cross-cutting: NOT a subsystem but present
- **Qwen / Qwen-Agent** (root) — submodules; PROTECTED, never touch.
- **PhoenixControl/** — native macOS Swift control-plane app (10 tabs). Documented in DOCS_INDEX; status = present, build via Xcode.
- **brand-wizard-app/** — React onboarding/director app → CF Pages on merge. `node_modules/` is tracked (6,984 files) — LFS/gitignore lane open.
- **server/** — FastAPI (brand onboarding routes, Fernet credential vault `server/crypto.py` + `/api/v1/admin/credentials`).

---

## Status roll-up

| STATUS | Subsystems |
|--------|-----------|
| done | integrations, naming, ite, devops/CI; (pearl_news done-but-high-drift; catalog_planning done/partial) |
| partial | core_pipeline, pearl_prime, manga_pipeline, video_pipeline, brand_admin, storefront, audiobook_pipeline, podcast_pipeline, music_mode, ei_v2, teacher_mode, translation, trend_feeds, dashboard |
| not-started | recommendations, music_companions, sangha_program |

The two load-bearing partials are **core_pipeline** (register_gate/word-budget HARD_FAILs, cohesion frontier) and **manga_pipeline** (V2 phases C–E). Everything customer-facing (storefront, brand_admin director data, music live route, video assembler) is mockup/scaffold-stage, not live.
