# 05 - Preservation-First Worktree Cleanup Handoff

STATUS=BLOCKED
SIGNAL: preservation-worktree-cleanup-terminal=blocked

Discovery:
- Free-space tier: low, `/System/Volumes/Data` has 12Gi available and 98% used.
- Root checkout: `/Users/ahjan/phoenix_omega`, branch `codex/registry-40x14-waystream`, HEAD `45eda6ddf049a874009643f5e48bda9b1ca4b1bb`, 263 status entries, remote branch pruned. HOLD.
- #5636 worktree: clean, merged, no local value remaining. Removed.
- pr5237 worktree: `/Users/ahjan/phoenix_omega_worktrees/mecha-native-proof-20260710`, branch `agent/pr5237-cloud-reconcile-20260710`, HEAD `321379f8f8efa5359b1a2af1ff6919cfc48011d4`, PR #5237 open, status includes an unresolved `UU` conflict and local additions/modifications. HOLD.
- #5623 candidate: `/Users/ahjan/phoenix_omega_worktrees/pr5623-frfr-overmatch-fix-20260715`, branch `codex/pr5623-frfr-overmatch-fix-20260715`, HEAD `6918f9800440c233c315c64811763afe313b2caf`, clean status but not an ancestor of current `origin/main` and branch does not match merged PR #5623 head. HOLD.

Worktrees removed:
- `/Users/ahjan/phoenix_omega_worktrees/freebie-post-experience-capture-pr-update`

Worktrees held:
- `/Users/ahjan/phoenix_omega`: dirty root checkout on pruned branch.
- `/Users/ahjan/phoenix_omega_worktrees/mecha-native-proof-20260710`: open PR #5237 plus unresolved conflict/local value.
- `/Users/ahjan/phoenix_omega_worktrees/pr5623-frfr-overmatch-fix-20260715`: clean but not contained in `origin/main`; branch/head mismatch with merged PR #5623.
- Remaining worktrees from `git worktree list --porcelain`: HOLD pending per-worktree branch/PR mapping; lane stopped after the required smoke/pilot checks and one proven safe removal.

Branches:
- Deleted local branch `codex/freebie-post-experience-capture-pr`.
- Held root branch `codex/registry-40x14-waystream` because checkout is dirty and the remote was pruned.
- Held `codex/pr5623-frfr-overmatch-fix-20260715` because its HEAD is not contained in `origin/main`.
- Held open-PR or unclassified worktree branches pending separate cleanup.

Remote branches:
- `codex/freebie-post-experience-capture-pr` already absent.
- Open PR branches held.

Scratch files:
- `/tmp/phoenix_old_chat_unblock_lane01_20260715` held as proof clone for unblock-wave PRs and handoffs.

Background jobs:
- none.

Tests and commands:
- `df -h / /Users /Users/ahjan/phoenix_omega`
- `git worktree list --porcelain`
- targeted `git status --short`, branch, HEAD, and PR checks for #5636, #5237, and #5623 candidates.
- `git worktree remove /Users/ahjan/phoenix_omega_worktrees/freebie-post-experience-capture-pr-update`
- `git worktree prune`
- `git branch -d codex/freebie-post-experience-capture-pr`

Blocker:
- Cleanup cannot safely continue in this dispatcher turn without per-worktree PR mapping for the held branches, and local free space remains below the 50Gi no-new-worktree threshold.

Next action:
- Run a dedicated preservation cleanup pass beginning with `git worktree list --porcelain`, then classify and remove only clean branches whose HEAD is contained in `origin/main` or whose merged PR head is proven identical.
