# YAML and mechanism thesis structure
_Exported on 4/16/2026 at 19:19:54 GMT+8 from Cursor (3.1.15)_

---

**User**

continue with your requested implementation while leaving those untouched

You are Pearl_Dev. Read these files before any work:
1. docs/SESSION_UNITY_PROTOCOL.md
2. phoenix_v4/rendering/chapter_composer.py (957 lines — full file, focus on lines 74–123 _derive_thesis, 260–329 _distill_mechanism, 409–437 _fallback_takeaway/_fallback_thread, 440–466 _exercise_setup_sentence, and 570–796 compose_chapter_prose)
3. phoenix_v4/planning/chapter_planner.py (focus on ChapterContract at line 59, emotional_job values)
4. config/source_of_truth/chapter_purpose_contracts.yaml
5. tests/test_bestseller_craft_quality.py
6. artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
STARTUP_RECEIPT
AGENT:              Pearl_Dev
TASK:               Build mechanism/thesis delivery system + exercise wrapper system (two new YAML configs, refactor 5 functions, add memory)
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;specs/PHOENIX_V4_5_WRITER_SPEC.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/SESSION_UNITY_PROTOCOL.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        config/rendering/mechanism_thesis_families.yaml;config/rendering/exercise_wrapper_families.yaml;phoenix_v4/rendering/chapter_composer.py;tests/test_mechanism_thesis_system.py;tests/test_exercise_wrapper_system.py;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       atoms/;SOURCE_OF_TRUTH/;phoenix_v4/rendering/golden_chapter_synthesis.py;phoenix_v4/planning/chapter_planner.py;config/source_of_truth/chapter_purpose_contracts.yaml;scripts/localization/
BLOCKERS:           none
READY_STATUS:       ready
---
## PART 1 — Mechanism / Thesis Delivery System
### Problem
In `chapter_composer.py`, two functions produce highly patterned output:
**`_derive_thesis()` (line 74):** Contains 25 keyword→thesis mappings, ALL starting with "The point is that…". Plus 7 generic fallbacks, ALL starting with "The point is that…". Every thesis in every chapter starts the same way.
**`_distill_mechanism()` (line 260):** Contains 8 topic-specific mechanism paragraphs and 5 generic templates. The generic templates use a rotating set of wrappers:
- "Underneath the feeling is a simple mechanism: {core}…"
- "Here is the mechanism: {core}…"
- "The pattern underneath: {core}…"
- "What drives this: {core}…"
- "The core mechanism is this: {core}…"
**`_fallback_takeaway()` (line 409):** Uses a single template: "Remember this: {core} That is not a philosophy. That is what happened in this chapter."
**Critical gap:** `emotional_role` is already passed into `compose_chapter_prose()` (line 581) but is NEVER forwarded to `_derive_thesis()`, `_distill_mechanism()`, or `_fallback_takeaway()`. These functions only get thesis/reflection text, not the chapter's emotional job.
### What to build
#### A. Create `config/rendering/mechanism_thesis_families.yaml`
Two top-level sections: `thesis_families` and `mechanism_families`.
**Thesis delivery shapes (8):**
- `direct_thesis` — "The alarm fires on prediction, not evidence."
- `quiet_distillation` — "What feels immediate is often only the body trying not to be caught off guard."
- `reframe_sentence` — "What feels like proof is often only prediction wearing urgency."
- `contrast_claim` — "The feeling is real. The story attached to it may not be."
- `identity_shift_claim` — "You are not fragile. You are mobilized."
- `permission_inflected_claim` — "You are allowed to act before certainty arrives."
- `consequence_claim` — "That is why ordinary situations can feel expensive before anything has actually gone wrong."
- `compression_claim` — "The body has already decided the moment matters."
**Mechanism delivery shapes (9):**
- `causal_explanation` — "Once the nervous system marks a moment as dangerous, perception narrows toward confirming data."
- `systems_model` — "The system was built for physical threats. It now runs in offices and group chats."
- `body_model` — "The body responds to prediction with the same chemistry it uses for actual danger."
- `pattern_recognition` — "Seeing the pattern clearly does not stop it. But it lets you choose a different response."
- `cost_explanation` — "The cost is not the moment itself. It is how much energy the system spends predicting the moment."
- `reversal_explanation` — "What looks like self-protection is often the pattern protecting itself from examination."
- `implication_line` — "That means the body can mobilize before the facts arrive."
- `evidence_based_explanation` — "You can see it most clearly where it lands in an ordinary hour."
- `quiet_explanatory_compression` — "The mechanism is automatic. Understanding it does not stop it. But it changes what obedience costs."
**Organized by emotional_job (7 values):** recognition, mechanism, deepening, reframe, practice, integration, resolution.
**YAML structure:**
```yaml
schema_version: 1

thesis_families:
recognition:
direct_thesis:
- text: "The alarm fires on prediction, not evidence."
stems: ["alarm fires on prediction"]
roots: ["alarm", "prediction", "evidence"]
- text: "The body can react before the facts have had time to arrive."
stems: ["body can react before facts"]
roots: ["body", "facts"]
quiet_distillation:
- text: "..."
stems: [...]
roots: [...]
mechanism:
# ...different thesis shapes for mechanism chapters
deepening:
# ...more cost/inevitability oriented
reframe:
# ...reversal, "what seemed like X is actually Y"
practice:
# ...minimal, practical
integration:
# ...connective, less didactic
resolution:
# ...settled, spacious

mechanism_families:
recognition:
body_model:
- text: "..."
# ...immediate, legible mechanisms
mechanism:
causal_explanation:
- text: "..."
systems_model:
- text: "..."
# ...strongest system explanations
deepening:
cost_explanation:
- text: "..."
# ...consequence and burden focus
reframe:
reversal_explanation:
- text: "..."
# ...contrastive, anti-misinterpretation

...etc
**Minimum sizes:**
- Thesis: 50–80 total entries across emotional_jobs × shapes
- Mechanism: 60–100 total entries (including topic-specific families migrated from current code)
**Preserve topic-specific mechanism blocks:** The current regret/choice, comparison, alarm, shame, watcher, overwhelm, grief, spiral mechanism paragraphs (lines 263–313) are good domain content. Migrate them into the YAML as topic-specific entries under appropriate emotional_jobs, rather than deleting them. They should be reachable when both topic keywords AND emotional_job match.
#### B. Refactor `_derive_thesis()` (line 74)
New signature:
```python
def _derive_thesis(
reflection: str,
chapter_index: int = 0,
*,
emotional_job: str = "",
thesis_memory: "MechanismThesisMemory | None" = None,
) -> str:

