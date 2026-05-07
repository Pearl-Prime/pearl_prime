# Per-Chapter Overlay Enforcement V1 Spec

**Spec ID:** PER-CHAPTER-OVERLAY-ENFORCEMENT-V1  
**Status:** ratified (2026-05-08)  
**Cap entry:** PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01 in `docs/PEARL_ARCHITECT_STATE.md`  
**Authority docs:**  
- `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`  
- `specs/PHOENIX_V4_5_WRITER_SPEC.md`  
- `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md`  
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`  
**Project:** PRJ-PEARL-PRIME-Q-GATES  
**Subsystem:** core_pipeline  
**Unblocks:** ITEM-2 (`your nervous system` removal from `config/quality/refrain_allowlist.yaml`)  
**Sprint 1 YELLOW ITEM-1 SHA:** aed7d2a017b5ecff6ede1cad8411ba35388cb724 (PR #941)  
**Owner:** Pearl_Dev (implementation), Pearl_Architect (spec authority)

---

## 1. Purpose and Scope

The book-wide refrain cap introduced in PR #941 (YELLOW ITEM-1) is a necessary but
insufficient quality gate. It catches phrases that appear too many times across the
entire manuscript but is blind to intra-chapter overuse: a phrase that appears only
twice per chapter across 12 chapters satisfies the book-wide cap of 18 but can still
produce a reader experience of relentless repetition within a single sitting.

This spec defines per-chapter overlay enforcement: a second-pass gate that runs on
individual chapter text after the book-wide check and enforces structural rules for
how refrain phrases are distributed across the book's chapters. The two gates compose
as a logical AND: a phrase must satisfy BOTH the book-wide cap AND every applicable
overlay rule to pass.

**Out of scope (this spec):** modifying `phoenix_v4/quality/book_quality_gate.py`
rule-enforcement code beyond extending `_repeated_phrase_violations` and the
allowlist schema loader. No changes to production pipelines, render paths, or atom
banks in this spec.

---

## 2. Overlay Rule Types

Four overlay rule types are defined. Each is precise, citeable, and maps to a
distinct reader-experience failure mode identified in
`docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md`.

### 2.1 DENSITY_CEILING

**Definition:** A phrase may appear at most N times within a single chapter.

**Default N:** 2 for `legitimate_motif` entries (one invocation early in chapter,
one later; a third signals the author is relying on the phrase as a crutch within
that chapter).

**Failure signal:** The gate reports: `OVERLAY:density_ceiling — "<phrase>" appears
<count> times in chapter <n> (limit: <N>)`.

**Spec source:** `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md §6 Pacing Rules`
— repetition of a phrase within the same chapter shifts the phrase from intentional
refrain to authorial tic; readers notice and annotate "repetitive" in reviews.

**Reader-experience failure mode:** Within-chapter mantra fatigue. Readers do not
step away from a chapter between occurrences; three uses in 2,000 words land as
relentless padding.

### 2.2 PRESENCE_FLOOR

**Definition:** A phrase must appear at least once in each of the named structural
chapter classes. Structural classes are: `opening` (chapter 1), `mid` (chapters
4–8 in a 12-chapter book), `climax` (chapters 9–10).

**Failure signal:** The gate reports: `OVERLAY:presence_floor — "<phrase>" absent
from structural chapter class [opening|mid|climax]`.

**Spec source:** `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (SOMATIC
SLOT GRID) — motif phrases defined as spine refrains are expected to appear in the
opening setup, mid-section development, and climax resolution to form a resonance
arc. Absence in a structural class breaks the arc.

**Reader-experience failure mode:** Arc discontinuity. If a refrain phrase that
anchors the book's spine vocabulary is absent from the climax, readers sense an
unresolved loop even if they cannot articulate why.

### 2.3 DRIFT_DETECTION

**Definition:** A chapter containing a phrase 3 or more times triggers a per-chapter
violation regardless of the book-wide cap. This is a tighter-than-book-wide threshold
applied per chapter.

