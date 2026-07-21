# Enhancement Contract V2 Working Priors

**Date:** 2026-07-13  
**Status:** Research-informed working priors memo  
**Truth label:** Useful for production calibration; not an empirically ratified 10-book count study

## 1. What This Is

This document turns current Phoenix research into practical enhancement targets we can build with now.

These targets are based on:

- `specs/ACCENT_BEATS_SYSTEM_SPEC.md` live class doctrine
- `config/authoring/bestseller_enrichment_signatures.yaml`
- `config/authoring/story_mix_profiles.yaml`
- `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md`
- `docs/BESTSELLER_STRUCTURES.md`
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`
- `docs/BESTSELLER_GAP_AUDIT.md`
- `docs/bestseller_enrichment_count__genini_research.txt`

They should be treated as **research-informed operating priors**, not courtroom-grade proof.

## 2. Current Phoenix Reality

### 2.1 Live explicit enhancement classes

Phoenix currently has explicit runtime logic or budgets around:

- `QUOTE`
- `ENCOURAGEMENT`
- `REFLECTION_QUESTION`
- `TROUBLESHOOTING`
- `CITED_EVIDENCE`
- `EXTERNAL_STORY`
- `WISDOM_ESSENCE`
- `AUTHOR_COMMENTARY`

### 2.2 Not fully live or not first-class yet

- `AFFIRMATION` exists in spec language but is not live
- `ANALOGY` is important, but not currently a first-class contract beat
- `METAPHOR` is important, but not currently a first-class contract beat
- `PARABLE` should be treated as a sparse story register, not a default accent
- `CALLBACK` exists partially in repo doctrine, but is not yet a clean end-to-end enhancement contract class
- `AUTHOR_DISCLOSURE` is not cleanly separated from `AUTHOR_COMMENTARY` in the live accent layer

### 2.3 Important framing rule

Enhancements should stay **sparse, intentional, and chapter-functional**. They are not decoration.

## 3. What The Research Reliably Says

Even without exact-edition counting, the current research is strong enough to support these working conclusions:

- Strong self-help books rely heavily on `author guidance`, `validation`, `mechanism explanation`, `story/case study`, and `transition glue`.
- Different subtypes use different mixes.
- Emotion-heavy books need more validation, encouragement, and personal voice.
- Science-forward books need more mechanism, evidence, and clean analogy.
- Weak books often fail because they command too early, skip troubleshooting, or feel episodic instead of threaded.
- `Parable` is niche, not core high-frequency scaffolding.
- `Quotes` matter less than many writers think; they should accent, not carry, the book.
- `Analogy`, `metaphor`, and `callback` are major cohesion tools and should be planned more deliberately than they currently are.

## 4. Core V2.1 Correction

The first version of this memo mixed four different things into one enhancement budget. That is too coarse for production enforcement.

Phoenix should distinguish:

- `chapter_engine`: elements that make a chapter work
- `proof_and_embodiment`: elements that make the teaching credible or lived
- `optional_accents`: sparse rhetorical flourishes
- `cohesion_and_craft`: devices that make the book feel threaded and interpretable

This keeps the useful sparsity doctrine for optional accents without mistakenly treating evidence, stories, or troubleshooting as decorative extras.

## 5. Contract V2.1 Design Rules

### 5.1 Global optional-accent budget

The optional-accent layer needs a coherent slot budget, otherwise class maxima become mathematically incompatible with chapter-share ceilings.

For a standard 12-chapter trade self-help book:

```yaml
optional_accent_budget:
  target_accent_chapters: 5-7
  hard_max_accent_chapters: 8
  target_total_accents: 7-9
  hard_max_total_accents: 10
  max_accents_per_chapter: 2
  accent_free_chapters_minimum: 4
  chapter_share_rounding: ceil
