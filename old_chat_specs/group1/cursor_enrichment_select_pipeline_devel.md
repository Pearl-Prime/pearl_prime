# Enrichment select pipeline development
_Exported on 4/16/2026 at 19:32:00 GMT+8 from Cursor (3.1.15)_

---

**User**

Act as Pearl_GitHub + Pearl_Dev + Pearl_Writer for Phoenix Omega.

Read these files before doing any work:

- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- docs/KNOB_APPLY_STAGE_CONTRACT.md (if on main after merge)
- phoenix_v4/planning/knob_apply.py (FULL — ShapedSpine output)
- phoenix_v4/planning/beatmap_compile.py (FULL — Beatmap output)
- phoenix_v4/planning/registry_resolver.py (FULL — current enrichment logic)
- phoenix_v4/planning/assembly_compiler.py (first 100 lines — current Stage 3)
- phoenix_v4/rendering/chapter_composer.py (FULL — how chapters render today)
- phoenix_v4/rendering/book_renderer.py (first 80 lines — prose rendering)
- phoenix_v4/exercises/component_assembler.py (first 60 lines — exercise assembly)
- phoenix_v4/exercises/practice_library_loader.py (first 60 lines — exercise fallback)
- scripts/run_pipeline.py (lines 500-600 — how stages connect, lines 904-990 — registry path)
- config/spines/anxiety_spine.yaml (first 60 lines)
- config/spines/grief_spine.yaml (first 60 lines)
- config/spines/burnout_spine.yaml (first 60 lines)
- config/knobs/topic_knob_profiles.yaml (first 80 lines)
- config/format_selection/format_registry.yaml (FULL)
- config/topic_engine_bindings.yaml (FULL)
- config/quality/ei_v2_config.yaml (first 40 lines)
- SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/ (ls — slot types + counts)
- atoms/gen_z_professionals/anxiety/ (ls — persona atom pool)
- registry/anxiety.yaml (first 40 lines — registry content for comparison)
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

Emit a STARTUP_RECEIPT then execute.

TASK: Merge PR #373 (BeatmapCompile), then build EnrichmentSelect,
wire into ChapterCompose, run 3 pilot books end-to-end through the
new spine→knob→beatmap→enrichment→compose pipeline, and produce a
comparison evaluation against the current baseline.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline

───────────────────────────────────────────────────────────────────────

PHASE 1: MERGE PR #373

  gh pr view 373 --json state,mergeStateStatus
  gh pr merge 373 --squash --admin

  # Also merge #371 (contract doc) if still open
  gh pr view 371 --json state 2>/dev/null
  # If open: gh pr merge 371 --squash --admin

  # Also merge #372 (knob apply implementation) if still open
  gh pr view 372 --json state 2>/dev/null
  # If open: gh pr merge 372 --squash --admin

  git checkout main && git pull origin main

  # Verify the full planning stack is on main
  ls phoenix_v4/planning/knob_apply.py && echo "KnobApply: ON MAIN"
  ls phoenix_v4/planning/beatmap_compile.py && echo "BeatmapCompile: ON MAIN"

  # Cleanup branches
  git push origin --delete agent/knob-apply-implementation 2>/dev/null
  git push origin --delete agent/knob-apply-contract 2>/dev/null
  git push origin --delete agent/beatmap-compile 2>/dev/null

───────────────────────────────────────────────────────────────────────

