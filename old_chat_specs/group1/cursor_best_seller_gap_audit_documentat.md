# Best seller gap audit documentation
_Exported on 4/16/2026 at 19:26:42 GMT+8 from Cursor (3.1.15)_

---

**User**

PHOENIX OMEGA — BESTSELLER DECONSTRUCTION + ATOM/PIPELINE AUDIT
Date: 2026-04-15
Agents: Pearl_Architect + Pearl_Editor + Pearl_Research + Pearl_Writer (advisory)
Mode: Analysis and documentation only. No code changes. No branch creation.
Output: One synthesis document — docs/BESTSELLER_GAP_AUDIT.md

══════════════════════════════════════════════════════════════════════
READ BEFORE ANY WORK
══════════════════════════════════════════════════════════════════════
1.  docs/SESSION_UNITY_PROTOCOL.md
2.  docs/BOOK_PLANNING_SYSTEM_SPEC.md          ← the new planning authority
3.  docs/BESTSELLER_STRUCTURES.md              ← 12 structures
4.  docs/CHAPTER_THESIS_BANK.md                ← intents + thread formulas
5.  docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md
6.  docs/BESTSELLER_SPINE_WRITER_SPEC.md
7.  docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
8.  phoenix_v4/planning/chapter_planner.py     ← structure assignment logic
9.  phoenix_v4/planning/catalog_planner.py     ← catalog selection logic
10. phoenix_v4/planning/assembly_compiler.py   ← slot assembly logic
11. phoenix_v4/planning/enrichment_select.py   ← atom selection logic
12. phoenix_v4/planning/slot_resolver.py       ← slot-to-atom mapping
13. phoenix_v4/planning/registry_resolver.py   ← registry query logic
14. phoenix_v4/rendering/chapter_composer.py   ← prose composition
15. atoms/INDEX.md + atoms/REFLECTION_MANIFEST.md
16. atoms/ directory structure (all persona/topic subdirs)
17. registry/ directory (all *.yaml registry files)
18. artifacts/coordination/ACTIVE_PROJECTS.tsv

Emit STARTUP_RECEIPT before any work.

══════════════════════════════════════════════════════════════════════
WHAT THE 20 BESTSELLERS ARE AND WHERE TO FIND THEM
══════════════════════════════════════════════════════════════════════
The 20 reference bestsellers used for ML pattern extraction are documented
in docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md. That document may contain
the titles, structural patterns, and research findings extracted from them.
If the actual text of the 20 books is present elsewhere in the repo (under
research/, artifacts/research/, SOURCE_OF_TRUTH/, or similar), locate and
read whatever structural/pattern analysis exists. If only the research doc
exists, work from that. Do not hallucinate book content — only analyze what
is verifiably present in the repo.

══════════════════════════════════════════════════════════════════════
PART 1 — ATOM AND TEMPLATE HEALTH AUDIT
══════════════════════════════════════════════════════════════════════

1A. INVENTORY EVERY ATOM TYPE IN THE REPO

Read atoms/ in full. For every atom you find, record:
  - atom_type (STORY, SCENE, PIVOT, APHORISM, EXERCISE, REFLECTION,
    PRACTICE, INTEGRATION, QUOTE, TEACHING, METAPHOR, or other)
  - persona coverage (which personas have atoms of this type)
  - topic coverage (which topics have atoms of this type)
  - approximate count per type
  - quality sample: pull 2 representative atoms per type — one strong,
    one weak — and note what makes them strong or weak

Build a coverage matrix:
  Rows: atom types
  Columns: personas (gen_z_professionals, millennial_women_professionals,
    burned_out_pro, corporate_managers, etc.)
  Cells: count (0 = gap, low = risk, adequate = 10+, strong = 20+)

1B. IDENTIFY ATOM TYPES THAT DO NOT EXIST AT ALL

