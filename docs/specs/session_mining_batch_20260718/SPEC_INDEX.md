# SPEC_INDEX - Phoenix Omega session-mining refresh set (2026-07-18)

This is the refreshed landing copy for the session-mining spec set from archive
`/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/`
and local commit `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`.

The original source artifacts are preserved. This copy classifies every spec and
ready-now dispatch brief against current SSOT, active workstreams, best Pearl
Prime book/story/exercise/atom/social/image/video work, and current repo
machinery. It is a spec refresh only. It does not implement systems and assumes
`GITHUB_WRITES=none` while the GitHub substrate is blocked.

## Classification Summary

| Classification | Count | Items |
|---|---:|---|
| KEEP | 1 | SPEC-5 |
| REFRESH | 9 | SPEC-1, SPEC-3, SPEC-4, SPEC-6, SPEC-8, SPEC-9, RN-1, RN-6, RN-9 |
| MERGE_WITH_EXISTING | 5 | SPEC-2, SPEC-7, RN-5, RN-7, RN-8 |
| RETIRE | 4 | RN-2, RN-3, RN-4, RN-10 |
| BLOCKED_NEEDS_OPERATOR | 0 | None |

## The 9 Specs

| ID | Spec | Source SHA256 | Classification | Landing Action |
|---|---|---|---|---|
| SPEC-1 | [ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST](ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md) | `957a74f9d89b6542feafb975ae69dc83ca1e105a96464e2abc42415b19b516dd` | REFRESH | Keep as measurement/spec work, but update from old surface-count framing to current atom-depth, reader-state, provenance, and exercise/story lessons. |
| SPEC-2 | [PROSE_INTEGRITY_VALIDATOR_SET](PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC.md) | `3c8b87267b0250e57a557cce3dc07d294e9093b79ba138fe8603390d8b8e5a40` | MERGE_WITH_EXISTING | Fold into existing `register_gate.py`, atom quality, story/literary, reader-layer, and exercise gates. Do not land a parallel validator module until gaps are mapped. |
| SPEC-3 | [CATALOG_GPU_DISPATCHER](CATALOG_GPU_DISPATCHER_V1_SPEC.md) | `598b183fab4aded8d017f638f9f1dee0da1419c8973bcdd081c1dfae6b6f5df3` | REFRESH | Keep as dispatcher spec, but align to Conductor V3, PearlStar/offline queue reality, V5 queue, IMG_RENDER_DUAL_PATH, no GitHub writes, and no public publishing. |
| SPEC-4 | [HUMAN_CALIBRATED_JUDGE](HUMAN_CALIBRATED_JUDGE_V1_SPEC.md) | `fcefdc443e12ae86fb91e4569c8af97d7392745e3f5cc3568d0f5a263736b593` | REFRESH | Keep as advisory calibration infrastructure. It must not become a hard ship gate or claim bestseller/public readiness without operator-read approval. |
| SPEC-5 | [STORE_SERIES_NAMING_ENGINE](STORE_SERIES_NAMING_ENGINE_V1_SPEC.md) | `39518d02dbc10a2502f0e0b32ba283476190f4fbf0732cd5cdc7f071780faea1` | KEEP | Still high-value and mostly additive. Extend existing naming machinery with current-status metadata and normal acceptance labels. |
| SPEC-6 | [FREE_TO_PAID_LADDER](FREE_TO_PAID_LADDER_V1_SPEC.md) | `17a766508b852075741b00317829fe45e3dc910933e63bf17e22d16ae27cf971` | REFRESH | Keep, but reconcile with live GHL feed, first paid EPUB, deterministic social dry-run, visual license gates, and no Metricool/live-publish assumption. |
| SPEC-7 | [MANGA_MULTIVOLUME_SPINE](MANGA_MULTIVOLUME_SPINE_V1_SPEC.md) | `4a30e5a12033b755dd513897f2c6a856f7359774af3143d4c166e7c8464ac630` | MERGE_WITH_EXISTING | Fold into current manga serial spine loader/config/story-architect machinery. Do not create parallel `series/spine.py` execution surface. |
| SPEC-8 | [ARTIFACTS_RETENTION_POLICY](ARTIFACTS_RETENTION_POLICY_V1_SPEC.md) | `d50932f496efee7513a94f5ccf87c0f97ff9a5025b5b99a907036b207dd1befa` | REFRESH | Keep, but extend the existing LFS-to-R2/offload policy with dry-run retention, owner signoff, pointer manifests, and no history rewrite. |
| SPEC-9 | [PLANTIME_CHAPTER_CONTRACT](PLANTIME_CHAPTER_CONTRACT_V1_SPEC.md) | `3c3d6e91993a3f0b40fad28a76a7d37107fdba2be1a12bfcfdb88e290f5f4596` | REFRESH | Keep, but use existing topic-aware chapter thesis resolver and book plan machinery. RN-2 is no longer a prerequisite. |

