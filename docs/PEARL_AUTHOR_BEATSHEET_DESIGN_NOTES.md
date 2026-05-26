# Pearl_Author Beatsheet Design Notes — Milestone C Step 0

**Status:** DESIGN NOTES (Step 0 deliverable per OPD-140, 2026-05-22; extended Milestone B Step 2 per OPDs 147+148, 2026-05-26)
**Authors:** Pearl_Author (this pass) + operator review
**Date:** 2026-05-22 (initial), amended 2026-05-26
**Method:** Bottom-up reverse-extraction from the 35 hand-authored ep_001 continuity_state YAMLs in `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_001/`. No theory-down design; every classification decision below is anchored to specific panel_ids.

**Version history:**
- **v1.0** (2026-05-22): Initial reverse-extraction; 12 ep_001 archetypes dispatched; single-character semantics.
- **v1.1** (2026-05-24): Schema gains `tension_override` field per OPD-146.
- **v1.2** (2026-05-26): Multi-character generator extension shipped (joint with OPDs 147+148). New archetypes: `secondary_character_face_close` (OPD-147, parametrized via `subject_actor`) and `typographic_caption_card` (OPD-148, META cluster). Promoted from declared-but-unimplemented (ep_002 surfaced): `walking_in_thought_medium`, `miyazaki_ma_pause`, `window_light_threshold`. OPEN-5 and OPEN-7 resolved.

**Companion deliverables:**
- `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_001/_extracted_beatsheet.yaml` — the actual reverse-extracted beatsheet for ep_001
- `docs/specs/MANGA_BEATSHEET_SCHEMA.yaml` — formal schema for what a beatsheet IS

**Authority cross-refs:**
- `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md` v1.0.0 — the schema this generator must emit
- `config/manga/panel_templates/iyashikei.yaml` — archetype dispatch source
- `config/manga/panel_templates/iyashikei.scene_context.yaml` — per-archetype subject_type + cutout policy
- `config/manga/light_rigs/iyashikei.yaml` — light rig library
- `config/source_of_truth/manga_profiles/series/stillness_en_01.scene_inventory.yaml` — scene → light_rig binding
- `config/source_of_truth/manga_profiles/series/stillness_en_01.yaml` — character_design + minor_cast
- `artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml` — the narrative source the beatsheet projects from

---

## §1 Field-by-field classification

**Legend (the contract of this section):**
- **A — Deterministic from external context.** Generator computes; not in beatsheet.
- **B — Explicit operator intent per beat.** Operator authors per beat; required slot.
- **C — Heuristic-inferred from other beatsheet fields.** Generator applies a documented rule; not in beatsheet (but the rule must be explicit and testable).
- **D — Archetype-specific.** Field appearance + value driven by the operator's archetype choice; generator dispatches per archetype.

Every field that appears in any of the 35 ep_001 YAMLs is classified below with evidence cites.

### 1.1 Top-level panel fields

| Field | Category | Evidence | Notes |
|---|---|---|---|
| `schema_version` | **A** | Constant `"1.0.0"` on all 35 panels | Generator emits a constant. |
| `panel_id` | **A** | Sequential `ep001_NNN` (panels 001..035) | Computed from `episode_id + zero-padded index`. |
| `inherits_from` | **A** | `null` on ep001_001; previous panel_id on 002..035 | Computed from sequence position. |
| `beat_type` | **B** | 5 distinct values used: `micro=18, spatial=11, standard=4, long_drop=1, null=1` (panel 1). See e.g. ep001_001 (null), ep001_002 (standard), ep001_005 (micro), ep001_016 (standard for flashback), ep001_029 (long_drop) | Operator-authored per beat. Each iyashikei archetype declares a `beat_type.primary` default in `iyashikei.yaml`, but the operator OVERRIDES for transitions: scene jumps require `spatial+`; flashbacks require `standard+`. The chapter_script's beat_type values match the YAMLs almost 1:1, with operator overrides for ep001_002 (spatial in script → standard in YAML; required by scene-jump invariant). |
| `archetype` | **B** | 12 distinct values; see distribution in §1.6 | Operator-authored per beat. Required. The single highest-leverage field. |

### 1.2 `scene_state` block

| Field | Category | Evidence | Notes |
|---|---|---|---|
| `scene_state.scene_id` | **B** (transitions only) | 3 distinct values across 35 panels: `bedroom_aoki=1, kitchen_table_aoki=32, conference_room_flashback=2`. Transitions happen at ep001_002 (bedroom→kitchen), ep001_016 (kitchen→flashback), ep001_018 (flashback→kitchen) | Sticky-inherited from previous beat; operator declares ONLY at transitions. Generator validates against `scene_state.scene_id == prev.scene_state.scene_id UNLESS beat_type ∈ {standard, long_drop, miyazaki_ma}` per V4 spec §6.3.A. |
| `scene_state.temporal` | **B** (transitions only) + **C** | Values: `dawn` (panels 1-12), `morning` (panels 13-15, 18-35), `midday` (flashback panels 16-17). Transitions at ep001_013 (dawn→morning, "light_rig advances dawn→morning (next-in-cycle)" per continuity_invariant) and ep001_016 (morning→midday, flashback) | Operator declares at transitions; generator validates `temporal ∈ {prev.temporal, next-step-in-cycle(prev.temporal)}` per V4 spec §6.3.A invariant 5. For flashback, operator MUST author `scene.temporal` explicitly because scene_inventory[conference_room_flashback] only declares one rig. |
| `scene_state.light_rig_id` | **C** | Derived from `(scene_id, temporal)`. Evidence: ep001_001..012 use `K01_dawn_window_warm` (kitchen + dawn); ep001_013..015, 018..035 use `K02_morning_window_neutral` (kitchen + morning); ep001_016..017 use `K_flashback_cool_grey_blue` (conference_room_flashback) | **Heuristic rule:** `light_rig_id = first(scene_inventory[scene_id].light_rigs ∩ light_rigs_supporting_temporal(temporal))`. Operator override allowed (see ep001_016 — operator pinned `K_flashback_cool_grey_blue` to be safe; with only one rig in that scene the lookup also returns it, so this is currently belt-and-suspenders). |
| `scene_state.weather_anchor` | **A** | Present ONLY on ep001_001 (`soft_clouded_light`); absent on all other 34 panels | Generator emits on beat 1 (and on scene-id transitions when scene_inventory declares a weather_anchor for the scene). Not operator-authored at beat level. |

