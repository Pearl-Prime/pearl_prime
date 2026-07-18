# Scene Recognition Bank Spec

**Status:** Canonical  
**Date:** 2026-04-22  
**Authority:** This document. Subordinate to `specs/PHOENIX_V4_5_WRITER_SPEC.md` (§13.6 Assembly Collision Guardrails), `docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md` (§7), and `specs/EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md`.  
**Owner:** Pearl_Content + Pearl_Editor  
**Routing code:** `phoenix_v4/planning/injection_resolver.py` → `_find_scene_content(bank_type="recognition")`  
**Variety enforcement:** `BookSlotTracker` (same file) — pass one per book assembly

---

## 1. What a Recognition Bank Is

A recognition bank is the delivery system for the ONTGP **"Orient"** move at the opening of every book chapter. It fires as the HOOK opening beat — the first thing a listener hears in a chapter.

Its job is exactly one thing: make the listener think *"that's me."* Not explain. Not teach. Not inspire. Show the listener themselves in a micro-scene so specific to their life that the book earns the right to proceed.

**ONTGP "Orient"** = first 30 seconds. Physical or behavioral recognition. No interpretation. No diagnosis. No "you might be feeling…" — the listener should feel seen before they are told anything.

A recognition bank is distinct from:
- **Story atoms** (`story_atoms/`) — third-person named characters (Priya, Jordan). Recognition bank is always second-person "you."
- **Teacher atoms** (`HOOK/`) — voice of the teacher. Recognition bank has no authorial voice.
- **Global scene anchor bank** — neutral body-sensation moments. Recognition bank is situational (Slack, calendar, meeting, transit) with persona and topic specificity.

---

## 2. Canonical Schema

Each bank lives at:
```
config/content_banks/{topic}_{persona_slug}_scene_recognition_bank.yaml
```

Example: `config/content_banks/anxiety_genz_scene_recognition_bank.yaml`

The YAML root is a named list key (e.g. `anxiety_genz_scene_recognition`) containing variant records:

```yaml
{topic}_{persona_slug}_scene_recognition:

  - variant_id: {bank_prefix}_{topic_code}_{nnn}   # e.g. agsr_a_001 (anxiety genz scene recognition, anxiety, 001)
    slot_type: SCENE_RECOGNITION
    body: >
      {2–4 sentence 2nd-person present-tense micro-scene. No interpretation.}
    topic_allowlist: ["{topic}"]
    topic_blocklist: []
    persona_allowlist: ["{persona_id}"]
    frame_allowlist: ["secular", "nervous_system", "workplace", "clinical"]
    frame_blocklist: ["buddhist", "christian", "law_of_attraction", "manifestation", "spiritual_bypassing", "trauma_focused"]
    runtime_allowlist: ["quick_book_15m", "quick_book_30m", "standard_book_1h", "deep_book_2h", "deep_book_4h", "deep_book_6h"]
    band: 1                     # 1 = early chapter, 2 = mid, 3 = late; used for future band-aware routing
    intensity: 1                # 1–3; matches chapter emotional temperature
    mechanism_depth: 0          # always 0 for SCENE_RECOGNITION; no mechanism teaching here
    ontgp_move: orient          # always "orient" for recognition bank variants
    ei_v2_targets:
      embodiment: 0.7           # How grounded in physical/behavioral detail
      somatic_precision: 0.6    # How precise the body/sensation reference is (optional)
      specificity: 0.8          # How persona-specific (vs generic)
      engagement: 0.8           # How likely to create "that's me" recognition
    collision_family: {family}  # See §4 — prevents same-setting repeats within a book
    signature_phrases: ["{short phrase that makes this variant distinct}"]
    forbidden_terms: ["forty minutes", "has been open", "you have been looking at it", "task is open"]
    notes_for_selector: "{setting + key behavioral observation + what NOT to do}"
```

### 2.1 Required fields

