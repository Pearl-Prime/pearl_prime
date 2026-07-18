# Phase 2: Current Pipeline Structural Audit

## Answers to the Five Questions

### 1. Does the current pipeline have a concept of "section within a chapter"?

**Minimally, in code. Not in rendered output.**

`phoenix_v4/planning/beatmap_compile.py` defines `SOMATIC_10_SLOT_GRID` and `BeatmapSlot`, and the code nominally assigns 10 slot types per chapter. However:

- The `standard_book` runtime format uses **4 base slots per chapter** in practice (HOOK, SCENE, REFLECTION, INTEGRATION), not 10
- These slots are not rendered as named structural sections — they are concatenated in sequence
- The chapter composer (`chapter_composer.py`) describes its assembly order as:
  `HOOK/SCENE → bridge → STORY → PIVOT → bridge → MECHANISM → REFLECTION → bridge → EXERCISE → COMPRESSION → PERMISSION → INTEGRATION → TAKEAWAY → THREAD`
  
  This is a fixed concatenation order, not a "section with a declared job" — no section is named or delimited in output

### 2. What determines chapter length?

**Format budget, not section count.**

- `SOMATIC_WORD_BUDGET` in `beatmap_compile.py` sets per-slot word targets (e.g., HOOK=320, SCENE_A=520)
- Depth pass (`enrichment_select.py`) appends `depth_module` rows when under-target
- Result: chapters are filled to budget by stacking atoms, not by filling 10 defined sections
- Actual delivery: `standard_book` produces ~600-700 words/chapter in spine mode (8,015 words / 12 chapters)
- Target: 54,000 words for 6h format = 4,500 words/chapter — **nowhere near achieved**

### 3. What is the unit of atom selection?

**Slot type (HOOK, SCENE, REFLECTION, EXERCISE) picked from an atom pool.**

- Atoms are selected by slot type from `SOURCE_OF_TRUTH/` registries
- Selection uses deterministic hash seeding on `(topic + persona + chapter_index)`
- Anti-repetition: cooldown tracking prevents same atom from appearing twice in nearby chapters
- No section-level job is declared — the atom pool is chosen by type, not by position-in-chapter narrative function

### 4. Are there named structural roles per section?

**In the beatmap spec, yes. In the rendered book, no.**

- `SOMATIC_10_SLOT_GRID` names 10 roles
- These names are internal planning metadata, not rendered headings or structural markers
- The reader cannot identify where "section_06_teacherdoctrine" begins in a chapter — it has no marker
- The chapter reads as continuous (or discontinuous) prose, not as named-section blocks

### 5. When you read a rendered chapter, can you identify where sections begin/end?

**No — and worse, the rendered output leaks assembly debris.**

---

## Canary Output: What a Chapter Actually Looks Like

From `artifacts/pilot/full_15_spine/anxiety/book.txt`, Chapter 1 (first ~100 words of visible prose):

```
Chapter 1
The Alarm That Won't Stop Ringing

Your body started keeping score before you did. It has been presenting the invoice in small ways ever since.

Someone stops at your desk. You take out one earbud. They ask a question. Your screen is behind you — open, visible. morning sun cutting through the blinds through the office window above your monitor. You answer. They nod and walk away. You put the earbud back. the avenue outside is there below. Your screen is still open behind you. You turn back to it.

Notice a thought that repeats itself in your mind. Follow it back. Who told you
this was true? How long have you carried it? If you set it down right now, what
would be different? Not forever. Just for today. What changes when the story stops?

[...then immediately the full pool of hook variants dumps into the chapter...]
## HOOK v01 --- --- You did everything they said to do. Your chest has not gotten the memo. ---
## HOOK v02 --- --- The task is open. You have been looking at it for forty minutes. --- 
[...19 hook variants appearing verbatim in the delivered book...]
```

**The "section" structure visible to a reader is: chapter title → 3 paragraphs of scene → 2 paragraphs of reflection → a dump of 19 raw HOOK variants labeled `## HOOK v01`, `## HOOK v02`...**

This is the atom pool leaking into delivery. The reader sees the variant selection apparatus, not a coherent chapter.

From `artifacts/pilot/stacked_packet/anxiety/book.txt`, Chapter 1 (the template pilot output):

```
Chapter 1
The Alarm That Won't Stop Ringing

Put your hand on your chest right now.
Feel what's there. The heartbeat. The breath. The warmth of your palm against your body.
[...coherent somatic prose, ~300 words, ends with a turning point...]

The phone was the first thing you touched this morning...
[teacher doctrine section, ~100 words]

Let me tell you about someone who carried everything in her shoulders.
Elena didn't know she was doing it...
[STORY_INJECTION_POINT]

Do you recognize anything in that story?...

Right now, scan your body. Start at the top of your head...
[exercise section, 150 words]

[EXERCISE_INJECTION_POINT]

[...then more somatic narrative from the next section...]
```

The template pilot output is **structurally legible** — hook, scene, story, reflection, exercise, integration — even with placeholder gaps. A reader could follow the progression. **This output does not have 19 raw hook variants dumped into it.**

---

## The Structural Gap in Numbers

| Metric | Current Assembly Pipeline | Template Pilot (v2_somatic) |
|--------|--------------------------|------------------------------|
| Sections per chapter with declared job | 0 (implicit only) | 10 (named) |
| Reader-visible section markers | None | None (but flow is legible) |
| Atom pool leakage in output | YES (## HOOK v01..v19) | No leakage |
| Word count per book | 8,015 (spine) / 4,828 (registry) | 14,397 (pilot, incomplete) |
| Section job enforced at assembly time | No | Yes (by template slot position) |
| Chapter flow gate pass | 0/12 (FAIL, all topics) | Not measured |
| Opening hook guaranteed | No (exercise or reflection can lead) | Yes (section_01 = hook always) |
| Structural coherence | Emergent / absent | Built-in by design |

---

## Why The Current Pipeline Fails at Coherence

From `DEFINITIVE_PIPELINE_COMPARISON.md`:

> "Primary issues include WEAK_TRANSITIONS, MISSING_CLEAR_POINT, and (where applicable) GENERIC_SCENE_FALLBACK. Root cause: spine mode uses `compose_from_enriched_book`, which concatenates slot bodies in beatmap order — not the full thesis-threaded `compose_chapter_prose` path."

The chapter flow gate fails all 12/12 chapters across all 15 topics. The pipeline knows this. It has been failing for every run. The fix attempted (`compose_chapter_prose`) adds bridge sentences between atoms but does not change the underlying structure problem: **there is no declared narrative arc within a chapter**.

---

## Current Pipeline Structure Diagram

```
Arc/Spine YAML
     ↓
Knob Apply (per-format weights)
     ↓
Beatmap Compile (4-10 slots per chapter, by slot type)
     ↓
EnrichmentSelect (atom pool → fill each slot by type)
     ↓
Depth Pass (append depth_module rows if under word target)
     ↓
compose_from_enriched_book (concatenate slot bodies in order)
     ↓
book.txt (delivered to reader)
```

At no point does a chapter have:
- A declared opening job (e.g., "arrest attention in 150 words")
- A declared mechanism job (e.g., "explain WHY at mechanistic level")
- A declared reader-mirror job
- An ordered sequence of these that is enforced
- Variant selection based on section identity (not just type)
