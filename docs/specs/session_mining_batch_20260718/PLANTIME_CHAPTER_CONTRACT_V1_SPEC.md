# PLANTIME_CHAPTER_CONTRACT_V1_SPEC

Status: REFRESHED SPEC
Classification: REFRESH
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/PLANTIME_CHAPTER_CONTRACT_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `3c3d6e91993a3f0b40fad28a76a7d37107fdba2be1a12bfcfdb88e290f5f4596`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

Plan-time chapter contracts remain useful, but the original dependency on the
thesis-bank re-key is stale. The repo already has topic-aware thesis overrides
and resolver tests. This spec should consume current planning machinery instead
of reworking it.

## Reconcile, Do Not Rebuild

Use:

- `phoenix_v4/planning/book_structure_plan.py`
- `config/planning/chapter_thesis_bank.yaml`
- current chapter purpose contract machinery
- Pearl Prime narrative form SSOT
- atom deepening, reader-layer, exercise, and story/literary standards

Do not create a second story planner or thesis resolver.

## Refreshed Contract Fields

Each chapter contract should include:

- topic/persona/engine/chapter identity;
- thesis and reader promise;
- reader-state entry and exit;
- same-person story requirement, or explicit non-story reason;
- exercise/tool policy and expected aha/integration;
- atom surface/depth expectations;
- source/evidence constraints;
- close/handoff requirement;
- acceptance profile: draft, structural, operator-read, production.

## Guardrails

- Structural plan success is not literary success.
- A valid thesis cannot compensate for weak story, weak source bridge, or shallow
  exercise integration.
- Public release requires downstream approval beyond this planning contract.

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: chapter contracts are emitted from current resolver
  paths and validate against at least one flagship and one non-flagship plan.
- `OPERATOR_READ_PASS`: operator/editor accepts sampled contracts as useful for
  Pearl Prime writing.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted by this spec.
