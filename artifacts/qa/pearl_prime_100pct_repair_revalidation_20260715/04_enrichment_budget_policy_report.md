# Enrichment Budget Policy Report

## Status

BLOCKED by GitHub 403 for merge/push, but local policy is implemented and tested.

## Policy

`minimal_accent` may legally assign zero optional accents only when the active brand/profile budget requests zero optional accent classes. This is now explicit as:

`enhancement_contract_v21.optional_accent_budget.zero_optional_accent_policy.authorized=true`

If the active budget requests optional accents and the assigned/rendered count is below target, the contract now hard-fails with `supported_budget_underfill` and `optional_accent_chapter_under_target`.

## Smoke Result

The smoke book used the explicit zero-budget exception:

`{'authorized': True, 'policy': 'authorized_exception', 'reason': 'No optional accent classes were requested by the active brand/profile budget.'}`

Optional accent zero is no longer ambiguous for this smoke target.

## Tests

PASS:

- `tests/planning/test_accent_planner.py::test_optional_accent_underfill_blocks_when_budget_requests_accents`
- `tests/planning/test_accent_planner.py::test_zero_optional_accent_budget_is_explicit_authorized_exception`

## Closeout

`pp-100pct-lane04=BLOCKED`

