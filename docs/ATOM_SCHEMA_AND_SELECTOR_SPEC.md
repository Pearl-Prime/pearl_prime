# ATOM SCHEMA AND SELECTOR SPEC

## Purpose

This document translates `docs/BESTSELLER_GAP_AUDIT.md` into an implementation-ready spec.
It defines:

1. the exact new atom metadata schema Phoenix should add,
2. the selector and planner changes required to consume that schema,
3. the migration strategy so the repo can improve without breaking current production flows.

This is intended as a dev handoff. It is not a research memo.

---

## 1. Core Diagnosis

Phoenix currently selects content mainly by:

- slot type
- band
- role
- semantic family
- thesis keyword overlap
- deterministic hash order

That is enough for structural coverage.
It is not enough for bestseller-grade reading experience.

The missing layer is **reader-state-aware selection**.

The selector must become able to answer questions like:

- What private shame is being named here?
- What objection must be handled before the exercise lands?
- What kind of proof earns trust in this chapter?
- What kind of tension should end this chapter?
- Is this atom planting a callback or paying one off?

---

## 2. Design Goals

### Required
- Preserve deterministic selection.
- Preserve backward compatibility with existing atoms.
- Avoid forcing immediate full-bank rewrites.
- Allow gradual metadata enrichment.
- Improve selection quality before large prose rewrites.

### Not required
- Rebuild the full pipeline.
- Replace section registries.
- Replace spines.
- Replace composer.

---

## 3. New Canonical Reader-State Metadata Schema

These fields are the minimum viable addition.

### 3.1 Required new metadata fields

```yaml
proof_mode: story | diagnosis | framework | data | lived_experience | witness
reader_objection: none | rest_is_lazy | if_i_stop_i_fail | if_seen_i_get_rejected | this_wont_work_for_me | too_late_for_me | my_case_is_different | i_should_be_over_this | feeling_it_will_make_it_worse
private_shame_type: none | invisibility | incompetence | neediness | dependency | envy | lateness | weakness | failure | being_too_much | being_not_enough
shame_level: 1 | 2 | 3 | 4 | 5
desire_type: none | relief | certainty | belonging | self_trust | rest | visibility | connection | permission | dignity
tension_type: none | contradiction | mystery | stakes | delayed_reveal | dread | social_exposure | relational_cost | identity_cost
propulsion_type: none | question | withheld_cost | relational_next | identity_next | myth_next | practice_next | consequence_next
callback_role: none | plant | echo | payoff
authority_mode: none | teacher | clinician | researcher | witness | confessional
story_function: none | case | turn | mirror | proof_case | callback_vehicle
framework_name: string
framework_role: none | introduce | deepen | apply | invert
shareability: 1 | 2 | 3 | 4 | 5
```

### 3.2 Optional but strongly recommended fields

```yaml
reader_state_entry: braced | ashamed | flooded | numb | confused | striving | vigilant | grieving
reader_state_exit: relieved | seen | destabilized | clearer | willing | emotionally_open | unresolved_but_moving
permission_type: none | legitimacy | grief_permission | rest_permission | uncertainty_permission | visibility_permission | incompleteness_permission
objection_target_phase: none | pre_mechanism | pre_practice | pre_identity_shift
callback_id: string
open_loop_id: string
line_memorability: 1 | 2 | 3 | 4 | 5
```

---

## 4. Field Semantics

### proof_mode
Defines what kind of authority the atom provides.

Use cases:
- `story`: narrative proof through character/event
- `diagnosis`: names what is happening clinically or psychologically
- `framework`: introduces or sharpens a model
- `data`: external evidence / pattern / statistic
- `lived_experience`: first-person credibility
- `witness`: validating stance without heavy explanation

### reader_objection
Names the resistance likely to block the next move.

This is critical because Phoenix currently asks readers to practice without always clearing resistance first.

### private_shame_type + shame_level
These determine how sharp or gentle the recognition should be.

