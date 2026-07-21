# MANGA_MULTIVOLUME_SPINE_V1_SPEC

Status: REFRESHED MERGE NOTE
Classification: MERGE_WITH_EXISTING
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/MANGA_MULTIVOLUME_SPINE_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `4a30e5a12033b755dd513897f2c6a856f7359774af3143d4c166e7c8464ac630`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

Multi-volume manga spine planning remains useful, but the old implementation
path is stale. Current repo machinery already includes serial spine loaders,
adopted series configs, and manga story architecture. This idea should merge
there instead of landing as a new parallel `phoenix_v4/manga/series/spine.py`
surface.

## Reconcile, Do Not Rebuild

Merge into:

- `phoenix_v4/manga/serial/spine_loader.py`
- `config/manga/serial_spines/*.yaml`
- `config/manga/serial_spines/_adopted_series.yaml`
- `phoenix_v4/manga/series/story_architect.py`
- `scripts/manga/assemble_from_bank.py`

Do not create `scripts/manga/assemble_volume.py` or a second spine model unless
the current serial loader proves insufficient.

## Refreshed Merge Requirements

The merged manga spine work should preserve:

- volume-level arc, recurrence, escalation, and payoff;
- panel/page production constraints;
- character continuity and store-series naming compatibility;
- visual proof and image/commercial-use gates;
- no assumption that one real series proof means pro-bar scale readiness.

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: serial spine config validates and assembles in dry-run
  using existing manga machinery.
- `OPERATOR_READ_PASS`: operator accepts story/visual continuity for a sampled
  spine.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted by this merge note.