### 1.3 `character_state` block (per stage character)

For ep_001, only one stage character: `mira_aoki`. Multi-character episodes are out of scope (V4 spec §15.B.1 multi-char cliff).

| Field | Category | Evidence | Notes |
|---|---|---|---|
| `character_state` presence | **D** (archetype-driven) | Empty `{}` on ep001_001, ep001_016, ep001_035; present on the other 32 | Generator emits empty `{}` when the chosen archetype has `subject_type: null` OR the operator explicitly suppresses the character. Specifically: `sparse_establishing_wide` at episode-open (`bedroom_aoki` with no character on stage), flashback opening (`conference_room_flashback` establishing shot — operator wrote a contradiction here, see OPEN-1), and episode-card panel. |
| `character_state.<char>.character_design_hash` | **A** | Constant `axes_only_PENDING_compute` on every L2 panel in ep_001 (PuLID-pending placeholder per V4 spec §15.A.2 launch limitation) | Generated from `character_design.axes` hash. Operator never authors this. |
| `character_state.<char>.pose_id` | **B** + **D** | 7 distinct values across 32 character-present panels: `hands_wrapping_cup=5, front_portrait_seated_calm=11, hand_only_table=4, front_portrait_seated_tense=4, chest_breath_micro=4, full_figure_standing_at_window=4, hand_only_reaching=1`. Strong correlation with archetype: `tea_beat_close_up → hands_wrapping_cup` (5/5), `chest_breath_micro → chest_breath_micro` (4/4), `character_face_micro_tension → front_portrait_seated_tense` (4/4) | **Mixed:** Each archetype has a default pose_id (defined in `iyashikei.yaml` composition_tokens or to be added explicitly). Operator overrides for specific intent (e.g., ep001_010 = hand_only_reaching for "Mira reaches for laptop"; ep001_022 = full_figure_standing_at_window inside `sparse_establishing_wide`). Treat: archetype default + B-override. |
| `character_state.<char>.expression_dial` | **B** | 6 distinct values used: `0.2, 0.3, 0.4, 0.5, 0.7, 0.9`. Bounded delta `|Δ| ≤ 0.3` on micro beats holds across all transitions except the chapter_script's nominal arc peak (ep001_017 dial=0.9; comment cites "0.8→0.9" but the literal prev panel ep001_016 has no character_state → see OPEN-2) | Operator-authored. Generator enforces V4 spec §6.3.A invariant 6 (delta bound). Allowed shorthand in beatsheet: operator can write `expression_dial: +0.1` and generator computes the absolute value with bound-check. (Not implemented in beatsheet v1; future ergonomic improvement.) |
| `character_state.<char>.emotional` | **B** | 6 distinct values in ep_001: `calm, calm_with_subtle_unease, anxious, anxious_diminishing, present, joyful_quiet` (all from `emotional_state_enum` per V4 spec §6.2) | Operator-authored. Heuristic invariant (V4 spec §6.3.B `emotional_pendulation_iyashikei`) flags discontinuous jumps (e.g., `calm → anxious` skipping `calm_with_subtle_unease`); WARN-not-fail at V4 launch. |
| `character_state.<char>.gaze_direction` | **C** | Strong correlation with `shared_attention_anchor`: `at_named_object_X` when anchor set (ep001_003 anchor=cup, gaze=at_named_object_cup; ep001_010 anchor=laptop, gaze=at_named_object_laptop). When anchor=null, operator picks freely (`off_frame_down`, `middle_distance`, `eyes_closed`, `off_frame_up`) | **Heuristic rule:** `if shared_attention_anchor is set AND archetype's composition supports it, gaze_direction = at_named_object_<anchor>`. Operator override allowed (see ep001_005: anchor=phone but gaze=off_frame_down because the operator wants "averted gaze under quickening pulse"). When anchor=null, gaze is **B** — operator-authored per beat. |
| `character_state.<char>.hand_state` | **D** + **B** | 4 distinct values: `relaxed_open, wrapping_cup, tucked_self_soothing, reaching_for_laptop`. Strong archetype correlation: `tea_beat_close_up → wrapping_cup` (5/5), `chest_breath_micro → tucked_self_soothing` (4/4), `hand_table_micro → variable per intent`. ep001_002 wraps cup; ep001_008 wraps cup (dappled_light_hand override) | Archetype default + operator override. e.g. ep001_004 archetype=hand_table_micro, operator-set hand_state=relaxed_open (default pose); ep001_010 same archetype, hand_state=reaching_for_laptop (B-override). |
| `character_state.<char>.breath_phase` | **D** | Present ONLY on `chest_breath_micro` archetype (4 panels: ep001_005 quickening, ep001_017 quickening, ep001_020 inhale, ep001_021 exhale_settling). Absent on all 31 other panels | Pure archetype dispatch: generator EMITS the field only when archetype=chest_breath_micro. Operator must provide the value per chest_breath_micro beat. |

### 1.4 `prop_state` block