After inventorying what exists, name every atom type the repo does NOT have
but that bestsellers require. Specifically check for absence of:
  - DESIRE atom: names what the reader secretly wants before they can name it
  - TENSION atom: creates productive discomfort or unresolved stakes
  - SHAME_RECOGNITION atom: names a specific private shame so precisely the
    reader feels "this is about me"
  - AUTHORITY_PROOF atom: builds trust through evidence, lived experience,
    named framework, or counterintuitive diagnosis — not just explanation
  - OBJECTION_HANDLING atom: anticipates and preempts reader resistance
  - MEMORABLE_FRAMEWORK atom: introduces a named concept the reader can
    retell in one sentence
  - CHAPTER_PROPULSION atom: ends a chapter with an unanswered pull question
    that creates compulsion to continue
  - CALLBACK atom: returns to an earlier scene, metaphor, or phrase in a way
    that creates resonance and structural integrity
  - IDENTITY_SHIFT atom: the moment a reader's self-narrative changes, not
    just their information level
  - STORY_TURN atom: the reversal inside a narrative where the reader's
    interpretation of a scene changes
  - COLD_OPEN atom: hook that drops the reader into scene before establishing
    context — the "in medias res" opening
  - CONFESSION atom: author vulnerability that earns reader trust
  - MYTH_BUST atom: specific false belief the reader holds, named precisely,
    then dismantled with evidence

For each missing type: name it, define what it does for the reader,
give one concrete example of what a strong instance would look like,
and note whether existing atoms partially fulfill this role.

1C. METADATA HEALTH AUDIT

For a sample of 30 atoms across 3 personas and 3 topics, audit the metadata
on each atom. Record which metadata fields are:
  - present and accurate
  - present but vague (e.g., band: 2 with no justification)
  - absent

Specifically check for:
  □ band (1–4)
  □ intensity (1–5)
  □ ontgp_move (orient/name/turn/give/pull)
  □ topic_allowlist
  □ topic_blocklist
  □ persona_allowlist
  □ collision_family
  □ tension_type (missing from all current atoms — does it exist anywhere?)
  □ shame_level (missing from all current atoms — does it exist anywhere?)
  □ proof_mode (data / story / diagnosis / lived_experience / framework)
  □ shareability (is this atom a screenshot candidate?)
  □ callback_role (does this atom plant a seed that should be called back?)
  □ reader_objection (what resistance does this atom preempt?)

Report: what % of audited atoms have each field. Identify the 5 most
critical missing metadata fields for bestseller-grade selection.

1D. PEARL_WRITER TRIAGE

After the audit, identify specifically which atoms need Pearl_Writer work.
Categorize them into three tiers:
  REWRITE: atom has the right intent but weak prose, lacks specificity,
    or is too generic to pass scene_anti_genericity_gate
  RECLASSIFY: atom is mislabeled (wrong type, wrong band, wrong persona)
  RETIRE: atom is a duplicate, off-topic doctrine, or so weak it adds noise
    rather than value
  EXPAND: atom is good but needs a variant bank (collision family has 1 atom)

Report counts per tier per atom type. This becomes Pearl_Writer's work queue.

══════════════════════════════════════════════════════════════════════
PART 2 — 20 BESTSELLERS DECONSTRUCTION
══════════════════════════════════════════════════════════════════════

For each bestseller documented in docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md,
extract and document the following. Work only from what the repo contains —
if a field cannot be answered from repo evidence, mark it as NOT_IN_REPO.

