# Knob apply implementation and beatmap compile
_Exported on 4/16/2026 at 19:32:13 GMT+8 from Cursor (3.1.15)_

---

**User**

Act as Pearl_GitHub + Pearl_Dev for Phoenix Omega.

Read these files before doing any work:

- docs/SESSION_UNITY_PROTOCOL.md
- docs/GITHUB_OPERATIONS_FRAMEWORK.md
- docs/KNOB_APPLY_STAGE_CONTRACT.md (if exists — check both main and PR #371)
- phoenix_v4/planning/knob_apply.py (FULL — the implementation from PR #372)
- tests/test_knob_apply.py (from PR #372)
- config/knobs/topic_knob_profiles.yaml (first 60 lines)
- config/spines/anxiety_spine.yaml (first 40 lines)
- config/format_selection/format_registry.yaml (FULL — runtime formats)
- config/pipeline_registry.yaml
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

Emit a STARTUP_RECEIPT then execute.

TASK: Merge PR #372 (knob apply implementation) and PR #371 (contract),
reconcile docs with code, then implement the BeatmapCompile stage that
consumes ShapedSpine output from knob_apply.py.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline

───────────────────────────────────────────────────────────────────────

PHASE 1: MERGE #372 AND #371

  # Check both PRs
  gh pr view 372 --json state,mergeStateStatus,files
  gh pr view 371 --json state,mergeStateStatus,files

  # PR #372 — knob apply implementation (code + tests)
  # Merge first since it has the working code
  gh pr merge 372 --squash --admin

  # PR #371 — knob apply contract (docs + dataclass signatures)
  # Check if it conflicts with #372 (both touch similar files)
  # If DIRTY → rebase onto post-#372 main, resolve conflicts
  # If clean → merge
  gh pr merge 371 --squash --admin

  # If #371 conflicts:
  git fetch origin
  git checkout agent/knob-apply-contract
  git rebase origin/main
  # Keep #372's implementation, add #371's docs
  git push --force-with-lease
  gh pr merge 371 --squash --admin

  # Pull main
  git checkout main && git pull origin main

  # Verify both are on main
  ls phoenix_v4/planning/knob_apply.py && echo "Implementation: ON MAIN"
  ls docs/KNOB_APPLY_STAGE_CONTRACT.md 2>/dev/null && echo "Contract doc: ON MAIN" || echo "Contract doc: MISSING — reconcile needed"

  # Cleanup
  git push origin --delete agent/knob-apply-implementation 2>/dev/null
  git push origin --delete agent/knob-apply-contract 2>/dev/null

───────────────────────────────────────────────────────────────────────

PHASE 2: RECONCILE DOCS WITH CODE

  If docs/KNOB_APPLY_STAGE_CONTRACT.md is NOT on main after merging:
    Extract it from #371 branch or recreate from the implementation.

  The contract doc must match the actual code. Verify:
    - SelectedSpine dataclass fields match doc schema
    - KnobProfile dataclass fields match doc schema
    - ShapedSpine dataclass fields match doc schema
    - Merge priority order in doc matches code logic
    - Dangerous combo resolution in doc matches code behavior

  If any mismatch: update the DOC to match the CODE (code is truth
  since it has passing tests).

───────────────────────────────────────────────────────────────────────

PHASE 3: IMPLEMENT BEATMAP COMPILE

  The pipeline architecture:
    SpineSelect → KnobApply → **BeatmapCompile** → EnrichmentSelect → ...

  KnobApply produces a ShapedSpine with per-chapter:
    - shaped_section_weights (float per section type)
    - emotional_temperature
    - pacing
    - target_word_count
    - phase (early/mid/late)
    - compression_allowed
    - enrichment_priority

  BeatmapCompile turns this into a CONCRETE execution plan:
    - slot_definitions per chapter (the actual [HOOK, SCENE, STORY, ...] list)
    - word budget per slot
    - atom selection criteria per slot
    - enrichment hooks per slot

  Create: phoenix_v4/planning/beatmap_compile.py

  ─── INPUT: ShapedSpine ───

  From phoenix_v4/planning/knob_apply.py:
    ShapedSpine with ShapedChapter list

  ─── OUTPUT: Beatmap ───

  ```python
  @dataclass
  class BeatmapSlot:
      slot_type: str                    # HOOK, SCENE, STORY, REFLECTION, etc.
      weight: float                     # from shaped_section_weights
      target_words: int                 # derived from chapter word budget × weight
      atom_selection_criteria: Dict[str, Any]  # topic, persona, engine constraints
      enrichment_hooks: List[str]       # what enrichments can overlay this slot
      emotional_temperature: str        # inherited from shaped chapter
      is_required: bool                 # from spine required_sections

  @dataclass
  class BeatmapChapter:
      number: int
      role: str                         # from spine (immutable)
      working_title: str                # from spine (immutable)
      thesis: str                       # from spine (immutable)
      phase: str                        # from shaped spine
      target_word_count: int            # from shaped spine
      slots: List[BeatmapSlot]          # THE CONCRETE SLOT LIST
      slot_definitions: List[str]       # simplified: ["HOOK", "SCENE", "STORY", ...]

  @dataclass
  class Beatmap:
      schema_version: int
      stage: str                        # always "beatmap_compile"
      topic: str
      family_id: str
      runtime_format: str
      total_target_words: int
      chapters: List[BeatmapChapter]
      compile_audit: Dict[str, Any]     # decisions made during compilation
  ```

  ─── LOGIC: compile_beatmap() ───

  ```python
  def compile_beatmap(
      shaped_spine: ShapedSpine,
      topic_engines: Dict[str, Any],    # from topic_engine_bindings.yaml
      format_spec: Dict[str, Any],      # from format_registry.yaml
  ) -> Beatmap:
  ```

  FOR EACH ShapedChapter in the ShapedSpine:

    STEP 1: Determine which sections appear in this chapter

      Read shaped_section_weights. For each section type:
        weight > 0.0 → include in slot_definitions
        weight == 0.0 → exclude (knob zeroed it out)

      BUT: if a section is in the spine's required_sections AND weight is 0:
        → this is a VALIDATION ERROR (KnobApply should have caught this)
        → log warning and include it anyway with weight 0.3 (minimum)

      ALSO: check the spine's forbidden_moves for this chapter.
        If a slot type would violate a forbidden move → exclude it.
        Example: ch1 says "no exercise yet" → even if EXERCISE weight > 0,
        skip it for this chapter.

    STEP 2: Order the sections

      Use the canonical slot order from format_registry.yaml:
        default: [HOOK, SCENE, STORY, REFLECTION, COMPRESSION, EXERCISE, INTEGRATION]
        F006 variant: [HOOK, SCENE, STORY, REFLECTION, COMPRESSION, EXERCISE, INTEGRATION]

      Filter to only included sections from Step 1.
      Maintain canonical order (don't randomize).

    STEP 3: Allocate word budget per slot

      chapter_word_target from shaped_spine (e.g., 833 words for standard_book/12 chapters)

      Distribute proportional to weights:
        total_weight = sum(weight for each included slot)
        per_slot_words = (weight / total_weight) * chapter_word_target

      Enforce minimums:
        HOOK: minimum 100 words (always needs a strong opening)
        EXERCISE: minimum 80 words (if included — must be specific)
        INTEGRATION: minimum 60 words
        Others: minimum 50 words

    STEP 4: Set atom selection criteria per slot

      For each slot, define what the enrichment layer should look for:

      ```python
      atom_selection_criteria = {
          "topic": shaped_spine.topic,
          "persona": None,                # filled by EnrichmentSelect
          "engine": topic_engines.get("allowed_engines", [])[0],
          "slot_type": slot_type,
          "emotional_temperature": chapter.emotional_temperature,
          "phase": chapter.phase,
          "chapter_role": chapter.role,
      }
      ```

    STEP 5: Set enrichment hooks

      From the shaped chapter's enrichment_priority:
        Map to slot types:
          "persona_alarm_behavior" → applies to HOOK and SCENE slots
          "teacher_voice" → applies to REFLECTION and INTEGRATION slots
          "somatic_exercise" → applies to EXERCISE slots
          "story_vividness" → applies to STORY slots

    STEP 6: Build BeatmapChapter

  AFTER ALL CHAPTERS:

    Validate total word count: sum of all chapter targets should be
    within runtime_format word_range ±10%.

    Build compile_audit:
      - sections_included_total
      - sections_excluded_total (with reasons)
      - word_budget_total
      - forbidden_moves_applied
      - minimum_word_overrides (where minimum was enforced)

───────────────────────────────────────────────────────────────────────

PHASE 4: TEST SUITE

  tests/test_beatmap_compile.py

  TEST GROUP 1: Basic compilation
    test_compile_anxiety_standard — 12 chapters, each with slots
    test_compile_grief_standard — 12 chapters
    test_compile_burnout_standard — 12 chapters
    test_all_chapters_have_slots — no empty slot lists
    test_slot_definitions_match_slots — simplified list matches full slots

  TEST GROUP 2: Section inclusion/exclusion
    test_exercise_excluded_when_weight_zero — ch1 anxiety has no EXERCISE
    test_required_section_survives_zero_weight — minimum 0.3 enforced
    test_forbidden_move_excludes_section — spine forbidden_moves respected

  TEST GROUP 3: Word budget allocation
    test_word_budget_proportional_to_weights — higher weight = more words
    test_hook_minimum_100_words — never below 100
    test_exercise_minimum_80_words — never below 80
    test_total_words_within_format_range — ±10% of runtime_format

  TEST GROUP 4: Slot ordering
    test_canonical_slot_order — HOOK before SCENE before STORY before REFLECTION
    test_no_random_ordering — deterministic output

  TEST GROUP 5: Enrichment hooks
    test_enrichment_hooks_mapped_to_slots — correct slot types
    test_teacher_voice_on_reflection — teacher enrichment on right slots
    test_exercise_enrichment_on_exercise — somatic enrichment mapped

  TEST GROUP 6: Audit trail
    test_audit_records_exclusions — excluded sections logged
    test_audit_records_minimum_overrides — minimum word enforcements logged
    test_audit_total_words_accurate — matches sum of chapter targets

  TEST GROUP 7: End-to-end (knob_apply → beatmap_compile)
    test_anxiety_full_pipeline — load_spine → apply_knobs → compile_beatmap
    test_grief_full_pipeline — same chain
    test_burnout_full_pipeline — same chain
    test_output_chapters_match_input — same count, same roles, same titles

  TARGET: ≥20 tests, all passing.

───────────────────────────────────────────────────────────────────────

PHASE 5: VERIFY ON 3 TOPICS (full chain)

  python3 -c "
  from phoenix_v4.planning.knob_apply import load_spine, load_knob_profile, apply_knobs
  from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_topic_engines, load_format_spec
  import json

  for topic in ['anxiety', 'grief', 'burnout']:
      spine = load_spine(topic)
      knobs = load_knob_profile(topic)
      shaped = apply_knobs(spine, knobs, runtime_format='standard_book')
      engines = load_topic_engines(topic)
      fmt = load_format_spec('standard_book')
      beatmap = compile_beatmap(shaped, engines, fmt)

      print(f'{topic}:')
      print(f'  chapters: {len(beatmap.chapters)}')
      print(f'  total slots: {sum(len(ch.slots) for ch in beatmap.chapters)}')
      print(f'  total words: {beatmap.total_target_words}')
      for ch in beatmap.chapters[:3]:
          print(f'  ch{ch.number}: {ch.slot_definitions} → {ch.target_word_count}w')
      print()
  "

  EXPECTED:
    anxiety: ~12 chapters, 60-84 slots, ~10000 words total
    grief: different slot distribution (fewer EXERCISE, more REFLECTION)
    burnout: different again

  The 3 beatmaps must be MEANINGFULLY DIFFERENT.

───────────────────────────────────────────────────────────────────────

GIT WORKFLOW:

  After merging #372 + #371:

  git fetch origin && git checkout -b agent/beatmap-compile origin/main
  Commits:
    a) "feat: BeatmapCompile dataclasses (BeatmapSlot, BeatmapChapter, Beatmap)"
    b) "feat: compile_beatmap() — ShapedSpine → concrete slot definitions"
    c) "feat: word budget allocation + enrichment hook mapping"
    d) "test: beatmap compile test suite (20+ tests on anxiety/grief/burnout)"
    e) "feat: end-to-end chain verification (spine → knobs → beatmap)"
  Run preflight, push, PR against main.

