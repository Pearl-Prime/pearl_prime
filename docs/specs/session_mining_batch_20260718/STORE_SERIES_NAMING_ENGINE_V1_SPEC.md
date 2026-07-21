# STORE_SERIES_NAMING_ENGINE_V1_SPEC

Status: REFRESHED SPEC
Classification: KEEP
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/STORE_SERIES_NAMING_ENGINE_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `39518d02dbc10a2502f0e0b32ba283476190f4fbf0732cd5cdc7f071780faea1`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

This spec is still high-value with no substantive concept change. Phoenix needs
store-safe series naming that generalizes beyond one winning title family while
preserving reader promise, author fingerprint, discoverability, and catalog
coherence.

## Reconcile, Do Not Rebuild

Implement as an extension of existing naming machinery:

- `phoenix_v4/naming/generator.py`
- current catalog/store metadata generators
- current author fingerprint and marketing feed systems

Do not create a disconnected title generator or separate marketing taxonomy.

## Refreshed Requirements

The naming engine must:

- produce store-safe series titles and subtitles with deterministic provenance;
- avoid stale W0-only assumptions while retaining proven store learnings;
- preserve topic, persona, promise, tone, and author-brand constraints;
- prevent collisions across current and planned series;
- mark operator-review status before any storefront use.

Suggested future config:

- `config/naming/series_taxonomy.yaml`
- optional collision manifest emitted under `artifacts/qa/`
- tests for collision, forbidden terms, and topic/persona fit

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: generated candidates pass schema, collision, and
  forbidden-term checks.
- `OPERATOR_READ_PASS`: operator/editor approves candidate naming families for
  storefront use.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted by this spec.
