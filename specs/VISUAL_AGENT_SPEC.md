# VISUAL AGENT

Full Agent Specification — AI Manga Dharma System

*SpiritualTech Systems · Confidential · v1.1*

> **Render-authority note (provenance, 2026-05-29):** this is the SpiritualTech-lineage visual spec (FLUX/SDXL prompt planning, LoRA identity). The **current production render pipeline** is V5.1 — `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (Qwen-Image-Layered) + `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md` + PuLID-FLUX identity. The two lineages are not yet cross-reconciled; confirm which render path applies (operator-tier) before production use. Prompt approach here aligns with `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md`. **Reconciliation decision (2026-05-29):** `docs/MANGA_RENDER_LINEAGE_DECISION_2026-05-29.md` recommends the V4/V5 contract + `continuity_state` chain as canonical for render and this spec's prompt-planning as **superseded for the layered-render approach** (✅ RATIFIED 2026-05-29 per cap `MANGA-RENDER-LINEAGE-01` in `docs/PEARL_ARCHITECT_STATE.md`; spec retained as experiment-of-record / non-layered fallback).

---

## 1. Role, Boundary & Position

The Visual Agent is a renderer and translator, not a storyteller. Its job is to convert panel objects from `chapter_script.json` into precise, style-locked image generation prompts — one prompt per panel — while preserving the staging intent, emotional meaning, and transmission integrity established by every upstream agent.

It does not change plot beats. It does not alter staging. It does not introduce new narrative information. It does not add text elements to panels. It does not compensate for silence. It renders what the script describes — exactly, consistently, and in the visual language of the series style bible.

### Pipeline Position

```
Chapter Writer Agent → chapter_script.json
        ↓
Visual Agent ← style_bible.json ← Visual Identity Agent
        ↓    ← character_model_sheets[]
        ↓    ← asset_registry.json
        ↓
   panel_prompts.json
     ↓        ↓           ↓
  Image Gen   Layout      Lettering Agent
  (Flux/SDXL/ Agent       (SFX, dialogue,
  Midjourney) (page comp)  bubbles)
