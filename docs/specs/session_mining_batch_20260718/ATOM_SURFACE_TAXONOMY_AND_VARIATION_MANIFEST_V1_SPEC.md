# ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC

Status: REFRESHED SPEC
Classification: REFRESH
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `957a74f9d89b6542feafb975ae69dc83ca1e105a96464e2abc42415b19b516dd`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

The original problem remains high-value: Phoenix needs a canonical way to
measure atom surface coverage and variation before claiming catalog-scale
quality. The old wording is stale where it frames the work as approximately 27
surface types and 10,000-book entropy. Current Pearl Prime work has sharper
requirements: atom depth, reader-state entry/exit, source truth, same-person
story progression, tool-versus-exercise separation, and exercise aha/integration
quality.

## Reconcile, Do Not Rebuild

- Extend `scripts/inventory/atom_coverage_audit.py` instead of forking coverage.
- Reuse `phoenix_v4/planning/enrichment_select.py` selection provenance and
  weights where available.
- Reconcile with the atom/job audit, atom deepening plan, reader-layer
  integration specs, deep five-layer exercise spec, and story/literary repair
  evidence.
- Do not edit canonical atom content or use this spec as a catalog rewrite wave.

## Refreshed Design

Create a canonical atom surface and depth registry that records both surface role
and reader transformation intent.

Required registry fields:

- `surface_key`
- `role`
- `allowed_slots`
- `min_variants_per_cell`
- `depth_contract`: intro, felt/concrete experience, insight/aha, integration,
  handoff
- `reader_state_entry`
- `reader_state_exit`
- `source_provenance_required`
- `exercise_policy`: canonical exercise, tool, reflection, or non-exercise
- `story_policy`: same-person story, external story, composite, or non-story

The first implementation should be measurement-only:

- `config/atoms/surface_taxonomy.yaml`
- `config/qa/variation_thresholds.yaml`
- `scripts/inventory/surface_inventory.py`
- `scripts/qa/variation_manifest.py`
- `scripts/ci/check_variation_manifest.py`

Any new CI gate starts as WARN. It must not block production until it has a
current dry-run against real flagship/catalog cells and reviewed false positives.

## Current-Best Requirements

- Count real parsed atoms, not header fragments.
- Separate structural slot fit from actual reader transformation quality.
- Detect shallow bullet-like atoms, missing handoff, cold source entry, evidence
  bridge weakness, and story atoms without event/stake/turn/cost/residue.
- Distinguish tools from canonical five-layer exercises.
- Preserve source/provenance truth gates for quote, composite, and external
  story material.
- Avoid claiming that entropy or variation pass equals bestseller quality.

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: registry and manifest produce current inventory for at
  least flagship plus one non-flagship cell; no content is edited.
- `OPERATOR_READ_PASS`: operator reviews sampled findings and accepts the
  taxonomy as useful for Pearl Prime quality decisions.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted by this spec. Any live
  catalog or storefront decision remains outside this measurement spec.

## Implementation Notes

Start with a smoke set and record unknown categories explicitly. Any category
created from inference must be marked provisional until it is reconciled with
current atom, exercise, story, and reader-layer SSOT.

## gt30d C04 — Bridge / Adjacency Cohesion (2026-07-22)

**Keepers:** I025, I048 · MERGE into SPEC-1 (no parallel taxonomy).

### Problem

Choppy books often lack adjacency-aware selection across:

- scene → story
- story → exercise
- data → teaching / bridge intros-outros

### Required measurement fields (additive)

- `bridge_role`: none | scene_to_story | story_to_exercise | data_to_teaching | custom
- `adjacency_group`: stable id for atoms that must not jarringly collide when sequenced
- `cohesion_min_score`: optional float threshold for pilot gates (advisory until calibrated)

### Cursor-may-implement (Wave-B or PM-advanced)

1. Extend atom coverage / selection provenance measurement only — do not rewrite banks in this lane.
2. Emit gap report of missing bridge roles per topic×engine cell (pilot 1 topic).
3. Do not create a second F9/judge module; fold craft checks into existing register/craft gates if needed.

### Signal

`gt30d-c04-spec-terminal` when this section lands with the SPEC-1 file.
