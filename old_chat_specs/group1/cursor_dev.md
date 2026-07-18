# dev
_Exported on 4/16/2026 at 19:38:10 GMT+8 from Cursor (3.1.15)_

---

**User**

Act as my Phoenix Omega agent prompt router.

When I give you a plain-English task, do not solve the task. Return only a paste-ready startup prompt for the next agent chat.

That startup prompt must:
- tell the agent to read docs/ONBOARDING_START_HERE.md and docs/SESSION_UNITY_PROTOCOL.md first and follow them exactly
- require STARTUP_RECEIPT only in the first reply
- include startup safety, PM/workstream, authority-doc, and temp-risk checks
- identify the most likely subsystem authority doc(s) from the repo when possible
- include PROJECT_ID and WORKSTREAM_ID if known from current coordination state
- include WORKSTREAM_STATUS if known, and warn if the workstream is completed/preserved/closed
- include APPROVED BASE if known
- include WRITE_SCOPE if known, otherwise say to determine it from authority docs
- route git mutations to Pearl_GitHub
- tell the agent to stop if there is overlap, missing authority, unsafe branch/worktree state, temp-only risk, existing equivalent artifacts, or contradiction with the approved base/workstream
- prefer existing canonical docs/files over creating new ones

Output format:
1. The exact prompt text I should paste into the next agent chat
2. Nothing else unless you are genuinely unsure, in which case add one short note after the prompt



---

**Cursor**

Gathering coordination state and authority-doc patterns from the repo so the paste-ready prompt is accurate. No plain-English task was included in your message.



**Note:** You didn’t include a concrete plain-English task in this message. The prompt below uses a single placeholder line for that task.

---

**1. Paste-ready startup prompt**

```
You are working in the Phoenix Omega repo.

Before anything else, read `docs/ONBOARDING_START_HERE.md` and `docs/SESSION_UNITY_PROTOCOL.md` in full and follow them exactly for startup, lane routing, receipts, and stop conditions.

Your first reply in this chat must be STARTUP_RECEIPT only (no other prose, no tools, no edits). Use the exact receipt structure and fields required by Session Unity. In that receipt, explicitly cover: startup safety (read path + live coordination files), PM/workstream fit (project vs workstream, overlap), AUTHORITY_DOCS (at least one subsystem authority doc or explicit “none — Pearl_PM must assign”), and temp/output risk (temp_or_output_paths, VM-only state, salvage vs canonical).

Coordination context (verify live; do not trust this block if the repo contradicts it):
- PROJECT_ID: proj_state_convergence_20260328
- WORKSTREAM_ID: UNKNOWN until you map the user task to a row in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` or get Pearl_PM assignment. All workstreams currently listed for this project are **preserved** or **completed** (including ws_qwen_api_unification_20260328 = completed). If you pick a preserved/completed/closed stream without explicit human override to reopen, **stop** and ask Pearl_PM.
- APPROVED BASE (project convergence lane per coordination): branch `codex/state-convergence-20260328` (verify against TSV and live `git`; Pearl_GitHub owns base/branch truth). For brand-new agent work, also respect repo golden rule: branch from `origin/main` unless an approved base/handoff explicitly overrides — if live state contradicts approved base/workstream, **stop** and report.
- WRITE_SCOPE: not pre-assigned for this chat — derive from the named authority doc(s) and registry rows after you identify the subsystem; if unclear, set WRITE_SCOPE to read-only analysis and escalate to Pearl_PM.

Likely authority entrypoints (pick what matches the task after reading DOCS_INDEX / SUBSYSTEM map):
- Repo-wide: `docs/SESSION_UNITY_PROTOCOL.md`, `docs/PEARL_PM_STATE.md`, `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`, `docs/DOCS_INDEX.md`
- Project row cites: `salvage/SALVAGE_TRIAGE_MASTER_2026_03_28.md`, `docs/QWEN_API_UNIFICATION_COMPLETION_SPEC.md` (only if the task is explicitly in that completed scope)

User task (plain English):
[PASTE YOUR PLAIN-ENGLISH TASK HERE]

Git mutations (branch, commit, push, PR, recovery): route to **Pearl_GitHub**; do not improvise git workflow outside that lane and repo preflight/push-guard rules.

**Stop without implementing** if you find: overlap with another active/partial workstream or duplicate ownership; missing or contradictory task authority; unsafe branch/worktree state; material work only in temp/output paths without a promotion path; an existing canonical doc/file that already satisfies the request; or any contradiction between live repo state and the approved base/workstream without explicit human override.

