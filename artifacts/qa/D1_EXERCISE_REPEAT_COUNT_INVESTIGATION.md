# D1 — EXERCISE `repeat_count` / `lean` Investigation + Concrete Sample (read-only)

**Investigator:** Pearl_Dev (read-only; no renderer/config/atom edits — this artifact is the only change)
**Date:** 2026-05-29
**Source defect:** `artifacts/qa/PEARL_PRIME_CH1_CONSTRUCTION_AUDIT.md` §D1/§D5
**Method:** Read the full call graph (book_renderer → chapter_composer → component_assembler →
models + assembly_components.yaml; spine path golden_chapter_synthesis; run_pipeline dispatch;
chapter_purpose_contracts; reference plan). Ran the real assembler read-only against the real
`gen_z_professionals × anxiety` EXERCISE atom in a throwaway `/tmp` script (no repo output committed).

> **Bottom line up front.** D1 is real but the merged audit has **two material errors** that change
> the decision:
> 1. **Lean = first _3_ sentences, not 2.** `description.lean` is precomputed with
>    `max_sentences=3` (`component_assembler.py:385`); `_get_text` LEAN returns that precomputed
>    value, so it never falls through to the 2-sentence default. Verified by running the code.
> 2. **The truncation only fires on the LEGACY (`--pipeline-mode registry`) render path.** The
>    **spine path — the canonical Pearl Prime route (`--pipeline-mode spine`)** — calls
>    `compose_chapter_prose` **without** `exercise_repeat_index`/`exercise_context`
>    (`golden_chapter_synthesis.py:1157`, `chapter_composer.py:2975`), so `repeat_count` is
>    **always 0** there and `quick_repeat` can **never** match. Root cause confirmed otherwise:
>    where it DOES fire, `repeat_count` is **truly book-global** (counts any prior EXERCISE chapter,
>    not the same technique).

---

## Q1 — Full `repeat_count` chain (init → increment → read)

`repeat_count` is an `int` field on `AssemblyContext` — **no technique/family/slot key**:

```
phoenix_v4/exercises/models.py:38-49
@dataclass
class AssemblyContext:
    first_encounter: bool = True
    repeat_count: int = 0          # ← plain counter, not keyed by technique
    is_session_close: bool = False
    ...
```

**Producer (the only real source) — book_renderer.py (LEGACY path):**

```
phoenix_v4/rendering/book_renderer.py:1495-1502
def _exercise_repeat_before_idx(chapter_sequences, before_ch) -> int:
    """How many prior chapters (0 .. before_ch-1) include an EXERCISE slot."""
    n = 0
    for i in range(max(before_ch, 0)):
        row = chapter_sequences[i] if i < len(chapter_sequences) else []
        if any(str(s).strip().upper() == "EXERCISE" for s in row):
            n += 1
    return n
```

Called at **two** legacy render sites, both passing the book-global count:
- `book_renderer.py:1320` (`render_book(...)` chapter loop)
- `book_renderer.py:1825` (`TxtWriter.write()` chapter loop)
  → `compose_chapter_prose(..., exercise_repeat_index=_exercise_repeat_before_idx(chapter_slot_sequence, ch))`

**Threaded into the context:**

```
phoenix_v4/rendering/chapter_composer.py:2387-2395   (inside compose_chapter_prose)
eff_context = exercise_context or _build_assembly_context(
    chapter_index=chapter_index, total_chapters=total_chapters, ...
    exercise_repeat_index=exercise_repeat_index + ex_idx,   # +ex_idx only for 2nd+ exercise in same chapter
)

phoenix_v4/rendering/chapter_composer.py:2103-2121   (_build_assembly_context)
return AssemblyContext(
    first_encounter=chapter_index == 0,        # ← NOTE: ch0-only, NOT per-technique
    repeat_count=exercise_repeat_index,        # ← the book-global count lands here
    is_session_close=chapter_index >= max(total_chapters - 1, 0),
    ...
)
```

**Reader (decision):**

