# Onboarding Post-Merge Hygiene Guide

Purpose: safe cleanup and stabilization guidance after onboarding/prez merge.

Repo-wide hygiene (branches, worktrees, stale refs): [docs/REPO_HYGIENE_AND_WORKTREE_CLEANUP.md](./REPO_HYGIENE_AND_WORKTREE_CLEANUP.md). Fidelity upgrades (demo → production exports): [docs/ONBOARDING_PROOF_FIDELITY_UPGRADE_LANE.md](./ONBOARDING_PROOF_FIDELITY_UPGRADE_LANE.md).

## Locked system status

Brand onboarding/prez is fully wired, fully proof-covered, and production-observable. Coverage is complete via in-repo pipeline-demo assets; future work is fidelity replacement.

## Safe-now cleanup (no behavior change)

Run only after confirming no one is actively using the referenced worktrees:

```bash
# 1) Remove temporary hygiene worktree branch (after this PR merges)
git worktree remove "/Users/ahjan/phoenix_omega/.worktrees/post-merge-onboarding-hygiene"
git branch -D agent/post-merge-onboarding-hygiene

# 2) Remove onboarding delivery worktree (if no longer needed)
git worktree remove "/Users/ahjan/phoenix_omega/.worktrees/brand-onboarding-100"
git branch -D agent/brand-onboarding-100
git push origin --delete agent/brand-onboarding-100
```

## Safe with caution (manual confirmation required)

Only run after inspecting branch ownership and active usage:

```bash
# Show active worktrees and attached branches
git worktree list --porcelain

# Show merged local branches
git branch --merged origin/main
```

If a branch is merged and not attached to an active worktree, it is usually safe to delete locally:

```bash
git branch -d <merged-branch>
```

## Historical cleanup (optional)

Many legacy `agent/*` and `claude/*` branches are already merged/gone-upstream. Keep them if you need forensic history; otherwise prune gradually:

```bash
# Prune stale remote tracking refs first
git remote prune origin
```

Then delete confirmed merged local branches one-by-one with `git branch -d`.

## What not to do

- Do not delete branches attached to active worktrees.
- Do not hard reset or force delete anything from the main working checkout without manual confirmation.
- Do not remove onboarding evidence artifacts (`artifacts/onboarding/proof_completion_latest.md`) unless superseded intentionally.
