# Story-Craft Contract — Supportive Stories That Read Like Bestseller Stories

**Author:** Pearl_Research · **Date:** 2026-07-07  
**Status:** Spec + exemplars (writer-lane input; does NOT modify `story_atoms/`)  
**Audience:** Live ch5–12 writer lane, catalog atom authors, `story_atom_lint` extenders  
**Authority chain:** Subordinate to [PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) §4.3 STORY; extends [STORY_TYPES_AND_STRUCTURES.md](./STORY_TYPES_AND_STRUCTURES.md), [HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md), [GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md](./writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md)

---

## Executive diagnosis

The operator read is correct and the repo already measured the root cause:

| Finding | Source | Implication |
|---------|--------|-------------|
| **86% of catalog STORY variants classified `character_study`** | [STORY_TYPE_BACKFILL_FINDINGS_2026-07-03.md](./STORY_TYPE_BACKFILL_FINDINGS_2026-07-03.md) | The default story shape is **portrait-without-arc** — ambiguity and open endings without movement |
| Five-element rubric checks specificity, conflict, cost, pivot — **not want→choice→consequence** | [HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md](./HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC.md) | Atoms pass lint while reading flat; micro-stakes guide under-applied at the **beat-role** level |
| `belief_flip` pattern documented but not enforced | [PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md](../specs/PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC.md) §3 | Mid-band stories lack belief-failure-in-the-moment structure |
| Flagship ch1 turning_point scores high; **20/36 assigned beats score ≤2/6 on stakes checklist** | This audit (§2 below) | Mass-pass stories are still-lifes; ch1 gold bar exists but is not propagated |

**What our stories have:** embodiment (body states, environmental cues), persona-native specificity (Slack, standup, deck, calendar), social presence (manager, roommate, channel activity), third-person present texture.

**What they lack:** a **concrete want**, something **at risk**, a **decision point**, a **paid cost on the page**, and a **verifiable delta** between opening and closing state. Without these five, recognition/mechanism_proof/turning_point beats read as extra SCENEs — Priya picks the phone up, puts it down, picks it up.

**Secondary flagship drift (writer lane):** The approved ch1 chapter uses **Priya** exclusively (`artifacts/qa/ch1_12shape_preview_v4_20260705/complete_ch1.txt`). The deterministic plan for ch2–12 still selects **29/36 beats starring other names** (Marcus, Zoë, Aisha, etc.) from the legacy pool. Newer Priya-centric atoms (v18–v24) exist but are not yet wired into the plan. Character continuity and story craft must be fixed together.

---

## §1 — External craft digest (how bestsellers do 120–200 word supporting stories)

Sources are cited for transferable mechanics, not for prose imitation.

### Atomic Habits — James Clear