| Field | Category | Evidence | Notes |
|---|---|---|---|
| `prop_state` presence | **D** + **B** | Empty `{}` only on ep001_035 (episode card). Otherwise present and accumulating | Beats inherit prop_state from prev unless `props_clear: true` (ep001_035) or `props_reset: true` (scene transition like flashback ep001_016 reset to {conference_table: present}, then ep001_018 `props_restore_from_scene_exit: true` restores kitchen props). |
| `prop_state.<prop_id>` introductions | **B** | Operator introduces 9 distinct props across ep_001: `phone, succulent_in_clay_pot` (defaults; on stage at b01), `cup` (b02), `laptop` (b10), `finch` (b13), `conference_table` (b16, flashback-only), `smoke_detector` (b22), `kettle` (b27). The intro panel always carries a continuity_invariant comment ("X introduced this panel; not in prev prop_state") | Operator-authored. Generator emits the intro-commentary continuity_invariant. |
| `prop_state.<prop_id>` state transitions | **B** | 4 transitions in ep_001: `phone: face_down → face_up_dark` (b04), `phone: face_up_dark → face_up_notification` (b05), `cup: full → half` (b19, "sip taken"), `kettle: on_burner_boiling → off_burner_residual_steam` (b30). All transitions are adjacent in `prop_evolution_enum` per V4 spec §6.2 | Operator-authored. Generator validates against `prop_evolution_enum` adjacency per V4 spec §6.3.A invariant 3. |

### 1.5 `continuity_invariants` list

| Field | Category | Evidence | Notes |
|---|---|---|---|
| Per-panel `continuity_invariants` list entries | **A** + **B** | Most entries are auto-derived commentary the generator should emit: "phone advances face_down → face_up_dark (adjacent in enum)" (ep001_004), "dial +0.2 from prev (0.5 → 0.7) within micro bound 0.3" (ep001_011), "scene jump bedroom → kitchen on spatial beat (allowed)" (ep001_002). A small minority are operator notes pulled from `intent` field: "POV shift (spatial beat) — scene anchor unchanged" (ep001_004). The recurring V4.1 per-axis edge-resolution boilerplate on 6 face-archetype panels (ep001_006, 011, 014, 015, 023, 026, 028, 031) is generator-emitted | **Generator-emitted** for delta narratives, prop introductions, scene jumps, dial deltas, face-archetype boilerplate. **Operator-passed-through** for intent strings (`beatsheet.beat.intent` → `continuity_invariants[]`) and free-form `notes`. Operator does NOT author the full list per panel. |
| `v41_per_axis_edge_resolved` | **A** | Boolean `true` on 6 face-only-archetype panels (ep001_006, 011, 014, 015, 023, 026, 028, 031). Absent on the other 27 | Generator emits when archetype ∈ {character_quiet_face, character_face_micro_tension}. Boilerplate per V4.1 per-axis subject_must_not_touch_edge contract (V4 spec §15.A.7). |

### 1.6 `relational_field` block

| Field | Category | Evidence | Notes |
|---|---|---|---|
| `relational_field.active_entities` | **A** + **D** | Almost always `[{id: mira_aoki, on_frame: <bool>, role: <subject\|implied_listener>}]`. `on_frame: false + role: implied_listener` on 7 panels (ep001_001, 014, 022, 025, 027, 032, 033); else `on_frame: true + role: subject` | Generator-emitted from `stage_characters` (header) + per-beat archetype + explicit beatsheet `character.<id>.on_frame` override. Heuristic: `on_frame = (archetype.subject_type != null) AND beatsheet doesn't override`. For pet_companion_micro and POV-from-character archetypes (e.g., the smoke-detector ceiling shot at ep001_022), operator declares `on_frame: false`. |
| `relational_field.shared_attention_anchor` | **B** | 7 distinct anchor values: `null` (15 panels), `cup` (8 panels), `phone` (3 panels), `laptop` (1 panel), `finch` (4 panels), `kettle` (2 panels), `smoke_detector` (2 panels) | Operator-authored per beat. Drives gaze_direction heuristic (§1.3 above). |
| `relational_field.implied_partner_position` | **A** | `null` on all 35 panels (solo character episode) | Generator emits `null` for solo episodes. Multi-character episodes (Phase 2) will populate. For V1, generator omits the field if it's null. |
| `relational_field.emotional_tension_vector.direction` | **C** | `rising` on ep001_004, ep001_005 (the activation onset). `steady` on all other 33 panels | **Heuristic rule:** `direction = sign_of_delta(expression_dial - prev.expression_dial)` mapped to `{rising > 0, steady = 0, diminishing < 0}`. Edge case (the only `rising` cases in ep_001 are +0.1; smaller positive deltas at ep001_006 +0.1 and ep001_026 +0.1 are inconsistently labeled `steady` — the operator appears to use `rising` only for the *narrative* activation onset, not every numerical uptick; see OPEN-3). |
| `relational_field.emotional_tension_vector.magnitude_delta_from_prev` | **C** | Numeric value of `expression_dial - prev.expression_dial`. ep001_004 = 0.3 - 0.2 = 0.1; ep001_005 = 0.4 - 0.3 = 0.1; everywhere else 0.0 by ground-truth (even when the actual dial delta is non-zero, e.g. ep001_006: 0.5 - 0.4 = 0.1 but ground truth says 0.0) | Heuristic computation collides with operator's narrative labeling. Generator should emit *both* the numerical delta (truthful) and accept an operator override. See OPEN-3. |

---

## §2 Heuristic rules to encode in the generator

Each rule below should be deterministically implementable; no LLM inference needed at V1.

### H1 — `light_rig_id` from `(scene_id, temporal)`

```python
def derive_light_rig(scene_id, temporal, scene_inventory, light_rig_library):
    candidate_rigs = scene_inventory.scenes[scene_id].light_rigs
    matching = [r for r in candidate_rigs
                if light_rig_library[r.light_rig_id].temporal_compatible(temporal)]
    if not matching:
        raise BeatsheetError(f"No light_rig in scene_inventory[{scene_id}] supports temporal={temporal}")
    return matching[0].light_rig_id   # first match; operator can override per beat
```

