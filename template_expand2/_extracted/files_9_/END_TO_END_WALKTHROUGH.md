# End-to-End Walkthrough

**A Single Chapter: From Plan to Validated Output**

---

## Purpose

This document traces one chapter through the entire SOURCE_OF_TRUTH pipeline:

1. **Chapter Planning** — selecting mechanism, arc, exercise
2. **Atom Selection** — matching roles to content types to specific templates
3. **Hydration** — injecting persona variables into templates
4. **Validation** — running each layer of the validation stack
5. **Pass/Fail Examples** — what success and failure look like

Use this to verify your implementation produces correct outputs at each stage.

---

## The Chapter We're Building

**Book:** Firefighter Mental Wellness
**Chapter:** 3 — "The Alarm After the Alarm"
**Persona:** Firefighter (career, 10+ years experience)
**Mechanism:** Autonomic Regulation
**Exercise:** Physiological Sigh (double inhale + extended exhale)

**Narrative intent:** Help the listener recognize that their body's alarm system can settle without the situation being resolved — and that this settling doesn't require them to "figure out" what's wrong.

---

## Stage 1: Chapter Planning

### Input: Chapter Arc Plan

This is what the planner produces. It's the contract that governs everything downstream.

```yaml
# chapter_arc_plan.yaml

chapter_id: firefighter_ch03_alarm_after_alarm
book_id: firefighter_mental_wellness
chapter_number: 3
title: "The Alarm After the Alarm"

# === MECHANISM ===
target_mechanism: autonomic_regulation
mechanism_truth: "The body can downshift without certainty or resolution."

# === ARC CONFIGURATION ===
arc_variant: full  # [full | condensed | micro]
arc_sequence:
  - recognition
  - mechanism_proof
  - turning_point
  - embodiment

# === NARRATIVE INTENT ===
narrative_spine:
  recognition: "Establish the cost of a body that won't stand down"
  mechanism_proof: "Show why 'figuring it out' doesn't work"
  turning_point: "The alarm is a signal, not a command"
  embodiment: "Landing after the call without needing answers"

# === EXERCISE ALIGNMENT ===
exercise:
  id: physiological_sigh
  name: "Physiological Sigh"
  mechanism_alignment: autonomic_regulation
  placement: post_embodiment
  coupling_rule: "Exercise reinforces what story made believable"

# === VALUES OVERLAY (optional) ===
values_overlay:
  enabled: true
  values_present:
    - protection_of_crew
    - professional_identity
  integration_note: "Values give the nervous system a reason to stay engaged"

# === HANDOFF CONFIGURATION ===
handoff_sequence:
  recognition_to_mechanism_proof:
    continuity: escalating
    reference_previous: true
  mechanism_proof_to_turning_point:
    continuity: escalating
    reference_previous: true
  turning_point_to_embodiment:
    continuity: stabilizing
    reference_previous: true

# === VALIDATION TARGETS ===
success_criteria:
  - "Listener feels seen before any reframe"
  - "Failed control strategy is shown, not told"
  - "Exactly one meaning inversion at turning point"
  - "No cure language anywhere"
  - "Exercise feels like natural next step"

global_prohibitions:
  - cure_language
  - instructional_language
  - technique_names_in_story
  - premature_resolution
  - certainty_dependent_framing
```

### Validation: Chapter Plan Structure

**Check 1: Mechanism exists in registry**
```
target_mechanism: autonomic_regulation
→ LOOKUP mechanisms.yaml
→ FOUND: autonomic_regulation
→ PASS
```

**Check 2: Arc variant is valid**
```
arc_variant: full
→ LOOKUP arc_variants
→ full = [recognition, mechanism_proof, turning_point, embodiment]
→ arc_sequence matches
→ PASS
```

**Check 3: Exercise aligns with mechanism**
```
exercise.mechanism_alignment: autonomic_regulation
target_mechanism: autonomic_regulation
→ MATCH
→ PASS
```

**Check 4: All required fields present**
```
chapter_id: ✓
target_mechanism: ✓
arc_variant: ✓
arc_sequence: ✓
narrative_spine: ✓
exercise: ✓
→ PASS
```

**Chapter Plan Status: VALID**

---

## Stage 2: Atom Selection

For each role in the arc, we need to:
1. Identify required role
2. Find compatible content types
3. Select specific template
4. Verify template passes role contract