| Field | Required | Notes |
|-------|----------|-------|
| `variant_id` | ✓ | Unique within bank. Format: `{bank_prefix}_{nnn}` |
| `slot_type` | ✓ | Always `SCENE_RECOGNITION` |
| `body` | ✓ | The prose content |
| `topic_allowlist` | ✓ | Non-empty; at least the topic this bank covers |
| `persona_allowlist` | ✓ | Non-empty; at least the persona this bank covers |
| `frame_blocklist` | ✓ | Always include the six blocked frames (see §6) |
| `ontgp_move` | ✓ | Always `orient` |
| `collision_family` | ✓ | See §4 — required for variety enforcement |
| `forbidden_terms` | ✓ | See §5 — at minimum the four generic markers |

### 2.2 Optional fields

| Field | Optional | Notes |
|-------|----------|-------|
| `band` | recommended | 1–3; enables future band-aware routing |
| `intensity` | recommended | 1–3; aligns with chapter emotional temperature |
| `ei_v2_targets` | recommended | Guides EI v2 quality scoring |
| `signature_phrases` | recommended | Helps collision scan (§13.6 of writer spec) |
| `notes_for_selector` | recommended | Writer guidance; stripped at runtime |
| `mechanism_depth` | optional | Always 0 for recognition banks |

---

## 3. Content Rules

### 3.1 Voice

Second-person present tense. Always.

```
✓  You opened the message, read it twice, and closed it.
✓  The Slack channel went quiet after your message, and you have reread your own words three times since.
✗  Elena didn't know she was doing it.          ← third person = STORY, not SCENE_RECOGNITION
✗  You might be feeling anxious today.          ← "might be" = tentative + names the emotion
✗  Most of us feel this way sometimes.          ← "us/we" = prohibited
✗  The nervous system does not distinguish...   ← mechanism = REFLECTION, not HOOK
```

### 3.2 The behavior, not the emotion

Show the behavior. The listener names the emotion themselves.

```
✓  Your jaw is still tight from whatever it said.          ← body behavior, no emotion label
✓  You have not closed the window yet.                     ← behavioral observation
✗  You feel anxious about the email.                       ← labels the emotion
✗  You are stressed about the meeting tomorrow.            ← labels the emotion
```

### 3.3 No setup, no payoff

Recognition variants do NOT offer interpretation, resolution, or comfort. They end in mid-air. The chapter that follows provides the turn.

```
✓  "...and your body has already started preparing for all three."  ← ends on observation
✗  "...but you know you can handle it."                            ← premature resolution
✗  "...which is why this book will help you."                      ← pivot to content
```

### 3.4 Length

- Minimum: 20 words
- Optimal: 25–50 words (2–3 sentences)
- Maximum: 70 words (TTS delivery; listeners hear each sentence once)

### 3.5 Sentence structure for TTS

- Short, declarative sentences.
- No em-dash lists inside sentences. No parentheticals. No footnote-style asides.
- Paragraph break (blank line in YAML `body`) only when a natural breath pause is intended.
- Avoid serial "and…and…and" constructions.

---

## 4. Collision Family Taxonomy

`collision_family` is the setting or trigger mechanism for the scene. Every variant must have exactly one.

The `BookSlotTracker` uses this field to enforce variety across a book's 12 HOOK slots — once a family appears, subsequent picks prefer other families until all are exhausted.

### Core families (required in every bank of 10+ variants)

| Family | Setting / trigger | Example signal |
|--------|------------------|----------------|
| `inbox_trigger` | Email or message inbox | Opening/rereading an email |
| `calendar_dread` | Calendar or schedule | Seeing overlapping commitments |
| `meeting_prep_dread` | Pre-meeting anticipation | Mind already in the debrief |
| `slack_silence` | Social/Slack ambiguity | No reply after sending a message |
| `home_office_unfinished` | Home workspace limbo | Work "done" but not closed |
| `transit_replay` | Commute / transit | Replaying the day on the train |
| `decision_body_lag` | Post-commitment doubt | Stomach hasn't agreed with the yes yet |
| `phone_screen_avoidance` | Device avoidance | Phone face-down, checking whether to flip it |
| `cafe_avoidance` | Third-space displacement | Can't start, changed location to delay |