Examples:
- invisibility + level 4 → “you learned to vanish before anyone could judge you”
- dependency + level 5 → “needing reassurance already feels like evidence against you”

### desire_type
Tracks what the reader actually wants beneath the symptom.

Examples:
- burnout topic might use `rest`, `dignity`, `self_trust`
- anxiety topic might use `certainty`, `relief`, `self_trust`

### tension_type
Defines how the chapter holds pressure.

Examples:
- `contradiction`: “the strategy is helping and harming”
- `identity_cost`: “what this protects is your self-concept”
- `relational_cost`: “this pattern is changing how others feel with you”

### propulsion_type
Defines what sort of unfinished pull ends the chapter.

Examples:
- `relational_next`: next chapter reveals relational consequence
- `identity_next`: next chapter moves from behavior to self-concept
- `withheld_cost`: next chapter reveals the price not yet faced

### callback_role
Supports real braid structure.

- `plant`: introduces motif/image/question
- `echo`: reminds without fully resolving
- `payoff`: returns and deepens/resolves

### authority_mode
Lets selector match the kind of voice needed.

Examples:
- grief often needs `witness`
- trauma may need `clinician + witness`
- Brené-style worthiness may need `confessional + researcher`

### framework_name + framework_role
Makes named models reusable and traceable.

Example:
- `framework_name: borrowed_verdict_loop`
- `framework_role: introduce`

### shareability / line_memorability
Supports memorable line targeting and future gates.

---

## 5. Where This Schema Lives

### 5.1 Atom-level metadata

Add these fields to:
- canonical atom metadata blocks
- registry variant metadata blocks
- teacher atom metadata where relevant

### 5.2 Chapter plan metadata

Chapter planning should also carry a subset of these as **requirements**, not just atom facts.

New chapter-level requirement fields:

```yaml
required_proof_mode: story | diagnosis | framework | lived_experience | witness | any
required_objection: none | ...
required_tension_type: contradiction | relational_cost | identity_cost | ...
required_propulsion_type: relational_next | identity_next | ...
required_private_shame_type: none | invisibility | incompetence | ...
required_desire_type: none | relief | belonging | ...
required_callback_role: none | plant | echo | payoff
```

This is the key design move:

**chapter plans request reader-state functions, then selector finds the best atom for that request.**

---

## 6. Minimum New Atom Taxonomy

These do not all need to become top-level slot types immediately.
But they must become **selection-aware classes**.

### 6.1 Functional atom classes

```yaml
COLD_OPEN
SHAME_RECOGNITION
DESIRE
TENSION
AUTHORITY_PROOF
STORY_CASE
STORY_TURN
MEMORABLE_FRAMEWORK
MYTH_BUST
OBJECTION_HANDLING
PRACTICE
PERMISSION
CALLBACK_PLANT
CALLBACK_ECHO
CALLBACK_PAYOFF
IDENTITY_SHIFT
INTEGRATION_LANDING
CHAPTER_PROPULSION
CONFESSION
```

### 6.2 Mapping to existing slot types

To avoid breaking the pipeline, use a compatibility layer:

| Functional class | Current slot type(s) it may live inside |
|---|---|
| COLD_OPEN | HOOK, SCENE |
| SHAME_RECOGNITION | HOOK, REFLECTION, STORY |
| DESIRE | HOOK, REFLECTION |
| TENSION | PIVOT, THREAD, STORY |
| AUTHORITY_PROOF | STORY, REFLECTION, TEACHER_DOCTRINE |
| STORY_CASE | STORY |
| STORY_TURN | STORY, PIVOT |
| MEMORABLE_FRAMEWORK | REFLECTION, TAKEAWAY |
| MYTH_BUST | PIVOT, REFLECTION |
| OBJECTION_HANDLING | REFLECTION, PIVOT, EXERCISE_SETUP |
| PRACTICE | EXERCISE |
| PERMISSION | PERMISSION, INTEGRATION |
| CALLBACK_* | STORY, THREAD, TAKEAWAY, INTEGRATION |
| IDENTITY_SHIFT | REFLECTION, TAKEAWAY, INTEGRATION |
| INTEGRATION_LANDING | INTEGRATION |
| CHAPTER_PROPULSION | THREAD |
| CONFESSION | STORY, REFLECTION, TEACHER_DOCTRINE |
```

This means you do **not** need to add 19 new slot types to the renderer immediately.
You first add metadata/classification.

---

## 7. Selector Changes

## 7.1 Current selector weakness

`slot_resolver.py` currently ranks mostly by:
- availability
- semantic_family exclusion
- band
- role
- thesis overlap
- deterministic atom_id order

That is too weak.

## 7.2 New ranking function

For each candidate atom, compute:

```python
score = (
    w_slot_compatibility
  + w_band_match
  + w_role_match
  + w_thesis_overlap
  + w_proof_mode_match
  + w_objection_match
  + w_shame_match
  + w_desire_match
  + w_tension_match
  + w_propulsion_match
  + w_callback_match
  + w_authority_mode_match
  + w_framework_match
  + w_memorability_match
  - w_repetition_penalty
  - w_same_function_penalty
)
```

### 7.3 Recommended weights (v1)

```yaml
slot_compatibility: 5.0
band_match: 2.0
role_match: 2.5
thesis_overlap: 1.5
proof_mode_match: 2.5
reader_objection_match: 3.0
private_shame_match: 3.0
desire_match: 2.0
tension_match: 3.0
propulsion_match: 3.5
callback_match: 2.5
authority_mode_match: 2.0
framework_match: 2.0
memorable_line_match: 1.0
repetition_penalty: 3.0
same_function_penalty: 2.0
```

### 7.4 New selection requirements in ResolverContext

Add to `ResolverContext`:

```python
required_proof_mode_by_chapter: Optional[dict[int, str]] = None
required_objection_by_chapter: Optional[dict[int, str]] = None
required_shame_type_by_chapter: Optional[dict[int, str]] = None
required_desire_type_by_chapter: Optional[dict[int, str]] = None
required_tension_type_by_chapter: Optional[dict[int, str]] = None
required_propulsion_type_by_chapter: Optional[dict[int, str]] = None
required_callback_role_by_chapter: Optional[dict[int, str]] = None
required_authority_mode_by_chapter: Optional[dict[int, str]] = None
required_framework_role_by_chapter: Optional[dict[int, str]] = None
```

Then selector reads these in exactly the same way band/role are currently read.

---

## 8. Planner Changes

## 8.1 chapter_planner.py must stop assigning only shape

Right now it assigns:
- archetype
- exercise_mode
- reflection_weight
- story_depth
- bestseller structure

Add chapter-level reader-state requirements.

## 8.2 New chapter plan output fields

For each chapter, output:

```yaml
required_proof_mode
required_objection
required_private_shame_type
required_desire_type
required_tension_type
required_propulsion_type
required_callback_role
required_authority_mode
required_framework_role
```

### 8.3 Example by chapter phase

#### Early chapter
```yaml
required_private_shame_type: invisibility
required_shame_level: 4
required_proof_mode: witness
required_tension_type: contradiction
required_propulsion_type: withheld_cost
required_callback_role: plant
```

#### Mid chapter
```yaml
required_proof_mode: framework
required_objection: this_wont_work_for_me
required_tension_type: identity_cost
required_propulsion_type: relational_next
required_framework_role: introduce
```

#### Late chapter
```yaml
required_proof_mode: lived_experience
required_objection: too_late_for_me
required_tension_type: consequence_next
required_propulsion_type: identity_next
required_callback_role: payoff
required_framework_role: apply
```

---

## 9. Compiler Changes

## 9.1 assembly_compiler.py

The compiler should continue to build slot sequences as now.
But it must also pass the new requirement maps into `ResolverContext`.

### Required change
When chapter planner returns new requirement arrays, compiler converts them to:

```python
required_proof_mode_by_chapter = {i: ...}
required_objection_by_chapter = {i: ...}
required_shame_type_by_chapter = {i: ...}
required_desire_type_by_chapter = {i: ...}
required_tension_type_by_chapter = {i: ...}
required_propulsion_type_by_chapter = {i: ...}
required_callback_role_by_chapter = {i: ...}
required_authority_mode_by_chapter = {i: ...}
required_framework_role_by_chapter = {i: ...}
```

and passes them into `ResolverContext`.

---

## 10. Composer Changes

The composer does not need a rewrite first.
But it should consume a few new concepts as soon as they exist.

### 10.1 THREAD shaping

If `propulsion_type` is available for the selected THREAD atom, the composer should not flatten it into a generic thread.

Instead:
- `relational_next` → thread must point toward another person / relationship cost
- `identity_next` → thread must point toward self-concept change
- `withheld_cost` → thread must point toward a price not yet fully seen

### 10.2 Integration landing

If selected INTEGRATION has `reader_state_exit`, composer can preserve that instead of over-normalizing through fallback bridge rhetoric.

### 10.3 Myth bust + framework

If a chapter contains both `MYTH_BUST` and `MEMORABLE_FRAMEWORK`, composer should keep them adjacent when possible.

---

## 11. Backward Compatibility Rules

### Rule 1
Atoms missing the new metadata remain valid.
They simply score neutral on those dimensions.

### Rule 2
If chapter planner does not emit a requirement field, selector ignores that dimension.

### Rule 3
No existing slot types are removed in phase 1.

### Rule 4
No existing registry format is invalidated.
Additive metadata only.

---

## 12. Migration Plan

## Phase 1 — Schema + selector support only

### Implement
- new optional metadata fields
- selector scoring support
- new ResolverContext fields
- planner output placeholders (optional defaults)

### Do not require yet
- full atom-bank rewrite
- new slot types
- composer rewrite

### Goal
Let already-strong atoms rank better when enriched with metadata.

---

## Phase 2 — Writer bank upgrade

Write or classify atoms for:
- SHAME_RECOGNITION
- OBJECTION_HANDLING
- STORY_TURN
- CHAPTER_PROPULSION
- MEMORABLE_FRAMEWORK
- CALLBACK_PLANT / PAYOFF

### Goal
Improve actual book quality using the new selector.

---

## Phase 3 — Planner requirement tuning

Tune chapter templates so each phase requests the right:
- proof mode
- tension type
- objection
- callback role
- propulsion type

### Goal
Move from “good atom ranking” to “real chapter choreography.”

---

## 13. Suggested Code Touchpoints

### Must update
- `phoenix_v4/planning/slot_resolver.py`
- `phoenix_v4/planning/chapter_planner.py`
- `phoenix_v4/planning/assembly_compiler.py`

### Should update soon after
- atom parsers / registry loaders that expose metadata
- writer docs for atom creation
- quality gates for propulsion, objection handling, framework presence

### Can wait
- `chapter_composer.py` deep rewrite
- full slot taxonomy rewrite
- registry format overhaul

---

## 14. Example Pseudocode for Selector Upgrade

```python
def _score_reader_state_fit(entry, chapter_idx, context, slot_type):
    meta = entry.metadata or {}
    score = 0.0

    if context.required_proof_mode_by_chapter:
        req = context.required_proof_mode_by_chapter.get(chapter_idx)
        if req and meta.get("proof_mode") == req:
            score += 2.5

    if context.required_objection_by_chapter:
        req = context.required_objection_by_chapter.get(chapter_idx)
        if req and meta.get("reader_objection") == req:
            score += 3.0

    if context.required_shame_type_by_chapter:
        req = context.required_shame_type_by_chapter.get(chapter_idx)
        if req and meta.get("private_shame_type") == req:
            score += 3.0

    if context.required_desire_type_by_chapter:
        req = context.required_desire_type_by_chapter.get(chapter_idx)
        if req and meta.get("desire_type") == req:
            score += 2.0

    if context.required_tension_type_by_chapter:
        req = context.required_tension_type_by_chapter.get(chapter_idx)
        if req and meta.get("tension_type") == req:
            score += 3.0

    if context.required_propulsion_type_by_chapter:
        req = context.required_propulsion_type_by_chapter.get(chapter_idx)
        if req and meta.get("propulsion_type") == req:
            score += 3.5

    if context.required_callback_role_by_chapter:
        req = context.required_callback_role_by_chapter.get(chapter_idx)
        if req and meta.get("callback_role") == req:
            score += 2.5

    return score
