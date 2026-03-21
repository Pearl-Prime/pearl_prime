# VISUAL IDENTITY AGENT

Full Agent Specification — AI Manga Dharma System

*SpiritualTech Systems · Confidential · v1.1*

---

## 1. Role, Boundary & Position

The Visual Identity Agent is the only agent in the pipeline permitted to make aesthetic decisions. It defines the visual language of a series — linework, shading, color, camera grammar, character design, location design, motif design, and silence visual grammar — and encodes those decisions into a frozen `style_bible.json` that all downstream agents consume as law.

It is not unconstrained. Every aesthetic decision must fit within a constraint envelope defined by four inputs: the `genre_blueprint` (from the Genre Agent), the market format requirements, the production system constraints (what the image generation model can actually render reliably), and the transmission requirements (silence purity, motif consistency, somatic weight). The Visual Identity Agent has creative authority within that envelope. Outside it, the agent stops and requests a constraint update — it does not improvise.

### Pipeline Position

```
Genre Agent → genre_blueprint.json
        ↓
Visual Identity Agent ← market_format_spec
        ↓              ← production_constraints
        ↓              ← transmission_requirements
        ↓
   style_bible.json (frozen, versioned)
   character_model_sheets[]
   asset_registry.json
   anchor_panels[]
        ↓        ↓           ↓              ↓
  Visual Agent   Lettering   Layout Agent   QC Agent
                 Agent
```

### What the Visual Identity Agent Owns

- Series visual style (linework, shading, rendering era, aspect ratio, format)
- Character visual design (model sheets, outfit registry, LoRA training specs)
- Location visual design (asset specs, lighting defaults, atmosphere)
- Recurring motif visual design (asset specs, placement rules, consistency requirements)
- Camera lexicon (fixed translations from script camera values to prompt framing terms)
- Action lexicon (fixed translations from script action verbs to pose descriptors)
- Mood lexicon (fixed translations from script mood_direction to lighting/shadow descriptors)
- Silence visual grammar (parameterized camera progression, subject rules, prohibition lists)
- Prohibited style terms (immutable negative prompt base)
- Anchor panels (reference images + embeddings for drift detection)
- Style bible versioning and migration governance

### What the Visual Identity Agent Never Does

- Does not write story beats, dialogue, or narrative content
- Does not alter upstream genre, arc, or chapter decisions
- Does not create visual content at render time — it defines the rules; the Visual Agent renders
- Does not make runtime decisions — all decisions are encoded in style_bible.json before any panel is generated
- Does not expose atom names, transmission annotations, carrier beat flags, or somatic intention fields in any writer-facing artifact (see §9 for formal artifact classification)
- Does not create motifs reactively to story events — all motifs are scheduled in advance (see §7)

---

## 2. Inputs

### 2.1 genre_blueprint.json — Creative Constraint

The genre blueprint from the Genre Agent defines the creative boundaries for the series: target genre, sub-genre blend, emotional range, action intensity, pacing expectations, and reference works. The Visual Identity Agent translates these into visual style decisions.

| Blueprint field | How Visual Identity Agent uses it |
|---|---|
| `primary_genre` | Selects the base aesthetic family: shōnen → clean lines, high contrast, dynamic action; seinen → detailed rendering, atmospheric shadow; josei → delicate linework, emotional subtlety; healing/iyashikei → soft lines, warm tones, low contrast. |
| `sub_genre_blend` | Adjusts the base aesthetic: psychological thriller overlay → dutch angle in camera lexicon, heavier shadow in mood lexicon; sports overlay → motion-focused action lexicon, speed line budget. |
| `reference_works` | Informs (but does not copy) the rendering era, linework weight, and screentone density. Used as anchor_panel composition references, not as style templates. |
| `emotional_range` | Defines the full range of mood_lexicon entries needed: a series with narrow emotional range needs fewer lighting states; a series spanning rage to stillness needs the full spectrum. |
| `silence_weight` | How much somatic weight silence carries in this series. High silence_weight → more parameterized silence grammar, stricter prohibition list, more anchor panels for silence sequences. |

### 2.2 market_format_spec — Technical Constraint

