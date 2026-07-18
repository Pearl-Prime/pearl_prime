# Agent Handoff Spec

Last updated: 2026-06-12
Owner: Pearl_PM
Subsystem: `repo_coordination` (per `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`)

## Purpose

Define the **agent-to-agent handoff contract** for Phoenix Omega: how one Pearl
session transfers an in-flight or blocked workstream to the next agent without
loss of context, ownership ambiguity, or orphaned work.

This document finishes the §4 outline in
[`docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md`](./AGENT_SYSTEM_IMPROVEMENT_SPEC.md)
and is the P0-5 deliverable ratified in
[`docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`](./specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md)
(cap `AGENT-SYSTEM-IMPROVEMENT-V2-01`, §2 P0-5).

It is **doc-only** and ships no code. It does **not** replace the
[`docs/SESSION_UNITY_PROTOCOL.md`](./SESSION_UNITY_PROTOCOL.md) STARTUP_RECEIPT /
CLOSEOUT_RECEIPT templates — it **composes with them**: the CLOSEOUT_RECEIPT is
the *carrier* of a handoff, this spec is the *contract* the carrier must satisfy.

**Authority precedence:** where this spec and `docs/SESSION_UNITY_PROTOCOL.md`
both speak, the Session Unity Protocol templates are canonical for *field shape*;
this spec is canonical for *handoff semantics* (who owns the next step, what must
travel with it, when a workstream is "blocked" vs "handed off"). Neither may
contradict the Pearl_GitHub push-guard / preflight / branch-from-`origin/main`
rules in [`skills/pearl-github/SKILL.md`](../skills/pearl-github/SKILL.md).

---

## 1. When a handoff applies

A handoff contract is **required** whenever any of the following is true at the
end of a session:

1. The workstream `owner_agent` in
   [`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`](../artifacts/coordination/ACTIVE_WORKSTREAMS.tsv)
   is a **multi-agent** string (slash-separated), e.g.
   `Pearl_Dev / Pearl_News / Pearl_Architect`, and the work passes between those
   agents.
2. The session ends with status `partial` or `blocked` (CLOSEOUT_RECEIPT
   `STATUS`) and a different agent must take the next step.
3. A git or PR action is the next step and the executing agent is **not**
   Pearl_GitHub — control of push/merge transfers to Pearl_GitHub (per
   [`docs/OWNERSHIP_MATRIX.md`](./OWNERSHIP_MATRIX.md) workflow ownership).
4. A blocker can only be cleared by another agent or by the operator.

A handoff is **not** required when the session completes the workstream in full
(`STATUS: completed`, `HANDOFF_TO: none`) and no follow-on owner is needed. In
that case a normal CLOSEOUT_RECEIPT with `HANDOFF_TO: none` is sufficient.

---

## 2. The one-owner rule (single accountable owner per commit)

**Every commit, and every handoff, has exactly one accountable next owner.**

- The CLOSEOUT_RECEIPT `HANDOFF_TO` field names that single accountable agent
  first. Collaborators or reviewers may follow after a slash or in a
  parenthetical, but the **first name is the owner** and is the agent the next
  session resumes as.
  - Canonical: `HANDOFF_TO: Pearl_PM` (single owner).
  - Canonical with collaborators: `HANDOFF_TO: Pearl_GitHub / Pearl_PM`
    (Pearl_GitHub owns the next step; Pearl_PM is the downstream collaborator).
  - Canonical with action note:
    `HANDOFF_TO: Pearl_PM / owner (optional PR merge after preflight)`.
  - These forms already appear on `origin/main` (e.g.
    `artifacts/audit/TEMPLATE_EXPAND2_INGEST_REPORT.md`,
    `artifacts/audit/CATALOG_DURATION_AUDIT.md`); this spec does not change
    them, it **names the convention**: leftmost = accountable owner.
- The `owner_agent` column may stay multi-agent (it records the lane's full
  cast), but the **`next_owner` column in `ACTIVE_WORKSTREAMS.tsv` must be a
  single agent** — the same agent named first in `HANDOFF_TO`. See §5.
- "One owner" means *one agent accountable for the next action*. It does **not**
  forbid multi-agent lanes; it forbids **ambiguous** ones (two agents each
  assuming the other will act, or neither).

**Rationale:** the recurring failure mode is a multi-agent workstream where the
baton is dropped because every agent believed another was holding it. A single
named `next_owner` per commit makes the baton-holder unambiguous at all times.

---

## 3. Artifact-continuity fields (what must travel with the handoff)

A handoff is only valid if the receiving agent can **resume without re-deriving
the prior session's state**. The CLOSEOUT_RECEIPT MUST therefore carry the
following artifact-continuity fields. Most map directly onto the existing
CLOSEOUT_RECEIPT template in `docs/SESSION_UNITY_PROTOCOL.md`; the additions are
marked **(handoff-required)**.

