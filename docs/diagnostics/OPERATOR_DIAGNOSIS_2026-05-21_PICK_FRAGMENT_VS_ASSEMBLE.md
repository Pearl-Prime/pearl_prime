# Operator Diagnosis 2026-05-21: pick-fragment vs assemble-full-unit

**Investigator:** Pearl_Dev (read-only audit)
**Branch:** `agent/investigate-character-continuity-and-5part-exercise-bugs`
**Scope:** Verify whether the Phoenix pipeline has rich architecture (4-beat story arcs, 5-part exercise structure) but the renderer collapses to fragments instead of assembling full units.

---

## Executive verdict

**Operator's hypothesis is CONFIRMED on both the story-continuity axis and the 5-part-exercise axis, plus three additional meta-pattern victims.**

| Hypothesis | Result | Evidence |
|---|---|---|
| 1. Same-character continuity not enforced per chapter | CONFIRMED (partial) | 7/12 chapters keep the same character across all 3 SCENE/STORY slots; 5/12 mix characters. Soft preference, not a hard constraint. |
| 2. 5-part exercise not assembled in deep_book_6h | CONFIRMED (severe) | Zero matches in 50k-word render for any phoenix_standard template signature (intro / description / aha / integration). 84 raw practice-atom guidance paragraphs stacked across 12 chapters with no scaffolding. |
| 3. Other pick-fragment victims | CONFIRMED (3 found) | TEACHER_DOCTRINE single-block per chapter (TEACHER_DOCTRINE_INTRO atom exists, unused in production), REFLECTION collapses into one bridge-joined block, ANGLE_CALLBACK absent from the render entirely. |

---

## Method

