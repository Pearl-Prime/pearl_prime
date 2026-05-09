# CI recovery Phase 1 — governance bypass false positive (2026-05-09)

**Project:** PRJ-CI-BASELINE-RECOVERY-V1  
**Subsystem:** pearl_devops  
**Cap:** CI-BASELINE-RECOVERY-V1-01 (Verify governance)

## Root cause

`scripts/ci/verify_github_governance.py` used `FORBIDDEN_PATTERNS` with a bare `bypass_actors` regex. That matched **legitimate** GitHub API field references in `scripts/ci/check_branch_protection_ruleset.py` (e.g. `data.get("bypass_actors", [])`), so `check_no_bypass_scripts()` reported `FAIL: Bypass logic in check_branch_protection_ruleset.py`.

## Fix (Option A)

Replaced the broad `bypass_actors` substring match with **script-level** indicators only:

- Ruleset enforcement weakened: YAML-style `enforcement: "disabled"` / `enforcement: 'disabled'` (unchanged intent).
- Explicit **always** bypass in payload or Python: `"bypass_mode": "always"` / `bypass_mode = "always"`.

Added `text_has_forbidden_bypass_logic()` as the single gate for “bypass logic” text scans.

## Before / after (local verify)

**Before:** `python3 scripts/ci/verify_github_governance.py --mode local` reported bypass failure on `check_branch_protection_ruleset.py` when the old pattern matched `bypass_actors`.

**After:** Same command reaches `PASS: No bypass scripts or logic` while still flagging synthetic bypass snippets (see `tests/ci/test_verify_github_governance_bypass_scope.py`).

## Tests

`PYTHONPATH=. python3 -m pytest tests/ci/test_verify_github_governance_bypass_scope.py -v`

Covers: legitimate API-field usage (pass), on-disk ruleset checker (pass), JSON/Python `bypass_mode` always (fail), `enforcement: disabled` (fail).
