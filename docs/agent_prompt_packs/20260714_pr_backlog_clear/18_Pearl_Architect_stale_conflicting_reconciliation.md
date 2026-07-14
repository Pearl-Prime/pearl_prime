# Lane 18 — Stale / Conflicting PR reconciliation (Wave 2)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Architect for Phoenix Omega, lane 18 (Wave 2) of the PR Backlog
Clear pack. This lane runs AFTER every Wave 1 lane is terminal — it diffs old
PRs against a settled origin/main, not a moving target.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Architect
- LANE=stale-conflicting-reconciliation
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud-agent
- PERSISTENCE_SURFACES=~21 old PRs, artifacts/coordination/handoffs/, artifacts/coordination/operator_decisions_log.tsv
- RESUME_SURFACE=artifacts/coordination/handoffs/stale-conflicting-reconciliation_2026-07-14.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/agent_brief.txt (Router v3 §6 git-first drift recovery, §11 stale-prompt reconciliation, §16 layer-honest reporting)
- docs/agent_prompt_packs/20260714_pr_backlog_clear/INDEX.md
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- ~/.claude memory equivalents referenced inline below (read the actual current
  docs they point to, not just the memory summary)

PRE-REQUISITE CHECKS:
- Every Wave 1 lane's signal must exist and be MERGED or BLOCKED (not silent):
  catalog-merge-sweep-{02..14}-complete, enhancement-contract-v21-landed,
  mergeable-singles-sweep-complete. If any is missing, STOP — this lane's
  diffs are invalid against a still-moving main.

LIVE STATE RECONCILIATION:
- fetch origin/main; re-list the actual current set of old/conflicting PRs —
  do not assume the list below is complete or unchanged:
  `gh pr list --state open --json number,title,headRefName,mergeable,createdAt --search "-in:title catalog" | jq 'sort_by(.createdAt)'`
- Snapshot at authoring time (verify each is still open before acting):
  #1276, #1429, #1536, #1628, #1778, #1796 (`[PR-NOT-MERGE: review]`), #1812,
  #1874, #1878, #2792, #3097, #3166 (`[DO NOT MERGE until Jul 1 reset]` — today
  is 2026-07-14, past that date; re-check whether the budget-reset condition
  has actually been lifted before treating the hold as expired), #3533, #4573,
  #4643, #4723, #5206, #5237, #5295, #5518, #5596 (only if lane 16 did not
  already resolve it — check its signal first, do not double-handle).

DISCOVERY REPORT BEFORE ACTION, per PR:
- current origin/main SHA;
- for each PR: `git diff origin/main...<pr-branch> --stat` — if the diff is
  now EMPTY or trivial (content already landed via a different path — squash-
  merge redundancy per memory "Verify ahead-branch not stale"), this PR is
  ALREADY-SUPERSEDED, not a merge candidate;
- for each PR carrying an explicit hold marker in its title (#1796, #3166),
  read the PR body/thread for the hold's actual condition and confirm live
  whether that condition is now met — do not lift a hold on your own judgment
  if the condition is ambiguous; escalate instead;
- cross-reference known-good-anchor memory for each: e.g. #4573 (peak-
  requirements SSOT — memory says "EDIT IN PLACE; NOT on main — lives on OPEN
  #4573" — this may mean the PR is intentionally long-lived, not stale);
  #4643 (connective-tissue pilot — memory says "pilot #4643 + Cursor subtract
  spec" is still active); #5206/#5237/#5295/#5518 (all CONFLICTING per the
  live snapshot — check whether their conflicts are against files this pack's
  Wave 1 lanes just touched, or pre-existing drift).

PROVENANCE:
- research: NONE — this lane classifies, it does not author
- documents: each PR's own body + linked authority docs; docs/PROGRAM_STATE.md for current truth
- builds_on: n/a (reconciliation lane)
- inventory: UNCHANGED unless a PR is actually merged, in which case EXTENDS per that PR's own provenance