When `emotional_job` is provided and YAML is loaded:
1. Look up thesis entries for this emotional_job
2. Score candidates (penalize: same stems/roots/shapes used recently; reward: emotional_job match, underused shapes)
3. Record selection in thesis_memory
When `emotional_job` is "" (backward compat): fall back to current keyword-matching behavior.
**Critical:** Thesis output must NOT always start with "The point is that…". The new system should produce varied thesis shapes. "The point is that…" can be ONE shape among many, not the default wrapper.
#### C. Refactor `_distill_mechanism()` (line 260)
New signature:
```python
def _distill_mechanism(
reflection: str,
thesis: str,
*,
emotional_job: str = "",
mechanism_memory: "MechanismThesisMemory | None" = None,
) -> str:

When `emotional_job` is provided:
1. Check topic-specific banks first (preserve regret/choice, comparison, alarm, etc. quality)
2. For generic mechanisms, use YAML families instead of the 5 rotating templates
3. Score candidates against memory
When `emotional_job` is "" (backward compat): fall back to current behavior.
#### D. Refactor `_fallback_takeaway()` (line 409)
New signature:
```python
def _fallback_takeaway(
thesis: str,
*,
emotional_job: str = "",
chapter_index: int = 0,
total_chapters: int = 1,
mechanism_memory: "MechanismThesisMemory | None" = None,
) -> str:

