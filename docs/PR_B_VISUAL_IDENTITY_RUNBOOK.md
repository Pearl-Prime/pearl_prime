# PR B — Visual identity covers (RunComfy / ComfyUI deployment)

**Full execution checklist (scope, acceptance, QA):** [PR_B_VISUAL_IDENTITY_EXECUTION_CHECKLIST.md](./PR_B_VISUAL_IDENTITY_EXECUTION_CHECKLIST.md)

**Goal:** Replace visual-identity placeholders with **real** KDP-honest cover outputs from the **RunComfy** path (same workflow family as `scripts/image_generation/runcomfy_batch.py`), then mark registry rows `ready` and validate onboarding surfaces.

## Credentials

See [INTEGRATION_CREDENTIALS_REGISTRY.md](./INTEGRATION_CREDENTIALS_REGISTRY.md) § **19. RunComfy**:

- `RUNCOMFY_API_KEY` (required)
- `RUNCOMFY_DEPLOYMENT_ID` (optional; default matches video bank)

Check your shell:

```bash
python3 scripts/ci/check_integration_env.py
```

## Fixed demo book (all six slots)

- **Title:** The Spiral Stops Here  
- **Subtitle:** A Practical Path Back to Calm, Clarity, and Direction  
- **Author:** Phoenix Press  
- **Lane / market / locale:** `self_help` / `us` / `en-US`  
- **Persona / topic:** `general_growth` / `transformation`  
- **Only variable:** `style_variant` (calm, dark, earthy, bold, premium, mysterious)

Prompt bodies match `specs/BRAND_ADMIN_ONBOARDING_IMAGE_PACK_V1_TRUST_LAYER_SPEC.md` § Batch 4.

## 1) Generate candidates

From repo root (3–5 candidates per slot recommended):

```bash
export RUNCOMFY_API_KEY="…"
python3 scripts/onboarding/generate_visual_identity_covers_runcomfy.py generate --candidates 5
```

Outputs land under `artifacts/onboarding_examples/visual_identity/runcomfy/<run_id>/` with a `manifest.json`.

Optional: one slot only:

```bash
python3 scripts/onboarding/generate_visual_identity_covers_runcomfy.py generate --candidates 5 --slots calm
```

## 2) Pick winners

Use the trust-layer rubric in the Image Pack v1 trust-layer spec (pass/fail gate + scorecard). Reject distorted anatomy, weak thumbnails, concept-art vibe, etc.

## 3) Promote winners into onboarding

Copy `scripts/onboarding/vi_winners.example.json` to a local file (e.g. `vi_winners.json`), replace paths with your chosen PNGs, then:

```bash
python3 scripts/onboarding/generate_visual_identity_covers_runcomfy.py promote \
  --winners vi_winners.json \
  --generation-run run_2026_04_03_approved \
  --qc-approved-by "<name>"
```

This copies files to `brand-wizard-app/public/onboarding/proof/generated/pack_v1_vi_*_v1.png` and syncs:

- `config/onboarding/example_registry.json`
- `brand-wizard-app/public/onboarding/example_registry.json`

## 4) UI validation

- Wizard visual-identity step (`brand-wizard-app` — `VISUAL_STYLES`)
- `brand-wizard-app/public/brand_admin_master_onboarding.html` proof strip
- `brand-wizard-app/public/lane_examples_gallery.html` — `cmp_visual_identity_v1`
- `brand-wizard-app/public/market_lane_matrix.html` thumbnails

## Copy alignment (sixth slot)

Registry id is **`pack_v1_vi_mysterious_v1`**. Product copy should say **Mysterious · Deep** (not “Cosmic” as the primary label). Wizard `VISUAL_STYLES` uses **Mysterious / Deep** for that card.

## Scope guard

Visual identity **only** — no archetypes, mission composite, systems boards, manga, or Pearl News in this PR.