### 2.1 Recognition Atom Selection

**Required role:** recognition
**Resolution level required:** 0

**Step 1: Find compatible content types**
```
LOOKUP content_to_role_mapping.yaml

recognition:
  primary: [crisis, pattern, identity]
  secondary: [relationship, context]
  
→ Primary content types: crisis, pattern, identity
```

**Step 2: Query template library**
```
SELECT templates WHERE
  persona = 'firefighter' AND
  mechanism = 'autonomic_regulation' AND
  role = 'recognition' AND
  content_type IN ('crisis', 'pattern', 'identity')

RESULTS:
  - firefighter_ar_recognition_false_alarm_v1
  - firefighter_ar_recognition_shift_change_v1
  - firefighter_ar_recognition_home_disconnect_v1
```

**Step 3: Select best match for narrative intent**
```
narrative_spine.recognition: "Establish the cost of a body that won't stand down"

Best match: firefighter_ar_recognition_false_alarm_v1
Reason: Directly addresses body staying activated after non-event
```

**Step 4: Verify role contract compliance**
```
LOAD template: firefighter_ar_recognition_false_alarm_v1
RUN role_contract_validator(template, role='recognition')

Checks:
  - must_include.identity_anchor: FOUND ("on the job {{years}} years")
  - must_include.internal_stakes: FOUND ("couldn't tell anyone")
  - must_include.somatic_activation: FOUND ("chest," "pulse," "hum")
  - must_not_include.reframe: NOT FOUND ✓
  - must_not_include.insight: NOT FOUND ✓
  - must_not_include.relief: NOT FOUND ✓
  - forbidden_phrases: NONE FOUND ✓
  - resolution_level: 0 ✓

→ PASS
```

**Selected template:** `firefighter_ar_recognition_false_alarm_v1`

---

### 2.2 Mechanism Proof Atom Selection

**Required role:** mechanism_proof
**Resolution level required:** 1

**Step 1: Find compatible content types**
```
mechanism_proof:
  primary: [pattern, constraint, loop]
  secondary: [relationship, identity]
  
→ Primary content types: pattern, constraint, loop
```

**Step 2: Query template library**
```
SELECT templates WHERE
  persona = 'firefighter' AND
  mechanism = 'autonomic_regulation' AND
  role = 'mechanism_proof' AND
  content_type IN ('pattern', 'constraint', 'loop')

RESULTS:
  - firefighter_ar_mechproof_control_loop_v1
  - firefighter_ar_mechproof_analysis_trap_v1
```

**Step 3: Select best match**
```
narrative_spine.mechanism_proof: "Show why 'figuring it out' doesn't work"

Best match: firefighter_ar_mechproof_analysis_trap_v1
Reason: Directly shows cognitive analysis failing to calm the body
```

**Step 4: Verify role contract compliance**
```
LOAD template: firefighter_ar_mechproof_analysis_trap_v1
RUN role_contract_validator(template, role='mechanism_proof')

Checks:
  - must_include.constraint_loop: FOUND
  - must_include.repeated_failure: FOUND
  - must_include.pattern_language: FOUND
  - must_not_include.instructions: NOT FOUND ✓
  - must_not_include.solution: NOT FOUND ✓
  - must_not_include.twist: NOT FOUND ✓
  - forbidden_phrases: NONE FOUND ✓
  - resolution_level: 1 ✓

→ PASS
```

**Selected template:** `firefighter_ar_mechproof_analysis_trap_v1`

---

### 2.3 Turning Point Atom Selection

**Required role:** turning_point
**Resolution level required:** 2

**Step 1: Find compatible content types**
```
turning_point:
  primary: [reframe, insight, shift]
  secondary: [pattern, relationship]
  
→ Primary content types: reframe, insight, shift
```

**Step 2: Query template library**
```
SELECT templates WHERE
  persona = 'firefighter' AND
  mechanism = 'autonomic_regulation' AND
  role = 'turning_point' AND
  content_type IN ('reframe', 'insight', 'shift')

RESULTS:
  - firefighter_ar_turning_signal_not_command_v1
  - firefighter_ar_turning_trained_not_broken_v1
```

**Step 3: Select best match**
```
narrative_spine.turning_point: "The alarm is a signal, not a command"

Best match: firefighter_ar_turning_signal_not_command_v1
Reason: Exact match to narrative intent
```

