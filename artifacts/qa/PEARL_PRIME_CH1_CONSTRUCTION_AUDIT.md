# Pearl Prime — Chapter-1 / Book Construction Audit (read-only)

**Auditor:** Pearl_Architect (read-only correctness audit; no renderer/atom/config edits)
**Date:** 2026-05-29
**Scope:** How Pearl Prime deterministically constructs a book / chapter 1 before we
batch-assemble ~925 en_US ebooks. Every verdict below is backed by source read in full
(book_renderer.py, prose_resolver.py, chapter_composer.py, golden_chapter_synthesis.py,
assembly_compiler.py, component_assembler.py, the two reference plans, format_registry.yaml,
the OVERLAY spec, and real STORY/EXERCISE atoms).

> **Bottom line up front:** Stories and exercises are placed as **WHOLE authored atoms** on
> the canonical path. There is **one** narrow truncation that is real and matters: the
> EXERCISE *guidance* is cut to its **first 2 sentences** from the **3rd exercise-bearing
> chapter onward** (the `quick_repeat` assembly rule). Chapter 1 itself is **not** fragmented:
> its single STORY atom and single EXERCISE atom render in full. The operator's "10 sections ×
> 5 variations" model is the wrong shape — the shipped spine is a **9-slot bestseller beat**
> and each slot has **~20–88 variations** (one chosen deterministically).

---

## THE TRUE CANONICAL RENDER PATH (which functions actually ship a book)

There are **two** code paths. The operator's premise ("`--pipeline-mode spine`") selects the
**spine / enriched path**, which is the one that ships bestseller books.

### Canonical (spine) path — call chain
```
scripts/run_pipeline.py : _run_spine_pipeline_mode()            # run_pipeline.py:507
  load_spine → apply_knobs → compile_beatmap                    # :613–624
  enrichment_select.select_enrichment(...)                      # builds EnrichedBook (slots per chapter)
  enrichment_select.apply_depth_pass(...)                       # ADDS DEPTH_ slots for long runtimes
  chapter_composer.compose_from_enriched_book(enriched, ...)    # run_pipeline.py:756  ← ships the book
    └─ per chapter: golden_chapter_synthesis.compose_golden_spine_chapter()   # chapter_composer.py:2975
         ├─ build_virtual_slot_streams()       # golden_chapter_synthesis.py:728  (bucket atoms → 1 stream/slot)
         ├─ chapter_composer.compose_chapter_prose()            # golden_chapter_synthesis.py:1157
         └─ frame_governor.apply_frame_enforcement()            # golden_chapter_synthesis.py:1182
    └─ strengthen_rendered_spine_manuscript() + dedupe_scene_furniture_book()  # chapter_composer.py:3005–3008
  clean_for_delivery() + delivery_contract_gate()               # whole-manuscript scrub
```
`scripts/pilot/run_spine_pipeline.py` is the standalone twin of the same chain
(`compose_from_enriched_book`, then `clean_for_delivery`).

### Legacy path (still present, used by registry/non-spine)
```
assembly_compiler.compile_plan() → CompiledBook(chapter_slot_sequence, atom_ids)   # assembly_compiler.py:686
  book_renderer.render_book() → TxtWriter.write()              # book_renderer.py:2030 / :1638
    └─ per chapter: chapter_composer.compose_chapter_prose()   # book_renderer.py:1814
```
Both paths converge on **`compose_chapter_prose`** (chapter_composer.py:2204) — that single
function is where atom prose is ordered into a chapter, so the STORY/EXERCISE integrity verdicts
hold for **both** paths.

### `scripts/compose_cohesive_chapter_from_plan.py` — NOT on the ship path
This is a standalone 8-part composer. It is **not** imported by `run_pipeline.py`,
`compose_from_enriched_book`, `compose_golden_spine_chapter`, or `compose_chapter_prose`.
**It does not ship books.** (Confirmed: no import edge from any of the above into it.)

