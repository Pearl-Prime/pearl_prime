# orchestrator_log_template — Durable Pearl_Conductor State Log

**PROJECT_ID:** PRJ-PEARL-CONDUCTOR-V2  
**SUBSYSTEM:** pearl_pm coordination + meta (orchestrator infra)  
**Pairing doc:** `artifacts/coordination/CONDUCTOR_HANDOFF_SCHEMA.md`

---

## 1. PURPOSE

Pearl_Conductor v1 state logs under `/tmp/` (e.g. `/tmp/pearl_conductor_2026-05-09.md`) are **operator-local**, **not crash-survivable**, and **not cross-session resumable**. v2 moves the canonical timeline to **tracked files under `artifacts/coordination/`** on `origin/main` (or the active integration branch), updated on a steady cadence so a new orchestrator or operator can reconstruct **what happened**, not only **what is open on GitHub**.

---

## 2. FILENAME CONVENTION

| Pattern | Example | When to use |
|---------|---------|--------------|
| `artifacts/coordination/orchestrator_log_<date>.md` | `orchestrator_log_2026-05-09.md` | **One file per calendar day** OR **one per long session** — pick at session start and stay consistent. |
| Rotation | Start `orchestrator_log_2026-05-10.md` at UTC day boundary or new PROJECT_ID | Never delete prior logs; append-only within a file. |

The orchestrator states the chosen file name in the first log entry `notes` field.

---

## 3. APPEND PROTOCOL

1. **Append only:** Add new rows/entries at the end of the log section. **Never edit** prior rows (typos stay; add a corrective row if needed).
2. **Commit cadence:** At minimum every **30–60 minutes wall time**, and **immediately after each wave** completes (success, partial, or halted).
3. **Isolation PR for log:** Log-only updates should use **`skills/phoenix-isolation-pr`** with WRITE_SCOPE = the log file (and any handoff if updated in same commit — prefer separate commits if it keeps WRITE_SCOPE clean).
4. **Concurrency:** If two orchestrators could run (should not), **serialize** writes via operator + distinct branches; do not merge conflicting append streams blindly.

---

## 4. ROW FORMAT — markdown table

Use a single table named **EVENT_LOG** per file. Columns:

| timestamp (UTC) | orchestrator_id | wave | ws_id | subagent_role | event_type | PR# | commit_sha | notes |
|-----------------|-----------------|------|-------|---------------|-------------|-----|------------|-------|

**event_type** ∈ { `spawned`, `complete`, `failed`, `halted`, `skipped` }

**Optional machine-readable mirror (JSONL):** If automation emits JSONL instead, each line must contain the same logical fields:

```json
{"ts":"2026-05-09T20:01:00Z","orch":"pearl_conductor_v2_...","wave":"B","ws_id":"WS-1","role":"Pearl_Dev","event":"spawned","pr":null,"sha":null,"notes":"task …"}
```

Human operators may read either form; routers should prefer one style per file for clarity.

---

## 5. EXAMPLE — sample wave (markdown table)

