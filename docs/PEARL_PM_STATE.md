# Pearl_PM State

Last verified: 2026-04-01
Owner: Pearl_PM

## Purpose

This file is the fast resume point for project management routing in Phoenix Omega.

It answers:

- what is active right now
- what is blocked
- what is the next priority
- where work should continue

## Core Distinction

- **Pearl_PM = where work should continue**
- **Pearl_Architect = where work belongs**

Pearl_PM resolves overlap, active workstreams, project fit, and handoffs.
Pearl_Architect resolves subsystem ownership, governing docs, required repo sources, and architecture drift risk.

## Active Project

| Field | Value |
|-------|-------|
| **project_id** | proj_state_convergence_20260328 |
| **project_name** | State Convergence And Salvage Cleanup |
| **status** | active |
| **subsystem** | repo coordination |
| **owner** | Pearl_PM |
| **authority_docs** | docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PM_STATE.md; salvage/SALVAGE_TRIAGE_MASTER_2026_03_28.md; docs/QWEN_API_UNIFICATION_COMPLETION_SPEC.md |

## Workstream Status Summary

| workstream_id | status | owner | subsystem |
|---------------|--------|-------|-----------|
| ws_external_sweep_20260328 | completed | Pearl_PM / Pearl_GitHub | repo coordination |
| ws_recommender_promotion_20260328 | completed | Pearl_GitHub | recommendation tooling |
| ws_experience_recovery_20260328 | completed | Pearl_GitHub | planning, gating, naming |
| ws_pearl_int_recovery_20260328 | completed | Pearl_GitHub | integrations, trend feeds |
| ws_pen_name_recovery_20260328 | completed | Pearl_GitHub / Pearl_Writer / Pearl_Editor | authoring, localization |
| ws_github_prod_readiness_20260328 | completed | Pearl_GitHub | GitHub operations, release evidence |
| ws_qwen_api_unification_20260328 | completed | Pearl_GitHub / Pearl_PM | GitHub operations, Pearl News governance |
| ws_brand_admin_investor_enhancement_20260328 | completed | Pearl_Writer / Pearl_Prez / Pearl_GitHub | presentation, investor materials |
| ws_source_bank_repair_20260329 | completed | Pearl_Editor | atoms, teacher_banks |
| ws_research_citation_gaps_20260330 | active | Pearl_Research | research, docs |
| ws_research_integration_20260330 | completed | Pearl_PM / Pearl_GitHub | config, localization, payouts, catalog |
| ws_ei_v2_kb_activation_20260330 | completed | Pearl_GitHub | EI v2 |
| ws_research_pipeline_activation_20260330 | blocked | Pearl_Research | research, artifacts |
| ws_branch_consolidation_20260401 | completed | Pearl_GitHub | repo coordination |

## What Is Active

1. **ws_research_citation_gaps_20260330** -- Batch 3 LOW done (audit items 19-20). Items 1-18 and 21-22 still open. Owner: Pearl_Research.

## What Is Blocked

1. **ws_research_pipeline_activation_20260330** -- Blocked on ws_research_citation_gaps_20260330 completion. Cannot activate generational research pipeline until citation gaps are closed per RESEARCH_CITATION_GAP_DEV_SPEC section 3.

## Open Questions

- Should old_chat_specs backlog items be promoted into the scored queue?
- Whether any external worktrees still hold unique non-promoted diffs.

## Priority Ordering (Next Actions)

1. **Close remaining citation gaps** (ws_research_citation_gaps_20260330) -- audit items 1-18, 21-22. This unblocks the research pipeline.
2. **Unblock research pipeline activation** (ws_research_pipeline_activation_20260330) -- becomes actionable once citation gaps close.
3. **Evaluate old_chat_specs promotion** -- decide whether backlog items from old_chat_specs enter the scored queue or stay archived.
4. **Governance file convergence** -- ensure all referenced governance files exist and are grounded (SUBSYSTEM_AUTHORITY_MAP.tsv, SESSION_UNITY_PROTOCOL.md, this file).

## Canonical Sources

- Active projects: artifacts/coordination/ACTIVE_PROJECTS.tsv
- Active workstreams: artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- Subsystem routing: artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- Architecture routing: docs/PEARL_ARCHITECT_STATE.md
- Session startup: docs/SESSION_UNITY_PROTOCOL.md
