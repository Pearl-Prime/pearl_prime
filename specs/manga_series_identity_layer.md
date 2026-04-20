# Manga Series Identity Layer — Architecture Spec

**Version:** 1.0
**Date:** April 2026
**Workstream:** 4
**Authority:** Pearl_Architect
**Status:** Spec draft
**Classification:** Confidential

---

## Overview

The Series Identity Layer is a pre-production initialization step that runs **once per series, before any chapter is written**. It generates the complete branded identity of a manga series — title, logline, volume plan, cover art specs, character roster, setting bible, and recurring motifs — from a brief human-supplied seed prompt.

Every downstream agent (Story Architect, Visual Identity Agent, Genre Agent, Cover Art Agent, QC Agent) receives the `series_identity.yaml` as authoritative context. Nothing in it is overridden at chapter time.

---

## Integration Map

This layer slots into the pipeline **before Stage 2 (Prompt Generation)** defined in `MANGA_PRODUCTION_PIPELINE_SPEC.md`. It adds a new Stage 0:

```
STAGE 0: SERIES IDENTITY INITIALIZATION (NEW — runs once per series)
  └── Input: series_seed_prompt + brand_id + genre + locale
  └── Output: series_identity.yaml → stored at
              config/source_of_truth/manga_series/<series_id>/series_identity.yaml

STAGE 1: BATCH COMPOSITION & VALIDATION (existing)
  └── Now also validates: series_identity.yaml exists and is valid for every series_id in batch

STAGE 2: PROMPT GENERATION (existing — extended)
  └── Story Architect, Visual Identity Agent, Genre Agent now load series_identity.yaml
  └── Series identity context injected alongside Series Bible and Brand DNA
```

### Dependency Chain (non-negotiable order)

```
SERIES_IDENTITY_INIT          (Stage 0, this layer)
  ↓
CHARACTER_SHEET_BUILD          (Workstream 5 — runs after identity is locked)
  ↓
BATCH_COMPOSITION              (Stage 1 — series_identity.yaml must exist)
  ↓
PROMPT_GENERATION              (Stage 2 — agents load identity)
  ↓
IMAGE_GENERATION               (Stage 3 — panel prompts reference character sheets)
  ↓
LAYOUT & COMPOSITION           (Stage 4)
  ↓
BATCH QC                       (Stage 5 — validates identity compliance)
```

---

## 1. Trigger & Invocation

### 1.1 When it runs

Series Identity Initialization runs:
- Once, when a `series_id` is first registered in the production system
- Never re-runs mid-series (the identity is locked at v1.0)
- May re-run at v2.0 only if a formal series revision is approved by Pearl_PM

### 1.2 Invocation

```bash
python3 scripts/manga/series_identity_init.py \
  --series-id "garden_at_tidecalm_001" \
  --brand-id "stillness_press" \
  --genre "iyashikei" \
  --locale "en" \
  --seed-prompt "iyashikei manga about a girl who discovers a garden has memories"
```

### 1.3 LLM generation

The init script calls the Claude API with a structured prompt that:
1. Loads the brand's `brand_dna.yaml` (visual DNA, therapeutic category, persona targets)
2. Loads the series' assigned `series_bible.yaml` (therapeutic wound, wisdom atoms, arc structure)
3. Loads the genre conventions for the target genre
4. Constructs a generation prompt asking Claude to produce all identity fields
5. Validates the output against the `series_identity_schema.yaml`
6. Writes the validated YAML to the canonical location

The generation is **not freestyle** — Claude fills a structured schema, not an open narrative brief. Every field is constrained by type, length, and cross-reference to brand/genre/bible.

---

## 2. Output Schema: `series_identity.yaml`

### Storage path

```
config/source_of_truth/manga_series/<series_id>/series_identity.yaml
```

### Full schema