| Format field | What it constrains |
|---|---|
| `format` | Traditional manga (right-to-left pages), webtoon (vertical scroll), or hybrid. Determines aspect ratio, reading direction, panel layout grammar. |
| `color_mode` | Black and white, full color, or limited palette. Constrains the entire shading and lighting vocabulary. |
| `target_resolution` | Output resolution for panels. Constrains detail level in prompt construction — higher resolution permits finer linework detail. |
| `locale_variants` | If the series ships in multiple markets: defines which locale-specific adjustments are needed (text direction, panel mirroring, SFX translation). |

### 2.3 production_constraints — System Constraint

| Constraint | What it limits |
|---|---|
| `image_gen_model` | Which model (Flux, SDXL, Midjourney) the Visual Agent will use. Each model has different prompt vocabulary, negative prompt behavior, and LoRA support. The Visual Identity Agent must design the style bible for the specific model. |
| `lora_support` | Whether the model supports character LoRA injection. If not, character consistency relies on detailed prompt descriptions + reference images. |
| `max_prompt_tokens` | Token budget ceiling from the image generation model. The Visual Identity Agent must ensure that the full prompt assembly (style tokens + camera + subject + action + background + mood + continuity + composition + silence) fits within this ceiling. Informs the token budget in Visual Agent Spec §3.4. |
| `batch_generation` | Whether panels are generated in sequence or in parallel batches. Affects continuity enforcement strategy. |

### 2.4 transmission_requirements — Dharma Constraint

| Requirement | What it mandates |
|---|---|
| `silence_purity_level` | How strict the silence visual grammar must be. Level 3 (maximum): full five-beat protocol, full prohibition list, parameterized ramps. Level 2: five-beat protocol, basic prohibition list. Level 1: silent panels only, no adjacency rules. |
| `motif_binding` | Whether recurring motifs are transmission-bound (must be rendered from asset_id, never described) or loose (description-based OK). All therapeutic brands use transmission-bound. |
| `carrier_beat_opacity` | How invisible carrier beats must be in the visual layer. Level 0: carrier beats are indistinguishable from surrounding panels. No visual emphasis, no special lighting, no compositional highlighting. The Visual Identity Agent does not know which beats are carriers — it designs a visual system where no beat gets unearned emphasis. |

---

## 3. Output — style_bible.json

### 3.1 Top-Level Structure

```json
{
  "series_id": "mirror_demon",
  "style_bible_version": "1.0",
  "created_at": "ISO timestamp",
  "created_by": "visual_identity_agent",
  "genre_blueprint_version": "1.0",
  "market_format": "traditional_manga_rtl",
  "color_mode": "black_and_white",
  "image_gen_model": "flux_v1",
  "frozen": true,

  "series_style_tokens": [ /* ordered token array */ ],
  "prohibited_style_terms": [ /* immutable negative prompt base */ ],

  "lexicons": {
    "camera_lexicon": { /* enum → prompt string */ },
    "action_lexicon": { /* verb phrase → pose descriptor */ },
    "mood_lexicon": { /* mood string → lighting descriptor */ }
  },

  "silence_visual_grammar": { /* parameterized silence rules */ },

  "character_registry": [ /* character design specs */ ],
  "location_registry": [ /* location asset specs */ ],
  "motif_registry": [ /* recurring motif specs */ ],

  "anchor_panels": [ /* reference panel specs */ ],

  "drift_detection": {
    "check_interval": 10,
    "threshold": { /* per-parameter thresholds */ }
  },

  "version_history": [ /* migration log */ ]
}
```

### 3.2 series_style_tokens — The Visual DNA

The ordered array of tokens that appear at the start of every positive prompt. These define the visual identity of the series and are immutable once the style bible is frozen.

```json
{
  "series_style_tokens": [
    "clean ink line 0.8pt weight",
    "screentone shading no gradient",
    "late 90s shōnen manga aesthetic",
    "black and white",
    "high contrast",
    "traditional right-to-left page format"
  ],
  "token_order": "fixed — never reorder, never insert, never remove",
  "modification_authority": "visual_identity_agent only, requires version bump"
}
```

### 3.3 prohibited_style_terms — The Immutable Negative Base