```

Interpretation:

- At least `4` of `12` chapters should have **no optional accent beat**
- Class-level maxima are ceilings, not instructions to maximize every class simultaneously
- `chapter_share_rounding: ceil` means profile ceilings round up to the next full chapter when converted from fractions

### 5.2 Layer rules

#### Chapter engine

These are not optional accents and should not consume optional-accent budget:

- `VALIDATION_NORMALIZATION`
- `MECHANISM_EXPLANATION`
- `PRACTICE_APPLICATION`
- `TROUBLESHOOTING`
- `TRANSITION_GLUE`
- `CLOSING_TAKEAWAY`
- `PROPULSION`

#### Proof and embodiment

These are not optional accents either:

- `HOOK_STORY`
- `EXTERNAL_STORY`
- `AUTHOR_DISCLOSURE`
- `CASE_STUDY`
- `CITED_EVIDENCE`

Required rules:

- Every `EXTERNAL_STORY` must have a function tag:
  - `recognition`
  - `mechanism_proof`
  - `turn`
  - `possibility`
  - `cautionary`
- Every `EXTERNAL_STORY` must also have truth/provenance metadata
- `AUTHOR_DISCLOSURE` must remain distinct from `AUTHOR_COMMENTARY`

#### Optional accents

These are the elements that should receive true sparsity control:

- `QUOTE`
- `ENCOURAGEMENT`
- `REFLECTION_QUESTION`
- `AUTHOR_COMMENTARY`
- `WISDOM_ESSENCE`

Rules:

- Do not exceed `2` optional accents in one chapter
- Do not stack `QUOTE + WISDOM_ESSENCE + AUTHOR_COMMENTARY` in the same chapter
- At least `30%` of chapters should carry **no optional accent beat**

#### Cohesion and craft

These should be tracked, but not counted as optional accent slots:

- `CALLBACK_PLANT`
- `CALLBACK_RETURN`
- `MOTIF`
- `ANALOGY`
- `METAPHOR`
- `BRIDGE`
- `TRANSITION`

Rules:

- `ANALOGY` and `METAPHOR` must explain, compress, or thread; never decorate
- `CALLBACK_RETURN` must point to a real plant and must change meaning, not merely repeat wording
- `PARABLE` should be treated as a story register inside `HOOK_STORY` or `EXTERNAL_STORY`, not as a generic accent

### 5.3 Counting units

Counts are only useful if the unit is explicit.

```yaml
count_units:
  QUOTE: "borrowed_authority_block"
  ENCOURAGEMENT: "substantial_encouragement_block"
  REFLECTION_QUESTION: "standalone_reflection_prompt"
  AUTHOR_COMMENTARY: "substantial_interpretive_commentary_block"
  WISDOM_ESSENCE: "distilled_wisdom_block"
  CITED_EVIDENCE: "evidence_block"
  EXTERNAL_STORY: "substantial_vignette"
  AUTHOR_DISCLOSURE: "substantial_first_person_disclosure"
  ANALOGY: "major_explanatory_analogy"
  METAPHOR: "developed_or_recurring_metaphor"
  CALLBACK_RETURN: "meaningful_motif_return"
```

Do not count:

- every figurative sentence as a metaphor
- every passing mention as a callback
- every citation footnote as an evidence block
- every first-person sentence as disclosure

### 5.4 Preferred positions, not rigid legality

These should be treated as preferred positions unless a stronger chapter-specific reason overrides them.

- `QUOTE`: opener or near-close preferred; avoid decorative mid-chapter drift
- `CITED_EVIDENCE`: early-to-middle preferred; in high-validation chapters, do not let evidence cold-open before the reader feels seen
- `EXTERNAL_STORY`: opening when story-led, otherwise middle-body preferred
- `ENCOURAGEMENT`: after exercise, after difficult realization, or after turning point
- `TROUBLESHOOTING`: after application or integration, not before understanding exists
- `REFLECTION_QUESTION`: after reflection, before thread, or occasionally chapter-open if the chapter is built around inquiry
- `AUTHOR_COMMENTARY`: after pivot, after exercise, after disclosure, or before thread
- `WISDOM_ESSENCE`: late reflection or near-close preferred
- `CALLBACK_RETURN`: late-middle to close preferred

Use `preferred_positions` and `disallowed_positions` in implementation, not brittle single-position hard gates.

### 5.5 Tie-break rules

When a chapter is already at the `max_accents_per_chapter` ceiling:

- `PARABLE` does not consume an optional-accent slot by itself; it rides inside `HOOK_STORY` or `EXTERNAL_STORY`
- if a contemplative flourish conflict remains, `PARABLE` displaces `WISDOM_ESSENCE` first
- `PARABLE` should not displace `AUTHOR_COMMENTARY` in emotionally intimate chapters
- `ENCOURAGEMENT` and `TROUBLESHOOTING` outrank decorative flourish when a practice chapter would otherwise lose reader support

## 6. Working Priors By Profile

These are recommended **per 12-chapter trade self-help book** targets. These numbers are subordinate to the global slot budget above.

```yaml
schema_version: "2.0.0-working-priors"
truth_label: "research_informed_working_priors"

