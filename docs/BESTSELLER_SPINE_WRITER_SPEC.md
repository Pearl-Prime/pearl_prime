# Bestseller Spine Writer Spec

*Owner: Pearl_Writer | Created: 2026-04-10 | Status: permanent reference*

---

## Purpose

This spec governs the creation and validation of topic-family book spines for Phoenix Omega.
A spine is the book's architecture — reader journey, chapter order, argument structure, emotional arc,
and transformation logic — written before atom enrichment. The spine does the heavy lifting.
Enrichment makes it exceptional, not viable.

**Spines live at:** `config/spines/{family_id}_spine.yaml`

---

## What A Spine Is

A spine is NOT:
- A chapter draft or prose text
- A set of atom prompts
- A table of contents with summaries
- A list of topics to cover

A spine IS:
- The reader's transformation arc, chapter by chapter
- The argument the book makes (claim + evidence + so what)
- The emotional pressure curve (where trust builds, where it's tested, where it pays off)
- The sequencing logic (why this order and no other)
- The practical payoff timing (when exercises arrive and why)
- The prohibition map (what this family must never do)

---

## Spine File Structure

```yaml
family_id: {id}
family_name: "{display name}"
adjacent_topics: [{list of related families}]
primary_mechanism: {primary engine}
allowed_engines: [{list from topic_engine_bindings.yaml}]

reader_starting_state: >
  [Where the reader is at page 1 — sensory, behavioral, cognitive. Not abstract. Specific.]

reader_ending_state: >
  [Where the reader is at the last page. Not "they will feel better." What has actually changed.]

what_makes_this_family_different: >
  [Structural demands unique to this family. What would go wrong if you used a different family's architecture here.]

chapters:
  chapter_01:
    number: 1
    role: {unique role}
    working_title: "{sounds like a real book chapter}"
    thesis: >
      [The one claim this chapter makes. A reader could disagree with it.]
    emotional_job: >
      [What the reader feels by chapter end. Not what they think — what they feel.]
    practical_job: >
      [What the reader can identify, name, or do that they couldn't before this chapter.]
    what_changes: >
      Before: "[reader's belief or experience at chapter start]"
      After: "[reader's belief or experience at chapter end]"
    required_sections: [HOOK, SCENE, REFLECTION]
    forbidden_moves:
      - [What NOT to do in this chapter — specific, not generic]
    recommended_enrichments:
      - [Persona or teacher voice suggestions for atom writers]
    claim_someone_could_argue: >
      [The chapter's most arguable claim — what a skeptical reader might push back on]
    why_this_chapter_exists: >
      [What breaks without this chapter. What the reader would miss.]
    what_comes_next: >
      [Bridge to next chapter — why the reader is ready for what comes next]

  # chapters 02-12 follow with unique roles

sequencing_rules:
  must_come_before:
    - [ordering dependencies]
  cannot_come_too_early:
    - [what must wait until trust is built]
  saved_for_late_book:
    - [what belongs in ch10-12 only]

tone_and_pacing:
  intensity_profile: [low/medium/high × 12]
  trust_curve: >
    [How trust is built (ch1-3), spent (ch4-6), rebuilt (ch7-9), deepened (ch10-12)]
  action_timing: >
    [When first real practice arrives; when escalation happens; when pressure arrives]
  mechanism_timing: >
    [When the mechanism is first named; when it's deepened; when it's challenged]
  permission_timing: >
    [When the key permissions are granted — permission to have learned this, to feel this, to be this]

prohibited_terms:
  global: [journey, transform, heal, self-care, wellness, mindfulness, empower, empowering,
           overcome, conquer, battle, fight, warrior, survivor, thrive, manifest,
           authentic self, best self, inner child, trigger warning, safe space, toxic,
           self-love, you've got this, be gentle with yourself]
  family_specific: [{terms from topic_skins.yaml for this family}]
```

---

## Chapter Role Schema

Every chapter must have a UNIQUE role. No two chapters in any spine may do the same job.
If two chapters can be swapped without damaging the arc, one must be rewritten.

| Role | What it does |
|------|-------------|
| `recognition` | "You do this and you didn't know it was a pattern." The reader sees themselves. |
| `cost_exposure` | "Here is what this pattern actually costs you." Real cost, not abstract. |
| `hidden_belief` | "Here is the belief underneath the pattern." The assumption the reader didn't know they had. |
| `destabilization` | "Your current strategy isn't working, and here's why." The reader's approach is named as the obstacle. |
| `somatic_legitimacy` | "Your body is not broken; it learned something." The physical response is intelligent. |
| `mechanism` | "This is what is actually happening." Named model, body terms, not cognitive abstraction. |
| `relational_consequence` | "This pattern affects your relationships like this." Real relational stakes. |
| `identity_fracture` | "Who you thought you were vs who you actually are." The reader's self-concept cracks. |
| `practical_interruption` | "Here is one thing you can do differently." Small, specific, somatic. Not a plan. |
| `practice_under_pressure` | "Now do it when it's hard." The real-world test. |
| `reframe` | "The same facts, seen differently." Not toxic positivity — a genuinely different frame that's true. |
| `self_relation_shift` | "How you relate to yourself is changing." The internal relationship, not the external behavior. |
| `integration` | "This is who you are becoming, and what comes next." Not triumph. Honest forward. |

Custom roles are permitted if they are more precise than the above. But they must still be unique within the spine.

---

## Quality Standards

### A Spine PASSES If:

- It produces a meaningful reader transformation (not just education)
- Chapter order feels NECESSARY — remove any chapter and the arc breaks
- The journey is FAMILY-APPROPRIATE — grief architecture ≠ anxiety architecture ≠ burnout architecture
- It can support multiple adjacent topics via the allowed_engines list
- It is strong BEFORE enrichment — enrichment makes it exceptional, not viable
- Every chapter has a claim someone could argue with
- No two chapters do the same job
- The emotional arc has real pressure AND real relief
- Practical payoff arrives at the right time (not too early, not too late)
- A reader would keep listening after chapter 3

### A Spine FAILS If:

- It repeats the same idea in different words across chapters
- It front-loads insight and back-loads only exercises
- It introduces action before trust and legitimacy are built
- It becomes preachy or generic
- It feels like "12 blog posts in a row"
- Grief resolves too quickly (grief doesn't resolve — it integrates)
- Anxiety becomes simple mindset advice
- Shame becomes affirmations
- Burnout becomes productivity optimization
- Depression becomes a pep talk
- Courage becomes "just do it" or fearlessness

---

## Family-Specific Structural Rules

### Grief
- Legitimacy and witnessing MUST come before any action
- No "fix" energy before chapter 8 minimum
- Integration must be gentle — grief doesn't resolve, it integrates
- Identity after loss must be addressed (ch10-11)
- The word "stages" is banned — grief doesn't follow stages
- Forbidden engines: false_alarm, spiral, shame, comparison, overwhelm

### Anxiety
- Recognition and false-protection logic must come early (ch1-2)
- Body legitimacy must precede heavy action asks
- Control strategies must be destabilized before practices land
- First real practice: ch5 or later (small, safe, somatic)
- Do NOT turn anxiety into mindset advice

### Burnout
- Exhaustion must be legitimized before responsibility reframing
- Collapse cost must become visible (not just "you're tired")
- Rebuilding comes AFTER disentangling worth from usefulness
- Rest is not the solution — relationship to capacity is
- Do NOT turn burnout into productivity optimization

### Self_Worth / Shame
- The scorecard must be named before it can be questioned
- Shame physiology must be addressed (not just cognitive reframe)
- External validation dependency must be exposed mid-book
- Unconditional ground arrives late (ch10-11), not early
- Do NOT turn shame into affirmations

### Imposter_Syndrome
- Comparison mechanism comes before shame mechanism
- Achievement does not resolve imposter — that's the trap
- The "evidence never counts" pattern must be named
- Identity must shift from "proving" to "being"

### Boundaries
- False alarm on saying "no" must be legitimized first
- Guilt is the body's response, not proof of wrongdoing
- Relational consequence must be faced honestly (ch7-8)
- Limits are clarity, not walls

### Depression
- Energy conservation must be respected, not pathologized
- Activation must be tiny and somatic (not motivational)
- Meaning-making comes late — do not rush it
- The numbness is protection, not failure
- No clinical vocabulary anywhere

### Courage
- Fear is expected and legitimate
- Action arrives earlier than in other families (ch4-5)
- Exposure and tolerance build across chapters
- The body's alarm on action is the material, not the obstacle

### Overthinking
- The spiral must be named as a pattern, not a personality trait
- Attention redirection alone doesn't work — address the WHY
- Body-based interruption before cognitive restructuring
- "Figuring it out" is the problem, not the solution

### Compassion_Fatigue
- Depletion must be legitimized without guilt
- The "I should be able to handle this" belief must be exposed
- Receiving must be practiced (not just "take a break")
- Professional identity and personal depletion must be separated

### Social_Anxiety
- False alarm + shame double mechanism — both must be named separately
- The scanning/performing pattern must be named
- Safety behaviors must be exposed as maintaining the problem
- Small exposures with somatic support (not "just do it")

### Sleep_Anxiety
- The vigilance-at-rest pattern must be named
- Control strategies (sleep hygiene obsession) must be destabilized
- Body trust before sleep arrives naturally
- The bed as a safe place must be rebuilt, not forced

### Financial_Anxiety / Financial_Stress
- Shame about money must be addressed early
- Avoidance pattern (not checking accounts) must be named
- Practical financial moves come AFTER emotional regulation
- Worth is not net worth — but do not dismiss real stress

### Somatic_Healing
- The body remembers what the mind forgot
- Observation precedes intervention
- Sensation is information, not emergency
- Integration is the goal, not catharsis

---

## Prohibited Terms

### Global (all families)

`journey`, `transform`, `heal`, `healing journey`, `self-care`, `wellness`, `mindfulness`,
`empower`, `empowering`, `overcome`, `conquer`, `battle`, `fight`, `warrior`, `survivor`,
`thrive`, `manifest`, `authentic self`, `best self`, `inner child`, `trigger warning`,
`safe space`, `toxic`, `self-love`, `you've got this`, `be gentle with yourself`

### Per-Family

See `config/topic_skins.yaml` for the authoritative per-family prohibited term list.
The spine YAML for each family must include its own `prohibited_terms.family_specific` list
pulled from the topic skin file.

---

## Sequencing Principles

### Universal ordering constraints

1. Recognition before mechanism — the reader must see themselves before they understand why
2. Legitimacy before action — the reader must feel their experience is real before being asked to change it
3. Cost before reframe — the reader must know the cost of their pattern before a new frame can land
4. Mechanism before practice — the reader must understand what's happening before they can practice something different
5. Body before cognition — somatic legitimacy before cognitive restructuring
6. Trust before destabilization — the reader must trust the author before their coping strategy can be challenged
7. Identity work in late book — not before chapter 9

### Timing by chapter position

| Position | What belongs here |
|----------|------------------|
| Ch 1-2 | Recognition and legitimacy — the reader sees themselves and feels seen |
| Ch 3-4 | Mechanism — what is actually happening and why |
| Ch 5-6 | Cost and turning point — what this costs and what's possible instead |
| Ch 7-8 | Practice — first real action and escalation under normal pressure |
| Ch 9-10 | Integration and relapse — the body updating; the pattern returning |
| Ch 11-12 | Identity and forward — who this person is becoming |

First practice window: ch5-7 (earlier for courage, later for grief and depression)

---

## Engine Binding Reference

All engines must come from `config/topic_engine_bindings.yaml`. Spines may not use
forbidden engines for their family. The allowed_engines list in each spine must match
the bindings file exactly.

| Engine | What it does in content |
|--------|------------------------|
| `false_alarm` | Body reacts as if danger when no real danger exists |
| `spiral` | Thought chains that escalate toward catastrophe |
| `watcher` | Observing one's own life from behind protective distance |
| `overwhelm` | Volume/saturation — everything feels equally urgent and too large |
| `shame` | Value tied to external outcomes; exposure fear; being seen as inadequate |
| `comparison` | Worth measured against others |
| `grief` | Absence made present; mourning what was |

---

## Relationship to Other Pipeline Components

| Component | Relationship to spine |
|-----------|----------------------|
| `registry/{family}.yaml` | Atom content that populates spine chapters — generated after spine |
| `config/topic_skins.yaml` | Vocabulary guard — governs all text generated from the spine |
| `config/topic_engine_bindings.yaml` | Engine authority — spine must not exceed allowed engines |
| `config/registry/topic_chapter_titles.yaml` | Production chapter titles — spine should use or extend these |
| `specs/PHOENIX_V4_5_WRITER_SPEC.md` | TTS prose law and atom type definitions — governs atom-level content |
| `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md` | Quality standard research — what real bestsellers do |

---

## Versioning and Updates

- Spines are versioned by family. Any update to a spine should be reflected in a new commit with the family name.
- If a spine's chapter order changes after atoms have been generated, atom regeneration may be required.
- The chapter title map in `config/registry/topic_chapter_titles.yaml` should be updated if spine working titles diverge significantly from production titles.
- New families must be added to `config/catalog_planning/canonical_topics.yaml` before a spine is created.

---

## Creation Checklist

Before marking a spine as production-ready:

- [ ] All 12 chapters present with unique roles
- [ ] Every chapter has: thesis, emotional_job, practical_job, what_changes, required_sections, forbidden_moves, claim_someone_could_argue, why_this_chapter_exists, what_comes_next
- [ ] No prohibited terms (global or family-specific) appear anywhere in the YAML
- [ ] Engine bindings match `config/topic_engine_bindings.yaml`
- [ ] sequencing_rules.must_come_before reflects the actual chapter order
- [ ] tone_and_pacing.intensity_profile has exactly 12 values
- [ ] reader_starting_state is specific and behavioral (not abstract)
- [ ] reader_ending_state describes actual change (not just "they will feel better")
- [ ] The family_specific prohibited_terms list is populated from topic_skins.yaml
- [ ] File parses as valid YAML
