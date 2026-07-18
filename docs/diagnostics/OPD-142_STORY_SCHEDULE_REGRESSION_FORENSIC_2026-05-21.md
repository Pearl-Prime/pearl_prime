# OPD-142 — Forensic: story_schedule routing regression between PR #669 and HEAD

**Date:** 2026-05-21
**Author:** Pearl_Dev forensic investigator
**Scope:** READ-ONLY diagnosis. NO production code changes in this PR.
**Window:** PR #669 (commit `cbfbe14c3`, 2026-04-26, working) → HEAD on `main` (commit `da2374e26`, 2026-05-21, broken)
**Evidence:** `artifacts/pearl_prime/deep_book_6h/HOLISTIC_V2_POST_PHASEB_2026-05-21/enrichment_audit.json`

---

## TL;DR (one-paragraph)

PR #1248 (commit `639f273fb`, "OPD-116/117 Phase B — angle journey chapter_planner + composer + gate") introduced `phoenix_v4/planning/angle_journey.py::apply_angle_journey_slots` / `patch_beatmap_angle_journey`. For any book with `angle_id` set and a long-form runtime (`standard_book`, `extended_book_2h`, `deep_book_4h`, `deep_book_6h`), this inserts `ANGLE_DEFINITION` into chapter 1 between `HOOK` and the first `STORY`, and inserts `ANGLE_CALLBACK` into chapters 2..N between `HOOK` and the first `STORY`. The insertion preserves the existing slots' `somatic_section_index` (2/5/9 for STORY), but shifts their **slot list position** from `(1, 4, 8)` to `(2, 5, 9)`. The story_schedule routing in `phoenix_v4/planning/enrichment_select.py` (PR #669 line 904, today at line 1707) keys off `_sec_idx = slot_i + 1` — the slot list index, NOT `slot.somatic_section_index`. With `angle_id` set, `slot_i + 1` for STORY slots becomes `(3, 6, 10)`, none of which are in `SCENE_SECTION_INDICES = (2, 5, 9)`. The entire `if stype in ("SCENE", "STORY") and _sec_idx in SCENE_SECTION_INDICES:` guard is bypassed, the `_sched_slot = _story_schedule.get(...)` consultation never happens, and the STORY slots fall through to the `persona_atoms["STORY"]` waterfall (which is what the audit shows: `source = "persona_atom"`, no story_plan routing). The schedule is still BUILT (audit shows 31 entries), it's just never CONSUMED.

---

## §1 Working state (PR #669, commit `cbfbe14c3`, 2026-04-26)

