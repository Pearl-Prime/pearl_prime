# SpiritualTech Systems: Brand DNA & Anti-Spam Specification

**Version:** 1.0
**Date:** March 2026
**Audience:** Product Engineering, QA, Brand Partners
**Classification:** Confidential

---

## Executive Summary

The Brand DNA & Anti-Spam system ensures that each of the 30 therapeutic brands produces visually and narratively distinct manga across all production runs. Brand DNA is NOT story content governance—it is the visual and production DNA that makes a book unmistakably recognizable as belonging to a specific therapeutic brand, locale, and production context.

Each brand receives a unique "fingerprint" composed of visual style parameters, lettering conventions, production constraints, and anti-spam safeguards. This prevents visual duplication, content homogenization, and replication attacks while preserving therapeutic integrity.

---

## 1. Brand DNA Schema

### 1.1 Core Brand Identity

```yaml
brand:
  brand_id: "brand_001"
  brand_name: "Stillness Harbor"
  therapeutic_category: "anxiety"
  brand_descriptor: "compassionate Buddhist-informed manga for anxiety management"

  target_personas:
    - "anxious_millennials_urban"
    - "burnout_professionals"
    - "somatic_awareness_seekers"

  genre_affinity:
    primary: ["slice_of_life", "psychological"]
    secondary: ["drama", "philosophical"]
    avoid: ["action_heavy", "thriller"]
```

### 1.2 Visual Style Parameters

Every brand encodes a unique visual DNA that distinguishes it from all other 29 brands across linework, shading, color rendering, and era authenticity.

#### Linework Signature
```yaml
visual_style:
  linework:
    stroke_weight: "medium"  # light | medium | heavy
    ink_consistency: "variable"  # uniform | variable | gestural
    line_quality: "clean_meditative"
    cross_hatching_density: 0.3  # 0-1 scale
    fluidity_score: 0.7  # how much line wobble/humanity
    signature_technique: "ink_wash_transitions"  # brand-specific line treatment
```

#### Shading System
```yaml
  shading:
    primary_method: "screentone"  # screentone | watercolor | charcoal | digital_gradient | none
    tone_palette: ["black", "50pct_grey", "20pct_grey"]
    shadow_intensity: "soft"  # soft | medium | high
    highlight_style: "minimal_white_space"
    depth_rendering: "atmospheric"  # flat | atmospheric | sculptural
```

#### Color Mode & Rendering Era
```yaml
  color_mode: "limited_palette"  # full_color | two_tone | limited_palette | grayscale
  primary_colors: ["calm_blue", "warm_beige", "deep_grey"]
  rendering_era: "early_2000s_digital"  # matches therapeutic accessibility + authenticity
  color_symbolism:
    - silence: "soft_white_negative_space"
    - breath: "pale_blue_gradients"
    - grounding: "earth_tones_ochre"
    - healing: "soft_greens"
```

### 1.3 Lettering & Typography Style

Lettering style controls not story voice but visual presentation consistency: bubble shapes, font families, SFX rendering, and reading direction adaptation.

```yaml
lettering_style:
  bubble_shapes:
    dialogue: "soft_rounded_rectangle"  # defines bubble boundary
    internal_monologue: "rounded_cloud"
    narration: "rectangular_clean"
    emotion: "jagged_but_contained"

  font_families:
    dialogue_primary: "Komika_Axis"  # readable, approachable
    internal_monologue: "Sohne_Light"  # introspective
    sfx: "Custom_SFX_Dharma"  # custom SFX font library

  bubble_positioning:
    emotion_height: 0.15  # how high bubbles sit on page
    reading_rhythm: "natural_pause_weight"  # allows somatic time
    silence_tolerance: "generous"  # white space breathing room

  sfx_style_set:
    - heartbeat: "soft_radiating_circles"
    - breath: "gentle_wave_notation"
    - silence: "empty_space_dominant"
    - footstep: "subtle_path_mark"
    - inner_voice: "whisper_italics_soft"

  locale_adaptations:
    ja: "right_to_left, vertical_option"
    en: "left_to_right, horizontal_only"
    es: "left_to_right, flow_adjusted"
    pt: "left_to_right, rhythm_adapted"
    de: "left_to_right, spacing_expanded"
    fr: "left_to_right, elegance_markers"
    zh: "vertical_or_horizontal, traditional_simplified"
    ko: "left_to_right, rhythm_markers"
    it: "left_to_right, pause_length_extended"
    ru: "left_to_right, letter_spacing_wide"
    ar: "right_to_left, diacritical_centered"
```

