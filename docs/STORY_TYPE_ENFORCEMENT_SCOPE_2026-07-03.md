# Scope — Story-Type / Naming / Variety Enforcement (the §9 mechanism)

**Author:** Pearl_Architect · **Date:** 2026-07-03
**Doctrine:** `feedback_memory_is_recall_not_enforcement` — a lesson that isn't a CI gate / can't-bypass default / CLAUDE.md rule will drift. The story-design authority (`docs/STORY_TYPES_AND_STRUCTURES.md`, restored #4595) is currently **recall only**. This scopes the enforcing mechanism.
**Rule 0 of this scope:** EXTEND the existing linter, do NOT greenfield.

---

## What already exists (anti-reinvention baseline)

| asset | state | covers |
|---|---|---|
| `phoenix_v4/quality/story_atom_lint.py` (304 lines, deterministic, no LLM) | **live, per-atom** | 4 of 5 elements — **specificity** (proper-noun∨action∨sensory), **internal conflict**, **cost**, **insight pivot**; word floor 120; PASS/WARN/FAIL via the rubric's "missing ≥2 → rewrite" rule. Already computes `count_proper_nouns()`. |
| `schemas/story_atom_lint_v1.schema.json` | live | the lint-report output contract (`status`, `summary`, per-atom `issues`) |
| teacher-mode STORY atoms (280 files) | **tagged** | carry `story_origin` + `story_type` (40/40 sampled) |
| `config/teachers/teacher_registry.yaml` | live | `teacher_as_principle: true` present (the principle-teacher rule input) |
| 218 persona STORY pools (`atoms/<p>/<t>/STORY/CANONICAL.txt`) | **UNtagged** | carry `MECHANISM_DEPTH / IDENTITY_STAGE / COST_TYPE` only — **no `story_type`** |
| CI wiring | **none** | nothing gates on `story_atom_lint.py`; tests reference sibling SCENE linters only |

**So the gap is precise:** the atom-quality half is built and strong; what's missing is (a) the `story_type`/`story_origin` **conformance** rules, (b) the **naming** flag for `character_study`, (c) **book-level variety**, (d) **CI wiring as a gate**, and (e) the 218 pools aren't tagged, so any type check is vacuous on the catalog until tagging lands.

---

## The checks to add (all deterministic, no LLM — extend `story_atom_lint.py`)

### A. `story_type` / `story_origin` conformance (§7 of the authority) — enforceable NOW on the 280 tagged teacher atoms
Pure metadata rules; FAIL on violation:
1. `story_origin: composite` ⇒ `story_type != recognition_exchange` (composite can't put the teacher in-scene).
2. teacher has `teacher_as_principle: true` (from registry) ⇒ `story_type ∈ {parable, atmospheric, direct_teaching}` (never `recognition_exchange`/`character_study`-as-character).
3. `story_type: recognition_exchange` ⇒ `story_origin: true_story` (required).
4. `story_type` present ⇒ value ∈ the 5-type enum; else `UNKNOWN_STORY_TYPE`.

### B. `character_study` naming flag (§3 rule #1: "give her a name") — reuse the existing `count_proper_nouns()`
- `story_type: character_study` AND `count_proper_nouns(prose) == 0` ⇒ flag `CHARACTER_STUDY_UNNAMED` (WARN).
- Rationale: the authority mandates a named protagonist for the deepest reader-recognition type. This is the enforceable form of the naming gap.

### C. Book-level variety (§9) — new book-level pass (not per-atom)
- Across a compiled book's selected STORY atoms, count distinct `story_type` values. `< 2 distinct` ⇒ WARN `LOW_STORY_TYPE_VARIETY` (advisory per §9, never a compile failure).

### D. Coverage/tagging gap surfacing (the honest interim)
- Report `story_type`-tagged vs untagged STORY atoms per scope. On the 218 persona pools this reads **0% tagged** today — emit as a **coverage WARN with a count**, NOT a per-atom FAIL (silent-cap avoidance; the gap must be visible, not a red wall).

---

## Phasing (because the catalog is untagged — order matters)

**Phase 1 — extend + prove (no gate flip).** Add checks A + B + C to `story_atom_lint.py` as pure functions + unit tests. Run in report-only mode. A/B/C are enforceable immediately on the 280 tagged teacher atoms; on persona pools they no-op (no `story_type`) except the coverage WARN (D). **Low risk, ships now.**

**Phase 2 — wire as a CI gate (WARN → then BLOCK on the tagged scope).** New `.github/workflows` step (or extend the atoms parse-sweep) running `story_atom_lint.py --json-out` over changed STORY atoms; BLOCK on schema-conformance FAILs (A) for tagged atoms; WARN on B/C/D. Add to required checks only after a green baseline. Paths-filtered to `atoms/**/STORY/**` + `SOURCE_OF_TRUTH/**/STORY/**` (CI-cost doctrine).

**Phase 3 — add `story_type` to the persona-pool format + tag the catalog.** Extend the `CANONICAL.txt` frontmatter to accept `STORY_TYPE:` (alongside `MECHANISM_DEPTH` etc.); backfill the 218 pools (Pearl_Writer / Claude-writes, Tier-1 — content classification, not code). Only after this does variety (C) and the naming flag (B) become meaningful catalog-wide.

**Phase 4 — flip variety + naming to enforced defaults.** Once the catalog is tagged and green, promote `LOW_STORY_TYPE_VARIETY` and `CHARACTER_STUDY_UNNAMED` from WARN to the book-acceptance criteria. This is the can't-bypass default the doctrine wants.

---

## Decisions for the operator (genuinely yours)

1. **Naming — enforce or accept?** The 196 unnamed pools are deep and pass the five-element check; the authority *mandates* names for `character_study`. Flip `CHARACTER_STUDY_UNNAMED` to BLOCK eventually, or leave WARN and accept unnamed-deep as catalog register? (Recommend: WARN now; decide at Phase 4 after reading a named vs unnamed book side-by-side.)
2. **Tagging owner/route** — Phase 3 backfill is content classification of 218 pools. Deterministic heuristic first-pass (classify by structure: has-name→character_study, no-character→atmospheric, teacher-voice→direct_teaching) then human review, vs full Pearl_Writer pass?
3. **Gate severity for untagged catalog** — coverage WARN (recommended) vs hard "must-tag" BLOCK (would red-wall CI until 218 pools are tagged — not recommended yet).

---

## Deliverable boundary

This doc is scope only. Phase 1 (extend `story_atom_lint.py` with A/B/C/D + tests, report-only) is a self-contained next PR — buildable now, low-risk, immediately enforcing on the 280 tagged teacher atoms. Say the word and it ships.