```

### Generation Mode Decision — Panel-First

This spec uses panel-first generation: each panel is generated as an independent image, then assembled into pages by the Layout Agent. This is the safer mode for character consistency, style locking, and individual panel QC. Page-first generation (generating a full manga page as a single image) is not used — it cannot guarantee panel-level continuity or allow targeted regeneration of individual failed panels.

The Layout Agent (not specified in this document) receives the assembled panel images and applies panel borders, gutters, page composition, and reading-direction formatting. SFX and lettering are handled by the Lettering Agent consuming the same `chapter_script.json` directly.

### Visual Identity Agent — Prerequisite

The Visual Agent requires a `style_bible.json` as its primary constraint set. If this document does not yet exist for a series, a Visual Identity Agent must be run first to produce it. The Visual Identity Agent takes series concept, genre, market, and reference art direction as inputs and outputs the style_bible, character model sheets, and asset registry. The Visual Agent cannot operate without these inputs — it will not generate defaults.

---

## 2. Inputs

### 2.1 chapter_script.json — Primary Input

The Visual Agent consumes the full `chapter_script.json` produced by the Chapter Writer. For each page object, it processes each panel object in sequence, building context from the chapter state as it progresses. It never processes panels in isolation — each prompt is built with awareness of the panels that preceded it in the chapter.

| Script field consumed | Type | How Visual Agent uses it |
|---|---|---|
| `panel.camera` | enum | Maps directly to prompt framing term via `camera_lexicon`. `close_up` → `"extreme close-up face shot"`. `wide` → `"establishing wide shot, full background"`. `over_shoulder` → `"over-shoulder shot, subject B visible in midground"`. Each camera value has a fixed prompt translation — no interpretation. |
| `panel.subject` | string | Determines which character model sheet(s) and asset references are injected. If subject references a named character, their `character_id` is pulled from `asset_registry` and their current `continuity_state` is loaded. |
| `panel.action` | string | Translated into pose and motion descriptors. Present-tense action descriptions map to specific prompt vocabulary defined in the style_bible's `action_lexicon`. The Visual Agent does not interpret — it translates. |
| `panel.background` | string/null | If a named location: pull location asset ID from `asset_registry`. If null: inherit background register from page context (interior/exterior/abstract). If first appearance of a location: flag for new asset creation before generation. |
| `panel.mood_direction` | string | Translates to lighting, shadow weight, and visual temperature descriptors from the style_bible's `mood_lexicon`. `"Heavy, still"` → `"deep shadow, flat diffuse light, low contrast"`. Each mood_direction term has a fixed translation. |
| `panel.page_type` | enum | If `silent`: triggers silence compliance protocol — no text requests in prompt, `silence_compliance` flag set to true. If `splash`: full-bleed composition, no panel border. If `double_spread`: two-page layout flag passed to Layout Agent. |
| `panel.sfx` | string/null | SFX text is NOT included in the image generation prompt. It is passed to the Lettering Agent separately. The Visual Agent's job is the image only. If sfx is present, the prompt includes compositional space for lettering placement — but no text. |
| `panel.dialogue` | array | Same as SFX: dialogue is not included in image prompts. Passed to Lettering Agent. Visual Agent includes speech bubble placement zones in `composition_notes` if `bubble_type` and `placement` are specified. |
| `panel.silence_guard` | bool | If true: prompt explicitly prohibits signage, text-like shapes, written words in background, symbolic text overlays. See §5.1 for precise adjacency definition. |

### 2.2 style_bible.json — Primary Constraint

The style bible is the Visual Agent's law. Every prompt must comply with it. No style decision is made outside it. If the style bible does not specify something, the Visual Agent flags it as a style bible gap and requests a style bible update — it does not improvise.

| Style bible section | What it defines |
|---|---|
| `series_style_tokens` | The fixed token set included in every prompt: linework weight (e.g. `"clean ink line, 0.8pt weight"`), shading method (e.g. `"screentone, no gradient"`), rendering era (e.g. `"late 90s shōnen manga aesthetic"`), aspect ratio, and market format (B&W webtoon / full-color vertical scroll / traditional right-to-left page). |
| `prohibited_style_terms` | The series-level negative prompt base: terms that break the style regardless of context. Examples: `"realistic render, photorealistic, 3D, oil painting, watercolor, western comic, anime screenshot, digital painting, illustration"`. These appear in every `negative_prompt` with no exceptions. |
| `camera_lexicon` | Fixed translation table: script camera value → prompt framing term. See §2.3 for full schema. |
| `action_lexicon` | Translation table from action verbs to pose descriptors. See §2.3 for full schema. |
| `mood_lexicon` | Translation table from `mood_direction` strings to lighting/shadow descriptors. See §2.3 for full schema. |
| `silence_visual_grammar` | The visual language specifically for silent pages: camera progression rules (arrival medium → stillness medium → detail close-up → world wide → return medium), subject matter rules (no faces in full detail on stillness panel, hands/objects for detail panel), and prohibition list (no symbolic imagery, no dream-filter effects, no vignette — silence is rendered as clean, ordinary, present-moment reality). |
| `recurring_motifs` | Visual motifs that appear throughout the series and must be rendered consistently: the covered mirror in Mirror Demon, the dojo symbol in a shōnen, the crack in a teacup in a healing series. Each motif has an `asset_id` and a visual spec. Motifs carry transmission weight — they must be rendered exactly, not interpretively. |

### 2.3 Lexicon Definitions — Schema, Location & Fallback Behavior

**[FIX 1 — Lexicons formally defined]**

All three lexicons (`camera_lexicon`, `action_lexicon`, `mood_lexicon`) live inside `style_bible.json` under the top-level key `lexicons`. They are NOT separate files. Each lexicon is a flat key→value translation table with the following schema:

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
      "stands still": "upright, weight even, arms at sides, no motion indication"
    },
    "mood_lexicon": {
      "_schema": "{ mood_direction_string: lighting_descriptor_string }",
      "_fallback": "style_bible_gap_flag",
      "heavy, still": "deep shadow, flat diffuse overhead light, low contrast ratio, muted midtones",
      "tense, kinetic": "hard rim lighting, high contrast, motion blur suggestion in background",
      "warm, safe": "soft diffuse warm light, gentle shadow, low contrast, amber midtones",
      "cold, exposed": "harsh overhead white light, deep sharp shadow, high contrast, blue cast"
    }
  }
}
```

**Fallback behavior per lexicon:**

| Lexicon | If script uses a term NOT in the table |
|---|---|
| `camera_lexicon` | **Hard fail.** Camera values are enums. An unknown camera value means the Chapter Writer produced invalid output. Halt generation, return error to Chapter Writer for correction. |
| `action_lexicon` | **Style bible gap flag.** Set `style_bible_gap_flags[]` entry with the unrecognized action phrase, panel_id, and a request for the Visual Identity Agent to add the translation. Use the closest existing translation + gap flag — do not invent a translation. |
| `mood_lexicon` | **Style bible gap flag.** Same as action_lexicon — flag the gap, use closest existing mood translation, mark the panel with `qc_flags: ["mood_lexicon_gap"]`. |

