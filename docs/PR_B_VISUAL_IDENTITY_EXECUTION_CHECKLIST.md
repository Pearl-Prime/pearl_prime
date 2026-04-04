# PR B — Generate real KDP-honest visual identity assets (execution checklist)

**Automation in repo:** RunComfy candidate generation + promote → `scripts/onboarding/generate_visual_identity_covers_runcomfy.py` and `docs/PR_B_VISUAL_IDENTITY_RUNBOOK.md`. **Raster fallbacks** (pipeline-demo tier, honest `production_fidelity`): `scripts/onboarding/generate_onboarding_proof_pngs.py`.

---

## Goal

Replace the six visual-identity placeholders with **real cover outputs** produced through the **actual cover pipeline path** (RunComfy when promoted; interim Pillow proofs remain `pipeline_demo`), then wire **ready** assets into onboarding surfaces.

**Six registry slots (wizard + proof strip + gallery):**

- `pack_v1_vi_calm_v1`
- `pack_v1_vi_dark_v1`
- `pack_v1_vi_earthy_v1`
- `pack_v1_vi_bold_v1`
- `pack_v1_vi_premium_v1`
- `pack_v1_vi_mysterious_v1`

Authority: `specs/BRAND_ADMIN_ONBOARDING_IMAGE_PACK_V1_TRUST_LAYER_SPEC.md` (Image Pack v1 trust layer).

---

## Scope

### In scope

- Generate six real cover outputs through the **cover pipeline** (RunComfy path documented; see runbook).
- Pick **one winner per style** from **3–5 candidates**.
- Export final **UI-ready** assets (2:3; web-optimized).
- Registry: `status: "ready"`, valid `asset_path`, traceability fields when available (`seed`, `model_id`, `template_id`, `generation_run`, `qc_approved_by`).
- Verify: wizard visual-identity step, `brand_admin_master_onboarding.html` proof strip, `lane_examples_gallery.html` (`cmp_visual_identity_v1`), `market_lane_matrix.html` thumbs.

### Out of scope

- Archetypes, mission composite, systems boards, manga proof, Pearl News proof, narrator voice step.

---

## Branch / PR naming

- **Branch:** `agent/brand-media-pr-b-visual-identity-ready`
- **PR title:** `feat(onboarding): ship real visual identity cover outputs for wizard step`

---

## Fixed contract (all six)

| Field | Value |
|--------|--------|
| `lane` | `self_help` |
| `market` | `us` |
| `locale` | `en-US` |
| `persona` | `general_growth` |
| `topic` | `transformation` |
| `platform_mix` | `["amazon_kdp"]` |
| Title / subtitle / author | Same demo package for all six (see below). |

**Only variable:** `style_variant` (teaches visual identity, not topic drift).

### Demo book metadata (suggested)

- **Title:** The Spiral Stops Here  
- **Subtitle:** A Practical Path Back to Calm, Clarity, and Direction  
- **Author:** Phoenix Press  

---

## Style intents (registry ids)

1. **Calm** — `pack_v1_vi_calm_v1` — serene, spacious, emotionally safe, soft, minimal, restrained.  
2. **Dark** — `pack_v1_vi_dark_v1` — moody, deep, intense, serious, premium, not horror.  
3. **Earthy** — `pack_v1_vi_earthy_v1` — grounded, natural, warm, restorative, tactile, trusted.  
4. **Bold** — `pack_v1_vi_bold_v1` — assertive, high contrast, decisive, modern, thumbnail-strong.  
5. **Premium** — `pack_v1_vi_premium_v1` — refined, geometric, precise, luxury-positioned, timeless.  
6. **Mysterious** — `pack_v1_vi_mysterious_v1` — atmospheric, magnetic, contemplative, subtle, spiritual-transformation adjacent.

---

## Generation workflow

1. **Run the real cover path** — 3–5 candidates per slot (RunComfy: `generate_visual_identity_covers_runcomfy.py generate`). Acceptable: full cover pipeline or cover-art-base + compositor. **Not acceptable:** raw concept art posing as a cover.  
2. **Candidate review** — reject distorted anatomy, weak thumbnails, concept-art vibe, bad title hierarchy, etc.  
3. **Winner selection** — trust-layer rubric (contract fidelity, product realism, legibility, commercial quality, distinctiveness, emotional precision, technical cleanliness).  
4. **Normalize set** — family resemblance + distinct identities + thumbnail check.

---

## Asset paths

**Canonical static URLs (Pages / Vite public):**  
`/onboarding/proof/generated/pack_v1_vi_<style>_v1.png`

Optional artifact staging (pre-promote):  
`artifacts/onboarding_examples/visual_identity/runcomfy/<run_id>/…`

---

## Registry files

- `config/onboarding/example_registry.json`  
- `brand-wizard-app/public/onboarding/example_registry.json` (must match canonical)

### Do not change on these rows

- `comparison_set_id`: `cmp_visual_identity_v1`  
- `proof_intent`: `teaches_comparison`  
- `production_fidelity`: upgrade only when team formally changes labeling  
- `product_family`: `book_engine`  

### Example row shape (after RunComfy promote)

```json
{
  "id": "pack_v1_vi_calm_v1",
  "status": "ready",
  "asset_path": "/onboarding/proof/generated/pack_v1_vi_calm_v1.png",
  "platform_mix": ["amazon_kdp"],
  "seed": "482001",
  "model_id": "runcomfy_flux_deployment_default",
  "template_id": "kdp_visual_identity_v1",
  "generation_run": "run_2026_04_xx",
  "qc_approved_by": "name_or_team"
}
```

---

## UI validation targets

1. **Wizard** — `brand-wizard-app` Step 6 visual style cards show proof thumbnails (paths above).  
2. **`brand_admin_master_onboarding.html`** — proof strip VI IDs resolve.  
3. **`lane_examples_gallery.html`** — `cmp_visual_identity_v1` board.  
4. **`market_lane_matrix.html`** — lane preview uses `pack_v1_vi_premium_v1` without broken paths.

---

## Copy alignment (sixth slot)

**Preferred:** UI label **Mysterious / Deep** (registry: `vi_mysterious` / `pack_v1_vi_mysterious_v1`). Do **not** add `vi_cosmic` in this PR.

Product labels aligned to registry:

- Calm / Minimal  
- Dark / Intense  
- Earthy / Organic  
- Bold / Modern  
- Premium / Geometric  
- Mysterious / Deep  

---

## Acceptance criteria

- [ ] Six cover assets exist at published paths.  
- [ ] All six share fixed demo metadata except `style_variant`.  
- [ ] Registry rows `ready` with valid `asset_path`.  
- [ ] Wizard, master onboarding strip, gallery board, matrix render without broken images.  
- [ ] No “Pending” for these six where the surface reads registry status.  
- [ ] `production_fidelity` and `source` remain truthful (RunComfy vs Pillow pipeline-demo).

---

## QA (abbreviated)

**Visual:** per-style intent + thumbnails + no concept-art pose.  
**Technical:** JSON valid; public registry synced; no console errors on proof surfaces.  
**Truthfulness:** `ready` only with real files; fidelity labels honest.

---

## Suggested PR body

**Summary:** Ship six visual-identity cover outputs; registry `ready`; proof surfaces populated; sixth slot copy = Mysterious / Deep.  
**Scope guard:** Visual identity only.  
**Validation:** Registry check, local Pages/Vite spot-check, manual visual QA.

---

## Merge when

Six assets on disk, registry truthful, proof surfaces green, sixth-slot copy decision recorded (this doc + wizard).
