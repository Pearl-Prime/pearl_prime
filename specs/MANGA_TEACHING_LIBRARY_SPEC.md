# Teaching Library Specification
## AI Manga Dharma System v1.0

**SpiritualTech Systems · Teaching Library Spec v1.0**

---

## Overview

The Teaching Library is the Dharma OS—the foundational layer containing every wisdom atom deployed across the entire manga creation pipeline. It is the source of truth that sits above all agents and directs all downstream storytelling.

**Core Mandate:** Define WHAT wisdom to teach; Genre Agent defines HOW to embed it into story. Teaching Library is philosophy; Genre Agent is craft.

**Data Flow:** Teaching Library → Genre Agent → Story Architect → Chapter Writer → Visual Agent → Lettering Agent → Layout Agent → QC Agent

Only the Genre Agent consumes Teaching Library atoms directly. Chapter Writer never accesses the Teaching Library; Chapter Writer receives shaped, genre-specific transmission maps from Genre Agent (with the actual atom text withheld; only hiding places and methods are given).

---

## Wisdom Atom Schema

Every wisdom atom is a structured container serving specific pipeline functions. Atoms are immutable once created; variants are new atoms, never modifications.

### Core Fields

```json
{
  "atom_id": "impermanence_01",
  "version": "1.0",
  "created_date": "2026-03-21",
  "tradition": "Buddhist",
  "sub_tradition": "Theravada",
  "author_lineage": "Thich Nhat Hanh",

  "wound_target": "clinging|control_need|identity_fixation|fear_of_loss|isolation",
  "somatic_target": "breath_rhythm|chest_constriction|jaw_tension|heart_space|gut_awareness",
  "depth_level": "surface|recognition|somatic|integration",
  "teaching_method": "structural|experiential|silence|accumulation",

  "text": "All conditioned phenomena are impermanent. Clinging to permanence is the source of suffering. Releasing the grip is not loss; it is the beginning of flow.",
  "text_source": "Buddhist Sutras / Personal Teaching",
  "text_length_characters": 142,

  "story_hooks": [
    {
      "genre": "shōnen",
      "hook_moment": "protagonist realizes teacher/mentor will not always be present",
      "narrative_function": "loss becomes fuel for growth",
      "integration_note": "absence becomes presence through internalized wisdom"
    },
    {
      "genre": "iyashikei",
      "hook_moment": "seasonal change, ritual shifts with weather",
      "narrative_function": "acceptance of rhythm, not resistance to change",
      "integration_note": "surrender to natural flow"
    }
  ],

  "deployment_constraints": [
    "Never deploy this atom through dialogue",
    "Requires minimum 2 chapters of setup before peak moment",
    "Forbidden near present-tense fear language",
    "Best deployed in moment of visible loss or absence"
  ],

  "compound_pairing_ids": ["grief_01", "interdependence_02"],
  "compound_synergy_notes": "When paired with grief_01, impermanence becomes 'letting go with love.' When paired with interdependence_02, impermanence becomes 'all things flow together.'",

  "reader_impact_level": "high_emotional|moderate|foundational",
  "processing_time_chapters": 3,

  "qa_approved": true,
  "approved_by": "pearl_editor",
  "qa_notes": "Somatic accuracy verified. Story hooks tested across 4 genres."
}
```

### Field Definitions

- **atom_id:** Unique identifier (tradition_concept_number format)
- **tradition:** Buddhist / Sufi / Vedic / Indigenous / Cross-tradition
- **wound_target:** Primary psychological wound this atom addresses (from reader profiling)
- **somatic_target:** Where in the body the reader embodies this teaching (breath, chest, belly, etc.)
- **depth_level:**
  - **surface:** Intellectual understanding only
  - **recognition:** Emotional knowing; reader says "oh, that's true"
  - **somatic:** Body-level integration; reader feels truth in cells
  - **integration:** Behavioral shift; reader acts from new understanding without conscious choice
- **teaching_method:**
  - **structural:** Teaching is embedded in story/arc/character structure itself
  - **experiential:** Teaching arrives through character choice and consequence
  - **silence:** Teaching transmitted through what is NOT shown, NOT said, NOT narrated
  - **accumulation:** Teaching delivered through repetition across chapters; pattern recognition becomes wisdom