### 2.4 character_model_sheets[] and asset_registry.json

Every named character has a model sheet in the asset registry: a reference image or LoRA embedding ID, a current outfit ID, a current hair state, and a `continuity_state` object tracking injuries, dirt, props held, and emotional baseline. The Visual Agent loads the `continuity_state` for every named character before generating any panel in the chapter and updates it after each panel.

```json
{
  "character_id": "kai",
  "chapter": 9,
  "last_updated_panel": "9-3-5",
  "outfit_id": "kai_streetwear_01",
  "hair_state": "disheveled, post-fight",
  "injuries": ["bruised_knuckles_right"],
  "props_held": [],
  "emotional_baseline": "exhausted, controlled",
  "position_last_panel": "seated, floor, back against wall"
}
```

---

## 3. Output — panel_prompts.json

### 3.1 Top-Level Structure

```json
{
  "series_id": "mirror_demon",
  "chapter_number": 9,
  "generated_at": "ISO timestamp",
  "style_bible_version": "1.0",
  "generation_mode": "panel_first",
  "total_panels": 47,
  "silence_panels_count": 9,
  "panels": [ /* panel_prompt objects */ ],
  "new_asset_flags": [ /* locations/props needing new asset creation */ ],
  "style_bible_gap_flags": [ /* anything style bible did not specify */ ],
  "continuity_state_end": { /* per-character state at chapter end */ }
}
```

### 3.2 panel_prompt Object — the atomic unit

```json
{
  "panel_id": "9-3-2",
  "page_number": 3,
  "panel_number": 2,
  "page_type": "standard",
  "panel_type": "standard",
  "prompt": "string — complete positive prompt for image generation",
  "negative_prompt": "string — complete negative prompt",
  "prompt_token_count": 74,
  "camera": "close_up",
  "camera_prompt_term": "extreme close-up, hands fill frame, shallow focus",
  "composition_notes": {
    "subject_placement": "center frame",
    "background_weight": "minimal, dark",
    "dialogue_space": null,
    "sfx_space": null,
    "reading_direction": "right_to_left"
  },
  "character_refs": [
    {
      "character_id": "kai",
      "model_sheet_id": "kai_v2",
      "lora_id": "kai_lora_v2",
      "outfit_id": "kai_streetwear_01",
      "continuity_state_at_panel": { /* snapshot */ }
    }
  ],
  "asset_refs": [
    { "asset_id": "mirror_pieces_covered", "placement": "background_left" }
  ],
  "continuity_tags": {
    "injuries_visible": ["bruised_knuckles_right"],
    "props_in_hand": [],
    "spatial_continuity": "same room as panel 9-3-1, camera moved closer"
  },
  "style_tokens_applied": [
    "clean ink line 0.8pt", "screentone shading",
    "late 90s shonen manga", "black and white", "high contrast"
  ],
  "silence_compliance": false,
  "silence_guard": false,
  "new_meaning_introduced": false,
  "qc_flags": []
}
```

### 3.3 Prompt Construction — the assembly algorithm

The prompt is not written freeform. It is assembled from parts in a fixed order. Each part is sourced from a specific input. This ensures consistency across panels and makes QC tractable.

```
prompt = [
  series_style_tokens,      // from style_bible — always first
  camera_prompt_term,        // from camera_lexicon translation
  subject_descriptor,        // character ref + current state
  action_descriptor,         // from action_lexicon translation
  background_descriptor,     // from asset_registry or location spec
  mood_descriptor,           // from mood_lexicon translation
  continuity_injections,     // injuries, props, outfit, hair state
  composition_directives,    // panel type, dialogue space, reading dir
  silence_directives         // only if silence_compliance = true
].join(', ')

negative_prompt = [
  series_prohibited_terms,   // from style_bible — always present
  camera_negatives,          // terms that break the camera type
  character_negatives,       // wrong outfit IDs, wrong hair, wrong age
  silence_negatives,         // if silence panel: text, signage, words
  continuity_negatives       // injuries not yet acquired, props not held
].join(', ')
```

### 3.4 Prompt Token Budget & Overflow Policy

**[FIX 3 — Token budget and required minimum fields]**

