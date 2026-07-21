# CATALOG_GPU_DISPATCHER_V1_SPEC

Status: REFRESHED SPEC
Classification: REFRESH
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/CATALOG_GPU_DISPATCHER_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `598b183fab4aded8d017f638f9f1dee0da1419c8973bcdd081c1dfae6b6f5df3`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

The dispatcher idea remains useful as a work-discovery and queue-feeding layer,
but the source spec is stale in two ways:

- It assumes credential and GitHub substrate availability that is currently
  blocked.
- It refers to "spec #8 PS_QUEUE_DSN creds"; in this batch spec #8 is artifact
  retention, not credentials. That dependency must be corrected.

## Reconcile, Do Not Rebuild

This spec must extend existing queue/render orchestration instead of inventing a
parallel dispatcher:

- `docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`
- current PearlStar offline/GitHub suspension handoffs
- V5 queue and job-dispatch workstreams
- IMG render dual-path/substrate work
- deterministic social, image-bank, and faceless-video pipelines where visual
  work is involved

## Refreshed Scope

The dispatcher may:

- discover renderable/catalog work from current SSOT manifests;
- normalize job metadata into the existing queue schema;
- feed local/offline or approved remote queues;
- record provenance, substrate, and artifact outputs;
- dry-run without GitHub or public side effects.

The dispatcher must not:

- push to GitHub;
- assume `PS_QUEUE_DSN` or other credentials are available;
- publish social posts, images, videos, EPUBs, or store assets;
- bypass visual license, operator approval, R2, PearlStar, or release gates.

## Required Dependency Correction

Replace the stale dependency claim "spec #8 PS_QUEUE_DSN creds" with:

`Depends on approved queue substrate credentials and Conductor/PearlStar offline
availability. Artifact-retention SPEC-8 is related for outputs but is not the
credential dependency.`

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: dry-run discovers and serializes jobs without external
  writes; dependency fields record blocked substrates explicitly.
- `OPERATOR_READ_PASS`: operator accepts the job taxonomy and priority policy.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted. Live queues and public
  release require separate operator authorization and working substrate.
