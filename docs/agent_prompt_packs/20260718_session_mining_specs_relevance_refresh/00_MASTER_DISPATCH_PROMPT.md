Act as Pearl_PM_Dispatcher.

EXECUTE this prompt pack. Do not merely report a plan.

PROMPT_PACK=`docs/agent_prompt_packs/20260718_session_mining_specs_relevance_refresh/`

## Mission

Verify and refresh the 9 session-mining implementation specs and 10 ready-now dispatch briefs before anyone lands them. The bar is not "old ideas are documented"; the bar is "these specs still match current Phoenix Omega truth and the best work we are doing now."

## Live Truth First

Read:

- `docs/agent_brief.txt`
- `docs/PROGRAM_STATE.md`
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PROMPT_ROUTER_OPERATING_MANUAL.md`
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`

Then verify:

- source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/`
- local branch: `agent/session-mining-specs-20260718`
- local commit: `4e314f94bb`
- whether the files already exist under `docs/specs/` in the current working tree or the local branch.

Try `git fetch --prune origin main`. If GitHub is still suspended/403, record `GITHUB_SUBSTRATE=blocked` and continue offline only.

## Current-Best Context To Reconcile

The specs must be checked against at least:

- Pearl Prime story methodology: `docs/narrative_form_ssot_spec.md`, `docs/ch01_full_assembly_v1.md`, `docs/ch01_mara_spine_prose_v2 (1).md`
- Pearl Prime bestseller/craft docs: `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` if present.
- Atom/job audit: `artifacts/qa/atom_job_deep_audit_20260717/` if present.
- Atom repair smoke: `artifacts/qa/atom_repair_trace_story_smoke_20260717/` if present.
- Corporate burnout repairs and operator packets from 2026-07-17 if present.
- Deterministic social dry-run pack/results: `docs/agent_prompt_packs/20260718_deterministic_social_media_system_100pct/` and `artifacts/qa/deterministic_social_system_20260718/` if present.
- Pearl Animator faceless shorts spec: `docs/PEARL_ANIMATOR_FACELESS_SHORTS_SPEC_2026-07-18.md` if present.
- Non-manga image inventory usage pack: `docs/agent_prompt_packs/20260718_non_manga_image_inventory_usage_audit/` if present.
- PearlStar offline/GitHub suspension handoffs if present.

If any file is missing, record it as missing evidence; do not invent.

## Decision Taxonomy

Every spec and ready-now brief must be classified:

- `KEEP`: still correct and high-value with no edits beyond metadata.
- `REFRESH`: still valuable but must be updated for current best practices or current repo state.
- `MERGE_WITH_EXISTING`: valid idea but should be folded into an existing spec/system, not landed as a separate spec.
- `RETIRE`: stale, already completed, superseded, or no longer worth implementing.
- `BLOCKED_NEEDS_OPERATOR`: operator-tier decision required.

## Wave Execution

Run lanes:

1. `01_spec_artifact_truth_lock.md`
2. `02_current_ssot_and_active_workstream_relevance.md`
3. `03_best_current_work_alignment_audit.md`
4. `04_existing_machinery_overlap_and_antireinvention.md`
5. `05_spec_refresh_patch_and_index_update.md`
6. `06_offline_landing_and_final_audit.md`

Do not run lane 05 until lanes 01-04 have produced matrices.

## Global Watchdog

Poll every 5 minutes. If a lane has no artifact mtime change for 10 minutes, write a watchdog note and narrow the scope to the next 3 specs/briefs. Do not hang on `git status`; use explicit file lists and `git show` where possible.

## Landing Rules

- `GITHUB_WRITES=none`.
- If edits are made, use a clean local/offline branch or plumbing commit.
- Push to PearlStar offline only if reachable and if the diff is exactly refreshed docs/specs plus proof/handoff artifacts.
- Do not rewrite or delete the durable archive.
- Do not implement the specs; this pack refreshes and validates the specs.

## Final CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM_Dispatcher
PROMPT_PACK=docs/agent_prompt_packs/20260718_session_mining_specs_relevance_refresh/
PROMPTS_LAUNCHED=6
WAVES_COMPLETE=
GITHUB_WRITES=none
GITHUB_SUBSTRATE=
PEARLSTAR_REF=
SOURCE_COMMIT=4e314f94bb
SPECS_AUDITED=9
READY_NOW_BRIEFS_AUDITED=10
KEEP=
REFRESH=
MERGE_WITH_EXISTING=
RETIRE=
BLOCKED_NEEDS_OPERATOR=
SPECS_UPDATED=
SPEC_INDEX_UPDATED=
FINAL_VERDICT=<PASS|BLOCKED>
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_relevance_refresh_final_2026-07-18.md
SIGNAL=session-mining-specs-relevance-refresh=<PASS|BLOCKED>
NEXT_ACTION=
```
