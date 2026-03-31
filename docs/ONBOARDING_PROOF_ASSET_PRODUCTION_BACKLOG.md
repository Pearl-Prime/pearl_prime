# Onboarding Proof Asset Fidelity Backlog

Purpose: track **fidelity replacement** now that onboarding proof coverage is complete.

Operational lane: [docs/ONBOARDING_PROOF_FIDELITY_UPGRADE_LANE.md](./ONBOARDING_PROOF_FIDELITY_UPGRADE_LANE.md).

Current baseline (locked):

- System is fully wired and production-observable.
- Proof coverage is complete via in-repo pipeline-demo assets.
- `artifacts/onboarding/proof_completion_latest.md` currently reports `ready=19, planned=0, missing=0`.

## What this backlog is now for

This backlog is **not** for system completeness anymore. It is for optional upgrade from demo fidelity to production-export fidelity.

## Fidelity replacement targets

### Candidate rows to upgrade from demo to production exports

- Comparison rows with `source: onboarding_pipeline_demo`
- Seed-backed rows (`source: onboarding_seed_asset`) that should eventually use production exports
- Any gallery anchor that currently points to generated demo art but should become production output

## Acceptance criteria per fidelity replacement

For each upgraded row:

1. Keep `status: "ready"` (no regression to planned/missing).
2. Replace `asset_path` with production-export path/URL.
3. Update metadata truthfully (for example `source: pipeline` or `production_export` and matching `production_fidelity`).
4. Keep caption aligned to actual asset type.
5. Re-run:
   - `PYTHONPATH=. python3 scripts/ci/validate_onboarding_registry.py`
   - `python3 scripts/ci/report_onboarding_proof_completion.py`
6. Re-run Pages smoke for changed paths.

## Guardrails

- Do not reintroduce `planned`/`missing` for critical onboarding proof rows unless explicitly intentional:
  - set `intentional_non_ready: true`
  - include a non-empty `placeholder_reason`

This policy is enforced by `scripts/ci/validate_onboarding_registry.py`.
