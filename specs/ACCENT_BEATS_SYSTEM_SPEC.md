# Accent Beats System Spec — Planner-Placed Chapter Elements

**Version:** 1.2.0 (V2.1 layer amendment)
**Date:** 2026-07-13 (amended; originally 2026-07-07)
**Authority:** Pearl_Research + Pearl_Architect; layer model superseded by [ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md](../docs/ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md) — **read that doc first**
**Status:** SPECCED (inventory + design only — no pipeline, composer, bank authoring, or flagship changes in this PR)
**GATE:** `flagship-read-approved` (golden-#2 freeze merged) before any build lane opens
**Implements:** Operator mission — planner-placed chapter elements (quotes, encouragement, reflection questions, evidence, external stories, callbacks, analogy/metaphor) that appear **sparsely and intelligently** where sparse is correct, and **reliably** where they are not optional, increasing catalog variation without reintroducing template glue.

**Build order after flagship read:** cast_structure + renditions wired → four-layer contract planned + banks seeded → composer consumer + gates → book-#2/#3 pilot read against no-accent sibling.

**Doctrine (non-negotiable):** Every element in this spec is **planner-assigned, never composer-improvised**, regardless of which of the four layers it belongs to. Framing lives **inside the atom** — entry and exit authored per position variant. Composer-injected wrappers are **banned** (same scar as `COMPOSER_DEINJECTION_AND_TISSUE_SPEC_2026-07-05.md`).

## §0.1 — V2.1 correction: this is not one flat "accent" bucket

**Read this before authoring anything from this spec.** The original v1.0/v1.1 version of this document (and the phrase "accent beats" in its title) treated all eight classes below as one undifferentiated, sparsity-governed "accent" bucket. That was wrong, and it produced writer guidance that implied evidence, troubleshooting, and external stories were decorative extras subject to the same "keep it sparse" instinct as a quote or a wisdom line. They are not.

Phoenix authoring now separates **four layers**. Only one of them is optional and sparse.

| Layer | What it is | Sparse? | Classes covered by this spec |
|-------|------------|---------|-------------------------------|
| **`chapter_engine`** | Elements that make a chapter work at all | **No** — expected in most/every chapter | `TROUBLESHOOTING` (this spec); `VALIDATION_NORMALIZATION`, `MECHANISM_EXPLANATION`, `PRACTICE_APPLICATION`, `TRANSITION_GLUE`, `CLOSING_TAKEAWAY`, `PROPULSION` (core spine, out of this spec's scope) |
| **`proof_and_embodiment`** | Elements that make the teaching credible or lived | **No** — required per profile minimums | `EXTERNAL_STORY`, `AUTHOR_DISCLOSURE`, `CITED_EVIDENCE` (this spec); `HOOK_STORY`, `CASE_STUDY` (core spine) |
| **`optional_accents`** | Sparse rhetorical flourishes | **Yes** — this is where the sparsity doctrine lives | `QUOTE`, `ENCOURAGEMENT`, `REFLECTION_QUESTION`, `AUTHOR_COMMENTARY`, `WISDOM_ESSENCE` |
| **`cohesion_and_craft`** | Devices that make the book feel threaded | **No** — tracked, not budgeted like an accent | `CALLBACK_PLANT`, `CALLBACK_RETURN`, `ANALOGY`, `METAPHOR`, `MOTIF` |

**If you take one thing from this correction:** the "sparse, intentional" doctrine in §0 below is real and stays real — but it applies to `optional_accents` only. `TROUBLESHOOTING`, `CITED_EVIDENCE`, `EXTERNAL_STORY`, and `AUTHOR_DISCLOSURE` are load-bearing chapter content with their own minimums, not accents you are being asked to ration.

`AFFIRMATION` remains not-live (TODO mantras only) and is excluded from all four layers until Pearl_Editor commissions real content — see §1.

---

## §0 — Problem statement

The twelve-shape spine + doctrine + story + exercise stack covers most classic self-help chapter anatomy. What remains missing or buried is the **accent layer** — the sparse, high-signal moments readers associate with premium books: an opening quote keyed to the chapter's teaching, a permission beat after a hard exercise, a reflection question before the thread, troubleshooting when integration fails in real life.

Today:

- **Encouragement** exists as dormant `PERMISSION` / `PERMISSION_GRANT` banks with structure-system hooks (`BESTSELLER_STRUCTURES.md` PERMISSION column) but is wired as a **structure-default slot**, not a **sparse planner accent**.
- **Reflection questions** appear inside doctrine closers and scattered CJK TAKEAWAY atoms — not as placeable beats.
- **Troubleshooting** lives inside INTEGRATION prose — not addressable as its own moment.
- **Quotes** and **cited evidence** have no bank, no beat class, no verification gate.

Without a governed accent system, two failure modes recur:

1. **Template glue** — composer wraps quotes/encouragement in injected "Let's begin with the words of…" scaffolding.
2. **Accent spam** — every chapter 7 gets a quote; accents become a fancier template.

This spec defines the **inverse**: planned, sparse, framed placement.

---

## §1 — Coverage inventory (15 classic self-help elements)

Six-layer taxonomy: `ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`.

| # | Classic element | Existing machinery | Accent class (if any) | Layer | Gap / action |
|---|-----------------|-------------------|----------------------|-------|--------------|
| 1 | **Promise** | `ANGLE_DEFINITION`, HOOK objects, twelve-shape `shape:` per plan, doctrine rotation | — (core spine) | **EXECUTED-REAL** | None — not an accent |
| 2 | **Pain points** | HOOK void-openers, SCENE embodiment, `chapter_continuity_plan` `object:` | — (core spine) | **EXECUTED-REAL** | None |
| 3 | **Framework / mechanism** | `doctrine_id`, COMPOSITE_DOCTRINE bank, REFLECTION teaching blocks, PIVOT | — (core spine) | **EXECUTED-REAL** | None |
| 4 | **Teaching / doctrine** | `SOURCE_OF_TRUTH/composite_doctrine/<topic>/REFLECTION/` (15 anxiety live), `doctrine_rotation.yaml` | — (core spine) | **EXECUTED-REAL** | Renditions layer (separate spec) reduces verbatim reuse |
| 5 | **Stories / examples** | `story_picks` (recognition / mechanism_proof / turning_point), [STORY_CRAFT_CONTRACT](../docs/STORY_CRAFT_CONTRACT_2026-07-07.md) | — (core spine) | **CODE-WIRED** + **SPECCED** craft bar | Cast_structure (parked) varies who carries stories |
| 6 | **Exercises / practices** | 311-item practice library (`practice_items.jsonl`), `exercise_id` per chapter, five-layer components | — (core spine) | **EXECUTED-REAL** | Journey attach partially dormant in baseline snapshots |
| 7 | **Integration / action steps** | INTEGRATION slot, `connective_picks.INTEGRATION`, twelve-shape plans | — (core spine) | **EXECUTED-REAL** | None |
| 8 | **Summaries / takeaways** | TAKEAWAY slot; COMPRESSION slot in composer order (`chapter_composer.py` :6–7) | `COMPRESSION` stays **spine-optional**, not accent | **CODE-WIRED** (composer reads slot) / **CONFIG-EXISTS** (1,272 persona COMPRESSION dirs) | COMPRESSION is format-driven, not planner-sparse; do not fold into accent budget |
| 9 | **Reflection questions** | Doctrine closers ("What is your climate today?" in `COMPOSITE_DOCTRINE v*`), CJK TAKEAWAY/SCENE `**Reflection Question:**` blocks | **`REFLECTION_QUESTION`** (new accent) | **EXECUTED-REAL** (embedded) → **SPECCED** (placeable) | Extract / author as accent atoms; plan assigns chapters |
| 10 | **Encouragement / permission** | `PERMISSION` (245 teacher-bank YAMLs + 64 persona dirs), `PERMISSION_GRANT` (64 persona `CANONICAL.txt` trees), Writer Spec §4.8, `BESTSELLER_STRUCTURES.md` PERMISSION column, composer `:3282–3285` | **`ENCOURAGEMENT`** ← reuse PERMISSION/PERMISSION_GRANT with accent semantics | **EXECUTED-REAL** (content) / **CODE-WIRED** (structure-default render) | Re-key from structure-default to **planner-sparse**; distinguish permission (chapter-cost) vs encouragement (post-exercise) |
| 11 | **Mantras / affirmations** | `config/angles/angle_registry.yaml` → `journey.core_mantras` (15 angles × TODO stubs) | **`AFFIRMATION`** ← reuse mantra content shape | **CONFIG-EXISTS** (schema) / **ABSENT** (authored mantras) / **NOT LIVE** in runtime | Do **not** claim AFFIRMATION is shipping; keep budget at 0 until Pearl_Editor commissions real mantras |
| 12 | **Quotes** | ~22 orphan `atoms/<persona>/<topic>/QUOTE/CANONICAL.txt` (retired per `QUOTE-ATOM-ROUTING-01`); **no verified bank** | **`QUOTE`** (new accent + new bank) | **ABSENT** (verified) / **RESEARCHED** (orphan content) | Pearl_Research bank program; **not** 11th grid slot — accent overlay only |
| 13 | **Case studies / cited evidence** | Fictional vignettes in STORY; Gladwell Spiral structure cites stats in `BESTSELLER_STRUCTURES.md` examples only | **`CITED_EVIDENCE`** (new accent + new bank) | **SPECCED** (structure examples) / **ABSENT** (bank + gate) | Pearl_Research claims ledger; distinct from fictional STORY |
| 14 | **Obstacles / troubleshooting** | INTEGRATION prose ("chest will object", "forget for three rooms/meetings") — e.g. `atoms/gen_z_professionals/anxiety/INTEGRATION/CANONICAL.txt` | **`TROUBLESHOOTING`** (new accent) | **EXECUTED-REAL** (embedded) → **SPECCED** (placeable) | Extract standalone beats keyed to `exercise_id` / `object` |
| 15 | **Forward thread / continuity** | THREAD slot (Writer Spec §4.7a), INTEGRATION-final placement | — (core spine) | **CODE-WIRED** | None — REFLECTION_QUESTION sits **before** THREAD, not replacing it |

### 1.1 Work split estimate

| Category | Share | Classes |
|----------|-------|---------|
| **Dormant asset wiring** | ~70% | ENCOURAGEMENT, REFLECTION_QUESTION, TROUBLESHOOTING (content partially exists). **AFFIRMATION remains deferred** (TODO mantras only). |
| **Genuinely new** | ~30% | QUOTE, CITED_EVIDENCE (banks + verification + gates) |

**Verified:** Only QUOTE and CITED_EVIDENCE require new bank programs from zero. All other accent classes reuse or refactor existing prose/assets.

### 1.2 Relationship to QUOTE-ATOM-ROUTING-01

The 2026-05-06 decision retired persona-keyed `QUOTE/` dirs as non-canonical 10-grid orphans. **This spec does not reopen the 10-slot grid.** QUOTE returns as an **accent overlay** with:

- Planner assignment in `accent_beats:` (not `connective_picks`)
- Verified primary-source bank (`SOURCE_OF_TRUTH/accent_banks/quote/`)
- Attribution gate (§6)

Orphan `QUOTE/CANONICAL.txt` files are **candidate content** for Pearl_Editor review — not routable until re-authored into the accent bank with verification metadata.

---

## §2 — Element classes across the four layers

Ten classes tracked by this spec (eight original + **WISDOM_ESSENCE** + **AUTHOR_COMMENTARY** v1.1, plus **EXTERNAL_STORY** and **AUTHOR_DISCLOSURE** added in the V2.1 amendment). Each is a **complete authored paragraph unit** with position variants — never a bare quote line plus composer wrapper. Per §0.1, only five of these ten are `optional_accents`; the rest are `chapter_engine` or `proof_and_embodiment` and are not subject to the sparsity budget.

### 2.1 Shared schema (`accent_atom.yaml`)

```yaml
accent_class: QUOTE | ENCOURAGEMENT | REFLECTION_QUESTION | AFFIRMATION | TROUBLESHOOTING | CITED_EVIDENCE | WISDOM_ESSENCE | AUTHOR_COMMENTARY
accent_id: quote_anxiety_stoic_v01__opener
topic_keys: [anxiety, overthinking]          # doctrine/topic affinity
doctrine_keys: ["COMPOSITE_DOCTRINE v03"]   # optional; QUOTE/CITED_EVIDENCE typically required
exercise_keys: [med_007]                    # ENCOURAGEMENT, TROUBLESHOOTING
object_keys: [after_send_reply_anxiety]     # continuity object affinity

allowed_positions:
  - before_HOOK      # chapter open (QUOTE opener only)
  - after_EXERCISE   # ENCOURAGEMENT primary
  - after_REFLECTION # REFLECTION_QUESTION primary
  - after_INTEGRATION # TROUBLESHOOTING primary
  - before_THREAD    # REFLECTION_QUESTION alternate
  - after_turning_point # ENCOURAGEMENT alternate (story handoff)

keys_to:
  doctrine: true|false
  exercise: true|false
  object: true|false
  story_beat: turning_point|null

position_variants:
  opener:
    body: |
      Let's begin with words that have held this teaching longer than any app on your phone.
      "Between stimulus and response there is a space." — Viktor Frankl, *Man's Search for Meaning* (1946).
      Carry that space into what happens next in this room.
  closer:
    body: |
      ...alternate exit framing pointing into THREAD...

framing_rule: INSIDE_ATOM_ONLY   # mandatory; gate-enforced
composer_wrapper_allowed: false  # mandatory

# QUOTE + CITED_EVIDENCE only:
attribution:
  author: Viktor Frankl
  work: Man's Search for Meaning
  year: 1946
  primary_source_verified: true
  verification_ref: pearl_research/claims/quote_frankl_stimulus_response_v01.json
  rights: public_domain | licensed | fair_use_doc_ref

# CITED_EVIDENCE only:
claim_ledger:
  claim_id: nhis_sleep_difficulty_2020
  statement: "14.5% of US adults reported trouble falling asleep (2020 NHIS)"
  source: CDC/NCHS NHIS 2020
  year: 2020
  accuracy_review_date: 2026-07-01
  stale_after: 2028-01-01
```

### 2.2 Class definitions

Layer column added in the V2.1 amendment — use it to decide whether an element is subject to the sparsity budget (§4.3) or not.

| Class | Layer | Reuse source | Purpose | Default allowed positions | Must key to |
|-------|-------|--------------|---------|---------------------------|-------------|
| **QUOTE** | `optional_accents` | New bank | Credibility + tonal entry/exit; doctrine echo | `before_HOOK`, `after_INTEGRATION` (closer) | `doctrine_id` or chapter `angle_id` |
| **ENCOURAGEMENT** | `optional_accents` | `PERMISSION` / `PERMISSION_GRANT` atoms | Post-effort recognition — "You just sat with that for two minutes" | `after_EXERCISE`, `after_turning_point` | `exercise_id` or story `turning_point` pick |
| **REFLECTION_QUESTION** | `optional_accents` | Doctrine closers, CJK reflection blocks | Reader pause before thread | `after_REFLECTION`, `before_THREAD` | `doctrine_id` or `object` |
| **AFFIRMATION** | *(excluded — not live)* | `angle_registry.yaml` `core_mantras` | Short repeatable phrase; angle journey surface (**NOT LIVE** — TODO stubs only; excluded from `ALL_ACCENT_CLASSES` and from every layer until commissioned) | `after_PIVOT`, `before_INTEGRATION` | `angle_id` |
| **TROUBLESHOOTING** | `chapter_engine` — **not an accent, not sparsity-budgeted** | INTEGRATION obstacle paragraphs | "When you forget for three days…" — reader support after a hard ask, not a flourish | `after_INTEGRATION` | `exercise_id` + `object` |
| **CITED_EVIDENCE** | `proof_and_embodiment` — **not an accent, not sparsity-budgeted** | New bank | Named study/stat moment (not fiction); credibility, not decoration | `after_HOOK`, `before_STORY` (Gladwell Spiral alignment) | `doctrine_id` + claim ledger |
| **EXTERNAL_STORY** | `proof_and_embodiment` — **not an accent, not sparsity-budgeted** | New bank (`accent_banks/external_story/`) | Real or disclosed-composite case that proves the mechanism outside the book's own cast; alternates `recognition` and `mechanism_proof` function across a book | `after_HOOK` (story-led open) or middle-body | `story_function` (§2.2a) + `story_metadata` (§10 of the V2.1 doc) |
| **AUTHOR_DISCLOSURE** | `proof_and_embodiment` — **not an accent, not sparsity-budgeted** | New bank (`accent_banks/author_disclosure/`); distinct from `AUTHOR_COMMENTARY` | Author reveals something experienced, feared, misunderstood, attempted, or learned — first-person lived proof, not interpretation | `after_REFLECTION`, `after_PIVOT` | `author_id` + `disclosure_function` (§2.2b) + bio license |
| **WISDOM_ESSENCE** | `optional_accents` | New bank (`accent_banks/wisdom_essence/`) | Traditions' distilled voice — corpus-convergent themes, not teacher doctrine | `after_REFLECTION`, `before_THREAD` | `topic_keys` + `doctrine_keys` + `theme`; `source_teachers` audit only |
| **AUTHOR_COMMENTARY** | `optional_accents`; distinct from `AUTHOR_DISCLOSURE` | New bank (`accent_banks/author_commentary/`) | Author *interprets* what the reader just encountered — orientation, permission, emphasis, boundary, transition. Not the author's own experience (that is `AUTHOR_DISCLOSURE`) | `after_REFLECTION`, `after_EXERCISE`, `after_PIVOT`, `before_THREAD` | `author_id` + `topic_keys`; bio-licensed |

### 2.2a EXTERNAL_STORY function tags (required)

Every `EXTERNAL_STORY` atom must carry exactly one `story_function`:

| Function | Use it when the story… |
|----------|--------------------------|
| `recognition` | Makes the reader feel seen — "someone else lives this too" |
| `mechanism_proof` | Demonstrates the chapter's mechanism working (or failing) in a real case |
| `turn` | Shows the moment a person's trajectory changed |
| `possibility` | Shows an outcome the reader can imagine for themselves |
| `cautionary` | Shows the cost of not acting, or acting wrong |

For anxiety-profile books, alternate `recognition` and `mechanism_proof` across the book rather than clustering one function early and abandoning it — see §14.2.

### 2.2b AUTHOR_DISCLOSURE functions (required)

Every `AUTHOR_DISCLOSURE` atom must carry exactly one `disclosure_function`: `credibility`, `vulnerability`, `companionship`, `failure_model`, `turning_point`, or `limits_of_authority`. Before shipping a disclosure, apply the test from the V2.1 doc §11.1: *"Does this disclosure help the reader understand themselves, or does it merely make the author more visible?"* If it's the latter, cut it or convert it to `AUTHOR_COMMENTARY`.

### 2.3 WISDOM_ESSENCE schema extensions

`WISDOM_ESSENCE` atoms extend the shared schema with register variants and corpus audit fields. **Hard boundary:** `WISDOM_ESSENCE ≠ TEACHER_DOCTRINE`. Composite books receive planner-placed accent atoms only; mode-bleed gate (OPD-115) is **untouchable**.

```yaml
# WISDOM_ESSENCE extensions on accent_atom.yaml
essence_id: we_anx_body_first_awareness_v01
theme: body_first_awareness                    # corpus-convergent theme (≥3/6 teachers)
source_teachers: [ahjan, junko, sai_ma, master_wu]  # audit trail — not rendered in composite
source_refs:                                   # TEACHER_DOCTRINE atom IDs backing convergence
  - ahjan_TEACHER_DOCTRINE_000
secular_safe: true                             # required for composite-mode assignment
dosage_class: sparse_flair                     # default sparse; max 2/book secular
register_variants:
  secular:                                     # (a) composite default — no teacher/tradition names
    body: |
      ...complete TTS paragraph with entry framing + exit handoff...
  wisdom_traditions:                           # (b) distilled lines — still no named teachers
    examples:
      - "The body registers before the mind explains — look there first."
  tradition_attributed:                        # (c) teacher-mode only — tradition named, not quoted doctrine
    examples:
      - "In the forest contemplative line, awareness begins at sensation, not belief."
```

**Register rules (gate-enforced):**

| Variant | Mode | Render rule |
|---------|------|-------------|
| **(a) `secular`** | composite + teacher_mode | Full paragraph; **zero** teacher/tradition names |
| **(b) `wisdom_traditions`** | composite + teacher_mode | Short distilled lines; no named teachers |
| **(c) `tradition_attributed`** | **teacher_mode only** | Tradition-flavored attribution; never `TEACHER_DOCTRINE` prose |

### 2.4 Framing-inside-the-atom rule

**Banned:** composer functions that prepend/append accent wrappers (same class of failure as `bridge_transition_families.yaml` glue).

**Required:** each `position_variant.body` is one coherent TTS paragraph unit containing:

1. **Entry framing** — orients the reader (opener vs closer register differs)
2. **Core content** — quote line, question, permission statement, stat
3. **Exit handoff** — last sentence points to the **next spine beat** by name ("Carry that question into the scene that follows." / "Now notice what your chest does when you try this tonight.")

Gate `check_accent_framing_in_atom.py` (proposed): FAIL if rendered accent text is concatenated with any string from `config/rendering/*_families.yaml` or if atom body lacks exit-handoff pattern for assigned position.

### 2.5 Truth and provenance for EXTERNAL_STORY and CITED_EVIDENCE (required)

Function tagging (§2.2a) is necessary but not sufficient. Every `EXTERNAL_STORY` atom also carries `story_metadata`:

```yaml
story_metadata:
  function: recognition | mechanism_proof | turn | possibility | cautionary
  source_type: documented_public_case | author_provided_story | interviewed_subject |
               anonymized_real_story | disclosed_composite | explicitly_hypothetical_example
  source_reference: "..."          # citation, interview record, or composite-disclosure note
  identity_handling: anonymized | named_with_consent | public_figure | not_applicable
  factuality_status: verified | unverified_reported | explicitly_hypothetical
```

**Hard rule: never invent a person and imply they are a real case.** If a story is invented for illustration, it must be tagged `source_type: explicitly_hypothetical_example` and written so the reader is not misled into thinking it is a documented case. `disclosed_composite` (a plausible blend of real patterns, disclosed as such) is allowed; a composite presented as one real, unnamed individual is not.

`CITED_EVIDENCE` atoms carry the matching `evidence_metadata` block (source tier, evidence strength, `limitations_acknowledged: true`). A chapter needing evidence should reach for **two accurately-framed, limitation-aware citations** over five thin ones — precision beats volume.

### 2.6 CALLBACK, ANALOGY, METAPHOR — cohesion and craft (tracked, not accent-budgeted)

These are `cohesion_and_craft`, the fourth layer (§0.1). They are planned like everything else in this spec, but they are never counted against the `optional_accents` sparsity budget in §4.3, and they are not optional in the sense of "the book is fine without them" — a book with zero callbacks reads as episodic.

**CALLBACK_PLANT / CALLBACK_RETURN.** A callback is a two-sided contract: something planted early, returned later, changed by the return. Every `CALLBACK_RETURN` requires:

```yaml
callback:
  plant_id: "caged-bird-image"
  planted_in_chapter: 1
  returned_in_chapter: 7
  return_function: remind | deepen | reinterpret | invert | transfer | resolve | close
  semantic_development: "from trapped nervous system to protective adaptation"
```

A return that merely repeats the planted phrase without `semantic_development` is not a callback — it is a tic. If you cannot articulate what changed between the plant and the return, don't write the return yet.

**ANALOGY and METAPHOR must explain, compress, or thread — never decorate.** Before writing one, ask: *does this make the mechanism easier to hold in the reader's head, or is it just a pretty sentence?* A recurring metaphor that is planted once and returned to later (functioning as a callback) is stronger than a fresh metaphor in every chapter. Count only `major_explanatory_analogy` and `developed_or_recurring_metaphor` units — not every figurative sentence.

### 2.6a PARABLE — sparse story register, not a generic accent

`PARABLE` is not its own accent class and does not get its own budget line. It is a **story register** that can appear inside `HOOK_STORY` or `EXTERNAL_STORY` when the profile calls for it (`timeless_wisdom` profiles use it most; `practical_credible` and the anxiety flagship hybrid use `parable_uses: 0` or `0-1`). If you are tempted to reach for a parable in a mechanism-forward, practical-credible chapter, don't — reach for `EXTERNAL_STORY` with `mechanism_proof` function instead.

---

## §3 — Placement grammar

Accent beats **insert between** spine slots; they do not replace HOOK/STORY/EXERCISE/INTEGRATION/THREAD.

### 3.1 Spine reference (twelve-shape chapter)

Canonical order in composer (`chapter_composer.py`):

```
HOOK → SCENE/STORY beats → REFLECTION → bridge → EXERCISE → COMPRESSION? →
PERMISSION? (legacy structure slot) → INTEGRATION → TAKEAWAY → THREAD
```

Accent insertion points (when plan assigns):

```
[QUOTE opener] → HOOK → … → REFLECTION → [REFLECTION_QUESTION] →
bridge → EXERCISE → [ENCOURAGEMENT] → COMPRESSION? → INTEGRATION →
[TROUBLESHOOTING] → TAKEAWAY → [REFLECTION_QUESTION alt] → THREAD →
[QUOTE closer]
```

`[CITED_EVIDENCE]`, `[AFFIRMATION]`, `[WISDOM_ESSENCE]`, and `[AUTHOR_COMMENTARY]` insert per class `allowed_positions` with the same handoff rule.

### 3.2 Per-class placement rules

| Class | May sit | Must reference | Handoff (last line →) |
|-------|---------|----------------|------------------------|
| **QUOTE** | `before_HOOK` or post-`TAKEAWAY` pre-`THREAD` | Chapter `doctrine_id` or `angle_id` | Opener → SCENE/HOOK; Closer → THREAD |
| **ENCOURAGEMENT** | Immediately after EXERCISE or after story `turning_point` | `exercise_id` or `story_picks.turning_point` | INTEGRATION or next story beat |
| **REFLECTION_QUESTION** | After REFLECTION or before THREAD | `doctrine_target` or `object` | STORY/EXERCISE or THREAD |
| **AFFIRMATION** | After PIVOT or before INTEGRATION | `angle_id` + `core_mantras` entry | INTEGRATION |
| **TROUBLESHOOTING** | After INTEGRATION | `exercise_id` + `object` | TAKEAWAY |
| **CITED_EVIDENCE** | After HOOK (Gladwell) or before first STORY | `claim_ledger.claim_id` + doctrine | STORY scene |
| **WISDOM_ESSENCE** | After REFLECTION (coda) or before THREAD (grace note) | `theme` + `doctrine_keys` + `topic_keys` | EXERCISE / STORY or THREAD |
| **AUTHOR_COMMENTARY** | After REFLECTION, after EXERCISE, after PIVOT, or before THREAD | `author_id` + `topic_keys` + `bio_license_refs` | EXERCISE / INTEGRATION / THREAD |

### 3.3 Invariants (gates)

1. **Planner-assigned only** — no accent renders unless `accent_beats` entry exists for `(chapter, accent_class)`.
2. **At most one accent per class per chapter** — no double-quote chapters unless plan explicitly lists two classes (quote + encouragement OK; two quotes not).
3. **No accent-only chapters** — every chapter with accents still carries full spine slots.
4. **Structure PERMISSION decoupled** — `BESTSELLER_STRUCTURES.md` PERMISSION column becomes a *hint* for planner; renderer prefers `accent_beats.ENCOURAGEMENT` when present, falls back to legacy PERMISSION slot only when plan marks `legacy_permission: true` (migration flag).

---

## §4 — Plan schema extension

### 4.1 Book-level `accent_budget` — optional_accents only

**V2.1 correction:** `accent_budget` governs the `optional_accents` layer only. `TROUBLESHOOTING`, `CITED_EVIDENCE`, `EXTERNAL_STORY`, and `AUTHOR_DISCLOSURE` are planned through `chapter_engine_expectations` / `proof_and_embodiment` minimums instead (§4.1a) — do not zero them out to "be sparse."

```yaml
# book_structure_plan / twelve_shape plan header
accent_budget:              # optional_accents layer only
  QUOTE: 3
  ENCOURAGEMENT: 2
  REFLECTION_QUESTION: 3
  AFFIRMATION: 0             # not live — keep at 0 until commissioned
  WISDOM_ESSENCE: 0
  AUTHOR_COMMENTARY: 0
accent_distribution_profile: somatic_reflective  # see §4.3
```

**Default for 12-chapter book:** all zeros in `optional_accents` (no accents) unless the profile calls for them. Pilot (§7) and the anxiety flagship hybrid (§14) are explicit exceptions.

### 4.1a Book-level `proof_and_embodiment` and `cohesion_and_craft` — tracked minimums, not sparsity budgets

```yaml
proof_and_embodiment:
  CITED_EVIDENCE: { minimum: 1, target: 2 }
  EXTERNAL_STORY: { minimum: 2, target: 3 }
  AUTHOR_DISCLOSURE: { minimum: 1, target: 1 }
chapter_engine_expectations:
  TROUBLESHOOTING: { minimum: 1, target: 2 }
cohesion_and_craft:
  callback_or_motif_returns: 5-8   # tracked count, no per-chapter cap
  analogy_or_metaphor_uses: 6-10   # tracked count, no per-chapter cap
```

These fields have **minimums**, not sparsity ceilings — a profile that assigns `EXTERNAL_STORY: { minimum: 0 }` is telling you the book genuinely doesn't need external proof (rare), not that you should ration it down like a quote.

### 4.2 Per-chapter `accent_beats`

```yaml
chapters:
  - chapter: 1
    character: Priya
    doctrine_id: "COMPOSITE_DOCTRINE v03"
  - chapter: 4
    accent_beats:
      - class: QUOTE
        accent_id: quote_anxiety_frankl_v01__opener
        position: before_HOOK
        keys:
          doctrine_id: "COMPOSITE_DOCTRINE v03"
      - class: ENCOURAGEMENT
        accent_id: enc_med007_noting_v02
        position: after_EXERCISE
        keys:
          exercise_id: med_007
  - chapter: 9
    accent_beats:
      - class: REFLECTION_QUESTION
        accent_id: rq_climate_weather_v01
        position: before_THREAD
        keys:
          object: chronic_somatic_tension
```

### 4.2a Global optional-accent slot budget (V2.1, applies across all `accent_distribution_profile` values)

Per the authority doc, class-level maxima in §4.1 are ceilings, not per-chapter quotas, and they must fit inside one coherent book-level slot budget for a standard 12-chapter book:

```yaml
optional_accent_budget:
  target_accent_chapters: 5-7
  hard_max_accent_chapters: 8
  target_total_accents: 7-9
  hard_max_total_accents: 10
  max_accents_per_chapter: 2
  accent_free_chapters_minimum: 4
```

At least 4 of 12 chapters carry **no** `optional_accent` beat. Do not stack `QUOTE + WISDOM_ESSENCE + AUTHOR_COMMENTARY` in one chapter. This budget applies **only** to `optional_accents` — it does not throttle `TROUBLESHOOTING`, `CITED_EVIDENCE`, `EXTERNAL_STORY`, or `AUTHOR_DISCLOSURE`.

### 4.3 Dosage + distribution governance (optional_accents only)

Joins the **experience / anti-spam tuple** ([EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md](./EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md)) as an **8th planning field**:

| Field | Values | Purpose |
|-------|--------|---------|
| `accent_signature` | hash of `(QUOTE_count, ENCOURAGEMENT_count, …, chapter_positions)` | Catalog dedup of accent *pattern*, not prose |

**Per-brand dosage profiles** (`config/accent/brand_accent_profiles.yaml` — proposed):

| Profile | Typical budget (12 ch) | Brands (examples) |
|---------|------------------------|-------------------|
| `somatic_reflective` | RQ: 4, ENC: 3, QUOTE: 1, TROUBLE: 2 | stillness_press, night_reset, stabilizer |
| `commercial_action` | QUOTE: 3, CITED: 2, ENC: 1, TROUBLE: 1 | focus_sprint, high_performer, cognitive_clarity |
| `minimal_accent` | all zeros or QUOTE: 1 only | minimal_mind, brands with high COMPRESSION reliance |

**Wave caps** (extend `config/experience/experience_wave_controls.yaml`):

```yaml
wave_max_identical_accent_signature: 2   # stricter than experience_tuple (3)
max_chapters_with_any_accent_share: 0.35 # no book >35% accent-bearing chapters without review
```

**Sparsity gate:** FAIL if `count(chapters with optional_accent beats) / total_chapters > brand_profile.max_accent_chapter_share` (default **0.25** — at most 3 of 12 chapters carry any `optional_accent` in somatic profile). This gate counts `optional_accents` only — `TROUBLESHOOTING`, `CITED_EVIDENCE`, `EXTERNAL_STORY`, and `AUTHOR_DISCLOSURE` beats do not count toward accent-chapter share.

---

## §5 — Bank programs (Pearl_Research — sized, not started)

### 5.1 QUOTE bank

| Attribute | Spec |
|-----------|------|
| **Location** | `SOURCE_OF_TRUTH/accent_banks/quote/<topic>/` |
| **Policy** | Public-domain-first; licensed quotes require `rights` doc ref; **no quote ships without `primary_source_verified: true`** |
| **Keying** | `topic`, `doctrine_id`, `angle_id`, `register` (somatic vs commercial) |
| **Sizing — pilot** | 12 quotes × 2 position variants = **24 authored units** (anxiety topic) |
| **Sizing — topic complete** | 30 quotes × 2 variants = **60 units/topic** |
| **Sizing — catalog** | 12 topics × 60 = **720 units** (staggered; not blocking scale) |
| **Authoring hours** | ~1.5h/quote (verification + framing) → ~1,080h upper bound full catalog |
| **Pearl_Research deliverable** | Verification ledger `artifacts/research/quote_verification_ledger.jsonl` |

### 5.2 CITED_EVIDENCE bank

| Attribute | Spec |
|-----------|------|
| **Location** | `SOURCE_OF_TRUTH/accent_banks/cited_evidence/<topic>/` |
| **Policy** | Source + year + `claim_ledger`; accuracy review date; `stale_after` → gate WARN/BLOCK |
| **Sizing — pilot** | 6 claims × 2 framing variants = **12 units** (anxiety) |
| **Sizing — topic complete** | 20 claims × 2 = **40 units/topic** |
| **Sizing — catalog** | 12 × 40 = **480 units** |
| **Authoring hours** | ~2h/claim (research + framing) → ~960h upper bound |
| **Pearl_Research deliverable** | `artifacts/research/claims_ledger.jsonl` (shared with Pearl News research infra where possible) |

### 5.3 Reuse banks (no new program — wiring only)

| Class | Existing pool | Count (repo today) | Wiring effort |
|-------|---------------|-------------------|---------------|
| ENCOURAGEMENT | `teacher_banks/*/PERMISSION/*.yaml` + `atoms/*/*/PERMISSION/` | 245 + 64 persona trees | Re-tag + position variants; ~40% need exit-handoff upgrade |
| ENCOURAGEMENT (long) | `atoms/*/*/PERMISSION_GRANT/CANONICAL.txt` | 64 dirs | Map to post-exercise encouragement; split permission-grant vs encouragement by plan |
| REFLECTION_QUESTION | Doctrine closers + CJK atoms | ~15 doctrine + scattered | Extract ~30 RQ candidates for anxiety pilot |
| AFFIRMATION | `angle_registry.yaml` `core_mantras` | 15 angles × 3–5 (TODO) | Pearl_Editor commission: **45–75 mantras** |
| TROUBLESHOOTING | INTEGRATION obstacle paragraphs | ~12 high-quality EN patterns | Extract + key to `exercise_id`/`object` |

### 5.4 WISDOM_ESSENCE bank

| Attribute | Spec |
|-----------|------|
| **Location** | `SOURCE_OF_TRUTH/accent_banks/wisdom_essence/<topic>/entries.yaml` |
| **Research** | [artifacts/research/WISDOM_ESSENCE_ESSENCE_MAP_2026-07-07.md](../artifacts/research/WISDOM_ESSENCE_ESSENCE_MAP_2026-07-07.md) — corpus convergence across six teacher-mode teachers; EI v2 `domain_thesis_similarity` offline scoring |
| **Policy** | Corpus-convergent themes (≥3/6 teachers at EI v2 ≥0.35); **not** persona-keyed doctrine; composite uses `secular` register only |
| **Keying** | `theme`, `topic_keys`, `doctrine_keys`, `position_fit`, `dosage_class` |
| **Sizing — pilot** | 12 essence entries × 3 register variants = **36 authored units** (anxiety topic) |
| **Sizing — topic complete** | 10 themes × 3 variants = **30 units/topic** |
| **Dosage default** | **0–1/book** secular; max **2/book**; variant (c) teacher-mode only (Q-WISDOM-02) |
| **Status** | `status: unwired` / `KNOWN_UNWIRED: accent_banks/wisdom_essence/` until build lane |
| **Pearl_Research deliverable** | Essence map (linked); `source_refs` audit per entry |

**Excluded themes (non-convergent / non-secular):** lineage-specific mechanics (Dragon Vein geomancy, light-language mechanics, Jagadguru lineage, Tao Calligraphy frequency field) — see essence map §Excluded.

---

## §6 — Gates (proposed — build lane)

| Gate | Script (proposed) | BLOCK condition |
|------|-------------------|-----------------|
| Plan assignment | `check_accent_plan_assignment.py` | Rendered accent not listed in `accent_beats` for that chapter |
| Framing in atom | `check_accent_framing_in_atom.py` | Composer wrapper detected OR missing position variant for assigned `position` |
| Quote attribution | `check_quote_attribution.py` | `primary_source_verified != true` OR missing `verification_ref` |
| Claims freshness | `check_cited_evidence_staleness.py` | `stale_after` passed without re-review |
| Sparsity | `check_accent_sparsity.py` | Accent chapter share > brand profile cap OR budget sum ≠ assigned count |
| Anti-spam | extend `check_experience_layer.py` | `accent_signature` collision exceeds wave cap |
| Wisdom essence mode bleed | `check_wisdom_essence_mode_bleed.py` | `secular_safe: false` atom in composite plan OR teacher name in composite `secular` body OR `tradition_attributed` variant in composite plan |
| Wisdom essence doctrine bleed | `check_wisdom_essence_doctrine_boundary.py` | Atom body matches `TEACHER_DOCTRINE` source text OR missing `source_refs` audit |
| Author commentary bio license | `check_author_commentary_bio_license.py` | `bio_license_refs` not satisfiable from author bio YAML |
| Author commentary mode bleed | `check_author_commentary_mode_bleed.py` | `composite_safe: false` atom in composite-mode plan OR teacher name in composite-safe atom body |
| Author commentary register | `check_author_commentary_register.py` | Expert-voice markers or clinical claim patterns |

Register in `scripts/run_production_readiness_gates.py` as gates **#24–#33** (numbers provisional; coordinate with Drift detectors roster at build time).

**Status:** all gates **ABSENT** until build lane; this spec is **SPECCED** only.

---

## §7 — Pilot plan (original v1.1; superseded for anxiety by §14)

**Historical note (V2.1 amendment):** this pilot table predates the four-layer split and still labels `TROUBLESHOOTING` and `CITED_EVIDENCE` as "accent budget" line items. Per §0.1 they are `chapter_engine` / `proof_and_embodiment`, not sparsity-governed accents — read the counts below as chapter-content minimums, not accent moments to ration. For the current anxiety-flagship authoring plan, use §14 and the pilot authoring packet it links to.

**GATE:** `flagship-read-approved` + cast_structure specced (optional composition test).

| Item | Book | Accent budget | Sibling control |
|------|------|---------------|-----------------|
| **Pilot A** | Golden cell book **#2** (`gen_z_professionals × anxiety`, twelve-shape) | QUOTE: 3, ENCOURAGEMENT: 2, REFLECTION_QUESTION: 3, TROUBLESHOOTING: 1 (9 accent moments across 12 chapters; **7 chapters bare**) | Book #1 (flagship) — **zero accents** by policy |
| **Pilot B (optional)** | Book **#3** adjacent cell | CITED_EVIDENCE: 2, AFFIRMATION: 2, QUOTE: 1 | Same persona×topic plan with `accent_budget` all zeros |

**Pilot assignments (illustrative — planner fills at build):**

| Ch | Accent | Position | Keys to |
|----|--------|----------|---------|
| 1 | QUOTE opener | before_HOOK | doctrine v03 |
| 4 | ENCOURAGEMENT | after_EXERCISE | med_016 |
| 6 | REFLECTION_QUESTION | after_REFLECTION | object: pre_presentation_activation |
| 8 | ENCOURAGEMENT | after turning_point | story v23 |
| 10 | QUOTE closer | before_THREAD | doctrine v02 |
| 11 | TROUBLESHOOTING | after_INTEGRATION | med_009 + morning_calendar_spiral |
| 12 | REFLECTION_QUESTION | before_THREAD | angle closure |

**Success criteria (operator read — Layer 2 authored candidate):**

1. Accent moments feel **planned**, not templated — bare chapters read clean without "missing something."
2. No composer wrapper strings in diff vs glue-off baseline.
3. Braided-cast book #2 + quote-opener ch1 + encouragement-after-exercise ch4 reads **nothing like** solo-arc no-accent sibling.
4. Shingle / CTSS gates still pass.

**No flagship edits:** pilot uses book #2/#3 plan YAML only; flagship Priya ch1 snapshot untouched.

---

## §8 — Composition with other parked lanes

| Lane | Interaction |
|------|-------------|
| **cast_structure** | Accents are character-agnostic; braided book with quote-opener + guest-chapter encouragement multiplies perceived variety |
| **rendition_system** | Doctrine renditions reduce verbatim teaching; accents add non-doctrine variation — orthogonal |
| **story_craft_contract** | Troubleshooting/encouragement key to `turning_point` picks — story must carry Contract-complete beats |
| **lesson pilot** | Lessons = doctrine; accents = non-doctrine spice — do not conflate |

---

## §9 — Out of scope (this spec)

- Flagship lane, ch1 snapshot, live composer changes
- Accent atom authoring (Pearl_Writer / Pearl_Editor / Pearl_Research)
- QUOTE / CITED_EVIDENCE bank population
- Composer injection paths or `config/rendering/*` wrapper families for accents
- Declaring any component "working" above **SPECCED**

---

## §10 — Registry and cross-references

| Doc / asset | Role |
|-------------|------|
| [COMPOSER_DEINJECTION_AND_TISSUE_SPEC_2026-07-05.md](./COMPOSER_DEINJECTION_AND_TISSUE_SPEC_2026-07-05.md) | Anti-glue doctrine |
| [BESTSELLER_STRUCTURES.md](../docs/BESTSELLER_STRUCTURES.md) | PERMISSION column → planner hint |
| [PHOENIX_V4_5_WRITER_SPEC.md](./PHOENIX_V4_5_WRITER_SPEC.md) §4.8 | PERMISSION authoring rules |
| [EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md](./EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md) | `accent_signature` tuple extension |
| [RENDITION_SYSTEM_SPEC.md](./RENDITION_SYSTEM_SPEC.md) | Shared-bank variation (parallel lane) |
| [STORY_CRAFT_CONTRACT_2026-07-07.md](../docs/STORY_CRAFT_CONTRACT_2026-07-07.md) | Story beat quality for keyed accents |
| `config/source_of_truth/twelve_shape_chapter_plans/*.yaml` | Plan schema to extend |
| `docs/PEARL_ARCHITECT_STATE.md` QUOTE-ATOM-ROUTING-01 | Orphan QUOTE retirement — accent path supersedes for new work only |

**Data dictionary:** `docs/DATA_DICTIONARY.tsv` is generated by `scripts/governance/build_data_dictionary.py`; accent schema rows appear when config paths land in build lane.

---

## §11 — Acceptance (this spec)

1. Fifteen-element coverage inventory with six-layer labels — §1.
2. Seven accent classes with shared schema + framing rule — §2.
3. Placement grammar + handoff table — §3.
4. Plan schema + dosage / anti-spam — §4.
5. QUOTE + CITED_EVIDENCE bank sizing — §5.
6. Gate inventory — §6.
7. Book-#2/#3 pilot plan — §7.
8. Registered in `specs/README.md`, `docs/DOCS_INDEX.md`, `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`.

**Status claim:** This document is **SPECCED**. Implementation layers remain **ABSENT** until `flagship-read-approved` and follow-on build PRs land.

---

## §12 — WISDOM_ESSENCE (v1.1 amendment)

**Research:** [artifacts/research/WISDOM_ESSENCE_ESSENCE_MAP_2026-07-07.md](../artifacts/research/WISDOM_ESSENCE_ESSENCE_MAP_2026-07-07.md)

**Problem:** Composite books need tradition-flavored depth without importing `TEACHER_DOCTRINE` prose or re-opening `teacher_wrapper` render-glue. Readers recognize convergent wisdom (body-first awareness, noticing without fixing, impermanence-as-weather) across lineages — but no governed accent class has ever shipped that distilled voice as planner-placed beats.

**Critical boundary:** `WISDOM_ESSENCE ≠ TEACHER_DOCTRINE`. Essence atoms are **corpus-convergent distillations** keyed by `theme`, not persona-keyed doctrine slots. Mode-bleed gate (OPD-115 Phase B in `phoenix_v4/planning/enrichment_select.py`) is **untouchable** — composite books receive WISDOM_ESSENCE **only** via `accent_beats` planner assignment.

**Parallel lane:** `AUTHOR_COMMENTARY` (§13) owns the author's witness voice. WISDOM_ESSENCE owns traditions' distilled voice under its own dosage and register rules.

### 12.1 Corpus-convergent themes (anxiety pilot)

Themes scored across six teacher-mode teachers (`ahjan`, `master_wu`, `master_feung`, `junko`, `sai_ma`, `master_sha`) with EI v2 `domain_thesis_similarity` offline scoring. Inclusion bar: **≥3/6 teachers** at EI v2 **≥0.35**.

| Theme | Supporting | Default placement |
|-------|------------|-------------------|
| `body_first_awareness` | 6/6 | `after_REFLECTION` |
| `noticing_without_fixing` | 6/6 | `after_REFLECTION` |
| `bracing_cost` | 6/6 | `after_REFLECTION` |
| `self_compassion_worth` | 6/6 | `before_THREAD` |
| `impermanence_weather` | 6/6 | `after_REFLECTION` |
| `observing_self` | 6/6 | `after_REFLECTION` |
| `already_complete` | 6/6 | `before_THREAD` |
| `suffering_as_pigment` | 6/6 | `after_REFLECTION` |
| `transmission_beyond_mind` | 6/6 | `before_THREAD` |
| `ordinary_life_practice` | 6/6 | `after_REFLECTION` |

**Excluded (non-convergent / non-secular):** Dragon Vein geomancy (`master_wu`-specific); light-language mechanics (`junko`); Jagadguru lineage (`sai_ma`); Tao Calligraphy frequency field (`master_sha`).

### 12.2 Three register variants

| Variant | Key | Composite | Teacher-mode | Render |
|---------|-----|-----------|--------------|--------|
| **(a) Secular** | `register_variants.secular.body` | **Yes** (default) | Yes | Full TTS paragraph; zero teacher/tradition names |
| **(b) Wisdom traditions** | `register_variants.wisdom_traditions.examples` | Yes | Yes | Short distilled lines; no named teachers |
| **(c) Tradition attributed** | `register_variants.tradition_attributed.examples` | **No** | **Yes only** | Tradition-flavored attribution; not doctrine quotation |

**Q-WISDOM-02 default:** variant (c) **disallowed** in secular/composite books.

### 12.3 Mode boundary (gate rule)

| Mode | Teacher/tradition in rendered text | Gate |
|------|-----------------------------------|------|
| **Composite** | **ZERO** named teachers; `secular_safe: true` required; variant (a) or (b) only | `check_wisdom_essence_mode_bleed.py` |
| **Teacher-mode** | Variant (c) allowed; `source_teachers` remain audit-only | `mode_allow` includes `teacher_mode` |

`AUTHOR_COMMENTARY` handles author witness voice; WISDOM_ESSENCE handles tradition-flavored distilled content — **do not conflate**.

### 12.4 Placement + dosage

| Field | Default (12-chapter book) |
|-------|---------------------------|
| `accent_budget.WISDOM_ESSENCE` | **0** (pilot exception) |
| Recommended production default | **0–1/book** secular (Q-WISDOM-01) |
| Secular hard cap | **2/book** |
| Max chapters with any accent share | unchanged (§4.3, default 0.25) |

Joins experience / anti-spam tuple: extend `accent_signature` hash to include `WISDOM_ESSENCE_count`.

**Allowed positions:**

| Position | Register | Handoff → |
|----------|----------|-----------|
| `after_REFLECTION` | secular coda (default) | EXERCISE / STORY |
| `before_THREAD` | grace note | THREAD |

### 12.5 Bank program

| Attribute | Spec |
|-----------|------|
| **Location** | `SOURCE_OF_TRUTH/accent_banks/wisdom_essence/<topic>/entries.yaml` |
| **Manifest** | `SOURCE_OF_TRUTH/accent_banks/wisdom_essence/_BANK_MANIFEST.yaml` |
| **Pilot** | `anxiety/entries.yaml` — 12 essence entries, 3 register variants each, golden-ch1 bar |
| **Sizing — topic complete** | 10 themes × 3 variants = **30 units/topic** |
| **Status** | `status: unwired` / `KNOWN_UNWIRED: accent_banks/wisdom_essence/` until build lane |

### 12.6 Gates (proposed — build lane)

| Gate | BLOCK condition |
|------|-----------------|
| `check_wisdom_essence_mode_bleed.py` | `secular_safe: false` in composite plan OR teacher name in composite `secular` body OR `tradition_attributed` variant in composite plan |
| `check_wisdom_essence_doctrine_boundary.py` | Atom body matches `TEACHER_DOCTRINE` source text OR missing `source_refs` audit |
| `check_accent_framing_in_atom.py` | (shared) composer wrapper detected |

### 12.7 Operator decisions (defaults recommended)

| ID | Question | Recommendation |
|----|----------|----------------|
| **Q-WISDOM-01** | Dosage default secular | Max **2/book**; most **0–1** |
| **Q-WISDOM-02** | Variant (c) in secular? | **(b) only** secular; **(c)** teacher-mode |
| **Q-WISDOM-03** | Placement default | **post-REFLECTION** coda |

### 12.8 Out of scope

- Re-open `TEACHER_DOCTRINE` routing for essence content
- Re-enable `teacher_wrapper` or render-glue for tradition voice
- `AUTHOR_COMMENTARY` witness-register atoms (§13)
- Flagship/live-lane file edits
- Pipeline/composer wiring (parks with accent build order)

### 12.9 Acceptance (WISDOM_ESSENCE amendment)

1. Essence map with six-layer labels — linked above.
2. Corpus-convergent theme table — §12.1.
3. Three register variants with mode rules — §12.2.
4. Mode boundary gate rule — §12.3.
5. Dosage + placement — §12.4.
6. Pilot bank path + unwired status — §12.5.
7. Operator questions with defaults — §12.7.

---

## §13 — AUTHOR_COMMENTARY (v1.1 amendment)

**Archaeology:** [artifacts/research/AUTHOR_COMMENTARY_ARCHAEOLOGY_2026-07-07.md](../artifacts/research/AUTHOR_COMMENTARY_ARCHAEOLOGY_2026-07-07.md)

**Problem:** Books lack the author's personality — the witness register ("I've seen people try this — it helped them; maybe it'll help you too"), distinct from expert register ("I know this") and distinct from teacher/science wrappers.

**Critical trap:** The teacher-mode "I came across the teachings of…" pattern **partially lived in `teacher_wrapper`** (render-glue path, default OFF since de-injection). **Resurrection = authored accent atoms only.** Re-enabling `teacher_wrapper` or any render-injection path for commentary is **out of scope and BLOCKED**.

### 13.1 Two forms (spec both; v1 implements beats-only)

| Form | Description | v1 recommendation |
|------|-------------|-------------------|
| **(a) Discrete commentary beats** | New `AUTHOR_COMMENTARY` accent class — planner-placed, sparse, framing inside atom | **Ship v1** |
| **(b) Register threading** | Witness voice as coloring of existing PIVOT/TAKEAWAY slots | **Defer** — risks locked chapter shape; line-edit-lane experiment later |

**Threading analysis:** PIVOT and TAKEAWAY carry thesis weight; threading witness register into them blurs slot voice zones (OPD-20260606-005). REFLECTION already accepts teacher_wrapper for attribution — commentary must not duplicate wrapper function. **Beats-only for v1.**

### 13.2 Commentary types taxonomy

| Type | `commentary_type` | Register rule | Example shape |
|------|-------------------|---------------|---------------|
| Observed pattern | `observed_pattern` | Third-person witness of others; never clinical | "I've watched people try this between meetings…" |
| Personal admission | `personal_admission` | First-person; licensed by bio only | "This one took me the longest to believe." |
| Gentle endorsement | `gentle_endorsement` | Outcome witness, not promise | "The ones who tried it came back sounding different — not fixed, just harder to gaslight." |
| Source disclosure | `source_disclosure` | **Teacher-mode only** — observer, not student | "I came across Ahjan's teaching on the alarm within…" |
| Skeptic's companion | `skeptics_companion` | Meets reader doubt without debate | "I didn't believe the body-lead thing either — until standup stopped being the loudest meeting." |

**Banned in all types:** expert-voice ("I know"), clinical/therapeutic claims, fabricated credentials, guru register.

### 13.3 Mode boundary (gate rule)

| Mode | Teacher/tradition in commentary | Gate |
|------|--------------------------------|------|
| **Teacher-mode** | `source_disclosure` may name teacher/tradition — author is **observer**, not student | `mode_allow` includes `teacher_mode` |
| **Composite** | **ZERO** teacher/tradition reference — witness *people and practices* only | `composite_safe: true` required; mode-bleed gate untouched |

WISDOM_ESSENCE lane handles tradition-flavored distilled content separately under its own dosage.

### 13.4 Bio-consistency contract

Every commentary atom must be **derivable from the author's bio** (`assets/authors/<author_id>/bio.yaml`). The bio is the **license**.

```yaml
# AUTHOR_COMMENTARY extensions on accent_atom.yaml
author_id: ravi_chandra                    # required
commentary_type: observed_pattern | personal_admission | gentle_endorsement | source_disclosure | skeptics_companion
mode_allow: [composite, teacher_mode]        # source_disclosure: [teacher_mode] only
composite_safe: true|false                   # must be true unless teacher_mode-only atom
bio_license_refs:                            # audit trail — which bio claims license this atom
  - watched_teammates_try_practices
register: witness                            # mandatory; gate-enforced
expert_register_allowed: false               # mandatory
```

**Bio-enrichment program:** When bio depth is insufficient to license commentary (thin roster line only), enrich bio first — `status: operator_approved` required before production wiring (operator ratification logged in `operator_decisions_log.tsv`). **Authenticity rule:** observational claims only for pen-name/EI authors; no fabricated credentials; no clinical claims — consistent with manga full-EI-disclosure posture.

**Positioning profile constraints** (`author_positioning_profiles.yaml`): commentary must respect `allowed_language` / `forbidden_language` for the author's profile (e.g. `research_guide` forbids `emotional_confession` — use observational witness, not memoir).

### 13.5 Placement + dosage

| Field | Default (12-chapter book) |
|-------|---------------------------|
| `accent_budget.AUTHOR_COMMENTARY` | **0** (pilot exception) |
| Recommended production default | **3** per book (Q-AUTH-01) |
| Brand tunable range | 2–4 |
| Max chapters with any accent share | unchanged (§4.3, default 0.25) |

Joins experience / anti-spam tuple: extend `accent_signature` hash to include `AUTHOR_COMMENTARY_count`.

**Allowed positions:**

| Position | Typical type | Handoff → |
|----------|--------------|-----------|
| `after_REFLECTION` | observed_pattern, source_disclosure (teacher) | EXERCISE / STORY |
| `after_EXERCISE` | gentle_endorsement, skeptics_companion | INTEGRATION |
| `after_PIVOT` | personal_admission | REFLECTION / EXERCISE |
| `before_THREAD` | personal_admission, gentle_endorsement | THREAD |

### 13.6 Bank program

| Attribute | Spec |
|-----------|------|
| **Location** | `SOURCE_OF_TRUTH/accent_banks/author_commentary/<topic>/<author_id>/` |
| **Pilot** | `anxiety/ravi_chandra/en_US.yaml` — 10 atoms, ≥3 types, golden-ch1 bar |
| **Sizing — topic complete** | 8–12 atoms × active authors per persona×topic cell |
| **Status** | `status: unwired` / `KNOWN_UNWIRED: accent_banks/author_commentary/` until build lane |

### 13.7 Gates (proposed — build lane)

| Gate | BLOCK condition |
|------|-----------------|
| `check_author_commentary_bio_license.py` | `bio_license_refs` not satisfiable from author bio YAML |
| `check_author_commentary_mode_bleed.py` | `composite_safe: false` atom in composite-mode plan OR teacher name in composite-safe atom body |
| `check_author_commentary_register.py` | Expert-voice markers or clinical claim patterns |
| `check_accent_framing_in_atom.py` | (shared) composer wrapper detected |

### 13.8 Operator decisions (defaults recommended)

| ID | Question | Recommendation |
|----|----------|----------------|
| **Q-AUTH-01** | Dosage default | **3/book** |
| **Q-AUTH-02** | Threading into existing beats? | **Beats-only for v1**; threading = line-edit-lane experiment later |
| **Q-AUTH-03** | Bio-enrichment scope | **Flagship author now** (`ravi_chandra` for gen_z × anxiety); others per-brand as books enter production |

### 13.9 Out of scope

- Re-enable `teacher_wrapper` or render-glue for commentary
- Teacher references in composite commentary
- Fabricated credentials or clinical claims
- Flagship/live-lane file edits
- Pipeline/composer wiring (parks with accent build order)

### 13.10 Acceptance (AUTHOR_COMMENTARY amendment)

1. Archaeology report with six-layer labels — linked above.
2. Two forms spec'd; v1 beats-only recommended — §13.1.
3. Five-type taxonomy with register rules — §13.2.
4. Mode boundary gate rule — §13.3.
5. Bio-consistency contract + enrichment program — §13.4.
6. Dosage + placement — §13.5.
7. Pilot bank path + unwired status — §13.6.
8. Operator questions with defaults — §13.8.

---

## §14 — Anxiety-book authoring guidance (V2.1 amendment)

This section is the writer-facing operating doctrine for anxiety-profile books. It replaces any earlier guidance that treated anxiety books as "practical_credible with more accents." The anxiety flagship preset is `practical_credible` **base** with `intimate_voice` **modifiers** (V2.1 doc §7.1) — mechanism-clear and actionable, but validation-forward. That means the accents stay roughly sparse (§4.2a still applies), while `proof_and_embodiment` and `chapter_engine` content — which are *not* accents — run denser than a pure `practical_credible` book.

### 14.1 What should be dense (not sparse) in anxiety books

- **Early validation.** `VALIDATION_NORMALIZATION` should be dense in the first third of the book — the reader needs to feel recognized before mechanism or instruction lands. This is `chapter_engine`, not `optional_accents`; do not ration it.
- **Recurring mechanism explanation.** `MECHANISM_EXPLANATION` should recur across the body of the book, not front-load into chapter 1 and disappear. Anxiety readers re-encounter the same nervous-system mechanism in different situations; re-explain it in context each time, don't assume chapter-1 retention.
- **Support after hard practices.** `TROUBLESHOOTING` shows up after the reader is asked to do something hard, not before understanding exists. `ENCOURAGEMENT` (the one true optional accent in this list) should land in the same neighborhood — after an exercise, after a difficult realization, or after a turning point — because that is where reader support is actually needed, not scattered decoratively.

### 14.2 EXTERNAL_STORY: alternate recognition and mechanism_proof

Anxiety-book external stories should **alternate** between `recognition` (the reader feels seen) and `mechanism_proof` (a real case shows the mechanism working) rather than clustering all-recognition early and going silent, or leading with proof before the reader feels safe. See the pilot packet (§14.4) for a worked chapter-by-chapter example.

### 14.3 CALLBACK_RETURN as a first-order cohesion tool

For this profile, `cohesion_and_craft` is not a nice-to-have. Anxiety books are read episodically (a reader picks it up mid-crisis, puts it down, comes back) — a well-planted image or phrase that returns changed in a later chapter is what makes the book feel like *one* book rather than twelve standalone essays. Plant early (chapters 1–3), return late-middle to close (chapters 7–11), and make sure the return has a real `semantic_development` (§2.6) — not a repeated phrase.

### 14.4 Author voice and evidence framing

- `AUTHOR_COMMENTARY` should feel human, not preachy — interpretation and permission, never a lecture. Keep it distinct from `AUTHOR_DISCLOSURE` (§2.2b): disclosure is the author's own experience; commentary is the author's read on the reader's experience.
- `WISDOM_ESSENCE` should be used carefully, not as filler. The anxiety flagship hybrid caps it at `hard_max: 1` per book — if you're reaching for a second one, that's the tell that it's becoming decorative.
- `CITED_EVIDENCE` should never cold-open a high-validation chapter ahead of emotional safety. Evidence lands early-to-middle in a chapter, after the reader has been met, not as the chapter's first move.

### 14.5 Chapter-by-chapter authoring packet

A compact, chapter-by-chapter pilot authoring packet for the anxiety flagship profile — dominant job per chapter, proof/embodiment placement, accent placement, callback plant/return map, and analogy/metaphor placement — lives at [docs/authoring/ANXIETY_FLAGSHIP_ENHANCEMENT_PILOT_PACKET_2026-07-13.md](../docs/authoring/ANXIETY_FLAGSHIP_ENHANCEMENT_PILOT_PACKET_2026-07-13.md). Use it as the reference shape when planning a new anxiety-profile book; it is illustrative, not a template to copy verbatim into every book.
