# SpiritualTech Systems: Series Bible Specification

**Version:** 1.0
**Date:** March 2026
**Audience:** Story Architects, Visual Identity Agents, Genre Agents, QC Leads
**Classification:** Confidential

---

## Executive Summary

The Series Bible is the per-series reference document that locks ALL production decisions for a manga series. One Series Bible per seed series (5 seed series → 5 Series Bibles). The Series Bible ensures internal consistency, therapeutic coherence, and narrative integrity across all iterations, brands, locales, and genres derived from that series.

The Series Bible is NOT a single story. It is a structural and thematic blueprint that governs:
- Which therapeutic wounds the series addresses
- How those wounds are sequenced through chapters
- The specific panel density patterns that mirror somatic rhythm
- Visual motifs that carry symbolic weight across the series
- Character design principles and registered character archetypes
- The exact deployment of wisdom atoms by chapter
- QC rules that must be satisfied regardless of brand or locale

---

## 1. Series Bible Schema

### 1.1 Series Identity Block

```yaml
series_metadata:
  series_id: "series_001"
  title: "The Boy Who Stopped Running"
  subtitle: "A Manga on Burnout, Impermanence, and the Art of Stopping"

  series_type: "seed_series"  # one of: seed_series (5 total), derivative_series (many)
  format: "episodic_chapters"
  chapter_count: 14
  pages_per_chapter: 19  # structural formula: pages map to specific beats
  total_series_pages: 266

  publication_status: "in_production"
  version: "1.0"
  locked_date: "2026-03-21"
  custodian: "Story_Steward_Burnout"

  therapeutic_intention: |
    This series addresses burnout as a failure of stopping, as running-toward
    without the counterbalance of resting-in. The series maps the Buddhist concept
    of impermanence (anicca) onto the protagonist's realization that their exhaustion
    is itself impermanent, and that stopping is not failure but return.
```

### 1.2 Therapeutic Foundation

```yaml
therapeutic_framework:
  primary_wound: "burnout"
  wound_descriptor: |
    Burnout is the felt sense of exhaustion from running toward things (achievement,
    approval, productivity) without the necessary pause. It manifests as:
    - Physical depletion masked by continued motion
    - Spiritual disconnection despite external success
    - Inability to feel rest as legitimate
    - Loss of capacity to notice the present moment
    - Somatic rigidity; frozen breath; lack of flexibility

  tradition: "Buddhism_contemporary"
  teaching_atom_source: "Pali_Canon_impermanence"

  key_teachings:
    - impermanence: "all conditioned things are in flux; exhaustion is not permanent"
    - anicca: "change is constant; stopping is not resistance but alignment with reality"
    - pausation: "the space between breaths is as important as the breath itself"
    - return: "stopping is not giving up but coming home"

  healing_modalities:
    - somatic_awareness: "learning to feel the body's signals beneath productivity"
    - intentional_pause: "practicing non-productive time as spiritual discipline"
    - impermanence_meditation: "using the passing of moments to release driven-ness"
    - return_ritual: "small acts that signal home-coming and stopping"

  target_demographic:
    primary: "high_achievers_burnt_out"
    secondary: "caregivers_exhausted"
    tertiary: "artists_blocked_by_overwork"
```

### 1.3 Genre & Narrative Structure

```yaml
narrative_structure:
  primary_genre: "slice_of_life"
  secondary_genre: "psychological"
  tertiary_genre: "philosophical"

  setting: "contemporary_urban"
  time_span: "3_months_in_protagonist_life"
  narrative_pov: "close_third_protagonist"

  story_arc_shape: "not_hero_journey_but_return_home"

  macro_arc_structure:
    act_1_setup: "chapters_1_3"
    act_1_descriptor: "protagonist_at_breaking_point_still_running"

    act_2_threshold: "chapters_4_6"
    act_2_descriptor: "small_moments_of_involuntary_stopping"

    act_2_midpoint: "chapters_7_8"
    act_2_midpoint_descriptor: "crisis_forces_full_stop"

    act_3_reconstruction: "chapters_9_12"
    act_3_descriptor: "learning_to_stop_on_purpose"

    act_4_landing: "chapters_13_14"
    act_4_descriptor: "not_conclusion_but_beginning_of_sustainable_stopping"

  narrative_principle: |
    This is NOT a hero's journey of ascent. It is a descent into stopping,
    a homecoming to the body, to rest, to the present moment. The protagonist
    does not "conquer" burnout but learns to stop running from it. Resolution
    is not triumph but permission.
```

