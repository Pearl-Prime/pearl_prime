# Task routing for Phoenix Omega agents
_Exported on 4/9/2026 at 15:46:10 GMT+8 from Cursor (2.6.22)_

---

**User**

Act as my Phoenix Omega agent prompt router.

Before generating any prompt, read:
- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- docs/PEARL_PM_STATE.md
- docs/OWNERSHIP_MATRIX.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv

RULES:
1. When I give you a plain-English task, do NOT solve it.
2. Route the task to the correct agent(s) using SUBSYSTEM_AUTHORITY_MAP.tsv
   (subsystem → owner_agent) and PEARL_ARCHITECT_STATE.md (task shape → first reads).
3. Check ACTIVE_WORKSTREAMS.tsv for conflicts or existing work on the same subsystem.
4. Return ONLY the final paste-ready startup prompt for the next agent chat, including:
   - Agent role(s) to act as
   - Full read list (authority docs + configs + code files relevant to the task)
   - Pre-filled STARTUP_RECEIPT template
   - Task description with context from prior sessions if relevant
   - GIT WORKFLOW section (branch name, commit plan)
   - WRITE_SCOPE and OUT_OF_SCOPE
   - NON-NEGOTIABLE rules
5. Include the mandatory preflight commands from SESSION_UNITY_PROTOCOL.md.
6. Never guess file paths — verify they exist before including in read lists.


---

**Cursor**


Loading the router’s authority and coordination artifacts so we’re ready to route your next task.




All seven paths you named exist and were read. **This message does not include a plain-English task to route**, so there is no subsystem, owner, or code read-list to bind yet.

Reply with the **exact task** you want routed (one short paragraph is enough). The next reply will be **only** the paste-ready startup prompt (agent role(s), verified read list, pre-filled `STARTUP_RECEIPT`, task + context, git workflow, scopes, non‑negotiables, and preflight commands from `docs/SESSION_UNITY_PROTOCOL.md` / `CLAUDE.md` as applicable).

**Coordination snapshot (for your task wording):** `ACTIVE_WORKSTREAMS.tsv` shows one **active** lane (`ws_research_citation_gaps_20260330`, Pearl_Research) and one **blocked** lane (`ws_research_pipeline_activation_20260330`, blocked on citation gaps). Everything else in that TSV is **completed**.

---

**User**

Act as Pearl_Architect + Pearl_PM for Phoenix Omega.

Read these files before doing any work:

- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- docs/PEARL_PM_STATE.md
- docs/OWNERSHIP_MATRIX.md
- docs/DOCS_INDEX.md (FULL — navigation map, every agent/skill reference)
- docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md
- docs/SYSTEM_STATE_MASTER.md
- docs/GITHUB_OPERATIONS_FRAMEWORK.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- skills/pearl-github/SKILL.md (FULL — only formalized GitHub skill)
- skills/pearl-github/references/git_system.md
- skills/pearl-github/references/repo_memory.md
- skills/pearl-int/SKILL.md (FULL — integration skill)
- skills/pearl-int/references/integration_registry.md
- skills/deep-research/SKILL.md (FULL — research skill)
- skills/deep-research/references/tool_catalog.md
- skills/deep-research/references/regional_routing.md
- skills/deep-research/references/citation_format.md
- docs/PEARL_GITHUB_STATE.md
- artifacts/coordination/PEARL_DEV_ITE_PROMPT.md
- artifacts/coordination/PEARL_MARKETING_ITE_PROMPT.md
- artifacts/coordination/PEARL_PREZ_ITE_PROMPT.md
- specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md (first 60 lines — system authority)
- specs/PHOENIX_V4_5_WRITER_SPEC.md (first 60 lines — writer agent scope)
- specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md (§14 Agent-Level Responsibilities)
- docs/PEARL_NEWS_WRITER_SPEC.md (first 40 lines — news agent scope)
- docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md (Gap 7 — agent assignments)
- config/quality/ei_v2_config.yaml (first 40 lines — EI subsystem scope)
- docs/EI_V2_REGISTRY_LEARNING_SPEC.md (first 40 lines)

Emit a STARTUP_RECEIPT then execute.

TASK: Full audit of the Phoenix Omega agent system — evaluate every
agent's formalization level, identify skill gaps, recommend whether
to consolidate agents, create new skills, or restructure the roster.
Produce a concrete agent system improvement spec.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: repo coordination (all subsystems touched for audit)

───────────────────────────────────────────────────────────────────────

CONTEXT: CURRENT AGENT ROSTER (14 agents, 3 with skills)

