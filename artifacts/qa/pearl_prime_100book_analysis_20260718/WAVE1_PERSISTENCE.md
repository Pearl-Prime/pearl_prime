# Wave-1 Persistence — Pearl Prime Perfect Books

**Date:** 2026-07-18  
**Branch:** `agent/pearl-prime-perfect-books-wave1`  
**Primary Wave-1 commit:** `16c431bb38f34088ac4218f0af03cb2242fd2630`  
**Branch tip (includes this note):** use `git rev-parse agent/pearl-prime-perfect-books-wave1`  
**Substrate:** local `origin/main` @ `9e9b9e606791590337cd7d0f2fb425def2e6f760` (fetch failed: GitHub 403 account suspended; not rebased onto newer remote)  
**Source working tree (not committed there):** `codex/realist-social-samples-20260718`

## Push status

**BLOCKED** — `git fetch` / `git push` return HTTP 403 (`Your account is suspended`). No force-push attempted. Branch exists **local only**.

## Files included (Wave-1 only)

- `.github/workflows/drift-detectors.yml`
- `CLAUDE.md`
- `scripts/ci/check_acceptance_claim_language.py`
- `scripts/ci/check_catalog_manifest_acceptance_layer.py`
- `scripts/ci/check_catalog_ship_wrap_defect4.py`
- `scripts/release/batch_catalog_epubs.py`
- `phoenix_v4/quality/register_gate.py`
- `phoenix_v4/planning/enrichment_select.py`
- `scripts/run_pipeline.py`
- `scripts/run_production_readiness_gates.py`
- `tests/test_acceptance_claim_language.py`
- `tests/test_catalog_manifest_acceptance_layer.py`
- `tests/test_register_gate_f16_wrap.py`
- `tests/test_spine_deprescribe_default_off.py`
- `artifacts/qa/flagship_line_edit/README.md`
- `artifacts/qa/pearl_prime_100book_analysis_20260718/IMPLEMENTATION_CLOSEOUT.md`
- `artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md`
- `artifacts/coordination/handoffs/pearl_prime_perfect_books_wave1_2026-07-18.md`
- `artifacts/qa/pearl_prime_100book_analysis_20260718/WAVE1_PERSISTENCE.md` (this note)

## Explicitly excluded

Unrelated dirty files on `codex/realist-social-samples-20260718` (accent banks, manga samples, practice library, etc.) were **not** staged.

## Recovery when GitHub works

```bash
git fetch origin
git push -u origin agent/pearl-prime-perfect-books-wave1
```