---

## MODEL-POINT 1 — "12 chapters × 10 sections × 5 variations, 1 placed per section"

**VERDICT: REFUTED (every number is wrong, though the *shape* — deterministic 1-of-N per slot — is right).**

### Chapter count — NOT a fixed 12
- The runtime default for the canonical book runtime is **10**, not 12:
  `config/format_selection/format_registry.yaml:116` →
  `standard_book: chapter_count_default: 10  # ... was 12; Python value 10 preserved`.
- Chapter count is **per-plan**, hard-set, not a constant:
  - `config/plans/anxiety_gen_z_professionals_1h.yaml:8` → `chapter_count: 6`
  - `config/plans/anxiety_gen_z_professionals_6h.yaml:8` → `chapter_count: 12`
- Enforced in the legacy compiler at `assembly_compiler.py:742`
  (`chapter_count = int(format_plan.get("chapter_count") or ... 12)` — 12 is only the *last-resort* default).
- So "12" is true for the **6h** reference plan only; the 1h plan is **6**, the default
  `standard_book` is **10**, micro is **5**, deep_book_6h default is **20**
  (`format_registry.yaml:96–137`).

### Sections per chapter — it is a **9-slot bestseller beat**, NOT 10 (and NOT 6/7)
- Both reference plans use the identical 9-slot template (`*slots` anchor):
  `[HOOK, SCENE, STORY, PIVOT, REFLECTION, EXERCISE, TAKEAWAY, INTEGRATION, THREAD]`
  (`anxiety_gen_z_professionals_6h.yaml:54–63`, `..._1h.yaml:54–63`), matching
  `bestseller_beat_order` (`..._6h.yaml:46`).
- The `format_registry.yaml` **default beat is 6** types
  (`default_slot_definitions: [HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION]`,
  line 9) — but the **plans override** with the 9-slot bestseller beat, so the shipped grid is 9.
- There is **no** `SOMATIC_10_SLOT_GRID` constant anywhere in the render path; the shipped
  per-chapter slot list comes from `format_plan.slot_definitions` (legacy,
  `assembly_compiler.py:739–748`) or from the beatmap/enriched chapter slots (spine). The
  spine `_bucket_slots` recognizes 14 canonical slot names
  (`golden_chapter_synthesis.py:637–641`) but each chapter still carries ~the 9-beat set.

### Variations per section — ~20 to 88, NOT 5; one chosen deterministically
- Real atom files for `gen_z_professionals × anxiety` (measured this run):
  STORY=43, HOOK=88, SCENE=82, PIVOT=49, INTEGRATION=35, REFLECTION=29, EXERCISE=30,
  COMPRESSION=30, TAKEAWAY=20, THREAD=20, PERMISSION=20 variation blocks per `CANONICAL.txt`.
- "1 placed per section" is **correct**: STORY selection is deterministic via SHA-256 seed:
  `assembly_compiler.py:_deterministic_select` (:659) →
  `h = hashlib.sha256(f"{seed}:ch{chapter_index}:slot{slot_index}").digest()`; non-STORY slots
  resolve via `slot_resolver.resolve_slot` (also seed-keyed, `assembly_compiler.py:917`). Same
  inputs → same `atom_ids` → same `plan_hash` (`assembly_compiler.py:1043`).

---

## MODEL-POINT 2 — "Bestseller injections layered on top: PIVOT, plus STORY / SCENE / EXERCISE"

**VERDICT: PARTIAL / mostly CONFIRMED — but they are AUTHORED SLOTS, not late injections.**

PIVOT / SCENE / STORY / EXERCISE / TAKEAWAY / THREAD / PERMISSION are first-class **slots in the
plan's beat order** (above), resolved to atoms by the compiler/resolver. They are **not** bolted
on after the fact. What `compose_chapter_prose` actually does is **reorder** those resolved slots
into argued flow and weave **bridge sentences** between them:

