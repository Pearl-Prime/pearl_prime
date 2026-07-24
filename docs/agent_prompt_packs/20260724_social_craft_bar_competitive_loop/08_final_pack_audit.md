# Lane 08 — Final Pack Audit + SSOT / Coordination Rows (SERIAL hot-file owner)

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_PM for Phoenix Omega. You are the ONLY writer of coordination hot files in this pack.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-craft-pack-audit-20260724). Explicit-path staging; poison protocol.

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- LANE=social_craft_pack_audit_20260724
- EXECUTION_MODE=local_fallback ; BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=branch/PR/SSOT
- RESUME_SURFACE=artifacts/coordination/handoffs/social_craft_pack_audit_2026-07-24.md

READ FIRST:
- docs/PEARL_PM_STATE.md ; docs/SESSION_UNITY_PROTOCOL.md
- every lane handoff under artifacts/coordination/handoffs/social_*_2026-07-24.md
- docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md
- docs/PROGRAM_STATE.md §Social Media Atom Bank

PRE-REQUISITE CHECK: every other lane (01–07) is TERMINAL — MERGED or BLOCKED with handoff. Verify
each signal token by grepping merged PR bodies / handoffs, never by trusting the dispatcher's
table. A lane neither merged nor blocked-with-handoff = this lane is BLOCKED on it.

DISCOVERY REPORT before action: signal-token verification table (token → surface found → full SHA);
any lane deltas vs the pack's claims.

PROVENANCE:
- research: n/a (coordination)
- documents: SESSION_UNITY §Handoff Protocol; agent_brief §5/§17
- builds_on: PROGRAM_STATE §Social Media Atom Bank row (EDIT IN PLACE); ACTIVE_WORKSTREAMS registry
- inventory: EXTENDS

MISSION (narrow):
1. **Audit:** verify every lane's landing contract was honored — merged SHAs real (`git log
   origin/main --grep`), proof roots exist and parse, cleanup ledgers complete (no stray branches:
   `git branch -r | grep social-`), no local-only value left (verify each lane's worktree/branch
   actually gone).
2. **PROGRAM_STATE.md §Social Media Atom Bank:** update Status/Details with what ACTUALLY landed
   (craft gate live? variety repair landed? recurrence wired + fired? flags flipped or
   BLOCKED-with-quote? blind packet ready/read? competitive spec landed at which status?). Every
   claim carries its acceptance layer + full SHA. Fix the pre-existing stale bits this pack
   obsoleted (e.g. "pending PR #75 merge" phrasing — #75 is MERGED; "zero recurring mechanism" if
   Lane 06 landed).
3. **ACTIVE_PROJECTS.tsv + ACTIVE_WORKSTREAMS.tsv:** add the missing project row for the social
   subsystem (it has NONE today — a verified gap) + one row per executed lane with terminal status.
4. **operator_decisions_log.tsv:** record the batch ratification outcomes
   (Q-SOCIAL-COMPETITIVE-INTEL-01, Q-SOCIAL-BLIND10-READ-01) as relayed by the dispatcher — quote
   the operator's actual words; if a question is still unanswered, log OPEN, do not fabricate.
5. **Memory-promotion check (agent_brief §14):** confirm each drift-class this pack fixed now has
   an enforced mechanism (craft gate in readiness gates; recurrence in cron; golden freeze live).
   Name any lesson still living only in prose — that is a finding, not a footnote.
6. One serial PR for all coordination edits.

DELIVERABLES: audit table in the handoff; the coordination PR; final pack status block appended to
the pack's INDEX.md (§Final Status updated in the same PR).

SMALLEST SAFE BATCH: n/a (audit lane) — but stage the coordination edits file-by-file with
`git diff --cached --stat origin/main` verification (these are THE hot files; poison protocol is
mandatory, one more time, here of all places).

HANG PREVENTION: standard 2/3 polling on CI; max window 2 h.

TESTS/PROOFS: TSV parse checks (python3 -c csv sniff) on every edited TSV; docs-only CI green.

DO NOT: paper over a BLOCKED lane as done; re-litigate lane decisions; edit anything outside the
coordination surfaces + INDEX.md; let a false premise survive in PROGRAM_STATE (the
router-was-wrong corollary: correct the SOURCE).

LANDING CONTRACT: MERGED or BLOCKED.

CLEANUP LEDGER + HANDOFF: artifacts/coordination/handoffs/social_craft_pack_audit_2026-07-24.md

CLOSEOUT_RECEIPT: standard fields + full MERGE_SHA + the signal-verification table.
SIGNAL: social-craft-pack-audit-complete=<full merge SHA>
ACCEPTANCE LAYER: coordination truth only — this lane makes no quality claims of its own.
~~~
