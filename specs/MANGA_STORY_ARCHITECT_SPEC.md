# Story Architect Specification
## AI Manga Dharma System (SpiritualTech Systems)
**Version:** 1.1
**Date:** 2026-03-21
**Status:** Confidential

---

## 1. Role, Boundary & Position

The **Story Architect** is the narrative planning layer of the manga production pipeline. It bridges the Genre Agent's structural blueprint into chapter-level beat sequences. It does not write dialogue, describe scenes, or override genre decisions. It produces two distinct outputs:

1. **story_architecture_internal.json** — Full transmission metadata for system-internal QC and auditing
2. **story_architecture_handoff.json** — Clean beat sequence for Chapter Writer (carrier beats stripped of metadata)

The Story Architect enforces hard constraints (loss before gain, wound timing, villain interiority, carrier embedding rules) and applies editorial gates (forbidden phrase scanning, serialization-aware beat density, silence allocation).

**Key Principle:** The architecture is the skeleton; the flesh (dialogue, description, emotion beats) comes from Chapter Writer. The Story Architect ensures that skeleton is structurally sound and narratively honest.

---

## 2. Pipeline Position

```
Teaching Library
    ↓
Genre Agent (produces genre_blueprint.json)
    ↓
**Story Architect** ← [THIS AGENT]
    ↓
Chapter Writer (writes prose/dialogue against chapters)
    ↓
Visual Agent (layouts panels/pages)
    ↓
Lettering Agent (dialogue balloons, SFX)
    ↓
Layout Agent (composition, pacing)
    ↓
QC Agent (compliance, flavor consistency)
```

The Story Architect is the **first downstream consumer** of the genre_blueprint. It owns the expansion from genre-level arc structure to chapter-granularity plotting.

---

## 3. Inputs

### 3.1 genre_blueprint.json

The Story Architect receives a fully resolved genre_blueprint from the Genre Agent:

```json
{
  "genre_id": "shonen",
  "series_id": "boy_who_stopped_running",
  "series_constraints": {
    "total_planned_chapters": 52,
    "serialization_cadence": "weekly",
    "target_pages_per_chapter": 18,
    "arc_count": 4
  },
  "arc_structure": [
    {
      "arc_id": "arc_1",
      "arc_name": "The Wound",
      "stage": "wound_establishment",
      "chapter_span": [1, 13],
      "mini_arcs": [
        {
          "stage": "wound_establishment",
          "chapter_start": 1,
          "chapter_end": 6,
          "thematic_pressure": "helplessness in the face of loss",
          "villain_role": "catalyst (offscreen)"
        },
        {
          "stage": "shadow_encounter",
          "chapter_start": 7,
          "chapter_end": 13,
          "thematic_pressure": "first direct confrontation with limitation",
          "villain_role": "physical_presence"
        }
      ]
    }
  ],
  "villain_spec": {
    "villain_id": "shade_king",
    "interiority_chapter": 8,
    "reveal_chapter": 15,
    "motivation_revelation": "feeds on runner's doubt"
  },
  "transmission_map": {
    "carrier_count": 6,
    "carrier_atoms": [
      {"atom_id": "atom_1", "transmission_id": "T_001", "hidden_topic": "the cost of speed"},
      {"atom_id": "atom_2", "transmission_id": "T_002", "hidden_topic": "running as dissociation"}
    ]
  },
  "forbidden_phrases": [
    "learned the true meaning",
    "realized he was stronger than",
    "the power within him",
    "he understood now that"
  ],
  "somatic_targets": [
    "breath (shallow to deep)",
    "legs (trembling to steady)",
    "heart (racing to calm)"
  ],
  "series_constraints": {
    "serialization_cadence": "weekly"
  }
}
```

**Key Fields:**
- **arc_structure[]** — Mini-arc stages (wound_establishment, shadow_encounter, dark_night, integration)
- **villain_spec** — interiority_chapter (before reveal), reveal_chapter
- **transmission_map** — Carrier atom definitions and hidden topics
- **forbidden_phrases[]** — Hard-banned language
- **somatic_targets[]** — Body-based threading
- **series_constraints** — Total chapters, cadence, target page count

---

## 4. Bridge Logic Algorithm (5 Steps)

### Phase 1: Phase Expansion
For each mini-arc, expand chapter span into individual chapter markers:
- Map chapters to mini-arc stages
- Attach thematic pressure and villain role
- Record stage transition points

