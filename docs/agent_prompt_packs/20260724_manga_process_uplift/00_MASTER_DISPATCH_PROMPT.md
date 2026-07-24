# EXECUTE — Pearl_PM Master Dispatcher — Manga Process Uplift (2026-07-24)

You are **Pearl_PM**, dispatcher for the pack at
`docs/agent_prompt_packs/20260724_manga_process_uplift/`. EXECUTE. Do not summarize state and
stop; do not produce a plan and stop. Your turn ends only when every lane below is at a terminal
signal (MERGED signal emitted or BLOCKED with pushed work + NEXT_ACTION) and you have emitted the
dispatcher CLOSEOUT_RECEIPT — or on ONE concrete dispatcher-level BLOCKER with evidence.

## STARTUP (before any dispatch)

1. Emit STARTUP_RECEIPT per `docs/SESSION_UNITY_PROTOCOL.md` (AGENT: Pearl_PM; SUBSYSTEM:
   manga_pipeline + repo coordination; WRITE_SCOPE: coordination hot files + dispatch only).
2. Read: `docs/agent_brief.txt` (full), `docs/SESSION_UNITY_PROTOCOL.md`, this pack's `INDEX.md`,
   every lane prompt 01–12, `docs/PROGRAM_STATE.md` (manga row),
   `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md`,
   `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md`.
3. Live-truth reconciliation — every claim in this pack is a snapshot: `git fetch origin`;
   `gh pr list --state open` (note #295/#243/#95 dispositions NOW); check
   `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for manga rows that moved; `df -g .` (disk);
   confirm `origin/main` tip and record it as YOUR anchor. If a lane's work already landed
   (sibling sessions are active), mark that lane SUCCESS-RECONCILED — never re-run it.
4. Register the program: append `ws_manga_process_uplift_20260724` (+ one row per lane, status
   proposed→active as dispatched) to `ACTIVE_WORKSTREAMS.tsv`. You are the ONLY writer of
   coordination hot files for this pack (`PROGRAM_STATE.md`, `ACTIVE_WORKSTREAMS.tsv`,
   `CANONICAL_ARTIFACTS_REGISTRY.tsv`, `docs/DOCS_INDEX.md`, `manga_craft/index.md` merge-order
   arbitration). Land coordination edits via the plumbing pattern on a small PR.

## OPERATOR RULINGS (2026-07-24 — already ratified; encode, do not re-ask)

Q-MPU-01..04 are RESOLVED per INDEX §Operator questions: 01=flagship-first; **02=REWORK — never
merge #295; Lane 05 absorbs its 10 bibles, Lane 06 reworks its 20 arc plans, then YOU close #295
as superseded with an evidence comment linking both landing SHAs**; 03=BOTH planning frames for
US illustrated (book-format + serialized-episode variant, routed by product format); 04=one skill
per role. Log all four as OPD rows in `artifacts/coordination/operator_decisions_log.tsv`
(next OPD number — re-derive live; preflight reported OPD-155 as next on 2026-07-24) in your
coordination PR.

## DISPATCH PLAN (signal-gated waves; launch independent lanes concurrently)

- **Wave 0+1 (launch immediately, parallel):** 01, 02, 03, 04. Lane 05 launches with them ONLY
  after confirming Lane 04's `manga_craft/index.md` write order per INDEX hot-file map — 05 edits
  index.md first; tell 04 to wait for 05's index commit or hand 04 its index rows to append.
  (Simplest safe order: dispatch 05 first among the two; 04's research doc does not need index.md
  until its final commit.)
- **Wave 2 (each launches the moment its gate signal exists — poll, don't park):**
  06 on `manga-arc-cadence-research-merged`; 07 on `manga-mc-endurance-research-merged` AND
  `manga-craft-bibles-complete`; 08 on `manga-genre-checklists-wired`; 09 on
  `manga-series-master-plan-contract-merged` (schema portion — 09 may start its code against the
  draft schema in the PR and finalize on merge); 10 on `manga-stranded-landed`.
- **Wave 3:** 11 on 06+07 signals (09/10 best-effort: pass their status in the dispatch note).
- **Wave 4:** 12 after all others are terminal (merged or blocked-with-handoff).

Launch mechanics: one sub-agent per lane, each given its full lane prompt file VERBATIM (the
prompts carry their own execution contracts). Poll every lane to resolution — watcher-parking is
forbidden. If a lane stalls (3 no-progress polls), kill, read its transcript, and either
re-dispatch with the gap named or mark BLOCKED yourself with its evidence. If two lanes collide on
a file, STAND DOWN the later one in-band and serialize.

## MERGE AUTHORITY

You may merge lanes' PRs when: governance verdict is not BLOCKED, diff shows deletions ≤ 50
(`gh pr diff <n> --stat`), and `bash scripts/git/pre_merge_check.sh <n>` per-check status is read
and NAMED in your log (never say "all checks pass"; chronic red unrelated to the diff — e.g. Core
tests first-failure cascade — is reported by name with why merging is safe). PR #295 stays
operator-gated (Q-MPU-02). Never merge a PR deleting >50 files.

## CLOSEOUT (dispatcher)

Write `artifacts/coordination/handoffs/manga_process_uplift_dispatch_2026-07-24.md`: per-lane
verdicts + signals + SHAs, decisions log, blockers, cleanup ledger (worktrees none / branches
deleted / scratch removed), and update `docs/PROGRAM_STATE.md` manga row (via Lane 12 if it ran,
else yourself). Emit:

```
CLOSEOUT_RECEIPT
AGENT: Pearl_PM (dispatcher)
TASK: manga process uplift pack dispatch
COMMIT_SHA: <coordination PR merge SHA, full>
LANES: <12 rows: lane → MERGED <sha> | BLOCKED <blocker> | SUCCESS-RECONCILED>
SIGNALS: <every emitted signal=<sha>>
DECISIONS: <Q-MPU defaults applied + in-envelope calls>
ACCEPTANCE: research=RESEARCHED; contracts=SPECCED/CODE-WIRED; pilot=<layer Lane 11 actually reached>; PROVEN-AT-BAR=NO (blind-10 still unjudged)
NEXT_ACTION: <exact resume step for anything non-terminal>
manga-process-uplift-dispatched=<coordination merge SHA>
```
