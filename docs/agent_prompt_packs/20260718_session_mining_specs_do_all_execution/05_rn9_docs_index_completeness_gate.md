Act as Pearl_PM with Pearl_DevOps support.

EXECUTE RN-9: current docs index completeness gate.

## Goal

Recompute current required-doc coverage and add a narrow docs-index governance check. Do not reuse stale 62% claims and do not churn broad docs.

## Read First

- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md` RN-9 row
- `docs/DOCS_INDEX.md`
- `docs/agent_brief.txt`
- any current required-read doc lists.

## Smoke

Inventory required docs from `docs/agent_brief.txt` and verify they appear in `DOCS_INDEX` or are explicitly exempt.

## Pilot

Add a narrow checker for required-read doc index coverage.

## Scale Micro-Batch

Run checker across current required-read docs. Do not auto-edit the whole index unless a tiny explicit patch is safe.

## Watchdog

Poll every 5 minutes. If docs scan grows broad, stop at report-only and mark missing rows.

## Landing Contract

`MERGED` if checker/report lands without broad docs churn. `BLOCKED` if required-doc authority is ambiguous.

## Cleanup Ledger

Record scratch inventory files, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/rn9_docs_index_completeness_gate_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=05_rn9_docs_index_completeness_gate
GITHUB_WRITES=none
REQUIRED_DOCS_SCANNED=
MISSING_INDEX_ROWS=
CHECKER_ADDED=
BROAD_DOCS_CHURN=no
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/rn9_docs_index_completeness_gate_2026-07-18.md
SIGNAL=rn9-docs-index-completeness-gate=<MERGED|BLOCKED>
NEXT_ACTION=
```
