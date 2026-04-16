# RHETORICAL_ANTI_REPETITION_ARCHITECTURE_HANDOFF_2026_04_16

## Purpose

This handoff documents the findings, diagnosis, architecture decisions, and proposed implementation plan for reducing machine-visible repetition across long books and multi-book series.

The work covered four separate repetition layers plus a shared cross-layer rhetorical memory/taxonomy layer:

1. Location-light fallback environment system
2. Chapter bridge / transition system
3. Mechanism / thesis delivery system
4. Exercise wrapper / post-exercise validation system
5. Shared rhetorical anti-repetition architecture across all four

The central conclusion is:

> The system problem is not only repeated phrases. It is repeated rhetorical behavior.

Even when exact wording changes, the system still risks sounding machine-generated through repeated:
- explanatory wrappers
- bridge glue
- validation tone
- environmental scene furniture
- roots
- cadence
- rhetorical shapes
- emotional register

---

## Key repo findings

### 1. Location-related fallback repetition source

Primary source file:
- `phoenix_v4/rendering/golden_chapter_synthesis.py`

Primary function:
- `_resolve_location_placeholders(...)`

Confirmed hardcoded fallback replacements included:
- `{weather_detail}` -> `Gray daylight filters in`
- `{street_name}` -> `The street`
- `{transit_line}` -> `train`

This function also contained multiple repair rules that collapse malformed location-like text into small recurring traffic/window/street phrases.

Confirmed secondary reinforcement:
- `dedupe_scene_furniture_book(...)`

This function already lists recurring signatures such as:
- `soft daylight along the sill`
- `gray daylight filters in`
- `the street below is visible through the glass`
- `gray light through the window`

Conclusion:
- unresolved location/weather/transit placeholders are being collapsed into a tiny ambient vocabulary
- this is not just an atom-bank problem; it is a placeholder-resolution fallback problem

### 2. Chapter bridge / transition repetition source

Primary source file:
- `phoenix_v4/rendering/chapter_composer.py`

Confirmed helper functions:
- `_bridge_after_opening(...)`
- `_bridge_before_story(...)`
- `_bridge_before_exercise(...)`
- `_bridge_before_integration(...)`
- `_fallback_takeaway(...)`
- `_fallback_thread(...)`

These currently use hardcoded option banks and contain semantically useful but highly visible structural glue language.

Conclusion:
- the repeated transition layer is real and is directly sourced from bridge/helper banks inside `chapter_composer.py`
- more variation alone is not enough; bridge selection must be chapter-function-aware

### 3. Mechanism / thesis wrapper repetition source

Primary source file:
- `phoenix_v4/rendering/chapter_composer.py`

Confirmed functions:
- `_derive_thesis(...)`
- `_distill_mechanism(...)`
- secondarily `_fallback_takeaway(...)`

Observed pattern:
- thesis delivery is repeatedly shaped through wrapper stems such as `The point is that...`
- mechanism delivery repeatedly uses templates like `Here is the mechanism...`, `The pattern underneath is...`, `What drives this is...`, `The core mechanism is...`

Conclusion:
- the system has a visible explainer voice caused by repeated mechanism/thesis delivery wrappers
- this layer needs a dedicated structured delivery system, not just more thesis lines

### 4. Exercise wrapper / validation repetition source

Primary source file:
- `phoenix_v4/rendering/chapter_composer.py`

Confirmed functions:
- `_exercise_setup_sentence(...)`
- `_bridge_before_exercise(...)`
- `_bridge_before_integration(...)`
- plus exercise assembly wrapper/fallback path used around practice content

Observed pattern:
- actual exercise content varies more than wrapper language
- repeated container language appears in:
  - pre-practice framing
  - setup sentence
  - permission framing
  - post-practice validation
  - post-practice debrief
  - transition into integration

Conclusion:
- the exercise wrapper layer is a distinct repetition system and should be refactored as its own subsystem

---

## Main architectural conclusion

The same general anti-repetition architecture applies to all four layers, but each layer needs role-specific conditioning.

### Shared anti-repetition pattern across all four layers

Each subsystem should use:

1. larger structured candidate banks
2. book-level anti-reuse memory
3. multiple rhetorical shapes
4. role-aware conditioning