Add a takeaway_fallback section in the YAML with 15–25 varied templates. The current single "Remember this: {core}…" template should be one option, not the only option.
#### E. Add `MechanismThesisMemory` class
```python
class MechanismThesisMemory:
"""Tracks mechanism/thesis usage across chapters for anti-reuse."""

Tracks: exact phrases, stems, roots, shapes used. Rules:
- Exact phrase: max 1/book
- Same stem: max 1 per 4 chapters
- Same shape: max 2 in 3 adjacent chapters
- Ban stems: "The point is that" max 2/book total (not every chapter)
- Ban stems: "Here is the mechanism" / "The pattern underneath" / "What drives this" max 1 each/book
#### F. Wire emotional_role into the call chain
In `compose_chapter_prose()` (line 570), `emotional_role` param exists at line 581 but is never passed to thesis/mechanism functions. Fix these call sites:
- Line 624: `_derive_thesis(reflection_raw, chapter_index)` → add `emotional_job=emotional_role, thesis_memory=mechanism_memory`
- Line 641: `_distill_mechanism(reflection_raw, thesis)` → add `emotional_job=emotional_role, mechanism_memory=mechanism_memory`
- Line 774: `_fallback_takeaway(thesis)` → add `emotional_job=emotional_role, chapter_index=chapter_index, total_chapters=total_chapters, mechanism_memory=mechanism_memory`
Create the `MechanismThesisMemory` in `compose_from_enriched_book()` (line 799) at book render start and thread it through each chapter's `compose_chapter_prose()` call. Add a new parameter to `compose_chapter_prose()`:
```python
mechanism_memory: Optional["MechanismThesisMemory"] = None,

---
## PART 2 — Exercise Wrapper / Post-Exercise Validation System
### Problem
**`_exercise_setup_sentence()` (line 440):** Has 6 body-locus-specific returns and 10 generic fallbacks. All start with "Start with…" or "Begin with…" or "Find the part…" or "Notice where…" — same sentence shape every time.
**`_bridge_before_exercise()` (line 211):** 12 generic options, all some variant of "do not turn this into homework / understanding without practice is just information / the body needs something to do."
**`_bridge_before_integration()` (line 237):** 12 flat options, all some variant of "notice what shifted / stay with what changed / do not rush."
These wrapper layers repeat more visibly than the exercise content itself.
### What to build
#### A. Create `config/rendering/exercise_wrapper_families.yaml`
**Wrapper types (4):**
- `setup_sentence` — pre-practice body-location entry
- `pre_practice_bridge` — transition from story/reflection into exercise
- `post_practice_validation` — "what you just experienced is valid" language
- `pre_integration_transition` — exercise → integration bridge
**Practice-type buckets (9):**
- `breath_regulation`
- `grounding`
- `body_scan`
- `somatic_discharge`
- `visualization`
- `reflective_prompt`
- `attention_training`
- `vagus_stimulation`
- `integration_pause`
**Emotional jobs (7):** recognition, mechanism, deepening, reframe, practice, integration, resolution
**Setup shapes (6):**
- `body_first_entry` — "Start with the breath that shortened when the chapter turned."
- `small_entry` — "Give the body one move it can make in the next thirty seconds."
- `permission_to_try` — "You do not have to get this right. You just have to try it once."
- `not_a_test` — "This is not a test. It is an experiment with no wrong outcome."
- `concrete_invitation` — "Place one hand where the tension is loudest."
- `gentle_directive` — "Begin where the weight settled."
**Validation shapes (7):**
- `neutral_validation` — "Whatever you noticed is enough."
- `data_framing` — "What just happened gave you information."
- `small_shift_counts` — "Even a small shift is still a shift."
- `no_wrong_answer` — "There is no wrong response here."
- `body_trust` — "Your body responded in its own language."
- `contrast_noticing` — "Notice what changed, even slightly."
- `anti_grading` — "This does not need a score to count."
**YAML structure:**
```yaml
schema_version: 1

wrapper_types:
setup_sentence:
breath_regulation:
recognition:
body_first_entry:
- text: "Start with the breath that shortened when the chapter turned."
stems: ["start with the breath that shortened"]
roots: ["breath", "chapter"]
small_entry:
- text: "..."
mechanism:
body_first_entry:
- text: "..."
grounding:
recognition:
concrete_invitation:
- text: "..."
# ...

post_practice_validation:
grounding:
mechanism:
data_framing:
- text: "What just happened gave your body a clearer signal than thought alone can provide."
stems: ["gave your body a clearer signal"]
roots: ["body", "signal", "thought"]
# ...

pre_integration_transition:
# wrapper from exercise → integration
# ...

**Minimum sizes:**
- Setup / entry: 30–50 total
- Pre-practice bridge: 25–40 total
- Post-practice validation: 40–60 total
- Pre-integration transition: 30–50 total
**Practice-type tone guidance (embed in YAML or use in selector):**
- `breath_regulation`: plain, stabilizing, rhythmic
- `grounding`: sensory, immediate, concrete
- `body_scan`: curious, non-forcing, observational
- `somatic_discharge`: direct, physical, practical
- `visualization`: permissive, imaginative, softer
- `reflective_prompt`: spacious, non-rushed
- `vagus_stimulation`: lightly instructional, embodied
- `integration_pause`: quieter, slower, less directive
#### B. Refactor `_exercise_setup_sentence()` (line 440)
New signature:
```python
def _exercise_setup_sentence(
reflection: str,
story: str,
*,
emotional_job: str = "",
practice_type: str = "",
exercise_memory: "ExerciseWrapperMemory | None" = None,
) -> str:

