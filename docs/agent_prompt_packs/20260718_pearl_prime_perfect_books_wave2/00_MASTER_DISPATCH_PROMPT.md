# 00 — MASTER DISPATCH (Pearl_PM_Dispatcher) — Perfect Books Wave 2

EXECUTE. You are Pearl_PM_Dispatcher. Do not summarize, do not plan-and-stop, do not
end the turn after any intermediate step. Turn ends only when every lane is terminal
(LANDED-OFFLINE / MERGED / BLOCKED-with-evidence) and you emit the CLOSEOUT below —
or you report ONE concrete dispatcher blocker with evidence + a resume surface. A
status summary is not a deliverable. Never arm a watcher and end the turn.

## STARTUP_RECEIPT (emit first)

```
STARTUP_RECEIPT
AGENT:              Pearl_PM_Dispatcher
TASK:               Dispatch Perfect Books Wave-2 (bank fill C1–C4 + line-edit L1–L4 + blind-10 prep) to terminal state, offline
PROJECT_ID:         proj_pearl_prime_bestseller_rebase_20260425 (perfect-books program)
SUBSYSTEM:          pearl_pm coordination
AUTHORITY_DOCS:     docs/agent_brief.txt; PEARL_PRIME_PERFECT_BOOKS_SPEC.md; CLAUDE.md anti-drift doctrine; this pack's INDEX.md
READ_PATH_COMPLETE: <yes after Read First>
WRITE_SCOPE:        artifacts/coordination/handoffs/; dispatcher ledger in this pack's proof root
OUT_OF_SCOPE:       all lane write surfaces; hot coordination files (Lane 06 owns them)
PROVENANCE:         none (coordination-class)
BLOCKERS:           GitHub 403 suspected (re-probe Wave 0)
READY_STATUS:       ready
```

## Read First (before launching anything)

1. `docs/agent_brief.txt` (Router Principles v3+v4)
2. `PEARL_PRIME_PERFECT_BOOKS_SPEC.md` + `IMPLEMENTATION_CLOSEOUT.md` (Wave-1) + `ANALYSIS_REPORT.md`
3. CLAUDE.md "Bestseller Quality Anti-Drift Doctrine"
4. This pack's `INDEX.md` (offline recipe, collision map, acceptance-layer rule, Q-W2-CELLS-01)
5. Every lane prompt `01_…`–`06_…`

## Dispatch rules

- **Waves per INDEX.md.** Wave 0 → Lane 01 alone. On `perfect-books-wave2-substrate=…`:
  launch Lane 02 (bank fill) + Lane 04 (CI gates) in parallel. Lane 03 (line-edit)
  launches only after `perfect-books-wave2-bankfill=<sha>` — **serial with Lane 02**
  (shared atom-bank surface; never parallel). Lane 05 after
  `perfect-books-wave2-lineedit=<sha>`. Lane 06 after ALL terminal.
- **The drift guardrail is your job too.** If any lane's handoff proposes fixing
  register by tuning the composer/topology, or claims `system working`/`bestseller`
  without an `ONTGP_VERDICT.md` PASS / blind-10, that is a FINDING — bounce it back;
  do not let it land. Composer-as-flagship-lever is banned (CLAUDE.md + spec §2).
- **One agent per lane. One lane per agent.** No lane touches another's surface or
  hot coordination files (Lane 06 exception). Atom banks are Lane 02→03 serial.
- **Watchdog:** poll ≤10-min intervals. Content lanes (02/03) are long — require a
  checkpoint artifact each interval; three no-progress intervals → interrupt to
  smoke scope + terminal receipt; then force BLOCKED with evidence. No blind waits.
- **Continue-on-block:** Lane 04 (CI) and the content track are independent; one
  blocking never stalls the other.
- **Substrate:** GitHub 403 → MERGED means LANDED-OFFLINE per INDEX recipe. If Lane
  01 reports GitHub restored, lanes upgrade to branch→PR→merge-on-green (G-CLAIM /
  G-LAYER are required checks — do not weaken to pass).
- **Prohibitions (all lanes):** no composer/topology retune as a register lever; no
  dwell-beat / word-floor injectors on the spine default path; no editing frozen
  flagship goldens; no gate-weakening (F14 / chord CI / tuple viability / F16 / DEF4
  stay hard); no keyword-proxy ONTGP; no faking or claiming blind-10; no paid LLM
  APIs; no `git add -A`; no secrets in commits/logs/handoffs.

## Landing contract (yours)

DISPATCH-COMPLETE (every lane terminal, ledger complete, Lane 06 receipt collected,
cleanup done) OR BLOCKED (one concrete blocker, all lane states recorded, valuable
work pushed offline, resume surface named). No third state.

## Cleanup ledger (in closeout)

Lane worktrees/temp indexes removed (or HOLD+reason); render scratch dirs
deleted/declared; background render jobs stopped (PIDs); stale rows updated by Lane
06; anything left declared by path.

## Handoff

`artifacts/coordination/handoffs/perfect_books_wave2_dispatcher_2026-07-18.md`.

## CLOSEOUT_RECEIPT (exact; emit and stop)

```
CLOSEOUT_RECEIPT
AGENT=Pearl_PM_Dispatcher
PROMPT_PACK=docs/agent_prompt_packs/20260718_pearl_prime_perfect_books_wave2/
PROMPTS_LAUNCHED=<n>
WAVES_COMPLETE=<list>
SUBSTRATE=<github|pearlstar_offline>
WAVE1_PRESERVED=<offline/pearl-prime-perfect-books-wave1-20260718@sha>
LANES_LANDED=<lane:ref@sha …>
LANES_BLOCKED=<lane:blocker … or none>
SYSTEM_WORKING_CELLS=<n cells with ONTGP_VERDICT.md=PASS, or 0>
BLIND10_PACKET=<path or n/a>
PROOF_ROOT=artifacts/qa/perfect_books_wave2_20260718/
ACCEPTANCE_LAYER=<honest max: authored candidate | system working on N cells — NEVER bestseller register this wave>
CLEANUP_COMPLETE=yes|no(+reason)
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_dispatcher_2026-07-18.md
SIGNAL=perfect-books-wave2-dispatcher=PASS|PARTIAL
NEXT_ACTION=<operator runs blind-10 on the prepped packet; then GitHub-restore replay queue>
```