- Assembly order (chapter_composer.py docstring :4–7 and body :2287–2594):
  `Opening(HOOK/SCENE) → ANGLE_CALLBACK → ANGLE_DEFINITION → SCENE → REFLECTION(trimmed) →
  STORY(+intro bridge) → PIVOT → COMPRESSION → mechanism bridge + derived MECHANISM + thesis →
  EXERCISE(bridge+setup+atom+validation) → PERMISSION → INTEGRATION → TAKEAWAY → THREAD`.
- The composer **derives** two non-atom blocks: a one-line **thesis** (`_derive_thesis`, :951;
  priority arc_thesis > chapter_thesis_bank > mechanism_thesis_families > legacy keyword) and a
  **MECHANISM** paragraph (`_distill_mechanism`, :1726) — these come from YAML families, not from
  a STORY/EXERCISE atom.
- **Bridges** (15–40-word transitions) are inserted between slots via
  `_bridge_after_opening`/`_bridge_before_story`/`_bridge_before_exercise`/`_bridge_before_integration`
  (:1017–1271) and within-slot via `_bridge_within_slot` (:1377). They are **additive** — they
  surround atoms, they never replace atom prose.
- PERMISSION is conditional ("high-cost chapters only" per the composer header :7; placed when a
  PERMISSION atom is present, :2546).
- TAKEAWAY can be arc-thesis-driven rather than a pool atom (`assembly_compiler.py:910–916` emits
  `arc_thesis:chN`, resolved in `prose_resolver.py:345–357`).

So: the bestseller beats are real and present, but the accurate mental model is
"**reorder + bridge-weave authored slots**", not "inject extras onto a base chapter".

---

## MODEL-POINT 3 — STORY / EXERCISE integrity (FULL atom vs FRAGMENT) — the critical question

### STORY integrity — **VERDICT: CONFIRMED FULL (atom placed whole). Not sliced.**

- A single STORY atom is **one self-contained paragraph** (no internal blank lines). Example:
  `atoms/gen_z_professionals/anxiety/STORY/CANONICAL.txt:8` — STORY v01 is a single ~70-word
  block (one scene + one named sensation). v02–v08 likewise each one block.
- Legacy path places the STORY string **verbatim**: `compose_chapter_prose` does
  `story_raw = slot_map.get("STORY", "")` (chapter_composer.py:2258) → `parts.append(story_raw)`
  (:2335). The only mutation is **prepending** a one-sentence intro bridge
  (`prepend_story_introduction_bridge`, :2325) — no truncation.
- Spine path aggregates STORY + depth-story and joins them:
  `story_blocks = list(b["STORY"]) + list(b["_depth_story"])` →
  `_first_or_join(story_blocks, ...)` (golden_chapter_synthesis.py:792–797). `_first_or_join`
  returns a single block **unchanged** (:703–704); for multiple stacked atoms it dedupes by
  paragraph and weaves bridges (`_dedupe_paragraphs`, :561) — it keeps whole paragraphs
  (drops only <24-char fragments and verbatim prefix/suffix duplicates).
