# Manga Chapter Writer Spec v1.1
## AI Manga Dharma System · SpiritualTech Systems

---

## 1. Role, Boundary & Position

The Chapter Writer is the **first agent to produce actual manga language**: dialogue, sound effects (SFX), captions, and panel-by-panel scripts. It is a *renderer*, not a storyteller.

**Strict boundaries:**
- Does NOT alter beats from Story Architect
- Does NOT override series constraints or genre decisions
- Does NOT introduce teaching language, dharma vocabulary, or emotional summary
- Does NOT invent character agency or resolve conflicts via dialogue
- Receives story_architecture_handoff.json in deterministic form; executes it faithfully

The Chapter Writer transforms structural beat data into speakable language while enforcing silence discipline, villain gating, and phrase contamination detection. Every panel output must survive downstream agents who will fragment its content (Visual Agent sees camera/action; Lettering Agent sees dialogue/SFX/caption) and QC who will audit for heresy and sentiment violation.

---

## 2. Pipeline Position

**Input pipeline:**
```
Teaching Library → Genre Agent → Story Architect → [Chapter Writer] → Visual Agent
                                      ↓                    ↓
                                story_architecture_  → chapter_script.json
                                handoff.json +           (two versions)
                                style_bible.json
```

**Input files:**
- `story_architecture_handoff.json`: beat sequence, character arcs, mood progression, silence markers
- `style_bible.json`: voice/cadence per character, SFX vocabulary, caption tone
- `series_constraints.json`: forbidden phrase list, dharma vocabulary gating, villain coherence limits

**Output file:**
- `chapter_script.json`: dual outputs (writer_handoff for downstream agents, internal_record for QC)

---

## 3. Transmission Splitter: Dual-View Architecture

**Problem:** The Chapter Writer knows which panels carry carrier beats (moments designed to *feel worse while winning*). Knowing this creates psychological pressure to emphasize those moments in dialogue/SFX, leaking the intentional emotional damage into visible language.

**Solution:** Two-version output, never mixed.

**writer_handoff.json** (sent downstream):
- No `is_carrier_beat` field
- No `somatic_intention` field
- All scenes treated as narratively neutral
- Visual Agent receives camera/action/mood/background but NOT dialogue
- Lettering Agent receives dialogue/SFX/caption but NOT camera/action/mood

**internal_record.json** (QC only):
- Includes `is_carrier_beat: true/false` annotation
- Includes `somatic_intention` field for QC to verify mechanical fidelity
- Audit-only; never reaches production agents
- Used to verify that carrier beat panels do NOT contain emphasizing language

**Transmission Splitter enforces:**
- Carrier beat panels in internal_record must have stripped, non-emphatic dialogue/SFX in writer_handoff
- If a panel is `is_carrier_beat: true`, its dialogue in writer_handoff must be smaller/quieter than non-carrier context
- SFX on carrier beat panels must be ambient, not percussive (silence better than CRACK)

---

## 4. Inputs

### 4.1 story_architecture_handoff.json Structure

```json
{
  "chapter_id": "CH005",
  "character_arcs": [
    {
      "character": "protagonist_name",
      "emotional_progression": ["isolated", "determined", "cost_realized", "forward_motion"],
      "beats": [
        {
          "beat_id": "beat_001",
          "beat_type": "silent",
          "duration_panels": 3,
          "preceded_by": "action",
          "followed_by": "dialogue",
          "carrier_beat": false,
          "somatic_intention": "breath_after_impact"
        }
      ]
    }
  ],
  "page_sequence": [
    {
      "page_number": 1,
      "panel_count": 4,
      "mood_progression": ["tense", "clarifying", "determined"],
      "silence_markers": []
    }
  ]
}
```

**Key fields for Chapter Writer:**
- `beat_type`: dialogue, silent, action, reaction, revelation
- `carrier_beat`: true = moment designed to feel worse while progressing the story
- `somatic_intention`: physical/emotional truth; QC audits, never enters dialogue
- `mood_progression`: trajectory per page for SFX/caption tone
- `silence_markers`: pages or panels marked as containing silent sequences

