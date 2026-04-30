# Q4 Audit — Manga Production Cluster

**Date:** 2026-04-29
**Branch:** `claude/wonderful-meitner-e5ac76`
**Scope:** read-only audit of 5 manga subsystems (`manga_pipeline`, `manga_catalog`, `ite`, `lora_pipeline`, `character_consistency`).
**Method:** filesystem existence checks, output-funnel counts, GitHub PR API, workflow grep, ACTIVE_WORKSTREAMS/ACTIVE_PROJECTS rows.

---

## 1. `manga_pipeline`

- **subsystem_id:** `manga_pipeline`
- **owner_agent:** `Pearl_Dev`
- **authority_doc_present:** YES — `specs/AI_MANGA_PIPELINE_SUMMARY.md`, `docs/MANGA_IMPLEMENTATION_OUTLINE.md`, `config/manga/gate_registry.yaml` (30 gates across Structural / Visual / Silence / Lettering / Layout / Transmission categories), `schemas/manga/` contains 26 schema files.
- **config_present:** YES — `config/manga/` has 27 YAML/dir entries (gate_registry, manga_taxonomy, manga_pacing_by_genre, format_routing, panel_layout_templates, etc.).
- **producing_observable_output:** PARTIAL.
  - `artifacts/manga/chapter_scripts/` → 2 series, 3 episode YAMLs total (`stillness_press__ahjan/ep_001.yaml`, `ep_002.yaml`; `warrior_calm_cultivation__master_wu/ep_001.yaml`).
  - `artifacts/manga/panel_prompts/` → 2 episodes, ep_001 each (e.g. `stillness_press__ahjan.../ep_001.panel_prompts.json` = 35 panel prompts, FLUX-schnell-fp8 ready, avg 664 / max 885 chars per ACTIVE_PROJECTS row).
  - `artifacts/manga/stillness_press_qa_run/` is a single end-to-end run from a prior pass that DID produce composites: `final_page_composite/page_001.png` … `page_003.png` + a 419 KB `manga.pdf`. This is QA-fixture territory, not a shipped episode.
  - `artifacts/manga/anxiety_series/final_page_composite/` → exactly 1 page (`page_001.png`).
  - **No `artifacts/manga/episodes/` directory exists.**