Evidence: All 35 ep_001 panels' `light_rig_id` values are reachable this way. Operator overrides only at flashback (ep001_016) where there's only one rig (so override is redundant but defensive).

### H2 — `gaze_direction` from `shared_attention_anchor`

```python
def derive_gaze(beat_character_block, shared_attention_anchor, archetype):
    if "gaze" in beat_character_block:        # explicit operator override
        return beat_character_block["gaze"]
    if shared_attention_anchor:
        return f"at_named_object_{shared_attention_anchor}"
    # No anchor + no override: operator MUST provide explicitly via B-cat
    raise BeatsheetError(f"beat requires explicit gaze when shared_attention_anchor is null")
```

Evidence: ep001_003 (anchor=cup, gaze=at_named_object_cup — derived); ep001_005 (anchor=phone but gaze=off_frame_down — operator override); ep001_006 (anchor=null, gaze=off_frame_down — explicit B).

### H3 — `emotional_tension_vector.direction` from `expression_dial` delta

**Simplified V1 rule (literal):**
```
direction = "rising"      if delta > 0
            "diminishing" if delta < 0
            "steady"      if delta == 0
```

This contradicts the ground truth (which uses `steady` for most positive deltas). See OPEN-3. Recommendation: ship the literal rule + emit an operator-overridable field `beatsheet.beat.emotional_tension_override`. The ground truth's "narrative steady" labeling is operator semantics, not heuristic semantics; the generator should not pretend to know which.

### H4 — `magnitude_delta_from_prev` from `expression_dial` arithmetic

Literal: `magnitude_delta_from_prev = expression_dial - prev.expression_dial`.

Same caveat as H3 — ground truth carries 0.0 even when arithmetic delta is 0.1. Recommendation: ship the truthful value; allow operator override.

### H5 — `on_frame` from archetype

```python
def derive_on_frame(beat_character_block, archetype, scene_context):
    if "on_frame" in beat_character_block:    # explicit operator override
        return beat_character_block["on_frame"]
    subject_type = scene_context.archetypes[archetype].subject_type
    return subject_type is not None           # null subject_type → off-frame implied
```

Evidence: ep001_001 (sparse_establishing_wide, no character on stage → off_frame); ep001_014 (pet_companion_micro, subject_type=character_pet_only → human implied off-frame); ep001_022 (sparse_establishing_wide POV-ceiling-shot → operator-overridden off_frame).

### H6 — `role` from `on_frame`

```python
role = "subject" if on_frame else "implied_listener"
```

100% consistent across all 35 ground-truth panels.

### H7 — `weather_anchor` emission

Emit only on beat 1 (episode open) AND on `scene_id` transitions where the new scene's `scene_inventory` entry declares a `weather_anchor`. ep_001 evidence: only beat 1.

### H8 — `v41_per_axis_edge_resolved` boilerplate

Emit `v41_per_axis_edge_resolved: true` + the standard V4.1 commentary string when `archetype ∈ {character_quiet_face, character_face_micro_tension}`.

### H9 — `continuity_invariants` auto-commentary

Generator emits formatted strings for:
- Scene transitions: `"scene jump <prev_scene> → <new_scene> on <beat_type> beat (allowed|FORBIDDEN)"`
- Prop introductions: `"<prop_id> introduced this panel; not in prev prop_state"`
- Prop state transitions: `"<prop_id> transitions <prev_state> → <new_state> (adjacent in enum|NON-ADJACENT)"`
- Dial deltas on micro: `"dial +X.X from prev within micro bound 0.3"` or `"dial Δ FORBIDDEN (>0.3 on micro)"`
- Light rig transitions: `"light_rig advances <prev_rig> → <new_rig> (next-in-cycle|operator-pinned)"`

Operator `beat.intent` and `beat.notes` strings are appended after the generator's commentary.

### H10 — `inherits_from` chain

```
inherits_from = null                                    if beat_index == 0
                f"{episode_id}_{beat_index:03d}"        otherwise
```

Trivial; no operator input.

---

## §3 Per-archetype dispatch table

For each iyashikei archetype dispatched by the generator. The 12 ep_001 archetypes seed the table; ep_002 surfaces 5 more (2 new candidates per OPDs 147/148, 3 promotions from declared-but-unimplemented).