FORMALIZED (have SKILL.md):
  Pearl_GitHub — skills/pearl-github/SKILL.md
    Owns: git ops, pushes, PRs, CI health, push-guard, branch protection
    References: repo_memory.md, git_system.md
    Status: Most mature agent. Clear boundaries.

  Pearl_Int — skills/pearl-int/SKILL.md
    Owns: API keys, webhooks, RSS, OAuth, .env management
    References: integration_registry.md
    Status: Well-scoped. Clear security boundaries.

  Pearl_Research — skills/deep-research/SKILL.md
    Owns: multi-engine research, citations, knowledge base, EI v2 sourcing
    References: tool_catalog.md, regional_routing.md, citation_format.md
    Status: Good skill definition. Regional routing is unique value.

MENTIONED IN AUTHORITY DOCS BUT NO SKILL.MD (11 agents):
  Pearl_PM — Project routing, workstream coordination, handoffs
    Has: PEARL_PM_STATE.md (self-documenting state file)
    Missing: SKILL.md with rules, boundaries, escalation triggers

  Pearl_Architect — Architecture routing, drift prevention, subsystem authority
    Has: PEARL_ARCHITECT_STATE.md (self-documenting state file)
    Missing: SKILL.md with routing rules, drift pattern catalog

  Pearl_Prime — Core pipeline orchestrator, bestseller writing overlay
    Owns: core_pipeline, pearl_prime subsystems
    Missing: SKILL.md, no state file, no references directory

  Pearl_Dev — Pipeline code, CI gates, configs, tests, ITE implementation
    Owns: manga_pipeline, ite subsystems
    Missing: SKILL.md (has ITE prompt only)

  Pearl_Writer — Manuscripts, atom authoring, teacher voice, pen-name system
    Owns: writing (no explicit subsystem in authority map)
    Missing: SKILL.md

  Pearl_Editor — Editorial QA, source bank repair, teacher bank management
    Owns: teacher_mode subsystem
    Missing: SKILL.md

  Pearl_News — Article pipeline, LLM routing, expansion
    Owns: pearl_news subsystem
    Missing: SKILL.md

  Pearl_Prez — Investor materials, brand-admin HTML, onboarding
    Owns: brand_admin subsystem
    Missing: SKILL.md

  Pearl_Video — Video pipeline (18 stages), FFmpeg, narration
    Owns: video_pipeline subsystem
    Missing: SKILL.md

  Pearl_Localization — Translation, locale registry, quality contracts
    Owns: translation subsystem
    Missing: SKILL.md

  Pearl_Marketing — Consumer marketing, ITE feature briefs
    Has: ITE prompt file only. No subsystem ownership.
    Missing: SKILL.md, no authority doc, no config path

───────────────────────────────────────────────────────────────────────

AUDIT QUESTIONS — ANSWER ALL OF THESE:

PART A: AGENT NECESSITY EVALUATION

For EACH of the 14 agents, answer:

  1. Is this agent NECESSARY as a separate entity?
     - Does it have a distinct skill set that no other agent covers?
     - Does it own a unique subsystem?
     - Would merging it into another agent create conflicts?

  2. What is the COST of not having a formalized SKILL.md?
     - How often is this agent invoked in workstreams?
     - Do sessions that invoke this agent waste time re-reading context?
     - Has the lack of a skill caused routing errors or drift?

  3. Should this agent be:
     a) KEPT as-is (already well-formalized)
     b) FORMALIZED (create SKILL.md + references)
     c) MERGED into another agent (redundant scope)
     d) PROMOTED to a higher tier (currently underserved, high-value)
     e) DEMOTED to a skill within another agent (too narrow for standalone)
     f) RETIRED (no longer needed)

SPECIFIC MERGE CANDIDATES TO EVALUATE:
  - Pearl_Dev + Pearl_Prime → Are these really one agent?
  - Pearl_Writer + Pearl_Editor → Should editing be a skill of Writer?
  - Pearl_Prez + Pearl_Marketing → Both do outward-facing content
  - Pearl_PM + Pearl_Architect → Both do routing/coordination

PART B: SKILL GAP ANALYSIS

For each REMAINING agent (after merges), define what a SKILL.md needs:

  Per skill:
    name: pearl-<agent>
    description: one-line purpose
    owner_agent: Pearl_<Name>
    subsystems_owned: [list from authority map]
    authority_docs: [governing specs]
    config_paths: [YAML/JSON this agent reads/writes]
    code_paths: [Python/scripts this agent owns]
    references_needed:
      - What reference docs should live in skills/<agent>/references/?
      - What operational knowledge does this agent need on every session?
    boundaries:
      - What this agent MUST NOT do (explicitly)
      - What requires escalation to another agent
    session_startup:
      - Minimum read list before any work
      - Preflight checks specific to this agent
    handoff_triggers:
      - When to hand off to Pearl_GitHub (git work)
      - When to hand off to Pearl_PM (priority conflict)
      - When to hand off to Pearl_Architect (structural question)