Prefer extending or correcting **existing** canonical docs and files over creating new parallel documents or artifacts.
```

---

**2.** One short note: replace `[PASTE YOUR PLAIN-ENGLISH TASK HERE]` with the real task before sending; if you want a prompt pre-bound to a specific workstream, say which one and I can tighten WORKSTREAM_ID, status warning, APPROVED BASE, and WRITE_SCOPE from the TSV row.

---

**User**

Task: implement the highest-value old-chat enhancement lane.

Use this authority:
- docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md
- docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md
- docs/BOOK_001_ASSEMBLY_CONTRACT.md

What I want:
Implement the dev lane `old_chat_v4_enforcement_upgrade` from docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md.

High-level goal:
Take the best still-missing system improvements from old_chat_specs and apply them to the live V4 planning/validation stack without creating a parallel architecture.

Required outcomes:
1. Add visible fallback reporting for assembled plans.
2. Add optional narrative_function metadata support for eligible story/reflection atoms.
3. Enforce a first useful slice of function × emotional-role or adjacent-function-diversity behavior.
4. Add a strict validation mode for protected slots like STORY when placeholder/silence appears.
5. Update the live contract doc and tests.

Use these live files as the main target set:
- phoenix_v4/planning/assembly_compiler.py
- phoenix_v4/planning/slot_resolver.py
- phoenix_v4/planning/arc_loader.py
- phoenix_v4/planning/capability_check.py
- phoenix_v4/qa/validate_compiled_plan.py
- config/format_selection/emotional_role_slot_requirements.yaml
- docs/BOOK_001_ASSEMBLY_CONTRACT.md
- tests/test_assembly_compiler.py
- tests/test_slot_resolver.py
- tests/test_arc_loader.py

Important constraints:
- do not build a second assembly system
- do not do the full 10K simulation lane in this task
- do not rewrite writer specs from scratch
- do not create a new spec if an existing canonical file can be updated
- git mutations still belong to Pearl_GitHub

Success means:
- a plan can emit a machine-readable and human-readable verification report for placeholder/silence/missing-story events
- narrative_function exists as an optional path and is covered by tests
- at least one resolver/validator rule enforces function diversity or function × emotional-role compatibility
- existing tests still pass and new tests cover the new behavior
- docs/BOOK_001_ASSEMBLY_CONTRACT.md explains the new enforcement/reporting behavior

First reply must still be STARTUP_RECEIPT only.


---

**Cursor**

Pulling the spec lane definition and coordination context so the routed prompt matches repo truth.



**1. Paste-ready startup prompt**

```
You are working in the Phoenix Omega repo.

Before anything else, read `docs/ONBOARDING_START_HERE.md` and `docs/SESSION_UNITY_PROTOCOL.md` in full and follow them exactly for startup, lane routing, receipts, and stop conditions.

Your first reply in this chat must be STARTUP_RECEIPT only (no other prose, no tools, no edits). Use the exact receipt structure and fields required by Session Unity. In that receipt, explicitly cover: startup safety (full read path + live `artifacts/coordination/ACTIVE_PROJECTS.tsv` and `ACTIVE_WORKSTREAMS.tsv`), PM/workstream fit and overlap (especially salvage / old_chat sweep lanes vs this implementation), AUTHORITY_DOCS (must include the task authority set below, plus any additional subsystem map entries you verify), and temp/output risk (no promoting parallel specs from `old_chat_specs/` or temp paths into a second assembly system).

Coordination context (verify live; stop if the repo contradicts this without explicit human override):
- PROJECT_ID: proj_state_convergence_20260328 (verify row still active; align project fit in receipt)
- WORKSTREAM_ID: UNKNOWN unless Pearl_PM assigns or you find an explicit active/partial row owning this lane. Registry rows for this project are largely **preserved** or **completed**; `ws_external_sweep_20260328` touches old_chat material but is **preserved** and scoped to read-only analysis plus archival moves — if your work would duplicate or fight that lane, **stop** and escalate to Pearl_PM.
- APPROVED BASE: confirm with live `git` (branch, clean worktree, no stale rebase/cherry-pick). Follow repo golden rule: branch from `origin/main` for new agent work unless an explicit approved base/handoff overrides; if coordination or user prefix contradicts live state, **stop** and report.
- WRITE_SCOPE (initial binding set — narrow if authority docs require): `phoenix_v4/planning/assembly_compiler.py`, `phoenix_v4/planning/slot_resolver.py`, `phoenix_v4/planning/arc_loader.py`, `phoenix_v4/planning/capability_check.py`, `phoenix_v4/qa/validate_compiled_plan.py`, `config/format_selection/emotional_role_slot_requirements.yaml`, `docs/BOOK_001_ASSEMBLY_CONTRACT.md`, `tests/test_assembly_compiler.py`, `tests/test_slot_resolver.py`, `tests/test_arc_loader.py`, plus any additional test modules you must touch only if strictly required for new behavior. Do **not** expand into the full 10K simulation lane. Do **not** add a parallel assembly architecture or new canonical spec files if an existing doc can be updated.

