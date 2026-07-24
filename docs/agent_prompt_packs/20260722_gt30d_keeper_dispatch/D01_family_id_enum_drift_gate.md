# D01 — Cursor Dev Lane (I006)

EXECUTE. Act as Pearl_Dev on **Cursor**. Depends on **W0 only**.

## Goal

Add CI/runtime family_id enum-drift gate under scripts/ci/ + test; wire into drift detectors / production readiness if appropriate. Eliminate silent registry drift.

## Shared SSOT (read first)

- `artifacts/qa/archived_session_audit_gt30d_20260722/RANKED_FINDINGS.md`
- `artifacts/qa/archived_session_audit_gt30d_20260722/IDEA_BACKLOG.tsv`
- `artifacts/qa/archived_session_audit_gt30d_20260722/DEDUP_LEDGER.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- this pack's `INDEX.md` and `KEEPER_LIVE_STATUS.tsv` (after Wave 0)
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PROGRAM_STATE.md`

## Role contract

You are a **Cursor** lane agent (Pearl_Dev / DevOps / GitHub). You implement **code/CI/wiring** only against a Claude-landed or already-canonical spec.

MUST NOT: invent new systems without a spec; fork parallel judges/validators; weaken drift detectors to pass.

## Turn contract (EXECUTE)

Do not stop at plan / PR-open / tests-running. End MERGED-or-BLOCKED (or LANDED-OFFLINE if GitHub blocked).

## Reuse-first

Extend existing modules. Four-piece chord for any production `run_pipeline` invocation.

## Smoke → Pilot → Scale

1. Smoke: minimal unit/script proof.
2. Pilot: one real tuple/cell or one CI invocation.
3. Scale: only if pilot green; stop on first systemic failure.

## Landing

Merge SHA or explicit BLOCKED with evidence. Manga layers: INTERIM vs REAL labeled.

## Cleanup Ledger

Branches, worktrees, scratch, background jobs. Explicit paths only.


## Keeper IDs

I006

## Handoff

`artifacts/coordination/handoffs/gt30d_d01_2026-07-22.md`

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=D01
STARTUP_RECEIPT_OK=
LIVE_MAIN_SHA=
FILES_CHANGED=
SPEC_PATH_OR_CODE_PATHS=
ACCEPTANCE_LAYER=
CLEANUP_COMPLETE=
HANDOFF=
SIGNAL=gt30d-d01-code-terminal=<sha-or-blocked>
NEXT_ACTION=
```