profiles:
  practical_credible:
    description: "Atomic-Habits-like; mechanism-forward, useful, low-theatrics"
    max_accent_chapter_share: 0.35
    optional_accents:
      QUOTE: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.20 }
      ENCOURAGEMENT: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.20 }
      REFLECTION_QUESTION: { minimum: 0, target: 1, hard_max: 2, priority_weight: 0.35 }
      AUTHOR_COMMENTARY: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.15 }
      WISDOM_ESSENCE: { minimum: 0, target: 0, hard_max: 0, priority_weight: 0.00 }
    proof_and_embodiment:
      CITED_EVIDENCE: { minimum: 2, target: 3, hard_max: 4, priority_weight: 0.90 }
      EXTERNAL_STORY: { minimum: 2, target: 3, hard_max: 4, priority_weight: 0.75 }
      AUTHOR_DISCLOSURE: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.10 }
    chapter_engine_expectations:
      TROUBLESHOOTING: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.75 }
      mechanism_explanation_chapters: 8-12
      analogy_or_metaphor_uses: 6-12
      callback_or_motif_returns: 4-8
      parable_uses: 0

  intimate_voice:
    description: "Emotion-near, reader-close, validation-heavy"
    max_accent_chapter_share: 0.55
    optional_accents:
      QUOTE: { minimum: 0, target: 1, hard_max: 2, priority_weight: 0.30 }
      ENCOURAGEMENT: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.85 }
      REFLECTION_QUESTION: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.70 }
      AUTHOR_COMMENTARY: { minimum: 0, target: 1, hard_max: 2, priority_weight: 0.60 }
      WISDOM_ESSENCE: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.15 }
    proof_and_embodiment:
      CITED_EVIDENCE: { minimum: 0, target: 1, hard_max: 2, priority_weight: 0.30 }
      EXTERNAL_STORY: { minimum: 2, target: 2, hard_max: 3, priority_weight: 0.75 }
      AUTHOR_DISCLOSURE: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.70 }
    chapter_engine_expectations:
      TROUBLESHOOTING: { minimum: 1, target: 1, hard_max: 2, priority_weight: 0.65 }
      high_validation_chapters: 5-8
      mechanism_explanation_chapters: 5-9
      analogy_or_metaphor_uses: 5-10
      callback_or_motif_returns: 5-9
      parable_uses: 0-1

  timeless_wisdom:
    description: "Reflective, distilled, less tactical, more contemplative"
    max_accent_chapter_share: 0.40
    optional_accents:
      QUOTE: { minimum: 0, target: 1, hard_max: 2, priority_weight: 0.30 }
      ENCOURAGEMENT: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.10 }
      REFLECTION_QUESTION: { minimum: 1, target: 1, hard_max: 2, priority_weight: 0.50 }
      AUTHOR_COMMENTARY: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.20 }
      WISDOM_ESSENCE: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.90 }
    proof_and_embodiment:
      CITED_EVIDENCE: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.10 }
      EXTERNAL_STORY: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.55 }
      AUTHOR_DISCLOSURE: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.25 }
    chapter_engine_expectations:
      TROUBLESHOOTING: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.20 }
      mechanism_explanation_chapters: 3-6
      analogy_or_metaphor_uses: 6-12
      callback_or_motif_returns: 5-8
      parable_uses: 1-3
```

## 7. Recommended Phoenix Default For Anxiety Books

For current Phoenix anxiety books, the best working model is a `practical_credible` base with `intimate_voice` modifiers. This is more extensible than proliferating custom hybrid profiles.

### 7.1 Anxiety flagship preset

```yaml
anxiety_flagship_hybrid:
  base: practical_credible
  description: "Validation-forward but still mechanism-clear and actionable"
  modifiers:
    validation_intensity: high
    reader_intimacy: medium_high
    mechanism_density: high
    evidence_density: medium
    action_support: high
    contemplative_register: low
    author_disclosure: medium
  max_accent_chapter_share: 0.50
  optional_accents:
    QUOTE: { minimum: 0, target: 1, hard_max: 2, priority_weight: 0.25 }
    ENCOURAGEMENT: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.85 }
    REFLECTION_QUESTION: { minimum: 1, target: 2, hard_max: 3, priority_weight: 0.75 }
    AUTHOR_COMMENTARY: { minimum: 0, target: 1, hard_max: 2, priority_weight: 0.60 }
    WISDOM_ESSENCE: { minimum: 0, target: 0, hard_max: 1, priority_weight: 0.10 }
  proof_and_embodiment:
    CITED_EVIDENCE: { minimum: 1, target: 1, hard_max: 2, priority_weight: 0.45 }
    EXTERNAL_STORY: { minimum: 2, target: 2, hard_max: 3, priority_weight: 0.80 }
    AUTHOR_DISCLOSURE: { minimum: 1, target: 1, hard_max: 2, priority_weight: 0.55 }
  chapter_engine_expectations:
    TROUBLESHOOTING: { minimum: 1, target: 2, hard_max: 2, priority_weight: 0.80 }
    high_validation_chapters: 5-7
    mechanism_explanation_chapters: 7-10
    analogy_or_metaphor_uses: 6-10
    callback_or_motif_returns: 5-8
    parable_uses: 0-1
  phase_anchors:
    early_chapters:
      prioritize:
        - VALIDATION_NORMALIZATION
        - AUTHOR_DISCLOSURE
        - MECHANISM_EXPLANATION
      optional_accent_bias:
        - REFLECTION_QUESTION
    middle_chapters:
      prioritize:
        - EXTERNAL_STORY
        - PRACTICE_APPLICATION
        - ANALOGY
      optional_accent_bias:
        - ENCOURAGEMENT
    late_chapters:
      prioritize:
        - TROUBLESHOOTING
        - CALLBACK_RETURN
        - PROPULSION
      optional_accent_bias:
        - AUTHOR_COMMENTARY