`phoenix_v4/planning/enrichment_select.py` (at the line referenced in the PR #669 commit message as ":904"):

```python
# 0) Story schedule: named-character arcs replace SCENE/STORY slots at section indices 2/5/9.
# section_index is 1-based (slot_i + 1). StorySchedule keys: (chapter_number, section_index).
# STORY check added 2026-04-26 alongside SOMATIC_10_SLOT_GRID sec 2/5/9 SCENE→STORY change:
# preserves story_schedule routing for personas with story_atoms/anchored coverage (gen_z_professionals × anxiety today);
# personas without coverage fall through to persona_atoms["STORY"] waterfall (engine bank + generic 859-bank merged).
_sec_idx = slot_i + 1
if stype in ("SCENE", "STORY") and _sec_idx in SCENE_SECTION_INDICES:
    _sched_slot = _story_schedule.get(bm_ch.number, _sec_idx)
    if _sched_slot is not None and _sched_slot.text:
        content = _sched_slot.text
        source = "story_plan"
        source_id = _sched_slot.source
        atom_id = _sched_slot.source
        audit_counts["slots_from_persona"] += 1  # story atoms count as persona-class
```

Companion grid in `phoenix_v4/planning/beatmap_compile.py` (PR #669 final state, unchanged through HEAD):

```python
SOMATIC_10_SLOT_GRID = [
    "HOOK",              # section_01
    "STORY",             # section_02 — RECOGNITION arc-position
    "REFLECTION",        # section_03
    "EXERCISE",          # section_04 — awareness phase
    "STORY",             # section_05 — MECHANISM_PROOF arc-position
    "TEACHER_DOCTRINE",  # section_06 — mechanism / teacher voice
    "REFLECTION",        # section_07
    "EXERCISE",          # section_08 — regulation phase
    "STORY",             # section_09 — TURNING_POINT arc-position
    "INTEGRATION",       # section_10
]
```

**Invariant that made it work in PR #669:** every chapter has exactly 10 slots. Slot list index `i` and somatic section index `i+1` are identical (0→1, 1→2, …, 9→10). So `_sec_idx = slot_i + 1` correctly identifies STORY positions at `_sec_idx ∈ {2, 5, 9}`.

**Verified working evidence (from PR #669 commit message):** Marcus(6)/Priya(3)/Jordan(2)/Sam(1)/Zoë(4) named characters in `/tmp/path_a_genz_v2/book.txt`, each chapter with same-character × 3 beats.

---

## §2 Broken state (HEAD, commit `da2374e26`, 2026-05-21)

The line at `phoenix_v4/planning/enrichment_select.py:1707-1715` is **identical** to PR #669:

```python
_sec_idx = slot_i + 1
if stype in ("SCENE", "STORY") and _sec_idx in SCENE_SECTION_INDICES:
    _sched_slot = _story_schedule.get(bm_ch.number, _sec_idx)
    if _sched_slot is not None and _sched_slot.text:
        content = _sched_slot.text
        ...
```

The grid in `beatmap_compile.py:42` is **identical** to PR #669.

**What changed:** the slot LIST is no longer the 10-slot grid. With `angle_id` set, every chapter's slot list is mutated by `patch_beatmap_angle_journey` (called from `scripts/run_pipeline.py:632`):

- **Chapter 1** (with `ANGLE_DEFINITION` inserted at list-index 1):

  | slot_i | slot_type        | somatic_section_index | `slot_i + 1` |
  |--------|------------------|------------------------|--------------|
  | 0      | HOOK             | 1                      | 1            |
  | 1      | ANGLE_DEFINITION | 2 (new sec_idx)        | 2            |
  | 2      | **STORY**        | 2 (preserved)          | **3**        |
  | 3      | REFLECTION       | 3                      | 4            |
  | 4      | EXERCISE         | 4                      | 5            |
  | 5      | **STORY**        | 5 (preserved)          | **6**        |
  | 6      | TEACHER_DOCTRINE | 6                      | 7            |
  | 7      | REFLECTION       | 7                      | 8            |
  | 8      | EXERCISE         | 8                      | 9            |
  | 9      | **STORY**        | 9 (preserved)          | **10**       |
  | 10     | INTEGRATION      | 10                     | 11           |

- **Chapter 2+** (with `ANGLE_CALLBACK` inserted at list-index 1): identical shift pattern.

**Runtime evidence (current broken state) from `HOLISTIC_V2_POST_PHASEB_2026-05-21/enrichment_audit.json`:**

```
angle_id: ENGINE
angle_layer_by_chapter: {2: 1, 3: 2, 4: 2, ...}

ch1:
  slot_index=0 stype=HOOK              source=persona_atom+registry+teacher_atom    words=126
  slot_index=1 stype=ANGLE_DEFINITION  source=angle_atom                            words=1317
  slot_index=2 stype=STORY             source=persona_atom (RECOGNITION v02)        words=95   ← should be story_plan
  slot_index=3 stype=REFLECTION        ...
  slot_index=4 stype=EXERCISE          ...
  slot_index=5 stype=STORY             source=persona_atom (RECOGNITION v07)        words=7    ← broken-tiny atom
  slot_index=6 stype=TEACHER_DOCTRINE  ...
  slot_index=7 stype=REFLECTION        ...
  slot_index=8 stype=EXERCISE          ...
  slot_index=9 stype=STORY             source=persona_atom (TURNING_POINT v05)      words=91   ← should be story_plan
  slot_index=10 stype=INTEGRATION      ...

story_schedule[ch=1]:
  sec=2, arc=recognition,     source=story_plan:HARDSHIP:story_0:recognition:overwhelm:v03
  sec=5, arc=mechanism_proof, source=story_plan:HARDSHIP:story_0:mechanism_proof:overwhelm:v05
  sec=9, arc=turning_point,   source=story_plan:HARDSHIP:story_0:turning_point:overwhelm:v08
```

**Diagnosis:**
- `story_schedule` is built correctly (31 entries, all keyed `(chapter, sec)` ∈ {1..12}×{2, 5, 9} = `SCENE_SECTION_INDICES`).
- The waterfall guard `_sec_idx in SCENE_SECTION_INDICES` evaluates `{3, 6, 10} ⊂ {2, 5, 9}` → **False** for every STORY slot in every chapter.
- `_sched_slot.text` is never even consulted; the STORY slot falls through to the persona_atoms["STORY"] waterfall.
- persona_atoms["STORY"] contains generic 859-bank RECOGNITION/MECHANISM_PROOF/TURNING_POINT variants. The dedup-aware pool rotation (OPD-109 Phase 3) picks `RECOGNITION v02`/`v07`/`TURNING_POINT v05` — three different characters across the three slots, wrong arc-positions in sec 5 (RECOGNITION v07 instead of MECHANISM_PROOF), and one broken-tiny atom (7 words).

**Note on the broken-tiny atom (RECOGNITION v07, 7 words):** orthogonal to OPD-142 — it's a separate atom-pool quality issue. OPD-142 only explains why the STORY slots fall through to persona_atoms in the first place.

---

## §3 Regression commit

| Field | Value |
|-------|-------|
| Commit SHA | `639f273fbdc21a94032260aae9ccdad428ed4c5e` |
| PR number | **#1248** |
| Title | `feat(angle): OPD-116/117 Phase B — angle journey chapter_planner + composer + gate` |
| Author | Ahjan108 (squash-merged from `agent/opd-116-117-phase-b-angle-journey`) |
| Date | 2026-05-20 09:18:10 -1000 |

**Added files** (relevant to regression):
- `phoenix_v4/planning/angle_journey.py` — NEW, 232 lines

**Modified files** (relevant to regression):
- `phoenix_v4/planning/chapter_planner.py` — calls `apply_angle_journey_slots` from chapter-planner path
- `scripts/run_pipeline.py:632` — calls `patch_beatmap_angle_journey` from spine path (deep_book_6h)

**Smoking-gun diff snippet** (`phoenix_v4/planning/angle_journey.py:103-161`):

```python
def apply_angle_journey_slots(slot_definitions, *, angle_id, runtime_format, ...):
    ...
    for ch_idx, base_row in enumerate(slot_definitions):
        row = [str(s).strip().upper() for s in base_row]
        ch_num = ch_idx + 1
        if ch_idx == 0:
            if ANGLE_DEFINITION_SLOT not in row:
                ins = 1 if row and row[0] == "HOOK" else 0
                row.insert(ins, ANGLE_DEFINITION_SLOT)   # ← shifts STORY from list-index 1 to 2
        else:
            ...
            if ANGLE_CALLBACK_SLOT not in row:
                if "HOOK" in row:
                    ins = row.index("HOOK") + 1
                else:
                    ins = min(1, len(row))
                row.insert(ins, ANGLE_CALLBACK_SLOT)     # ← shifts STORY from list-index 1 to 2
        out.append(row)
    return out, layer_by_ch, warnings
```

And `patch_beatmap_angle_journey` (lines 186-231) preserves existing slots' `somatic_section_index` (line 209-212: `existing = by_type.get(st); if existing is not None: new_slots.append(existing); continue`) but the LIST position shifts. Only NEW (angle) slots get the running `sec_idx` counter, so existing STORY slots still report `somatic_section_index ∈ {2, 5, 9}` even though their list-index moved.

**Why this regressed PR #669 silently:**
- `apply_angle_journey_slots` was designed assuming downstream code reads `slot.somatic_section_index`, but `enrichment_select.py:1707` uses `slot_i + 1` (the raw list index).
- No test in PR #1248 ran a `story_schedule × angle_id` book end-to-end with named-character verification. The OPD-116/117 changes were validated against angle slot rendering, not against the story_schedule consumption path.
- The PR #1248 description explicitly says "v1 books unchanged unless --chapter-architecture-version 2" — but this is misleading. The `patch_beatmap_angle_journey` path is triggered by `angle_id` being set in the BookSpec, NOT by the chapter-architecture-version flag.

---

## §4 Recommended fix (3 sentences)

Replace `_sec_idx = slot_i + 1` at `phoenix_v4/planning/enrichment_select.py:1707` with `_sec_idx = slot.somatic_section_index or (slot_i + 1)`, so the routing keys off the canonical somatic section index (which `patch_beatmap_angle_journey` correctly preserves for existing slots and assigns to new angle slots). This restores PR #669's story_schedule consumption for any book with `angle_id` set, while remaining backward-compatible for books without angle_id (where `somatic_section_index = slot_i + 1` already). Estimated LOC: 1 line changed; downstream `_sec_idx` references (line 1996 — `resolve_injections` and line 3019 — depth pass) should be audited but appear independent because they use `_sec_idx` for audit reporting, not for SCENE_SECTION_INDICES membership tests.

---

## §5 Tests to add

Test file: `tests/unit/planning/test_story_schedule_routing_opd142.py`

### Test 1 — story_schedule consumed when angle_id is set (deep_book_6h, hard mode)
```python
def test_story_schedule_consumed_with_angle_id_deep_book_6h():
    """
    Regression guard for OPD-142.
    Renders a deep_book_6h book with angle_id=ENGINE and asserts:
    - story_schedule has 12 chapters × 3 sections = 36 entries.
    - Every STORY slot in every chapter (slot_index 2/5/9 after angle injection) has
      audit source == "story_plan" (NOT "persona_atom").
    - All three STORY slots in chapter 1 share the same primary character name.
    - Arc-position order is RECOGNITION → MECHANISM_PROOF → TURNING_POINT across slot 2/5/9.
    """
```

### Test 2 — same-character × 3 beats per chapter (named-character continuity)
```python
def test_same_character_three_beats_per_chapter_with_angle():
    """
    For gen_z_professionals × anxiety × deep_book_6h × angle_id=ENGINE:
    - Iterate book.txt by chapter.
    - For each chapter, extract STORY slot content.
    - Assert a single recurring proper-noun character spans all three STORY slots.
    - Reject the regression pattern: three DIFFERENT characters across slot 2/5/9.
    """
```

### Test 3 — story_schedule arc-position alignment with slot
```python
def test_story_schedule_arc_position_matches_section_index():
    """
    For each (chapter, section) in story_schedule.assignments:
    - section_index ∈ {2, 5, 9}.
    - section_index == 2 → arc_position == "recognition".
    - section_index == 5 → arc_position == "mechanism_proof".
    - section_index == 9 → arc_position ∈ {"turning_point", "embodiment"}  # final chapter of phase
    """
```

### Test 4 — somatic_section_index preserved through angle injection
```python
def test_somatic_section_index_preserved_after_patch_beatmap_angle_journey():
    """
    Build a 10-slot beatmap, run patch_beatmap_angle_journey with angle_id=ENGINE.
    Assert the post-patch chapter:
    - Has 11 slots in chapter 1 (10 + ANGLE_DEFINITION) and chapter 2 (10 + ANGLE_CALLBACK).
    - STORY slots retain somatic_section_index ∈ {2, 5, 9}.
    - HOOK retains somatic_section_index == 1, INTEGRATION retains somatic_section_index == 10.
    - The new angle slot has somatic_section_index based on its list-index (currently 2 for both
      ANGLE_DEFINITION and ANGLE_CALLBACK because both are inserted at list-position 1).
    """
```

### Test 5 — broken-tiny atom guard at STORY slot (orthogonal to OPD-142, but exposed by it)
```python
def test_story_atom_minimum_word_count():
    """
    Defense in depth: assert no STORY slot in a rendered book is < 50 words.
    The current broken render has RECOGNITION v07 at 7 words; the root cause is
    OPD-142 (story_schedule bypassed → persona_atoms["STORY"] fallthrough → unfiltered tiny atom).
    With OPD-142 fixed, this test should also pass; if it fails after the fix,
    the broken-tiny atom is a separate atom-pool quality issue and should be opened
    as a follow-up OPD.
    """
```

---

## Appendix A — interaction with other recent OPDs

The recommended fix is a **one-line change to `_sec_idx` initialization**. None of these OPDs touch that line; all should be regression-free under the fix:

| OPD | PR | Touches enrichment_select.py? | Interaction with fix |
|-----|----|---------------------------------|---------------------|
| OPD-107 | #1211 | Yes (EXERCISE branch line 1773+) | Independent. EXERCISE branch runs after the STORY guard; unaffected. |
| OPD-107 follow-up | #1213 | Yes (residue filter `_is_practice_atom`) | Independent. Filter runs on EXERCISE pool only. |
| OPD-109 Phase 1 | #1212 | Yes (within-slot bridges) | Independent. Runs in chapter_composer, not in `_sec_idx` path. |
| OPD-109 Phase 3 | #1233 | Yes (PersonaPoolRotationState) | Independent. Rotation state is consulted in the persona waterfall AFTER the story_schedule guard; with OPD-142 fixed, STORY slots short-circuit to story_plan before rotation state is touched. |
| OPD-118 | #1244 | Yes (persona isolation) | Independent. PersonaPoolEmptyError signal is orthogonal to STORY routing. |
| OPD-116/117 | #1248 | Yes (`_try_angle_definition`, `_try_angle_callback`) | **This IS the regression source.** The fix preserves angle_journey functionality unchanged — angle slots still render via the dedicated branch at line 1675-1699. |
| OPD-115 Phase B | (in #1248) | Yes (`_COMPOSITE_*_SLOT_TYPES`, `_try_composite_content`) | Independent. Composite doctrine runs on DOCTRINE/REFLECTION/COMPRESSION slot types, not STORY. |
| OPD-129/113/134 | #1275 | Yes (story_planner enhancements) | Synergistic. PR #1275 added hard-mode same-character continuity to `build_story_schedule` — that work only pays off if the schedule is consumed (OPD-142 fixed). |

**Conclusion:** the one-line fix at line 1707 is isolated; no downstream OPD work is at risk.

---

## Appendix B — Bisection summary

Commits touching `phoenix_v4/planning/enrichment_select.py` between `cbfbe14c3..origin/main`:

```
da2374e26  feat(architecture): Holistic v2 Phase B (#1275)
639f273fb  feat(angle): OPD-116/117 Phase B (#1248)               ← REGRESSION COMMIT
a333eb6b8  fix(planning): OPD-118 (#1244)
8a20978d4  fix(selector,dedup): OPD-109 Phase 3 (#1233)
0b9285862  fix(planning): residue filter (#1213)
3feeff09c  fix(spine): OPD-107 (#1211)
07b816988  OPD-109 Phase 1 (#1212)
3822c4c21  fix(spine): per-section ARC selection (#1144)
c359300a0  fix(spine): EXERCISE slot-type contract (#1165)
d33e8c110  fix(pipeline): locale CANONICAL.txt (#1086)
635e1a96b  fix(spine-pipeline): Sprint 1 (#939)
f052d38d5  qa(bestseller): compact-format smoke (#858)
ef4f6c2f2  feat(spec-739 Phase 3): strict variant-coverage (#768)
a21c677a4  feat(enrichment): emit story_schedule as audit key (#716)
```

`_sec_idx = slot_i + 1` and the `if stype in ("SCENE", "STORY") and _sec_idx in SCENE_SECTION_INDICES:` guard are IDENTICAL between PR #669 (cbfbe14c3) and HEAD (da2374e26). The break is structural: PR #1248 changed the slot LIST structure in a way that invalidated the `slot_i + 1` assumption baked into PR #669.

The bisect lands on `639f273fb` (PR #1248). Before this commit, no slot insertion existed; the 10-slot grid was canonical and `slot_i + 1 == slot.somatic_section_index` always held.

---

## Constraints satisfied

- READ-ONLY forensic analysis. No production code changed in this PR.
- No paid-LLM callers introduced.
- Investigation completed within 60-minute cap.
- Branch: `agent/opd-142-forensic-story-schedule-regression`.
- Title: `diag(forensic): OPD-142 — find story_schedule routing regression between PR #669 and HEAD`.