---

## 2. The 19-Page Structural Formula

The heart of the Series Bible is the 19-page chapter structure that maps narrative beats to somatic pacing. Every chapter in "The Boy Who Stopped Running" follows this formula. This structure encodes the rhythm of burnout → pause → choice → exhale → landing.

### 2.1 The Formula Architecture

```
PAGES 1-4: COMPRESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Narrative: Protagonist under pressure, running, driven
Visual Density: 7-10 panels per page (high density)
Pacing: Fast, relentless, overwhelming
Visual Motif: Grey heaviness, closed body language, phone face-down
Panel Composition: Tight grids, vertical stacks, no breathing room
Silence: Minimal; little white space; constant motion
Somatic Resonance: Mirrors reader's own exhaustion and overwhelm
Silence Weight: 0.1 (heavy on content, light on pause)

PAGES 5-8: MA (Negative Space / Breath)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Narrative: Involuntary moment of stopping, pause in the action
Visual Density: 5-7 panels per page (opening up)
Pacing: Slowing; breath becoming noticeable
Visual Motif: Ma (negative space) increases; sky appears; white space grows
Panel Composition: Wider spacing between panels; panels smaller, breathing room
Silence: Growing; the space between things becomes visible
Somatic Resonance: Permission to pause; exhale; notice presence
Silence Weight: 0.5 (balance between content and pause)

PAGES 9-12: CHOICE (The Pivot)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Narrative: The moment where protagonist makes a choice to stop (or not)
Visual Density: 3-5 panels per page (significant opening)
Pacing: Poised; intentional; liminal
Visual Motif: Shoes off-foot; hands open; posture shifting; sky dominant
Panel Composition: White space as co-protagonist; panels are sparse; pauses visible
Silence: Substantial; white space carries meaning; quietness is active
Somatic Resonance: The felt sense of crossing a threshold; choosing differently
Silence Weight: 0.7 (silence and content nearly balanced)

PAGES 13-16: TONGLEN (Breathing Exchange)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Narrative: Protagonist breathes, feels, exchanges; receiving and giving back
Visual Density: 2-4 panels per page (open, spacious)
Pacing: Slow; meditative; rhythm of breath
Visual Motif: Breath visible (steam, wind, light); body at rest; hands receiving
Panel Composition: Generous white space; panels float on page; breathing room dominant
Silence: Pervasive; the space between panels is as meaningful as panels
Somatic Resonance: Deep exhale; permission to receive; exchange of self and world
Silence Weight: 0.85 (silence is protagonist; content is minimal)

PAGES 17-19: AFTER (Landing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Narrative: Post-pause moment; reentry to ordinary moment with new awareness
Visual Density: 1-2 panels per page (extremely sparse, almost empty)
Pacing: Still; grounded; settled
Visual Motif: Shoes on feet; hands resting; light natural; body integrated
Panel Composition: Final page may have only 1-2 full-page or half-page panels
Silence: Total; white space is default; content is minimal
Somatic Resonance: The peace after stopping; body knows itself again
Silence Weight: 0.95 (almost entire page is silence; content is breath)
```

### 2.2 Per-Chapter Breakdown: How the Formula Maps to Story