```markdown
# orchestrator_log_2026-05-09.md

_SESSION_START_: PRJ-PEARL-CONDUCTOR-V2 | baseline: Pearl_Conductor v1 Wave B running; v2 docs landed in PR #TBD_

## EVENT_LOG

| timestamp (UTC) | orchestrator_id | wave | ws_id | subagent_role | event_type | PR# | commit_sha | notes |
|-----------------|-----------------|------|-------|---------------|-------------|-----|------------|-------|
| 2026-05-09T18:00:05Z | pearl_conductor_v2_2026-05-09T18:00:05Z | A | WS-CI-01 | Pearl_GitHub | spawned | — | — | Isolation PR prep for workflow tweak |
| 2026-05-09T18:22:41Z | pearl_conductor_v2_2026-05-09T18:00:05Z | A | WS-CI-01 | Pearl_GitHub | complete | #1001 | aaaa1111… | PR opened; CI pending |
| 2026-05-09T18:25:10Z | pearl_conductor_v2_2026-05-09T18:00:05Z | A | WS-DOC-02 | Pearl_Architect | spawned | — | — | Spec clarification for v2 template |
| 2026-05-09T18:40:02Z | pearl_conductor_v2_2026-05-09T18:00:05Z | A | WS-DOC-02 | Pearl_Architect | complete | #1002 | bbbb2222… | Doc-only PR merged |
| 2026-05-09T19:05:00Z | pearl_conductor_v2_2026-05-09T18:00:05Z | B | WS-FEAT-03 | Pearl_Dev | spawned | — | — | Implementation wave |
| 2026-05-09T19:45:18Z | pearl_conductor_v2_2026-05-09T18:00:05Z | B | WS-FEAT-03 | Pearl_Dev | failed | — | — | pytest failure on scripts/foo; branch pushed for inspection |
| 2026-05-09T20:00:00Z | pearl_conductor_v2_2026-05-09T18:00:05Z | B | — | — | halted | — | — | H4 safety gate mismatch on accidental `git add .`; operator paged |
```

---

## 6. INTEGRATION — log vs handoff

| Dimension | `orchestrator_log_<date>.md` | `CONDUCTOR_HANDOFF.md` |
|-----------|------------------------------|-------------------------|
| **Time shape** | Append-only **timeline** | **Snapshot** at halt/complete/timeout |
| **Granularity** | Per-event rows | Latest known tables + decisions |
| **Recovery use** | Understand ordering & retries | Immediate “where we left off” |
| **Update frequency** | Every 30–60 min + end of wave | On halt, completion, or timeout |

**Practice:** When writing `CONDUCTOR_HANDOFF.md`, also append a `halted` or `complete` row to the log with the same timestamp and cross-reference PR / SHA in `notes`.

---

## 7. FIELD CONSTRAINTS (validation)

| Field | Constraint |
|-------|--------------|
| `timestamp` | ISO8601 UTC with `Z` suffix |
| `orchestrator_id` | Must match the orchestrator packet ID for the session |
| `wave` | Single token (`A`, `B`, `C`, … or `named`) |
| `ws_id` | Non-empty unless event is global (`—` allowed in table rendering) |
| `subagent_role` | PascalCase role name (`Pearl_Dev`, …) |
| `event_type` | Enum only (see §4) |
| `PR#` | `#NNNN` form or `—` if unknown |
| `commit_sha` | 40-hex lowercase or `—` if not applicable |
| `notes` | Single-line preferred; use `|` continuation only when unavoidable |

If a correction is required, **append** a new row referencing the prior timestamp in `notes` (`corrects row 2026-…`).

---

## 8. JSONL EXAMPLE (optional stream)

```json
{"ts":"2026-05-09T18:00:05Z","orch":"pearl_conductor_v2_2026-05-09T18:00:05Z","wave":"A","ws_id":"WS-CI-01","role":"Pearl_GitHub","event":"spawned","pr":null,"sha":null,"notes":"Isolation PR for workflow tweak"}
{"ts":"2026-05-09T18:22:41Z","orch":"pearl_conductor_v2_2026-05-09T18:00:05Z","wave":"A","ws_id":"WS-CI-01","role":"Pearl_GitHub","event":"complete","pr":1001,"sha":"aaaa1111bbbb2222cccc3333dddd4444eeee5555","notes":"PR opened; awaiting Core tests"}
```

---

## 9. PR COMMIT STRATEGY FOR LOG-ONLY UPDATES

1. Prefer **one-file** WRITE_SCOPE: the log file itself.
2. Commit message: `chore(coord): orchestrator log append <token>`
3. If handoff file also changes in the same minute, **prefer two commits** (log then handoff) to keep `git blame` legible — orchestrator may batch push once.

---

## 10. OPERATOR VISIBILITY

Operators may skim only:

- The latest **20 rows** of the log, and
- The current `CONDUCTOR_HANDOFF.md`

Everything older remains in git history for forensics.

End of template.