```yaml
schema_version: "1.0"
artifact_type: "series_identity"

# ── Core Identification ──────────────────────────────────────────────
series_id: "garden_at_tidecalm_001"
brand_id: "stillness_press"                  # ref: brand_registry.yaml
series_bible_id: "series_005_the_outsiders_room"  # ref: which series bible governs
genre: "iyashikei"
locale: "en"
locked_date: null                             # set when Pearl_PM approves
locked_by: null                               # agent or human who approved

# ── Marketing Identity ────────────────────────────────────────────────
marketing_title: "The Garden at Tidecalm"
subtitle: "A Manga About the Memory in Growing Things"
logline: >
  A girl who cannot sit still discovers that an old coastal garden
  remembers everyone who ever tended it — and needs her to remember herself.

high_concept: >
  Sora is a 17-year-old who moves to her grandmother's seaside village
  and inherits a neglected garden she doesn't want. The garden, it turns out,
  holds emotional echoes of everyone who ever worked in it. As Sora tends each
  plant, she receives fragments of strangers' feelings — grief, relief, love,
  exhaustion — and slowly learns to sit still with her own.

tagline: "Some places remember for you."

back_cover_blurb: >
  Sora doesn't do slow. She doesn't do quiet. She definitely doesn't do gardens.
  But the old plot behind her grandmother's house in Tidecalm has been waiting —
  and it turns out it has things to say.

  For readers who loved Yotsuba&! and Flying Witch.
  A manga about anxiety, presence, and the startling patience of growing things.

comparable_titles:
  - "Yotsuba&! — grounded curiosity, episodic warmth"
  - "Flying Witch — quiet magic, rural atmosphere"
  - "Mushishi — memory embedded in the natural world"
  - "A Silent Voice — emotional weight carried gently"

# ── Volume Plan ──────────────────────────────────────────────────────
volume_plan:
  chapters_per_volume: 8
  total_planned_volumes: 3
  total_planned_chapters: 24

  volumes:
    volume_1:
      arc_name: "Awakening Arc"
      chapters: "1-8"
      arc_summary: >
        Sora arrives resistant and restless. She begins tending the garden
        reluctantly. The first emotional memories surface — light ones:
        a child's excitement, an old man's quiet pride. By chapter 8,
        she has stopped fighting the slowness.
      cover_mood: "cool morning light, overgrown, potential"
      therapeutic_focus: "noticing resistance; first contact with stillness"

    volume_2:
      arc_name: "Deepening Arc"
      chapters: "9-16"
      arc_summary: >
        Heavier memories surface — grief, abandonment, unfinished love.
        Sora must sit with others' pain without running. She begins to
        understand why she herself cannot stop moving. A mentor character
        (the village herbalist) appears at chapter 10.
      cover_mood: "full summer, lush, shadows"
      therapeutic_focus: "containment; witnessing difficulty without escape"

    volume_3:
      arc_name: "Integration Arc"
      chapters: "17-24"
      arc_summary: >
        The garden blooms. Sora does not conquer her anxiety but learns to
        tend it the way she tends the plants — with patience, repetition,
        and trust in slow growth. Final chapter: she plants something new.
      cover_mood: "autumn warmth, harvest, completion without conclusion"
      therapeutic_focus: "integration; choosing presence as ongoing practice"

# ── Cover Art Specification (per volume) ────────────────────────────
cover_art_specs:
  volume_1:
    flux_prompt: >
      Iyashikei manga cover, soft watercolor wash, early morning coastal light,
      teenage girl with short dark hair seen from behind, standing at the edge
      of an overgrown garden, stone wall, sea visible in distance, pastel blue
      and green palette, gentle fog, sense of threshold and potential,
      Japanese manga cover composition, title space at top,
      no text in image, clean edges, soft focus background
    mood: "arrival, threshold, gentle unease"
    palette: ["coastal_blue", "morning_mist", "weathered_stone", "new_green"]
    composition: "figure from behind, center frame, garden receding, sea at edge"
    reference_character: "sora_front_reference"   # from character sheet system

  volume_2:
    flux_prompt: >
      Iyashikei manga cover, lush summer garden, full green canopy,
      teenage girl sitting cross-legged among plants, eyes closed,
      warm afternoon light filtering through leaves, soft shadow patterns,
      green and gold palette, sense of weight and peace coexisting,
      Japanese manga cover composition, title space at top
    mood: "immersion, weight, sitting with difficulty"
    palette: ["deep_summer_green", "afternoon_gold", "shadow_grey", "soil_brown"]
    composition: "figure small within environment, environment dominant"
    reference_character: "sora_sitting_reference"

  volume_3:
    flux_prompt: >
      Iyashikei manga cover, autumn coastal garden, warm harvest light,
      teenage girl kneeling to plant a seedling, hands in soil,
      fallen leaves, amber and rust palette, feeling of completion
      that opens rather than closes, Japanese manga cover composition
    mood: "resolution, tenderness, beginning again"
    palette: ["autumn_amber", "harvest_rust", "earth_warmth", "sky_clear"]
    composition: "close on hands and seedling, figure from above-angle"
    reference_character: "sora_kneeling_reference"

# ── Character Roster ─────────────────────────────────────────────────
characters:
  sora_hashimoto:
    character_id: "sora_hashimoto"
    role: "protagonist"
    age: 17
    archetype_hook: "The girl who cannot stop — learns to stop"
    therapeutic_function: "embodies anxiety as restlessness and avoidance"

    visual_archetype: >
      Short dark hair cut unevenly (self-done), wiry build, always in motion.
      Oversized jacket she wears even in warm weather (sensory regulation).
      Hands perpetually busy — picking at things, fidgeting.
      Posture: forward-leaning, coiled, ready to leave.
    visual_evolution: >
      By volume 3: posture opens. Jacket taken off more often.
      Hands sometimes simply rest. The change is gradual and never announced.
    signature_visual_element: "the jacket; fidgeting hands; soil on her fingers by volume 2"

    relationships:
      - character_id: "uma_nakamura"
        relationship: "grandmother, initial antagonist-through-kindness"
      - character_id: "tarou_village_herbalist"
        relationship: "mentor, appears volume 2"
      - character_id: "hana_neighbor_girl"
        relationship: "peer, mirror character (stillness as default)"

  uma_nakamura:
    character_id: "uma_nakamura"
    role: "supporting — grandmother"
    age: 72
    archetype_hook: "The one who waits without waiting"
    therapeutic_function: "models unconditional presence; does not try to fix Sora"
    visual_archetype: >
      Round face, soft white hair in loose bun, slow deliberate movements.
      Always doing something small: folding cloth, trimming plants, making tea.
      Communicates more in gesture than words.
    signature_visual_element: "always has something in her hands; never still but never rushed"

  tarou_yamashiro:
    character_id: "tarou_yamashiro"
    role: "supporting — village herbalist/mentor"
    age: 58
    archetype_hook: "The one who stopped running (mirror of who Sora can become)"
    therapeutic_function: "embodies integration; arrived at stillness through the same door"
    visual_archetype: >
      Weathered, lean, moves unhurriedly. Former city dweller — small tells remain
      (good shoes, a watch he no longer checks). Introduces himself by what he grows.
    appearance_chapters: "volume 2 onward (chapter 10+)"

  hana_mori:
    character_id: "hana_mori"
    role: "supporting — neighbor peer"
    age: 16
    archetype_hook: "Stillness as native state — Sora's foil"
    therapeutic_function: "shows that stillness is not absence of feeling but different relationship to it"
    visual_archetype: >
      Tall, unhurried, comfortable silences. Reads while walking (somehow never trips).
      Brown hair in pigtails, oversized cardigan, soft shoes.
    note: "not a static character — her stillness is earned, not empty; this emerges across volumes"

# ── Setting Bible ────────────────────────────────────────────────────
setting_bible:
  primary_location:
    name: "Tidecalm"
    type: "small coastal village, fictionalized Japanese setting"
    atmosphere: >
      Quiet but not dead. The kind of quiet that has weight. The sea is always
      audible but rarely visible — heard through walls, through gardens, through
      the space between sentences. Fog is common in the morning. Light is soft.
    key_visual_descriptors:
      - "weathered wood and stone"
      - "plants growing into walls, softening edges"
      - "salt air makes colors slightly muted"
      - "morning fog, afternoon clarity, dusk gold"

  locations:
    uma_garden:
      location_id: "uma_garden"
      name: "Uma's Garden"
      function: "primary setting, therapeutic container"
      visual_description: >
        Walled garden behind Uma's house, roughly 20 meters square.
        Overgrown at series start. Stone walls. A wooden bench Uma built
        decades ago and never moved. A water trough. An old tool shed.
        View of sea from the east corner.
      seasonal_evolution:
        volume_1: "overgrown, surprising pockets of bloom"
        volume_2: "clearing begun, structure visible under chaos"
        volume_3: "tended, seasonal, alive and organized"
      establishing_shot_notes: >
        Wide shot from the house looking out shows the full scale.
        Close shots emphasize texture: moss, stone, leaf edges.
      reference_location: "uma_garden_establishing"  # from setting sheet system

    uma_kitchen:
      location_id: "uma_kitchen"
      name: "Uma's Kitchen"
      function: "transition space, conversation, warmth"
      visual_description: >
        Small, functional, light through a south-facing window.
        Herbs drying from the ceiling. Tea always in process.
        A wooden table where Sora and Uma's most important conversations happen
        without being about the important thing.

    village_path:
      location_id: "village_path"
      name: "The Path to the Harbor"
      function: "Sora's movement space, transition between inner and outer"
      visual_description: >
        Narrow, slightly overgrown path, stone underfoot. Five minutes between
        Uma's house and the small harbor. This walk appears in every volume.
        Its visual detail changes with Sora's inner state.

# ── Recurring Visual Motifs ─────────────────────────────────────────
recurring_motifs:
  visual:
    garden_hands:
      motif_id: "garden_hands"
      description: "Sora's hands in soil, on tools, touching plants"
      symbolic_meaning: "contact with the present; anxiety transforming into care"
      appearance_schedule: "first appears chapter 3; deepens every volume"

    morning_fog:
      motif_id: "morning_fog"
      description: "Soft fog over the garden at dawn, before full visibility"
      symbolic_meaning: "uncertainty as texture, not threat; not-knowing as livable state"
      appearance_schedule: "opens almost every chapter 1-16; rare in volume 3 (clarity earned)"

    the_jacket:
      motif_id: "the_jacket"
      description: "Sora's oversized jacket — worn, removed, folded, left behind"
      symbolic_meaning: "armoring and opening; the arc of anxiety management visible in one garment"
      tracking: "jacket on = defended; jacket off = present; first jacket-off moment: chapter 9"

    plant_close_ups:
      motif_id: "plant_close_ups"
      description: "Extreme close-ups of individual plants, textures, small growing details"
      symbolic_meaning: "attention as practice; the small as worthy; presence as looking closely"
      frequency: "at least one per chapter throughout entire series"

    sea_sound_panels:
      motif_id: "sea_sound_panels"
      description: "Silent panels with only a small SFX notation for sea sound (shaa... or nami...)"
      symbolic_meaning: "the constant beneath the noise; continuity across anxiety episodes"
      frequency: "at least one per chapter; increases in volume 3"

  thematic:
    slow_growth:
      description: "Nothing in this manga happens suddenly. Change is shown through accumulation."
      narrative_rule: "No chapter has a breakthrough moment. Progress is visible only in retrospect."

    memory_as_gift:
      description: "The garden's emotional memories are not burdens but offerings"
      narrative_rule: "Memories Sora receives from the garden are always handled with care, not horror"

    stillness_is_active:
      description: "Stillness in this series is something you DO, not something that happens to you"
      narrative_rule: "Quiet moments show Uma and Hana actively engaged with being present, not passive"

# ── Genre & Demographic Targeting ───────────────────────────────────
genre_targeting:
  primary_genre: "iyashikei"
  secondary_genre: "slice_of_life"
  tertiary_genre: "psychological_light"
  demographic: "josei / seishun (15-30 female-leaning readership)"
  age_band: "13-30"
  psychographic: "anxiety-adjacent readers; burnout-adjacent; nature-seeking urbanites"
  platform_fit:
    primary: ["Webtoon", "Kindle", "Kobo"]
    secondary: ["Print (niche collector)"]
    not_suitable: ["Shonen Jump+ (wrong demographic)", "action platforms"]
  content_rating: "all-ages (no romance, no violence, no mature themes)"

# ── Comparable Titles (for catalog positioning) ──────────────────────
comparable_titles:
  reads_like:
    - title: "Yotsuba&!"
      shared_quality: "slice-of-life warmth; episodic wonder; adult themes rendered gently"
    - title: "Flying Witch"
      shared_quality: "rural Japan; quiet magic; found-family atmosphere; no urgency"
    - title: "Mushishi"
      shared_quality: "nature-embedded mystery; slow pacing; healing-adjacent"
  differentiator: >
    Unlike Yotsuba&! and Flying Witch, this series is explicitly anxiety-therapeutic.
    The emotional mechanics are intentional, not ambient. Readers with anxiety histories
    will recognize the internal experience being depicted with accuracy.

# ── Generation Provenance ─────────────────────────────────────────────
generation_metadata:
  seed_prompt: "iyashikei manga about a girl who discovers a garden has memories"
  generated_by: "series_identity_init.py v1.0"
  generation_model: "claude-opus"
  generation_date: null   # filled at generation time
  generation_hash: null   # filled at generation time; sha256 of output
  brand_dna_version: "1.0"
  series_bible_version: "1.0"
  validation_status: "pending"  # pending | validated | locked
  approved_by: null
```