```yaml
chapter_001:
  title: "The Phone"
  pages_1_4_compression:
    narrative_beat: "Protagonist wakes to 47 unread messages; begins running"
    panel_count: 9  # 7-10 range
    visual_strategy: "close-ups of messages, hands gripping phone, face stressed"
    key_motif: "phone face-down by pillow; messages glowing"
    wisdom_atom_seeding: "impermanence (each notification is fleeting but endless)"

  pages_5_8_ma:
    narrative_beat: "Mid-morning, moment in bathroom mirror; sees own face"
    panel_count: 6  # 5-7 range
    visual_strategy: "mirror reflection; light through bathroom window; shoulders dropping"
    key_motif: "first appearance of sky; white wall space; breath visible"
    wisdom_atom_development: "anicca (noticing that exhaustion is not fixed state)"

  pages_9_12_choice:
    narrative_beat: "Decision point: answer messages or sit with coffee?"
    panel_count: 4  # 3-5 range
    visual_strategy: "split panel of two paths; hand hovering over phone"
    key_motif: "shoes by door (journey); coffee steam; decision moment"
    wisdom_atom_deepening: "pausation (learning that stopping is possible)"

  pages_13_16_tonglen:
    narrative_beat: "Sitting with coffee; noticing breath; receiving morning"
    panel_count: 3  # 2-4 range
    visual_strategy: "full-page coffee cup from above; hands warming on cup"
    key_motif: "steam rising; window light; body at rest in space"
    wisdom_atom_anchor: "return (this moment is home)"

  pages_17_19_after:
    narrative_beat: "Gets up; answers 3 messages mindfully; day continues differently"
    panel_count: 2  # 1-2 range
    visual_strategy: "two panels: hands typing slowly; feet on ground"
    key_motif: "shoes on feet; light; ordinary moment made sacred"
    closing_silence: "final panel is almost entirely white; tiny figure in space"

  qc_notes: |
    Verify panel density stays in formula ranges.
    Silence weight must increase across the 5 sections.
    Check that motifs (phone, shoes, breath, light) are visible.
    Confirm wisdom atom appears in seeding → development → deepening → anchor.
```

---

## 3. Visual Motifs Library

The Series Bible locks specific visual motifs that carry symbolic weight across all 14 chapters. These motifs are REQUIRED to appear in the specified chapters and carry consistent meaning.

### 3.1 Master Motif Map

```yaml
visual_motifs:
  motif_phone:
    name: "The Phone (Endless Connectivity)"
    appears_chapters: [1, 2, 3, 4, 5]  # early half; fades as protagonist stops
    symbolic_meaning: "the voice of demand; never-ending pull toward productivity"
    visual_treatment:
      early_chapters: "phone glowing, face-down, buzzing, demanding"
      mid_chapters: "phone face-down intentionally; being resisted"
      late_chapters: "phone mostly absent; sometimes visible but ignored"
    qc_gate: "phone visible in chapters 1-3 every chapter; chapters 4-5 optional"

  motif_shoes:
    name: "Shoes (Readiness to Run / Grounding)"
    appears_chapters: [1, 2, 3, 7, 8, 9, 13, 14]
    symbolic_meaning: |
      Early chapters: shoes on, laced, ready to run (running from self)
      Chapter 9: shoes being untied (choice to stop)
      Chapter 13: shoes off (full stopping)
      Chapter 14: shoes back on differently (walking intentionally)
    visual_treatment:
      chapter_1_3: "feet in motion; shoes worn, scuffed, moving fast"
      chapter_7_8: "shoes visible but protagonist stationary; tension"
      chapter_9: "moment of untying; shoes coming off"
      chapter_13_14: "barefoot or shoes off; if shoes on, protagonist moving slowly"
    qc_gate: "shoes appear in all specified chapters; transition narrative is clear"

  motif_grey_heaviness:
    name: "Grey Tones (Burnout Weight)"
    appears_chapters: [1, 2, 3, 4, 5, 6]
    symbolic_meaning: "the visual weight of exhaustion; greyness as heaviness"
    visual_treatment:
      chapters_1_3: "dominant greyscale; limited color; heavy shadows"
      chapters_4_5: "grey still present but lightening; color appearing"
      chapters_6_onward: "grey fades; color, sky, warmth increase"
    qc_gate: "color_mode must be grayscale or very desaturated chapters 1-5; color palette expands chapters 6+"

  motif_ma_negative_space:
    name: "Ma / Negative Space (Absence as Presence)"
    appears_chapters: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    symbolic_meaning: "white space becomes a character; emptiness is permission; silence is active"
    visual_treatment:
      chapters_5_6: "white space begins to appear; sky visible"
      chapters_7_10: "panels spaced generously; white space grows"
      chapters_11_14: "white space is co-protagonist; pages are mostly empty"
    qc_gate: |
      pages_1_4: white_space < 20% of page
      pages_5_8: white_space 20-40% of page
      pages_9_12: white_space 40-70% of page
      pages_13_16: white_space 70-90% of page
      pages_17_19: white_space >= 90% of page

  motif_breath_visibility:
    name: "Breath Made Visible (Spirit Returning)"
    appears_chapters: [6, 7, 8, 9, 10, 11, 12, 13, 14]
    symbolic_meaning: "spiritedness returns through visible breath; life becoming noticeable"
    visual_treatment:
      chapter_6: "first subtle breath notations; steam from coffee"
      chapters_7_10: "breath more visible; wind visible; light effects"
      chapters_11_14: "breath continuous; breathe and world exchanging"
    visual_techniques: "steam, light rays, particle effects, wind lines, subtle sfx"
    qc_gate: "breath visibility must increase progressively chapters 6-14"

  motif_phone_face_down:
    name: "Phone Face Down (Turning Away from Demand)"
    appears_chapters: [2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]
    symbolic_meaning: "intentional refusal; boundary; the choice to not-respond"
    visual_treatment: "phone screen dark; phone resting; sometimes protagonist's hand on phone gently"
    qc_gate: "phone face-down visible in at least 2 panels per chapter (chapters 2-6, 9-14)"

  motif_light_increasing:
    name: "Light (Hope, Clarity, Presence)"
    appears_chapters: [7, 8, 9, 10, 11, 12, 13, 14]
    symbolic_meaning: "metaphor for returning awareness; clarity increasing"
    visual_treatment:
      early: "light filtered, soft, from windows"
      mid: "light more direct; sky taking up more space"
      late: "light dominant; almost entire page can be illuminated"
    qc_gate: "light quality and quantity must increase progressively"
```

