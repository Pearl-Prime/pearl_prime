# `config/music/` — Music-mode configuration directory

Last updated: 2026-05-09  
Owner: pearl_brand  
Authority: `MUSIC-MODE-BRAND-INTEGRATION-V1-01` (cap entry in `docs/PEARL_ARCHITECT_STATE.md`)  
Spec: `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md`

## What lives here

This directory holds the SSOT configuration for **music-mode** content — the
first-class brand archetype introduced by `MUSIC-MODE-BRAND-INTEGRATION-V1-01`.

| File | Role |
|---|---|
| **`music_brand_registry.yaml`** | **SSOT** index of music-mode brands (38+). Authoritative cross-walk to per-brand wizard YAML survey output. **NEW in this PR.** |
| `brand_music_dna.yaml` | Per-brand sonic-signature parameters (key offset, BPM multiplier, etc.) for anti-spam differentiation. Pre-existing; unrelated to brand identity. |
| `exercise_music_mapping.yaml` | Mapping between somatic-exercise variants and music tracks. Pre-existing; consumer of brand DNA. |
| `therapeutic_music_prompts.yaml` | Prompts for therapeutic music generation. Pre-existing; consumer of brand DNA. |

## `music_brand_registry.yaml` is the SSOT for music-mode brands

`music_brand_registry.yaml` is the **only** authoritative index of music-mode
brands. New brands enter the registry **exclusively** via the brand wizard +
`musician_reflections_survey` save flow (separate workstreams — see spec §2/§3).
The registry references each brand's persisted wizard YAML through a
`survey_yaml_pointer`; brands without that backing are forbidden ("silent-mint"
prohibition, spec §5).

Schema, ID-space, and per-entry contract are documented inline in
`music_brand_registry.yaml` (file header). Defaults locked by the
`MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT` (PR #975, commit `38c6596f95`):

- **Q1** — UX flow placement: mode selector at wizard step 1
- **Q2** — `brand_id` slug: `<musician_handle>_music`
- **Q3** — Catalog volume tier: 800 baseline
- **Q4** — Inactive brand path: same brand wizard YAML SSOT (do not delete; flip
  `status` to `inactive`)

## Path X boundary — `config/manga/canonical_brand_list.yaml` is read-only

Path X (`config/manga/canonical_brand_list.yaml`) holds the **37 manga-pipeline
canonical brands**. From the music-mode side, that file is **read-only**:

- Music-mode brands **MUST NOT** be appended to `canonical_brand_list.yaml`.
- `brand_id` values in `music_brand_registry.yaml` **MUST NOT** collide with any
  key under `canonical_brand_list.yaml.brands`.
- The `id_space_start: 38` field in `music_brand_registry.yaml` reserves the
  numeric space above the 37 Path X entries.

Reference: `config/manga/canonical_brand_list.yaml` header lines 1–38; cap
entries `BR-CANON-01` and `MUSIC-MODE-BRAND-INTEGRATION-V1-01` in
`docs/PEARL_ARCHITECT_STATE.md`.

## Cross-references

- Cap entries: `MUSIC-MODE-BRAND-INTEGRATION-V1-01`,
  `MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT`,
  `MUSIC-MODE-V1-01` (rendering / atom-bank authority — distinct concern),
  `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` (active-brand SSOT alignment, Q4).
- Spec: `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` (esp. §4 catalog
  volume rule, §5 registry architecture, §7 anti-drift, §16 operator decision
  card).
- Survey schema: `artifacts/musician_survey/SURVEY_TEMPLATE.yaml`.
- Active workstreams (`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`):
  - `ws_music_brand_registry_music_brand_registry_yaml_20260509` (this PR)
  - `ws_music_brand_wizard_step1_step4_survey_pane_20260509`
  - `ws_music_brand_survey_save_post_yaml_advance_20260509`
  - `ws_music_brand_catalog_generator_100pct_music_mode_20260509`
  - `ws_music_brand_wizard_live_embed_routing_20260509`
  - `ws_music_brand_freebie_funnel_followup_cap_20260509` (placeholder; future cap)

## Out of scope for this directory

- Wizard UX code (`brand-wizard-app/*`).
- Loader / validator scripts (`scripts/*`).
- Catalog generator wiring (`artifacts/catalog/*`,
  `phoenix_v4/catalog_planner.py`, etc.).
- The `MUSIC-MODE-V1-01` overlay / `musician_banks/` rendering system — that is
  a *rendering* authority and is consumed unchanged by this program.

These land under their own workstreams; do not extend this directory's scope
without an AMENDMENT to `MUSIC-MODE-BRAND-INTEGRATION-V1-01`.