### 1.4 Production Parameters & Constraints

These parameters control how this brand's books are produced at scale, preventing homogenization and enabling diversity.

```yaml
production_parameters:
  series_affinity:
    weighted_series:
      - series_id: "the_boy_who_stopped_running"
        weight: 0.4
      - series_id: "grieflight_atlas"
        weight: 0.3
      - series_id: "identity_crossing"
        weight: 0.2
      - series_id: "relational_root"
        weight: 0.1

  locale_distribution:
    primary_locales: ["en", "ja"]
    secondary_locales: ["es", "de", "fr"]
    tertiary_locales: ["pt", "zh", "ko", "it", "ru", "ar"]

  anti_spam_constraints:
    min_visual_distance_from_brands: ["brand_002", "brand_007"]  # don't produce in same batch
    max_books_same_genre_per_batch: 1  # prevents genre clustering
    max_books_same_locale_per_month: 3  # distribution across time
    min_visual_style_variance: 0.6  # 0-1, forces visual iteration
    forbidden_combinations: [
      { genre: "action", locale: "ja", reason: "brand_affinity_low" },
      { series: "s5", locale: "ar", reason: "insufficient_localization_support" }
    ]

  silence_weight:
    somatic_silence_intensity: 0.8  # how much negative space this brand tolerates
    panels_per_page_range: [3, 8]  # page density distribution
    ma_spacing_premium: true  # prioritize Ma negative space
    breathing_room_required: true  # pages must have breath
```

### 1.5 Persona Targeting

```yaml
persona_targets:
  - persona_id: "p_anxiety_01"
    name: "Urban Professional with Generalized Anxiety"
    therapeutic_need: "somatic_grounding"
    manga_resonance_markers: ["realistic_settings", "internal_dialogue_heavy", "slow_pacing"]

  - persona_id: "p_anxiety_02"
    name: "Anxious Parent Managing Overwhelm"
    therapeutic_need: "permission_to_pause"
    manga_resonance_markers: ["relatable_family_dynamics", "humor_gentle", "resolution_possible"]

  - persona_id: "p_anxiety_03"
    name: "Somatic Awareness Practitioner"
    therapeutic_need: "metaphor_for_practice"
    manga_resonance_markers: ["sensory_detail", "internal_landscape", "embodied_language"]
```

---

## 2. The 30-Brand Therapeutic Matrix

The 30 brands are distributed across therapeutic categories, ensuring diversity of approach and cultural authenticity.

### 2.1 Therapeutic Category Map

```
ANXIETY DISORDERS (6 brands):
  - Stillness Harbor (Buddhist, grounding)
  - Breath Returning (somatic nervous system)
  - Golden Moment (mindfulness accessible)
  - Threshold Keeper (anxiety + identity)
  - Night Caller (insomnia, sleep anxiety)
  - Spiral Return (panic + somatic)

GRIEF & LOSS (5 brands):
  - Grieflight Atlas (universal loss, non-dogmatic)
  - Ancestral Echo (intergenerational grief)
  - Seasonal Threshold (grief in time)
  - Tender Remains (object + place grief)
  - Unfinished Conversation (relational loss)

BURNOUT & EXHAUSTION (4 brands):
  - The Boy Who Stopped Running (primary burnout, Buddhist)
  - Ember Keeper (slow restoration)
  - Boundary Tender (saying no gently)
  - Rest is Resistance (systemic exhaustion)

IDENTITY & BELONGING (5 brands):
  - Mirror Crossing (gender identity, affirming)
  - Rooted Becoming (cultural identity, diaspora)
  - The Outsider's Room (social anxiety + identity)
  - Found Family (belonging non-biological)
  - Sacred Skin (body image, disability affirmation)

RELATIONAL WOUNDS (4 brands):
  - Relational Root (attachment, secure base)
  - Conversations Tender (conflict resolution, non-violent)
  - Betrayal Mosaic (trust repair)
  - Love After Harm (healing relationships post-trauma)

SOMATIC & EMBODIMENT (3 brands):
  - Felt Sense (Gendlin-inspired somatic therapy)
  - Breath Becomes Path (breathwork, pranayama)
  - Nervous System Stories (polyvagal theory accessible)

TRAUMA-INFORMED (2 brands):
  - Safe Ground (trauma recovery, choice-centered)
  - Threshold Guardian (dissociation, grounding)

CROSS-CUTTING / SECULAR DHARMA (1 brand):
  - Dharma Commons (secular Buddhist, all ages)
```

