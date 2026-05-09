# Music-mode catalog branch — implementation notes (2026-05-10)

**Workstream:** `ws_music_brand_catalog_generator_100pct_music_mode_20260509`  
**Authority:** `MUSIC-MODE-BRAND-INTEGRATION-V1-01` / `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` §4

## Behavior

1. **`CatalogPlanner.generate_for_brand(brand_id, n, ...)`** (`phoenix_v4/planning/catalog_planner.py`) calls **`scripts/catalog/music_mode_branch.resolve_catalog_branch`** using `config/music/music_brand_registry.yaml` and `config/manga/canonical_brand_list.yaml`.
2. **Music registry hit** → branch `MUSIC_ONLY`: wave is built with `default_teacher` and `teacher_mode=False`, then **`filter_to_music_mode_book_specs`** removes any row with `teacher_mode` or `catalog_pipeline_mode` in `composite` / `teacher_mode` (defensive for future hybrid tagging).
3. **Path X / other brands** → branch `STANDARD`: same as **`produce_wave`** with identical arguments (no extra filter).
4. **Brand in both YAMLs** (misconfiguration) → **music precedence** + **WARNING** log from `resolve_catalog_branch`.

## Sample (`_template_music`, `n=3`, `seed="demo"`)

First row (`BookSpec.to_dict()`), from `CatalogPlanner().generate_for_brand("_template_music", 3, seed="demo")`:

```json
{
  "topic_id": "relationship_anxiety",
  "persona_id": "gen_z_professionals",
  "series_id": "overthinking",
  "installment_number": 1,
  "teacher_id": "default_teacher",
  "brand_id": "_template_music",
  "angle_id": "analysis_paralysis",
  "domain_id": "cognitive_cluster",
  "seed": "45800820c858930d25685cf9",
  "locale": "en-US",
  "territory": "US",
  "teacher_mode": false
}
```

All rows for a music-registry brand share **`teacher_mode: false`** and **`teacher_id: default_teacher`** under the music branch.

## Files

| File | Role |
|------|------|
| `scripts/catalog/music_mode_branch.py` | Registry load, branch resolution, dict + BookSpec filters |
| `phoenix_v4/planning/catalog_planner.py` | `generate_for_brand` entry point |
| `tests/catalog/test_music_mode_branch.py` | Unit + planner parity tests |