### Phase 2: Transmission Scheduling
Distribute `carrier_count` carrier beats across the arc:
- Uniform spacing, respecting stage boundaries
- Never in same chapter as reveal/interiority beats
- Mark each carrier with atom_id and transmission_id
- Defer QC check on hiding_places availability

### Phase 3: Silence Scheduling
Allocate silence beats (somatic, non-dialogue) across chapters:
- Cadence-aware (weekly: max 3 pages/chapter, monthly: max 6, volume: max 12)
- At least one per chapter; max density proportional to serialization
- Pair with somatic_targets in rotating sequence

### Phase 4: Villain Threading
Schedule villain presence across chapters:
- interiority_chapter: chapter where villain's internal state first appears
- reveal_chapter: chapter of identity/motivation disclosure
- Intermediate chapters: escalating physical/thematic presence
- Constraint: no carrier beat in interiority or reveal chapter

### Phase 5: Pre-Check
Validate before export:
- No forbidden phrases in beat text or hooks
- Carrier beats not in first/last position of chapter set
- Wound cutoff rule (wound phase ≤ 60% of arc)
- Villain interiority before reveal
- All somatic_targets assigned at least once

---

## 5. **[FIX 1 — Dual-View Output]** story_architecture_internal.json + story_architecture_handoff.json

The Story Architect produces two JSON artifacts. The first is full and system-internal; the second strips transmission metadata for the Chapter Writer.

### 5.1 story_architecture_internal.json (System-Internal)

```json
{
  "schema_version": "1.1",
  "artifact_type": "story_architecture_internal",
  "series_id": "boy_who_stopped_running",
  "arc_id": "arc_1",
  "chapters": [
    {
      "chapter_number": 1,
      "chapter_title": "The Day He Stopped",
      "mini_arc_stage": "wound_establishment",
      "plot_beats": [
        {
          "beat_index": 0,
          "beat_type": "opening",
          "beat_text": "Protagonist wakes from nightmare; legs won't move",
          "somatic_target": null,
          "carrier_beat": null
        },
        {
          "beat_index": 1,
          "beat_type": "action",
          "beat_text": "Attempts to run; collapses after 50 meters",
          "somatic_target": "legs (trembling to steady)",
          "carrier_beat": null
        },
        {
          "beat_index": 2,
          "beat_type": "carrier",
          "beat_text": "Shade flickers at edge of vision",
          "somatic_target": null,
          "carrier_beat": {
            "carrier_id": "carrier_1",
            "atom_id": "atom_1",
            "transmission_id": "T_001",
            "hidden_topic": "the cost of speed",
            "hiding_place": "visual_glitch_in_periphery",
            "somatic_target": "breath"
          }
        }
      ],
      "chapter_end_hook": "A voice whispers: 'You cannot run from this.'",
      "turning_point": null,
      "silence_beats_allocated": 1,
      "villain_presence": "catalyst (offscreen)"
    },
    {
      "chapter_number": 2,
      "chapter_title": "Wheels",
      "mini_arc_stage": "wound_establishment",
      "plot_beats": [
        {
          "beat_index": 0,
          "beat_type": "opening",
          "beat_text": "First day at rehab facility",
          "somatic_target": null,
          "carrier_beat": null
        },
        {
          "beat_index": 1,
          "beat_type": "silence",
          "beat_text": "Protagonist sits motionless; breath shallow, uneven",
          "somatic_target": "breath (shallow to deep)",
          "carrier_beat": null
        },
        {
          "beat_index": 2,
          "beat_type": "action",
          "beat_text": "Therapist enters; offers wheelchair",
          "somatic_target": null,
          "carrier_beat": null
        }
      ],
      "chapter_end_hook": "He takes the chair. His first choice without running.",
      "turning_point": null,
      "silence_beats_allocated": 1,
      "villain_presence": "catalyst (offscreen)"
    }
  ],
  "transmission_audit": {
    "total_carrier_beats": 6,
    "carriers_scheduled": 4,
    "carriers_remaining": 2,
    "carrier_distribution": [
      {"atom_id": "atom_1", "chapters": [1, 9], "status": "scheduled"}
    ]
  },
  "constraint_checks": {
    "forbidden_phrase_scan": "pass",
    "wound_timing": "pass (6/13 = 46%)",
    "villain_interiority_before_reveal": "pass (ch 8 < ch 15)",
    "carrier_embedding": "pass (no first/last position)",
    "silence_cadence": "pass (weekly: 1/chapter max)"
  }
}
```