| Archetype | Count (ep_001) | Count (ep_002) | Default `pose_id` | Default `hand_state` | Special fields | `subject_type` (drives on_frame) |
|---|---|---|---|---|---|---|
| `sparse_establishing_wide` | 7 | 4 | `front_portrait_seated_calm` OR `full_figure_standing_at_window` (operator picks) | `relaxed_open` | none | `null` → on_frame default false; operator overrides up |
| `tea_beat_close_up` | 5 | 2 | `hands_wrapping_cup` | `wrapping_cup` | none | `character_hands_only` → on_frame: true |
| `character_quiet_face` | 5 | 4 | `front_portrait_seated_calm` | `relaxed_open` | EMITS `v41_per_axis_edge_resolved` + V4.1 boilerplate | `character_face_only` → on_frame: true |
| `chest_breath_micro` | 4 | 3 | `chest_breath_micro` | `tucked_self_soothing` | **REQUIRES** `breath_phase` ∈ {quickening, inhale, exhale_settling} | `character_chest_partial` → on_frame: true |
| `character_face_micro_tension` | 4 | 3 | `front_portrait_seated_tense` | `tucked_self_soothing` OR `relaxed_open` (operator picks) | EMITS `v41_per_axis_edge_resolved` + V4.1 boilerplate | `character_face_only` → on_frame: true |
| `hand_table_micro` | 4 | 3 | `hand_only_table` | varies — `relaxed_open` / `tucked_self_soothing` / `reaching_for_X` per intent | none | `character_hand_only` → on_frame: true |
| `dappled_light_hand` | 1 | 0 | `hand_only_table` | `wrapping_cup` (often holds prop) | none | `character_hand_only` → on_frame: true |
| `pet_companion_micro` | 1 | 0 | (off-frame implied: `front_portrait_seated_calm`) | `relaxed_open` | none; human is OFF-frame | `character_pet_only` → human on_frame: false |
| `seasonal_anchor_object` | 1 | 2 | (off-frame implied) | n/a | none; object-only panel, no L2 cutout | `null` → on_frame: false |
| `kettle_steam_macro` | 1 | 1 | (off-frame implied) | n/a | none; object-only panel, no L2 cutout | `null` → on_frame: false |
| `long_drop_decompression` | 1 | 1 | `full_figure_standing_at_window` | `relaxed_open` | beat_type forced to `long_drop` | `null` → on_frame: true if operator wants tiny figure (ep001_029 has on_frame: true) |
| `pendulation_pair_visual_rhyme` | 1 | 0 | (inherits from rhyme partner) | (inherits) | takes `rhyme_partner_beat` field; copies composition | `null` → off-frame |
| **`secondary_character_face_close`** *(OPD-147, 2026-05-26)* | 0 | 2 | `face_close_seated_calm` | `relaxed_open` | **REQUIRES `subject_actor` (character_id in stage_characters)**; EMITS `v41_per_axis_edge_resolved` + V4.1 boilerplate; EMITS `subject_actor` in panel output for downstream PuLID binding | `character_face_only` → on_frame: true for subject_actor, false for all other stage_characters (POV-from-protagonist) |
| **`typographic_caption_card`** *(OPD-148, 2026-05-26, META cluster)* | 0 | 1 | (n/a — META) | (n/a) | **REQUIRES `caption_style` ∈ {mid_episode_strip, end_episode_card}** + **`caption_text: string`**; EMITS `render_directive: typographic_only`, drops `scene_state.light_rig_id`; suppresses character_state for ALL stage_characters | `null` → on_frame: false for all stage_characters |
| `walking_in_thought_medium` *(ep_002 promotion from declared-but-unimplemented)* | 0 | 2 | `full_figure_walking_three_quarter` | `relaxed_open` | none | `character_full_figure_walking` → on_frame: true |
| `miyazaki_ma_pause` *(ep_002 promotion)* | 0 | 1 | `full_figure_seated_tiny` | `relaxed_open` | beat_type primary forced to `miyazaki_ma` | `null` (`character_ELS_in_L0` — figure baked into L0) → on_frame: operator-picks (b14 ep_002 has on_frame: true for tiny figure) |
| `window_light_threshold` *(ep_002 promotion)* | 0 | 2 | `full_figure_threshold_door` | `relaxed_open` | none | `character_silhouette_back` → on_frame: true |

### §3.1 The first parametrized archetype (OPD-147)

`secondary_character_face_close` is the **first parametrized archetype**: it requires a `subject_actor: <character_id>` field per beat that binds the on-frame focal character. This is also the first archetype that diverges from the V1 "single stage_character" assumption. The generator's multi-character extension (this PR, joint with OPD-147) supports parametrized subject binding by:

1. Beat schema validates `subject_actor ∈ stage_characters`.
2. Generator's per-character state loop SUPPRESSES the protagonist (and any other non-subject_actor stage_character) when archetype is in `ARCHETYPES_REQUIRING_SUBJECT_ACTOR` and no operator state was authored for them.
3. `derive_on_frame_for_character()` (new H5 extension) returns on_frame=true only for cid == subject_actor.
4. Panel output emits `subject_actor: <character_id>` so downstream prompt compiler / PuLID binds the right reference sheet.
5. Protagonist's dial cache is PRESERVED across the off-frame beat — the inheritance chain continues so the next protagonist-on-frame beat reads against the right prev_dial.

Future parametrized archetypes (e.g. multi-character `shared_meal_table_medium` when promoted) will join `ARCHETYPES_REQUIRING_SUBJECT_ACTOR`.

### §3.2 META archetypes (OPD-148)

`typographic_caption_card` introduces a **META cluster** of renderable-but-no-L0/L1/L2/L3 archetypes. META archetypes:

1. Drop `scene_state.light_rig_id` from output (no L0 lighting).
2. Emit empty `character_state: {}` for ALL stage_characters (no L2 cutouts).
3. Emit `render_directive: <directive>` so downstream pipeline routes around the layer stack.
4. Take their own parametrized fields (here: `caption_style` + `caption_text`).
5. Force every active_entities entry to `on_frame: false`.

Future META archetypes (e.g. title cards, transition wipes) will join `META_ARCHETYPES_SUPPRESSING_ALL_CHARACTERS`.

**Coverage status post-ep_002:** iyashikei.yaml now declares 21 archetypes (was 19; +2 from OPDs 147+148). The generator dispatches 17 of these (14 supported from ep_001+ep_002 + 3 promoted from declared-but-unimplemented). The remaining 4 (`morning_routine_sequence`, `food_preparation_overhead`, `shared_meal_table_medium`, `phone_notification_macro`) stay declared-but-unimplemented until ep_003+ beatsheets surface their need.

---

## §4 Beat → panel mapping logic

### §4.1 V1 mapping rule: 1 beat → 1 panel

For ep_001, the operator authored 35 distinct panel YAMLs and the generator produces 35 panel YAMLs. The beatsheet has 35 beats. Mapping is 1:1, in order.

