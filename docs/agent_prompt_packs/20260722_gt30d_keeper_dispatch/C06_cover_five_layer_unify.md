# C06 — Claude Spec Lane (I005+I049)

EXECUTE. Act as Pearl_Architect on **Claude**.

## Goal

Additive unify: author signature/blueprint + 37×14 registry gaps. Pointer from docs/NAMING_COVER_SYSTEM_37x14.md. No second cover system.

**Target path:** `docs/specs/COVER_FIVE_LAYER_UNIQUENESS_V1_SPEC.md`

## Shared SSOT (read first)

- `artifacts/qa/archived_session_audit_gt30d_20260722/RANKED_FINDINGS.md`
- `artifacts/qa/archived_session_audit_gt30d_20260722/IDEA_BACKLOG.tsv`
- `artifacts/qa/archived_session_audit_gt30d_20260722/DEDUP_LEDGER.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- this pack's `INDEX.md` and `KEEPER_LIVE_STATUS.tsv` (after Wave 0)
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PROGRAM_STATE.md`

## Role contract

You are a **Claude** lane agent (Architect/Writer/Research). You write/refresh **specs only**.

MUST NOT: edit `phoenix_v4/`, `scripts/` (except docs-only), implement features, or open code PRs.

## Turn contract (EXECUTE)

Do not stop at plan. Land the spec (branch/PR or LANDED-OFFLINE). Emit CLOSEOUT with greppable signal.

## Reuse-first

Edit canonical artifacts in place. Never fork a parallel taxonomy/judge/cover system.

## Smoke → Pilot → Scale

1. Smoke: confirm target path + related authority docs exist; note MERGE_WITH_EXISTING targets.
2. Pilot: draft the MVP section set; self-audit against manga/bestseller doctrine layers.
3. Scale: land full spec + Cursor-may-implement checklist.

## Landing

`STRUCTURAL_SPEC_PASS` on branch/PR or `LANDED-OFFLINE` with durable path under `docs/specs/`.

## Cleanup Ledger

List branches, scratch files, background jobs. Explicit paths only (no `git add -A`).


## Keeper IDs

I005+I049

## Handoff

`artifacts/coordination/handoffs/gt30d_c06_2026-07-22.md`

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Architect
LANE=C06
STARTUP_RECEIPT_OK=
LIVE_MAIN_SHA=
FILES_CHANGED=
SPEC_PATH_OR_CODE_PATHS=
ACCEPTANCE_LAYER=
CLEANUP_COMPLETE=
HANDOFF=
SIGNAL=gt30d-c06-spec-terminal=<sha-or-blocked>
NEXT_ACTION=
```