```json
{
  "prohibited_style_terms": [
    "photorealistic", "realistic render", "3D render", "3D",
    "oil painting", "watercolor", "western comic", "anime screenshot",
    "digital painting", "illustration", "concept art", "art station",
    "unreal engine", "CGI", "photo", "photograph"
  ],
  "immutable": true,
  "modification_authority": "visual_identity_agent only, requires version bump and downstream notification"
}
```

### 3.4 Lexicons

All three lexicons follow the schema defined in Visual Agent Spec §2.3. The Visual Identity Agent creates and maintains these tables. The Visual Agent consumes them as fixed translations — it never interprets or extends them.

```json
{
  "lexicons": {
    "camera_lexicon": {
      "_schema": "{ script_camera_enum: prompt_string }",
      "_fallback": "hard_fail",
      "close_up": "extreme close-up, face fills frame, shallow depth",
      "medium": "medium shot, full torso visible",
      "wide": "wide establishing shot, full background, character small in frame",
      "dutch": "dutch angle, tilted horizon, psychological unease",
      "pov": "first-person perspective shot",
      "over_shoulder": "over-shoulder shot, subject B visible in midground",
      "bird_eye": "bird's-eye view, straight down, character small",
      "low_angle": "low angle looking up, character dominant in frame",
      "extreme_close": "extreme macro close-up, single feature fills frame"
    },
    "action_lexicon": {
      "_schema": "{ action_verb_phrase: pose_descriptor_string }",
      "_fallback": "style_bible_gap_flag",
      "sits on floor": "seated, legs folded, back against wall, body weight low",
      "looks away": "head turned 3/4 from viewer, eye contact avoided, tension in jaw",
      "runs": "mid-stride, forward lean, arms pumping, hair trailing",
      "stands still": "upright, weight even, arms at sides, no motion indication",
      "falls": "body mid-collapse, limbs loose, gravity pulling down",
      "reaches out": "arm extended forward, fingers spread, body leaning into reach",
      "clenches fist": "fist tight, knuckles white, forearm tense, veins visible",
      "turns around": "body mid-rotation, shoulders leading, head following"
    },
    "mood_lexicon": {
      "_schema": "{ mood_direction_string: lighting_descriptor_string }",
      "_fallback": "style_bible_gap_flag",
      "heavy, still": "deep shadow, flat diffuse overhead light, low contrast ratio, muted midtones",
      "tense, kinetic": "hard rim lighting, high contrast, motion blur suggestion in background",
      "warm, safe": "soft diffuse warm light, gentle shadow, low contrast, amber midtones",
      "cold, exposed": "harsh overhead white light, deep sharp shadow, high contrast, blue cast",
      "dreamlike": "soft focus, low contrast, slight glow, diffuse light from no source",
      "aggressive": "hard directional light from below or side, extreme contrast, sharp shadow edges"
    }
  }
}
```

### 3.5 Silence Visual Grammar — Parameterized

The silence visual grammar is not descriptive — it is parameterized with measurable values. Every field must have a numeric value or range that QC can validate against rendered output.

```json
{
  "silence_visual_grammar": {
    "protocol": "five_beat",
    "beats": ["arrival", "stillness", "detail", "world", "return"],

    "camera_progression": {
      "arrival": { "type": "medium", "framing_shift": "pull_0.15_from_previous" },
      "stillness": { "type": "medium", "framing_shift": "identical_to_arrival" },
      "detail": { "type": "extreme_close", "subject": "not_face", "allowed_subjects": ["hands", "object", "texture", "fabric"] },
      "world": { "type": "wide", "character_scale": "< 0.15_of_frame_height" },
      "return": { "type": "medium", "framing_shift": "match_arrival_with_subtle_posture_change" }
    },

    "lighting_ramp": {
      "arrival": { "contrast_ratio": "0.4-0.5", "shadow_depth": "medium" },
      "stillness": { "contrast_ratio": "0.3-0.4", "shadow_depth": "flat" },
      "detail": { "contrast_ratio": "0.3-0.4", "shadow_depth": "flat", "direction": "overhead_only" },
      "world": { "contrast_ratio": "0.5-0.6", "shadow_depth": "ambient", "source": "environmental" },
      "return": { "contrast_ratio": "0.4-0.5", "shadow_depth": "medium", "warming": "+0.05_from_arrival" }
    },

    "prohibition_list": [
      "text", "written words", "signage", "signs", "banners", "graffiti",
      "captions", "speech bubbles", "thought bubbles", "SFX lettering",
      "onomatopoeia", "narration box", "caption box", "title card",
      "watermark", "subtitle", "label", "symbolic word overlay",
      "calligraphy as decoration", "newspaper", "book text visible",
      "screen text", "any readable language",
      "symbolic imagery", "dream-filter effects", "vignette",
      "dramatic lighting", "god rays", "lens flare"
    ],

    "guard_prohibition_subset": [
      "text", "signage", "written words", "speech bubbles",
      "caption box", "SFX lettering", "onomatopoeia"
    ]
  }
}
```

