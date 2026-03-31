# Onboarding Example Production Checklist

**Purpose:** Operational steps to maintain onboarding proof coverage and execute optional fidelity upgrades in [config/onboarding/example_registry.json](../config/onboarding/example_registry.json).

**Related:** [specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md](../specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md), [docs/BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md](./BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md).
Backlog tracker: [docs/ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md](./ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md). Fidelity upgrade lane: [docs/ONBOARDING_PROOF_FIDELITY_UPGRADE_LANE.md](./ONBOARDING_PROOF_FIDELITY_UPGRADE_LANE.md). Repo hygiene: [docs/REPO_HYGIENE_AND_WORKTREE_CLEANUP.md](./REPO_HYGIENE_AND_WORKTREE_CLEANUP.md).

---

## Current baseline

- [x] Proof coverage complete: `ready=19, planned=0, missing=0` (see latest report).
- [x] Comparison sets fully populated with ready assets.
- [x] Pages deployment and smoke routes verified.

## Phase 1 — Inventory (for fidelity upgrades)

- [ ] Pull existing shippable outputs: `public/breathwork/`, `delf/`, `funnel/`, `SOURCE_OF_TRUTH/freebies/templates/`, manga artifacts, Pearl News layouts, covers.
- [ ] For each file, add or update a registry row with correct `proof_intent`, `production_fidelity`, `product_family`.
- [ ] Keep `status: "ready"` for existing covered rows; only replace asset fidelity.

## Phase 2 — Coverage/fidelity analysis

- [ ] Map inventory to [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md §3.1](../specs/ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md#31-by-lane-minimum-slots) lane slots.
- [ ] Map to each **`cmp_*`** set in §3.3; ensure every member row remains `ready`.
- [ ] Run `python3 scripts/ci/report_onboarding_proof_completion.py` and review `artifacts/onboarding/proof_completion_latest.md`.

## Phase 3 — Generate replacement production exports

Priority: self-help covers → persona/topic supporting visuals (honest `supporting_visual`) → manga panels → article heroes → audiobook packaging → landing variants.

- [ ] Run pipeline jobs per `product_family` (commands TBD in dev runbooks).
- [ ] Set `generation_run` / commit ref on rows where available.

## Phase 4 — Comparison board fidelity hardening

- [ ] Replace demo assets in priority comparison sets while keeping all rows `ready`.

## Phase 5 — Wire UI

- [ ] Gallery + wizard consume JSON from deployed `/onboarding/` path.
- [ ] Verify load-failure fallbacks (stale `ready`).

## Phase 6 — Sign-off

- [ ] Internal “example-complete”: all required `cmp_*` rows remain `ready`.
- [ ] Pearl_Editor QC sign-off on captions and `proof_intent` accuracy.

## Phase 7 — Smoke test (local + Pages)

- [ ] Local static serve from repo root: `python3 -m http.server 8765`
- [ ] Verify routes:
  - [ ] `http://localhost:8765/brand_onboarding_hub.html`
  - [ ] `http://localhost:8765/lane_examples_gallery.html`
  - [ ] `http://localhost:8765/market_lane_matrix.html`
- [ ] Verify deployed routes:
  - [ ] `https://brand-admin-onboarding.pages.dev/onboarding/example_registry.json` (200)
  - [ ] `https://brand-admin-onboarding.pages.dev/onboarding/proof/generated/cmp_bp_caregiver_v1.svg` (200)
- [ ] In live wizard, validate persona -> lane -> market changes alter proof IDs shown in Output Proof strip.