---

## 3. Anti-Spam Mechanisms

### 3.1 Visual Fingerprinting

Each brand encodes unique style_tokens that make books visually distinct across the 1,000-book corpus.

```yaml
visual_fingerprinting:
  style_tokens:
    brand_001_stillness_harbor:
      - token: "soft_screentone_waves"
        frequency: 0.65  # % of panels using this technique
        distinctiveness_score: 0.92

      - token: "rounded_bubble_cloud_shape"
        frequency: 0.45
        distinctiveness_score: 0.78

      - token: "pale_blue_limited_palette"
        frequency: 0.70
        distinctiveness_score: 0.88

      - token: "minimalist_sfx_whisper_style"
        frequency: 0.55
        distinctiveness_score: 0.91

      - token: "atmospheric_depth_soft_shading"
        frequency: 0.62
        distinctiveness_score: 0.85

  fingerprint_hash:
    method: "visual_signature_composite"
    components: ["color_histogram", "line_density_map", "bubble_shape_ratio", "sfx_style_distribution"]
    expected_uniqueness: 0.95  # 95% dissimilar from other brands
```

### 3.2 Content Variation Strategy

The same wisdom atom produces 30 different manga across the 30 brands because each brand brings its own visual, narrative, and cultural lens.

```yaml
content_variation:
  example_atom: "impermanence"

  brand_001_interpretation:
    visual_angle: "subtle_seasonal_shift_in_urban_setting"
    narrative_vehicle: "protagonist_notices_changing_weather_pattern"
    cultural_frame: "Buddhist_contemporary_mindfulness"
    sfx_treatment: "gentle_wind_notations"

  brand_015_interpretation:
    visual_angle: "ancestral_lineage_visible_in_photographs"
    narrative_vehicle: "character_discovers_old_family_photos"
    cultural_frame: "African_diaspora_ancestral_presence"
    sfx_treatment: "soft_heartbeat_memory_markers"

  brand_024_interpretation:
    visual_angle: "body_changing_through_medical_transition"
    narrative_vehicle: "transgender_protagonist_documents_physical_shifts"
    cultural_frame: "transgender_joy_and_embodiment"
    sfx_treatment: "internal_monologue_affirming_language"

  rule: "same_wisdom_atom → 30_unique_visual_treatments → 30_distinct_books"
```

### 3.3 Locale Variation Mechanism

Same story concept adapted per locale with locale-specific lettering, SFX translation, reading direction, and cultural adaptation.

```yaml
locale_variation:
  base_concept: "protagonist_learns_to_sit_with_discomfort"

  ja_locale:
    reading_direction: "right_to_left"
    sfx_language: "Japanese_onomatopoeia"
    cultural_frame: "Zen_temple_setting"
    lettering_bubble_shape: "traditional_cloud_soft"
    color_treatment: "muted_earth_tones_ink_brush"

  en_locale:
    reading_direction: "left_to_right"
    sfx_language: "English_SFX_soft_sounds"
    cultural_frame: "urban_meditation_studio"
    lettering_bubble_shape: "rounded_modern"
    color_treatment: "minimal_palette_digital_clean"

  es_locale:
    reading_direction: "left_to_right"
    sfx_language: "Spanish_contemporary_sfx"
    cultural_frame: "family_home_setting_warm_colors"
    lettering_bubble_shape: "gentle_rounded"
    color_treatment: "warm_ochres_terracottas"

  ar_locale:
    reading_direction: "right_to_left"
    sfx_language: "Arabic_poetic_sfx"
    cultural_frame: "Islamic_garden_setting"
    lettering_bubble_shape: "elegant_rounded"
    color_treatment: "rich_jewel_tones_traditional"
```

### 3.4 Production Mix Diversity Rules

No two books from the same brand in the same production batch have identical genre + locale + visual style combinations.

