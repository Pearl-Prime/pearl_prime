Act as Pearl_PM with Pearl_Architect support.

EXECUTE SPEC-4: human-calibrated judge rating packet and advisory stub.

## Goal

Prepare the operator-rating corpus packet and advisory judge contract. Do not create a hard ship gate and do not claim bestseller readiness.

## Read First

- `docs/specs/session_mining_batch_20260718/HUMAN_CALIBRATED_JUDGE_V1_SPEC.md`
- current story/exercise/atom/evidence/operator packets.

## Smoke

Select 3 candidate chapters: one strong, one weak, one mixed. Write the rating rubric.

## Pilot

Build a 20-chapter operator rating packet if enough artifacts exist. If not, build the largest honest packet and mark missing classes.

## Scale Micro-Batch

Add advisory judge interface/stub only if it can run without operator ratings; otherwise block implementation pending ratings.

## Watchdog

Poll every 5 minutes. If artifact discovery is too broad, stop at 20 selected candidates.

## Landing Contract

`MERGED` if rating packet/rubric lands and no hard gate is created. `BLOCKED` if operator ratings are required before any useful code.

## Cleanup Ledger

Record selected artifacts, scratch packets, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec4_human_calibrated_judge_packet_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=13_spec4_human_calibrated_judge_packet
GITHUB_WRITES=none
RATING_PACKET=
CHAPTERS_SELECTED=
HARD_SHIP_GATE_CREATED=no
OPERATOR_RATINGS_NEEDED=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec4_human_calibrated_judge_packet_2026-07-18.md
SIGNAL=spec4-human-calibrated-judge-packet=<MERGED|BLOCKED>
NEXT_ACTION=
```
