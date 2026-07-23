# EXECUTE — Lane 03 (Pearl_GitHub): Worktree + branch cleanup, rescue real work

This is an execution prompt, not a planning request. End state: **dead worktrees
gone, stale branches gone, every rescued branch MERGED-or-BLOCKED as its own PR,
and this branch's 9 stranded commits landed.** "Cleanup later" is not an end state.

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD SHA, `git worktree list`, `gh auth status`,
  `git fetch origin && git log origin/main -1 --oneline`.
- Every verdict below is a CLAIM from the 2026-07-24 survey — re-verify each before
  deleting: **verify-ahead-not-stale** (`git diff origin/main <branch> --stat` empty
  ⇒ squash-merge-redundant ⇒ safe to delete; "N commits ahead" alone proves nothing).
- Deletion discipline: worktree removal = `git worktree remove <path>` (+ `--force`
  only for the poisoned ones) then `git worktree prune`. NEVER `rm -rf` a non-empty
  tracked worktree directly (field-clear hazard). Branch deletion = local `-D` only
  after the diff-empty check; remote branches only for merged PRs.
- Rescue pattern (golden branch): `git fetch origin && git checkout -b <name>-land
  origin/main && git cherry-pick <shas>` — never push an old-base branch. LFS:
  `GIT_LFS_SKIP_SMUDGE=1` on every worktree add (~3.2GB smudge otherwise).
- Preflight before every push: push_guard + preflight_push + health_check. Merge
  rules: Rule-0, pre_merge_check (live CI gate), governance review. Operator has
  pre-authorized squash-merge of green rescue PRs.
- Rule-0 hard line: this lane deletes NOTHING that shows >50 tracked-file deletions
  in any PR it opens. Local branch/worktree deletion after verified-merged is exempt.
- Layer-honest closeout + cleanup ledger. Manga-content branches belong to Lane 07 —
  do not land them here (listed below to hand off, not to work).

## Phase A — land THIS branch's stranded commits first (highest value)
`agent/bestseller-atom-flow-lanes-20260721` is 9 ahead of origin/main and its tree
is shared+dirty (multiple sessions). NEVER push it as-is.
1. `git log origin/main..agent/bestseller-atom-flow-lanes-20260721 --oneline` —
   identify the commits: handoffs (`6756fe5fe1`, `f551bb48ec`, `b0323b81ca`),
   waystream zh-TW pack (`cd70b60924`), genre-bubble wiring (`aad5cf2152`), others.
2. Cherry-pick the DOCS commits (handoffs + waystream pack) onto a clean branch
   `agent/land-stranded-docs-20260724` off origin/main → PR → merge. Lane 06 needs
   the waystream pack ON MAIN — signal `PIPER100-L03-WAYSTREAM-PACK-LANDED`.
3. The genre-bubble commit (`aad5cf2152`) is manga CODE → cherry-pick onto
   `agent/manga-genre-bubble-land-20260724`, push, open PR, then HAND TO Lane 07
   (do not merge here; manga review discipline applies).
4. Do NOT delete or reset the source branch — other sessions are live on it. Note
   remaining ahead-commits in the ledger.

## Phase B — delete verified-dead worktrees (9)
For each: confirm merged/empty via `gh pr list --head <branch> --state merged` +
diff-empty check, then remove worktree, then delete local branch.
`wt-zhtw-registry`†, `gov-exception-wt`† (†dirs already gone — `git worktree prune`),
`.claude/worktrees/agent-a1ee798b347ab3a6f` (bare main checkout),
`.claude/worktrees/agent-a44a14eb8ebd93d42` (#147), `.claude/worktrees/fervent-shaw-761791`
(#201; its 13 dirty files are test-run noise — confirm none are new source files before
force-remove), `.worktrees/teacher-ob-20260721` (#18),
`phoenix_omega_worktrees/zh-cn-phase3` (#77),
`phoenix_omega_worktrees/social-atom-scaleup-wave3-20260721` (#13, poisoned),
`phoenix_omega_worktrees/main-ci-unbreak-20260722` (poisoned, no content).

## Phase C — rescue non-manga real work (each → clean branch → PR → merge)
1. **`translation-100pct-unblock`** (poisoned worktree, 1 real commit: slot-role
   schema + safe Ollama translation). Cherry-pick from a CLEAN checkout by SHA —
   never work inside the poisoned tree.
2. **`prod_2h_20260719`** (7 commits — Perfect Books Wave-1/2: bank fill, lane03
   flagship line-edit, lane06 audit). The line-edit lane is the flagship-register
   lever per doctrine — this is the most valuable rescue. Dedupe vs main first
   (some may have landed via other PRs).
3. **`translate_20260716`** (13 commits, 14-locale waves). DEDUPE HARD vs the merged
   retranslation waves #152–155 before landing — land only what main lacks.
4. **`session-mining-specs-do-all-20260718`** (3 commits, 9 DRAFT specs + APPROVE
   decision — previously blocked on a 403 that is now resolved).
5. **`zhtw-clean-retranslate-20260722`** — **verify-then-discard**: per
   `ZHTW_TRANSLATION_QUALITY_HANDOFF_20260724`, local batches 015–020 are broken
   (phantom mass deletes) and the retranslation shipped via #152–155. Confirm
   committed batches 1–8 add nothing over main (spot-diff 5 files); then delete
   branch + worktree. If they DO add real content, cherry-pick the delta only.
6. Uncommitted WIP — inspect and decide (commit-to-branch or discard with a note):
   `agent-fix-ci-two-gates-20260722` (7 mod + 10 untracked: manga gates yaml,
   register_output_strengthen.py — if manga-relevant, tar to
   `~/phoenix_workspace_archive/` and hand the path to Lane 07),
   `worldwide_lang_20260720` (spec + 4 scripts, all untracked — commit to a branch
   + PR if coherent, else archive-tar + note).

**Hand to Lane 07 (do not land here):** `manga-one-us-en-book-20260716`,
`manga-genre-story-only`, `outfit_continuity` (+ the genre-bubble PR from Phase A).

## Phase D — stale branch sweep (~980 local)
Script it: for each local branch not in {protected, active-lane, rescue list}:
`git diff origin/main <branch> --stat | tail -1` empty AND no open PR ⇒ delete local.
Batch-report counts, list survivors with reasons. Do not touch remote branches
except merged-PR branch deletion (GitHub setting may do this already).

## Closeout
```
CLOSEOUT_RECEIPT: PIPER100-L03-DONE
stranded_commits_landed: <PR#s + SHAs; waystream pack on main yes/no>
worktrees_removed: <count + list>
branches_deleted: <count>  branches_kept: <list + why>
rescues_merged: <PR#s>  rescues_blocked: <branch + blocker>
handed_to_lane07: <branch/PR list>
archived_tars: <paths or none>
NEXT_ACTION: <...>
```
Append a dated note to this pack's INDEX.md.