### 3.2 Motif Deployment Schedule

Every chapter must validate against this schedule:

```yaml
chapter_by_chapter_motif_validation:
  chapter_001:
    required_motifs: [phone_on, shoes_laced, grey_heaviness, no_ma_yet]
    forbidden_motifs: [phone_face_down, shoes_off, breath_visible, excessive_white_space]

  chapter_002:
    required_motifs: [phone_present, phone_face_down, shoes_on, grey_heaviness]
    optional_motifs: [first_light_hints]

  chapter_003:
    required_motifs: [phone_face_down, shoes_visible, grey_heaviness, phone_silent]
    optional_motifs: [subtle_sky_appearance]

  chapter_004:
    required_motifs: [phone_face_down, shoes_on, grey_fading, ma_appearing]
    optional_motifs: [first_color, breath_subtle]

  chapter_005:
    required_motifs: [phone_off_screen_sometimes, shoes_less_prominent, color_appearing, ma_stronger]
    optional_motifs: [light_increasing, breath_coffee_steam]

  chapter_006:
    required_motifs: [shoes_stillness, color_present, light_visible, breath_visible, ma_strong]
    forbidden_motifs: [grey_heaviness_dominant, phone_buzzing]

  chapter_007:
    required_motifs: [shoes_tension_visible, light_strong, breath_present, ma_dominant, phone_off]
    forbidden_motifs: [grey_overwhelming]

  chapter_008:
    required_motifs: [shoes_coming_off_motion, light_large, breath_prominent, ma_very_strong]

  chapter_009:
    required_motifs: [shoes_untied_or_off, choice_visible, light_filling_space, breath_central]

  chapter_010:
    required_motifs: [shoes_off, barefoot_possible, light_dominant, breath_rhythm, ma_overwhelming]

  chapter_011:
    required_motifs: [barefoot_or_shoes_off, ma_dominant, light_fills_page, breath_visible, near_silence]

  chapter_012:
    required_motifs: [body_at_rest, light_natural, ma_very_strong, breath_slow, silence_strong]

  chapter_013:
    required_motifs: [shoes_off, barefoot_ground_contact, light_warm, ma_dominant, breath_exchange]

  chapter_014:
    required_motifs: [shoes_on_differently, walking_slowly, light_natural, ma_very_strong, silence_peace]
```

---

## 4. Character Registry & Design Principles

### 4.1 Character Archetypes

Every character in the series is registered with name, archetype, visual design anchors, and role in therapeutic narrative.