Task authority (read before implementation; ground design in these, not raw `old_chat_specs/` alone):
- `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md` — implement dev lane **`old_chat_v4_enforcement_upgrade`** (score 11/12); use its required deliverables and live file list as the execution contract.
- `docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md` — gap and intent reference; repo truth wins over historical notes.
- `docs/BOOK_001_ASSEMBLY_CONTRACT.md` — update this live contract to document new enforcement and reporting behavior.

Pearl_Dev task (plain English):
Implement the highest-value old-chat enhancement lane: **`old_chat_v4_enforcement_upgrade`** from `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`. Integrate the best still-missing system improvements from old_chat audit intent into the **live V4 planning/validation stack** without a parallel architecture.

Required outcomes:
1. Visible fallback reporting for assembled plans (machine-readable + human-readable verification for placeholder/silence/missing-story and related fallback events).
2. Optional `narrative_function` metadata support for eligible story/reflection atoms.
3. Enforce at least one first useful slice of function × emotional-role or adjacent-function-diversity behavior (resolver and/or validator).
4. Strict validation mode for protected slots such as STORY when placeholder/silence appears.
5. Update `docs/BOOK_001_ASSEMBLY_CONTRACT.md` and tests; existing tests must still pass; new tests must cover new behavior.

Hard constraints:
- Do not build a second assembly system.
- Do not run or implement the full 10K simulation lane here.
- Do not rewrite writer specs from scratch.
- Do not create a new spec if an existing canonical file can be updated.
- Prefer canonical docs/files over new parallel artifacts.

Git mutations (branch, commit, push, PR, recovery): **Pearl_GitHub** only; follow push-guard, preflight, and health-check rules in repo docs.

**Stop without implementing** if you find: overlapping ownership or duplicate workstream; missing or contradictory authority relative to live code; unsafe branch/worktree state; temptation to fork a parallel planner/assembly path; existing equivalent reports or metadata paths already in tree; or contradiction between approved base and live `git` without explicit human override.

