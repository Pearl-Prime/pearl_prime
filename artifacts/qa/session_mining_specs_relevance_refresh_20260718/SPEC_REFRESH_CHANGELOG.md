# SPEC_REFRESH_CHANGELOG - session-mining specs 2026-07-18

## Scope

Refreshed the offline landing copies for the 9 implementation specs and the
10 ready-now dispatch briefs under:

- `docs/specs/session_mining_batch_20260718/`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/`
- `artifacts/coordination/handoffs/session_mining_specs_*_2026-07-18.md`

No implementation files were edited. No GitHub writes were performed.

## Classification Counts

- KEEP: 1
- REFRESH: 9
- MERGE_WITH_EXISTING: 5
- RETIRE: 4
- BLOCKED_NEEDS_OPERATOR: 0

## Spec Changes

- SPEC-1 refreshed from surface-count inventory to atom surface/depth,
  reader-state, source, story, exercise, and variation measurement.
- SPEC-2 converted to a merge note because existing register/atom/story/exercise
  machinery already covers or partially covers the proposed validators.
- SPEC-3 refreshed for Conductor/PearlStar/offline queue reality, GitHub
  suspension, no-live-publish constraints, and corrected stale credential
  dependency.
- SPEC-4 refreshed as advisory human-calibration infrastructure only.
- SPEC-5 kept with metadata, acceptance labels, and existing naming machinery
  reconciliation.
- SPEC-6 refreshed for GHL feed, first paid EPUB, deterministic social dry-run,
  visual license gates, faceless video, and no live-publish assumption.
- SPEC-7 converted to a merge note for existing manga serial spine machinery.
- SPEC-8 refreshed as an extension of LFS-to-R2/offload/pointer-manifest policy
  with dry-run and owner signoff.
- SPEC-9 refreshed to consume existing topic-aware thesis resolver and current
  story/exercise/atom/reader-layer standards.

## Ready-Now Brief Changes

- RN-1 remains actionable but is refreshed as a repro-first patch against the
  current tuple viability gate.
- RN-2 retired as already completed.
- RN-3 retired as already completed.
- RN-4 retired as already completed under the existing placeholder leak gate.
- RN-5 merged with existing catalog metadata work; only validator remains.
- RN-6 remains actionable but requires current renderer repro.
- RN-7 merged into artifact retention/offload policy.
- RN-8 merged into cover/visual authority cleanup.
- RN-9 remains actionable but requires a current docs completeness sweep.
- RN-10 retired as already covered by F13 dwell/integration-starvation tests.

## Known Substrate Limits

- `GITHUB_SUBSTRATE=blocked`
- `GITHUB_WRITES=none`
- `PEARLSTAR_REF=not_pushed_dirty_shared_root`

PearlStar offline push was not attempted because the shared working tree had
substantial unrelated dirty state before this refresh. The safe landing artifact
is the explicit path-scoped local diff plus this proof bundle.