2A. PER-BOOK PROFILE (repeat for each of the 20)

  Book: [title]
  transformation_promise: The one-sentence transformation — what the reader
    believes is wrong with them on page 1, and what they believe instead by
    the final chapter.
  emotional_contract: comfort / challenge / permission / awakening /
    strategy / identity_upgrade / belonging (pick 1–2)
  private_shame_named: The specific private shame or desire the book names
    so precisely that the reader feels "this is about me."
  reader_identity_offered: What identity does buying this book let the
    reader claim? ("I am someone who...")
  cultural_conversation_entered: What public conversation is this book
    joining? What is the ambient anxiety or aspiration it is speaking to?
  controlling_idea: The one elegant mental model the reader leaves with.
    Not a list of insights — the one frame that reorganizes everything.
  authority_mechanism: How does the author earn trust?
    (data + story / pure narrative / lived_experience + framework /
    diagnosis + reversal / counterintuitive_claim + proof)
  sticky_language: 3–5 phrases, sentences, or coined terms that are
    quotable, repeatable, and memorable. These are the lines readers underline.
  compulsion_mechanism: What unanswered question or open loop pulls
    the reader from chapter to chapter?
  chapter_ending_pattern: How do chapters close? (cliff / soft_pull /
    reframe_drop / practice_cue / identity_offer / callback_plant)
  scene_to_abstraction_ratio: Rough % of concrete scene vs. explanation.
  atom_types_observed: Which of the atom types listed in 1B are present?
    (list observed types — this is the comparative gap map)
  assembly_grammar_observed: The actual sequence of moves in a chapter
    (e.g., COLD_OPEN → TENSION → AUTHORITY_PROOF → MECHANISM → STORY_TURN
    → MEMORABLE_FRAMEWORK → PRACTICE → PROPULSION)
  pacing_signature: How the bestseller varies paragraph length, scene vs.
    explanation, acceleration vs. deceleration across a chapter.

2B. CROSS-BESTSELLER PATTERNS

After profiling all 20, identify:

  UNIVERSAL PATTERNS (appear in 15+ of the 20):
    - Which atom types are always present?
    - Which assembly sequences recur?
    - What pacing patterns appear across genres and tones?
    - What emotional contract types dominate?

  DIFFERENTIATING PATTERNS (appear in 8–14 of 20):
    - What structural choices separate the top 20% from the rest?
    - What makes a book memorable vs. merely useful?

  ABSENCE PATTERNS (what the 20 bestsellers almost never do):
    - What atom types are almost never used in isolation?
    - What assembly sequences are absent?
    - What metadata would describe these negative examples?

2C. WHAT PHOENIX CURRENTLY CANNOT REPRODUCE

Comparing the observed atom types, assembly grammar, and metadata from
Part 2A against the Phoenix inventory from Part 1, list:

  GAP 1: Atom types that appear in bestsellers but do not exist in Phoenix.
  GAP 2: Assembly sequences that the chapter_composer / assembly_compiler
    cannot produce because the required atom types are missing.
  GAP 3: Metadata fields the bestsellers imply (tension_type, shame_level,
    proof_mode, callback_role, shareability) that Phoenix atoms do not encode,
    which means the selector cannot make these distinctions.
  GAP 4: ChapterPlan schema fields from docs/BOOK_PLANNING_SYSTEM_SPEC.md
    that would need to reference the missing atom types but cannot because
    the atom taxonomy is incomplete.

══════════════════════════════════════════════════════════════════════
PART 3 — PIPELINE AUDIT: FROM CATALOG TO ASSEMBLED PROSE
══════════════════════════════════════════════════════════════════════

Read the full pipeline in order:

  catalog_planner.py → chapter_planner.py → assembly_compiler.py
  → enrichment_select.py + slot_resolver.py + registry_resolver.py
  → chapter_composer.py

For each stage, answer:

3A. CATALOG PLANNER
  - What does it use to select which books to plan?
  - Does it use buying trigger logic, or only topic/persona coverage?
  - Does it know about the reader's private shame, desire, or cultural
    conversation? Or only about topic and persona IDs?
  - What would a bestseller's catalog entry look like vs. what Phoenix
    currently generates?

3B. CHAPTER PLANNER
  - What decides which bestseller structure is assigned to each chapter?
  - Is the assignment deterministic by hash, or by chapter_role + arc_position?
  - Does it know what emotional state the reader is in entering this chapter?
  - Does it specify the open-loop propulsion strategy for the chapter ending?
  - Does it specify the tension type or shame_level this chapter should address?
  - What information is passed downstream to assembly_compiler?
    What information is NOT passed that assembly needs to make good decisions?

3C. ASSEMBLY COMPILER
  - What is the actual slot sequence it produces?
  - Does it understand escalation (each slot must advance the reader's state
    from the previous slot), or only coverage (each slot fills a type)?
  - Does it have any concept of contrast (heavy slot → light slot), relief
    (tension → release), or payoff timing?
  - Does it handle open-loop → resolution across chapters?
  - Does it select atoms based on tension_type, shame_level, proof_mode,
    or callback_role? Or only topic/persona/band?
  - What is the maximum chapter-level dramatic movement it can produce
    vs. what a bestseller chapter requires?