```
phoenix_v4/exercises/component_assembler.py:226-228   (_match_rule)
elif key == "repeat_count_gte":
    if ctx.repeat_count < value:
        return False
```

**Verdict on the audit's "book-global" claim: CONFIRMED** (citation corrected — it lives in
`book_renderer.py:1495-1502`, **not** `chapter_composer.py:1495`). The counter increments once per
prior chapter that has *any* EXERCISE slot; it is **not** keyed by technique id, exercise family, or
slot. Two completely different practices in chapters 3 and 4 are both counted as "repeats." `first_encounter`
is likewise chapter-0-only, so from chapter 1 on, the system already assumes "not first time" regardless
of whether the specific technique is new.

**Critical scope caveat (NEW — corrects the audit's blast radius):** the **spine** path never supplies
`exercise_repeat_index`. `compose_golden_spine_chapter` → `compose_chapter_prose` at
`golden_chapter_synthesis.py:1157` passes no `exercise_repeat_index` and no `exercise_context`; its
caller `compose_from_enriched_book` (`chapter_composer.py:2975`) likewise. So on the spine path the
default `exercise_repeat_index=0` (`chapter_composer.py:2218`) → `repeat_count=0` every chapter →
`quick_repeat` cannot match. Dispatch is gated strictly: `run_pipeline.py:2388` runs spine only when
`pipeline_mode == "spine"` (default is `"registry"` → legacy → `render_book` at `run_pipeline.py:3524`).

---

## Q2 — The lean rule + exactly what `lean` does

**`config/practice/assembly_components.yaml:20-30` (`quick_repeat`, first rule = highest priority):**

```yaml
  - name: quick_repeat
    description: "Exercise done 2+ times already in this session — minimal wrapper"
    match:
      repeat_count_gte: 2          # line 23
    components:
      bridge: skip
      introduction: skip   # OPD-113
      intro: skip
      description: lean            # line 28  ← the truncation switch
      aha: skip
      integration: skip
```

When this fires, **every wrapper is skipped** and only the leaned atom remains.

**The truncation code — `component_assembler.py:188-197`:**

```python
def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

def _derive_lean(full_text: str, max_sentences: int = 2) -> str:
    """Derive lean variant: first N sentences of full text."""
    sents = _sentences(full_text)
    if not sents:
        return full_text
    return " ".join(sents[:max_sentences])
```

**But the description component is precomputed at N=3, and that precomputed value wins:**

```python
# component_assembler.py:383-386   (resolve_exercise_components)
description = ComponentVariants(
    full=description_text,
    lean=_derive_lean(description_text, max_sentences=3) if description_text else "",   # ← N=3
)

# component_assembler.py:472-481   (_get_text)
if mode == ComponentMode.LEAN:
    return variants.lean or _derive_lean(variants.full)   # variants.lean is the N=3 string → used
```

**So `lean` = the first _3_ sentences of the atom**, naive `[.!?]`-split, **plain truncation**. It
does **not** select steps, preserve timing, or keep body cues — it just keeps sentences 1-3 in source
order and discards the rest. For a sequential breathing practice, sentences 1-3 are pure setup
("sit back / feet flat / feel heels"); the entire breathing pattern, the cycle count, the
"don't rush / keep counts even" pacing cues, the shoulder-drop body cue, and the return cue are gone.
**The audit's "first 2 sentences" is incorrect — verified by execution it is 3.**

---

## Q3 — Affected matrix (exact chapters per runtime)

**Threshold:** `repeat_count_gte: 2` (`assembly_components.yaml:23`). Because `_exercise_repeat_before_idx`
counts prior EXERCISE chapters, on the legacy path the **first two** exercise-bearing chapters render
FULL and the **third onward** lean (only if `quick_repeat` is the first matching rule — and it always
is once `repeat_count>=2`, since `quick_repeat` precedes `session_close`/`familiar_new_context` in
file order, so even the final session-close chapter leans).

Chapter counts (`config/format_selection/format_registry.yaml:96-137`):
micro_book_15=5, micro_book_20=6, short_book_30=8, **standard_book=10** (canonical default),
extended_book_2h=14, deep_book_4h=16, **deep_book_6h=20**. Reference plans:
`anxiety_gen_z_professionals_1h.yaml:8` `chapter_count: 6`; `..._6h.yaml:8` `chapter_count: 12`.

### Path A — LEGACY (`--pipeline-mode registry`, the default) — D1 FIRES HERE
On the reference plans every chapter carries an EXERCISE slot via the shared `*slots` anchor
(`..._6h.yaml:54-63`, slot_index 5 = EXERCISE). So EXERCISE-bearing chapters = ALL chapters, and
lean hits chapter indices **2 .. (N-1)**:

| Runtime (legacy, EXERCISE in every ch) | Total ch | Exercise-bearing ch | FULL (idx) | LEAN (idx) | # LEAN |
|---|---|---|---|---|---|
| micro_book_15 | 5 | 0-4 (5) | 0,1 | 2,3,4 | **3** |
| 1h ref plan | 6 | 0-5 (6) | 0,1 | 2,3,4,5 | **4** |
| standard_book | 10 | 0-9 (10) | 0,1 | 2-9 | **8** |
| 6h ref plan | 12 | 0-11 (12) | 0,1 | 2-11 | **10** |
| deep_book_6h | 20 | 0-19 (20) | 0,1 | 2-19 | **18** |

(Even the 15-min book leans 3 of 5 chapters on the legacy path — contradicting the audit's "15-min
usually never triggers." That audit claim is only true if the 15-min book is rendered via the spine
path or its short arc drops EXERCISE from chapters, which the reference-plan legacy render does not.)

### Path B — SPINE (`--pipeline-mode spine`, the canonical Pearl Prime route) — D1 CANNOT FIRE
`repeat_count` is always 0 (Q1), so **0 chapters lean** regardless of runtime. For completeness, the
exercise-bearing chapters here come from `chapter_purpose_contracts.yaml` (`max_exercises>=1` AND
EXERCISE in `allowed_slot_types`), e.g. **standard_book arc**: ch0 and ch11 have `max_exercises:0`
(recognition / forward-path), ch1-10 bear exercises (ch4, ch8 cap 2). All render FULL.

| Runtime (spine) | Total ch | Exercise-bearing ch (contract) | FULL | LEAN |
|---|---|---|---|---|
| standard_book (10) | 10 | ch1-9 (ch0 = 0) | all | **0** |
| deep_book_6h (20) | 20 | ch1-20 minus ch0/ch21+ (`max_ex:0`) | all | **0** |

**The decisive question for the operator: which path does the ~925 en_US batch actually run?**
The Pearl Prime catalog SSOT declares the canonical route as **spine**
(`scripts/catalog/generate_pearl_prime_book_script_catalog.py:24,87` and
`scripts/catalog/validate_pearl_prime_catalogs.py:45`:
`pipeline_route = "scripts/run_pipeline.py --pipeline-mode spine"`, `DEFAULT_RUNTIME_FORMAT="standard_book"`).
But the QA batch runner `scripts/run_max_quality_catalog.py:149-166` invokes `run_pipeline.py` with
`--render-book` and **no `--pipeline-mode`**, i.e. it runs the **legacy** path where D1 DOES fire.
**AMBIGUOUS which driver ships the 925 — if it is spine, D1 is dormant; if it is the max-quality/QA
runner or any registry-mode driver, D1 hits the Path-A matrix above.** This must be resolved before
sizing the fix.

---

## Q4 — CONCRETE SAMPLE (real atom, real assembler output)

**Config:** `gen_z_professionals × anxiety`, EXERCISE atom **v01** (box-breathing), file
`atoms/gen_z_professionals/anxiety/EXERCISE/CANONICAL.txt:7`. Outputs below were produced by running
the real `assemble_exercise_for_chapter` / `_get_text` against this atom (read-only, `/tmp`).

### (a) FULL authored atom (what chapter 0 / first two exercise chapters ship) — **13 sentences**
```
Sit back from your screen. Place both feet flat on the floor. Feel your heels make contact.
Breathe in for four counts. Hold for four counts. Breathe out for four counts. Hold for four counts.
That is one cycle. Do not rush the holds. Keep the counts even. Complete four cycles. On the fourth
exhale, let your shoulders drop before you breathe in again. Return to the screen after the fourth cycle.
```
Full experience = **setup** (sentences 1-3), **the box-breathing pattern** (4-7: in-4/hold-4/out-4/hold-4),
**cycle definition + count** (8, 11), **pacing cues** (9-10: don't rush, keep counts even),
**body cue** (12: shoulders drop on the 4th exhale), **integration/exit** (13: return to screen).
Assembled with all 5 wrapper parts (bridge + "Now we're going to do a breath practice" +
description-of-practice + atom + aha + integration), the full chapter-0 exercise block runs **38 sentences**.

### (b) LEAN form actually emitted in an affected chapter (legacy ch2+) — **3 sentences**
Real assembler output (`quick_repeat` selection: bridge=skip, introduction=skip, intro=skip,
description=lean, aha=skip, integration=skip). The **entire** exercise block the reader receives is:
```
Sit back from your screen. Place both feet flat on the floor. Feel your heels make contact.
```

### Side-by-side
| | FULL (ch0 / 1st-2nd ex chapter) | LEAN (legacy ch2+, quick_repeat) |
|---|---|---|
| atom guidance sentences | 13 | **3** |
| assembled block (with wrappers) | 38 | **3** (all wrappers skipped) |
| breathing pattern present? | yes (in-4/hold-4/out-4/hold-4) | **no** |
| cycle count / pacing cues? | yes | **no** |
| body cue (shoulders drop)? | yes | **no** |
| aha + integration? | yes | **no** |
| net for reader | a complete, doable practice | three setup sentences, **no actual exercise** |

The reader is told to sit back, plant their feet, and feel their heels — then the practice simply
stops. ~10 of 13 instructions and 100% of the breathing mechanics are dropped.

---

## Q5 — Blast radius

Two scenarios; arithmetic shown. (`~800` high-confidence configs per
`artifacts/research/full_content_audit.md:65`; operator's working en_US slice ≈ **925** books;
4-locale plan ≈ 925 × 4 ≈ **3,700** books.)

**If the batch runs SPINE (canonical route):** leaned (book,chapter) exercise instances = **0**.
D1 is entirely dormant; the operator's "fragment" intuition would have to come from a different
defect (e.g. D2/D3) or from QA renders done via the legacy runner.

**If the batch runs LEGACY / registry (e.g. via `run_max_quality_catalog.py`) at `standard_book` (10ch):**
- per book: 10 exercise-bearing chapters, FULL = 2, **LEAN = 8**.
- en_US 925 books × 8 = **~7,400 leaned exercise instances** (vs ~1,850 full).
- 4-locale ≈ 3,700 books × 8 = **~29,600 leaned instances**.
- at `deep_book_6h` (20ch) it would be 18/book → 925 × 18 ≈ **16,650** (en_US) — but the canonical
  default runtime is `standard_book`, so the 8/book figure is the realistic legacy estimate.

So the blast radius is **binary on the pipeline-mode choice**: 0, or ~7.4k (en_US) / ~29.6k (4-locale)
leaned exercises. **Resolving which driver ships the 925 is the single highest-leverage fact** and
should precede any code change.

---

## Q6 — Fix options (recommend; NOT implemented)

**Why `lean` exists at all:** the rule's own description (`assembly_components.yaml:21`) is
"Exercise done 2+ times already in this session — minimal wrapper" — an **intentional
anti-repetition** device. Its design assumption is that by the 3rd time the reader meets *the same
technique* they don't need the full walk-through again. The bug is purely in the **trigger**:
`_build_assembly_context` feeds it a count of prior exercise *chapters* (`book_renderer.py:1495`),
not prior occurrences of *the same technique*, so distinct practices get falsely leaned. The intent
is sound; the keying is wrong.

**Test/gate coverage today:** `tests/test_exercise_component_assembler.py:40` asserts only that
`quick_repeat` *fires* on `repeat_count=3`; `:100` tests `_derive_lean` in isolation with N=2. **No
test asserts the assembled output retains exercise steps/timing/body cues**, and there is **no
exercise-length/step-count quality gate** under `phoenix_v4/quality/` (checked: book_quality_gate,
bestseller_craft_gate, chapter_flow_gate, register_gate, memorable_line_gate). Consequence: any of
the fixes below would pass existing tests unchanged — but so does the current bug, i.e. **regressions
are not caught either way**; add a targeted test alongside whichever fix.

### Option A — make `repeat_count` per-technique (key by exercise/technique id)
- **Change:** replace the book-global counter with a per-technique tally.
  - `phoenix_v4/rendering/book_renderer.py:1495-1502` — rewrite `_exercise_repeat_before_idx` to count
    prior chapters whose EXERCISE resolved to the *same technique id* (needs the per-chapter exercise
    atom/technique id, available as `ex_aid`/`exercise_aid` at `:1304`/`:1810`). Likely signature
    change to take the resolved exercise-id sequence, threaded at `:1320` and `:1825`.
  - Optionally tighten `first_encounter` (`chapter_composer.py:2113`) to "first time *this technique*
    appears" rather than chapter-0-only, for consistency.
- **Risk:** MEDIUM — touches the legacy render hot loop and a signature; must ensure technique ids are
  populated for both legacy call sites and the library/fallback exercises (where id may be empty →
  treat empty as "always first encounter" = full).
- **Tests/gates:** none would break; add a unit test (two different techniques in ch3/ch4 → both FULL;
  same technique repeated → 2nd+ leans).

### Option B — disable lean entirely (always full exercises)
- **Change:** one line — `config/practice/assembly_components.yaml:28` `description: lean` →
  `description: full` (and optionally restore `bridge/intro/aha/integration` from `skip` if full
  wrappers are wanted on repeats; minimum is just the description line).
- **Risk:** LOW (config-only, fully reversible). Downside: re-introduces verbatim repetition of an
  identical technique on books that legitimately reuse one practice many times — the exact thing the
  rule was added to prevent. Word counts rise on legacy long books.
- **Tests/gates:** `test_quick_repeat_fires` still passes (it asserts rule name, not description mode).
  No gate enforces non-repetition of exercise prose, so nothing else breaks.

### Option C — raise the threshold / cap lean frequency
- **Change:** `assembly_components.yaml:23` `repeat_count_gte: 2` → `4` (or higher). Optionally cap
  consecutive leans.
- **Risk:** LOW (config-only) but **does not fix the root cause** — distinct techniques are still
  falsely counted; it only delays onset (e.g. on standard_book legacy, lean would start at ch4 instead
  of ch2 → 6 leaned chapters instead of 8). Palliative.
- **Tests/gates:** `test_quick_repeat_fires` uses `repeat_count=3`, which would **no longer match**
  `quick_repeat` at threshold 4 — that test would need updating. Minor but real test churn.

### Recommendation
**Resolve the pipeline-mode question first (Q3/Q5).** If the 925 ships via **spine**, D1 is dormant
and the correct action is a low-cost guard + test, not a render change: either Option B (config-only,
makes legacy QA renders match spine behavior) **plus** a regression test, since lean is a legacy-only
artifact with no upside on the canonical route.

If any registry/legacy driver ships books, **Option A** is the right structural fix (it preserves the
rule's legitimate anti-repetition intent while eliminating the false-positive truncation), gated by a
new unit test asserting distinct techniques stay FULL. **Lead with Option A** on the legacy path;
keep Option C only as a stopgap if Option A cannot land before the batch.

Primary file:line targets for the recommended fix:
`phoenix_v4/rendering/book_renderer.py:1495-1502` (per-technique keying) + call sites `:1320`/`:1825`;
or, for the config-only stopgap, `config/practice/assembly_components.yaml:28` (and `:23`).

---
*Read-only investigation. No renderer/atom/config files were modified. This artifact is the only
change. The throwaway sample script ran under `/tmp` and is not committed.*