### Important nuance by layer

#### Environment fallback
Needs:
- context-aware ambient fallback families
- location-light specificity
- object-grounding emphasis

#### Bridges
Needs:
- chapter-function-aware selection
- emotional-job-aware transition banks
- thread-forward logic aware of chapter position

#### Mechanism / thesis delivery
Needs:
- split between thesis delivery and mechanism delivery
- emotional-job-aware argument shaping
- reduction of visible explainer wrapper stems

#### Exercise wrappers
Needs:
- practice-type-aware wrapper selection
- emotional-job-aware support tone
- separate handling of setup / permission / validation / debrief / landing

---

## Why independent fixes are not enough

A central insight from this work:

> If each subsystem solves repetition independently, the system can still converge into one shared house voice.

For example:
- environment becomes muted and atmospheric
- bridges become quiet-authoritative
- mechanism lines become compact explanatory
- exercise wrappers become softly validating

Even if each layer individually improves, the combined result can still feel machine-generated because the same:
- register
- cadence
- roots
- rhetorical shapes
- guidance style
repeat across layers.

This led to the unified solution:

> build a shared rhetorical taxonomy and cross-layer memory system so the selectors can avoid not only repeated phrases, but repeated rhetorical behavior.

---

## Proposed subsystem refactors

### A. Phase 1 — Rich location-light fallback environment system

#### Goal
Replace tiny hardcoded placeholder fallbacks with rich ambient environment families.

#### Planned file
- `config/rendering/environment_fallback_families.yaml`

#### Families proposed
- `light_ambient`
- `outside_sound`
- `interior_building`
- `motion_transit`
- `object_grounding`
- `window_reference`

#### Main implementation target
- `phoenix_v4/rendering/golden_chapter_synthesis.py`

#### Core idea
When location is not a focus, unresolved placeholders should resolve into:
- ambient sensory detail
- background motion
- object grounding
- interior texture
- non-specific exterior sound

not literal generic place labels.

#### Important design note
Object-grounding should become a major fallback path so books do not over-rely on window/light/outside phrasing.

---

### B. Phase 1 — Chapter bridge / transition system refactor

#### Goal
Replace visible structural glue with chapter-function-aware transition selection.

#### Planned file
- `config/rendering/bridge_transition_families.yaml`

#### Main implementation target
- `phoenix_v4/rendering/chapter_composer.py`

#### Existing helper functions to preserve but refactor internally
- `_bridge_after_opening(...)`
- `_bridge_before_story(...)`
- `_bridge_before_exercise(...)`
- `_bridge_before_integration(...)`
- `_fallback_takeaway(...)`
- `_fallback_thread(...)`

#### Key emotional-job buckets proposed
- `recognition`
- `mechanism`
- `deepening`
- `reframe`
- `practice`
- `integration`
- `resolution`

#### Key rhetorical shapes proposed
- `direct_assertion`
- `embodied_noticing`
- `causal_turn`
- `contrast_turn`
- `quiet_compression`
- `question_turn`
- `forward_pull`
- `permission_turn`
- `implication_turn`
- `evidence_turn`

#### Key conclusion
Variation alone is not enough here.
Bridge selection must be:
- bridge-type-aware
- emotional-job-aware
- chapter-position-aware

---

### C. Phase 1 — Mechanism / thesis delivery system refactor

#### Goal
Reduce repeated explanatory scaffolds and stop all chapters from sounding like they are summarized by the same explainer voice.

#### Planned file
- `config/rendering/mechanism_thesis_families.yaml`

#### Main implementation target
- `phoenix_v4/rendering/chapter_composer.py`

#### Existing helpers to preserve but refactor internally
- `_derive_thesis(...)`
- `_distill_mechanism(...)`

#### Proposed split
- thesis selector
- mechanism selector

#### Thesis shapes proposed
- `direct_thesis`
- `quiet_distillation`
- `reframe_sentence`
- `contrast_claim`
- `identity_shift_claim`
- `permission_inflected_claim`
- `consequence_claim`
- `compression_claim`

