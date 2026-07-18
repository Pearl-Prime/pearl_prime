# Phase 3: Template System Formalized

## The Operator's Description (Verbatim Reconstruction)

"A template has 12 chapters, 7-10 sections per chapter, 3-5 variants per section. That gives you a coherent book. What we ship now is scene/story/scene with no structure."

The existing `v2_somatic` library already implements this: 12 × 10 × 5. The section roles are named. The content exists. The production wiring was never completed.

The formalized spec below synthesizes:
- The operator's description
- The existing `v2_somatic` grid structure
- The section role map in `legacy_template_index.yaml`
- Bestseller chapter structure analysis (Phase 4/5)
- The `SOMATIC_10_SLOT_GRID` already defined in `beatmap_compile.py`

---

## Formalized YAML Spec

```yaml
book_template_v2:
  id: book_template_v2_standard
  total_chapters: 12
  
  chapter_structure:
    sections_per_chapter: 10
    each_section_has_variants: 5
    section_job_required: true
    variant_selection: deterministic_hash_per(book_id + chapter_index + section_id)
    anti_repetition: no variant_id used in more than 1 chapter across the book
  
  section_jobs:
    - id: section_01_hook
      job: "Arrest attention in 100-200 words. No advice. No setup. Start mid-situation."
      position: chapter_start
      variants_required: 5
      word_target: 150
      constraint: "Must not begin with 'I' or 'When'. Must land in reader's body before explaining."
      example_opening: "Your shoulders have been near your ears since Tuesday. You just noticed."

    - id: section_02_scene
      job: "Ground the listener in a concrete sensory location. Reader/character in motion."
      position: after_hook
      variants_required: 5
      word_target: 300-500
      constraint: "No emotional interpretation. Pure observation: light, sound, physical detail."
      example_opening: "The conference room is cold. Your hands rest on the table. Someone's laptop fan runs loud."

    - id: section_03_reflection
      job: "Bring the scene's meaning to surface. One question the reader is now carrying."
      position: after_first_scene
      variants_required: 5
      word_target: 200-350
      constraint: "End with an open question. Do not answer it yet."

    - id: section_04_exercise
      job: "One specific somatic or cognitive practice. Do it now, not later."
      position: mid_early
      variants_required: 5
      word_target: 200-400
      constraint: "Must be completable in 3-5 minutes. Must not require equipment. Ends with what-did-you-notice."

    - id: section_05_scene
      job: "Second scene — a different moment, earlier or later, same character or reader-mirror."
      position: middle
      variants_required: 5
      word_target: 300-500
      constraint: "Must move forward in time or zoom out in space relative to section_02."

    - id: section_06_teacher_doctrine
      job: "The WHY at a mechanistic level. Teacher voice explaining the system at work."
      position: middle
      variants_required: 5
      word_target: 300-500
      constraint: "Must explain mechanism (nervous system, cognitive pattern, social dynamic). No anecdote. Plain prose."
      example_opening: "The body doesn't distinguish between a tiger and a deadline."

    - id: section_07_reflection
      job: "Bring mechanism explanation back to reader's specific experience."
      position: after_mechanism
      variants_required: 5
      word_target: 200-350
      constraint: "Must name one pattern the reader likely recognizes in themselves."

    - id: section_08_exercise
      job: "Second practice — regulation-phase. Consolidates the chapter's learning."
      position: late
      variants_required: 5
      word_target: 250-450
      constraint: "Must be different modality from section_04. If 04 is somatic, 08 is cognitive or relational."

    - id: section_09_scene
      job: "Resolution scene — same or different character, after the shift."
      position: near_end
      variants_required: 5
      word_target: 200-400
      constraint: "Shows what it looks like when the chapter's mechanism has been engaged. Not triumphant — just different."

    - id: section_10_integration
      job: "Install one new lens the reader carries forward. One sentence takeaway + one forward gesture."
      position: chapter_end
      variants_required: 5
      word_target: 100-200
      constraint: "The takeaway must be a single declarative sentence. Not a question. Not advice. A new framing."
      example: "Your anxiety is not the enemy of your productivity. It is information about your relationship to what matters."

  coherence_guarantees:
    - every chapter opens with section_01_hook (not scene, not exercise, not reflection)
    - section_06_teacher_doctrine always before section_08_exercise
    - section_04_exercise always after section_03_reflection
    - section_10_integration is always the final section
    - no chapter ends with a question
    - character name from section_05_scene is referenced in section_09_scene if in same chapter
    
  variant_selection_spec:
    method: deterministic_hash
    seed_components:
      - book_id (topic × persona × teacher)
      - chapter_index (0-11)
      - section_id (01-10)
    anti_repetition_scope: book_level
    rule: "no f{N} variant reused across the same section_id in the same book"
    note: "This produces ~5^120 theoretically unique books from the same grid"

  six_hour_targets:
    chapters: 12
    sections_per_chapter: 10
    target_words_per_section: 320
    target_words_per_chapter: 3200
    target_book_words: 38400
    realistic_with_pearl_writer_expansion: 45000-55000

  what_is_not_in_the_template:
    - chapter titles (resolved from arc/spine)
    - teacher-specific doctrine variants (injected at section_06)
    - persona-specific scene variants (injected at section_02, 05, 09)
    - topic-specific exercises (injected at section_04, 08)
    - transition sentences between sections (generated by bridge layer)
```

---

## How This Differs from the Current System

| Dimension | Current System | Template v2 |
|-----------|---------------|-------------|
| Chapter opening | Any slot type (exercise led ch4 in pilot) | Always section_01_hook |
| Mechanism placement | Emergent / depth_module appended | Always section_06 |
| Exercise count | 0-3 per chapter, variable | Always 2 (section_04 + section_08) |
| Scene count | 1-9 per chapter | Always 3 (section_02, 05, 09) |
| Chapter ending | Variable (compression, integration, takeaway) | Always section_10_integration |
| Variant source | Atom pool (flat list) | Named section YAML (grid) |
| Coherence guarantee | None | Structural (section sequence enforced) |

---

## Relationship to Existing `v2_somatic` Grid

The formalized spec above maps **directly** to the 600 YAML files already on disk:

```
v2_somatic on disk → formalized spec mapping:
section_01_hook        → section_01_hook (this spec)
section_02_scene       → section_02_scene
section_03_reflection  → section_03_reflection
section_04_exercise    → section_04_exercise
section_05_scene       → section_05_scene
section_06_teacherdoctrine → section_06_teacher_doctrine
section_07_reflection  → section_07_reflection
section_08_exercise    → section_08_exercise
section_09_scene       → section_09_scene
section_10_integration → section_10_integration
```

**The content grid already exists. The spec formalizes its use as the production path.**

What's missing to make this production-ready:
1. Chapter 3-12 v2_somatic sections (pilot confirms ch01-02 and ch08 exist; full 12 may depend on zip archives listed as `status: missing` in index)
2. Persona and topic injection rules per section type
3. Pearl_Writer expansion to hit 320 words/section target (current avg: 153 words/section)
4. Removal of `[STORY_INJECTION_POINT]` and `[EXERCISE_INJECTION_POINT]` placeholders
5. Pipeline wiring to use 10-slot beatmap as default for standard_book