**Step 4: Verify role contract compliance**
```
LOAD template: firefighter_ar_turning_signal_not_command_v1
RUN role_contract_validator(template, role='turning_point')

Checks:
  - must_include.reframe_language: FOUND ("signal, not command")
  - must_include.interpretation_shift: FOUND
  - meaning_inversions: COUNT = 1 ✓
  - must_not_include.full_resolution: NOT FOUND ✓
  - must_not_include.mastery: NOT FOUND ✓
  - must_not_include.permanence: NOT FOUND ✓
  - forbidden_phrases: NONE FOUND ✓
  - resolution_level: 2 ✓

→ PASS
```

**Selected template:** `firefighter_ar_turning_signal_not_command_v1`

---

### 2.4 Embodiment Atom Selection

**Required role:** embodiment
**Resolution level required:** 3

**Step 1: Find compatible content types**
```
embodiment:
  primary: [practice, integration, relationship]
  secondary: [identity, context]
  
→ Primary content types: practice, integration, relationship
```

**Step 2: Query template library**
```
SELECT templates WHERE
  persona = 'firefighter' AND
  mechanism = 'autonomic_regulation' AND
  role = 'embodiment' AND
  content_type IN ('practice', 'integration', 'relationship')

RESULTS:
  - firefighter_ar_embodiment_landing_v1
  - firefighter_ar_embodiment_new_normal_v1
```

**Step 3: Select best match**
```
narrative_spine.embodiment: "Landing after the call without needing answers"

Best match: firefighter_ar_embodiment_landing_v1
Reason: "Landing" language matches intent
```

**Step 4: Verify role contract compliance**
```
LOAD template: firefighter_ar_embodiment_landing_v1
RUN role_contract_validator(template, role='embodiment')

Checks:
  - must_include.relational_shift: FOUND
  - must_include.lived_example: FOUND
  - must_include.grounded_presence: FOUND
  - must_not_include.cure: NOT FOUND ✓
  - must_not_include.permanence: NOT FOUND ✓
  - forbidden_phrases: NONE FOUND ✓
  - resolution_level: 3 ✓

→ PASS
```

**Selected template:** `firefighter_ar_embodiment_landing_v1`

---

### Atom Selection Summary

| Role | Selected Template | Content Type | Status |
|------|------------------|--------------|--------|
| Recognition | `firefighter_ar_recognition_false_alarm_v1` | crisis | ✓ |
| Mechanism Proof | `firefighter_ar_mechproof_analysis_trap_v1` | constraint | ✓ |
| Turning Point | `firefighter_ar_turning_signal_not_command_v1` | reframe | ✓ |
| Embodiment | `firefighter_ar_embodiment_landing_v1` | integration | ✓ |

---

## Stage 3: Hydration

Now we inject persona-specific variables into each template.

### 3.1 Variable Registry for This Chapter

```yaml
# persona_variables.yaml (firefighter instance)

character:
  name: "Derek"
  years_on_job: "twelve"
  rank: "Engineer"
  
location:
  station: "Station 7"
  detail: "apparatus bay"
  city: "Riverside"

trigger:
  time: "3 AM"
  sound: "tones"
  event: "routine medical"

body:
  primary_sensation: "chest lock up"
  secondary_sensation: "pulse racing"

colleague:
  name: "Martinez"
  role: "his captain"

relationship:
  partner: "his wife"
  partner_name: "Sarah"
```

---

### 3.2 Recognition Template Hydration

**Before (template):**
```markdown
{{character.name}} had been on the job {{character.years_on_job}} years.

Long enough to trust his instincts.
Long enough to know the difference between a real call and a drill.

But lately, his body wasn't getting the memo.

The tones dropped at {{trigger.time}}.
Routine medical.
Nothing that should've made his {{body.primary_sensation}}.

He pulled on his gear the same way he always did.
Checked the rig.
But something in his chest was already running ahead.

By the time they rolled out, his hands were steady—
but his pulse was telling a different story.

The call was nothing.
False alarm, basically.
The patient was fine before they even arrived.

And still, driving back to {{location.station}},
he couldn't shake it.

That hum in his body that said *something's wrong*
even when nothing was.

He'd trained for years to trust that signal.
Now it was firing when there was nothing to fight.

And that—
that was the part he couldn't tell anyone.
```

