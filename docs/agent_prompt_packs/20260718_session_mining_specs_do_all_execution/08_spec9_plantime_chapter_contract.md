Act as Pearl_Dev with Pearl_Architect support.

EXECUTE SPEC-9: plan-time chapter contract.

## Goal

Add or pilot a plan-time chapter contract that consumes current topic-aware thesis resolver and current story/exercise/reader-layer requirements. Do not duplicate planning systems.

## Read First

- `docs/specs/session_mining_batch_20260718/PLANTIME_CHAPTER_CONTRACT_V1_SPEC.md`
- current book planning code and chapter thesis resolver/tests
- narrative form SSOT docs.

## Smoke

Emit contract data for one known book/cell without changing render output. Ch1 frozen parity must remain intact.

## Pilot

Add validator/test for distinct thesis, rising line, reader promise/callback, story progression, and tool/exercise contract fields.

## Scale Micro-Batch

Run the contract on 3 bounded cells. No catalog scale.

## Watchdog

Poll every 5 minutes. If planning code path is ambiguous, stop with a report and do not create a parallel planner.

## Landing Contract

`MERGED` if contract proof lands and bounded tests pass. `BLOCKED` if planning ownership/path is ambiguous.

## Cleanup Ledger

Record generated plans, scratch dirs, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec9_plantime_chapter_contract_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=08_spec9_plantime_chapter_contract
GITHUB_WRITES=none
CONTRACT_SMOKE_PASS=
CELLS_VALIDATED=
CH1_PARITY_PRESERVED=
TESTS_RUN=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec9_plantime_chapter_contract_2026-07-18.md
SIGNAL=spec9-plantime-chapter-contract=<MERGED|BLOCKED>
NEXT_ACTION=
```
