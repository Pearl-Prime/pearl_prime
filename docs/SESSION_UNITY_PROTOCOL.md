# Session Unity Protocol

Last updated: 2026-04-27
Owner: Pearl_PM / Pearl_Architect

## Purpose

Standard startup and handoff protocol for all agent sessions in Phoenix Omega.
Every session begins with a STARTUP_RECEIPT. Every session ends with a CLOSEOUT_RECEIPT or explicit handoff.

---

## STARTUP_RECEIPT Template

Every agent session must emit this receipt before doing any work.

```
STARTUP_RECEIPT
AGENT:              <agent name, e.g. Pearl_GitHub>
TASK:               <one-line task description>
PROJECT_ID:         <from ACTIVE_PROJECTS.tsv, or "none">
SUBSYSTEM:          <from SUBSYSTEM_AUTHORITY_MAP.tsv>
AUTHORITY_DOCS:     <semicolon-separated list of governing docs read>
READ_PATH_COMPLETE: <yes/no — have all authority docs been read?>
WRITE_SCOPE:        <paths this session will modify>
OUT_OF_SCOPE:       <paths this session must NOT touch>
BLOCKERS:           <known blockers, or "none">
READY_STATUS:       <ready / blocked / needs-clarification>
```

---

## When To Read Authority Docs

Read authority docs **before** any of these actions:

1. Creating or modifying files in a governed subsystem
2. Creating a branch for a workstream
3. Opening a PR
4. Running push-guard or preflight
5. Resuming a previously started workstream
6. Routing a task to a subsystem for the first time in a session

**Minimum read set for any session:**

- docs/DOCS_INDEX.md (navigation map)
- artifacts/coordination/ACTIVE_PROJECTS.tsv (what is active)
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (workstream state)
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (subsystem routing)

**Subsystem-specific reads:** Look up the subsystem in SUBSYSTEM_AUTHORITY_MAP.tsv and read the authority_doc column entries before writing to that subsystem's config_path.

---

## When To Stop

Stop and escalate (do not proceed) when:

1. Push-guard or preflight fails and the fix is not obvious
2. The task requires writing outside your declared WRITE_SCOPE
3. A blocker listed in ACTIVE_WORKSTREAMS.tsv has not been resolved
4. The authority doc for the target subsystem does not exist
5. Your work would conflict with another active workstream
6. You cannot emit a valid STARTUP_RECEIPT (missing project_id, unclear subsystem, no authority doc)

When stopping, emit:

```
STOP_REASON:   <why>
BLOCKED_ON:    <what must change>
HANDOFF_TO:    <agent or "owner">
```

---

## Handoff Protocol

When handing off to another agent or ending a session:

1. Emit a CLOSEOUT_RECEIPT:

```
CLOSEOUT_RECEIPT
AGENT:          <agent name>
TASK:           <original task>
COMMIT_SHA:     <last commit SHA, or "no commits">
FILES_WRITTEN:  <list of files created or modified>
FILES_READ:     <key authority docs consulted>
STATUS:         <completed / partial / blocked>
HANDOFF_TO:     <next agent, or "none">
NEXT_ACTION:    <what the next agent should do>
```

2. If status is "partial" or "blocked", the NEXT_ACTION must be specific enough for the next agent to resume without re-reading the full context.

3. Update ACTIVE_WORKSTREAMS.tsv if workstream status changed.

---

## Rules

1. One agent, one workstream at a time. Do not interleave workstreams.
2. STARTUP_RECEIPT before work. CLOSEOUT_RECEIPT after work. No exceptions.
3. Authority docs are not optional. If the map says read it, read it.
4. WRITE_SCOPE declared in STARTUP_RECEIPT is binding. Do not exceed it.
5. If a file referenced in SUBSYSTEM_AUTHORITY_MAP.tsv does not exist, that is a gap. Report it; do not invent a replacement.
6. Prefer small commits with clear scope over large commits with mixed scope.
7. Never mark a workstream as completed without evidence (commit SHA, test output, or artifact path).

---

## Quick Reference

| What | Where |
|------|-------|
| Active projects | artifacts/coordination/ACTIVE_PROJECTS.tsv |
| Active workstreams | artifacts/coordination/ACTIVE_WORKSTREAMS.tsv |
| Subsystem routing | artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv |
| Architecture routing | docs/PEARL_ARCHITECT_STATE.md |
| PM state and priorities | docs/PEARL_PM_STATE.md |
| Navigation map | docs/DOCS_INDEX.md |
| Ownership boundaries | docs/OWNERSHIP_MATRIX.md |

---

## Universal router prompt (prompt-building chats)

Use this in chats whose job is to **build the next agent's startup prompt** rather than do the work themselves. The router reads the coordination TSVs and authority docs, then returns one paste-ready startup prompt for the next agent chat — it does not solve the task.

**Canonical full text:** [./agent_brief.txt](./agent_brief.txt) — paste-ready, single source of truth. Do not duplicate the template here; edit `agent_brief.txt` and let this section continue to point at it to prevent drift.

Operating reflexes (deconfliction, reconciliation, turn contracts, signal tokens, poison protocol, enforcement promotion, batching) are encoded as "Router Operating Principles v3" below the bootstrap in that same file; a compliant router reads the whole file.