Keep the body-locus-specific logic (sternum, jaw, throat, shoulders, hand, breath) as high-priority matches. But when falling back to generic options, use the YAML bank with practice-type and emotional_job conditioning instead of the flat 10-item fallback list.
#### C. Refactor `_bridge_before_exercise()` (line 211)
Add `emotional_job` and `exercise_memory` params (keeping `thesis`, `reflection`, `story` as-is for backward compat). When YAML is loaded, use scored selection; otherwise fall back to current behavior.
#### D. Refactor `_bridge_before_integration()` (line 237)
Add `emotional_job` and `exercise_memory` params. When YAML is loaded, use scored selection with practice-type awareness.
#### E. Add `ExerciseWrapperMemory` class
```python
class ExerciseWrapperMemory:
"""Tracks exercise wrapper usage across chapters for anti-reuse."""

Rules:
- Exact phrase: max 1/book
- Same stem: max 1 per 4 chapters
- Same validation family: no clustering (e.g., not "no wrong answer" + "exactly right" + "useful information" in adjacent chapters)
- Ban stems: "before you continue" / "just try it" / "whatever happened" / "useful information" max 1 each/book
- Same dominant roots (body, notice, continue, shift, information) max 3 in 4 adjacent chapters
#### F. Wire into call chain
In `compose_chapter_prose()`:
- Line 712/737/749: `_exercise_setup_sentence(reflection_raw, story_raw)` → add `emotional_job=emotional_role, exercise_memory=exercise_memory`
- Line 748: `_bridge_before_exercise(thesis, reflection=reflection_raw, story=story_raw)` → add `emotional_job=emotional_role, exercise_memory=exercise_memory`
- Line 770: `_bridge_before_integration(thesis, integration=integration_raw)` → add `emotional_job=emotional_role, exercise_memory=exercise_memory`
Determine `practice_type` from `exercise_type_hint` (line 583) or `exercise_atom_id` — map to one of the 9 practice buckets. If unmappable, default to `"body_awareness"`.
Create `ExerciseWrapperMemory` in `compose_from_enriched_book()` alongside the `MechanismThesisMemory` and thread both through the chapter loop.
Add new parameter to `compose_chapter_prose()`:
```python
exercise_memory: Optional["ExerciseWrapperMemory"] = None,

