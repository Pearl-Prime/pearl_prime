# Sellability Rollup

**Date:** 2026-06-30

## Sellable as-is (ship / list now)

| Book | Persona × Topic | Why |
|------|-----------------|-----|
| `way_stream_sanctuary__corporate_managers__burnout__overwhelm.epub` | corporate_managers × burnout | Highest composite (0.76); register-PASS; marketing promise delivered; leakage clean |
| Teacher micro-EPUBs (6) | various | `pamela_fellows_anxiety`, `omote_sleep_anxiety`, `ra_imposter_syndrome`, `miki_imposter_syndrome`, `master_sha_grief`, `adi_da_self_worth` — complete ~5k-word samples, clean, no placeholder stubs |

## Sellable with advisory (quality OK for beta; cohesion lane open)

**All 8 wave_proof draft books** + **6 clean pilot_10 books** (anxiety/boundaries cells without HOOK stubs):

- Marketing promise: **delivers YES** on all catalog-matched cells checked
- Bestseller: CONCERN on most (driven by `content_uniqueness` 0.10–0.16, not prose quality)
- Engaging: PASS on all full-spine books
- **Advisory:** Reader will notice template cadence between atoms before they notice weak hooks. Acceptable for proof/listening samples; not ideal for paid launch at scale until cohesion lane lands.

**Recommended near-term sell test cell:** `burnout_overwhelm__corporate_managers` (wave_proof) — clean, delivers *Permission to Pause* listing, no placeholders.

## Blocked on cohesion fix (Q1/Q2 — Atom Cohesion lane)

**Not individual book failures — systemic lane:**

| Scope | Evidence | Route |
|-------|----------|-------|
| All 17 full-spine Pearl Prime books | Tier-1 CONCERN despite EI cohesion PASS 0.80+; REPETITION_CENSUS 1281/1281 MEDIUM; engine-keyed thesis in 128 cells | Atom Cohesion Chunked Plan A–F / OPD-20260629-002 |
| `master_feung_burnout`, `master_wu_courage` | Incomplete stubs (260–303 words) | Re-assemble or exclude |

**Do not fix in this verification run.** Detect + route only.

## Blocked on leakage (marketing-facing hard stop)

| Book | Issue |
|------|-------|
| `pilot_10/02_gen_z_professionals__burnout` | `[Persona-specific hook for gen_z_professionals × burnout]` × ~24 |
| `pilot_10/04_corporate_managers__burnout` | HOOK stubs + cross-persona `[gen_z_professionals × burnout]` contamination |
| `pilot_10/05_corporate_managers__financial_anxiety` | Same HOOK stub pattern |

**Fix lane:** Author real HOOK variants in `atoms/corporate_managers/burnout/HOOK/CANONICAL.txt` (per PILOT_10_REVIEW_PACKAGE §10). wave_proof rebuilds of same cells are already clean.

## Marketing-promise gaps

| Book | Gap |
|------|-----|
| nyc_executives × anxiety | No `en_US_catalog.csv` row — cannot verify listing promise (prose quality PASS) |
| Teacher-mode EPUBs | No persona-specific listing — marketing-fit assessed on lexicon only |
| gen_x_sandwich × boundaries | Delivers YES but subtitle keyword match thin (2/6) — PARTIAL on keywords, still topic-faithful |

**No bait-and-switch detected** on any catalog-matched full-spine book. Subtitles promise recovery/practice language; books deliver somatic self-help prose in matching register.

## Leakage summary

- **28/31 clean** after `clean_for_delivery`
- **3 FAIL:** pilot_10 HOOK square-bracket stubs (not caught by brace gate — recommend extending `delivery_contract_gate` to flag `[Persona-specific` pattern)
- wave_proof set: **100% clean**

## Decisions

| ID | Decision | Alt considered |
|----|----------|----------------|
| Q-VERIFY-SET-01 | Verified all on-disk assembled EPUBs + #3605 pilot + wave_proof draft; no gap-fill assembly | Assemble educators×burnout (blocked arc) — skipped |
| Q-VERIFY-BAR-01 | EI ≥ 0.5 PASS; Tier-1 override cohesive-flow → CONCERN on all 12-ch spine | Strict deterministic only — rejected (under-predicts per meta-finding) |

## Next action

1. **Q1/Q2 cohesion lane** — engine-keyed thesis diversification (highest ROI per REPETITION_CENSUS)
2. **HOOK atom authoring** — unblock 3 pilot_10 leakage FAILs (or use wave_proof clean renders for same cells)
3. **Extend delivery_contract_gate** — square-bracket persona hook stubs
4. **Optional:** Stage evidence PR off `origin/main` (operator call — artifacts local-only for now)