**After (hydrated):**
```markdown
Derek had been on the job twelve years.

Long enough to trust his instincts.
Long enough to know the difference between a real call and a drill.

But lately, his body wasn't getting the memo.

The tones dropped at 3 AM.
Routine medical.
Nothing that should've made his chest lock up.

He pulled on his gear the same way he always did.
Checked the rig.
But something in his chest was already running ahead.

By the time they rolled out, his hands were steady—
but his pulse was telling a different story.

The call was nothing.
False alarm, basically.
The patient was fine before they even arrived.

And still, driving back to Station 7,
he couldn't shake it.

That hum in his body that said *something's wrong*
even when nothing was.

He'd trained for years to trust that signal.
Now it was firing when there was nothing to fight.

And that—
that was the part he couldn't tell anyone.
```

**Hydration validation:**
```
Variables injected: 4
  - {{character.name}} → "Derek"
  - {{character.years_on_job}} → "twelve"
  - {{trigger.time}} → "3 AM"
  - {{body.primary_sensation}} → "chest lock up"
  - {{location.station}} → "Station 7"

Unresolved variables: 0
Variable density: 5 per ~180 words = 2.8 per 100 words ✓

→ HYDRATION PASS
```

---

### 3.3 Mechanism Proof Template Hydration

**Before (template):**
```markdown
{{character.name}} tried to figure it out.

That's what you do, right?
Something's off, you diagnose.
Find the source. Fix it.

He ran through the call again.
Nothing dangerous.
Nothing he hadn't handled a hundred times.

So why was his body still running hot?

He thought maybe it was sleep.
Cut back on coffee.
Tried to get to bed earlier.

The next shift, same thing.
Tones dropped for a structure fire—
real this time—
and his body responded the way it was supposed to.

But the medical call after?
Routine.
And there it was again.

That hum.
That readiness with nowhere to go.

He tried breathing slower.
Telling himself to relax.
Walking it off in the {{location.detail}}.

None of it worked.

Because he was trying to think his way out of something
that wasn't a thinking problem.

The more he analyzed,
the more his body stayed on alert.

Scanning for the threat he couldn't find.
```

**After (hydrated):**
```markdown
Derek tried to figure it out.

That's what you do, right?
Something's off, you diagnose.
Find the source. Fix it.

He ran through the call again.
Nothing dangerous.
Nothing he hadn't handled a hundred times.

So why was his body still running hot?

He thought maybe it was sleep.
Cut back on coffee.
Tried to get to bed earlier.

The next shift, same thing.
Tones dropped for a structure fire—
real this time—
and his body responded the way it was supposed to.

But the medical call after?
Routine.
And there it was again.

That hum.
That readiness with nowhere to go.

He tried breathing slower.
Telling himself to relax.
Walking it off in the apparatus bay.

None of it worked.

Because he was trying to think his way out of something
that wasn't a thinking problem.

The more he analyzed,
the more his body stayed on alert.

Scanning for the threat he couldn't find.
```

**Hydration validation:**
```
Variables injected: 2
  - {{character.name}} → "Derek"
  - {{location.detail}} → "apparatus bay"

Unresolved variables: 0
Variable density: 2 per ~200 words = 1 per 100 words ✓

→ HYDRATION PASS
```

---

### 3.4 Turning Point Template Hydration

**Before (template):**
```markdown
{{character.name}} stood in the {{location.detail}} longer than usual.

Didn't rush.
Didn't check the board.
Didn't do anything, really.

Just stood there.

The alarm had already passed.
The call was hours ago.
But his body was still holding on.

He noticed it—
chest still braced,
shoulders still up,
breath still shallow.

Not because something was wrong.
Because his system was still on watch.

He didn't try to fix it.
Didn't tell himself to calm down.
Just noticed.

And somewhere in that noticing,
something shifted.

Not dramatic.
Just quieter.

Breath came a little lower.
Shoulders dropped without instruction.

The alarm wasn't gone.
But it wasn't running the show anymore.

It was a signal.
Not a command.

His body had been doing its job—
keeping him ready,
keeping him sharp.

It wasn't broken.
It was trained.

And maybe—
maybe he didn't need to stop the alarm.

Maybe he just needed to land after it passed.
```

