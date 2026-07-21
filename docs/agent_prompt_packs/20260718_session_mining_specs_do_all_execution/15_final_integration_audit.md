Act as Pearl_PM.

EXECUTE final integration audit.

## Goal

Reconcile all implemented lanes, verify no retired stale work was re-run, and produce the next-action matrix.

## Read First

- all lane handoffs from this pack;
- changed-file lists for each offline branch/bundle;
- proof root `artifacts/qa/session_mining_specs_do_all_20260718/`.

## Smoke

Verify lane 01 preserved refreshed specs/proofs/prompts.

## Pilot

Reconcile wave 1 and wave 2 outputs. Confirm no public release/live publish/catalog scale/destructive prune occurred.

## Scale Micro-Batch

Reconcile all lanes, all PearlStar refs/bundles, tests, blockers, and cleanup ledgers.

## Watchdog

Poll every 5 minutes. If any lane lacks a handoff, mark it `BLOCKED_MISSING_HANDOFF` and continue audit.

## Landing Contract

`PASS` if all launched lanes are terminal, outputs reconcile, and cleanup is complete.

`BLOCKED` if any required lane is non-terminal or unsafe changes were made.

## Cleanup Ledger

Confirm no worktrees, branches, scratch files, or background jobs remain except explicitly recorded offline refs/bundles.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_do_all_final_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=15_final_integration_audit
GITHUB_WRITES=none
LANES_LAUNCHED=
LANES_MERGED=
LANES_BLOCKED=
RETIRED_ITEMS_RERUN=0
PUBLIC_RELEASE_AUTHORIZED=no
CATALOG_SCALE_RUN=no
DESTRUCTIVE_PRUNE_RUN=no
PEARLSTAR_REFS=
FINAL_VERDICT=<PASS|BLOCKED>
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_do_all_final_2026-07-18.md
SIGNAL=session-mining-specs-do-all-final=<PASS|BLOCKED>
NEXT_ACTION=
```
