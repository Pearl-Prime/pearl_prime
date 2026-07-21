# Handoff — Pearl Prime Perfect Books Wave-1 enforcement

**Date:** 2026-07-18  
**Lane:** pearl-prime-perfect-spec-impl  
**Spec:** `artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md`  
**Closeout:** `artifacts/qa/pearl_prime_100book_analysis_20260718/IMPLEMENTATION_CLOSEOUT.md`

## Wave completed

**Wave-1** = sequencing steps 1–2 from the spec:

1. G-CLAIM + G-LAYER  
2. G-WRAP + G-DEF4  

Plus durable scaffolding: D2 regression test, D3 ship-profile reject, line-edit lane README, CLAUDE.md claim-language promotion.

## Mechanisms landed

| ID | Mechanism | Path |
|---|---|---|
| G-CLAIM | Q-ENFORCE-02 closeout/PR claim language | `scripts/ci/check_acceptance_claim_language.py` |
| G-LAYER | Manifest `acceptance_layer` + Layer-3 artifact | `scripts/ci/check_catalog_manifest_acceptance_layer.py` + `scripts/release/batch_catalog_epubs.py` |
| G-WRAP | F16 wrapper stem ≥4 chapters → HARD_FAIL | `phoenix_v4/quality/register_gate.py` + ship checker |
| G-DEF4 | Audit `defect4_drops` + production SystemExit | `enrichment_select.py` + `run_pipeline.py` |
| D3 | Reject draft/debug catalog ship | `batch_catalog_epubs.py` |
| D2 | Deprescribe inject default-off test | `tests/test_spine_deprescribe_default_off.py` |
| L1 scaffold | Flagship line-edit lane README | `artifacts/qa/flagship_line_edit/README.md` |

Wired into `.github/workflows/drift-detectors.yml` and readiness gates **35–37**.

## Deferred (later waves)

- G-F1H (cluster ≥6 chapters HARD), G-ORIENT, G-ACCENT weekly matrix  
- C1–C4 bank fill for full ship matrix  
- L1–L4 execution on 3 flagship cells (human ONTGP)  
- B1–B3 operator blind-10  

## STALE-SOURCE CORRECTION — 2026-07-18/19 (Lane 06, Wave-2 final audit)

The "Deferred" list above is now stale for 3 of its 4 items — **do not treat
it as still-open without reading this correction**. Wave-2 (offline,
`pearlstar_offline`, GitHub still 403 — none of this is on `origin/main`)
advanced each item as follows:

- **G-F1H / G-ORIENT / G-ACCENT** — **SHIPPED**, mutation-verified, additive.
  `offline/perfect-books-wave2-cigates-20260718@b2d6761d9d641e53af8f27b91974adaebddef24b`.
- **C1–C4 bank fill** — **C1–C3 filled** for 3 designated cells (burnout accent
  banks); **C4 NOT fixed** — root-caused as a catalog-wide single-persona-per-
  topic registry defect (14/16 topics), independently reproduced on 3 cells,
  correctly left unfixed (compliant fix is composer/registry-adjacent, a
  banned lever for a bank-fill lane).
  `offline/perfect-books-wave2-bankfill-20260718@d48fbdacacabc21641709f9411af90dd46c3ed27`.
- **L1–L4 execution on 3 flagship cells** — **executed honestly, 0/3 PASS.**
  Real ONTGP reads on Ch1/Ch5/Ch12 for all 3 cells; all 3 `ONTGP_VERDICT.md`
  are evidenced **FAIL** (no fabricated PASS); 24 atoms fixed and bank-
  promoted (L4) as a forward-looking correction.
  `offline/perfect-books-wave2-lineedit-20260718@4356fb0dea205510e7c82a5afad0a629c9117d25`.
- **B1–B3 operator blind-10** — **packet prepared** (10/10 real, non-padded
  Layer-1-ceiling production EPUBs); **operator read still not performed** —
  this remains genuinely open, not stale.
  `offline/perfect-books-wave2-blind10-prep-20260718@2a7332763db2105a7ff24e7c521699b2fa0dbdc0`.

Full lane-by-lane evidence, diff-stat verification, and residual blockers:
`artifacts/qa/perfect_books_wave2_20260718/FINAL_AUDIT.md`.

## SIGNAL

See IMPLEMENTATION_CLOSEOUT — `SIGNAL=pearl-prime-perfect-spec-impl=PARTIAL` (Wave-1 complete; full spec Done-when checklist not yet).
Wave-2 (Lane 06 final audit): `SIGNAL=perfect-books-wave2-final=PARTIAL` — see correction above.
