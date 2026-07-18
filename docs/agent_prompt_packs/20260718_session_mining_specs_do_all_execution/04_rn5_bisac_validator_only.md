Act as Pearl_Dev.

EXECUTE RN-5 as validator-only catalog metadata work.

## Goal

Do not redo the BISAC map. Add only a narrow validator if the map is already corrected but no CI validator exists.

## Read First

- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md` RN-5 row
- catalog skeleton generators
- current BISAC mapping files/tests

## Smoke

Prove anxiety/sleep_anxiety map to `SEL036000` in current files. If not true, stop `BLOCKED_MAP_NOT_CORRECT`.

## Pilot

Add a validator script/test that checks the topic-to-BISAC mapping for known mental-health topics.

## Scale Micro-Batch

Run validator against current catalog metadata only. No catalog rewrite.

## Watchdog

Poll every 5 minutes. If metadata scan is too large, validate the canonical map plus one generated sample.

## Landing Contract

`MERGED` if validator passes and no mapping rewrite occurs. `BLOCKED` if current map is not corrected.

## Cleanup Ledger

Record scratch metadata samples and branches/jobs.

## Handoff

Write `artifacts/coordination/handoffs/rn5_bisac_validator_only_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=04_rn5_bisac_validator_only
GITHUB_WRITES=none
MAP_ALREADY_CORRECT=
VALIDATOR_ADDED=
TESTS_RUN=
CATALOG_REWRITE=no
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/rn5_bisac_validator_only_2026-07-18.md
SIGNAL=rn5-bisac-validator-only=<MERGED|BLOCKED>
NEXT_ACTION=
```