**Threshold:** ≥ 3 occurrences in any single chapter = violation.

**Failure signal:** The gate reports: `OVERLAY:drift_detection — "<phrase>" appears
<count> times in chapter <n> (drift threshold: 3)`.

**Spec source:** `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md §2 Voice/Register`
— books that underperform in audio format show phrase repetition clusters; a word or
phrase that appears three or more times in one chapter is flagged by listeners as a
narrator error or manuscript defect, not intentional style.

**Reader-experience failure mode:** Phrase drift. The original legitimate_motif
purpose of the phrase is undermined when it clusters in a single chapter; the phrase
stops functioning as a motif and starts functioning as unedited output noise.

**Interaction with book-wide cap:** DRIFT_DETECTION fires independently of whether
the book-wide cap is exceeded. An entry with cap_book_wide=18 that appears 18 times
book-wide but clusters 5 times in chapter 3 triggers DRIFT_DETECTION even though
it is within the book-wide limit.

### 2.4 ABSENCE_GUARD

**Definition:** A phrase must NOT appear in certain chapter classes. Chapter classes
that are out-of-scope for a given phrase type are defined per-entry in `overlay_param`.

**Default excluded classes for `doctrinal_attribution` entries:**
`compression_chapters` — chapters flagged in the chapter flow spec as
"compression" (high-concept density; reader already processing abstract content;
adding attribution phrases competes for cognitive space).

**Failure signal:** The gate reports: `OVERLAY:absence_guard — "<phrase>" appears
in excluded chapter class [<class>] (chapter <n>)`.

**Spec source:** `specs/PHOENIX_V4_5_WRITER_SPEC.md §4 TEACHER_DOCTRINE` —
attribution phrases serve a distinct rhetorical function (establishing doctrinal
credibility); they are appropriate in setup and integration chapters but
inappropriate in compression chapters where reader attention is fully absorbed by
mechanism explanation.

**Reader-experience failure mode:** Attribution overload in concept-heavy sections.
When a reader is already tracking a new concept, adding "drawing on ahjan" or
"according to ahjan" interrupts the cognitive chain.

---

## 3. Composition Rule

The composition rule is:

```
PASS = book_wide_cap_ok AND all_overlay_rules_ok
```

The violation dict returned by `_repeated_phrase_violations` must include a `rule`
key reporting which rule fired:

```python
{
    "phrase": "your nervous system",
    "count": 22,
    "rule": "book_wide_cap"            # fired by book-wide check
}

{
    "phrase": "your nervous system",
    "count": 4,
    "chapter": 3,
    "rule": "overlay:drift_detection"  # fired by per-chapter overlay
}
```

**Critical distinction:** `cap_per_chapter` (a numeric ceiling, the integer field
in the YAML) and `overlay_rule` (a structural rule type, the enum field in the YAML)
are distinct concepts and must not be conflated.

- `cap_per_chapter` is a simple integer threshold: how many times a phrase may appear
  in any single chapter before triggering a density ceiling violation. It applies to
  ALL entries unconditionally.
- `overlay_rule` is a structural rule type (`density_ceiling`, `presence_floor`,
  `drift_detection`, `absence_guard`, or `none`) that encodes a structural assertion
  about the phrase's distribution across the book's chapter architecture. An entry
  may have `cap_per_chapter: 2` AND `overlay_rule: presence_floor` simultaneously:
  the former says "no more than 2 per chapter"; the latter says "must appear at least
  once in opening + mid + climax chapters".

---

## 4. Extended YAML Schema

The following optional fields are added to each entry in
`config/quality/refrain_allowlist.yaml`. All fields are optional; absence of
`overlay_rule` defaults to `none` (full backward compatibility).

```yaml
# Extended schema — optional overlay fields (default: overlay_rule: none)
overlay_rule: none  # density_ceiling | presence_floor | drift_detection | absence_guard | none
overlay_param:
  N: 2                                            # for density_ceiling: per-chapter ceiling
  structural_chapters: [opening, mid, climax]     # for presence_floor: required chapter classes
  excluded_chapter_classes: []                    # for absence_guard: banned chapter classes
```