**Why 1:1 and not 1:N?** I considered allowing one beat to fan out into multiple panels with auto-progressed `expression_dial` (e.g., "5-panel breath bracket with dial 0.5 → 0.4 → 0.3 → 0.3 → 0.2"). But:
- Every adjacent pair of ground-truth panels carries an operator decision somewhere (pose_id change, hand_state change, gaze change, archetype change). I found ZERO consecutive panel pairs in ep_001 where ONLY expression_dial changes.
- The chapter_script (the upstream narrative source) also enumerates 35 distinct panel descriptions. Operator's authoring unit is already the panel.
- Auto-fan-out would force the generator to invent a panel-progression heuristic for fields the operator demonstrably wants to control. That violates Step 0's bottom-up principle.

**V2 future work:** If empirical data from ep_002..010 shows operator-repeated patterns (e.g., always wanting `chest_breath_micro` to come in threes), the generator can expose a `repeat: 3` / `progression: dial_minus_0.1` shorthand that expands at parse-time. Don't speculate until the data demands it.

### §4.2 Generator pipeline (high level)

```
beatsheet.yaml + (series_profile, scene_inventory, style_state, panel_template, character_design)
   ↓
[1] Parse + validate beatsheet schema
[2] Compute header fields (series_id, episode_id, stage_characters)
[3] For each beat in beats[]:
        [3a] Initialize panel from inheritance: prev_panel.copy() OR defaults
        [3b] Apply beat's explicit overrides (scene, character.<id>.*, props, shared_attention_anchor)
        [3c] Run archetype dispatch (§3 table) to fill defaults
        [3d] Run heuristic rules H1-H10 (§2)
        [3e] Emit panel YAML
   ↓
[4] Write 35 panel YAMLs to artifacts/manga/<series>/continuity_state/<episode>/ep001_NNN.yaml
[5] Run validate_continuity_invariants.py to confirm class-A gates green
```

### §4.3 Beat boundaries that take care

- **Scene transitions**: beat must use `beat_type ∈ {standard, long_drop, miyazaki_ma}` or generator FAILS (V4 spec §6.3.A invariant 1). ep_001 evidence: b02 (bedroom→kitchen) uses `beat_type: standard` (operator-promoted from chapter_script's `spatial` to satisfy invariant); b16 (kitchen→flashback) uses `standard`; b18 (flashback→kitchen) uses `standard`.
- **Flashback transition**: requires explicit `scene.light_rig_id` (operator-pinned) because flashback rigs (`K_flashback_cool_grey_blue`) are not in any non-flashback scene's `light_rigs` list — H1 derivation handles this naturally because the flashback scene only has one rig.
- **POV shots (character off-frame)**: operator must explicitly set `character.<id>.on_frame: false` because H5 otherwise emits true for any non-null `subject_type`.
- **Pendulation rhyme beats**: `pendulation_pair_visual_rhyme` archetype takes a `rhyme_partner_beat: bNN` field. Generator copies the partner's composition + adjusts prop_state for the later-state form. Not implemented in V1 if the panel YAML can be authored without composition copying (ep_001's b33 simply uses standard fields).

---

## §5 What this surfaces about Step 1+ generator complexity

**Empirical assessment: SMALL-TO-MEDIUM LIFT.** No LLM needed for V1.

**Why small:**
- All 10 heuristics (H1-H10) are pure-Python lookup + dict-merge + simple delta arithmetic. No model inference required.
- Per-archetype dispatch (§3) is a static lookup table — ~12 rows for iyashikei, ~25 entries to fill at most.
- Inheritance is `dict.copy() + dict.update()` per beat. ~50 lines of Python.
- All five validation gates the generator must respect (V4 spec §6.3.A invariants 1-7) are already implemented in `scripts/manga/validate_continuity_invariants.py`. Generator emits, validator confirms. The validator IS the round-trip test target.

**Why "medium" not "small":**
- The `props_reset` / `props_restore_from_scene_exit` semantics (used twice in ep_001 for the flashback excursion) need a small stack/snapshot mechanism. ~30 lines.
- The H3/H4 disagreement with ground truth (see OPEN-3) means I need to confirm with operator: ship truthful-numerical with operator-override, or copy the ground-truth's narrative-only labeling. Either path is implementable.
- The beat 16 contradiction (OPEN-1) needs an operator decision before the round-trip can be 100% lossless.
- Documenting all the archetype defaults requires authoring `iyashikei.yaml` extensions OR a separate `iyashikei.continuity_dispatch.yaml`. ~1 day of structured authoring.

**Total Step 1+ estimate (Pearl_Author + operator collaboration):**
- Generator code (Python, modular): **3-4 days** (parser, dispatch, heuristics, inheritance, emitter, tests)
- Archetype dispatch table authoring: **1-2 days**
- Round-trip test harness: **1 day** (regenerate the 35 YAMLs, diff against ground truth with tolerance rules)
- Beatsheet ergonomics polish: **1-2 days** (shorthand for dial deltas, prop manipulations)

**Tier policy compliance:** This generator is pure deterministic + heuristic Python. No paid LLM API calls. Falls cleanly under the "scheduled pipelines" tier (Pearl Star Ollama for any future LLM enhancements only). Per CLAUDE.md tier policy.

**Compare to "with LLM" alternative:** If we let an LLM generate panel YAMLs from a free-form prose beat description, the round-trip test becomes "non-deterministic prose interpretation," and we lose the ability to validate against `validate_continuity_invariants.py` byte-exactly. The deterministic generator IS the right architecture.

---

## §6 Open uncertainties

**OPEN-1 — ep001_016 character_state vs relational_field contradiction.** Ground truth has `character_state: {}` (empty) but `relational_field.active_entities[0].on_frame: true` and `role: subject`. These contradict. The downstream prompt builder reads from `character_state` to decide L2 cutout; from `relational_field` to decide composition role. Operator decision needed: which is authoritative for ep001_016? Beatsheet currently encodes `on_frame: true` in the relational_field block + null character_state (the ground-truth shape), but the generator will need to know how to reconcile. Recommendation: ASK operator whether ep001_016's flashback opening was intended as character-present-but-off-frame (then character_state should have a partial entry) or character-absent-establishing (then on_frame should be false). My beatsheet preserves the contradiction verbatim because changing it would break the round-trip test against ground truth.