```

---

## 15. Minimum Acceptance Tests

A dev implementation is ready when:

1. Selector can rank two atoms differently based on `reader_objection`.
2. Planner can request a `propulsion_type` and selector honors it.
3. Callback `plant` and `payoff` can be selected in different chapters intentionally.
4. Atoms without new metadata still compile and resolve.
5. Existing books still render.
6. A regression test can show chapter-end THREAD selection improving from generic to targeted.

---

## 16. Highest-Leverage First Patch

If only one patch is possible first, do this:

### Patch order
1. Add metadata support in loaders/parsers.
2. Add requirement maps to `ResolverContext`.
3. Add scoring in `slot_resolver.py` for:
   - `reader_objection`
   - `proof_mode`
   - `tension_type`
   - `propulsion_type`
4. Emit dummy defaults from chapter planner.
5. Hand-label a small pilot bank of atoms.

This will produce visible gains without requiring a full rewrite.

---

## 17. Direct Dev Intake Text

Use this as the next dev handoff.

```text
STARTUP_RECEIPT
AGENT:              Pearl_Dev
TASK:               Implement reader-state atom metadata + selector upgrade
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          planning / selection / assembly
AUTHORITY_DOCS:     docs/BESTSELLER_GAP_AUDIT.md;docs/ATOM_SCHEMA_AND_SELECTOR_SPEC.md;docs/BESTSELLER_SPINE_WRITER_SPEC.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
WRITE_SCOPE:        phoenix_v4/planning/slot_resolver.py;phoenix_v4/planning/chapter_planner.py;phoenix_v4/planning/assembly_compiler.py;any atom/registry metadata parsers required to expose new fields
OUT_OF_SCOPE:       composer rewrite; registry migration; atom prose rewrites

