# Full Repo Reconciliation — Execution Spec

**Spec ID:** specs/FULL_REPO_RECONCILIATION_EXECUTION_SPEC.md
**Status:** active
**Owner:** Pearl_Architect (lead) + Pearl_PM (coordination)
**Created:** 2026-04-26
**Supersedes:** none (new)

---

## 1. Purpose

This spec governs a **full repo historical audit + canonical system reconciliation**.
It is broader in scope than `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (PR #682),
which covers only the manga subsystem.

The audit covers every subsystem in the repo — Pearl Prime, Pearl News, Manga,
Brand Wizard, Brand Admin, Teacher Mode, Pearl Marketing, Pearl DevOps, Pearl LegalBiz,
plus repo coordination and integrations.

## 2. Why this spec exists — banned failure mode

PR #680 (manga pipeline audit, merged 2026-04-26 00:43 UTC) used **narrow filename
patterns** like `docs/MANGA_*.md` and missed five load-bearing strategic docs:

- `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (303 lines) — outside `docs/`
- `docs/GENRE_PORTFOLIO_PLAN.md` (563 lines) — different prefix
- `docs/CJK_CATALOG_PLAN.md` (300 lines) — `CJK`, not `MANGA`
- `docs/US_CATALOG_PLAN.md` (279 lines) — `US`, not `MANGA`
- `docs/MANGA_MODE_STRATEGY.docx` → `.md` — wrong extension

