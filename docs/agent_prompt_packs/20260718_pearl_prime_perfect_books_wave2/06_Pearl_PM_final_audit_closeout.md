# 06 — Final Wave: Audit + Coordination Closeout (Pearl_PM)

EXECUTE. Last lane; ONLY writer of hot coordination files. Turn ends only on the
signal below or one concrete BLOCKER with evidence.

GATE CHECK (all greppable, from lane handoffs + dispatcher ledger):
`perfect-books-wave2-substrate`, `perfect-books-wave1-preserved`, and a terminal
signal (or recorded BLOCKED) for lanes 02, 03, 04, 05. Any non-terminal ⇒ STOP,
return to dispatcher.

```
STARTUP_RECEIPT
AGENT: Pearl_PM (lane 06)
TASK: Verify every lane's landing, check the spec §8 "Done when" boxes honestly, update coordination + PROGRAM_STATE, open the operator packets
SUBSYSTEM: pearl_pm coordination (hot files: sole writer)
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/agent_brief.txt §16–§18; PEARL_PRIME_PERFECT_BOOKS_SPEC.md §8; this pack's INDEX.md; every lane handoff
WRITE_SCOPE: artifacts/coordination/operator_decisions_log.tsv; ACTIVE_WORKSTREAMS.tsv (this pack's rows); docs/PROGRAM_STATE.md (offline-pending note only — offline ≠ on-main); PEARL_PRIME_PERFECT_BOOKS_SPEC.md §8 checkboxes (tick only what is truly proven); artifacts/qa/perfect_books_wave2_20260718/; docs/agent_prompt_packs/20260718_pearl_prime_perfect_books_wave2/ (land the pack itself — local-only); handoffs
OUT_OF_SCOPE: all lane content/code surfaces
PROVENANCE: none (coordination-class)
BACKGROUND_SAFE: no   RESUME_SURFACE: artifacts/qa/perfect_books_wave2_20260718/FINAL_AUDIT.md
```

## AUDIT (verify, don't trust receipts)

Ramp: SMOKE = fully audit Lane 04 (self-contained CI) + checkpoint; SCALE = the
content lanes 02/03/05. Network verifications carry ConnectTimeout/lowSpeed guards;
a verification that stalls twice ⇒ record UNVERIFIED + continue.

Per lane (02–05): (1) landed ref exists on `pearlstar_offline` (ls-remote) or merge
SHA on origin/main; (2) `git diff --stat <base> <sha>` shows only intended surfaces
(spot-check 3 files); (3) handoff carries commands/evidence/cleanup ledger; (4)
**acceptance-layer honesty is the headline check** — a lane claiming `system working`
MUST have an `ONTGP_VERDICT.md`=PASS at the cited path; a lane using
`bestseller`/`shippable`/`production-ready` without matching proof is a FINDING you
correct in its handoff and record; (5) drift check — any lane that fixed register by
composer/topology retune instead of the line-edit lane is a FINDING; (6) cleanup:
no stray worktrees (`git worktree list`), no orphaned render jobs, no scratch in root.

## SPEC §8 "DONE WHEN" — tick ONLY what is proven

- `≥3 flagship cells have Layer-3 ONTGP_VERDICT.md = PASS` → tick iff Lane 03 landed
  ≥3 PASS verdicts (record the actual N; 1–2 is honest partial progress, not the box).
- `One operator blind-10 PASS recorded` → **stays unticked** (operator-only; Lane 05
  only prepped the packet). Do NOT tick.
- G-F1H / G-ORIENT / G-ACCENT rows → tick per Lane 04's landed+mutation-verified set.

## COORDINATION WRITES (serial, you only)

1. `operator_decisions_log.tsv`: OPD-W2-01 (Wave-2 content track authorized —
   operator "say the word"/"do next", 2026-07-18); Q-W2-CELLS-01 resolution (the 3
   cells used) with evidence.
2. `ACTIVE_WORKSTREAMS.tsv`: one row per lane thread, terminal status + ref@sha.
3. `docs/PROGRAM_STATE.md`: append ONE bounded "2026-07-18 Perfect Books Wave-2
   offline wave (pending GitHub replay)" note — offline refs + honest layer
   (`system working` on N cells; SYSTEM still `authored candidate`; NO bestseller
   claim). Do NOT rewrite the flagship/track statuses as if merged to main.
4. Stale-source correction (§11): update the router memory-facing handoff + the
   Wave-1 handoff's "Deferred" list to reflect what Wave-2 landed.

## FINAL PACKET

`artifacts/qa/perfect_books_wave2_20260718/FINAL_AUDIT.md`: lane × terminal-state ×
ref × acceptance-layer matrix; the honest scorecard (N `system working` cells; gates
added; banks filled; blind-10 packet ready-but-unread); the consolidated
GitHub-restore replay queue (Wave-1 preserved ref + every Wave-2 offline ref in
order); residual blockers (G-ORIENT lexicon if BLOCKED; ship-matrix cells deferred).
Land this lane's writes + the pack directory via the INDEX recipe onto
`offline/perfect-books-wave2-final-20260718`. Last step: `open` the blind-10 packet +
the ONTGP verdicts + FINAL_AUDIT.md for the operator.

## DO NOT

- No "100%" / "bestseller register" claim — this wave's honest max is "`system
  working` on N cells; blind-10 packet ready for the operator." Do NOT tick the
  blind-10 box. Do NOT edit lane content; findings route through the dispatcher.

## CLEANUP LEDGER + HANDOFF

Dispatcher ledger complete; temp index removed; every HOLD path declared. Handoff:
`artifacts/coordination/handoffs/perfect_books_wave2_final_audit_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_PM_lane06
LANES_VERIFIED=<n>/4 (+dispatcher, +Wave-0)
LANDINGS_VERIFIED=<lane:ref@sha …>
SYSTEM_WORKING_CELLS=<n> (ONTGP_VERDICT.md=PASS paths)
SPEC_S8_TICKED=<boxes truly proven; blind-10 box UNticked>
FINDINGS=<acceptance-honesty/drift/cleanup corrections, or none>
OPD_ROWS=<ids>
COORDINATION_UPDATED=<files>
BLIND10_PACKET=<path — ready, unread>
REPLAY_QUEUE=artifacts/qa/perfect_books_wave2_20260718/FINAL_AUDIT.md §replay
OPERATOR_REVIEW_OPENED=<paths>
ACCEPTANCE_LAYER=system working on <n> cells; SYSTEM=authored candidate (NO bestseller register)
LANDED=<ref@full-sha>
CLEANUP_COMPLETE=yes
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_final_audit_2026-07-18.md
SIGNAL=perfect-books-wave2-final=PASS|PARTIAL
NEXT_ACTION=operator runs blind-10; on GitHub restore, replay Wave-1 + Wave-2 refs to main
```
