# Session-Mining Specs Do-All Execution Prompt Pack - 2026-07-18

Status: ready to execute offline/PearlStar. GitHub writes are forbidden.

Goal: implement the refreshed session-mining spec set and ready-now work in dependency order, without re-running retired stale prompts and without building parallel systems where the refresh says to merge into existing machinery.

## Inputs

- Refreshed spec index: `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- Relevance matrix: `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_RELEVANCE_MATRIX.tsv`
- Best-work matrix: `artifacts/qa/session_mining_specs_relevance_refresh_20260718/BEST_WORK_ALIGNMENT_MATRIX.tsv`
- Overlap ledger: `artifacts/qa/session_mining_specs_relevance_refresh_20260718/OVERLAP_RECONCILE_LEDGER.tsv`

## Do Not Execute

The refresh retired these items. Do not re-run them:

- RN-2 thesis-bank re-key
- RN-3 register gate F2.B phrasal-verb whitelist
- RN-4 bare-slot detector as new F9
- RN-10 dwell/integration pacing as a new module

## Wave Order

| Wave | Lane | Owner | Depends On | Main Output | Status |
| --- | --- | --- | --- | --- | --- |
| 0 | `01_substrate_and_refresh_docs_landing.md` | Pearl_PM | none | offline landing of refreshed specs/proofs | ready |
| 1A | `02_rn1_tuple_viability_repro_fix.md` | Pearl_Dev | 01 | repro-first tuple viability fix | ready |
| 1B | `03_rn6_boundary_aware_word_clamp.md` | Pearl_Dev | 01 | boundary-aware clamp repro/fix | ready |
| 1C | `04_rn5_bisac_validator_only.md` | Pearl_Dev | 01 | validator-only BISAC CI gate | ready |
| 1D | `05_rn9_docs_index_completeness_gate.md` | Pearl_PM + Pearl_DevOps | 01 | current docs index completeness gate | ready |
| 2A | `06_spec1_atom_depth_manifest.md` | Pearl_Dev + Pearl_Architect | 01 | atom depth/source/variation manifest | ready |
| 2B | `07_spec2_integrity_gap_map_merge.md` | Pearl_Dev | 06 | merge-only prose integrity gap map | ready |
| 2C | `08_spec9_plantime_chapter_contract.md` | Pearl_Dev + Pearl_Architect | 06 | plan-time chapter contract smoke | ready |
| 2D | `13_spec4_human_calibrated_judge_packet.md` | Pearl_PM + Pearl_Architect | 01 | operator rating packet + advisory judge stub | ready |
| 3A | `09_spec5_store_series_naming_engine.md` | Pearl_Dev + Pearl_Editor | 01 | store series naming pilot | ready |
| 3B | `10_spec6_free_to_paid_ladder.md` | Pearl_Marketing + Pearl_Dev | 01 | free-to-paid feed schema pilot | ready |
| 4A | `11_spec8_artifact_retention_policy.md` | Pearl_DevOps | 01 | retention/offload dry-run policy | ready |
| 4B | `12_spec3_catalog_gpu_dispatcher_dryrun.md` | Pearl_Int + Pearl_Dev | 11 | queue discovery/feeder dry-run | ready |
| 4C | `14_spec7_manga_serial_spine_merge.md` | Pearl_Dev | 01 | manga serial-spine merge plan/pilot | ready |
| 5 | `15_final_integration_audit.md` | Pearl_PM | all prior terminal | final audit and next-action matrix | ready |

## Outputs

- Proof root: `artifacts/qa/session_mining_specs_do_all_20260718/`
- Handoffs: `artifacts/coordination/handoffs/session_mining_specs_do_all_*_2026-07-18.md`
- Offline bundles/branches only; no GitHub writes.

## Pack Self-Audit

- Retired stale items are explicitly excluded.
- Merge-with-existing specs are not allowed to create parallel systems.
- Every lane has smoke, pilot, scale micro-batch, watchdog, MERGED/BLOCKED landing, cleanup ledger, handoff, and `CLOSEOUT_RECEIPT`.
- Catalog-scale operations, public publishing, destructive artifact pruning, and operator-taste decisions are blocked unless a later explicit authorization says otherwise.