```yaml
characters:
  protagonist:
    character_id: "char_001"
    name: "Kenji"  # or adapts per locale
    archetype: "The_Driven_One"
    age: "32"
    background: "Corporate professional; high achiever; success-driven"

    visual_design_anchors:
      build: "lean, slightly hunched from tension"
      face: "sharp features; lines around eyes from stress"
      posture_early: "forward-leaning, tense shoulders, closed arms"
      posture_late: "opening, shoulders relaxed, hands open"
      signature_feature: "small scar on left hand (metaphor for past injury)"

    character_arc: |
      Learns that stopping is not failure. Discovers that underneath the running
      is longing for home. The series charts his somatic transformation from
      tension → pause → opening → presence.

    appearance_consistency: |
      Kenji's face softens progressively across the series. Early chapters show
      tension lines, sharp shadows. Later chapters show his face becoming rounder,
      softer, more open. This is visual proof of internal change.

  mentor_character:
    character_id: "char_002"
    name: "Ito_sensei"  # or adapts: "Ms. Park", "Professor Elena", etc.
    archetype: "The_One_Who_Stopped"
    age: "68"
    background: "Former executive; now runs small tea house; has walked the path of stopping"

    visual_design_anchors:
      build: "soft, relaxed; moves slowly"
      face: "weathered, open, kind; eyes suggest deep peace"
      posture: "consistently open, grounded, present"

    character_arc: "Not protagonist. Ito is the mirror of what Kenji is learning. Ito doesn't change; Kenji's relationship to Ito changes."

  secondary_character_colleague:
    character_id: "char_003"
    name: "Yuki"
    archetype: "The_Mirror_Still_Running"
    age: "30"
    background: "Kenji's colleague; also burnt out; but chooses to keep running"

    character_arc: |
      Yuki shows what NOT choosing to stop looks like. Her arc is parallel to
      Kenji's but divergent. She represents Kenji's possible future if he doesn't
      choose the threshold.

character_consistency_rules:
  rule_1: "Kenji appears in every chapter; visual softening must be progressive"
  rule_2: "Ito appears chapters 2, 6, 9, 12, 14 (at key threshold moments)"
  rule_3: "Yuki appears chapters 1-7 (fades as Kenji's world changes)"
  rule_4: "Minor characters (coworkers, neighbors) support series themes; not developed in detail"
```

---

## 5. Wisdom Atom Deployment Map

The Series Bible specifies WHICH wisdom atoms appear in WHICH chapters, how they unfold, and in what narrative vehicles they manifest.

### 5.1 The Atoms for This Series