---
## BOTH PARTS — Shared requirements
### YAML loader pattern
Use the same caching pattern for both YAML files:
```python
_MECHANISM_THESIS_CACHE: dict[str, Any] | None = None
_EXERCISE_WRAPPER_CACHE: dict[str, Any] | None = None

Load once, cache in module globals. Graceful fallback to current behavior if YAML missing.
### Scorer pattern
Both systems should use the same scored-selection approach. Do NOT just hash-pick. Score all candidates and choose the best low-repetition candidate.
### compose_from_enriched_book() changes (line 799)
At book render start (before the chapter loop at line 869), create both memory objects:
```python
mechanism_memory = MechanismThesisMemory()
exercise_memory = ExerciseWrapperMemory()

Thread both into each `compose_chapter_prose()` call (currently at line 564 via `compose_golden_spine_chapter`, which calls `compose_chapter_prose` at line 564 of golden_chapter_synthesis.py).
**Note:** `compose_golden_spine_chapter()` (in golden_chapter_synthesis.py, line 527) calls `compose_chapter_prose()`. The memory objects need to be passed through this chain. You'll need to add memory parameters to `compose_golden_spine_chapter()` and forward them. This is the ONLY change to golden_chapter_synthesis.py — adding pass-through parameters, not changing any logic there.
**Update OUT_OF_SCOPE:** You MAY add pass-through parameters to `compose_golden_spine_chapter()` in golden_chapter_synthesis.py, but do not change any other logic in that file.
---
## Tests
### `tests/test_mechanism_thesis_system.py` (new file)
1. Same reflection text + different emotional_job yields different thesis shapes
2. Thesis output does not always start with "The point is that" — at least 4 of 7 emotional_jobs produce non-"point is that" thesis
3. Same reflection text + different emotional_job yields different mechanism explanations
4. Exact thesis phrase not reused in synthetic 12-chapter book (create MechanismThesisMemory, call 12 times)
5. Exact mechanism phrase not reused in synthetic 12-chapter book
6. "The point is that" stem appears max 2 times in 12-chapter book
7. Same mechanism wrapper stem ("Here is the mechanism" etc.) appears max 1 time/book
8. Same shape not overused in 3-adjacent-chapter window
9. Topic-specific mechanisms (alarm, comparison, shame etc.) still fire when keywords match and emotional_job=""
10. YAML missing → graceful fallback to current behavior (not crash)
11. All functions still work with emotional_job="" (backward compat)
12. `_fallback_takeaway()` produces varied output, not always "Remember this: {core}…"
### `tests/test_exercise_wrapper_system.py` (new file)
1. Same body context + different emotional_job yields different setup sentences
2. Same practice_type + different emotional_job yields different wrapper pools
3. Exact wrapper phrase not reused in synthetic 12-chapter book
4. Same validation stem not overused in adjacent chapters
5. Different practice_types route to different wrapper families
6. Body-locus-specific logic (sternum, jaw, throat) still fires when keywords match
7. Late chapters (integration/resolution) use softer, less instructive wrappers
8. YAML missing → graceful fallback to current behavior (not crash)
9. All functions still work with emotional_job="" and practice_type="" (backward compat)
10. _bridge_before_integration produces varied output, not all "notice what shifted"
### Existing test regression
- `PYTHONPATH=. pytest tests/test_bestseller_craft_quality.py -v` must still pass
- `PYTHONPATH=. pytest tests/test_golden_chapter_synthesis.py -v` must still pass
---
## Acceptance criteria
1. `python3 -m py_compile phoenix_v4/rendering/chapter_composer.py` passes
2. `python3 -m py_compile tests/test_mechanism_thesis_system.py` passes
3. `python3 -m py_compile tests/test_exercise_wrapper_system.py` passes
4. `PYTHONPATH=. pytest tests/test_mechanism_thesis_system.py -v` — all pass
5. `PYTHONPATH=. pytest tests/test_exercise_wrapper_system.py -v` — all pass
6. `PYTHONPATH=. pytest tests/test_golden_chapter_synthesis.py tests/test_bestseller_craft_quality.py -v` — all still pass
7. `config/rendering/mechanism_thesis_families.yaml` has ≥110 total entries (50+ thesis, 60+ mechanism)
8. `config/rendering/exercise_wrapper_families.yaml` has ≥125 total entries (30+ setup, 25+ pre-practice, 40+ validation, 30+ integration)
9. Thesis output shows ≥4 distinct opening patterns (not just "The point is that…") when rendered across 12 chapters
10. Pilot render shows varied mechanism/thesis/exercise wrapper language:
    ```
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --no-job-check --pipeline-mode spine \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__false_alarm__F006.yaml \
  --runtime-format short_book_30 --render-book \
  --render-dir /tmp/mech-thesis-exercise-pilot \
  --golden-chapter-pilot 1 --quality-profile draft
```
11. Push-guard and preflight pass