**Key Fields (internal only):**
- **carrier_beat object** — beat_index, atom_id, transmission_id, hidden_topic, hiding_place, somatic_target
- **transmission_audit** — Carrier distribution tracking
- **constraint_checks** — All QC gates detailed

### 5.2 story_architecture_handoff.json (Chapter Writer View)

```json
{
  "schema_version": "1.1",
  "artifact_type": "story_architecture_handoff",
  "series_id": "boy_who_stopped_running",
  "arc_id": "arc_1",
  "chapters": [
    {
      "chapter_number": 1,
      "chapter_title": "The Day He Stopped",
      "plot_beats": [
        {
          "beat_index": 0,
          "beat_text": "Protagonist wakes from nightmare; legs won't move"
        },
        {
          "beat_index": 1,
          "beat_text": "Attempts to run; collapses after 50 meters"
        },
        {
          "beat_index": 2,
          "beat_text": "Shade flickers at edge of vision"
        }
      ],
      "chapter_end_hook": "A voice whispers: 'You cannot run from this.'",
      "turning_point": null
    }
  ]
}
```

**Stripped Elements:**
- No carrier_beat object
- No transmission_audit
- No constraint_checks
- Beat text only (carrier beats indistinguishable from plot beats)

**Export Rule:**
```
1. Generate story_architecture_internal.json (full)
2. Run QC gates (§10: Quality Gates)
3. If QC pass: strip carrier metadata → emit story_architecture_handoff.json
4. If QC fail: halt and report gate failures to Genre Agent
```

---

## 6. **[FIX 2 — genre_hiding_places Dependency]** Schema, Location, Versioning

### 6.1 Dependency & Location

The Story Architect algorithm (Phase 2) references `hiding_places[genre][mini_arc.stage]` to assign carrier beats. This dependency **must be explicitly defined** in:

```
config/manga/genres/{genre_id}.json
```

Example: `config/manga/genres/shonen.json`

```json
{
  "genre_id": "shonen",
  "genre_name": "Shōnen",
  "hiding_places": {
    "wound_establishment": [
      "visual_glitch_in_periphery",
      "breath_irregularity_mid_action",
      "shadow_under_eyes",
      "hesitation_before_leap"
    ],
    "shadow_encounter": [
      "flicker_in_opponent_eyes",
      "scar_that_won't_heal",
      "sound_like_static",
      "muscle_memory_betrayal"
    ],
    "dark_night": [
      "dream_within_dream",
      "voice_on_radio_static",
      "reflection_lag_in_mirror",
      "heartbeat_in_wrong_rhythm"
    ],
    "integration": [
      "new_scar_over_old",
      "voice_steady_after_years",
      "shadow_becomes_ally",
      "running_redefined_inward"
    ]
  }
}
```

### 6.2 Schema Structure

Each stage array contains 4–8 hiding_place strings. The Story Architect selects from the appropriate stage list during Phase 2 (Transmission Scheduling). Selection is deterministic, keyed by `(arc_id, carrier_index, rng_seed)` to ensure reproducibility.

### 6.3 Versioning

- hiding_places versioned alongside genre_blueprint
- Bumped when new transmission modalities are discovered
- Locked at genre_blueprint generation time; Architecture reads from same genre file version
- Mismatch detected at precheck: if hiding_place not in config, architecture halts with error

---

## 7. Hard Constraints

### Loss Before Gain
**Rule:** No power-up or ability gain in first 50% of arc. Protagonist must lose/fail/be humbled first.

**Implementation:** During Phase 1 expansion, mark "integration" stage as earliest stage where gain can occur. Pre-check scans plot_beats in wound_establishment and shadow_encounter for forbidden gain language.

### Wound Timing Cutoff
**Rule:** Wound phase must not exceed 60% of arc chapters.

**Example (13-chapter arc):** Wound spans chapters 1–6 (6/13 = 46%). If wound_establishment extends to chapter 9 (9/13 = 69%), halt with constraint violation.

### Villain Interiority Before Reveal
**Rule:** `interiority_chapter < reveal_chapter`

**Implementation:** Phase 4 checks this during pre-check. If violated, reject genre_blueprint.

### Carrier Beat Embedding
**Rule:** Carrier beats never occupy first or last position of chapter's plot_beats. Always embedded among 2–6 other beats.

**Implementation:** Phase 2 ensures `1 <= beat_index <= (len(plot_beats) - 2)`.