WRITE_SCOPE:
  phoenix_v4/planning/beatmap_compile.py (NEW)
  tests/test_beatmap_compile.py (NEW)
  docs/KNOB_APPLY_STAGE_CONTRACT.md (UPDATE if needed — reconcile with code)
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (add workstream)

OUT_OF_SCOPE: Pipeline wiring (do NOT touch run_pipeline.py);
EnrichmentSelect (next stage, separate PR); ChapterCompose;
BookRender; registry edits; spine edits; knob profile edits

NON-NEGOTIABLE:
  Merge #372 FIRST. Then #371. Then reconcile docs. Then build BeatmapCompile.
  BeatmapCompile consumes ShapedSpine — NOT raw spines or registries.
  Spine thesis, role, working_title remain IMMUTABLE through BeatmapCompile.
  Section order follows format_registry.yaml canonical order.
  Word budget respects minimums (HOOK ≥100, EXERCISE ≥80, INTEGRATION ≥60).
  Forbidden moves from spine are ENFORCED — override section weights.
  Required sections from spine cannot be zeroed — minimum 0.3 weight.
  Total word count within runtime_format ±10%.
  The beatmap is the CONCRETE execution plan — no ambiguity in output.
  Test on all 3 topics — outputs must be meaningfully different.
  20+ tests, all passing.
  No external API calls. Pure Python, stdlib + yaml.
  Check `gh pr diff <number> --stat | tail -1` before merging.
  If deletions > 50 files, STOP and ask the owner.