| Field | Source / column | Meaning | Required when |
|-------|-----------------|---------|---------------|
| `AGENT` | CLOSEOUT_RECEIPT | The handing-off agent (who is releasing the baton). | always |
| `HANDOFF_TO` | CLOSEOUT_RECEIPT | The single accountable next owner (§2), collaborators after a slash. | always |
| `COMMIT_SHA` | CLOSEOUT_RECEIPT | **Full** last commit SHA on the work branch, or `no commits` (then a file dump per `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`). | always |
| `BRANCH` **(handoff-required)** | `ACTIVE_WORKSTREAMS.tsv` `branch` | The exact work branch the next owner checks out. `none` only if no branch exists yet. | partial / blocked / multi-agent |
| `BASE_REF` **(handoff-required)** | `ACTIVE_WORKSTREAMS.tsv` `base_ref` | What the branch was cut from — normally `origin/main` (per Non-Negotiable Git Rule 1). | partial / blocked / multi-agent |
| `FAILING_CHECKS` **(handoff-required)** | derived (`gh pr checks` / CI) | List of red CI checks the next owner inherits, or `none` / `not-run`. Distinguish a *known-tolerated* red (e.g. documented Cloudflare worker-build exception) from a real failure. | partial / blocked / multi-agent |
| `EVIDENCE_PATHS` **(handoff-required)** | `ACTIVE_WORKSTREAMS.tsv` `evidence_paths` | Semicolon-separated paths to artifacts/test-output/PR links proving state (no claim of done without evidence — Session Unity Rule 7). | partial / blocked / multi-agent |
| `FILES_WRITTEN` | CLOSEOUT_RECEIPT | Files created/modified this session. | always |
| `FILES_READ` | CLOSEOUT_RECEIPT | Authority docs consulted. | always |
| `STATUS` | CLOSEOUT_RECEIPT | `completed` / `partial` / `blocked`. | always |
| `NEXT_ACTION` | CLOSEOUT_RECEIPT | Specific enough to resume without re-reading full context (Session Unity Rule 2 for partial/blocked). | always |

**Continuity completeness gate:** a handoff with `STATUS: partial` or `blocked`
is **invalid** if any handoff-required field above is missing or empty. The
receiving agent should **refuse the handoff and bounce it back** (re-emit with
`HANDOFF_TO` = the original sender) rather than guess the missing branch/SHA.

### 3.1 Extended CLOSEOUT_RECEIPT template (handoff variant)

This is the `docs/SESSION_UNITY_PROTOCOL.md` CLOSEOUT_RECEIPT with the
artifact-continuity fields made explicit. Use it verbatim for any handoff:

```
CLOSEOUT_RECEIPT
AGENT:           <handing-off agent, e.g. Pearl_Dev>
TASK:            <original task>
WORKSTREAM_ID:   <workstream_id from ACTIVE_WORKSTREAMS.tsv>
COMMIT_SHA:      <full SHA, or "no commits" + file dump>
BRANCH:          <work branch, or "none">
BASE_REF:        <e.g. origin/main>
FAILING_CHECKS:  <red CI checks, or "none" / "not-run"; flag known-tolerated reds>
EVIDENCE_PATHS:  <semicolon-separated artifact/test/PR paths>
FILES_WRITTEN:   <files created or modified>
FILES_READ:      <key authority docs consulted>
STATUS:          <completed / partial / blocked>
HANDOFF_TO:      <single accountable next owner; collaborators after a slash>
NEXT_ACTION:     <specific resume instruction for the next owner>
```

`WORKSTREAM_ID` and the four handoff-required `BRANCH` / `BASE_REF` /
`FAILING_CHECKS` / `EVIDENCE_PATHS` lines are the additions over the base
template; everything else is the Session Unity CLOSEOUT_RECEIPT unchanged. A
session that is not handing off may use the base 8-field template
(`AGENT`, `TASK`, `COMMIT_SHA`, `FILES_WRITTEN`, `FILES_READ`, `STATUS`,
`HANDOFF_TO`, `NEXT_ACTION`).

---

## 4. Blocked-state semantics

"Blocked" and "handed off" are distinct states and must not be conflated.

- **Handed off** — work can continue *now*, just by a different agent. The next
  owner can act immediately. `STATUS: partial`, `HANDOFF_TO: <next agent>`,
  `NEXT_ACTION` is a do-this-next instruction.
- **Blocked** — work *cannot* continue until an external condition changes (a
  dependency PR merges, a credential is provisioned, the operator decides, a
  sibling workstream completes). `STATUS: blocked`.