### Extended families (for banks of 20+ variants)

| Family | Setting / trigger |
|--------|------------------|
| `task_list_paralysis` | Open task list, no clear start |
| `colleague_silence` | Coworker doesn't respond; room goes quiet |
| `end_of_day_hover` | Day officially over but still online |
| `morning_window` | First moment of day before phone; foreboding |
| `weekend_work_guilt` | Off-hours; work visible but supposedly not active |
| `approval_waiting` | Waiting on feedback/review from someone important |
| `video_call_off` | Camera off; visible self-monitoring |

### Persona-specific families (add for non-gen_z personas)

| Persona | Family | Setting |
|---------|--------|---------|
| `healthcare_rns` | `chart_handoff` | Shift change; patient status unclear |
| `healthcare_rns` | `break_room_debrief` | Can't stop thinking about a case on break |
| `healthcare_rns` | `supply_shortage` | Mid-task realization of missing resource |
| `corporate_managers` | `board_deck_review` | Scrolling deck the night before a presentation |
| `corporate_managers` | `direct_report_silence` | Team member visibly disengaged in 1:1 |
| `corporate_managers` | `budget_line_item` | Single line in a P&L that doesn't reconcile |
| `entrepreneurs` | `mrr_dashboard` | Revenue metric not trending right |
| `entrepreneurs` | `investor_email` | Reply slower than expected |
| `working_parents` | `school_notification` | Missed school notification during a meeting |
| `working_parents` | `evening_transition` | Work call bleeds into dinner |
| `first_responders` | `call_replay` | Replaying a call from earlier in the shift |
| `educators` | `parent_email` | Email from a parent that landed poorly |

---

## 5. Forbidden Terms

Every variant must list the four core forbidden terms, plus any persona-specific terms that would break character specificity.

### Universal forbidden terms (every bank)

```yaml
forbidden_terms:
  - "forty minutes"          # the generic v02 failure pattern
  - "has been open"          # same pattern
  - "you have been looking at it"  # same
  - "task is open"           # same
```

These exist because the original HOOK atom v02 ("The task is open. You have been looking at it for forty minutes.") was the canonical example of generic content that failed persona specificity. Any phrase with this structure (duration marker + passive description of a generic task) is blocked.

### Additional forbidden terms by persona

| Persona | Forbidden terms | Reason |
|---------|-----------------|--------|
| `healthcare_rns` | "productivity", "inbox zero", "Slack", "standup" | Wrong workplace context |
| `corporate_managers` | "hustle", "side project", "grind", "vibe check" | Register mismatch |
| `gen_z_professionals` | "office memo", "fax", "voicemail" | Anachronistic |
| All | "you are anxious", "you feel stressed", "your anxiety" | Names the emotion (see §3.2) |
| All | "it's okay", "you've got this", "breathe through it" | Premature resolution |

---

## 6. Frame Blocklist (all banks)

All banks must include this exact `frame_blocklist` on every variant:

```yaml
frame_blocklist:
  - buddhist
  - christian
  - law_of_attraction
  - manifestation
  - spiritual_bypassing
  - trauma_focused
```

Recognition bank variants are secular and somatic only. They describe observable behavior, not inner states requiring a spiritual or clinical frame.

---

## 7. Build Priority Matrix