- **last_real_output_date:** Apr 29 2026 (this worktree's checkout — files are committed; the last real catalog/pipeline merge was 2026-04-26 PR #696 "2X.4 atomic — schema flip + 848 stale YAML deletes + 1,410 regen").
- **test_coverage:** 25 dedicated `tests/test_manga_*.py` files + `tests/manga/`, `tests/duration/test_plan_manga_pages.py`, `tests/fixtures/manga`. `grep -r 'manga' tests/ | wc -l` = 244 occurrences. Coverage spans schemas, schema-refs, chapter writer, lettering, bubble e2e, dialogue gates, pacing YAML, runner replay, runcomfy backend, image_bank gate.
- **CI_workflow_coverage:** 16 manga-prefixed workflows (`backend-flip`, `bubble-regression`, `catalog-plan-regen-check`, `character-sheet-build`, `fonts-acquire`, `image-bank-build`, `image-gen`, `operator-setup-verify`, `pipeline`, `quality-analysis`, `quality-forensic-analysis`, `rollout-notify`, `series-pitch`, `smoke-test`, `stash-reminder`, `workflows-yml-validate`) + `weekly-manga-rollout.yml`. Only **3 are scheduled** (`manga-bubble-regression`, `manga-operator-setup-verify`, `weekly-manga-rollout` cron `0 14 * * 1`). Remaining 14 are `workflow_dispatch`-only. Two require self-hosted runner `[self-hosted, pearl-star-gpu]` (manga-pipeline, weekly-manga-rollout — implicit GPU dependency).
- **active_workstream_count:** 11 manga-bearing workstreams in ACTIVE_WORKSTREAMS.tsv (5 under `proj_state_convergence_20260328`, 11 under `proj_manga_catalog_reconciliation_20260426`, plus brand-canon row dated 2026-04-27).
- **percent_complete_estimate:** **35%.** Schemas, gates, scripts, and CI are wired. The actual production run has shipped 0 episodes through the full funnel (35 panel prompts → 0 production renders for ep_001 The Alarm Is Lying); the only end-to-end output is the QA fixture, not a real episode.
- **top_3_blockers:**
  1. `scripts/manga/queue_panel_renders.py` IS present (verified) but per ACTIVE_PROJECTS `proj_manga_first_ship_20260425` row was flagged "NOT YET COMMITTED per runbook §5 B" — needs reverify against current ep_001 ship state (likely landed but ship still hasn't fired).
  2. R2 secrets gate: `R2_ACCOUNT_ID` and `R2_BUCKET` ARE in `scripts/ci/integration_env_registry.py` (lines 52–53) — registry gap is closed. Outstanding: GATE-OP-1 (operator add to GitHub Actions secrets) + GATE-OP-2 (Pearl Star marker file install). Both still operator-pending per `proj_manga_first_ship_20260425.next_action`.
  3. Drift on FLUX renders — PR #802 (open, MERGEABLE, +1097/-0, created 2026-04-29) identifies `flux1-schnell-fp8.safetensors` running at `steps=24, cfg=4.0` as a known anti-pattern + `no text, no typography` smuggled into the POSITIVE prompt + en_US locale-hint actively suppressing manga prior. Not yet merged → operator action #1 pending.
- **phase_tag:** `READY_TO_SHIP_BUT_BLOCKED_ON_GPU_OPS`.

---

## 2. `manga_catalog`

- **subsystem_id:** `manga_catalog`
- **owner_agent:** `Pearl_Architect`
- **authority_doc_present:** YES — `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (refreshed 2026-04-26 to v1.1 via PR #687), `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md`, `docs/GENRE_PORTFOLIO_PLAN.md`, `docs/CJK_CATALOG_PLAN.md`, `docs/US_CATALOG_PLAN.md`. `MANGA_FULL_CATALOG_PLAN.md` is now AUTO-GENERATED (per spec D-17) by `scripts/manga/generate_catalog_plan_from_strategic.py`.
- **config_present:** YES — `config/source_of_truth/manga_series_plans/` and `config/source_of_truth/manga_book_plans/` are populated (counts below).
- **producing_observable_output:** YES.
  - **series_plans:** 1,350 YAMLs (5 locales × 270 each: en_US, ja_JP, ko_KR, zh_CN, zh_TW).
  - **book_plans:** 1,351 series-dirs containing 18,900 episode YAMLs.
  - 37-brand canon plus a 5-locale routing matrix (en_US distributed; ja_JP distributed; zh_TW distributed; zh_CN `gray_zone_disclosed`; ko_KR `hold_pending_market_clearance`).
- **last_real_output_date:** 2026-04-26 (PR #696 — schema flip + 848 stale YAML deletes + 1,410 regen + #688 catalog plan generator + #694 revenue-weighted genre distribution).
- **test_coverage:** `test_manga_catalog_parity.py`, `test_manga_catalog_extractor.py`, `test_manga_catalog_plan_generator.py`. Material.
- **CI_workflow_coverage:** `manga-catalog-plan-regen-check.yml` (regen-validation), `manga-series-pitch.yml` (catalog driver). Both `workflow_dispatch`.
- **active_workstream_count:** 11 phase-2X workstreams under `proj_manga_catalog_reconciliation_20260426` (1_schema_atomic completed via #696; 2_taxonomy_routing_pacing, 3_craft_bibles, 4_catalog_generator completed via #688, 5_replace_catalog_plan completed via #696, 8_archive_specs, 9_onboarding_docs_index completed via #700).
- **percent_complete_estimate:** **80%.** Spec is canonical (v1.1), generator runs, 1,350 series + 18,900 book plans regenerated. Outstanding: 9 craft bibles (ws_2x_3) per spec §7.8, audiobook AUDIOBOOK_ rename (OQ-9 separate PR), spec-refresh-after-coordination-PR.
- **top_3_blockers:**
  1. PRE-RECONCILIATION CLIFF VERIFIED: ACTIVE_PROJECTS row warned of "132 stale series_plans + 716 stale book_plans" + retired `MANGA_FULL_CATALOG_PLAN.md`. Verification: PR #696 deleted 848 stale YAMLs and regenerated 1,410, then #688 wired the auto-generator. The cliff is **resolved**, but the new substrate (1,350 + 18,900) has not yet been validated end-to-end against any rendered episode.
  2. The 1,351-row × ~14-episode book_plan grid creates 18,900 candidate episodes; with 0 actually shipped, the catalog is overproduced relative to the pipeline's real throughput (35 panels per ep × 0 production renders).
  3. zh_CN `gray_zone_disclosed` framework needs `scripts/publish/zh_cn_release.py` per platform (OQ-6 carve-out) — not yet present.
- **phase_tag:** `RECONCILED_AND_REGENERATED_AWAITING_RENDERS`.

---

## 3. `ite` (Implicit Therapeutic Engine)

- **subsystem_id:** `ite`
- **owner_agent:** `Pearl_Dev`
- **authority_doc_present:** YES — `phoenix_v4/manga/ite_pipeline.py` (754 LOC), gates referenced in `config/manga/gate_registry.yaml` (`TRANSMISSION.STEALTH_DIALOGUE`, `TRANSMISSION.HANDOFF_CLEAN`, `TRANSMISSION.INTERNAL_RECORD_COMPLETE`, plus the schemas `ite_color_arc.schema.json`, `ite_fractal_report.schema.json`, `ite_qc_report.schema.json`).
- **config_present:** YES — `config/manga/ite_config.yaml`, `config/manga/genre_ite_profiles.yaml`.
- **producing_observable_output:** INDIRECT — runs as part of chapter pipeline; outputs land in chapter_script_internal_record + revision_queue (visible in `stillness_press_qa_run/` and `anxiety_series/`).
- **last_real_output_date:** 2026-04-26 (catalog reconciliation refresh of `genre_ite_profiles.yaml` per spec §4.1).
- **test_coverage:** Captured under chapter-runner integration tests + dialogue/transmission gates; not its own dedicated test file. Indirectly via `test_manga_dialogue_gates.py`, `test_manga_transmission.py`, `test_manga_chapter_runner_e2e_replay.py`.
- **CI_workflow_coverage:** Implicit — runs inside `manga-pipeline.yml`, `manga-quality-analysis.yml`, `manga-quality-forensic-analysis.yml`. No standalone ITE workflow.
- **active_workstream_count:** 0 dedicated; folded into chapter pipeline workstreams.
- **percent_complete_estimate:** **75%.** Engine code exists, gates wired, scripts present (`scripts/manga/ite_panel_breath.py`, `ite_qc.py`, `ite_fractal_check.py`, `ite_gutter_therapy.py`, `ite_color_arc.py`). Output flows through QA fixture but no production episode has actually exercised it end-to-end.
- **top_3_blockers:**
  1. No standalone ITE regression — depends on full chapter run, which has not happened in production.
  2. `genre_ite_profiles.yaml` post-reconciliation 5-locale × 15-genre matrix means 75 cells need profile coverage; coverage status not captured in any ITE-dedicated audit.
  3. ITE QC report schema is defined but no production episode has emitted one — gates are theoretically armed only.
- **phase_tag:** `WIRED_NEVER_FIRED_AT_PRODUCTION`.

---

## 4. `lora_pipeline` (PROPOSED)

- **subsystem_id:** `lora_pipeline`
- **owner_agent:** `Pearl_Dev` (proposed; not in authority map yet).
- **authority_doc_present:** PARTIAL — `config/manga/brand_lora_plans.yaml` present (v1, last_updated 2026-04-08, base_model FLUX.1-dev, rank=16, alpha=16, output `~/content_bank/loras/{brand_id}/`, trigger convention `{teacher_id}_{brand_suffix}`). Authority spec NOT in authority map. `PR #610` (open, MERGEABLE, created 2026-04-24) "feat(manga): protagonist LoRA specs + character image pipeline (Saki/Honoka/Ai)" still unmerged.
- **config_present:** YES — brand_lora_plans.yaml lists 12 brand_suffixes (sp/cc/sw/qf/dg/hb/rc/wc/sr/bm/so/dp), per-teacher reference_image lists (front_portrait, three_quarter_view, profile_view, expression_sheet), training_steps=1500, ip_adapter_weight 0.83–0.85.
- **producing_observable_output:** **NO.** No trained LoRA artifacts in repo. `image_bank/` contains 840 stillness_press renders organized by topic (15 topics × 56 renders each) — these are **base-model FLUX outputs, not LoRA-conditioned**. PR #623 explicitly documents LoRA training as **BLOCKED on VRAM** (FLUX-schnell-fp8 = 10.6 GB of 16 GB on Pearl Star RTX 5070 Ti, ≤5 GB left for training; OOM at rank=4, checkpoint_depth=5, fp8 dtypes, offloading, quantized_backward).
- **last_real_output_date:** N/A — no LoRA has ever been trained.
- **test_coverage:** Zero LoRA-specific tests. `test_manga_runcomfy_backend.py` exercises base-model FLUX path only.
- **CI_workflow_coverage:** None dedicated. `manga-character-sheet-build.yml` produces reference inputs but does not train.
- **active_workstream_count:** 0 dedicated; surfaces as PR #610 (open) + PR #623 (open, CONFLICTING) blocker discussion.
- **percent_complete_estimate:** **15%.** Plan exists, reference-image pipeline exists, but the actual training step is structurally infeasible on current hardware.
- **top_3_blockers:**
  1. **VRAM hard ceiling** — Pearl Star RTX 5070 Ti has 16 GB. PR #623 documents three options: (1) GPU upgrade ≥24 GB, (2) cloud training $600–$1500 for 289 chars, (3) IP-Adapter (no training, lower fidelity). No decision recorded.
  2. PR #610 unmerged — protagonist LoRA specs (Saki/Honoka/Ai) sitting open since 2026-04-24.
  3. No LoRA → drift in renders (the entire content of PR #802) is the downstream symptom: schnell-fp8 runs without character LoRAs and without proper negative-prompt routing.
- **phase_tag:** `BLOCKED_ON_HARDWARE_DECISION`.

---

## 5. `character_consistency` (12-shell × 37-brand canon)

- **subsystem_id:** `character_consistency`
- **owner_agent:** `Pearl_Architect`
- **authority_doc_present:** YES — `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (auto-generated, lists 37 brands across flagship/core/niche tiers with genre mix), `config/manga/canonical_brand_list.yaml` (Path X canon, 37 brands intent declared in header), `config/manga/character_brand_registry.yaml` (Big View Phase 3, supporting archetypes + brand→character map, generated 2026-04-22). PR #722 (merged 2026-04-26) split manga canon (37 brands) from book canon (24 archetypes × 13 lanes = 312 rows in `config/brand_management/global_brand_registry.yaml`).
- **config_present:** YES — `canonical_brand_list.yaml`, `character_brand_registry.yaml`, `manga_brand_series_plan.yaml`, `teacher_character_prompts.yaml`. Brand-canon split is post-#722 reality.
- **producing_observable_output:** PARTIAL.
  - `artifacts/manga/teacher_character_art/batch_manifest.json` — single manifest, not visible per-character art.
  - 12 of 37 brands appear to have brand_suffix entries in `brand_lora_plans.yaml`; the remaining 25 brand entries in `MANGA_FULL_CATALOG_PLAN.md` lack matching LoRA plan entries.
- **last_real_output_date:** 2026-04-27 (`ws_brand_count_canon_reconciliation_20260427` last_updated; PR #722 merged 2026-04-26).
- **test_coverage:** `test_manga_author_system.py`, `test_manga_series_setup.py`, `test_manga_chapter_visual.py`. Brand-canon reconciliation not directly tested as such; tested via series_plan generation parity.
- **CI_workflow_coverage:** `manga-character-sheet-build.yml` (workflow_dispatch).
- **active_workstream_count:** 1 active row (`ws_brand_count_canon_reconciliation_20260427` under `proj_state_convergence_20260328`).
- **percent_complete_estimate:** **45%.** Canon split landed (#722). Brand registry exists. But: only 12/37 brands have LoRA plan rows; per-brand visual style bibles are 9 craft bibles (per `proj_manga_catalog_reconciliation` ws_2x_3) still proposed-not-built; character drift documented in PR #802 confirms consistency is the failure mode in practice.
- **top_3_blockers:**
  1. 25/37 brands have no LoRA plan entry (`brand_lora_plans.yaml.brand_suffixes` has 12 entries; catalog declares 37 brands).
  2. 9 craft bibles (`docs/research/manga_craft/` synthesis per spec §7.8) still proposed.
  3. PR #802 drift autopsy is empirical proof that en_US locale + schnell-fp8 + smuggled negatives produces non-manga output → consistency is functionally absent at the render layer regardless of canon documents.
- **phase_tag:** `CANON_DECLARED_LOCALLY_WIRED_RENDER_DRIFT_LIVE`.

---

## Summary table

| subsystem | owner | authority | config | output | tests | scheduled CI | %  | phase |
|---|---|---|---|---|---|---|---|---|
| manga_pipeline | Pearl_Dev | YES | YES | 35 panels for ep_001, 0 prod renders | 25 files / 244 grep | 3/16 cron | 35% | READY_TO_SHIP_BLOCKED_OPS |
| manga_catalog | Pearl_Architect | YES (v1.1) | YES | 1,350 series_plans + 18,900 book_plans | strong | 0 cron | 80% | RECONCILED_AWAITING_RENDERS |
| ite | Pearl_Dev | YES | YES | indirect via chapter run | indirect | 0 cron | 75% | WIRED_NEVER_FIRED |
| lora_pipeline | Pearl_Dev (proposed) | PARTIAL | YES (v1) | 0 LoRA artifacts ever | 0 | 0 cron | 15% | BLOCKED_ON_HARDWARE |
| character_consistency | Pearl_Architect | YES (post-#722) | YES | 12/37 brands LoRA-planned; renders drift | indirect | 0 cron | 45% | CANON_DECLARED_DRIFT_LIVE |

---

## Pipeline ratio analysis (the funnel)

The reality, in counts:

```
Catalog declared:        37 brands, 5 locales, 15 genres → 1,350 series_plans → 18,900 book_plans
                         ↓
Series setup launched:   2 (stillness_press__ahjan__en_US__anxiety,
                            warrior_calm_cultivation__master_wu__en_US__burnout)
                         ↓
Chapter scripts:         3 episodes (SP ep_001, ep_002; WC ep_001)
                         ↓
Panel prompts emitted:   2 episodes × 35 panels = 70 prompts (FLUX-schnell-fp8 ready)
                         ↓
Image_bank renders:      840 stillness_press renders (15 topics × 56) — but these are
                         BASE-MODEL FLUX, not bound to ep_001 panels and not LoRA-conditioned;
                         they are bank/seed assets, not the 35 ep_001 panels rendered.
                         ↓
Production panel renders
bound to a panel_id:     0  (ep_001 has 0 panel renders matching its 35 prompts)
                         ↓
Bubble-composed:         0 production episodes; the 1 fixture (`stillness_press_qa_run/manga.pdf`,
                         3-page composite) was assembled from non-bound imagery.
                         ↓
R2-uploaded:             0 episodes (R2 secrets registered in env_registry; GATE-OP-1 GitHub
                         Actions secrets pending; no upload events recorded).
                         ↓
Distributed to platform: 0 (KDP / LINE Manga / WEBTOON Canvas)
```

**Stage with the choke:** between **panel prompts emitted (70)** and **production panel renders bound to ep_001 panel_ids (0)**. The 840 image_bank assets exist but they are **decoupled from the 35 ep_001 panel prompts** — they are bank reference imagery, not chapter-bound renders.

**Secondary choke:** between **renders (0)** and **R2 upload (0)** — the operator-side gates GATE-OP-1 (R2 GitHub Actions secrets) and GATE-OP-2 (Pearl Star marker file install) are both pending per `proj_manga_first_ship_20260425.next_action`. Even if renders existed, upload is currently blocked.

**Tertiary choke:** PR #802 drift autopsy reveals that even when the `runcomfy_batch.py` pipeline does fire, the engine config (schnell-fp8 at steps=24/cfg=4.0) is wrong, so the renders that DO get produced (the 840 reference assets in image_bank) carry character drift, hallucinated kanji, and en_US locale-suppression of the manga prior — i.e. the bottleneck is not just throughput but quality.

**Cluster rollup:** spec/config/CI scaffolding is mature (catalog 80%, ITE 75%, pipeline 35%). Production-funnel reality is `prompt-emit-stage` for ep_001, and structurally blocked at training-step for any LoRA-conditioned consistency.
