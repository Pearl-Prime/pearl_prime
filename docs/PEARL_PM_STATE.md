# Pearl_PM State

Last verified: 2026-04-27
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

## Active Projects

5 active projects on `ACTIVE_PROJECTS.tsv` as of 2026-04-27.

| project_id | name | subsystem | owner |
|------------|------|-----------|-------|
| proj_state_convergence_20260328 | State Convergence And Salvage Cleanup | repo coordination | Pearl_PM |
| proj_pearl_prime_bestseller_rebase_20260425 | Pearl Prime Bestseller Pipeline Rebase | pearl_prime;core_pipeline | Pearl_PM |
| proj_manga_first_ship_20260425 | Manga First-Ship — ep_001 of "The Alarm Is Lying" | manga_pipeline;integrations;video_pipeline;translation | Pearl_PM |
| proj_manga_catalog_reconciliation_20260426 | Manga Catalog Reconciliation — 12-shell × 37-brand strategic alignment (Phase 2X) | manga_pipeline;manga_catalog | Pearl_Architect |
| (audit-followup work routed under) proj_state_convergence_20260328 | covers ws_full_repo_audit_reconciliation + 7 follow-up ws rows from 2026-04-26 audit | repo coordination | Pearl_PM |

**Primary active project (Pearl_PM-owned):**

| Field | Value |
|-------|-------|
| **project_id** | proj_state_convergence_20260328 |
| **project_name** | State Convergence And Salvage Cleanup |
| **status** | active |
| **subsystem** | repo coordination |
| **owner** | Pearl_PM |
| **authority_docs** | docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PM_STATE.md; salvage/SALVAGE_TRIAGE_MASTER_2026_03_28.md; docs/QWEN_API_UNIFICATION_COMPLETION_SPEC.md; docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md |

## Workstream Status Summary

