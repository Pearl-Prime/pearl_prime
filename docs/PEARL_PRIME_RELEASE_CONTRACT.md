# Pearl Prime Release Contract

**Purpose:** Define the repo-owned, authoritative release and evidence contract for the Pearl Prime main pipeline.

**Scope:** This contract covers the main pipeline that compiles books through [`scripts/run_pipeline.py`](../scripts/run_pipeline.py), the CI/release gates that protect `main`, and the evidence artifacts that must exist for release-path claims.

## What Pearl Prime is in this repo

Pearl Prime is the main system pipeline for book compilation and release validation in this repository.

Its authoritative surfaces are:

- pipeline entrypoint: [`scripts/run_pipeline.py`](../scripts/run_pipeline.py)
- production readiness gates: [`scripts/run_production_readiness_gates.py`](../scripts/run_production_readiness_gates.py)
- rigorous suite: [`scripts/ci/run_rigorous_system_test.py`](../scripts/ci/run_rigorous_system_test.py)
- real pipeline canary: [`scripts/ci/run_canary_100_books.py`](../scripts/ci/run_canary_100_books.py)
- rollback smoke: [`scripts/release/rollback_smoke.sh`](../scripts/release/rollback_smoke.sh)
- release workflow: [`.github/workflows/release-gates.yml`](../.github/workflows/release-gates.yml)

## What is authoritative

For Pearl Prime release readiness, authoritative proof lives in:

1. canonical required GitHub checks on `main`
2. repo-owned release evidence artifacts written by the release path
3. rollback proof and release checklist artifacts under `artifacts/`

The canonical required checks remain:

- `Core tests`
- `Release gates`
- `EI V2 gates`
- `Change impact`

Machine authority for that set is [`config/governance/required_checks.yaml`](../config/governance/required_checks.yaml).

## What is not authoritative

`Workers Builds: pearl-prime` from Cloudflare is currently **non-blocking operational noise**, not the authoritative Pearl Prime release signal.

Unless this repo gains a versioned Cloudflare deployment contract for that target, Cloudflare preview/build status must not be treated as the source of truth for Pearl Prime release readiness.

## Required release evidence

For release-path claims, the repo-owned evidence bundle is:

- [`artifacts/release/pearl_prime_release_evidence.json`](../artifacts/release/pearl_prime_release_evidence.json)

That bundle must summarize the presence of:

- rollback smoke evidence: `artifacts/release/rollback_smoke_evidence.json`
- canary summary: `artifacts/canary_plans/canary_summary.json`
- latest systems-test report: `artifacts/systems_test/report_*.json`

Optional but useful supporting evidence:

- `artifacts/canary_plans/canary_failures.json`
- `artifacts/reports/pearl_prime_sim_analysis.json`
- `artifacts/observability/signal_snapshot*.json`
- `artifacts/observability/evidence_log.jsonl`

## Release workflow contract

The release workflow must:

1. run production readiness gates
2. run rigorous system test on non-PR release paths
3. run a real pipeline canary on non-PR release paths
4. run rollback smoke on non-PR release paths
5. write `artifacts/release/pearl_prime_release_evidence.json`
6. upload the evidence artifact bundle

## Relationship to production 100%

This contract does not lower the bar in [`docs/RIGOROUS_SYSTEM_TEST.md`](./RIGOROUS_SYSTEM_TEST.md). It makes the release path repo-owned and explicit.

Production 100% still requires:

- real pipeline canaries
- CI gate on analyzer regression thresholds
- evidence on `main`
- release-path smoke with rollback proof

## Operational implication

If Pearl Prime is the main system pipeline, the release claim should be made from this contract and its evidence bundle, not from a detached external integration.