## Ready-Now Dispatch Briefs

These are not implementation instructions to fire blindly. Their refreshed status
is the authoritative dispatch state for this batch.

| ID | Brief | Classification | Current Dispatch Action |
|---|---|---|---|
| RN-1 | `check_tuple_viability` false `NO_STORY_POOL` | REFRESH | Still plausible/current. Patch only after confirming `phoenix_v4/gates/check_tuple_viability.py` does not consult the generic fallback or registry resolver before failing. |
| RN-2 | Thesis-bank re-key intent x engine x topic | RETIRE | Already landed in `config/planning/chapter_thesis_bank.yaml` with topic override and engine fallback resolver/tests. Do not re-run the old cohesion prompt. |
| RN-3 | `register_gate` F2.B phrasal-verb false positive | RETIRE | Already covered in `phoenix_v4/quality/register_gate.py` with stranded-preposition/phrasal tests. Do not add duplicate whitelist work. |
| RN-4 | F9 bare-slot detector | RETIRE | Already covered as F2.D wrapper placeholder/tradition leak detection with tests. Do not create a second F9 gate for the same failure class. |
| RN-5 | BISAC topic to `SEL036000` fix plus validator | MERGE_WITH_EXISTING | Mapping is already corrected in catalog skeleton generators. Add only the missing CI validator as part of catalog metadata gate coverage. |
| RN-6 | Word-budget clamp mid-sentence | REFRESH | Keep as a narrow renderer/boundary issue, but rederive current repro before patching. Do not reuse stale word-count claims as proof. |
| RN-7 | `.gitattributes` LFS carve-out CI gate | MERGE_WITH_EXISTING | Fold into SPEC-8 and existing LFS-to-R2 policy. Avoid standalone drift-gate duplication. |
| RN-8 | Cover-render consolidation | MERGE_WITH_EXISTING | Fold into current cover/visual registry and deterministic social/image-bank systems. No new isolated cover pipeline. |
| RN-9 | `DOCS_INDEX` completeness gate | REFRESH | Still useful, but the old 62% claim is stale. Recompute current completeness and avoid broad docs churn. |
| RN-10 | Dwell/integration-pacing craft gate | RETIRE | Existing F13 dwell/integration-starvation detector and tests cover the brief's core ask. Future severity tuning belongs to the register/craft-gate roadmap. |

## Acceptance Labels For This Batch

- `STRUCTURAL_SPEC_PASS`: each item is classified, stale claims are patched or retired, and no implementation files are changed.
- `OPERATOR_READ_PASS`: an operator accepts the refreshed priorities and any future public-facing release gates.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: explicit downstream authorization for live catalog, social, image, video, paid, or storefront release. No spec in this batch grants that authorization.

## No-GitHub Assumption

`git fetch --prune origin main` returned a 403 account-suspended failure during the refresh. This batch therefore records `GITHUB_SUBSTRATE=blocked` and `GITHUB_WRITES=none`.
