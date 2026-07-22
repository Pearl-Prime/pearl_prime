# Lane 3 — Pearl_GitHub: Push and open a PR for the already-committed outfit/object continuity work

EXECUTE. This is a landing task, not an authoring task — the code, tests, and commit
already exist. Do not re-implement or re-review the design; just get it into a PR
correctly.

## STARTUP_RECEIPT

Re-verify live:
```
git worktree list
```
Confirm a worktree at `/Users/ahjan/phoenix_omega_wt_outfit_continuity` (or find its
current path if moved/pruned — check `git worktree list` output directly, don't assume
the path from this prompt is still valid) on branch `agent/outfit-object-continuity`,
with commit `61f9a8fb85` (`feat(manga): system-wide outfit and object continuity
locks`, 19 files, +1672/-8) as its tip, working tree clean.

```
git ls-remote origin agent/outfit-object-continuity
```
Confirm this returns nothing (branch not yet pushed). If it now returns a ref, someone
else already pushed it — check for an open PR first (`gh pr list --head
agent/outfit-object-continuity`) before doing anything, per this repo's sibling-session
collision protocol.

## Context

This branch implements a 3-PR-scope architecture (continuity schema/cache-key fix,
outfit/object bank contracts, LoRA ladder spec) that was reviewed and approved by the
operator earlier today, then implemented and committed as a single combined commit in
one worktree session rather than split into the originally-planned 3 PRs. 80 tests
passed at commit time. Re-run them — don't trust the prior session's count without
verification.

## Task

1. From the worktree (or a fresh `origin/main`-based branch if the worktree was
   pruned — in that case, cherry-pick `61f9a8fb85` onto a clean branch off current
   `origin/main` instead of rebasing the whole worktree), run the mandatory preflight:
   `git status --short`, `git fetch origin`,
   `git rev-list --left-right --count origin/main...HEAD`,
   `PYTHONPATH=. python3 scripts/git/push_guard.py`,
   `scripts/ci/preflight_push.sh`, `bash scripts/git/health_check.sh`,
   `PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py`.
2. Re-run the test suite this commit touches (manga continuity, cache-key, bank-lookup
   tests) and confirm the same ~80-pass result before pushing — do not push on a stale
   "tests passed" claim from a prior session.
3. Check whether `origin/main` has moved meaningfully since this commit's base (it's
   likely several commits behind after today's session) — if `phoenix_v4/social` or
   related manga modules changed underneath this diff, rebase and re-resolve rather
   than force-pushing a stale base.
4. Push, open the PR (title: `feat(manga): system-wide outfit and object continuity
   locks`), and run the same governance checks as every other PR in this pack
   (`pre_merge_check.sh`, `pr_governance_review.py --pr <n>`).
5. Given the operator explicitly approved a 3-PR split originally but the work landed
   as one combined commit — flag this in the PR description as a deviation from the
   agreed plan (single PR instead of three) so reviewers know it wasn't silently
   re-scoped, and let the operator decide whether to split it retroactively or accept
   it as one PR.

## Landing

MERGED or BLOCKED, same as every other lane. Watch CI to terminal state (poll, no
monitor-parking).

## CLOSEOUT_RECEIPT (required, exact)

PR number, final SHA, test re-run results, explicit note on the single-PR-vs-three-PR
deviation. Signal token: `LANE3_OUTFIT_CONTINUITY_LANDED_<PR number>`.
