# Q3 — Last-7-Days Reconciliation (2026-04-22 → 2026-04-29)

**Date:** 2026-04-29

## A. Volume

- **PRs merged in last 7 days:** 181
- **Commits to main since 2026-04-15 (14 days):** 1,038
- **Recent merge SHA range:** `9205b23079` (#722, 2026-04-27) → `6375c8fcbf` (#792, 2026-04-29)

## B. What landed (clustered)

### B.1 spec-739 wave — variant coverage gate (the dominant work)
PRs #739, #743, #744, #746, #750, #751, #752, #753–#770, #780, #784, #785, #788–#795. 
- Authored a spec, built a phased rollout (warn → strict), reconciled threshold ≥5 → ≥3, filled gen_z_student/gen_x_sandwich/working_parents/healthcare_rns/etc COMPRESSION/THREAD/TAKEAWAY/PERMISSION/INTEGRATION variants across personas, flipped the gate to strict, added `InsufficientVariantsError`. 
- **Outcome:** the variant-coverage validator now blocks builds with <3 variants per (persona × topic × section). Mature contract layer. Net new content: ~30 personas × ~10 sections × ~3 variants new authored.

### B.2 catalog scoring + B1/B2/B3/B4 wave
PRs #771 (book script catalogs across 4 locales + manga plan + genre reconciliation), #780 (B3+B4 score backfill across 3,608 rows × 4 locales), #788 (B2 title dedup 42→1,149 distinct titles), #790 (B2 cannibalization fix PASS all 4 gates), #792 (B2 cluster_titles.py acceptance gate), #793 (locale-native titles for ja_JP/zh_TW/zh_CN), #795/#796 (final launch readiness reports).
- **Outcome:** catalog quality gates closed for 4 locales × 1,149 distinct titles. Book/manga catalog substrate is strong.

### B.3 manga catalog reconciliation
PRs #722 (Path X — 37 manga canon as separate registry), #727 (catalog generator spec compliance — per-brand × per-genre allocations, regen 1,410 → 1,350), #738 (extend generators 5 → 8 markets: es_LA, hu_HU, zh_HK), #737 (sync to v2.1 schema).
- **Outcome:** Manga catalog moved from 5 to 8 markets and is spec-compliant.

### B.4 teacher_showcase repair
PRs #772 (retire teacher_select.html, redirect), #773 (consolidate 7 missing portraits — 13/13 covered), #781 (PR-B portraits + dup-id + dead R2 URL), #784 (PR-D maat boundaries ch1 audiobook 4:01), #785 (PR-C per-teacher CTA blocks).
- **Outcome:** teacher_showcase has 13 portraits, basic CTA structure. The format-grid overhaul (PR #798) is in flight.

### B.5 Pearl Prime governance + dashboard
PRs #730 (PIPELINE_DASHBOARD_INDEX), #745 (Workers Builds: pearl-prime required-check audit), #728 (next-phase execution plan), #729 (marketing conversion-rate hardening + marketing_assumptions.yaml).
- **Outcome:** Single-page dashboard index exists at `docs/PIPELINE_DASHBOARD_INDEX.md`. Workers deployment audited.

### B.6 manga episode pilot work
PRs #719 (teacher_manga_triptych closeout), #721 (build_thumbnail_review_grid.py), #722 (Path X), #723 (pilot_anchor_mecha × master_wu × burnout — the_chassis_is_listening ep_001), #725 (queue_panel_renders.py + Pearl Star runbook), #726 (rebrand mecha ep_001 to canonical warrior_calm_cultivation).
- **Outcome:** ep_001 chapter content + 35 panel prompts + Pearl Star queue runbook landed. **Renders did NOT happen — pipeline still at "prompts emitted, queue ready, no GPU run."**

### B.7 Pearl News + integrations
PRs #732 (teacher truth resolver from Pearl Prime sources — closes G4), #731 (RUNCOMFY_TOKEN env alias).
- **Outcome:** Pearl News G4 (teacher truth) closed. Integration env coverage extended.

## C. What didn't land but is on the docket

From open MERGEABLE active PRs (top of list):

- PR #803 — manga community assets audit (research, no engineering)
- PR #802 — drift autopsy + ComfyUI/FLUX prompting research §0-§2 (will land as 1-of-2)
- PR #801 — JP LINE freebie funnel plan (paper-only, no engineering yet)
- PR #798 — teacher_showcase format-grid overhaul (985 files, 30,860 additions; large)
- PR #797 — operator QA packet + stale work audit
- PR #787 — teacher_showcase locale spec PR-E
- PR #734 — TTS free-tier policy (ElevenLabs banned; CosyVoice2 + Edge + OpenAI freemium)
- PR #736 — LLM policy relax (freemium-OK + paid-overage-banned)
- PR #732 — Pearl News teacher truth resolver

The "open" cohort is heavily research/spec/audit-flavored. Very little engineering-to-ship is queued.

## D. Plan vs reality

**Per `docs/sessions/SESSION_HANDOFF_2026-04-25.md` and `proj_manga_first_ship_20260425`** (the explicit ship plan):

| target | status | evidence |
|---|---|---|
| ship ep_001 of "The Alarm Is Lying" en_US to KDP comics | NOT SHIPPED | 35 panel prompts emitted; 0 renders; 0 R2 uploads |
| close zh_TW atoms to 100% | partial — 92.1% as of last data | per `ws_cjk_atom_translation_qwen25_20260420` |
| close ja_JP atoms | partial — 89.3% with ~366 atoms remaining | same |
| close zh_CN atoms | NOT STARTED — ~2,200 atoms pending | same |
| land queue_panel_renders.py | LANDED — PR #725 | runbook §5 B reference still says "uncommitted" — drift |
| add R2_* env to scripts/ci/integration_env_registry.py (Pearl_Int Phase 0) | LANDED — confirmed line 52-53 of registry | per Q4 manga cluster audit |
| operator GATE-OP-1 (GitHub Actions secrets for R2_*) | UNKNOWN — operator-side | no signal in repo |
| operator GATE-OP-2 (Pearl Star marker file) | UNKNOWN — operator-side | no signal in repo |

**Per the broader Phoenix Omega roadmap** (catalog → storefront, Phase 1 of pathway):

| target | status |
|---|---|
| package authored prose into EPUB | NOT STARTED — no packager script |
| KDP submission pipeline | NOT STARTED — `kdp_comics_upload.py` is manga-only, manual-paste |
| Apple Books submission | NOT STARTED |
| LINE Manga submission | NOT STARTED |
| live brand-admin landing pages per brand | partial — generic admin shell only |

## E. The reconciliation finding

**The repo is producing more spec/code/content per week than any team this size could ship.** Throughput per-PR is healthy. Production-output throughput is zero. The bottleneck is between "content generated" and "content deliverable" — a packager, a publisher, a submission pipeline.

**Phase-1 priority** (from this 7-day reconciliation): the next 7 days should contain *fewer authoring PRs* and *one EPUB packager + one KDP submission test ship*. Otherwise the same pattern repeats.
