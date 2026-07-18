# Agent System Improvement Spec

**Status:** Dev-ready outline (2026-04-09)  
**Companion:** `docs/AGENT_SYSTEM_AUDIT_2026_04.md`  
**Authority for session protocol:** `docs/SESSION_UNITY_PROTOCOL.md` (lines 13–29 STARTUP_RECEIPT template)

---

## 1. Purpose

Implement the P0/P1 recommendations from the audit:

1. Machine-readable roster: `config/agents/agent_registry.yaml`
2. Human dispatch rules: `docs/AGENT_DISPATCH_PROTOCOL.md` (new file — **section 3 is the full outline to paste into that doc**)
3. Optional handoff contract: `docs/AGENT_HANDOFF_SPEC.md` (new file — **section 4**)
4. SKILL.md files for agents still informal (**separate PRs per agent**; templates in section 2)

**Non-negotiable:** Pearl_GitHub push-guard, preflight, and branch-from-`origin/main` rules remain as in `skills/pearl-github/SKILL.md` (STEP 0–2). No SKILL may contradict `docs/GITHUB_OPERATIONS_FRAMEWORK.md` required checks matrix without a governance PR.

---

## 2. SKILL.md template (match `skills/pearl-github/SKILL.md` depth)

Each new skill should use this YAML front matter pattern (copy from `skills/pearl-int/SKILL.md` lines 1–4, `skills/deep-research/SKILL.md` lines 1–16):

```yaml
---
name: pearl-<short-name>
description: >
  One paragraph: when to load this skill, what NOT to use it for,
  mandatory sister-agent handoffs (e.g. Pearl_GitHub for git).
---
```

### 2.1 Required sections inside the Markdown body

1. **Identity** — who this agent is in Phoenix Omega (one paragraph).
2. **Sister agents** — bullet list mirroring `skills/pearl-github/SKILL.md` lines 20–26 style.
3. **Authority docs** — table: path | why read it.
4. **Config paths** — may read/write (from `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` where applicable).
5. **Code paths** — primary Python/scripts dirs (high level).
6. **STEP 0: Preflight** — commands or read order **before** edits.
7. **Boundaries** — MUST NOT (bullets); escalation triggers (Pearl_GitHub / Pearl_PM / Pearl_Architect).
8. **File persistence** — if agent touches atoms/content: cite `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` lines 97–112 block.
9. **FILES YOU OWN** — table (like `skills/pearl-github/SKILL.md` lines 463–479).

### 2.2 Priority order for authoring SKILL.md files (P0 implementation sequence)

| Order | Agent | Rationale |
|-------|-------|-----------|
| 1 | Pearl_Prime | Podcast Gap 7 owners + core pipeline map rows |
| 2 | Pearl_Dev | ITE prompt + manga/ITE map rows + frequent multi-agent WS |
| 3 | Pearl_News | Distinct civics/journalism rules (`docs/PEARL_NEWS_WRITER_SPEC.md` lines 26–39) |
| 4 | Pearl_PM | State file exists; needs operational checklist skill |
| 5 | Pearl_Architect | Drift pattern catalog from `docs/PEARL_ARCHITECT_STATE.md` lines 35–44 |

Defer Pearl_Video / Pearl_Localization / Pearl_Marketing / Pearl_Prez / Pearl_Writer / Pearl_Editor to P1 unless a workstream spikes demand.

---

## 3. `docs/AGENT_DISPATCH_PROTOCOL.md` — full outline (create this file next)

**Title:** Agent Dispatch Protocol for Phoenix Omega

### 3.1 Roles

- **Human operator** — selects task.
- **Router session** (may be Pearl_PM + Pearl_Architect) — resolves subsystem, emits paste-ready prompt; **never** invents paths — verify with `test -f` or repo search.
- **Executor agent** — follows STARTUP_RECEIPT; stays in WRITE_SCOPE.

### 3.2 Minimum resolver algorithm

