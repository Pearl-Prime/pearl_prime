# Lane 2 — Pearl_GitHub/Engineering: Fix the R2-vs-canonical brand-assignment bug (real, live-failing)

EXECUTE. This is a genuine logic bug, not infra breakage — do not treat it as another
instance of the `phoenix_v4.social` repo-wide failure (that's Lane 1's job).

## STARTUP_RECEIPT

Re-verify live: `gh pr checks 56` should show `Core tests: fail`. Pull the failure log
(`gh run view --job <job-id> --log-failed`) and confirm it's still
`tests/brand_wizard/test_pages_assignment_lookup.py::
test_pages_assignment_lookup_prefers_canonical_brand_index` failing with "canonical
assignment did not win" — R2 live-assignment data (`source: "r2_live_assignment"`) is
returned instead of the canonical `brand_admin_brands.json` entry.

## Context — why this wasn't already fixed

Earlier today a separate session investigated this exact test failure, produced a
`pearl_prime_followups_20260722/assignment.js` fix + `README_APPLY.md`, and claimed it
was "verified" — but the branch was never actually pushed (`403 Resource not
accessible by integration` from the GitHub app). So the fix exists only as a
downloaded ZIP on the operator's machine, not in git, and the bug is still live in CI
right now (confirmed on #56 today). Check whether that ZIP or its extracted contents
are still present anywhere in this working tree or a known scratch location before
re-deriving the fix from scratch — if you find it, verify its logic against the
current `assignment.js` (don't trust the old session's "verified" claim without
re-running the test yourself) rather than discarding it.

## Task

1. Read `brand-wizard-app/functions/api/onboarding/assignment.js` in full.
2. Read `tests/brand_wizard/test_pages_assignment_lookup.py` to understand the exact
   contract: when both `brand_admin_brands.json` (canonical) and R2 live-assignment
   data are available for the same brand, the canonical index must win, and the
   handler must not even fetch R2 in that case (`if (calls.some(url =>
   url.startsWith("https://r2.example/"))) throw ...`).
3. Fix `assignment.js` so canonical lookup is checked first and short-circuits before
   any R2 fetch. Do not weaken the test to pass — the test's contract (documented
   in-file) is the correct behavior; fix the handler.
4. Run `PYTHONPATH=. pytest tests/brand_wizard/test_pages_assignment_lookup.py -x -v`
   and confirm it passes. Then run the broader
   `pytest tests/brand_wizard/ -m "not slow and not integration" -x` to check for
   regressions in sibling assignment/onboarding tests.
5. Check for a Node syntax/lint step on this file (`brand-wizard-app/` may have its own
   `package.json` with a lint script) and run it if present.

## Landing

Branch from `origin/main` per the Golden Branch Pattern. One-file fix (plus its test
file only if the test itself needs adjustment for a genuinely new edge case — do not
touch it to loosen the assertion). Standard PR flow: push-guard, preflight,
`pre_merge_check.sh`, `pr_governance_review.py --pr <n>`. Merge once green.

Then: rebase PR #56 onto the new `main` (post-merge) so its Core tests check picks up
the fix, confirm #56 goes green, and note in #56 whether the PR itself still needs
review for its own content (the Pearl Prime pipeline audit prompt) — that's not this
lane's job to evaluate, just confirm CI is unblocked.

## CLOSEOUT_RECEIPT (required, exact)

Fix PR number + merge SHA. Test results before/after (exact pass counts). Confirm #56
CI status post-rebase. Signal token: `LANE2_ASSIGNMENT_BUG_FIXED_<merge SHA>`.