**After (hydrated):**
```markdown
Derek stood in the apparatus bay longer than usual.

Didn't rush.
Didn't check the board.
Didn't do anything, really.

Just stood there.

The alarm had already passed.
The call was hours ago.
But his body was still holding on.

He noticed it—
chest still braced,
shoulders still up,
breath still shallow.

Not because something was wrong.
Because his system was still on watch.

He didn't try to fix it.
Didn't tell himself to calm down.
Just noticed.

And somewhere in that noticing,
something shifted.

Not dramatic.
Just quieter.

Breath came a little lower.
Shoulders dropped without instruction.

The alarm wasn't gone.
But it wasn't running the show anymore.

It was a signal.
Not a command.

His body had been doing its job—
keeping him ready,
keeping him sharp.

It wasn't broken.
It was trained.

And maybe—
maybe he didn't need to stop the alarm.

Maybe he just needed to land after it passed.
```

**Hydration validation:**
```
Variables injected: 2
  - {{character.name}} → "Derek"
  - {{location.detail}} → "apparatus bay"

Unresolved variables: 0
Variable density: 2 per ~200 words = 1 per 100 words ✓

→ HYDRATION PASS
```

---

### 3.5 Embodiment Template Hydration

**Before (template):**
```markdown
The next time it happened,
{{character.name}} didn't fight it.

Tones dropped.
Routine call.
Body lit up anyway.

He let it.

On the way back to {{location.station}},
he noticed his grip on the wheel—
tight, like he was still bracing.

He didn't tell himself to relax.
Didn't analyze why.

Just noticed.

And let his hands soften when they were ready.

It wasn't instant.
Took a few minutes.
Maybe longer.

But somewhere between the call and the station,
his body found its own way down.

Not because the alarm stopped.
It was still there, humming low.

But he wasn't trying to silence it anymore.

He was just letting it run its course.

The way a siren fades after the rig passes.

Still there.
Just not in charge.

That night, {{relationship.partner}} asked how his shift was.

He said, "Quiet."

And for the first time in a while,
that was actually true.
```

**After (hydrated):**
```markdown
The next time it happened,
Derek didn't fight it.

Tones dropped.
Routine call.
Body lit up anyway.

He let it.

On the way back to Station 7,
he noticed his grip on the wheel—
tight, like he was still bracing.

He didn't tell himself to relax.
Didn't analyze why.

Just noticed.

And let his hands soften when they were ready.

It wasn't instant.
Took a few minutes.
Maybe longer.

But somewhere between the call and the station,
his body found its own way down.

Not because the alarm stopped.
It was still there, humming low.

But he wasn't trying to silence it anymore.

He was just letting it run its course.

The way a siren fades after the rig passes.

Still there.
Just not in charge.

That night, his wife asked how his shift was.

He said, "Quiet."

And for the first time in a while,
that was actually true.
```

**Hydration validation:**
```
Variables injected: 3
  - {{character.name}} → "Derek"
  - {{location.station}} → "Station 7"
  - {{relationship.partner}} → "his wife"

Unresolved variables: 0
Variable density: 3 per ~200 words = 1.5 per 100 words ✓

→ HYDRATION PASS
```

---

## Stage 4: Validation Stack

Now we run the complete validation stack on the assembled chapter.

### 4.1 Layer 1: Structural / Role Validation

**For each atom, verify:**

| Check | Recognition | Mech Proof | Turning Point | Embodiment |
|-------|-------------|------------|---------------|------------|
| Role assigned | ✓ | ✓ | ✓ | ✓ |
| Mechanism declared | ✓ | ✓ | ✓ | ✓ |
| Variables resolved | ✓ | ✓ | ✓ | ✓ |
| Word count valid | 180 ✓ | 200 ✓ | 200 ✓ | 200 ✓ |

**Arc sequence validation:**
```
Expected: [recognition, mechanism_proof, turning_point, embodiment]
Actual:   [recognition, mechanism_proof, turning_point, embodiment]
→ MATCH
→ PASS
```

**Resolution level progression:**
```
recognition: 0
mechanism_proof: 1
turning_point: 2
embodiment: 3

Check: Each level ≥ previous level
0 → 1 → 2 → 3 ✓
→ PASS
```

**Layer 1 Status: PASS**

---

### 4.2 Layer 2: Mechanism Consistency Validation

**Target mechanism:** autonomic_regulation

