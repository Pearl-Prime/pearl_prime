# Repo hygiene and worktree cleanup

Purpose: **repo-wide** safe cleanup after merges — branches, worktrees, and stale remote refs — without breaking active lanes.

**Onboarding-specific** quick path: [docs/ONBOARDING_POST_MERGE_HYGIENE.md](./ONBOARDING_POST_MERGE_HYGIENE.md).

**Automation:** [docs/PEARL_GITHUB_AUTOPILOT_RUNBOOK.md](./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md) (hourly alignment + prune guidance), `bash scripts/git/health_check.sh` (session/push sanity).

---

## 1. Inspect before deleting

```bash
git fetch origin
git worktree list --porcelain
git branch -vv
git branch --merged origin/main
git remote prune origin --dry-run
```

Treat **any branch listed in `worktree list`** as *do not delete* until that worktree is removed.

---

## 2. Safe-now sequence (local)

Typical pattern after a feature branch merged and remote branch deleted:

```bash
git worktree remove /path/to/worktree-directory
git branch -d agent/feature-branch-name   # or -D only if you accept losing unpushed commits
```

If GitHub still shows the remote branch (rare after squash merge + delete):

```bash
git push origin --delete agent/feature-branch-name
```

---

## 3. Optional historical cleanup

- **`git remote prune origin`** — drop stale `origin/*` refs after teammates delete branches.
- **`git branch --merged origin/main`** — list local merge commits that are fully contained in `main`; delete with `git branch -d` one at a time after confirming no exclusive commits you care about.
- **Gone-upstream locals** (`git branch -vv` shows `[origin/foo: gone]`) — usually safe to remove locally if not attached to a worktree.

Keep old branches when they are evidence for an audit, incident, or open recovery spec.

---

## 4. What not to do

- Do not `git branch -D` on shared or ambiguous branches without checking `git reflog` and worktrees.
- Do not force-push to `main` / `master`.
- Do not delete evidence artifacts under `artifacts/` unless a newer governed artifact supersedes them (see repo persistence protocol).

---

## 5. Docs and CI drift

- **Stale docs:** Prefer surgical updates to authority rows in [docs/DOCS_INDEX.md](./DOCS_INDEX.md) over one-off handoff files. **Docs CI** runs governance checks when `docs/**` or `specs/**` change.
- **Onboarding registry:** `scripts/ci/validate_onboarding_registry.py` runs in **Core tests** (required) and in **Docs CI** when onboarding config/public paths change — see `.github/workflows/docs-ci.yml`.
