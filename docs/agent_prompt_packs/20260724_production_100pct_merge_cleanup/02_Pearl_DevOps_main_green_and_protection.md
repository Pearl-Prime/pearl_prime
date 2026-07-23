# EXECUTE — Lane 02 (Pearl_DevOps): Make main GREEN + enable branch protection

This is an execution prompt, not a planning request. End state: **main's required
checks green on a fresh run, branch-protection ruleset applied (or BLOCKED-on-operator
with the exact command ready)**. Do not stop at plan, PR-open, or tests-running.

## Contract (in-band, non-negotiable)
- STARTUP_RECEIPT: `git branch --show-current`, HEAD SHA, `git status --short | head`,
  `gh auth status`, `git fetch origin && git log origin/main -1 --oneline`.
- Every claim below is a CLAIM — re-verify live (`gh run list --branch main`,
  `gh api repos/Pearl-Prime/pearl_prime/branches/main/protection`). It was true at
  2026-07-24 authoring; the repo moves hourly.
- Reuse-first: fixes for these failures may already exist in open PRs or recent
  commits — search `gh pr list --search` and `git log origin/main --oneline -30`
  BEFORE authoring anything. Restore from good SHAs (`git checkout <sha> -- <path>`),
  never fresh-fix what git already has.
- Branch from origin/main: `git fetch origin && git checkout -b agent/main-green-20260724 origin/main`
  (worktree with `GIT_LFS_SKIP_SMUDGE=1` if the main tree is contended; never
  `worktree add --no-checkout` — it poisons the tree with phantom deletions).
- Preflight before any push: `PYTHONPATH=. python3 scripts/git/push_guard.py`,
  `scripts/ci/preflight_push.sh`, `bash scripts/git/health_check.sh`.
- Merge rules: Rule-0 deletion check, `bash scripts/git/pre_merge_check.sh <n>`,
  `python3 scripts/ci/pr_governance_review.py`. Operator has pre-authorized squash-merge
  for green PRs in this pack's scope.
- Layer-honest closeout. NEVER weaken a gate to pass — fix the real cause
  (CLAUDE.md drift doctrine; the gates ARE the product here).

## Authority reads (before touching CI)
`docs/GITHUB_GOVERNANCE.md`, `docs/BRANCH_PROTECTION_REQUIREMENTS.md`,
`.github/workflows/` (core-tests + release-gates workflows),
`docs/handoffs/` entries from 2026-07-23/24 mentioning `enhancement_contract_v21`,
`opencc`, `parse-sweep`, DATA_DICTIONARY. Produce a short DISCOVERY REPORT:
what is failing on main RIGHT NOW (run names, job step, exact error), and provenance.

## Known failure inventory (verify each, then fix)
1. **Core tests:** `tests/test_enhancement_contract_v21_integrity.py` failing —
   repeatedly cited as THE chronic Core-tests red across 5+ handoffs. Root-cause it:
   is the test stale against a contract change, or is the contract genuinely broken?
   Fix the real side. `pytest -x` note: Core red often shows only the FIRST failure —
   after fixing, re-run the full suite to flush the cascade.
2. **Release gates:** `opencc` module missing on the CI runner (gate 44 import error,
   found 2026-07-24). Add the dependency to the workflow's install step (find where
   sibling deps are pinned — do not create a new requirements file).
3. **parse-sweep / stub baseline:** #234 merged real prose for the zh-CN
   compassion_fatigue stubs — verify `scripts/ci/check_canonical_atom_parse_sweep.py --json`
   is green on origin/main HEAD. If a stale baseline still trips, regenerate it
   honestly (additions AND removals justified — see PR #235's handoff for the method,
   then close #235 as superseded by your fix or adopt it if byte-correct).
4. **DATA_DICTIONARY staleness:** #133 merged a fix — verify no residual gate trips.
   DATA_DICTIONARY is GENERATED — regenerate, never hand-append.
5. Sweep: `gh run list --branch main --limit 20` for anything else red that is a
   required check. `pages build and deployment` failure is expected until operator
   item B (CF token) — note it, don't chase it.

Ship the fixes as ONE small PR (or two if test-fix and workflow-dep are cleaner apart).
Merge per rules above. Then trigger a fresh main run (empty-commit retrigger if needed —
`gh run rerun` does NOT refetch PR body/baselines, a known trap) and confirm all
required checks green. Signal the dispatcher: **`PIPER100-L02-MAIN-GREEN`**.

## Branch protection (second half — do not skip)
Live 404 confirmed: main has NO protection. CLAUDE.md claims ruleset enforcement —
that claim is currently false.
1. Build the ruleset JSON per `docs/BRANCH_PROTECTION_REQUIREMENTS.md` (required
   status checks: Core tests, Release gates, EI V2 gates, Change impact, Drift
   detectors; block force-push; require PRs).
2. Show the exact `gh api` command + JSON to the operator and wait for
   "apply branch protection" (OPERATOR_ACTIONS.md item D). Applying a repo security
   setting needs that explicit yes even under the blanket merge authorization.
3. On yes: apply, then verify with a read-back API call AND a test push-to-main
   rejection (from a throwaway clone, expect failure).

## Closeout
```
CLOSEOUT_RECEIPT: PIPER100-L02-DONE
main_green: <yes/no; failing checks if no>
fixes_merged: <PR#s + SHAs>
retrigger_run: <run URL + conclusions>
branch_protection: <applied+verified / ready-blocked-on-operator (command attached)>
gates_weakened: NONE (mandatory line — if you weakened anything, this lane FAILED)
cleanup_ledger: <branches/worktrees created & removed>
acceptance_layer: system working (CI green) — content quality unaffected by this lane
NEXT_ACTION: <what unblocks next>
```
Append a dated handoff note to this pack's INDEX.md. BLOCKED is an acceptable end
state only with the blocker + resume signal named.
