# Accent Beats System Spec — Planner-Placed Optional Chapter Elements

**Version:** 1.1.0  
**Date:** 2026-07-07  
**Authority:** Pearl_Research + Pearl_Architect  
**Status:** SPECCED (inventory + design only — no pipeline, composer, bank authoring, or flagship changes in this PR)  
**GATE:** `flagship-read-approved` (golden-#2 freeze merged) before any build lane opens  
**Implements:** Operator mission — optional, planner-placed chapter elements (quotes, encouragement, reflection questions, affirmations, troubleshooting, cited evidence) that appear **sparsely and intelligently** across books, increasing catalog variation without reintroducing template glue.

**Build order after flagship read:** cast_structure + renditions wired → accent layer planned + banks seeded → composer consumer + gates → book-#2/#3 pilot read against no-accent sibling.

**Doctrine (non-negotiable):** Accent beats are **planner-assigned, never composer-improvised**. Framing lives **inside the atom** — entry and exit authored per position variant. Composer-injected wrappers are **banned** (same scar as `COMPOSER_DEINJECTION_AND_TISSUE_SPEC_2026-07-05.md`).

**Personality layer (WISDOM_ESSENCE v1.1):** traditions' distilled voice — corpus-convergent essence beats, distinct from `TEACHER_DOCTRINE`, `QUOTE`, and `AUTHOR_COMMENTARY` (parallel lane). Planner-placed, dosage-governed; composite mode uses secular register only.

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
| 11 | **Mantras / affirmations** | `config/angles/angle_registry.yaml` → `journey.core_mantras` (15 angles × TODO stubs) | **`AFFIRMATION`** ← reuse mantra content shape | **CONFIG-EXISTS** (schema) / **ABSENT** (authored mantras) | Surface reader-facing beat; Pearl_Editor commissions mantras per angle |
| 12 | **Quotes** | ~22 orphan `atoms/<persona>/<topic>/QUOTE/CANONICAL.txt` (retired per `QUOTE-ATOM-ROUTING-01`); **no verified bank** | **`QUOTE`** (new accent + new bank) | **ABSENT** (verified) / **RESEARCHED** (orphan content) | Pearl_Research bank program; **not** 11th grid slot — accent overlay only |
| 13 | **Case studies / cited evidence** | Fictional vignettes in STORY; Gladwell Spiral structure cites stats in `BESTSELLER_STRUCTURES.md` examples only | **`CITED_EVIDENCE`** (new accent + new bank) | **SPECCED** (structure examples) / **ABSENT** (bank + gate) | Pearl_Research claims ledger; distinct from fictional STORY |
| 14 | **Obstacles / troubleshooting** | INTEGRATION prose ("chest will object", "forget for three rooms/meetings") — e.g. `atoms/gen_z_professionals/anxiety/INTEGRATION/CANONICAL.txt` | **`TROUBLESHOOTING`** (new accent) | **EXECUTED-REAL** (embedded) → **SPECCED** (placeable) | Extract standalone beats keyed to `exercise_id` / `object` |
| 15 | **Forward thread / continuity** | THREAD slot (Writer Spec §4.7a), INTEGRATION-final placement | — (core spine) | **CODE-WIRED** | None — REFLECTION_QUESTION sits **before** THREAD, not replacing it |

### 1.1 Work split estimate

| Category | Share | Classes |
|----------|-------|---------|
| **Dormant asset wiring** | ~70% | ENCOURAGEMENT, AFFIRMATION, REFLECTION_QUESTION, TROUBLESHOOTING (content partially exists) |
| **Genuinely new** | ~30% | QUOTE, CITED_EVIDENCE (banks + verification + gates) |

**Verified:** Only QUOTE and CITED_EVIDENCE require new bank programs from zero. All other accent classes reuse or refactor existing prose/assets.

### 1.2 Relationship to QUOTE-ATOM-ROUTING-01

The 2026-05-06 decision retired persona-keyed `QUOTE/` dirs as non-canonical 10-grid orphans. **This spec does not reopen the 10-slot grid.** QUOTE returns as an **accent overlay** with:

- Planner assignment in `accent_beats:` (not `connective_picks`)
- Verified primary-source bank (`SOURCE_OF_TRUTH/accent_banks/quote/`)
- Attribution gate (§6)

Orphan `QUOTE/CANONICAL.txt` files are **candidate content** for Pearl_Editor review — not routable until re-authored into the accent bank with verification metadata.

---

## §2 — Accent atom classes

Seven accent classes (six original + **WISDOM_ESSENCE** v1.1). Each is a **complete authored paragraph unit** with position variants — never a bare quote line plus composer wrapper.

### 2.1 Shared schema (`accent_atom.yaml`)

```yaml
accent_class: QUOTE | ENCOURAGEMENT | REFLECTION_QUESTION | AFFIRMATION | TROUBLESHOOTING | CITED_EVIDENCE | WISDOM_ESSENCE
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

| Class | Reuse source | Purpose | Default allowed positions | Must key to |
|-------|--------------|---------|---------------------------|-------------|
| **QUOTE** | New bank | Credibility + tonal entry/exit; doctrine echo | `before_HOOK`, `after_INTEGRATION` (closer) | `doctrine_id` or chapter `angle_id` |
| **ENCOURAGEMENT** | `PERMISSION` / `PERMISSION_GRANT` atoms | Post-effort recognition — "You just sat with that for two minutes" | `after_EXERCISE`, `after_turning_point` | `exercise_id` or story `turning_point` pick |
| **REFLECTION_QUESTION** | Doctrine closers, CJK reflection blocks | Reader pause before thread | `after_REFLECTION`, `before_THREAD` | `doctrine_id` or `object` |
| **AFFIRMATION** | `angle_registry.yaml` `core_mantras` | Short repeatable phrase; angle journey surface | `after_PIVOT`, `before_INTEGRATION` | `angle_id` |
| **TROUBLESHOOTING** | INTEGRATION obstacle paragraphs | "When you forget for three days…" | `after_INTEGRATION` | `exercise_id` + `object` |
| **CITED_EVIDENCE** | New bank | Named study/stat moment (not fiction) | `after_HOOK`, `before_STORY` (Gladwell Spiral alignment) | `doctrine_id` + claim ledger |
| **WISDOM_ESSENCE** | New bank (`accent_banks/wisdom_essence/`) | Traditions' distilled voice — corpus-convergent themes, not teacher doctrine | `after_REFLECTION`, `before_THREAD` | `topic_keys` + `doctrine_keys` + `theme`; `source_teachers` audit only |

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

`[CITED_EVIDENCE]`, `[AFFIRMATION]`, and `[WISDOM_ESSENCE]` insert per class `allowed_positions` with the same handoff rule.

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

### 3.3 Invariants (gates)

1. **Planner-assigned only** — no accent renders unless `accent_beats` entry exists for `(chapter, accent_class)`.
2. **At most one accent per class per chapter** — no double-quote chapters unless plan explicitly lists two classes (quote + encouragement OK; two quotes not).
3. **No accent-only chapters** — every chapter with accents still carries full spine slots.
4. **Structure PERMISSION decoupled** — `BESTSELLER_STRUCTURES.md` PERMISSION column becomes a *hint* for planner; renderer prefers `accent_beats.ENCOURAGEMENT` when present, falls back to legacy PERMISSION slot only when plan marks `legacy_permission: true` (migration flag).

---

## §4 — Plan schema extension

### 4.1 Book-level `accent_budget`

```yaml
# book_structure_plan / twelve_shape plan header
accent_budget:
  QUOTE: 3
  ENCOURAGEMENT: 2
  REFLECTION_QUESTION: 3
  AFFIRMATION: 0
  TROUBLESHOOTING: 1
  CITED_EVIDENCE: 0
  WISDOM_ESSENCE: 0
accent_distribution_profile: somatic_reflective  # see §4.3
```

**Default for 12-chapter book:** all zeros (no accents). Pilot (§7) is an explicit exception.

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

### 4.3 Dosage + distribution governance

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

**Sparsity gate:** FAIL if `count(chapters with accent_beats) / total_chapters > brand_profile.max_accent_chapter_share` (default **0.25** — at most 3 of 12 chapters carry any accent in somatic profile).

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

Register in `scripts/run_production_readiness_gates.py` as gates **#24–#30** (numbers provisional; coordinate with Drift detectors roster at build time).

**Status:** all gates **ABSENT** until build lane; this spec is **SPECCED** only.

---

## §7 — Pilot plan

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

**Parallel lane:** `AUTHOR_COMMENTARY` (separate PR `#4713`) owns the author's witness voice. WISDOM_ESSENCE owns traditions' distilled voice under its own dosage and register rules.

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
- `AUTHOR_COMMENTARY` witness-register atoms (owned by `#4713`)
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