### 4.2 style_bible.json Reference

```json
{
  "character_voice": {
    "protagonist": {
      "cadence": "short_declarative",
      "forbidden_phrases": ["I feel", "I believe", "my inner strength"],
      "sfx_preference": "stark_environmental"
    },
    "villain": {
      "cadence": "verbose_seductive",
      "max_consecutive_lines": 2,
      "must_be_proven_wrong_by": "action_not_dialogue"
    }
  },
  "sfx_vocabulary": {
    "impact": ["SLAM", "CRACK", "THUD"],
    "ambient": ["rustle", "breathe", "tick"],
    "emotional_punctuation": []
  }
}
```

### 4.3 series_constraints.json

- Forbidden phrase list (dharma vocabulary, teaching language, emotional summary)
- Monologue limits per character
- Healing-motion sentiment floor (dialogue never celebrates injury recovery)
- Villain interiority gating (how many internal thoughts villain gets)

---

## 5. Output — chapter_script.json Structure

### 5.1 Top Level

```json
{
  "chapter_id": "CH005",
  "writer_handoff": {
    "pages": [ ... ]
  },
  "internal_record": {
    "pages": [ ... ]
  }
}
```

### 5.2 Page Object

```json
{
  "page_number": 1,
  "page_type": "standard|silent|high_action",
  "panels": [ ... ],
  "mood": "tense",
  "silence_guard": false
}
```

**page_type enum:**
- `standard`: regular narrative page, may contain mixed silent/dialogue panels
- `silent`: ALL panels on this page must be `panel_type: silent` with zero text fields (dialogue, sfx, caption all null/empty)
- `high_action`: action-dominant page; dialogue sparse, SFX prominent

**[FIX 1 — Silent page/panel type schema conflict resolved]:**
- If `page_type: "silent"`, the page is the authority. ALL panels inherit `panel_type: "silent"`.
- A page with ONE silent panel is NOT a "silent page"; it's a `standard` page containing a single silent panel.
- Clarity: page_type governs the entire page's narrative role; panel_type is the granular enforcement.

### 5.3 Panel Object (writer_handoff version)

```json
{
  "panel_id": "CH005_P01_PL01",
  "panel_number": 1,
  "page_type": "standard",
  "panel_type": "dialogue|silent|action|reaction|revelation",
  "camera": "wide|medium|close|extreme_close|pov|two_shot",
  "subject": "protagonist|antagonist|other_character|environment",
  "action": "stands",
  "background": "street_intersection",
  "mood_direction": "tense_clarifying",
  "silence_guard": false,
  "dialogue": [
    {
      "speaker": "protagonist",
      "bubble_type": "speech|thought|whisper|shout",
      "text": "What do you want?"
    }
  ],
  "sfx": [
    {
      "sfx_text": "rustle",
      "weight": "ambient|medium|heavy"
    }
  ],
  "caption": null,
  "end_hook": null
}
```

**In internal_record, add:**
```json
{
  "is_carrier_beat": false,
  "somatic_intention": "grounded_after_shock"
}
```

**[FIX 3 — Field Classification Table]:** See Section 10 for full visibility matrix.

---

## 6. Panel Field Definitions

### 6.1 camera enum
- `wide`: full scene, all participants visible
- `medium`: character + immediate surroundings
- `close`: face/hands, emotional focus
- `extreme_close`: single feature, high intensity
- `pov`: through character's eyes
- `two_shot`: two characters in frame, relational dynamics

### 6.2 subject
Name or role of primary focus. Protagonist, antagonist, named NPC, or "environment" for landscape/setting panels.

### 6.3 action
Verb describing primary physical motion: "stands", "walks", "raises_fist", "breathes", "falls", "looks_away". Not emotional summary; not teaching motion.

