# Master Dispatch — gt30d Wave-B

EXECUTE as Pearl_PM. Wave-A is closed locally. This pack runs deferred keepers.

## Shared SSOT
- `artifacts/qa/archived_session_audit_gt30d_20260722/KEEPER_DISPATCH_CLOSEOUT_20260722.md` (Wave-A done)
- `artifacts/qa/archived_session_audit_gt30d_20260722/IDEA_BACKLOG.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- this pack `INDEX.md`


## Order
1. Claude C01–C06 (max 3 concurrent)
2. Cursor D01–D05 in parallel
3. W3 final audit → `KEEPER_DISPATCH_WAVE_B_CLOSEOUT_20260722.md`

## Guardrails
Same as Wave-A: no parallel judges; manga layer-honest; no OPERATOR_GATE reopen; merge-with-existing specs.