**Schema field definitions:**

| Field | Type | Default | Applies to |
|---|---|---|---|
| `overlay_rule` | enum | `none` | all entries |
| `overlay_param.N` | int | 2 | `density_ceiling` |
| `overlay_param.structural_chapters` | list[str] | `[opening, mid, climax]` | `presence_floor` |
| `overlay_param.excluded_chapter_classes` | list[str] | `[]` | `absence_guard` |

**Chapter class definitions (12-chapter canonical book):**

| Class name | Chapter indices (1-based) | Source |
|---|---|---|
| `opening` | 1 | `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md §3 Opening Hook` |
| `mid` | 4–8 | `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (SOMATIC SLOT GRID) |
| `climax` | 9–10 | `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (SOMATIC SLOT GRID) |
| `compression_chapters` | runtime-determined via chapter flow gate | `specs/PHOENIX_V4_5_WRITER_SPEC.md §4` |

**Anti-drift rule:** Every `overlay_param` value must have a corresponding
`spec_citation` field on the entry citing the source. Silent thresholds are prohibited.

---

## 5. Migration Path (ITEM-2 Unblock Chain)

### Phase 1 — Implement overlay enforcement (back-compat)

Pearl_Dev implements:

1. Extend the YAML loader in `phoenix_v4/quality/book_quality_gate.py` to parse
   `overlay_rule` and `overlay_param` fields from `config/quality/refrain_allowlist.yaml`.
2. Extend `_repeated_phrase_violations` to accept a list of allowlist entries with
   overlay rules and apply them per-chapter after the book-wide check.
3. All current entries default to `overlay_rule: none` — NO behavior change in Phase 1.
4. Violation dicts include `rule` key reporting `book_wide_cap` or
   `overlay:<rule_type>` for every violation.
5. Tests: unit tests for each of the four overlay rule types plus the composition rule.
6. Validate against the 50,344-word reference book (deep_book_6h anxiety×gen_z,
   first produced at SHA 635e1a96bf) — no new violations introduced in Phase 1.

**Phase 1 acceptance:** All existing tests pass. Reference book produces same
violation count as pre-Phase-1. Four overlay rule type unit tests pass.

### Phase 2 — Per-entry overlay_rule assignment sweep

Pearl_Dev (in a separate PR after Phase 1 merges):

For each of the 43 entries in `config/quality/refrain_allowlist.yaml`, assign the
appropriate `overlay_rule` and `overlay_param` per the table in §6 below. Revalidate
the reference book end-to-end after each batch of assignments. Iterate until the
reference book produces the expected violation profile.

**Phase 2 acceptance:** All 43 entries have an explicit `overlay_rule` (no `null`
or absent overlay_rule left). Reference book revalidated with at least one end-to-end
run after final assignments.

### Phase 3 — ITEM-2 removal of `your nervous system`

Preconditions (both required):

- Phase 2 merged and validated.
- EITHER: the `drift_detection` overlay rule catches `your nervous system` clustering
  in the reference book (≥3 occurrences in any chapter), OR the default book-wide
  cap (>12 for non-allowlisted phrases) catches it when the allowlist entry is removed.

Pearl_Dev removes the `your nervous system` entry from
`config/quality/refrain_allowlist.yaml` in a separate PR. Reruns the reference book.
The gate must fire on `your nervous system` without the allowlist entry — proving the
overlay enforcement is the actual enforcement mechanism and the allowlist entry was
only masking a real defect.

**Phase 3 acceptance:** Reference book run WITHOUT the allowlist entry produces a
violation for `your nervous system`. The violation dict reports `rule: overlay:drift_detection`
OR `rule: book_wide_cap` (the latter means the phrase density exceeds 12 book-wide,
so the default cap is sufficient). Either outcome is acceptable; the requirement is
that at least one gate catches it.