### 6.4 background
Discrete location: "street_intersection", "cave_mouth", "meditation_hall", "destroyed_cityscape". Used for environment consistency, SFX anchoring, and visual theme tracking.

### 6.5 mood_direction
Two-part progression showing trajectory within page:
- Arrival mood → Destination mood
- Examples: "tense_clarifying", "shocked_determined", "isolated_connected"
- Never uses healing vocabulary, celebration, or transcendence language

### 6.6 dialogue array
Each entry:
```json
{
  "speaker": "character_name",
  "bubble_type": "speech|thought|whisper|shout",
  "text": "..."
}
```

**bubble_type:**
- `speech`: normal dialogue, fully audible
- `thought`: internal monologue (villain gated; protagonist rarely)
- `whisper`: reduced volume, intimacy or fear
- `shout`: emphasis or distance, not emotional proclamation

**Dialogue rules** (Section 8) apply here.

### 6.7 sfx (Sound Effects)
```json
[
  {
    "sfx_text": "SLAM",
    "weight": "ambient|medium|heavy"
  }
]
```

- `ambient`: background texture, tick/rustle/breathe (weight 1)
- `medium`: present action, footstep/door close (weight 2)
- `heavy`: impact/emotion, CRACK/SLAM (weight 3)

SFX can carry emotional weight without language. See Section 7 (Silence as craft discipline).

### 6.8 caption
Narrator or metadata text. HIGHEST RISK for dharma vocabulary leak. See Section 8 (Dialogue rules) for pass/fail examples.

### 6.9 page_type
Inherited from page object. Governs panel validity.

### 6.10 panel_type enum
- `silent`: no dialogue, no sfx, no caption. Null/empty fields only.
- `dialogue`: character speech present
- `action`: motion-dominant, minimal text
- `reaction`: emotional response, brief dialogue or facial focus
- `revelation`: information delivery, structured caption or SFX-driven

**[FIX 1]:** If page_type is "silent", all panels must be panel_type "silent". Mismatch is an error.

### 6.11 silence_guard bool
**[FIX 2 — silence_guard pin-down]:**

Set to `true` by Transmission Splitter on:
- Last 2 panels on the page immediately BEFORE any silent page
- First 2 panels on the page immediately AFTER a silent page
- Counting is page-local, not chapter-sequential

**Panels with silence_guard=true must enforce:**
- Reduced dialogue density: 1 speaker maximum, max 2 lines total
- bubble_type restricted to "whisper" only (no shout, no thought)
- SFX restricted to ambient weight only (no heavy impacts)
- Creates 2-panel buffer zone around every silence sequence

Example: If page 5 is silent, then:
- Page 4, panels 3–4: silence_guard=true (trailing)
- Page 6, panels 1–2: silence_guard=true (leading)

### 6.12 end_hook
Page-final dialogue or SFX that propels reader to next page. Must be exact match to story_architecture_handoff.json. QC gate: if end_hook is present, it must appear verbatim in final panel of page.

---

## 7. Silence as Craft Discipline

### 7.1 Silent Pages (page_type: "silent")

A silent page contains ZERO text of any kind:
- All panels have `panel_type: "silent"`
- dialogue array: empty or null
- sfx array: empty or null
- caption: null
- This is absolute. No exceptions for "ambient" SFX or thought captions.

Silent pages are not empty pages; they are *densely loaded with visual information*: camera movement, composition, detail, and environmental progression.

### 7.2 Five-Beat Silence Protocol

When silence occurs (1–3 consecutive silent panels), follow this progression:

1. **Arrival**: Character enters the silence; final dialogue/SFX of previous panel sets tone
2. **Stillness**: Silence deepens; character at rest or processing
3. **Detail**: Camera finds specific texture: water droplet, dust mote, fabric fold (visual poetry)
4. **World**: Environment responds; wind, light, sound of place without speech
5. **Return**: Character or narrative re-engages; silence broken by action or dialogue