```

### 7.2 Functional interpretation

- `Validation` should be dense early
- `Mechanism explanation` should recur across the body, not just chapter 1
- `Troubleshooting` should show up after the reader is asked to do something hard
- `External stories` should alternate between recognition and mechanism proof
- `Author commentary` should feel human, not preachy
- `Wisdom essence` should be used carefully, not as filler
- `CITED_EVIDENCE` should not cold-open high-validation chapters ahead of emotional safety
- `CALLBACK_RETURN` should be treated as a first-order cohesion tool for this profile

## 8. Chapter Archetypes, Not Formulaic Four-Phase Repetition

The four-phase blueprint remains useful at the book level:

- arrival
- discovery
- action
- integration

But Phoenix should not force every chapter to execute all four phases in the same order. That becomes workshop-like and predictable.

Preferred dominant chapter archetypes:

- `recognition_chapter`
- `mechanism_chapter`
- `reframe_chapter`
- `practice_chapter`
- `resistance_chapter`
- `integration_chapter`

The whole book should achieve the four-phase journey. Individual chapters can emphasize different jobs.

## 9. Callback Ledger Requirements

Callback quality cannot be governed by counts alone.

Every callback return should point to a real plant:

```yaml
callback:
  plant_id: "caged-bird-image"
  planted_in_chapter: 1
  returned_in_chapter: 7
  return_function: "reinterpret"
  semantic_change: "from trapped nervous system to protective adaptation"
```

Useful `return_function` values:

- `remind`
- `deepen`
- `reinterpret`
- `invert`
- `transfer`
- `resolve`
- `close`

Strong returns change meaning. They do not merely repeat a phrase.

Required fields for `CALLBACK_RETURN`:

- `plant_id`
- `return_function`
- `semantic_development`

## 10. Truth Controls For Stories And Evidence

Function tagging is necessary but insufficient.

### 10.1 External story metadata

```yaml
story_metadata:
  function: "recognition"
  source_type: "documented_public_case"
  source_reference: "..."
  identity_handling: "anonymized"
  factuality_status: "verified"
```

Allowed `source_type` values should include:

- `documented_public_case`
- `author_provided_story`
- `interviewed_subject`
- `anonymized_real_story`
- `disclosed_composite`
- `explicitly_hypothetical_example`

Phoenix should never invent a person and imply that person is a real case.

### 10.2 Evidence metadata

```yaml
evidence_metadata:
  claim_supported: "..."
  source_tier: "peer_reviewed_primary"
  evidence_strength: "moderate"
  limitations_acknowledged: true
```

Two strong, accurately framed evidence blocks are often more credible than many weak citations.

## 11. Author Disclosure Versus Author Commentary

These should remain separate.

### 11.1 Author disclosure

The author reveals something experienced, feared, misunderstood, attempted, or learned.

Possible functions:

- `credibility`
- `vulnerability`
- `companionship`
- `failure_model`
- `turning_point`
- `limits_of_authority`

### 11.2 Author commentary

The author interprets what the reader has just encountered.

Possible functions:

- `interpretation`
- `emphasis`
- `permission`
- `orientation`
- `boundary`
- `transition`

For anxiety books, disclosure should remain reader-serving:

> Does this disclosure help the reader understand themselves, or does it merely make the author more visible?

## 12. Recommended V2.1 Structure

```yaml
schema_version: "2.1.0-working-priors"
truth_label: "research_informed_working_priors"

