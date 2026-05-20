# Prompt Template Slots — Human-Readable Index

**Authority:** `slot_registry.yaml` is the machine-readable canonical source. This file is a human-readable index.
**Spec:** `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §5.9 (v0.5.1 additive-safe semantics).

## Validation rules (compiler enforces)

| condition | behavior |
|---|---|
| Template uses slot, registry has `required`, contract provides value | OK — substitute |
| Template uses slot, registry has `required`, contract missing value | **FATAL** |
| Template uses slot, registry has `optional`, contract missing value | OK — use `default_when_missing` |
| Template uses slot NOT in registry | **FATAL** |
| Contract provides slot value, template doesn't reference | WARN (logged, not blocking) |
| Registry declares slot, no template uses it yet | OK (additive-safe future capacity) |

## Slot source bindings (where the values come from)

| slot prefix | source | notes |
|---|---|---|
| `scene.*` | `config/source_of_truth/manga_profiles/series/<series>.scene_inventory.yaml` | per scene_id |
| `character.*` | `config/source_of_truth/manga_profiles/series/<series>.yaml` `character_design` block | per character_id |
| `continuity.*` | `artifacts/manga/<series>/continuity_state/<episode>/<panel>.yaml` | per panel; inherits from prior panel |
| `safe_zone.*` | `config/manga/compiled/safe_zones.yaml` row keyed by `subject=X\|framing=Y\|genre=Z` | output of `compile_safe_zones.py` |
| `light_rig.*` | `config/manga/light_rigs/<genre>.yaml` keyed by `light_rig_id` from scene_inventory | per scene + temporal_state |
| `style_state.*` | `config/source_of_truth/manga_profiles/series/<series>.style_state.yaml` | per series, canonical |
| `genre.*` | `config/manga/drawing_tradition_per_genre.yaml` for the series's genre | per genre |
| `resolution.*` | panel template `render_resolution` or scene_inventory override | typically [1080, 1920] webtoon vertical |

## L0 slots — Foundation backdrop

### Required
- `scene.description` — multi-sentence description of the scene
- `scene.subject_bbox_region_clause` — natural-language description of where subject will go (e.g., "upper-right third", "lower-left")
- `scene.scene_specific_composition_clause` — scene-unique composition guidance (e.g., "houseplant on windowsill at lower-left")
- `scene.forbidden_objects_clause` — comma list of hero objects to exclude (e.g., "kettle, cup, phone")
- `light_rig.prompt_clause` — full lighting injection string (§6.9)
- `style_state.line_weight_clause`, `style_state.wash_softness_clause`, `style_state.tonal_density_clause`, `style_state.shading_aggression_clause` — 4 style axes (§6.12)
- `genre.drawing_tradition_clause` — drawing-tradition prose from `drawing_tradition_per_genre.yaml`
- `genre.forbidden_grammar_clause` — per-genre forbidden visual grammar (e.g., iyashikei → "no speed lines, no dutch angles")
- `resolution.width`, `resolution.height` — output dimensions (int)

### Optional
- `scene.atmospheric_clause` — extra atmospheric notes (`""` default)
- `scene.palette_clause` — series-specific palette override (`""` default; genre palette inherited if absent)

## L2 slots — Character on isolated backdrop

### Required
- `character.render_prompt_base` — full character description from `character_design`
- `character.negative_prompt_base` — character-specific negative prompt
- `continuity.pose_clause` — pose description (e.g., "seated upright, hands wrapping cup")
- `continuity.gaze_clause` — gaze direction phrase
- `continuity.hand_state_clause` — hand-state phrase
- `continuity.emotional_clause` — emotional state description (matches §6.2 enum)
- `continuity.expression_dial` — float 0.0–1.0 (formatted to one decimal in template)
- `safe_zone.framing_clause` — framing-type description (e.g., "close-up: face + shoulders")
- `safe_zone.subject_zone_pct_str` — formatted "65% × 80%" string
- `safe_zone.margin.top`, `safe_zone.margin.bottom`, `safe_zone.margin.left`, `safe_zone.margin.right` — numbers
- `safe_zone.shoulder_margin_clause` — pre-rendered clause (e.g., "both shoulders fully inside frame with ≥17% margin")
- `safe_zone.backdrop_name` — "pure white" / "pure black" / "mid-gray"
- `safe_zone.backdrop_hex` — "#FFFFFF" / "#000000" / "#808080"
- `light_rig.prompt_clause`, `style_state.*` — same as L0
- `genre.forbidden_grammar_clause` — same as L0
- `resolution.width`, `resolution.height` — same as L0

### Optional
- `character.wardrobe_override` — per-panel wardrobe variation (`""` default)
- `continuity.breath_phase_clause` — for somatic archetypes (`""` default)

## L1, L3, L4

Schema-reserved in `slot_registry.yaml` but no slots declared yet. Templates land in Phase C alongside inventory authoring.

## Adding a new slot

1. Add to `slot_registry.yaml` under the appropriate layer's `required` or `optional` block
2. Add row to this file
3. Identify source binding (which YAML produces it)
4. Optionally reference it from a template (otherwise registry-only is fine — additive-safe)
5. Bump template version if a template now requires it (MAJOR if required, MINOR if optional)