3D. ENRICHMENT SELECTOR + SLOT RESOLVER
  - When slot_resolver maps a plan slot to atom candidates, what fields
    does it use to filter?
  - Does it understand that a STORY atom that plants a callback seed must
    be selected before the CALLBACK atom that resolves it?
  - Does it understand that an AUTHORITY_PROOF atom must precede the
    mechanism it is proving?
  - Does it understand reader objection handling — that some chapters need
    an OBJECTION_HANDLING atom before the PRACTICE atom or the reader resists?
  - Can it select atoms for dramatic function (e.g., "this slot needs the
    atom that will most surprise the reader given what came before"), or
    only for metadata match?

3E. CHAPTER COMPOSER
  - What is the actual prose assembly grammar?
  - Does it create transitions that explain why each atom follows the previous
    one, or does it stitch with generic glue?
  - Can it produce the "slow down to let truth land" pacing pattern?
  - Can it produce the "short aphoristic line after long explanatory section"
    rhythm that bestseller prose uses for impact?
  - Does it flatten distinctive atom voice into one house tone?
  - Where does it produce mechanical-sounding prose that a human reader
    would identify as AI-assembled?

3F. PLANNING MISTAKES SUMMARY
  After auditing all five stages, list the top 10 specific planning and
  assembly mistakes that are causing Phoenix books to fail as reading
  experiences, ranked by impact. For each:
    - What the mistake is
    - Which stage produces it
    - What the bestseller equivalent looks like
    - What change would fix it

══════════════════════════════════════════════════════════════════════
PART 4 — THE 60 BESTSELLER QUESTIONS
══════════════════════════════════════════════════════════════════════

Answer each of the following questions using evidence from the repo
(atom inventory, registry, pipeline code, bestseller research doc,
BOOK_PLANNING_SYSTEM_SPEC.md). Mark each answer:
  ✓ ADDRESSED — Phoenix has a mechanism for this
  ⚠ PARTIAL — something exists but is incomplete or advisory only
  ✗ MISSING — nothing in Phoenix handles this

Group A — Reader Promise
  1. Does Phoenix encode the transformation promise as a first-class field
     that governs every chapter's selection criteria?
  2. Does any part of the pipeline track what the reader believes entering
     chapter 1 vs. what they should believe in the final chapter?
  3. Do we have atoms that name specific private shame with the precision
     of "this is about me" rather than general empathy?
  4. Does the plan layer define the emotional contract (comfort / challenge /
     permission / awakening / strategy / identity_upgrade / belonging)?
  5. Does every chapter plan specify whether it advances the transformation
     promise or is merely topically relevant?

Group B — Compulsion
  6. Does the ChapterPlan schema have a field for the chapter's open loop
     (the unanswered question that pulls the reader forward)?
  7. Do chapter endings currently create anticipation, or do they conclude?
  8. Does assembly_compiler select a CHAPTER_PROPULSION atom type, or does
     the chapter just end when slots are filled?
  9. Do we have a tension_type metadata field on atoms so the selector can
     choose contradiction vs. mystery vs. stakes vs. delayed reveal?
  10. Can the pipeline produce a "before/after gap" chapter structure —
      where the reader sees the problem, then the promise, then the path?

Group C — Authority
  11. Do atoms encode proof_mode so the selector can balance data / story /
      diagnosis / lived_experience / named_framework across a chapter?
  12. Do we have the "I see you / I can explain this / here is what to do"
      three-move authority sequence in the assembly grammar?
  13. Do we have CONFESSION atoms (author vulnerability that earns trust)?
  14. Do we have MEMORABLE_FRAMEWORK atoms that let the reader retell the
      core idea in one sentence?
  15. Does the pipeline produce named concepts or just explanations?

Group D — Voice
  16. Does chapter_composer vary sentence structure, paragraph length, and
      rhythm within a chapter, or does it produce uniform prose?
  17. Do we have a short-aphoristic-line atom type that can be placed after
      long explanatory passages for impact?
  18. Do our templates flatten distinctive atom voice into one house tone?
  19. Can we identify which phrases in current Phoenix output would be
      impossible to imagine in a strong human-authored book?
  20. Is there a voice consistency gate that checks authored voice vs.
      assembled voice?

Group E — Memorability
  21. Does memorable_line_gate detect actual shareable insight, or just
      polished sentences?
  22. Do we produce at least one quotable, screenshottable line per chapter?
  23. Do we develop metaphors across a book (motif), or only introduce them
      once and abandon them?
  24. Is there a sticky_language density target per chapter in any plan or gate?
  25. Do atoms encode shareability as a metadata field?

Group F — Structural Emotion
  26. Does the BookStructurePlan schema define the emotional arc as rupture /
      recognition / explanation / relief / challenge / agency / integration?
  27. Does the plan specify where the book intentionally makes the reader
      uncomfortable?
  28. Does the plan specify where it slows down to let truth land?
  29. Does the plan specify where it accelerates with practical momentum?
  30. Do our plans define emotional movement per chapter, or only topic coverage?

Group G — Narrative and Scene
  31. What % of Phoenix atoms are concrete scene vs. explanation/instruction?
      (estimate from atom inventory)
  32. Do we have all of these scene types: personal_anecdote, client_story,
      cultural_scene, reader_mirror, historical_vignette, research_example?
  33. Does chapter_composer have a transition grammar for moving from scene
      to lesson without sounding mechanical?
  34. Do our atoms contain enough "lived world" — specificity of place, time,
      body, sensation — or are they mostly explanation and instruction?
  35. Do we have COLD_OPEN atoms that drop the reader into scene before
      establishing context?

Group H — Framework Design
  36. Do the 12 bestseller structures in BESTSELLER_STRUCTURES.md include
      guidance on how long each framework takes to unfold across chapters?
  37. Are frameworks introduced at the right moment (when the reader has
      already felt the problem), or are they introduced before the reader
      needs them?
  38. Does Phoenix produce books with one controlling idea, or books with
      many disconnected insights?
  39. Is the plan layer preventing "too many concepts, too few controlling
      ideas" — or is it permitting it?
  40. Does the assembly grammar produce framework revelation, or just
      framework explanation?

Group I — Assembly Grammar
  41. Is the actual assembly grammar of Phoenix chapters documented anywhere?
      If so, where? If not, this is a gap.
  42. Does assembly_compiler support COLD_OPEN, REVERSAL, CONFESSION,
      OBJECTION_HANDLING, MYTH_BUST, CALLBACK_BRAID, CRESCENDO as named
      structural moves?
  43. Are atoms selected for dramatic function (what they do to the reader's
      state relative to the previous atom), or only for metadata match?
  44. Does the assembler understand escalation, contrast, and relief as
      chapter-level structural concepts?
  45. Can the assembler produce a callback braid — where a motif introduced
      in chapter 2 returns in chapters 5 and 10 with escalating meaning?

Group J — Pacing
  46. Does chapter_composer vary paragraph length at high-emotion moments
      vs. explanation moments?
  47. Is there a maximum gap between hook and first payoff in any plan or gate?
  48. Does any gate enforce alternation of heavy and light material?
  49. Does semantic_dedup distinguish intentional repetition (rhythmic
      emphasis) from accidental repetition (duplication)?
  50. Do our chapters pace like chapters, or like stitched atom reports?

Group K — Market Fit
  51. Does catalog_planner select books because the reader has a buying
      trigger, or because the topic exists in the registry?
  52. Does any plan or atom encode cultural_conversation_entered — the
      ambient anxiety or aspiration the book is speaking to?
  53. Does the pipeline distinguish surface pain (what the reader says they
      want) from deep pain (what they actually need)?
  54. Are any commercial promises in our catalog emotionally dangerous or
      overused (e.g., "fix your anxiety in 7 days")?
  55. Does the reader identity offered by each book create buying motivation?

Group L — Comparative Gap
  56. Which atom types exist in the 20 bestsellers but not in Phoenix?
      (answer from Part 1B + Part 2C)
  57. Which metadata fields do bestsellers imply that Phoenix atoms do not
      encode? (answer from Part 1C + Part 2A)
  58. Which Phoenix chapters would our current gates incorrectly pass that a
      human reader would abandon? (give a specific example from a recent pilot)
  59. Which bestseller chapters would our gates incorrectly score as weak?
  60. What does a bestseller do that cannot be represented in the current
      ChapterPlan schema — even after the recent BOOK_PLANNING_SYSTEM_SPEC
      additions?

══════════════════════════════════════════════════════════════════════
PART 5 — THE MINIMUM VIABLE ATOM TAXONOMY
══════════════════════════════════════════════════════════════════════

The sharpest diagnostic question for this entire audit:

  What is the minimum set of atom types, metadata fields, and assembly
  rules required to reproduce the reading experience of a bestseller
  chapter — not just its topic coverage?

Answer this question directly. Produce:

5A. THE COMPLETE ATOM TAXONOMY
  List every atom type that Phoenix needs to produce bestseller chapters.
  For each type:
    - name and definition
    - what it does to the reader's state
    - what metadata it must carry
    - which ONTGP move it primarily serves
    - example of a strong instance (1 sentence description, not full prose)
    - present / missing / partial in current Phoenix repo

5B. THE REQUIRED METADATA SCHEMA EXTENSION
  List every metadata field that needs to be added to atoms that does not
  currently exist. For each:
    - field name
    - allowed values
    - which part of the pipeline consumes it
    - which gate or selector needs it

5C. THE ASSEMBLY GRAMMAR SPEC
  Write the canonical assembly grammar for a bestseller chapter as an
  ordered sequence of atom types with:
    - required vs. optional slots
    - minimum and maximum slot counts per type
    - escalation rules (what must come before what)
    - contrast rules (what cannot be adjacent)
    - the emotional state the reader should be in entering vs. leaving
      each slot

══════════════════════════════════════════════════════════════════════
OUTPUT: docs/BESTSELLER_GAP_AUDIT.md
══════════════════════════════════════════════════════════════════════
Write one file: docs/BESTSELLER_GAP_AUDIT.md

Structure:
  §1  Executive Summary (1 page — the 5 highest-leverage findings)
  §2  Atom Inventory and Coverage Matrix (Part 1A)
  §3  Missing Atom Types (Part 1B — with examples)
  §4  Metadata Health Report (Part 1C)
  §5  Pearl_Writer Work Queue (Part 1D — REWRITE/RECLASSIFY/RETIRE/EXPAND)
  §6  Per-Bestseller Profiles (Part 2A — condensed, one section per book)
  §7  Cross-Bestseller Universal Patterns (Part 2B)
  §8  What Phoenix Cannot Currently Reproduce (Part 2C)
  §9  Pipeline Audit: Five-Stage Failure Map (Part 3)
  §10 Top 10 Planning and Assembly Mistakes (Part 3F)
  §11 The 60 Questions — Scored (Part 4 — ✓ / ⚠ / ✗ per question)
  §12 The Minimum Viable Atom Taxonomy (Part 5A)
  §13 Required Metadata Schema Extension (Part 5B)
  §14 The Assembly Grammar Spec (Part 5C)
  §15 Prioritized Action List
      Rank every finding by: (impact on book quality) × (implementation effort)
      Top 10 highest-ROI fixes with estimated scope (hours / days / sprint)

After writing the file, print:
  - Total §§ written
  - Total missing atom types identified
  - Total metadata fields missing from current atoms
  - Number of the 60 questions answered ✗ MISSING
  - The single highest-ROI fix (one sentence)

══════════════════════════════════════════════════════════════════════
WRITE SCOPE
══════════════════════════════════════════════════════════════════════
CREATE:  docs/BESTSELLER_GAP_AUDIT.md
READ:    everything listed above
MODIFY:  nothing else

No branches. No code changes. No registry edits.
This is a read-and-synthesize session only.

CLOSEOUT_RECEIPT required fields:
  AGENT / TASK / COMMIT_SHA (no commits) / FILES_WRITTEN / STATUS /
  NEXT_ACTION

NEXT_ACTION must name:
  1. The specific Pearl_Writer workstream to queue from §5 (Pearl_Writer
     work queue)
  2. The specific schema extension to implement from §13
  3. The specific assembly grammar change to implement from §14
  4. Whether BOOK_PLANNING_SYSTEM_SPEC.md needs amendment based on findings

---

**Cursor**

Starting the bestseller gap audit: emitting STARTUP_RECEIPT and reading mandatory sources in parallel.



Writing the synthesis document: incorporating verified findings, including that `docs/BOOK_PLANNING_SYSTEM_SPEC.md` is absent from the repo and that `pool_index._parse_block_file_canonical` drops metadata for non-STORY block atoms.



Marking questions 56–57 as addressed (answered in this document) and updating the MISSING count.



Here is what was delivered.

## STARTUP_RECEIPT (emitted before work)

```
STARTUP_RECEIPT
AGENT:              Pearl_Architect (+ advisory synthesis)
TASK:               Bestseller deconstruction + atom/pipeline audit → docs/BESTSELLER_GAP_AUDIT.md
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          docs / Pearl Prime planning & quality (cross-cutting)
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md;docs/BESTSELLER_STRUCTURES.md;docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;phoenix_v4/planning/*;phoenix_v4/rendering/chapter_composer.py
READ_PATH_COMPLETE: yes — docs/BOOK_PLANNING_SYSTEM_SPEC.md not found in repo (noted in audit)
WRITE_SCOPE:        docs/BESTSELLER_GAP_AUDIT.md
OUT_OF_SCOPE:       code, registries, branches
BLOCKERS:           none
READY_STATUS:       ready
```

## Output

**Created:** [docs/BESTSELLER_GAP_AUDIT.md](docs/BESTSELLER_GAP_AUDIT.md) — full §1–§15 synthesis (executive summary, atom inventory + matrix, missing types, metadata audit, Pearl_Writer queue, 20 book profiles derived from the benchmark doc + five cross-cited titles, cross patterns, Phoenix gaps, five-stage pipeline map, top mistakes, 60 scored questions, MV taxonomy, metadata extension, assembly grammar spec, prioritized actions, receipts).

**Notable repo facts embedded in the audit**

- **`docs/BOOK_PLANNING_SYSTEM_SPEC.md`** is absent; planning is inferred from code (`ChapterPlanResult`, `chapter_planner`, configs).
- **`PoolIndex._parse_block_file_canonical`** attaches **`metadata={}`** to non-STORY block atoms — a core selector blind spot.
- **~4,531** non-locale `CANONICAL.txt` files; **`atoms/INDEX.md` is outdated**; sample **placeholder HOOK** bodies under `gen_z_professionals/burnout/HOOK/`.

### Required printout

| Metric | Value |
|--------|--------|
| Total §§ written | **15** |
| Missing atom types (Part 1B list) | **13** |
| New metadata fields listed in §13 | **10** |
| Of 60 questions: **✗ MISSING** | **19** |
| Single highest-ROI fix | **Parse and propagate metadata for all slot types into `PoolIndex` / `AtomEntry` so selection is not STORY-only.** |

### CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:              Pearl_Architect (synthesis)
TASK:               docs/BESTSELLER_GAP_AUDIT.md
COMMIT_SHA:         none (no commits)
FILES_WRITTEN:      docs/BESTSELLER_GAP_AUDIT.md
STATUS:             complete
NEXT_ACTION:        (1) Pearl_Writer: REWRITE/RETIRE placeholder HOOK/SCENE + generic PIVOT/THREAD (§5). (2) Schema: `proof_mode`, `tension_type`, `shame_level`, `shareability`, `reader_objection` + PoolIndex propagation (§13). (3) Assembly: §14 objection-before-practice + proof-before-prescription in planner/compiler. (4) Add/restore `docs/BOOK_PLANNING_SYSTEM_SPEC.md` with open-loop, proof balance, shame/tension targets, callback graph — file missing today; code `ChapterPlanResult` lags bestseller needs (§8–§9).
```