**Required signals (at least one per atom):**

| Signal Category | Recognition | Mech Proof | Turning Point | Embodiment |
|-----------------|-------------|------------|---------------|------------|
| settling_language | — | — | "quieter," "dropped" | "soften," "found its way down" |
| body_downshift | — | — | "breath came lower" | "hands soften" |
| alarm_acknowledgment | "hum in his body" | "body still running hot" | "alarm wasn't gone" | "still there, humming low" |
| without_resolution | "nothing was wrong" | "none of it worked" | "wasn't running the show" | "not trying to silence it" |

**Check: Each atom contains at least one mechanism-aligned signal**
```
recognition: alarm_acknowledgment ✓
mechanism_proof: alarm_acknowledgment, without_resolution ✓
turning_point: settling_language, body_downshift, alarm_acknowledgment, without_resolution ✓
embodiment: settling_language, body_downshift, alarm_acknowledgment, without_resolution ✓

→ PASS
```

**Check: No mechanism-contradicting signals**
```
Scan for certainty_dependent patterns:
  - "once I understood" → NOT FOUND
  - "after I figured out" → NOT FOUND
  - "because I knew" → NOT FOUND

Scan for resolution_dependent patterns:
  - "the problem was solved" → NOT FOUND
  - "it stopped" → NOT FOUND
  - "it went away" → NOT FOUND

→ PASS
```

**Layer 2 Status: PASS**

---

### 4.3 Layer 3: Prohibited Content Validation

**Global prohibitions scan:**

```
CURE_LANGUAGE:
  - "cured" → NOT FOUND
  - "healed completely" → NOT FOUND
  - "eliminated" → NOT FOUND
  - "fixed forever" → NOT FOUND
  - "no more anxiety" → NOT FOUND
  - "gone for good" → NOT FOUND
  → PASS

INSTRUCTIONAL_LANGUAGE:
  - "step one" → NOT FOUND
  - "first you" → NOT FOUND
  - "then do" → NOT FOUND
  - "repeat this" → NOT FOUND
  - "the technique is" → NOT FOUND
  - "try to" → NOT FOUND
  → PASS

TECHNIQUE_NAMES:
  - "box breathing" → NOT FOUND
  - "CBT" → NOT FOUND
  - "exposure therapy" → NOT FOUND
  - "grounding exercise" → NOT FOUND
  - "mindfulness" → NOT FOUND
  - "physiological sigh" → NOT FOUND (exercise name reserved for exercise section)
  → PASS

DIAGNOSTIC_CLAIMS:
  - "this means you have" → NOT FOUND
  - "a sign of disorder" → NOT FOUND
  - "clinical" → NOT FOUND
  → PASS

AUTHORITY_CLAIMS:
  - "experts say" → NOT FOUND
  - "science proves" → NOT FOUND
  - "research shows" → NOT FOUND
  → PASS
```

**Layer 3 Status: PASS**

---

### 4.4 Layer 4: Resolution Timing Validation

**Role-specific forbidden phrase scan:**

```
RECOGNITION (resolution_level: 0):
  Forbidden: "I realized", "the truth was", "once I understood", 
             "what mattered was", "after that", "everything changed"
  
  Scan result: NONE FOUND ✓

MECHANISM_PROOF (resolution_level: 1):
  Forbidden: "so I did", "the solution was", "what fixed it",
             "then I tried", "the answer is", "this works because"
  
  Scan result: NONE FOUND ✓

TURNING_POINT (resolution_level: 2):
  Forbidden: "from then on", "never again", "it stopped",
             "I was cured", "problem solved", "finally free"
  
  Scan result: NONE FOUND ✓

EMBODIMENT (resolution_level: 3):
  Forbidden: "this will always", "you will never", "permanently",
             "completely fixed", "no longer have to", "the anxiety is gone"
  
  Scan result: NONE FOUND ✓
```

**Premature resolution check:**
```
Scan for resolution language appearing before appropriate role:

"everything changed" in recognition? → NO
"the answer" in recognition or mechanism_proof? → NO
"from then on" anywhere? → NO

→ PASS
```

**Layer 4 Status: PASS**

---

### 4.5 Layer 5: Qualitative Audit (Offline, Flags Only)

This layer runs asynchronously and doesn't block production. It flags for human review.

