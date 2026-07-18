# Session-Mining Specs Relevance Refresh Prompt Pack - 2026-07-18

Status: ready to execute offline. GitHub writes are forbidden.

Goal: verify the 9 session-mining implementation specs and 10 ready-now dispatch briefs are still relevant against current Phoenix Omega truth, current best practices, and the newer work from Pearl Prime story/exercise/atom/social/offline lanes. Refresh, demote, merge, or retire stale items before any landing attempt.

## Source Spec Set

Archive source:

`/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/`

Local branch/commit source:

- branch: `agent/session-mining-specs-20260718`
- commit: `4e314f94bb`
- base: local `origin/main` `9e9b9e606791590337cd7d0f2fb425def2e6f760`

Spec files:

1. `ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`
2. `PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC.md`
3. `CATALOG_GPU_DISPATCHER_V1_SPEC.md`
4. `HUMAN_CALIBRATED_JUDGE_V1_SPEC.md`
5. `STORE_SERIES_NAMING_ENGINE_V1_SPEC.md`
6. `FREE_TO_PAID_LADDER_V1_SPEC.md`
7. `MANGA_MULTIVOLUME_SPINE_V1_SPEC.md`
8. `ARTIFACTS_RETENTION_POLICY_V1_SPEC.md`
9. `PLANTIME_CHAPTER_CONTRACT_V1_SPEC.md`
10. `SPEC_INDEX.md`

Known stale-risk examples to check:

- `CATALOG_GPU_DISPATCHER_V1_SPEC.md` says it depends on "spec #8 PS_QUEUE_DSN creds" even though spec #8 is artifact retention.
- Some ready-now briefs may have landed, been superseded, or be lower priority after the newer Pearl Prime story/exercise and deterministic social work.
- The specs predate the latest Ch1 story/atom architecture, five-layer exercise feedback, deterministic social dry-run, Pearl Animator faceless shorts spec, and non-manga image audit pack.

## Wave Order

| Wave | Lane | Owner | Depends On | Output | Status |
| --- | --- | --- | --- | --- | --- |
| 0 | `01_spec_artifact_truth_lock.md` | Pearl_PM | none | source/branch/archive truth | ready |
| 1 | `02_current_ssot_and_active_workstream_relevance.md` | Pearl_PM + Pearl_Architect | 01 | relevance matrix | ready |
| 2 | `03_best_current_work_alignment_audit.md` | Pearl_Architect + Pearl_Editor | 01,02 | best-work alignment gaps | ready |
| 3 | `04_existing_machinery_overlap_and_antireinvention.md` | Pearl_Dev | 01,02 | overlap/reconcile ledger | ready |
| 4 | `05_spec_refresh_patch_and_index_update.md` | Pearl_Architect + Pearl_PM | 01-04 | refreshed specs/index | ready |
| 5 | `06_offline_landing_and_final_audit.md` | Pearl_PM | 01-05 | final audited offline branch/handoff | ready |

## Required Outputs

- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_SOURCE_TRUTH.md`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_RELEVANCE_MATRIX.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/BEST_WORK_ALIGNMENT_MATRIX.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/OVERLAP_RECONCILE_LEDGER.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_REFRESH_CHANGELOG.md`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/FINAL_SPEC_REFRESH_AUDIT.md`
- `artifacts/coordination/handoffs/session_mining_specs_relevance_refresh_final_2026-07-18.md`

## Pack Self-Audit

- Overlap controlled: each lane owns one audit layer; only lane 05 edits specs.
- Missing gates fixed: all lanes include smoke, pilot, scale micro-batch, watchdog, landing, cleanup, handoff, and `CLOSEOUT_RECEIPT`.
- Cleanup fixed: any temp worktree, scratch file, branch, archive, and background job must be ledgered.
- Unsafe landing avoided: GitHub writes are forbidden; PearlStar offline only after generated diffs are reviewed and exact paths are listed.
- Stale idea risk handled: every spec and ready-now brief must be categorized `KEEP`, `REFRESH`, `MERGE_WITH_EXISTING`, `RETIRE`, or `BLOCKED_NEEDS_OPERATOR`.