READ FIRST:
- docs/BESTSELLER_GAP_AUDIT.md
- docs/ATOM_SCHEMA_AND_SELECTOR_SPEC.md
- phoenix_v4/planning/slot_resolver.py
- phoenix_v4/planning/chapter_planner.py
- phoenix_v4/planning/assembly_compiler.py

TASK
Implement additive support for new atom metadata fields:
- proof_mode
- reader_objection
- private_shame_type
- shame_level
- desire_type
- tension_type
- propulsion_type
- callback_role
- authority_mode
- framework_name
- framework_role
- shareability

Then update chapter planner and assembly compiler so chapter plans can pass chapter-level requirement maps into ResolverContext.

Then update slot_resolver scoring so these fields influence candidate ranking while preserving deterministic selection and backward compatibility.

REQUIREMENTS
- additive only
- atoms without new metadata remain valid
- no existing books should stop compiling
- deterministic selection preserved
- tests or evidence must show ranking changes when metadata differs

SUCCESS CRITERIA
- Selector can prefer an atom whose reader_objection matches the chapter request
- Selector can prefer an atom whose propulsion_type matches the chapter ending request
- Compiler passes requirement maps into ResolverContext
- Planner emits requirement placeholders or defaults without breaking current output
```

---

## Final Recommendation

Do not start by rewriting prose.

Start by making the system able to distinguish:
- what the reader is ashamed of,
- what they want,
- what they will resist,
- what kind of proof they need,
- and what should make them turn the page.

That is the leverage point.