```yaml
wisdom_atoms:
  atom_impermanence:
    atom_id: "atom_001"
    name: "Impermanence (Anicca)"
    tradition: "Pali_Buddhism"
    core_teaching: |
      All conditioned things are in flux. Nothing lasts. This is not pessimism
      but liberating truth: the exhaustion will not last, the success will not last,
      the stopping will not last. All is flux. The practitioner's task is to align
      with flux rather than resist it.

    deployment_chapters: [1, 2, 3, 5, 7, 9, 11, 13]

    chapter_001_vehicle:
      narrative_vehicle: "messages arriving and disappearing on phone"
      visual_anchor: "notifications appearing and vanishing; text glowing and fading"
      reader_resonance: "feeling the endless flux of demands"
      wisdom_depth: "SEEDING: Reader notices that each message is temporary but endless"

    chapter_002_vehicle:
      narrative_vehicle: "noticing that fatigue changes moment to moment"
      visual_anchor: "Kenji's face showing different degrees of tiredness in different moments"
      reader_resonance: "permission to notice that exhaustion itself is not monolithic"
      wisdom_depth: "DEVELOPMENT: If exhaustion is impermanent, it can change"

    chapter_003_vehicle:
      narrative_vehicle: "small moment where Kenji notices a pain in his shoulder has eased slightly"
      visual_anchor: "close-up of shoulder, then release, then return to tension"
      reader_resonance: "even the body's pain is not fixed; it fluctuates"
      wisdom_depth: "DEEPENING: Impermanence applies to physical sensation too"

    chapter_005_vehicle:
      narrative_vehicle: "realizing that the urgency of a deadline has passed; the emergency wasn't real"
      visual_anchor: "calendar pages turning; deadline passing; normal day continuing"
      reader_resonance: "what felt like emergency in chapter 1 is now just... past"
      wisdom_depth: "REALIZATION: I survived the panic. It was temporary."

    chapter_007_vehicle:
      narrative_vehicle: "moment of choice: recognizing that choosing to stop is also temporary; he can always resume"
      visual_anchor: "pivot moment; shoes coming off; choice to try something new"
      reader_resonance: "permission to stop because stopping is also impermanent"
      wisdom_depth: "TRANSFORMATION: Impermanence means I can try stopping without permanent consequence"

    chapter_009_vehicle:
      narrative_vehicle: "sitting in silence and noticing that even silence changes moment to moment"
      visual_anchor: "sitting; breathing; light subtle changes; awareness of flux"
      reader_resonance: "even rest is alive; nothing is stuck"
      wisdom_depth: "ANCHOR: This is how to live with impermanence: notice, allow, let go"

    chapter_011_vehicle:
      narrative_vehicle: "Kenji realizes that his own life is impermanent; death is inevitable; this releases ambition"
      visual_anchor: "moment of mortality awareness; not grim but clarifying"
      reader_resonance: "what am I running from if I'm going to die anyway?"
      wisdom_depth: "LIBERATION: Accepting impermanence is accepting mortality, which frees from driven-ness"

    chapter_013_vehicle:
      narrative_vehicle: "integrating impermanence as lived experience; understanding that change is the only constant"
      visual_anchor: "seasons visible changing; body changing; awareness continuous"
      reader_resonance: "I can rest into the flux; I don't have to fight change"
      wisdom_depth: "INTEGRATION: Living aligned with impermanence is the path"

  atom_pausation:
    atom_id: "atom_002"
    name: "The Sacred Pause (Tonglen Practice)"
    tradition: "Tibetan_Buddhism / Pema_Chodron"
    core_teaching: |
      Tonglen is breathing-in the difficulty, breathing-out relief. But more
      fundamentally, it is the practice of pause: the moment between breath-in
      and breath-out where nothing is happening, where there is space for choice.

    deployment_chapters: [4, 6, 8, 10, 12, 13, 14]

    vehicle_progression: |
      Chapter 4: First involuntary pause (bathroom moment; breath noticed)
      Chapter 6: Intentional pause with tea (practice begins)
      Chapter 8: Pause deepening (sits in silence intentionally)
      Chapter 10: Pause as major rhythm (day organized around pauses)
      Chapter 12: Pause as wisdom (understanding why pause matters)
      Chapter 13: Tonglen proper (breathing in suffering, breathing out relief)
      Chapter 14: Pause as lifestyle (integrated, not forced)

  atom_return:
    atom_id: "atom_003"
    name: "Return (Home-Coming)"
    tradition: "Taoism / Daoism; also Zen"
    core_teaching: |
      The journey is not ascent but return. You are always already home.
      The practice is learning to recognize home when you find it.
      Home is the body. Home is this moment. Home is breath.

    deployment_chapters: [2, 4, 6, 9, 11, 13, 14]

    narrative_vehicle_example:
      chapter_002: "Kenji notices his own home (apartment) as a place; begins to sense ground"
      chapter_004: "Memory of childhood rest; longing for home awakens"
      chapter_006: "Recognizing that home is not a place but a way of being in the body"
      chapter_009: "Choosing to return to the body as home"
      chapter_011: "Understanding that he never really left home; just forgot"
      chapter_013: "Living in the home of his own presence"
      chapter_014: "Walking through the world from the home of his body"

atom_deployment_validation: |
  Every chapter must satisfy atom deployment requirements.
  Atoms must appear in sequence (seeding → development → deepening → integration).
  Atoms cannot disappear and reappear; they must have narrative continuity.
```

---

## 6. QC Rules: Series-Level Validation

These rules apply to every chapter of every iteration of this series, regardless of brand or locale.

### 6.1 Structural QC Rules

```
QC RULE 1: PAGE DENSITY FORMULA
✓ Pages 1-4: 7-10 panels (tight compression)
✓ Pages 5-8: 5-7 panels (opening)
✓ Pages 9-12: 3-5 panels (choice space)
✓ Pages 13-16: 2-4 panels (breathing)
✓ Pages 17-19: 1-2 panels (silence)
FAIL: If any section violates these ranges

QC RULE 2: SILENCE WEIGHT PROGRESSION
✓ Pages 1-4: White space < 20% of total page area
✓ Pages 5-8: White space 20-40%
✓ Pages 9-12: White space 40-70%
✓ Pages 13-16: White space 70-90%
✓ Pages 17-19: White space >= 90%
FAIL: If silence weight does not increase monotonically

QC RULE 3: VISUAL MOTIF DEPLOYMENT
✓ All motifs appear in designated chapters (see Motif Deployment Schedule)
✓ Motif treatment evolves as per specification (e.g., shoes change from laced to off)
✓ No motif appears where forbidden
FAIL: If motif requirements not met

QC RULE 4: WISDOM ATOM DEPLOYMENT
✓ Atoms appear in designated chapters in correct order
✓ Each appearance deepens the teaching (seeding → development → deepening → anchor)
✓ Atoms have consistent narrative vehicles (phone as impermanence carrier, etc.)
FAIL: If atom deployment breaks sequence or narrative consistency

QC RULE 5: CHARACTER CONSISTENCY
✓ Kenji appears every chapter; visual softening progressive
✓ Supporting characters appear in designated chapters only
✓ Character visual design matches registered anchors
✓ Character arcs align with series intention
FAIL: If character consistency broken

QC RULE 6: SOMATIC MIRRORING
✓ Reader's somatic experience should match protagonist's arc
✓ Tight pages should feel overwhelming; open pages should feel free
✓ Silence should feel earned, not arbitrary
✓ Motif appearance should feel thematically resonant
FAIL: If somatic resonance not achieved (subjective QC; expert review required)
```