---

**Cursor**

Reading required files, checking PR state and the repo, then executing the phased plan.



Locating config paths and checking GitHub PR state. Emitting STARTUP_RECEIPT and continuing investigation.



Checking PR diff stats for mass-deletion safety, then merging PRs.



Emitting STARTUP_RECEIPT and merging PRs #372 and #371 (0 deletions — safe).



Rebasing PR #371 onto updated main to resolve merge conflicts.



Verifying main contents and reconciling the contract with `knob_apply.py`.



Updating the contract doc to match the implementation, then implementing `beatmap_compile.py` and tests. Checking fixture spines for test scenarios:



Implementing `beatmap_compile.py` and updating the contract documentation to match the implementation.



Tightening forbidden-move detection: broad matching treated grief ch9's "Do not frame the practice..." as banning EXERCISE. Matching only lines that forbid introducing practice/exercise.



Writing the test suite.



Updating the contract document to match the implementation: replacing inaccurate schema sections.



```
STARTUP_RECEIPT
AGENT:              Pearl_GitHub + Pearl_Dev
TASK:               Merge PRs #372/#371, reconcile knob contract docs, implement BeatmapCompile + tests + PR
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/DOCS_INDEX.md (via SESSION_UNITY); artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; specs/PHOENIX_V4_5_WRITER_SPEC.md (authority map)
READ_PATH_COMPLETE: yes (required protocol + framework + configs + knob_apply/tests/fixtures + format_registry + pipeline_registry + ACTIVE_WORKSTREAMS)
WRITE_SCOPE:        phoenix_v4/planning/beatmap_compile.py; tests/test_beatmap_compile.py; docs/KNOB_APPLY_STAGE_CONTRACT.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       run_pipeline.py; EnrichmentSelect; spine/knob/registry edits; knob_apply_contract.py body
BLOCKERS:           Local `main` checkout blocked by another worktree at `/private/tmp/pearl_github_rebase` (work continued on `agent/beatmap-compile` from `origin/main`)
READY_STATUS:       ready
```