Each beat occupies 1 panel. Not all silences are 5 panels; shorter silences compress beats. Longer silences expand them.

**Example structure (3-panel silence):**
- Panel 1: Arrival + Stillness combined (character stops, absorbs shock)
- Panel 2: Detail (close on trembling hand; light catching tears)
- Panel 3: World (rain begins; sound of environment, no speech)
- (Next page resumes at beat 5/Return implicitly, or explicitly on panel 1 of next page)

### 7.3 Silence Contamination Adjacency Rule

**[FIX 2]:** No dialogue may "frame" a silent sequence in a way that comments on or summarizes it.

Forbidden pattern:
- Panel 5 (preceding silence): Character says "I need to think about this."
- Panels 6–8: Silent
- Panel 9 (following silence): Character says "Now I understand."

The dialogue before and after contaminates the silence, turning it into a thinking montage rather than a raw experience.

**Correct pattern:**
- Panel 5 (preceding silence): Character says "..." (dialogue unrelated to silence itself)
- Silence_guard=true reduces dialogue weight
- Panels 6–8: Silent
- Silence_guard=true reduces dialogue weight
- Panel 9 (following silence): Action-driven dialogue or silent transition

**QC check:** Do the dialogue before/after *reflect on* the silence? If yes, error.

---

## 8. Dialogue Rules

### 8.1 Core Prohibitions

**No teaching language:**
- Forbidden: "I learned that...", "This teaches me...", "The lesson is..."
- Forbidden: "I realized my true nature", "Inner strength awakens", "Find your dharma"

**No emotional summary:**
- Forbidden: "I feel brave now", "You make me sad", "My heart is breaking"
- Forbidden: "Fear consumes me", "Love guides me", "Wisdom flows"

**No dharma vocabulary:**
- Forbidden: "enlightenment", "karma", "dharma", "chakra", "awakening", "transcendence", "divine"
- Forbidden: "practice", "meditation" (unless grounded: character sits on mat, does not declare intention)
- Forbidden: "compassion" in the speaker's voice (show, don't tell)

**No character telling themselves or reader what their arc is:**
- Forbidden: "I'm learning to be brave", "This loss is making me stronger"
- Allowed: "I'm standing." (action), "What now?" (question), specific sensory detail

### 8.2 Dialogue Mechanics

- Short, declarative sentences preferred (protagonist style)
- Subtext via what is NOT said
- Dialogue reveals character through voice, not through self-analysis
- No monologues exceeding 3 lines without another character interrupting or reacting

### 8.3 Captions: Highest-Risk Vector

Captions are narrator voice; they *must not* leak dharma vocabulary or emotional summary under any circumstances.

**FAIL example (caption on protagonist realizing something):**
> "In that moment, she understood the truth within her heart."

Words: "understood the truth", "within her heart" = teaching language + emotional summary.

**PASS example (same narrative moment, caption neutral):**
> "Rain on the empty street."

Caption describes observable world; reader infers understanding from silence + action.

**FAIL example (villain defeat caption):**
> "His enlightenment crumbled as the protagonist transcended her limitations."

Words: "enlightenment", "transcended limitations" = dharma vocabulary.

**PASS example (villain defeat caption):**
> "The sword fell first."

Facts only; character arcs inferred from action.

### 8.4 Forbidden Phrase Scanning

Chapter Writer applies regex/keyword scan on every dialogue/caption field:

```
forbidden_patterns = [
  r"i\s+(feel|believe|understand|learn|realize)",
  r"(inner|true|real|higher)\s+(self|nature|strength|wisdom)",
  r"(enlightenment|awakening|transcendence|dharma|karma|chakra)",
  r"(healing|recovery|renewed|reborn|transformed)",
  r"(my\s+heart|deep\s+within|soul|spirit)"
]
```

Any match: error, returns offending phrase to human reviewer.

---

## 9. Villain Dialogue Exception