Image generation models degrade when prompts exceed their effective context window. The Visual Agent enforces a prompt token budget to prevent quality loss from over-long prompts.

**Maximum prompt length:** 120 tokens (positive prompt), 60 tokens (negative prompt). Token count is whitespace-delimited words. The `prompt_token_count` field in every `panel_prompt` object records the actual count.

**Required minimum fields (cannot be dropped):**

| Priority | Assembly segment | Droppable? |
|---|---|---|
| P0 | `series_style_tokens` | Never. If tokens alone exceed budget, escalate to Visual Identity Agent to compress token set. |
| P0 | `camera_prompt_term` | Never. |
| P0 | `subject_descriptor` | Never. Character identity is non-negotiable. |
| P1 | `action_descriptor` | Never for action panels. May be reduced to single verb for stillness/silent panels. |
| P1 | `background_descriptor` | Never for first appearance of location. May use `asset_id` shorthand for repeat locations. |
| P2 | `mood_descriptor` | May be shortened to 2-word lighting term if budget exceeded. |
| P2 | `continuity_injections` | Drop cosmetic continuity (hair state) before structural (injuries, props). |
| P3 | `composition_directives` | Drop reading_direction (Layout Agent handles it). Keep panel_type. |
| P3 | `silence_directives` | Never drop if `silence_compliance = true`. |

**Overflow policy:** When assembled prompt exceeds 120 tokens, drop in reverse priority order (P3 → P2). If still over budget after P2 trimming, flag `qc_flags: ["prompt_budget_exceeded"]` and escalate to Visual Identity Agent for style token compression.

---

## 4. Style Lock — Enforcement Rules

Style lock is not a preference — it is a system constraint. The Visual Agent's primary failure mode in production is style drift: panels generated later in a series look different from panels generated earlier. The following rules are the mechanical enforcement of style consistency.

**Rule 1 — Style tokens are non-negotiable and first**

The `series_style_tokens` from the style bible appear at the start of every positive prompt, in the same order, with no additions or removals. If a panel requires a style departure (e.g., a dream sequence in a different visual register), the Visual Identity Agent must first update the style bible with a `dream_sequence_style_tokens` set. The Visual Agent cannot invent style token variations.

**Rule 2 — Character identity is reference-locked**

Every panel containing a named character must include their LoRA embedding ID or model sheet reference in the generation call. Generation without a character reference is not permitted. If the image generation system does not support LoRA injection for a panel (e.g., the character is seen from very far away), the panel is flagged as `reference-exempt` and the `continuity_tags` must note the exemption reason.

**Rule 3 — Prohibited style terms appear in every negative prompt**

The style bible's `prohibited_style_terms` list is injected into the negative prompt of every single panel without exception. There is no panel for which `photorealistic`, `3D render`, `western comic`, or `oil painting` is acceptable. The list is treated as immutable — the Visual Agent cannot remove terms from it.

**Rule 4 — Continuity state is chapter-local and panel-sequential**

Before generating panel N, the Visual Agent loads the continuity state as it exists after panel N-1. If Kai's knuckles were bruised in panel 9-3-2, they are bruised in panel 9-3-3 unless a healing event occurs in the script. The Visual Agent does not assume continuity — it enforces it from the `continuity_state` object. Continuity drift (a character's injury disappearing between panels) is a system failure, not an artistic choice.

**Rule 5 — Recurring motifs use asset references, not descriptions**

If a recurring motif (the covered mirror, the dojo banner, the cracked teacup) appears in a panel, the prompt uses the motif's `asset_id` reference, not a description. Describing the same object differently in different prompts produces visual inconsistency across the series. The asset registry is the single source of truth for how every recurring visual element looks.

**Rule 6 — Drift detection runs every 10 panels**

The Visual Agent includes a drift detection step: every 10 panels, a style coherence check compares the current panel's style token application against the first panel of the chapter. If drift is detected (style tokens missing, prohibited terms appearing in prompt, character reference not injected), a `drift_warning` flag is set and the QC Agent is notified before the next panel is generated.

---

## 5. Silence Visual Protocol

Silent panels and silent pages are the highest-stakes visual output in the system. They carry the greatest somatic load. The Visual Agent's silence protocol is a direct translation of the Chapter Writer's five-beat silence sequence into visual generation instructions.