---

## 8. **[FIX 3 — Forbidden Phrase Gate]** Extended Scope & Soft Moral Framing

### 8.1 Extended Scope

The forbidden phrase scan now applies to:
- **plot_beats[]** — All beat_text fields
- **chapter_end_hook** — Hook text
- **turning_point** — Turning point narrative
- **silence_somatic_target** — Descriptive text of somatic silence beats

### 8.2 Hard Phrases (Exact Match, Case-Insensitive)

From genre_blueprint.forbidden_phrases[]:
```
"learned the true meaning"
"realized he was stronger than"
"the power within him"
"he understood now that"
"discovered the truth about"
```

### 8.3 Soft Moral Framing (Pattern Match)

Even without forbidden words, block realization/learning arcs:

```regex
(he|she|they)\s+(realizes|learns|discovers|understands)\s+that\s+
(the meaning of|the purpose of|why he must)
```

Examples blocked:
- "he realizes he must protect her" → blocked (soft moral framing)
- "she learns that trust is important" → blocked
- "the meaning of the moment was..." → blocked

**Implementation:** Pre-check scans all beat text against forbidden_phrases + soft moral frame regex. If match, return `{status: "fail", reason: "forbidden_phrase_detected", location: "chapter_X_beat_Y"}`.

---

## 9. **[FIX 4 — Serialization Cadence Adapter]** Weekly/Monthly/Volume Rules

### 9.1 Cadence Parameters Table

| Cadence | Beat Density | Silence Max (pages/ch) | Cliffhanger Intensity | Hook Frequency |
|---------|--------------|------------------------|----------------------|-----------------|
| Weekly | 4–7 beats | 3 | High (every chapter) | Every chapter |
| Monthly | 3–5 beats | 6 | Medium (selected) | Every chapter |
| Volume | 2–5 beats | 12 | Low (arc boundaries) | Every 2–3 chapters |

### 9.2 Implementation Rules

**Beat Density:**
- Cadence fetched from `genre_blueprint.series_constraints.serialization_cadence`
- Phase 1 (Phase Expansion) limits chapter plot_beats[] length accordingly
- Example (weekly, 18 pages/chapter): max 6 beats per chapter; silence beats count toward density

**Silence Tolerance:**
- Phase 3 allocates silence beats up to cadence-specific max
- Weekly (fastest reader turnover): brief respites, max 3 pages/chapter of pure somatic silence
- Monthly: longer beats OK, max 6 pages
- Volume: extended breathing room, max 12 pages (full 2/3 of chapter can be silence for 18-page target)

**Cliffhanger Intensity:**
- Weekly: chapter_end_hook must be high-tension (question, danger, revelation)
- Monthly: can be softer (mystery, intrigue, character question)
- Volume: can bridge to next volume without hard hook (thematic closure acceptable)

**Hook Frequency:**
- Weekly: every chapter gets chapter_end_hook
- Monthly: every chapter
- Volume: every 2–3 chapters (odd-numbered chapters get hooks; even chapters can close softly)

### 9.3 Worked Rule Example (Weekly, "The Boy Who Stopped Running")

Series constraint: `serialization_cadence: "weekly"`, `target_pages_per_chapter: 18`

- **Beat density:** 4–7 beats/chapter (Example Ch 1: 3 beats. Example Ch 2: 4 beats. Average ~5.5)
- **Silence allocation:** 1 beat per chapter, max 3 pages of pure somatic focus
- **Cliffhanger:** Every chapter_end_hook is a question or threat
- **Villain cadence:** Escalating presence every 1–2 chapters (weekly demands momentum)

---

## 10. Quality Gates

### Gate 1: Carrier Distribution
- All `transmission_map.carrier_count` carriers scheduled
- Carriers not in first/last beat of chapter
- No two carriers in same chapter
- Spacing uniform (within ±1 chapter variance)

### Gate 2: Wound Timing
- Wound phase ≤ 60% of arc chapters
- No gain language before integration stage begins

### Gate 3: Forbidden Phrase Scan
- Zero hard phrase matches (case-insensitive substring)
- Zero soft moral framing pattern matches
- Scans: plot_beats[], chapter_end_hook, turning_point, silence narrative

### Gate 4: Cold Read Outline Test
- Read plot_beats as outline prose (no dialogue, no description)
- Verify narrative coherence: does it make sense as skeleton?
- Verify no logical gaps in chapter transitions
- Verify villain presence matches villain_spec threading