MISSION:
- Produce a verdict for every PR in the live old/conflicting set:
  - **MERGE** — rebase onto current main, resolve conflicts faithfully (never
    by discarding the side that fixed a bug), re-run its tests, merge.
  - **CLOSE-AS-SUPERSEDED** — diff is empty/redundant against main; close with
    a comment citing the SHA(s) that already deliver the same result.
  - **ESCALATE** — genuine operator-tier call (explicit hold marker whose
    condition is ambiguous, or a real unresolved product/scope conflict). Use
    Q-<TAG>-NN format with a recommended default; do NOT force either outcome.
- Never silently close a PR without a citation, and never force-merge a PR
  carrying an explicit human hold marker.

DELIVERABLES:
- A verdict table: PR#, title, verdict, evidence (SHA cited / conflict
  description / Q-tag).

SMALLEST SAFE BATCH:
- smoke: fully resolve ONE PR end-to-end (pick the oldest, #1276, as it has
  had the most time to go stale — likely a CLOSE-AS-SUPERSEDED or ESCALATE
  candidate) before touching the rest.
- pilot: resolve the next 4.
- scale: resolve the remainder, but STOP and escalate rather than rush any
  PR carrying an explicit hold marker or touching a frozen golden file.

HANG PREVENTION:
- checkpoint: after every 5 PRs resolved.
- no-progress rule: if a rebase conflict can't be resolved in one clean
  attempt, don't retry blindly — read both diffs fully once, then either
  resolve or escalate.
- hard stall rule: 3 PRs in a row needing escalation is not a failure of this
  lane — batch them into one escalation report rather than stalling on each individually.
- max window: 90 minutes.

TESTS/PROOFS:
- Each merged PR's own test suite green post-rebase.
- `git diff origin/main...<branch> --stat` captured per PR, before-and-after
  the reconciliation verdict, as the evidence trail.

DO NOT:
- do not force-close a PR carrying an explicit `[PR-NOT-MERGE]` or
  `[DO NOT MERGE]` marker without operator sign-off — that marker is itself
  an instruction from a prior session/operator, not staleness;
- do not force-merge over a real conflict by discarding either side;
- do not treat "old" as automatically "wrong" — some of these PRs are
  deliberately long-lived per project memory (#4573, #4643);
- no `--admin` merge, no `--no-verify`;
- no local-only finish.

LANDING CONTRACT:
- MERGED: every PR in the live set has a terminal verdict (merged, closed, or
  escalated-and-logged) — none left simply "open, unexamined."
- BLOCKED: name any PR whose verdict genuinely cannot be determined without
  operator input beyond a simple escalation (e.g. requires reading a private
  Slack thread not available here).

CLEANUP LEDGER REQUIRED:
- worktree: declare removed after each rebase, or HOLD with reason for any PR
  left mid-resolution for operator review.
- local branch: deleted after resolution.
- remote branch: deleted on merge; left open (not deleted) on close-as-superseded
  per GitHub's own close semantics — declare explicitly.
- scratch files: remove diff-capture files.
- background jobs: none expected.
- held artifacts: any PR left for operator escalation, declared by number.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/stale-conflicting-reconciliation_2026-07-14.md
  with the full verdict table and evidence links.
- Any ESCALATE verdicts also get a row in
  artifacts/coordination/operator_decisions_log.tsv per Router v3 §3.

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Architect
- LANE=stale-conflicting-reconciliation
- STATUS=MERGED|BLOCKED
- MERGED=<list of PR#:SHA>
- CLOSED_AS_SUPERSEDED=<list of PR#:citing-SHA>
- ESCALATED=<list of PR#:Q-tag>
- SIGNAL=stale-reconciliation-complete=<resolved>/<total in live set>
- PROOF_ROOT=<per-PR diff-stat evidence>
- TESTS=<CI results per merged PR>
- CLEANUP=<ledger above, filled in>
- HANDOFF=artifacts/coordination/handoffs/stale-conflicting-reconciliation_2026-07-14.md
- NEXT_ACTION=<report to Pearl_PM dispatcher; list any Q-tags awaiting operator ratification>
```