---

## 4. Character Registry

### 4.1 Character Design Spec

Each named character in the series has a design entry in the style bible that the Visual Agent and Lettering Agent reference by ID.

```json
{
  "character_registry": [
    {
      "character_id": "kai",
      "display_name": "Kai",
      "model_sheet_id": "kai_v2",
      "lora_id": "kai_lora_v2",
      "lora_training_spec": {
        "reference_images": 20,
        "angles": ["front", "3/4_left", "3/4_right", "profile_left", "profile_right", "back"],
        "expressions": ["neutral", "exhausted", "focused", "angry", "vulnerable"],
        "training_prompt_prefix": "kai_character, male, late teens"
      },
      "outfits": [
        {
          "outfit_id": "kai_streetwear_01",
          "description_tokens": "dark hoodie, worn jeans, white sneakers, no accessories",
          "context": "default everyday, chapters 1-12"
        },
        {
          "outfit_id": "kai_dojo_01",
          "description_tokens": "white training gi, bare feet, cloth belt",
          "context": "training scenes, dojo location"
        }
      ],
      "physical_constants": {
        "height_relative": "average, 170cm frame",
        "build": "lean, wiry, not muscular",
        "hair": "short, dark, slightly messy",
        "distinguishing": "scar on right eyebrow, bruise-prone knuckles"
      },
      "continuity_init": {
        "injuries": [],
        "props_held": [],
        "emotional_baseline": "guarded, controlled",
        "hair_state": "default messy"
      }
    }
  ]
}
```

### 4.2 Character Design Rules

- Every named character must have a `character_id`, `model_sheet_id`, and at least one `outfit_id` before any chapter featuring them enters the Visual Agent
- LoRA training specs define the minimum reference set for character consistency — the Visual Identity Agent specifies these; the production team executes training
- Outfit changes require a new `outfit_id` entry — the Visual Agent never generates a character in an outfit not in the registry
- Physical constants are immutable within a series unless a story event changes them (e.g., haircut), in which case the Visual Identity Agent issues a style bible version bump with the change

---

## 5. Location & Asset Registry

### 5.1 Location Design Spec

```json
{
  "location_registry": [
    {
      "asset_id": "apartment_interior_kai",
      "display_name": "Kai's Apartment — Interior",
      "description_tokens": "small studio apartment, single window, futon on floor, low table, minimal furnishing, dim overhead light, worn wooden floor",
      "lighting_default": "flat overhead, warm-cool mix, shadow under table",
      "atmosphere": "confined, lived-in, quiet",
      "first_appearance": "chapter 1, page 3",
      "reference_image_id": "loc_kai_apt_ref_01",
      "consistency_anchors": ["window_position_left_wall", "futon_against_right_wall", "table_center"]
    }
  ]
}
```

### 5.2 Asset Reuse Rule

Every recurring location, prop, and motif must be referenced by `asset_id` in all downstream agents. Free-text descriptions of registered assets are prohibited — they produce visual drift across chapters. If the Visual Agent, Lettering Agent, or Layout Agent needs to reference a location or prop, it uses the `asset_id` from this registry. The asset registry is the single source of truth.

---

## 6. Anchor Panels — Drift Detection Reference

### 6.1 What Anchor Panels Are

Anchor panels are reference-grade rendered panels that define "what this series looks like." They serve as the ground truth for drift detection: every 10 panels, the Visual Agent compares the current panel against the nearest relevant anchor panel. If measured parameters (contrast ratio, linework weight, shadow distribution) drift beyond threshold, the panel is flagged.

### 6.2 Required Anchor Panel Categories