| Beat | Name | Camera directive | Prompt additions | Negative prompt additions |
|---|---|---|---|---|
| **1** | Arrival | Pull slightly from prev panel. Same camera type, looser framing. | `"Moment of pause, weight in stillness, no motion indication"` | `"dramatic pose, dynamic angle, action lines"` |
| **2** | Stillness | Same camera as arrival. Identical framing. Nothing has moved. | `"stillness, quiet, nothing happening, same position as previous panel"` | `"motion blur, speed lines, changed position, new element"` |
| **3** | Detail | Close-up. Not the face. The hands, an object, a texture. | `"extreme detail, texture, material weight, quiet focus"` | `"face, expression, eyes, dramatic lighting, symbolic overlay"` |
| **4** | World | Wide or establishing. Character small or absent. | `"wide shot, environment continues, ordinary world, ambient light"` | `"character centered, dramatic focus, vignette, dark overlay"` |
| **5** | Return | Back to same camera as arrival. Same subject. Subtle shift in posture or gaze. | `"subtle shift, same location, slight change in body position only"` | `"transformation, dramatic change, new outfit, new location"` |

### 5.1 silence_guard — Precise Adjacency Definition

**[FIX 2 — silence_guard adjacency pinned down]**

`silence_guard = true` is set on panels that flank a silent page sequence. The adjacency rule is:

- **Before silence:** The last 2 panels on the page immediately preceding the first silent page. If that page has fewer than 2 panels, all panels on that page are silence_guard. Adjacency does NOT cross backward to earlier pages.
- **After silence:** The first 2 panels on the page immediately following the last silent page. If that page has fewer than 2 panels, all panels on that page are silence_guard. Adjacency does NOT cross forward to later pages.
- **Page boundary rule:** silence_guard adjacency is counted by panel position within a page, not by absolute panel index across the chapter. This means: on a 5-panel page before silence, only panels 4 and 5 are silence_guard. On a 3-panel page after silence, only panels 1 and 2 are silence_guard.
- **Who sets it:** The Transmission Splitter in the Chapter Writer sets `silence_guard = true` on the qualifying panels before handoff. The Visual Agent reads it — it does not compute it.

Silence_guard panels receive the core text prohibition subset in their negative prompt: `text, signage, written words, speech bubbles, caption box, SFX lettering, onomatopoeia`. They do NOT receive the full silence prohibition list (that is reserved for `silence_compliance = true` panels only).

### 5.2 Silence Prompt Prohibition List

Every panel with `silence_compliance = true` must include ALL of the following in its negative prompt, regardless of other content:

> text, written words, signage, signs, banners, graffiti, captions, speech bubbles, thought bubbles, SFX lettering, onomatopoeia, narration box, caption box, title card, watermark, subtitle, label, symbolic word overlay, calligraphy as decoration, newspaper, book text visible, screen text, any readable language

The prohibition extends to visual text even when it is part of the background or set dressing. A coffee shop sign in the background of a silent panel is a silence violation.

---

## 6. No New Meaning — Violation Checklist

**[FIX 4 — No New Meaning gate formalized as operational checklist]**

The Visual Agent must not introduce elements not present in `panel.action`, `panel.subject`, `panel.background`, or `asset_refs`. The following is the complete list of common violations to scan for:

| # | Violation type | Example | Detection method |
|---|---|---|---|
| 1 | **Symbolic props not in script** | Rosary beads, broken chains, butterflies, falling petals, prayer candles | Check every noun in positive prompt against `panel.subject` + `panel.action` + `asset_refs`. Any noun not traceable to these sources = violation. |
| 2 | **Time-of-day/weather changes for mood** | Script says interior → prompt adds rain outside window. Script says daytime → prompt uses moonlight for atmosphere. | Compare lighting/environment terms against `panel.background` and `panel.mood_direction` lexicon translation. Any environment term not sourced from these = violation. |
| 3 | **Extra characters as atmosphere** | Adding crowd figures, background pedestrians, or onlookers not specified in `panel.subject` | Character count in prompt must match character count in `panel.subject`. Zero unnamed figures unless `panel.background` explicitly specifies crowd/populated setting. |
| 4 | **Dramatic lighting/effects not specified** | Speed lines when no motion in script. God rays. Lens flare. Dramatic rim lighting when mood_lexicon translation says flat diffuse. | Compare all lighting/effect terms against mood_lexicon translation output. Any lighting term not in the translation = violation. Speed lines only if `panel.action` contains rapid motion verb. |
| 5 | **Villain/character not in scene** | Script has Kai alone in room → prompt adds shadow figure or silhouette suggesting antagonist presence | Named or implied character presence must match `panel.subject` exactly. Shadows, silhouettes, and reflections suggesting off-script characters = violation. |
| 6 | **Upgraded emotional expression** | Script says "exhausted, controlled" → prompt says "tears streaming" or "face twisted in agony" | Emotional descriptors must come from `continuity_state.emotional_baseline` or `panel.action` verb translation. Any emotional escalation beyond source = violation. |
| 7 | **Symbolic composition** | Framing character behind bars (window frame), positioning hands in prayer-like pose not in script, using dutch angle for "psychological" effect when camera says `medium` | Camera angle must match `camera_lexicon` translation exactly. Compositional framing must match `composition_notes` only. |