- **story_hooks:** Pre-mapped integration points for specific genres (helps Genre Agent in Step 2)
- **deployment_constraints:** Hard restrictions on where/how atom can be used
- **compound_pairing_ids:** Other atoms that unlock deeper teaching when paired
- **reader_impact_level:** Expected emotional weight; helps Genre Agent prioritize

---

## Wisdom Atom Taxonomy

### By Tradition

**Buddhist Atoms (Primary Focus)**
- Impermanence (anicca)
- Non-self (anatta)
- Suffering/Dukkha and its cessation
- Dependent origination
- Right effort/right livelihood
- Mindful awareness

**Sufi Atoms (Heart-Centered)**
- Heart opening / Qalb expansion
- Annihilation of ego (fana)
- Love as teaching method
- Mirror principle (recognizing God in other)
- Service as spiritual practice
- Divine intoxication / Sobriety balance

**Vedic Atoms (Consciousness-Centered)**
- Witness consciousness (Sakshi)
- Brahman / non-dual reality
- Prarabdha karma (played-out karma)
- Dharma / cosmic order
- Sat-chit-ananda (being-consciousness-bliss)
- Vasanas (latent impressions)

**Indigenous Atoms (Relational)**
- Interconnection / All my relations
- Reciprocal responsibility
- Land as ancestor
- Seasonal alignment
- Grief as relational honoring
- Community healing

**Cross-Tradition Atoms (Universal Truths)**
- Forgiveness / release of harm-holding
- Grief embodiment and integration
- Belonging (not fitting in; true belonging)
- Shadow integration
- Presence in difficulty
- Integrity as alignment with deepest values

---

## Seed Library: 20 Foundation Atoms

These 20 atoms form the core teaching toolkit. They are battle-tested, genre-compatible, and deployable across multiple story contexts.

### Impermanence Cluster

1. **impermanence_01** (Buddhist)
   - Wound: clinging to permanence
   - Depth: recognition → somatic
   - Method: structural
   - Genres: shōnen, seinen, iyashikei, isekai
   - Somatic: breath awareness of transitions

2. **impermanence_02** (Buddhist)
   - Wound: fear of loss
   - Depth: somatic → integration
   - Method: experiential + silence
   - Genres: shōjo, iyashikei, horror
   - Somatic: chest softening in acceptance

3. **impermanence_03_isekai** (Buddhist + Cross-tradition)
   - Wound: fatalism, "things cannot change"
   - Depth: recognition → integration
   - Method: structural
   - Genres: isekai (primary), shōnen
   - Somatic: gut relaxation as rules are broken

### Non-Self / Identity Cluster

4. **anatta_01** (Buddhist)
   - Wound: identity fixation, "I am my story"
   - Depth: recognition → somatic
   - Method: silence + accumulation
   - Genres: seinen, shōjo, cultivation
   - Somatic: subtle shift in how protagonist holds identity

5. **mirror_02** (Sufi)
   - Wound: not seeing oneself reflected in other
   - Depth: somatic → integration
   - Method: experiential
   - Genres: shōjo, seinen, webtoon romance
   - Somatic: heart opening as mutual recognition
   - Paired with: anatta_01

6. **witness_consciousness_03** (Vedic)
   - Wound: entanglement in thoughts/emotions
   - Depth: recognition → somatic
   - Method: structural + silence
   - Genres: cultivation, seinen, iyashikei
   - Somatic: space between thought and awareness

### Suffering & Cessation Cluster

7. **dukkha_01** (Buddhist)
   - Wound: denial of difficulty, spiritual bypass
   - Depth: recognition → somatic
   - Method: structural (plot demonstrates)
   - Genres: shōnen, seinen, horror
   - Somatic: honoring of difficulty

8. **dukkha_cessation_02** (Buddhist)
   - Wound: belief that suffering cannot end
   - Depth: somatic → integration
   - Method: accumulation + silence
   - Genres: iyashikei, shōjo, seinen
   - Somatic: gradual body relaxation
   - Paired with: dukkha_01

### Heart & Service Cluster

