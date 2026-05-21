# Manga Layer Render Contract Spec (v0.6.2 — V4 spec doc-split: §6 to MANGA_CONTINUITY_STATE_SPEC, §13 to MANGA_V4_MIGRATION_PLAN_ARCHIVE)

**Status:** AUTHORITY (v0.6.2 — doc-split executed 2026-05-20 per §15.C.6 trip-wire + operator directive)
**Author:** Pearl_Architect + Pearl_Int + Pearl_Research
**Schema version:** 0.6.2 (doc-split execution — §6 + §13 moved to sibling docs; cross-references updated)
**Changes since v0.6.1 (v0.6.2 — doc-split execution):**
- §6 SHORTENED — State Continuity Architecture extracted to standalone sibling spec `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md` v1.0.0. V4 spec retains a short §6 DOC-SPLIT MARKER. Honors §15.C.6 trip-wire + operator directive 2026-05-20 (target <1,800 lines). Continuity state will become a dual-architecture authority (V4 + V5) once PR #1258 lands.
- §13 ARCHIVED — V3.1-to-V4 validator-first migration plan extracted to standalone historical archive `docs/specs/MANGA_V4_MIGRATION_PLAN_ARCHIVE.md` v1.0.0. V4 spec retains a short §13 ARCHIVE MARKER. Plan is frozen as historical record; V5 will have its own acceptance criteria in `MANGA_V5_LAYERED_ARCHITECTURE.md` once that spec lands.
- Cross-references updated throughout §1.3, §2.4 "See:" line, §4.4, §7.2, §8.3, §12.3, §12.5, §14.B.1, §14.C, §14.D, §14.F, §15.A.1, §15.A.2, §15.A.4, §15.A.6, §15.B.1, §15.C.5, §15.C.7, §17 Appendix B.
- Header schema version bumped 0.6.1 → 0.6.2.
- Resulting V4 spec length: ~1,479 lines (was 2,032). Buffer below 1,800 trip-wire: ~321 lines.
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
| light_rig as scene-state metadata (sibling `MANGA_CONTINUITY_STATE_SPEC.md §9`) | actual lighting calculation / shadow casting |
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

**See:** §5 (Subject Safe Zones — applied to post-cutout subject bbox), sibling `MANGA_CONTINUITY_STATE_SPEC.md` (continuity state — formerly §6 of this spec), §8.1 (cutout contract), §12.3 (revised class-A gates).

### 4.4 L3 — Close objects (in-hand, on-table, in-foreground)

**Purpose:** Objects that are in the foreground plane with the character (cup in hand, phone on table, food on plate).

**Render contract:**
- Same as L1, but margin requirements relax to 10% (close foreground tolerates tight crop)
- Backdrop: pure white default; pure black for translucent (glass, steam)
- Z-order: paste AFTER L2 if the object occludes the character (cup blocking part of face); paste BEFORE L2 if character occludes the object (hand wrapping cup)
- **prop_state**-aware: same `object_id` at different states (cup_empty, cup_half, cup_full) = different cached renders (see sibling `MANGA_CONTINUITY_STATE_SPEC.md §5`)

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

## 6. State Continuity Architecture (DOC-SPLIT MARKER; full spec in standalone doc) — NEW v0.6.2

**The continuity-state architecture is documented in a standalone sibling spec:**
- **`docs/specs/MANGA_CONTINUITY_STATE_SPEC.md` v1.0.0** — canonical continuity-state schema, state vocabularies, deterministic + heuristic invariants (§3.A / §3.B), prompt-modification semantics, state-driven cache strategy, cardinality controls, light rigs (§9), cache telemetry, style-state continuity.

**Doc-split rationale:** Per §15.C.6 (1,900-line trip-wire) + operator directive 2026-05-20 (target <1,800), §6's 506 lines were extracted to a standalone authority. Continuity state will become a dual-architecture authority once V5 lands (PR #1258); a contract shared by two render architectures belongs in its own doc.

**V4-side sections that depend on continuity state (cross-references point to sibling doc):**
- §1.3 image-first boundary table
- §4.3 L2 (character)
- §7.2 archetype schema
- §8.3 object_inventory
- §12.3 L2 gates
- §12.5 composite gates
- §13 (now archived; see §13 archive marker)
- §14.B.1 / §14.C — failure tables citing continuity invariants
- §14.F — failure-budget provenance
- §15.A.1 / §15.A.2 / §15.A.4 — identity-lock + extraction + continuity acceptance gates
- §15.B.1 / §15.C.5 — multi-character cliff + pose-transition research tracks
- §16 Appendix A — Authority chain
- §17 Appendix B — Operator summary