Clear opens chapters with a **vivid anchor story**, then states the principle ([MANUSCRIPTS framework analysis](https://manuscripts.com/write-like-a-thought-leader-james-clear-principles-framework/)). His marginal-gains anecdote (Dave Brailsford / British Cycling) demonstrates the transferable pattern:

- **Named agent** (Brailsford), not "a coach"
- **Quantified intervention** (1% improvements; heated overshorts; white-painted truck)
- **Before/after delta** (Olympic dominance; measurable performance shift)
- **Specificity as credibility** — numbers and object names signal research access

Clear's own quote: *"When explaining strategies, emphasize stories over patterns. People forget numbers and charts. Everyone remembers a great story."* ([jamesclear.com](https://jamesclear.com/quotes/when-researching-strategies-emphasize-patterns-over-stories-one-person-succeeding-means-nothing-100-people-succeeding-is-a-signal))

**Transferable mechanic:** Even a 150-word anecdote carries **one number or named object** and ends with a **world-verifiable change** — not an internal adjective.

### Brené Brown — functional vulnerability

Brown uses **functional vulnerability**: minimum story that earns trust, framed as evidence ([Draftly analysis](https://joindraftly.com/en/authors/brene-brown)). Vulnerability = uncertainty + risk + emotional exposure ([Lisa Cooper Ellison on Brown's definition](https://lisacooperellison.com/when-your-best-writing-feels-terrible/)).

**Transferable mechanic:** One moment of **social risk on the page** — something Priya could lose (status, belonging, accuracy) — shown in behavior, not labeled "vulnerable."

### Malcolm Gladwell — withheld information / tension slope

Gladwell structures nonfiction as **imperfect puzzles**: open on a person in a moment, leave one motive unclear, end the section with a question the reader must lean into ([MasterClass — Ketchup Conundrum](https://www.masterclass.com/articles/malcolm-gladwells-tips-for-structuring-a-story-like-the-ketchup-conundrum); [Draftly](https://joindraftly.com/en/authors/malcolm-gladwell)). He withholds information "for unreasonable periods" to create suspense in nonfiction ([MasterClass Moments](https://www.youtube.com/watch?v=CtRtwnoylaY)).

**Transferable mechanic:** **Recognition** beats can withhold the full cost until the last sentence — but something must be **at risk** from sentence two, not only observed.

### Charles Duhigg — cue / routine / reward loop

Duhigg's Pepsodent and Eugene Pauly vignettes follow **cue → routine → reward**, with the reward **visible in the world** ([Slate excerpt](https://slate.com/culture/2012/02/an-excerpt-from-charles-duhiggs-the-power-of-habit.html); [LitCharts Ch.2](https://www.litcharts.com/lit/the-power-of-habit/chapter-2-the-craving-brain-how-to-create-new-habits)). Eugene's story: named people, timestamps ("Within twenty-four hours"), temperature (105°), **paid cost** (memory loss; cannot recognize son).

**Transferable mechanic:** **Mechanism_proof** beats must show the pattern **paying a cost** — a missed moment, wrong routine, lost reward — not merely describing the loop.

### Bessel van der Kolk — case vignettes with cost and outcome

The Marilyn vignette: specific trigger (Michael's body at 2am), **explosive cost** (attack; partner flees), aftermath (humiliation; help-seeking), clinical frame ([psychotherapy.net excerpt](https://www.psychotherapy.net/perspectives/articles/the-body-keeps-the-score-brain-mind-and-body-in-the-healing-of-trauma/)).

**Transferable mechanic:** Trauma-adjacent self-help still uses **consequence in the social world** — someone leaves, a thread closes, a meeting moves on — not only internal sensation.

### Flash fiction / micro-fiction stakes craft

Flash fiction requires **focused conflict**, not vignette ([Gotham Writers Workshop](https://www.writingclasses.com/toolbox/ask-writer/what-is-flash-fiction)). Stakes = consequences of action/inaction ([Black Anvil Books](https://www.black-anvil-books.com/blog/showing-the-stakes-in-flash-fiction-and-short-stories)). Short-short structure: **desire → obstacle → resolution/revelation** ([flashfiction.net](http://flashfiction.net/2009/07/30/thursday-flash-craft-desire-narrative-structure-in-writing-the-short-short/)).

**Transferable mechanic:** 120–200 words is enough for **one want, one obstacle, one outcome** — not zero.

### Synthesis — the bestseller micro-anecdote checklist

| Mechanic | What bestsellers do | Our gap |
|----------|---------------------|---------|
| **Want** | Character pursues something concrete (send update, keep job, rest, belong) | 25% of flagship beats surface explicit want |
| **Risk** | Something could be lost — status, relationship beat, opportunity, accuracy | 14% |
| **Choice** | A decision point, not only reflex | 97% have verbs — but mostly **habit loops**, not decisions |
| **Cost** | Paid on the page — missed, declined, moved on, wrong notes | 39% |
| **Delta** | End state differs from open — verifiable in world | 56% |
| **Specificity** | Number, time, or named thing | Sparse outside ch1/ch7 |
| **Movement vs portrait** | Story **moves** through want→choice→consequence; scene **holds** a moment | 42% distinct from SCENE; 56% read as portrait |

---

## §2 — Flagship corpus scorecard (ch1–12 assigned beats)

**Method:** Read all 36 beats assigned by `artifacts/pearl_prime/standard_book/.../selected_content_variants.json`. Score six binary criteria: **Want**, **Risk**, **Choice**, **Cost**, **Delta** (verifiable world change), **≠SCENE** (movement not portrait). Scale 0–6.

**Anchor:** ch1 `turning_point` v08 (sick-day → meeting moved on without her) scores **5/6** — the operator's gold reference.

### Per-beat table

| Ch | Beat | Var | W | Wnt | Rsk | Chc | Cost | Del | ≠SCN | Score | Verdict |
|----|------|-----|---|-----|-----|-----|------|-----|------|-------|---------|
| 1 | recognition | v03 | 92 | ✓ | · | ✓ | ✓ | ✓ | ✓ | 4/6 | Portrait loop; cost=rumination not loss |
| 1 | mechanism_proof | v05 | 101 | ✓ | · | ✓ | · | ✓ | · | 3/6 | Spread to life; no paid cost |
| 1 | **turning_point** | **v08** | 130 | · | ✓ | ✓ | ✓ | ✓ | ✓ | **5/6** | **Gold bar** |
| 2 | recognition | v06 | 94 | · | · | ✓ | ✓ | ✓ | ✓ | 4/6 | Marcus; envy portrait |
| 2 | mechanism_proof | v06 | 126 | · | · | ✓ | · | · | · | 1/6 | **Flat** — meeting fog |
| 2 | turning_point | v09 | 130 | ✓ | · | ✓ | · | · | · | 2/6 | Feedback sent; weak delta |
| 3 | recognition | v10 | 121 | · | · | ✓ | ✓ | ✓ | ✓ | 4/6 | PTO doc portrait |
| 3 | mechanism_proof | v14 | 128 | · | · | ✓ | · | ✓ | · | 2/6 | Vacation scan |
| 3 | embodiment | v12 | 88 | · | · | ✓ | ✓ | · | ✓ | 3/6 | Handoff; no arc |
| 4 | recognition | v16 | 142 | · | · | ✓ | ✓ | ✓ | ✓ | 4/6 | Hallway pacing |
| 4 | mechanism_proof | v01 | 85 | ✓ | · | ✓ | · | · | · | 2/6 | PTO approved; no cost |
| 4 | turning_point | v11 | 129 | · | · | ✓ | ✓ | ✓ | ✓ | 4/6 | Lights down; soft |
| 5 | recognition | v14 | 118 | ✓ | · | ✓ | ✓ | ✓ | ✓ | 4/6 | |
| 5 | mechanism_proof | v08 | 43 | · | · | ✓ | · | · | ✓ | 2/6 | **Stub** — under 120w |
| 5 | turning_point | v14 | 104 | · | ✓ | ✓ | ✓ | · | · | 3/6 | |
| 6 | recognition | v01 | 80 | · | · | ✓ | ✓ | ✓ | ✓ | 4/6 | Under 120w |
| 6 | mechanism_proof | v09 | 154 | · | ✓ | ✓ | ✓ | ✓ | ✓ | 5/6 | Strong; wrong protagonist |
| 6 | embodiment | v02 | 108 | · | · | ✓ | · | ✓ | · | 2/6 | |
| 7 | recognition | v02 | 88 | · | · | ✓ | ✓ | · | · | 2/6 | Under 120w |
| 7 | **mechanism_proof** | **v20** | 113 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** | Rare full pass |
| 7 | turning_point | v03 | 118 | · | · | ✓ | · | · | · | 1/6 | **Flat** — shoulder note |
| 8 | recognition | v05 | 100 | · | · | ✓ | ✓ | · | · | 2/6 | Idea stolen; no movement |
| 8 | mechanism_proof | v10 | 146 | ✓ | · | ✓ | · | ✓ | · | 3/6 | Cancel drafts; no send |
| 8 | turning_point | v17 | 116 | · | · | ✓ | · | ✓ | · | 2/6 | Still "in it" — no choice |
| 9 | recognition | v07 | 59 | · | · | ✓ | · | · | ✓ | 2/6 | **Stub portrait** |
| 9 | mechanism_proof | v12 | 131 | ✓ | · | ✓ | · | ✓ | · | 3/6 | Car sitting |
| 9 | embodiment | v10 | 107 | · | · | ✓ | · | · | ✓ | 2/6 | Calendar block |
| 10 | recognition | v09 | 128 | · | · | ✓ | ✓ | ✓ | · | 2/6 | Rent math loop |
| 10 | mechanism_proof | v04 | 115 | · | · | ✓ | ✓ | · | · | 2/6 | #wins snub |
| 10 | turning_point | v01 | 104 | · | · | ✓ | · | ✓ | · | 2/6 | Banking app loop |
| 11 | recognition | v11 | 127 | ✓ | · | ✓ | ✓ | ✓ | ✓ | 5/6 | Strong; wrong protagonist |
| 11 | mechanism_proof | v11 | 149 | · | ✓ | ✓ | · | · | · | 2/6 | Tab spiral |
| 11 | turning_point | v02 | 110 | · | · | ✓ | · | · | · | 1/6 | **Flat** — posture note |
| 12 | recognition | v13 | 120 | · | · | · | · | · | · | 0/6 | **Flat** — prep loop |
| 12 | mechanism_proof | v21 | 110 | · | · | ✓ | · | · | · | 1/6 | Demo "yeah" |
| 12 | embodiment | v05 | 117 | ✓ | · | ✓ | · | · | · | 2/6 | Trip chat drafts |

### Aggregate

| Metric | Result |
|--------|--------|
| Beats scoring **≥4/6** | 12/36 (33%) |
| Beats scoring **≤2/6** (flat/stub) | 20/36 (56%) |
| Beats scoring **6/6** | 1/36 (ch7 mechanism_proof v20) |
| **Want** present | 9/36 (25%) |
| **Risk** present | 5/36 (14%) |
| **Cost** paid on page | 14/36 (39%) |
| **Verifiable delta** | 20/36 (56%) |
| **Distinct from SCENE** | 15/36 (42%) |
| Priya as actor (assigned) | 7/36 (19%) |
| Under 120 words | 4/36 |

**Pattern:** `character_study` collapse → three beats per chapter that **observe** Priya (or Marcus/Zoë) in states rather than **moving** her through stakes. ch1 `turning_point` and ch7 `mechanism_proof` prove the bar is reachable within the envelope.

---

## §3 — Story-Craft Contract (per-beat-type spec)

### Global envelope (unchanged)

- 120–200 words
- Opens with **"The"** (anchored flagship convention)
- Third-person present
- Exactly **one named actor: Priya** (no second named characters; role references OK: "her manager," "the skip-level")
- No tidy self-help resolution; world-evidenced outcome OK

### SCENE vs STORY — the distinct-from-SCENE rule

| Slot | Cognitive job | Shape | Must NOT |
|------|---------------|-------|----------|
| **SCENE** | Embodied still moment **before** action | Sensory hold; pre-decision; body ahead of mind | Resolve; pay cost; complete arc |
| **STORY** | **Movement** through want → choice → consequence | Verbs that change the situation; delta in world | Repeat SCENE's stillness; portrait-only looping |

**Lint signal:** A STORY beat that lacks both (a) a **world-outcome sentence** and (b) a **choice verb** (`sends`, `closes`, `deletes`, `stays`, `does not`) is likely a SCENE duplicate.

---

### Beat type: `recognition`

**Job:** Pattern surfaces **with a cost glimpsed** — not just observed behavior; something **almost lost**.

| Floor | Requirement |
|-------|-------------|
| **Want** | Priya wants something specific in-scene (reply, accuracy, rest, belonging, competence) |
| **Risk** | One concrete thing at stake (deadline, relationship beat, reputation, opportunity) — **glimpsed**, not fully paid |
| **Choice** | At least one micro-decision (send anyway, check again, default answer, pick phone up) |
| **Cost glimpse** | Near-miss or small loss shown: typo sent, four minutes unanswered, wrong default chosen |
| **Specificity** | ≥1 number OR time OR named object (11:47pm, four minutes, Thai place, 102.4°) |
| **≠SCENE** | Situation **changes** (message sent, phone picked up twice, suggestion made) — not only body state |

**Anti-pattern:** "She feels X. She notices Y. She is aware Z." (portrait)

**Model:** ch1 recognition v03 is close but needs sharper **risk glimpse** (what sending could cost besides rumination).

---

### Beat type: `mechanism_proof`

**Job:** Pattern **pays a concrete cost on the page** — missed moment, relationship beat, opportunity — shown with number/time/name of thing lost.

| Floor | Requirement |
|-------|-------------|
| **Want** | Priya wants normal function (focus, vacation, dinner opinion, meeting contribution) |
| **Mechanism visible** | Pattern interferes with that want **in action** |
| **Cost (paid)** | Documented loss: wrong doc opened, section skipped, notes already wrong, vacation hour lost to Slack, question she cannot answer |
| **Specificity** | ≥1 number/time/name anchoring the cost |
| **Delta** | End shows pattern's tax: "nineteen minutes," "notes are not hers," "urgent thread was not urgent" |
| **≠SCENE** | Cause→effect chain, not only somatic description |

**Anti-pattern:** "She is on a call and not tracking" without **what the call cost her**.

**Model:** ch7 mechanism_proof v20 (6/6) — activation before performance, tremor on camera, hard part named.

---

### Beat type: `turning_point`

**Job:** A **choice** against the pattern + **changed outcome with evidence** — world responds differently; delta stated in world, not adjectives.

| Floor | Requirement |
|-------|-------------|
| **Choice** | Priya chooses **against** default pattern (closes doc unsaved, sends shorter message, does not draft follow-up, leaves phone on nightstand) |
| **Risk** | Real downside if choice fails (meeting derailed, coverage incomplete, reputation hit) |
| **Outcome evidence** | World response: "four replies," "threads resolved without her," "meeting moved forward anyway," "did not need the follow-up" |
| **Delta sentence** | Explicit before/after in world terms — not "she felt better" |
| **Specificity** | ≥1 timestamp or count in outcome block |
| **≠SCENE** | Post-choice time jump OK (that night → morning) |

**Anti-pattern:** Somatic observation (shoulders, headache, chair height) without choice + world response.

**Model:** ch1 turning_point v08 (5/6) — **the acceptance test for the book**.

---

### Beat type: `embodiment` (ch3, ch6, ch9, ch12 third slot)

When the third STORY slot is `embodiment` rather than `turning_point`, apply **turning_point-lite**: a **small choice** + **body delta** (loosened jaw, shoulders drop one inch) — still movement, not pure hold.

---

### Writer checklist (human bar + lintable subset)

**Human read (operator Layer-4 bar — not automated):**
- [ ] Would a bestseller reader lean forward?
- [ ] Does the beat do a job the SCENE before it did not?
- [ ] Is there a line someone would underline?

**Structural (lintable — promote to soft gate):**

| Check | Code | Beat types |
|-------|------|------------|
| Word count 120–200 | `STORY_LENGTH` | all |
| Opens with "The" | `STORY_THE_START` | anchored flagship |
| Named actor = Priya only | `STORY_SINGLE_ACTOR` | anchored flagship |
| Contains `\d` or time pattern | `STORY_SPECIFICITY_ANCHOR` | all |
| Contains choice verb from closed set | `STORY_CHOICE_VERB` | all |
| Contains outcome/cost lexeme | `STORY_OUTCOME_LEXEME` | mechanism_proof, turning_point |
| Temporal delta marker (Then/After/In the morning/By) | `STORY_TEMPORAL_DELTA` | turning_point |
| Not portrait-only (state verbs ≤ threshold without choice) | `STORY_PORTRAIT_COLLAPSE` | recognition, mechanism_proof |

**Do NOT automate:** prose quality, emotional register, persona specificity score — those stay human.

---

## §4 — Exemplars (before / after)

Three live flat beats rewritten to Contract. **Spec only — not written to banks.**

Constraints honored: Priya only, "The" start, 120–200w, no second named characters.

---

### Exemplar A — `recognition` (was ch12 v13, 0/6)

**BEFORE** (Leo, portrait prep loop — no want/risk/cost):

> Leo is in a conference bathroom stall eleven minutes before the networking mixer starts. He ran cold water over his wrists at the last conference, at the team kickoff in January, before two Zoom presentations he did from his own apartment. The cold water is not helping now either. He reads his list of three talking points on his phone. He goes out at the seven-minute mark.
>
> The first five minutes of the mixer he shakes four hands. He remembers a name. He asks a follow-up question. The second conversation runs twelve minutes and ends with a LinkedIn request. He is very good at this. The bathroom was nine minutes ago and is not visible from where he is standing.

**AFTER** (Contract — want: get through mixer without visible panic; risk: being seen frozen; cost glimpse: almost late):

> The networking mixer starts in eleven minutes and Priya is still in the bathroom stall with the cold water running over her wrists — the same trick she used before the January kickoff and two Zooms that worked until they didn't. She reads her three talking points on her phone. Her hands are not steady enough to put it away cleanly. She could stay until someone knocks. She could walk out at the seven-minute mark like last time and hope nobody noticed how long she was gone.
>
> She walks out at the six-minute mark instead. The room is already loud. She shakes two hands, loses the third person's company name mid-sentence, and fills the gap with a question she did not plan. The answer runs long. She laughs at the right moment anyway. By minute twelve she has a LinkedIn request and a dry mouth and the distinct sense that she has performed competence she does not feel. Nobody mentions the bathroom. She keeps the talking-points note open in her pocket anyway, just in case the next conversation goes wrong.

**Delta felt:** Reader gets want (survive mixer), risk (visible delay), choice (exit at 6 not 7), cost glimpse (lost company name), specificity (11/6/12 minutes), movement.

---

### Exemplar B — `mechanism_proof` (was ch2 v06, 1/6)

**BEFORE** (Marcus, meeting fog — no paid cost):

> Marcus is on a call. The project lead is explaining the revised timeline and he is looking at his own hands on the keyboard and they are not moving. He has been in this meeting for nineteen minutes and he has not typed anything and he is not sure he has understood anything said in the last four of those minutes and he cannot make himself care enough to scroll back. He types "sounds good" in the chat at the moment that seems right. The project lead says his name, asking for his section update. He opens the wrong doc. He opens the right one. He reads the first line aloud and his voice is steady and he does not recognize the person it belongs to.

**AFTER** (Contract — cost paid on page):

> The revised timeline call has been running nineteen minutes when the project lead asks for Priya's section update. She has not typed since minute four. She typed "sounds good" in the chat eleven minutes ago when the moment seemed right and she is now realizing she cannot reconstruct what she agreed to. She opens the wrong doc first — last quarter's deck — and loses eight seconds she does not have while three faces wait on her tile.
>
> She finds the right doc. She reads the first slide aloud. Her voice is steady. The second slide is the one she rewrote yesterday and did not save to the shared folder. The version on screen still says the launch is March 14. The lead says, "I thought we moved that." Priya says she will follow up offline. The thread after the call has four questions tagged to her. She answers two from memory and leaves two unanswered until 6pm, when both have already been resolved by someone else with less accurate numbers. The meeting moved on. Her section did not land. That is the cost of nineteen minutes of looking attentive while nowhere on the call.

**Delta felt:** Mechanism (scanning/dissociation) pays — wrong date, unanswered tags, section failed to land.

---

### Exemplar C — `turning_point` (was ch7 v03, 1/6; gold = ch1 v08)

**BEFORE** (Jordan, somatic portrait — no choice, no world outcome):

> Jordan's shoulders have been at the wrong height for so long that he notices them now only when someone mentions it. His desk chair is not the right height for the desk. He adjusted it once and it drifted back. By 2pm every day a specific band of tension runs from the base of his skull to his right shoulder blade. He has a note in his phone that says "stretching" from November. He opens the note sometimes and does not read it. The headache that starts at 3pm is the same headache it was last Tuesday. He drinks more water and it doesn't help and he drinks more water.

**AFTER** (Contract — choice against pattern + world evidence):

> The 2pm headache starts on schedule and Priya opens the stretching note she saved in November — the same note she has opened four times without doing the thing. Her shoulders are already at the wrong height. She could push through the next call the way she did last Tuesday and the Tuesday before that. The deck review is in twenty-six minutes. She closes the laptop instead.
>
> She sets a timer for four minutes — not to fix the headache, just to put her feet flat and let her shoulders drop without an audience. At 2:09 she joins the call two minutes late with her camera on and no apology speech. The first slide loads. She asks one clarifying question she would normally skip to avoid taking up space. The lead answers. Nobody mentions the two minutes. The headache is still there at 2:40, but it is not running the meeting. Afterward she does not reopen the deck to pre-edit her comments. She puts the phone face-down and the thread continues without her for the rest of the hour. That is not recovery. It is the first hour in a week where the pattern did not get the last word.

**Gold reference (ch1 v08 — do not rewrite; emulate):**

> Priya's temperature is 102.4 and she opens a new doc anyway… She closes the doc without saving… She sends it… In the morning there are four replies… Two threads that resolved without her. The roadmap sync happened… They are not the notes she would have written. The meeting moved forward anyway.

---

## §5 — Handoff plan

### A. Live ch5–12 writer lane (immediate)

**Cheapest path — adopt checklist before mass pass completes:**

1. **Remaining stories (ch5–12 not yet landed):** Write directly to §3 Contract + writer checklist. Use v18–v24 Priya atoms as **texture reference**, not copy source.
2. **Already-landed flat beats:** Targeted revision list (priority = ≤2/6 scores):

   | Priority | Ch | Beat | Var | Score |
   |----------|-----|------|-----|-------|
   | P0 | 12 | recognition | v13 | 0/6 |
   | P0 | 2 | mechanism_proof | v06 | 1/6 |
   | P0 | 7 | turning_point | v03 | 1/6 |
   | P0 | 11 | turning_point | v02 | 1/6 |
   | P0 | 12 | mechanism_proof | v21 | 1/6 |
   | P1 | 5 | mechanism_proof | v08 | 2/6 (43w stub) |
   | P1 | 9 | recognition | v07 | 2/6 (59w stub) |
   | P1 | 6 | recognition | v01 | 4/6 but 80w |
   | P1 | 7 | recognition | v02 | 2/6, 88w |

3. **Character continuity:** Rewrites must **re-home to Priya** even when the plan still points at legacy variants (Marcus/Zoë/etc.). Do not wait for plan re-index — prose authority is the approved ch1 chapter.
4. **Acceptance test per beat:** Side-by-side read against ch1 `turning_point` v08. If the beat could swap with the chapter SCENE without the reader noticing, it fails.

### B. `story_atom_lint` extension (catalog — soft gate)

Extend [phoenix_v4/quality/story_atom_lint.py](../phoenix_v4/quality/story_atom_lint.py) per [STORY_TYPE_ENFORCEMENT_SCOPE_2026-07-03.md](./STORY_TYPE_ENFORCEMENT_SCOPE_2026-07-03.md) Phase 1+:

| Phase | Addition | Severity |
|-------|----------|----------|
| **Now** | `STORY_SPECIFICITY_ANCHOR` — require `\d` or `\b\d{1,2}:\d{2}\b` or time word + number | WARN |
| **Now** | `STORY_CHOICE_VERB` — closed set from Contract | WARN |
| **Now** | `STORY_OUTCOME_LEXEME` for `mechanism_proof` / `turning_point` paths | WARN |
| **Now** | `STORY_TEMPORAL_DELTA` for `turning_point` | WARN |
| **Now** | `STORY_PORTRAIT_COLLAPSE` — state-verb density without choice | WARN |
| **Now** | `STORY_SINGLE_ACTOR` for `story_atoms/*/anchored/**` — Priya-only | FAIL (anchored) |
| **Phase 2** | Wire WARN bundle into Drift detectors (report-only 1 sprint) | WARN |
| **Phase 3** | Promote to soft BLOCK on anchored flagship paths after writer lane green | BLOCK |

**Explicitly NOT gated:** prose quality metrics, LLM scoring, persona specificity score (stays human QA per Golden Phoenix guide).

### C. Story-type enforcement interaction

The 86% `character_study` tag is **correct classification of current shape** — not mis-tagged. Fixing craft may re-type some beats to `atmospheric` (recognition hold) or keep `character_study` but with **movement inside the type**. Do not re-tag until post-rewrite; classification follows structure.

### D. Success criteria for this lane

- [ ] Writer lane confirms Contract received before ch10–12 mass pass
- [ ] P0 beats revised to ≥4/6 on checklist
- [ ] Full-book read: STORY slots distinguishable from SCENE slots without being told
- [ ] Layer-4 blind read: stories no longer cited as "flat" failure mode

---

## §6 — What this doc does NOT do

- Does **not** edit `story_atoms/` (writer lane owns banks)
- Does **not** touch plan YAML or pipeline indexing
- Does **not** propose prose-quality metric tuning
- Does **not** claim corpus fixed — specs and proves the bar only

---

## References

- Internal: STORY_TYPES_AND_STRUCTURES, STORY_TYPE_BACKFILL_FINDINGS, HIGH_IMPACT_STORY_ATOM_UPGRADE_RUBRIC, GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE, NARRATIVE_TENSION_VALIDATOR, PHOENIX_DEEP_RESEARCH_INTEGRATION_SPEC §3, STORY_TYPE_ENFORCEMENT_SCOPE
- External: Clear (Atomic Habits marginal gains, jamesclear.com); Brown (functional vulnerability, Draftly / Cooper Ellison); Gladwell (MasterClass, Draftly); Duhigg (Slate, LitCharts); van der Kolk (psychotherapy.net); flash-fiction stakes (Black Anvil, Gotham, flashfiction.net)

---

*story-craft-specced=docs/STORY_CRAFT_CONTRACT_2026-07-07.md*
