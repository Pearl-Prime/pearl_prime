# ARTIFACTS_RETENTION_POLICY_V1_SPEC

Status: REFRESHED SPEC
Classification: REFRESH
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/ARTIFACTS_RETENTION_POLICY_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `d50932f496efee7513a94f5ccf87c0f97ff9a5025b5b99a907036b207dd1befa`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

Artifact retention remains necessary. The refresh must extend the existing
LFS-to-R2 and pointer-manifest work rather than creating a separate cleanup
system.

## Reconcile, Do Not Rebuild

Primary authority:

- `docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md`
- `.gitattributes`
- current R2 pointer-manifest and large-file audit artifacts
- existing drift/CI machinery

Do not rewrite git history. Do not delete durable archive content.

## Refreshed Policy

Each retention rule must define:

- artifact class and owner;
- keep duration;
- durable archive requirement;
- R2/offline pointer requirement;
- local-prune eligibility;
- dry-run evidence path;
- explicit owner/operator approval requirement for deletion;
- restore procedure.

Large binary directories require `.gitattributes`/offload coverage before new
assets are accepted.

## Required Tools

Future implementation may add:

- `scripts/ci/check_artifact_retention.py`
- `scripts/devops/prune_artifacts.py`

Both must default to dry-run, produce manifests, and avoid destructive behavior
without explicit operator approval.

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: retention manifest validates and dry-run identifies
  candidates without deleting or rewriting anything.
- `OPERATOR_READ_PASS`: owner/operator signs off on retention classes and any
  prune candidate list.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not applicable; this spec authorizes
  neither deletion nor release.