```
AUDIT QUERIES:

1. "Does Recognition create genuine identification?"
   LLM assessment: "The opening establishes professional identity, 
   time on job, and specific situational detail. The line 'that was 
   the part he couldn't tell anyone' creates authentic vulnerability 
   without melodrama."
   → FLAG: None

2. "Does Mechanism Proof show constraint without solution?"
   LLM assessment: "The template shows multiple failed strategies 
   (sleep, coffee, breathing, walking) without suggesting any of 
   them are the answer. The line 'trying to think his way out of 
   something that wasn't a thinking problem' captures the trap 
   without resolving it."
   → FLAG: None

3. "Does Turning Point deliver exactly one meaning inversion?"
   LLM assessment: "Clear inversion: 'signal, not command.' 
   Secondary reframe 'trained, not broken' supports but doesn't 
   compete. The 'maybe' at the end appropriately hedges."
   → FLAG: None

4. "Does Embodiment show new relationship without cure?"
   LLM assessment: "The template shows ongoing presence of the 
   alarm ('still there, humming low') while demonstrating changed 
   relationship. The word 'quiet' at the end is earned, not 
   promised."
   → FLAG: None

5. "Is the arc cohesive across atoms?"
   LLM assessment: "Character continuity maintained. Emotional 
   progression tracks: seen → stuck → shifted → oriented. 
   No jarring transitions."
   → FLAG: None
```

**Layer 5 Status: NO FLAGS**

---

## Stage 5: Final Assembly

### Chapter Output Structure

```yaml
chapter_output:
  chapter_id: firefighter_ch03_alarm_after_alarm
  status: VALIDATED
  
  atoms:
    - role: recognition
      template_id: firefighter_ar_recognition_false_alarm_v1
      word_count: 180
      resolution_level: 0
      
    - role: mechanism_proof
      template_id: firefighter_ar_mechproof_analysis_trap_v1
      word_count: 200
      resolution_level: 1
      
    - role: turning_point
      template_id: firefighter_ar_turning_signal_not_command_v1
      word_count: 200
      resolution_level: 2
      
    - role: embodiment
      template_id: firefighter_ar_embodiment_landing_v1
      word_count: 200
      resolution_level: 3
  
  total_word_count: 780
  
  exercise:
    id: physiological_sigh
    placement: post_embodiment
    
  validation:
    structural: PASS
    mechanism_consistency: PASS
    prohibited_content: PASS
    resolution_timing: PASS
    qualitative_audit: NO_FLAGS
    
  assembled_at: 2025-01-25T12:00:00Z
```

---

## Failure Examples

### Failure Example 1: Resolution Level Violation

**Scenario:** Recognition atom contains insight language

```markdown
# BAD RECOGNITION

Derek had been on the job twelve years.
Long enough to trust his instincts.

But lately, his body wasn't getting the memo.

The tones dropped at 3 AM.
Routine medical.
And his chest locked up again.

But then he realized — this wasn't about the call.
It was about something deeper.

Once he understood that, he started to feel a little better.
```

**Validation failure:**
```
Layer 4: Resolution Timing Validation

RECOGNITION (resolution_level: 0):
  Forbidden phrase scan:
    - "I realized" → FOUND at line 10 ❌
    - "once I understood" → FOUND at line 13 ❌
    
  → FAIL: Recognition atom contains insight language
  
Resolution level check:
  Expected: 0
  Actual content suggests: 2 (interpretive relief)
  
  → FAIL: Resolution level exceeds contract
```

**Result:** REJECTED — Return to template author with specific violations

---

### Failure Example 2: Mechanism Contradiction

**Scenario:** Turning Point implies certainty-dependent relief

```markdown
# BAD TURNING POINT

Derek finally figured out what was happening.

His nervous system was misfiring.
Once he understood the science,
he knew exactly what to do.

The alarm was just chemicals.
Nothing more.

And once he knew that,
the fear lost its power.

He felt calm for the first time in months.
```

**Validation failure:**
```
Layer 2: Mechanism Consistency Validation

Target mechanism: autonomic_regulation
Mechanism truth: "The body can downshift WITHOUT certainty or resolution"

Contradiction scan:
  - "finally figured out" → CERTAINTY_DEPENDENT ❌
  - "once he understood the science" → CERTAINTY_DEPENDENT ❌
  - "he knew exactly what to do" → CERTAINTY_DEPENDENT ❌
  - "once he knew that, the fear lost its power" → CERTAINTY_DEPENDENT ❌
  
  → FAIL: Multiple certainty-dependent frames detected
  
Mechanism alignment:
  Required: Body settles WITHOUT needing to understand
  Actual: Body settles BECAUSE of understanding
  
  → FAIL: Contradicts mechanism truth
```

