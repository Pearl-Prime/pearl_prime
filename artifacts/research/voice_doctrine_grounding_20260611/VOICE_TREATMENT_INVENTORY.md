# Voice Treatment Inventory — Author-First + Wrapper Voice Doctrine Grounding

**Authority (provisional):** grounding input for the orchestrator's bestseller fit-plan spec **#5**. Not itself a governing spec — §3 becomes the canonical voice-zone table only when spec #5 ratifies it and the operator confirms.
**Date:** 2026-06-11
**Author:** Pearl_Prime (Phoenix Omega) — Tier 1 (operator present: Ahjan)
**Status:** Read-only audit. One doc. Parallel-safe. Touches no config, no `teacher_wrapper.py`, no bestseller spec, no hot coordination file, no open PR.
**Evidence book:** `/tmp/pearl_prime_qa_book_20260611_clean/book.txt` — `anxiety × gen_z_professionals × ahjan`, 12 chapters / 1486 lines (most-recent clean render). Template: `config/source_of_truth/book_templates/anxiety_gen_z_professionals_overwhelm_v1.yaml`.

**Extends (does not redo):** #1509 `research/bestseller-pattern-fit-20260611` →
`artifacts/research/bestseller_pattern_fit_20260611/OUR_SYSTEM_VS_PATTERNS_GAP.md`. #1509 **diagnosed** F5 ("voice fragmentation") and named the missing fix verbatim — *"no voice/slot zoning"* (its gap-table) and root cause C2: *"the overlay waterfall lets one voice bleed into a slot it shouldn't own."* This doc **supplies that zoning** (the §3 table), **quantifies F5 in a real book** (§2), and **adds the genuinely-new fourth voice** the operator's clarification surfaces — the *scientist* — as a ready-to-formalize wrapper (§4) + lint (§5). #1509 named only consultant/teacher/Brené; the operator adds *scientist*.

**Aligns with (must not touch):** the in-flight **doctrine-stitch PR** `agent/pearl-prime-doctrine-intro-stitch-20260611` (worktree `/Users/ahjan/pp_doctrine_wt`), which owns `phoenix_v4/rendering/teacher_wrapper.py` and is fixing the dangling-teacher-lead-in render. The science engine in §4/§6 **reuses that PR's hardened `join_wrapped` helper** (principle 9 — reuse, don't reinvent).

---

## §1 — The doctrine restated (author-first + wrappers)

**One voice owns the book: the AUTHOR.** Their personality, their view, their second-person address to the reader. Everything the reader hears is the author narrating, analyzing, or addressing them.

**Teacher mode's premise is author-first by construction.** It is **not** Ahjan teaching. It is a fictional **author** (the pen-name / EI profile — see `docs/PEN_NAME_AUTHOR_SYSTEM.md`, profiles `somatic_companion | research_guide | elder_stabilizer`) who **studied Ahjan's books, teachings, and videos** and now **references** them. The author says *"What I learned from Ahjan is…"*, *"Ahjan's teaching shows…"* — the author never dissolves into the teacher.

**The author never becomes the teacher, and never becomes the scientist.** Both are borrowed authorities. Borrowed authority is only admissible **wrapped** — i.e. introduced, owned, and handed back by the author's own voice:

| Borrowed authority | Wrapper system | Author stance |
|---|---|---|
| **TEACHER** (Ahjan / tradition / doctrine) | existing `teacher_wrapper` (`config/catalog_planning/teacher_wrapper_templates.yaml`) | author references Ahjan; Ahjan never speaks first-person |
| **SCIENCE** (neuroscience / physiology / research) | **NEW `science_wrapper`** (drafted §4; spec #5 creates the file) | author references research; the clinic never speaks in its own cold voice |

**The failure mode (F5).** Any teacher or scientific content that appears **without a wrapper** is a raw voice-shift — the reader is dropped, mid-paragraph, into a voice that is not the author's. Stack two or three of these and you get #1509's F5 verbatim: *"Am I reading Brené Brown? A Buddhist teacher? A management consultant?"* — to which this book adds a fourth: **a clinician.** (Closely related: #1509 **F8**, "Ahjan-as-generic-Buddhist" — doctrine so generic it reads as anonymous scripture rather than this author's specific teacher.)

**The rule, stated for enforcement:** *voice/person is bound to slot-type; borrowed-authority content is admissible only behind its wrapper.* §3 is that binding; §5 enforces it.

---

## §2 — Un-wrapped voice-shift audit (real-book evidence, quantified)

Read end to end. **29 hard un-wrapped voice-shifts across 12 chapters**, in three classes, **plus** the systemic dangling-teacher-lead-in render that the doctrine-stitch PR already owns (counted separately, not in the 29).

> **Headline:** **Class A — 14** science cold-shifts · **Class B — 8** broken teacher wrappers · **Class C — 7** un-framed third-party / scripture = **29**. Every one of the 12 chapters contains at least one.

### Class A — SCIENCE cold-shifts (the genuinely-new finding) — 14 instances

**Pattern:** after every practice, a "debrief" block drops into a **third-person clinical voice** that names physiological mechanism with **no author frame** — not first-person author, not the second-person reflective beat that REFLECTION requires. Source: the `aha_noticing` post-practice debrief bank (`SOURCE_OF_TRUTH/exercises_v4/aha_noticing_phoenix_standard.yaml`), emitted un-wrapped. (Distinct from the *short warm closer* `_post_practice_validation_sentence` in `phoenix_v4/rendering/chapter_composer.py:2059` — "Whatever you noticed is enough" — which is already in good author voice and is **not** a violation.)

This is not merely a doctrine violation — it **already breaks the REFLECTION spec's own ceiling** (`specs/PHOENIX_V4_5_WRITER_SPEC.md` §4.4: *"Max 2 mechanism terms per reflection," "No rhetorical questions / statement-based only"*). Each block below carries 3–6 mechanism terms in a cold register.

| # | Ch | Line | After practice | Raw cold-voice excerpt | Cold mechanism terms |
|---|----|------|----------------|------------------------|----------------------|
| A1 | 1 | 147 | Enough-ness affirmations | "Nasal airflow regulates **nitric oxide production** and improves **oxygen efficiency**… It's **optimization**. Your system **recalibrated** when the entry point shifted." | nitric oxide, oxygen efficiency, optimization, recalibrated, overactivated |
| A2 | 2 | 279 | sensory orientation | "If your gaze softened, **peripheral awareness** may have widened. Narrowed vision often accompanies **threat detection**. Softening the eyes signals safety." | peripheral awareness, threat detection, scanning |
| A3 | 3 | 401 | body scan / countdown | "…that indicates reduced **forward guarding**. Stress often shortens the **posterior chain** subtly… Reduced effort lowers **internal alarm signaling**." | posterior chain, forward guarding, alarm signaling |
| A4 | 4 | 534 | breath-pause | "…chronic stress often anchors in the **upper trapezius**. When shoulders drop, the body reduces **protective bracing**… posture influences perception." | upper trapezius, protective bracing, vigilance |
| A5 | 5 | 626 | settling (4-2-6) | "**Heart rate variability** increases when inhale and exhale are balanced. That balance stabilizes **internal signaling**." | heart rate variability, internal signaling |
| A6 | 5 | 643 | fist / release | "The double inhale increases **oxygen intake**, and the long exhale reduces **carbon dioxide buildup** linked to anxiety spikes… your stress was partly **chemical**." | oxygen intake, CO₂ buildup, chemical |
| A7 | 6 | 796 | jaw / shoulder | "Pushing into a stable surface engages **large muscle groups**. Large muscle engagement can **discharge accumulated tension**." | large muscle groups, discharge, grounding-through-exertion |
| A8 | 7 | 892 | heaviness / chair | "Exhalation directly activates **calming pathways**. Many stress states overemphasize inhale — bracing for impact. You reversed that ratio." | calming pathways, inhale-bracing ratio |
| A9 | 8 | 956 | feet / contact | "Stress narrows awareness upward toward thought. Redirecting attention downward **redistributes awareness**… Grounding is not metaphorical. It is **sensory**." | awareness redistribution, constriction |
| A10 | 9 | 1052 | emotional completion | "When attention is precise, the body organizes itself differently… **Attention itself can alter muscle tone**. You just witnessed that effect." | muscle tone, sensation precision |
| A11 | 9 | 1069 | three-point press | "Rocking introduces predictable motion. Predictability reduces **defensive activation**… **Synchronization** often reduces **internal fragmentation**." | defensive activation, synchronization, internal fragmentation |
| A12 | 10 | 1180 | spine stacking | "If the chest feels more open, that suggests **contraction eased**. Stress often pulls shoulders inward defensively… it reflects **mechanical change, not mindset change**." | contraction, mechanical-not-mindset |
| A13 | 11 | 1344 | palming | *(repeat of A11)* "Rocking introduces predictable motion. Predictability reduces defensive activation…" | *(same)* |
| A14 | 12 | 1480 | thought observer | *(repeat of A1)* "Nasal airflow regulates nitric oxide production and improves oxygen efficiency…" | *(same)* |

**Why each breaks author-first:** there is no "I" and no "you-as-experiencer" — the sentence subject is a body part or a gas ("Nasal airflow regulates…", "Heart rate variability increases…"). The author has left the room and a physiology lecturer is talking. **The fix (per instance):** prepend an author-owned `science_wrapper` lead-in that flows *inline* into the mechanism, e.g. *"And here's what your body just did, if you want the mechanism — nasal breathing lifts nitric oxide, and…"* The clinical content survives; the **voice** returns to the author. (Draft phrases: §4.)

**Secondary (embedded science, 3 more, not in the 29 count — flagged for completeness):**
- Ch7 L887 (EXERCISE intro): "…stimulates the **vagus nerve**, which runs from your brainstem to your gut and controls your rest-and-digest response. The effect is **measurable**." (+ L883 "Sound vibration reaches a nerve…")
- Ch1 L120 (REFLECTION transition): "The body responds to prediction with the same **chemistry** it uses for actual danger."
These are shorter and more woven, but still cold register; the §4 `exercise_rationale` variant covers the vagus case.

### Class B — broken TEACHER wrappers — 8 instances

The Ahjan content is *meant* to be wrapped (a lead-in like "What Ahjan keeps pointing toward is…"). Two render failures leave the doctrine **unframed**:

**B-orphan (5): the wrapper truncated to a dangling preposition** — the reader sees a sentence fragment with no subject floating above a spiritual teaching:

| # | Ch | Line | Orphan fragment (verbatim) | What's missing |
|---|----|------|----------------------------|----------------|
| B1 | 6 | 660 | "and somatic approach…" | entire "Drawing on Ahjan's mindfulness…" head |
| B2 | 7 | 871 | "and somatic approach…" | same |
| B3 | 8 | 909 | "and somatic approach…" | same |
| B4 | 8 | 937 | "and somatic approach…" | same |
| B5 | 9 | 1029 | "and somatic approach…" | same |

**B-missing-name (3): the wrapper rendered with an unfilled teacher token** — "Sit with **\_\_** long enough and one thread emerges…" (the `{TEACHER_NAME}`/lineage slot dropped, so the variant resolved without its subject):

| # | Ch | Line | Rendered (verbatim) | Should read |
|---|----|------|---------------------|-------------|
| B6 | 6 | 738 | "Sit with long enough and one thread emerges…" | "Sit with **Ahjan's** [lineage] long enough…" |
| B7 | 10 | 1090 | "Sit with long enough and one thread emerges…" | same |
| B8 | 10 | 1157 | "Sit with long enough and one thread emerges…" | same |

**Why these break author-first (hardest cases):** with the head truncated, the doctrine block that follows (e.g. L1159 *"Hatred does not cease by hatred, but only by love; this is the eternal rule"*) reads as **anonymous scripture** — no author, no Ahjan, no frame at all. This is F5 at its most acute *and* F8 (generic-Buddhist). **Fix:** the truncation/empty-slot is a wrapper-resolution bug; the **lint** (§5) must flag any line that is *only* a wrapper fragment (dangling preposition, ellipsis-with-no-head, or unresolved `{TOKEN}`).

### Class C — un-framed third-party authorities + orphaned scripture — 7 instances

**C-thirdparty (3): a named outside authority appears with no wrapper at all** — a *fifth* voice, beyond even Ahjan:

| # | Ch | Line | Verbatim | Issue |
|---|----|------|----------|-------|
| C1 | 2 | 187 | "**Maté** would name it cleanly: a sane response to a setup…" | Gabor Maté dropped in raw; not in teacher registry, not author-framed |
| C2 | 4 | 446 | "**Foo's line** keeps surfacing for me here: both things are true." | "Foo" — un-framed; also reads as an **unfilled placeholder token** (double bug) |
| C3 | 5 | 563 | "**Foo's word** is right here: both." | same |

**C-scripture (4): a parable/aphorism fragment with no narrative container:**

| # | Ch | Line | Verbatim | Issue |
|---|----|------|----------|-------|
| C4 | 2 | 258 | "Now, put this salt into a cup of water and drink it." | salt-koan fragment; orphaned imperative, no "Ahjan tells the story of…" frame |
| C5 | 5 | 605 | "Now take another handful of salt and put it in the nearby river. Then, bring me water from the river." | same koan, second orphan |
| C6 | 10 | 1159 | "Hatred does not cease by hatred, but only by love; this is the eternal rule." | Dhammapada line as anonymous scripture (follows B7 orphan) |
| C7 | 3 / 9 | 380 / 1031 | "In the end, only three things matter: how much you loved…" | generic inspirational aphorism, un-authored register (appears twice) |

**Why these break author-first:** each introduces a voice the reader cannot place — a second expert (Maté), a literal unfilled variable (Foo), or disembodied scripture. The salt koans are the most disorienting: the reader is abruptly commanded to drink salt water with zero narrative reason. **Fix:** third-party authorities route through the **teacher_wrapper** (author references them) or are cut; parables need an author/teacher narrative frame ("Ahjan tells the story of the salt…"). The lint flags external proper-noun authorities and bare imperative-parable fragments.

### Systemic (owned by the doctrine-stitch PR — counted separately)

Essentially **every** named Ahjan intro lead-in renders as its **own dangling paragraph** (e.g. L8 "What Ahjan keeps pointing toward is…" then a blank line then the doctrine), instead of flowing **inline** into the doctrine's first sentence. This is exactly the bug `join_wrapped` documents (`phoenix_v4/rendering/teacher_wrapper.py:240–263`, *"the TEACHER_DOCTRINE_INTRO bleed, follow-up to PR #1508"*). The book audited here is the **pre-stitch** state. **Not in scope for this doc and not in the 29** — but it is the direct precedent for why the science wrapper must use the hardened `join_wrapped` from day one (§6).

---

## §3 — Complete slot × treatment table (the voice-zone binding)

Every renderer-emitted slot, mapped to its author-first treatment. **No gaps.** This is the table #1509 said was missing ("no voice/slot zoning") and the table the Stage-6 lint (§5) enforces. Voice/person confirmed against `specs/PHOENIX_V4_5_WRITER_SPEC.md` §3 (voice table) and §4.1–4.8.

**Four treatments:**
- **A = Pure author** (no wrapper; the author's own voice — narration, analysis, address)
- **C = Character** (author-directed third-person; named cast; never teaches, never first-person)
- **TW = Teacher-wrapped** (author references Ahjan via `teacher_wrapper`)
- **SW = Science-wrapped** (author references research via the new `science_wrapper`)

| Slot | Person / voice (spec) | Treatment | Wrapper required? | Notes / where borrowed authority may enter |
|------|----------------------|-----------|-------------------|--------------------------------------------|
| **HOOK** | 1st-person author OR 2nd-person direct (§3) | **A** | no | Author's grab. Never teacher/science. |
| **SCENE** | 2nd-person present always (§3, §4.2) | **A** | no | Author narrates the reader's world. *Illustrates, does not teach* (§4.2) — so no doctrine/science ever lands here. |
| **STORY** | 3rd-person present (§3, §4.3) | **C** | no | Named cast (Priya, Jordan, Marcus…). Author-directed. Never 1st-person, never teaches. |
| **PIVOT** | 3rd/1st-person author, present (§4.3a) | **A** | no | Names the pattern from the story; *ends before teaching begins* — no mechanism, so no wrapper. |
| **REFLECTION** *(the teach slot)* | 1st-person author + 2nd-person beat (§3, §4.4) | **A** default; **TW** if borrowing Ahjan; **SW** if carrying research | **conditional** | Author's own mechanic = A. If it leans on Ahjan → TW. If it cites neuroscience/physiology → **SW**. Hard ceiling: **≤2 mechanism terms** (§4.4). This is the primary slot where Class-A science *should* live — wrapped. |
| **TEACHER_DOCTRINE** | teacher content | **TW** | **always** | Author references Ahjan; doctrine must be **Ahjan-specific**, not generic (F8). Source: teacher banks. |
| **TEACHER_DOCTRINE_INTRO** | the lead-in head | **TW** | **always** | Ellipsis continuation lead-in; must flow **inline** via `join_wrapped` (not a dangling paragraph). Class-B failures live here. |
| **EXERCISE** | 2nd-person imperative (§3, §4.5) | **A** (instruction) | instruction: no — rationale: **SW** if physiological | The imperative steps are author-owned. If the *rationale* cites physiology ("stimulates the vagus nerve") → science-wrap the rationale (secondary finding, Ch7). |
| **post_practice_validation** *(short closer)* | 2nd-person warm | **A** | no | "Whatever you noticed is enough." Already correct author voice. **Not** a violation. |
| **post_practice_reflection** *(the "aha_noticing" debrief)* | currently raw clinical | **SW** | **always** | **The new science zone.** Inherently physiological → must be author-wrapped every time. Class-A (14) lives here. |
| **INTEGRATION** | 1st-person author, quiet (§3, §4.6) | **A** | no | Landing. Author's own concrete body-state. |
| **THREAD** | 1st/2nd-person, tail of INTEGRATION (§4.7a) | **A** | no | Forward pull, author voice. |
| **TAKEAWAY** | 1st-person author declarative (§4.7) | **A** | no | One-sentence thesis crystallization. Author. |
| **PERMISSION** | 2nd-person only (§4.8) | **A** | no | Chapter-specific permission. Author receiving the reader. |
| **COMPRESSION** | high-recall distillation (§ F006) | **A** | no | Memory anchor / shareable line. Author. |
| **ANGLE_DEFINITION / CALLBACK** | author framing device | **A** | no | The book's organizing conceit ("the alarm"), author-owned throughout. |

**Reading of the table:** the overwhelming majority of slots are **pure author** and must never carry an un-owned teacher/science voice. Exactly **two** zones admit borrowed authority, and both demand a wrapper: **teacher** content (TEACHER_DOCTRINE[_INTRO], and REFLECTION when it leans on Ahjan) and **science** content (post_practice_reflection always; REFLECTION when it cites research; EXERCISE rationale when physiological). Everything else un-wrapped in those positions = F5.

---

## §4 — Science-wrapper phrase DRAFT

**This is a DRAFT inside this doc.** Spec #5 turns it into `config/catalog_planning/science_wrapper_templates.yaml`. **This session does not create that file** (collision avoidance). Structure mirrors `teacher_wrapper_templates.yaml` (modes → `intro_wrapper` / `exercise_wrapper` / `conclusion_wrapper`, each `pattern` + `variants` + `slot_requirements`).

**Design rules (carried from the teacher system + the doctrine-stitch lesson):**
1. **Author-first.** Every variant is the author *bringing in* research, never the clinic speaking. Subject is "I / the research / what your body did," never a bare body-part.
2. **Ellipsis continuation lead-ins that flow inline.** Intro variants end in `…` and are authored to join the physiological body's first sentence with a single space — **reuse `join_wrapped`** (`phoenix_v4/rendering/teacher_wrapper.py:240`) so they never dangle as their own paragraph (the Class-B/-systemic lesson).
3. **Generalized mode preferred** (no named study/researcher), mirroring the teacher system's 65–70% generalized default; a **specific** mode (named field/mechanism, e.g. "polyvagal research") is gated to sparing use like named-teacher mode.
4. **A conclusion variant hands the voice back to the author** after the science, closing the wrapper so the reader exits in the author's voice.

**Slot variables:** `{MECHANISM}` (e.g. "nitric oxide", "heart-rate variability"), `{FIELD}` (e.g. "the neuroscience", "polyvagal research"), `{EFFECT}` (e.g. "your system settles").

```yaml
# DRAFT — science_wrapper_templates.yaml (spec #5 creates the real file)
# Author-first wrappers for SCIENCE/physiology content. Mirrors teacher_wrapper_templates.yaml.
# Variant variables: {MECHANISM}, {FIELD}, {EFFECT}

# ── Generalized mode (preferred — no named study/researcher) ──────────────────
generalized:
  intro_wrapper:
    # Ellipsis lead-ins: join INLINE into the physiology via join_wrapped (no dangling paragraph).
    pattern: "And here's what your body just did, if you want the mechanism..."
    variants:
      - "And this is even proven scientifically..."          # operator's own phrasing
      - "There's hard evidence for this, too..."
      - "Research shows the same thing your body just felt..."
      - "What I've learned from the neuroscience here is..."  # mirrors "What I learned from Ahjan is..."
      - "If you want to know why that worked, the physiology is simple..."
      - "The science underneath this is quieter than it sounds..."
      - "Researchers have a name for what just shifted..."
      - "This isn't just a feeling — the studies show..."
      - "There's a measurable reason your system settled..."
      - "And the body has its own logic here, one the research has mapped..."
      - "What the research keeps finding is..."
    slot_requirements: []          # generalized needs no named field
  # Continuation lead-ins (mid-block, to flow a second physiological sentence inline
  # so it never dangles): "— and what the studies show is...", "the mechanism being...",
  # "which researchers link to...".
  exercise_wrapper:
    # For EXERCISE rationale that cites physiology (the vagus-nerve case, Ch7).
    pattern: "There's a reason this works in the body — research shows {MECHANISM}..."
    variants:
      - "The body has a mechanism for this: {MECHANISM}..."
      - "This isn't woo — {MECHANISM} is doing the work..."
    slot_requirements: [MECHANISM]
  conclusion_wrapper:
    # Hands the voice BACK to the author after the science closes.
    pattern: "But you don't need the science to feel it — your body already did the work."
    variants:
      - "The research is just confirming what your system already knew."
      - "That's the mechanism. What matters is the shift you just felt."
    slot_requirements: []

# ── Specific mode (gated — named field/mechanism; use sparingly, like named-teacher) ──
specific:
  intro_wrapper:
    pattern: "What {FIELD} shows here is precise..."
    variants:
      - "Drawing on {FIELD}, the reason is {MECHANISM}..."
      - "{FIELD} has a clean explanation: {MECHANISM}..."
    slot_requirements: [FIELD]
```

**Count:** **11** generalized intro variants (+ pattern) — author bringing in research; **3** continuation lead-ins; **3** exercise-rationale variants; **3** conclusion (hand-back) variants; **3** specific-mode variants. The operator's exact phrasings — *"And this is even proven scientifically…"*, *"Research shows…"*, *"The neuroscience underneath this…"*, *"There's hard evidence here too…"* — are all represented.

---

## §5 — Stage-6 LINT rule (drafted for Pearl_Dev)

**Goal:** flag any teacher- or science-register content that is **not** preceded by a resolved wrapper (a raw voice-shift), plus orphaned/broken wrappers. Runs at **Stage 6** (prose resolution), where the assembled section text *and* its `slot_type` *and* the resolved wrapper prefix are all available.

**Per assembled section:**

```
register := classify_register(section.text)   # AUTHOR | TEACHER | SCIENCE | CHARACTER

# R1 — un-wrapped science (Class A)
if register == SCIENCE and not section.science_wrapper_resolved:
    FAIL "F5-science: clinical voice-shift with no author wrapper"   # e.g. A1..A14

# R2 — un-wrapped teacher doctrine (Class B content)
if register == TEACHER and not section.teacher_wrapper_resolved:
    FAIL "F5-teacher: doctrine with no author reference"

# R3 — orphaned / truncated wrapper (Class B-orphan + B-missing-name)
if is_orphan_wrapper_fragment(section.text):
    FAIL "F5-orphan: dangling/truncated wrapper head"
    # matches: line that is ONLY a leading conjunction/preposition + ellipsis
    #   (^\s*(and|but|drawing on|according to)\b.*\.\.\.\s*$),
    #   an ellipsis lead-in with no following body on the same block,
    #   or any unresolved {TOKEN} / empty teacher-name slot
    #   ("Sit with  long enough", double space where {TEACHER_NAME} was)

# R4 — un-framed third-party authority (Class C-thirdparty)
if names_external_authority(section.text) and authority not in teacher_registry
        and not author_framed(section.text):
    FAIL "F5-thirdparty: outside authority not wrapped"   # Maté, Foo, …
    # also flag literal placeholder tokens surfacing as names (e.g. "Foo")

# R5 — orphaned parable/scripture (Class C-scripture)
if is_bare_parable_fragment(section.text):   # imperative koan / aphorism with no narrative frame
    WARN "F5-scripture: parable fragment without teacher/author container"

# R6 — REFLECTION ceiling cross-check (catches un-wrapped science hiding in REFLECTION)
if section.slot == REFLECTION and count_mechanism_terms(section.text) > 2:
    WARN "REFLECTION exceeds 2-mechanism-term ceiling — likely un-wrapped science (route to SW)"
```

**Register classification — `SCIENCE` detection (the precise part Pearl_Dev needs):**
- Maintain a **clinical-term lexicon** (seed from the Class-A evidence): `nitric oxide, oxygen, carbon dioxide, vagus nerve, heart rate variability, cortisol, parasympathetic, trapezius, posterior chain, muscle group(s), nervous system, peripheral vision/awareness, threat detection, defensive activation, synchronization, calming pathways, optimization, recalibrat*`.
- A section is **SCIENCE register** when it contains **≥2 lexicon hits in third-person declarative sentences** (subject is a body part / substance / process, not "I" or "you-as-experiencer") **and** lacks a first-person-author or second-person-experiencer frame in the same block.
- `science_wrapper_resolved` is true when the block is immediately preceded (inline, via `join_wrapped`) by a resolved `science_wrapper` intro variant.
- `TEACHER register`: content sourced from a teacher bank / Ahjan-attributable, where `teacher_wrapper_resolved` is false.

**Severity:** R1–R4 **BLOCK** (hard voice-shift / broken render). R5–R6 **WARN** (route-to-wrapper / ceiling). Thresholds (lexicon min-count, fragment regexes) are tunable in `config`; this draft gives the detection shape, not final regex.

---

## §6 — Handoff (grounds orchestrator spec #5)

This doc is the grounded input for the orchestrator's **bestseller fit-plan spec #5**. Mapping:

| This doc | Becomes, in spec #5 |
|----------|---------------------|
| **§3** complete slot × treatment table | the **canonical voice-zone table** (the binding #1509 called "no voice/slot zoning") — operator confirms when #5 returns it |
| **§4** science-wrapper phrase draft | the spec to **create** `config/catalog_planning/science_wrapper_templates.yaml` (this session deliberately did **not** create it) |
| **§5** Stage-6 lint rule | the **lint** Pearl_Dev builds (raw-voice-shift detector: R1–R6) |
| **§2** 29-instance audit | the **F5 evidence base** — concrete, quantified, real-book |

**Reuse, don't reinvent (principle 9):** the science engine **must reuse `join_wrapped`** (`phoenix_v4/rendering/teacher_wrapper.py:240–263`) so science intro lead-ins flow **inline** into the physiology — the exact contract the doctrine-stitch PR hardened for teacher lead-ins. Do **not** author a parallel join.

**Sequencing / non-collision:**
- The **doctrine-stitch PR** (`agent/pearl-prime-doctrine-intro-stitch-20260611`) owns `teacher_wrapper.py` and fixes the systemic dangling-teacher lead-in (and should also resolve the Class-B orphans B1–B8, which are teacher-wrapper resolution bugs). The science wrapper lands **after / on top of** its hardened `join_wrapped`.
- Spec #5 creates `science_wrapper_templates.yaml` and wires `post_practice_reflection` (the `aha_noticing` debrief) + REFLECTION-with-research + EXERCISE-rationale through it, then ships the §5 lint.

**Open items for the operator (spec #5 decision points):**
1. Confirm the §3 zoning table (especially: REFLECTION as conditional A/TW/SW; post_practice_reflection as always-SW).
2. Generalized-vs-specific science mode ratio (proposed: generalized default like the teacher 65–70%).
3. Class-C third-party policy: route Maté-type authorities through `teacher_wrapper`, or cut? ("Foo" is a separate placeholder-resolution bug to file.)

**Cross-references:** #1509 `OUR_SYSTEM_VS_PATTERNS_GAP.md` (F5/F8/C2) · `specs/PHOENIX_V4_5_WRITER_SPEC.md` §3/§4.4/§4.x · `config/catalog_planning/teacher_wrapper_templates.yaml` · `phoenix_v4/rendering/teacher_wrapper.py` · `phoenix_v4/rendering/chapter_composer.py:2059` · `SOURCE_OF_TRUTH/exercises_v4/aha_noticing_phoenix_standard.yaml` · `docs/PEN_NAME_AUTHOR_SYSTEM.md`.

---

*End — VOICE_TREATMENT_INVENTORY.md. Read-only audit; one doc; no config, no `teacher_wrapper.py`, no bestseller spec, no hot file touched.*