A blocked session MUST emit the Session Unity Protocol stop triad in addition to
the CLOSEOUT_RECEIPT:

```
STOP_REASON:   <why work cannot continue>
BLOCKED_ON:    <the exact condition that must change>
HANDOFF_TO:    <agent or operator who can clear it, or "none — awaiting <event>">
```

Blocked-state recording rules:

1. **`blockers` column** in `ACTIVE_WORKSTREAMS.tsv` carries the human-readable
   blocker text (mirrors `BLOCKED_ON`). This is the same column already used for
   in-flight blocker notes (e.g. the bridge/transition lane's "preflight reports
   unrelated repo-state issues" note).
2. **`status` column** is set to `blocked` (the TSV already uses this value — see
   `ws_research_pipeline_activation_20260330`).
3. **`next_owner`** stays the agent who will resume once the blocker clears
   (normally the lane `owner_agent`). When the blocker is a *sibling
   workstream*, that sibling's **workstream id goes in the `blockers` column**
   (precedent: `ws_research_pipeline_activation_20260330` carries
   `blockers = ws_research_citation_gaps_20260330` while `next_owner =
   Pearl_Research`). When the blocker is the operator, set `next_owner = none`
   and name the awaited operator decision in `blockers`.
4. **Operator-tier blockers** (a decision only the operator can make) are
   recorded as decisions in
   [`artifacts/coordination/operator_decisions_log.tsv`](../artifacts/coordination/operator_decisions_log.tsv)
   when an in-envelope decision is made on the operator's behalf; genuinely
   out-of-envelope blockers escalate to the operator. Do not stall a lane on an
   operator ping that an already-logged decision (or an operator-proxy lane,
   where the project has one) could clear. When such a decision is logged, cite
   its `OPD-` id in the CLOSEOUT_RECEIPT `EVIDENCE_PATHS` so the un-block is
   auditable.

**Un-blocking is a handoff in reverse:** when the blocking condition clears, the
agent (or proxy) that cleared it performs a handoff back to the workstream's
`owner_agent` with a fresh CLOSEOUT_RECEIPT citing the clearing evidence (merged
PR SHA, provisioned credential, logged operator decision), and flips the `status`
column back to `in_progress` / `runnable`.

---

## 5. Composition with `ACTIVE_WORKSTREAMS.tsv`

The handoff contract is the bridge between the per-session CLOSEOUT_RECEIPT and
the durable `ACTIVE_WORKSTREAMS.tsv` row. On every handoff the handing-off agent
(or Pearl_PM on its behalf) MUST reconcile the row so the receipt and the TSV
agree:

| CLOSEOUT_RECEIPT field | `ACTIVE_WORKSTREAMS.tsv` column | Reconciliation rule |
|------------------------|----------------------------------|---------------------|
| `HANDOFF_TO` (first name) | `next_owner` | MUST be identical single agent. If `HANDOFF_TO: none`, `next_owner = none`. |
| `STATUS` | `status` | `completed`→`completed`; `partial`→`in_progress`; `blocked`→`blocked`. |
| `BRANCH` | `branch` | Same branch string. |
| `BASE_REF` | `base_ref` | Same base ref. |
| `EVIDENCE_PATHS` | `evidence_paths` | Receipt paths are a subset of / appended to the column. |
| `BLOCKED_ON` (if blocked) | `blockers` | Same blocker text. |

**Invariants** (a `check_agent_registry.py`-style validator MAY enforce these in
a future workstream — out of scope for this doc-only deliverable, but specified
here so the validator has a contract):

- INV-1: For any row with `status` in {`in_progress`, `blocked`}, `next_owner`
  is a **single** agent id (no slash) — or `none` when the lane is blocked on an
  operator decision (§4.3). A sibling-blocking workstream id belongs in the
  `blockers` column, not `next_owner`.
- INV-2: A row's `next_owner`, when an agent, SHOULD resolve to a
  `display_name` in [`config/agents/agent_registry.yaml`](../config/agents/agent_registry.yaml)
  (the machine-readable roster). Unknown agent names are drift.
- INV-3: A `completed` row has `next_owner = none` (or a follow-on ws id) and
  carries evidence (`COMMIT_SHA` / PR link / test path) — never marked complete
  on vibes (Session Unity Rule 7).
- INV-4: A `blocked` row has non-empty `blockers` text matching the
  CLOSEOUT_RECEIPT `BLOCKED_ON`.

`owner_agent` (the lane's full cast, possibly multi-agent) and `next_owner` (the
single accountable baton-holder) are **different columns with different
cardinality** and must not be conflated: `owner_agent` may be
`Pearl_Dev / Pearl_GitHub`; `next_owner` is exactly one of them at any moment.

---

## 6. Worked example (multi-agent lane crossing a blocker)

A book-pipeline lane owned by `Pearl_Dev / Pearl_GitHub` reaches a point where a
dependency PR must merge before the next step:

1. **Pearl_Dev** finishes its implementation slice, commits, and hands off the
   merge step to Pearl_GitHub:
   ```
   CLOSEOUT_RECEIPT
   AGENT:           Pearl_Dev
   WORKSTREAM_ID:   ws_example_lane_20260612
   COMMIT_SHA:      a1b2c3d4e5f60718293a4b5c6d7e8f9012345678
   BRANCH:          agent/example-lane-20260612
   BASE_REF:        origin/main
   FAILING_CHECKS:  none (Cloudflare pearl-prime worker-build red is the documented tolerated exception)
   EVIDENCE_PATHS:  /tmp/example-pilot/book.txt;artifacts/example/smoke_evidence.json
   STATUS:          partial
   HANDOFF_TO:      Pearl_GitHub / Pearl_Dev
   NEXT_ACTION:     Run preflight + push-guard, open PR; on merge, hand back to Pearl_Dev for the post-merge smoke.
   ```
   → `ACTIVE_WORKSTREAMS.tsv`: `status=in_progress`, `next_owner=Pearl_GitHub`.
2. **Pearl_GitHub** opens the PR but the dependency PR is not yet merged, so the
   lane is now blocked:
   ```
   STOP_REASON:   Lane depends on PR #NNNN (auto-plan SSOT) which is still open.
   BLOCKED_ON:    PR #NNNN merged to origin/main.
   HANDOFF_TO:    none — awaiting PR #NNNN merge (operator-gated)
   ```
   → `ACTIVE_WORKSTREAMS.tsv`: `status=blocked`,
   `blockers=PR #NNNN (auto-plan SSOT) not yet merged`, `next_owner=none`.
3. When **PR #NNNN merges**, the merging agent hands back to the lane owner:
   `status=in_progress`, `next_owner=Pearl_Dev`, evidence = the merge SHA. The
   baton is unambiguous at every step.

---

## 7. Rules (normative summary)

1. One accountable owner per commit and per handoff; leftmost name in
   `HANDOFF_TO` is that owner.
2. `next_owner` in `ACTIVE_WORKSTREAMS.tsv` is a single agent (or a sibling
   workstream id for blocked-on-sibling rows) — never multi-agent.
3. A `partial`/`blocked` handoff is invalid if any handoff-required
   artifact-continuity field (§3) is missing; the receiver bounces it back.
4. `blocked` ≠ handed off. Blocked sessions emit the STOP triad and set
   `status=blocked` with non-empty `blockers`.
5. Never report a workstream `completed` without evidence (SHA / PR / test path)
   — Session Unity Rule 7, restated as INV-3.
6. Operator-tier blockers route through Pearl_Operator_Proxy and are logged;
   they do not silently stall a lane.
7. This contract composes with — never overrides — `docs/SESSION_UNITY_PROTOCOL.md`
   field shapes and `skills/pearl-github/SKILL.md` git rules.

---

## 8. Cross-references

| What | Where |
|------|-------|
| STARTUP_RECEIPT / CLOSEOUT_RECEIPT / STOP triad templates | [`docs/SESSION_UNITY_PROTOCOL.md`](./SESSION_UNITY_PROTOCOL.md) |
| Workstream state (owner_agent, branch, base_ref, blockers, next_owner) | [`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`](../artifacts/coordination/ACTIVE_WORKSTREAMS.tsv) |
| Project-level continuity (active_workstreams, next_action) | [`artifacts/coordination/ACTIVE_PROJECTS.tsv`](../artifacts/coordination/ACTIVE_PROJECTS.tsv) |
| Machine-readable agent roster (next_owner validation target) | [`config/agents/agent_registry.yaml`](../config/agents/agent_registry.yaml) |
| Subsystem routing / ownership | [`artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`](../artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv) |
| Git / push / merge ownership (forces Pearl_GitHub handoff) | [`docs/OWNERSHIP_MATRIX.md`](./OWNERSHIP_MATRIX.md), [`skills/pearl-github/SKILL.md`](../skills/pearl-github/SKILL.md) |
| File persistence (no "done" without SHA or dump) | [`docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`](./AGENT_FILE_PERSISTENCE_PROTOCOL.md) |
| Operator-tier decision log (un-block audit trail) | [`artifacts/coordination/operator_decisions_log.tsv`](../artifacts/coordination/operator_decisions_log.tsv) |
| Originating outline (§4) + ratifying cap (P0-5) | [`docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md`](./AGENT_SYSTEM_IMPROVEMENT_SPEC.md), [`docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`](./specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md) |
