# GitHub Governance Cleanup Summary — 2026-03-23

## Before

- Active rulesets on `main`: `3`
- Conflicting required-check sets:
  - `Main protection` -> `Core tests`, `EI V2 gates`, `change-impact`
  - `main_branch_protection` -> `Core tests`, `EI V2 gates`, `change-impact`
  - `Protect main` -> `Core tests`, `Release gates`, `EI V2 gates`, `Change impact`
- Strict verifier result: `FAIL`

Evidence:

- `20260323_before_rulesets_list.json`
- `20260323_before_ruleset_13568047.json`
- `20260323_before_ruleset_13682674.json`
- `20260323_before_ruleset_13451138.json`
- `20260323_before_verify_api_strict.txt`

## Live cleanup

- Deleted stale ruleset `13568047` (`Main protection`)
- Deleted stale ruleset `13682674` (`main_branch_protection`)
- Kept canonical ruleset `13451138` (`Protect main`)

## After

- Active rulesets on `main`: `1`
- Canonical required checks:
  - `Core tests`
  - `Release gates`
  - `EI V2 gates`
  - `Change impact`
- Legacy required context `change-impact`: removed from live rulesets
- Non-blocking Cloudflare preview `Workers Builds: pearl-prime`: not required
- Strict verifier result: `PASS`

Evidence:

- `20260323_after_rulesets_list.json`
- `20260323_after_ruleset_13451138.json`
- `20260323_after_verify_api_strict.txt`