PHASE 2: BUILD ENRICHMENT SELECT

  The pipeline so far:
    SpineSelect → KnobApply → BeatmapCompile → **EnrichmentSelect** → ChapterCompose

  BeatmapCompile produces a Beatmap with:
    - Per-chapter slot list (BeatmapSlot with type, weight, target_words)
    - Atom selection criteria per slot (topic, engine, temperature, phase)
    - Enrichment hooks per slot (what overlays are recommended)

  EnrichmentSelect fills those slots with ACTUAL CONTENT from:
    1. Teacher atom banks (SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms/)
    2. Persona atom pools (atoms/{persona}/{topic}/)
    3. Registry variants (registry/{topic}.yaml)
    4. Practice library fallback (library_34)

  Create: phoenix_v4/planning/enrichment_select.py

  ─── INPUT ───

  ```python
  @dataclass
  class EnrichmentRequest:
      beatmap: Beatmap                    # from beatmap_compile
      teacher_id: Optional[str]           # Ahjan, Joshin, etc.
      persona_id: str                     # gen_z_professionals, etc.
      topic_id: str                       # anxiety, grief, etc.
      seed: str                           # deterministic selection seed
  ```

  ─── OUTPUT ───

  ```python
  @dataclass
  class EnrichedSlot:
      slot_type: str                      # HOOK, SCENE, STORY, etc.
      content: str                        # THE ACTUAL PROSE TEXT
      source: str                         # "teacher_atom", "persona_atom", "registry", "practice_library"
      source_id: str                      # atom_id or variant_id
      target_words: int                   # from beatmap
      actual_words: int                   # len(content.split())
      enrichment_applied: List[str]       # which enrichment hooks fired

  @dataclass
  class EnrichedChapter:
      number: int
      role: str                           # immutable from spine
      working_title: str                  # immutable from spine
      thesis: str                         # immutable from spine
      slots: List[EnrichedSlot]
      total_words: int
      source_breakdown: Dict[str, int]    # {"teacher_atom": 3, "registry": 4, ...}

  @dataclass
  class EnrichedBook:
      schema_version: int
      stage: str                          # "enrichment_select"
      topic: str
      teacher_id: Optional[str]
      persona_id: str
      runtime_format: str
      chapters: List[EnrichedChapter]
      total_words: int
      enrichment_audit: Dict[str, Any]
  ```

  ─── LOGIC: select_enrichment() ───

  ```python
  def select_enrichment(
      request: EnrichmentRequest,
      repo_root: Optional[Path] = None,
  ) -> EnrichedBook:
  ```

  FOR EACH BeatmapChapter, FOR EACH BeatmapSlot:

    SELECTION WATERFALL (same priority as registry_resolver.py):

    PRIORITY 1: Teacher atoms (if teacher_id provided)
      Look in SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/approved_atoms/{SLOT_TYPE}/
      Select deterministically via seed hash.
      Teacher atoms overlay: HOOK, EXERCISE, INTEGRATION, PIVOT,
        PERMISSION, TAKEAWAY, THREAD, TEACHER_DOCTRINE

    PRIORITY 2: Persona atoms (always checked)
      Look in atoms/{persona_id}/{topic_id}/{SLOT_TYPE}/ or engine dirs
      Persona atoms overlay: HOOK, SCENE, STORY

    PRIORITY 3: Registry variants
      Look in registry/{topic_id}.yaml for this chapter + section
      Select one variant deterministically via seed hash.
      This is the BASE content if no teacher/persona atoms exist.

    PRIORITY 4: Practice library fallback (EXERCISE only)
      If EXERCISE slot has no content from above, use
      practice_library_loader.get_exercise_for_chapter()
      Log a WARNING when this fires.

    PRIORITY 5: Empty slot
      If nothing found for this slot → log ERROR, set content to
      "[CONTENT GAP: {slot_type} for {topic} ch{number}]"
      This makes gaps visible instead of silently skipping.

    AFTER SELECTION:
      Record which source provided the content.
      Count actual words vs target words.
      Note which enrichment hooks from the beatmap actually fired.

  AFTER ALL CHAPTERS:
    Build enrichment_audit:
      - total_slots
      - slots_from_teacher: N
      - slots_from_persona: N
      - slots_from_registry: N
      - slots_from_practice_library: N (with WARNING count)
      - slots_empty: N (with ERROR — these are gaps)
      - total_words vs total_target_words

───────────────────────────────────────────────────────────────────────