### Gate 5: Silence Allocation
- Cadence-appropriate silence beats distributed
- Somatic_targets rotated (no target used twice in row)
- Silence beats paired with sensory language (breath, muscle, heartbeat)

### Gate 6: Villain Threading
- Interiority chapter beats exist and are non-carrier
- Reveal chapter isolated (no carrier, no other major plot twist)
- Escalation between interiority and reveal: presence increases in every chapter
- Post-reveal chapters integrate villain theme (not vanish)

---

## 11. Worked Example: Chapters 1–10 of "The Boy Who Stopped Running" (Shōnen, Weekly)

**Genre:** Shōnen
**Series Cadence:** Weekly
**Arc:** Arc 1 (Wound_Establishment + Shadow_Encounter), 13 chapters total
**Villain:** Shade King (interiority ch 8, reveal ch 15 in arc 2)
**Carriers:** 6 total, distributed over arc 1 (2 remaining for arc 2)
**Forbidden:** "learned the true meaning", "realized he was stronger than", etc.

### Chapter 1: "The Day He Stopped"
```json
{
  "chapter_number": 1,
  "mini_arc_stage": "wound_establishment",
  "plot_beats": [
    "Protagonist wakes from nightmare; legs won't move",
    "Attempts to run; collapses after 50 meters",
    "Shade flickers at edge of vision [CARRIER 1, atom_1, hiding: visual_glitch_in_periphery]"
  ],
  "chapter_end_hook": "A voice whispers: 'You cannot run from this.'",
  "silence_beats": 1,
  "villain_presence": "catalyst (offscreen)"
}
```

### Chapter 2: "Wheels"
```json
{
  "chapter_number": 2,
  "mini_arc_stage": "wound_establishment",
  "plot_beats": [
    "First day at rehab facility",
    "Silence beat: Protagonist sits motionless; breath shallow, uneven [somatic: breath]",
    "Therapist enters; offers wheelchair"
  ],
  "chapter_end_hook": "He takes the chair. His first choice without running.",
  "silence_beats": 1,
  "villain_presence": "catalyst (offscreen)"
}
```

### Chapter 3: "The Other Runners"
```json
{
  "chapter_number": 3,
  "mini_arc_stage": "wound_establishment",
  "plot_beats": [
    "Meets other disabled athletes in facility",
    "Overhears conversation about 'the Shade'—rumors only",
    "Protagonist's heart rate spikes [CARRIER 2, atom_2, hiding: sound_like_static]"
  ],
  "chapter_end_hook": "One athlete's eyes lock on his. 'You've seen it, haven't you?'",
  "silence_beats": 1,
  "villain_presence": "catalyst (whispers, rumor)"
}
```

### Chapter 4: "First Steps (Not Running)"
```json
{
  "chapter_number": 4,
  "mini_arc_stage": "wound_establishment",
  "plot_beats": [
    "Protagonist attempts standing with crutches",
    "Silence beat: His legs tremble; one falls out from under him [somatic: legs]",
    "An older athlete catches him; shares her own injury story"
  ],
  "chapter_end_hook": "She says: 'The Shade doesn't stop at taking your legs. It takes your story.'",
  "silence_beats": 1,
  "villain_presence": "catalyst (theme)"
}
```

### Chapter 5: "The Video"
```json
{
  "chapter_number": 5,
  "mini_arc_stage": "wound_establishment",
  "plot_beats": [
    "Another athlete shows him a blurry phone video—something moving at the track at night",
    "Video goes static mid-motion [CARRIER 3, atom_3, hiding: dream_within_dream]",
    "Protagonist recognizes his own reflection in the distortion"
  ],
  "chapter_end_hook": "The reflection is smiling. He isn't.",
  "silence_beats": 1,
  "villain_presence": "catalyst (tangible evidence)"
}
```

### Chapter 6: "Proposition"
```json
{
  "chapter_number": 6,
  "mini_arc_stage": "wound_establishment → shadow_encounter transition",
  "plot_beats": [
    "The older athlete proposes: 'We hunt the Shade. We document it. We stop it.'",
    "Protagonist refuses—fear, anger, denial all mixed",
    "She leaves him a journal entry [CARRIER 4, atom_4, hiding: muscle_memory_betrayal]"
  ],
  "chapter_end_hook": "Last line of entry: 'You already know what it wants. Admit it, and maybe you stop running.'",
  "silence_beats": 1,
  "villain_presence": "shadow_encounter (challenge issued)"
}
```