9. **heart_opening_01** (Sufi)
   - Wound: emotional closure, protective numbness
   - Depth: recognition → somatic
   - Method: experiential
   - Genres: shōjo, iyashikei, webtoon romance
   - Somatic: chest/throat opening

10. **service_02** (Sufi + Cross-tradition)
    - Wound: isolating self-focus, false autonomy
    - Depth: recognition → integration
    - Method: structural + experiential
    - Genres: shōnen, sports, cultivation
    - Somatic: shared heartbeat, collective rhythm

### Interconnection & Responsibility Cluster

11. **interconnection_01** (Indigenous)
    - Wound: isolation, false separateness
    - Depth: recognition → somatic
    - Method: accumulation + silence
    - Genres: iyashikei, seinen, cultivation
    - Somatic: sense of belonging to larger system

12. **reciprocal_responsibility_02** (Indigenous)
    - Wound: exploitation, one-way extraction
    - Depth: recognition → integration
    - Method: structural (consequences show duty)
    - Genres: shōnen, isekai, seinen
    - Somatic: sense of mutual obligation and joy

### Grief & Integration Cluster

13. **grief_embodiment_01** (Cross-tradition)
    - Wound: grief avoidance, numbness
    - Depth: somatic → integration
    - Method: silence + experiential
    - Genres: seinen, shōjo, iyashikei, horror
    - Somatic: throat, chest, belly opening
    - Paired with: impermanence_01

14. **grief_as_love_02** (Buddhist + Sufi)
    - Wound: seeing grief as failure
    - Depth: recognition → somatic
    - Method: structural + accumulation
    - Genres: shōjo, iyashikei, webtoon romance
    - Somatic: heart expansion in sorrow
    - Paired with: grief_embodiment_01

### Shadow & Integration Cluster

15. **shadow_recognition_01** (Cross-tradition)
    - Wound: split self, denying disowned parts
    - Depth: somatic → integration
    - Method: structural (villain as shadow)
    - Genres: seinen, horror, shōnen
    - Somatic: integration of opposite within
    - Pairing note: Use in villain design

16. **shadow_integration_02** (Vedic + Cross-tradition)
    - Wound: perfectionism, self-rejection
    - Depth: recognition → integration
    - Method: silence + accumulation
    - Genres: cultivation, seinen, shōjo
    - Somatic: acceptance at core
    - Paired with: shadow_recognition_01

### Belonging & Acceptance Cluster

17. **true_belonging_01** (Cross-tradition)
    - Wound: fitting in vs. true belonging
    - Depth: recognition → somatic
    - Method: accumulation + experiential
    - Genres: shōjo, iyashikei, webtoon romance
    - Somatic: ease in presence of others
    - Pairing note: Often appears late-story

18. **presence_in_difficulty_02** (Sufi + Buddhist)
    - Wound: avoidance, escape fantasy
    - Depth: somatic → integration
    - Method: structural + silence
    - Genres: seinen, horror, cultivation
    - Somatic: breath in difficulty

### Forgiveness & Release Cluster

19. **forgiveness_01** (Cross-tradition)
    - Wound: harm-holding, grudge-carrying
    - Depth: recognition → somatic
    - Method: experiential + silence
    - Genres: shōnen, shōjo, seinen, iyashikei
    - Somatic: jaw release, heart softening
    - Pairing note: Usually deployed late in arc

20. **dharma_integrity_02** (Vedic + Cross-tradition)
    - Wound: disconnection from values, drifting
    - Depth: recognition → integration
    - Method: structural (choices encode dharma)
    - Genres: shōnen, cultivation, seinen, isekai
    - Somatic: alignment throughout body
    - Pairing note: Often the final arc atom

---

## 5 Seed Series Concepts

These are pre-mapped story frameworks showing how the teaching library deploys across full narrative arcs. They serve as templates for Genre Agent and Story Architect.

### Series 1: "The Boy Who Stopped Running"

**Concept:** Shōnen story of a protagonist driven by ambition, burning out through constant escalation, learning Buddhist impermanence as the path to sustainable growth.

**Target Wound:** Burnout, fear of worthlessness without constant achievement

**Primary Atoms:**
- impermanence_01 (core teaching)
- dukkha_01 (the suffering of striving)
- dukkha_cessation_02 (finding ease in effort)
- dharma_integrity_02 (aligning with deeper purpose)

