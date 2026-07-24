# 03 — Lane C (Pearl_Architect) — Phase B History-Rewrite Decision Packet (author, do NOT execute)

```text
EXECUTE the PACKET. Do NOT execute the history rewrite. End with a delivered decision
packet + an explicit operator go/no-go gate — that PENDING gate IS the correct terminal
state for this lane. You are Pearl_Architect for Phoenix Omega.

WHAT THIS LANE IS: the LFS→R2 offload was FORWARD-ONLY — it stopped NEW commits from
LFS-tracking moved families, but every offloaded blob STILL LIVES IN GIT HISTORY. The repo
was measured at ~76 GB / ~994k files (prior session handoff). The only lever that reclaims
that historical weight is a history rewrite (`git lfs migrate import --everything` + GC +
force-push) — docs/GIT_LFS_MIGRATION_PLAN.md §Phase B. That is the sole open item in
ws_lfs_setup_20260410, it is OWNER-GATED, and it has NEVER been turned into a decision the
operator can actually rule on. Your job is to author that decision packet: the honest
cost/benefit, blast radius, prerequisites, rollback, and a recommendation. NOT to run it.

WHAT THIS LANE IS NOT: you do NOT run `git lfs migrate`, BFG, filter-repo, `git gc
--aggressive`, or ANY force-push. You do NOT modify .git. Phase B execution is a separate,
owner-scheduled maintenance window that only fires on the operator's explicit written GO.

Repo: Ahjan108/phoenix_omega_v4.8. Branch from origin/main: agent/phase-b-decision-packet-20260724.
DEPENDS ON: Lanes A + B MERGED — so your "current state" section cites a reconciled,
continuously-verified R2 baseline (the packet's whole risk model assumes the R2 copies are
provably retrievable; that's what Lane B establishes). If A/B aren't merged, note it and
author against best-available state, flagging the dependency.

STARTUP_RECEIPT:
- AGENT=Pearl_Architect
- LANE=phase-b-history-rewrite-decision-packet
- EXECUTION_MODE=github_actions (the PACKET lands as a reviewed docs PR; the REWRITE does not run)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=fresh worktree/clone of origin/main (read-only measurement; NO .git surgery)
- RESUME_SURFACE=artifacts/coordination/handoffs/phase-b-decision-packet_2026-07-24.md

READ FIRST:
- docs/GIT_LFS_MIGRATION_PLAN.md §Phase B (lines ~108-134) and §Phase C worktree cleanup — the
  existing sketch you are turning into a ratifiable packet.
- docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md §0/§Q-LFS-05 — "FORWARD-ONLY; history rewrite =
  operator-ratification only". Your packet is that ratification instrument.
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv → ws_lfs_setup_20260410 ("Phase B still owner-gated").
- CLAUDE.md "Non-Negotiable Git Rules" 0 + AGENT_FILE_PERSISTENCE_PROTOCOL — the deletion-scale
  discipline; a history rewrite is the single most destructive git op in this repo's playbook.
- Memory: [[project_worktree_disk_constraint]] (~3.2GB/agent LFS, GIT_LFS_SKIP_SMUDGE=1),
  [[feedback_workflow_worktree_lfs_smudge]] — the rewrite changes LFS pointers repo-wide, so
  EVERY worktree/checkout/CI-clone the team runs is affected. That blast radius is your §"impact".
- The manga agent's stated interface (from the operator's handoff to you): (1) preserve the
  check_render_progress_bytes.py R2-offload byte-verify contract; (2) Phase B "affects every
  checkout and worktree — I'd want a heads-up before it fires." Both are packet inputs.

LIVE MEASUREMENT (read-only — this is where your numbers come from; do NOT trust the ~76GB
snapshot, re-measure):
- Repo pack/history size: `git count-objects -vH` (size-pack, size), and the .git dir size.
- What a rewrite would actually reclaim: `git lfs migrate info --everything --include="<the
  Phase B extension list>"` is a DRY-RUN INFO command (read-only, safe) — run it to get the real
  per-type reclaimable bytes. This is the benefit number. (info only — NOT `migrate import`.)
- Open PR count (a Phase B prerequisite is "all open PRs merged/closed"):
  `gh pr list --state open` — how many, and are any long-lived? This gates when a window is even
  possible.
- Active worktrees / collaborators who'd need to re-clone: `git worktree list`; enumerate the
  known agent worktrees + CI clones from the coordination docs. Each is a re-clone cost.

DISCOVERY REPORT BEFORE ACTION: the measured repo size, the dry-run reclaimable bytes by type,
the open-PR count, the worktree/CI-clone inventory, and the R2-baseline status from Lanes A/B.

PROVENANCE:
- research: read the git-lfs migrate + force-with-lease semantics from the tool's own docs (cite);
  do NOT invent behavior. documents: GIT_LFS_MIGRATION_PLAN.md §Phase B; spec §0.
- builds_on: the Phase A forward-tracking + the landed R2 offload (the rewrite is the "reclaim"
  half of the plan whose "stop-the-bleeding" half already shipped).