**OPEN-2 — ep001_017 dial citation ("0.8→0.9") vs literal previous dial (0.5).** ep001_017's `continuity_invariants` says `"dial +0.1 from prev (0.8 -> 0.9) within micro bound"`. But its literal predecessor ep001_016 has `character_state: {}` (no dial), and the predecessor-with-dial ep001_015 has 0.2. The comment cites "0.8" which appears nowhere in the inheritance chain. Two interpretations: (a) operator was authoring nonlinearly + the comment is stale; (b) there's an implicit "internal" dial that's not the same as the panel's `expression_dial` field. Recommendation: ASK operator; my beatsheet sets ep001_017's expression_dial=0.9 and accepts that the H4 delta computation will not match the comment. Generator should ALWAYS use literal arithmetic; operator's narrative-comment is information loss otherwise.

**OPEN-3 — `emotional_tension_vector.direction` operator vs heuristic semantics.** Ground truth uses `direction: rising` only for ep001_004 and ep001_005 (narrative activation onset). Other positive dial deltas (ep001_006 +0.1, ep001_026 +0.1) get `direction: steady`. The operator is using `direction` as a narrative signal, not a numerical sign. H3 above ships the literal numerical version; the operator's semantics are lost. Recommendation: ship literal as default, let operator override via `beatsheet.beat.tension_override` field. (Not yet in beatsheet schema; add in v0.2.)