Branch
git fetch origin
git checkout -b agent/mechanism-thesis-exercise-wrapper-20260416 origin/main

Emit CLOSEOUT_RECEIPT when done.



---

**Cursor**

I’m starting by reading the required context files you listed (including the full `chapter_composer.py`) so I can implement exactly within scope and preserve backward compatibility. After that I’ll branch and begin the refactor + new YAML systems.

I’ve finished the required six-file read and confirmed the exact hotspots in `chapter_composer.py`. Next I’m doing the mandatory governance/authority reads (so branch + write actions stay compliant), then I’ll implement the two YAML systems and threaded memory pass-through.

I’ve completed the mandatory authority/governance reads and now I’m finalizing the startup protocol check, then I’ll run preflight + create the requested branch from `origin/main` before coding.

```
STARTUP_RECEIPT
AGENT:              Pearl_Dev
TASK:               Build mechanism/thesis delivery + exercise wrapper systems with memory threading
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;specs/PHOENIX_V4_5_WRITER_SPEC.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/SESSION_UNITY_PROTOCOL.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        config/rendering/mechanism_thesis_families.yaml;config/rendering/exercise_wrapper_families.yaml;phoenix_v4/rendering/chapter_composer.py;phoenix_v4/rendering/golden_chapter_synthesis.py;tests/test_mechanism_thesis_system.py;tests/test_exercise_wrapper_system.py;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       atoms/;SOURCE_OF_TRUTH/;phoenix_v4/planning/chapter_planner.py;config/source_of_truth/chapter_purpose_contracts.yaml;scripts/localization/
BLOCKERS:           none
READY_STATUS:       ready
```

I’m running required git preflight next, then creating your requested `agent/mechanism-thesis-exercise-wrapper-20260416` branch from `origin/main`.

Preflight/branching is done, but I hit an important repo-state issue: there are pre-existing modified paths in `.claude/worktrees/*`, `_wt_beatmap`, and `_wt_inj` now visible on this branch (outside your requested scope).  
How do you want to proceed: continue with your requested implementation while leaving those untouched, or stop and first clean/resolve that workspace state?

---

**User**

continue with your requested implementation while leaving those untouched

---

**Cursor**

Proceeding with implementation now and keeping all unrelated existing changes untouched. I’ll first update `chapter_composer.py`/`golden_chapter_synthesis.py` wiring and memory classes, then add the two YAML banks and targeted tests.

I found that `chapter_composer.py` content on this clean branch differs from what I read before branching, so I’m refreshing the file now to avoid patching against stale context before I edit.

I’m now editing `chapter_composer.py` in one pass: adding the two cache loaders, both memory classes, candidate scoring, and backward-compatible wrappers around the six target functions. Then I’ll wire the memory objects through compose paths.

I’ve finished the core refactor and YAMLs; next I’m adding focused tests for the two new systems, then I’ll run compile + pytest and fix any regressions.

Implemented the mechanism/thesis delivery system and exercise wrapper system end-to-end, including YAML-driven selection, anti-reuse memory, and call-chain wiring.

### What I changed

- Added new config banks:
  - `config/rendering/mechanism_thesis_families.yaml`
  - `config/rendering/exercise_wrapper_families.yaml`