PHASE 3: WIRE INTO CHAPTER COMPOSE

  ChapterCompose (phoenix_v4/rendering/chapter_composer.py) currently
  receives raw slot content and renders prose. We need it to accept
  an EnrichedBook and render from there.

  ADD a new entry point (don't break the existing one):

  ```python
  def compose_from_enriched_book(
      enriched: EnrichedBook,
      quality_profile: str = "draft",
  ) -> str:
      """
      Render an EnrichedBook to prose text.

      This is the new pipeline path:
        Spine → Knobs → Beatmap → Enrichment → THIS → BookRender

      The old path (assembly_compiler → chapter_composer) still works
      for backward compatibility.
      """
      chapters_prose = []
      for ch in enriched.chapters:
          chapter_text = f"Chapter {ch.number}\n{ch.working_title}\n\n"
          for slot in ch.slots:
              if slot.content and not slot.content.startswith("[CONTENT GAP"):
                  chapter_text += slot.content + "\n\n"
          chapters_prose.append(chapter_text)

      return "\n\n".join(chapters_prose)
  ```

  This is INTENTIONALLY simple for the pilot. Full compose logic
  (exercise wrapping, aha/integration standards, bridge templates)
  gets wired in a follow-up. For now: content → prose, no fancy assembly.

───────────────────────────────────────────────────────────────────────

PHASE 4: BUILD THE PILOT RUNNER

  Create scripts/pilot/run_spine_pipeline.py

  This is a STANDALONE script that runs the full new pipeline for
  one book, without touching run_pipeline.py.

  ```
  PYTHONPATH=. python3 scripts/pilot/run_spine_pipeline.py \
    --topic anxiety \
    --persona gen_z_professionals \
    --teacher ahjan \
    --format standard_book \
    --output-dir artifacts/pilot/anxiety_spine/
  ```

  LOGIC:
    1. Load spine: load_spine(topic)
    2. Load knob profile: load_knob_profile(topic)
    3. Apply knobs: apply_knobs(spine, knobs, runtime_format)
    4. Compile beatmap: compile_beatmap(shaped_spine, engines, format_spec)
    5. Select enrichment: select_enrichment(EnrichmentRequest(beatmap, teacher, persona, topic, seed))
    6. Compose prose: compose_from_enriched_book(enriched_book)
    7. Write outputs:
       - book.txt (full prose)
       - book_plan.json (enriched book as JSON)
       - enrichment_audit.json (source breakdown)
       - budget.json (word counts per chapter)

───────────────────────────────────────────────────────────────────────

PHASE 5: RUN 3 PILOT BOOKS

  For each of: anxiety, grief, burnout

  Run TWO versions:

  VERSION A: New pipeline (spine → knobs → beatmap → enrichment → compose)
    PYTHONPATH=. python3 scripts/pilot/run_spine_pipeline.py \
      --topic anxiety --persona gen_z_professionals --teacher ahjan \
      --format standard_book \
      --output-dir artifacts/pilot/anxiety_new/

  VERSION B: Current pipeline (registry fast-path)
    python3 scripts/run_pipeline.py \
      --topic anxiety --persona gen_z_professionals \
      --arc $(ls config/source_of_truth/master_arcs/gen_z_professionals__anxiety__* | head -1) \
      --render-book --quality-profile draft \
      --render-dir artifacts/pilot/anxiety_baseline/ \
      --out artifacts/pilot/anxiety_baseline/book.plan.json \
      --no-job-check

  Repeat for grief and burnout.

  Total: 6 books (3 new pipeline + 3 baseline).

───────────────────────────────────────────────────────────────────────

PHASE 6: EVALUATION COMPARISON

  For each pair (new vs baseline), compare:

  ```python
  for topic in ['anxiety', 'grief', 'burnout']:
      new_path = f'artifacts/pilot/{topic}_new/book.txt'
      old_path = f'artifacts/pilot/{topic}_baseline/book.txt'

      new_words = len(open(new_path).read().split())
      old_words = len(open(old_path).read().split())

      # Read enrichment audit for new pipeline
      audit = json.load(open(f'artifacts/pilot/{topic}_new/enrichment_audit.json'))

      print(f'{topic}:')
      print(f'  NEW: {new_words} words')
      print(f'  OLD: {old_words} words')
      print(f'  Delta: {new_words - old_words} words ({((new_words/old_words)-1)*100:.0f}%)')
      print(f'  Sources: teacher={audit["slots_from_teacher"]}, '
            f'persona={audit["slots_from_persona"]}, '
            f'registry={audit["slots_from_registry"]}, '
            f'fallback={audit["slots_from_practice_library"]}, '
            f'empty={audit["slots_empty"]}')
  ```

  Produce: artifacts/pilot/PIPELINE_COMPARISON_REPORT.md

  ## Pipeline Comparison — Spine+Knob+Beatmap vs Registry Fast-Path

  ### Per-Topic Results
  | Topic | New Words | Old Words | Delta | Teacher Atoms Used | Persona Atoms | Registry | Fallback | Gaps |
  ...

  ### Content Quality Assessment
  For each topic, manually read the FIRST CHAPTER of both versions:
    - Which opens stronger? (recognition hook quality)
    - Which has more specific language? (body parts, behaviors, not abstractions)
    - Which has better exercise sections? (time + body part + completion marker)
    - Which has better flow? (chapters feel connected vs isolated)

  ### Enrichment Analysis
  - What percentage of slots got teacher atoms vs registry defaults?
  - Are teacher atoms LONGER than registry variants? (expected: yes)
  - Are persona atoms adding locale/demographic specificity? (expected: yes)
  - How many slots fell to practice library fallback? (target: <10%)
  - How many slots were EMPTY? (target: 0)

  ### Architecture Assessment
  - Does the new pipeline produce MEANINGFULLY DIFFERENT books per topic?
  - Does the knob system create visible differences (grief vs anxiety feel different)?
  - Is the beatmap allocating words proportionally to section weights?
  - Does the enrichment waterfall fire in the correct priority order?

  ### Recommendations
  - What's working — keep
  - What's broken — fix before wider rollout
  - What's the next improvement with highest impact
  - Is this ready to replace the registry fast-path? (yes/no + conditions)

───────────────────────────────────────────────────────────────────────

GIT WORKFLOW:

  After merging #373 (+#371, +#372 if open):

  git fetch origin && git checkout -b agent/enrichment-pilot origin/main
  Commits:
    a) "feat: EnrichmentSelect — fill beatmap slots from teacher/persona/registry atoms"
    b) "feat: compose_from_enriched_book() — new pipeline prose renderer"
    c) "feat: pilot runner script (spine → knobs → beatmap → enrichment → compose)"
    d) "feat: 3 pilot books (anxiety + grief + burnout) — new vs baseline"
    e) "docs: pipeline comparison report — new spine pipeline vs registry fast-path"
  Run preflight, push, PR against main.