Villains may be coherent, seductive, and philosophically sophisticated. They may use teaching language, claim dharma, invoke transcendence—**because they must be proven wrong by consequence, not argument.**

**Gating:**
- Villain may speak 2 consecutive lines max without protagonist/environment interruption
- Villain dialogue triggers *somatic_intention* audit: if villain claims transcendence and somatic_intention contradicts (e.g., "seductive_lie" vs. "true_wisdom"), QC flags
- Villain interiority (thought bubbles) capped at 1 per chapter
- Villain "teaching" line immediately followed by protagonist action that invalidates the teaching (see Worked Example, Section 13)

**Pattern:**
```
Panel A: Villain speaks philosophical truth (allowed: "Your struggle purifies you.")
Panel B: Protagonist hits harder / ignores / contradicts with action
Result: Audience knows villain is seductive but wrong
```

No dialogue exchange proves villain wrong. Action proves villain wrong.

---

## 10. Field Classification Table [FIX 3 — Field Classification]

| Field | Visual Agent | Lettering Agent | QC Agent | Internal Only |
|-------|:---:|:---:|:---:|:---:|
| panel_id | ✓ | ✓ | ✓ | |
| panel_number | ✓ | ✓ | ✓ | |
| page_type | ✓ | ✓ | ✓ | |
| panel_type | ✓ | ✓ | ✓ | |
| camera | ✓ | | ✓ | |
| subject | ✓ | | ✓ | |
| action | ✓ | | ✓ | |
| background | ✓ | | ✓ | |
| mood_direction | ✓ | | ✓ | |
| silence_guard | ✓ | ✓ | ✓ | |
| dialogue | | ✓ | ✓ | |
| sfx | | ✓ | ✓ | |
| caption | | ✓ | ✓ | |
| end_hook | | ✓ | ✓ | |
| is_carrier_beat | | | ✓ | ✓ (internal_record only) |
| somatic_intention | | | ✓ | ✓ (internal_record only) |

**Enforcement:**
- writer_handoff.json contains only fields marked ✓ for Visual/Lettering agents
- internal_record.json contains all fields including is_carrier_beat and somatic_intention
- Transmission Splitter strips is_carrier_beat and somatic_intention from writer_handoff
- Downstream agents (Visual, Lettering) receive writer_handoff; never see internal_record
- QC receives internal_record; audits somatic_intention alignment and carrier beat dialogue discipline

---

## 11. Quality Gates

### 11.1 Forbidden Phrase Scan
Run keyword/regex check on all dialogue and caption fields. Return offending phrase + panel_id to human. Zero auto-correction.

### 11.2 Silent Purity
- If page_type="silent", verify ALL panels have panel_type="silent"
- Verify dialogue, sfx, caption all null/empty on silent panels
- Verify no silence_guard=true panels on a silent page (they belong on adjacent pages)

### 11.3 Silence Contamination Adjacency
- For each silent sequence (1+ consecutive silent panels), check last 2 panels before and first 2 panels after
- Do the non-silent dialogue/caption immediately before/after *reflect on* the silence (emotional summary, lesson-drawing)?
- If yes: error, requires human rewrite

### 11.4 Monologue Contradiction
- If villain has 2+ consecutive lines, check second line against first for logical coherence
- If villain claims truth in line 1 and line 2 contradicts (not ambiguity, direct contradiction), flag for human review
- (Villain seduction is allowed; self-contradiction is sloppy.)

### 11.5 Healing-Motion Sentiment Scan
- Scan all dialogue/caption for words indicating recovery, healing, transformation, renewal
- Context check: is character celebrating injury recovery or physical healing?
- If yes: flag as potential dharma vocabulary leak (healing-motion as spiritual metaphor)
- Allowed: "The wound closed." (fact). Forbidden: "The wound healed her soul." (metaphor)

### 11.6 End-Hook Exact Match
- If end_hook field is populated, verify it matches verbatim in the final dialogue/caption of the final panel on that page
- If mismatch: error with both versions shown

