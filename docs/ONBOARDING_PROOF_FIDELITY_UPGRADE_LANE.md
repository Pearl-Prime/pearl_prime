# Onboarding proof — fidelity upgrade lane

Purpose: replace **pipeline-demo** (and optional seed) proof assets with **production-export** outputs while keeping the onboarding system fully wired and fully proof-covered.

**Locked baseline:** Coverage is complete today via `onboarding_pipeline_demo` assets; this lane is **fidelity only**, not completeness.

**Companion:** [docs/ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md](./ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md), [specs/ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md](../specs/ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md), [scripts/onboarding/generate_onboarding_proof_demos.py](../scripts/onboarding/generate_onboarding_proof_demos.py) (deterministic demos — **do not** treat as production exports).

---

## Governance and inference

- Use the **Qwen API key lane** for any automated LLM steps in this repo ([docs/AGENT_QWEN_API_KEY_LANE.md](./AGENT_QWEN_API_KEY_LANE.md)); do not frame the default path as a local runtime.
- **Honest metadata:** `source`, `production_fidelity`, and captions must match the actual asset. `validate_onboarding_registry.py` enforces consistency for `ready` rows and blocks critical rows from slipping back to `planned`/`missing` without an explicit intentional marker.

---

## Suggested upgrade order

1. High-visibility comparison rows (`source: onboarding_pipeline_demo` under `/onboarding/proof/generated/`).
2. Remaining seed-backed rows (`source: onboarding_seed_asset`) where product marketing needs production parity.
3. Gallery anchors that should showcase real pipeline variety, not demo gradients.

---

## Per-asset procedure

1. **Generate or export** the real output using the same path that ships product for that `product_family` / `format` (see real-example spec).
2. **Commit the asset** under `brand-wizard-app/public/onboarding/proof/…` (or R2/Pages path if you later move binaries; keep `asset_path` truthful).
3. **Update** the row in `config/onboarding/example_registry.json`:
   - keep `status: "ready"`
   - set `asset_path` to the new file
   - set `source` / `production_fidelity` to production truth (for example `production_export` + `production` where appropriate)
   - remove or update `placeholder_reason`
4. **Sync** public mirror: `scripts/onboarding/sync_onboarding_config_to_public.sh` (or `npm run build` in `brand-wizard-app/`, which runs prebuild sync).
5. **Validate:**
   - `PYTHONPATH=. python3 scripts/ci/validate_onboarding_registry.py`
   - `python3 scripts/ci/report_onboarding_proof_completion.py`
6. **Deploy + smoke:** merge to `main`, run `brand-admin-onboarding-pages.yml`, then `curl` new `asset_path` URLs on Pages.

---

## Definition of done (this lane)

- No regression: proof completion report stays `planned=0, missing=0` for critical paths unless explicitly intentional and documented.
- Pages 200 for every changed `asset_path`.
- No claim of “production-real” unless metadata says so.
