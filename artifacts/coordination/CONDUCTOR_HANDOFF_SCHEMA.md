# CONDUCTOR_HANDOFF_SCHEMA — Cross-Session Orchestrator Handoff

**PROJECT_ID:** PRJ-PEARL-CONDUCTOR-V2  
**SUBSYSTEM:** pearl_pm coordination + meta (orchestrator infra)  
**AUTHORITY_DOCS:** `docs/SESSION_UNITY_PROTOCOL.md`, `CLAUDE.md`, `skills/pearl-github/SKILL.md`, `skills/pearl-int/SKILL.md`

---

## 1. PURPOSE

Pearl_Conductor (and future routers) may stop mid-wave due to halts, timeouts, or operator context switches. This schema defines a **single, canonical handoff artifact** so a **fresh orchestrator** can resume without re-deriving recent attempts from GitHub PR lists alone. The handoff is a **snapshot** at stop time; the **timeline** lives in `artifacts/coordination/orchestrator_log_<date>.md` (see `orchestrator_log_template.md`).

---

## 2. FILENAME CONVENTION

| Artifact | Path | Semantics |
|----------|------|-----------|
| **Active handoff** | `artifacts/coordination/CONDUCTOR_HANDOFF.md` | Always this basename. **Overwritten** when a new handoff is written. |
| **History** | Git commits on the integration branch / `main` | Prior versions remain recoverable via `git log -p -- artifacts/coordination/CONDUCTOR_HANDOFF.md`. |

Do not scatter multiple handoff basenames; routers and humans grep one path.

---

## 3. SCHEMA (markdown structured)

Orchestrators **populate all sections**. Use `null` or `_None_` explicitly where optional fields are absent.

```markdown
# CONDUCTOR_HANDOFF

## orchestrator_id
<string, e.g. pearl_conductor_v2_2026-05-09T22:00:00Z>

## last_wave_attempted
<A | B | C | D | <named>>

## last_wave_outcome
<success | partial | halted>

## subagents_in_flight

| subagent_role | task_description | branch | expected_completion | last_known_status |
|----------------|-------------------|--------|---------------------|-------------------|
| ... | ... | ... | ISO8601 or window | queued|running|blocked|unknown |

## subagents_complete_this_wave

| subagent_role | PR# | commit_sha | outcome |
|----------------|-----|------------|---------|
| ... | #NNNN | full_sha | merged|opened|abandoned|failed |

## main_HEAD_at_handoff
<full_sha of origin/main at handoff time>

## planned_next_wave
**description:** <1–3 sentences>  
**reasoning:** <why this ordering>  
**ws_ids:** <comma-separated workstream / ticket ids, or empty>

## operator_decisions_pending
- <item or `_None_`>

## halt_reason
<H1 | H2 | H3 | H4 | H5 | null>  
**detail:** <short human sentence>

## resumption_pointer
<specific instruction for the next orchestrator, e.g. "Read PRs #980 #981; verify CI green; plan Wave C with 2 isolation PRs using phoenix-isolation-pr skill.">
```

### Halt code reference (H1–H5)

| Code | Meaning | Typical `operator_decisions_pending` |
|------|---------|----------------------------------------|
| **H1** | Governance / ruleset / merge policy BLOCK | Links to failing check + governance log |
| **H2** | Operator product / scope decision | Explicit questions |
| **H3** | Infra: network, lock, LFS, worktree corruption | Diagnosis + last command |
| **H4** | Safety gate / WRITE_SCOPE drift / wrong PR base | Diff snippets, branch names |
| **H5** | Max wall-time / session timeout | What completed vs not |

When `halt_reason` is `null` (normal completion), `resumption_pointer` should still suggest a no-op or “start next PROJECT packet” line.

---

## 3b. FIELD-LEVEL RULES

