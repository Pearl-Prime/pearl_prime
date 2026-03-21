# Pearl_GitHub Repo Memory

This is lived operational memory, not theory. Read this before risky git work.

## Incident Memory

### 2026-03-20 — Wrong-base branch triggered push-guard hard block

What happened:

- `agent/manga-mode` was created from `codex/runtime-consolidation`, not from `origin/main`
- Push attempt was blocked by pre-push guard with:
  - `commits=200`
  - `files=22573`
  - `total_mb=2716.5`
  - `max_blob_mb=37.3`
- The actual intended change was small, but ancestry made the push look enormous

What this means:

- Branch name is not enough
- Small staged diff is not enough
- Pearl_GitHub must inspect ancestry against `origin/main` before any push

Recovery pattern that worked:

```bash
git fetch origin
git checkout -b agent/<task>-clean origin/main
git cherry-pick <good-commit>
git push -u origin agent/<task>-clean
```

Permanent lesson:

- Never create agent branches from `codex/*`
- Always verify with `git rev-list --left-right --count origin/main...HEAD`
- If ahead count is unexpectedly large, stop immediately

### 2026-03-20 — Branch existed on GitHub but local worktree did not actually contain Pearl_GitHub

What happened:

- Local branch `agent/pearl-github` existed but matched `origin/main`
- The intended Pearl_GitHub commit existed in history (`d7971156`) but was not present in the checked-out branch files
- `ps.txt` was missing on the branch
- `CLAUDE.md` was also missing on the branch

Recovery pattern that worked:

- Cherry-pick the intended commit onto the real branch
- Resolve `CLAUDE.md` conflict
- Create branch-valid `ps.txt`
- Push the repaired branch

Permanent lesson:

- Do not assume a branch name means the branch contains the feature
- Verify with:

```bash
git log --oneline --decorate -n 5
git status --short --branch
find skills -maxdepth 2 -type f
```

### 2026-03-20 — Tooling mismatch across branches

What happened:

- `ps.txt` instructed Pearl_GitHub to run `python scripts/git/push_guard.py`
- On this branch:
  - `python` was not available, only `python3`
  - `scripts/git/push_guard.py` did not exist
  - `scripts/ci/preflight_push.sh` existed but required `bash` invocation

Permanent lesson:

- Pearl_GitHub must check repo reality before following a command literally
- Health checks must degrade gracefully when branch-specific tooling is absent
- Preferred pattern:
  - use `python3` when available
  - check file existence before invoking tooling
  - invoke shell scripts with `bash ...`

## Branch Memory Snapshot — 2026-03-20

### Healthy / intentional

- `main` tracks `origin/main`
- `agent/manga-mode-clean` is a clean one-commit branch from `origin/main`
- `agent/pearl-github` is a clean one-commit branch from `origin/main`
- `codex/pearl-news-cleanup` is a small diverged branch (`1 behind / 1 ahead` vs `origin/main`)

### High-risk / cleanup candidates

- `agent/manga-mode`
  - `202` commits ahead of `origin/main`
  - wrong-base branch
  - should not be pushed
  - keep only if needed for local recovery/reference; otherwise delete after confirming nothing unique remains

- `codex/runtime-consolidation`
  - `199` commits ahead of `origin/main`
  - local branch is also `34` commits ahead of `origin/codex/runtime-consolidation`
  - not safe for blind merge
  - must be audited before any merge or push

- `codex/pearl-news-full-qa-v2`
  - upstream is gone
  - local branch should be either rehomed, archived, or deleted after review

- `preflight/runtime-merge-check`
  - behind upstream by `144`
  - clearly a worktree/helper branch, not active development truth

### Worktree clutter

- Multiple `worktree-agent-*` branches are fully merged into `origin/main`
- They are likely safe local cleanup candidates once their linked worktrees are no longer needed

### Local dirt observed during audit

- Untracked: `11.txt`
- Untracked directory: `config/musicians/`
- Untracked temp file: `scripts/video/test_write.tmp`

These are not part of Pearl_GitHub, but they do mean the working tree is not pristine.

## Pearl_GitHub Operating Posture

When in doubt:

1. Check ancestry before checking diff size
2. Check branch contents before trusting branch names
3. Check tool existence before following scripted instructions
4. Prefer recovery branches from `origin/main`
5. Treat stale local branches and worktree branches as debt until explicitly cleaned

## Cleanup Memory — 2026-03-20 / 2026-03-21 verification

Verified current end state after cleanup:

- only one live worktree remains: the main repo checkout
- only four local branches remain:
  - `main`
  - `codex/runtime-consolidation`
  - `codex/pearl-news-cleanup`
  - `codex/next-dev-clean`
- the previously merged remote branches were deleted successfully:
  - `origin/codex/fix-wp-site-url-normalization`
  - `origin/codex/harden-pearl-news-pipeline`

Operational lessons:

- do not trust pasted cleanup summaries without re-running `git branch -vv`, `git worktree list --porcelain`, and merged/unmerged remote branch checks
- on this repo, `scripts/git/push_guard.py` may be absent even though `ps.txt` references it
- `scripts/ci/preflight_push.sh` should be invoked with `bash`
- `git branch -r --merged origin/main` and `git branch -r --no-merged origin/main` are the fastest safe branch cleanup inventory pair
- local `main` can look "healthy enough" while still being unsuitable for direct work because of autobackup commits and unrelated local modifications

Ongoing state tracking:

- use `docs/PEARL_GITHUB_STATE.md` as the fast resume/checklist file
- update it whenever branch inventory, Colab verification status, or next actions materially change

Latest verified state change:

- PR #24 merged on 2026-03-21T07:35:43Z
- local `main` was repaired by saving autobackup commits to `codex/main-autobackup-20260320-2124` and resetting `main` to `origin/main`
- PR #25 merged on 2026-03-21T07:49:08Z
- local `main` was then fast-forwarded again and now matches `origin/main`
- Step 10 PDF export was visibly confirmed in thread, and the user explicitly confirmed Colab Steps 1-13 are done
- the remaining 10 remote `codex/*` branches were dispositioned into `delete`, `harvest`, and `keep-open` buckets in `docs/BRANCH_DISPOSITION_2026_03_20.md`
- a local-only credentials source may exist at `docs/all_credentials.txt`; agents should use `scripts/integrations/intake_all_credentials_local.sh`, avoid echoing secrets, and never try random username/password combinations across services
- for messaging work, agents should run `scripts/integrations/report_messaging_requirements_local.sh` before setup or send attempts so missing API tokens, recipient IDs, and handles are explicit
- PR #31 merged on 2026-03-21T21:34:27Z and placed the AI Manga Dharma system on `main` as a 14-document spec suite under `specs/`; future manga work should start from `specs/AI_MANGA_PIPELINE_SUMMARY.md` and `specs/README.md`