Every series must have anchor panels in the following categories before production begins:

| Category | What it anchors | Minimum count |
|---|---|---|
| **Standard dialogue** | Two characters talking, medium shot, standard lighting | 2 |
| **Action/motion** | High-intensity physical movement, dynamic camera | 2 |
| **Silent — stillness beat** | Silent panel, medium shot, flat light, no motion | 2 |
| **Silent — detail beat** | Extreme close-up, hands/object, no face | 1 |
| **Silent — world beat** | Wide establishing, character small or absent | 1 |
| **Character close-up** | Per named character, neutral expression | 1 per character |
| **Location establishing** | Per major location, wide shot, default lighting | 1 per location |
| **Motif** | Per recurring motif, isolated clear render | 1 per motif |

### 6.3 Anchor Panel Spec

```json
{
  "anchor_panels": [
    {
      "anchor_panel_id": "anchor_silent_stillness_01",
      "category": "silent_stillness",
      "reference_image_id": "anchor_img_ss01",
      "embedding_id": "anchor_emb_ss01",
      "measured_parameters": {
        "contrast_ratio": 0.38,
        "linework_weight_px": 2.1,
        "shadow_coverage_pct": 0.22,
        "highlight_coverage_pct": 0.45,
        "detail_density": "medium",
        "color_temperature": "neutral_cool"
      },
      "prompt_used": "clean ink line 0.8pt weight, screentone shading...",
      "generation_settings": {
        "model": "flux_v1",
        "seed": 42,
        "cfg_scale": 7.5,
        "steps": 30
      }
    }
  ]
}
```

### 6.4 Drift Detection Logic

```
every 10 panels:
  current_panel = measure_parameters(rendered_panel)
  nearest_anchor = find_anchor(category=current_panel.category)

  for param in measured_parameters:
    delta = abs(current_panel[param] - nearest_anchor[param])
    if delta > drift_detection.threshold[param]:
      set drift_warning flag
      notify QC Agent
      halt generation until reviewed

  drift_detection.threshold = {
    "contrast_ratio": 0.10,
    "linework_weight_px": 0.5,
    "shadow_coverage_pct": 0.08,
    "highlight_coverage_pct": 0.10,
    "detail_density": "one_tier"  // low→medium = OK, low→high = drift
  }
```

---

## 7. Motif Registry — Binding & Safety Rules

### 7.1 Motif Design Spec

```json
{
  "motif_registry": [
    {
      "asset_id": "mirror_pieces_covered",
      "display_name": "The Covered Mirror",
      "visual_spec": "rectangular wall mirror, cloth draped over top half, lower half reflecting but dark, ornate wooden frame slightly chipped",
      "reference_image_id": "motif_mirror_ref_01",
      "placement_rules": {
        "default_position": "background_left_or_right_wall",
        "scale": "occupies 10-15% of panel width",
        "never_position": "center_foreground"
      },
      "scheduled_appearances": [
        { "chapter": 1, "page": 3, "context": "first appearance, background" },
        { "chapter": 5, "page": 12, "context": "kai notices it" },
        { "chapter": 9, "page": 8, "context": "cloth has slipped, more reflection visible" }
      ],
      "transmission_bound": true,
      "evolution_schedule": {
        "chapters_1_4": "fully covered, only frame visible",
        "chapters_5_8": "cloth slipped, 30% of mirror surface visible",
        "chapters_9_12": "cloth half off, reflection increasingly clear"
      }
    }
  ]
}
```

### 7.2 Motif Safety Rules

- **No text or symbols in motifs:** Motifs must never contain readable text, glyphs, symbols, or calligraphy. A dojo banner is rendered as a blank banner with texture — not with text on it.
- **No atom names in writer-facing artifacts:** The motif registry may internally note which wisdom atom a motif serves (for QC cross-referencing), but this annotation is stripped from all writer-facing outputs. See §9.
- **Scheduled, not reactive:** All motif appearances are scheduled in `scheduled_appearances` during series design. The Visual Agent does not add motifs to panels reactively based on story events. If a motif needs to appear in an unscheduled location, the Visual Identity Agent updates the schedule and bumps the style bible version.
- **Asset-referenced only:** All downstream agents reference motifs by `asset_id`, never by description. See §10.

---