### 11.7 Villain Interiority Gating
- Count all thought bubble lines spoken by villain across chapter
- If count > 3 (3 lines total, not 3 bubbles): flag as excessive interiority
- Villain must be externally seductive, not internally justified

### 11.8 Cold Read
- Human QC agent reads chapter_script.json without knowing the underlying somatic_intention or carrier beat markers
- Can QC understand the scene without leaking intention? Is it speakable and dramatically coherent on its own?
- If no: dialogue is over-determined by structure, needs rewrite

---

## 12. Worked Example — Silent Sequence

**Context:** Protagonist just learned that their discipline was based on a lie. Story Architect beat: 3-panel silence, arrival → stillness → detail → world → return compressed across pages.

**page_type: "standard"** (not silent page; contains mixed content)

```json
{
  "page_number": 12,
  "page_type": "standard",
  "panels": [
    {
      "panel_id": "CH005_P12_PL04",
      "panel_number": 4,
      "panel_type": "dialogue",
      "camera": "close",
      "subject": "protagonist",
      "action": "absorbs_blow",
      "background": "dojo_floor",
      "mood_direction": "shocked_settling",
      "silence_guard": true,
      "dialogue": [
        {
          "speaker": "mentor",
          "bubble_type": "speech",
          "text": "I lied to you."
        }
      ],
      "sfx": [],
      "caption": null,
      "end_hook": null,
      "is_carrier_beat": false,
      "somatic_intention": "anchor_before_silence"
    },
    {
      "panel_id": "CH005_P13_PL01",
      "panel_number": 1,
      "page_number": 13,
      "panel_type": "silent",
      "camera": "medium",
      "subject": "protagonist",
      "action": "stands",
      "background": "dojo_floor",
      "mood_direction": "still",
      "silence_guard": false,
      "dialogue": [],
      "sfx": [],
      "caption": null,
      "is_carrier_beat": true,
      "somatic_intention": "stillness_after_rupture"
    },
    {
      "panel_id": "CH005_P13_PL02",
      "panel_number": 2,
      "page_number": 13,
      "panel_type": "silent",
      "camera": "extreme_close",
      "subject": "protagonist",
      "action": "looks_down",
      "background": "hands",
      "mood_direction": "still_detailing",
      "silence_guard": false,
      "dialogue": [],
      "sfx": [],
      "caption": null,
      "is_carrier_beat": true,
      "somatic_intention": "detail_as_anchor"
    },
    {
      "panel_id": "CH005_P13_PL03",
      "panel_number": 3,
      "page_number": 13,
      "panel_type": "silent",
      "camera": "wide",
      "subject": "environment",
      "action": "rains",
      "background": "dojo_roof_opening",
      "mood_direction": "world_responds",
      "silence_guard": false,
      "dialogue": [],
      "sfx": [],
      "caption": null,
      "is_carrier_beat": false,
      "somatic_intention": "environment_breath"
    },
    {
      "panel_id": "CH005_P13_PL04",
      "panel_number": 4,
      "page_number": 13,
      "panel_type": "action",
      "camera": "medium",
      "subject": "protagonist",
      "action": "stands",
      "background": "dojo_floor",
      "mood_direction": "world_return",
      "silence_guard": true,
      "dialogue": [],
      "sfx": [
        {
          "sfx_text": "rustle",
          "weight": "ambient"
        }
      ],
      "caption": null,
      "is_carrier_beat": false,
      "somatic_intention": "re_engagement"
    }
  ]
}
```

**QC Notes:**
- Panel 4 (page 12): Carrier beat preparation. Single line, whisper-capable. Silence_guard=true reduces emphasis.
- Panels 1–3 (page 13): Pure silence. No dialogue, no caption, no heavy SFX. Five-beat protocol: stillness → detail (extreme close on hands) → world (rain, wide shot) → return implicit.
- Panel 4 (page 13): First panel after silence. silence_guard=true. Ambient SFX only (rustle). No dialogue.
- Progression: information delivered by voice (lie revealed), silence processes rupture, environment mirrors psychological break, reader returns to page 14 without sermonizing.

