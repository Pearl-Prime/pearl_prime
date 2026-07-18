# Rendition System Spec — Shared-Bank Prose (Doctrine + Practice Library)

**Version:** 1.1.0 — A+ amendments per cross-session verification review (PR #4693, comment 4897941260) + operator description-layer ruling **OPD-20260707-001**  
**Date:** 2026-07-07  
**Authority:** Pearl_Research + Pearl_Architect  
**Status:** SPECCED (research + design only — no pipeline, plan YAML, or flagship changes in this PR)  
**Implements:** Operator mission — eliminate verbatim shared-bank exposure across ~3,700 anxiety catalog titles while preserving written-for-that-reader quality at **paragraph/section unit**, never sentence-level swapping.

**Build order after flagship read:** journeys wired → bridges + renditions authored → shingle gate live → catalog scale with zero verbatim overlap.

---

## §0 — Problem statement (grounded in math)

| Input | Value |
|-------|-------|
| Anxiety catalog scale | ~100 books/brand × 37 brands ≈ **3,700 titles** |
| Doctrine bank target | **~30 lessons/topic** (anxiety has **15 live** today: `COMPOSITE_DOCTRINE v01`–`v15`) |
| Doctrine slots per book | **12** (one REFLECTION teaching block per chapter) |
| Typical doctrine block size | **~350 words** |
| Practice library | **311** inbox items (`272` in `practice_items.jsonl` store + `39` ab_tady_37) |

**Exposure without renditions:** 3,700 books × 12 doctrine slots ≈ 44,400 chapter-slots. Divided across 30 canonical lessons ≈ **1,480 verbatim appearances per lesson** (~1,500). Any reader who buys two books from different brands can hit identical REFLECTION paragraphs. The same class applies to practice bodies: `med_007` Noting ships unchanged wherever selected.

**Hard constraint (repo scar):** Variation happens at **paragraph/section unit — NEVER sentence-level swapping.** Sentence-swap is the madlib/template-glue pattern that previously broke quality ("assembled on the page"). The proven in-repo pattern is paragraph-unit components (5-layer exercise model; complete doctrine retellings).

---

## §1 — KDP policy findings (verified sources)

Amazon does **not** publish numeric similarity thresholds or shingle sizes. Policy is qualitative and enforced via automated review + human escalation.

### 1.1 Primary policy text

| Source | Rule | Implication for catalog |
|--------|------|-------------------------|
| [Guide to Kindle Content Quality — Disappointing content](https://kdp.amazon.com/en_US/help/topic/G200952510#disappointing) | **"Content that is not significantly different from content in another book available in the Kindle Store"** is not allowed. | Shared-bank prose reused verbatim across hundreds of titles is squarely in scope. |
| Same page — romance exception | Same interior allowed if **covers differ** and title/subtitle carries a version indicator (e.g. "Discreet Version"). | Does **not** apply to self-help/workbook catalog; cover-only differentiation is insufficient. |
| [Content Guidelines — Poor customer experience](https://kdp.amazon.com/en_US/help/topic/G200672390) | Content "typically disappointing to customers" includes examples in the Content Quality guide; enforcement uses ML + automation + human reviewers. | Account-level review and unpublish are documented outcomes, not just single-title rejection. |
| KDP Community / account enforcement (secondary) | Messages cite **"do not contain significantly differentiated content"** and **"excessively reused, recycled, or repeated within or across books."** | Confirms cross-title reuse is an enforcement axis; granularity is not specified publicly. |

### 1.2 What KDP does **not** specify

- No published minimum edit distance, n-gram size, or % overlap threshold.
- "Duplicated text" in the Content Quality guide ([§Duplicated text](https://kdp.amazon.com/en_US/help/topic/G200952510)) targets **within-book** copy-paste errors (repeated chapters/sections), not cross-title farms — but **Disappointing content** explicitly covers cross-title sameness.
- Low-content / planner / series-house carve-outs are **not** documented as exemptions for full-prose self-help interiors.

### 1.3 Design proxy for enforcement

Because KDP does not publish a number, this spec adopts a **conservative internal proxy:**

> Fail publish when any two books' shared-bank blocks overlap **≥3 consecutive sentences** after normalization.

Rationale: three consecutive sentences is clearly reader-visible duplication, above within-book typo class, below structural-only similarity (CTSS). This proxy is **stricter than CTSS** and **complementary**, not redundant.

---

## §2 — In-repo machinery inventory (extend, never fork)

Six-layer taxonomy: `ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`.

| Asset | Location | What it does | Where it stops | Layer |
|-------|----------|--------------|----------------|-------|
| **Content Fragment Variation Writer Spec** | `docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md` | Variant banks, collision families, lexical rules, YAML record shape for fragment families (scene, glue, reflection, practice). Closest **doctrine/exercise rendition ancestor**. | Targets renderer fallbacks + registry duplicates; not wired to `composite_doctrine` or practice-library renditions; no `rendition_id` planner assignment. | **SPECCED** |
| **DupEval / CTSS** | `specs/DUPE_EVAL_SPEC.md`, `scripts/ci/check_platform_similarity.py` | Pre-publish **structural** similarity (arc, band_seq, slot_sig, exercise placement, story/exercise family vectors). Block ≥0.78, review ≥0.65. | **Does not compare prose.** Cannot detect verbatim doctrine or `med_007` body overlap. | **CODE-WIRED** |
| **Wave density** | `scripts/ci/check_wave_density.py` | Batch arc/band/slot_sig concentration limits. | Structural only. | **CODE-WIRED** |
| **Prose duplication gate** | `scripts/ci/check_prose_duplication.py` | Paragraph SHA-256 exact match, opening-12-word, closing sentence, 6-gram Jaccard across a wave. | Not shingle-based; not scoped to shared-bank blocks only; no planner `rendition_id` audit. | **CODE-WIRED** |
| **SPEC-5 Variants + Beat Wiring** | `specs/SPEC_5_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md` | ≥3 persona×topic atom variants per section; deterministic pick; beat overlays. | Persona×topic **registry atoms**, not shared doctrine bank or practice-library bodies; beat overlay **partially wired**. | **SPECCED** (+ partial **CODE-WIRED** selector) |
| **Composite doctrine bank** | `SOURCE_OF_TRUTH/composite_doctrine/<topic>/REFLECTION/CANONICAL.txt` | Multi-variant REFLECTION teaching blocks (`COMPOSITE_DOCTRINE vNN`). Anxiety: **15 live variants** (~350 words each). | **No renditions** — one prose body per variant; rotation reuses same text across brands. `doctrine_rotation.yaml` still documents 5-variant cycle (stale vs bank). | **EXECUTED-REAL** (content) / **CODE-WIRED** (rotation without renditions) |
| **Doctrine rotation** | `config/source_of_truth/doctrine_rotation.yaml`, `phoenix_v4/planning/doctrine_rotation.py`, `docs/doctrine_distribution_plan.md` | Per-chapter variant assignment, bounded reuse, brand dosage (somatic_heavy vs commercial_light). | Assigns **variant id**, not **rendition id**; no cross-book dedup. | **CODE-WIRED** |
| **Practice item schema (5-layer)** | `specs/PRACTICE_ITEM_SCHEMA.md`, `SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl` | `components.{bridge,intro,description,aha,integration}` × `{full,lean}` — **proven paragraph-unit pattern**. | `description` is canonical shared body; bridges generic, not object-aware; no rendition registry. | **EXECUTED-REAL** (schema + store) |
| **Persona overlays (exercises_v4)** | `SOURCE_OF_TRUTH/exercises_v4/persona_overlays.yaml`, `phoenix_v4/exercises/overlay_substitution.py` | Phrase-level lexical shift on `aha_noticing` (and optional `integration`); structure frozen. | **Phrase substitution only** — explicitly not rewrites; does not cover bridge/intro/description; 3 personas defined (executive, gen_z, healthcare). | **CONFIG-EXISTS** — `overlay_substitution.py` exists but its only importer is `tests/test_bestseller_craft_quality.py`; **production-dormant**, wiring is an implementation item |
| **Bridge templates** | `SOURCE_OF_TRUTH/exercises_v4/bridge_templates.yaml` | Exercise-type-level bridge variants (full/lean/gentle). | Not chapter-object-aware; not persona/register keyed. | **CONFIG-EXISTS** |
| **Exercise journeys** | `phoenix_v4/planning/exercise_journey_planner.py`, `attach_exercise_journeys()` in `enrichment_select.py`, `config/exercises/journey_templates.yaml` | Multi-phase arc (awareness → regulation → integration) on sections 4/8/10; thesis alignment; `journey_exercise_id` on slots. | Uses **exercises_v4 registry ids** (`body_scan_v1`, etc.), not practice-library `med_*`; smoke artifacts show `journey_exercise_id: null` when journeys not attached; composer journey intro consumption **partial** on spine path. | **CODE-WIRED** (planner) / **CONFIG-EXISTS** (templates) — **dormant in baseline snapshots** |
| **Rendition system (this spec)** | `specs/RENDITION_SYSTEM_SPEC.md` | Unified architecture for doctrine + exercise shared-bank variation. | Implementation not started. | **SPECCED** |
| **Shingle gate (proposed)** | `scripts/ci/check_catalog_shingle_dedup.py` (to be implemented) | Cross-book ≥3-sentence shared-bank overlap. | **ABSENT** | **SPECCED** |

### 2.1 Journey layer — designed vs wired vs dormant

**Designed:** `plan_exercise_journey()` builds 1–3 phases from runtime profile, maps to sections 4/8/10 via `journey_templates.yaml`, picks from awareness/regulation/integration pools, validates thesis outcomes and prerequisites.

**Wired:** `run_pipeline.py --exercise-journeys` calls `attach_exercise_journeys()` after enrichment; sets `slot.journey_exercise_id` and `slot.exercise_phase`; `section_packet_composer.py` injects `JOURNEY_INTROS` when phase is present.

**Dormant evidence:** Byte-verified planning artifacts export null journey fields when the journey attach path is not exercised or not propagated to `selected_content_variants.json`:

- `artifacts/qa/bestseller_smoke_books/selected_content_variants.json` — all slots: `"journey_exercise_id": null, "exercise_phase": null`
- `artifacts/wave_proof/prod_burnout/selected_content_variants.json` — same pattern

**Gap:** Production chord requires `--exercise-journeys`, but flagship / NEXT-5 baseline snapshots do not carry journey metadata into variant exports; journey intros use generic strings, not practice-library exercises or chapter callbacks.

---

## §3 — Rendition System architecture (doctrine + exercises, one system)

### 3.1 Core concepts

| Term | Definition |
|------|------------|
| **Canonical lesson / exercise** | SSOT teaching or practice body (`lesson_id` / `practice_id`). Immutable mechanism; one authoritative `description` or doctrine block. |
| **Rendition** | A **complete paragraph-unit retelling** of the same lesson logic or a **complete component block** (bridge, intro, aha, integration) — whole authored prose, not sentence swaps. |
| **rendition_id** | Stable key: `{lesson_id or practice_id}__{persona_cluster}__{register}__{rendition_seq}` (e.g. `COMPOSITE_DOCTRINE_v03__gen_z_work__commercial__r02`). |
| **Persona cluster** | Planner-facing grouping of personas (not per-persona renditions for v1). |
| **Register** | Brand voice axis: `somatic_heavy` \| `commercial_light` (extends `doctrine_rotation.yaml` `brand_dosage_profiles`). |
| **Anchor domain** | Concrete imagery surface: workplace_slack, clinical_shift, classroom, etc. |

### 3.2 Lesson schema (doctrine renditions)

Extends `composite_doctrine/<topic>/REFLECTION/` — **does not replace** variant ids (`COMPOSITE_DOCTRINE v03`).

```yaml
lesson_id: COMPOSITE_DOCTRINE_v03          # invariant canonical key
rendition_id: COMPOSITE_DOCTRINE_v03__gen_z_work__commercial__r01
persona_cluster: gen_z_work                  # gen_z_work | managers_work | caregivers | frontline_care | educators (§5.1)
register: commercial_light                   # somatic_heavy | commercial_light
anchor_domain: workplace_slack               # concrete anchor family
teaching_core: "Sensation and story are separable; freedom lives in the gap."
sections:
  - role: claim
    prose: |
      ...complete paragraph(s)...
  - role: mechanism
    prose: |
      ...
  - role: concrete_anchor
    prose: |
      ...Slack ping, not charting...
  - role: objection
    prose: |
      ...
  - role: landing
    prose: |
      ...
metadata:
  word_count: 340
  collision_family: sensation_vs_story
  forbidden_terms: []
  source_canonical: SOURCE_OF_TRUTH/composite_doctrine/anxiety/REFLECTION/CANONICAL.txt#v03
  quality_bar_ref: flagship_ch1_v03_register   # ch1-approved register anchor
```

**Rules:**

1. **Invariant `teaching_core`** — one-sentence thesis; identical across renditions of the same lesson.
2. **Structured sections** — claim → mechanism → concrete_anchor → objection → landing; each section is **≥1 complete paragraph**; no sentence-level alternation inside a section.
3. **Vary the concrete, keep the abstract** — persona-anchor swaps (Slack-ping → charting → lesson plans) and register swaps (somatic-heavier vs commercial-lighter) are the variation surface; mechanism and landing logic stay stable.
4. **Complete retellings** — renditions are authored as wholes, not assembled from sentence pools.

**Storage (v1 proposal):** `SOURCE_OF_TRUTH/composite_doctrine/<topic>/REFLECTION/renditions/<rendition_id>.yaml` with compiled flat prose cache for renderer parity checks.

### 3.3 Exercise renditions

**Canonical body — core/frame split (A+ ruling, OPD-20260707-001):** each `practice_id` description splits into an invariant **instruction core** — ≤2 sentences of exact steps, **bit-identical catalog-wide**, registered in `config/governance/shingle_exemptions.yaml` (the shingle gate skips registered cores) — and **frame renditions**: an opening context sentence + closing encouragement sentence pair, authored whole per persona_cluster and planner-assigned. Instruction words inside the core are untouchable (`med_007` Noting steps never vary); frames carry all persona variation. **Synonym/word-level skinning of instruction cores is BANNED** — it is pedagogical drift, and it defeats our internal 3-sentence proxy without addressing Amazon's actual qualitative review.

**Variation surface — components:**

| Component | Rendition scope | Notes |
|-----------|-----------------|-------|
| **bridge** | **Object-aware** — keyed by `(practice_id, chapter_object_id)` | e.g. "Before you open Slack again — do this one out loud." Authored per chapter-object from twelve-shape plan. |
| **intro** | Persona-cluster × register rendition | Names practice; frames why **now** for this reader. |
| **description** | **Core/frame split (A+, OPD-20260707-001)** | Invariant instruction core (≤2 sentences, exemption-ledger-registered — gate skips it) + persona_cluster frame renditions (opening/closing sentence pairs, authored whole). Word-level skinning of cores banned. |
| **aha** | Persona-cluster rendition + **extends** `persona_overlays.yaml` | Full paragraph retelling preferred over phrase-only for production brands; overlays remain for narrow lexical calibration. |
| **integration** | Persona-cluster × register + **journey callbacks** | "The space you practiced finding in chapter one — now find it mid-meeting." |

**Extension of `persona_overlays.yaml` (not replacement):**

```yaml
# Existing — keep for aha_noticing phrase-level calibration
persona_overlays:
  gen_z:
    lexical_shift: { ... }

# New — rendition registry reference (persona_cluster level)
rendition_refs:
  med_007:
    intro: med_007__gen_z_work__commercial__intro_r01
    aha: med_007__gen_z_work__somatic__aha_r01
    integration: med_007__gen_z_work__commercial__int_r01

# New — object-aware bridges (separate bank)
object_bridges:
  med_007:
    after_send_reply_anxiety:
      full: "Before you open the thread again — do this one out loud."
      lean: "Before you reopen the thread — thirty seconds."
    sunday_night_dread:
      full: "..."
```

**Assembly order:** resolve canonical exercise → instruction core (bit-identical) + assigned frame renditions → apply `rendition_refs` component overrides (paragraph blocks) → inject `object_bridges[practice_id][chapter_object_id]`. (`lexical_shift` overlays are production-dormant today — see §2 — and are **never** applied to instruction cores; any future overlay wiring is aha-calibration only.)

### 3.4 Exercise journeys — target arc ladder

**Practice-arc ladder (per book):**

| Phase | Function | Typical sections | Callback behavior |
|-------|----------|------------------|-------------------|
| **regulation** | Downshift alarm; safe entry | Early chapters (sec 4) | Establish somatic anchor |
| **awareness** | Name pattern; interoception | Mid chapters (sec 4/8) | Reference regulation rep |
| **exposure** | Stay with signal in context | Mid-late (sec 8) | Reference awareness from ch1–3 |
| **integration** | Carry into life | Late (sec 8/10) | Explicit callback prose in `integration` rendition |

**Wire requirements (future PR — out of scope here):**

1. Planner emits `chapter_object_id` into EXERCISE slot metadata.
2. `attach_exercise_journeys()` selects practice-library ids when plan specifies `exercise_id: med_007`, not only exercises_v4 pool ids.
3. `integration` renditions include `callback_refs: [{chapter: 1, object_id: after_send_reply_anxiety}]`.
4. Export `journey_exercise_id` / `exercise_phase` into `selected_content_variants.json` on all production builds.

### 3.5 Pearl_Writer derivation guide

Mechanical procedure for authoring a rendition from canonical source:

1. **Load canonical** — doctrine variant or exercise component; extract `teaching_core` or instruction skeleton.
2. **Lock abstract** — copy `teaching_core` verbatim; outline section roles without prose.
3. **Pick axes** — `persona_cluster`, `register`, `anchor_domain` from planner assignment sheet.
4. **Retell per section** — write each section as a fresh paragraph block; swap anchors and examples; **do not** reuse sentences from canonical.
5. **Register pass** — somatic_heavy: body-first, slower sentences; commercial_light: shorter clauses, workplace outcome framing.
6. **Quality bar** — diff against flagship ch1-approved register (`artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json` invocation profile); reject if read as template or madlib.
7. **Metadata** — fill `rendition_id`, `collision_family`, `word_count`; run shingle self-check against canonical (must fail ≥3-sentence overlap).

**Tier policy:** Tier-1 (Claude Code, operator-present) for all renditions until shingle gate is green on pilot.

---

## §4 — Enforcement (gates, not discipline)

### 4.1 `check_catalog_shingle_dedup` (proposed CI gate)

**Script:** `scripts/ci/check_catalog_shingle_dedup.py` (to implement)

**Scope:** Extract **shared-bank blocks** only:

- Doctrine: REFLECTION bodies from `composite_doctrine` + rendition files
- Exercises: `components.*` and `text` from practice library

Exclude: STORY/SCENE/HOOK persona atoms (already persona×topic unique per SPEC-5).

**Exemption ledger:** `config/governance/shingle_exemptions.yaml` — append-only, reason-required, operator-signed entries. Registered instruction cores (A+ ruling) and deliberate sharing (e.g. intentional series recap) are skipped by the gate. An exemption is visible governance, not a bypass — governance review flags any PR that adds one.

**Algorithm:**

1. **Normalize:** lowercase, collapse whitespace, strip punctuation except apostrophe, unify smart quotes.
2. **Sentence split:** `.!?` boundaries; drop fragments <5 words.
3. **Shingle:** sliding window of **3 consecutive sentences** → hash SHA-256 of normalized join.
4. **Index (persistent, cross-wave):** check candidates against `artifacts/catalog_similarity/shingle_index.jsonl` — the durable published-catalog index (sibling of the CTSS `index.jsonl`) — **and** against the current wave; on publish, append the new books' shingles via `scripts/ci/update_shingle_index.py` (pattern: `update_similarity_index.py`). Books published in different waves are therefore always compared; a wave-local index alone cannot enforce the invariant.
5. **Fail:** any hash appearing in **≥2 books** with different `book_id` (index or wave) where the shingle is not covered by an exemption-ledger entry (registered instruction cores; intentional series recap).
6. **Report:** top 20 collisions by frequency; emit `artifacts/governance/shingle_dedup_report.json`.

**Rollout ladder (transition honesty — today every same-topic pair collides; strict-from-day-one would freeze the catalog):**

1. `report` — full-catalog collision census; baseline artifact `artifacts/qa/SHINGLE_BASELINE_<date>.json`. Already-published titles are grandfathered in the baseline, **not** the index.
2. `strict-per-topic` — a topic flips to strict for **new** builds once its rendition floor (§5) exists; the flip list is gate config, so flipping a topic is a reviewable one-line PR.
3. `strict-global` — all doctrine topics flipped; exercise scope follows the same ladder.

**Composition with existing gates:**

| Gate | Layer | Relationship |
|------|-------|--------------|
| CTSS / DupEval | Plan structure | Orthogonal — run before render |
| `check_prose_duplication` | Full-book prose | Shingle gate is **shared-bank scoped** and **sentence-triple** sensitive; run on same wave; shingle fails first on doctrine/exercise reuse |
| `check_catalog_shingle_dedup` | Shared-bank blocks | **New** — blocks catalog scale verbatim exposure |

**Exit codes:** 0 pass; 1 fail (block publish); 2 warn (review tier — optional duplicate in same brand family).

### 4.2 Planner-side rendition assignment

**Config:** `config/catalog_planning/rendition_assignment.yaml` (to implement)

**Assignment rule:**

```
rendition_index = hash(f"{book_id}:{lesson_id}") mod N_renditions(lesson_id, persona_cluster, register)
```

**Constraints:**

1. **No concentration:** no `rendition_id` may appear in > `ceil(catalog_cell_count / N_renditions) + 2` books per brand per wave.
2. **Coverage:** every `(lesson_id, persona_cluster, register)` tuple used in a wave must have ≥1 authored rendition before publish gate passes.
3. **Audit:** compiled plan carries `rendition_ids: {chapter: {slot: rendition_id}}`; CI verifies assignment matches hash rule and appears in rendition registry.

**Audit script:** `scripts/ci/check_rendition_assignment_audit.py` — compares plan metadata to `SOURCE_OF_TRUTH/renditions/registry.jsonl`.

---

## §5 — Sizing + pilot

### 5.1 Persona clusters (v1)

| Cluster | Personas (SSOT: `config/catalog_planning/canonical_personas.yaml` — all 13 canonical covered, none phantom) |
|---------|----------------------------------------|
| `gen_z_work` | gen_z_professionals, gen_z_student, gen_alpha_students |
| `managers_work` | corporate_managers, entrepreneurs, tech_finance_burnout, millennial_women_professionals |
| `caregivers` | working_parents, gen_x_sandwich, midlife_women |
| `frontline_care` | healthcare_rns, first_responders |
| `educators` | educators |

Notes: `nyc_executives` appears in `config/catalog_planning/series_templates.yaml` / `description_templates.yaml` / `brand_teacher_assignments.yaml` but is **not** in the canonical 13 — the planner maps it to `managers_work` if encountered. The v1.0.0 draft's `empty_nesters` / `retirees` exist nowhere in tracked config and are removed; `unified_personas.md` does not exist — the YAML above is the SSOT.

**Registers:** 2 (`somatic_heavy`, `commercial_light`)  
**Renditions per lesson (full coverage):** 5 clusters × 2 registers = **10 renditions/lesson**

### 5.2 Doctrine sizing — anxiety

| Stage | Lessons | Renditions each | Total renditions | Est. words (@350) | Authoring hours (@2.5h) |
|-------|---------|-----------------|------------------|-------------------|-------------------------|
| **Pilot** | 1 (v03) | 3 | 3 | ~1,050 | ~7.5 |
| **Anxiety complete** | 15 | 10 | 150 | ~52,500 | ~375 |
| **Topic scale** | 30 | 10 | 300 | ~105,000 | ~750 |

At 3,700 books without renditions: each lesson ~1,480 verbatim uses. With 10 renditions: ~148 uses/rendition — acceptable if shingle gate passes.

### 5.3 Exercise sizing — 311 library

| Strategy | Scope | Count order | When |
|----------|-------|-------------|------|
| **Object-aware bridges** | `(practice_id, chapter_object_id)` for objects in twelve-shape plans | ~311 exercises × ~avg 8 objects used in catalog ≈ **2,500** bridge texts (staggered authoring) | Phase 2 — highest ROI |
| **Intro/aha/integration renditions** | 5 clusters × 2 registers × 3 components | 311 × 10 × 3 = **9,330** blocks (upper bound; defer) | Phase 3 — after bridges |
| **Description cores + frames (A+)** | Invariant core ≤2 sentences (ledger-registered) + frame pairs per cluster | 311 cores registered; frames for hot ids first (~40–60/topic × 5 clusters); full: 311 × 5 = **1,555** frame pairs (~30 words each) | Phase 2 — with bridges |

**Practical v1:** Author bridges only for exercises appearing in compiled catalog plans (~40–60 hot ids per topic).

### 5.4 Pilot plan (prove shingle gate)

| Item | Deliverable | Success criterion |
|------|-------------|-------------------|
| Doctrine | `COMPOSITE_DOCTRINE v03` × **3 renditions** (gen_z_work/commercial, caregivers/somatic, managers_work/commercial) | Shingle gate **RED** on canonical v03 + v03 copy verbatim across two mock books; **GREEN** with 3 renditions |
| Exercise | `med_007` **core/frame split** — invariant core (≤2 sentences, ledger-registered) + **3 frame pairs** (one per pilot persona cluster) | Core bit-identical to canonical instruction words; frames pass shingle self-check; mechanism unchanged. (Object-aware bridges stay Phase 2, §5.3.) |
| Gate stub | `check_catalog_shingle_dedup.py` implemented with `--pilot` mode on fixture books | Deterministic exit codes documented in test |

**Pilot fixtures:** `tests/fixtures/rendition_pilot/` — two book txt files sharing canonical block (expect fail) and rendition blocks (expect pass).

**No flagship edits:** pilot uses standalone fixtures, not `atoms/gen_z_professionals/anxiety/*` or plan YAML.

---

## §6 — Out of scope (this PR)

- Flagship lane files, ch1 atoms/snapshot, plan YAML changes
- Pipeline code changes (`run_pipeline.py`, `enrichment_select.py`, composer)
- Production prose authoring beyond pilot fixture stubs
- Sentence-level swapping or madlib templates
- Declaring any component "working" above its verified layer

---

## §7 — Registry and cross-references

| Doc | Role |
|-----|------|
| `docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md` | Collision-family + variant record ancestor |
| `specs/DUPE_EVAL_SPEC.md` | Structural CTSS gate |
| `specs/PRACTICE_ITEM_SCHEMA.md` | 5-layer component model |
| `docs/doctrine_distribution_plan.md` | Doctrine rotation (variant-level today) |
| `SOURCE_OF_TRUTH/exercises_v4/persona_overlays.yaml` | Lexical overlay extension point |
| `book_structure.txt` | Catalog math and knob table |
| `config/governance/shingle_exemptions.yaml` (proposed) | Signed shingle exemption ledger — instruction cores + deliberate sharing |
| `artifacts/coordination/operator_decisions_log.tsv` | **OPD-20260707-001** — description-layer A+ ruling (core/frame; skinning ban) |

**Data dictionary:** `docs/DATA_DICTIONARY.tsv` is **generated** by `scripts/governance/build_data_dictionary.py` and staleness-gated (Drift detectors); hand-added rows do not survive a rebuild. Rows for the gate, ledger, and index appear automatically when those files land in scanned paths — do not pre-seed them by hand.

---

## §8 — Acceptance (this spec PR)

1. KDP policy cited with primary URLs — §1.
2. Reuse inventory with six-layer labels — §2.
3. Unified rendition architecture (lessons + exercises + journeys + derivation) — §3.
4. Enforcement spec (shingle gate + planner assignment) — §4.
5. Sizing tables + pilot plan — §5.
6. Registered in `specs/README.md` and `docs/DOCS_INDEX.md`.
7. **v1.1.0 A+ amendments applied:** description core/frame ruling (OPD-20260707-001, skinning ban), persona table re-keyed to the canonical SSOT, overlay layer label corrected to production-dormant truth, persistent cross-wave shingle index + rollout ladder + exemption ledger.

**Status claim:** This document is **SPECCED**. Implementation layers remain **ABSENT** until follow-on PRs land.
