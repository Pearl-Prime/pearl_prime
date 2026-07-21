# IMPLEMENTATION CLOSEOUT — Pearl Prime Perfect Books Spec (Wave-1)

**Date:** 2026-07-18  
**Lane:** pearl-prime-perfect-spec-impl  
**Spec:** `PEARL_PRIME_PERFECT_BOOKS_SPEC.md`  
**Acceptance language:** Wave-1 lands enforceable mechanisms at the **structurally clear** floor for claim/manifest/machinery detectors. This does **not** certify any book as `system working` or `bestseller register`.

## SIGNAL

`SIGNAL=pearl-prime-perfect-spec-impl=PARTIAL`

### Why PARTIAL (not PASS / not BLOCKED)

- **Wave-1 of the spec sequencing is complete** (G-CLAIM + G-LAYER + G-WRAP + G-DEF4 + D2/D3 scaffolding).  
- **Full spec “Done when” is not met:** no Layer-3 ONTGP PASS on ≥3 flagship cells; no operator blind-10; bank fill (C1–C4) and G-F1H / G-ORIENT / G-ACCENT deferred.  
- **Not BLOCKED:** mechanisms are wired and tested locally; gates were not weakened.

## Wave completed

**Wave-1** = spec §5 steps 1–2:

1. Ship G-CLAIM + G-LAYER  
2. Ship G-WRAP + G-DEF4  

Plus durable extras that fit the same smallest-safe-diff pass: D3 ship-profile reject, D2 deprescribe default-off regression test, flagship line-edit lane scaffold, CLAUDE.md claim-language promotion.

## Mechanisms landed

| ID | What | Path(s) | How to run |
|---|---|---|---|
| **G-CLAIM** | Closeout/PR claim words require acceptance-layer term; “improve catalog register” needs Layer-3 packet | `scripts/ci/check_acceptance_claim_language.py` | `PYTHONPATH=scripts/ci:. python3 scripts/ci/check_acceptance_claim_language.py --base origin/main --head HEAD` |
| **G-LAYER** | Catalog manifests require `acceptance_layer`; `system_working` needs Layer-3 artifact | `scripts/ci/check_catalog_manifest_acceptance_layer.py`; writer: `scripts/release/batch_catalog_epubs.py` | `PYTHONPATH=. python3 scripts/ci/check_catalog_manifest_acceptance_layer.py` |
| **G-WRAP** | Cleared wrapper stem in ≥4 chapters → register F16 `HARD_FAIL` on production/flagship | `phoenix_v4/quality/register_gate.py` (`_detect_f16_exercise_wrapper_spam`); ship helper `scripts/ci/check_catalog_ship_wrap_defect4.py` | Runs inside `evaluate_register`; or `PYTHONPATH=. python3 scripts/ci/check_catalog_ship_wrap_defect4.py --book path/to/book.txt --skip-defect4` |
| **G-DEF4** | `enrichment_audit.defect4_drops` recorded; production/flagship `SystemExit` if count > 0 | `phoenix_v4/planning/enrichment_select.py`; `scripts/run_pipeline.py` | Produced on every enrichment; ship check: `PYTHONPATH=. python3 scripts/ci/check_catalog_ship_wrap_defect4.py --enrichment-audit path/to/enrichment_audit.json --skip-wrap` |
| **D3** | `draft`/`debug` cannot enter catalog ship without explicit bypass | `batch_catalog_epubs.py` (`--allow-non-ship-profile` / `--dry-run` only) | Invoke batch with `--quality-profile draft` (expect SystemExit) |
| **D2** | Deprescribe one-line inject stays default-off | `tests/test_spine_deprescribe_default_off.py` | `pytest tests/test_spine_deprescribe_default_off.py -q` |
| **L1 scaffold** | Line-edit lane process stub | `artifacts/qa/flagship_line_edit/README.md` | Create dated cell dirs + `ONTGP_VERDICT.md` when Pearl_Editor runs |
| **Doctrine** | CLAUDE.md claim / composer-lever rules promoted | `CLAUDE.md` (items 2 + 4 under bestseller anti-drift) | Read-first |

### CI / readiness wiring

- `.github/workflows/drift-detectors.yml` — three new BLOCK steps (G-CLAIM, G-LAYER, G-WRAP+G-DEF4 integrity).  
- `scripts/run_production_readiness_gates.py` — gates **35 / 36 / 37**.

### Tests

```bash
PYTHONPATH=. python3 -m pytest \
  tests/test_acceptance_claim_language.py \
  tests/test_catalog_manifest_acceptance_layer.py \
  tests/test_register_gate_f16_wrap.py \
  tests/test_spine_deprescribe_default_off.py -q
```

Result this session: **14 passed**.

## Deferred (with reason)

| Item | Reason |
|---|---|
| G-F1H (templated cluster ≥6 chapters HARD) | Spec step after Wave-1; F1 already FAIL at size ≥3 — escalate carefully next wave |
| G-ORIENT (Ch1 body/scene lexicon) | Needs approved lexicon SSOT + authored-candidate eligibility wiring |
| G-ACCENT weekly preflight matrix | Needs catalog eligibility matrix job + accent fill report (ops cadence) |
| C1–C4 bank completeness | Content authoring across ship matrix; not a small CI diff |
| L2–L4 line-edit execution on 3 cells | Requires Pearl_Editor human/agent ONTGP — scaffold only this wave |
| B1–B3 operator blind-10 | Operator-attended; calendar / Pearl_PM — not agent-fakeable as Layer 4 |
| Routing fix C4 (Gen-Z registry depth default) | G-DEF4 now surfaces debt; actual bank/persona labeling fills are Editor lane |

## Operational note (G-DEF4)

Production/flagship renders that previously *silently* dropped foreign-persona registry sections will now **hard-stop**. That is intentional: fix bank routing / persona labels; do not silence the DEFECT4 detector. Expect some previously “green” cells to fail until C4 bank work lands.

## Explicit non-claims

- No book is `bestseller register`.  
- No book is `system working` (no `ONTGP_VERDICT.md` PASS artifacts).  
- Gate wiring ≠ catalog quality certification.

## Handoff

`artifacts/coordination/handoffs/pearl_prime_perfect_books_wave1_2026-07-18.md`