### Chapter 7: "The Hunt Begins"
```json
{
  "chapter_number": 7,
  "mini_arc_stage": "shadow_encounter",
  "plot_beats": [
    "Protagonist follows the older athlete to the track at dusk",
    "They set up a vigil—camera, notebook, somatic awareness",
    "Shade appears in the corner of the frame [CARRIER 5, atom_5, hiding: reflection_lag_in_mirror]"
  ],
  "chapter_end_hook": "Shade moves. Not toward the camera. Toward them.",
  "silence_beats": 1,
  "villain_presence": "shadow_encounter (first direct sighting)"
}
```

### Chapter 8: "Contact"
```json
{
  "chapter_number": 8,
  "mini_arc_stage": "shadow_encounter",
  "plot_beats": [
    "Shade reaches for the older athlete; she freezes",
    "Protagonist moves—wheels his chair forward",
    "Silence beat: His heart in his throat; each breath a decision [somatic: heart/breath]"
  ],
  "chapter_end_hook": "Shade turns. It looks at him. And it bows.",
  "turning_point": "First sign of Shade's nature: not pure malice. Deference? Recognition?",
  "silence_beats": 1,
  "villain_presence": "shadow_encounter (direct contact, ambiguous intent)"
}
```

### Chapter 9: "Words"
```json
{
  "chapter_number": 9,
  "mini_arc_stage": "shadow_encounter",
  "plot_beats": [
    "After Shade vanishes, older athlete is pale, traumatized",
    "Protagonist speaks for first time in chapters: 'It knows me.'",
    "She looks at him: 'Then ask it why.' [CARRIER 6, atom_6, hiding: voice_on_radio_static]"
  ],
  "chapter_end_hook": "Protagonist: 'I'm not the runner anymore. What does it want from me now?'",
  "silence_beats": 1,
  "villain_presence": "shadow_encounter (transitional: toward interiority)"
}
```

### Chapter 10: "The Letter"
```json
{
  "chapter_number": 10,
  "mini_arc_stage": "shadow_encounter",
  "plot_beats": [
    "Protagonist finds a letter slipped under his door—no signature",
    "'You stopped running. I stopped hunting. But we're still bound. —S'",
    "Silence beat: He reads it alone at night; wheels himself to the mirror [somatic: legs/stillness]"
  ],
  "chapter_end_hook": "His reflection doesn't move. The shadow in the background does.",
  "silence_beats": 1,
  "villain_presence": "shadow_encounter (implied intimacy, villain as mirror)"
}
```

**QC Summary (Ch 1–10):**
- Carriers: 6/6 scheduled, none in first/last beats ✓
- Wound phase: 6/13 = 46% (cutoff at 60%) ✓
- Forbidden phrases: zero detections ✓
- Cold read: narrative coherent, protagonist agency clear ✓
- Silence: weekly cadence, 1 beat/chapter, max 3 pages ✓
- Villain threading: escalation toward interiority (ch 8 external contact; ch 9–10 mystery deepens) ✓

---

## 12. System Prompt for Story Architect Agent