chapter_engine:
  tracked_fields:
    - VALIDATION_NORMALIZATION
    - MECHANISM_EXPLANATION
    - PRACTICE_APPLICATION
    - TROUBLESHOOTING
    - TRANSITION_GLUE
    - CLOSING_TAKEAWAY
    - PROPULSION

proof_and_embodiment:
  tracked_fields:
    - HOOK_STORY
    - EXTERNAL_STORY
    - AUTHOR_DISCLOSURE
    - CASE_STUDY
    - CITED_EVIDENCE
  require_function_tags: true
  require_provenance: true

optional_accents:
  tracked_fields:
    - QUOTE
    - ENCOURAGEMENT
    - REFLECTION_QUESTION
    - AUTHOR_COMMENTARY
    - WISDOM_ESSENCE
  budget:
    target_accent_chapters: 5-7
    hard_max_accent_chapters: 8
    target_total_accents: 7-9
    hard_max_total_accents: 10
    max_per_chapter: 2

cohesion_and_craft:
  tracked_fields:
    - CALLBACK_PLANT
    - CALLBACK_RETURN
    - MOTIF
    - ANALOGY
    - METAPHOR
  callback_returns_require_plant: true
  callback_returns_require_function: true
```

## 13. What Should Be Added In Contract V2
These should be promoted into explicit tracked planning fields even if they do not all become optional accent classes:

- `CALLBACK_PLANT`
- `CALLBACK_RETURN`
- `ANALOGY`
- `METAPHOR`
- `STORY_FUNCTION`
- `OBJECTION_HANDLING`
- `SHAME_RECOGNITION`
- `PROPULSION`

### 13.1 Recommended treatment

- `CALLBACK_*`: tracked explicitly in planner and outline
- `ANALOGY` / `METAPHOR`: tracked as craft counts and chapter placement signals
- `PARABLE`: tracked as a story subtype, not a universal beat class
- `OBJECTION_HANDLING` / `SHAME_RECOGNITION`: either folded into chapter-engine support or promoted if the books need finer control

## 14. Recommended Changes Versus Current Config

These are the main adjustments this working-priors spec recommends:

- Keep `practical_credible` relatively sparse
- Lower the effective aggressiveness of `intimate_voice` from a near-ubiquitous accent feel to a still-rich but less noisy one
- Treat `QUOTE` as optional and selective, not mandatory prestige
- Move `TROUBLESHOOTING` out of the optional-accent bucket and into chapter-engine expectations
- Move `CITED_EVIDENCE` and `EXTERNAL_STORY` out of the optional-accent bucket and into proof/embodiment expectations
- Govern `EXTERNAL_STORY` by function and provenance, not just by count
- Add explicit planning for `CALLBACK`, `ANALOGY`, and `METAPHOR`
- Separate `AUTHOR_DISCLOSURE` from `AUTHOR_COMMENTARY`
- Keep `PARABLE` sparse and profile-bound

## 15. What We Should Not Overclaim

We should not claim:

- that exact numeric dosage is scientifically settled
- that current per-book counts are fully benchmarked across 10 analyzable editions
- that Phoenix has already proven the exact count targets by empirical chapter-by-chapter observation

We can honestly claim:

- these are research-informed working priors
- they are aligned with current bestseller-pattern research
- they are safer and more grounded than ad hoc guessing
- they are better suited to memo-level calibration than immediate hard-gate enforcement

## 16. Immediate Dev Priority

If Phoenix wants a stronger real-world enhancement contract next, the most valuable implementation order is:

1. Separate `chapter_engine`, `proof_and_embodiment`, `optional_accents`, and `cohesion_and_craft`
2. Resolve optional-accent slot-budget arithmetic
3. Make `CALLBACK` explicit end-to-end
4. Add `STORY_FUNCTION` plus provenance tracking for all `EXTERNAL_STORY` beats
5. Define count units for each tracked class
6. Add chapter-level `ANALOGY` / `METAPHOR` audit counts
7. Separate `AUTHOR_DISCLOSURE` from `AUTHOR_COMMENTARY`
8. Move `PROPULSION`, `TRANSITION_GLUE`, and `CLOSING_TAKEAWAY` into chapter-flow enforcement
9. Add profile-specific gates for over-accenting and under-support
10. Keep `PARABLE` behind profile gating, not global default
