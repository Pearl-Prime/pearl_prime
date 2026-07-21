Act as Pearl_Marketing with Pearl_Dev support.

EXECUTE SPEC-6: free-to-paid ladder schema pilot.

## Goal

Extend marketing feed planning with access tier, ladder tier, asset family, and release authorization boundaries, aligned to GHL, deterministic social, image license gates, and faceless video.

## Read First

- `docs/specs/session_mining_batch_20260718/FREE_TO_PAID_LADDER_V1_SPEC.md`
- `scripts/marketing/build_marketing_feed.py`
- deterministic social dry-run artifacts if present.

## Smoke

Build one dry-run feed row showing `access`, `ladder_tier`, `asset_family`, and `manual_review_required`.

## Pilot

Add schema/test for one brand/topic ladder. Paid items must require real asset/proof.

## Scale Micro-Batch

Dry-run up to 5 brands. No live publish, no Metricool scheduling, no GHL writes.

## Watchdog

Poll every 5 minutes. If feed builder dependencies are missing, write schema-only proof and block implementation.

## Landing Contract

`MERGED` if schema/test/dry-run pass. `BLOCKED` if live feed contract is ambiguous.

## Cleanup Ledger

Record dry-run payloads, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec6_free_to_paid_ladder_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Marketing
LANE=10_spec6_free_to_paid_ladder
GITHUB_WRITES=none
LIVE_PUBLISHING_AUTHORIZED=no
GHL_WRITES=none
DRY_RUN_ROWS=
SCHEMA_TESTS=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec6_free_to_paid_ladder_2026-07-18.md
SIGNAL=spec6-free-to-paid-ladder=<MERGED|BLOCKED>
NEXT_ACTION=
```
