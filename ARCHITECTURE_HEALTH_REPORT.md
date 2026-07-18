# Architecture Health Report

**Date:** 2026-04-01
**Auditor:** Pearl_Architect (automated)
**Branch:** main (bb6ce281)
**Scope:** Full system architecture health audit per PEARL_ARCHITECT_STATE.md

---

## Executive Summary

The Phoenix Omega architecture is **structurally sound at the core** -- the canonical authority chain (Arc-First spec, DOCS_INDEX, SYSTEMS_V4, OWNERSHIP_MATRIX) is intact, and the vast majority of referenced files exist on disk. However, there are **three critical gaps** and **several moderate issues** that create routing confusion and incomplete architecture coverage.

**Critical findings:** 3
**High findings:** 4
**Medium findings:** 5
**Low findings:** 3

---

## 1. CRITICAL: Missing Architecture Anchor Files (Not on `main`)

### 1.1 SUBSYSTEM_AUTHORITY_MAP.tsv -- Never Merged

**Severity:** CRITICAL
**File:** `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
**Status:** Referenced as canonical anchor #5 in `docs/PEARL_ARCHITECT_STATE.md` but **does not exist on `main`**. Was created on branch `agent/verify-and-fix` (commit 07810fff) but never merged.

**Impact:** PEARL_ARCHITECT_STATE.md says "When routing a task, start here" and lists this file as a shortcut map. Without it, subsystem routing falls back entirely to DOCS_INDEX (which works, but the promised fast-path shortcut is broken). Additionally, this audit cannot verify subsystem authority_doc and config_path coverage because the map itself is missing.

**Fix:** Merge the SUBSYSTEM_AUTHORITY_MAP.tsv from `agent/verify-and-fix` to main via a clean PR, or regenerate it from current state.

### 1.2 SESSION_UNITY_PROTOCOL.md -- Never Merged

**Severity:** CRITICAL
**File:** `docs/SESSION_UNITY_PROTOCOL.md`
**Status:** Referenced by ACTIVE_PROJECTS.tsv (authority_docs column for proj_state_convergence), by ACTIVE_WORKSTREAMS.tsv (multiple workstreams), and by PEARL_ARCHITECT_STATE.md ("Keep Pearl_Architect docs aligned with SESSION_UNITY_PROTOCOL.md"). Only exists on `agent/verify-and-fix`.

**Impact:** The protocol that governs session state convergence and agent coordination is not on main. Any agent resuming from main state cannot access it.

**Fix:** Merge to main via PR.

### 1.3 PEARL_PM_STATE.md -- Never Merged

**Severity:** CRITICAL
**File:** `docs/PEARL_PM_STATE.md`
**Status:** Referenced in PEARL_ARCHITECT_STATE.md (task shape table: "Recovery / overlap / salvage -> Start here: docs/PEARL_PM_STATE.md"). Only exists on `agent/verify-and-fix`.

**Impact:** Pearl_PM fast-resume is broken. Recovery and overlap routing has no entry point.

**Fix:** Merge to main via PR.

---

## 2. HIGH: DOCS_INDEX Stale References

### 2.1 Phoenix Recommender Marked as "Backlog" but Exists

**Severity:** HIGH
**Files affected:** 7 files listed as "Backlog ... not present" in DOCS_INDEX that **do exist** on main:

| DOCS_INDEX says absent | Actually present |
|------------------------|-----------------|
| `phoenix_recommender/candidate_generator.py` | Yes |
| `phoenix_recommender/scoring_model.py` | Yes |
| `phoenix_recommender/recommendation_report.py` | Yes |
| `phoenix_recommender/cli.py` | Yes |
| `config/recommender/scoring_weights.yaml` | Yes |
| `config/recommender/constraints.yaml` | Yes |
| `config/recommender/hard_gates.yaml` | Yes |

Two files remain genuinely absent: `phoenix_recommender/feature_builder.py` and `phoenix_recommender/ranker.py`.

**Impact:** Developers following DOCS_INDEX believe the recommender is unimplemented and skip it. The index misrepresents current state.

**Fix:** Update the "Phoenix Recommender (document all)" section in DOCS_INDEX to reflect that the package exists on main, and mark only the two genuinely missing modules.

### 2.2 DOCS_INDEX Last Updated Date is Stale

**Severity:** HIGH
**Detail:** DOCS_INDEX says "Last updated: 2026-03-30" but significant merges have landed since (PR #144, #145, #147, #150, #151 through 2026-04-01). The index does not reference integration credentials registry, video upload/publish, or brand-wizard polish.

**Fix:** Update DOCS_INDEX with recent merges and reset the date.

### 2.3 Salvage Files Referenced in ACTIVE_WORKSTREAMS but Not on Main

**Severity:** HIGH
**Files:** 8 salvage files referenced as `evidence_paths` or `authority_doc` in workstream records:

- `salvage/SALVAGE_TRIAGE_MASTER_2026_03_28.md`
- `salvage/SALVAGE_ENHANCE_CLEANUP_PLAN_2026_03_28.md`
- `salvage/SALVAGE_EXTERNAL_SWEEP_2026_03_28.md`
- `salvage/SALVAGE_EXTERNAL_RECOVERY_PASS_2026_03_28.md`
- `salvage/SALVAGE_PROMOTION_QUEUE_2026_03_28.tsv`
- `salvage/RECOVERY_STATUS_2026_03_28.md`
- `salvage/salvage_report_pearl_int_2026-03-28.md`
- `salvage/SALVAGE_PEN_NAME_AUTHOR_SYSTEM_2026_03_28.md`

These workstreams are all `completed` status so this is historical evidence, not blocking. The `salvage/` directory on main only has session snapshots.

**Impact:** Audit trail for completed workstreams is incomplete on main. Cannot verify salvage decisions without branch archaeology.

**Fix:** Either promote salvage evidence to main or annotate ACTIVE_WORKSTREAMS.tsv to note that evidence is branch-only historical.

### 2.4 Workstream Branch References Are Stale

**Severity:** HIGH
**Detail:** ACTIVE_WORKSTREAMS.tsv references branches that no longer exist as remote branches:

- `codex/state-convergence-20260328` -- not on origin (was cleaned up in branch consolidation PR #146)
- `agent/consolidation-promo-01` -- not on origin

All affected workstreams are `completed` so no work is blocked, but the TSV does not reflect current branch reality.

**Fix:** Update branch column to note "(archived)" or "(deleted after merge)" for cleaned-up branches.

---

## 3. MEDIUM: Drift Patterns and Structural Issues

### 3.1 Orphaned Docs (Not in DOCS_INDEX or SYSTEMS_V4)

**Severity:** MEDIUM
**Count:** 23 doc files exist on disk but are not referenced in either DOCS_INDEX or SYSTEMS_V4:

| File | Category |
|------|----------|
| `docs/ATOM_DEBT_REPAIR_DEV_SPEC.md` | Content/atoms |
| `docs/BRANCH_CLEANUP_2026_03_21.md` | Repo hygiene (historical) |
| `docs/CONTENT_DURATION_MARKETING_PLAN.md` | Marketing |
| `docs/GLOBAL_PERSONA_MARKETING_PLAN.md` | Marketing |
| `docs/GO_LIVE_EVIDENCE_D2_D3_D5_D6.md` | Go-live evidence |
| `docs/MANGA_GTM_PLAN.md` | Manga/marketing |
| `docs/ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md` | Onboarding |
| `docs/PEARL_ARCHITECT_STATE.md` | Architecture (itself!) |
| `docs/PEARL_GITHUB_PS_TXT_PATCH.md` | GitHub ops |
| `docs/PEN_NAME_AUTHOR_SYSTEM.md` | Authoring |
| `docs/VIDEO_AND_COVER_ART_FLUX_WIRING.md` | Video |
| `docs/VIDEO_CONTENT_MARKETING_PLAN.md` | Video/marketing |
| `docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md` | Video |
| `docs/WORDPRESS_LOCAL_SETUP.md` | Integration |
| `docs/anxiety_fear_writer_spec.md` | Writer (legacy?) |
| `docs/audiobook_ops_manual.md` | Audiobook |
| `docs/brand_admin/DISTRIBUTION_INDEX.md` | Brand admin |
| `docs/europe_latam_briefing_data.md` | Marketing/locale |
| `docs/europe_latam_marketing_addendum.md` | Marketing/locale |
| `docs/marketing/ITE_FEATURE_BRIEF.md` | Marketing |
| `docs/marketing_templates.md` | Marketing |
| `docs/phoenix_protocol/Phoenix_Protocol_Dev_Spec.md` | Legacy |
| `docs/research/manga_platform_research_2026.md` | Research |

**Impact:** Matches the drift pattern "introduce a new workbook, doc, or spec when a canonical file already exists" -- these docs may contain information that should be in governed locations. Developers may find them and treat them as authoritative.

**Fix:** Triage each: index in DOCS_INDEX, archive to `deprecated/`, or delete. Priority: `PEARL_ARCHITECT_STATE.md` (the architecture routing doc) is ironically not indexed in DOCS_INDEX.

### 3.2 PEARL_ARCHITECT_STATE.md Not Indexed in DOCS_INDEX

**Severity:** MEDIUM
**Detail:** The architecture routing doc that says "When routing a task, start here" is itself not linked from the canonical navigation layer (DOCS_INDEX). This creates a circular gap: DOCS_INDEX is the navigation layer, but the architecture routing doc isn't in it.

**Fix:** Add PEARL_ARCHITECT_STATE.md to the "Canonical authority" or a new "Architecture routing" section in DOCS_INDEX.

### 3.3 Worktree Sprawl (14 Active Worktrees)

**Severity:** MEDIUM
**Detail:** 14 git worktrees exist, 8 of which are `worktree-agent-*` (auto-created Claude Code worktrees). All are on the same commit (bb6ce281 / HEAD of main). This creates disk overhead and potential confusion about which worktree has uncommitted work.

**Fix:** Run `docs/REPO_HYGIENE_AND_WORKTREE_CLEANUP.md` procedure to prune worktrees that have no uncommitted changes.

### 3.4 DOCS_INDEX Pearl News Qwen Research Path Mismatch

**Severity:** MEDIUM
**Detail:** DOCS_INDEX references `docs/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md` (in the ws_qwen_api_unification workstream write_scope) but the actual file is at `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md` (in the `research/` subdirectory). The bare path does not exist.

**Fix:** Update the reference to use the correct `docs/research/` path.

### 3.5 Main Repo Not on Expected Branch

**Severity:** MEDIUM
**Detail:** The main worktree at `/Users/ahjan/phoenix_omega` is checked out on `agent/translation-quality-contracts` instead of `main`. This is unusual for a primary working copy.

**Fix:** Consider switching the main worktree back to `main` to avoid confusion.

---

## 4. LOW: Minor Issues

### 4.1 Marketing Backlog Items Correctly Documented as Absent

**Severity:** LOW (informational)
**Detail:** 9 marketing closed-loop files are documented as "Backlog ... not present" and are indeed absent. This is correct documentation. No action needed.

### 4.2 SYSTEMS_V4.md Last Updated Date

**Severity:** LOW
**Detail:** SYSTEMS_V4.md says "Last updated: 2026-03-03" -- nearly a month old. The system has evolved significantly since then (source bank repair, research integration, brand wizard, video publish, credentials registry). The doc content may be accurate for architecture (which is stable) but the date signals staleness.

**Fix:** Review and update the date if content is still accurate, or add a note about what's changed since 2026-03-03.

### 4.3 Two Active Workstreams With No Branch

**Severity:** LOW
**Detail:** `ws_research_citation_gaps_20260330` (active) and `ws_research_pipeline_activation_20260330` (blocked) have `branch: none`. This is acceptable for workstreams that haven't started branch work yet, but worth noting for tracking.

---

## 5. Positive Findings

The following architecture areas are healthy and well-wired:

1. **Core authority chain intact:** Arc-First spec, Writer spec, SYSTEMS_V4, DOCS_INDEX all exist and cross-reference correctly.
2. **All 35+ workflow files exist** on disk and match DOCS_INDEX references.
3. **All core pipeline modules exist:** catalog_planner, format_selector, assembly_compiler, rendering, practice_selector, coverage_checker, chapter_planner, variation_selector -- all present.
4. **All config directories exist:** source_of_truth, format_selection, catalog_planning, angles, video, manga, quality, marketing, experience, localization, payouts, narrators, authoring, recommender, practice, trend_keywords.
5. **All CI/QA scripts exist:** push_guard, preflight, health_check, governance verifier, entropy checker, similarity checker, wave density, prepublish gates, release evidence writer.
6. **SOURCE_OF_TRUTH directories intact:** teacher_banks, compression_atoms, exercises_v4, practice_library, freebies all present.
7. **PhoenixControl app intact:** All Swift sources, views, models, services present.
8. **Pearl News subsystem complete:** Pipeline, config, templates, governance, tests all present.
9. **Manga subsystem wired:** Schemas, models, transmission, gate registry, tests all present.
10. **Skills intact:** pearl-github (SKILL.md, references), pearl-int present.
11. **Branch consolidation completed:** PR #146 successfully reduced branches from 46 to 8 remote.
12. **All CLAUDE.md referenced files present:** PEARL_GITHUB_ONBOARDING, SKILL, git_system, repo_memory, GITHUB_OPERATIONS_FRAMEWORK, GITHUB_GOVERNANCE, BRANCH_PROTECTION_REQUIREMENTS, GITHUB_GOVERNANCE_INCIDENT_RUNBOOK, DOCS_INDEX, AGENT_FILE_PERSISTENCE_PROTOCOL.

---

## 6. Prioritized Fix List

| Priority | Issue | Effort | Fix |
|----------|-------|--------|-----|
| P0 | SUBSYSTEM_AUTHORITY_MAP.tsv not on main | Small PR | Merge from `agent/verify-and-fix` or regenerate |
| P0 | SESSION_UNITY_PROTOCOL.md not on main | Small PR | Merge from `agent/verify-and-fix` |
| P0 | PEARL_PM_STATE.md not on main | Small PR | Merge from `agent/verify-and-fix` |
| P1 | DOCS_INDEX recommender section stale | Edit | Update "not present" to reflect actual state |
| P1 | DOCS_INDEX date stale (2026-03-30) | Edit | Update with recent PR merges |
| P1 | ACTIVE_WORKSTREAMS branch refs stale | Edit | Annotate archived branches |
| P1 | Salvage evidence not on main | Decision | Promote or annotate as branch-only |
| P2 | PEARL_ARCHITECT_STATE not in DOCS_INDEX | Edit | Add to canonical authority section |
| P2 | 23 orphaned docs not indexed | Triage | Index, archive, or delete each |
| P2 | 14 worktrees active | Cleanup | Prune idle worktrees |
| P2 | Pearl News Qwen research path wrong | Edit | Fix path in DOCS_INDEX |
| P2 | Main worktree on non-main branch | Manual | Switch to main |
| P3 | SYSTEMS_V4 date stale | Edit | Review and update date |
| P3 | Two workstreams with no branch | Monitor | Expected; track when branch work starts |

---

## Methodology

- Read architecture anchor docs: PEARL_ARCHITECT_STATE.md, SYSTEMS_V4.md, DOCS_INDEX.md, OWNERSHIP_MATRIX.md, Arc-First spec
- Read coordination artifacts: ACTIVE_PROJECTS.tsv, ACTIVE_WORKSTREAMS.tsv
- Verified 200+ file references from DOCS_INDEX against disk
- Verified all 35 workflow files
- Verified all config directories and core modules
- Checked all workstream branch references against local and remote branches
- Checked for orphaned docs not referenced in DOCS_INDEX or SYSTEMS_V4
- Checked for PEARL_ARCHITECT_STATE drift patterns
- Inventoried worktrees and branch state

---

*Report generated: 2026-04-01*