### 6.2 Narrative QC Rules

```
QC RULE 7: NO EXTRANEOUS PLOT
✗ Do not introduce subplots unrelated to burnout/stopping/return
✗ Do not include romantic storylines (unless they serve stopping theme)
✗ Do not include external antagonists (enemy is self-driven-ness, not others)
✓ Keep story confined to protagonist's internal landscape
FAIL: If story veers into territory outside healing intention

QC RULE 8: RESOLUTION INTEGRITY
✓ Chapter resolutions do NOT solve the burnout (that's not possible in 19 pages)
✓ Resolutions are PIVOTS or DEEPENINGS in understanding
✓ Final chapter does not "conclude" the story; it begins living the teaching
FAIL: If chapter seems to "fix" burnout or provide false closure

QC RULE 9: DIALOGUE AUTHENTICITY
✓ Dialogue is sparse and purposeful (not exposition-heavy)
✓ Internal monologue carries more weight than spoken words
✓ Silence is communication (many chapters have minimal dialogue)
✓ Dialogue reflects contemporary speech patterns but without slang overload
FAIL: If dialogue feels forced, unnatural, or over-explains

QC RULE 10: PACING INTEGRITY
✓ Early chapters move fast (reader experiences overwhelm)
✓ Middle chapters decelerate (reader learns pause)
✓ Late chapters move slowly (reader inhabits silence)
✓ No chapter should feel rushed or padded
FAIL: If pacing does not support somatic arc
```

### 6.3 Visual QC Rules

```
QC RULE 11: COLOR CONSISTENCY
✓ Chapters 1-5: Grayscale or heavily desaturated
✓ Chapters 6-10: Color introduces gradually
✓ Chapters 11-14: Warm, natural colors; light dominant
FAIL: If color strategy violates this progression

QC RULE 12: LINE QUALITY
✓ Linework remains consistent with series visual style (not shifting between chapters)
✓ Linework quality does not degrade in open space (sparse chapters still technically precise)
FAIL: If linework inconsistency detected

QC RULE 13: PANEL COMPOSITION
✓ Tight chapters use vertical stacking, grids, minimal gutters
✓ Open chapters use generous gutters, white space breathing, off-center placement
✓ Transition is gradual, not abrupt
FAIL: If panel composition does not reflect silence weight progression
```

---

## 7. TikTok Clip Spine

For each chapter, there are 2-3 moments that can be extracted as short video clips for TikTok engagement. These moments must capture the essence of the chapter teaching.

```yaml
tiktok_clip_spines:
  chapter_001:
    clip_001:
      moment: "Phone notifications arriving endlessly"
      duration_seconds: 15
      beat: "overwhelm; endless; no pause"
      music_mood: "fast, tense, anxious"
      caption: "Your phone never stops. But you can. #BurnoutIsReal #Manga"

  chapter_002:
    clip_001:
      moment: "Kenji noticing his own face in mirror; seeing fatigue"
      duration_seconds: 12
      beat: "recognition; seeing yourself; turning toward pain"
      music_mood: "slow, introspective, soft"
      caption: "The first step is noticing. #SelfAwareness #MangaHealing"

  chapter_006:
    clip_001:
      moment: "Tea steam rising; breath becoming visible"
      duration_seconds: 20
      beat: "pause; presence; breath; permission"
      music_mood: "calm, meditative"
      caption: "This pause is real. This breath is real. You deserve this. #Healing #Manga"

  chapter_009:
    clip_001:
      moment: "The moment shoes come off; choice point"
      duration_seconds: 18
      beat: "decision; threshold; vulnerability; courage"
      music_mood: "hopeful, tender, brave"
      caption: "What if stopping is brave, not weakness? #ChooseDifferently #Manga"

  chapter_014:
    clip_001:
      moment: "Final page: Kenji walking slowly through ordinary world"
      duration_seconds: 15
      beat: "integration; ordinary; sacred; alive"
      music_mood: "warm, grounded, hopeful"
      caption: "The journey ends where it began. Now you're home. #BeingVsBecoming #Manga"
```

