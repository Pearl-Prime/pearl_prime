# RUNNER_RESUME — gt30d Keeper Dispatch

Paste when a run is interrupted or partially complete.

1. Read `INDEX.md` + all existing handoffs under `artifacts/coordination/handoffs/gt30d_*`.
2. List which signals already exist (`gt30d-*-terminal=`).
3. Resume **only** the next unmet lane in operator order (W0 → C* → D01–D05 → D06–D08 → W3).
4. Do not re-run MERGED lanes. Do not start D06–D08 without Claude deps.
5. If GitHub blocked: LANDED-OFFLINE + bundle; continue other lanes.

## Shared SSOT (read first)

- `artifacts/qa/archived_session_audit_gt30d_20260722/RANKED_FINDINGS.md`
- `artifacts/qa/archived_session_audit_gt30d_20260722/IDEA_BACKLOG.tsv`
- `artifacts/qa/archived_session_audit_gt30d_20260722/DEDUP_LEDGER.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- this pack's `INDEX.md` and `KEEPER_LIVE_STATUS.tsv` (after Wave 0)
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PROGRAM_STATE.md`