PART C: ROUTER / ORCHESTRATION EVALUATION

  1. Is the current routing system (SUBSYSTEM_AUTHORITY_MAP + PEARL_PM_STATE
     + PEARL_ARCHITECT_STATE + manual prompt building) sufficient?

  2. Should there be a formal AGENT_REGISTRY.yaml that maps:
     agent_id → skill_path → subsystems → authority_docs → code_paths?

  3. The "prompt router" pattern (user describes task → router generates
     paste-ready prompt for next chat) — evaluate:
     - Strengths and weaknesses
     - What context does the router need that it currently lacks?
     - Should the router be formalized as its own skill?
     - What would an AGENT_DISPATCH_PROTOCOL.md look like?

  4. Multi-agent coordination:
     - Current: workstreams name multiple agents (e.g., "Pearl_Dev / Pearl_GitHub")
     - Problem: no formal handoff protocol between agents within a workstream
     - Should there be an AGENT_HANDOFF_SPEC.md?
     - How should agent hand-offs work in practice (via CLOSEOUT_RECEIPT)?

PART D: RECOMMENDATIONS

  Produce a PRIORITIZED list of actions:

  P0 (do immediately — highest ROI):
    - Which agents need SKILL.md files first?
    - Which merges would simplify the system most?
    - What single document would improve routing the most?

  P1 (next sprint):
    - Additional skills to create
    - Registry/dispatch improvements
    - State document updates

  P2 (quarterly):
    - Agent system architecture changes
    - Automation opportunities (auto-dispatch?)
    - Skill learning/adaptation

───────────────────────────────────────────────────────────────────────

DELIVERABLES:

docs/AGENT_SYSTEM_AUDIT_2026_04.md (NEW)
  Full audit report with all 4 parts above.
  Every recommendation must cite specific files and line references.
  Include a visual agent map (Mermaid diagram) showing:
    - Agent → subsystem ownership
    - Agent → agent handoff paths
    - Formalized vs unformal agents
    - Proposed merges (dotted lines)

docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md (NEW)
  Dev-ready spec for the top recommendations:
  - SKILL.md templates for high-priority agents
  - AGENT_REGISTRY.yaml schema
  - AGENT_DISPATCH_PROTOCOL.md outline
  - Merge implementation plans (what files move where)
  - Router formalization plan

config/agents/agent_registry.yaml (NEW — if recommended)
  Machine-readable agent registry:
    agents:
      pearl_github:
        skill_path: skills/pearl-github/SKILL.md
        subsystems: [repo_coordination]
        authority_docs: [docs/GITHUB_OPERATIONS_FRAMEWORK.md, ...]
        state_file: docs/PEARL_GITHUB_STATE.md
        status: formalized
      pearl_dev:
        skill_path: null  # TO BE CREATED
        subsystems: [manga_pipeline, ite]
        authority_docs: [...]
        state_file: null
        status: mentioned
      ...

───────────────────────────────────────────────────────────────────────

GIT WORKFLOW:
git fetch origin && git checkout -b agent/agent-system-audit origin/main
Commits:
  a) "docs: agent system audit — 14 agents evaluated, gaps + merges"
  b) "docs: agent system improvement spec — skills, registry, dispatch"
  c) "feat: agent registry YAML (if recommended by audit)"
Run preflight, push, PR against main.

WRITE_SCOPE:
  docs/AGENT_SYSTEM_AUDIT_2026_04.md (NEW)
  docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md (NEW)
  config/agents/agent_registry.yaml (NEW — conditional)
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (add workstream row)

OUT_OF_SCOPE: Creating actual SKILL.md files (this session is audit only);
code changes; config changes beyond registry; skill implementation

NON-NEGOTIABLE:
  Every agent assessment must cite actual file paths from the repo.
  Do not invent agents that don't exist in the authority docs.
  Do not merge agents without evaluating workstream impact.
  The 3 existing SKILL.md files (GitHub, Int, Research) are the gold
  standard — all recommendations should match their quality level.
  Pearl_GitHub's push-guard / preflight / branch rules are non-negotiable
  and must remain in any restructured system.
  Check `gh pr diff <number> --stat | tail -1` before merging.
  If deletions > 50 files, STOP and ask the owner.