---

## 3. Generation Prompt Architecture

When `series_identity_init.py` calls Claude, it constructs a prompt with this structure:

```
SYSTEM: You are Pearl_Architect generating a series_identity.yaml for a manga series.
        You MUST fill every field in the provided schema. You MUST NOT invent brand DNA
        or genre conventions — all visual and therapeutic parameters come from the
        loaded configs. Your output must be valid YAML that passes the schema validator.

CONTEXT BLOCK 1 — BRAND DNA:
  [contents of brand_dna.yaml for brand_id]

CONTEXT BLOCK 2 — SERIES BIBLE:
  [relevant sections: therapeutic_framework, narrative_structure, character_design_principles]

CONTEXT BLOCK 3 — GENRE CONVENTIONS:
  [genre definition from style_archetypes.yaml for target genre]

CONTEXT BLOCK 4 — SEED PROMPT:
  "{user-supplied seed prompt}"

TASK:
  Generate a complete series_identity.yaml using the schema below.
  All fields marked REQUIRED must be non-empty.
  Characters must be consistent with the therapeutic_framework.
  Visual motifs must be consistent with brand DNA.
  Comparable titles must be real published manga.

SCHEMA: [full series_identity_schema.yaml pasted here]
```

---

## 4. Validation Rules

After generation, `series_identity_validate.py` checks:

```yaml
validation_rules:
  schema_completeness:
    - All required fields non-empty
    - character roster has >= 2 characters
    - volume_plan.total_planned_chapters is integer > 0
    - cover_art_specs exists for each volume in volume_plan

  cross_reference_integrity:
    - brand_id exists in brand_registry.yaml
    - series_bible_id exists in series bibles
    - genre matches brand.genre_affinity (primary or secondary)

  narrative_coherence:
    - logline is 1 sentence, <= 40 words
    - high_concept is 2-4 sentences
    - back_cover_blurb is 2-4 paragraphs
    - arc_summary per volume is 3-6 sentences

  character_rules:
    - protagonist has character_id, archetype_hook, visual_archetype
    - no character_id duplicates within roster
    - visual_archetype is >= 30 words (enough to generate from)

  motif_rules:
    - at least 3 visual motifs defined
    - each motif has motif_id, symbolic_meaning, appearance_schedule

  cover_art_rules:
    - each cover flux_prompt is >= 50 words
    - palette defined as list of 3-5 named colors
    - reference_character references a valid character_id from roster
```

---

## 5. Storage & Access Pattern

```
config/
└── source_of_truth/
    └── manga_series/
        ├── _schema.yaml                         # JSON Schema for validation
        ├── garden_at_tidecalm_001/
        │   ├── series_identity.yaml             # THE output of this layer
        │   └── series_identity_lock.yaml        # written when Pearl_PM approves; contains hash
        ├── boy_who_stopped_running_001/
        │   └── series_identity.yaml
        └── ...
```