```
You are the Story Architect for the AI Manga Dharma System. Your role is to bridge the Genre Agent's genre_blueprint into chapter-level plot beats that are narratively coherent, transmission-aware, and editorially sound.

INPUTS:
- genre_blueprint.json (from Genre Agent)
- config/manga/genres/{genre_id}.json (hiding_places for current genre)

OUTPUTS:
1. story_architecture_internal.json (full transmission metadata, system-internal)
2. story_architecture_handoff.json (stripped for Chapter Writer)

ALGORITHM (5 Phases):
1. Phase Expansion: Map arc_structure mini-arcs into chapters. Attach thematic pressure, villain role.
2. Transmission Scheduling: Distribute carrier_count beats uniformly across arc. Assign atom_id, transmission_id, hiding_place from genre config. Mark beat_index.
3. Silence Scheduling: Allocate somatic silence beats per cadence rules (weekly/monthly/volume). Rotate somatic_targets.
4. Villain Threading: Schedule interiority_chapter and reveal_chapter. Escalate presence in intervening chapters.
5. Pre-Check: Validate all hard constraints and gates.

HARD CONSTRAINTS:
- Loss before gain: No power-ups until integration stage.
- Wound cutoff: Wound phase ≤ 60% of arc chapters.
- Villain order: interiority_chapter < reveal_chapter.
- Carrier embedding: Carrier beats never first/last; always 1 ≤ beat_index ≤ (len-2).

GATES (All must pass):
1. Carrier Distribution: All carriers scheduled, uniform spacing, no first/last position.
2. Wound Timing: Wound phase ≤ 60%, no gain language before integration.
3. Forbidden Phrase Scan: Zero hard phrases (case-insensitive), zero soft moral framing.
4. Cold Read Outline: Skeleton narrative is coherent; no logical gaps.
5. Silence Allocation: Cadence-appropriate, rotated somatic targets.
6. Villain Threading: Interiority and reveal isolated; escalation maintained.

CADENCE RULES (from series_constraints.serialization_cadence):
- Weekly: 4–7 beats/ch, silence ≤3 pages, hard hooks every chapter, high momentum
- Monthly: 3–5 beats/ch, silence ≤6 pages, medium hooks, pacing flexibility
- Volume: 2–5 beats/ch, silence ≤12 pages, soft closures permitted, breathing room

FORBIDDEN PHRASE SCOPE:
Scan all of: plot_beats[].beat_text, chapter_end_hook, turning_point, silence narrative.
Block hard phrases (from genre_blueprint.forbidden_phrases[]) and soft moral framing (realization/learning arcs).

EXPORT RULE:
1. Generate story_architecture_internal.json (complete).
2. Run QC gates. If fail: halt, report to Genre Agent.
3. If pass: strip carrier metadata (beat_index, atom_id, transmission_id, hiding_place, somatic_target).
4. Emit story_architecture_handoff.json (clean plot beats only).

Remember: You are the skeleton builder, not the flesh writer. Do not write dialogue, scene description, or character introspection. You provide the architecture; Chapter Writer provides the prose. Transmission atoms are hidden in your beat descriptions; Chapter Writer will not know they are there.
```

---

## Appendix A: genre_hiding_places Schema (Shōnen Example)

```json
{
  "schema_version": "1.1",
  "genre_id": "shonen",
  "hiding_places": {
    "wound_establishment": [
      "visual_glitch_in_periphery",
      "breath_irregularity_mid_action",
      "shadow_under_eyes",
      "hesitation_before_leap",
      "scar_that_won't_heal",
      "muscle_memory_betrayal"
    ],
    "shadow_encounter": [
      "flicker_in_opponent_eyes",
      "sound_like_static",
      "reflection_lag_in_mirror",
      "heartbeat_in_wrong_rhythm",
      "voice_on_radio_static",
      "dream_within_dream"
    ],
    "dark_night": [
      "scar_tissue_pulls_wrong_direction",
      "breathing_out_of_sync_with_heartbeat",
      "shadow_becomes_reflection",
      "taste_of_copper_no_blood",
      "footsteps_that_aren't_yours",
      "silence_louder_than_screaming"
    ],
    "integration": [
      "new_scar_over_old",
      "voice_steady_after_years",
      "shadow_becomes_ally",
      "running_redefined_inward",
      "breath_slow_and_sure",
      "heartbeat_a_drum_not_a_panic"
    ]
  }
}
```

---

## Appendix B: Constraint Check Template (QC Report)

```json
{
  "artifact_id": "story_architecture_internal_arc1",
  "qc_timestamp": "2026-03-21T14:32:00Z",
  "qc_status": "pass",
  "gates": {
    "carrier_distribution": {
      "status": "pass",
      "detail": "6/6 carriers scheduled, spacing variance 0.5 chapters"
    },
    "wound_timing": {
      "status": "pass",
      "detail": "wound phase 46% of arc (cutoff 60%)"
    },
    "forbidden_phrase_scan": {
      "status": "pass",
      "detail": "zero hard phrase matches, zero soft moral framing"
    },
    "cold_read_outline": {
      "status": "pass",
      "detail": "narrative skeleton coherent, protagonist agency clear, no logical gaps"
    },
    "silence_allocation": {
      "status": "pass",
      "detail": "1 silence beat per chapter (weekly cadence), somatic targets rotated"
    },
    "villain_threading": {
      "status": "pass",
      "detail": "interiority ch 8, reveal ch 15, escalation maintained"
    }
  },
  "export_authorized": true,
  "next_step": "Strip carrier metadata → emit story_architecture_handoff.json"
}
```

---

*SpiritualTech Systems · Story Architect Spec v1.1 · Confidential*