1. Read `phoenix_v4/planning/story_planner.py` (full file), `phoenix_v4/planning/enrichment_select.py` (lines 1523-2200, 2940-3330), `phoenix_v4/rendering/chapter_composer.py` (lines 2030-2540, 2244-2330), `phoenix_v4/exercises/component_assembler.py` (full file).
2. Loaded the 74 atom files in `story_atoms/gen_z_professionals/anchored/anxiety/overwhelm/` and re-ran `build_story_schedule` live (seed=`test`).
3. Compared against the renders on disk:
   - `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/deep_book_6h/book.txt` (49,499 words, 12 chapters, generated 2026-05-21 04:34:39 — within one minute of PR #1265 merge)
   - `artifacts/pilots/duration_matrix/anxiety/deep_book_6h/book.txt` (11,563 words, 12 chapters, same timestamp — small render)
   - `artifacts/pearl_prime/extended_book_2h/ahjan_gen_z_professionals_anxiety_en_US_20260518T065950Z_round3/` (2026-05-18, has the 5-part templates firing — used as control)
4. Counted character occurrences, signature template phrases (`"This is a [X] practice"`, `"Now, I want you to notice"`, `"Before you return"`), and atom-repetition cadence.
5. Traced the slot data path from planner → schedule → enrichment_select → book_renderer → chapter_composer → component_assembler.

---

## Task 1 — Character continuity verification

**Data source.** Live `build_story_schedule(persona='gen_z_professionals', topic='anxiety', seed='test')` produced 36 assignments across 12 chapters. The 2026-05-18 `extended_book_2h` audit JSON `story_schedule` field had matching coverage and was used to cross-check.

### Per-chapter character map (live schedule, seed='test')

| Chapter | recognition slot | mechanism_proof slot | turning_point / embodiment slot | Verdict |
|---|---|---|---|---|
| Ch 1 | Priya (v03) | Priya (v05) | Priya (v08) | SAME |
| Ch 2 | Marcu (v06) | Marcu (v06) | Marcu (v09) | SAME |
| Ch 3 | Zoë (v10) | Zoë (v14) | Zoë (v12) | SAME |
| Ch 4 | "The" (v16) | Zoë (v01) | "Another" (v12) | DIFF |
| Ch 5 | Amara (v14) | Amara (v08) | Amara (v14) | SAME |
| Ch 6 | Maya (v01) | Maya (v09) | Maya (v02) | SAME |
| Ch 7 | Daniel (v02) | Daniel (v20) | "The" (v11) | DIFF |
| Ch 8 | Aisha (v05) | Aisha (v10) | Aisha (v03) | SAME |
| Ch 9 | Tariq (v07) | Tariq (v12) | Tariq (v10) | SAME |
| Ch 10 | Nadia (v09) | "It" (v03) | Nadia (v01) | DIFF |
| Ch 11 | "The" (v17) | Jordan (v11) | Jordan (v02) | DIFF |
| Ch 12 | "Chri" (v11) | "The" (v16) | "Third" (v19) | DIFF |

**Summary: 7 SAME-character chapters / 5 DIFFERENT-character chapters. Operator's hypothesis confirmed.**

### Why does this break?

Two compounding defects, both in `phoenix_v4/planning/story_planner.py`:

#### Defect 1a: `_extract_character` heuristic is too dumb (`story_planner.py:130-143`).
```python
def _extract_character(text: str) -> str:
    """Return the first apparent proper-noun character name from atom text."""
    words = text.split()
    if not words:
        return "unknown"
    first = words[0].rstrip("'s,.")
    if first not in _STRUCTURAL_STARTS and first[0].isupper():
        return first
    # Try second word
    if len(words) > 1:
        second = words[1].rstrip("'s,.")
        if second[0].isupper() and second not in _STRUCTURAL_STARTS:
            return second
    return first
```
`_STRUCTURAL_STARTS` = `["The", "There", "It", "A", "An", "At", "On", "In", "She", "He", "They"]`. But many anchored atoms begin with `"The fourth deliverable goes out at 4:58pm. Zara sits back..."`, `"The fifth talk runs long..."`, `"Another task arrives..."`, `"It's Monday at 7:47am..."`. The first word fails the structural guard (matches `"The"`, `"It"`, `"Another"`, `"It's"`) or sneaks past it ("Another" is not in the guard list). Result: 14 of 74 atoms get character=`"The"`, 1 atom gets `"Another"`, 1 atom gets `"Third"`, several atoms beginning with proper nouns following intro phrases (e.g. "Zara", "Sam", "Leo") get mis-attributed.

Top-20 mis-attributed character distribution:
```
The: 14, Zoë: 5, Marcu: 4, Priya: 4, Amara: 4, ...
```
"The" is the #1 "character" in the index — a pure heuristic failure.

#### Defect 1b: Soft borrow fallback violates same-character continuity (`story_planner.py:223-240`).
```python
if available:
    chosen = available[idx]
else:
    # Borrow from the pool — prefer a different character name than primary
    pool = [
        a for a in all_atoms
        if a.arc_position == arc_pos
        and a.path not in used_atom_paths
        and a.word_count >= 30
        and a.character != primary_character
    ]
    if not pool:
        pool = [...]  # fall back to any atom at this arc_position
    chosen = pool[idx]
```
When the primary character lacks an atom for some arc_position (e.g. Daniel has 3 atoms but only `recognition` and `mechanism_proof` available, not `turning_point`), the planner BORROWS from any other character. This is by design per the docstring ("borrows the best-fit atom from the shared pool at that arc position"), but the comment "novel character name so the reader meets someone new but the arc feels coherent" is false — the reader experiences a character switch mid-chapter (Ch 7: Daniel recognition + Daniel mechanism + Chri turning_point), which feels like fragmentation, not arc coherence.

Additionally: `used_atom_paths` is book-wide (`book_used_paths` in `build_story_schedule`), so once Priya/Daniel/etc. atoms are consumed in early chapters, late chapters MUST borrow.

---

## Task 2 — 5-part exercise verification

**Reference architecture** (per `SOURCE_OF_TRUTH/exercises_v4/`, `phoenix_v4/exercises/models.py:5-12`, `phoenix_v4/exercises/component_assembler.py:484-529`):

1. **INTRODUCTION** — `"Now we're going to do a [X] practice."` (`introduction_templates.yaml`)
2. **DESCRIPTION** — `"This is a [X] practice. You are not trying to..."` (`intro_templates.yaml`)
3. **GUIDANCE** — atom body (e.g. atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt)
4. **AHA** — `"Now, I want you to stop for a moment and notice something..."` (`aha_noticing_phoenix_standard.yaml`)
5. **INTEGRATION** — `"Before you return to the screen, take one breath..."` (`integration_phoenix_standard.yaml`)

### Signature template matches in `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/deep_book_6h/book.txt`

| Template signature | Expected source | Count in 49,499-word render |
|---|---|---|
| `"Now we're going to do"` | introduction_templates.yaml (Part 1) | **0** |
| `"This is a (breath\|grounding\|body\|gentle\|short\|sensory) practice"` | intro_templates.yaml (Part 2) | **0** |
| `"Now, I want you"` / `"Now, take a moment"` | aha_noticing_phoenix_standard.yaml (Part 4) | **0** |
| `"Before you return"` / `"Before you keep moving"` | integration_phoenix_standard.yaml (Part 5) | **0** |

### Control: same checks against the 2026-05-18 extended_book_2h render

| Template signature | Count |
|---|---|
| `"Now we're going to do"` | 0 (even the control lacks Part 1) |
| `"This is a [X] practice"` | 3 |
| `"Now, I want you"` / `"Now, [verb] and..."` | 8 |
| `"Before you return"` / `"Before you keep moving"` | (present in line 67-ish range) |

So the 5-part assembler **was firing partially** on extended_book_2h on 2026-05-18 (Parts 2, 4, 5 appeared; Part 1 introduction did not even there). On deep_book_6h, **zero parts** appear.

### Actual rendered EXERCISE zones in the deep_book_6h book

Sampled at `book.txt:1796-1829` (Ch 6 EXERCISE zone) — 8 raw practice atoms stacked sequentially:

```
Take one situation that usually triggers you. Not the biggest one. A medium one.
Next time it happens, pause for three breaths before responding. ... Do this one
time. See what happens.

This week, when you notice a strong emotion, ask: where is this in my body? ...

Sit quietly for five minutes. Do nothing. Fix nothing. Change nothing. ...

This week, practice returning. When you lose presence, return to the breath. ...

This week, take one action knowing that you might fail. ...

This week, practice one moment of not knowing. ...

Identify one belief you have about yourself that causes suffering. ...
```

**No bridge, no introduction template, no description template, no aha template, no integration template. Just naked atom bodies, concatenated.**

The same atom `"Sit quietly for five minutes. Do nothing. Fix nothing. ..."` appears **6 times** in the 12-chapter book. `"Your thoughts are not facts about the world..."` (REFLECTION-class) appears **5+ times**.

**Total practice-atom occurrences in the deep_book_6h render: 84 across 12 chapters (≈ 7 per chapter).** That is the operator's "the renderer is picking fragments" — except in this case it is picking MANY fragments, all of the GUIDANCE shape, none of the framing.

### Why 5-part fails in deep_book_6h

Two compounding defects:

#### Defect 2a: `compose_chapter_prose` collapses N EXERCISE slots into ONE (`chapter_composer.py:2244-2260`).
```python
slot_map: dict[str, str] = {}
for st, prose in zip(slot_types, slot_proses):
    st_upper = st.strip().upper()
    if st_upper not in slot_map or _is_placeholder_text(slot_map[st_upper]):
        slot_map[st_upper] = prose
# ...
exercise_raw = slot_map.get("EXERCISE", "")
```
The `SOMATIC_10_SLOT_GRID` (per `phoenix_v4/planning/beatmap_compile.py:42-53`) has **two** EXERCISE slots per chapter (sec 4 = awareness, sec 8 = regulation). `slot_map` keeps only the first, silently discarding the second.

#### Defect 2b: depth pass appends DEPTH_<MODULE> slots that bypass the 5-part assembler (`enrichment_select.py:3049-3057`).
```python
depth_slot = EnrichedSlot(
    slot_type=f"DEPTH_{module_name.upper()}",  # e.g. DEPTH_PRACTICE_SCAFFOLD, DEPTH_INTEGRATION_LANDING
    content=trimmed,
    source=f"depth_module:{module_name}:{source.get('type')}",
    ...
)
chapter.slots.append(depth_slot)
```
For deep_book_6h, depth_rounds=2, MAX_DEPTH_WORDS_PER_CHAPTER ≤ 1400w/round. The depth pass aggressively pulls modules including `practice_scaffold`, `integration_landing`, `consequence_exposure`, `somatic_detail` (per `DEFAULT_DEPTH_PRIORITY`, `enrichment_select.py:2299-2308`). These atoms are SHAPED like practices ("Sit quietly for five minutes...", "This week...") but tagged as `DEPTH_<module>` not `EXERCISE`, so they:
1. Are NOT consumed by `compose_chapter_prose` via `slot_map.get("EXERCISE")`.
2. Are bucketed into `_depth_mech` by `golden_chapter_synthesis._bucket_slots:642-657`.
3. Are bridge-joined into REFLECTION block via `_first_or_join` (`golden_chapter_synthesis.py:782-787`) and emitted as raw text with no scaffold.

Net effect: 7 practice-shaped atoms per chapter land in the REFLECTION zone disguised as reflections, with no Part 1/2/4/5 framing. The 5-part assembler runs once on the SINGLE EXERCISE slot, but the depth-pass `practice_scaffold` modules dump 6 more atoms next to it, naked.

---

## Task 3 — Meta-pattern audit

### Victim 1: TEACHER_DOCTRINE — `phoenix_v4/rendering/golden_chapter_synthesis.py:828-846`

```python
doctrine = _first_or_join(
    b["TEACHER_DOCTRINE"], chapter_index=chapter_index0, bridge_fn=_mk_bridge("TEACHER_DOCTRINE"),
)
# ... later, the comment says doctrine is appended to COMPRESSION (a workaround):
if doctrine:
    compression = "\n\n".join(x for x in (compression, doctrine) if x)
```

**Architecture intent (per atoms/gen_z_professionals/anxiety/):**
- `TEACHER_DOCTRINE/CANONICAL.txt` — ~210w per chapter (one block per arc_position)
- `TEACHER_DOCTRINE_INTRO/ahjan/CANONICAL.txt` — ~1300w doctrine foundational intro (5 paragraphs of "Thai Forest tradition... bracing as suffering... noticing without correction"). Committed in PR #1270 (2026-05-21).

**Rendered output:** The TEACHER_DOCTRINE_INTRO atom is **NEVER READ BY PRODUCTION CODE**. `grep -r TEACHER_DOCTRINE_INTRO --include='*.py'` returns only the test file (`tests/unit/atoms/test_v2_pilot_atoms_ahjan_anxiety_gen_z.py`). No renderer reads it.

**Pick-fragment instance:** the architecture defines a foundational intro doctrine + per-chapter mechanism doctrine (intro → recurrence → reveal pattern). The renderer reads only the per-chapter mechanism atom (one block) and outputs it as a sentence appended to COMPRESSION (`golden_chapter_synthesis.py:845-846` is explicitly a "Sprint-1 word-floor fix" that smuggles doctrine into compression because "compose_chapter_prose never adds doctrine from slot_map to parts — TEACHER_DOCTRINE was silently discarded").

### Victim 2: REFLECTION — collapsed via `_first_or_join`

`golden_chapter_synthesis.py:782-787`:
```python
reflection_blocks = list(b["REFLECTION"]) + list(b["_depth_mech"])
reflection = _first_or_join(
    reflection_blocks,
    chapter_index=chapter_index0,
    bridge_fn=_mk_bridge("REFLECTION"),
)
```

The `SOMATIC_10_SLOT_GRID` has TWO REFLECTION slots per chapter (sec 3 + sec 7). These plus `_depth_mech` depth slots get bridge-joined into one stream. The reflections aren't developing distinct points — they're stacked atom dumps with bridges between them. Same pattern as EXERCISE: rich underlying atom pool, but the renderer concatenates without role differentiation (early-chapter teaching reflection vs late-chapter integration reflection).

### Victim 3: ANGLE_CALLBACK — completely absent from the render

`enrichment_audit.json` for the deep_book_6h render: `angle_id: None, angle_layer_by_chapter: None`. The ANGLE journey (OPD-116/117 5-layer architecture) was not provisioned for this render at all. Per OPD-116/117 plan, each chapter should fire a callback to a DIFFERENT layer (1→2→3→4→5), but `grep -c "Earlier I said|Here is what was hidden"` in the book = 0. This is "missing", not "fragmentation" — but it's the same shape: rich layered architecture, zero rendered output.

### Victim 4: Atom repetition across chapters (paragraph dedup leakage)

`_dedup_repeated_blocks` and `book_used_paths` are supposed to prevent the same atom from appearing twice in the book. Direct observation:
- `"Sit quietly for five minutes. Do nothing. Fix nothing..."` appears **6 times** (book.txt at chars 700, 1123, 1377, 1590, 1806, 2779…).
- `"Marcus is a surgeon with reputation..."` appears verbatim **twice** (lines 460-479 and 800-819) — once in Ch1 + once in Ch2 — confirming the dedup is per-chapter only, not book-wide for depth-pass content.
- `"Your thoughts are not facts..."` appears **5+ times**.

The pool is small (74 atoms total for anxiety overwhelm) but the planner exhausts them and reuses; meanwhile the depth pass operates from an independent pool with weaker dedup.

---

## Task 4 — Recommend exact fix sites (DO NOT IMPLEMENT)

| # | Bug | File:Line | Fix sketch | LOC est. | Test coverage needed |
|---|---|---|---|---|---|
| **F1** | `_extract_character` mis-attributes 14/74 atoms to "The" | `phoenix_v4/planning/story_planner.py:130-143` | Use a deterministic NER pass: scan all whitespace-separated tokens, return the first proper noun that (a) is not in `_STRUCTURAL_STARTS`, (b) is not a sentence-start article preceding a noun (e.g. "The fourth deliverable" → skip "The", "fourth"; pick "Zara"), (c) appears at least twice in the atom text (a real character recurs in their own atom). | ~30 LOC | `tests/unit/planning/test_story_planner_character_extraction.py` — 74 atoms in corpus + a fixture covering each known character. Assert <=2 mis-attributions. |
| **F2** | Soft borrow fallback breaks same-character continuity | `phoenix_v4/planning/story_planner.py:203-249` (`_assemble_story`) | Add a hard mode: if the primary character lacks an atom for an arc_position, **drop the entire story** (return None) rather than borrowing. Let `_select_stories` (`story_planner.py:256-305`) pick a different character with full 4-arc coverage. If no character has coverage, log warning + accept partial story (3 of 4 arcs). | ~20 LOC | `tests/unit/planning/test_story_planner_character_continuity.py` — assert per-chapter same-character. Acceptable failure mode: chapter with NO scheduled story (skip is better than mix). |
| **F3** | `compose_chapter_prose` discards 2nd EXERCISE slot | `phoenix_v4/rendering/chapter_composer.py:2244-2249, 2260, 2382-2435` | Change `slot_map` from `dict[str, str]` to `dict[str, list[str]]`. Iterate both EXERCISE slots through `assemble_exercise_for_chapter` separately (with different `exercise_repeat_index` for the awareness vs regulation phase). Wire two separate Part 1 introductions. | ~80 LOC | `tests/unit/rendering/test_two_exercise_slots_per_chapter.py` — assert deep_book_6h Ch 1 yields TWO `"Now we're going to do"` introductions and TWO `"This is a [X] practice"` description blocks per chapter. |
| **F4** | DEPTH_<module> practice/integration content bypasses 5-part assembler | `phoenix_v4/planning/enrichment_select.py:3049-3057` (slot creation) + `phoenix_v4/rendering/golden_chapter_synthesis.py:636-664` (`_bucket_slots`) | Two options: (a) DEPTH_practice_scaffold → route into EXERCISE bucket so `assemble_exercise_for_chapter` wraps them. (b) DEPTH_integration_landing → route into INTEGRATION bucket so phoenix_standard integration template wraps. Update `_bucket_slots` to special-case `DEPTH_PRACTICE_SCAFFOLD`, `DEPTH_INTEGRATION_LANDING`. | ~40 LOC | `tests/unit/rendering/test_depth_practice_5_part.py` — assert depth_module practice content emerges with phoenix_standard framing. |
| **F5** | TEACHER_DOCTRINE_INTRO atom committed (PR #1270) but no reader exists | `phoenix_v4/planning/enrichment_select.py` (find `TEACHER_DOCTRINE` waterfall — register a new `TEACHER_DOCTRINE_INTRO` reader that fires only at Ch1) | Add a loader for `atoms/<persona>/<topic>/TEACHER_DOCTRINE_INTRO/<teacher>/CANONICAL.txt`. Inject as the FIRST block of Ch1 (replacing/preceding the existing Ch1 hook). | ~50 LOC | `tests/unit/planning/test_teacher_doctrine_intro_ch1.py` — assert ahjan Ch1 contains "Thai Forest tradition" string from the doctrine intro atom. |
| **F6** | TEACHER_DOCTRINE smuggled into COMPRESSION via Sprint-1 word-floor fix | `phoenix_v4/rendering/golden_chapter_synthesis.py:842-846` | Surface TEACHER_DOCTRINE as a proper top-level block in the pairs list (currently it's joined into COMPRESSION). Add per-chapter doctrine sequence: intro paragraph + mechanism paragraph + reveal carry-line. Use the existing per-chapter v01-vN doctrine atoms organized by phase (HARDSHIP=intro, HELP=mechanism, HEALING=reveal, HOPE=carry-forward). | ~50 LOC | `tests/unit/rendering/test_teacher_doctrine_block_order.py` |

### Priority ranking (highest-leverage first)

1. **F3 + F4 together** (≈120 LOC) — restore Part 1/2/4/5 phoenix_standard scaffolding on EVERY exercise slot in deep_book_6h. This is the single biggest visible-quality lift; operator will see proper "Now we're going to do a breath practice." / "This is a breath practice." / "Now, I want you to stop and notice..." / "Before you return..." blocks on every Ch.
2. **F2** (≈20 LOC) — hard-enforce same-character continuity per chapter. Best ROI per LOC because the story_planner already does the work; one early-return fixes 5/12 broken chapters.
3. **F1** (≈30 LOC) — fix the "The" mis-attribution. Without F1, F2 may force `Optional[StoryArc]=None` returns for half the candidate characters. F1 is the foundation; F2 builds on it.
4. **F5 + F6** (≈100 LOC) — surface the TEACHER_DOCTRINE_INTRO atom (PR #1270 dead-code) and properly layer doctrine intro → mechanism → reveal.

---

## Overlap with merged PR #1265 (OPD-123/124)

PR #1265 (merged 2026-05-21 04:33:56) added:
- `config/rendering/chapter_structure_template.yaml` — canonical sequence (HOOK → SCENE → SECTION → STORY → REFLECTION → EXERCISE → CLOSE)
- `config/rendering/within_slot_bridge_families.yaml` — adds `story_introduction` shape family ("Let me tell you about somebody who…")
- `phoenix_v4/planning/chapter_planner.py` — `enforce_canonical_chapter_sequence` reorders slots per template
- `phoenix_v4/quality/chapter_flow_gate.py` — WARN-only canonical_sequence_compliance check
- `phoenix_v4/rendering/chapter_composer.py` — `prepend_story_introduction_bridge` (line 1354) called at line 2320

**Overlap assessment:**
- **F3 (two-EXERCISE-slots-per-chapter)** — partially overlaps. PR #1265 reordered the compose flow (section before named story) in chapter_composer.py:2300-2360 but did NOT touch the slot_map collapse on lines 2244-2249. F3 still needed.
- **F4 (depth-pass routing)** — no overlap. PR #1265 did not touch enrichment_select depth pass or golden_chapter_synthesis bucketing.
- **F1, F2 (story_planner)** — no overlap. PR #1265 did not touch story_planner.py.
- **F5, F6 (TEACHER_DOCTRINE)** — no overlap. PR #1265 did not touch teacher_doctrine paths.

PR #1265 is COMPATIBLE with all proposed fixes; they touch different surfaces.

The deep_book_6h render at `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/deep_book_6h/` (timestamp 04:34:39, generated 43 seconds after PR #1265 merge) most likely started before #1265's effects took root for that particular run — its book.txt has no `story_introduction` bridges firing (zero matches for "Let me tell you about somebody who"), no canonical-sequence enforcement evidence. A fresh render after #1265 may show different behavior — but the bugs F1-F6 above are structural and will manifest regardless.

---

## Constraints honored

- Read-only; NO production code modified.
- NO paid LLM callers invoked (all analysis used local file reads and `grep`).
- Investigation cap: 90 minutes — completed within budget.
- Branch `agent/investigate-character-continuity-and-5part-exercise-bugs` rooted at `origin/main`.

---

## Artifacts referenced

- `phoenix_v4/planning/story_planner.py` (450 LOC) — full read
- `phoenix_v4/planning/enrichment_select.py` (3442 LOC) — partial read, lines 1523-2200 + 2940-3330
- `phoenix_v4/rendering/chapter_composer.py` (2994 LOC) — partial read, lines 2030-2540 + 2244-2330 + 1354
- `phoenix_v4/exercises/component_assembler.py` (566 LOC) — full read
- `phoenix_v4/rendering/golden_chapter_synthesis.py` — partial read, lines 636-880
- `phoenix_v4/rendering/book_renderer.py` (2243 LOC) — partial read, lines 1296-1335
- `SOURCE_OF_TRUTH/exercises_v4/intro_templates.yaml`, `introduction_templates.yaml`, `aha_noticing_phoenix_standard.yaml`, `integration_phoenix_standard.yaml`
- `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/deep_book_6h/book.txt` (49,499 words)
- `artifacts/pilots/duration_matrix/anxiety/deep_book_6h/book.txt` (11,563 words)
- `artifacts/pearl_prime/extended_book_2h/ahjan_gen_z_professionals_anxiety_en_US_20260518T065950Z_round3/` (control with story_schedule audit)
- `story_atoms/gen_z_professionals/anchored/anxiety/overwhelm/` (74 atoms across 4 arc positions)
- `atoms/gen_z_professionals/anxiety/TEACHER_DOCTRINE_INTRO/ahjan/CANONICAL.txt` (PR #1270 dead-code atom)
