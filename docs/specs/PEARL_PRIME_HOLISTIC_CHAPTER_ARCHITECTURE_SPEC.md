> ⛔ SUPERSEDED 2026-06-25 — craft doctrine consolidated into the canonical
> `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (§ "Added from
> PEARL_PRIME_HOLISTIC_CHAPTER_ARCHITECTURE_SPEC — 2026-06-25"). The 8-role
> chapter-architecture doctrine now lives in the OVERLAY. Retained for history +
> the per-runtime `chapter_role_assignment.yaml` derivation detail. Build off the
> OVERLAY, not this file.

# PEARL_PRIME_HOLISTIC_CHAPTER_ARCHITECTURE — Chapter as narrative unit, not slot-grid

**Status:** SUPERSEDED 2026-06-25 (consolidated into OVERLAY). Was: v2 — chapter architecture upgrade, coexisting with v1 via opt-in.
**Effective:** 2026-05-20
**Authority:** `docs/PEARL_ARCHITECT_STATE.md`
**Operator diagnosis source:** OPDs 129–133 (2026-05-20 — Holistic Chapter Architecture diagnosis)
**Reference models (bestseller bar):**
- `artifacts/pipeline_examples/miki/book_miki_imposter_syndrome_15min.txt` — primary; 4-chapter holistic architecture
- `artifacts/pipeline_examples/joshin/book_joshin_anxiety_15min.txt` — Zen mirror, 4-chapter named-story arc
- `artifacts/pipeline_examples/ahjan/book_ahjan_anxiety_15min.txt` — Theravada alarm, 4-chapter named-story arc with practice-multipack
**Current planner files this spec governs:**
- `phoenix_v4/planning/chapter_planner.py`
- `phoenix_v4/planning/enrichment_select.py`
- `phoenix_v4/planning/beatmap_compile.py`
- `phoenix_v4/rendering/chapter_composer.py`
- `config/catalog_planning/teacher_wrapper_templates.yaml`
- `config/catalog_planning/chapter_role_assignment.yaml` (NEW — per §3)

---

## §1 — Problem statement: the 6h pipeline treats chapters as slot-fills, not narrative units

The operator's 2026-05-20 diagnostic on the Ahjan × gen_z_professionals × anxiety × deep_book_6h render
(artifacts/pipeline_examples ledger comparison) reveals a structural mismatch between what the current
pipeline produces and what the miki/joshin/ahjan 15-minute reference models exemplify. The pipeline
treats each chapter as an instance of the 10-slot somatic grid (HOOK → STORY → REFLECTION → EXERCISE
→ STORY → TEACHER_DOCTRINE → REFLECTION → EXERCISE → STORY → INTEGRATION; see `beatmap_compile.py:42-53`
`SOMATIC_10_SLOT_GRID`), then fills every slot in every chapter from atom pools with median atom
length ~117 words. The result is ~60–80 short atoms per chapter that read as a checklist, not a
chapter. The 15-minute reference models do the opposite: each chapter has a **dominant narrative role**
(THE WITNESS, THE COSTUME, THE SEEING, THE LIGHT) and develops that role across 10–12 long atoms
(400–1,500 words each), one sustained arc, one named character, one undivided exercise.

The 10-point comparison below extracts the architectural differences from the miki book vs the 6h
Ahjan render. Each point includes (a) verbatim sample from miki, (b) verbatim sample from the 6h
slot-fill, (c) the architectural difference.

### Diagnostic 1: Sustained narrative vs fragmented (Kenji 1,500w vs Priya 140w)

- **(a) miki book**, Chapter 2 (THE COSTUME) — Kenji's story spans line 56 to line 102, roughly 1,500
  words. The reader follows Kenji from glass-walled office through Portland rain home, then through
  internal monologue cataloguing every project as fluke, into the moment Mochi the cat presses skull
  against his hand and his shoulders drop half an inch. The story is one continuous arc:
  > "His name is Kenji, and he is twenty-six years old, and he has just been promoted to lead
  > developer at a startup in Portland, Oregon." (line 56)
  > … 45 lines later …
  > "Kenji does not know this yet. He knows only that the cat is warm and the rain is steady and
  > for the first time since Tuesday afternoon, his shoulders are not touching his ears." (line 100)
- **(b) 6h book** — Priya appears in ~140 words inside a single STORY atom, then disappears. The
  atom pool's median is 117 words, so the persona STORY slot in chapter 3 yields a 140-word vignette
  that gets sandwiched between unrelated REFLECTION and EXERCISE atoms. Priya never returns.
- **(c) architectural difference**: miki's COSTUME chapter is built around a single named-character
  story that develops continuously over ~1,500 words. The 6h slot-grid has 3 STORY slots per chapter
  (sections 02 / 05 / 09) each filled from independent atom rows, so the chapter never gets one long
  arc — it gets three short, unrelated vignettes.

### Diagnostic 2: Doctrinal scaffold up front

- **(a) miki book** opens with `A NOTE ON THE TEACHINGS` (lines 12–20): four paragraphs that name
  amae, ikigai, define the Shinto frame, and end with "This book is that gift." The reader enters
  Chapter 1 already knowing the vocabulary the chapters will operationalize.
- **(b) 6h book** opens directly into Chapter 1 HOOK with no pre-chapter doctrinal preamble. The
  reader must reverse-engineer the framework from the chapters themselves.
- **(c) architectural difference**: the 15-minute books have a **TEACHER_DOCTRINE_INTRO** rendered
  before Chapter 1 — a doctrinal preamble that loads the reader's vocabulary. The 6h pipeline has
  no such pre-chapter shape; doctrine is scattered across in-chapter TEACHER_DOCTRINE slots.

### Diagnostic 3: Coherent teaching arc per chapter

- **(a) miki book**, Chapter 1 (THE WITNESS) — the chapter does ONE thing: it recognizes the
  imposter feeling as a body-level signal, not a competence verdict. Every paragraph from line
  26 through line 50 develops that single thesis. No exercise. No multi-track teaching.
- **(b) 6h book** — chapters have HOOK + STORY × 3 + REFLECTION × 2 + EXERCISE × 2 + TEACHER_DOCTRINE
  + INTEGRATION = ten different micro-teachings per chapter, with no dominant role.
- **(c) architectural difference**: chapter as **monothematic narrative unit** vs chapter as
  **10-slot variety pack**.

### Diagnostic 4: ONE sustained exercise vs micro-exercises

- **(a) miki book**, Chapter 3 (THE SEEING) — one 5-part exercise (find a place → sit → close
  eyes → 3 breaths → hand on body → ask the feeling a question → 3 more breaths → open eyes), lines
  108 through 168. The exercise occupies the entire chapter, with integration paragraphs woven
  inside the exercise instructions.
- **(b) 6h book** — two EXERCISE slots per chapter (slot 4 and slot 8 in the 10-slot grid), each
  filled with a short ~100-word exercise atom. The reader never gets one undivided exercise — they
  get two short ones flanked by REFLECTION.
- **(c) architectural difference**: the chapter is **the exercise** (in THE SEEING role), not a
  container that holds two short exercises.

### Diagnostic 5: Wrapper fragments breaking flow

- **(a) miki book** — no template wrappers. Every transition is authored prose. Lines 67–68:
  > "Miki would notice the shoulders first. Not the thoughts. The shoulders."
  This is the teacher's voice as a complete sentence, not an ellipsis-stub.
- **(b) 6h book** — wrappers ending in ellipsis from `config/catalog_planning/teacher_wrapper_templates.yaml`
  (line 15: `"In {TEACHER_NAME}'s framework, the path begins with..."`) get emitted standalone with
  no atom completing them. The reader sees "In Ahjan's framework, the path begins with…" as a
  hanging fragment.
- **(c) architectural difference**: wrappers must be **followed by an atom that semantically
  completes the sentence**, or dropped from rendering entirely.

### Diagnostic 6: Permission section

- **(a) miki book**, Chapter 4 (THE LIGHT), lines 182–195 — eight sentences each granting an
  explicit permission. Mantra-quotable, declarative, therapeutic:
  > "The listener is allowed to need people." (line 184)
  > "The listener is allowed to feel the doubt." (line 188)
  > "The listener is allowed to succeed without feeling ready." (line 190)
  > "The listener is allowed to receive good things." (line 192)
  > "The listener is allowed to let the hand rest on the belly." (line 194)
- **(b) 6h book** — no equivalent PERMISSION block. The composer has a `PERMISSION` slot (composer
  line 2171; line 2445: "PERMISSION (receive the reader — Writer Spec §4.8)") but no PERMISSION_GRANT
  atom shape exists in the atom registry to fill it.
- **(c) architectural difference**: PERMISSION_GRANT is a **first-class atom shape** with a
  declared format (5–8 "you are allowed to ___" sentences), not a derivative of REFLECTION.

### Diagnostic 7: Closing arc

- **(a) miki book**, Chapter 4 (THE LIGHT) closes lines 196–209 with a compressed re-statement of
  ikigai, then a deliberate door-handoff: "The hand. The breath. The body. The landing. / The
  listener has arrived." The reader is *closed out of the book* with a single image.
- **(b) 6h book** — the closing chapter is structurally identical to the middle chapters (same
  10-slot grid). The book doesn't close; it stops.
- **(c) architectural difference**: the LIGHT chapter (or THRESHOLD chapter in longer runtimes)
  has a **distinct closing-role shape** that doesn't appear in middle chapters.

### Diagnostic 8: Holistic chapters vs slot-cram

- **(a) miki book** — 4 chapters × ~1,400 words/chapter × ~10–12 paragraphs/chapter = ~6,000 words
  total in roles {WITNESS, COSTUME, SEEING, LIGHT}.
- **(b) 6h book** — 12 chapters × ~5,000 words/chapter × ~60 atoms = 720 atoms total across 12
  chapters. Every chapter renders all 10 slots, regardless of narrative phase.
- **(c) architectural difference**: chapter role is a **first-class planning dimension** that
  selects WHICH slots/atoms a chapter renders. Not every chapter renders every slot.

### Diagnostic 9: Teacher voice woven vs isolated

- **(a) miki book**, Chapter 2 (THE COSTUME) — Miki's voice appears interleaved with Kenji's
  story: lines 68 ("Miki would notice the shoulders first"), 86 ("Miki teaches that imposter
  syndrome is not a thinking problem"), 96 ("Miki says: that unlocking is the sound of attention
  arriving at the wound"). Three teacher-voice interventions woven into one continuous story.
- **(b) 6h book** — TEACHER_DOCTRINE lives in slot 6 (the 6th of 10 slots), isolated between two
  REFLECTION slots, fed by a separate TEACHER_DOCTRINE atom that doesn't reference the surrounding
  story atoms.
- **(c) architectural difference**: in COSTUME-role chapters, teacher voice is **woven into the
  story atom itself** (one long STORY-with-reflection atom), not isolated in a dedicated
  TEACHER_DOCTRINE slot.

### Diagnostic 10: Fewer + longer atoms vs many + short

- **(a) miki book** — Chapter 2 is approximately 1,800 words, served by what looks like 1 long
  STORY-with-reflection atom (~1,500 words covering Kenji) + 1 closing reflection atom (~300
  words). Total 2 atoms.
- **(b) 6h book** — Chapter 3 (selected typical) gets 65 atoms from the persona/registry pools
  across the 10 slots. Median atom length 117 words.
- **(c) architectural difference**: select **fewer + longer atoms per chapter** (cap at 15 atoms,
  with avg 400–600 words/atom yielding the target 4,500–6,000-word chapter), not many + short.

---

## §2 — The holistic chapter architecture (v2)

### §2.1 Chapter as narrative unit with a dominant role

Each chapter has a **dominant role** (1–2 narrative tasks), NOT all 10 slot-roles. The chapter
develops the dominant role across sustained paragraphs from a smaller, longer atom set. The 8
canonical roles extend miki's WITNESS / COSTUME / SEEING / LIGHT to cover runtimes up to
`deep_book_6h` (12 chapters).

| Role | Hook word | Chapter task |
|---|---|---|
| **WITNESS** | Recognition | Opens the book with vignette that establishes the felt experience the book addresses. ONE protagonist (anonymous), present-tense scene, no exercise, no named-cast story. |
| **COSTUME** | Story+reflection | Named character (e.g. Kenji, Mara, Priya) carrying ONE sustained story-arc ≥1,000 words, with teacher voice woven into the story (not isolated in TEACHER_DOCTRINE slot). |
| **SEEING** | Exercise | One sustained 5-part exercise (per OPD-113 introduction/description/guidance/aha/integration), occupying the bulk of the chapter, integration paragraphs woven into the exercise. |
| **LIGHT** | Compression+permission | Distills the teaching to a compressed thesis and grants explicit permissions via a PERMISSION_GRANT atom (5–8 "you are allowed to ___" lines). Closing-only in micro_book_15. |
| **ENGINE** | Mechanism reveal | The angle's named-object (e.g. "The Mechanism", "The Alarm") gets a deep teaching block. Sourced from the OPD-116/117 ENGINE atom shape. |
| **TEST** | Practice under pressure | Scenario where the practice from SEEING is tested under real conditions (job interview, difficult conversation, sleepless night). Confirms the practice survives contact with life. |
| **NAMING** | Identity shift | Reader names what they've been carrying. "You are not anxious. You are a body that learned to scan a house that no longer exists." Identity-naming, not behavior-naming. |
| **THRESHOLD** | Closing+doorway | Chapter-close that hands the practice off into life — the deep_book_6h equivalent of the LIGHT chapter's "the door was always open" closing. |

Each role declares (in the chapter-role registry, see §3) which atom shapes it requires, which it
forbids, and target word/atom counts.

### §2.2 Chapter role assignment per runtime

For each runtime, declare the canonical role assignment per chapter index. Per OPD-130, this
assignment is encoded in `config/catalog_planning/chapter_role_assignment.yaml` (NEW), consumed by
`chapter_planner.py` before slot-row construction.

```yaml
# config/catalog_planning/chapter_role_assignment.yaml
schema_version: 1
authority: docs/specs/PEARL_PRIME_HOLISTIC_CHAPTER_ARCHITECTURE_SPEC.md
chapter_role_assignment:
  # 4–5 chapters; the canonical miki shape
  micro_book_15:
    1: WITNESS
    2: COSTUME
    3: SEEING
    4: LIGHT
    5: LIGHT   # optional when chapter_count=5

  # 7 chapters; standard_book opting in to v2
  standard_book:
    1: WITNESS
    2: COSTUME
    3: SEEING
    4: ENGINE
    5: TEST
    6: NAMING
    7: THRESHOLD

  # 10 chapters; extended_book_2h opting in to v2
  extended_book_2h:
    1: WITNESS
    2: COSTUME    # first named story
    3: SEEING     # first sustained exercise
    4: ENGINE
    5: COSTUME    # second named story
    6: TEST
    7: NAMING
    8: ENGINE     # deeper angle teaching
    9: LIGHT      # compression + permission
    10: THRESHOLD

  # 12 chapters; deep_book_6h opting in to v2 (the operator's primary target)
  deep_book_6h:
    1: WITNESS
    2: COSTUME    # first named story
    3: SEEING     # first sustained exercise
    4: ENGINE     # angle's named-object deep teaching
    5: COSTUME    # second named story
    6: SEEING     # second exercise
    7: TEST
    8: COSTUME    # third named story
    9: LIGHT      # compression + permission
    10: ENGINE    # deeper angle teaching
    11: NAMING
    12: THRESHOLD

  # 12 chapters; deep_book_4h — same as 6h, but compressed
  deep_book_4h:
    1: WITNESS
    2: COSTUME
    3: SEEING
    4: ENGINE
    5: COSTUME
    6: SEEING
    7: TEST
    8: COSTUME
    9: LIGHT
    10: ENGINE
    11: NAMING
    12: THRESHOLD