1. Read `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — if `status=active` on target subsystem, **prepend conflict warning** to prompt.
2. Look up `subsystem_id` in `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`; if missing, fall through to `docs/DOCS_INDEX.md` task table (`docs/DOCS_INDEX.md` lines 13–27).
3. Load `owner_agent` from `config/agents/agent_registry.yaml` (new) — if `skill_path` non-null, include skill in read list.
4. If task touches `.github/`, `scripts/git/`, PR, merge: **force Pearl_GitHub** in loop per `docs/OWNERSHIP_MATRIX.md` lines 16–23.

### 3.3 Paste-ready prompt shell

Embed `docs/SESSION_UNITY_PROTOCOL.md` lines 17–29 STARTUP_RECEIPT template verbatim.

Include **Preflight block** from `skills/pearl-github/SKILL.md` lines 39–60 when any git operation is anticipated.

### 3.4 Persistence block for content agents

When target agent is Pearl_Writer, Pearl_Editor, or Pearl_Dev writing user-facing files: append `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` lines 101–112.

### 3.5 Merge governance reminder

Before any merge approval: `gh pr diff <number> --stat | tail -1` — if deletions > 50 files, STOP (per `CLAUDE.md` non-negotiable rules).

---

## 4. `docs/AGENT_HANDOFF_SPEC.md` — outline (create next)

1. **Trigger:** Multi-agent `owner_agent` string in `ACTIVE_WORKSTREAMS.tsv` (e.g. `Pearl_Dev / Pearl_News / Pearl_Architect`).
2. **Primary for this commit:** Exactly one agent name in CLOSEOUT_RECEIPT `HANDOFF_TO` or inline in PR description.
3. **Artifact continuity:** Next agent must accept: branch name, last commit SHA, list of failing CI checks (if any).
4. **Blocked state:** Must reference blocker column semantics already used for research pipeline (`docs/PEARL_PM_STATE.md` lines 59–61).

---

## 5. `config/agents/agent_registry.yaml` — schema

```yaml
# Schema version for validators (future scripts/ci/check_agent_registry.py)
schema_version: "1.0"

agents:
  <snake_case_id>:
    display_name: "Pearl_X"           # Human label
    skill_path: <path | null>         # e.g. skills/pearl-github/SKILL.md
    state_docs: [<paths>]             # e.g. docs/PEARL_GITHUB_STATE.md
    subsystems: [<subsystem_id>]      # keys from SUBSYSTEM_AUTHORITY_MAP.tsv
    authority_docs: [<paths>]         # governing specs
    status: formalized | partial | mentioned
    notes: <optional string>
```

**Validation rules (future):**

- Every `subsystem_id` in `SUBSYSTEM_AUTHORITY_MAP.tsv` must appear in exactly one agent’s `subsystems` list unless explicitly shared (document exception in `notes`).
- `skill_path` must be null or an existing file.

Initial population: see **`config/agents/agent_registry.yaml`** in repo (committed with this spec).

---

## 6. Merge implementation plans

### 6.1 No org-agent merges in P0

Audit rejected Pearl_Dev+Pearl_Prime, Pearl_PM+Pearl_Architect, Pearl_Prez+Pearl_Marketing merges — see `docs/AGENT_SYSTEM_AUDIT_2026_04.md` Part A.2.

### 6.2 Optional doc-only “playbook merge”

If the owner wants a **single onboarding doc** for Writer+Editor without merging agents: add `docs/AUTHORING_PLAYBOOK.md` that links to `specs/PHOENIX_V4_5_WRITER_SPEC.md` and `docs/SYSTEMS_V4.md` (teacher_mode authority per map) — **no code moves**.

---

## 7. Router formalization plan

| Phase | Action |
|-------|--------|
| P0 | Land `agent_registry.yaml` + dispatch protocol doc |
| P1 | Add optional `skills/pearl-router/SKILL.md` if human routers skipdispatch steps |
| P2 | Script: suggest agent from `git diff --name-only` against registry `code_globs` (extend field in registry v1.1) |

---

## 8. SUBSYSTEM_AUTHORITY_MAP extension proposal (governance PR)

Add rows (exact wording subject to owner edit):

| subsystem_id | authority_doc | config_path | owner_agent |
|--------------|---------------|--------------|-------------|
| repo_coordination | docs/SESSION_UNITY_PROTOCOL.md;docs/GITHUB_OPERATIONS_FRAMEWORK.md | artifacts/coordination/*.tsv;docs/PEARL_*_STATE.md | Pearl_PM |
| github_operations | docs/GITHUB_OPERATIONS_FRAMEWORK.md;docs/BRANCH_PROTECTION_REQUIREMENTS.md | .github/workflows/;scripts/git/ | Pearl_GitHub |
| consumer_marketing | docs/DOCS_INDEX.md (marketing sections) | config/marketing/* (when present) | Pearl_Marketing |

**Do not** fold Pearl_GitHub under Pearl_PM: ownership matrix reserves workflows for repo governance (`docs/OWNERSHIP_MATRIX.md` lines 16–18).

---

## 9. Acceptance criteria (this improvement spec)

- [ ] `config/agents/agent_registry.yaml` exists and validates on `main`
- [ ] `docs/AGENT_DISPATCH_PROTOCOL.md` created from section 3 above
- [ ] At least two new `skills/pearl-*/SKILL.md` land for P0 agents (Pearl_Prime, Pearl_Dev)
- [ ] `SUBSYSTEM_AUTHORITY_MAP.tsv` updated in a dedicated governance PR if section 8 approved
