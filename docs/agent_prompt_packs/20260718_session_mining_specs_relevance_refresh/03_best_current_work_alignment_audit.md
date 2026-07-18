Act as Pearl_Architect with Pearl_Editor support.

EXECUTE lane 03: best current work alignment audit.

## Goal

Verify each spec reflects the strongest current lessons, not stale summaries: Ch1/Mara narrative craft, same-person story progression, atom deepening, five-layer exercise/tool policy, evidence truth gates, deterministic social dry-run, faceless video, non-manga image curation, PearlStar offline, and GitHub suspension.

## Read First

- `docs/narrative_form_ssot_spec.md`
- `docs/ch01_full_assembly_v1.md`
- `docs/ch01_mara_spine_prose_v2 (1).md`
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` if present
- `artifacts/qa/atom_job_deep_audit_20260717/` if present
- `artifacts/qa/atom_repair_trace_story_smoke_20260717/` if present
- `artifacts/qa/corporate_burnout_story_literary_repair_20260717/` if present
- `artifacts/qa/corporate_burnout_evidence_repair_20260717/` if present
- `docs/PEARL_ANIMATOR_FACELESS_SHORTS_SPEC_2026-07-18.md` if present
- `docs/agent_prompt_packs/20260718_deterministic_social_media_system_100pct/` if present
- `docs/agent_prompt_packs/20260718_non_manga_image_inventory_usage_audit/` if present
- all 9 source specs.

## Best-Work Questions

For each spec ask:

- Does it encode atom depth beyond bullet points: introduction, felt/concrete experience, insight, and handoff?
- Does it enforce same-person story progression and real story depth rather than mechanical word counts?
- Does it distinguish tools from canonical five-layer exercises?
- Does it include meaningful aha/integration requirements for exercises?
- Does it handle quote/composite/evidence/external-story bridging?
- Does it preserve source/provenance/truth gates?
- Does it use current deterministic social/video/image-bank architecture where relevant?
- Does it acknowledge offline/PearlStar and no-GitHub-write constraints?
- Does it avoid claiming `PASS` equals bestseller unless operator read approves?

## Smoke

Audit 3 specs:

- `ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`
- `PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC.md`
- `HUMAN_CALIBRATED_JUDGE_V1_SPEC.md`

## Pilot

Audit all Pearl Prime/book-quality adjacent specs: atom taxonomy, prose validator, human judge, plantime chapter contract.

## Scale Micro-Batch

Audit all 9 specs and all ready-now briefs. Write:

`artifacts/qa/session_mining_specs_relevance_refresh_20260718/BEST_WORK_ALIGNMENT_MATRIX.tsv`

Required columns:

`item_id,title,alignment_score_0_5,missing_current_lesson,required_update,proof_source,classification_after_alignment,notes`

## Watchdog

Poll every 5 minutes. If a proof directory is missing, record `MISSING_EVIDENCE_PATH` and continue. Do not invent contents.

## Landing Contract

`MERGED` if every item has an alignment score and required-update note.

`BLOCKED` if key current-best docs cannot be read and no alternate evidence exists.

## Cleanup Ledger

Record scratch notes and temporary extracts.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_best_work_alignment_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Architect
LANE=03_best_current_work_alignment_audit
GITHUB_WRITES=none
ITEMS_AUDITED=19
ALIGNMENT_PASS=
ALIGNMENT_REFRESH_REQUIRED=
ALIGNMENT_RETIRE_OR_MERGE=
BEST_WORK_MATRIX=artifacts/qa/session_mining_specs_relevance_refresh_20260718/BEST_WORK_ALIGNMENT_MATRIX.tsv
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_best_work_alignment_2026-07-18.md
SIGNAL=session-mining-specs-best-work-alignment=<MERGED|BLOCKED>
NEXT_ACTION=
```
