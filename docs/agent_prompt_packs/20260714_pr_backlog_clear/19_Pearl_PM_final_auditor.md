# Lane 19 — Final auditor + PROGRAM_STATE update (Wave 4)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_PM for Phoenix Omega, lane 19 (Wave 4, final) of the PR Backlog
Clear pack.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- LANE=pr-backlog-clear-final-audit
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud-agent
- PERSISTENCE_SURFACES=docs/PROGRAM_STATE.md, artifacts/coordination/ACTIVE_WORKSTREAMS.tsv, artifacts/coordination/handoffs/
- RESUME_SURFACE=artifacts/coordination/handoffs/pr-backlog-clear-final_2026-07-14.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/agent_brief.txt (Router v3 §5 CLOSEOUT discipline, §16 layer-honest reporting, v4 §26)
- docs/agent_prompt_packs/20260714_pr_backlog_clear/INDEX.md
- every handoff file this pack's lanes produced under artifacts/coordination/handoffs/

PRE-REQUISITE CHECKS:
- Lane 18's signal (stale-reconciliation-complete=<n>/<total>) must exist.
  If missing, STOP, BLOCKED — do not audit a pack that hasn't finished Wave 2.

LIVE STATE RECONCILIATION:
```bash
git fetch --prune origin
git switch main && git pull --ff-only origin main
gh api "search/issues?q=repo:Ahjan108/phoenix_omega_v4.8+is:pr+is:open&per_page=1" -q '.total_count'
```
This is the real number — not a copy of any earlier lane's claim. Compare
against the pack's opening count of 1,609.

DISCOVERY REPORT BEFORE ACTION:
- read every lane's CLOSEOUT_RECEIPT (from handoff files) and tabulate:
  merged count, closed-as-superseded count, escalated count, blocked count,
  per lane;
- re-derive the live open-PR count and confirm it matches
  (1,609 − merged − closed) within a small margin (new PRs may have opened
  from other CI runs during this program's execution — note any such drift,
  don't silently absorb it).

PROVENANCE:
- research: NONE
- documents: docs/PROGRAM_STATE.md (being updated), every lane handoff in this pack
- builds_on: the pack's own INDEX.md and 18 lane closeouts
- inventory: EXTENDS (PROGRAM_STATE.md gets a new dated section; nothing existing is removed)

MISSION:
- Produce the single source-of-truth closeout for the whole "PR Backlog Clear"
  program: total merged, total closed-as-superseded, total escalated (with
  Q-tags awaiting operator ratification), total genuinely blocked, and the
  final live open-PR count.
- Update docs/PROGRAM_STATE.md with a new dated section recording this
  program's result and the new "LAST VERIFIED @ origin/main <sha>" anchor.
- Update artifacts/coordination/ACTIVE_WORKSTREAMS.tsv: close out the row lane
  01 opened (status=complete, or status=blocked with the remaining scope named).

DELIVERABLES:
- Updated docs/PROGRAM_STATE.md.
- Updated artifacts/coordination/ACTIVE_WORKSTREAMS.tsv row.
- The full program closeout packet.

SMALLEST SAFE BATCH: n/a — single audit/write pass.

HANG PREVENTION:
- if any lane's handoff file is missing, do not stall waiting for it — report
  that lane as BLOCKED/incomplete in the final audit rather than blocking the
  whole audit indefinitely. Max window: 30 minutes.

TESTS/PROOFS:
- The live `gh api search/issues` re-count, verbatim.
- A reconciliation line showing: 1,609 (start) − merged − closed_as_superseded
  = expected remaining, vs. actual live remaining, with any delta explained.

DO NOT:
- do not claim "backlog cleared" or "100%" unless the live re-count actually
  shows it — label the result honestly on the acceptance taxonomy (a mostly-
  cleared backlog with N genuine escalations pending is "system working," not
  "PROVEN-AT-BAR" — that label doesn't really apply to git hygiene, but the
  discipline of not overclaiming does: don't round up);
- do not silently drop any lane's BLOCKED or ESCALATED items from the final
  report — every one must appear in the closeout;
- no local-only finish — PROGRAM_STATE.md and ACTIVE_WORKSTREAMS.tsv updates
  must be committed and pushed to main (small, low-risk coordination-file
  commits — direct commit is acceptable per Router v3 §0(b), same as lane 01).

LANDING CONTRACT:
- MERGED: PROGRAM_STATE.md and ACTIVE_WORKSTREAMS.tsv updates committed to
  main; full closeout packet produced.
- BLOCKED: if the live re-count can't be reconciled with lane reports (e.g.
  handoff files missing/contradictory), report BLOCKED with specifics rather
  than guessing at final numbers.

CLEANUP LEDGER REQUIRED:
- worktree: none-needed
- local branch: none-needed
- remote branch: none-needed
- scratch files: remove any /tmp aggregation files this lane created
- background jobs: none-needed
- held artifacts: none expected

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/pr-backlog-clear-final_2026-07-14.md — the
  program-level closeout, superset of all 18 lane handoffs' summaries.

CLOSEOUT_RECEIPT:
- AGENT=Pearl_PM
- LANE=pr-backlog-clear-final-audit
- STATUS=MERGED|BLOCKED
- OPEN_PR_COUNT_BEFORE=1609
- OPEN_PR_COUNT_AFTER=<live re-count>
- TOTAL_MERGED=<sum across all lanes>
- TOTAL_CLOSED_AS_SUPERSEDED=<sum>
- TOTAL_ESCALATED=<list of Q-tags>
- TOTAL_BLOCKED=<list of lane:reason>
- SIGNAL=pr-backlog-clear-final=<open-pr-count-after>
- PROOF_ROOT=<search/issues re-count output>
- TESTS=<reconciliation math shown>
- CLEANUP=<ledger above, filled in>
- HANDOFF=artifacts/coordination/handoffs/pr-backlog-clear-final_2026-07-14.md
- NEXT_ACTION=<if escalations remain: "operator ratifies Q-tags in operator_decisions_log.tsv"; else: "program complete">
```