#### Mechanism shapes proposed
- `causal_explanation`
- `systems_model`
- `body_model`
- `pattern_recognition`
- `cost_explanation`
- `reversal_explanation`
- `implication_line`
- `evidence_based_explanation`
- `quiet_explanatory_compression`

#### Key conclusion
This should be treated as a mechanism/thesis delivery system, not just a bigger thesis bank.

---

### D. Phase 1 — Exercise wrapper / validation system refactor

#### Goal
Reduce repeated practice container language while keeping exercises safe, usable, and grounded.

#### Planned file
- `config/rendering/exercise_wrapper_families.yaml`

#### Main implementation target
- `phoenix_v4/rendering/chapter_composer.py`
- exercise assembly wrapper/fallback path around exercise content

#### Existing helpers to preserve but refactor internally
- `_exercise_setup_sentence(...)`
- `_bridge_before_exercise(...)`
- `_bridge_before_integration(...)`

#### Proposed wrapper roles
- `pre_practice_bridge`
- `setup_sentence`
- `permission_frame`
- `entry_instruction`
- `post_practice_validation`
- `post_practice_debrief`
- `pre_integration_transition`

#### Practice buckets proposed
- `breath_regulation`
- `grounding`
- `body_scan`
- `somatic_discharge`
- `visualization`
- `reflective_prompt`
- `attention_training`
- `vagus_stimulation`
- `integration_pause`

#### Key conclusion
This layer is one of the cleanest candidates for a structured refactor because the wrapper roles are narrow and well-defined.

---

## Unified rhetorical anti-repetition architecture

### Purpose
Coordinate anti-repetition across all four subsystems so they do not independently improve while still producing one shared generator voice.

### Planned shared files
- `config/rendering/rhetorical_style_taxonomy.yaml`
- `artifacts/render_memory/rhetorical_memory.json`

### Shared taxonomy fields proposed
All candidates across all layers should support at least:
- `shape`
- `register`
- `movement`
- `instruction_tone`
- `roots`
- `cadence`
- `intensity`
- `abstraction_level`

### Example shapes
- `direct_assertion`
- `quiet_compression`
- `embodied_noticing`
- `causal_turn`
- `contrast_turn`
- `question_turn`
- `forward_pull`
- `permission_turn`
- `data_framing`
- `sensory_observation`
- `object_grounding`
- `systems_explanation`
- `validation_line`

### Example registers
- `plain`
- `warm`
- `clinical_light`
- `somatic`
- `reflective`
- `quiet_authoritative`
- `soft_guiding`
- `compressed`
- `emotionally_open`

### Example movements
- `naming`
- `explaining`
- `deepening`
- `reframing`
- `guiding`
- `landing`
- `validating`
- `forwarding`

### Shared memory must track
Per book:
- phrases used
- stems used
- roots used
- shapes used
- registers used
- movements used
- instruction tones used
- per-layer usage stats

Later-ready series-level tracking should also be supported.

### Shared cross-layer anti-repetition goal
Prevent chapters where every layer sounds like it is doing the same rhetorical move.

Example bad outcome:
- environment: quiet compressed sensory cue
- bridge: quiet compressed explanation-adjacent cue
- mechanism: quiet compressed explanatory claim
- exercise debrief: quiet compressed validating line

Each line may be individually fine, but together they create a detectable machine voice.

### Shared scoring idea
All selectors should penalize:
- repeated phrases
- repeated stems
- repeated roots
- repeated shapes
- repeated registers
- repeated movements
- repeated instruction tones
- same family overuse
- recent collision across layers

All selectors should reward:
- underused shape
- underused register
- underused movement
- cross-layer contrast
- topic fit
- chapter-role fit
- coherent local fit without echoing recent rhetoric

---

## Proposed scoring engine approach

A shared candidate-scoring engine was designed conceptually to support all four layers.

### Core inputs
Each selector should operate on candidates tagged with:
- layer
- family
- shape
- register
- movement
- instruction_tone
- roots
- stems
- optional topic / emotional_job / practice / position biases

### Context inputs
Each selection should consider:
- chapter index
- total chapters
- emotional job
- topic id
- persona id
- optional practice type / bridge type
- local text context
- book seed

