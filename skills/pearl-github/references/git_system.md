# Pearl_GitHub — Git System Quick Reference

## Push-Guard Limits (scripts/git/push_guard.py)

```
max_commits:    30      (env: PUSH_GUARD_MAX_COMMITS)
max_files:      300     (env: PUSH_GUARD_MAX_FILES)
max_total_mb:   25      (env: PUSH_GUARD_MAX_TOTAL_MB)
max_single_mb:  8       (env: PUSH_GUARD_MAX_SINGLE_MB)
```

## PR Scope Limits (ps.txt STEP 6)

```
max_files:      15
max_lines:      1000
max_layers:     2       (e.g. scripts + tests OK; scripts + config + docs + content NOT OK)
```

## Branch Naming

```
main                          — production (PR-only, never direct push)
codex/<topic>-<yyyymmdd>      — long-lived development branches
agent/<task-summary>           — temporary agent branches (delete after PR merge)
```

## Required Status Checks for main

1. core-tests.yml
2. release-gates.yml
3. ei-v2-gates.yml
4. change-impact.yml
5. truth-audit-gate.yml
6. drift-gate.yml
7. pearl-prime-smoke.yml (path-filtered)

## EXCLUSIVE Files (only one agent at a time)

- config/teachers/teacher_registry.yaml
- config/musicians/musician_registry.yaml
- config/gates.yaml
- docs/SYSTEM_TRUTH.md
- docs/DEV_ENTRY.md
- docs/DOCS_INDEX.md
- scripts/go_live.py
- scripts/run_pipeline.py
- scripts/run_pearl_news_teacher_batch.py
- pearl_news/pipeline/assemble_v52.py

## Commit Message Format

```
<type>(<scope>): <summary>

Types: feat, fix, chore, docs, test, refactor, ci
Scope: manga, pearl-prime, pearl-news, gates, config, etc.
```

## Pre-Push Checklist (run before EVERY push)

```bash
git fetch origin
git rev-list --left-right --count origin/main...HEAD
sed -n '1,220p' skills/pearl-github/references/repo_memory.md
[ -f scripts/git/push_guard.py ] && PYTHONPATH=. python3 scripts/git/push_guard.py
bash scripts/ci/preflight_push.sh
PYTHONPATH=. python scripts/pr_risk.py
```

If `scripts/git/push_guard.py` does not exist on the current branch, do not
pretend it ran. Fall back to ancestry inspection, file-count inspection, and
preflight.

## Recovery: Cherry-Pick to Clean Branch

```bash
git fetch origin
git checkout -b agent/<task>-clean origin/main
git cherry-pick <commit-hash>
git push -u origin agent/<task>-clean
```

## Docs to Update After Push

1. docs/SYSTEM_TRUTH.md — if system status changed
2. docs/DEV_ENTRY.md — if run commands changed
3. docs/DOCS_INDEX.md — if docs created/moved
4. CHANGELOG.md — if significant
