# Manga Layer Render Contract Spec (v0.6.1 — scene-prior is load-bearing)

**Status:** AUTHORITY (v0.6.1 — operator-directed 2026-05-19 after B-test #2)
**Author:** Pearl_Architect + Pearl_Int + Pearl_Research
**Schema version:** 0.6.1 (sub-amendment: L2 prompt flips from suppression to specification)
**Changes since v0.6 (B-test #2 follow-up):**
- §8.1 EXTENDED — L2 prompt contract flips from "suppress scene" to "specify archetype-appropriate scene context"
- §7.2 EXTENDED — archetype `layer_render_contract.L2_char` gains required `scene_context_clause` field
- slot_registry.yaml: `archetype.scene_context_clause` is now a REQUIRED L2 slot (replaces the generic `scene_context.minimal_scene_clause`)
- L2 prompt template: scene context becomes archetype-specific not generic
- **Empirical evidence (B-test #2):** Qwen ignored "NO ATTACHED OBJECTS" positive + "no objects in foreground, no table, no chair, no cup, no kettle, no phone" negative — rendered a kitchen scene with stove/counter/chair anyway. Negative prompts barely dent the scene-prior. Eye geometry showed mild drift toward anime-cute (less grounded face) when scene context was reduced. Conclusion: **Qwen requires archetype-appropriate scene grounding to render the character correctly. Scene is part of the identity signal.**
**Changes since v0.5.1 (B-test pivot):**
- §4.3 REFRAMED — L2 is "character in minimal scene context, extracted via rembg" (was: "character on isolated pure-white backdrop")
- §8.1 REWRITTEN — backdrop moves from RENDER contract to CUTOUT contract; per-archetype `cutout_policy` block
- §7.2 EXTENDED — archetype `layer_render_contract` schema gains `cutout_policy` field (model, keep_attached_props, alpha_matting)
- §12.3 RESTRUCTURED — L2 class-A gates updated: `backdrop_corner_check` SKIP for L2; new `character_extraction_coverage` + `background_bleed_check`; `rembg_clean_alpha` threshold relaxed to 3% for L2
- §15.A.2 UPDATED — backdrop-purity acceptance criterion replaced with extraction-coverage + bleed acceptance
- **Empirical evidence:** B-test 2026-05-19 — Qwen-Image rendered Mira with full kitchen scene context despite explicit "PURE WHITE BACKGROUND #FFFFFF" directive. Top corners ✓ (delta 2.5-2.9), bottom corners FAIL (delta 35-89). Character render quality EXCELLENT (identity on-target, on-beat). u2net_human_seg cutout clean visually but kept attached props (cup, table edge). Operator decision: Qwen's scene-prior is load-bearing, not a bug. Embrace scene context; extract subject downstream.
**Changes since v0.5 (tightening pass):**
- §14.F.7 NEW — hold-queue drain mechanism (review SLA + auto-escalation; `hold` is no longer an open valve)
- §5.9 EXTENDED — additive-safe slot semantics + `slot_registry.yaml` as machine-readable canonical source (replaces prose-only `SLOTS.md`)
- §6.12 EXTENDED — class-C → class-A drift-detector promotion trip-wire (declarative trigger condition)
- §15.A.6 NEW — composite-level operator-review acceptance gate (layer-pass is not composite-pass)
- §15.C.6 EXTENDED — doc-split trip-wire (commit to split BEFORE 1900 lines)
**Changes since v0.4:**
- §5.9 NEW — contract-to-prompt compiler (closes the deterministic-contract → natural-language-prompt seam; Phase B.1 step 1.5)
- §6.12 NEW — style-state continuity (the missing 4th dimension alongside identity / structural / semantic — line weight, wash softness, tonal density, shading aggression)
- §13.2 EXTENDED — Phase B.1 step 1.5 inserted: `contract_to_prompt_compiler.py` (between safe-zone compiler and layer validator)
- §14.F NEW — failure budget & recovery semantics (declared retry limits, fallback hierarchy, per-episode/series thresholds, halt conditions — without this, validators detect failures but the orchestrator has no exit condition at catalog scale)
- §15.A REWRITTEN — launch blockers converted from narrative to **acceptance criteria** (declarative pass/fail tests; each blocker is now operationally verifiable)
**Changes since v0.3:**
- §6.1 EXTENDED — `relational_field` schema seeded (single-char archetypes already implicitly relational: gaze, off-frame presence, shared attention anchor)
- §6.3 SPLIT — invariants partitioned into deterministic vs heuristic; V1 enforces deterministic-only
- §6.10 NEW — visual-compilation vs narrative-evolution boundary (continuity layer modularization risk acknowledged; concerns kept separable)
- §6.11 NEW — cache telemetry schema (hit_rate, invalidation_fanout, continuity_reuse_ratio, render_cost_per_episode)
- §12 RESTRUCTURED — validator taxonomy split: A. contract validators (deterministic) / B. heuristic scorers (probabilistic) / C. perceptual evaluators (model-based fuzzy) / D. narrative invariants (semantic/LLM-assisted). FAIL / WARN / SCORE severity classes.
- §13 SHARPENED — Phase B is brutally deterministic V1; heuristic + perceptual + narrative scorers come in Phase B.2 (after deterministic core proven)
**Changes since v0.2:** §1.3 image-first boundary; §6.8 state cardinality; §6.9 light rigs; §13 validator-first migration; §14.B.1 light-rig coherence; §15.B.1 multi-char cliff; §15.D.5 constraint-solver evolution.
**Changes since v0.1:** §1 architectural reframe; §4.6 namespace reservation; §5 hierarchical inheritance; §6 state continuity; §14 failure modes; §15 frontier map.

---

## 1. Purpose & Scope

### 1.1 Architectural reframe (the most important thing in this spec)

We are not "generating manga panels." We are **compiling manga panels from typed render assets under constrained contracts**. The model is no longer the source of truth — the **layer contract is**. The diffusion model becomes a renderer that fulfills a typed contract; if it can't, the contract fails and we re-render with adjusted inputs, exactly like a compiler fails a type check.

This reframe matters because the failures the operator caught in V3 / V3.1 / layer-demo-v1 / layer-demo-v2 are not prompting failures. They are **contract failures**:
- "Cross-engine drift" = no engine-consistency contract
- "Same person / different person" = no identity-continuity contract
- "Shoulders cut off" = no subject-safe-zone contract
- "Pale sage background didn't cut out" = no backdrop-verification contract

The spec below defines the contracts. Solving them at the contract layer (not the prompt layer) is what unlocks catalog scale.

### 1.2 Scope

This spec defines **how to render a manga panel as a stack of isolated layers** — background, character(s), object(s), atmospheric overlay — and **how each layer must be framed so that automated background-removal (rembg) produces a clean alpha cutout that composites into the final panel without artifacts**.

It is the layer-pipeline counterpart to:
- `docs/specs/MANGA_V3_3_MODEL_ROUTING_SPEC.md` (which engine renders which thing)
- `docs/specs/MANGA_V3_ROUTING_BY_GENRE.md` (catalog-wide routing matrix)
- `config/manga/panel_templates/iyashikei.yaml` (per-archetype composition intent)
- `config/manga/character_design_axes.yaml` (per-character identity contract)

**In scope:**
- The 8 top-priority genres in `config/manga/drawing_tradition_per_genre.yaml` (healing/iyashikei, dark_fantasy, psychological_horror, mecha, romance, slice_of_life, fantasy_adventure, comedy)
- All 19 iyashikei archetypes (fully specified). Stubs + safe defaults for the other 7 genres pending Phase-2 archetype expansion.
- The 288 series profiles in `config/source_of_truth/manga_profiles/`
- The 800 high-confidence catalog configs target (`artifacts/research/full_content_audit.md:65`)
- All 13 target locales (en_US, ja_JP, zh_TW, zh_CN, ko_KR, es_ES, pt_BR, fr_FR, de_DE, it_IT, vi_VN, id_ID, th_TH)

**Out of scope (this draft):**
- LoRA training for character-lock (separate spec — `CHARACTER_INDIVIDUATION_PIPELINE_SPEC.md`)
- B&W iyashikei register (Mushishi-style) — future `iyashikei_bw.yaml`
- Animation / video pipelines (reserved namespace; see §4.6 + §15.D)
- Multi-character layered compositing (explicitly deferred; see §15.B)

### 1.3 Where this architecture deliberately stops (image-first boundary)

This is an **image-first** architecture. We deliberately do NOT build:

- **Scene graphs** with geometry — no 3D meshes, no transforms, no parented nodes. L0 is a 2D image; L2 is a 2D image. Their spatial relationship is the archetype's `subject_placement_bbox` — nothing more.
- **Camera systems** with intrinsic/extrinsic parameters — no focal length, no projection matrices. "Framing" is a prompt clause, not a camera state.
- **Rigging or articulated pose** — no skeletons, no IK. Pose is a prompt clause + a CLIP-detected check, not a kinematic structure.
- **Physics simulation** — no collision, no gravity, no fluid dynamics. Steam in L4 is a rendered image, not a particle system.
- **Semantic scene graphs** — no "Mira is HOLDING cup AT 0.5m FROM table" relational structure. Continuity_state (§6) carries SOME relational info (`gaze.at_named_object_X`, `prop_state.cup = full`) but it's enums, not a knowledge graph.

**Why declare the boundary:** the architecture now has *momentum* toward simulation (typed asset inventories + continuity state + composite math + light rigs + per-archetype layer maps). It would be easy to slide into reinventing a 2.5D renderer or a scene graph DB. We're choosing to remain image-first because:
- The diffusion model already gives us composition for free at the layer level — we don't need geometry to ask "render Mira sitting."
- Image-domain operations (alpha cutout, alpha composite, screen-blend, PIL ops) are deterministic and fast.
- The escape hatch exists: if Phase 4+ needs true 3D consistency (camera moves, parallax that depends on actual depth), we'll bridge to a real 2.5D engine (Blender/Three.js/native) at that point. For V4, we're not paying that cost.

**Concretely, the line is here:**
| we do (image-first) | we don't (would be world-engine) |
|---|---|
| 2D bbox placement | 3D coordinates / transforms |
| temporal_state enum (`dawn/day/evening/night`) | continuous time-of-day with light-position interpolation |
| light_rig as scene-state metadata (§6.9) | actual lighting calculation / shadow casting |
| prop_state enum (`empty/half/full`) | physical fluid simulation |
| gaze_at_named_object_X enum | eye-line vector geometry between two characters |
| pose enum + CLIP-detected verification | skeletal pose vector or IK |

The continuity_state vocabulary IS the constraint surface. The renderer is allowed to be opinionated within those constraints; it is not allowed to invent geometry.

---

## 2. The Problem (Why a Layer-Render Contract Is Required)

### 2.1 What V3 (single-pass FLUX-schnell) failed at

V3 rendered each panel as a single image with one prompt: "Mira in the kitchen drinking tea, soft light, watercolor wash, iyashikei style." Results:
- **Cross-engine drift** — Qwen for faces + FLUX for objects produced visibly different character styles in adjacent panels (operator review 2026-05-18: "image 3 great, image 4 different person, image 5 same as 3").
- **Character inconsistency** — even single-engine, prompt-based identity drifted across 30+ panels.
- **No reuse** — every panel re-rendered the same kitchen 30 times.

### 2.2 What V3.1 (single-engine Qwen) partially fixes

V3.1 renders all panels with Qwen-Image only — solves style drift. But still:
- Character identity still drifts across panels (no anchor reference).
- Backgrounds get re-rendered every panel (wasteful, inconsistent).
- Composition stays in the model's "head" — operator can't surgically edit just the character without rerolling the whole panel.

### 2.3 What V4 (layer-render contract) fixes

Render the panel as **N isolated layers**, each on a high-contrast backdrop, cut out via `rembg`, then `PIL.alpha_composite` them onto a single background:
- Background rendered once per **scene**, reused across all panels in that scene (huge efficiency win).
- Character rendered with **identity-locking inputs** (PuLID reference, or LoRA, or both) on a pure backdrop → clean cutout → consistent across all panels.
- Objects rendered once per **object instance**, reused.
- Edits stay surgical: re-render just the character layer, recomposite. Background + objects untouched.
- Final composite is deterministic from layer files + archetype bbox + continuity state + this spec.

### 2.4 What the layer demo (2026-05-19) proved

The 6-up demo at `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/experiments/layer_demo_qwen/layer_grid_v2.png` showed:
- ✅ Object cutout (kettle, `u2net` model) worked — 12.4% non-transparent, clean silhouette.
- ❌ Character cutout (`isnet-anime` AND `u2net_human_seg` AND `birefnet-portrait`) all left the pale-sage backdrop attached — 75%+ non-transparent. Root cause: Qwen rendered the "plain pale sage background" as a soft watercolor wash, not a flat color → rembg models treat it as scene context, not removable background.
- ❌ Mira's shoulders touched the canvas edges in the raw render → composite shows shoulders clipped at the paste boundary.

Both failures trace to **missing render contracts** — there is no rule today that says "character layer must render on pure-white backdrop with ≥17% margin on every side." This spec defines those rules.

---

## 3. Architecture: The Layer Pipeline

```
       ┌─────────────────────────────────────────────────────┐
       │  L0  Foundation backdrop (the scene/environment)     │   bottom
       │      Rendered once per <series, scene_id>            │
       ├─────────────────────────────────────────────────────┤
       │  L1  Mid-distance anchors (large objects in scene)   │
       │      Rendered once per <series, object_id, scene_id> │
       ├─────────────────────────────────────────────────────┤
       │  L2  Hero subjects: character(s)                     │
       │      Rendered once per <series, character_id, pose,  │
       │                          continuity_state>            │
       ├─────────────────────────────────────────────────────┤
       │  L3  Hero subjects: close objects (in hand, on table)│
       │      Rendered once per <series, object_id,            │
       │                          continuity_state>            │
       ├─────────────────────────────────────────────────────┤
       │  L4  Atmospheric overlay (steam, light shafts)       │   top
       │      Rendered once per <effect_id>                   │
       └─────────────────────────────────────────────────────┘
```

A panel is the result of:
```python
canvas = L0_bg.copy()
for layer in [L1, L2, L3, L4]:
    if layer.is_present_in(archetype):
        canvas.alpha_composite(layer.cutout, dest=archetype.placement_for(layer))
return canvas
```

Not every panel uses all 5 layers. The archetype declares which layers it needs (see §7). The **continuity_state** (see §6) further partitions L2/L3 so the same character pose at different emotional states is two distinct cached renders.

---

## 4. Layer Taxonomy

Each layer type has a distinct render contract. Below are the type definitions.

### 4.1 L0 — Foundation backdrop

**Purpose:** The environment. What the scene looks like with no humans or hero objects in it.

**Examples:**
- A kitchen at dawn with empty wooden table, no kettle, no Mira
- A bedroom with empty unmade bed, no phone, no character
- A café exterior with no customers
- A forest clearing with no figure

**Render contract:**
- Full panel resolution (1080×1920 for vertical webtoon; 2480×3508 for print B5)
- **Negative prompt mandatory:** `"people, person, character, human, figure, hero-object-X, hero-object-Y, ..."`
- Composition leaves **negative space** where the archetype's `subject_placement_bbox` indicates the character or object will be composited
- Backdrop is NOT pure white — it IS the scene
- No alpha channel; this is the canvas
- Single source of truth: rendered ONCE per `<series_id, scene_id, temporal_state>` and reused (temporal_state = dawn/day/evening/night per continuity, see §6)

### 4.2 L1 — Mid-distance anchors

**Purpose:** Large environmental objects that anchor the scene but aren't the panel's hero (e.g., the window, the houseplant, the table).

**When needed:** Usually baked into L0. L1 is only used when an object needs to be:
- Reused across multiple scenes (e.g., the same kettle appears in kitchen AND on a tray), OR
- Surgically editable (e.g., empty cup → full cup as story progresses, driven by `prop_state` in §6)

**Render contract:**
- Same resolution as panel
- Backdrop: **pure white (255,255,255)** for shiny/dark objects, **pure black (0,0,0)** for light/translucent objects (steam, glass)
- Subject occupies center 60% × 70% of frame
- Min 15% margin all sides (no part of object touches edge)
- No drop shadow; no environmental reflection; alpha cutout via `rembg(u2net)`

### 4.3 L2 — Character (hero subject) — REFRAMED v0.6

**Purpose:** The named character (1+) doing the panel's beat.

**Render contract (v0.6 reframe):** L2 is **NOT** "character on isolated pure-white backdrop." L2 is **"character rendered in minimal scene context, extracted via rembg with per-archetype cutout policy."** Empirical evidence from B-test 2026-05-19 showed that Qwen-Image's scene-prior is load-bearing — character coherence (identity, pose, lighting consistency) depends on having scene context to render against. Fighting the model to produce isolated subjects degrades the character render. Embracing the scene context produces a better character; the cutout step removes the background.

**Two-stage L2 architecture:**

1. **Render stage** — Qwen-Image renders character + minimal scene context (subject in foreground, soft-focus background). Prompt includes `minimal_scene_context` directive instead of `pure_white_backdrop`.
2. **Extract stage** — `rembg` cuts subject from background. Per-archetype `cutout_policy` declares which model (`u2net_human_seg` for character+attached props; `birefnet-portrait` for tight character-only) and which attached props to preserve (cup for `tea_beat_close_up`; none for `character_quiet_face`).

The L2 *layer asset* is the post-cutout RGBA PNG. The L2 *render artifact* is the pre-cutout RGB PNG (preserved for re-cutout if policy changes).

**See:** §5 (Subject Safe Zones — applied to post-cutout subject bbox), §6 (continuity state), §8.1 (cutout contract), §12.3 (revised class-A gates).

### 4.4 L3 — Close objects (in-hand, on-table, in-foreground)

**Purpose:** Objects that are in the foreground plane with the character (cup in hand, phone on table, food on plate).

**Render contract:**
- Same as L1, but margin requirements relax to 10% (close foreground tolerates tight crop)
- Backdrop: pure white default; pure black for translucent (glass, steam)
- Z-order: paste AFTER L2 if the object occludes the character (cup blocking part of face); paste BEFORE L2 if character occludes the object (hand wrapping cup)
- **prop_state**-aware: same `object_id` at different states (cup_empty, cup_half, cup_full) = different cached renders (see §6.4)

### 4.5 L4 — Atmospheric overlay

**Purpose:** Steam, light shafts, dappled shadows, dust motes, snowfall, petal fall — diffuse pixel-level effects.

**Render contract:**
- Same resolution as panel
- Backdrop: pure black (0,0,0) so light-colored effects pop into alpha
- For dark overlays (shadow lattice), backdrop is pure white
- Composited with **screen blend mode** (not alpha_composite) for additive effects like steam/light; alpha_composite for opaque effects

### 4.6 Layer namespace reservation

The five layer types above (L0–L4) are **render layers** — they are the diffusion-rendered, rembg-cut, alpha-composited image stack. The schema reserves additional layer namespaces for future use so we don't repaint the bike-shed when those needs arrive:

| prefix | name | purpose | reserved IDs |
|--------|------|---------|--------------|
| **L** | render_layer | diffusion → alpha cutout → composite (this spec) | L0–L9 |
| **S** | semantic_layer | machine-derived from L: depth_map, normal_map, segmentation_mask | S0–S9 |
| **E** | export_layer | derived views for downstream use: line_art_only, color_only, FX_only, dialogue_safe_matte, screentone_overlay | E0–E9 |
| **I** | ink_layer | manga-native sub-layers if we ever decompose L2/L3 into outline/fill/shading/tone | I0–I9 |
| **A** | animation_layer | motion derivatives: parallax_BG, eye_blink, steam_motion, rack_focus_mask | A0–A9 |

**Why reserve now?** The L0/L2 split unlocks every one of these. Once layers are stable image-domain assets, depth maps fall out of monocular-depth models; line-art-only exports fall out of edge detection on L2/L3; eye-blink/breathing animations fall out of L2 with face-region masking. The architecture supports all of it. We are not building it today, but if we let "L5" mean different things in different scripts, we will regret it at 800-series scale.

**Rule:** any new layer type added to the pipeline MUST claim an ID from one of these namespaces and update this table. No ad-hoc layer IDs.

---

## 5. Subject Safe Zones — Hierarchical Contract Inheritance

This is the rule set that prevents the "shoulders cut off" failure. v0.1 of this spec presented the rules as a flat ~600-cell table. v0.2 makes the rules **compositional** — a 5-level inheritance chain with explicit precedence — so the rules can grow without becoming brittle. The flat table at §5.6 is the **compiled view**, not the source of truth.

### 5.1 The inheritance chain

```
base_contract                              (universal defaults)
   ↓ inherited by
framing_contract                           (CU / MCU / MS / LS / ELS / ECU / insert)
   ↓ inherited by
subject_contract                           (character_face_only / hand_only / object_macro / ...)
   ↓ modified by
genre_modifier                             (healing / dark_fantasy / mecha / ...)
   ↓ overridden by
archetype_exception                        (one specific archetype's deviation)
```

**Precedence:** later wins. An `archetype_exception` beats a `genre_modifier` beats a `subject_contract` beats a `framing_contract` beats `base_contract`.

**Why this matters:** when we add a 9th genre, we add ONE `genre_modifier` entry that lists only deviations from the base/framing/subject contracts above it — we don't author 600 new cells. When we discover a new archetype edge case (one panel where the rule has to bend), we add ONE `archetype_exception` rather than editing the genre-wide rule.

### 5.2 base_contract (universal)

```yaml
base_contract:
  margin_min_pct_all_sides: 5       # nothing ever touches the canvas edge
  backdrop: pure_white               # default for cutout-isolated subjects
  backdrop_corner_tolerance: 5       # RGB ±5 from declared backdrop at all 4 corners
  subject_must_not_touch_edge: true  # bbox of non-backdrop pixels has ≥5px clearance
  feather_px: 0                      # hard alpha (manga line-art demand)
  alpha_bimodal: true                # post-rembg histogram peaks at 0 and 255, no gray bleed
```

### 5.3 framing_contract (extends base, indexed by framing type)

```yaml
framing_contract:
  CU:                                # close-up: face + shoulders
    subject_zone_pct: [65, 80]
    margin: {top: 10, bottom: 5, left: 17.5, right: 17.5}
    notes: "forehead has air; shoulders may crop at the very bottom edge intentionally"
  MCU:                               # mid-close-up: chest + face
    subject_zone_pct: [55, 75]
    margin: {top: 12, bottom: 13, left: 22.5, right: 22.5}
    notes: "used when chest+arm gesture matters"
  MS:                                # medium: full upper body, knees-up
    subject_zone_pct: [50, 90]
    margin: {top: 5, bottom: 5, left: 25, right: 25}
    notes: "most common character framing"
  LS:                                # long shot: full body
    subject_zone_pct: [35, 95]
    margin: {top: 2, bottom: 0, left: 32.5, right: 32.5}
    notes: "feet may align with bottom edge; head has 2% air"
  ELS:                               # extreme long: figure < 1/3 frame
    subject_zone_pct: null
    margin: null
    notes: "character is part of L0 background — NOT a separate L2 layer"
  ECU:                               # extreme close-up: macro of object/eye/hand
    subject_zone_pct: [75, 80]
    margin: {top: 10, bottom: 10, left: 12.5, right: 12.5}
    notes: "subject IS the panel; tight tolerances OK"
  insert:                            # overhead / top-down view
    subject_zone_pct: [65, 75]
    margin: {top: 12.5, bottom: 12.5, left: 17.5, right: 17.5}
    notes: "object(s) center-frame"
```

### 5.4 subject_contract (extends framing, indexed by subject type)

```yaml
subject_contract:
  character_full_figure:
    inherits_from: framing.MS         # or framing.LS by archetype declaration
  character_face_only:
    inherits_from: framing.CU
    override: {margin.top: 15}        # extra forehead air for portrait emphasis
  character_silhouette_back:
    inherits_from: framing.CU         # or framing.MCU
    override: {margin.all: 10}        # silhouettes are forgiving — looser rules
  character_hand_only:
    inherits_from: framing.ECU
    override: {subject_zone_pct: [65, 65], margin.all: 17.5}
  character_hands_and_arms:           # e.g., cup-wrapping pose
    inherits_from: framing.ECU
    override: {subject_zone_pct: [70, 60], margin.all: 15}
  object_macro:
    inherits_from: framing.ECU
  object_scene_fit:                   # L3 object positioned per archetype bbox
    inherits_from: framing.insert
    override: {subject_zone_pct: [35, 45]}
  multi_object_overhead:              # food preparation, table spread
    inherits_from: framing.insert
  food_close_up:                      # single dish, plate-on-table angle
    inherits_from: framing.ECU
    override: {subject_zone_pct: [60, 55], margin.all: 20}
```

### 5.5 genre_modifier (modifies any layer in the chain above)

```yaml
genre_modifier:
  healing:                            # iyashikei
    additions:
      composite_rule.negative_space_min_pct: 40
  slice_of_life:
    additions:
      composite_rule.negative_space_min_pct: 30
  dark_fantasy:
    overrides:
      framing.CU.margin: {top: 7, bottom: 3, left: 12, right: 12}    # ⅔ default
      framing.MCU.margin: {top: 8, bottom: 9, left: 17, right: 17}
    additions:
      archetype_flag.dramatic_bleed_allowed: true
  psychological_horror:
    overrides:
      framing.CU.margin.top: 15        # extra above-head air for dread
      framing.CU.margin.bottom: 0       # chin/throat crop allowed (looming gaze)
    additions:
      framing.dutch_angle.margin_all_bonus: 5   # rotation eats space
  mecha:
    overrides:
      framing.LS.subject_zone_pct: [50, 95]    # mecha-pilot context widens zone
      subject_contract.object_macro.margin.all: 8   # mechanism detail intentional bleed
  romance:
    additions:
      framing.CU.eye_height_alignment: rule_of_thirds_upper
  fantasy_adventure:
    overrides:
      framing.LS.subject_zone_pct: [40, 95]
      framing.MS.subject_zone_pct: [55, 90]    # weapon/prop in subject zone
  comedy:
    overrides:
      framing.CU.margin.top: 18         # room for exaggerated expression burst
      framing.MCU.margin.top: 20
    additions:
      composite_rule.expression_burst_zone: outside_subject_zone_within_canvas
```

### 5.6 archetype_exception (per-archetype overrides; rare)

Most archetypes inherit cleanly from `genre_modifier ∘ subject_contract ∘ framing_contract ∘ base_contract`. An `archetype_exception` is only added when a specific archetype's intent breaks one of those rules deliberately.

Iyashikei example: `window_light_threshold` declares `character_silhouette_back` and a 35% body bleed left. The framing+subject chain says "no edge touch." The archetype overrides: `subject_must_not_touch_edge: false` and pins `subject_placement_bbox_character: [5, 30, 45, 95]` — character intentionally bleeds left edge as composition signature.

```yaml
archetype_exception:
  window_light_threshold:
    inherits_from: subject_contract.character_silhouette_back + genre_modifier.healing
    overrides:
      base.subject_must_not_touch_edge: false
      placement_pinned: [5, 30, 45, 95]
      rationale: "Composition signature — left-bleed silhouette against window light"
```

### 5.7 Compiled view (flat table — derived, not source of truth)

For human readability, here is the compiled table for the most common (archetype × genre × subject) combinations. **This is regenerated from the YAML above by `scripts/manga/compile_safe_zones.py` — do not hand-edit.**

| framing | subject_type | genre | subject_zone | margin (T/B/L/R) |
|---|---|---|---|---|
| CU | character_face_only | healing | 65% × 80% | 15 / 5 / 17.5 / 17.5 |
| CU | character_face_only | psychological_horror | 65% × 80% | 15 / 0 / 17.5 / 17.5 |
| CU | character_face_only | comedy | 65% × 80% | 18 / 5 / 17.5 / 17.5 |
| MCU | character_full_figure | healing | 55% × 75% | 12 / 13 / 22.5 / 22.5 |
| MS | character_full_figure | healing | 50% × 90% | 5 / 5 / 25 / 25 |
| MS | character_full_figure | fantasy_adventure | 55% × 90% | 5 / 5 / 22.5 / 22.5 |
| LS | character_full_figure | healing | 35% × 95% | 2 / 0 / 32.5 / 32.5 |
| LS | character_full_figure | mecha | 50% × 95% | 2 / 0 / 25 / 25 |
| ECU | object_macro | healing | 75% × 80% | 10 / 10 / 12.5 / 12.5 |
| ECU | object_macro | mecha | 75% × 80% | 8 / 8 / 8 / 8 |
| ECU | character_hand_only | healing | 65% × 65% | 17.5 / 17.5 / 17.5 / 17.5 |
| insert | multi_object_overhead | healing | 65% × 75% | 12.5 / 12.5 / 17.5 / 17.5 |

### 5.8 What this gives the prompt builder

Concrete prompt suffix injection — for an iyashikei CU character face layer:
```
"...full upper body visible, head centered in upper-third of frame,
  shoulders WITH MARGIN — both shoulders fully inside the frame with at
  least 17% empty space on left and right of body, forehead with at least
  15% empty space above hairline, no body part touching the frame edge,
  isolated subject on PURE WHITE BACKGROUND (#FFFFFF), no scene, no shadow
  on background, no environmental texture, high-contrast silhouette."
```

This replaces today's "Plain pale sage background" failure mode. The values (`17%`, `15%`) come from the compiled compose of `healing.character_face_only.CU`.

### 5.9 Contract-to-prompt compiler (NEW in v0.5 — closes the prompt-injection seam)

A deterministic safe-zone contract is worthless if the natural-language prompt that fulfills it is hand-written. v0.4 implicitly assumed someone would translate `subject_zone_pct: [65, 80], margin.top: 15` into "head centered in upper-third of frame, ≥15% empty space above hairline" — and that translator is where contract ambiguity silently leaks back in.

v0.5 specifies the **contract-to-prompt compiler** as a first-class artifact that runs between the compiled safe-zones (§5.7 output) and the renderer dispatcher (§11). Its job: convert structured contract values to prompt strings via deterministic template substitution.

**Inputs to the compiler:**
| input | source |
|---|---|
| compiled safe-zone row | `config/manga/compiled/safe_zones.yaml` (output of `compile_safe_zones.py`) |
| character_design | `config/source_of_truth/manga_profiles/series/<series>.yaml` |
| continuity_state | `artifacts/manga/<series>/continuity_state/<episode>/<panel>.yaml` |
| light_rig | `config/manga/light_rigs/<genre>.yaml` → keyed by `light_rig_id` |
| layer type + archetype | `config/manga/panel_templates/<genre>.yaml` `layer_render_contract` block |

**Output of the compiler:**
```python
@dataclass
class PromptBundle:
    positive: str            # full positive prompt string
    negative: str            # full negative prompt string
    parameters: dict         # model params (steps, cfg, sampler) per §11 routing
    cache_key: str           # sha256 of (positive, negative, parameters, model_id)
    provenance: dict         # which template + input dict produced this (for debugging)
```

**Template system (deterministic, NOT LLM-based):**
- Templates live in `config/manga/prompt_templates/<layer_type>.<form>.template.txt`
  - `L0.positive.template.txt`, `L0.negative.template.txt`
  - `L1.positive.template.txt`, `L1.negative.template.txt`
  - `L2.positive.template.txt`, `L2.negative.template.txt`
  - `L3.positive.template.txt`, `L3.negative.template.txt`
  - `L4.positive.template.txt`, `L4.negative.template.txt`
- Plain Python `str.format_map(...)` substitution with a known slot set per template — no Jinja2 logic, no conditionals beyond `{slot or default}` fallbacks
- Each slot has a typed source: `{character.render_prompt_base}`, `{safe_zone.shoulder_margin_clause}`, `{light_rig.prompt_clause}`, `{continuity.gaze_clause}`, etc.
- The compiler errors fatally on missing slot data (no silent fallback to empty string)

**Example L2 character template (skeleton):**
```
{character.render_prompt_base}.

POSE: {continuity.pose_clause}.
GAZE: {continuity.gaze_clause}.
HAND STATE: {continuity.hand_state_clause}.
EXPRESSION: {continuity.emotional_clause} at intensity {continuity.expression_dial}.

FRAMING: {safe_zone.framing_clause} — subject zone {safe_zone.subject_zone_pct_str}, margins top {safe_zone.margin.top}% / bottom {safe_zone.margin.bottom}% / sides {safe_zone.margin.left}%.
SHOULDERS WITH MARGIN: {safe_zone.shoulder_margin_clause}.
NO BODY PART TOUCHING FRAME EDGE.

LIGHTING: {light_rig.prompt_clause}.

STYLE: {style_state.line_weight_clause}, {style_state.wash_softness_clause}, {style_state.tonal_density_clause}.

BACKDROP: isolated subject on {safe_zone.backdrop_name} background ({safe_zone.backdrop_hex}), no scene, no shadow on background, no environmental texture, no color wash, high-contrast silhouette.
```

**Slot vocabulary — additive-safe semantics (v0.5.1):**

- Canonical machine-readable source: `config/manga/prompt_templates/slot_registry.yaml`
- Human-readable index: `config/manga/prompt_templates/SLOTS.md` (auto-generated from registry; do not hand-edit)
- Per-layer-type, slots are declared as `required` or `optional`

**Three slot-validation rules (compiler enforces):**

| condition | behavior |
|---|---|
| Template uses a slot, registry has it as `required`, contract provides a value | OK — substitute the value |
| Template uses a slot, registry has it as `required`, contract does NOT provide a value | **FATAL** — missing required slot |
| Template uses a slot, registry has it as `optional`, contract does NOT provide a value | OK — substitute the registry-declared `default_when_missing` (or empty string with debug log) |
| Template uses a slot that is NOT in the registry | **FATAL** — unknown slot reference |
| Contract provides a slot value that template doesn't reference | **WARN** (logged once per compile run) — extra data ignored; not blocking |
| Registry declares a slot that no template uses yet | OK — additive-safe; documented future capacity |

**Why additive-safe matters:** new slots can be introduced into the registry + contract pipeline (e.g., adding `light_rig.color_temp_K` for an upcoming workflow) WITHOUT breaking templates that don't yet reference them. The vocabulary grows without re-locking the system. Only when a template references a slot does that template's contract become responsible for providing it.

**Template version bump triggers:**
- Adding a `required` slot reference to an existing template → template MAJOR version bump (breaks existing contracts)
- Adding an `optional` slot reference → template MINOR bump (additive)
- Adding a slot to the registry without any template using it → no version bump (advisory)
- Removing a slot reference from a template → template MINOR bump
- Removing a slot from the registry → spec amendment required (registry is authority)

**Determinism contract:** identical input → identical output prompt string. The compiler is golden-snapshot tested same as `compile_safe_zones.py`: a fixed (compiled_row, character_design, continuity_state, light_rig) tuple hashes to a stable `(positive, negative)` pair.

**What this prevents:** the operator-flagged failure mode — "deterministic contract produces a deterministic dict that then gets translated to natural language by whoever writes the prompt, which reintroduces the ambiguity the whole spec is designed to eliminate." With v0.5, the translation IS the spec.

**Implementation:** `scripts/manga/contract_to_prompt_compiler.py` — Phase B.1 step 1.5 (between step 1 `compile_safe_zones.py` and step 2 `validate_layer.py`).

---

## 6. State Continuity Architecture (NEW in v0.2)

The biggest weakness of v0.1: it solved framing, isolation, reuse — but the pipeline still couldn't tell that "Mira sitting in panel 3" is **emotionally adjacent** to "Mira sitting in panel 4." Panels rendered correctly in isolation; they didn't read coherently in sequence.

v0.2 adds **continuity state** as a first-class input that sits between `story_beat` and `archetype`:

```
chapter_script.yaml
   ↓ extracts
story_state                    (the beat's narrative position)
   ↓ rolls forward through
continuity_state               (per-character, per-prop, per-scene running state)
   ↓ selects
archetype                      (composition contract)
   ↓ instantiates
layers (L0-L4)                 (render assets)
   ↓ composites
panel                          (the deliverable)
```

The continuity state is what makes consecutive panels feel like the same world.

### 6.1 Continuity state schema

Continuity state is **per-panel** but **inherits from the previous panel** by default (with explicit deltas).

```yaml
# Path: artifacts/manga/<series>/continuity_state/<episode_id>/<panel_id>.yaml
schema_version: "1.0.0"
panel_id: "ep001_004"
inherits_from: "ep001_003"           # previous panel (or null for episode opening)

character_state:                     # one block per character on stage
  mira_aoki:
    emotional: "anxious_diminishing"  # enum — see §6.2
    posture: "seated_upright_to_slumped"  # transition or steady-state
    gaze_direction: "down_at_cup"     # one of: at_camera / at_named_object_X / off_frame_L / off_frame_R / up / down
    hand_state: "wrapping_cup"        # registers with §6.4 prop_state
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

**Note:** for V4 launch, `relational_field` exists in the schema but only `active_entities`, `shared_attention_anchor`, and `emotional_tension_vector.direction` are validated. Full multi-character relational fields (eye-line geometry, paired emotional state, contact continuity) are Phase 2 — see §15.B.1. The schema reservation here prevents Phase-2 work from requiring a continuity_state migration.

### 6.2 The state vocabularies (enums)

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

### 6.3 Continuity invariants (the gates that prevent jarring transitions)

Invariants are split into **deterministic** (V4 launch enforced, brutally simple, no model inference) and **heuristic / narrative** (Phase B.2+ — model-assisted, advisory rather than enforced).

#### 6.3.A Deterministic invariants (V4 launch — enforced by `validate_continuity_invariants.py` V1)

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
    # V4 LAUNCH LIMITATION (called out per §15.A.2):
    #   When PuLID is blocked (EVA-CLIP hang) AND no per-character LoRA exists,
    #   character_design_hash = axes_hash only. The structural invariant PASSES
    #   when two panels declare the same axes — but this does NOT guarantee the
    #   diffusion model rendered the same face. Perceptual identity drift is a
    #   class-C concern (Phase B.2), explicitly deferred. §15.A.2's "identity
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

#### 6.3.B Heuristic / narrative invariants (Phase B.2 — model-assisted, advisory)

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

V4 launch: deterministic invariants block render-cache writes. Heuristic invariants surface in `qa_review_queue.yaml` (§14.E) for operator triage but do NOT block. Phase B.2 work elevates heuristics to enforced after the deterministic core has stabilized.

### 6.4 How continuity state modifies layer prompts

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

### 6.5 Prop state evolution drives separate L3 renders

`cup_ceramic` at three states = three cached L3 layers:
- `cup_ceramic__empty.png`
- `cup_ceramic__half.png`
- `cup_ceramic__full.png`

The chapter_script declares prop_state per panel; the builder selects the matching L3 cutout. No re-rendering at panel time.

### 6.6 Temporal state drives separate L0 renders

`kitchen_table` at four temporals = four cached L0 layers:
- `kitchen_table__dawn.png`
- `kitchen_table__morning.png`
- `kitchen_table__evening.png`
- `kitchen_table__night.png`

Single scene, four lighting states. Composited identically; light direction continuity preserved within each temporal block.

### 6.7 Continuity state record (what gets persisted)

For each panel: `artifacts/manga/<series>/continuity_state/<episode>/<panel>.yaml` — full state record. Inherited diffs only (the previous panel's values carry forward unless overridden). Validates against §6.3 invariants pre-render.

For each rendered layer: `artifacts/manga/<series>/render_cache/<layer_id>.png` — the binary asset. Cache key = `(layer_type, subject_id, pose_id, continuity_state_hash)`. Cache invalidation: §14.

### 6.8 State cardinality management (combinatorial explosion containment)

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
- Light rig: indexed (not freeform parameters) — see §6.9.
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

### 6.9 Light rig as first-class scene state (replaces v0.2's lighting-direction-only model)

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
4. QA gate §14.B.1 validates light rig coherence post-composite by detecting the 7 axes above (direction, softness, temperature, rim, bounce, diffusion, exposure) and comparing against the declared light_rig values.

**Why this is image-first not world-engine (per §1.3):** the light rig is a *prompt-injected metadata bundle and a post-render-validation target*, not an actual lighting calculation. We don't compute shadows. We constrain the renderer to produce consistent shadows. That's a contract, not a simulation.

**Pre-built light rig library:** `config/manga/light_rigs/iyashikei.yaml` defines ~8 named rigs (K01–K08) covering: dawn window warm, dawn window cool, morning bright, midday flat, afternoon golden, evening warm, dusk dim, night lamp-warm, night moonlight-cool. Phase-2 genres add their own (mecha cockpit, fantasy_torchlight, horror_fluorescent, etc.).

**Scene_inventory references rigs by ID** (not by inline definition). One rig serves many scenes. One scene can have several time-of-day rigs.

### 6.10 Visual-compilation vs narrative-evolution boundary (architectural modularization risk)

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

**V4 design choice:** keep them together with explicit section labels. Don't entangle the validators across the boundary. The deterministic continuity validator (§6.3.A) reads ONLY visual-compilation fields. The heuristic validator (§6.3.B) reads ONLY narrative fields. Operators editing one section don't break the other.

**The lesson:** as the architecture grows, resist the merge. Render orchestration and dramaturgy are different problem domains. Sharing a YAML file is fine; sharing a validator code path is not.

### 6.11 Cache telemetry (economic instrumentation)

Cardinality controls (§6.8) are necessary but invisible without telemetry. v0.4 adds an observability contract so the cache can be reasoned about operationally.

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

### 6.12 Style-state continuity (NEW in v0.5 — the missing 4th continuity dimension)

v0.4 covered three continuity dimensions:
1. **Identity** — same character across panels (PuLID / LoRA, embedding distance)
2. **Structural** — same layer composition / framing / spatial layout (archetype contracts)
3. **Semantic / narrative** — same gaze / pose / emotional arc (continuity_state §6.1)

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
- Render prompts (§5.9): `{style_state.line_weight_clause}` and friends are template slots injected into every L0/L2/L3 prompt
- QA gates (§12): class-C perceptual evaluator `style_fingerprint_drift` — extract style features (edge density via Canny + tonal histogram via grayscale variance + stroke-width estimation) per render, cluster within the series, flag outliers > 2σ
- Telemetry (§6.11): per-episode `style_drift_pct` reports outlier count

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

## 7. Per-Archetype Layer Composition Maps

For each of iyashikei's 19 archetypes (the only fully populated genre), this section defines:
- Which layers (L0, L1, L2, L3, L4) the archetype consumes
- The `subject_type` field for each layer (drives §5 lookup)
- The placement bbox (already in `iyashikei.yaml`)
- The engine routing per layer

This is the deterministic mapping `archetype_id` → `[layer_render_contracts]`.

### 7.1 Iyashikei archetype × layer matrix

| archetype_id | L0 (BG) | L1 (env) | L2 (char) | L3 (close obj) | L4 (overlay) |
|---|---|---|---|---|---|
| `tea_beat_close_up` | bg_kitchen_table_dawn | — | char_hands_only | obj_cup | overlay_steam |
| `kettle_steam_macro` | bg_kitchen_table_dawn | — | — | obj_kettle | overlay_steam |
| `morning_routine_sequence` | bg_kitchen | — | char_full_figure | obj_kettle, obj_cup | — |
| `window_light_threshold` | bg_window_view | — | char_silhouette_back (35% bleed L) | — | overlay_dappled_light |
| `character_quiet_face` | bg_kitchen_or_softfocus | — | char_face_only | — | overlay_dappled_light |
| `character_face_micro_tension` | bg_softfocus | — | char_face_only | — | — |
| `chest_breath_micro` | bg_softfocus | — | char_chest_partial | — | — |
| `hand_table_micro` | bg_kitchen_table_top | — | char_hand_only | obj_phone or obj_cup | — |
| `pet_companion_micro` | bg_floor_or_lap_softfocus | — | char_pet_only | — | — |
| `food_preparation_overhead` | bg_table_overhead | — | char_hands_and_arms_overhead | obj_food_array | — |
| `shared_meal_table_medium` | bg_table_two_seats | — | char_full_figure×2 (deferred — §15.B) | obj_food, obj_cup×2 | — |
| `sparse_establishing_wide` | bg_room_wide_no_subject | — | — (or ELS char in L0) | — | overlay_dappled_light |
| `dappled_light_hand` | bg_window_sill_or_lap | — | char_hand_only | — | overlay_dappled_light |
| `seasonal_anchor_object` | bg_table_or_sill | — | — | obj_seasonal | — |
| `walking_in_thought_medium` | bg_street_path_softfocus | — | char_full_figure_walking | — | overlay_dappled_light |
| `phone_notification_macro` | bg_table_or_lap_softfocus | — | char_hand_holding_phone | obj_phone | — |
| `long_drop_decompression` | bg_sky_or_water_wide | — | — | — | overlay_atmospheric |
| `miyazaki_ma_pause` | bg_landscape_wide | — | char_ELS_in_L0 (no separate layer) | — | overlay_atmospheric |
| `pendulation_pair_visual_rhyme` | (paired panels — uses L0 from earlier archetype) | — | — | — | — |

### 7.2 Schema extension to `iyashikei.yaml`

Each archetype gains a new top-level field `layer_render_contract`:

```yaml
tea_beat_close_up:
  # ... existing fields ...
  layer_render_contract:
    L0_bg:
      scene_id: "kitchen_table_dawn"
      reuse_policy: "render_once_per_series_scene_temporal"
    L1_env: null
    L2_char:
      subject_type: "character_hands_only"
      framing_row: "ECU"
      identity_lock: "qwen_pulid_or_lora"
      continuity_inputs: [hand_state, gaze_direction, emotional]
      scene_context_clause: "soft morning kitchen, warm window light, gentle wooden table edge"   # v0.6.1 REQUIRED
      cutout_policy:                     # v0.6 per-archetype cutout contract
        model: u2net_human_seg            # u2net_human_seg keeps cup attached
        keep_attached_props: ["cup"]      # tea_beat_close_up: cup is part of the gesture
        alpha_matting: true
        alpha_matting_foreground_threshold: 240
        alpha_matting_background_threshold: 10
        character_extraction_coverage_min_pct: 0.40   # ECU allows tighter bbox than safe-zone area
        background_bleed_max_pct: 5
    L3_close_obj:
      object_type: "object_macro"
      object_id: "cup_ceramic"
      framing_row: "ECU"
      continuity_inputs: [prop_state]
      reuse_policy: "render_once_per_series_object_state"
      z_order: "above_L2"
    L4_overlay:
      effect_id: "steam_warm"
      blend_mode: "screen"
      opacity: 0.6
```

### 7.3 Phase-2 genres

The other 7 top-priority genres currently have **no archetype catalog**. Phase 2 work (separate spec): author `panel_templates/<genre>.yaml` per genre with `layer_render_contract` schema. Until then, those panels render via V3.1 single-engine single-pass — layer pipeline is gated to genres with populated archetype catalogs.

---

## 8. Per-Story Layer Inventory

Each series needs **three inventories** so layers can be rendered once and reused.

### 8.1 `character_design.yaml` (already exists per series)

`config/source_of_truth/manga_profiles/series/<series_id>.yaml` already has `character_design` with 12 axes (`config/manga/character_design_axes.yaml`). No change needed to existing structure.

**Additions per series:**
- `character_pose_inventory:` — list of poses (front-portrait, side-portrait, hand-only, hands-and-arms-on-cup, full-body-walking, full-body-sitting, etc.) cross-referenced with continuity_state vocabularies from §6.2.
- Each pose × emotional × hand_state combination eligible for caching.

### 8.2 `scene_inventory.yaml` (NEW — to author per series)

Path: `config/source_of_truth/manga_profiles/series/<series_id>.scene_inventory.yaml`

```yaml
schema_version: "1.0.0"
series_id: "stillness_en_01"
scenes:
  - scene_id: "kitchen_table_dawn"
    description: "Mira's kitchen — warm cream + sage, soft window light camera-left, wooden table, houseplant on sill"
    locale_variant_required: false
    temporal_variants_required: [dawn, morning, evening, night]   # if multiple needed
    render_resolution: [1080, 1920]
    used_in_archetypes: [tea_beat_close_up, kettle_steam_macro, morning_routine_sequence, character_quiet_face, hand_table_micro]
    L0_prompt: "Wide establishing shot of a kitchen at dawn..."
    L0_negative_prompt: "people, person, character, human, figure, kettle, cup, phone..."
```

Typical iyashikei series: 4–8 scenes. Each rendered ONCE per (scene_id, temporal_variant, locale_variant).

### 8.3 `object_inventory.yaml` (NEW — to author per series)

Path: `config/source_of_truth/manga_profiles/series/<series_id>.object_inventory.yaml`

```yaml
schema_version: "1.0.0"
series_id: "stillness_en_01"
objects:
  - object_id: "cup_ceramic"
    description: "Matte ceramic cup, warm cream glaze, slight rim chip (continuity detail)"
    object_type: "object_macro"
    state_variants_required: [empty, half, full]   # drives §6.5
    render_resolution: [1080, 1920]
    used_in_archetypes: [tea_beat_close_up, hand_table_micro, shared_meal_table_medium]
    backdrop: "pure_white"
    L3_prompt_template: "Macro close-up of a matte ceramic cup, warm cream glaze, {state_clause}..."
    L3_negative_prompt: "people, hands, scene, text..."
```

Typical iyashikei series: 6–15 hero objects, 1–4 state variants each.

### 8.4 Compute budget (revised for v0.2)

For a typical iyashikei 10-episode series:
- 1 character × 8 poses × 4 emotional × 4 hand_states ≈ ~30 L2 candidates BUT cache hit rate ~70% (most panels reuse the same `pose, emotional, hand_state` triple). Net: ~25 unique L2 renders per character.
- 8 scenes × 4 temporal variants = 32 L0 renders
- 10 objects × 2 state variants average = 20 L3 renders
- 5 atmospheric overlays = 5 L4 renders

Total: ~82 unique renders. Composed into ~300 panels per series. **~3.7× efficiency vs V3.1's 1-render-per-panel** (down from the v0.1 estimate of 10× — continuity_state inflates the unique-render count, but adds the semantic-coherence v0.1 was missing).

---

## 9. Backdrop Rules for Cutout Success

### 9.1 Character layers (L2) — REWRITTEN v0.6: backdrop moves from render-contract to cutout-contract

**v0.5.1 had:** "Mandatory pure white backdrop. Verification gate: corner RGB within ±5 of (255,255,255). Fail-and-rerender if not."

**v0.6 has (empirical pivot):** L2 character renders allow scene context. Backdrop verification at render time is SKIPPED for L2. The backdrop contract becomes a **cutout contract** — applied AFTER rembg extraction.

**Render prompt for L2 (v0.6.1 — flipped from suppression to specification):**

v0.6 attempted to suppress the scene ("minimal scene context"). v0.6.1 (post-B-test #2) flips to **specifying** the scene per archetype, because B-test #2 proved Qwen ignores absence-of directives. The prompt declares what scene context the archetype wants; Qwen renders it; rembg extracts the subject.

```
"[character_description]. [pose_description]. [archetype.scene_context_clause]
  — soft focus, shallow depth of field, subject in sharp foreground,
  background atmospherically blurred and supportive (not competing detail)."
```

Where `archetype.scene_context_clause` is a **REQUIRED L2 slot** (slot_registry v0.6.1), sourced from `iyashikei.yaml` per-archetype `layer_render_contract.L2_char.scene_context_clause`. Examples:
- `tea_beat_close_up`: "soft morning kitchen, warm window light, gentle wooden table edge"
- `character_quiet_face`: "soft morning kitchen, warm window light, implied domestic warmth"
- `window_light_threshold`: "threshold between interior and exterior, diffuse backlight"
- `walking_in_thought_medium`: "quiet residential walking path, soft daylight, suggestion of low garden walls"

**Why this works:** Qwen's scene-prior is part of how it renders identity. Telling it the scene gives it the grounding signal; it produces a coherent character. The cutout policy then extracts the subject — the scene was instrumental, not the deliverable.

**Per-archetype cutout_policy (NEW v0.6 — declared in `iyashikei.yaml` per §7.2):**

```yaml
cutout_policy:
  model: u2net_human_seg            # or birefnet-portrait for tight character-only
  keep_attached_props: ["cup"]       # archetype-specific list of props to PRESERVE post-cutout
  alpha_matting: true                # cleans soft edges (rembg's alpha_matting=True flag)
  alpha_matting_foreground_threshold: 240
  alpha_matting_background_threshold: 10
  post_cutout_validation:
    character_extraction_coverage_min_pct: 0.50    # bbox area ≥ 50% of declared subject_zone_pct
    background_bleed_max_pct: 5                    # 20px-inward edge alpha ≤ 5%
```

**Model selection guidance (driven by B-test + birefnet comparison):**
- `u2net_human_seg`: best for character + tightly-attached objects (cup-wrapping pose, hand-holding-phone). Keeps the held object naturally.
- `birefnet-portrait`: best for face-heavy CU where only the character body should remain (character_quiet_face, character_face_micro_tension). Tighter silhouette; faster to converge.
- `isnet-anime`: deferred — failed on watercolor-wash backdrops in layer-demo-v2; only useful if Qwen produces hard-edged anime-flat renders (not our iyashikei aesthetic).

**Alpha matting (NEW v0.6):** mandatory for L2 cutouts. `rembg.remove(im, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10)`. Reduces silhouette edge softness from ~1.5-2% gray-band to <1%.

**Alternative pure-black backdrop:** still permitted for dark-haired/dark-clothed characters where scene context might compromise readability. Same cutout-contract pipeline applies.

### 9.2 Object layers (L1, L3)

| object property | backdrop | rembg model |
|---|---|---|
| default | pure white | u2net |
| translucent (glass, steam, ice) | pure black | u2net |
| reflective (chrome, mirror) | mid-gray (128,128,128) | u2net + alpha-matting flag |

### 9.3 Overlay layers (L4)

| effect | backdrop |
|---|---|
| steam, dust motes, light shafts | pure black (light effect → alpha = brightness) |
| dappled shadows | pure white (dark effect → invert → alpha) |
| snowfall, petals | pure black |

### 9.4 Background layers (L0)

No backdrop rule — L0 IS the backdrop. The rule for L0: **scene must have empty space in the bbox region where the character will be composited.** L0 prompt suffix: `"...with generous empty space at [bbox_region] of the frame for the subject."`

---

## 10. Composite Placement Math

```python
def composite_layer(canvas, layer_cutout, archetype_bbox):
    W, H = canvas.size
    x_pct, y_pct, w_pct, h_pct = archetype_bbox
    target_x = int(W * x_pct / 100)
    target_y = int(H * y_pct / 100)
    target_w = int(W * w_pct / 100)
    target_h = int(H * h_pct / 100)
    layer_tight = layer_cutout.crop(layer_cutout.getbbox())
    scale = min(target_w / layer_tight.width, target_h / layer_tight.height)
    new_size = (int(layer_tight.width * scale), int(layer_tight.height * scale))
    layer_scaled = layer_tight.resize(new_size, Image.LANCZOS)
    paste_x = target_x + (target_w - new_size[0]) // 2
    paste_y = target_y + (target_h - new_size[1]) // 2
    canvas.alpha_composite(layer_scaled, dest=(paste_x, paste_y))
    return canvas
```

**Z-order (bottom to top):**
```
1. L0  (background)
2. L1  (mid-distance objects)
3. L2  (character)             OR L3 if L3.z_order = "below_L2"
4. L3  (close objects)         OR L2 if L3.z_order = "below_L2"
5. L4  (atmospheric overlay; screen-blend, not alpha-composite)
```

**Feathering policy:** 0px (hard alpha). Manga line art needs crisp edges. L4 overlays get 2–3px Gaussian on alpha before screen-blend.

---

## 11. Engine Routing Per Layer

Cross-reference `docs/specs/MANGA_V3_3_MODEL_ROUTING_SPEC.md`.

| layer | preferred engine | fallback | rationale |
|---|---|---|---|
| **L0** (BG) | Qwen-Image (no-PuLID) | FLUX-dev | Scene without people |
| **L1** (env object) | Qwen-Image | FLUX-schnell | Same as L0 |
| **L2** (character) | Qwen-Image + PuLID-FaceNet | Qwen-Image alone (V3.1) | Identity lock from face reference |
| **L3** (close object) | Qwen-Image | FLUX-schnell | Consistency with rest of stack |
| **L4** (atmospheric) | FLUX-schnell | Qwen-Image | Style-invisible; speed wins |

**Hard rule:** if any layer in a panel uses a different engine than another layer in the same panel, the composite WILL show style drift. **All non-L4 layers in a panel use the same engine.** L4 is screen-blended and style-invisible — engine choice is free.

**V3.1 status (today):** PuLID blocked → L2 renders as Qwen-Image alone. Identity drift across panels is a known V3.1 limitation. V4 requires PuLID OR per-character LoRA.

---

## 12. QA Gates Per Layer — Validator Taxonomy

The operator critique flagged a critical drift: v0.3 treated deterministic checks (corner RGB) and probabilistic checks (lighting coherence, identity distance) as one undifferentiated category. v0.4 splits them.

### 12.0 The four validator classes

| class | nature | severity | runs in | example |
|---|---|---|---|---|
| **A. Contract validators** | deterministic; pure structural / numeric checks; no model inference | **FAIL** (blocks cache write) | V4 launch | backdrop_corner_check, bbox clearance, alpha histogram bimodal |
| **B. Heuristic scorers** | rule-based statistical; computable from pixels but with thresholds, not certainties | **WARN** (advisory; logged) | V4 launch | effect_density coverage range, palette_compliance |
| **C. Perceptual evaluators** | model-based fuzzy; require a vision model to evaluate | **SCORE** (diagnostic) | V4 launch (advisory) → Phase B.2 (enforced where stable) | identity_distance (cosine via face embedding), pose_match (CLIP zero-shot), saliency_drop |
| **D. Narrative invariants** | semantic / LLM-assisted; require language model to evaluate intent | **SCORE** (diagnostic only at V4) | Phase B.2+ | emotional_pendulation, gaze_continuity_semantic, tension_arc_coherence |

**Hard rule:** a class-A failure blocks render-cache write. Classes B / C / D produce structured logs to `qa_review_queue.yaml` (§14.E) for operator triage but do NOT block. This protects the deterministic core from being contaminated by probabilistic outputs.

**Severity escalation path:** as a class-B/C/D check matures in production (calibration tightens, false-positive rate drops below ~3%), it MAY be promoted to FAIL. Promotion requires explicit spec amendment + telemetry evidence.

### 12.1 L0 gates

| check | class | severity |
|---|---|---|
| `forbidden_subject_check` (no human/face/object via CLIP zero-shot) | C — perceptual | SCORE (advisory V4; FAIL Phase B.2) |
| `negative_space_in_bbox` (archetype bbox region pixel variance < 0.15) | A — contract | FAIL |
| `palette_compliance` (dominant colors match series palette) | B — heuristic | WARN |
| `forbidden_grammar_check` (per-genre forbidden_grammar list via CLIP) | C — perceptual | WARN (advisory V4) |

### 12.2 L1 / L3 (object) gates

| check | class | severity |
|---|---|---|
| `backdrop_corner_check` (4 corners within ±5 of declared backdrop) | A — contract | FAIL |
| `subject_safe_zone` (bbox of non-backdrop ⊆ §5 safe zone) | A — contract | FAIL |
| `subject_does_not_touch_edge` (≥5px clearance from canvas edge) | A — contract | FAIL |
| `rembg_clean_alpha` (histogram bimodal at 0 and 255) | A — contract | FAIL |

### 12.3 L2 (character) gates — RESTRUCTURED v0.6 for Path B (cutout contract)

L2 gates differ from L1/L3 because L2 is two-stage (pre-cutout render + post-cutout extraction). L1/L3 inherit all class-A gates from §12.2 directly.

**Pre-cutout render (the Qwen output PNG):**

| check | class | severity |
|---|---|---|
| `backdrop_corner_check` | A | **SKIP for L2** (replaced by post-cutout `background_bleed_check`; v0.6 amendment) |
| `subject_safe_zone` | A | SKIP for pre-cutout (run on post-cutout only) |
| `subject_does_not_touch_edge` | A | SKIP for pre-cutout (run on post-cutout only) |

**Post-cutout RGBA layer (the extracted L2 asset that gets composited):**

| check | class | severity |
|---|---|---|
| `rembg_clean_alpha` (gray band threshold relaxed to **3%** for L2; scene renders have softer edges than synthetic-white renders) | A | FAIL |
| `character_extraction_coverage` (NEW v0.6 — character bbox area ≥ `coverage_min_pct` × declared subject_zone area; proves character wasn't eaten by cutout) | A | FAIL |
| `background_bleed_check` (NEW v0.6 — sample 20px-inward from each canvas edge post-cutout; alpha ≤ 5% there proves background was removed) | A | FAIL |
| `subject_safe_zone` (post-cutout bbox ⊆ §5 safe zone) | A | FAIL |
| `subject_does_not_touch_edge` (post-cutout clearance) | A | FAIL |
| `identity_distance` (cosine ≤ 0.55 vs character reference) | C — perceptual | SCORE (V4 advisory; FAIL Phase B.2 once calibrated) |
| `subject_type_pose_match` (CLIP zero-shot) | C — perceptual | WARN |
| `face_visible_for_face_archetypes` (upstream face_confidence > 0.85) | A — contract | FAIL |
| `forbidden_anatomy` (extra fingers, missing limbs — model-based) | C — perceptual | WARN |
| `continuity_invariants_deterministic` (§6.3.A) | A — contract | FAIL |
| `continuity_invariants_heuristic` (§6.3.B) | D — narrative | SCORE |

**KNOWN LIMITATION (v0.6.3 logged 2026-05-20, post-B-test-#3):** `background_bleed_check` cannot distinguish subject-body-at-edge from scene-fragment-at-edge without ML segmentation. For face-only archetypes (`character_quiet_face`, `character_face_micro_tension`, `pet_companion_micro`), treat `background_bleed_check` PASS as **necessary but not sufficient**; the primary gate is `subject_does_not_touch_edge`. If both bleed and edge-touch FAIL together, the diagnosis is over-tight framing (subject fills canvas) — re-author scene_context_clause to use breathing-room language per the compile-time WARN in `contract_to_prompt_compiler.py` (looks for "fill the frame", "edge to edge", etc., when safe_zone declares non-zero margins).


**Two new class-A gates (v0.6) detailed:**

```python
def check_character_extraction_coverage(cutout_rgba, safe_zone_row, archetype_cutout_policy):
    """Confirms rembg didn't eat the character. The opaque bbox must cover
    at least `coverage_min_pct` of the declared safe zone area."""
    alpha = np.array(cutout_rgba)[:, :, 3]
    opaque = alpha > 250
    if not opaque.any():
        return FAIL("no character extracted")
    ys, xs = np.where(opaque)
    bbox_area_px = (xs.max() - xs.min()) * (ys.max() - ys.min())
    zone_w_pct, zone_h_pct = safe_zone_row["subject_zone_pct"]
    W, H = cutout_rgba.size
    zone_area_px = (W * zone_w_pct / 100) * (H * zone_h_pct / 100)
    coverage_min = archetype_cutout_policy.get("character_extraction_coverage_min_pct", 0.50)
    return PASS if bbox_area_px >= coverage_min * zone_area_px else FAIL


def check_background_bleed(cutout_rgba, edge_inset_px=20, max_bleed_pct=5):
    """Sample alpha values in a 20px-inward frame from each canvas edge.
    These pixels should be ≥95% transparent if rembg cleaned the background."""
    alpha = np.array(cutout_rgba)[:, :, 3]
    H, W = alpha.shape
    edge_band = np.concatenate([
        alpha[:edge_inset_px, :].flatten(),
        alpha[-edge_inset_px:, :].flatten(),
        alpha[:, :edge_inset_px].flatten(),
        alpha[:, -edge_inset_px:].flatten(),
    ])
    bleed_pct = (edge_band > 30).sum() / edge_band.size * 100
    return PASS if bleed_pct <= max_bleed_pct else FAIL(bleed_pct)
```

### 12.4 L4 (overlay) gates

| check | class | severity |
|---|---|---|
| `backdrop_corner_check` (within ±5 of declared backdrop) | A — contract | FAIL |
| `effect_density` (5–35% non-backdrop coverage) | A — contract | FAIL |
| `effect_pattern_match` (declared effect_id matches CLIP classification) | C — perceptual | WARN |

### 12.5 Composite (final panel) gates

| check | class | severity |
|---|---|---|
| `archetype_compliance` (iyashikei.yaml qa_gates: negative space %, eye-flow, forbidden grammar) | mixed A/B/C — split per gate | per-gate severity |
| `seam_check` (no visible cutout artifacts at paste boundaries via edge-detection density) | B — heuristic | WARN |
| `lettering_safe_zones_clear` (bubble paste zones don't conflict with composited subjects) | A — contract | FAIL |
| `lighting_rig_coherence` (§14.B.1 — 7-axis per §6.9) | C — perceptual (will mature toward A as detectors stabilize) | WARN (advisory V4; FAIL by axis as calibrated) |

### 12.6 What the validators output

Each validator returns a structured `ValidationResult`:

```python
@dataclass
class ValidationResult:
    check_id: str                # e.g., "backdrop_corner_check"
    class_: Literal["A", "B", "C", "D"]
    severity: Literal["FAIL", "WARN", "SCORE"]
    passed: bool
    score: float                 # 0.0 = perfect; 1.0 = worst (for SCORE/WARN; FAIL is binary)
    evidence: dict               # e.g., {"corner_RGBs": [(254,253,251), (10,10,12), ...]}
    remediation_hint: str        # e.g., "Re-render with explicit '#FFFFFF NO COLOR' clause"
```

Only class-A FAIL results halt the pipeline. Class B/C/D results aggregate into `qa_review_queue.yaml` for operator triage.

---

## 13. Migration Plan (V3.1 → V4) — Validator-First

**Architectural principle (operator-directed, v0.3 critique):** _"Build the validator infrastructure BEFORE expanding archetypes. Validators are what transform the architecture from AI art workflow into contract-governed render system."_

Phases are reordered accordingly: validators are Phase B (was Phase C in v0.2). No archetype authoring proceeds until the validators can verify what's authored.

### 13.1 Phase A — Spec review (THIS doc, 2026-05-19)
Operator reviews v0.3. Approve §5 inheritance + §6.1-6.9 continuity + light-rig + cardinality controls + §8 inventories + §14 failure modes.

### 13.2 Phase B — Build validator infrastructure (THE FOUNDATION) — V1 = brutally deterministic only

Built **against the spec, not against any series authoring**. Per the v0.4 operator critique, V1 implements ONLY class-A contract validators (§12.0) — no model inference, no heuristic thresholds beyond fixed-rule numeric checks. Heuristic / perceptual / narrative scorers come in Phase B.2 after the deterministic core is stable.

**Phase B.1 — Deterministic core (V4 launch dependency):**

Three deterministic foundation scripts, in strict dependency order.

1. **`scripts/manga/compile_safe_zones.py`** (FIRST — foundational)
   - Inputs: §5 inheritance YAML (`base_contract` + `framing_contract` + `subject_contract` + `genre_modifier` + `archetype_exception`)
   - Output: flat compiled table (§5.7) as `config/manga/compiled/safe_zones.yaml`
   - **Implementation constraint:** fully deterministic. YAML loader + dict merge + override precedence. No AI, no heuristics, no thresholds. Pure data transformation.
   - **Tests:** golden snapshot — input YAML hash → output table hash must be stable across runs. Every cell in v0.3's compiled-view table (§5.7) must reproduce from inheritance composition.
   - Why first: §5 is the source of truth; the other validators read from `safe_zones.yaml`.

2. **`scripts/manga/contract_to_prompt_compiler.py`** (NEW v0.5 — Phase B.1 step 1.5)
   - Inputs: compiled safe_zone row + character_design + continuity_state + light_rig + style_state + layer type
   - Output: `PromptBundle(positive, negative, parameters, cache_key, provenance)` per §5.9
   - **Implementation constraint:** plain `str.format_map(...)` substitution. No LLM. No fuzzy fallbacks. Missing slot data is fatal.
   - **Tests:** golden snapshot — fixed input tuple → stable `(positive, negative)` sha256. Spot-check that injecting the §5.5 example contract produces the §5.5 example prompt suffix exactly.
   - Why between steps 1 and 2: `validate_layer.py` needs to verify renders against prompts that were generated; without a deterministic prompt compiler, the validator chases a moving target.

3. **`scripts/manga/validate_layer.py`** (THIRD — class-A gates from §12.1–§12.5)
   - Inputs: a rendered layer PNG + the layer's declared contract (subject_type, framing, genre, backdrop)
   - **Implements ONLY class-A gates in V1:**
     - `backdrop_corner_check` (4 corner RGB sample, ±5 tolerance)
     - `subject_safe_zone` (non-backdrop bbox vs compiled safe zone from compile_safe_zones.py output)
     - `subject_does_not_touch_edge` (5px clearance check)
     - `rembg_clean_alpha` (post-cutout alpha histogram bimodality)
     - `face_visible_for_face_archetypes` (face detection MAY use a model but threshold is a fixed 0.85; result is binary)
     - `negative_space_in_bbox` (pixel variance check, fixed threshold 0.15)
     - `effect_density` (non-backdrop pixel % within 5–35% range)
     - `lettering_safe_zones_clear` (bbox intersection — pure geometric)
   - Output: list of `ValidationResult` (per §12.6). ANY class-A FAIL halts cache write.
   - **Tests:** take the 3 layer-demo Mira renders (sage backdrop) — validator MUST flag them ALL as backdrop_corner_check FAIL. Take synthetic pure-white-bg image with subject in safe zone — validator MUST pass it. Take pure-white-bg with subject touching edge — validator MUST flag.

4. **`scripts/manga/validate_continuity_invariants.py`** (FOURTH — §6.3.A deterministic only)
   - Inputs: panel N continuity_state YAML + panel N+1 continuity_state YAML + archetype IDs
   - **Implements ONLY §6.3.A deterministic invariants in V1:**
     - scene_continuity (string equality + beat_type allow-list)
     - character_identity_continuity (character_design_hash equality)
     - prop_persistence (state ∈ prev_state ∪ reachable-in-1-step set)
     - gaze_target_validity (named target exists in scene/prop state)
     - temporal_continuity (next-step-in-cycle check)
     - expression_dial_bounded_delta (|Δ| ≤ bound by beat_type)
     - light_rig_within_scene (set membership)
   - Output: list of `ValidationResult` per §12.6. FAIL on any deterministic violation.
   - **§6.3.B heuristic invariants explicitly NOT implemented in V1** — they live in Phase B.2.
   - **Tests:** synthetic state pairs covering each invariant — each MUST catch the violation it targets, MUST NOT false-positive on valid pairs.

**Phase B.1 definition of done:** all four scripts in `scripts/manga/`, each with a pytest suite exercising pass AND fail cases. Run `pytest scripts/manga/tests/validators/` → green. NO Phase C authoring before B.1 is green.

**Phase B.2 — Heuristic / perceptual / narrative scorers (post-launch hardening):**

Built AFTER B.1 is stable and Phase C has produced enough real renders to calibrate against.
- `validate_layer.py` extended with class-B heuristics (palette_compliance, seam_check)
- `validate_layer.py` extended with class-C perceptual evaluators (identity_distance, pose_match, lighting_rig_coherence)
- `validate_continuity_invariants.py` extended with class-D narrative invariants (emotional_pendulation, tension_arc_coherence)
- Severity is `SCORE` or `WARN` until per-check calibration data shows < 3% false-positive rate; then per-check spec amendment may promote to `FAIL`.

Phase B.2 is NOT a V4 launch blocker. V4 ships with deterministic-only validation; advisory scorers add safety net incrementally.

### 13.3 Phase C — Schema authoring for ONE series (target: stillness_en_01)
Now the validators exist; authoring is verifiable.
- Author `stillness_en_01.scene_inventory.yaml` (4–6 scenes × ≤4 temporal variants × declared light_rig_id from §6.9 library)
- Author `stillness_en_01.object_inventory.yaml` (8–12 objects × state variants)
- Add `layer_render_contract` to all 19 iyashikei archetypes
- Add `character_pose_inventory` to Mira's character_design
- Hand-author `continuity_state/ep_001/*.yaml` from existing chapter_script
- Author `config/manga/light_rigs/iyashikei.yaml` (~8 rigs K01-K08)
- Every authored file passes its corresponding validator.

### 13.4 Phase D — Render pipeline scripts
- New: `scripts/manga/build_layer_render_prompts.py` — emits per-layer prompts from inventory + continuity_state + safe_zones; injects light_rig.prompt_clause
- New: `scripts/manga/render_layer_inventory.py` — renders the L0/L1/L2/L3/L4 cache for a series
- New: `scripts/manga/compose_layered_panel.py` — rembg + PIL composite using §10 math
- Modify: `build_panel_prompts_v3.py` → layer mode when archetype has `layer_render_contract`
- Modify: `queue_panel_renders.py` → dispatch layer-renders; route per §11 engine map
- Every render output passes `validate_layer.py` before entering cache; every panel composite passes the composite gates.

### 13.5 Phase E — Validate vs V3.1 baseline
Render `stillness_en_01 ep_001` via V4. Side-by-side vs V3.1 (currently rendering at PID 37394). Operator review.

### 13.6 Phase F — Catalog rollout
Apply V4 to all `stillness_press` iyashikei series. Author archetype catalogs for the other 7 top-priority genres (separate Phase 2 spec — `MANGA_LAYER_GENRE_EXTENSIONS_SPEC.md`).

### 13.7 What V3.1 in-flight today still ships
V3.1 single-engine re-render running now (PID 37394) ships as V3.1 — better than V3 (no cross-engine drift), worse than V4 (no identity lock, no layer reuse, no continuity invariants, no light-rig coherence). V3.1 is the operational fallback for archetypes V4 doesn't yet cover (§15.B).

### 13.8 Why this order matters (validator-first rationale)

Two failure modes that validator-first prevents:

**Without validators:** I author a `scene_inventory.yaml`, run the prompt builder, get rendered layers — and have no way to know if they're contract-compliant short of eyeballing the output. Errors compound silently. The system reverts to probabilistic prompting (better-than-V3.1 but not deterministic).

**With validators:** every authored input passes a gate before render; every rendered layer passes a gate before composite; every composite passes a gate before delivery. Errors are caught at the boundary they occur. The system is a contract-governed pipeline, which is the entire point of the spec.

---

## 14. Failure Modes & Recovery Strategy (NEW in v0.2)

Layered systems fail differently than monolithic systems. v0.1 had QA gates (§12) — what's missing is the **recovery contract** per failure class: detection method, fallback behavior, rerender policy, cache invalidation policy.

### 14.A Per-layer rendering failures

| failure | detection | fallback | rerender policy | cache invalidation |
|---|---|---|---|---|
| **A.1 Alpha fringing** (rembg leaves halo around subject silhouette) | histogram of alpha channel: bimodal gate (peaks at 0 and 255). If ≥10% of pixels fall in 50–200 alpha band, fringing detected. | retry rembg with `alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10`. If still fails, escalate to A.2. | retry up to 2 alternate rembg models per backdrop type (u2net → birefnet → silueta). If all fail, mark layer FAILED and queue manual review. | invalidate `<layer_id>` cache; keep `<scene_id>` cache. |
| **A.2 Backdrop violation** (corners not within ±5 of declared backdrop) | corner_check at QA gate §12.2/12.3 | rerender with hardened backdrop clause: `"PURE_WHITE_BACKGROUND_NO_SCENE_NO_SHADOW_HEX_FFFFFF_EXACTLY"` | retry up to 3× with progressively stricter backdrop clauses (rare in practice — usually a one-time prompt slip). | invalidate `<layer_id>` only. |
| **A.3 Subject touches edge** (non-backdrop bbox within 5px of canvas edge) | bbox-distance check at QA gate §12.2 | rerender with safe-zone clause re-emphasized + width/height reduction hint | retry up to 2×. If still fails, downgrade safe_zone by one tier (e.g., CU → CU_loose with 12.5% margin instead of 17.5%) and log. | invalidate `<layer_id>` only. |
| **A.4 Identity drift** (cosine > 0.55 from character reference) | embedding distance at QA gate §12.3 | rerender with stronger identity inputs (more PuLID weight; or LoRA strength bump from 0.7 → 0.9) | retry up to 3×. If still fails, escalate to manual review — character_design YAML may need refinement. | invalidate `<layer_id>` and all `<character_id>` cache entries (drift may be systemic). |
| **A.5 Pose-archetype mismatch** (character rendered standing when archetype declared sitting) | CLIP zero-shot pose detection vs archetype.subject_type at QA gate §12.3 | rerender with explicit pose clause prepended | retry up to 2×. If still fails, mark archetype + character_id pair UNRENDERABLE and downgrade panel to single-pass V3.1. | invalidate `<layer_id>` only. |
| **A.6 Rembg false-positive** (rembg removes part of the subject — e.g., a white sleeve disappears against white backdrop) | post-cutout, check that subject's expected color regions (per character_design) are present | re-cutout with alternative backdrop (white → black) and rerender | retry once on black backdrop; if fails, queue manual review. | invalidate `<layer_id>` only. |

### 14.B Cross-layer composition failures (detected at composite time)

| failure | detection | fallback | rerender policy | cache invalidation |
|---|---|---|---|---|
| **B.1 Lighting rig mismatch** (any of: direction, softness, color_temp, rim, ambient_bounce, atmospheric_diffusion, exposure — see §6.9) | 7-axis detector per §6.9: (i) direction via gradient analysis on L0 vs L2 shadow side; (ii) softness via shadow-edge falloff length; (iii) color_temp via white-balance estimation on highlights; (iv) rim_intensity via rim-region brightness vs body avg; (v) ambient_bounce via shadow-side color sampling; (vi) diffusion via global contrast / haze measure; (vii) exposure via histogram center. Any axis exceeding tolerance = mismatch. | rerender L2 with the FULL light_rig.prompt_clause re-injected (not just direction) | retry L2 up to 2×. If still fails: accept axis-by-axis (some axes are acceptable mismatches, e.g., exposure within 30% is fine; direction must match within 45°). Log per-axis. | invalidate `<L2_layer_id>` only; keep L0. |
| **B.2 Perspective mismatch** (L0 isometric overhead; L2 character rendered front-on) | declared archetype framing (insert/CU/MS/...) compared against detected L2 perspective via CLIP | rerender L2 with explicit perspective clause from archetype framing row | retry L2 up to 2×. | invalidate `<L2_layer_id>` only. |
| **B.3 Pose-scale mismatch** (character rendered at portrait scale but archetype's subject_placement_bbox calls for long-shot scale) | post-cutout-bbox vs archetype subject_zone — if cutout bbox > 2× the zone area or < 0.5× | rescale at composite time (acceptable for ±30%); rerender if outside that range | retry up to 2× with explicit framing clause | invalidate `<L2_layer_id>` only. |
| **B.4 Atmospheric overlay contamination** (steam L4 overlapping face L2 causes visual artifact — e.g., face features fade into steam) | post-composite saliency map; if L2-face-region saliency drops > 50% after L4 composite | reduce L4 opacity to 0.3 max in face region (per-pixel masking) | accept reduced opacity; no rerender needed | no invalidation. |
| **B.5 Seam visibility** (composite paste boundary visible — edge halo, sudden tone shift) | edge-detection across paste boundary; if edge density > scene mean × 2 | apply 1px alpha matting at composite boundary as remediation (NOT full feather — just edge-AA) | no rerender; remediation in composite step. | no invalidation. |

### 14.C Continuity failures (detected by §6.3 invariants)

| failure | detection | fallback | rerender policy | cache invalidation |
|---|---|---|---|---|
| **C.1 Gaze discontinuity** (panel N gaze at_cup; panel N+1 gaze at_camera with no transitional beat) | §6.3 gaze-continuity invariant | flag panel N+1 for chapter_script edit (add transitional beat OR change gaze) | no auto-rerender — requires chapter_script change. Escalate to writer. | no invalidation. |
| **C.2 Prop state regression** (cup_full in panel N, cup_empty in panel N+1, no drink-action panel between) | §6.3 prop continuity invariant | flag chapter_script for review — likely a continuity bug | no auto-rerender. | no invalidation. |
| **C.3 Emotional pendulation violation** (calm → peak_anxious in one beat for iyashikei) | §6.3 emotional invariant per iyashikei rules | flag for chapter_script edit (insert intermediate beat) | no auto-rerender. | no invalidation. |
| **C.4 Identity flip across panels** (Mira's hair color shifts; eye geometry shifts) | embed all L2 renders for same character in episode; cluster — if outlier > 0.55 distance | rerender outlier L2 with stronger identity inputs | retry up to 3× | invalidate the outlier `<layer_id>`. |

### 14.D Cache invalidation triggers (across the system)

| trigger | invalidate |
|---|---|
| `character_design.yaml` edit | all `<L2_layer_id>` for that character_id |
| `scene_inventory.yaml` edit | all `<L0_layer_id>` and `<L1_layer_id>` for that scene_id |
| `object_inventory.yaml` edit | all `<L3_layer_id>` for that object_id |
| `iyashikei.yaml` archetype edit | nothing automatic (archetype changes affect composition, not layer renders) BUT next composite for that archetype rebuilds |
| spec (this doc) edit affecting §5 or §6 | regenerate `scripts/manga/compile_safe_zones.py` output; recompute continuity_state hashes |

### 14.E Manual-review queue

Some failures (A.4 systemic identity drift, C.1–C.3 chapter_script issues) require human intervention. The pipeline writes them to `artifacts/manga/<series>/qa_review_queue.yaml` with full failure context. Operator reviews and either approves a downgrade-to-V3.1 panel OR queues a chapter_script revision.

### 14.F Failure budget & recovery semantics (NEW in v0.5 — orchestration contract above the validator contract)

§14.A–§14.E define **per-failure** detection and single-retry recovery. v0.5 adds the **orchestration contract** that governs what happens when retries are exhausted, when failures pile up, and when the pipeline must halt vs ship-with-degradation.

Without this, the validators detect failures but the orchestrator has no exit condition. At catalog scale (800 series × ~300 panels = ~240,000 panels), even a 1% terminal failure rate is 2,400 panels in limbo. The system must declare what happens to them.

**Path:** `config/manga/orchestration/failure_policy.yaml` — series-overridable defaults.

```yaml
schema_version: "1.0.0"

failure_policy:
  # ── per-layer retry budget ───────────────────────────────────────────
  per_layer:
    max_attempts: 3                          # 1 initial + 2 retries
    cooldown_seconds: 60                     # spacing between retries
    on_exhaust: "mark_layer_unbuildable"
    escalation: "queue_for_step_down"        # → try alternate engine; → try alternate cutout model; → manual

  # ── per-panel retry budget ───────────────────────────────────────────
  per_panel:
    max_attempts: 5                          # across all layers + composite gates
    on_exhaust:                              # per-series override-able
      default: "ship_v31_fallback"           # render the panel V3.1-single-pass and ship it
      alternatives:
        - "hold_for_operator_review"         # write to qa_review_queue.yaml; episode waits
        - "skip_panel"                       # ship the episode minus this panel (only if archetype allows omission)
        - "ship_v3_fallback"                 # absolute last resort — original V3 FLUX single-pass

  # ── per-episode thresholds ───────────────────────────────────────────
  per_episode:
    failure_rate_threshold_pct: 3            # if > 3% of panels in an episode fail terminally, escalate
    on_threshold_exceeded: "halt_dispatch"   # stop rendering more layers; ship what's complete + log held panels
    on_partial_completion: "ship_completable_panels"   # don't block the whole episode for 1 bad panel
    min_panels_for_episode_ship_pct: 90      # ≥90% of panels must succeed to ship the episode at all

  # ── per-series cumulative thresholds ─────────────────────────────────
  per_series:
    cumulative_failure_threshold_pct: 5      # if > 5% of panels across all shipped episodes failed terminally, pause
    on_threshold_exceeded: "pause_series_and_alert_operator"
    cumulative_window: "rolling_3_episodes"

  # ── fallback hierarchy (top wins) ────────────────────────────────────
  fallback_hierarchy:
    - "V4_layered_full"                      # the goal — all layers pass class-A
    - "V4_layered_partial"                   # composite ships even if class-B/C/D scorers warn (V4 launch reality)
    - "V3.1_single_pass_qwen"                # single-engine fallback (today's running dispatcher)
    - "V3_single_pass_flux"                  # operational floor — accepted as last-resort visible output
    - "hold_for_operator_review"             # nothing ships; queued for human

  # ── decision authority ───────────────────────────────────────────────
  decision_authority:
    default_actor: "automated_orchestrator"
    operator_override_required_for:
      - "pause_series_and_alert_operator"    # only operator can resume
      - "ship_v3_fallback"                   # explicit ack required
      - "skip_panel"                         # archetype-by-archetype operator approval list in series config

  # ── per-series overrides ─────────────────────────────────────────────
  series_overrides:
    # Format: <series_id>: { ... policy fields ... }
    stillness_en_01:
      per_panel.on_exhaust.default: "hold_for_operator_review"   # iyashikei flagship — quality > velocity
    # other series default to the global policy
```

**Recovery semantics — flow:**

```
panel render attempt
   ↓
layer L_i renders
   ↓
validate_layer.py
   ↓
   FAIL? → retry_layer (up to max_attempts per_layer)
              ↓ exhausted?
              → mark_layer_unbuildable
              → escalate per per_layer.escalation
                  ↓ (alternate engine / cutout) failed?
                  → ESCALATE to panel-level fallback
   PASS? → next layer

(after all layers attempt)
   ↓
composite gates §12.5
   ↓
   FAIL? → retry_panel (up to max_attempts per_panel)
              ↓ exhausted?
              → apply per_panel.on_exhaust policy for this series
                  ├─ ship_v31_fallback → re-render whole panel single-pass V3.1; mark provenance: "v31_fallback"; pass to episode shipper
                  ├─ hold_for_operator_review → write to qa_review_queue; episode WAITS on this panel
                  ├─ skip_panel → mark panel skipped; episode ships without it (archetype permission required)
                  └─ ship_v3_fallback → last resort, requires operator override

(after all panels in episode resolved)
   ↓
per_episode threshold check
   ↓
   failure_rate > 3%? → halt_dispatch, alert operator
   completion_rate < 90%? → episode can't ship, hold whole episode

(after episode shipped — bookkeeping)
   ↓
per_series cumulative check
   ↓
   cumulative > 5% over rolling 3 episodes? → pause_series, alert operator
```

**Provenance stamped on every shipped panel:**
```yaml
panel_provenance:
  pipeline: "V4_layered_full" | "V4_layered_partial" | "V3.1_single_pass_qwen" | ...
  failure_count: 0..max_attempts
  failed_class_a_checks: []      # any class-A FAIL events that were eventually resolved
  fallback_chain: []             # the sequence of attempts that led to the final output
```

This provenance feeds `render_telemetry/<episode>.yaml` (§6.11) and surfaces per-panel quality tier for operator dashboards.

**Halt conditions (when the orchestrator stops on its own):**
- per_episode failure_rate > 3% (transient — episode-scoped)
- per_series cumulative > 5% over rolling 3 episodes (systemic — series-scoped)
- repeated identity-distance failures across > 3 panels in one session (signals a character_design problem, not a render problem)
- backdrop-corner-check fails > 10% of first attempts within one episode (signals systemic prompt-compiler / template issue)

In all halt cases: structured incident report → `artifacts/manga/<series>/incidents/<timestamp>.yaml` + operator alert. NO auto-resume; operator must explicitly clear.

**What this gives the orchestrator:**
A finite, declarative state machine for "what happens when V4 doesn't work." Validators detect; this policy decides. Together they form the complete recovery contract.

### 14.F.7 Hold-queue drain mechanism (NEW in v0.5.1 — `hold` must release)

Without a drain mechanism, `hold_for_operator_review` is a pressure valve that doesn't release. At catalog scale a hold queue grows unboundedly. v0.5.1 declares the drain contract.

```yaml
hold_queue_drain:
  # ── review SLA (the human cadence) ───────────────────────────────────
  review_sla:
    target_review_window_hours: 48           # operator commits to draining within 48h of entry
    measurement: "time from hold-queue write to operator action (review_resolve OR review_escalate)"
    breach_alert_threshold_hours: 72         # if any item sits > 72h unactioned, alert
    breach_alert_channel: "operator_dashboard + email"

  # ── auto-escalation (the safety valve) ───────────────────────────────
  auto_escalation:
    per_series:
      max_hold_items_before_pause: 10        # if a single series accumulates > 10 hold items, pause series dispatch
      action: "pause_series_dispatch + alert_operator"
    per_episode:
      max_hold_items_before_episode_block: 3 # if an in-flight episode has > 3 hold items, block episode ship
      action: "do_not_ship_episode + queue_full_episode_review"
    catalog_wide:
      max_hold_items_before_global_alert: 50 # catalog-wide hold count > 50 = systemic problem
      action: "halt_all_dispatch + incident_report + operator_alert"

  # ── operator actions on a hold item ──────────────────────────────────
  operator_resolution_actions:
    - "approve_fallback_v31"            # accept the V3.1 fallback and ship
    - "approve_fallback_v3"             # accept the V3 fallback (last resort)
    - "approve_skip_panel"              # archetype permits omission; ship episode without it
    - "request_chapter_script_revision" # routes to writer with structured failure record
    - "request_character_design_revision" # systemic identity drift; routes to character design owner
    - "queue_for_manual_re-render"      # human-supervised single-pass render with operator-edited prompt
    - "defer_to_next_episode"           # bookmark for re-attempt with updated cache/state
  
  # ── reporting (what the operator sees) ───────────────────────────────
  hold_queue_report:
    path: "artifacts/manga/<series>/hold_queue/<timestamp>.yaml"
    fields: [panel_id, episode_id, failure_classes, attempts, age_hours, suggested_action, telemetry_summary]
    sort_default: "age_hours DESC"     # oldest items surface first
    rollup_frequency: "every 12h or on threshold breach (whichever first)"
```

**Default series behavior:** any series's `per_panel.on_exhaust` set to `hold_for_operator_review` (e.g., `stillness_en_01`) MUST have an operator owner assigned in `series_overrides`; otherwise the orchestrator refuses to enable that fallback.

**Catalog-scale guarantee:** at the global `max_hold_items_before_global_alert` threshold, ALL dispatch halts. The system never quietly accumulates failures past the threshold.

---

## 15. Frontier Map (replaces v0.1 "Open Questions")

Organized into 4 buckets so the boundary of "what V4 supports" is unambiguous.

### 15.A Launch blockers (V4 cannot ship without these) — declared as acceptance criteria

Each blocker is a testable pass/fail gate, not a narrative goal. V4 ships when all five pass; V4 does NOT ship when any one fails.

#### 15.A.1 Identity lock for L2 — ACCEPTANCE CRITERIA

**Pass requires all of:**
- One of: (i) PuLID-FaceNet operational (EVA-CLIP download issue resolved) OR (ii) per-character LoRA trained on `ai-toolkit` for at least the `stillness_en_01` protagonist (Mira Aoki)
- Synthetic test: across N=30 panels rendered for character X, **embedding cosine distance ≤ 0.55 on 100% of panels** (per §12.3 `identity_distance` gate, class-C threshold)
- **Hash-equality is necessary but NOT sufficient.** Per §6.3.A amendment, when PuLID and LoRA are both inactive, `character_design_hash = axes_hash` only — same hash does not guarantee same rendered face. §15.A.2 explicitly requires one of {PuLID-active, per-character-LoRA-trained} as a precondition for this gate to be evaluable. The structural validator (§6.3.A) can still pass; the perceptual gate (this §15.A.2) cannot pass without an identity-locking engine.
- First-attempt success rate ≥ 95% (≤ 5% requiring retry to clear the distance gate)
- After one retry, success rate ≥ 99%
- Operator manual review: random sample of 5 panels — "is this the same character?" → **5/5 yes** required

**Test path:** `scripts/manga/tests/validators/test_identity_lock_acceptance.py` (Phase B.2)
**Fallback if unmet:** V4 cannot launch with character_id X. Either fix the engine OR remove that character from V4 scope and ship via V3.1.

#### 15.A.2 Extraction reliability — ACCEPTANCE CRITERIA (UPDATED v0.6 from "backdrop reliability")

**v0.5.1 had:** backdrop_corner_check pass rate ≥95% on first render attempt. **Empirical B-test 2026-05-19 invalidated this premise** — Qwen-Image renders scenes, not isolated subjects. The acceptance criterion shifts from render-time backdrop purity to post-cutout extraction quality.

**Pass requires all of (post-cutout RGBA, per §12.3):**
- `rembg_clean_alpha`: gray-band (50-200 alpha) ≤ 3% with `alpha_matting=True` (relaxed from 1% — scene renders have softer silhouettes than synthetic-white renders)
- `character_extraction_coverage`: post-cutout opaque bbox area ≥ `character_extraction_coverage_min_pct × declared_safe_zone_area` (proves the character wasn't eaten by the cutout)
- `background_bleed_check`: alpha ≤ 5% on the 20px-inward edge frame (proves the background scene was removed even though it wasn't white)
- L1/L3 object renders (still simple backdrops): pass §9.2 contract on ≥95% of first attempts
- Operator manual review: random sample of 5 cutouts inspected for: (i) character silhouette clean, (ii) attached props match `keep_attached_props` declaration, (iii) no scene fragments bleed in — **5/5 clean** required

**Test path:** `scripts/manga/tests/validators/test_extraction_reliability_acceptance.py` (Phase B.2)
**Fallback if unmet for an archetype:** try alternate `cutout_policy.model` (u2net_human_seg ↔ birefnet-portrait). If both fail for an archetype, that archetype falls back to V3.1 single-pass.

#### 15.A.3 Layer QA validator stability — ACCEPTANCE CRITERIA

**Pass requires all of:**
- `scripts/manga/validate_layer.py` exists and `pytest scripts/manga/tests/validators/test_validate_layer.py` → green
- All class-A checks from §12.1–§12.5 implemented; class-A FAIL severity actually halts cache write
- Synthetic test fixtures cover both pass AND fail cases for each class-A check
- Validator runs in ≤ 2 seconds per layer on Pearl Star CPU (no GPU dependency for V1 class-A)
- False-positive rate ≤ 1% across a 100-panel pilot (i.e., no more than 1 valid render flagged as FAIL)

**Test path:** included in the validator's own test suite
**Fallback if unmet:** V4 cannot launch — no validator means no contract enforcement; pipeline reverts to V3.1 with no gate.

#### 15.A.4 Continuity invariant validator stability — ACCEPTANCE CRITERIA

**Pass requires all of:**
- `scripts/manga/validate_continuity_invariants.py` exists and `pytest scripts/manga/tests/validators/test_continuity_invariants.py` → green
- All §6.3.A deterministic invariants implemented; class-A FAIL halts panel build
- All §6.3.B heuristic invariants implemented at SCORE/WARN severity (advisory only at V4)
- Synthetic test fixtures cover each invariant pass + fail case
- Validator runs in ≤ 500 ms per panel-pair on Pearl Star CPU
- False-positive rate ≤ 0.5% on 100-panel pilot for deterministic invariants

**Fallback if unmet:** V4 launches without continuity invariant gate; sequence coherence is operator-reviewed; halt-condition (§14.F) lowered to compensate.

#### 15.A.5 Contract-to-prompt compiler — ACCEPTANCE CRITERIA (NEW in v0.5)

**Pass requires all of:**
- `scripts/manga/contract_to_prompt_compiler.py` exists and `pytest scripts/manga/tests/validators/test_contract_to_prompt_compiler.py` → green
- All L0/L1/L2/L3/L4 templates exist in `config/manga/prompt_templates/`
- Slot vocabulary (`config/manga/prompt_templates/SLOTS.md`) complete; every slot referenced in any template is documented + has a source binding in §5.9 inputs
- Golden-snapshot test: fixed (compiled_safe_zone_row, character_design, continuity_state, light_rig, style_state) → stable `(positive, negative)` sha256 across runs
- Missing-slot test: removing any required slot value causes fatal compiler exit (no silent empty-string fallback)
- Spot-check: §5.5 example contract produces §5.5 example prompt suffix exactly (including the literal "17%" and "15%" values traced through inheritance)

**Fallback if unmet:** V4 cannot launch — without a deterministic prompt compiler, the contract scaffolding has no execution path. Pipeline reverts to V3.1 (which doesn't need contracts).

#### 15.A.6 Composite-level operator review — ACCEPTANCE CRITERIA (NEW v0.5.1)

The first five gates test layers in isolation; this gate tests the assembled composite. Layer-pass is NOT composite-pass — passing all class-A gates per layer doesn't prove the layers integrate well.

**Pass requires all of:**
- A **representative panel set** of ≥20 fully-composited panels rendered via the V4 pipeline for at least one series (target: `stillness_en_01 ep_001`)
- Coverage requirements within the set:
  - ≥1 panel per archetype that the series uses in ep_001 (typically 8–12 of iyashikei's 19 archetypes)
  - ≥3 panels showing the same character in different emotional states (continuity_state evolution visible)
  - ≥1 panel from each scene declared in `scene_inventory.yaml`
  - ≥1 panel using each light_rig declared in `light_rigs/iyashikei.yaml`
- Operator binary review per panel: "is this a shippable manga panel?" → **≥18 of 20 yes (≥90%)**
- Operator open-text review surfaces no systemic visual artifact (e.g., "every panel has a 2px halo around Mira's hair" would block even if 90% are "shippable")
- Side-by-side comparison against ≥5 V3.1 single-pass renders of the same panel_ids — **V4 must be visually equal-or-better on ≥4 of 5** (V4 is allowed to lose 1 panel; if it loses ≥2, the pipeline isn't an upgrade)
- Composite-level class-A gates (§12.5: lettering_safe_zones_clear, archetype_compliance for deterministic sub-gates) pass on 100% of the set

**Test path:** `artifacts/manga/<series>/v4_acceptance_review/<timestamp>/` — composited panels + filled review template
**Manual gate:** this one cannot be automated. Operator review IS the gate.
**Fallback if unmet:** V4 does not launch for that archetype set / series. Diagnose which panels failed, iterate on prompt templates / continuity_state / light_rig, re-run review. Catalog rollout (§13.6) does not begin until composite review passes for `stillness_en_01`.

#### 15.A.7 Per-axis `subject_does_not_touch_edge` — V4.1 design item (NEW 2026-05-20 post-B-test-#4)

**Empirical finding (B-test #1–#4):** CU character portraits *naturally* extend to the right edge (arm) and bottom edge (shoulders/chest crop). The current `subject_does_not_touch_edge` validator applies `margin_min_pct_all_sides` uniformly to all 4 axes, which causes face-only CU archetypes (`character_quiet_face`, `character_face_micro_tension`) to FAIL on bottom + right edges even when the render is otherwise pristine — no scene context, identity on-target, micro-tension expression rendered correctly, alpha_matting cutout at 0.65% gray-band.

The architectural fix is per-axis edge tolerance, matching the pattern already used by `archetype_exception=window_light_threshold` (which sets `subject_must_not_touch_edge: false` for intentional left-edge bleed).

**V4.1 schema addition:**

```yaml
# in compiled safe_zone row OR archetype_exception
subject_must_not_touch_edge_axes:
  top: true       # forehead must have clearance
  bottom: false   # CU portraits naturally crop at shoulders
  left: true      # face does not bleed
  right: false    # arm naturally extends past frame in CU portrait composition
```

`validate_layer.py:check_subject_does_not_touch_edge` reads the per-axis dict instead of the all-or-nothing boolean.

**Why deferred from V4:** the change touches `validate_layer.py` (~40 lines), `iyashikei.scene_context.yaml` per archetype, `archetype_exception.yaml`, plus tests. Worth doing properly. The 8 face-only panels in `ep_001` carry `render_deferred: true` with `deferral_reason` pointing to this section until V4.1 lands.

### 15.B Deferred launch constraints (V4 EXPLICITLY unsupported — `unsupported ≠ unresolved`)

These are decisions, not gaps. Out-of-scope intentionally.

1. **Multi-character layered composites — the cliff.** `shared_meal_table_medium` and any other 2+ character archetype falls back to single-pass V3.1 rendering for V4. The deferral is not a small gap. The reason: multi-character complexity is **multiplicative, not additive**. Single-character V4 requires (pose × emotional × hand × gaze × dial × temporal × rig). Two-character composites add:
   - **Relational state.** `character_A.gaze.at_named_character_B` requires character_B to actually exist as a named entity in the L2 layer, not just appear at coordinate (x,y). Today's continuity_state schema has gaze enum but no relational target validator.
   - **Eye-line geometry.** If A is looking at B, the rendered angle of A's gaze must terminate at B's actual rendered head position post-composite. This is a geometric constraint the renderer doesn't know about.
   - **Pose interdependence.** A reaching for B's hand requires both renders to agree on contact geometry. Independent layer renders won't unless they're conditioned on each other (which is a circular dependency).
   - **Overlap semantics.** Z-order between A and B is dynamic per archetype, not static (A passes in front of B in one panel; B in front of A in the next). The flat L2 namespace can't express it without sub-layering.
   - **Shared light rig.** §6.9 handles this — both characters inherit the scene's light_rig — but it requires the QA gate to validate BOTH L2 renders, not one.
   - **Touch / contact continuity.** Hands touching, shoulders brushing — pixel-level boundary must be consistent across panels (no "fingers visibly separate, then visibly joined, then visibly separate" in three consecutive panels).
   - **Emotional co-regulation.** If A is calming B, their `emotional_state` is COUPLED — not independent. The continuity invariant system has no concept of paired-state dynamics yet.

   **Phase-2 architectural sketch (for `MANGA_MULTI_CHARACTER_LAYER_SPEC.md`):** introduce a `relational_state` block above `character_state` in continuity_state; introduce a `composite_geometry` block (eye-line vectors, contact points) as image-domain metadata; introduce a paired-render pipeline that conditions L2_charA on L2_charB pose; treat the pair as one composite unit (`L2_pair_id`) for caching.

   **Why V4 cannot include this:** it's not "spec a few more rules and you're done." It's a separate architectural workstream of comparable size to V4 itself. Trying to bolt it into V4 would either (a) bog V4 down by 6+ weeks of architectural design, or (b) ship a half-built system that produces visibly broken multi-character panels. Single-pass V3.1 fallback is the correct interim. Phase 2 is the proper next workstream.
2. **Action / motion archetypes.** Shonen, mecha, fantasy_adventure combat archetypes with intentional edge-bleed, speed lines, impact effects defer to Phase 2 alongside those genres' archetype catalogs.
3. **Locale-aware signage.** Café signs, book covers, magazine titles visible in scenes — V4 renders English-only L0; per-locale variants defer to Phase 2.
4. **Pose-interdependent panels.** Two characters reaching for the same object, eyes meeting, hands touching — V4 single-passes these.
5. **B&W iyashikei register.** Mushishi-style sumi-e rendering — future `iyashikei_bw.yaml` template, separate spec.

### 15.C Research tracks (require experimentation before they're spec-able)

1. **Pose atlas auto-generation.** Today: `character_pose_inventory` is hand-authored. Goal: derive the required pose set automatically from `subject_type` declarations across a series's archetypes. Research questions: how many poses per character on average? Is there a universal base set across all iyashikei series?
2. **Semantic continuity inference.** Today: continuity_state must be hand-authored per panel. Goal: infer it from chapter_script.yaml using an LLM (Pearl_Star qwen-instruct). Research questions: what's the inference accuracy? What's the operator override cost?
3. **Adaptive safe-zone inference.** Today: safe zones are fixed-percentage rules from §5. Goal: per-archetype, learn the actual safe zone empirically from successful renders. Research questions: do the §5 defaults hold up across genres? Where do they fail?
4. **Lighting coherence detector.** §14.B.1 requires detecting lighting direction mismatch. Today: no such detector exists. Research questions: which models do this well? Cost per panel?
5. **Pose transition grammar.** §6.3 invariants enforce gross continuity. Sub-question: are there pose-specific transition rules? (e.g., "sitting → standing" needs 1 transitional beat; "sitting → reaching" can be direct).

6. **Spec gravity (document partition at scale).** This spec is approaching the threshold where one document tries to serve both implementation and theory readers. **v0.5.1 trip-wire (initial commitment):** when the spec reaches **1900 lines**, partition is required before next material amendment.

   **v0.6 amendment (operator-directed 2026-05-19, post-B-test):** trip-wire moved from "before next amendment" to **"before Phase D begins"**. Rationale: the 1900-line threshold fired during active architectural convergence (Path B pivot), not cruft accumulation. Splitting mid-build interrupts the most productive phase for a maintenance task that can wait. Phase D (operator-review of V4 panels vs V3.1 baseline) is when humans actively reference the spec as ground truth — that's when the partition earns its keep. **New trigger:** spec MUST be partitioned before Phase D start; target line budget **≤ 2100 lines** before partition (gives headroom for B-test-#2 amendment + minor follow-ups without further drift).

   **Current debt:** as of v0.6 amendment, spec stands at ~2000 lines, over the original 1900 trip-wire. Partition deferred. Tracked in this section.

   At partition time, split into two artifacts:
   - **`MANGA_LAYER_IMPLEMENTATION_CORE.md`** — only executable invariants, schemas, validator semantics, cache rules, composition rules, dispatch rules. Pure operational substrate. Stable; rare amendments.
   - **`MANGA_LAYER_THEORY_FRONTIER.md`** — architectural framing, research tracks, philosophical decisions (image-first boundary, constraint-solver bridge, world-model trajectory), future unlocks. Living document; frequent updates.
   - Cross-linked by section. Implementation reader does not need theory; theory reader does not need every validator detail. Threshold rule: if Phase C inventory authors find themselves grep-bouncing through theory sections to find executable rules, partition.

7. **Ontology hardening risk.** The enums (`emotional_state`, `posture`, `gaze`, `hand_state`, `prop_evolution`, light_rig taxonomy, archetype families) constrain chaos, which is good. But over time, they risk **calcifying into hidden storytelling-grammar assumptions** — the ontology starts shaping what stories CAN be told rather than reflecting stories being told.
   - Iyashikei is a forgiving stress test: small vocabularies, slow pacing, internal-focus. The current enums fit.
   - Action genres, ensemble casts, branching narratives, cross-cultural stories may need vocabulary EXTENSIONS the current ontology forecloses (e.g., `emotional_state` has no `betrayal_recognition` or `tactical_focus`; `gaze` has no `combat_target_lock`).
   - **Mitigation:** before each genre rollout (per §13.6), audit the ontology against ≥3 bestseller exemplars in that genre and explicitly approve additions/deprecations. The enum is a contract, not a frozen truth.
   - **Detection signal:** if writers start using "Other" / freeform fields more than rare-edge-case rates (~5%), the ontology is constraining the work and needs revision.
   - Not actionable in V4 (iyashikei-only). Logged for Phase 2 onward.

### 15.D Future unlocks (strategic upside; not part of V4)

1. **Motion manga / video derivatives.** L0/L2 separation unlocks parallax_BG, eye_blink animation, steam_motion, breathing micro-animation, rack-focus mask — all without rerendering panels. Reserve namespace `A0–A9` (§4.6).
2. **VN-style storytelling.** Same architecture supports visual-novel branching: same scene_inventory + character_pose_atlas + multiple chapter_script branches = multi-route narrative without combinatorial render cost.
3. **Reusable cinematic grammar.** Once `subject_placement_bbox` + `eye_flow_anchor` + safe-zone inheritance + continuity_state are stable, the system encodes a **portable visual grammar** that translates across genres. A camera-system extension (lens, focus, parallax) becomes feasible.
4. **Persistent cinematographic world model.** The end-state architectural target. Each series accumulates: a world (L0 scene inventory), a cast (L2 character roster with pose atlases), a prop set (L3 object inventory with state variants), a continuity history (panel-by-panel continuity_state). Future episodes write into the same world model. The pipeline stops being "image generation" and starts being **persistent narrative world simulation**. This is the strategic bridge from "manga catalog" to "studio cinematic pipeline."

5. **The constraint-solver inversion (the next architectural shift after V4).** v0.3 takes the system from "prompt-based generation" to "contract-governed rendering." The next inversion is from "contract-governed rendering" to "constraint-satisfaction-based rendering." Sketch:

   ```
   render_intent             (operator declares what they want — high-level)
       ↓
   contract_resolution       (system resolves intent against all contracts: safe_zone × continuity × engine × failure-recovery × budget)
       ↓
   constraint_solver         (system FINDS a feasible assignment of layer choices, cache hits, render strategies)
       ↓
   render_plan               (deterministic sequence of layer renders, validations, composites)
       ↓
   backend_dispatch          (executes the plan; diffusion model is one of several backends)
   ```

   Under this model, the operator doesn't say "build_layer_render_prompts.py then queue_panel_renders.py then compose_layered_panel.py." They say "render `stillness_en_01 ep_001`," and the constraint solver produces the optimal plan given current cache state, available engines, validator passes, and budget.

   Today's V4 is one rung below this — the human still orchestrates phase ordering. v0.3's spec is what makes the constraint solver eventually possible (typed contracts, validatable inputs, deterministic outputs, recoverable failures). Without v0.3's contract scaffolding, a constraint solver has nothing to satisfy.

   **Time horizon:** V5+. Not on the V4 roadmap. Listed here so the architecture's next inversion is named and won't surprise anyone.

---

## 16. Appendix A — Authority chain

This spec inherits from / extends:
- `docs/specs/MANGA_V3_3_MODEL_ROUTING_SPEC.md` (engine routing per archetype)
- `docs/specs/MANGA_V3_ROUTING_BY_GENRE.md` (catalog-wide routing matrix)
- `config/manga/panel_templates/iyashikei.yaml` (19 archetypes — extended with `layer_render_contract`)
- `config/manga/drawing_tradition_per_genre.yaml` (per-genre style axes — drives §5.5 overrides)
- `config/manga/character_design_axes.yaml` (12-axis individuation — drives L2 identity)
- `config/source_of_truth/manga_profiles/series/*.yaml` (per-series character_design — drives L2 prompts)
- `artifacts/research/iyashikei_panel_composition_study_2026-05-18.md` (the source of the 19 archetypes)
- `artifacts/research/full_content_audit.md` (800 high-confidence catalog scope)

This spec is referenced by (planned):
- `config/manga/panel_templates/iyashikei.yaml` (after schema extension)
- All future `panel_templates/<genre>.yaml`
- All future `<series>.scene_inventory.yaml` and `<series>.object_inventory.yaml`
- All future `<series>.continuity_state/<episode>/*.yaml`
- `scripts/manga/build_layer_render_prompts.py` (new)
- `scripts/manga/compose_layered_panel.py` (new)
- `scripts/manga/validate_layer.py` (new)
- `scripts/manga/validate_continuity_invariants.py` (new)
- `scripts/manga/compile_safe_zones.py` (new)

---

## 17. Appendix B — One-page operator summary

**The architectural reframe:** we stop "generating manga panels" and start **compiling manga panels from typed render assets under constrained contracts**. The model fulfills the contract or fails it — like a compiler.

**The four contracts:**

1. **Safe-zone contract** (§5) — hierarchical: `base → framing → subject → genre_modifier → archetype_exception`. Flat table is a compiled view; YAML inheritance is source of truth.

2. **Continuity contract** (§6) — `story_state → continuity_state → archetype → layers → composite`. Per-panel state record (emotional, posture, gaze, hand_state, prop_state, temporal). §6.3 invariants gate sequence coherence.

3. **Layer contract** (§3, §4, §7, §8) — 5 render layers (L0–L4) + reserved namespaces for semantic / export / ink / animation layers. Per-archetype layer composition map. Per-series inventories (character_pose, scene, object).

4. **Failure-recovery contract** (§14) — every failure class has detection / fallback / rerender / cache-invalidation policy. Layered systems fail differently; spec covers it.

**Compute economics:** ~82 unique renders per series compose to ~300 panels (3.7× vs V3.1's per-panel render). Continuity state inflates unique count vs v0.1's optimistic 10× — the trade buys semantic coherence.

**Launch blockers (§15.A):** identity lock (PuLID or LoRA), backdrop reliability, layer QA validator, continuity invariant validator. All four required before V4 ships.

**Explicitly unsupported in V4 (§15.B — not gaps, decisions):** multi-character layered composites, action archetypes, locale-aware signage, pose-interdependent panels, B&W iyashikei register. All fall back to single-pass V3.1.

**The strategic bridge:** once layers are stable image assets, motion manga, VN-style branching, reusable cinematic grammar, and persistent cinematographic world models all become feasible without architectural rework. Reserve namespace `A0–A9` for animation today (§4.6) so we don't repaint the bike-shed when the unlock arrives.

**Recommended next action (v0.3, validator-first):** operator approves §5, §6 (including §6.8 cardinality + §6.9 light rigs), §8, §13 reordered, §14 → I build Phase B's three validators (`compile_safe_zones.py` → `validate_layer.py` → `validate_continuity_invariants.py`) → only after validators pass synthetic tests do I author Phase C inventories for `stillness_en_01` → re-prompt Mira on pure-white backdrop → second layer demo passes validators end-to-end → V4 dispatcher ships ep_001 layered.

— end of spec v0.2 —