```yaml
production_mix_diversity:
  rules:
    rule_1: "no_duplicate_brand_genre_locale_in_batch"
    rule_2: "max_2_books_same_brand_per_batch_of_100"
    rule_3: "if_brand_A_uses_visual_style_X_in_batch_N, brand_A_cannot_use_style_X_in_batch_N+1"
    rule_4: "min_visual_variance_coefficient: 0.65 (pairwise distance)"
    rule_5: "stagger_series_distribution: no_more_than_2_same_series_per_batch"

  example_batch_of_100:
    valid_distribution:
      - brand_001: [genre_romance_locale_en, genre_slice_life_locale_ja]
      - brand_002: [genre_psychological_locale_es]
      - brand_003: [genre_philosophical_locale_de]
      - ...

    invalid_distribution:
      - brand_001: [genre_romance_locale_en, genre_romance_locale_en]  # DUPLICATE
      - brand_001: [genre_slice_life_locale_ja, genre_slice_life_locale_ja, genre_drama_locale_fr]  # 3 same brand
```

### 3.5 Cross-Brand Uniqueness Validation

Before a book enters production, it is checked against all previously published books for visual + textual similarity.

```yaml
cross_brand_uniqueness:
  similarity_scoring_algorithm: "multi_modal_composite"

  components:
    visual_similarity:
      method: "perceptual_hash_distance"
      threshold: 0.10  # must differ by 90%
      weights:
        - color_palette: 0.25
        - linework_signature: 0.30
        - bubble_shape_distribution: 0.20
        - sfx_style_pattern: 0.25

    textual_similarity:
      method: "semantic_embedding_distance"
      threshold: 0.15  # must differ by 85%
      weights:
        - plot_points: 0.40
        - dialogue_patterns: 0.30
        - internal_monologue_voice: 0.30

    brand_fingerprint_match:
      method: "style_token_overlap"
      threshold: 0.08  # max 8% style token overlap with any other book

  action_on_similarity_threshold_exceeded:
    - alert: "WARN_VISUAL_SIMILARITY_HIGH"
    - review: "manual_QA_inspection"
    - decision: "redesign_or_block"
```

---

## 4. Brand DNA Configuration File Schema

Each brand is represented as a machine-readable configuration that all downstream agents consume.

```yaml
# File: brand_dna/brand_001_stillness_harbor.json

{
  "metadata": {
    "brand_id": "brand_001",
    "brand_name": "Stillness Harbor",
    "version": "1.0",
    "updated": "2026-03-21",
    "custodian": "Brand_Steward_Anxiety"
  },

  "therapeutic_profile": {
    "category": "anxiety",
    "therapeutic_approach": "Buddhist_mindfulness_somatic",
    "target_wound": ["generalized_anxiety", "panic", "somatic_dysregulation"],
    "healing_modalities": ["breath_awareness", "mindful_pause", "body_sensation_mapping"]
  },

  "visual_dna": {
    "linework": {
      "stroke_weight": "medium",
      "ink_consistency": "variable",
      "signature_technique": "ink_wash_transitions"
    },
    "shading": {
      "primary_method": "screentone",
      "tone_palette": ["black", "50pct_grey", "20pct_grey"],
      "shadow_intensity": "soft"
    },
    "color": {
      "mode": "limited_palette",
      "primary_colors": ["calm_blue_5B7C99", "warm_beige_D4C4A8", "deep_grey_4A4A4A"],
      "rendering_era": "early_2000s_digital"
    }
  },

  "lettering_dna": {
    "bubble_shapes": {
      "dialogue": "soft_rounded_rectangle",
      "internal_monologue": "rounded_cloud",
      "narration": "rectangular_clean"
    },
    "fonts": {
      "dialogue": "Komika_Axis",
      "internal_monologue": "Sohne_Light",
      "sfx": "Custom_SFX_Dharma"
    }
  },

  "production_constraints": {
    "series_affinity": { ... },
    "locale_distribution": { ... },
    "anti_spam_rules": { ... }
  },

  "quality_gates": {
    "visual_fingerprint_hash": "fx7A2k9mP3Q1Lx8",
    "uniqueness_threshold": 0.95,
    "batch_incompatibilities": ["brand_002", "brand_007"]
  }
}
```

---

## 5. QC Gates: Anti-Spam Validation

### 5.1 Per-Book QC Checklist

Every book produced undergoes these checks before publication:

