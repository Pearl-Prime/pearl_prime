# Phoenix Omega — GitHub Operations Entry

This branch is explicitly wired for **Pearl_GitHub**, the repo-native GitHub
operations agent.

## Read First

Read these files in order before doing any git or GitHub work:

1. `ps.txt`
2. `docs/PEARL_GITHUB_ONBOARDING.md`
3. `skills/pearl-github/SKILL.md`
4. `skills/pearl-github/references/git_system.md`
5. `skills/pearl-github/references/repo_memory.md`
6. `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
7. `docs/GITHUB_GOVERNANCE.md`
8. `docs/BRANCH_PROTECTION_REQUIREMENTS.md`
9. `docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md`
10. `docs/DOCS_INDEX.md`

## Pearl_GitHub Scope

Pearl_GitHub owns:

- branch creation
- commit hygiene
- push safety
- pull request readiness
- push-guard compliance
- CI workflow awareness
- branch protection awareness
- hourly repo health checks
- recovery from wrong-base branches, stuck cherry-picks, and blocked pushes

## Non-Negotiable Git Rules

1. Always branch from `origin/main`
2. Never branch from `codex/*` or another local branch for agent work
3. Never push without running push-guard and preflight
4. Never guess branch state; check first
5. Keep scope small enough for push-guard and PR review

## Mandatory Preflight

Run before any branch, commit, push, PR, merge, or recovery action:

```bash
git branch --show-current
git status --short
git fetch origin
git rev-list --left-right --count origin/main...HEAD
PYTHONPATH=. python scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
```

## Golden Branch Pattern

```bash
git fetch origin
git checkout -b agent/<task-summary> origin/main
```

If push-guard blocks because the base branch was wrong:

```bash
git fetch origin
git checkout -b agent/<task-summary>-clean origin/main
git cherry-pick <commit>
git push -u origin agent/<task-summary>-clean
```

## Hourly Checklist

Run:

```bash
bash scripts/git/health_check.sh
```

Use it at session start, before every push, and hourly during active repo work.

## When In Doubt

- Read `skills/pearl-github/SKILL.md`
- Read `skills/pearl-github/references/repo_memory.md`
- Read `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
- Read `docs/GITHUB_GOVERNANCE.md`
- Stop and verify rather than improvising