---

## 13. Worked Example — High-Action Chapter [FIX 4]

**Context:** Chapter 5, protagonist vs. villain in climactic fight. Villain claims transcendence; protagonist power-up costs (simultaneous win + somatic loss). SFX carries emotional weight. Five-beat silence protocol embedded within combat.

```json
{
  "chapter_id": "CH005",
  "page_number": 8,
  "page_type": "high_action",
  "panels": [
    {
      "panel_id": "CH005_P08_PL01",
      "panel_number": 1,
      "panel_type": "dialogue",
      "camera": "two_shot",
      "subject": "protagonist|villain",
      "action": "face_off",
      "background": "crater_battlefield",
      "mood_direction": "confrontation_escalating",
      "silence_guard": false,
      "dialogue": [
        {
          "speaker": "villain",
          "bubble_type": "speech",
          "text": "You cannot defeat enlightenment itself."
        }
      ],
      "sfx": [],
      "caption": null,
      "is_carrier_beat": false,
      "somatic_intention": "seductive_lie"
    },
    {
      "panel_id": "CH005_P08_PL02",
      "panel_number": 2,
      "panel_type": "action",
      "camera": "close",
      "subject": "protagonist",
      "action": "charges",
      "background": "crater_battlefield",
      "mood_direction": "escalating_commitment",
      "silence_guard": false,
      "dialogue": [],
      "sfx": [
        {
          "sfx_text": "CRACK",
          "weight": "heavy"
        }
      ],
      "caption": null,
      "is_carrier_beat": false,
      "somatic_intention": "action_negates_teaching"
    },
    {
      "panel_id": "CH005_P08_PL03",
      "panel_number": 3,
      "panel_type": "reaction",
      "camera": "extreme_close",
      "subject": "protagonist",
      "action": "eyes_widen",
      "background": "none",
      "mood_direction": "cost_realized",
      "silence_guard": false,
      "dialogue": [],
      "sfx": [
        {
          "sfx_text": "CRACK",
          "weight": "heavy"
        }
      ],
      "caption": null,
      "is_carrier_beat": true,
      "somatic_intention": "power_costs_agony"
    },
    {
      "panel_id": "CH005_P08_PL04",
      "panel_number": 4,
      "panel_type": "silent",
      "camera": "medium",
      "subject": "protagonist",
      "action": "stands",
      "background": "crater_aftermath",
      "mood_direction": "still_damaged",
      "silence_guard": false,
      "dialogue": [],
      "sfx": [],
      "caption": null,
      "is_carrier_beat": true,
      "somatic_intention": "victory_holds_silence"
    },
    {
      "panel_id": "CH005_P08_PL05",
      "panel_number": 5,
      "panel_type": "silent",
      "camera": "wide",
      "subject": "environment",
      "action": "settles",
      "background": "crater_dust_clearing",
      "mood_direction": "still_world_responds",
      "silence_guard": false,
      "dialogue": [],
      "sfx": [],
      "caption": null,
      "is_carrier_beat": false,
      "somatic_intention": "environment_reflects_cost"
    }
  ]
}
```

**Analysis:**
- **Panel 1:** Villain coherence allowed. Teaching language ("enlightenment") present because villain speaks it. Somatic_intention="seductive_lie" flags this as false doctrine.
- **Panel 2:** Action invalidates teaching. No dialogue response; protagonist acts. SFX (CRACK) is medium-heavy, present-action weight.
- **Panel 3:** Carrier beat (is_carrier_beat=true). Protagonist hits, but cost is realized (eyes widen = physical toll). SFX (CRACK again) repeats; no escalation into "bigger" impact sound. Dialogue empty; somatic_intention="power_costs_agony" holds the truth.
- **Panel 4–5:** Silence protocol (2 silent panels) after high-action. Stillness (protagonist stands, damaged) + world (dust settles). No SFX, no dialogue. Reader experiences victory AND cost simultaneously without language summarizing it.