## 8. Version Governance

### 8.1 Immutability Rule

Once `frozen: true` is set on a `style_bible.json`, no field may be changed without a formal version bump. The Visual Identity Agent is the only agent that can modify the style bible, and every modification follows this protocol:

1. Create a new version entry in `version_history` with the change description
2. Bump `style_bible_version` (semver: major.minor for breaking changes, patch for additive)
3. Update all affected anchor panels if the change affects rendering parameters
4. Notify all downstream agents of the version change
5. All downstream agents must reject any `style_bible.json` whose version does not match their expected version

### 8.2 What Counts as a Breaking Change (Major Bump)

- Adding or removing series_style_tokens
- Changing prohibited_style_terms
- Modifying camera_lexicon or mood_lexicon translations
- Changing character model sheet references or LoRA IDs
- Modifying silence visual grammar parameters

### 8.3 What Counts as an Additive Change (Minor Bump)

- Adding new action_lexicon entries (gap fills)
- Adding new location or motif entries to registries
- Adding new outfit entries for existing characters
- Adding new anchor panels

### 8.4 Version History

```json
{
  "version_history": [
    {
      "version": "1.0",
      "date": "ISO timestamp",
      "changes": "Initial style bible creation",
      "breaking": true
    },
    {
      "version": "1.1",
      "date": "ISO timestamp",
      "changes": "Added 12 action_lexicon entries for fight choreography",
      "breaking": false
    }
  ]
}
```

---

## 9. Artifact Classification — Writer-Facing vs Internal-Only

**[FIX 1 — Formal artifact classification to prevent leakage]**

Every output artifact in the pipeline is classified as either **writer-facing** or **internal-only**. The Visual Identity Agent must ensure that no transmission metadata, atom references, carrier beat flags, or somatic intention annotations appear in any writer-facing artifact.

### 9.1 Writer-Facing Artifacts (transmission metadata stripped)

These artifacts are consumed by agents that produce narrative content or visual content a reader will see. They must contain zero references to atoms, transmission, carrier beats, or somatic intention.

| Artifact | Consuming agent | What is stripped |
|---|---|---|
| `style_bible.json` (writer-facing export) | Visual Agent, Lettering Agent, Layout Agent | `motif_registry[].atom_reference`, any `transmission_*` fields, any `somatic_*` fields |
| `character_model_sheets[]` | Visual Agent | No transmission metadata should be present in model sheets |
| `panel_prompts.json` | Layout Agent, Lettering Agent | Produced by Visual Agent from writer-facing style_bible; inherits clean state |
| `lettering_spec.json` | Layout Agent | Produced by Lettering Agent from writer-facing inputs; inherits clean state |
| `chapter_script.json` (writer_handoff) | Visual Agent, Lettering Agent | `is_carrier_beat` always false, `somatic_intention` stripped. See Chapter Writer Spec §3 |
| `genre_blueprint.json` (writer-facing export) | Chapter Writer, Story Architect | Atom references stripped; genre/arc decisions presented as narrative craft only |

### 9.2 Internal-Only Artifacts (transmission metadata permitted)

These artifacts are consumed only by QC, the system owner, or agents that need cross-referencing capability. They may contain full transmission metadata.

| Artifact | Consuming agent | What is present |
|---|---|---|
| `style_bible.json` (internal version) | QC Agent, Visual Identity Agent | Full `motif_registry[].atom_reference`, `transmission_binding` annotations, `carrier_beat_visual_notes` |
| `chapter_script.json` (internal_record) | QC Agent | `is_carrier_beat` true values, `somatic_intention` fields, transmission annotations |
| `motif_registry` (internal version) | QC Agent | `atom_reference` per motif, `transmission_weight` scores |
| `anchor_panels` (QC metadata) | QC Agent | Drift thresholds, style coherence scores, carrier-adjacent panel audit flags |

### 9.3 Stripping Rule

The Visual Identity Agent produces TWO versions of the style bible:

1. **Writer-facing:** All `atom_reference`, `transmission_*`, and `somatic_*` fields removed. This is the version that `style_bible_version` references. All downstream rendering agents consume this version.
2. **Internal:** Full metadata retained. Only the QC Agent and the Visual Identity Agent itself consume this version. The internal version carries the same `style_bible_version` number but is tagged `"internal": true`.

