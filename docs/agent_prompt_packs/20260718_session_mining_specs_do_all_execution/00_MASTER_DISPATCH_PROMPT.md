Act as Pearl_PM_Dispatcher.

EXECUTE this prompt pack in dependency order. Do not merely summarize.

PROMPT_PACK=`docs/agent_prompt_packs/20260718_session_mining_specs_do_all_execution/`

## Mission

Implement the refreshed session-mining spec set and ready-now work that still matters. Do not execute stale retired briefs. Do not create duplicate systems where the refresh says to merge into existing machinery.

## Live Truth First

Read:

- `docs/agent_brief.txt`
- `docs/PROGRAM_STATE.md`
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_RELEVANCE_MATRIX.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/BEST_WORK_ALIGNMENT_MATRIX.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/OVERLAP_RECONCILE_LEDGER.tsv`

Try `git fetch --prune origin main`. If GitHub returns 403/account-suspended, record `GITHUB_SUBSTRATE=blocked` and continue offline only.

## Global Rules

- `GITHUB_WRITES=none`.
- Prefer PearlStar offline branches for durable landing.
- No `git add -A` or broad staging.
- No raw artifact deletion.
- No public publishing, live scheduling, catalog-scale rendering, or production release authorization.
- Every code lane must run a smoke proof before implementing, then a pilot proof, then a bounded scale micro-batch only if the pilot passes.
- Every lane ends `MERGED` or `BLOCKED`.

## Wave Execution

Wave 0:
- `01_substrate_and_refresh_docs_landing.md`

Wave 1, after wave 0 terminal:
- `02_rn1_tuple_viability_repro_fix.md`
- `03_rn6_boundary_aware_word_clamp.md`
- `04_rn5_bisac_validator_only.md`
- `05_rn9_docs_index_completeness_gate.md`

Wave 2, after wave 0 terminal and wave 1 not conflicting:
- `06_spec1_atom_depth_manifest.md`
- `07_spec2_integrity_gap_map_merge.md`
- `08_spec9_plantime_chapter_contract.md`
- `13_spec4_human_calibrated_judge_packet.md`

Wave 3:
- `09_spec5_store_series_naming_engine.md`
- `10_spec6_free_to_paid_ladder.md`

Wave 4:
- `11_spec8_artifact_retention_policy.md`
- `12_spec3_catalog_gpu_dispatcher_dryrun.md`
- `14_spec7_manga_serial_spine_merge.md`

Wave 5:
- `15_final_integration_audit.md`

If dependencies conflict, stop only the conflicting lane and continue independent lanes.

## Global Watchdog

Poll every 5 minutes. If any lane makes no progress for 10 minutes, write a watchdog note, reduce to smoke scope, and decide `MERGED` or `BLOCKED` honestly. Do not leave background jobs.

## Final CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM_Dispatcher
PROMPT_PACK=docs/agent_prompt_packs/20260718_session_mining_specs_do_all_execution/
PROMPTS_LAUNCHED=
WAVES_COMPLETE=
GITHUB_WRITES=none
GITHUB_SUBSTRATE=
PEARLSTAR_REFS=
PROOF_ROOT=artifacts/qa/session_mining_specs_do_all_20260718/
LANES_MERGED=
LANES_BLOCKED=
IMPLEMENTATION_FILES_CHANGED=
PUBLIC_RELEASE_AUTHORIZED=no
CATALOG_SCALE_RUN=no
FINAL_VERDICT=<PASS|BLOCKED>
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_do_all_final_2026-07-18.md
SIGNAL=session-mining-specs-do-all-dispatcher=<PASS|BLOCKED>
NEXT_ACTION=
```