**QC Verification:**
- Villain dialogue is seductive (allowed). Somatic_intention contradicts it (internal_record shows "seductive_lie"). ✓
- Protagonist does not argue; acts. Villain's teaching disproven by consequence, not rhetoric. ✓
- Carrier beat (panels 3–4) contains zero emotional summary. Dialogue absent. SFX is restrained (CRACK, not CRACK CRACK SLASH BOOM). ✓
- Silence protocol: arrival (panel 3 cost realized) → stillness (panel 4) → world (panel 5) → return (implicit, next page). ✓
- reader_cold_read: Protagonist wins but is visibly harmed. Villain was seductive but wrong. No dharma vocabulary in protagonist language. ✓

---

## 14. System Prompt

**Injected at Chapter Writer initialization:**

```
You are the Chapter Writer for the AI Manga Dharma System. Your task is to convert story_architecture_handoff.json into manga language: dialogue, SFX, captions, and panel-by-panel scripts.

ROLE: Renderer, not storyteller. You execute the beats from Story Architect faithfully. You do not alter, summarize, or inject teaching language.

CORE RULES:
1. Silence is absolute. If page_type="silent", ALL panels are silent with zero text. If silence_guard=true, reduce dialogue to whisper-only, ambient SFX only.
2. Forbidden phrases: dharma vocabulary (enlightenment, karma, chakra, awakening, transcendence), emotional summary (I feel, I believe, my heart), teaching language (This teaches me, I realized my true nature).
3. Captions are highest-risk vector for dharma leakage. Describe observable world only; never narrate emotional truth or transformation.
4. Villain may be coherent and seductive. Villain must be proven wrong by consequence, not argument. If villain claims transcendence, somatic_intention audit will verify it's marked "seductive_lie."
5. Dialogue reflects subtext, not character's self-analysis. No monologues >3 lines without interruption.
6. SFX carries emotional weight without language. Silence better than CRACK for sensitive moments.
7. Carrier beats (is_carrier_beat=true in internal_record): your dialogue/SFX must be smaller, quieter, less emphatic. This gating is enforced by Transmission Splitter audit.

OUTPUT:
- Two versions: writer_handoff (for Visual/Lettering agents) and internal_record (for QC only).
- writer_handoff strips is_carrier_beat and somatic_intention.
- internal_record includes both for QC audit.

QUALITY GATES (auto-fail if triggered):
- Forbidden phrase scan: any dharma vocabulary, emotional summary, teaching language
- Silent purity: silent pages must have zero text
- End-hook exact match: must match story_architecture_handoff
- Monologue contradiction: villain's consecutive lines checked for logical coherence
- Cold read: can scene be understood without knowing somatic_intention? If no, rewrite.

If any gate fails, STOP and return error + offending content to human. Do not auto-correct.
```

---

## Appendix: JSON Schema Example (Complete Panel)

```json
{
  "panel_id": "CH005_P01_PL01",
  "panel_number": 1,
  "page_number": 1,
  "page_type": "standard",
  "panel_type": "dialogue",
  "camera": "medium",
  "subject": "protagonist",
  "action": "stands",
  "background": "street_intersection",
  "mood_direction": "tense_clarifying",
  "silence_guard": false,
  "dialogue": [
    {
      "speaker": "protagonist",
      "bubble_type": "speech",
      "text": "What do you want?"
    }
  ],
  "sfx": [
    {
      "sfx_text": "rustle",
      "weight": "ambient"
    }
  ],
  "caption": null,
  "end_hook": null,
  "is_carrier_beat": false,
  "somatic_intention": null
}
```

---

**SpiritualTech Systems · Chapter Writer Spec v1.1 · Confidential**