Any agent receiving a style_bible without `"internal": true"` must assume it is the writer-facing version and must not request or expect transmission metadata.

---

## 10. Downstream ID Contract

**[FIX 2 — Strict ID contract for all downstream agents]**

All downstream agents (Visual Agent, Lettering Agent, Layout Agent, QC Agent) must reference characters, locations, motifs, outfits, and anchor panels exclusively by their registered IDs. Free-text names are non-authoritative and must never be used as primary references.

### 10.1 The Rule

| Entity type | Authoritative ID field | Example | Non-authoritative (prohibited as primary ref) |
|---|---|---|---|
| Character | `character_id` | `"kai"` | `"the protagonist"`, `"the boy"`, `"Kai"` |
| Character model sheet | `model_sheet_id` | `"kai_v2"` | `"Kai's design"` |
| LoRA embedding | `lora_id` | `"kai_lora_v2"` | `"Kai's LoRA"` |
| Outfit | `outfit_id` | `"kai_streetwear_01"` | `"Kai's hoodie"`, `"casual outfit"` |
| Location | `asset_id` | `"apartment_interior_kai"` | `"Kai's apartment"`, `"the room"` |
| Motif | `asset_id` | `"mirror_pieces_covered"` | `"the mirror"`, `"covered mirror"` |
| Anchor panel | `anchor_panel_id` | `"anchor_silent_stillness_01"` | `"the reference panel"` |

### 10.2 Enforcement

- **Visual Agent:** Every `character_refs[]` entry must use `character_id`, `model_sheet_id`, `lora_id`, and `outfit_id` from the registry. Every `asset_refs[]` entry must use `asset_id`. QC gate: any prompt containing a character or asset reference that doesn't match a registry ID fails validation.
- **Lettering Agent:** Speaker identification uses `character_id` for font selection. Location-dependent lettering adjustments (if any) use `asset_id`.
- **Layout Agent:** Panel composition references use `asset_id` for location-specific layout rules.
- **QC Agent:** All cross-referencing uses registry IDs. Drift detection uses `anchor_panel_id`. Character continuity tracking uses `character_id` + `outfit_id`.

### 10.3 Why This Matters

Free-text references produce silent failures: "the mirror" in a prompt might get a different render than `asset_id: "mirror_pieces_covered"` because the description is slightly different each time. ID-based referencing forces the system to look up the canonical visual spec every time, eliminating the most common source of cross-chapter visual inconsistency.

---

## 11. Visual Identity Agent System Prompt

Injected at runtime with `genre_blueprint.json`, `market_format_spec`, `production_constraints`, and `transmission_requirements`.

```
You are the Visual Identity Agent in a spiritual manga creation system.

Your role: define the complete visual language of a series and encode
it into a frozen, versioned style_bible.json that all downstream
agents consume as law.

You are the only agent permitted to make aesthetic decisions.

CONSTRAINT ENVELOPE:
Every aesthetic decision must fit within:
1. genre_blueprint (creative boundaries from Genre Agent)
2. market_format_spec (technical format requirements)
3. production_constraints (image gen model capabilities)
4. transmission_requirements (silence purity, motif binding, opacity)
Outside this envelope: stop and request a constraint update.

YOU PRODUCE:
- style_bible.json (frozen, versioned, writer-facing + internal)
- character_model_sheets[] (LoRA training specs, outfit registry)
- asset_registry.json (locations, props, motifs)
- anchor_panels[] (reference images + measured parameters)

STYLE BIBLE CONTENTS:
- series_style_tokens (ordered, immutable once frozen)
- prohibited_style_terms (immutable negative prompt base)
- camera_lexicon (enum → prompt string, hard_fail on unknown)
- action_lexicon (verb → pose descriptor, gap_flag on unknown)
- mood_lexicon (mood → lighting descriptor, gap_flag on unknown)
- silence_visual_grammar (parameterized five-beat protocol)
- character_registry (model sheets, outfits, LoRA specs)
- location_registry (asset specs, lighting defaults)
- motif_registry (asset specs, placement rules, evolution schedule)
- anchor_panels (reference renders + measured parameters)
- drift_detection (thresholds, check interval)

IMMUTABILITY RULES:
- frozen: true means no changes without version bump
- breaking changes = major version bump + downstream notification
- additive changes = minor version bump
- downstream agents reject version mismatches

ARTIFACT CLASSIFICATION:
- Writer-facing: all transmission metadata stripped
- Internal-only: full metadata, QC Agent + self only
- Two versions of style_bible always produced in parallel

ID CONTRACT:
- All entities referenced by registered ID only
- Free-text names are non-authoritative
- Downstream agents must use character_id, outfit_id, asset_id,
  anchor_panel_id — never display_name or description

MOTIF SAFETY:
- No text/symbols in motif visual specs
- No atom names in writer-facing artifacts
- Scheduled appearances only — no reactive placement
- Asset-referenced only — no free-text descriptions

genre_blueprint: {{ genre_blueprint_json }}
market_format: {{ market_format_spec }}
production_constraints: {{ production_constraints }}
transmission_requirements: {{ transmission_requirements }}
```