- inventory: CREATES one new decision packet doc + one ADR; changes NO history, NO code.

MISSION — author docs/decisions/PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md containing:
1. **Decision asked** — one sentence: "Do we execute the LFS history rewrite (reclaim ~<X>GB) in
   a scheduled maintenance window, accepting a force-push to main + mandatory re-clone for all
   collaborators and CI?" with a clear recommended answer + confidence.
2. **Benefit (measured)** — reclaimable bytes by file type from the dry-run; repo-size before/
   projected-after; concrete effects (clone time, Codespace spin-up, worktree disk per agent,
   Cursor/indexer load — tie back to the original 76GB/994k-file pain that started this program).
3. **Cost / blast radius** — force-push to a PROTECTED main (the ruleset "Protect main" is LIVE,
   [[project_main_branch_protection_live]] — the rewrite requires temporarily lifting protection,
   a privileged owner action; document that dependency); every collaborator + every agent worktree
   + every CI clone must re-clone (enumerate from discovery); the window during which no one may
   push; the irreversibility of a botched force-push.
4. **Prerequisites checklist** — all open PRs merged/closed (cite live count); `.git.backup`
   taken; R2 copies proven retrievable (Lane B green — this is WHY C depends on B: you must not
   rewrite away history-of-record for blobs you can't re-fetch); collaborators + concurrent agent
   sessions notified with a scheduled UTC window; branch-protection lift plan + re-enable plan.
5. **Execution runbook (for the owner window, NOT run now)** — the exact command sequence from
   §Phase B, each with its safety rail (dry-run before import, --force-with-lease not --force,
   verify LFS pointers + a sample blob fetch post-rewrite, re-enable protection). Mark the whole
   block "DO NOT RUN outside an owner-approved window."
6. **Rollback** — restore from `.git.backup`; the "if force-push corrupts main" recovery; the
   fact that once collaborators re-clone the rewritten history, rollback cost rises sharply
   (name the point of no return).
7. **Recommendation + go/no-go gate** — your Architect recommendation (GO now / GO after N open
   PRs drain / DEFER — with the trigger condition), and an explicit "OPERATOR DECISION: __" field
   left blank for the operator to fill. Also write an ADR
   docs/decisions/ADR-<n>-lfs-history-rewrite.md summarizing the decision + status PROPOSED.

LAYER-HONEST FRAMING: label the packet's status. Delivering the packet = "decision-packet-
delivered". Operator ruling = the acceptance event. Do NOT describe Phase B as "ready to ship"
or "done" — it is a PROPOSED decision awaiting ratification. A gate PASS on your docs PR is not
Phase-B-approved.

DO NOT:
- Do NOT run `git lfs migrate import`, filter-repo, BFG, `git gc --aggressive`, or any force-push.
- Do NOT lift branch protection (owner-only, and only in the window).
- Do NOT modify .git or any history. Read-only measurement only (`migrate info` is read-only; do
  not "accidentally" run `import`).
- Do NOT recommend GO without the measured benefit + a drained-or-scheduled path for open PRs +
  Lane B green. A history rewrite recommended on vibes is malpractice for this repo (PR #245
  precedent: irreversible mass git ops cost hundreds of hours).
- Do NOT touch manga content; preserve the byte-gate R2 contract in your impact analysis.

LANDING CONTRACT:
- MERGED: the decision packet + ADR land as a reviewed docs PR (governance green, named). The
  Phase B EXECUTION remains PENDING operator ruling — that is the intended terminal state.
- BLOCKED: if you cannot get the measurement numbers (e.g. dry-run fails) or Lanes A/B aren't
  merged and that materially blocks an honest packet — say so, push the partial to remote.

CLEANUP LEDGER: read-only worktree removed post-merge; local + remote branch deleted after merge;
NO .git.backup created by you (that's a step in the owner window, not this lane); no background jobs.

HANDOFF: artifacts/coordination/handoffs/phase-b-decision-packet_2026-07-24.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Architect
- LANE: phase-b-history-rewrite-decision-packet
- STATUS=MERGED|BLOCKED   (MERGED = packet delivered; Phase B execution intentionally NOT done)
- BRANCH: agent/phase-b-decision-packet-20260724
- PR: / MERGE_SHA:
- SIGNAL: phase-b-decision-packet=<merge-sha>
- ACCEPTANCE_LAYER: decision-packet-delivered (operator go/no-go PENDING = correct end-state)
- PACKET: docs/decisions/PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md + ADR
- MEASURED: <repo size; dry-run reclaimable GB; open-PR count; worktree/clone inventory>
- RECOMMENDATION: <GO / GO-after-<trigger> / DEFER-until-<trigger>>
- CLEANUP: <ledger>
- HANDOFF: artifacts/coordination/handoffs/phase-b-decision-packet_2026-07-24.md
- NEXT_ACTION: "Operator rules GO/NO-GO on the packet; on GO, a separate owner-window lane
  executes Phase B — that lane is NOT authored here (it fires only on written approval)"
```