---

## 6. Per-Entry Overlay Assignment Table

This table defines the target `overlay_rule` assignment for each entry in Phase 2.
Phase 1 leaves all entries at `overlay_rule: none`. Phase 2 implements these
assignments.

**Legend:**
- `DC(N)` = density_ceiling with N per chapter
- `PF` = presence_floor (opening + mid + climax)
- `DD` = drift_detection (fires at ≥3 in any chapter)
- `AG(class)` = absence_guard for the named chapter class

Note: `cap_per_chapter` handles the numeric DC(2) threshold in the existing YAML
field. `overlay_rule` in Phase 2 is set to the structural type only. An entry
showing `DC(2) + PF` in this table means `cap_per_chapter: 2` (already set in
Phase 1) and `overlay_rule: presence_floor` (set in Phase 2).

### Group A — Core somatic instruction motifs (entries 1–15)

Full-phrase entries warrant `presence_floor` (the exercise frame should appear in
each structural zone); fragment entries warrant `density_ceiling` numeric only
(governed by parent's structural placement).

| # | Phrase | Classification | Target overlay_rule (Phase 2) |
|---|---|---|---|
| 1 | "the point is that" | legitimate_motif | presence_floor |
| 2 | "i want you to" | legitimate_motif | presence_floor |
| 3 | "now i want you" | legitimate_motif | presence_floor |
| 4 | "not to fix anything" | legitimate_motif | presence_floor |
| 5 | "anything just to" | legitimate_motif | none (fragment; governed by parent #4) |
| 6 | "fix anything" | legitimate_motif | none (fragment) |
| 7 | "to fix anything" | legitimate_motif | none (fragment) |
| 8 | "just to give yourself" | legitimate_motif | presence_floor |
| 9 | "to give yourself" | legitimate_motif | none (fragment) |
| 10 | "give yourself a" | legitimate_motif | none (fragment) |
| 11 | "before you move on" | legitimate_motif | presence_floor |
| 12 | "a different input" | legitimate_motif | presence_floor |
| 13 | "different input for" | legitimate_motif | none (fragment) |
| 14 | "input for a" | legitimate_motif | none (fragment) |
| 15 | "one breath at a time" | legitimate_motif | presence_floor |

### Group B — Sprint-1 scene-anchor motifs (entries 16–36)

Root motif sentences warrant `presence_floor`; n-gram fragments warrant
`drift_detection` (fragment clustering ≥3 signals parent is overused in that chapter).

| # | Phrase | Classification | Target overlay_rule (Phase 2) |
|---|---|---|---|
| 16 | "you have been looking" | legitimate_motif | presence_floor |
| 17 | "have been looking" | legitimate_motif | drift_detection |
| 18 | "been looking at" | legitimate_motif | drift_detection |
| 19 | "looking at it for" | legitimate_motif | drift_detection |
| 20 | "at it for forty" | legitimate_motif | drift_detection |
| 21 | "it for forty minutes" | legitimate_motif | drift_detection |
| 22 | "the task is open" | legitimate_motif | presence_floor |
| 23 | "task is open you" | legitimate_motif | drift_detection |
| 24 | "is open you have" | legitimate_motif | drift_detection |
| 25 | "open you have been" | legitimate_motif | drift_detection |
| 26 | "your body knows" | legitimate_motif | presence_floor |
| 27 | "your nervous system" | legitimate_motif | **drift_detection** (ITEM-2 target: Phase 3 removes when DD catches it) |
| 28 | "body knows something" | legitimate_motif | drift_detection |
| 29 | "knows something your" | legitimate_motif | drift_detection |
| 30 | "something your calendar" | legitimate_motif | drift_detection |
| 31 | "not forever just" | legitimate_motif | presence_floor |
| 32 | "it was the cost" | legitimate_motif | presence_floor |
| 33 | "was the cost of" | legitimate_motif | drift_detection |
| 34 | "the alarm does not" | legitimate_motif | presence_floor |
| 35 | "the alarm dressed" | legitimate_motif | presence_floor |
| 36 | "the foundation of contemplative" | legitimate_motif | presence_floor |

### Group C — TEACHER_DOCTRINE attribution phrases (entries 37–43)

Attribution phrases must not appear in compression chapters.

| # | Phrase | Classification | Target overlay_rule (Phase 2) |
|---|---|---|---|
| 37 | "drawing on ahjan" | doctrinal_attribution | absence_guard(compression_chapters) |
| 38 | "ahjan's mindfulness" | doctrinal_attribution | absence_guard(compression_chapters) |
| 39 | "mindfulness and somatic" | doctrinal_attribution | absence_guard(compression_chapters) |
| 40 | "somatic teaches us" | doctrinal_attribution | absence_guard(compression_chapters) |
| 41 | "according to ahjan" | doctrinal_attribution | absence_guard(compression_chapters) |
| 42 | "that is the part" | doctrinal_attribution | absence_guard(compression_chapters) |
| 43 | "the remote work improved" | doctrinal_attribution | absence_guard(compression_chapters) |

---

## 7. Anti-Drift Rules

1. **No silent thresholds.** Every `overlay_param` value must be backed by a
   `spec_citation` field on the entry pointing to the spec section that mandates it.

2. **No removal from allowlist without reference-book revalidation.** Before any
   entry is removed from `config/quality/refrain_allowlist.yaml`, the 50,344-word
   reference book (deep_book_6h anxiety×gen_z, SHA 635e1a96bf) must be regenerated
   end-to-end and the gate must fire on the removed phrase without the allowlist entry.

3. **No overlay rule changes without end-to-end rerun.** Changing `overlay_rule` or
   `overlay_param` for any entry requires regenerating the reference book through
   the full pipeline before the PR merges.

4. **Gate must report which rule fired.** Every violation dict must include a `rule`
   key. Valid values: `book_wide_cap`, `overlay:density_ceiling`,
   `overlay:presence_floor`, `overlay:drift_detection`, `overlay:absence_guard`.
   A violation that does not name its rule is non-conforming.

5. **cap_per_chapter and overlay_rule are distinct.** `cap_per_chapter` is a numeric
   ceiling enforced on every chapter unconditionally. `overlay_rule` is a structural
   rule type that applies additional structural logic. They compose independently and
   must be documented separately in the violation dict.

6. **Tier 1 only for design and spec authoring.** Per LLM Tier Policy in `CLAUDE.md`:
   spec authoring is Claude Code (operator-present). No paid LLM API.

---

## 8. Action Items

| # | Owner | Task | Gate |
|---|---|---|---|
| a | Pearl_Dev | Phase 1: extend gate + YAML schema + tests; separate PR after this cap merges | cap-entry PR merged |
| b | Pearl_Dev | Phase 2: per-entry overlay_rule assignment sweep PR | Phase 1 merged + validated |
| c | Pearl_Dev | Phase 3: ITEM-2 — remove `your nervous system` from allowlist | Phase 2 merged; DD catches phrase in reference book |
| d | Pearl_PM | Track `ws_per_chapter_overlay_enforcement_impl` through Phases 1/2/3 | this cap-entry PR merged |

---

## 9. Reference Book Anchor

**Book:** deep_book_6h anxiety×gen_z (ahjan × gen_z_professionals × anxiety)  
**Word count:** 50,344  
**SHA:** 635e1a96bf (PR #939, Sprint 1 all-PASS gate run)  
**PR #941 SHA (ITEM-1):** aed7d2a017b5ecff6ede1cad8411ba35388cb724  
**Gate artifact:** `artifacts/qa/sprint1_ignored_prefixes_conformance_2026-05-08.md`
(absent at spec authoring time; to be produced in Phase 1 revalidation)

---

*Spec authority: Pearl_Architect | 2026-05-08*
