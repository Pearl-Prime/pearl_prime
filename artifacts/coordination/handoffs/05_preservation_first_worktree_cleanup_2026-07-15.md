# 05 - Preservation-First Worktree Cleanup Handoff

STATUS=BLOCKED
SIGNAL: preservation-worktree-cleanup-terminal=blocked

Discovery:
- Free-space tier: critical-low, `/System/Volumes/Data` has 9.3Gi available and 98% used.
- Root checkout: `/Users/ahjan/phoenix_omega`, branch `codex/registry-40x14-waystream`, HEAD `45eda6ddf049a874009643f5e48bda9b1ca4b1bb`, 271 status entries, remote branch pruned. HOLD.
- #5636 worktree: clean, merged, no local value remaining. Removed.
- pr5237 worktree: `/Users/ahjan/phoenix_omega_worktrees/mecha-native-proof-20260710`, branch `agent/pr5237-cloud-reconcile-20260710`, HEAD `321379f8f8efa5359b1a2af1ff6919cfc48011d4`, PR #5237 open, status includes an unresolved `UU` conflict and local additions/modifications. HOLD.
- #5623 candidate: `/Users/ahjan/phoenix_omega_worktrees/pr5623-frfr-overmatch-fix-20260715`, branch `codex/pr5623-frfr-overmatch-fix-20260715`, HEAD `6918f9800440c233c315c64811763afe313b2caf`, clean status but not an ancestor of current `origin/main` and branch does not match merged PR #5623 head. HOLD.
- 2026-07-15 resume candidate: `/Users/ahjan/phoenix_omega_worktrees/translate-hu-HU-b1-v2`, branch `agent/translate-hu-HU-b1_hook_story_reflection-100pct-v2`, HEAD `a03a80e6b10681e4b9716d0a0bb9857165558de8`, clean tracked status and contained in `origin/main`, but `git worktree remove` refused because untracked hu-HU atom locale files exist. HOLD; no force deletion.

Worktrees removed:
- `/Users/ahjan/phoenix_omega_worktrees/freebie-post-experience-capture-pr-update`

Worktrees held:
- `/Users/ahjan/phoenix_omega`: dirty root checkout on pruned branch.
- `/Users/ahjan/phoenix_omega_worktrees/mecha-native-proof-20260710`: open PR #5237 plus unresolved conflict/local value.
- `/Users/ahjan/phoenix_omega_worktrees/pr5623-frfr-overmatch-fix-20260715`: clean but not contained in `origin/main`; branch/head mismatch with merged PR #5623.
- `/Users/ahjan/phoenix_omega_worktrees/translate-hu-HU-b1-v2`: HEAD contained in `origin/main`, but untracked `atoms/corporate_managers/adhd_focus/.../hu-HU` locale files may be value; removal was not forced.
- Remaining worktrees from `git worktree list --porcelain`: HOLD pending per-worktree branch/PR mapping; resume classified 49 worktrees and found no further force-safe deletion candidate.

Branches:
- Deleted local branch `codex/freebie-post-experience-capture-pr`.
- Held root branch `codex/registry-40x14-waystream` because checkout is dirty and the remote was pruned.
- Held `codex/pr5623-frfr-overmatch-fix-20260715` because its HEAD is not contained in `origin/main`.
- Held `agent/translate-hu-HU-b1_hook_story_reflection-100pct-v2` because its worktree has untracked locale value.
- Held open-PR or unclassified worktree branches pending separate cleanup.

Remote branches:
- `codex/freebie-post-experience-capture-pr` already absent.
- Open PR, dirty, untracked-value, and unclassified branches held.

Scratch files:
- `/tmp/phoenix_old_chat_unblock_lane01_20260715` held as proof clone for unblock-wave PRs and handoffs.

Background jobs:
- none.

Tests and commands:
- `df -h / /Users /Users/ahjan/phoenix_omega`
- `git worktree list --porcelain`
- targeted `git status --short`, branch, HEAD, and PR checks for #5636, #5237, and #5623 candidates.
- 2026-07-15 resume classified worktrees with tracked status and `merge-base --is-ancestor HEAD origin/main`.
- `git worktree remove /Users/ahjan/phoenix_omega_worktrees/translate-hu-HU-b1-v2` refused due untracked files; no force deletion.
- `git worktree remove /Users/ahjan/phoenix_omega_worktrees/freebie-post-experience-capture-pr-update`
- `git worktree prune`
- `git branch -d codex/freebie-post-experience-capture-pr`

Blocker:
- Cleanup cannot safely continue without per-worktree PR/value mapping for the held branches, and local free space remains below the 50Gi no-new-worktree threshold. The one clean-contained resume candidate had untracked locale files, so deletion requires a value decision or preservation manifest for those files.

Next action:
- Run a dedicated preservation cleanup pass that first preserves or promotes the untracked hu-HU locale files, then remove only worktrees with clean tracked/untracked status and HEAD contained in `origin/main`.
