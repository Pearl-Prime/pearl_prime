# Pearl_GitHub — Onboarding Guide

**Purpose:** Quick-start guide for the Pearl_GitHub agent. Read this before doing any git/GitHub operation in Phoenix Omega.

**Skill file:** `skills/pearl-github/SKILL.md` (full reference)
**Quick reference:** `skills/pearl-github/references/git_system.md`

---

## What Pearl_GitHub Does

Pearl_GitHub owns all git operations in Phoenix Omega: branching, committing, pushing, PRs, CI workflow management, and repo health. Other agents (Pearl_Dev, Pearl_Writer, Pearl_Editor) do the work — Pearl_GitHub handles the git lifecycle.

## The #1 Rule

**Always branch from `origin/main`.** Never from `codex/*` or other local branches.

```bash
git fetch origin
git checkout -b agent/<task> origin/main
```

If you violate this rule, push-guard will block with "too many commits / too many files" because it sees the entire parent branch's history.

## The 4 Things You Must Run Before Every Push

```bash
git fetch origin
git rev-list --left-right --count origin/main...HEAD    # should be 0 <small-number>
PYTHONPATH=. python scripts/git/push_guard.py            # must pass
scripts/ci/preflight_push.sh                              # must pass
```

## Push-Guard Limits

| Limit | Value |
|-------|-------|
| Max commits | 30 |
| Max changed files | 300 |
| Max total payload | 25 MB |
| Max single file | 8 MB |

## PR Scope Limits

| Limit | Value |
|-------|-------|
| Max files changed | 15 |
| Max lines changed | 1000 |
| Max system layers | 2 |

## Hourly Health Check

```bash
bash scripts/git/health_check.sh
```

Run this at session start, before pushes, and ideally every hour. It checks: branch state, remote sync, push-guard compliance, lock files, stale branches, and large files.

For a full hourly cleanup loop that can merge clean PRs, sync local `main`, and prune stale local branches, use:

```bash
bash scripts/git/hourly_repo_alignment.sh
```

## When Push-Guard Blocks

```bash
# Diagnose
PYTHONPATH=. python scripts/git/push_guard.py --json

# Fix: cherry-pick to clean branch
git fetch origin
git checkout -b agent/<task>-clean origin/main
git cherry-pick <your-commit-hash>
git push -u origin agent/<task>-clean
```

## Key Files

| File | What it does |
|------|-------------|
| `scripts/git/push_guard.py` | Blocks oversized pushes |
| `scripts/git/safe_push.sh` | Push with retry + backoff |
| `scripts/git/health_check.sh` | Hourly health check |
| `scripts/git/hourly_repo_alignment.py` | Hourly Pearl_GitHub autopilot |
| `scripts/git/hourly_repo_alignment.sh` | Shell wrapper for hourly autopilot |
| `scripts/git/install_push_guard.sh` | Install push hook |
| `scripts/ci/preflight_push.sh` | Pre-push validation |
| `.githooks/pre-push` | Active push hook |
| `.github/pull_request_template.md` | PR template |
| `docs/LOCAL_GIT_DRIFT_PREVENTION_SOP.md` | Branching SOP |
| `docs/BRANCH_PROTECTION_REQUIREMENTS.md` | Branch protection |

## Key Docs

- `skills/pearl-github/SKILL.md` — Full agent skill (all rules, workflows, recovery)
- `docs/LOCAL_GIT_DRIFT_PREVENTION_SOP.md` — Branching rules
- `docs/BRANCH_PROTECTION_REQUIREMENTS.md` — CI requirements for main
- `docs/PEARL_GITHUB_AUTOPILOT_RUNBOOK.md` — Hourly repo-alignment loop and report outputs
- `docs/GITHUB_GOVERNANCE.md` — Governance rules
- `docs/AUTO_MERGE_POLICY.md` — Auto-merge for bot-fix PRs