**Automated scan:** Before finalizing each `panel_prompt`, run the 7-point violation scan. Any hit sets `new_meaning_introduced: true` and adds the violation type to `qc_flags[]`. Panel is not finalized until all violations are resolved.

---

## 7. Visual Agent System Prompt

Injected at runtime with `chapter_script.json`, `style_bible.json`, `character_model_sheets`, and `asset_registry.json`.

```
You are the Visual Agent in a spiritual manga creation system.

Your role: translate panel objects from chapter_script.json into
precise, style-locked image generation prompts.

You are a renderer and translator, not a storyteller.

ABSOLUTE BOUNDARY:
You do not change plot beats, alter staging intent, introduce new
narrative information, add text elements to panels, or compensate
for silence. You render what the script describes — exactly.

YOU CONSUME:
- chapter_script.json: pages and panels with camera, action, mood
- style_bible.json: series style tokens, lexicons, prohibited terms
- character_model_sheets[]: LoRA IDs, outfit IDs, continuity states
- asset_registry.json: location IDs, prop IDs, motif specs

YOU PRODUCE:
- panel_prompts.json: one panel_prompt object per panel

PROMPT ASSEMBLY ORDER (fixed — never reorder):
1. series_style_tokens (always first, always complete)
2. camera_prompt_term (from camera_lexicon — no interpretation)
3. subject_descriptor (character ref + continuity state)
4. action_descriptor (from action_lexicon — no interpretation)
5. background_descriptor (asset_id or location spec)
6. mood_descriptor (from mood_lexicon — no interpretation)
7. continuity_injections (injuries, props, outfit, hair)
8. composition_directives (panel type, space for lettering)
9. silence_directives (if silence_compliance = true)

PROMPT TOKEN BUDGET:
- Positive prompt: max 120 tokens
- Negative prompt: max 60 tokens
- If over budget: drop P3 → P2 segments (see §3.4)
- If still over: flag qc_flags and escalate

NEGATIVE PROMPT — always include:
- series_prohibited_style_terms (every panel, no exceptions)
- camera_negatives (terms breaking the camera type)
- continuity_negatives (injuries not yet acquired, wrong outfit)
- silence_negatives (if silence_compliance or silence_guard = true)

LEXICON RULES:
- All lexicons live in style_bible.json under "lexicons" key
- camera_lexicon: hard fail on unknown camera value
- action_lexicon: style_bible_gap_flag on unknown action, use closest match
- mood_lexicon: style_bible_gap_flag on unknown mood, use closest match
- NEVER invent a translation — flag it

SILENCE RULES:
- silent page_type: silence_compliance = true on all panels
- silence_guard = true: last 2 panels before + first 2 panels after silent page sequence (page-local counting, set by Transmission Splitter)
- silence_compliance prohibits all text-like elements in prompt
- silence_guard applies core text prohibition subset only
- follow five-beat visual protocol: arrival/stillness/detail/world/return

STYLE LOCK RULES:
- never generate without character LoRA reference for named characters
- never omit series_style_tokens
- never interpret camera, action, or mood — translate from lexicons only
- run drift check every 10 panels
- flag style bible gaps — do not improvise

NO NEW MEANING RULE — 7-point violation scan:
1. No symbolic props not in script
2. No time-of-day/weather changes for mood
3. No extra characters as atmosphere
4. No dramatic lighting/effects not specified
5. No villain/character not in scene
6. No upgraded emotional expression beyond source
7. No symbolic composition not in camera_lexicon
Run scan on every panel before finalization.

OUTPUT: valid JSON matching panel_prompts schema.

chapter_script: {{ chapter_script_json }}
style_bible: {{ style_bible_json }}
```

---

## 8. Worked Example — Chapter 9, Pages 4–6 (Silent Sequence)