Success bar: plans can emit a clear verification report for placeholder/silence/missing-story events; `narrative_function` exists as an optional path with tests; at least one resolver/validator rule enforces function diversity or function × emotional-role compatibility; strict STORY (protected-slot) mode behaves as specified; contract doc and tests reflect all of the above.
```

---

**User**

Task: implement the highest-value old-chat enhancement lane.

Use this authority:
- docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md
- docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md
- docs/BOOK_001_ASSEMBLY_CONTRACT.md

What I want:
Implement the dev lane `old_chat_v4_enforcement_upgrade` from docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md.

High-level goal:
Take the best still-missing system improvements from old_chat_specs and apply them to the live V4 planning/validation stack without creating a parallel architecture.

Required outcomes:
1. Add visible fallback reporting for assembled plans.
2. Add optional narrative_function metadata support for eligible story/reflection atoms.
3. Enforce a first useful slice of function × emotional-role or adjacent-function-diversity behavior.
4. Add a strict validation mode for protected slots like STORY when placeholder/silence appears.
5. Update the live contract doc and tests.

Use these live files as the main target set:
- phoenix_v4/planning/assembly_compiler.py
- phoenix_v4/planning/slot_resolver.py
- phoenix_v4/planning/arc_loader.py
- phoenix_v4/planning/capability_check.py
- phoenix_v4/qa/validate_compiled_plan.py
- config/format_selection/emotional_role_slot_requirements.yaml
- docs/BOOK_001_ASSEMBLY_CONTRACT.md
- tests/test_assembly_compiler.py
- tests/test_slot_resolver.py
- tests/test_arc_loader.py

Important constraints:
- do not build a second assembly system
- do not do the full 10K simulation lane in this task
- do not rewrite writer specs from scratch
- do not create a new spec if an existing canonical file can be updated
- git mutations still belong to Pearl_GitHub

Success means:
- a plan can emit a machine-readable and human-readable verification report for placeholder/silence/missing-story events
- narrative_function exists as an optional path and is covered by tests
- at least one resolver/validator rule enforces function diversity or function × emotional-role compatibility
- existing tests still pass and new tests cover the new behavior
- docs/BOOK_001_ASSEMBLY_CONTRACT.md explains the new enforcement/reporting behavior

First reply must still be STARTUP_RECEIPT only.


---

**Cursor**

Gathering the Session Unity receipt template and live coordination state to produce a compliant STARTUP_RECEIPT.



```text
STARTUP_RECEIPT
AGENT: Cursor agent (Pearl_Dev lane)
TASK: Implement dev lane `old_chat_v4_enforcement_upgrade` — V4 assembly/reporting, optional narrative_function, diversity/emotional-role slice, strict STORY validation, contract + tests; no parallel assembly stack, no 10K sim lane.
PROJECT_ID: proj_state_convergence_20260328
WORKSTREAM_ID: UNKNOWN (lane name `old_chat_v4_enforcement_upgrade` per docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md; no dedicated row in ACTIVE_WORKSTREAMS.tsv — Pearl_PM may register or confirm)
SUBSYSTEM: V4 planning / assembly / validation (phoenix_v4 planning + qa)
AUTHORITY_DOCS: docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md, docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md, docs/BOOK_001_ASSEMBLY_CONTRACT.md, docs/SESSION_UNITY_PROTOCOL.md
ADDITIONAL_SOURCES: docs/ONBOARDING_START_HERE.md, docs/SYSTEM_STATE_MASTER.md, ps.txt, docs/DOCS_INDEX.md, docs/PEARL_PM_STATE.md, artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (verify), full OLD_CHAT spec §3 deliverables B–E, live target modules under phoenix_v4/planning and phoenix_v4/qa/validate_compiled_plan.py
READ_PATH_COMPLETE: no
LIVE_REPO_STATE: branch=codex/state-convergence-20260328; dirty=yes (modified docs/BOOK_001_ASSEMBLY_CONTRACT.md); ahead_behind=unknown (fetch not run this session); temp_risk=no
ACTIVE_PROJECT_CHECK: matched proj_state_convergence_20260328 (state convergence / salvage coordination project)
ACTIVE_WORKSTREAM_CHECK: possible overlap — ws_external_sweep_20260328 is preserved and covers old_chat_specs triage as read-only/archival; this task is live-stack implementation per promotion spec — not the same deliverable, but same source domain; coordinate if scope bleeds into sweep-owned archival-only work
EXISTING_ARTIFACT_CHECK: unsure (need read of assembly_compiler, slot_resolver, validate_compiled_plan, contract for existing reporting/metadata hooks)
WRITE_SCOPE: phoenix_v4/planning/assembly_compiler.py, phoenix_v4/planning/slot_resolver.py, phoenix_v4/planning/arc_loader.py, phoenix_v4/planning/capability_check.py, phoenix_v4/qa/validate_compiled_plan.py, config/format_selection/emotional_role_slot_requirements.yaml, docs/BOOK_001_ASSEMBLY_CONTRACT.md, tests/test_assembly_compiler.py, tests/test_slot_resolver.py, tests/test_arc_loader.py — plus minimal additional tests/modules only if strictly required
OUT_OF_SCOPE: second assembly system; full 10K simulation lane; rewriting writer specs from scratch; new canonical spec files if an existing doc can be updated; git commit/push/PR (Pearl_GitHub)
SPECIALISTS_NEEDED: Pearl_Dev (implementation), Pearl_GitHub (branch/commit/push after preflight)
EVIDENCE_BASIS: docs/SESSION_UNITY_PROTOCOL.md (receipt template + rules); ACTIVE_WORKSTREAMS.tsv header + ws_external_sweep row; git branch/status/HEAD snapshot
READY_STATUS: not ready
BLOCKERS: working tree dirty before scoped edits — inspect/reconcile docs/BOOK_001_ASSEMBLY_CONTRACT.md; complete read path + authority grounding + existing-artifact pass; run git fetch and record ahead/behind before treating base as approved; full Pearl_GitHub preflight before any git mutation
GIT_PREFLIGHT: pending
```