**Pacing:** 12-15 chapter serialization
- Chapters 1-3: Setup (ambition as identity)
- Chapters 4-7: Fracture (burnout manifests)
- Chapters 8-11: Integration (new approach emerges)
- Chapters 12-15: Resolution (sustainable growth revealed)

**Villain:** The Shadow of Ambition—a character who represents unchecked striving, showing the protagonist their own future if they don't shift

**Genre Notes:** Shōnen reader expects escalation, but the teaching inverts expectation: escalation leads to collapse; descent into acceptance leads to true strength. This breaks shōnen convention intentionally to deliver the teaching.

---

### Series 2: "Mirror Demon"

**Concept:** Seinen psychological story of a protagonist confronting a doppelgänger villain who embodies their disowned self, leading to shadow integration and true identity.

**Target Wound:** Identity fracture, self-worth collapse, perfectionism

**Primary Atoms:**
- anatta_01 (non-self: identity is fluid)
- mirror_02 (Sufi mirror: recognizing self in other)
- shadow_recognition_01 (villain as disowned self)
- shadow_integration_02 (integrating opposite)
- true_belonging_01 (belonging to self, first)

**Pacing:** 20+ chapter serialization (seinen allows extended subtlety)
- Chapters 1-5: Normalcy (protagonist's careful identity construction)
- Chapters 6-12: Cracks (mirror moments reveal disowned self)
- Chapters 13-18: Dissolution (identity construct collapses)
- Chapters 19+: Reconstruction (integration of shadow into wholeness)

**Villain:** The Doppelgänger—not evil, but the protagonist's shadow made visible. Defeat isn't annihilation; it's absorption.

**Genre Notes:** Seinen reader expects moral complexity and subtext. The villain is sympathetic; the teaching lives in the moment protagonist realizes they ARE the villain (and the villain IS them).

---

### Series 3: "The 10,000 Nets"

**Concept:** Cultivation/Xianxia story of a protagonist learning that control and mastery are illusions; true power emerges from witness consciousness and non-attachment.

**Target Wound:** Control obsession, fear of powerlessness, identity through acquisition

**Primary Atoms:**
- witness_consciousness_03 (Vedic awareness beyond mind)
- impermanence_02 (impermanence of power itself)
- anatta_01 (non-self applied to cultivator identity)
- dharma_integrity_02 (alignment with cosmic order, not personal will)
- reciprocal_responsibility_02 (power as service, not possession)

**Pacing:** 30+ chapter arc (cultivation allows epic scale)
- Chapters 1-8: Initiation (protagonist pursues mastery)
- Chapters 9-18: Escalation (power increases, control tightens)
- Chapters 19-26: Threshold (enlightenment moment: mastery was the cage)
- Chapters 27+: Integration (power used from witness consciousness, not ego will)

**Villain:** The Immortal Tyrant—a cultivator who achieved ultimate power through ultimate control, now trapped in that achievement. Cannot evolve further. Shows protagonist the teaching through negative example.

**Genre Notes:** Xianxia reader expects progression and power revelation. The teaching inverts: highest power is non-action (wu wei), greatest achievement is the dissolution of the achiever.

---

### Series 4: "Grief Garden"

**Concept:** Iyashikei story of a protagonist arriving in a quiet village to heal from loss, learning that grief is not a problem to solve but a relationship to honor, embodying interconnection through seasonal cycles.

**Target Wound:** Grief avoidance, disconnection, loss of belonging

**Primary Atoms:**
- grief_embodiment_01 (somatic grief work)
- grief_as_love_02 (grief reveals the depth of love)
- interconnection_01 (belonging to larger cycles)
- true_belonging_01 (village acceptance without transformation)
- impermanence_02 (seasonal impermanence as natural rhythm)

**Pacing:** 12-16 chapter serialization (iyashikei allows extended meditative pacing)
- Chapters 1-2: Arrival (exhaustion, need for rest)
- Chapters 3-6: Spring/First Acceptance (small permissions to rest)
- Chapters 7-10: Summer/Deepening (ritual participation, community inclusion)
- Chapters 11-14: Autumn/Integration (grief as part of belonging)
- Chapters 15-16: Winter/Resolution (grief transformed into love-memory)

**Villain:** There is no villain. The antagonist is the protagonist's own resistance to staying, the fear that stillness equals abandonment. The teaching is that staying is itself the healing.

**Genre Notes:** Iyashikei reader seeks restoration and permission to rest. The teaching is that grief is welcome here; this community holds grief as love. No resolution is necessary; belonging is itself the resolution.

---

### Series 5: "Thread Walker"

**Concept:** Manhwa/Webtoon series of a protagonist discovering they can see the "threads" of inherited trauma and choice running through their family, learning to honor family history while breaking harmful cycles through compassionate action.

**Target Wound:** Inherited trauma, intergenerational guilt, false responsibility for family patterns

**Primary Atoms:**
- interconnection_01 (family as living system)
- reciprocal_responsibility_02 (mutual obligation and choice)
- shadow_recognition_01 (ancestors' unhealed wounds show in descendants)
- forgiveness_01 (releasing family grudges)
- dharma_integrity_02 (choosing integrity aligned with values, not family expectation)
- grief_as_love_02 (honoring family through grief work)

**Pacing:** 20+ chapter serialization (webtoon allows episodic structure with continuing arc)
- Chapters 1-4: Discovery (protagonist learns thread-seeing ability)
- Chapters 5-10: Investigation (exploring family history through threads)
- Chapters 11-16: Shadow Work (seeing family members' wounds and choices)
- Chapters 17+: Healing (protagonist makes different choices, healing both self and lineage)

**Villain:** The Cycle Itself—not a person, but the pattern of unhealed trauma repeating. The teaching is that compassionate choice can break cycles.

**Genre Notes:** Webtoon/Manhwa reader expects social realism and systemic awareness. The teaching is that individual healing is collective healing; changing one's own response changes the whole system.

---

## Deployment Rules & Pipeline Integration

### Rule 1: Atoms Flow Only Through Genre Agent

**Never:** Chapter Writer, Story Architect, or Visual Agent access Teaching Library directly.

**Always:**
- Teaching Library → Genre Agent
- Genre Agent → Story Architect (receives arc_structure + villain_spec)
- Genre Agent → Chapter Writer (receives transmission_map WITHOUT atom text; only hiding places + methods)
- Genre Agent → QC Agent (sends forbidden_phrases)

**Why:** Isolating atoms at the Genre Agent layer ensures consistent methodology. If Chapter Writer has direct atom access, embedding methods fragment and didactic language leaks in.

### Rule 2: Atom Text is Withheld from Chapter Writer

Chapter Writer receives:
- Canonical moment (where to deploy)
- Hiding place (how specific: "in the panel where mentor's absence is felt")
- Method (structural|experiential|silence|accumulation)
- Depth level (recognition|somatic|integration)
- Forbidden phrases list
- Somatic target (where reader feels it)

Chapter Writer does **NOT** receive:
- The atom's teaching text itself
- The tradition origin
- The teaching philosophy

**Why:** If Chapter Writer has the atom text, they will subconsciously work backward from the text, creating didactic moments. Working blind to the text, Chapter Writer creates naturally from the story need, and the teaching arrives indirectly.

### Rule 3: Compound Pairing Unlocks Depth

Some atoms are designed to pair with others for compounded teaching:

- **impermanence_01 + grief_01** → "All things pass, and this passing is how love proves itself"
- **anatta_01 + mirror_02** → "The more I dissolve, the more I recognize myself in others"
- **witness_consciousness_03 + dharma_integrity_02** → "From witness awareness, action flows with perfect integrity"

Genre Agent checks compound_pairing_ids during Atom Selection (Step 2). If the story wound calls for compound teaching, both atoms are selected, and their pairing synergy is noted in transmission_map.

Compound atoms are spaced throughout the arc; the reader doesn't see the pairing consciously, but the combined effect deepens somatic integration.

### Rule 4: Wound Target Matching

Every reader comes to manga seeking healing of a specific wound:

- Shōnen reader seeks healing of powerlessness
- Seinen reader seeks healing of meaninglessness/complicity
- Shōjo reader seeks healing of unworthiness
- Iyashikei reader seeks healing of exhaustion/disconnection
- Isekai reader seeks healing of fatalism

Genre Agent prioritizes atoms whose wound_target matches the genre's typical wound. This ensures resonance.

A shōnen story can deploy Sufi heart-opening atoms, but they must be framed as power-building (heart opening = spiritual power), not as emotional vulnerability (which would break shōnen contract).

---

## Quality Control: Pearl Editor & EI Decision Layer

**QC Flow:**

1. **Atom Creation:** Teaching specialist (informed by contemplative practice, not intellectual design) proposes new atom
2. **Pearl Editor Review:** pearl_editor reviews for:
   - Somatic accuracy (does the teaching live in a real somatic location?)
   - Absence of spiritual bypass (does it honor the full journey, or skip to transcendence?)
   - Tradition authenticity (is it true to the lineage it claims?)
   - Story hookability (can it actually embed in narrative?)
   - Compound compatibility (does it pair well with existing atoms?)
3. **EI Review:** EI (emotional intelligence reviewer) assesses:
   - Reader safety (will this teaching arrive too aggressively?)
   - Developmental readiness (is this paced for realistic integration?)
   - Cultural appropriateness (if cross-tradition, is it respectful?)
   - Accessibility (can a 16-year-old manga reader metabolize this teaching?)
4. **Approval:** Only atoms approved by both pearl_editor AND EI are added to Teaching Library
5. **Versioning:** If an atom is revised, it receives a new atom_id (not modified in place)

**Rejected Atom Reasons:**
- Didactic teaching (doesn't live in body)
- Spiritual bypassing (skips the difficulty)
- Cultural appropriation (takes from tradition without honoring it)
- Story incompatibility (cannot embed in narrative without dialogue-explanation)
- Somatic inauthenticity (proposed "somatic" location is intellectual, not embodied)

---

## Teaching Library Metadata

### Version Control
- Current Teaching Library version: 1.0
- Seed atoms: 20 (locked; no modifications; new atoms receive new IDs)
- Seed series: 5 (locked; serve as templates)
- Custom atoms created per-project: unlimited (tracked separately by project_id)

### Access Control
- Genre Agent: Read access to all atoms + fields
- Story Architect: Read-only access to arc_structure from Genre Agent output (NOT direct Teaching Library access)
- Chapter Writer: No direct access; receives transmission_map from Genre Agent (atom text withheld)
- Visual Agent: No direct access; receives transmission_map from Genre Agent (atom text withheld)
- QC Agent: Read access to forbidden_phrases only
- Pearl Editor: Admin access (atom creation, approval, versioning)

### Update Protocol
- Atoms are immutable once approved
- No "fixing" existing atoms; create new atoms instead
- Teaching Library maintains full history of all atom versions
- If an atom is deprecated, it's marked deprecated (not deleted); new atoms replace it
- Project-specific atom variants are tracked in project metadata, not in core Teaching Library

---

## Implementation Checklist

**For Genre Agent Integration:**

- [ ] Teaching Library fully populated with 20 seed atoms
- [ ] All 5 seed series concepts mapped to atom deployments
- [ ] Atom schema implemented in data structure
- [ ] compound_pairing_ids relationships verified
- [ ] Somatic targets validated by embodied practitioners
- [ ] Story hooks tested across all 10 genres
- [ ] Deployment constraints enforced in QC scan
- [ ] Forbidden phrases auto-generated per atom + genre combo

**For Genre Agent Workflow:**

- [ ] Genre Agent can query Teaching Library by wound_target
- [ ] Genre Agent can query Teaching Library by genre compatibility
- [ ] Genre Agent can query Teaching Library by depth_level
- [ ] Genre Agent can retrieve compound_pairing synergies
- [ ] Genre Agent generates transmission_map without exposing atom text
- [ ] Genre Agent passes forbidden_phrases to QC Agent

**For Quality Assurance:**

- [ ] Pearl editor reviews all custom atoms before deployment
- [ ] EI validates developmental readiness before approval
- [ ] QC Agent scans completed chapters against forbidden_phrases
- [ ] Somatic accuracy verified by practice lineage specialists
- [ ] Reader feedback loop captures real integration patterns

---

*SpiritualTech Systems · Teaching Library Spec v1.0 · Confidential*
