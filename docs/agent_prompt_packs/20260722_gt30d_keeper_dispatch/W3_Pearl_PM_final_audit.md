# W3 — Pearl_PM Final Keeper Dispatch Audit

EXECUTE. Act as Pearl_PM.

## Goal

Reconcile all lane signal tokens. Write
`artifacts/qa/archived_session_audit_gt30d_20260722/KEEPER_DISPATCH_CLOSEOUT_20260722.md`
mapping each Wave-A keeper → SPEC_LANDED | CODE_MERGED | BLOCKED (with evidence).

Update `artifacts/qa/archived_session_audit_gt30d_20260722/WAVE_PROGRESS.md` resume pointer to **Wave-B**.

## Shared SSOT (read first)

- `artifacts/qa/archived_session_audit_gt30d_20260722/RANKED_FINDINGS.md`
- `artifacts/qa/archived_session_audit_gt30d_20260722/IDEA_BACKLOG.tsv`
- `artifacts/qa/archived_session_audit_gt30d_20260722/DEDUP_LEDGER.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- this pack's `INDEX.md` and `KEEPER_LIVE_STATUS.tsv` (after Wave 0)
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PROGRAM_STATE.md`


## Smoke

Collect every `gt30d-*-terminal=` token from handoffs/closeouts.

## Pilot

Verify no lane reopened DEDUP_LEDGER duplicates.

## Scale

Write closeout + WAVE_PROGRESS update. Land explicit paths.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=W3_final_audit
STARTUP_RECEIPT_OK=
LIVE_MAIN_SHA=
FILES_CHANGED=
SPEC_PATH_OR_CODE_PATHS=
ACCEPTANCE_LAYER=
CLEANUP_COMPLETE=
HANDOFF=
SIGNAL=gt30d-keeper-dispatch-final=<sha-or-blocked>
NEXT_ACTION=
```

