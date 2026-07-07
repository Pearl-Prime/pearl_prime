# Author Commentary — Archaeology Report

**Date:** 2026-07-07  
**Mission:** Investigate prior art for witness-register author commentary before spec + pilot.  
**Six-layer key:** `ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`

---

## Executive finding

**No dedicated `AUTHOR_COMMENTARY` accent class, atom bank, or witness-register engine has ever shipped.** The pattern the operator remembers is **real but split across three layers** that must not be conflated:

| Layer | What it was | Status today | Resurrection path |
|-------|-------------|--------------|-------------------|
| **Content pattern** | Witness voice — "I've seen people… / maybe it'll help you too" | **ABSENT** in banks; **RESEARCHED** in grief/shame doctrine | Authored `AUTHOR_COMMENTARY` accent atoms |
| **Teacher disclosure** | "I came across this teaching tradition…" generalized wrapper variant | **CONFIG-EXISTS** in `teacher_wrapper_templates.yaml` | **Teacher-mode `source_disclosure` atoms only** — never re-enable wrapper injection |
| **Render glue** | Seven template families + flow glue + component stacking | **CODE-WIRED, default OFF** (`render_glue_enabled()` → `False`) | **Must stay retired** |

**Critical trap (confirmed):** The teacher-mode "I came across the teachings of…" pattern **partially lived in `teacher_wrapper`** — one of the glue sources killed by de-injection (#4644 / `COMPOSER_DEINJECTION_AND_TISSUE_SPEC_2026-07-05.md`). The resurrection is **authored atoms in the accent system**, never the wrapper coming back.

---

## 1. Witness-register prior art

### 1.1 Searches (negative)

| Pattern | Result | Layer |
|---------|--------|-------|
| `"I've seen people"` in atoms/banks | **ABSENT** | — |
| `AUTHOR_COMMENTARY` / `COMMENTARY_*` atom IDs | **ABSENT** | — |
| `witness_register` code module | **ABSENT** | — |

### 1.2 Searches (positive — adjacent, not commentary)

| Artifact | Path | Layer | Relevance |
|----------|------|-------|-----------|
| Author voice doctrine | `specs/PHOENIX_V4_5_WRITER_SPEC.md` §2 | **SPECCED** | "The author. Not a guru." Slot×person voice table |
| One Author + Wrappers | `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` § Voice Architecture | **SPECCED** | Author references teacher; never speaks as teacher |
| Shame STORY witness | `specs/PHOENIX_V4_5_WRITER_SPEC.md` shame row | **SPECCED** | "witness (real or implied)" in STORY atoms |
| Grief witnessing_presence | `docs/DEPTH_MODULE_PROTOCOL.md` | **CONFIG-EXISTS** | Grief-only PERMISSION/REFLECTION depth module |
| Megan Devine benchmark | `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md` | **RESEARCHED** | 70% witness/validation ratio (grief) |
| Pearl News teacher_witness | `docs/PEARL_NEWS_5_VARIATION_EXPANSION_PROGRAM.md` | **SPECCED** | "teacher has seen this" bridge atoms (news lane, not book accent) |
| Pen-name bio witness voice | `assets/authors/*/bio.yaml`, `why_this_book.yaml` | **CONFIG-EXISTS** | Lived-experience positioning without clinical claims |

**Verdict:** Witness register is **doctrinally supported** but **never banked as placeable commentary beats**.

---

## 2. Teacher-mode disclosure pattern — today vs retired

### 2.1 What survives (authored / config — keep-able)

**`config/catalog_planning/teacher_wrapper_templates.yaml`** — generalized mode variant (line 89):

> "I came across this teaching tradition at a time when nothing else was landing."

Anti-patterns explicitly banned (lines 69–77): `"I came across this teacher"`, `"Master X says…"`, named-individual attribution in generalized mode.

**`phoenix_v4/rendering/teacher_wrapper.py`** — **CODE-WIRED**, resolves `(prefix, suffix)` for teacher atoms. Returns `("", "")` on unresolved slots (safety).

**`phoenix_v4/planning/enrichment_select.py`** — `apply_wrapper()` on teacher substance slots.

**Overlay doctrine** — author references Ahjan; never impersonates (`PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`).

**F12 register gate** — `phoenix_v4/quality/register_gate.py` catches raw "Master X says…" bypassing wrappers.

### 2.2 What was retired (render glue — must stay OFF)

**`phoenix_v4/rendering/render_glue.py`** — `render_glue_enabled()` returns **`False`** unless `PHOENIX_ENABLE_RENDER_GLUE=1`.

Seven de-injection families (`COMPOSER_DEINJECTION_AND_TISSUE_SPEC_2026-07-05.md` Part A):

1. `bridge_transition_families.yaml`
2. `mechanism_thesis_families.yaml`
3. `exercise_wrapper_families.yaml`
4. `within_slot_bridge_families.yaml`
5. `_takeaway_fallback` (composer)
6. Constant chapter handoff (composer)
7. `_append_anxiety_chapter_one_scan_practice` (composer)

**Git anchor:** `665e390ded` — "template glue OFF — teacher/science wrappers + exercise intros"

**Distinction for this mission:**

| Mechanism | Layer | In scope? |
|-----------|-------|-----------|
| `teacher_wrapper` resolver + templates | **CODE-WIRED** (attribution framing on teacher atoms) | **Out of scope** — do not extend; do not re-enable as accent injection |
| Render-time glue families | **CODE-WIRED, OFF** | **Banned** — any proposal to re-enable is BLOCKER |
| `AUTHOR_COMMENTARY` authored atoms | **ABSENT → SPECCED** | **In scope** — carries disclosure pattern as complete paragraphs |

**`source_disclosure` commentary type** rehomes the *content* of generalized intro_wrapper ("I came across…") into planner-placed accent atoms for teacher-mode books only. Composite commentary **must carry zero teacher/tradition reference**.

---

## 3. Author system — verified live state

| Component | Path | Layer | State |
|-----------|------|-------|-------|
| Author registry | `config/author_registry.yaml` | **CONFIG-EXISTS** | 12 stillness_press + way_stream + legacy; all `status: draft` |
| Positioning profiles | `config/authoring/author_positioning_profiles.yaml` | **CONFIG-EXISTS** | 4 profiles (somatic_companion, research_guide, elder_stabilizer, devotional_companion) |
| Bio bundles | `assets/authors/<author_id>/` | **CONFIG-EXISTS** | 4-file bundle where complete: bio, authority_position, why_this_book, audiobook_pre_intro |
| Topic routing | `config/brand_author_assignments.yaml` + resolver | **CODE-WIRED** | Operator memory: router collapses to `lena_thorne` for unmatched pools (OPD-20260701-002) — **topic-fit selection specced, not commentary-specific** |
| Multi-brand design | registry comments | **CONFIG-EXISTS** | Multi-author designed; stillness_press has 12 pen-names; way_stream has 12 |

### 3.1 Bio depth inventory (active pilot-relevant authors)

| Author | Persona × topic fit | Bio depth | Authority bundle | Commentary license |
|--------|---------------------|-----------|------------------|-------------------|
| **ravi_chandra** | `gen_z_professionals` × `anxiety` (+ related) | **Thin** (1 paragraph) | **ABSENT** | **Insufficient** — enriched in pilot PR |
| kai_okafor | `gen_z_professionals` × overthinking/social_anxiety | Medium (6 sentences) | Partial (bio only) | Anxiety commentary weak |
| lena_thorne | millennial_women/healthcare × anxiety | **Deep** (6 sentences + full bundle) | **CONFIG-EXISTS** | Wrong persona for flagship cell |
| rowan_beck | tech_finance/millennial × anxiety | Medium | Partial | Wrong persona |

### 3.2 Flagship cell author selection

| Field | Value |
|-------|-------|
| **Pearl Prime acceptance cell** | `ahjan × gen_z_professionals × anxiety × en-US` |
| **Teacher** | Ahjan (cited, not impersonated) |
| **Pen-name for gen_z × anxiety catalog** | **ravi_chandra** (`way_stream_sanctuary`) — only registry row with both |
| **Stillness_press gap** | No pen-name maps `gen_z_professionals` + `anxiety` — catalog assignment debt, not commentary blocker |

---

## 4. Accent family context

| Accent class | Bank path | Layer (today) |
|--------------|-----------|---------------|
| QUOTE | `SOURCE_OF_TRUTH/accent_banks/quotes/` | **CONFIG-EXISTS** (`status: unwired`) |
| CITED_EVIDENCE | specced, not banked | **SPECCED** |
| ENCOURAGEMENT / etc. | reuse PERMISSION/INTEGRATION | **EXECUTED-REAL** (embedded) → accent re-key **SPECCED** |
| WISDOM_ESSENCE | — | **ABSENT** (parallel lane; traditions' distilled voice) |
| **AUTHOR_COMMENTARY** | — | **ABSENT** → **SPECCED** (this mission) |

Four-source personality layer (operator framing): **quotes** (others' words) · **evidence** (science) · **wisdom essence** (traditions) · **author commentary** (author's witness voice).

---

## 5. Git history anchors

```
61be885ced research(voice): author-first + wrapper voice-doctrine grounding (#1531)
8a83945303 spec(bestseller): dwell-beat + one-author/wrapper voice doctrine (#1527)
56809c9d97 fix(teacher-wrapper): diversify named.intro_wrapper variants 4→11 (#1183)
5272cc245b feat(arch): TEACHER-MODE-WRAPPER-SEMANTICS-01 cap entry (#1179)
665e390ded fix(render): template glue OFF — teacher/science wrappers + exercise intros
13441bbc80 feat(authoring): brand-1 author system atomic — registries + 48 author bundles (#885)
```

No commit ever landed `AUTHOR_COMMENTARY` atoms. Commentary grep hits are **manga** research docs, not book accent lane.

---

## 6. Enriched bio — ravi_chandra (operator approved)

**Status:** `operator_approved` (OPD-20260707-002, 2026-07-07) — pilot atoms licensed against this bio; Q-AUTH defaults ratified (3/book, beats-only v1, ravi_chandra now).

```yaml
author_id: ravi_chandra
pen_name: "Ravi Chandra"
bio: >
  Ravi Chandra is a startup engineer in Brooklyn who spent years performing calm in standups while his chest ran a louder meeting underneath.
  He writes for Gen Z professionals who are good at their jobs and tired of pretending the alarm in their body is a personal failure.
  What changed for him was not a mindset hack — it was learning to treat the chest noise as information arriving early, not evidence that he was broken.
  He has watched teammates try the same small practices he uses between commits: a pause before replying, a hand on the sternum during a loading screen, naming the freeze without calling it laziness.
  The ones who stuck with it did not become zen — they became harder to gaslight about how they were feeling.
  His writing draws on Ahjan's contemplative-Buddhism framework of the alarm within, translated into the language of Slack threads and sprint reviews — always as an observer sharing what helped, never as a teacher impersonating a lineage.
word_count_target: 120-180
status: operator_approved
```

**License claims usable in commentary:**

- Performed calm while body alarm ran (personal-admission, skeptic's-companion)
- Watched teammates try small practices (observed-pattern, gentle-endorsement)
- Startup engineer / Gen Z professional context (setting color)
- Ahjan framework as observer disclosure (source_disclosure — **teacher-mode only**)
- No clinical credentials, no cure promises (authority_position enforced)

---

## 7. Six-layer summary

| Component | Layer |
|-----------|-------|
| Witness-register banks | **ABSENT** |
| Teacher disclosure templates | **CONFIG-EXISTS** |
| teacher_wrapper resolver | **CODE-WIRED** (teacher atoms — not accent injection) |
| render_glue + 7 families | **CODE-WIRED, default OFF** (retired) |
| Author registry + bios | **CONFIG-EXISTS** (draft) |
| AUTHOR_COMMENTARY spec | **SPECCED** (amendment in `ACCENT_BEATS_SYSTEM_SPEC.md` §12) |
| Pilot bank | **CONFIG-EXISTS** (`SOURCE_OF_TRUTH/accent_banks/author_commentary/`, unwired) |

**Wiring:** **ABSENT** by design — parks with accent build order after `flagship-read-approved`.
