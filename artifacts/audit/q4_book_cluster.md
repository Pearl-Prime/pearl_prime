# Q4 BOOK CLUSTER PRODUCTION AUDIT

Audit window: 2026-04-29
Worktree: `wonderful-meitner-e5ac76` @ branch `claude/wonderful-meitner-e5ac76`
Baseline commit: `6375c8fcbf` (HEAD)
Subsystem authority map: `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
Active workstreams source: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (105 lines, 104 rows)

Read-only audit. No production code, content, spec, or workflow modification was performed. The only write target was this file.

Method
- Authority + config existence: `ls`/`wc -l`.
- Observable output: `find artifacts/...` for real artifacts; `git log -1 -- <path>` for last-output dates.
- Test coverage: `find tests -name '*.py' -exec grep -l <kw> {} \; | wc -l`.
- CI coverage: `grep -l -i <kw> .github/workflows/*.yml`.
- Active workstreams: column-6 (subsystem) match in TSV.
- Drift spot-check: pull 2-3 must-have features per authority doc and locate code.

---

## 1. core_pipeline

- **subsystem_id**: `core_pipeline`
- **owner_agent**: Pearl_Prime (per `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv:2`)
- **authority_doc_present?**: yes
  - `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` — 361 lines, present
  - `specs/PHOENIX_V4_5_WRITER_SPEC.md` — 1235 lines, present
- **config_present?**: yes — `config/governance/system_registry.yaml` (150 lines; `head -3` confirms it is the change-observation registry, not the pipeline runtime config)
- **producing_observable_output?**: yes
  - 13 EPUBs in `artifacts/epub/` ranging 498 KB–1.77 MB (e.g. `master_wu_courage.epub` 1,765,143 bytes)
  - Multiple `book.txt` outputs: `artifacts/production_run/adi_da_self_worth_full/book.txt`, `artifacts/qa_book_6h/book.txt`, `artifacts/audiobook_samples/_registry_grief_render/book.txt` (42,583 bytes), `artifacts/simulation/book_0052/book.txt`
  - 6-hour book artifacts: `artifacts/gen_alpha_anxiety_6hr_book.txt` and `_with_alias.txt`
- **last_real_output_date**: 2026-04-17 (`git log -1 -- artifacts/video/` SHA `4ae70c79ae`, "Rhetorical architecture: memory, scorer, and 4 YAML banks (BSG-016-019)" — most recent core_pipeline-adjacent artifact movement); EPUBs themselves last touched 2026-04-05 via `8d6c550969`
- **test_coverage**: 0 files match literal `core_pipeline`, but ~10 cover the actual code paths: `tests/test_book_renderer.py`, `tests/test_bridge_transition_system.py`, `tests/test_compose_from_enriched_book_bridges.py`, `tests/test_mechanism_thesis_system.py`, `tests/test_registry_plan_runtime_format.py`, `tests/test_exercise_governance.py`, `tests/test_topic_identity_resolution.py`, `tests/test_teacher_mode_e2e_smoke.py`, `tests/test_exercise_wrapper_system.py`, `tests/test_budget_check.py`. (Keyword `core_pipeline` is sparse in test code — naming drift.)
- **CI_workflow_coverage**: `catalog-book-pipeline.yml`, `book-flagship-qa-ladder.yml`, `single-book-smoke.yml`, `weekly-book-rollout.yml`, `full-catalog-cli-en-us.yml`, `release-gates.yml`, `regression-investigation-deep-book.yml`, `simulation-10k.yml`, `nightly-regression.yml` (9 named workflows on the book hot path)
- **active_workstream_count**: 22 with `core_pipeline` as sole subsystem; 43 with `core_pipeline` somewhere in subsystem column (TSV col-6 grep). Recent: `ws_bridge_transition_system_20260416` (in_progress, 2026-04-16), `ws_spec_739_phase_3_strict_runtime_20260427` (proposed), `ws_spec_739_validator_teacher_banks_awareness_20260428` (proposed)
- **percent_complete_estimate**: **70%** — ships real EPUB output, has 9 CI workflows, deep test coverage. Still drifting on Spec 739 strict-runtime + bridge-transition rebuild + topic identity (3 in-flight workstreams with "proposed"/"in_progress" states).
- **top_3_blockers_to_100%**:
  1. `ws_bridge_transition_system_20260416` in_progress — bridge bank rebuild blocks spec compliance with `specs/PHOENIX_V4_5_WRITER_SPEC.md` chapter composer expectations (TSV row, evidence_paths cite `phoenix_v4/rendering/chapter_composer.py`)
  2. Spec 739 phase-3 strict runtime is still `proposed` (`ws_spec_739_phase_3_strict_runtime_20260427`) — runtime truth gate not yet enforcing
  3. Test naming drift: zero test files literally match `core_pipeline`; coverage exists but is unaddressable by subsystem-keyed tooling
- **phase_tag**: **Phase 2** (Pearl Prime book pipeline) — core renderer/ARC/composer is the engine under Pearl Prime

---

## 2. pearl_prime

- **subsystem_id**: `pearl_prime`
- **owner_agent**: Pearl_Prime
- **authority_doc_present?**: yes
  - `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` — 442 lines
  - `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` — 587 lines
- **config_present?**: yes — `config/brand_registry.yaml` (150 lines, `schema_version: 1`, `owner: pearl_prime`); `config/brand_author_assignments.yaml` (20 lines)
- **producing_observable_output?**: yes — Pearl Prime release evidence persisted: `artifacts/release/pearl_prime_release_evidence.json`, `artifacts/release/latest_systems_test_report.json`, `artifacts/release/rollback_smoke_evidence.json`, `artifacts/release/workflow_run_manifest.json`. EPUBs in `artifacts/epub/` are downstream of Pearl Prime planning. Bestseller compile gate produced output as recently as #548 (`fix(pearl_prime): canary sentinel engine mismatch — bestseller FAIL→PASS (#548)`, 2026-04-21).
- **last_real_output_date**: 2026-04-22 (`git log -1 -- artifacts/ei_v2/` `f2b023a3fc`; release evidence in artifacts/release tracked through #563)
- **test_coverage**: 5 files match `pearl_prime`; 17 match `bestseller` (the heart of the overlay spec). E.g. `tests/test_pearl_prime_release_evidence.py`, `tests/test_bestseller_craft_quality.py`, `tests/test_pearl_prime_*` family
- **CI_workflow_coverage**: `release-gates.yml`, `simulation-10k.yml`, `audiobook-regression.yml`, `no-binary-blobs.yml`, `variant-coverage-gate.yml`, `translate-bestseller-atoms.yml`. Plus implicit gates on `book-flagship-qa-ladder.yml` and `weekly-book-rollout.yml`.
- **active_workstream_count**: 24 (col-6 contains `pearl_prime`). Recent: `ws_spec_739_phase_2_persona_atom_authoring_20260427` proposed, `ws_midlife_women_arc_authoring_20260427` pending, `ws_story_cell_authoring_20260425` active, `ws_pilot_pipeline_default_20260425` completed, `ws_bestseller_pipeline_default_path_a_20260425` completed
- **percent_complete_estimate**: **65%** — overlay spec is partially implemented (`tests/duration/test_duration_qc.py` covers 5F runtime truth; teacher compile gate at `scripts/ci/check_teacher_readiness.py`/`run_teacher_production_gates.py` covers 5C). 5A topic identity has only one matching file (`phoenix_v4/planning/output_contract.py`). Sentinel acceptance evidence dir is empty (`artifacts/sentinel/` returned no files).
- **top_3_blockers_to_100%**:
  1. **Sentinel acceptance tuple not produced as on-disk artifact** — `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md:99` defines sentinel acceptance tuple but `ls artifacts/sentinel/` returns empty. Only `artifacts/release/pearl_prime_release_evidence.json` exists.
  2. 5A "topic identity must not silently drift" (`docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md:118`) — single file (`phoenix_v4/planning/output_contract.py`) covers it; weak surface area
  3. Multiple proposed Spec-739 phases (phase_2, validator_teacher_banks_awareness, phase_3_strict_runtime) still gating final pearl_prime hardening
- **phase_tag**: **Phase 2** (Pearl Prime book pipeline)

---

## 3. audiobook_pipeline

- **subsystem_id**: `audiobook_pipeline`
- **owner_agent**: Pearl_Dev
- **authority_doc_present?**: yes
  - `docs/AUDIOBOOK_OPS_MANUAL.md` — 853 lines
  - `docs/AUDIOBOOK_PIPELINE_SPEC.md` — 543 lines (Qwen-only comparator loop)
- **config_present?**: **partial** — `scripts/audiobook/` exists but has only **2 files** (`__init__.py` + `generate_showcase_bundle.py`, 36 KB). The spec's actual implementation lives at `scripts/audiobook_script/` (note: different dir!) — `run_comparator_loop.py` and `run_regression.py` confirm spec features. `config/audiobook/` is **MISSING**. `config/video/audiobook_style.yaml` (58 lines) is present.
- **producing_observable_output?**: yes — 13 chapter-1 MP3s in `artifacts/audiobook_samples/` (3.6–6.2 MB each, e.g. `joshin_anxiety_ch1.mp3` = 5.7 MB), `manifest.json` (14 KB), prose siblings in `_prose/`. **Only ch1 — no full audiobooks.**
- **last_real_output_date**: 2026-04-12 (`git log -1 -- artifacts/audiobook_samples/` SHA `a887415038`)
- **test_coverage**: 3 files match `audiobook` — `tests/test_legacy_template_loader.py`, `tests/test_intro_ending_variation.py`, `tests/duration/test_plan_book_duration.py`
- **CI_workflow_coverage**: `audiobook-regression.yml` (CI runs **dry-run + schema only**; "Full regression (requires LM Studio) runs on manual dispatch only" — `.github/workflows/audiobook-regression.yml:3`), `translate-bestseller-atoms.yml`
- **active_workstream_count**: 8 hits for `audiobook` in TSV; only a couple are audiobook-primary (most are video/manga workstreams that mention audiobook tangentially in evidence column)
- **percent_complete_estimate**: **35%** — spec is rich (1396 combined lines) but the canonical implementation dir per the spec (`scripts/audiobook/`) has only a single non-init file. The actual scripts moved/forked to `scripts/audiobook_script/` — directory authority is split. Output is ch1-only — no full-book audiobook has shipped.
- **top_3_blockers_to_100%**:
  1. **Authority/code path drift**: spec authority says `scripts/audiobook/` (per `SUBSYSTEM_AUTHORITY_MAP.tsv:15`) but real code is at `scripts/audiobook_script/run_comparator_loop.py`. Authority TSV is wrong OR scripts are misplaced.
  2. **No full-book audiobook output**: `artifacts/audiobook_samples/*_ch1.mp3` is the only output. Multi-chapter render pipeline has not been exercised end-to-end on disk.
  3. **CI is shallow**: `audiobook-regression.yml` only runs schema check in CI; full regression is dispatch-only and requires LM Studio (self-hosted) — no automated full-book gate.
- **phase_tag**: **Phase 5/6** (multi-locale ship + full automation; audiobook is downstream of Pearl Prime book completion)

---

## 4. podcast_pipeline

- **subsystem_id**: `podcast_pipeline`
- **owner_agent**: Pearl_Prime (status="proposed" per `SUBSYSTEM_AUTHORITY_MAP.tsv:18`)
- **authority_doc_present?**: **partial**
  - `docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md` — 688 lines, present
  - `pearl_news/research/podcast/` — **MISSING** (`ls` returns no such dir)
- **config_present?**: **partial** — `scripts/podcast/` exists with 7 files (all spec gaps 7a–7e implemented: `assemble_podcast_episode.py` 260 lines, `render_podcast_audio.py` 580 lines, `generate_podcast_feed.py` 162 lines, `upload_podcast_to_r2.py` 98 lines, `run_podcast_pipeline.py` 263 lines). `config/integrations/podcast_credentials.yaml` is **MISSING** (referenced by `SUBSYSTEM_AUTHORITY_MAP.tsv:18`). `config/podcast/` exists.
- **producing_observable_output?**: **no** — only `artifacts/podcast_pilot/pilot_report.md` (2179 bytes) and a stale `artifacts/production_run/adi_da_self_worth_full/podcast.log`. Zero rendered audio episodes, zero feed XML on disk.
- **last_real_output_date**: 2026-04-08 (`git log -1 -- artifacts/podcast_pilot/` SHA `25860d0531`, "feat: podcast pipeline — scripts, admin API, CI, marketing research")
- **test_coverage**: 2 files — `tests/test_podcast_pipeline.py`, `tests/duration/test_duration_qc.py`
- **CI_workflow_coverage**: `podcast-weekly.yml` only
- **active_workstream_count**: 6 hits; the live one is `ws_podcast_pipeline_execution_20260427` (proposed, 2026-04-27, subsystem=`core_pipeline` — spec/run cluster not yet kicked off)
- **percent_complete_estimate**: **30%** — scripts exist (spec gaps 7a–7e all coded) but no episodes ever rendered to disk; credentials config missing; status is officially "proposed" per authority map.
- **top_3_blockers_to_100%**:
  1. **Missing credentials config**: `config/integrations/podcast_credentials.yaml` does not exist (authority map line 18 references it as required)
  2. **Missing pearl_news research dir**: `pearl_news/research/podcast/` not created — authority doc is half-present
  3. **No actual podcast output on disk**: only pilot_report.md (2 KB) — `ws_podcast_pipeline_execution_20260427` is still `proposed`, and no full episode trace exists in `artifacts/podcast*`
- **phase_tag**: **Phase 4** (Pearl News + brand_admin layer; podcast is content-feed adjacent and downstream of brand_admin platform lanes per spec gaps 2 + 4)

---

## 5. video_pipeline

- **subsystem_id**: `video_pipeline`
- **owner_agent**: Pearl_Video
- **authority_doc_present?**: yes — `scripts/video/README.md` (50 lines), `config/video/` (34 items)
- **config_present?**: yes — `config/video/render_params.yaml` (38), `config/video/upload_config.yaml` (218), `config/video/audiobook_style.yaml` (58), `config/video/format_specs.yaml` (158), `config/release_velocity/video_cadence.yaml` (76) — **all 5 configs present**
- **producing_observable_output?**: yes — `artifacts/video/` has 13 subdirs including `rendered/`, `timelines/`, `tiktok_body_awareness/`, `provenance/`, `image_banks/`, `plan-therapeutic-001/`, `test-vce-001/`, `test_render_out/2`. Code surface is heavy: 38 items in `scripts/video/` including `orchestrate_book_to_video.py`, `render_videos.py`, `run_pipeline.py`, full render/QC/upload chain.
- **last_real_output_date**: 2026-04-17 (`git log -1 -- artifacts/video/` SHA `4ae70c79ae`)
- **test_coverage**: 22 files match `video` (highest in cluster after ei_v2)
- **CI_workflow_coverage**: `generate-video-bank.yml`, `video-daily-publish.yml` (and overlap from `flux*` adjacent workflows). Path-filtered.
- **active_workstream_count**: 12 hits; closures dominate (`ws_voice_pipeline_activation_20260409`, `ws_unified_pipeline_jobs_20260410`, `ws_video_p0_upgrades_20260410`, `ws_pipeline_verification_audit_20260410`, `ws_tts_provider_hardening_20260410`, `ws_video_enhancement_research_20260410`); `ws_video_image_washout_fix_20260411` is `active`
- **percent_complete_estimate**: **75%** — heavy code surface (38 scripts), 22 tests, 5 configs, 2 dedicated workflows, real rendered output. Upload/cadence wiring proven.
- **top_3_blockers_to_100%**:
  1. `ws_video_image_washout_fix_20260411` still `active` — image quality regression not yet closed
  2. Many `test_render_*` dirs in artifacts/ suggest test/staging output dominates — no clear shipped-to-platform manifest in `artifacts/video/rendered/`
  3. `video-daily-publish.yml` exists but the daily-publish loop's success/failure trace isn't visible in artifacts (no published-episode ledger)
- **phase_tag**: **Phase 4/5** (video is brand-admin/marketing-fed and ships to multiple platforms; depends on Pearl Prime audiobook prerequisites)

---

## 6. ei_v2

- **subsystem_id**: `ei_v2`
- **owner_agent**: Pearl_Research
- **authority_doc_present?**: yes — `phoenix_v4/quality/ei_v2/` exists with 18 modules (`config.py`, `cross_encoder_reranker.py`, `dimension_gates.py`, `domain_embeddings.py`, `duration_fit.py`, `ei_warnings.py`, `emotion_arc_validator.py`, `hybrid_selector.py`, `learner.py`, `llm_callback.py`, `manga_dialogue_gates.py`, `marketing_lexicons.py`, `research_lexicons.py`, `safety_classifier.py`, `semantic_dedup.py`, `tts_readability.py`, `visual_therapeutic.py`)
- **config_present?**: yes — `config/quality/ei_v2_config.yaml` (219 lines, head shows marketing_sources/research_kb/safety_classifier sections all populated)
- **producing_observable_output?**: yes — `artifacts/ei_v2/` has 14 files including `eval_rigorous_report.json` (6.1 MB), `ei_v1_v2_comparison.json` (250 KB), `learner_feedback.jsonl` (22 KB), `marketing_integration.log` (36 KB), `learned_params.json`, `promotion_gate_result.json`, `promotion_history.jsonl`, `pr_ri_kb_activation_evidence.txt`
- **last_real_output_date**: 2026-04-22 (`git log -1 -- artifacts/ei_v2/` SHA `f2b023a3fc`)
- **test_coverage**: 21 test files match `ei_v2` — `tests/test_ema_learner_integration.py`, `tests/test_book_renderer.py`, `tests/test_ei_v2_marketing_lexicons.py`, `tests/test_llm_callback.py`, `tests/test_exercise_governance.py` (and 16 more)
- **CI_workflow_coverage**: `ei-v2-gates.yml` (dedicated, runs on every PR + weekly cron + push to main; `name: EI V2 gates`), `catalog-book-pipeline.yml`. EI V2 explicitly **advisory until promotion** per workflow header — V1 still authoritative.
- **active_workstream_count**: 7 (TSV grep `ei_v2`)
- **percent_complete_estimate**: **70%** — code is rich (18 modules), tests are deep (21 files), CI is dedicated, output is voluminous. Honest discount: per `.github/workflows/ei-v2-gates.yml:5` "V1 remains authoritative; V2 is advisory until promotion." So V2 is not yet load-bearing in production decisions.
- **top_3_blockers_to_100%**:
  1. **EI V2 still advisory, not authoritative**: `.github/workflows/ei-v2-gates.yml:5` says V1 authoritative. Promotion gate at `artifacts/ei_v2/promotion_gate_result.json` (696 bytes) but `promotion_history.jsonl` is only 302 bytes — promotion not yet executed at scale.
  2. `learner_feedback.jsonl` (22 KB) implies learner has run, but `learned_params.json` (292 bytes) vs `learned_params_seed.json` (290 bytes) — learning delta is essentially seed; no real learning yet
  3. Promotion criteria gate (`config/research_metadata/promotion_criteria.yaml` referenced in `config/quality/ei_v2_config.yaml`) not verified to be enforced in any CI job
- **phase_tag**: **Phase 0** (foundation/safety) — EI V2 is the quality safety net underlying every other subsystem

---

## 7. translation

- **subsystem_id**: `translation`
- **owner_agent**: Pearl_Localization
- **authority_doc_present?**: yes — `config/localization/quality_contracts/` has 4 files (`README.md`, `glossary.yaml`, `golden_translation_regression.yaml`, `release_thresholds.yaml`)
- **config_present?**: yes — `config/localization/locale_registry.yaml` (400 lines, `schema_version: 1`, defines en-US, ja-JP, zh-CN, zh-TW, zh-HK, etc. per `head -25` showing canonical locale block)
- **producing_observable_output?**: **partial** — `artifacts/translations/` has 3 resume logs (ja-JP, zh-CN, zh-TW each ~360 KB) from 2026-04-22; `artifacts/localization/` has parity report (3.4 KB), checkpoints (3 KB), coverage snapshots, plus `batch_runs/`. **No actual translated book/atom output found at top-level — output paths flow through `SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms_localized/`** (e.g. `SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms_localized` exists)
- **last_real_output_date**: 2026-04-22 (`git log -1 -- artifacts/translations/` SHA `f2b023a3fc`); 2026-04-20 for `artifacts/localization/` (SHA `c76a4a1971`)
- **test_coverage**: 6 files match `translation`; many under `phoenix_v4/manga/translation`
- **CI_workflow_coverage**: `locale-gate.yml`, `generate-and-translate-atoms.yml`, `translate-bestseller-atoms.yml`, `translate-atoms-qwen-matrix.yml` (4 workflows — strong CI surface)
- **active_workstream_count**: 3 with subsystem-col-6=`translation`; 10 total hits across the file. Recent ship: 2026-04-20 commit `feat(localization): CJK atom translation tooling (DashScope-only, qwen2.5-plus, resumable)` — directly the resume logs above.
- **percent_complete_estimate**: **60%** — locale registry is canonical and 4 quality contract files present. Translation tooling shipped 2026-04-20 with resume logs as evidence. Per `proj_state_convergence_20260328 / ws_post_pr478_manga_activation_20260418` row (TSV active workstreams), CJK locale coverage is uneven: zh_TW 92.1%, ja_JP 89.3% (~366 atoms remaining), zh_CN sprint pending ~2200 atoms. Not 100% atom-coverage anywhere yet.
- **top_3_blockers_to_100%**:
  1. **Atom coverage gap**: zh_CN ~2200 atoms remaining; ja_JP ~366 remaining (per `ACTIVE_WORKSTREAMS.tsv:ws_post_pr478_manga_activation_20260418` blockers col)
  2. **No `artifacts/translation/` (singular)**: authority doc directs `config/localization/quality_contracts/` but artifact persistence pattern is split between `artifacts/translations/` (logs) and `artifacts/localization/` (checkpoints) and `SOURCE_OF_TRUTH/teacher_banks/*/approved_atoms_localized/` — three-way fragmentation
  3. `golden_translation_regression.yaml` exists (`config/localization/quality_contracts/`), but no run output proving regression is currently green — `release_thresholds.yaml` may be unverified at last ship
- **phase_tag**: **Phase 5** (multi-locale ship) — direct enabler for this phase

---

## SUMMARY TABLE

| # | subsystem_id        | auth_doc | config  | output  | last_output | tests | CI workflows                 | workstreams | %   | phase |
|---|---------------------|----------|---------|---------|-------------|-------|------------------------------|-------------|-----|-------|
| 1 | core_pipeline       | yes      | yes     | yes     | 2026-04-17  | ~10   | 9 (catalog/flagship/single/weekly/full/release/regression/sim/nightly) | 22 / 43 | 70  | 2     |
| 2 | pearl_prime         | yes      | yes     | yes     | 2026-04-22  | 5/17* | 6 (release/sim/audiobook-reg/no-binary/variant-cov/translate-bestseller) | 24      | 65  | 2     |
| 3 | audiobook_pipeline  | yes      | partial | partial | 2026-04-12  | 3     | 2 (audiobook-regression CI=schema-only; translate-bestseller-atoms) | 8       | 35  | 5/6   |
| 4 | podcast_pipeline    | partial  | partial | no      | 2026-04-08  | 2     | 1 (podcast-weekly)            | 6           | 30  | 4     |
| 5 | video_pipeline      | yes      | yes     | yes     | 2026-04-17  | 22    | 2 (generate-video-bank, video-daily-publish) | 12 | 75  | 4/5   |
| 6 | ei_v2               | yes      | yes     | yes     | 2026-04-22  | 21    | 2 (ei-v2-gates dedicated, catalog-book-pipeline) | 7 | 70  | 0     |
| 7 | translation         | yes      | yes     | partial | 2026-04-22  | 6     | 4 (locale-gate, generate-and-translate, translate-bestseller, translate-qwen-matrix) | 3 / 10 | 60 | 5 |

`*` pearl_prime test count: 5 literal `pearl_prime`, 17 `bestseller`-keyed.

Cluster averages: mean ≈ **57.9%**; median = 65%.

---

## CLUSTER-LEVEL ROLLUP

- **Cluster average %**: 57.9% (mean), 65% (median)
- **Subsystems shipping observable production output**: 4 (core_pipeline, pearl_prime, video_pipeline, ei_v2) — all >= 65%
- **Subsystems blocked / partial output**: 3 (audiobook_pipeline 35%, podcast_pipeline 30%, translation 60%)
- **Subsystems with broken authority alignment**: 2 (audiobook — TSV authority points to `scripts/audiobook/` but code lives at `scripts/audiobook_script/`; podcast — `pearl_news/research/podcast/` and `config/integrations/podcast_credentials.yaml` both missing)
- **Subsystems where spec is "advisory" not "authoritative"**: 1 (ei_v2 — V1 still authoritative per `.github/workflows/ei-v2-gates.yml:5`)