- Refactored in `phoenix_v4/rendering/chapter_composer.py`:
  - Added cached YAML loaders:
    - `_load_mechanism_thesis_families()`
    - `_load_exercise_wrapper_families()`
  - Added memory classes:
    - `MechanismThesisMemory`
    - `ExerciseWrapperMemory`
  - Added scored candidate selectors with anti-reuse rules.
  - Refactored signatures and behavior for:
    - `_derive_thesis(...)`
    - `_distill_mechanism(...)`
    - `_fallback_takeaway(...)`
    - `_exercise_setup_sentence(...)`
    - `_bridge_before_exercise(...)`
    - `_bridge_before_integration(...)`
  - Added practice-type routing via `_resolve_practice_type(...)`.
  - Added post-practice validation layer via `_post_practice_validation_sentence(...)`.
  - Updated `compose_chapter_prose(...)` to pass `emotional_role`, `mechanism_memory`, `exercise_memory`, and `practice_type` through all relevant calls.
  - Added new optional params to `compose_chapter_prose(...)`:
    - `mechanism_memory`
    - `exercise_memory`
- Threaded memory through enriched render path in `compose_from_enriched_book(...)`.
- Added pass-through params in `phoenix_v4/rendering/golden_chapter_synthesis.py`:
  - `mechanism_memory`
  - `exercise_memory`
  - and forwarded them into `compose_chapter_prose(...)`.
- Added tests:
  - `tests/test_mechanism_thesis_system.py`
  - `tests/test_exercise_wrapper_system.py`

### Validation run

- Compile:
  - `python3 -m py_compile phoenix_v4/rendering/chapter_composer.py phoenix_v4/rendering/golden_chapter_synthesis.py tests/test_mechanism_thesis_system.py tests/test_exercise_wrapper_system.py` ✅
- New tests:
  - `PYTHONPATH=. python3 -m pytest tests/test_mechanism_thesis_system.py tests/test_exercise_wrapper_system.py -v` ✅ (22 passed)
- Regression tests:
  - `PYTHONPATH=. python3 -m pytest tests/test_golden_chapter_synthesis.py tests/test_bestseller_craft_quality.py -v` ✅ (34 passed)
- Pilot render command you requested:
  - Ran successfully and produced artifacts in `/tmp/mech-thesis-exercise-pilot` ✅
- YAML entry counts:
  - `mechanism_thesis_families.yaml`: 140 total (56 thesis, 63 mechanism, 21 takeaway) ✅
  - `exercise_wrapper_families.yaml`: 141 total (37 setup, 30 pre-practice, 44 post-validation, 30 pre-integration) ✅

### Important blocker (unexpected repo state)

I detected unexpected branch/context drift during final preflight: current branch reported as `agent/rhetorical-architecture-issues-and-scorer-20260416` instead of the requested branch, with many unrelated modified/untracked files outside this task.

Per your repo safety rules, I’m stopping here and waiting for direction before any further git operations (commit/push/workstream updates).

---

CLOSEOUT_RECEIPT  
AGENT:          Pearl_Dev  
TASK:           Build mechanism/thesis delivery system + exercise wrapper system  
COMMIT_SHA:     no commits  
FILES_WRITTEN:  `config/rendering/mechanism_thesis_families.yaml`; `config/rendering/exercise_wrapper_families.yaml`; `phoenix_v4/rendering/chapter_composer.py`; `phoenix_v4/rendering/golden_chapter_synthesis.py`; `tests/test_mechanism_thesis_system.py`; `tests/test_exercise_wrapper_system.py`  
FILES_READ:     `docs/SESSION_UNITY_PROTOCOL.md`; `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`; `specs/PHOENIX_V4_5_WRITER_SPEC.md`; `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`; required startup/governance docs  
STATUS:         partial  
HANDOFF_TO:     owner  
NEXT_ACTION:    Confirm how you want to handle the unexpected branch/worktree drift; then I can stage/commit only scoped files and (optionally) update `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.

