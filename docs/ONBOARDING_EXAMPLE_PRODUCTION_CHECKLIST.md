# Onboarding Example Production Checklist

**Purpose:** Operational steps to fill [config/onboarding/example_registry.json](../config/onboarding/example_registry.json) with **`status: "ready"`** assets per [specs/ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md](../specs/ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md).

**Related:** [specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md](../specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md), [docs/BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md](./BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md).
Backlog tracker: [docs/ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md](./ONBOARDING_PROOF_ASSET_PRODUCTION_BACKLOG.md).

---

## Phase 1 — Inventory

- [ ] Pull existing shippable outputs: `public/breathwork/`, `delf/`, `funnel/`, `SOURCE_OF_TRUTH/freebies/templates/`, manga artifacts, Pearl News layouts, covers.
- [ ] For each file, add or update a registry row with correct `proof_intent`, `production_fidelity`, `product_family`.
- [ ] Set `status: "ready"` only after QC pass.

## Phase 2 — Gap analysis

- [ ] Map inventory to [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md §3.1](../specs/ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md#31-by-lane-minimum-slots) lane slots.
- [ ] Map to each **`cmp_*`** set in §3.3; ensure every member row exists (can stay `planned`).
- [ ] Run `python3 scripts/ci/report_onboarding_proof_completion.py` and review `artifacts/onboarding/proof_completion_latest.md`.

## Phase 3 — Generate missing pipeline outputs

Priority: self-help covers → persona/topic supporting visuals (honest `supporting_visual`) → manga panels → article heroes → audiobook packaging → landing variants.

- [ ] Run pipeline jobs per `product_family` (commands TBD in dev runbooks).
- [ ] Set `generation_run` / commit ref on rows.

## Phase 4 — Comparison boards

- [ ] Complete `cmp_burnout_cross_persona_v1`, `cmp_anxiety_locale_v1`, `cmp_burnout_format_v1` first (tier 1).
- [ ] Then `cmp_burnout_posture_v1`, `cmp_manga_style_mode_v1`.

## Phase 5 — Wire UI

- [ ] Gallery + wizard consume JSON from deployed `/onboarding/` path.
- [ ] Verify load-failure fallbacks (stale `ready`).

## Phase 6 — Sign-off

- [ ] Internal “example-complete”: ≥3 of 5 `cmp_*` sets fully `ready` or documented exception (Real Example Spec §3.3).
- [ ] Pearl_Editor QC sign-off on captions and `proof_intent` accuracy.

## Phase 7 — Smoke test (local + Pages)

- [ ] Local static serve from repo root: `python3 -m http.server 8765`
- [ ] Verify routes:
  - [ ] `http://localhost:8765/brand_onboarding_hub.html`
  - [ ] `http://localhost:8765/lane_examples_gallery.html`
  - [ ] `http://localhost:8765/market_lane_matrix.html`
- [ ] Verify deployed routes:
  - [ ] `https://brand-admin-onboarding.pages.dev/onboarding/example_registry.json` (200)
  - [ ] `https://brand-admin-onboarding.pages.dev/onboarding/proof/cmp_bp_founder_v1.svg` (200)
- [ ] In live wizard, validate persona -> lane -> market changes alter proof IDs shown in Output Proof strip.
