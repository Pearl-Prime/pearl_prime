# Manga Continuity State Spec (formerly §6 of MANGA_LAYER_RENDER_CONTRACT_SPEC.md)

**Status:** AUTHORITY (v1.0.0 — extracted 2026-05-20 from V4 spec §6 per §15.C.6 doc-split)
**Author:** Pearl_Architect + Pearl_Int (original authorship preserved)
**Schema version:** 1.0.0 (extraction snapshot of V4 spec §6 as of v0.6.1, 2026-05-20)
**Doc-split rationale:** Per V4 spec §15.C.6 (trip-wire at 1,900 lines) + operator directive 2026-05-20 (target <1,800), §6 (~506 lines) was extracted to this standalone authority. Continuity state is authoritative under both V4 and (forthcoming) V5 render architectures; a contract shared by two render architectures belongs in its own doc.

**Authority surface:** This doc is the canonical home for the manga continuity-state schema, state vocabularies, deterministic + heuristic invariants, prompt-modification semantics, state-driven cache strategy, cardinality controls, light rigs as first-class scene state, telemetry, and style-state continuity.

**Consumed by:** V4 render pipeline (`scripts/manga/render_v4_episode.py`), V5 render pipeline (`scripts/manga/render_v5_episode.py` once V5 lands per PR #1258), validator infrastructure (`scripts/manga/validate_continuity_invariants.py`), prompt compiler (`scripts/manga/contract_to_prompt_compiler.py`).

**Cross-spec references:** This doc references the parent `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` for §5 safe-zone contracts, §8 inventory schemas, §12 validators, §14 failure modes. Those V4-spec sections cross-reference this doc for continuity primitives.

---

## 1. Continuity state schema

Continuity state is **per-panel** but **inherits from the previous panel** by default (with explicit deltas).

```yaml
# Path: artifacts/manga/<series>/continuity_state/<episode_id>/<panel_id>.yaml
schema_version: "1.0.0"
panel_id: "ep001_004"
inherits_from: "ep001_003"           # previous panel (or null for episode opening)

character_state:                     # one block per character on stage
  mira_aoki:
    emotional: "anxious_diminishing"  # enum — see §2
    posture: "seated_upright_to_slumped"  # transition or steady-state
    gaze_direction: "down_at_cup"     # one of: at_camera / at_named_object_X / off_frame_L / off_frame_R / up / down
    hand_state: "wrapping_cup"        # registers with §4 prop_state
    breath_phase: "exhale_settling"   # for somatic archetypes (chest_breath_micro)
    expression_dial: 0.3              # 0.0 = fully neutral, 1.0 = peak expression cap

scene_state:
  scene_id: "kitchen_table_dawn"
  temporal: "dawn_to_morning"        # enum — affects L0 light direction
  weather_anchor: "soft_clouded_light"

prop_state:                          # per-prop running state
  cup_ceramic: "full_warm_steam_visible"
  kettle: "off_burner_residual_steam"

continuity_invariants:               # things that MUST match prior panel
  - "mira gaze direction continuous from ep001_003 (was looking down at cup; still looking down)"
  - "cup is the same cup (no rim chip flip)"
  - "window light source still camera-left"

relational_field:                    # NEW v0.4 — single-char archetypes are already implicitly relational
  active_entities:                   # who is "on stage" — even off-frame
    - id: "mira_aoki"
      on_frame: true
    - id: "off_frame_presence_partner"  # operator/reader sometimes implied as conversational partner
      on_frame: false
      role: implied_listener
  shared_attention_anchor: "cup_ceramic"  # what's the focus of attention — driven by gaze enum
  implied_partner_position: null     # null for solo; for paired scenes, "camera_left" / "across_table" / etc.
  emotional_tension_vector:          # the running emotional gradient through the scene
    direction: "diminishing"          # rising | steady | diminishing | inflection
    magnitude_delta_from_prev: -0.1   # bounded change from previous panel's expression_dial
```

**Note:** for V4 launch, `relational_field` exists in the schema but only `active_entities`, `shared_attention_anchor`, and `emotional_tension_vector.direction` are validated. Full multi-character relational fields (eye-line geometry, paired emotional state, contact continuity) are Phase 2 — see parent V4 spec §15.B.1. The schema reservation here prevents Phase-2 work from requiring a continuity_state migration.

## 2. The state vocabularies (enums)

Limited vocabularies so the system stays finite and the prompt builder can map them deterministically.

```yaml
emotional_state_enum:
  - calm
  - calm_with_subtle_unease
  - anxious
  - anxious_diminishing                 # mid-regulation (iyashikei core arc)
  - exhausted
  - present                              # post-regulation, the iyashikei "yes" moment
  - dissociating                         # disconnect (rare; trauma arcs)
  - joyful_quiet
  - joyful_active
  # (~12 entries for V4 launch; extensible per genre)

posture_enum:
  - seated_upright
  - seated_slumped
  - standing_grounded
  - standing_braced
  - walking_thoughtful
  - reaching_for_object
  - holding_object_close_to_chest
  - lying_down_relaxed
  - lying_down_tense

gaze_enum:
  - at_camera
  - at_named_object_X        # X = specific prop_id
  - at_named_character_Y     # Y = specific character_id
  - off_frame_left
  - off_frame_right
  - off_frame_up
  - off_frame_down
  - eyes_closed
  - middle_distance         # "thousand-yard stare" — iyashikei + horror staple

hand_state_enum:
  - relaxed_open
  - clenched
  - gripping_X              # X = prop_id
  - wrapping_X
  - reaching_for_X
  - gesturing_open
  - tucked_self_soothing
  - covering_face

prop_evolution_enum:        # extends per prop type
  cup:
    - empty
    - half
    - full
    - tipped_spilled
  kettle:
    - off_burner
    - on_burner_just_lit
    - on_burner_boiling
    - off_burner_residual_steam
  phone:
    - face_down
    - face_up_dark
    - face_up_notification
    - in_hand_being_read
```

## 3. Continuity invariants (the gates that prevent jarring transitions)

Invariants are split into **deterministic** (V4 launch enforced, brutally simple, no model inference) and **heuristic / narrative** (Phase B.2+ — model-assisted, advisory rather than enforced).

### 3.A Deterministic invariants (V4 launch — enforced by `validate_continuity_invariants.py` V1)

These are pure structural checks — string equality, set membership, bounded numeric delta. Zero model inference, zero ambiguity.

```yaml
continuity_invariants_deterministic:
  - id: "scene_continuity"
    rule: "scene_state.scene_id == prev.scene_state.scene_id UNLESS beat_type ∈ {standard, long_drop, miyazaki_ma}"
  - id: "character_identity_continuity"
    rule: "character_state[id].character_design_hash == prev.character_state[id].character_design_hash for all id ∈ stage"
    # character_design_hash definition (v0.5.1 amendment):
    #   Required component:
    #     axes_hash = sha256(canonical_json(character_design.axes))
    #       — covers the 12 locked semantic axes per character_design_axes.yaml
    #   Optional component (concatenated when present):
    #     ref_hash = sha256(file_content(character_design.reference_image_path))
    #       — captures the PuLID/LoRA identity-anchor image
    #   character_design_hash = axes_hash if no reference_image_path
    #                         = axes_hash + "|" + ref_hash if reference_image_path populated
    #
    # V4 LAUNCH LIMITATION (called out per V4 spec §15.A.2):
    #   When PuLID is blocked (EVA-CLIP hang) AND no per-character LoRA exists,
    #   character_design_hash = axes_hash only. The structural invariant PASSES
    #   when two panels declare the same axes — but this does NOT guarantee the
    #   diffusion model rendered the same face. Perceptual identity drift is a
    #   class-C concern (Phase B.2), explicitly deferred. V4 spec §15.A.2's "identity
    #   lock" acceptance gate is NOT satisfied by hash-equality alone; it
    #   requires either PuLID OR LoRA active to pass.
  - id: "prop_persistence"
    rule: "prop_state[id] in {prev.prop_state[id], any value in prop_evolution_enum[type] reachable in 1 step} for all id ∈ stage_props"
  - id: "gaze_target_validity"
    rule: "if gaze == at_named_object_X, X must exist in scene_state OR prop_state"
  - id: "temporal_continuity"
    rule: "temporal ∈ {prev.temporal, next-step-in-cycle(prev.temporal)} UNLESS beat_type == standard"
  - id: "expression_dial_bounded_delta"
    rule: "|expression_dial - prev.expression_dial| ≤ 0.3 if beat_type == micro; ≤ 0.5 if spatial; unbounded if standard+"
  - id: "light_rig_within_scene"
    rule: "light_rig_id ∈ scene_inventory.scenes[scene_id].light_rigs"
```

These rules are evaluable by a YAML reader + string ops + numeric comparisons. They form V1 of the continuity validator.

### 3.B Heuristic / narrative invariants (Phase B.2 — model-assisted, advisory)

These are the rules the operator critique flagged as "heuristic scorers pretending to be validators." They are STILL useful, but they cannot share a severity class with deterministic invariants.

```yaml
continuity_invariants_heuristic:
  - id: "emotional_pendulation_iyashikei"
    rule: "emotional state transitions follow pendulation grammar (no calm→peak_anxious in one beat)"
    enforcement: WARN_NOT_FAIL              # advisory at V4 launch
    detector: "LLM zero-shot via Pearl_Star qwen-instruct against pendulation_grammar.yaml"
  - id: "gaze_continuity_semantic"
    rule: "if prev gaze at_named_object_X and curr gaze ≠ at_named_object_X, curr gaze should be off_frame in the direction of X (semantic intent: 'character looked away' rather than 'character teleported attention')"
    enforcement: WARN_NOT_FAIL
    detector: "rule-based check against gaze enum + direction vocabulary; advisory because intent is ambiguous"
  - id: "emotional_tension_arc_coherence"
    rule: "emotional_tension_vector.direction should be coherent across chapter (not flipping rising/diminishing every 2 panels without narrative cause)"
    enforcement: SCORE_ONLY                  # diagnostic, never blocking
    detector: "LLM evaluation against chapter pacing model"
```

V4 launch: deterministic invariants block render-cache writes. Heuristic invariants surface in `qa_review_queue.yaml` (V4 spec §14.E) for operator triage but do NOT block. Phase B.2 work elevates heuristics to enforced after the deterministic core has stabilized.

## 4. How continuity state modifies layer prompts

```python
# Pseudo-code for prompt builder
def build_l2_prompt(character_id, archetype, continuity_state, series):
    base = series.character_design[character_id].render_prompt_base
    pose_suffix = archetype.subject_type.pose_clause(continuity_state[character_id].posture)
    gaze_suffix = render_gaze(continuity_state[character_id].gaze_direction)
    hand_suffix = render_hand(continuity_state[character_id].hand_state)
    emotion_suffix = render_emotion_via_axes(
        continuity_state[character_id].emotional,
        continuity_state[character_id].expression_dial,
        character_design.expression_frequency_cap  # respects identity contract
    )
    return f"{base}. {pose_suffix}. {gaze_suffix}. {hand_suffix}. {emotion_suffix}. {safe_zone_clause(archetype)}"
```

Result: same Mira identity, different emotional inflection per panel — **without re-prompting the character_design**. Identity preserved; state varied.

## 5. Prop state evolution drives separate L3 renders

`cup_ceramic` at three states = three cached L3 layers:
- `cup_ceramic__empty.png`
- `cup_ceramic__half.png`
- `cup_ceramic__full.png`

The chapter_script declares prop_state per panel; the builder selects the matching L3 cutout. No re-rendering at panel time.

## 6. Temporal state drives separate L0 renders

`kitchen_table` at four temporals = four cached L0 layers:
- `kitchen_table__dawn.png`
- `kitchen_table__morning.png`
- `kitchen_table__evening.png`
- `kitchen_table__night.png`

Single scene, four lighting states. Composited identically; light direction continuity preserved within each temporal block.

## 7. Continuity state record (what gets persisted)

For each panel: `artifacts/manga/<series>/continuity_state/<episode>/<panel>.yaml` — full state record. Inherited diffs only (the previous panel's values carry forward unless overridden). Validates against §3 invariants pre-render.

For each rendered layer: `artifacts/manga/<series>/render_cache/<layer_id>.png` — the binary asset. Cache key = `(layer_type, subject_id, pose_id, continuity_state_hash)`. Cache invalidation: V4 spec §14.

## 8. State cardinality management (combinatorial explosion containment)

State has a multiplication problem. For a single L2 character layer:

```
unique_renders = |pose| × |emotional| × |hand_state| × |gaze| × |expression_dial steps|
              × |temporal| × |light_rig_id|
```

For Mira with V4 launch vocabularies: 9 poses × 9 emotional × 8 hand_state × 9 gaze × 11 dial-steps × 4 temporal × 4 light-rigs = **102,816 theoretically distinct cache entries per character**. The actual demand from a chapter_script is ~0.1% of that, but **left unchecked the cache stops being a cache and starts being a per-render output dir** — which defeats the architecture.

The spec contains the explosion with four orthogonal strategies:

**Strategy 1 — Empirical caching (lazy, not eager).** Never pre-compute the cartesian product. Render the (pose, emotional, hand, gaze, dial, temporal, rig) tuple ONLY when a chapter_script panel demands it. Cache it. Evict LRU when total cache exceeds budget (default: 200 entries per character).

**Strategy 2 — State quantization.** Continuous fields are quantized to coarse buckets:
- `expression_dial`: 11 steps (0.0, 0.1, ... 1.0). Render budget says ~5 used per series.
- Light rig: indexed (not freeform parameters) — see §9.
- Temporal: 4 buckets (dawn/day/evening/night). No interpolation.

Quantization is a contract: if two panels declare `expression_dial: 0.34` and `expression_dial: 0.37`, both map to bucket `0.3` → same cache key → same render. Reader will not see the difference; cache hit rate skyrockets.

**Strategy 3 — Hierarchical state inheritance (continuity exploits sequence-locality).** Most state changes are small-delta. A panel inherits 90% of the previous panel's state by default; only the explicit deltas are unique to it. The state-hash for caching is computed AFTER inheritance, so:
- Panel 3: `(pose=seated_upright, emotional=anxious_diminishing, hand=wrapping_cup, gaze=down_at_cup, dial=0.3, temporal=dawn, rig=K01)` → cache key A
- Panel 4: inherits panel 3, overrides `(dial=0.4)` → key A' (one-step-removed) — likely cache MISS first time, then HIT on similar 0.3→0.4 transitions in other panels.

Sequence-locality means real chapter_scripts visit ~30-60 unique state tuples per 30-panel episode, not 100,000.

**Strategy 4 — Factorized render deltas (Phase 2; not V4 launch).** If the cache still explodes for action genres or ensemble casts, the next move is factorization: render a base L2 (pose-only, neutral emotional, plain hand, forward gaze) ONCE per pose; then synthesize the (emotional, hand, gaze, dial) inflection as an *additive image delta* via img2img-with-low-strength or LoRA-residual. Reduces cardinality by ~50× at the cost of an extra render pipeline stage. NOT implemented for V4 — flagged here as the escape hatch.

**Cardinality budgets per series (gates):**
- L0 cache: ≤ 32 entries (8 scenes × 4 temporals)
- L1 cache: ≤ 20 entries
- L2 cache: ≤ 200 entries per character (LRU evict beyond)
- L3 cache: ≤ 60 entries (15 objects × 4 state variants)
- L4 cache: ≤ 20 entries (atmospheric effects, often reused across series)

**What this protects against:** the architecture remaining safe for iyashikei single-protagonist scale (✅ launch). For action genres / ensemble casts (Phase 2), Strategy 4 (factorized deltas) is the escape; it's a known-future-work item, not a launch blocker.

## 9. Light rig as first-class scene state (replaces v0.2's lighting-direction-only model)

v0.2's lighting coherence checking was a direction vector with 45° tolerance. That's necessary but insufficient. Lighting mismatch shows up across many axes:

| axis | mismatch symptom |
|---|---|
| direction | shadows fall opposite ways across L0 vs L2 |
| softness | L0 has hard shadows (sunlight), L2 has soft shadows (cloudy) — character looks pasted in |
| color_temperature | L0 is warm 2800K (dawn), L2 is cool 6500K (noon) — character looks "wrong time of day" |
| rim_intensity | L0 has dramatic rim-light from window; L2 has flat lighting — character pops as a sticker |
| ambient_bounce | L0 ambient is warm cream (warm walls reflecting); L2 ambient is neutral gray — character feels cold in a warm scene |
| atmospheric_diffusion | L0 has hazy morning-fog atmospheric; L2 is sharp/crisp — character feels foregrounded inappropriately |
| exposure_range | L0 is high-key (most pixels in 200–255 range); L2 is mid-key (100–180 range) — character feels darker than scene |

The fix: **light rigs are first-class scene state**, declared in `scene_inventory.yaml` and inherited by every layer rendered into that scene.

```yaml
# scene_inventory.yaml
scenes:
  - scene_id: "kitchen_table_dawn"
    light_rigs:
      - light_rig_id: "K01_dawn_window_warm"
        primary_direction: "camera_left_slightly_above"   # 8-direction enum
        primary_softness: "soft"                            # hard | medium | soft | very_soft
        primary_color_temp_K: 3200
        rim_intensity: 0.3                                  # 0–1
        ambient_bounce_color: "warm_cream_FFE6C2"
        atmospheric_diffusion: 0.4                          # 0–1; 0=clear, 1=heavy fog/dust
        exposure_key: "high_key_dawn"                       # low | mid | high
        prompt_clause: "warm dawn light from camera-left, soft window-diffused, gentle warm bounce on shadow side, slight atmospheric haze, high-key exposure with 200-250 brightness range"
      - light_rig_id: "K02_morning_window_neutral"
        # ... different rig for same scene at later time
```

**Enforcement at render time:**
1. L0 render is associated with one `light_rig_id` (the canonical lighting for that L0).
2. L2 render PROMPT inherits the light_rig.prompt_clause: every character render literally includes "warm dawn light from camera-left, soft window-diffused, gentle warm bounce ..."
3. L3 render PROMPT inherits the same clause for objects.
4. QA gate V4 spec §14.B.1 validates light rig coherence post-composite by detecting the 7 axes above (direction, softness, temperature, rim, bounce, diffusion, exposure) and comparing against the declared light_rig values.

**Why this is image-first not world-engine (per V4 spec §1.3):** the light rig is a *prompt-injected metadata bundle and a post-render-validation target*, not an actual lighting calculation. We don't compute shadows. We constrain the renderer to produce consistent shadows. That's a contract, not a simulation.

**Pre-built light rig library:** `config/manga/light_rigs/iyashikei.yaml` defines ~8 named rigs (K01–K08) covering: dawn window warm, dawn window cool, morning bright, midday flat, afternoon golden, evening warm, dusk dim, night lamp-warm, night moonlight-cool. Phase-2 genres add their own (mecha cockpit, fantasy_torchlight, horror_fluorescent, etc.).

**Scene_inventory references rigs by ID** (not by inline definition). One rig serves many scenes. One scene can have several time-of-day rigs.

## 10. Visual-compilation vs narrative-evolution boundary (architectural modularization risk)

v0.3's continuity_state has accumulated responsibilities. As the operator flagged:
> "continuity_state is creeping toward semantic dramaturgy state management. That is no longer 'render continuity.' It is partially a writing engine, partially a cinematography engine, partially a render QA engine. Those concerns may need modularization."

The spec acknowledges the risk and pre-declares the modularization boundary so V4 doesn't entangle systems that should be separable.

**Two systems coexist in `continuity_state.yaml` today:**

| system | concern | examples |
|---|---|---|
| **Visual compilation state** | what the renderer needs to fulfill the layer contract | pose, hand_state, gaze enum, prop_state, temporal, light_rig_id, character_design_hash |
| **Narrative evolution state** | what the next chapter beat needs to track | emotional, emotional_tension_vector, relational_field, expression_dial as dramatic intensity |

For V4 launch they share one file. For Phase 2 they may need separation:
- `continuity_state.visual.yaml` — feeds the renderer + render-cache
- `continuity_state.narrative.yaml` — feeds the writer + chapter coherence checks
- A shared join key: `panel_id`

**V4 design choice:** keep them together with explicit section labels. Don't entangle the validators across the boundary. The deterministic continuity validator (§3.A) reads ONLY visual-compilation fields. The heuristic validator (§3.B) reads ONLY narrative fields. Operators editing one section don't break the other.

**The lesson:** as the architecture grows, resist the merge. Render orchestration and dramaturgy are different problem domains. Sharing a YAML file is fine; sharing a validator code path is not.

## 11. Cache telemetry (economic instrumentation)

Cardinality controls (§8) are necessary but invisible without telemetry. v0.4 adds an observability contract so the cache can be reasoned about operationally.

**Path:** `artifacts/manga/<series>/render_telemetry/<episode_id>.yaml`

Emitted by `render_layer_inventory.py` at the end of each episode build:

```yaml
schema_version: "1.0.0"
series_id: "stillness_en_01"
episode_id: "ep_001"
build_started_utc: "2026-05-19T14:00:00Z"
build_completed_utc: "2026-05-19T15:30:00Z"

layer_cache:
  L0:
    unique_renders: 4              # 1 scene × 4 temporals
    panels_served: 30
    hit_rate: 0.93                  # 28 cache hits / 30 panels
    invalidation_fanout: 0          # times this episode's L0 layer was invalidated downstream
  L2_mira_aoki:
    unique_renders: 12              # 8 poses × ~1.5 state inflection avg
    panels_served: 26               # panels with character (vs 4 without)
    hit_rate: 0.69                  # 18 hits / 26 — first run; will rise on subsequent episodes
    avg_rerenders_per_success: 1.2  # validator rejected 20% of first attempts; rerendered with hardened prompts
    invalidation_fanout: 1          # character_design.yaml edited mid-build invalidated 12 cached L2 renders
  L3:
    unique_renders: 6
    panels_served: 22
    hit_rate: 0.82
  L4:
    unique_renders: 3
    panels_served: 14
    hit_rate: 1.00                  # overlay reused every time

continuity_reuse_ratio: 0.71        # 0.71 of panels inherited >80% of their continuity_state from prev panel — high inheritance = good locality
deterministic_validator:
  pass: 27
  fail: 3                            # 3 panels failed deterministic gates; rerendered
  fail_classes:
    backdrop_corner_check: 2
    subject_does_not_touch_edge: 1
heuristic_validator:
  pass: 28
  warn: 2                            # advisory only at V4 launch
  warn_classes:
    emotional_pendulation_iyashikei: 1
    gaze_continuity_semantic: 1

render_cost:
  total_gpu_seconds: 2580
  unique_render_seconds: 1620        # what we actually paid (vs 30-panel single-pass would be ~3600s)
  cache_savings_pct: 55              # 1620 vs 3600 — half the cost via reuse
  per_panel_avg_seconds: 86          # composite-time per delivered panel
```

**What this enables:**
- After episode 1, see hit_rate trends. If L2 hit_rate < 0.5 across multiple series, cardinality strategy needs tuning.
- After series 1, see continuity_reuse_ratio. If < 0.5, the chapter_script is doing too many gratuitous state changes; flag for writer.
- After 10 episodes, see invalidation_fanout. High numbers mean character_design/scene_inventory churn is expensive; freeze them earlier.
- After 1 catalog (~10 series), see cache_savings_pct vs render_cost. Trade-off this against quality.

**Telemetry is data, not policy.** v0.4 does not auto-tune based on telemetry. Future work (Phase 3+) may close the loop. For V4: observability is enough.

## 12. Style-state continuity (NEW in v0.5 — the missing 4th continuity dimension)

v0.4 covered three continuity dimensions:
1. **Identity** — same character across panels (PuLID / LoRA, embedding distance)
2. **Structural** — same layer composition / framing / spatial layout (archetype contracts)
3. **Semantic / narrative** — same gaze / pose / emotional arc (continuity_state §1)

v0.5 adds the fourth: **stylistic / aesthetic continuity** — the renderer-level look-and-feel that operates above palette and below identity.

| axis | what it controls | drift symptom |
|---|---|---|
| **line_weight** | thickness + variation of ink linework | one panel feels sketchy, the next feels heavily inked |
| **wash_softness** | watercolor blending edge softness | one panel has hard cel-shading, the next bleeds painterly |
| **tonal_density** | screentone / hatching density | panels with similar light feel differently weighted |
| **shading_aggression** | shadow saturation, halftone cutoffs | character feels "flatter" or "deeper" between scenes |
| **panel_border_treatment** | gutter widths, border ink weight | continuity broken at composite seam |

These can drift even when identity, structural, and semantic continuity all hold. **Across 300 panels of one episode they may look "off but not wrong"; across 10 episodes of one series, or across 288 series in a catalog, the drift accumulates into a perceptible quality ceiling.**

**Schema — `style_state.yaml` per series:**
```yaml
# config/source_of_truth/manga_profiles/series/<series>.style_state.yaml
schema_version: "1.0.0"
series_id: "stillness_en_01"
canonical_style:
  line_weight:
    primary: "soft pen-and-ink, variable 0.5-1.2px"
    consistency_target: "warm uneven hand-inked, not vector-perfect"
  wash_softness:
    primary: "watercolor wash, soft edge bleed 2-4px"
    avoid: ["hard cel-shading", "vector flats", "airbrush gradient"]
  tonal_density:
    primary: "low — 15-25% non-white coverage outside subject"
    avoid: ["heavy hatching", "dense screentone"]
  shading_aggression:
    primary: "gentle — value range 180-240 for shadows on light skin"
    avoid: ["dramatic chiaroscuro", "high-contrast black/white"]
  panel_border_treatment:
    primary: "no rendered borders — vertical scroll webtoon"
prompt_clauses:                    # the strings that get injected into prompts
  line_weight_clause: "soft pen-and-ink linework, variable line weight, warm uneven hand-inked aesthetic"
  wash_softness_clause: "soft watercolor wash with gentle 2-4px edge bleed"
  tonal_density_clause: "low tonal density, breathable negative space, no heavy hatching"
  shading_aggression_clause: "gentle shading, low contrast, value range 180-240 on light skin"
```

**Where it's enforced:**
- Render prompts (V4 spec §5.9): `{style_state.line_weight_clause}` and friends are template slots injected into every L0/L2/L3 prompt
- QA gates (V4 spec §12): class-C perceptual evaluator `style_fingerprint_drift` — extract style features (edge density via Canny + tonal histogram via grayscale variance + stroke-width estimation) per render, cluster within the series, flag outliers > 2σ
- Telemetry (§11): per-episode `style_drift_pct` reports outlier count

**V4 launch posture:** `style_state.yaml` authored per series (Phase C). Prompt clauses injected (class-A — deterministic). Drift detector is class-C — advisory only at V4; promotion to class-A FAIL via the trip-wire below.

**Class-C → class-A promotion trip-wire (NEW v0.5.1 — no more indefinite "pending calibration"):**

The drift detector auto-promotes from class-C SCORE/WARN to class-A FAIL when ALL of the following are observed in production telemetry:

```yaml
style_drift_detector_promotion_trip_wire:
  observation_window: "last 5 episodes shipped" 
  correlation_threshold:
    metric: "rate of operator-rejected panels that ALSO triggered drift detector"
    minimum_correlation_pct: 80           # if ≥80% of operator-rejected panels were already flagged by drift detector, the detector is calibrated enough to trust
  false_positive_ceiling:
    metric: "rate of drift-flagged panels that operator did NOT reject"
    maximum_false_positive_pct: 5         # FP rate must be ≤5% before promotion
  panel_volume_minimum: 200               # ≥200 panels reviewed in window (statistical floor)
  on_trip_wire_met:
    action: "auto-emit promotion proposal to qa_review_queue.yaml + alert operator"
    requires: "operator approval to enact class-A FAIL severity" 
    documentation: "promotion records appended to MANGA_LAYER_RENDER_CONTRACT_SPEC.md changelog"
  on_trip_wire_not_met:
    action: "remain class-C; log telemetry; re-evaluate after next 5 episodes"
```

**Why this matters:** "pending calibration" without a trigger is indefinite by default. v0.5.1 makes the promotion an explicit data-driven decision with a numerical condition. The detector promotes itself when the data supports it; without that data the detector stays advisory.

**Why class-C at V4 (still):** the drift detector itself is a perceptual model with non-trivial false-positive rate. The prompt-injection of canonical style clauses IS the V4 enforcement; the detector is the V4.5+ confirmation that fires automatically when its accuracy clears the bar.

**Cross-spec interaction:** `style_state.yaml` references the same `genre_modifier` palette in `drawing_tradition_per_genre.yaml`. Style state is the series-level expression of the genre-level drawing tradition. Genre = "iyashikei watercolor"; style_state = "this series's specific iyashikei watercolor."

---

## Appendix: Cross-spec mapping (former §6.x → new §N)

| Former location (V4 spec §6.x) | New location (this spec §N) |
|---|---|
| §6.1 Schema | §1 |
| §6.2 Vocabularies | §2 |
| §6.3 Continuity invariants (intro) | §3 |
| §6.3.A Deterministic invariants | §3.A |
| §6.3.B Heuristic / narrative invariants | §3.B |
| §6.4 Prompt modification | §4 |
| §6.5 Prop state → L3 renders | §5 |
| §6.6 Temporal state → L0 renders | §6 |
| §6.7 State persistence | §7 |
| §6.8 Cardinality management | §8 |
| §6.9 Light rigs | §9 |
| §6.10 Visual-vs-narrative boundary | §10 |
| §6.11 Cache telemetry | §11 |
| §6.12 Style-state continuity | §12 |

---

## Version history

- **v1.0.0 (2026-05-20):** Initial extraction from `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §6 per the §15.C.6 doc-split commitment + operator directive 2026-05-20 (target <1,800 lines). Content preserved verbatim; section numbering remapped (former §6.x → §N). Internal cross-references to other §6.x subsections were rewritten to reference the new local §N. References to other V4-spec sections (§1.3, §5, §8, §12, §14, §15) were prefixed with "V4 spec" for clarity.