### Shared memory inputs
Each selection should consult:
- book-local used phrases
- book-local stems
- book-local roots
- recent shapes
- recent registers
- recent movements
- recent families
- optional series-level counts

### Selection behavior
Do not use only direct seeded picks.
Use:
- candidate scoring
- top-band selection
- deterministic-ish seeded randomness among top candidates

This preserves reproducibility while preventing brittle deterministic repeats.

---

## Five recommended implementation tickets

The work was broken into five execution tickets.

### Ticket 1
Phase 1 rich location-light fallback environment system

### Ticket 2
Phase 1 chapter bridge / transition system refactor

### Ticket 3
Phase 1 mechanism / thesis delivery system refactor

### Ticket 4
Phase 1 exercise wrapper / validation system refactor

### Ticket 5
Phase 1 shared rhetorical taxonomy + cross-layer memory

These were drafted in issue-ready format and are intended to be created as child tasks under a master architecture ticket.

---

## Recommended implementation order

### Strongest practical order

1. exercise wrapper / validation system
2. environment fallback system
3. mechanism / thesis system
4. bridge system
5. shared rhetorical taxonomy + cross-layer memory

### Alternate engineering-first order

1. shared scoring engine skeleton
2. environment fallback wiring
3. exercise wrapper system
4. mechanism/thesis system
5. bridge system
6. shared cross-layer enforcement

### Reasoning
The exercise wrapper and environment layers provide the fastest visible quality improvements.
The shared memory/scoring layer should ideally arrive early enough that the four subsystems do not diverge into incompatible selector logic.

---

## Main risks and cautions

### 1. Solving repetition with random noise
Not acceptable.
The goal is controlled variation, not random style drift.

### 2. Over-diversification causing loss of clarity
The system must preserve:
- clarity
- teachability
- therapeutic safety
- readability

Variation should never make the text feel ornate or self-conscious.

### 3. Local fixes creating a stronger house voice
If all fixes independently move toward:
- quiet authority
- soft validation
- compact explanation
- muted atmosphere

then the system will still sound unified in a machine-detectable way.
This is why the shared rhetorical taxonomy and memory layer are necessary.

### 4. Series-scale insufficiency
A small bank with no series memory is not enough for:
- 10-book series
- long books
- repeated topic/persona lanes

Phase 1 will help materially, but Phase 2 series-memory work is still needed for large-scale invisibility.

---

## Honest bottom-line conclusions

### What was learned

1. The repetition problems are real and are sourceable to specific repo functions.
2. The location issue is strongly driven by placeholder fallback collapse.
3. The bridge issue is strongly driven by hardcoded structural glue helpers.
4. The mechanism/thesis issue is strongly driven by repeated explainer wrapper stems.
5. The exercise issue is strongly driven by wrapper and validation container language.
6. Fixing each subsystem independently is not enough; a shared rhetorical architecture is needed.

### Best concise summary

> The system is consistent in a way humans can feel.

The problem is not only repeated wording.
It is repeated rhetorical behavior.

### Final architectural direction

Build:
- four config-driven anti-repetition subsystems
- one shared rhetorical taxonomy
- one shared cross-layer memory/scoring architecture

This is the cleanest path toward long-book and multi-book authored feel.

---

## Suggested file targets

### Existing code files to refactor
- `phoenix_v4/rendering/golden_chapter_synthesis.py`
- `phoenix_v4/rendering/chapter_composer.py`

### New config files proposed
- `config/rendering/environment_fallback_families.yaml`
- `config/rendering/bridge_transition_families.yaml`
- `config/rendering/mechanism_thesis_families.yaml`
- `config/rendering/exercise_wrapper_families.yaml`
- `config/rendering/rhetorical_style_taxonomy.yaml`

### New memory / artifact shapes proposed
- `artifacts/render_memory/rhetorical_memory.json`
- optional per-subsystem memory shapes later if needed

---

## Status at handoff

This handoff captures:
- repo-level diagnosis
- identified source functions
- architecture decisions
- subsystem refactor specs
- unified anti-repetition architecture
- issue-ready execution decomposition
- shared scoring model direction

Implementation is not yet completed in code.
This document is intended to guide implementation cleanly and prevent the design from fragmenting across future sessions.
