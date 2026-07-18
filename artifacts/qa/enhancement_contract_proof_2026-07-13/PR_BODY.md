## Summary

- add an authoritative `enhancement_contract.json` / `enhancement_contract.md` proof surface that reconciles planned accents and required slot families against the delivered `book.txt`
- auto-activate `enrichment_contract_v1` for the real flagship chord `anxiety × gen_z_professionals × extended_book_2h` instead of relying on a demo render-dir suffix
- fix the multiple-accent insertion double-offset bug and carry renderer stream indices / body hashes into the durable accent audit
- upgrade the accent truth gate and operator outline surfaces to consume the stronger proof data when present

## Proof

- proof root: `artifacts/qa/enhancement_contract_proof_2026-07-13/`
- flagship render: `book_pass_report.json` PASS, `book_quality_report.json` Pass
- contract proof: `enhancement_contract.json` PASS with `validation.errors=[]`
- accent truth gate: `ACCENT_FLAGSHIP_TRUTH_GATE_2026-07-13.json` PASS
- assignment gate: `ACCENT_PLAN_ASSIGNMENT_2026-07-13.json` PASS

## Tests

```bash
PYTHONPATH=. python3 -m pytest -q \
  tests/test_enhancement_contract.py \
  tests/planning/test_accent_planner.py \
  tests/ci/test_accent_flagship_truth_gate.py \
  tests/test_book_outline.py
```

## Honest notes

- the contract proof labels accent selected-body provenance as `partial` because the repo still has no dedicated selected-accent artifact; the proof uses `EnrichedChapter.accent_bodies` as the repo-native selected-body surface
- the production flagship render still emits pre-existing exercise-journey outcome mismatch warnings in stderr; they did not fail `book_pass`, `book_quality`, the contract proof, or the accent truth gate