| Priority | Persona × Topic | Status | Min variants | Notes |
|----------|-----------------|--------|--------------|-------|
| **P0** | `gen_z_professionals × anxiety` | ✅ Done | 40 | `anxiety_genz_scene_recognition_bank.yaml` |
| **P1** | `gen_z_professionals × burnout` | ◻ Not built | 20 | Same delivery context; adapt exhaustion/depletion triggers |
| **P1** | `gen_z_professionals × overthinking` | ◻ Not built | 20 | Cognitive loop variants; browser tabs, half-written messages |
| **P1** | `gen_z_professionals × shame` | ◻ Not built | 15 | Post-meeting replay; the thing they said; silence after a joke |
| **P2** | `healthcare_rns × anxiety` | ◻ Not built | 20 | Chart/handoff/break-room settings (see §4 extended families) |
| **P2** | `corporate_managers × anxiety` | ◻ Not built | 20 | Board deck / P&L / direct report settings |
| **P2** | `working_parents × anxiety` | ◻ Not built | 20 | School notification / evening transition settings |
| **P3** | `millennial_women_professionals × anxiety` | ◻ Not built | 20 | Hybrid between gen_z and corporate register |
| **P3** | `entrepreneurs × anxiety` | ◻ Not built | 20 | MRR dashboard / investor email settings |
| **P3** | `first_responders × anxiety` | ◻ Not built | 15 | Call replay / handoff settings |
| **P4** | All remaining personas × anxiety | ◻ Not built | 10 each | |
| **P5** | All personas × non-anxiety somatic topics | ◻ Not built | 10 each | |

**Minimum viable bank:** 10 variants minimum before routing activates. Below 10, the system falls back to the HOOK atom pool.

---

## 8. File Naming Convention

```
config/content_banks/{topic}_{persona_slug}_scene_recognition_bank.yaml
```

Where `{persona_slug}` uses underscores matching the persona_id exactly:

| persona_id | persona_slug in filename |
|------------|--------------------------|
| `gen_z_professionals` | `genz` (abbreviated) |
| `healthcare_rns` | `healthcare_rns` |
| `corporate_managers` | `corporate_managers` |
| `working_parents` | `working_parents` |
| `entrepreneurs` | `entrepreneurs` |
| `millennial_women_professionals` | `millennial_women` |

Multiple topics for the same persona may share a single file with separate list keys:

```yaml
anxiety_genz_scene_recognition:
  - ...

burnout_genz_scene_recognition:
  - ...
```

The `_load_scene_bank()` in `injection_resolver.py` reads all list values and filters by `topic_allowlist` + `persona_allowlist` at load time.

---

## 9. Routing and Fallback

### 9.1 Routing path

```
compose_section_packet(section_type="HOOK")
  → _find_scene_content(topic, persona_id, seed, repo_root, bank_type="recognition", slot_tracker=tracker)
    → _load_scene_bank(topic, persona_id, repo_root, "recognition")
      → reads anxiety_genz_scene_recognition_bank.yaml (or topic+persona equivalent)
      → filters by topic_allowlist + persona_allowlist
    → slot_tracker.pick(variants, seed, slot_type="scene_recognition")
      → hard-excludes already-used variant_ids
      → prefers least-used collision_family
      → falls back gracefully if all variants exhausted
```

### 9.2 Fallback chain

1. Matching recognition bank exists + has 10+ variants → **bank pick** (variety-enforced)
2. Bank exists but has <10 variants → **WARN** + fall back to enrichment slot content
3. No bank for this topic × persona combination → fall back to enrichment slot content
4. Enrichment slot content starts with `[CONTENT GAP:` → nothing appended for HOOK opening beat (template somatic text follows anyway)

### 9.3 BookSlotTracker threading

One `BookSlotTracker` instance must be created per book and passed to all `compose_section_packet()` calls for that book. Do not create a new tracker per chapter or per section.

```python
tracker = BookSlotTracker()   # once per book
for chapter in chapters:
    for section in sections:
        packet = compose_section_packet(..., slot_tracker=tracker)
```

The tracker is stateless between books — create a new instance for each book.

---

## 10. EI v2 Quality Gates for Recognition Bank Variants