The following shows complete `panel_prompt` objects for the three-page silent sequence from chapter 9 of Mirror Demon. Script input: Kai seated on floor after physical failure. `silence_pages_planned: 3`. `beat_ref: "after physical failure — kai on floor"`. Five-beat silence protocol: arrival (ch9-p3-p5), stillness (p4-pn1), detail (p4-pn2), world (p5-pn1), return (p6-pn1).

### Pre-silence arrival panel — panel 9-3-5 (silence_guard: true)

```json
{
  "panel_id": "9-3-5",
  "page_type": "standard",
  "silence_compliance": false,
  "silence_guard": true,
  "prompt_token_count": 68,
  "prompt": "clean ink line 0.8pt weight, screentone shading, late 90s shonen manga aesthetic, black and white, high contrast, medium shot, torso and face visible, slight pull back from previous close-up, Kai character ref lora:kai_v2, kai_streetwear_01 outfit, disheveled hair post-fight, bruised right knuckles, face-down on floor beginning to turn over, physical exhaustion, flat diffuse light, still interior, apartment floor, no motion indication, weight of stillness, reading direction right to left, space for no lettering",
  "negative_prompt": "photorealistic, 3D render, western comic, oil painting, watercolor, anime screenshot, digital painting, dynamic action pose, speed lines, motion blur, text, signage, written words, speech bubble, caption box, SFX lettering, onomatopoeia, dramatic lighting, hopeful expression, forward motion"
}
```

### Silent page 1, panel 1 — stillness beat — panel 9-4-1

```json
{
  "panel_id": "9-4-1",
  "page_type": "silent",
  "silence_compliance": true,
  "silence_guard": false,
  "prompt_token_count": 72,
  "prompt": "clean ink line 0.8pt weight, screentone shading, late 90s shonen manga aesthetic, black and white, high contrast, medium shot, same framing as previous panel, Kai seated, back against wall, knees up, head tilted back, eyes open toward ceiling, stillness, nothing happening, same position, lora:kai_v2, kai_streetwear_01, disheveled hair, bruised right knuckles, apartment interior, flat ambient light, no motion, quiet, weight in stillness",
  "negative_prompt": "photorealistic, 3D render, western comic, oil painting, watercolor, text, written words, signage, speech bubble, thought bubble, caption box, SFX lettering, onomatopoeia, graffiti, banners, any readable language, calligraphy, screen text, newspaper, symbolic word overlay, dramatic pose, changed position, new element, motion blur, speed lines, action lines, dynamic angle"
}
```

### Silent page 1, panel 2 — detail beat — panel 9-4-2

```json
{
  "panel_id": "9-4-2",
  "page_type": "silent",
  "silence_compliance": true,
  "prompt_token_count": 58,
  "prompt": "clean ink line 0.8pt weight, screentone shading, late 90s shonen manga aesthetic, black and white, high contrast, extreme close-up, hands fill frame, palms up resting on knees, open hands doing nothing, bruised right knuckles visible, extreme detail, texture of skin, material weight, quiet focus, no face visible, no expression, only hands, flat light from above, stillness",
  "negative_prompt": "[full silence prohibition list] + face, eyes, expression, dramatic lighting, symbolic overlay"
}
```

### Silent page 2, panel 1 — world beat — panel 9-5-1

```json
{
  "panel_id": "9-5-1",
  "page_type": "silent",
  "silence_compliance": true,
  "prompt_token_count": 65,
  "prompt": "clean ink line 0.8pt weight, screentone shading, late 90s shonen manga aesthetic, black and white, high contrast, exterior shot through window glass, Kai seen from outside, small figure in midground, city visible behind viewer, ordinary world continues, ambient exterior night light, apartment_interior_kai asset_id, window frame, character small in frame, world goes on without him, wide establishing, no drama, no focus on character",
  "negative_prompt": "[full silence prohibition list] + character centered, dramatic focus, vignette, dark overlay, character large in frame"
}
```

### Silent page 3, panel 1 — return beat — panel 9-6-1

```json
{
  "panel_id": "9-6-1",
  "page_type": "silent",
  "silence_compliance": true,
  "prompt_token_count": 73,
  "prompt": "clean ink line 0.8pt weight, screentone shading, late 90s shonen manga aesthetic, black and white, high contrast, medium shot, same location as 9-4-1, same wall, same light, Kai seated, lora:kai_v2, subtle shift: head now forward, looking at hands not ceiling, same body position otherwise, same room, same clothes, slight change in gaze direction only, bruised right knuckles, disheveled hair, first time eyes are focused not vacant, present not resolved",
  "negative_prompt": "[full silence prohibition list] + transformation, dramatic change, hopeful expression, standing, new location, new outfit, healed knuckles"
}
```