```

Notes:

- Chapter role assignment is **deterministic, not phase-derived**. The current
  `chapter_planner.py:_PHASE_POOLS` (opening / early_middle / mid_book / late_middle / closing)
  governs *bestseller structure shape*, NOT chapter narrative role. Both planning dimensions
  coexist: a chapter has both a chapter_role (e.g. COSTUME) AND a bestseller_structure (e.g.
  `gladwell_spiral`). Role drives WHICH ATOM SHAPES are allowed; structure drives WHICH BEAT
  STEPS the slot row carries.
- For runtimes not present in `chapter_role_assignment`, the planner falls back to v1
  (slot-grid behavior). This is the migration safety net.

### §2.3 Atom-count and length targets per chapter role × runtime

Per OPD-129. For each role × runtime, the planner enforces:

| Role | Runtime | Target atoms | Target words | Required shapes | Forbidden shapes |
|---|---|---:|---:|---|---|
| WITNESS | micro_book_15 | 1–2 | 800–1,400 | HOOK + 1 long REFLECTION (≥600w) | EXERCISE, named STORY |
| WITNESS | deep_book_6h | 2–3 | 1,200–1,800 | HOOK + REFLECTION (≥800w) | EXERCISE, named STORY |
| COSTUME | micro_book_15 | 2 | 1,400–1,800 | ≥1 STORY atom ≥1,000 words + REFLECTION woven | EXERCISE, separate TEACHER_DOCTRINE |
| COSTUME | deep_book_6h | 3–4 | 4,500–6,000 | ≥1 STORY atom ≥1,000 words + REFLECTION woven, optionally TEACHER_DOCTRINE_WOVEN | second STORY (use ENGINE for second teaching block) |
| SEEING | micro_book_15 | 2–3 | 1,400–2,000 | EXERCISE (5-part per OPD-113), INTEGRATION | named STORY, separate REFLECTION |
| SEEING | deep_book_6h | 4–6 | 4,500–6,000 | EXERCISE (5-part), INTEGRATION × 2 | named STORY |
| ENGINE | deep_book_6h | 4–6 | 4,500–6,000 | ENGINE atom (per OPD-116/117 named-object), TEACHER_DOCTRINE, optionally REFLECTION | EXERCISE, named STORY |
| TEST | deep_book_6h | 4–6 | 4,500–6,000 | STORY (test scenario, named), REFLECTION, optional EXERCISE | PERMISSION_GRANT |
| NAMING | deep_book_6h | 3–5 | 4,000–5,500 | REFLECTION (identity-frame), TEACHER_DOCTRINE | EXERCISE, multiple STORY |
| LIGHT | deep_book_6h | 3–4 | 3,500–5,000 | COMPRESSION + PERMISSION_GRANT | EXERCISE, named STORY |
| THRESHOLD | deep_book_6h | 2–4 | 2,500–4,500 | INTEGRATION, REFLECTION, optional COMPRESSION | EXERCISE, named STORY, PERMISSION_GRANT |

Hard caps (per OPD-129):

- **Maximum atoms per chapter:** 15 (hard cap). The current pipeline routinely exceeds 60.
- **Minimum STORY atom word count for deep_book_6h COSTUME:** 800 words. The current median atom
  is 117 words.
- **Per-chapter word target for deep_book_6h:** 4,500–6,000 words drawn from 10–15 atoms (avg
  400–600 words per atom).

If the atom pool does not contain atoms meeting the length floor, the planner emits
`planner_warning`, uses the longest available, and does NOT compensate by selecting more atoms.
Authoring gap is surfaced to Pearl_Editor; the render still completes.

### §2.4 Doctrinal preamble (TEACHER_DOCTRINE_INTRO)

Per OPD-130: NEW atom shape rendered BEFORE Chapter 1. Equivalent of miki book's "A NOTE ON THE
TEACHINGS" (lines 12–20).

**Atom path:**

```
atoms/<persona>/<topic>/TEACHER_DOCTRINE_INTRO/<teacher_id>/CANONICAL.txt
```

Example: `atoms/gen_z_professionals/anxiety/TEACHER_DOCTRINE_INTRO/ahjan/CANONICAL.txt`

**Required structure:**

- 4–6 paragraphs, 800–1,200 words total.
- Paragraph 1: Tradition + lineage frame (one sentence). Example, from miki:
  > "Miki teaches from the intersection of ancient Shinto awareness and the lived reality of being
  > young and alive in a world that moves too fast to feel."
- Paragraphs 2–3: Define 2–3 core concepts the book operationalizes. Each concept introduced with
  the term, the literal meaning, and the lived-experience definition. Example, from miki on amae:
  > "The first is amae — the natural, healthy need to be held, supported, received by others.
  > Modern culture treats dependence as weakness. Miki treats it as biology."
- Paragraph 4 (or final paragraph): The "this book is that gift" closer. Hand the reader into
  Chapter 1 with the felt frame loaded. Example, from miki:
  > "This book is that gift. Fifteen minutes of undivided attention aimed at the part of the
  > listener that already knows it belongs."

**Render position:** Between the book front matter (cover/title) and Chapter 1 header. Emitted by
`render_spine_book` as a `--- A NOTE ON THE TEACHINGS ---` (miki) or `A NOTE ON THE TEACHINGS`
(joshin/ahjan) section.

**Fallback when atom missing:** templated 1-paragraph preamble synthesized from the teacher's
`doctrine.yaml` `tradition`, `lineage`, and `core_concepts` fields. The composer emits a
`planner_warning` so Pearl_Editor knows to author the full atom.

### §2.5 PERMISSION_GRANT atom shape

Per OPD-133: NEW atom shape used in LIGHT-role chapters. Equivalent of miki book's lines 182–195.

**Atom path:**

```
atoms/<persona>/<topic>/PERMISSION_GRANT/CANONICAL.txt
```

(Note: PERMISSION_GRANT may be per-topic rather than per-(teacher × topic) — operator decision
needed; see §5 P1.)

**Required structure:**

- 5–8 sentences, each starting with **"You are allowed to ___"** or **"The reader is allowed to
  ___"** (declarative, second-person, therapeutic).
- Each sentence stands alone — mantra-quotable.
- Each sentence grants ONE permission that **contradicts the topic's typical shame frame**.
  Example, from miki on imposter syndrome:
  > "The listener is allowed to need people." (contradicts independence-shame)
  > "The listener is allowed to succeed without feeling ready." (contradicts readiness-shame)
  > "The listener is allowed to receive good things." (contradicts unworthiness-shame)
- Tone is **declarative, therapeutic, mantra-quotable** — NOT argumentative, NOT proof-based.
  This is permission-granting, not persuasion.

**Render position:** Inside a LIGHT-role chapter, after a COMPRESSION block, before the closing
INTEGRATION. Lines 182 ("Now the permission.") through 195 (the last "allowed to" line) in the
miki reference.

### §2.6 Wrapper-template behavior (OPD-132 fix)

The current `config/catalog_planning/teacher_wrapper_templates.yaml:15-17` has wrappers ending in
ellipsis (`"In {TEACHER_NAME}'s framework, the path begins with..."`). These are designed to be
followed by an atom that semantically completes them, but the composer currently emits them
standalone when no completion atom is in scope. Per OPD-132:

**Rule 1 — Wrappers ending in ellipsis MUST be followed by a completing atom.**

The wrapper templates declare a `completion_required: true` flag (NEW field), and the
`chapter_planner` checks: if no TEACHER_DOCTRINE atom or COMPRESSION atom is in scope to complete
the wrapper, the wrapper is **DROPPED** from rendering.

**Rule 2 — Composer never emits a standalone ellipsis-wrapper.**

The composer's wrapper-emission path checks for the `completion_required` flag and, if true,
verifies the following slot in the rendered sequence is a TEACHER_DOCTRINE / COMPRESSION /
TEACHER_DOCTRINE_INTRO atom (or another shape whose first sentence syntactically completes the
wrapper). If no completion exists, the wrapper is omitted entirely and the next atom is rendered
without a wrapper preamble.

**YAML extension (additive, back-compat):**

```yaml
named:
  intro_wrapper:
    pattern: "According to {TEACHER_NAME}, {TEACHING_LINEAGE} teaches us..."
    completion_required: true   # NEW; default false for back-compat
    completion_atom_shapes: [TEACHER_DOCTRINE, COMPRESSION, TEACHER_DOCTRINE_INTRO]
    variants:
      - "In {TEACHER_NAME}'s framework, the path begins with..."
      - ...
