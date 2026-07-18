# origin/main Force-Push Rewind Incident — 2026-05-06

**P0 incident.** Origin/main was force-pushed by `Ahjan108` at `2026-05-05T21:57:36Z`, replacing the post-finish-out tip `3bf8937eb9` (PR #888) with `3c346c5466` (a teacher-showcase commit that did not contain `3bf8937eb9` in its history). The 14 commits of the 2026-05-04 → 2026-05-05 finish-out merge train were orphaned from origin/main.

**The lost commits are NOT lost** — every squash-merge SHA is preserved as a git object and reachable from still-open PR branches (#889, #891, #892, #893). Recovery is feasible.

---

## 1. Timeline (from local reflog + GitHub events API)

| Time (UTC) | origin/main tip | Source | Notes |
|---|---|---|---|
| 2026-05-05T14:10:00Z | `304f0c233e` | gh pr merge #884 squash | Pearl_Architect routing batch |
| 2026-05-05T14:40:34Z | `87a66af6c3` | gh pr merge #881 squash | Pearl_PM coordination |
| 2026-05-05T14:40:45Z | `6af1d0d456` | gh pr merge #875 squash | audit-handoff persistence |
| 2026-05-05T14:41:05Z | `2df0ebd98e` | gh pr merge #876 squash | Pearl Star handoff persistence |
| 2026-05-05T14:41:18Z | `fb6815201c` | gh pr merge #877 squash | PR-D handoff persistence |
| 2026-05-05T14:41:48Z | `13441bbc80` | gh pr merge #885 squash | brand-1 atomic |
| 2026-05-05T14:51:42Z | `0142d88337` | gh pr merge #886 squash | PR-D residual wiring |
| 2026-05-05T15:11:01Z | `cd56856d65` | gh pr merge #887 squash | atom backfill |
| 2026-05-05T15:16:19Z | `3bf8937eb9` | gh pr merge #888 squash | DOCS_INDEX MASTER-CATALOG-01 (last good) |
| **2026-05-05T21:57:36Z** | **`3c346c5466`** | **`Ahjan108` push** | **REWIND EVENT** — non-fast-forward; head does not contain `3bf8937eb9` in history |
| 2026-05-05T22:01:36Z | `53e6ed782d` | `Ahjan108` push (FF) | teacher-showcase subtitle |
| 2026-05-05T22:06:33Z | `cac08f252e` | `Ahjan108` push (FF) | teacher-showcase manga portraits |
| 2026-05-05T22:18:39Z | `569a8ae413` | `Ahjan108` push (FF) | current tip |

The 2026-05-05T21:57:36Z push is the rewind. Verified non-fast-forward by `git merge-base --is-ancestor 3bf8937eb908 3c346c5466a2` returning non-zero (= not an ancestor).

GitHub events API reports `forced=None` for all pushes (the API doesn't reliably populate this field), but the SHA-ancestry test is definitive.

## 2. The rewind event

| Field | Value |
|---|---|
| Actor | `Ahjan108` (repo owner) |
| Timestamp | 2026-05-05T21:57:36Z |
| Before | `3bf8937eb908` (post-#888) |
| After | `3c346c5466a2` (teacher-showcase initials commit, built on `cfcace6983` = pre-finish-out base) |
| Mechanism | `git push` to main; non-fast-forward |
| Bypass | `current_user_can_bypass: always` on ruleset 13451138; `actor_id: 5` (admin role) bypassed `non_fast_forward` + `required_linear_history` rules |

The post-rewind chain has accumulated:
- ~30 `chore(backup): auto backup …` commits between 2026-05-05 and 2026-05-06 (running every ~hour; built on `cfcace6983` not the merge train)
- 5 `feat(teacher-showcase): …` commits (legitimate operator work)

The `chore(backup)` chain appears to be an automated process that was building a parallel "snapshot" history. It originated from a working tree that did NOT have the merge train applied — likely because the auto-backup process and the gh-pr-merge process were running in different environments. When that auto-backup process pushed to main at 21:57:36Z, it overwrote the merge train.

## 3. Lost commits (orphaned from origin/main; reachable elsewhere)

| PR | SHA | Type | In origin/main today? | Reachable from |
|---|---|---|---|---|
| #874 | `38af30e9e5` | doc | NO | #885+#886+#887+#889+#891+#892+#893 + 4 more branches |
| #850 | `4b198508ce` | doc/code | NO | (same set) |
| #853 | `8070e81fd8` | code | NO | (same set) |
| #855 | `3aaadadb14` | code | NO | (same set) |
| #858 | `f052d38d5e` | code | NO | (same set) |
| #884 | `304f0c233e` | doc | NO | (same set) |
| #881 | `87a66af6c3` | coord | NO | #889+#891+#892+#893 |
| #875 | `6af1d0d456` | doc | NO | #889+#891+#892+#893 |
| #876 | `2df0ebd98e` | doc | NO | #889+#891+#892+#893 |
| #877 | `fb6815201c` | doc | NO | #889+#891+#892+#893 |
| #885 | `13441bbc80` | code | NO | #889+#891+#892+#893 |
| #886 | `0142d88337` | code | NO | #889+#891+#892+#893 |
| #887 | `cd56856d65` | code | NO | #889+#891+#892+#893 |
| #888 | `3bf8937eb9` | doc | NO | #889+#891+#892+#893 |

All 14 commits exist in the GitHub object store and can be re-attached to origin/main via force-push. The fully-loaded post-#888 tip (`3bf8937eb9`) is preserved as the ancestry of `agent/pearl-pm-finalization-20260505` (PR #889).

## 4. Recoverable PRs vs needs-recreation

| Status | Count | PRs | Mechanism |
|---|---|---|---|
| Source branch still on remote | 2 | #874 (`docs/session-handoff-2026-05-04`), #881 (`agent/pm-coordination-bookkeeping-20260504`) | Could re-merge via `gh pr create` from same head ref + squash-merge |
| Source branch deleted (`--delete-branch` on close) | 8 | #875, #876, #877, #884, #885, #886, #887, #888, #850, #853, #855, #858 | Re-merge requires recreating the branch from the orphaned mergeCommit's parents, OR cherry-picking the squash diff |
| MERGED state on GitHub but not in main | all 14 | n/a | `gh pr merge` refuses to merge already-MERGED PRs; this is a known limitation |

`gh pr merge` is not viable for re-merge. The two viable mechanisms are:
1. `git push --force-with-lease` to main (Path 2 of receipt) — restores the lost merge train atomically.
2. Cherry-pick each squash diff onto current main (Path 3 of receipt) — high-effort; loses original SHAs.

## 5. Force-push consequence (CLAUDE.md rule violation)

Per `CLAUDE.md`'s git rules: "Never force-push to main." The actor here is the repo owner with explicit bypass authority — technically not a rule violation in the agent-policy sense, but a P0 incident in the spirit of the rule. The `audit handoff §3.7` from 2026-05-04 named this exact scenario as the P0 finding: "main is unprotected" (now refined to: "main has a ruleset, but the owner has unconditional bypass; the ruleset doesn't deny operator-initiated force-pushes").

**Branch protection should have prevented this.** Concrete options for hardening:
- Remove `current_user_can_bypass: always` from ruleset 13451138.
- Remove `actor_id: 5` (RepositoryRole admin) from `bypass_actors`.
- Add `non_fast_forward` rule with no bypass exemption.
- Require the auto-backup process to push to a non-main branch (`refs/auto-backup/*`) instead of main.

Tracked as `ws_main_branch_protection_restore_20260505` (Pearl_DevOps, blocked-on-operator-go) per Pearl_PM 2026-05-04 finalization closeout — **upgraded to P0 immediate** by this incident.

## 6. Recovery path analysis

### Path 1 — `gh pr merge` re-merge (NOT FEASIBLE)
`gh pr merge` refuses to act on PRs in `MERGED` state. To use this path we'd have to:
- Reopen each PR (`gh pr reopen`) — 14 reopenings
- Recreate 8 deleted branches from orphaned mergeCommit parents
- Re-run gh pr merge on each
Effort: very high. Risk: low. End state: equivalent to Path 2.

### Path 2 — force-restore main (FEASIBLE; RECOMMENDED)
Construct a recovery branch:
```
git checkout -b recovery/post-rewind 3bf8937eb9
git cherry-pick 3c346c5466..569a8ae413  # the 5 teacher-showcase commits
# (the chore(backup) commits between the rewind and the teacher-showcase
# work are NOT cherry-picked — they're stale pre-merge-train snapshots
# whose entire purpose was to mirror main's state, and that mirror is
# already correct in 3bf8937eb9)
git log recovery/post-rewind --oneline | head -20  # verify train + 5 ts commits
git push --force-with-lease=origin/main:origin/main recovery/post-rewind:main
```

**Effort:** ~10 minutes, single force-push. **Risk:** medium — force-push to main needs separate explicit authorization.

**End state:** origin/main = 14 squash merges (rest of finish-out block) + 5 teacher-showcase commits, in correct chronological order. Auto-backup chain discarded (it was stale).

**Caveat:** the auto-backup process must be **stopped before recovery completes**, or it will push again and undo the recovery. Operator action required: identify and stop the cron / launchd / agent that emits `chore(backup): auto backup …` to main.

### Path 3 — cherry-pick onto current main (HIGHER COST; LOWER RISK)
Reapply each of the 14 squash diffs onto `569a8ae413` (current main):
```
for sha in 38af30e9e5 4b198508ce 8070e81fd8 3aaadadb14 f052d38d5e \
           304f0c233e 87a66af6c3 6af1d0d456 2df0ebd98e fb6815201c \
           13441bbc80 0142d88337 cd56856d65 3bf8937eb9; do
  git cherry-pick $sha
done
```

**Effort:** ~30-60 minutes (cherry-picks may have conflicts; each needs manual review). **Risk:** medium-low (no force-push). **End state:** origin/main has the teacher-showcase work + new commits with the merge-train content (different SHAs). Original SHAs become historical-only. Test results from prior PRs may need re-verification on the new state.

## 7. Recommendation

**Path 2 — force-restore main** is the cleanest recovery. Preserves original SHAs, preserves the 5 teacher-showcase commits, discards only the stale auto-backup chain. Single force-push. Operator must authorize the force-push separately (doubly-gated per receipt) AND must stop the auto-backup process before pushing.

If Path 2 isn't acceptable (operator declines force-push), Path 3 is the fallback. Path 1 is not feasible.

**Pre-recovery checklist:**
1. Operator confirms Path 2 is the chosen path.
2. Operator authorizes the force-push (`FORCE-PUSH-AUTHORIZED` in chat).
3. Operator confirms the auto-backup process has been stopped (or names the process so Pearl_GitHub can stop it).
4. Operator confirms intent to harden the ruleset post-recovery (or schedules `ws_main_branch_protection_restore_20260505` upgrade as a separate Pearl_DevOps follow-up — but the rewind WILL repeat without hardening).

---

*Pearl_GitHub diagnostic phase complete. Awaiting operator authorization on recovery path.*