WRITE_SCOPE:
  phoenix_v4/planning/enrichment_select.py (NEW)
  phoenix_v4/rendering/chapter_composer.py (UPDATE — add compose_from_enriched_book)
  scripts/pilot/run_spine_pipeline.py (NEW)
  tests/test_enrichment_select.py (NEW — ≥15 tests)
  artifacts/pilot/ (NEW — 6 books + comparison report)
  artifacts/pilot/PIPELINE_COMPARISON_REPORT.md (NEW)
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (add workstream)

OUT_OF_SCOPE: Modifying run_pipeline.py (don't wire into main pipeline yet);
modifying registry_resolver.py; modifying assembly_compiler.py;
full ChapterCompose integration (pilot uses simple prose concat);
EI v2 scoring (comparison is manual for pilot); production runs

NON-NEGOTIABLE:
  Merge #373 (+ #371, #372) BEFORE building EnrichmentSelect.
  EnrichmentSelect uses the SAME priority waterfall as registry_resolver.py:
    teacher > persona > registry > practice library > empty gap marker.
  Content gaps are VISIBLE ("[CONTENT GAP: ...]"), not silently skipped.
  Practice library fallback logs a WARNING every time it fires.
  compose_from_enriched_book() is ADDITIVE — do not break existing compose path.
  The pilot runner is STANDALONE — does not modify or depend on run_pipeline.py.
  ALL 3 topics must produce books. If one fails, document why and continue.
  Comparison report must be HONEST — if new pipeline is worse, say so.
  English prose from Pearl_Writer subagents. Qwen = CJK only.
  15+ tests for EnrichmentSelect, all passing.
  Check `gh pr diff <number> --stat | tail -1` before merging.
  If deletions > 50 files, STOP and ask the owner.


---

**Cursor**

Reading the required files and gathering repository state, then emitting STARTUP_RECEIPT and executing the phases.



Emitting STARTUP_RECEIPT, then merging PR #373 (4 files changed; safe). Implementing EnrichmentSelect using registry_resolver's waterfall: for EXERCISE, try practice library before the registry default.



Implementing `enrichment_select.py`, updating `chapter_composer.py`, adding the pilot script and tests.



```
STARTUP_RECEIPT
AGENT:              Pearl_GitHub + Pearl_Dev + Pearl_Writer
TASK:               Merge PR #373; build EnrichmentSelect; wire compose; run 3-topic pilots; compare to baseline; push PR
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md;docs/PEARL_ARCHITECT_STATE.md;docs/KNOB_APPLY_STAGE_CONTRACT.md;docs/DOCS_INDEX.md (via SESSION_UNITY minimum set);artifacts/coordination/ACTIVE_PROJECTS.tsv;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv;specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md (subsystem map);specs/PHOENIX_V4_5_WRITER_SPEC.md (subsystem map)
READ_PATH_COMPLETE: yes (required planning/rendering/exercise/run_pipeline slices + configs listed in task; `config/spines/*` and `config/knobs/topic_knob_profiles.yaml` are not present in this workspace — `load_spine` / `load_knob_profile` resolve via `tests/fixtures/knob_apply/`)
WRITE_SCOPE:        phoenix_v4/planning/enrichment_select.py;phoenix_v4/rendering/chapter_composer.py;scripts/pilot/run_spine_pipeline.py;tests/test_enrichment_select.py;artifacts/pilot/**;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       run_pipeline.py;registry_resolver.py;assembly_compiler.py;production wiring;EI v2 scoring
BLOCKERS:           none (local `main` is bound to another worktree — used `origin/main` via `agent/enrichment-pilot`; unrelated untracked paths remain — health_check reports noise but push_guard/preflight passed)
READY_STATUS:       ready
```

### Execution summary

**Phase 1 — merges**  
- Checked PR **#373**: 4 files changed, line deletions only (not >50 files). **`gh pr merge 373 --squash --admin`** succeeded.  
- **#371** and **#372**: already **MERGED**.  
- Remote **`agent/beatmap-compile`** deleted successfully; **`agent/knob-apply-*`** remotes did not exist (already removed or different names).

**Phase 2–4 — implementation**  
- Added [`phoenix_v4/planning/enrichment_select.py`](phoenix_v4/planning/enrichment_select.py): `EnrichmentRequest`, `select_enrichment()`, JSON/budget helpers. Waterfall matches **`registry_resolver.resolve_book`** (including **practice library before registry** for `EXERCISE`, with warnings from `get_exercise_for_chapter`). Gaps → `[CONTENT GAP: …]` + `ERROR` log.  
- Added [`compose_from_enriched_book()`](phoenix_v4/rendering/chapter_composer.py) at the end of [`phoenix_v4/rendering/chapter_composer.py`](phoenix_v4/rendering/chapter_composer.py) (additive; skips gap lines).  
- Added [`scripts/pilot/run_spine_pipeline.py`](scripts/pilot/run_spine_pipeline.py) (fixed `mkdir(..., exist_ok=True)`).

**Tests**  
- [`tests/test_enrichment_select.py`](tests/test_enrichment_select.py): **18 passed** (`PYTHONPATH=. python3 -m pytest tests/test_enrichment_select.py -q`).

**Phase 5–6 — pilots + report**  
- New path: `artifacts/pilot/{anxiety,grief,burnout}_new/`.  
- Baseline: `artifacts/pilot/{anxiety,grief,burnout}_baseline/` via `run_pipeline.py` + registry.  
- Comparison: [`artifacts/pilot/PIPELINE_COMPARISON_REPORT.md`](artifacts/pilot/PIPELINE_COMPARISON_REPORT.md) — **honest verdict**: pilot is shorter (≈51 beatmap slots vs full registry section counts), placeholders like `{weather_detail}` leak in new output without `clean_for_delivery`, **not** ready to replace registry fast-path until full compose + delivery hygiene.

**Git**  
- Five commits on **`agent/enrichment-pilot`**, pushed; **PR #375**: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/375  
- **`HEAD` / last doc commit SHA:** `4dde6cfd5498a2147f07704ecaaf7654463b8069`

**Workstreams**  
- [`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`](artifacts/coordination/ACTIVE_WORKSTREAMS.tsv): **`ws_beatmap_compile_20260410`** → completed (PR #373); added **`ws_enrichment_pilot_20260410`** → completed.

---

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_GitHub + Pearl_Dev + Pearl_Writer
TASK:           EnrichmentSelect pilot + PR #373 merge + comparison
COMMIT_SHA:     4dde6cfd5498a2147f07704ecaaf7654463b8069
FILES_WRITTEN:  phoenix_v4/planning/enrichment_select.py;phoenix_v4/rendering/chapter_composer.py;scripts/pilot/run_spine_pipeline.py;tests/test_enrichment_select.py;artifacts/pilot/**;artifacts/pilot/PIPELINE_COMPARISON_REPORT.md;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md;docs/PEARL_ARCHITECT_STATE.md;docs/KNOB_APPLY_STAGE_CONTRACT.md;planning/rendering/registry/run_pipeline slices per task;ACTIVE_* TSV;SUBSYSTEM_AUTHORITY_MAP.tsv
STATUS:         completed
HANDOFF_TO:     owner (merge PR #375 when satisfied)
NEXT_ACTION:    Review PR #375; merge to main; optionally run `clean_for_delivery` on pilot `book.txt` and plan full `compose_chapter_prose` wiring as report recommends
```

