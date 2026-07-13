# Enhancement Contract V2.1 Integrity Apply Receipt

Applied locally in `/Users/ahjan/phoenix_omega_worktrees/enhancement-contract-proof-20260713`.

## Files Created

- `phoenix_v4/planning/enhancement_contract_v21_runtime.py`
- `tests/planning/test_enhancement_contract_v21_integrity.py`
- `tests/planning/test_enhancement_contract_v21_followup.py`
- `docs/ENHANCEMENT_CONTRACT_V21_INTEGRITY_FOLLOWUP_2026-07-13.md`
- `artifacts/research/enhancement_contract_v21_integrity_apply_receipt.md`

## Files Updated

- `phoenix_v4/planning/accent_planner.py`
- `phoenix_v4/qa/enhancement_contract.py`
- `phoenix_v4/rendering/accent_renderer.py`
- `phoenix_v4/rendering/chapter_composer.py`
- `config/accent/brand_accent_profiles.yaml`
- `config/authoring/story_mix_profiles.yaml`
- `config/authoring/bestseller_enrichment_signatures.yaml`

## Integrity Rules Added

- Optional-accent arithmetic and hard ceilings.
- External-story function, source, citation, and truth metadata.
- Cited-evidence citation and verification metadata.
- Author disclosure/commentary separation.
- Callback plant/return integrity.
- Parable container legality.
- Render-audit metadata carry-through for V2.1 surfaces.

## Proof Command

Run:

```bash
PYTHONPATH=. python3 -m pytest -q \
  tests/planning/test_enhancement_contract_v21_integrity.py \
  tests/planning/test_enhancement_contract_v21_followup.py \
  tests/planning/test_accent_planner.py \
  tests/test_enhancement_contract.py \
  tests/test_book_outline.py
```