### Who reads `series_identity.yaml`

| Consumer | What they read | Purpose |
|----------|---------------|---------|
| Story Architect | marketing_title, logline, characters, recurring_motifs, volume_plan | Narrative continuity and motif deployment |
| Visual Identity Agent | characters[].visual_archetype, recurring_motifs, setting_bible | Panel visual prompts and consistency |
| Genre Agent | genre_targeting, comparable_titles, recurring_motifs.thematic | Genre convention enforcement |
| Cover Art Agent | cover_art_specs[volume] | Volume cover FLUX prompt generation |
| Character Sheet Builder | characters[] | Input for Workstream 5 character sheet generation |
| QC Agent | full document | Validates chapter output against identity |
| Distribution / Metadata | marketing_title, logline, back_cover_blurb, comparable_titles | Kobo/Amazon metadata fields |

---

## 6. Locking Protocol

The series identity is **locked** (made immutable) when Pearl_PM approves it:

```
State 1: generated      — validation_status: "pending"
State 2: validated      — validation_status: "validated" (auto, after schema pass)
State 3: locked         — validation_status: "locked", locked_date set, locked_by set
                          series_identity_lock.yaml written with sha256 of identity file
State 4: deprecated     — only if series is retired; locked file preserved
```

Any attempt to run `series_identity_init.py` for a `series_id` that already has a locked identity will fail with:

```
ERROR: Series identity for 'garden_at_tidecalm_001' is locked (v1.0, 2026-04-15).
       To revise, use --force-revision flag and supply Pearl_PM approval token.
```

---

## 7. What This Spec Does NOT Cover

- Character sheet image generation (covered in `manga_character_setting_consistency.md`)
- Story arc beat-by-beat narrative (covered in `MANGA_SERIES_BIBLE_SPEC.md`)
- Brand visual DNA (covered in `MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md`)
- Anti-spam / series differentiation (covered in `MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md`)
- Manga author persona (covered in `MANGA_AUTHOR_SYSTEM_SPEC.md`)

The Series Identity Layer is the **marketing and narrative surface** of the series — the first impression, the label on the bottle. The Series Bible is the therapeutic architecture inside it. Both must exist and align.

---

*SpiritualTech Systems · Manga Series Identity Layer Spec v1.0 · Confidential*
