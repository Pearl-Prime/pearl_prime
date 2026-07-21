# Master Dispatch — gt30d Keeper Multi-Agent Pack (2026-07-22)

**EXECUTE.** You are Pearl_PM for the Wave-A keeper dispatch from the >30d archived-session audit.

## Role split (enforce)

- **Claude agents** → specs only (`docs/specs/`, handoffs, acceptance labels).
- **Cursor agents** → code/CI/wiring only against Claude-landed or canonical specs.
- Do **not** reopen DEDUP_LEDGER duplicates or OPERATOR_GATE items.

## Shared SSOT (read first)

- `artifacts/qa/archived_session_audit_gt30d_20260722/RANKED_FINDINGS.md`
- `artifacts/qa/archived_session_audit_gt30d_20260722/IDEA_BACKLOG.tsv`
- `artifacts/qa/archived_session_audit_gt30d_20260722/DEDUP_LEDGER.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- this pack's `INDEX.md` and `KEEPER_LIVE_STATUS.tsv` (after Wave 0)
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PROGRAM_STATE.md`


## Paste-ready order

| Step | Paste file | Surface | Notes |
|---|---|---|---|
| 0 | `W0_Pearl_PM_reverify.md` | Claude or Cursor | Blocks everything |
| 1a | `C01`…`C06` | **Claude** | Max 3 concurrent |
| 1b | `D01`…`D05` | **Cursor** | After W0; parallel OK |
| 2 | `D06`…`D08` | **Cursor** | After C01 / C02 / C05 terminals |
| 3 | `W3_Pearl_PM_final_audit.md` | Claude or Cursor | After all terminals |

## Non-negotiables

- Manga: six-layer acceptance taxonomy; no stub-as-done; INTERIM ≠ REAL.
- Bestseller: gate-PASS ≠ bestseller; four-piece chord on production builds.
- No parallel judge/validator systems (SPEC-4 / retired RNs stay retired).
- Disk <15Gi free → no new local worktrees; prefer cloud/sparse/LANDED-OFFLINE.

## Success

Every Wave-A keeper maps to `SPEC_LANDED` / `CODE_MERGED` / `BLOCKED` in
`artifacts/qa/archived_session_audit_gt30d_20260722/KEEPER_DISPATCH_CLOSEOUT_20260722.md`.

Signal: `gt30d-keeper-dispatch-pack-ready=1` once this pack is on disk and W0 can start.
