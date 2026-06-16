# Storefront-V1 Phase A Tracker — iter 2 SEED (for Pearl_PM dispatch)

**Status:** SEED — pre-staged Pearl_PM addendum. When Pearl_PM iter-2 dispatch fires per the operator's prior iter-2 tracker prompt, append the content below into `artifacts/coordination/storefront_v1_phase_a_tracker.md` as the new sections (per the prompt's §A-§I structure).

**Author:** Pearl_Architect, 2026-06-06, post-operator-green-light on `OPD-20260606-001` through `OPD-20260606-016` in `artifacts/coordination/operator_decisions_log.tsv`.

**Purpose:** the iter-2 PM dispatch prompt was written BEFORE the operator answered the 13 ONE-PATH Q-OP-* + decided STOREFRONT_LAUNCH_GATE + defined Q-PRP-STOREFRONT-CONTENT-GATE-01. This seed captures the post-answer state so Pearl_PM doesn't have to re-derive it.

---

## Operator decisions landed (cross-link to operator_decisions_log.tsv)

| OPD-id | Decision_axis | Answer | Status |
|---|---|---|---|
| OPD-20260606-001 | accept_all_lockdown_defaults_META | ACCEPT ALL 13 recommended defaults | logged |
| OPD-20260606-002 | Q-OP-L01-ARC-STRATEGY-01 | (a) auto-compress 20-arc → 12 via spine-subset | logged |
| OPD-20260606-003 | Q-OP-L09-PERSONA-FLOOR-01 | (b) staged: corp_mgrs + working_parents + first_responders first | logged |
| OPD-20260606-004 | Q-OP-L10-LOCALE-SCOPE-01 | (b) demote to top-3 (en-US + ja-JP + zh-TW) | logged |
| OPD-20260606-005 | Q-OP-VOICE-BRAID-01 | (b) slot-zoned | logged |
| OPD-20260606-006 | Q-OP-CHAPTER-REPETITION-THRESHOLD-01 | (a) T=0.85; sentence-transformers all-MiniLM-L6-v2 local | logged |
| OPD-20260606-007 | Q-OP-METAPHOR-CAP-N-01 | (a) N=5 per chapter | logged |
| OPD-20260606-008 | Q-OP-SIGNATURE-PHRASES-COUNT-01 | (a) 5 phrases/book whitelist | logged |
| OPD-20260606-009 | Q-OP-DRAFT-PROFILE-SMOKE-01 | (a) --smoke flag exempt | logged |
| OPD-20260606-010 | Q-OP-RUNTIME-FAIL-MESSAGE-LANGUAGE-01 | (c) both layers per §12 template | logged |
| OPD-20260606-011 | Q-OP-MIGRATION-CADENCE-01 | (a) single-PR-per-ws atomic | logged |
| OPD-20260606-012 | Q-OP-MOVE-4-VERDICT-RECOMPUTE-01 | (a) YES before Phase 1 dispatches | logged |
| OPD-20260606-013 | Q-OP-GOLD-REFERENCE-SHA-PIN-01 | (a) pin gold-ref SHA to MEMORY.md | logged |
| OPD-20260606-014 | Q-OP-CRAFT-DEPTH-OVERLAY-PROPOSAL-DISPOSITION-01 | (a) SUPERSEDED-BY frontmatter | logged |
| OPD-20260606-015 | STOREFRONT_LAUNCH_GATE | **Option B SCOPE-GATED launch** | logged |
| OPD-20260606-016 | Q-PRP-STOREFRONT-CONTENT-GATE-01_NEW | NEW mechanical SKU-join criterion ratified | logged |

---

## §J — Cross-program intersection (NEW section for iter 2)