- **Chapter-1 caveat (real, but does NOT fire for a single atom):**
  `_collapse_chapter_one_story_stack` (golden_chapter_synthesis.py:713–725) runs only for
  `chapter_index0 == 0` (:809) and keeps **only the first piece** when the STORY is a *stack*
  (split on `---` runs or on `\n\n` blocks >50 chars). Because a single CANONICAL STORY atom is
  one block with no `---`/`\n\n` split, this returns it **whole**. It only trims a Ch-1
  *montage* of multiple stacked STORY atoms down to the first beat (deliberate: "one embodied
  narrative beat, not a stitched montage"). The 6h reference plan's Ch-1 has exactly **one**
  STORY slot (`..._6h.yaml:57`, `count: 1`), so Ch-1 STORY ships full.

### EXERCISE integrity — **VERDICT: PARTIAL — FULL by default, but TRUNCATED to 2 sentences from the 3rd exercise-chapter onward.**

- A single EXERCISE atom is a **complete, self-contained practice** (e.g.
  `atoms/gen_z_professionals/anxiety/EXERCISE/CANONICAL.txt:7` — full box-breathing, ~12 ordered
  instructions). It is a full unit, never authored as a fragment.
- The EXERCISE atom prose is passed as the **`description` component** into the 5-part assembler:
  `compose_chapter_prose` → `assemble_exercise_for_chapter(... description_text=exercise_raw ...)`
  (chapter_composer.py:2400–2407) → `resolve_exercise_components(description_text=...)` sets
  `description = ComponentVariants(full=description_text, ...)` (component_assembler.py:382–386)
  → `assemble_exercise` emits `desc_text = _get_text(components.description, selection.description)`
  (component_assembler.py:517–519).
- **Default = FULL atom.** `ComponentSelection.description` defaults to `ComponentMode.FULL`
  (`phoenix_v4/exercises/models.py:87`); `_get_text` in FULL mode returns `variants.full`
  i.e. the **entire atom** (component_assembler.py:481). Every assembly rule except one keeps
  `description: full` (`config/practice/assembly_components.yaml`: emotional_pivot, flow_state,
  session_close, familiar_new_context, first_encounter, default — all `description: full`).
- **THE TRUNCATION (single site):** the `quick_repeat` rule sets `description: lean`
  (`config/practice/assembly_components.yaml:28`), matched when
  `repeat_count_gte: 2` (:25). `lean` = `_derive_lean(full_text, max_sentences=2)` =
  **first 2 sentences only** (component_assembler.py:192–197).
- `repeat_count` = number of **prior chapters that contained an EXERCISE**:
  `compose_chapter_prose` → `_build_assembly_context(..., exercise_repeat_index=_exercise_repeat_before_idx(...))`
  (chapter_composer.py:2387–2394, :1495–1502 counts prior EXERCISE chapters). So the 1st and 2nd
  exercise-bearing chapters render the **full** exercise; from the **3rd** onward the guidance is
  reduced to **2 sentences**. With a ~12-instruction box-breathing atom, that drops ~10 steps —
  i.e. the reader gets "Sit back from your screen. Place both feet flat on the floor." and nothing
  else of the practice (the bridge/intro/aha/integration wrappers still render).
- Note the fallback ladder: if the component_assembler raises, `compose_chapter_prose` tries
  `practice_library_loader.compose_exercise` (:2454) and finally appends `exercise_raw` **whole**
  (:2524). The truncation is specific to the **successful registry/component path** at
  repeat_count ≥ 2.

**For Chapter 1 specifically:** `repeat_count == 0` (no prior exercise chapters) → `first_encounter`
rule (or default) → **`description: full`** → Chapter-1 exercise ships the **full** atom.

---

## MODEL-POINT 4 — Runtime reuse: does the 6h book use the same atoms as the 15-min book?

**VERDICT: CONFIRMED — same persona×topic atom pool; depth scales by MORE atoms + MORE chapters, not longer single atoms.**

- The atom **pool is keyed only by persona × topic × slot × locale**, with no runtime/length
  dimension: `prose_resolver.resolve_prose_for_plan` reads
  `atoms/<persona>/<topic>/<engine|slot>/CANONICAL.txt` (prose_resolver.py:300–322);
  `assembly_compiler` selects from the same pool (`PoolIndex`, :841–847). A 15-min and a 6h book
  for `gen_z_professionals × anxiety` draw from the **identical** atom files. (The 1h and 6h
  reference plans are literally the same persona/topic/engine — `..._1h.yaml:2–7` ==
  `..._6h.yaml:2–7`.)
- **What differs by runtime is selection breadth and depth, not atom length:**
  1. **More chapters** → more `(chapter,slot)` seed coordinates → more distinct atoms pulled
     (15-min/`micro_book_15` default 5 chapters vs 6h/`deep_book_6h` default 20; the reference
     6h plan = 12). Selection is `used`-set aware so chapters don't repeat the same atom
     (`assembly_compiler.py:854`, `:923`).
  2. **Depth pass adds *new* atoms** (it does not lengthen existing ones):
     `enrichment_select.apply_depth_pass` (:3105) appends `DEPTH_*` slots up to
     180→300→600 words/chapter (`MIN/TARGET/MAX_DEPTH_WORDS_PER_CHAPTER`, :3322–3324) via
     `chapter.slots.append(depth_slot)` (:3074). The golden bucketer routes those depth atoms
     into the REFLECTION / STORY / EXERCISE streams
     (`golden_chapter_synthesis.py:649–661`), so longer runtimes = **stacked atoms** inside a
     slot, joined with within-slot bridges (`_bridge_within_slot`).
  3. **Exercise floor rises** for `deep_book_6h`: `compose_from_enriched_book` sets
     `five_part_floor = 2` (chapter_composer.py:2888) so practice chapters carry ≥2 EXERCISE slots.
  4. **Word-range / flow profile** differ by runtime: `format_registry.yaml`
     micro_book_15 `[2500,4500]` vs deep_book_6h `[50000,72000]` (:99, :135); flow profile
     micro→`short_form`, 6h→`deep_form` (`chapter_flow_gate.py:51–57`).

- **Can / should the 6h reuse the 15-min atoms?** It already does — same pool. The 6h doesn't
  re-use the *same selected instances* per chapter (the `used` set forces variety), and it stacks
  depth atoms to reach length. The 15-min book reads as "full atoms" because each of its few
  chapters carries a single full STORY + single full EXERCISE with no depth stacking and
  (critically) **repeat_count rarely reaches 2** across only 5 chapters, so its exercises stay
  full. The 6h book reaches length by **breadth + depth stacking**, which is also where its
  fragmentation risks concentrate (see DEFECTS).

---

## DEFECTS / RISKS (concrete; file:line; recommended — NOT implemented)

### D1 — EXERCISE guidance truncated to 2 sentences from the 3rd exercise-chapter on  *(HIGH for 6h/long books)*
- **Where:** `config/practice/assembly_components.yaml:25–28` (`quick_repeat`: `match: repeat_count_gte: 2`
  → `description: lean`); `component_assembler.py:192–197` (`_derive_lean` = first 2 sentences);
  trigger fed by `chapter_composer.py:2387–2394` / `:1495–1502`.
- **Effect:** From the 3rd EXERCISE-bearing chapter onward the practice atom is cut to its first
  2 sentences (~10 of ~12 instructions lost). On a 12-chapter 6h book this hits most chapters; on
  a 5-chapter 15-min book it usually never triggers — which is exactly why the operator perceives
  the 15-min book as "full atoms" and suspects the long book of fragments.
- **Recommended (do not implement here):** Reinterpret `repeat_count` as **per-unique-exercise**
  (truncate only when the *same* practice technique repeats), not "any prior exercise chapter";
  OR change `quick_repeat` to `description: full` (keep only bridge/intro lean); OR gate
  `quick_repeat` behind `repeat_count_gte: 4`. Validate against `book_quality_gate` repetition caps.

### D2 — Chapter-1 STORY montage collapses to first beat only  *(LOW–MED; only when Ch-1 has stacked STORY)*
- **Where:** `golden_chapter_synthesis.py:713–725` + `:809–810`
  (`_collapse_chapter_one_story_stack` returns `pieces[0]` / `blocks[0]`).
- **Effect:** If depth/enrichment stacks multiple STORY atoms into Chapter 1, only the first is
  kept; the rest are dropped (not truncated mid-atom, but the *other* full atoms vanish). Does
  **not** fragment a single atom. Reference 6h Ch-1 has `count:1` STORY so this is dormant there,
  but a long-runtime depth pass that injects DEPTH_STORY into Ch-1 would lose those beats.
- **Recommended:** Confirm Ch-1 enrichment never stacks STORY (then this is intended and safe), or
  bridge-join the first 2 beats instead of dropping all-but-first.

### D3 — Depth-module multi-variant dumps truncated to one body at 2400 chars  *(LOW; depth path only)*
- **Where:** `golden_chapter_synthesis.py:473–533` (`_extract_single_body_from_depth_canonical_dump`
  picks `chunks[0][:2400]`).
- **Effect:** When a depth module ships a multi-block CANONICAL dump, exactly one body is kept and
  hard-capped at 2400 chars. Correct intent (don't forward a montage) but the 2400-char clamp can
  clip a long depth teaching. Does not affect primary HOOK/SCENE/STORY/EXERCISE atoms.
- **Recommended:** Raise/remove the 2400 cap for depth bodies, or split into paragraphs and keep
  all that fit the chapter depth budget.

### D4 — REFLECTION "trim" is now a no-op (FYI, not a defect)  *(NONE — documents a prior fix)*
- `_trim_reflection` (chapter_composer.py:1761–1780) was historically a keyword filter that
  "silently discarded ~75%" of routed depth content; it now returns the **full** reflection after
  stripping hedging phrases only. Verified safe — full REFLECTION is preserved.

### D5 — `repeat_count` is book-global, so even *different* exercises get truncated  *(part of D1 root cause)*
- `_exercise_repeat_before_idx` (chapter_composer.py:1495–1502) counts **any** prior EXERCISE
  chapter, so two completely different practice atoms in chapters 3 and 4 are both treated as
  "repeats" and leaned. Fold into D1's fix.

---

## SUMMARY VERDICTS

| # | Model point | Verdict |
|---|-------------|---------|
| 1 | 12 ch × 10 sec × 5 var, 1 placed/section | **REFUTED** — chapters per-plan (6/10/12/20, not fixed 12); slots = **9-slot bestseller beat** (not 10/6/7); variations = **~20–88/slot** (not 5); the "1 deterministic pick/slot" part is **CONFIRMED**. |
| 2 | Bestseller injections (PIVOT/SCENE/STORY/EXERCISE…) | **PARTIAL/CONFIRMED** — they are authored **slots** reordered into argued flow with additive bridges + a derived thesis/MECHANISM; not late injections onto a base chapter. |
| 3 | STORY/EXERCISE = full atom or fragment | **STORY = CONFIRMED FULL.** **EXERCISE = PARTIAL:** full by default and in Ch-1, but **cut to first 2 sentences from the 3rd exercise-chapter onward** (`quick_repeat`/`lean`). |
| 4 | 6h reuses 15-min atoms? | **CONFIRMED** — same persona×topic pool; depth scales by **more chapters + appended DEPTH_ atoms (stacked)**, not by lengthening single atoms. |

**Single most important defect:** D1 — the `quick_repeat` rule truncates EXERCISE guidance to 2
sentences from the 3rd exercise-bearing chapter on. This is the concrete source of the operator's
"fragment of an exercise" intuition, and it is exactly why the 15-min book (few chapters, repeat_count
rarely ≥2) feels whole while a 12-chapter 6h book degrades mid-book.

**Will the deterministic ~925-en_US batch produce GOOD chapter-1s or fragmented ones?**
**Chapter 1 specifically: GOOD.** Ch-1 uses a single full STORY atom and a single full EXERCISE
atom (repeat_count 0 → full), with whole-atom placement and additive bridges. The fragmentation
risk (D1) lands on **later** chapters of long runtimes, **not** Chapter 1. If the batch is en_US
books at short/standard runtimes, exercises are largely full; for `deep_book_6h`/long runtimes,
expect 2-sentence exercise guidance in chapters 3+ unless D1 is addressed first.

---
*Read-only audit. No renderer/atom/config files were modified. This artifact is the only change.*