Canonical row-level truth lives in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (99 rows as of 2026-04-27, all conforming to 15-field schema after this PR's normalization of 7 previously-malformed rows). The table below mirrors that file at the **2026-04-10** snapshot for fast scanning of the older rows; **all rows added 2026-04-25 onward are not enumerated here — query the TSV directly**.

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
| ws_content_inventory_20260407 | completed | Pearl_PM / Pearl_Dev | content; observability; portal |
| ws_brand_lane_architecture_20260407 | completed | Pearl_Dev / Pearl_GitHub | brand_admin; video_pipeline; teacher_mode; ei_v2; pearl_practice |
| ws_voice_pipeline_activation_20260409 | completed | Pearl_Dev / Pearl_Research | integrations; video_pipeline; brand_admin |
| ws_video_hardening_docs_20260409 | completed | Pearl_GitHub | video_pipeline |
| ws_pearl_news_llm_routing_20260409 | completed | Pearl_Dev / Pearl_News / Pearl_Architect | pearl_news; ei_v2; integrations |
| ws_branch_cleanup_20260408 | completed | Pearl_GitHub | repo coordination |
| ws_podcast_pipeline_execution_20260409 | completed | Pearl_Dev + Pearl_Research | docs: research; config: podcast + platform_marketing; scripts/podcast; server/routes |
| ws_pr_triage_20260409 | completed | Pearl_GitHub / Pearl_PM | repo coordination |
| ws_agent_system_audit_20260409 | completed | Pearl_Architect / Pearl_PM | repo coordination |
| ws_brand_admin_gap_analysis_20260409 | completed | Pearl_Marketing / Pearl_Prez / Pearl_Research | brand_admin, recommendations |
| ws_topic_registries_20260409 | completed | Pearl_Prime / Pearl_Writer | core_pipeline;teacher_mode |
| ws_full_funnel_system_20260410 | completed | Pearl_Marketing + Pearl_PM + Pearl_Dev | brand_admin;core_pipeline;recommendations |
| ws_teacher_manga_triptych_20260410 | active | Pearl_Dev + Pearl_Video | manga_pipeline;brand_admin |
| ws_unified_pipeline_jobs_20260410 | completed | Pearl_GitHub + Pearl_Dev + Pearl_Architect | core_pipeline;video_pipeline;manga_pipeline;podcast_pipeline |
| ws_funnel_activation_20260410 | completed | Pearl_GitHub + Pearl_Dev + Pearl_Marketing | brand_admin;core_pipeline;integrations |
| ws_p1_health_audit_20260410 | completed | Pearl_Architect + Pearl_PM + Pearl_GitHub | repo coordination |
| ws_ci_fix_20260410 | completed | Pearl_Dev + Pearl_GitHub | core_pipeline |
| ws_atom_gap_fill_20260410 | pending | Pearl_Editor + Pearl_Writer | atoms;teacher_mode |
| ws_pipeline_verification_audit_20260410 | completed | Pearl_Architect | core_pipeline;video_pipeline;manga_pipeline;podcast_pipeline;audiobook |
| ws_tts_provider_hardening_20260410 | active | Pearl_GitHub | video_pipeline |

## What Is Active

Carried over (unchanged since 2026-04-10):

1. **ws_research_citation_gaps_20260330** — Close remaining citation gaps per `docs/RESEARCH_CITATION_GAP_DEV_SPEC.md` (Batch 3 LOW done; §A 1–18 and 21–22 still open). Owner: Pearl_Research.
2. **ws_teacher_manga_triptych_20260410** — Teacher showcase FLUX triptych (portrait, scene, symbolic), ComfyUI on Pearl Star, HTML grid. Owners: Pearl_Dev + Pearl_Video.

Audit follow-up (added 2026-04-27 from `docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md`):

3. **ws_coord_refresh_pm_state_20260427** — This PR. Refresh PEARL_PM_STATE + 7 schema fixes + 7 new ws rows. Owner: Pearl_PM.
4. **ws_subsystem_authority_fills_20260427** — Add 4 missing subsystems to authority map; document brand canon = 37 + dashboard routing in PEARL_ARCHITECT_STATE. Owner: Pearl_Architect.
5. **ws_pr_governance_workflow_wiring_20260427** — Wire `pr_governance_review.py` to a GitHub Actions workflow. Owner: Pearl_DevOps. Closes GAP-G1.
6. **ws_d1_dead_code_cluster_deletion_20260427** — PR D1.bcdefgh: `pearl_news copy/`, `del_*/`, `deli/`, `delf/`, `files-4/` (~25 files). Owner: Pearl_GitHub.
7. **ws_brand_count_canon_reconciliation_20260427** *(proposed)* — Reconcile brand-count canon to 37 per PR #682 spec. Owner: Pearl_Brand.
8. **ws_dashboard_subsystem_routing_20260427** *(proposed)* — Pearl_Architect picks canonical home for `dashboard/` (decision 9b: revive). Owner: Pearl_Architect.
9. **ws_podcast_pipeline_execution_20260427** *(proposed)* — 12-16 day buildout per `docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md` (decision 11a). Owners: Pearl_Prime + Pearl_Int + Pearl_GitHub.

Carried over from earlier:

10. **ws_tts_provider_hardening_20260410** — Narrow follow-up: soundtrack_plan ElevenLabs URL from `config/tts/locale_voice_routing.yaml` (no hardcoded host). Owner: Pearl_GitHub.

## What Is Pending

1. **ws_atom_gap_fill_20260410** — Fill P0 atom gaps from the P1 health audit (QUOTE+TEACHING atoms and persona×topic zero-atom combos). Owners: Pearl_Editor + Pearl_Writer. Evidence: `artifacts/audit/P1_NEXT_STEPS_2026_04_10.md`.

## What Is Blocked

1. **ws_research_pipeline_activation_20260330** — Blocked on `ws_research_citation_gaps_20260330` completion. Cannot activate the generational research pipeline until citation gaps are closed per RESEARCH_CITATION_GAP_DEV_SPEC section 3.

## Open Questions

- Should old_chat_specs backlog items be promoted into the scored queue?
- Whether any external worktrees still hold unique non-promoted diffs.

## Priority Ordering (Next Actions)

1. **Close remaining citation gaps** (`ws_research_citation_gaps_20260330`) — audit items 1–18, 21–22. This unblocks the research pipeline.
2. **Unblock research pipeline activation** (`ws_research_pipeline_activation_20260330`) — becomes actionable once citation gaps close.
3. **Evaluate old_chat_specs promotion** — decide whether backlog items from old_chat_specs enter the scored queue or stay archived.
4. **Governance file convergence** — keep this file, `SUBSYSTEM_AUTHORITY_MAP.tsv`, and `SESSION_UNITY_PROTOCOL.md` aligned with `ACTIVE_WORKSTREAMS.tsv` (this doc is a summary only; the TSV wins on conflict).
5. **Atom gap fill** (`ws_atom_gap_fill_20260410`) — execute per `artifacts/audit/P1_NEXT_STEPS_2026_04_10.md` once Pearl_Editor + Pearl_Writer are queued.

## Canonical Sources

- Active projects: artifacts/coordination/ACTIVE_PROJECTS.tsv
- Active workstreams: artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- Subsystem routing: artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- Architecture routing: docs/PEARL_ARCHITECT_STATE.md
- Session startup: docs/SESSION_UNITY_PROTOCOL.md