The Pearl Prime ebook-assembly program (PR #1473 ONE-PATH lockdown) and the Storefront-V1 e-commerce program (PRs #1448-1455) intersect at exactly two contracts. Iter 2 ratifies both:

### J.1 — Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanical SKU-join criterion (NEW)

**Definition (operator-ratified per OPD-20260606-016):**
> A SKU joins the storefront catalog when its **persona×topic** has all 16 persona-keyed atom dirs (HOOK / STORY / SCENE / REFLECTION / EXERCISE / COMPRESSION / PIVOT / PERMISSION / PERMISSION_GRANT / TAKEAWAY / THREAD / INTEGRATION / TEACHER_DOCTRINE / TEACHER_DOCTRINE_INTRO / ANGLE_DEFINITION / ANGLE_CALLBACK) AND a smoke `book.txt` lands within **±10% of gold-reference word count envelope** for the runtime format.

**Mechanics:**
- Catalog growth = **mechanical consequence of Phase 3a landing per persona×topic.**
- **No operator approval per-SKU.** Pearl_PM dispatches catalog-expansion automation once Phase 3a's per-persona PR lands.
- The gold-reference word-count envelope per runtime format (from `artifacts/pearl_prime/gold_reference_ladder_2026-05-30/`):
  - micro_book_15: 6548 wc ±10% = [5893, 7203]
  - micro_book_20: 8338 wc ±10% = [7504, 9172]
  - short_book_30: 10538 wc ±10% = [9484, 11592]
  - standard_book: 19986 wc ±10% = [17987, 21985]
  - extended_book_2h: 27102 wc ±10% = [24392, 29812]
  - deep_book_4h: 39693 wc ±10% = [35724, 43662]
  - deep_book_6h: 56210 wc ±10% = [50589, 61831]

**Implementation hook (post Phase 3a per-persona PR merge; Pearl_PM automation):**
1. CI smoke runs all 7 runtime formats for the newly-backfilled persona × {anxiety, burnout, overthinking, ...whichever topics it has full atom coverage for}.
2. For each smoke that lands within ±10% of gold-ref envelope AND exits 0 (under production profile lockdown), append a SKU row to `config/storefront/sku_url_map.yaml` (or successor projector output).
3. Cloudflare deploy workflow picks up the new SKU; storefront catalog grows.

### J.2 — Storefront-V1 launch scope (OPD-20260606-015 ratified)

**Launch-day SKU subset (Option B SCOPE-GATED):**
- `gen_z_professionals × anxiety × ahjan × {micro_15, micro_20, short_30, standard_book, extended_2h, deep_4h, deep_6h}` × {en-US, ja-JP, zh-TW}
- = 7 formats × 3 locales × 1 persona × 1 topic = **21 launch-day SKUs**
- (Per Q-PRP-STOREFRONT-CONTENT-GATE-01: ja-JP and zh-TW must have BOTH gen_z_professionals × anxiety persona-keyed atoms in their locale AND smoke pass the wc envelope; if either locale fails, scope further reduces to en-US-only = 7 SKUs.)

**Catalog growth path (post-launch):**
- Phase 3a backfill order per OPD-20260606-003 (b): corp_mgrs → working_parents → first_responders → healthcare_rns → gen_x_sandwich → tech_finance_burnout → millennial_women_professionals → gen_alpha_students → gen_z_student → nyc_executives → educators → midlife_women (the last blocked on arc-authoring per `ws_midlife_women_arc_authoring_20260427`).
- Each persona × topic combo that lands Phase 3a + passes the J.1 criterion = +7 formats × 3 locales = +21 SKUs (or less if some topics aren't covered).
- Theoretical full-catalog (per OPD-20260606-004 (b) top-3 demote): 12 personas × ~15 topics × 7 formats × 3 locales ≈ 3,780 SKUs (vs. the 17,688 in #1453's hand-curated `sku_url_map.yaml` which assumed top-5 locales × all personas including ungated).

### J.3 — Cross-program coordination contract

| Pearl Prime side | Storefront side | Trigger |
|---|---|---|
| Phase 3a per-persona PR lands + smoke passes J.1 | Pearl_PM automation appends to `sku_url_map.yaml` + redeploy | Mechanical (no operator) |
| Phase 2 runtime gates land | Storefront catalog adoption is safe (no silent lesser-config) | Mechanical (no operator) |
| Phase 4 craft gates land | Storefront catalog adoption hits §13 rubric not just structural-assembly | Mechanical (no operator) |
| ONE-PATH ws_pearl_pm_one_path_lockdown_sequencing_tracker_20260606 status update | Storefront-V1 Phase A tracker iter N+1 fires | Pearl_PM cron weekly |

---

## §K — Updated 6-PR merge cascade (REPLACES iter-2 dispatch prompt's §C)

Two cap-entry PRs land first, then the 5 child storefront PRs. Pearl Prime's PR #1473 needs to merge alongside (or just before) #1455 since #1473 unblocks the per-persona Phase 3a backfill that Q-PRP-STOREFRONT-CONTENT-GATE-01 depends on:

| Step | PR | Owner | Gating |
|---|---|---|---|
| 0 | **#1473 ONE-PATH lockdown** | Pearl_Architect | Operator merges (decisions logged; no other gating) |
| 1 | **#1455 AMENDMENT-2026-06-04.2** | Pearl_Architect | Operator merges (Q-PRP-AMEND-* already pre-answered via OPD-20260606-001..-016) |
| 2 | #1448 PM tracker iter 1 | Pearl_PM | Merge after #1473 + #1455 ratify; iter-2 dispatch fires THIS SEED into iter-2 doc |
| 3 | #1454 Pearl_Writer audit Stage 1 | Pearl_Writer | Merge after #1448 (Q-PRP-WRITER-AUDIT-STAGE-02 = (a) localized-first per OPD-20260606-003's persona-staging logic) |
| 4 | #1450 Pearl_Int CF + Snipcart | Pearl_Int | Merge after #1454 + operator validates 8 operator-action-required slots |
| 5 | #1452 Pearl_Dev mockups | Pearl_Dev | Merge after #1450 (or parallel) |
| 6 | #1453 Pearl_Marketing CTA cutover | Pearl_Marketing | Merge LAST; `sku_url_map.yaml` 17,688 rows is retained as the catalog upper-bound; Q-PRP-STOREFRONT-CONTENT-GATE-01 mechanics gate which subset is actually live |

**Post-merge cascade:**
- Pearl_PM dispatches the 6 child ws's per PR #1473 spec §7 phase order (Phase 1 mechanical → Phase 2 runtime → Phase 3a + 3b parallel → Phase 4 craft).
- Pearl_Marketing spawns `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` per OPD-20260606-016's launch gate (15 ja-JP freebie pages mirror en-US `brand-wizard-app/public/free/`).
- Pearl_Writer spawns `ws_pearl_writer_next_step_atom_audit_stage_2a_localized_20260606` per Q-PRP-WRITER-AUDIT-STAGE-02 = (a) (9 localized atom files identified in Pearl_Architect's S1 evidence in PR #1455).

---

## §L — Phase A launch readiness gate (UPDATE)

Original iter-1 gate matrix unchanged + add:

| Gate | Source | Status |
|---|---|---|
| Pearl Prime ONE-PATH lockdown cap-entry merged (#1473) | this seed | gating |
| Storefront AMENDMENT-2026-06-04.2 cap-entry merged (#1455) | this seed | gating |
| 5 child storefront PRs cascade merged (#1448 → #1454 → #1450 → #1452 → #1453) | iter-2 PM prompt §C | gating |
| `ws_pearl_marketing_ja_jp_freebie_pages_authoring_20260606` lands | AMENDMENT-2026-06-04.2 §B | gating |
| Pearl Prime gen_z_professionals × anxiety launch-SKU subset passes Q-PRP-STOREFRONT-CONTENT-GATE-01 criterion (≥7 SKUs en-US confirmed; ja-JP + zh-TW SKUs added if pass) | §J.2 | **gating launch declaration** |
| Pearl Prime Phase 3a per-persona backfill ws's begin landing (corp_mgrs first) | ONE-PATH §7 Phase 3a | post-launch; gates catalog expansion |

**Phase A launch declaration criterion** (operator-tier):
- All 5 storefront-program child PRs merged
- ja-JP freebie pages ws merged
- At least the 7-SKU en-US gen_z_professionals × anxiety subset passes J.1 + appears in `sku_url_map.yaml` live
- Operator declares Phase A live; catalog expands automatically per §J.1 from there

---

*End of iter-2 SEED. Pearl_PM iter-2 dispatch incorporates §J + §K + §L + the OPD-20260606-* decision table into the live tracker doc on next fire.*
