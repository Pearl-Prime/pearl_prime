# Lane 1 — Pearl_GitHub: Resolve #53/#55 collision, unbreak main CI, rebase downstream PRs

EXECUTE. Do not stop at "plan," "PR open," "tests running," or "cleanup later." Land or
report BLOCKED with a full triage — no other terminal state.

## STARTUP_RECEIPT (re-verify every claim below live before acting — these are CLAIMS
from a 2026-07-22 audit, not ground truth)

1. `git fetch origin`, `gh pr list --state open --json number,title,headRefName,mergeable,statusCheckRollup`
2. Confirm: PR #53 (`agent/land-deterministic-social-metricool-payload-20260722`) and
   PR #55 (`agent/main-unbreak-missing-imports-20260722`) both add
   `phoenix_v4/social/__init__.py` and `phoenix_v4/social/media_selector.py`.
3. Confirm: `gh pr diff 55 --name-only` touches only 4 files
   (`config/publishing/book_engine_policy_v1.yaml`,
   `phoenix_v4/planning/book_engine_policy.py`, `phoenix_v4/social/__init__.py`,
   `phoenix_v4/social/media_selector.py`). `gh pr diff 53 --name-only` touches ~26
   files spanning social-schema spec/config, storyblocks licensing, manga doctrine
   config, flagship-book snapshots, and `docs/DATA_DICTIONARY.tsv`, in addition to the
   same two social-package files.
4. Confirm: #49, #50, #42 are all red on Core tests / Drift detectors / Release gates
   with the same underlying `ModuleNotFoundError` / data-dictionary-staleness pattern
   — `gh run view --log-failed` on any of their failing Core-tests jobs.

If any of these claims don't hold anymore (e.g. someone already merged #55, or #53 has
been rescoped), STOP re-deriving strategy from stale memory — work from what you
actually observe and adapt the plan below accordingly.

## Read first

Read `docs/GITHUB_OPERATIONS_FRAMEWORK.md`, `docs/GITHUB_GOVERNANCE.md`,
`docs/BRANCH_PROTECTION_REQUIREMENTS.md`, and this repo's CLAUDE.md Non-Negotiable Git
Rules before touching any of these PRs (mass-deletion check applies to #53's 26-file
diff too — confirm 0 deletions, per the poison-protocol gate, before merging anything
built from it).

## Task

**Step A — land the narrow fix.** #55 is the correctly-scoped fix (2 real modules, no
scope creep). Verify its 4-file diff actually resolves both
`ModuleNotFoundError: No module named 'phoenix_v4.social'` and the
`book_engine_policy` import error when run against a fresh `origin/main` checkout
(`PYTHONPATH=. pytest tests/test_metricool_client.py tests/ -k book_engine_policy -x`
plus the broader `pytest tests/ -m "not slow and not integration" -x` sweep). If it's
clean, land it via this repo's standard branch/PR/governance flow (push-guard,
preflight, `pre_merge_check.sh 55`, `pr_governance_review.py --pr 55`) and merge.

**Step B — untangle #53.** Once #55 is merged, #53's two social-package files become
pure duplicates. Do NOT force-merge #53 as-is (26 files including generated
`DATA_DICTIONARY.tsv` and flagship snapshots is exactly the kind of PR-size/scope
violation `docs/GITHUB_GOVERNANCE.md` flags). Instead:
   - Check out #53's branch, rebase onto post-#55 `main` (the duplicate
     `phoenix_v4/social/` files should now merge-conflict-resolve to "already present,
     drop from this diff").
   - Split what remains into the legitimate social-schema payload (spec doc, brand/
     author-voice YAML, anti-spam gate `check_social_post_variation.py`, and its
     tests) as its own tightly-scoped PR. Leave the storyblocks-licensing and manga
     `modern_reader_context.py` / `modern_reader_story_doctrine.yaml` changes out
     unless they're a genuine dependency of the social work — if they're unrelated,
     they belong in their own PR too (do not silently drop real work; open a follow-up
     PR for them and say so in this lane's CLOSEOUT_RECEIPT).
   - Do NOT hand-edit `docs/DATA_DICTIONARY.tsv` in this new PR — regenerate it via
     `python3 scripts/governance/build_data_dictionary.py` against the post-#55 tree
     and diff against what #53 originally staged; if they match, that confirms #53's
     copy was correct and gate 27 was a false positive on stale `main`, not real drift.
   - Close the original #53 with a comment pointing to the two replacement PRs (or
     amend #53 in place if GitHub allows a clean force-push without losing review
     history — operator's call if ambiguous, otherwise prefer close+reopen for a clean
     diff).

**Step C — rebase the queue.** Once main's CI is green (confirm Core tests, Drift
detectors, Release gates all pass on a fresh push to `main`), rebase #49, #50, #42 onto
current `main` and re-push each. Watch CI to terminal state on each (poll, do not
monitor-park). Merge each once green, following `bash scripts/git/pre_merge_check.sh
<PR_NUMBER>` and `python3 scripts/ci/pr_governance_review.py --pr <PR_NUMBER>` for
every one — do not batch-skip governance checks because you already ran them once
today on a different PR.

## Landing

MERGED or BLOCKED for each of: #55, #53 (or its replacement PR(s)), #49, #50, #42. Name
the exact SHA for every merge. If any PR is genuinely blocked on something outside this
lane's scope (e.g. a real conflicting change from a sibling session mid-flight), say so
explicitly rather than forcing it.

## CLOSEOUT_RECEIPT (required, exact)

For each of the 5 PRs (or their replacements): PR number, final SHA or BLOCKED reason,
CI status of all 3 previously-red checks. Name any new PR opened for the split-out #53
payload. Confirm `docs/PROGRAM_STATE.md` updated if this counts as a milestone (main
CI unblocked repo-wide). Signal token: `LANE1_MAIN_CI_UNBROKEN_<final main SHA>`.