### Style lock verification — silent sequence

Series style tokens: present in all 5 panels. LoRA reference: injected in all character panels. Prohibited style terms: absent from all positive prompts, present in all negative prompts. Silence text prohibition: applied to all silence_compliance panels. Silence_guard core subset: applied to panel 9-3-5. Continuity: bruised right knuckles carried through all 5 panels. No new meaning: 7-point scan passed — no elements introduced not present in script. Camera progression: medium → medium (same) → close-up → wide → medium. Five-beat protocol: arrival → stillness → detail → world → return. Token budget: all panels under 120 tokens. All gates pass.

---

## 9. Quality Gates — Prompt Level

| Gate | Pass condition | Check method | Fail action |
|---|---|---|---|
| **Style token completeness** | Every panel's prompt begins with the complete `series_style_tokens` set in the specified order. No tokens missing, no tokens reordered, no tokens added. | Token prefix scan on every prompt | Regenerate prompt with full token set. Flag to Visual Identity Agent if token set requires update. |
| **Prohibited style terms** | No word from `series_prohibited_style_terms` appears in any positive prompt across the chapter. | Automated text scan — positive prompts only | Remove prohibited term. If scene requirement makes it unavoidable, escalate to Visual Identity Agent for style bible update. |
| **Character reference injection** | Every panel containing a named character includes their LoRA ID or model sheet reference. Zero panels with named characters generated without reference. | `character_refs` array non-empty check for named-character panels | Halt generation. Inject reference. Regenerate panel. |
| **Silence purity** | Every panel with `silence_compliance = true` has zero text-requesting terms in its positive prompt and includes the full silence prohibition list in its negative prompt. | Silence text scan on positive prompts + negative prompt prohibition list check | Remove text terms from positive prompt. Add missing prohibitions to negative prompt. Regenerate. |
| **Silence guard compliance** | Every panel with `silence_guard = true` includes at minimum the core text prohibition terms in its negative prompt (text, signage, written words, speech bubbles, caption box, SFX lettering, onomatopoeia). | Guard panel negative prompt check | Add missing prohibitions. Regenerate. |
| **Camera fidelity** | Each panel's `camera_prompt_term` is the exact translation specified in the `camera_lexicon` for the script's camera value. No camera term has been interpreted, substituted, or invented. | `camera_lexicon` lookup crosscheck | Replace with correct lexicon translation. Regenerate. |
| **No new meaning** | 7-point violation scan passes. No prompt element introduces a subject, character, object, lighting, or location not present in `panel.action`, `panel.subject`, `panel.background`, or `asset_refs`. | Prompt element vs script field crosscheck (7-point checklist §6) | Remove non-script element. If element is legitimate background detail, add to `asset_refs` and recheck. |
| **Continuity consistency** | Character injuries, outfit IDs, hair states, and props match the `continuity_state` at that panel's position in the chapter. Healed injury before healing event = violation. | `continuity_state` vs prompt `continuity_injections` crosscheck | Correct `continuity_injections`. Regenerate panel. |
| **Asset reuse** | Every recurring location, prop, or motif uses its `asset_registry` ID reference, not a freeform description. Same location looks the same across all chapters. | Asset mention scan vs `asset_registry` lookup | Replace description with `asset_id` reference. If asset not in registry, flag as `new_asset` and create before generation. |
| **Drift detection** | Every 10 panels: style token application in current panel matches style token application in panel 1 of chapter. No token drift, no prohibited term creep. | 10-panel interval style scan | Set `drift_warning` flag. Audit previous 10 panels. Regenerate drifted panels. |
| **Five-beat silence structure** | Every silent page sequence of 2+ pages follows camera progression: arrival (medium, same as pre-silence) → stillness (medium, unchanged) → detail (close-up, no face) → world (wide) → return (medium, subtle shift). Verifiable from camera values. | Camera sequence check on silent page runs | Restructure silent page camera sequence. Regenerate affected panels. |
| **Token budget** | Every positive prompt ≤ 120 tokens. Every negative prompt ≤ 60 tokens. | `prompt_token_count` field check | Apply overflow policy (§3.4). Regenerate. |

---

*SpiritualTech Systems · Visual Agent Spec v1.1 · Confidential*