```

### §2.7 Atom selection: fewer + longer

Per OPD-129. The selector logic changes in `enrichment_select.py`:

**For STORY slot in COSTUME-role chapters:**

1. Select the LONGEST atom (by `word_count` metadata) that has not been used elsewhere in this
   book. Per-book rotation is already in place via `PersonaPoolRotationState` (see
   `enrichment_select.py:1624`); the cost function is updated to **prefer maximum length** over
   least-used, with least-used as the secondary tiebreaker.
2. **Minimum STORY atom word count for deep_book_6h COSTUME role:** 800 words. If no atom in the
   pool meets the floor, log `planner_warning("costume_story_atom_below_length_floor", chapter=N,
   pool_min=X, floor=800)` and pick the longest available.

**For all slots:**

1. **Maximum atoms per chapter:** 15 (hard cap). The selector stops appending atoms once the cap
   is reached, even if remaining slots are unfilled. Unfilled slots are dropped from the chapter's
   rendered slot row.
2. **Per-chapter word target:** 4,500–6,000 words from 10–15 atoms (avg 400–600 words per atom).
   The selector consults this target after each atom selection and short-circuits remaining slot
   selection if the target is met.

**Fallback behavior when atom pool is too short:**

If the pool's longest atom is below the length floor, the planner does NOT compensate by selecting
more atoms (that yields the current "many + short" failure mode). Instead:

- The chapter renders with the longest available atom.
- `planner_warning` is emitted with `pool_min` and `floor` so Pearl_Editor sees the authoring gap.
- The chapter's `target_word_count` is reduced proportionally so downstream gates do not block on
  word-count.

This is a deliberate trade: short-but-coherent over long-but-fragmented.

---

## §3 — Implementation roadmap

### §3.1 File-by-file changes (for Cursor reference)

For each file, the change is additive to v1 behavior and gated on the new `BookSpec`
field `chapter_architecture_version: 1 | 2` (see §3.2). v1 = current behavior. v2 = holistic.

| File | Change | LOC | Tests |
|---|---|---:|---|
| `phoenix_v4/planning/chapter_planner.py` | Role assignment via NEW yaml; atom-count caps; route slot row through role registry. v1 path unchanged. | ~250 | `tests/unit/planning/test_chapter_role_assignment.py` (NEW) — verify role-per-chapter for each runtime; verify v1 fallback when no role assignment exists |
| `phoenix_v4/planning/enrichment_select.py` | Longest-atom selection for STORY in COSTUME role; preamble routing for TEACHER_DOCTRINE_INTRO; hard cap 15 atoms/chapter; per-chapter word target check | ~180 | `tests/unit/planning/test_enrichment_longest_atom.py` (NEW); `tests/unit/planning/test_enrichment_atom_cap.py` (NEW) |
| `phoenix_v4/planning/beatmap_compile.py` | New per-role slot row builders (e.g., `_witness_slot_row()`, `_costume_slot_row()`, `_seeing_slot_row()`, etc.). v1 path unchanged. | ~200 | `tests/unit/planning/test_beatmap_role_slot_rows.py` (NEW) |
| `phoenix_v4/rendering/chapter_composer.py` | Wrapper completion check; PERMISSION_GRANT render path; TEACHER_DOCTRINE_INTRO pre-book emission | ~120 | `tests/unit/rendering/test_composer_wrapper_completion.py` (NEW); `tests/unit/rendering/test_composer_permission_grant.py` (NEW); `tests/unit/rendering/test_composer_doctrine_intro.py` (NEW) |
| `config/catalog_planning/chapter_role_assignment.yaml` | NEW — declares per-runtime role-per-chapter, per-role atom caps and length targets | ~120 | `tests/unit/config/test_chapter_role_assignment_yaml.py` (NEW) — schema + completeness checks |
| `config/catalog_planning/teacher_wrapper_templates.yaml` | Additive: `completion_required` + `completion_atom_shapes` on intro_wrapper / conclusion_wrapper entries | ~20 | `tests/unit/config/test_teacher_wrapper_templates.py` extension |
| `atoms/*/*/TEACHER_DOCTRINE_INTRO/<teacher_id>/CANONICAL.txt` | NEW shape directory + initial pilot atoms (ahjan × gen_z_professionals × anxiety, joshin × gen_z_professionals × anxiety, miki × gen_spark × imposter_syndrome) | ~25 lines/atom × 3 pilots | `tests/unit/atoms/test_doctrine_intro_atom_shape.py` (NEW) |
| `atoms/*/*/PERMISSION_GRANT/CANONICAL.txt` | NEW shape directory + initial pilot atoms (one per pilot topic) | ~10 lines/atom × 3 pilots | `tests/unit/atoms/test_permission_grant_atom_shape.py` (NEW) |
| `phoenix_v4/planning/book_spec.py` | Additive: optional field `chapter_architecture_version: int = 1`, validates {1, 2} | ~10 | `tests/unit/planning/test_book_spec_architecture_version.py` (NEW) |

**Estimated total LOC for v2 code paths:** ~900. Plus ~150 lines of new config + ~100 lines of
pilot atoms.

### §3.2 Migration path

The v2 architecture is opt-in per book:

1. `BookSpec` gains an optional field `chapter_architecture_version: int = 1`.
   - `= 1` (default) → current slot-fill behavior. All existing books render unchanged.
   - `= 2` → holistic chapter architecture. Planner consults
     `chapter_role_assignment.yaml`, enforces atom caps, runs wrapper-completion check, renders
     TEACHER_DOCTRINE_INTRO and PERMISSION_GRANT.

2. The operator approves opting in **per book** to architecture v2. Initial rollout: ahjan ×
   gen_z_professionals × anxiety × deep_book_6h (the diagnostic-source book). Once the v2 render
   on that book matches the bestseller bar, the operator opts in additional books.

3. Pearl_Prime CLI gains `--chapter-architecture-version 2` flag that overrides the BookSpec
   value (operator-only, for canary runs).

4. Once 80%+ of new books render under v2 without quality regressions for 4 weeks, the default
   flips to `= 2` and v1 becomes legacy behavior preserved for the older catalog.

### §3.3 Backwards compatibility

- The existing `micro_book_15` books in `artifacts/pipeline_examples/` (miki, joshin, ahjan, et al)
  should still render **identically** under v2. They are reference exemplars — their roles
  (WITNESS/COSTUME/SEEING/LIGHT) match the v2 chapter_role_assignment.micro_book_15 schedule.
  Verification: re-render the miki book under v2 architecture; diff against the reference text
  is expected to be near-empty modulo non-content metadata.

- `standard_book` and `deep_book_6h` books opt in to v2 via the BookSpec field. Default is v1.

- Tests cover both v1 (existing behavior preserved) and v2 (new behavior). The CI gate verifies
  that under v1, the v1 fixtures pass with byte-exact output (modulo timestamps).

- The v2 atom shapes (TEACHER_DOCTRINE_INTRO, PERMISSION_GRANT) are additive. v1 books continue
  to skip them. Adding the shape directories does not affect v1 selection logic.

- The wrapper-completion check is gated on `chapter_architecture_version == 2`. v1 books continue
  to emit standalone wrappers as today (acceptable for legacy renders).

---

## §4 — Risk register

What could go wrong, plus mitigation:

### Risk 4.1 — Existing atom pools don't have atoms long enough

- **Risk:** The atom pool median is 117 words. v2 requires STORY atoms ≥800 words for COSTUME-role
  deep_book_6h chapters. Most existing pools fail this floor.
- **Mitigation:** ship the architecture (it is mostly back-compat — the floor is a soft warning,
  not a hard block). Surface the authoring gap via `planner_warning`. Defer the actual long-atom
  authoring to Pearl_Editor commissions. The first ahjan canary will render below the bar; the
  operator can then prioritize which long atoms to commission.
- **Confidence:** high. This is a known authoring debt and the operator already runs a
  Pearl_Editor commission backlog.

### Risk 4.2 — The 12-chapter role assignment may not fit every topic

- **Risk:** The deep_book_6h chapter_role_assignment in §2.2 declares 3 COSTUME chapters (2, 5,
  8) for three named-character stories. Some topics may not have 3 distinct named characters in
  the atom pool. Others may have more than 3 and would benefit from a different sequence.
- **Mitigation:** the role assignment yaml supports per-topic overrides:
  ```yaml
  chapter_role_assignment:
    deep_book_6h:
      __default__:
        1: WITNESS
        2: COSTUME
        ...
      <topic_id>:
        # full or partial override
        5: NAMING   # override slot 5 from COSTUME to NAMING for this topic
  ```
- **Open question:** see §5 P2.

### Risk 4.3 — Wrapper drop may surface ugly content joins

- **Risk:** When the composer drops an ellipsis-wrapper (per §2.6), the atom that follows
  it now appears without a preamble. That atom may itself start with a sentence-fragment ("And
  the body knows...") that read naturally with the wrapper but reads jarringly standalone.
- **Mitigation:** the composer's bridge layer (existing
  `phoenix_v4/rendering/chapter_composer.py:_BRIDGE_TRANSITION_*`) already synthesizes bridges
  between slot transitions. When a wrapper is dropped, the composer emits a default bridge
  ("Here, the teaching turns to ...") so the join isn't ugly. The bridge content draws from
  `config/rendering/bridge_transition_families.yaml`.
- **Verification:** v2 canary's `chapter_flow_report.json` must show WEAK_TRANSITIONS=0 for
  COSTUME-role chapters.

### Risk 4.4 — Preamble rendering may interact with existing book-open templates

- **Risk:** The current `render_spine_book` may already emit a book-open template (cover,
  copyright, dedication). Inserting TEACHER_DOCTRINE_INTRO between front matter and Chapter 1
  may double-emit or break ordering.
- **Mitigation:** the v2 render path inserts TEACHER_DOCTRINE_INTRO at a specific anchor in
  `render_spine_book` (after `_render_book_front_matter`, before `_render_first_chapter_header`).
  The anchor is a NEW codepath gated on `chapter_architecture_version == 2`. Existing v1 render
  path skips the anchor entirely.
- **Verification:** unit test `test_composer_doctrine_intro.py` verifies the emission order.

### Risk 4.5 — Atom selection cap (15/chapter) may break existing chapter-flow gates

- **Risk:** The current chapter_flow gate may expect minimum slot counts that a 10-15-atom chapter
  cannot satisfy.
- **Mitigation:** the chapter_flow gate is itself v1 behavior. Under v2, a parallel gate
  (`chapter_role_flow_report.json`) verifies that the chapter's atom set covers the **role's
  required shapes** (per §2.3 table), not the slot grid. The legacy chapter_flow gate is run only
  for v1 chapters.
- **Verification:** integration test asserts that re-rendering the miki book under v2 yields
  identical output AND zero chapter_role_flow warnings.

---

## §5 — Open questions for operator

Format: P0 (blocks execution) / P1 (needs answer before Phase B) / P2 (needs answer eventually).

### P0 — Default opt-in policy

**Q:** Should v2 architecture apply to ALL new books once the canary passes, or only those with
explicit opt-in?

- (a) Opt-in only forever (safe; slow rollout)
- (b) Default v2 for deep_book_6h and longer; opt-in for short formats (matches the diagnosis —
  the 6h book is the broken one)
- (c) Default v2 across the board once the canary passes (aggressive; matches the operator's
  "bestseller bar" goal)

**Recommendation from spec:** (b). v2 was diagnosed against the 6h book; the 15-min books are
already at bestseller bar under v1. Apply v2 where it is needed.

### P0 — STORY atom pool floor enforcement

**Q:** For chapters without a sufficiently long STORY atom in the pool (≥800 words for
deep_book_6h COSTUME), do we:

- (a) Render shorter (current spec proposal §2.7): use longest available, warn, accept the
  shorter chapter
- (b) Skip COSTUME role and substitute ENGINE for that chapter (preserves chapter count and
  word target, sacrifices the named-character story)
- (c) Block the render entirely (forces the authoring gap to be filled before render)

**Recommendation from spec:** (a). The current bottleneck is render success rate, not chapter
quality. A shorter-but-coherent COSTUME chapter is better than a blocked render. The
planner_warning surfaces the gap to Pearl_Editor.

### P1 — PERMISSION_GRANT scoping

**Q:** Should PERMISSION_GRANT be per-topic (`atoms/<persona>/<topic>/PERMISSION_GRANT/CANONICAL.txt`)
or per-(teacher × topic) (`atoms/<persona>/<topic>/PERMISSION_GRANT/<teacher_id>/CANONICAL.txt`)?

- Per-topic is cheaper (1 atom per topic, ~25 topics in catalog = 25 atoms).
- Per-(teacher × topic) is more voice-authentic (~25 topics × 13 teachers = 325 atoms; matches
  the existing teacher-specific atom layout for REFLECTION, etc.).

**Recommendation from spec:** per-topic. The "allowed to" lines in the miki reference (lines
182–195) are not voice-specific — they would read identically in joshin's or ahjan's chapter.
The permission frame is more about the topic's typical shame frame than the teacher's voice.

### P1 — Wrapper drop default

**Q:** Should the wrapper-completion check default to DROP-IF-NO-COMPLETION or KEEP-WITH-DEFAULT-BRIDGE?

- DROP-IF-NO-COMPLETION (spec proposal §2.6): the wrapper is omitted; the composer emits a
  bridge from `bridge_transition_families.yaml` instead.
- KEEP-WITH-DEFAULT-BRIDGE: the wrapper is rewritten on the fly to a non-ellipsis variant (e.g.
  "In Ahjan's framework, the path begins with **the breath**" — auto-filled from the next atom's
  first noun phrase).

**Recommendation from spec:** DROP-IF-NO-COMPLETION. KEEP-WITH-DEFAULT-BRIDGE is brittle (the
auto-fill is hard to make read naturally; risks producing nonsense). DROP is safer and the bridge
layer already handles the join.

### P2 — Chapter role assignment confirmation

**Q:** The deep_book_6h chapter_role_assignment in §2.2 — confirm the sequence?

```
1: WITNESS
2: COSTUME    (first named story)
3: SEEING     (first sustained exercise)
4: ENGINE     (angle's named-object deep teaching)
5: COSTUME    (second named story)
6: SEEING     (second exercise)
7: TEST
8: COSTUME    (third named story)
9: LIGHT      (compression + permission)
10: ENGINE    (deeper angle teaching)
11: NAMING
12: THRESHOLD
```

**Alternatives the operator may prefer:**

- 12 chapters with 4 COSTUME chapters (one per quartile) instead of 3
- 12 chapters with a single SEEING at chapter 6 (rather than two, at 3 and 6)
- A LIGHT chapter at position 6 (mid-book breathing room) instead of position 9

**Recommendation from spec:** the proposed sequence echoes the operator's diagnosis (three
named characters, two sustained exercises, distinct LIGHT/NAMING/THRESHOLD closing arc). If the
operator wants different cadence, the yaml supports overrides without code change.

### P2 — Bestseller structure assignment under v2

**Q:** Does the existing `assign_bestseller_structures` (`chapter_planner.py:211-266`) continue
to run alongside the new chapter_role assignment, or does v2 replace it?

- Coexist (spec proposal): chapter has both a `role` (drives atom shapes) AND a
  `bestseller_structure` (drives beat order within the slot row). The two planning dimensions
  are independent.
- Replace: under v2, the role IS the bestseller structure (e.g. COSTUME → `gladwell_spiral` is
  always; SEEING → `atomic` is always).

**Recommendation from spec:** coexist. The bestseller structure governs micro-rhythm at the
sentence/paragraph level; the chapter role governs macro-architecture. The two are orthogonal.
Test this assumption by re-rendering the canary and observing whether the existing bestseller
phase pools produce sensible structures inside each role.

---

## §6 — Acceptance criteria for the Phase B implementation

When all of these pass on the ahjan × gen_z_professionals × anxiety × deep_book_6h canary:

- [ ] `chapter_architecture_version: 2` accepted on BookSpec
- [ ] `chapter_role_assignment.yaml` exists with deep_book_6h schedule
- [ ] TEACHER_DOCTRINE_INTRO renders before Chapter 1
- [ ] PERMISSION_GRANT renders inside the LIGHT chapter
- [ ] No standalone ellipsis-wrappers in book.txt (grep `\.{3}$` against assembled chapter prose
      yields zero hits where the following line is not a TEACHER_DOCTRINE / COMPRESSION / DOCTRINE_INTRO
      atom)
- [ ] COSTUME-role chapters contain ≥1 STORY atom ≥800 words (or warning emitted if pool insufficient)
- [ ] No chapter exceeds 15 atoms
- [ ] Each chapter's word count is within the role's target range (§2.3 table)
- [ ] Existing v1 books in `artifacts/pipeline_examples/` re-render byte-identical under
      `chapter_architecture_version: 1`
- [ ] The miki book re-renders under `chapter_architecture_version: 2` with near-identical
      output (modulo metadata) — sanity check that v2 captures the reference shape

When the canary passes acceptance, the operator opts in additional deep_book_6h books one at a
time.

---

## §7 — Cross-references

- `docs/specs/ANGLE_REGISTRY_SSOT_V2_SPEC.md` — angle registry v2 with parent_universal
  inheritance + journey blocks. The ENGINE-role chapter consumes the journey block's
  `named_object` for the chapter's mechanism reveal.
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (§570-577) — canonical Pearl_Prime CLI
  contract. v2 architecture rides on top of this.
- `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` (§3-4) — fail-early gate behavior;
  v2 introduces parallel gates (chapter_role_flow) without replacing the legacy chapter_flow.
- `phoenix_v4/planning/chapter_planner.py` — current planner. v2 extends; does not replace.
- `phoenix_v4/planning/beatmap_compile.py:42-53` — `SOMATIC_10_SLOT_GRID` (v1). v2 introduces
  per-role slot rows.
- `phoenix_v4/rendering/chapter_composer.py` — current composer. v2 extends with
  wrapper-completion check, PERMISSION_GRANT emission, TEACHER_DOCTRINE_INTRO emission.
- `config/catalog_planning/teacher_wrapper_templates.yaml` — current wrapper templates.
  v2 adds `completion_required` + `completion_atom_shapes`.
- `artifacts/pipeline_examples/miki/book_miki_imposter_syndrome_15min.txt` — primary reference
  model. 4-chapter holistic shape, ~6,000 words total.
- `artifacts/pipeline_examples/joshin/book_joshin_anxiety_15min.txt` — secondary reference; Zen
  mirror frame, 4-chapter THE MIRROR / THE REFLECTION / THE SITTING / THE RETURN arc.
- `artifacts/pipeline_examples/ahjan/book_ahjan_anxiety_15min.txt` — tertiary reference;
  Theravada alarm frame, 4-chapter THE ALARM / THE PATTERN / THE PRACTICE / THE RETURN arc.

---

## §8 — Operator decisions captured at spec-write time

1. **Holistic chapter architecture is the diagnosis.** The 6h pipeline is broken at the
   architecture layer, not the atom layer. Per OPDs 129–133, the fix is structural.
2. **Chapter as narrative unit, not slot grid.** Each chapter develops ONE dominant role
   across sustained atoms, not all 10 slot-roles every chapter.
3. **8 canonical roles cover all runtimes.** WITNESS / COSTUME / SEEING / LIGHT (the miki four)
   extend to ENGINE / TEST / NAMING / THRESHOLD for longer runtimes.
4. **TEACHER_DOCTRINE_INTRO is a new atom shape.** Per OPD-130. Renders before Chapter 1.
   Equivalent of miki's "A NOTE ON THE TEACHINGS" preamble.
5. **PERMISSION_GRANT is a new atom shape.** Per OPD-133. Renders inside LIGHT chapter.
   Format: 5–8 "you are allowed to ___" lines.
6. **Wrappers ending in ellipsis must be followed by a completing atom or DROPPED.**
   Per OPD-132. No standalone ellipsis fragments.
7. **Fewer + longer atoms.** Per OPD-129. Cap 15 atoms/chapter, avg 400–600 words/atom,
   STORY atom floor 800 words for deep_book_6h COSTUME role.
8. **v2 opt-in via BookSpec field.** Default = v1 (current behavior preserved). v2 enables the
   holistic architecture. Migration is per-book at operator's discretion.

---

## §9 — Out of scope for this spec

- Authoring the actual TEACHER_DOCTRINE_INTRO atoms — Pearl_Editor commissions
- Authoring the actual PERMISSION_GRANT atoms — Pearl_Editor commissions
- Authoring long-form (≥800w) STORY atoms for the COSTUME role — Pearl_Editor commissions
- Implementing the planner / composer code changes — Phase B (separate PR)
- Tests for the implementation — Phase B (separate PR)
- Bestseller structure assignment changes under v2 — see §5 P2 (operator decision needed first)
- v2 → v1 fallback when atom pool is too short for v2 — defer to Phase C
- Visual identity per chapter role (cover art, chapter break glyph) — deferred (similar to angle
  visual identity in `ANGLE_REGISTRY_SSOT_V2_SPEC.md` §11.4)

---

**End of spec.**