Subsequent reconciliation (PR #682, #684, #685, #686) confirmed the miss.

This spec **PERMANENTLY BANS narrow-pattern enumeration** as the audit method.
Every classifier here uses full-tree enumeration:
- `git ls-files` (all paths, no glob filter)
- `git log --all --name-status` (all commits, all branches)
- `git log --all --follow -- <path>` (rename-aware history)
- `git grep` (full-text)

Filename prefix shortcuts (e.g., `docs/MANGA_*.md`, `*_PLAN.md`) are **not permitted**.

## 3. Scope

### 3.1 In scope

- All 42,257 tracked files in the repo as of `origin/main` HEAD `1f4f8a28f`
- All 2,006 commits captured across all branches
- All 11 anchor PRs (#674-#686)
- All 14 subsystems in `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
- All 5 active projects in `artifacts/coordination/ACTIVE_PROJECTS.tsv`

### 3.2 Out of scope

- Any file deletion (PR-5+ scope; this spec authorizes a *deletion plan*, not deletions)
- Any code edit to existing pipelines
- Operator authentication / tokens / secrets (referenced via env registry only)
- Workstream creation beyond `ws_full_repo_audit_reconciliation_20260426`

## 4. Required deliverables

The audit lands in **4 sequential PRs**:

| PR | Branch | Contents | File count |
|----|--------|----------|-----------:|
| 1 | `agent/full-repo-recon-spec-20260426` | This spec | 1 |
| 2 | `agent/full-repo-recon-tools-20260426` | 4 audit scripts | 4 |
| 3 | `agent/full-repo-recon-inventory-20260426` | 4 inventory CSVs + baseline doc | 5 |
| 4 | `agent/full-repo-recon-canonical-docs-20260426` | 6 canonical/synthesis docs | 6 |

Subsequent PRs (PR-5 deletion buckets, PR-6+ subsystem remediation) are **NOT** in
scope of this spec. They are gated on operator review of PR-4 deliverables.

## 5. Phase sequence

| Phase | Deliverable | Wall-clock |
|-------|-------------|-----------:|
| 0 | Branch + baseline | 15 min |
| 1 | 5 parallel inventory subagents | 30-90 min |
| 2 | Synthesis CSVs + baseline.md | 15 min |
| 3 | 3 parallel subsystem reviewers (consolidated from spec's 9) | 30-45 min |
| 4 | 6 canonical docs | 60-90 min |
| Land PRs | 4 PR cycles × ~15 min | 60-90 min |

## 6. Hard rules

1. **No narrow-pattern enumeration** (per §2)
2. **No deletions** in PR-1 through PR-4
3. **No paid LLM APIs** per [CLAUDE.md](../CLAUDE.md) Tier 1/2/banned policy
4. **Full git history awareness**: `git log --all`, `git log --follow`, no shallow clones
5. **Subagent output validation**: every Phase 1 subagent's row count must match
   its enumeration source (within 1%)
6. **Strategic-miss test**: all 5 PR #680 misses MUST appear in the doc canonicality
   matrix classified `canonical` under `manga_pipeline` (mandatory regression test)
7. **Cite paths + line numbers** in every recommendation
8. **Mass-delete protection**: no PR in this sequence may delete >50 files (none
   should delete *any* files; sequence is audit-and-plan only)

## 7. Subagent contracts

### 7.1 Phase 1 subagents (parallel)

| Subagent | Scope | Output | Required row count |
|----------|-------|--------|--------------------|
| A — Repo Inventory | every tracked file | `agent_a_inventory.csv` | matches `git ls-files` ±1% |
| B — Git History | every commit + 11 anchor PRs | `agent_b_history.csv` + `agent_b_pr_index.csv` | all commits captured; all 11 PRs |
| C — Doc Canonicality | every doc-like file | `agent_c_doc_status_full.csv` | matches `git ls-files '*.md' '*.txt' '*.docx' '*.rst' '*.adoc'` |
| D — Pipeline + Code | every pipeline + every .py | `agent_d_pipeline_full.csv` + `agent_d_code_modules_full.csv` + `agent_d_orphan_candidates.txt` | all .py files; all subsystems' pipelines |
| E — Business Reqs | requirements transcript or inferred | `agent_e_business_reqs.csv` | 25-40 reqs |

### 7.2 Phase 3 reviewers (parallel)

Consolidated from spec authoring's 9 reviewers to 3 for context efficiency:

| Reviewer | Perspectives | Output |
|----------|--------------|--------|
| Code + pipelines | Pearl_Prime + Pearl_News + Pearl_Manga + Pearl_DevOps | `phase3_code_pipelines_report.md` |
| Docs + governance | Pearl_Architect + Pearl_PM + Pearl_LegalBiz | `phase3_docs_governance_report.md` |
| Brand + content | Pearl_Brand + Pearl_Marketing | `phase3_brand_content_report.md` |

## 8. PR-3 inventory CSVs — schema contracts

### 8.1 `full_repo_file_inventory_2026-04-26.csv`

TAB-separated. Columns:
`path`, `top_level_area`, `extension`, `size_bytes`, `line_count`, `classification`,
`last_commit_sha`, `last_commit_date`, `last_author`

One row per `git ls-files` result.

### 8.2 `full_repo_git_history_index_2026-04-26.csv`

TAB-separated. Columns:
`row_type` (commit|pr), `key`, `date`, `author`, `subject_or_title`,
`files_changed`, `additions`, `deletions`, `branch_or_state`,
`merge_or_keyword_flags`, `head_branch`, `base_branch`

One row per commit OR per PR.

### 8.3 `full_repo_doc_status_matrix_2026-04-26.csv`

TAB-separated. Columns:
`path`, `top_level_area`, `subsystem`, `title_or_h1`, `line_count`,
`last_commit_date`, `classification`, `references_in`, `references_out`,
`conflict_with`, `notes`

One row per doc-like file. `classification` ∈ {canonical, current_support,
historical_context, superseded, conflicting, duplicate, generated_artifact,
deletion_candidate, archived, README, fixture, test, unknown}.

### 8.4 `full_repo_pipeline_matrix_2026-04-26.csv`

TAB-separated. Wide schema with `row_type` discriminator ∈ {pipeline, module,
orphan_module, requirement}.

Pipeline columns: `pipeline_entry_point`, `pipeline_called_by`, `pipeline_calls_into`,
`pipeline_config_paths`, `pipeline_schema_paths`, `pipeline_test_coverage`.

Module columns: `module_top_level_area`, `module_line_count`, `module_imports_count`,
`module_imported_by_count`, `module_has_main`, `module_has_tests`, `module_last_author`.

Requirement columns: `req_text`, `req_topic_cluster`, `req_source`, `req_evidence_path`.

### 8.5 `full_repo_audit_baseline_2026-04-26.md`

Markdown summary. ~150 lines. Covers branch + baseline SHA + open/merged PRs +
failure-mode citation + headline findings + subagent provenance.

## 9. PR-4 canonical docs — content contracts

| Doc | Purpose | Target lines |
|-----|---------|-------------:|
| `FULL_REPO_SYSTEM_AUDIT_2026-04-26.md` | Synthesis of Phase 1-3 findings | 400-700 |
| `FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md` | Subsystem → canonical doc/spec map | 200-400 |
| `PLAIN_ENGLISH_SYSTEM_OVERVIEW.md` | 15-section plain-English explainer | 300-500 |
| `FULL_REPO_ARCHITECTURE_MAP_2026-04-26.md` | Mermaid system diagrams (≥7) | 200-400 |
| `FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` | Deletion classes + PR D1-D6 buckets | 300-500 |
| `FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md` | Req matrix + remediation per gap | 300-500 |

## 10. Out-of-scope work routed elsewhere

| Item | Routed to |
|------|-----------|
| Deletion buckets PR D1-D6 | Pearl_GitHub follow-up; gated on operator approval |
| Per-subsystem remediation PRs | Pearl_<subsystem> agents per gap plan |
| PEARL_PM_STATE.md refresh | Pearl_PM separate session (last_verified 2026-04-10 stale) |
| ACTIVE_WORKSTREAMS.tsv schema-malformed rows | Pearl_PM separate session |
| `brand-wizard-app/node_modules/` mass cleanup (6,984 committed files) | PR D1 candidate; Pearl_GitHub |
| Brand-count canon fracture (24/28/36/37/312 mismatch) | Pearl_Brand separate session |

## 11. Coordination registry edits

This audit may add:
- 1 row to `artifacts/coordination/ACTIVE_PROJECTS.tsv` —
  `proj_full_repo_reconciliation_20260426`
- 1 row to `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` —
  `ws_full_repo_audit_reconciliation_20260426`

Pearl_PM judgment call: may roll under existing `proj_state_convergence_20260328`
to avoid project sprawl.

## 12. Governance

Every PR in this sequence must:
- Pass `scripts/git/push_guard.py`
- Pass `scripts/ci/preflight_push.sh`
- Pass `scripts/ci/audit_llm_callers.py` (no banned LLM API references)
- Pass `scripts/ci/pr_governance_review.py` (APPROVED, optionally [WITH WARNINGS:n])
- Capture full 40-char merge commit SHA via `gh pr view --json mergeCommit` AND
  `git ls-remote origin main` cross-confirmed

Workers Builds is the established orthogonal Cloudflare blocker; UNSTABLE-solely-from-it
is mergeable per CLAUDE.md governance pattern.

## 13. Closeout contract

After PR-4 lands, emit a `CLOSEOUT_RECEIPT` per `docs/SESSION_UNITY_PROTOCOL.md`
with all 4 PR numbers + full 40-char SHAs + handoff list (operator review primary;
Pearl_GitHub deletion execution; Pearl_<subsystem> remediation per gap plan).

## 14. References

- Prior failed audit: `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` (PR #680)
- Manga reconciliation: `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (PR #682)
- Subsystem ownership: `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
- Project state: `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- Workstream state: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- Architecture routing: `docs/PEARL_ARCHITECT_STATE.md`
- Project routing: `docs/PEARL_PM_STATE.md` (NOTE: last_verified 2026-04-10, stale)
- LLM tier policy + non-negotiable rules: `CLAUDE.md`