---

## 8. Integration Points: How Series Bible is Consumed

### 8.1 Story Architect
- Reads: Therapeutic_framework, macro_arc_structure, wisdom_atom_deployment_map
- Uses: To lock chapter-by-chapter narrative beats and atom deployment
- Validates: Each generated chapter against atom deployment schedule and narrative QC rules

### 8.2 Visual Identity Agent
- Reads: Visual_motifs_library, color_progression, character_design_anchors
- Uses: To apply motif scheduling, color evolution, character consistency
- Validates: Each panel against motif appearance requirements and visual QC rules

### 8.3 Genre Agent
- Reads: Primary_genre, narrative_pov, genre_constraints
- Uses: To apply genre conventions (slice-of-life pacing, psychological depth)
- Validates: That genre adaptation doesn't violate series therapeutic intention

### 8.4 QC Agent
- Reads: Entire Series Bible
- Uses: All structural, narrative, and visual QC rules
- Validates: Every chapter against all 13 QC rules before publication

### 8.5 Production Orchestrator
- Reads: Chapter_count, page_formula, tiktok_clip_spines
- Uses: To estimate production time, schedule batch jobs, prepare clip extraction
- Validates: That all chapters will include TikTok clip spine moments

---

## 9. Series Bible Versioning & Evolution

The Series Bible is LOCKED at v1.0 for the initial production run (chapters 1-14 across all brands and locales). After production is complete and therapeutic efficacy is measured, the Series Bible may be updated to v1.1 with minor refinements.

Version updates are tracked:

```
v1.0 (2026-03-21):
  - Initial specification
  - 14 chapters locked
  - All QC rules finalized

v1.1 (TBD):
  - Updates based on reader feedback
  - Refinements to atom deployment if needed
  - Minor motif clarifications
```

---

## 10. The Other 4 Seed Series (Brief Summary)

While this spec focuses on "The Boy Who Stopped Running" as the detailed example, there are 4 other seed series, each with its own Series Bible:

```
series_001: "The Boy Who Stopped Running" (Burnout)
  - Detailed Series Bible (this document)
  - 14 chapters, 19-page formula
  - Atoms: impermanence, pausation, return

series_002: "Grieflight Atlas" (Grief & Loss)
  - Series Bible (separate document)
  - 12 chapters, variable page formula (grief doesn't follow rhythm)
  - Atoms: impermanence, acceptance, love-persists

series_003: "Identity Crossing" (Identity & Belonging)
  - Series Bible (separate document)
  - 16 chapters, mirror-structure (external world mirrors internal becoming)
  - Atoms: non-self, radical-acceptance, belonging

series_004: "Relational Root" (Attachment & Relationship)
  - Series Bible (separate document)
  - 13 chapters, conversation-based structure
  - Atoms: interdependence, trust, secure-base

series_005: "The Outsider's Room" (Social Anxiety & Longing)
  - Series Bible (separate document)
  - 15 chapters, threshold-structure (chapters at doorways, thresholds)
  - Atoms: courage, visibility, worthy-of-space
```

---

## 11. Success Metrics for Series Bible Effectiveness

By the end of production, the Series Bible should achieve:

- **Chapter Consistency:** 100% of chapters meet page density formula
- **Motif Deployment:** 100% compliance with motif scheduling
- **Atom Deployment:** 100% correct wisdom atom placement and progression
- **Character Consistency:** Character arcs coherent across all 14 chapters
- **Therapeutic Efficacy:** Reader surveys show >80% felt the series addressed their experience
- **Visual Coherence:** Series maintains recognizable visual style across all 30 brands
- **Somatic Resonance:** Readers report physical/emotional responses matching intended somatic arc

---

*SpiritualTech Systems · Series Bible Spec v1.0 · Confidential*
