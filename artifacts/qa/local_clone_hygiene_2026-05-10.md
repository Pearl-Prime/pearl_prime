# Local clone hygiene audit — 2026-05-10

**PROJECT_ID:** PRJ-PEARL-DEVOPS-LOCAL-HYGIENE  
**SUBSYSTEM:** pearl_devops (operator-machine cleanup; no push from damaged primary clone)  
**Operator clone:** `/Users/ahjan/phoenix_omega`

## Initial state (pre-hygiene)

| Item | Value |
|------|--------|
| Branch (reported) | `agent/ci-baseline-recovery-v1-cap-20260509` (later observed on other topic branches at same drifted `HEAD`) |
| Diff vs `origin/main` | ~31,474 paths (`git diff-tree --name-only -r origin/main HEAD`); operator report ~31,492 files / ~201.8 MB |
| Noise vs genuine | ~30,480 paths under `.claude/worktrees/`; ~994 paths outside that prefix (includes large `artifacts/`, workflows, binaries) |
| Monster commit | `221b35dfe1` — ~31,485 files changed (nested `.claude/worktrees/` snapshot) |
| `origin/main` at reset | `e25bd63e8a20f1c13fa4285ccfe1be095523546a` |
| Root cause | `.claude/worktrees/` ephemera committed into the local branch tree; concurrent git + interrupted cleanup left **corrupt `.git/index`** (`index file smaller than expected`), blocking normal fetch/checkout until repaired |

## Phase 2 — conservative backup

**Location:** `/tmp/phoenix_omega_local_hygiene_2026-05-10/`

| Artifact | Description |
|----------|-------------|
| `patches/excluding_dot_claude_worktrees.patch` | Unified diff `origin/main..HEAD` with pathspec exclude `.claude/worktrees` (~2.3 MB text) |
| `patches/genuine_vs_origin_main_excluding_worktrees.patch.gz` | Earlier gzip of the same class of diff |
| `patches/0001-*.patch` | `git format-patch -1` for small commits after the monster commit (docs, CI cover-art warn mode, coordination, chore backups) |
| `patches/commits_ahead_of_origin_main.txt` | Local commits that had been ahead of `origin/main` |
| `non_worktree_changed_paths.txt` | Path manifest (~994 entries) |
| `new_files/` | Wave-pattern / coordination captures (includes `artifacts_wave_refresh/` rsync where present; post-reset `artifacts/coordination/CONDUCTOR_HANDOFF.md` and `orchestrator_log_2026-05-10.md` moved here for a **fully empty** `git status`) |
| `needs_review/` | Manifests / samples as captured during triage |
| `BACKUP_INVENTORY.txt` | Human-readable inventory |
| `quarantine/worktrees_*` | **Fast path:** entire repo `.claude/worktrees/` **moved aside** with `mv` (avoids multi-hour `rm -rf` on millions of files); operator may delete this quarantine after verifying backups |

Skipped in patch backup: live `.claude/worktrees/**` contents (machine ephemera; not patch-worthy per policy).

## Phase 3 — reset to `origin/main` (2026-05-10 completion)

1. **`git fetch origin`** — confirmed `origin/main` = `e25bd63e8a`.
2. **Ephemera out of the way:** `mv /Users/ahjan/phoenix_omega/.claude/worktrees` → `/tmp/phoenix_omega_local_hygiene_2026-05-10/quarantine/worktrees_<timestamp>` (after stopping a long-running `rm -rf` attempt).
3. **Index rebuild:** removed corrupt `.git/index` / stale `.git/index.lock`; `git update-ref refs/heads/main origin/main`; `git symbolic-ref HEAD refs/heads/main`; `git read-tree -u -m origin/main` (removed blocking untracked paths such as `.claude/scheduled_tasks.lock` and `.cursor/*.log` where they conflicted with tracked paths).
4. **`git reset --hard origin/main`** — repopulated working tree to match `origin/main` (expect LFS smudge warnings if `GIT_LFS_SKIP_SMUDGE=1` was used elsewhere; tree still matches commit).
5. **`git worktree prune`**.
6. **Clean slate:** two residual untracked coordination files under `artifacts/coordination/` were moved to `new_files/` so **`git status` is empty**.

No commits and **no push** were made from `/Users/ahjan/phoenix_omega` during hygiene (per policy). `origin/main` was not rewritten.

## Final state (operator clone)

| Check | Result |
|--------|--------|
| `HEAD` | `e25bd63e8a20f1c13fa4285ccfe1be095523546a` |
| Branch | `main` |
| Committed tree vs `origin/main` | **0** paths (`git diff-tree --name-only -r origin/main HEAD`) |
| Working tree | **`git status --short` empty** |
| File-count delta (reported noise) | ~31k path diff → **0** vs `origin/main` |

## PR for this audit document

- **PR:** https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1003  
- **Branch:** `agent/local-clone-hygiene-2026-05-10`  
- **Initial audit commit on branch:** `f6cbbc248a40b8be20f3580ed6544335fa735e81` (doc-only; sibling clone `phoenix_omega_local_hygiene_pr_wt`)

**HANDOFF_TO:** operator — primary clone is aligned to `main` at `e25bd63e8a` with a clean index and empty status; delete `/tmp/.../quarantine/worktrees_*` when satisfied backups are enough.