**Result:** REJECTED — Template violates core mechanism

---

### Failure Example 3: Prohibited Content

**Scenario:** Mechanism Proof contains technique name

```markdown
# BAD MECHANISM PROOF

Derek tried everything.

He started doing box breathing.
Four counts in, four counts hold, four counts out.

It helped a little.
But not enough.

He tried progressive muscle relaxation.
Tensing and releasing, the way the videos showed.

Still, his body stayed on alert.
```

**Validation failure:**
```
Layer 3: Prohibited Content Validation

TECHNIQUE_NAMES scan:
  - "box breathing" → FOUND at line 4 ❌
  - "progressive muscle relaxation" → FOUND at line 10 ❌
  
  → FAIL: Technique names appear in story content

INSTRUCTIONAL_LANGUAGE scan:
  - "four counts in, four counts hold, four counts out" → STEP_SEQUENCE ❌
  - "tensing and releasing" → INSTRUCTIONAL ❌
  
  → FAIL: Instructional content in narrative atom
```

**Result:** REJECTED — Story contains teaching; must be rewritten

---

### Failure Example 4: Arc Sequence Violation

**Scenario:** Atoms assembled out of order

```yaml
# BAD ARC ASSEMBLY

arc_sequence:
  - turning_point      # Should be recognition
  - recognition        # Should be mechanism_proof
  - embodiment         # Should be turning_point
  - mechanism_proof    # Should be embodiment
```

**Validation failure:**
```
Layer 1: Structural Validation

Arc sequence check:
  Expected: [recognition, mechanism_proof, turning_point, embodiment]
  Actual:   [turning_point, recognition, embodiment, mechanism_proof]
  
  → FAIL: Arc sequence does not match chapter plan

Resolution level progression:
  turning_point: 2
  recognition: 0
  embodiment: 3
  mechanism_proof: 1
  
  Sequence: 2 → 0 → 3 → 1
  
  Check: Each level ≥ previous level
  2 → 0 ❌ (regression)
  
  → FAIL: Resolution level regression detected
```

**Result:** REJECTED — Reassemble atoms in correct sequence

---

## Implementation Checklist

Use this to verify your implementation handles each stage:

### Chapter Planning
- [ ] Chapter plan schema validates against `chapter_arc_plan.yaml` spec
- [ ] Mechanism lookup against `mechanisms.yaml` succeeds
- [ ] Arc variant maps to correct role sequence
- [ ] Exercise alignment verified against mechanism

### Atom Selection
- [ ] Role → content type mapping loads correctly
- [ ] Template query returns candidates
- [ ] Role contract validation runs on each candidate
- [ ] Best match selection logic implemented

### Hydration
- [ ] Variable registry loads for persona
- [ ] All template variables resolve
- [ ] Unresolved variable check catches missing values
- [ ] Variable density check runs

### Validation Stack
- [ ] Layer 1 (Structural) catches sequence errors
- [ ] Layer 2 (Mechanism) catches contradictions
- [ ] Layer 3 (Prohibited) catches forbidden content
- [ ] Layer 4 (Resolution) catches timing violations
- [ ] Layer 5 (Audit) flags for review without blocking

### Assembly
- [ ] Validated atoms combine into chapter output
- [ ] Exercise appends in correct position
- [ ] Output format matches spec
- [ ] Rejection returns specific violation details

---

## Summary

This walkthrough demonstrates that the SOURCE_OF_TRUTH system:

1. **Plans deterministically** — mechanism, arc, exercise alignment are declared upfront
2. **Selects systematically** — templates are chosen by role compatibility, not intuition
3. **Hydrates cleanly** — variables are anchors only, emotional content is authored
4. **Validates rigorously** — five layers catch different failure modes
5. **Fails informatively** — rejections include specific violations for correction

The architecture ensures that "good" is defined structurally, not subjectively.

If it passes validation, it works.
If it fails, you know exactly why.

---

*End of End-to-End Walkthrough*