---

## 12. Quality Gates — Identity Level

| Gate | Pass condition | Check method | Fail action |
|---|---|---|---|
| **Style token completeness** | `series_style_tokens` array is non-empty, ordered, and covers: linework, shading, rendering era, color mode, contrast, format. | Schema validation | Halt. Add missing tokens. |
| **Lexicon coverage** | `camera_lexicon` covers all camera enums used in any genre_blueprint. `action_lexicon` covers minimum 20 common actions. `mood_lexicon` covers the full `emotional_range` from genre_blueprint. | Cross-reference genre_blueprint requirements | Add missing entries. Minor version bump. |
| **Silence grammar parameterization** | All silence_visual_grammar fields have numeric values or ranges, not descriptive text. `lighting_ramp` has contrast_ratio ranges per beat. `camera_progression` has measurable framing_shift values. | Schema validation — no string-only fields in numeric slots | Replace descriptive values with parameters. |
| **Anchor panel coverage** | All required categories (§6.2) have minimum anchor panel count met. Every named character and major location has at least one anchor. | Count check per category | Generate missing anchor panels. |
| **Character registry completeness** | Every character appearing in any planned chapter has: `character_id`, `model_sheet_id`, at least one `outfit_id`, `physical_constants`, `continuity_init`. | Registry vs chapter plan cross-reference | Add missing character entries. |
| **Motif safety** | Zero motifs contain text, symbols, or glyphs in their `visual_spec`. Zero writer-facing artifacts contain `atom_reference` or `transmission_*` fields. | Text scan on motif visual_specs + field scan on writer-facing exports | Remove text from motif specs. Strip transmission metadata from writer-facing outputs. |
| **Version integrity** | `style_bible_version` matches `version_history` latest entry. `frozen: true` is set. All downstream agents report version match. | Version cross-check | Correct version numbering. Notify downstream. |
| **ID uniqueness** | All `character_id`, `asset_id`, `outfit_id`, `model_sheet_id`, `lora_id`, and `anchor_panel_id` values are globally unique within the style bible. Zero collisions. | Uniqueness scan | Rename colliding IDs. Propagate to all references. |
| **Prohibited term isolation** | Zero terms from `prohibited_style_terms` appear in any `series_style_tokens`, `camera_lexicon` value, `action_lexicon` value, or `mood_lexicon` value. | Cross-scan prohibited list vs all positive-prompt sources | Remove contradictory terms. |
| **Drift threshold definition** | All `drift_detection.threshold` parameters have numeric values. No threshold is zero (too strict) or > 0.5 (too loose). | Range validation | Adjust thresholds to meaningful ranges. |
| **Writer-facing purity** | Writer-facing style_bible export contains zero instances of: `atom_reference`, `transmission_binding`, `somatic_intention`, `carrier_beat`, `is_carrier`. | Field name scan on exported JSON | Strip fields. Re-export. |
| **Production constraint fit** | Total token count of (series_style_tokens + longest camera_lexicon value + longest action_lexicon value + longest mood_lexicon value) does not exceed `max_prompt_tokens` minus 40 (headroom for continuity/composition). | Token count calculation | Compress tokens. Shorten lexicon values. Escalate if infeasible. |

---

*SpiritualTech Systems · Visual Identity Agent Spec v1.1 · Confidential*