```
□ VISUAL FINGERPRINT MATCH
  ✓ Visual similarity score < 0.10 (at least 90% unique)
  ✓ Color palette not within 15% of any existing brand_001 book
  ✓ Linework signature confidence match < 0.05
  ✓ SFX style distribution < 0.08 overlap

□ TEXTUAL UNIQUENESS
  ✓ Plot semantic embedding distance > 0.85
  ✓ Dialogue voice signature distinct
  ✓ No reused internal monologue passages

□ PRODUCTION MIX VALIDATION
  ✓ Not same genre + locale as another brand_001 book in batch
  ✓ Series distribution within constraints
  ✓ Locale distribution within monthly caps

□ BRAND DNA COMPLIANCE
  ✓ Linework matches brand_001 visual_dna specification
  ✓ Color palette within brand_001 approved range
  ✓ Lettering bubble shapes correct for brand_001
  ✓ SFX style set matches brand_001 dictionary
  ✓ Silence weight and Ma spacing appropriate

□ LOCALE ADAPTATION INTEGRITY
  ✓ Reading direction correct for target locale
  ✓ SFX translation culturally appropriate
  ✓ Character names/references localized
  ✓ Cultural context respected and authentic
```

### 5.2 Batch-Level QC Validation

Every production batch of 100 books undergoes similarity matrix analysis:

```
BATCH QC CHECKLIST:
□ No duplicate brand-genre-locale triplets
□ Average pairwise visual distance >= 0.65
□ No brand appears > 2 times in batch
□ Series distribution coefficient within tolerance (0.8-1.2)
□ Cross-brand similarity matrix all entries < 0.15
□ Anti-spam flags: 0 high-severity, <3 medium-severity
```

---

## 6. Integration Points

### 6.1 Downstream Agent Consumption

```
Brand DNA Config consumed by:

Visual Identity Agent:
  - Reads: linework, shading, color, lettering parameters
  - Applies: visual style to all panel outputs
  - Updates: style compliance scores

Genre Agent:
  - Reads: genre_affinity, persona_targets
  - Constrains: which genres are allowed for this brand
  - Validates: narrative alignment with brand therapy approach

Story Architect:
  - Reads: therapeutic_category, therapeutic_approach, target_wound
  - Informs: narrative beats, conflict intensity, resolution type
  - Ensures: story serves brand's healing intention

QC Agent:
  - Reads: entire brand_dna config
  - Validates: against uniqueness thresholds, production constraints
  - Reports: compliance status, similarity scores, batch diagnostics

Production Orchestrator:
  - Reads: production_constraints, locale_distribution, anti_spam_rules
  - Schedules: book production respecting constraints
  - Tracks: brand-level quotas, locale distribution, batch composition
```

### 6.2 Feedback Loop: Brand Evolution

Every 3 months, brand DNA is reviewed and updated based on:
- Reader engagement metrics (which visual styles resonate)
- QC validation success rate (are the fingerprints effective?)
- Therapeutic efficacy feedback (are stories actually helping?)
- Competitive landscape (visual distinctiveness maintained?)

---

## 7. Implementation Roadmap

**Phase 1 (Week 1-2):**
- Define all 30 brand therapeutic profiles
- Create brand_dna.json schema and validation
- Build visual fingerprinting algorithm (color histogram, line density)

**Phase 2 (Week 3-4):**
- Implement uniqueness scoring (visual + textual)
- Build anti-spam validation pipeline
- Create QC gate automation

**Phase 3 (Week 5-6):**
- Integrate Brand DNA config consumption into Visual Identity, Genre, Story agents
- Implement batch-level diversity validation
- Build production constraint enforcement in orchestrator

**Phase 4 (Week 7-8):**
- End-to-end testing across 30 brands
- Uniqueness validation on sample corpus of 200 books
- Brand evolution feedback loop setup

---

## 8. Success Metrics

- **Visual Distinctiveness:** 95%+ unique (< 0.10 similarity score) across all 1,000 books
- **Anti-Spam Effectiveness:** Zero detected duplicates in production corpus
- **QC Efficiency:** >99% books pass uniqueness validation on first generation
- **Batch Diversity:** 100% batches meet production mix diversity rules
- **Brand Recognition:** Reader surveys show >85% can identify brand from visual style alone

---

*SpiritualTech Systems · Brand DNA & Anti-Spam Spec v1.0 · Confidential*