**OPEN-4 — Pose_id default per archetype.** The `iyashikei.yaml` panel template declares composition_tokens but no `default_pose_id`. The 7 distinct pose_ids used in ep_001 correlate strongly with archetype but not deterministically (e.g., `sparse_establishing_wide` uses 3 different pose_ids depending on what's in frame). Recommendation: extend `iyashikei.yaml` archetypes with an optional `default_pose_id` field; operator override always allowed. Document this as a Milestone-D pre-req for cross-genre rollout.

**OPEN-5 — RESOLVED (OPD-148, 2026-05-26).** Archetype for ep001_035 (episode card) / ep_002 b24 (mid-episode caption strip): resolved by the new `typographic_caption_card` META archetype shipped jointly with OPD-148. The archetype takes `caption_style` ∈ {`mid_episode_strip`, `end_episode_card`} so the same archetype serves both the ep_002 b24 mid-strip and the ep_001 b35 outro pattern. ep_001 b35 retroactive cleanup (re-author from `sparse_establishing_wide` to `typographic_caption_card` with `caption_style: end_episode_card`) is a sibling follow-up workstream (the ep_001 ground truth YAMLs stay immutable for round-trip integrity; retroactive cleanup happens in a fresh ep_001 v2 if and when operator pulls that trigger).

**OPEN-6 — `pendulation_pair_visual_rhyme` composition copying.** Beatsheet declares `rhyme_partner_beat: b25` for b33. The generator needs to decide whether to copy partner's composition_tokens / pose_id / framing into the new panel, or whether the operator should re-author. Ground truth at ep001_033 has explicit `pose_id: front_portrait_seated_calm` (different from b25 which has no pose_id because off-frame); operator did NOT auto-copy. Recommendation: V1 generator treats `pendulation_pair_visual_rhyme` as documentation only (no composition copying); operator re-authors per beat. V2 may add copy-with-override.

**OPEN-7 — RESOLVED (OPD-147, 2026-05-26, joint with this PR).** Multi-character beats are now supported in the generator. The first concrete user is the new `secondary_character_face_close` archetype (Dr. Morimoto across the meeting table in ep_002 b17 + b22). The extension preserves V1 single-character behavior exactly (ep_001 round-trip remains byte-clean — proven by `test_ep_001_round_trip_still_passes_after_multi_char_extension`). Key surface: `stage_characters` is a list; each beat may declare `subject_actor: <character_id>` to bind the on-frame focal character; protagonist (stage_characters[0]) drives the panel's `emotional_tension_vector` regardless of on-frame status; protagonist dial cache PRESERVES across off-frame beats so inheritance chain continues. ep_003 (mother) + ep_004+ (Kenji) will exercise additional shapes without further generator changes expected.

**OPEN-8 — Style state injection.** The style_state.yaml prompt_clauses (line_weight, wash_softness, tonal_density, shading_aggression) are injected into rendering prompts, NOT into continuity_state YAMLs. The beatsheet correctly omits them. Confirm with Pearl_Architect that this boundary holds.

---

## §7 Validation plan (the round-trip test)

The Milestone C exit criteria (per `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md` §Milestone-C) requires: *"Round-trip test: regenerate ep_001 from the Step 0 beatsheet; output matches existing 35 YAMLs within declared tolerance."*

### §7.1 Tolerance classes

| Class | Definition | Examples | Tolerance |
|---|---|---|---|
| **EXACT** | Must match byte-for-byte | `panel_id`, `inherits_from`, `schema_version`, `scene_state.scene_id`, `scene_state.light_rig_id`, `archetype`, `prop_state.*` values, `character_state.<id>.character_design_hash` | 0 diff |
| **NUMERIC** | Match within tolerance | `expression_dial`, `magnitude_delta_from_prev` | ±0.0 (quantized to 0.1 per V4 spec §6.8 Strategy 2) |
| **ENUM** | Exact enum match | `emotional`, `gaze_direction`, `hand_state`, `breath_phase`, `beat_type`, `temporal` | 0 diff |
| **SET-EQUAL** | Same set, order-independent | `continuity_invariants` list, `prop_state` keys | 0 diff on set; order may differ |
| **COMMENTARY** | Auto-generated commentary may differ in wording | `continuity_invariants` boilerplate strings, V4.1 face-archetype string | Allow regex-equivalent variation (e.g., different number formatting in dial-delta string) |
| **OPERATOR-NARRATIVE** | Operator-authored intent strings | `intent` field passed through to `continuity_invariants` | EXACT match if beatsheet carries the field; absent otherwise |

### §7.2 Known-acceptable divergences

These are conscious design decisions where the generator's output will differ from ground truth and that's correct:

1. **`emotional_tension_vector.direction` on ep001_006, ep001_026** — generator emits `rising` (literal H3); ground truth has `steady`. Tagged as expected divergence pending OPEN-3 resolution.
2. **`magnitude_delta_from_prev` numeric values** — generator emits arithmetic delta (e.g., +0.1); ground truth has 0.0 in some cases. Tagged as expected divergence pending OPEN-3.
3. **`continuity_invariants` ordering** — generator emits auto-commentary first, operator notes second; ground truth has mixed ordering. Tagged as expected divergence (set-equal class).
4. **`weather_anchor`** — generator emits only on beat 1; ground truth ALSO only emits on ep001_001. Matches.
5. **`relational_field.implied_partner_position: null`** — generator OMITS this field for solo episodes; ground truth EMITS it as `null` (see ep001_001 line 24). Need decision: emit always (preserves ground-truth shape) or omit when null (cleaner). Recommendation: emit always for round-trip parity at V1.

### §7.3 Round-trip test command (proposed)

```bash
# After generator implementation (Milestone C Step 1+):

python3 scripts/manga/continuity_state_generator.py \
    --beatsheet artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_001/_extracted_beatsheet.yaml \
    --series-profile config/source_of_truth/manga_profiles/series/stillness_en_01.yaml \
    --output-dir /tmp/round_trip_ep_001/

python3 scripts/manga/diff_continuity_state.py \
    --ground-truth artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_001/ \
    --regenerated /tmp/round_trip_ep_001/ \
    --tolerance-spec docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md \
    --known-divergences §7.2

# PASS criteria:
#   - 35 panel YAMLs generated
#   - 0 EXACT-class divergences
#   - 0 ENUM-class divergences
#   - 0 NUMERIC-class divergences (after quantization)
#   - All COMMENTARY divergences regex-match the expected pattern
#   - All OPERATOR-NARRATIVE intent strings preserved verbatim
#   - Known-acceptable divergences from §7.2 are the ONLY divergences
#   - Generator output also passes scripts/manga/validate_continuity_invariants.py
```

### §7.4 Test as gate, not as suggestion

The round-trip test is the **acceptance gate for Milestone C exit** per the rollout plan. It's also the prerequisite for Milestone B (V5.1 ep_002-010 dispatch) per OPD-135 (C-before-B sequencing). If the test fails, the generator is not ready; iterate on the heuristics / dispatch / inheritance until it passes.

After passing on ep_001, the next checkpoint is generating ep_002..010 from operator-authored beatsheets (no ground truth to round-trip against; instead, operator §11 acceptance review on the rendered output). That validates the *forward* direction.

---

## Appendix A — Field count summary

Pure tally for the §1 classifications, counting every distinct field schema position:

| Category | Distinct fields | % of total |
|---|---|---|
| A (deterministic from context) | 9 fields | 35% |
| B (explicit operator intent) | 9 fields | 35% |
| C (heuristic from other beatsheet fields) | 5 fields | 19% |
| D (archetype-specific) | 3 fields | 11% |
| **Total** | **26 fields** | 100% |

(Fields counted: `schema_version`, `panel_id`, `inherits_from`, `beat_type`, `archetype`, `scene_state.scene_id`, `scene_state.temporal`, `scene_state.light_rig_id`, `scene_state.weather_anchor`, `character_state` (presence), `character_state.<id>.character_design_hash`, `character_state.<id>.pose_id`, `character_state.<id>.expression_dial`, `character_state.<id>.emotional`, `character_state.<id>.gaze_direction`, `character_state.<id>.hand_state`, `character_state.<id>.breath_phase`, `prop_state` (presence), `prop_state.<id>` introductions, `prop_state.<id>` transitions, `continuity_invariants`, `v41_per_axis_edge_resolved`, `relational_field.active_entities`, `relational_field.shared_attention_anchor`, `relational_field.implied_partner_position`, `relational_field.emotional_tension_vector.direction`, `relational_field.emotional_tension_vector.magnitude_delta_from_prev`.)

## Appendix B — Reduction metrics

| Metric | Ground-truth 35 YAMLs | Extracted beatsheet | Ratio |
|---|---|---|---|
| Total file size (load-bearing lines, excluding inline comments/blanks) | 1205 lines (35 files) | 356 lines (1 file) | **3.4x reduction** |
| Operator-authored field-values (excludes inherited, computed, boilerplate) | ~580 explicit values across 35 panels | ~150 explicit values across 35 beats | **3.9x reduction** |
| Operator-required-decision points per panel | ~16 fields per panel × 32 character-present panels = ~510 | ~4-5 fields per beat avg × 35 beats = ~150 | **3.4x reduction** |
| Schema fields requiring per-panel operator authoring | 16 of 26 (the B-cat + B-overrides on C/D) | 9 of 26 (B-cat only; C/D-cat are dispatch + heuristic) | **1.8x reduction** |

**The 3-4x reduction is conservative.** Once `props_reset` / `props_restore_from_scene_exit` / `props_clear` shorthand land, and once dial-delta shorthand (`expression_dial: +0.1`) is implemented, the reduction grows further. The principle: **the operator authors decisions, not echoes.**

---

— end of design notes —