**What V4 spec retains in §6:** only this marker. Sibling doc is source of truth.

<!-- Detailed continuity-state architecture (schema, state vocabularies, invariants,
     prompt-modification semantics, cache strategy, cardinality, light rigs, telemetry,
     style-state continuity) is in docs/specs/MANGA_CONTINUITY_STATE_SPEC.md.
     V4 spec retains this short doc-split marker only (per §15.C.6 + operator
     directive 2026-05-20). -->

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
- `character_pose_inventory:` — list of poses (front-portrait, side-portrait, hand-only, hands-and-arms-on-cup, full-body-walking, full-body-sitting, etc.) cross-referenced with continuity_state vocabularies from sibling `MANGA_CONTINUITY_STATE_SPEC.md §2`.
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
    state_variants_required: [empty, half, full]   # drives sibling MANGA_CONTINUITY_STATE_SPEC.md §5
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
| `continuity_invariants_deterministic` (sibling `MANGA_CONTINUITY_STATE_SPEC.md §3.A`) | A — contract | FAIL |
| `continuity_invariants_heuristic` (sibling `MANGA_CONTINUITY_STATE_SPEC.md §3.B`) | D — narrative | SCORE |

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
| `lighting_rig_coherence` (§14.B.1 — 7-axis per sibling `MANGA_CONTINUITY_STATE_SPEC.md §9`) | C — perceptual (will mature toward A as detectors stabilize) | WARN (advisory V4; FAIL by axis as calibrated) |

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

## 13. Migration Plan V3.1 → V4 (ARCHIVE MARKER; full plan in standalone doc) — NEW v0.6.2

**The V3.1-to-V4 validator-first migration plan is archived in a standalone sibling spec:**
- **`docs/specs/MANGA_V4_MIGRATION_PLAN_ARCHIVE.md` v1.0.0** — Phase A spec review, Phase B.1 deterministic validator core + Phase B.2 hardening, Phase C schema authoring, Phase D render pipeline, Phase E baseline comparison, Phase F catalog rollout, V3.1 in-flight handling, validator-first rationale.

**Archive rationale:** Phase D (former §13.4 — render pipeline scripts) is set to be superseded by the V5 orchestrator (`render_v5_episode.py`) once PR #1258 lands — V5 replaces V4's `build_layer_render_prompts.py` + `render_layer_inventory.py` + `compose_layered_panel.py`. The rest of the plan remains true as a historical record but is no longer the active migration plan; V5 will have its own acceptance criteria in `MANGA_V5_LAYERED_ARCHITECTURE.md` once that spec lands.

**V4-side sections that still reference §13 (cross-references point to sibling archive):**
- §15.A.6 (V4 composite review gate) cites former §13.6 catalog-rollout precondition
- §15.C.7 (ontology hardening) cites former §13.6 per-genre rollout audit
- §17 Appendix B operator summary references former "§13 reordered"

**What V4 spec retains in §13:** only this marker. Sibling archive preserves the validator-first phase plan as historical authority.