Recognition bank variants fire at the ONTGP "Name" check position (sec 2, `name_start_frac: 0.12`). EI v2 should verify:

| Gate | Check | Expected |
|------|-------|----------|
| **Orient present** | sec 1 (HOOK) contains a 2nd-person situational scene, not a generic statement | PASS if `source` includes `scene_recognition` |
| **No emotion naming** | Body text does not contain "anxious", "stressed", "worried", "panicked" as applied to "you" | Regex check on HOOK text |
| **Persona specificity** | Collision family is in the persona's known-good family list | Cross-ref tracker slot_history |
| **Collision family spread** | No collision family appears more than twice in the first 6 chapters | Inspect `slot_tracker_variety.collision_family_counts` in word_budget.json |
| **Forbidden terms absent** | No `forbidden_terms` appear in any HOOK section | Regex check |

---

## 11. Writer Brief: How to Write Recognition Variants

### The test

After writing a variant, ask: "Would someone say 'that's me'?" If the answer is "maybe" or "I think so," the variant is not specific enough.

### The structure

```
[Setting + small specific detail]
[Behavioral observation — what the body or hands are doing]
[Optional: the gap — what is not happening, the open loop]
```

Examples of structure at work:

```
The calendar shows three things at the same time tomorrow morning,     ← setting + specific detail
and your body has already started preparing for all three.             ← behavioral observation (anticipatory body)
```

```
On the train you are not reading.                                      ← setting + what's NOT happening (open loop)
You are running through what happened at the end of the day,           ← behavioral observation
looking for the part you might have misread.                           ← the cognitive behavior
```

### What to avoid

| Pattern | Example | Why |
|---------|---------|-----|
| Named emotions | "You feel anxious" | Listener names the feeling; writer shows the behavior |
| Generic time markers | "for forty minutes" | Not persona-specific |
| Generic task descriptions | "the task is open" | Could be anything; not concrete |
| Resolution offers | "but you can handle this" | Premature turn |
| Second-guessing hedges | "you might be noticing" | Weak — write declaratively |
| Lists | "the email, the meeting, the report" | TTS reads flatly; use one concrete anchor |

### Persona registers

| Persona | Language register | Setting vocabulary |
|---------|------------------|-------------------|
| `gen_z_professionals` | Casual-precise. Contraction-light. No slang. | Slack, calendar invite, Notion, PR review, startup, remote desk |
| `healthcare_rns` | Clinical-familiar. Shift language. | Chart, handoff, break room, call light, patient name withheld |
| `corporate_managers` | Professional. Understated. | Board deck, P&L, direct report, one-on-one, executive briefing |
| `entrepreneurs` | Terse. Metric-aware. | MRR, runway, investor, pitch, Stripe dashboard |
| `working_parents` | Parallel-track. Time-compressed. | School notification, pickup, overlap, dinner, after-hours email |

---

## 12. Relationship to Other Systems

| System | Relationship |
|--------|-------------|
| `story_atoms/` (SCENE sections) | Third-person named characters. Recognition bank = second-person always. |
| `atoms/{persona}/{topic}/HOOK/CANONICAL.txt` | Legacy HOOK atom pool. Recognition bank replaces this for the opening beat in all cases where a bank exists. |
| `config/content_banks/global_scene_anchor_bank.yaml` | Fallback for `[INTEGRATION_SCENE_POINT]` (post-exercise release scenes). Recognition bank is topic+persona specific; anchor bank is neutral. |
| `bestseller_craft_gate.yaml` ONTGP | `orient_present: true` satisfied when recognition bank fires in sec 1. `name_start_frac` satisfied when story_planner fires a named character in sec 2. These are two separate structural requirements. |
| `EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md` | Catalog-level variety. Recognition bank + BookSlotTracker = within-book variety (these operate at different scopes). |
| `BookSlotTracker` | Enforces no-repeat and collision-family spread within a single book. One tracker per book assembly. |