| Field | Rule |
|-------|------|
| `orchestrator_id` | Globally unique per session start; include time zone (`Z`). |
| `last_wave_attempted` | Must match the wave token used in logs for that period. |
| `last_wave_outcome` | `success` only if all planned slots succeeded per orchestrator template; otherwise `partial` or `halted`. |
| `subagents_in_flight` | If empty, render a single row with `subagent_role=_none_` OR omit table body entirely but keep header — pick one house style per org and stick to it for grep stability. |
| `main_HEAD_at_handoff` | Record **after** `git fetch origin` in the orchestrator shell; full 40-char SHA. |
| `planned_next_wave` | If unknown, set description to `_TBD_` and move questions to `operator_decisions_pending`. |

---

## 4. EXAMPLE — filled handoff

```markdown
# CONDUCTOR_HANDOFF

## orchestrator_id
pearl_conductor_v2_2026-05-09T21:47:12Z

## last_wave_attempted
B

## last_wave_outcome
halted

## subagents_in_flight

| subagent_role | task_description | branch | expected_completion | last_known_status |
|----------------|-------------------|--------|---------------------|-------------------|
| Pearl_Dev | Fix import shadowing in scripts/foo | agent/foo-import-20260509 | 2026-05-09T23:00:00Z | running |
| Pearl_GitHub | Open isolation PR for docs only | agent/docs-typo-20260509 | 2026-05-09T22:30:00Z | blocked |

## subagents_complete_this_wave

| subagent_role | PR# | commit_sha | outcome |
|----------------|-----|------------|---------|
| Pearl_Architect | #990 | 7d2c9e4f8a1b… | opened |
| Pearl_PM | #989 | 91aa0043dead… | merged |

## main_HEAD_at_handoff
bc925776985702995da65a6ebb21086ce961f7c5

## planned_next_wave
**description:** After Pearl_Dev PR merges, run Wave C: two parallel isolation PRs for config gates + snapshot refresh.  
**reasoning:** Config gate must land before snapshot to avoid double CI churn.  
**ws_ids:** WS-PEARL-CI-12, WS-SNAPSHOT-03

## operator_decisions_pending
- Approve temporary `no-verify` for docs-only hotfix? (default: **no**)
- Confirm whether Wave C may touch `config/gates.yaml` (EXCLUSIVE)

## halt_reason
H1  
**detail:** Governance workflow reported BLOCKED on #990 due to subsystem authority doc warning — needs operator override or doc add.

## resumption_pointer
Read `artifacts/coordination/orchestrator_log_2026-05-09.md` tail 40 lines; open `gh pr view 990`; if governance clears, resume Pearl_GitHub on branch `agent/docs-typo-20260509` and Pearl_Dev on `agent/foo-import-20260509`; plan Wave C only after both are green on origin/main.
```

---

## 5. RECOVERY PROTOCOL — how a fresh orchestrator resumes

1. **Fetch + sync context:** `git fetch origin`; note current `origin/main` SHA (compare to `main_HEAD_at_handoff` in the file — expect forward progress).
2. **Read handoff first:** Open `artifacts/coordination/CONDUCTOR_HANDOFF.md` **before** spawning subagents.
3. **Replay timeline:** Tail `artifacts/coordination/orchestrator_log_<date>.md` for ordering, PR URLs, and failure notes.
4. **Reconcile in-flight table:** For each row, run `gh pr view` / `git ls-remote` as appropriate; mark reality vs `last_known_status`.
5. **Execute `resumption_pointer` literally** unless operator message overrides; if blocked by H1/H2, **stop** and surface `operator_decisions_pending`.
6. **On next halt or completion:** Overwrite `CONDUCTOR_HANDOFF.md` with a fresh instance of this schema (preserve history via commit, not via rename).

---

## Integration note

| Artifact | Role |
|----------|------|
| `CONDUCTOR_HANDOFF.md` | Latest **snapshot** for resumption |
| `orchestrator_log_<date>.md` | **Append-only** event timeline for the session/day |

End of schema.