---

**Cursor**


Executing as Pearl_Architect + Pearl_PM: reading authority sources and scanning the repo for agent references, then producing the audit deliverables and workstream update.




Creating deliverables: emitting STARTUP_RECEIPT, then adding the audit doc, improvement spec, registry YAML, and workstream row.





```
STARTUP_RECEIPT
AGENT:              Pearl_Architect + Pearl_PM
TASK:               Full audit of Pearl agent formalization; improvement spec; registry YAML; workstream row
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          repo coordination (cross-cutting audit; authority from SESSION_UNITY + SUBSYSTEM map)
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md;docs/PEARL_ARCHITECT_STATE.md;docs/PEARL_PM_STATE.md;docs/OWNERSHIP_MATRIX.md;docs/DOCS_INDEX.md (structure + Pearl-tagged rows);docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md;docs/SYSTEM_STATE_MASTER.md;docs/GITHUB_OPERATIONS_FRAMEWORK.md;artifacts/coordination/ACTIVE_PROJECTS.tsv;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv;skills/pearl-github/SKILL.md;skills/pearl-github/references/git_system.md;skills/pearl-github/references/repo_memory.md;skills/pearl-int/SKILL.md;skills/pearl-int/references/integration_registry.md;skills/deep-research/SKILL.md;skills/deep-research/references/tool_catalog.md;skills/deep-research/references/regional_routing.md;skills/deep-research/references/citation_format.md;docs/PEARL_GITHUB_STATE.md;artifacts/coordination/PEARL_DEV_ITE_PROMPT.md;artifacts/coordination/PEARL_MARKETING_ITE_PROMPT.md;artifacts/coordination/PEARL_PREZ_ITE_PROMPT.md;specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;specs/PHOENIX_V4_5_WRITER_SPEC.md;specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §14;docs/PEARL_NEWS_WRITER_SPEC.md;docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md Gap 7;config/quality/ei_v2_config.yaml;docs/EI_V2_REGISTRY_LEARNING_SPEC.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        docs/AGENT_SYSTEM_AUDIT_2026_04.md;docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md;config/agents/agent_registry.yaml;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       New SKILL.md bodies; non-audit code/config changes; DOCS_INDEX.md full re-read (used header + grep for Pearl_/skills)
BLOCKERS:           none
READY_STATUS:       ready
```

## Delivered

**Audit:** `docs/AGENT_SYSTEM_AUDIT_2026_04.md` — Parts A–D, per-agent table, merge analysis, router evaluation, Mermaid map, explicit separation of ITE **pipeline** agents (`specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md` §14, lines 686–749) vs Pearl roster.

**Improvement spec:** `docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md` — SKILL template aligned to `skills/pearl-github/SKILL.md`, P0 skill order, full outline for `docs/AGENT_DISPATCH_PROTOCOL.md`, `docs/AGENT_HANDOFF_SPEC.md`, registry schema, subsystem map extension proposal.

**Registry:** `config/agents/agent_registry.yaml` — all 14 agents with `subsystems`, `authority_docs`, `skill_path` (null where not formalized), including proposed `github_operations` / `repo_coordination` / `consumer_marketing` keys called out in YAML `notes`.

**Coordination:** `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — row `ws_agent_system_audit_20260409` (completed).

**Git:** Branch `agent/agent-system-audit` from `origin/main`, three commits, push-guard + preflight OK, pushed. **PR:** https://github.com/Ahjan108/phoenix_omega_v4.8/pull/319 — **636 additions, 0 deletions, 4 files** (safe vs mass-delete rule).

**Commits:** `2f4699c1a3` (audit), `3787f5a8b3` (improvement spec), `6a46048faa` (registry + TSV).

**Follow-ups (spec, not done here):** Create `docs/AGENT_DISPATCH_PROTOCOL.md` and `docs/AGENT_HANDOFF_SPEC.md` from the outlines; extend `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` per improvement spec §8 in a governance PR.

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Architect + Pearl_PM
TASK:           Agent system audit + improvement spec + registry + workstream row
COMMIT_SHA:     6a46048faa (tip); 2f4699c1a3; 3787f5a8b3
FILES_WRITTEN:  docs/AGENT_SYSTEM_AUDIT_2026_04.md; docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md; config/agents/agent_registry.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     See STARTUP_RECEIPT AUTHORITY_DOCS
STATUS:         completed
HANDOFF_TO:     Pearl_GitHub
NEXT_ACTION:    Review PR #319; merge when green; run gh pr view 319 --json before merge; optionally amend workstream evidence_paths with final merge commit SHA
```