<!-- Detailed V3.1-to-V4 migration plan (Phase A spec review, Phase B.1 deterministic
     validator core + Phase B.2 hardening, Phase C schema authoring, Phase D render
     pipeline, Phase E baseline comparison, Phase F catalog rollout, V3.1 in-flight
     handling, validator-first rationale) is in
     docs/specs/MANGA_V4_MIGRATION_PLAN_ARCHIVE.md. V4 spec retains this short
     archive marker only (per §15.C.6 + operator directive 2026-05-20). -->

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
| **B.1 Lighting rig mismatch** (any of: direction, softness, color_temp, rim, ambient_bounce, atmospheric_diffusion, exposure — see sibling `MANGA_CONTINUITY_STATE_SPEC.md §9`) | 7-axis detector per sibling `MANGA_CONTINUITY_STATE_SPEC.md §9`: (i) direction via gradient analysis on L0 vs L2 shadow side; (ii) softness via shadow-edge falloff length; (iii) color_temp via white-balance estimation on highlights; (iv) rim_intensity via rim-region brightness vs body avg; (v) ambient_bounce via shadow-side color sampling; (vi) diffusion via global contrast / haze measure; (vii) exposure via histogram center. Any axis exceeding tolerance = mismatch. | rerender L2 with the FULL light_rig.prompt_clause re-injected (not just direction) | retry L2 up to 2×. If still fails: accept axis-by-axis (some axes are acceptable mismatches, e.g., exposure within 30% is fine; direction must match within 45°). Log per-axis. | invalidate `<L2_layer_id>` only; keep L0. |
| **B.2 Perspective mismatch** (L0 isometric overhead; L2 character rendered front-on) | declared archetype framing (insert/CU/MS/...) compared against detected L2 perspective via CLIP | rerender L2 with explicit perspective clause from archetype framing row | retry L2 up to 2×. | invalidate `<L2_layer_id>` only. |
| **B.3 Pose-scale mismatch** (character rendered at portrait scale but archetype's subject_placement_bbox calls for long-shot scale) | post-cutout-bbox vs archetype subject_zone — if cutout bbox > 2× the zone area or < 0.5× | rescale at composite time (acceptable for ±30%); rerender if outside that range | retry up to 2× with explicit framing clause | invalidate `<L2_layer_id>` only. |
| **B.4 Atmospheric overlay contamination** (steam L4 overlapping face L2 causes visual artifact — e.g., face features fade into steam) | post-composite saliency map; if L2-face-region saliency drops > 50% after L4 composite | reduce L4 opacity to 0.3 max in face region (per-pixel masking) | accept reduced opacity; no rerender needed | no invalidation. |
| **B.5 Seam visibility** (composite paste boundary visible — edge halo, sudden tone shift) | edge-detection across paste boundary; if edge density > scene mean × 2 | apply 1px alpha matting at composite boundary as remediation (NOT full feather — just edge-AA) | no rerender; remediation in composite step. | no invalidation. |

### 14.C Continuity failures (detected by sibling `MANGA_CONTINUITY_STATE_SPEC.md §3` invariants)

| failure | detection | fallback | rerender policy | cache invalidation |
|---|---|---|---|---|
| **C.1 Gaze discontinuity** (panel N gaze at_cup; panel N+1 gaze at_camera with no transitional beat) | sibling `MANGA_CONTINUITY_STATE_SPEC.md §3` gaze-continuity invariant | flag panel N+1 for chapter_script edit (add transitional beat OR change gaze) | no auto-rerender — requires chapter_script change. Escalate to writer. | no invalidation. |
| **C.2 Prop state regression** (cup_full in panel N, cup_empty in panel N+1, no drink-action panel between) | sibling `MANGA_CONTINUITY_STATE_SPEC.md §3` prop continuity invariant | flag chapter_script for review — likely a continuity bug | no auto-rerender. | no invalidation. |
| **C.3 Emotional pendulation violation** (calm → peak_anxious in one beat for iyashikei) | sibling `MANGA_CONTINUITY_STATE_SPEC.md §3` emotional invariant per iyashikei rules | flag for chapter_script edit (insert intermediate beat) | no auto-rerender. | no invalidation. |
| **C.4 Identity flip across panels** (Mira's hair color shifts; eye geometry shifts) | embed all L2 renders for same character in episode; cluster — if outlier > 0.55 distance | rerender outlier L2 with stronger identity inputs | retry up to 3× | invalidate the outlier `<layer_id>`. |

### 14.D Cache invalidation triggers (across the system)

| trigger | invalidate |
|---|---|
| `character_design.yaml` edit | all `<L2_layer_id>` for that character_id |
| `scene_inventory.yaml` edit | all `<L0_layer_id>` and `<L1_layer_id>` for that scene_id |
| `object_inventory.yaml` edit | all `<L3_layer_id>` for that object_id |
| `iyashikei.yaml` archetype edit | nothing automatic (archetype changes affect composition, not layer renders) BUT next composite for that archetype rebuilds |
| spec edit affecting §5 of this doc OR sibling `MANGA_CONTINUITY_STATE_SPEC.md` | regenerate `scripts/manga/compile_safe_zones.py` output; recompute continuity_state hashes |

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

This provenance feeds `render_telemetry/<episode>.yaml` (sibling `MANGA_CONTINUITY_STATE_SPEC.md §11`) and surfaces per-panel quality tier for operator dashboards.

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
- **Hash-equality is necessary but NOT sufficient.** Per sibling `MANGA_CONTINUITY_STATE_SPEC.md §3.A` amendment, when PuLID and LoRA are both inactive, `character_design_hash = axes_hash` only — same hash does not guarantee same rendered face. §15.A.2 explicitly requires one of {PuLID-active, per-character-LoRA-trained} as a precondition for this gate to be evaluable. The structural validator (sibling `MANGA_CONTINUITY_STATE_SPEC.md §3.A`) can still pass; the perceptual gate (this §15.A.2) cannot pass without an identity-locking engine.
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
- All sibling `MANGA_CONTINUITY_STATE_SPEC.md §3.A` deterministic invariants implemented; class-A FAIL halts panel build
- All sibling `MANGA_CONTINUITY_STATE_SPEC.md §3.B` heuristic invariants implemented at SCORE/WARN severity (advisory only at V4)
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
**Fallback if unmet:** V4 does not launch for that archetype set / series. Diagnose which panels failed, iterate on prompt templates / continuity_state / light_rig, re-run review. Catalog rollout (sibling `MANGA_V4_MIGRATION_PLAN_ARCHIVE.md §7`, formerly §13.6 of this spec) does not begin until composite review passes for `stillness_en_01`.

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
   - **Shared light rig.** Sibling `MANGA_CONTINUITY_STATE_SPEC.md §9` handles this — both characters inherit the scene's light_rig — but it requires the QA gate to validate BOTH L2 renders, not one.
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
5. **Pose transition grammar.** Sibling `MANGA_CONTINUITY_STATE_SPEC.md §3` invariants enforce gross continuity. Sub-question: are there pose-specific transition rules? (e.g., "sitting → standing" needs 1 transitional beat; "sitting → reaching" can be direct).

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
   - **Mitigation:** before each genre rollout (per sibling `MANGA_V4_MIGRATION_PLAN_ARCHIVE.md §7`, formerly §13.6 of this spec), audit the ontology against ≥3 bestseller exemplars in that genre and explicitly approve additions/deprecations. The enum is a contract, not a frozen truth.
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

2. **Continuity contract** (see sibling `MANGA_CONTINUITY_STATE_SPEC.md` — formerly §6 of this spec) — `story_state → continuity_state → archetype → layers → composite`. Per-panel state record (emotional, posture, gaze, hand_state, prop_state, temporal). Sibling spec §3 invariants gate sequence coherence.

3. **Layer contract** (§3, §4, §7, §8) — 5 render layers (L0–L4) + reserved namespaces for semantic / export / ink / animation layers. Per-archetype layer composition map. Per-series inventories (character_pose, scene, object).

4. **Failure-recovery contract** (§14) — every failure class has detection / fallback / rerender / cache-invalidation policy. Layered systems fail differently; spec covers it.

**Compute economics:** ~82 unique renders per series compose to ~300 panels (3.7× vs V3.1's per-panel render). Continuity state inflates unique count vs v0.1's optimistic 10× — the trade buys semantic coherence.

**Launch blockers (§15.A):** identity lock (PuLID or LoRA), backdrop reliability, layer QA validator, continuity invariant validator. All four required before V4 ships.

**Explicitly unsupported in V4 (§15.B — not gaps, decisions):** multi-character layered composites, action archetypes, locale-aware signage, pose-interdependent panels, B&W iyashikei register. All fall back to single-pass V3.1.

**The strategic bridge:** once layers are stable image assets, motion manga, VN-style branching, reusable cinematic grammar, and persistent cinematographic world models all become feasible without architectural rework. Reserve namespace `A0–A9` for animation today (§4.6) so we don't repaint the bike-shed when the unlock arrives.

**Recommended next action (v0.3, validator-first):** operator approves §5, sibling `MANGA_CONTINUITY_STATE_SPEC.md` (including §8 cardinality + §9 light rigs — formerly §6.8 + §6.9 of this spec), §8 of this spec, sibling `MANGA_V4_MIGRATION_PLAN_ARCHIVE.md` (formerly §13 of this spec, reordered to validator-first), §14 → I build Phase B's three validators (`compile_safe_zones.py` → `validate_layer.py` → `validate_continuity_invariants.py`) → only after validators pass synthetic tests do I author Phase C inventories for `stillness_en_01` → re-prompt Mira on pure-white backdrop → second layer demo passes validators end-to-end → V4 dispatcher ships ep_001 layered.

— end of spec v0.2 —