### Executed

**PR merges (GitHub)**  
- [PR #372](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/372) — squash-merged first (`gh pr view 372` showed **0 deletions**).  
- [PR #371](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/371) — was **CONFLICTING**; rebased `agent/knob-apply-contract` onto `origin/main`, resolved `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, force-pushed, then squash-merged.  
- Remote branches `agent/knob-apply-implementation` and `agent/knob-apply-contract` deleted after merge.

**BeatmapCompile** — new module `phoenix_v4/planning/beatmap_compile.py`:  
- `Beatmap` / `BeatmapChapter` / `BeatmapSlot` dataclasses, `compile_beatmap()`, `load_format_spec()` (adds `canonical_slot_order` from F006 / fallbacks), `load_topic_engines()`, `beatmap_to_jsonable()`.  
- Loads spine via `load_spine(shaped.topic)` for `required_sections`, `forbidden_moves`, and `is_required`.  
- Forbidden practice lines narrowed so real practice chapters (e.g. grief ch9 “Do not **frame** the practice…”) are not misclassified as banning the EXERCISE slot.  
- Word floors: HOOK ≥100, EXERCISE ≥80, INTEGRATION ≥60, others ≥50; total book words checked against runtime midpoint ±10%.

**Tests** — `tests/test_beatmap_compile.py` (**30** tests); `tests/test_knob_apply.py` unchanged; **67** tests green together.

**Docs** — `docs/KNOB_APPLY_STAGE_CONTRACT.md` rewritten to match **`knob_apply.py`** (dataclasses, phase=`early`/`mid`/`late`, `pacing`, `knob_snapshot`, merge/repair order, `KnobAudit` fields) and to describe **BeatmapCompile** in §7.

**Coordination** — `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`: knob PRs marked completed, `ws_beatmap_compile_20260410` added as active.

**PR opened** — [PR #373](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/373) (`agent/beatmap-compile` → `main`). Stats: **4 files**, **355 deletions** (mostly contract doc trim), **842 additions**.

**Verification (3 topics)** — anxiety: **51** slots / **9996** words; grief: **49**; burnout: **48**; exercise-slot counts **3 / 1 / 0** respectively (distinct).

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_GitHub + Pearl_Dev
TASK:           Merge #372/#371, reconcile knob contract, BeatmapCompile + tests + PR
COMMIT_SHA:     9265d51bf1 (branch tip agent/beatmap-compile); main includes 372+371 merges at 46c98a7c71 area before this branch
FILES_WRITTEN:  phoenix_v4/planning/beatmap_compile.py; tests/test_beatmap_compile.py; docs/KNOB_APPLY_STAGE_CONTRACT.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; specs/PHOENIX_V4_5_WRITER_SPEC.md (via SUBSYSTEM_AUTHORITY_MAP); phoenix_v4/planning/knob_apply.py; tests/test_knob_apply.py; config/format_selection/format_registry.yaml; config/pipeline_registry.yaml; config/topic_engine_bindings.yaml; tests/fixtures/knob_apply/*
STATUS:         completed (PR #373 open for merge)
HANDOFF_TO:     owner / CI
NEXT_ACTION:    Merge PR #373 when checks pass; optional — resolve local main worktree lock if you need `git checkout main` on this clone
```

