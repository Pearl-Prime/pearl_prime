# Local clone hygiene audit — 2026-05-10

**PROJECT_ID:** PRJ-PEARL-DEVOPS-LOCAL-HYGIENE  
**SUBSYSTEM:** pearl_devops (operator-machine cleanup; no direct push from damaged clone)  
**Operator clone:** `/Users/ahjan/phoenix_omega`

## Initial state (pre-hygiene)

| Item | Value |
|------|--------|
| Branch (stated) | `agent/ci-baseline-recovery-v1-cap-20260509` |
| Approx. diff vs `origin/main` | ~31,474 paths (`git diff-tree`); operator report ~31,492 files / ~201.8 MB |
| Noise vs genuine | ~30,480 paths under `.claude/worktrees/`; ~994 paths outside that prefix |
| `origin/main` at time of reset | `e25bd63e8a20f1c13fa4285ccfe1be095523546a` |
| Root cause | Stale `.claude/worktrees/` ephemera plus local branch drift; prior `git reset --hard` left a **zero-byte `.git/index`**, breaking `git fetch` / `git status` until repaired |

## Phase 2 — conservative backup

**Location:** `/tmp/phoenix_omega_local_hygiene_2026-05-10/`

| Artifact | Description |
|----------|-------------|
| `patches/genuine_vs_origin_main_excluding_worktrees.patch.gz` | Unified diff `origin/main..HEAD` excluding `.claude/worktrees` (gzip) |
| `patches/commits_ahead_of_origin_main.txt` | Seven local commits that had been ahead of `origin/main` |
| `non_worktree_changed_paths.txt` | Path manifest (~994 entries) |
| `new_files/artifacts_wave_refresh/` | Rsync of `artifacts/wave_refresh/` (Wave-pattern JSON; 196 files) |
| `needs_review/` | Manifest + copies of two untracked coordination templates |
| `BACKUP_INVENTORY.txt` | Human-readable inventory |

Skipped: `.claude/worktrees/**` (operator ephemera; not patch-worthy per policy).

## Phase 3 — reset to `origin/main` and index repair

1. Prior session completed `git reset --hard origin/main` to commit `e25bd63e8a` (HEAD matched `origin/main`; `git diff-tree origin/main HEAD` count **0**).
2. **Index repair:** `.git/index` was corrupt (0 bytes). A valid index was copied from a **donor shallow clone** at the same commit:  
   `/tmp/phoenix_omega_index_donor_20260510` (clone of `https://github.com/Ahjan108/phoenix_omega_v4.8.git`, depth 1, `main` = `e25bd63e8a`).
3. `git symbolic-ref HEAD` → `refs/heads/main`; `git reset --hard origin/main` re-aligned the working tree (LFS: ~967 “should have been pointers” warnings when smudge skipped — expected for local binaries vs pointer mode).
4. `git worktree prune` executed.
5. **Residual local-only noise (acceptable):** untracked and dirty entries under `.claude/worktrees/` (active Claude Code worktrees) and optional untracked `artifacts/coordination/*.md` logs. **Does not change the committed tree;** `origin/main` is unchanged.

## Final state (operator clone)

| Check | Result |
|--------|--------|
| `HEAD` | `e25bd63e8a20f1c13fa4285ccfe1be095523546a` |
| Branch | `main` |
| Committed tree vs `origin/main` | **0** paths (`git diff-tree --name-only -r origin/main HEAD`) |
| File-count delta (reported noise) | ~31k path diff → **0** (committed baseline) |

## PR for this audit document

This file is added via a **fresh sibling clone** (not from `/Users/ahjan/phoenix_omega`) as `artifacts/qa/local_clone_hygiene_2026-05-10.md` on branch `agent/local-clone-hygiene-2026-05-10`.

**HANDOFF_TO:** operator — clone is usable for normal git operations against `main` at `e25bd63e8a`; keep or delete `.claude/worktrees/` scratch dirs locally as you prefer.
