# W0 — Pearl_PM Keeper Live Reverify

EXECUTE. Act as Pearl_PM.

## Goal

Re-check the 12 Wave-A keepers against live `origin/main` + on-disk paths. Write
`docs/agent_prompt_packs/20260722_gt30d_keeper_dispatch/KEEPER_LIVE_STATUS.tsv`.

Do **not** start C* or D* lanes until this lands.

## Shared SSOT (read first)

- `artifacts/qa/archived_session_audit_gt30d_20260722/RANKED_FINDINGS.md`
- `artifacts/qa/archived_session_audit_gt30d_20260722/IDEA_BACKLOG.tsv`
- `artifacts/qa/archived_session_audit_gt30d_20260722/DEDUP_LEDGER.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- this pack's `INDEX.md` and `KEEPER_LIVE_STATUS.tsv` (after Wave 0)
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PROGRAM_STATE.md`


## Keepers to reverify

I042, I043, I029, I034, I025, I048, I026, I005, I049, I006, I032, I045, I007, I001
(I025+I048 share C04; I005+I049 share C06; I043+I029 share C02 — still one row each).

## Columns for KEEPER_LIVE_STATUS.tsv

`idea_id\ttitle\taudit_status\tlive_status\tevidence_paths\tnotes\trecommended_lane`

`live_status` ∈ TRULY_MISSING | PARTIAL | LIKELY_LANDED | SUPERSEDED | OPERATOR_GATE | DUPLICATE_OF_PRIOR_MINING

## Smoke

`git fetch origin` (record blocker if fail). Confirm audit folder exists.

## Pilot

Path-existence + light rg for each keeper's named artifacts (no repo-wide recursive glob storms).

## Scale

Write the TSV. Commit/land pack-local status (explicit paths).

## Landing

MERGED/LANDED-OFFLINE when TSV exists and every keeper has a live_status.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=W0_reverify
STARTUP_RECEIPT_OK=
LIVE_MAIN_SHA=
FILES_CHANGED=
SPEC_PATH_OR_CODE_PATHS=
ACCEPTANCE_LAYER=
CLEANUP_COMPLETE=
HANDOFF=
SIGNAL=gt30d-keeper-reverify-terminal=<sha-or-blocked>
NEXT_ACTION=
```

