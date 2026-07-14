# Lane 01 — Foundation & Triage (Wave 0)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_GitHub for Phoenix Omega, lane 01 (Wave 0) of the PR Backlog Clear pack.
This lane is read-only/registration-only — it gates every other lane in this pack.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=foundation-triage
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud-agent
- PERSISTENCE_SURFACES=artifacts/coordination/ACTIVE_WORKSTREAMS.tsv, artifacts/coordination/handoffs/
- RESUME_SURFACE=artifacts/coordination/handoffs/foundation-triage_2026-07-14.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/agent_brief.txt (Router Operating Principles v3 §1, §4, §10; v4 §20, §25)
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_prompt_packs/20260714_pr_backlog_clear/INDEX.md
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv

PRE-REQUISITE CHECKS: none — this is Wave 0, the first lane in the pack.

LIVE STATE RECONCILIATION:
```bash
git fetch --prune origin
git switch main && git pull --ff-only origin main
git rev-parse origin/main
gh api "search/issues?q=repo:Ahjan108/phoenix_omega_v4.8+is:pr+is:open&per_page=1" -q '.total_count'
gh pr list --state open --limit 100 --json number,title,createdAt,mergeable | jq length
```
Treat every count in INDEX.md as a 2026-07-14 snapshot — re-derive it live here
and report the delta. If the live open-PR count has changed materially from
1,609 (e.g. another session already merged a chunk), that is SUCCESS — narrow
the pack's remaining scope accordingly and say so, don't re-do finished work.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- live total open-PR count and live per-locale catalog-batch breakdown
  (re-run the per-locale `gh api search/issues?q=...+in:title+"catalog-<locale>-"`
  counts from INDEX.md's table and confirm/correct them);
- confirm no other running agent/workstream already owns "PR backlog clear" or
  any single locale's catalog merge sweep — grep
  `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for `catalog.merge` / `pr.backlog`;
- confirm disk/push-guard/governance health repo-wide is not currently red
  (a repo-wide CI outage would make every downstream merge lane pointless):
  `bash scripts/git/health_check.sh` (read-only check, do not fix anything found — report it).

PROVENANCE:
- research: NONE
- documents: docs/agent_brief.txt, docs/GITHUB_OPERATIONS_FRAMEWORK.md, docs/GITHUB_GOVERNANCE.md
- builds_on: existing ACTIVE_WORKSTREAMS.tsv registry
- inventory: EXTENDS (adds one new workstream row; changes nothing existing)

MISSION:
- Confirm it is safe to launch the 13 Wave 1 lanes (catalog merge sweeps ×11
  files covering 13 locale-scopes, the Enhancement Contract V2.1 chain, and the
  mergeable-substantive-singles sweep).
- Register ONE new row in artifacts/coordination/ACTIVE_WORKSTREAMS.tsv for
  "PR backlog clear" naming this pack's path, so no sibling session duplicates
  the work mid-flight.
- Emit the go/no-go signal every Wave 1 lane is gated on.

DELIVERABLES:
- Live-verified open-PR count (total + per-locale breakdown), diffed against
  the INDEX.md snapshot.
- One new row in artifacts/coordination/ACTIVE_WORKSTREAMS.tsv.
- The `foundation-triage-complete` signal.

SMALLEST SAFE BATCH: n/a (this lane is a single read+register pass, not a batch operation).

HANG PREVENTION:
- poll interval: n/a — this lane should complete in one pass, under 10 minutes.
- if `gh api search/issues` calls are rate-limited, back off and retry once;
  if still failing after 3 attempts, report BLOCKED with the API error, don't
  guess at counts.

TESTS/PROOFS:
- `gh api search/issues?q=repo:Ahjan108/phoenix_omega_v4.8+is:pr+is:open&per_page=1 -q '.total_count'` output, verbatim, in the closeout.
- `bash scripts/git/health_check.sh` output (or equivalent) attached as evidence.

DO NOT:
- do not merge or close any PR from this lane — it is triage/registration only;
- do not edit any file except artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;
- do not fabricate a "green" health check — if health_check.sh reports an
  issue, surface it as a BLOCKER for the whole pack, not just a note.

LANDING CONTRACT:
- MERGED: the ACTIVE_WORKSTREAMS.tsv row is committed directly to main (a
  one-line coordination-file append counts as a trivial, already-verified
  landing per Router Operating Principles v3 §0(b) — squash-commit it with a
  clear message, no PR ceremony required for a pure coordination-tracker append).
- BLOCKED: if repo health is red, or a sibling workstream already claims this
  scope, or the ACTIVE_WORKSTREAMS.tsv write itself conflicts — report BLOCKED
  and do NOT let the dispatcher launch Wave 1.

CLEANUP LEDGER REQUIRED:
- worktree: none-needed
- local branch: none-needed
- remote branch: none-needed
- scratch files: remove any /tmp PR-list dumps this lane created
- background jobs: none-needed
- held artifacts: none

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/foundation-triage_2026-07-14.md containing:
  live open-PR count, per-locale breakdown table, health-check output, the
  ACTIVE_WORKSTREAMS.tsv row added, and the go/no-go verdict.

CLOSEOUT_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=foundation-triage
- STATUS=MERGED|BLOCKED
- SIGNAL=foundation-triage-complete=<live open PR count>,<GO|NO-GO>
- PROOF_ROOT=<search/issues output>, <health_check.sh output>
- TESTS=<commands run above>
- CLEANUP=none-needed (read/registration-only lane)
- HANDOFF=artifacts/coordination/handoffs/foundation-triage_2026-07-14.md
- NEXT_ACTION=<if GO: "launch lanes 02-14,16,17 in parallel"; if NO-GO: name the exact blocker>
```
