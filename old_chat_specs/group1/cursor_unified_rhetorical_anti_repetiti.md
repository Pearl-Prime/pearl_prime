# Unified rhetorical anti-repetition architecture
_Exported on 4/16/2026 at 19:19:11 GMT+8 from Cursor (3.1.15)_

---

**User**

You are Pearl_GitHub + Pearl_Dev acting together. This session creates 5 GitHub
issues for the unified rhetorical anti-repetition architecture, then implements
the shared scoring engine skeleton as repo-ready modules.
─── STARTUP_RECEIPT ───────────────────────────────────────────────────────
AGENT:              Pearl_GitHub + Pearl_Dev
TASK:               Create 5 GitHub child issues for rhetorical architecture
                    workstreams; implement shared scoring engine, memory, and
                    taxonomy as repo-ready modules
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     docs/DOCS_INDEX.md; docs/SESSION_UNITY_PROTOCOL.md;
                    docs/GITHUB_OPERATIONS_FRAMEWORK.md;
                    docs/GITHUB_GOVERNANCE.md;
                    artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;
                    artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        .github/ISSUE_TEMPLATE/ (optional);
                    phoenix_v4/rendering/rhetorical_memory.py (new);
                    phoenix_v4/rendering/rhetorical_scorer.py (new);
                    config/rendering/rhetorical_style_taxonomy.yaml (new);
                    tests/test_rhetorical_scorer.py (new);
                    tests/test_rhetorical_memory.py (new)
OUT_OF_SCOPE:       chapter_composer.py; golden_chapter_synthesis.py;
                    anything in scripts/localization/; manga_pipeline
BLOCKERS:           none
READY_STATUS:       ready
───────────────────────────────────────────────────────────────────────────
Read before doing anything:
  1. docs/DOCS_INDEX.md
  2. artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
  3. artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
  4. phoenix_v4/rendering/chapter_composer.py  (lines 54-65: _pick_variant;
     lines 570-587: compose_chapter_prose signature; lines 74-122: _derive_thesis;
     lines 129-253: all four _bridge_* functions; lines 260-329: _distill_mechanism;
     lines 440-466: _exercise_setup_sentence)
  5. phoenix_v4/rendering/golden_chapter_synthesis.py  (lines 62-96:
     _resolve_location_placeholders; lines 774-801: dedupe_scene_furniture_book)
  6. phoenix_v4/planning/chapter_planner.py  (lines 58-69: ChapterContract dataclass)
  7. config/rendering/ — confirm directory does NOT exist; create it.
Branch: agent/rhetorical-architecture-issues-and-scorer-20260416
Branch from: origin/main
Remote: https://github.com/Ahjan108/phoenix_omega_v4.8.git
══════════════════════════════════════════════════════════════════════════
PART A — CREATE 5 GITHUB ISSUES
══════════════════════════════════════════════════════════════════════════
Use `gh issue create` to make these 5 issues. Apply label "rhetorical-architecture"
(create the label first if it doesn't exist: `gh label create rhetorical-architecture
--color 7B68EE --description "Unified rhetorical anti-repetition architecture"`).
Each issue body uses the exact text below. Do NOT paraphrase.
────────────────────────────────────────────────────────────────────────
ISSUE 1 of 5: Rich Location-Light Fallback Environment System
Title: rhetorical-arch: environment fallback — location-light replacements
       with chapter-function conditioning
Body:
## Summary
Replace the hardcoded placeholder map in `golden_chapter_synthesis.py`
`_resolve_location_placeholders()` (lines 62-96) with a YAML-driven,
chapter-function-aware, scored-selection environment system.
## Current State
- 10 hardcoded regex replacements (e.g. `{weather_detail}` → "Gray daylight
  filters in", `{street_name}` → "The street")
- Zero awareness of chapter emotional_job or position
- Identical fallback text appears in every chapter of a 20-chapter book
## Deliverables
1. `config/rendering/environment_variants.yaml` — 8-12 variants per slot,
   each tagged with `shape`, `register`, `movement`, `tone` from the shared
   taxonomy. Minimum slots: weather_detail, street_name, transit_line,
   park_name, cafe_name, building_detail, ambient_sound, time_of_day.
2. `phoenix_v4/rendering/environment_selector.py` — scored selection using
   `RhetoricalScorer` (from shared taxonomy issue). Receives chapter_index,
   emotional_job, book-level `RhetoricalMemory`. Returns resolved environment
   dict.
3. Update `_resolve_location_placeholders()` to call environment_selector
   instead of the hardcoded map. Keep hardcoded map as last-resort fallback
   only.
4. Tests: at minimum, verify no two adjacent chapters get identical
   environment strings for any slot. Verify emotional_job filtering works
   (e.g. "recognition" chapters prefer gentler weather).
## Depends On
- Shared taxonomy + memory + scorer (Issue 5)
## Files Modified
- `golden_chapter_synthesis.py` (modify _resolve_location_placeholders)
- `config/rendering/environment_variants.yaml` (new)
- `phoenix_v4/rendering/environment_selector.py` (new)
- `tests/test_environment_selector.py` (new)
Labels: rhetorical-architecture, core_pipeline
────────────────────────────────────────────────────────────────────────
ISSUE 2 of 5: Chapter Bridge / Transition System Refactor
Title: rhetorical-arch: chapter bridges — function-aware transition selection
       with rolling anti-reuse
Body:
## Summary
Replace the 4 bridge functions in `chapter_composer.py` (lines 129-253) with
a YAML-driven, chapter-function-conditioned, scored-selection bridge system.
## Current State
- `_bridge_after_opening()`: 12 generic + keyword-specific options (lines 129-172)
- `_bridge_before_story()`: 12 generic + keyword-specific (lines 175-208)
- `_bridge_before_exercise()`: 12 generic + 2 body-specific (lines 211-234)
- `_bridge_before_integration()`: 12 flat options (lines 237-253)
- All use `_pick_variant()` (hash-seeded, lines 54-65) — no awareness of
  chapter position, emotional_job, or what was used in adjacent chapters
- `emotional_role` enters `compose_chapter_prose()` at line 581 but is NEVER
  forwarded to any bridge function
## Deliverables
1. `config/rendering/bridge_variants.yaml` — 15-20 variants per bridge point,
   each tagged with taxonomy dimensions (shape, register, movement, tone,
   cadence). 4 bridge points: after_opening, before_story, before_exercise,
   before_integration.
2. `phoenix_v4/rendering/bridge_selector.py` — scored selection per bridge
   point. Receives bridge_point, chapter_index, emotional_job, topic_id,
   book-level RhetoricalMemory. Returns selected bridge string + updates memory.
3. Wire `compose_chapter_prose()` to forward emotional_role to bridge selector.
   The 4 existing bridge functions become thin wrappers calling bridge_selector.
4. Rolling window: within any 3-chapter window, no bridge stem may repeat at
   the same bridge point. Memory tracks this.
5. Tests: verify no stem repeats in 3-chapter window; verify emotional_job
   filtering; verify fallback to generic when filtered pool is empty.
## Depends On
- Shared taxonomy + memory + scorer (Issue 5)
## Files Modified
- `chapter_composer.py` (modify 4 bridge functions + compose_chapter_prose)
- `config/rendering/bridge_variants.yaml` (new)
- `phoenix_v4/rendering/bridge_selector.py` (new)
- `tests/test_bridge_selector.py` (new)
Labels: rhetorical-architecture, core_pipeline
────────────────────────────────────────────────────────────────────────
ISSUE 3 of 5: Mechanism / Thesis Delivery System
Title: rhetorical-arch: mechanism + thesis — emotional-job-aware delivery
       with anti-repetition scoring
Body:
## Summary
Replace `_derive_thesis()` (lines 74-122) and `_distill_mechanism()` (lines
260-329) in `chapter_composer.py` with scored, YAML-driven, emotional-job-aware
systems.
## Current State
- `_derive_thesis()`: 25 keyword→thesis mappings, ALL starting "The point is
  that…" + 7 fallbacks all "The point is that…". Zero variation in frame.
- `_distill_mechanism()`: 8 topic-specific paragraphs + 5 generic templates.
  Wrappers like "Underneath the feeling is a simple mechanism:" repeat across
  chapters.
- Neither function receives emotional_role — it enters compose_chapter_prose
  at line 581 but stops there.
## Deliverables
1. `config/rendering/thesis_variants.yaml` — per-emotional-job thesis frames.
   Minimum 6 distinct opening frames (NOT all "The point is that…"). Tagged
   with taxonomy dimensions. 7 emotional_job values × 4+ frame variants each.
2. `config/rendering/mechanism_variants.yaml` — mechanism wrapper variants
   tagged with shape, register, abstraction_level. Minimum 10 wrappers.
   Topic-specific mechanism bodies remain as-is but the framing varies.
3. `phoenix_v4/rendering/thesis_mechanism_selector.py` — scored selection for
   both thesis frame and mechanism wrapper. Receives emotional_job,
   chapter_index, topic_id, RhetoricalMemory.
4. Wire compose_chapter_prose to forward emotional_role to thesis/mechanism
   selector.
5. Tests: verify thesis opening varies across chapters; verify mechanism
   wrapper varies; verify emotional_job conditioning (e.g. "recognition"
   gets gentler thesis frames, "mechanism" gets direct/technical frames).
## Depends On
- Shared taxonomy + memory + scorer (Issue 5)
## Files Modified
- `chapter_composer.py` (modify _derive_thesis, _distill_mechanism,
  compose_chapter_prose)
- `config/rendering/thesis_variants.yaml` (new)
- `config/rendering/mechanism_variants.yaml` (new)
- `phoenix_v4/rendering/thesis_mechanism_selector.py` (new)
- `tests/test_thesis_mechanism_selector.py` (new)
Labels: rhetorical-architecture, core_pipeline
────────────────────────────────────────────────────────────────────────
ISSUE 4 of 5: Exercise Wrapper / Validation System
Title: rhetorical-arch: exercise wrappers — practice-type-aware setup with
       body-locus conditioning
Body:
## Summary
Replace `_exercise_setup_sentence()` (lines 440-466) in `chapter_composer.py`
with a scored, YAML-driven setup system conditioned on practice type,
body locus, and emotional_job.
## Current State
- 6 body-locus-specific + 10 generic fallback setup sentences
- No awareness of practice type (somatic, cognitive, relational, breath,
  grounding, etc.) or emotional_job
- `_fallback_takeaway()` (lines 409-419): single rigid template
- `_fallback_thread()` (lines 422-437): 6 keyword-specific + 1 generic
## Deliverables
1. `config/rendering/exercise_wrapper_variants.yaml` — setup sentence variants
   per practice_type × body_locus combination. Tagged with taxonomy dimensions.
   Minimum 8 variants per practice type.
2. Extend to also cover takeaway and thread fallback variants (currently
   single-template).
3. `phoenix_v4/rendering/exercise_wrapper_selector.py` — scored selection.
   Receives practice_type, body_locus, emotional_job, chapter_index,
   RhetoricalMemory.
4. Wire compose_chapter_prose to forward emotional_role + exercise_type_hint
   to wrapper selector.
5. Tests: verify practice-type conditioning works; verify no identical setup
   sentence in adjacent exercise chapters; verify body-locus variants are
   preferred when body_locus is known.
## Depends On
- Shared taxonomy + memory + scorer (Issue 5)
## Files Modified
- `chapter_composer.py` (modify _exercise_setup_sentence, _fallback_takeaway,
  _fallback_thread, compose_chapter_prose)
- `config/rendering/exercise_wrapper_variants.yaml` (new)
- `phoenix_v4/rendering/exercise_wrapper_selector.py` (new)
- `tests/test_exercise_wrapper_selector.py` (new)
Labels: rhetorical-architecture, core_pipeline
────────────────────────────────────────────────────────────────────────
ISSUE 5 of 5: Shared Taxonomy + Memory + Scorer (Foundation)
Title: rhetorical-arch: shared taxonomy, RhetoricalMemory, and
       RhetoricalScorer — foundation layer
Body:
## Summary
Build the shared foundation that Issues 1-4 all depend on: a rhetorical
style taxonomy YAML, a book-level memory class, and a scoring engine that
replaces hash-seeded `_pick_variant()`.
## Current State
- `_pick_variant()` in chapter_composer.py (lines 54-65): hash-seeded
  deterministic selection. Zero memory, zero scoring, zero cross-layer
  awareness.
- No taxonomy of rhetorical dimensions exists.
- No book-level memory tracks what was used in previous chapters.
## Deliverables
1. `config/rendering/rhetorical_style_taxonomy.yaml` — canonical dimension
   definitions:
   - shape: declarative | interrogative | imperative | conditional |
     participial | fragment | list | metaphor_frame
   - register: clinical | conversational | poetic | somatic | instructional |
     philosophical | urgent
   - movement: inward | outward | stillness | tension_release | building |
     returning
   - instruction_tone: gentle | direct | invitational | challenge | neutral
   - cadence: short_staccato | medium_flowing | long_immersive
   - abstraction_level: concrete_body | concrete_scene | mid_concept |
     high_abstraction
   - root_family: (open — populated per variant, e.g. "notice", "feel",
     "beneath", "remember", "pause")
   Plus canonical `emotional_job` values: recognition, mechanism, deepening,
   reframe, practice, integration, resolution.
2. `phoenix_v4/rendering/rhetorical_memory.py` — RhetoricalMemory class:
   - Book-level singleton, created once per book render
   - Tracks per-chapter, per-layer usage: which dimensions were used, which
     stems appeared, which root_families were hit
   - Rolling window queries: "in the last N chapters at layer X, which shapes
     were used?" / "has stem Y appeared at bridge_point Z in the last 3
     chapters?"
   - Budget tracking: per-dimension per-book caps (e.g. max 30% interrogative
     shape across a 20-chapter book)
   - Thread-safe (book render may parallelize chapter rendering)
3. `phoenix_v4/rendering/rhetorical_scorer.py` — RhetoricalScorer:
   - score_candidates(candidates, context) → ranked list
   - Context includes: layer, chapter_index, emotional_job, topic_id, memory
   - Scoring factors:
     a. emotional_job alignment bonus (+3 if variant's tagged job matches)
     b. recency penalty (−5 if same shape used in last chapter at same layer,
        −3 if 2 chapters ago, −1 if 3 chapters ago)
     c. cross-layer echo penalty (−2 if same root_family used at a different
        layer in the same chapter)
     d. book-level budget penalty (−4 if dimension is over its book-wide cap)
     e. stem repeat veto (score = −∞ if exact stem used at same layer in
        rolling window)
   - Returns best candidate (highest score, tiebreak by original pool order)
   - Updates memory after selection
4. Tests:
   - test_rhetorical_memory.py: rolling window, budget tracking, thread safety
   - test_rhetorical_scorer.py: scoring math, veto logic, tiebreak,
     emotional_job bonus, cross-layer penalty
## Implementation Priority
This is Issue 5 but must be IMPLEMENTED FIRST — it is the foundation that
Issues 1-4 import from. Create the branch, implement this issue's deliverables,
push, and open a PR. Issues 1-4 can then be developed in parallel on branches
that build on this one.
## Files Modified
- `config/rendering/rhetorical_style_taxonomy.yaml` (new)
- `phoenix_v4/rendering/rhetorical_memory.py` (new)
- `phoenix_v4/rendering/rhetorical_scorer.py` (new)
- `tests/test_rhetorical_memory.py` (new)
- `tests/test_rhetorical_scorer.py` (new)
Labels: rhetorical-architecture, core_pipeline
══════════════════════════════════════════════════════════════════════════
PART B — IMPLEMENT ISSUE 5 (SCORING ENGINE SKELETON)
══════════════════════════════════════════════════════════════════════════
After creating all 5 issues, implement Issue 5's deliverables on the branch.
Use the following pseudocode as the implementation specification. This is the
EXACT architecture to follow — do not redesign.
────────────────────────────────────────────────────────────────────────
FILE: config/rendering/rhetorical_style_taxonomy.yaml
────────────────────────────────────────────────────────────────────────
Create this YAML with the full dimension definitions from Issue 5 above.
Include a `schema_version: 1` header. Each dimension gets:
- name
- values (list of canonical strings)
- description (one line)
Include the `emotional_job` canonical list and a `root_families` section
that lists common root families with examples (notice, feel, beneath,
remember, pause, allow, hold, return, breathe, land).
────────────────────────────────────────────────────────────────────────
FILE: phoenix_v4/rendering/rhetorical_memory.py
────────────────────────────────────────────────────────────────────────
```python
"""
Book-level rhetorical memory for cross-layer anti-repetition.

Single instance per book render. All four subsystem selectors
(environment, bridge, thesis/mechanism, exercise wrapper) share one
RhetoricalMemory so cross-layer echo detection works.
"""
from future import annotations

import threading
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional

── data structures ────────────────────────────────────────────────
@dataclass
class UsageRecord:
"""One selection event."""
chapter_index: int
layer: str # "environment" | "bridge" | "thesis" | "mechanism" | "exercise"
sublayer: str # e.g. "after_opening" for bridges, "weather_detail" for env
variant_id: str # unique ID of the variant chosen
shape: str
register: str
movement: str
instruction_tone: str
cadence: str
abstraction_level: str
root_family: str
stem: str # first 6 words, lowercased, for stem-repeat detection

── main memory class ──────────────────────────────────────────────
class RhetoricalMemory:
"""
Thread-safe, book-level memory of all rhetorical selections.
Created once per book render; passed to every selector.
"""

def __init__(self, total_chapters: int = 20):
    self._lock = threading.Lock()
    self.total_chapters = total_chapters
    self._records: list[UsageRecord] = []
    # Fast lookups
    self._by_chapter: dict[int, list[UsageRecord]] = defaultdict(list)
    self._by_layer: dict[str, list[UsageRecord]] = defaultdict(list)
    # Book-wide dimension counters for budget tracking
    self._dimension_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # Total selections for budget ratio calculation
    self._total_selections: int = 0
def record(self, rec: UsageRecord) -> None:
    """Record a selection. Thread-safe."""
    with self._lock:
        self._records.append(rec)
        self._by_chapter[rec.chapter_index].append(rec)
        self._by_layer[rec.layer].append(rec)
        # Update dimension counters
        for dim_name in ("shape", "register", "movement",
                         "instruction_tone", "cadence",
                         "abstraction_level", "root_family"):
            val = getattr(rec, dim_name, "")
            if val:
                self._dimension_counts[dim_name][val] += 1
        self._total_selections += 1
def recent_at_layer(self, layer: str, sublayer: str,
                    current_chapter: int, window: int = 3
                    ) -> list[UsageRecord]:
    """Return records at (layer, sublayer) within the last `window` chapters."""
    with self._lock:
        min_ch = max(0, current_chapter - window)
        return [
            r for r in self._by_layer.get(layer, [])
            if r.sublayer == sublayer and min_ch <= r.chapter_index < current_chapter
        ]
def same_chapter_other_layers(self, chapter_index: int,
                               exclude_layer: str
                               ) -> list[UsageRecord]:
    """Return all records for the same chapter from OTHER layers."""
    with self._lock:
        return [
            r for r in self._by_chapter.get(chapter_index, [])
            if r.layer != exclude_layer
        ]
def dimension_ratio(self, dim_name: str, dim_value: str) -> float:
    """Return ratio of selections using dim_value for dim_name."""
    with self._lock:
        if self._total_selections == 0:
            return 0.0
        return self._dimension_counts[dim_name][dim_value] / self._total_selections
def stem_used_recently(self, layer: str, sublayer: str,
                       stem: str, current_chapter: int,
                       window: int = 3) -> bool:
    """Check if exact stem was used at (layer, sublayer) in last `window` chapters."""
    recent = self.recent_at_layer(layer, sublayer, current_chapter, window)
    return any(r.stem == stem for r in recent)
────────────────────────────────────────────────────────────────────────
FILE: phoenix_v4/rendering/rhetorical_scorer.py
────────────────────────────────────────────────────────────────────────
```python
"""
Scored candidate selection for rhetorical variants.

Replaces _pick_variant() hash-seeded selection with penalty/reward scoring
across memory state. Each subsystem selector calls score_and_select()
with its candidate pool and context.
"""
from future import annotations

from dataclasses import dataclass, field
from typing import Optional

from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory, UsageRecord

── scoring context ────────────────────────────────────────────────
@dataclass
class ScoringContext:
"""Everything the scorer needs from the caller."""
layer: str
sublayer: str
chapter_index: int
emotional_job: str # from ChapterContract
topic_id: str
memory: RhetoricalMemory
book_seed: str = "" # for tiebreak determinism

@dataclass
class CandidateVariant:
"""A single variant to be scored. Tags come from the YAML."""
variant_id: str
text: str
shape: str = ""
register: str = ""
movement: str = ""
instruction_tone: str = ""
cadence: str = ""
abstraction_level: str = ""
root_family: str = ""
emotional_jobs: list[str] = field(default_factory=list) # which jobs this variant suits

@property
def stem(self) -> str:
    """First 6 words, lowercased."""
    words = self.text.strip().split()[:6]
    return " ".join(w.lower() for w in words)
── scoring weights (tunable) ─────────────────────────────────────
EMOTIONAL_JOB_BONUS = 3
RECENCY_PENALTIES = {1: -5, 2: -3, 3: -1} # chapters_ago → penalty
CROSS_LAYER_ECHO_PENALTY = -2
BUDGET_OVER_PENALTY = -4
BUDGET_THRESHOLD = 0.30 # 30% cap per dimension value
STEM_VETO_SCORE = float("-inf")

── core scoring ───────────────────────────────────────────────────
def score_candidate(candidate: CandidateVariant,
ctx: ScoringContext) -> float:
"""Score a single candidate against current memory state."""
score = 0.0

# 1. Emotional job alignment bonus
if ctx.emotional_job and ctx.emotional_job in candidate.emotional_jobs:
    score += EMOTIONAL_JOB_BONUS
# 2. Stem repeat veto
if ctx.memory.stem_used_recently(ctx.layer, ctx.sublayer,
                                  candidate.stem, ctx.chapter_index):
    return STEM_VETO_SCORE
# 3. Recency penalty — same shape at same layer/sublayer
recent = ctx.memory.recent_at_layer(ctx.layer, ctx.sublayer,
                                     ctx.chapter_index, window=3)
for rec in recent:
    chapters_ago = ctx.chapter_index - rec.chapter_index
    if chapters_ago in RECENCY_PENALTIES and rec.shape == candidate.shape:
        score += RECENCY_PENALTIES[chapters_ago]
# 4. Cross-layer echo — same root_family used elsewhere this chapter
if candidate.root_family:
    same_ch = ctx.memory.same_chapter_other_layers(ctx.chapter_index,
                                                    ctx.layer)
    if any(r.root_family == candidate.root_family for r in same_ch):
        score += CROSS_LAYER_ECHO_PENALTY
# 5. Book-level budget
for dim_name in ("shape", "register", "movement"):
    val = getattr(candidate, dim_name, "")
    if val and ctx.memory.dimension_ratio(dim_name, val) > BUDGET_THRESHOLD:
        score += BUDGET_OVER_PENALTY
return score
def score_and_select(candidates: list[CandidateVariant],
ctx: ScoringContext) -> tuple[CandidateVariant, UsageRecord]:
"""
Score all candidates, pick the best, record in memory, return both
the chosen candidate and the usage record.

Tiebreak: original pool order (first candidate wins ties).
"""
if not candidates:
    raise ValueError("Empty candidate pool — cannot select")
scored = [(score_candidate(c, ctx), i, c) for i, c in enumerate(candidates)]
scored.sort(key=lambda t: (-t[0], t[1]))  # highest score, lowest index
_, _, best = scored[0]
record = UsageRecord(
    chapter_index=ctx.chapter_index,
    layer=ctx.layer,
    sublayer=ctx.sublayer,
    variant_id=best.variant_id,
    shape=best.shape,
    register=best.register,
    movement=best.movement,
    instruction_tone=best.instruction_tone,
    cadence=best.cadence,
    abstraction_level=best.abstraction_level,
    root_family=best.root_family,
    stem=best.stem,
)
ctx.memory.record(record)
return best, record
def check_chapter_budget(memory: RhetoricalMemory,
threshold: float = BUDGET_THRESHOLD
) -> dict[str, list[str]]:
"""
Return any dimension values that have exceeded the budget threshold.
Useful for QA reports. Returns {dim_name: [over_budget_values]}.
"""
warnings: dict[str, list[str]] = {}
for dim_name in ("shape", "register", "movement", "instruction_tone",
"cadence", "abstraction_level"):
over = []
with memory._lock:
for val, count in memory._dimension_counts[dim_name].items():
if memory._total_selections > 0:
ratio = count / memory._total_selections
if ratio > threshold:
over.append(f"{val} ({ratio:.0%})")
if over:
warnings[dim_name] = over
return warnings

────────────────────────────────────────────────────────────────────────
TESTS
────────────────────────────────────────────────────────────────────────
Create `tests/test_rhetorical_memory.py` and `tests/test_rhetorical_scorer.py`.
test_rhetorical_memory.py must cover:
- record() and retrieval via recent_at_layer
- stem_used_recently returns True/False correctly
- same_chapter_other_layers excludes the queried layer
- dimension_ratio math is correct
- Thread safety: concurrent record() calls from multiple threads don't lose data
test_rhetorical_scorer.py must cover:
- Emotional job bonus: candidate with matching job scores higher
- Stem veto: candidate with recently-used stem gets -inf
- Recency penalty: same shape 1 chapter ago gets -5
- Cross-layer echo: same root_family at different layer in same chapter gets -2
- Budget penalty: dimension over 30% gets -4
- Tiebreak: first candidate in pool wins ties
- score_and_select records the winner in memory
- check_chapter_budget reports over-budget dimensions
Run all tests with: `python -m pytest tests/test_rhetorical_memory.py tests/test_rhetorical_scorer.py -v`
All tests must pass before committing.
══════════════════════════════════════════════════════════════════════════
PART C — COMMIT, PUSH, PR
══════════════════════════════════════════════════════════════════════════
After all 5 issues are created and Issue 5's code + tests pass:
1. Run preflight:
   git branch --show-current
   git status --short
   git fetch origin
   git rev-list --left-right --count origin/main...HEAD
   PYTHONPATH=. python3 scripts/git/push_guard.py
   scripts/ci/preflight_push.sh
   bash scripts/git/health_check.sh
2. Commit with message:
   "Add shared rhetorical taxonomy, RhetoricalMemory, and RhetoricalScorer
   Foundation layer (Issue 5 of 5) for the unified rhetorical
   anti-repetition architecture. Implements scored candidate selection
   to replace hash-seeded _pick_variant(). Issues 1-4 (environment,
   bridges, thesis/mechanism, exercise wrappers) build on this."
3. Push branch, open PR targeting main. PR body should reference all 5
   issue numbers and note this is the foundation layer.
══════════════════════════════════════════════════════════════════════════
CLOSEOUT_RECEIPT REQUIREMENTS
══════════════════════════════════════════════════════════════════════════
CLOSEOUT_RECEIPT must include:
- COMMIT_SHA: full 40-char SHA
- BRANCH: exact branch name
- ISSUE_NUMBERS: all 5 GitHub issue numbers
- PR_NUMBER: the opened PR number
- TEST_RESULTS: pytest output summary
- FILES_CREATED: full list of new files
- FILES_MODIFIED: full list of modified files
- NEXT_ACTION: "Issues 1-4 can now be developed in parallel on branches
  forked from this PR's branch. Each subsystem selector imports from
  rhetorical_memory and rhetorical_scorer."
If push-guard blocks, follow the Golden Branch Pattern from CLAUDE.md.
If tests fail, fix them before committing — do not commit with failing tests.
Do not report "done" without the full CLOSEOUT_RECEIPT.

---

**Cursor**

I’m starting by reading the required authority/context files and the specific code sections you listed, then I’ll create the branch from `origin/main`, open the five GitHub issues exactly as provided, and implement Issue 5’s foundation modules and tests.

I’ve loaded the required coordination docs; next I’m reading the exact code regions you specified in the rendering/planning modules before starting git/issue operations.

I’ve finished the required targeted code reads; before any git/GitHub commands I’m now loading the Pearl_GitHub startup docs listed in `CLAUDE.md` in the required order.

I had to stop before continuing because I found unexpected repo state changes that I did not make, and your guardrails require me to pause and confirm with you.

- Current branch is `agent/unified-rhetorical-architecture-20260416` (not the requested `agent/rhetorical-architecture-issues-and-scorer-20260416`).
- There are many unexpected dirty entries, including the exact Issue 5 target files already present as untracked:
  - `config/rendering/`
  - `phoenix_v4/rendering/rhetorical_memory.py`
  - `phoenix_v4/rendering/rhetorical_scorer.py`
  - `tests/test_rhetorical_memory.py`
  - `tests/test_rhetorical_scorer.py`
- There are also multiple modified/untracked `.claude/worktrees/*` paths beyond the initial snapshot.

How do you want to proceed?

1. Continue on this current branch/state and I’ll build on top of what exists.
2. Create the requested clean branch from `origin/main` and ignore current untracked work.
3. Inspect the existing untracked Issue 5 files first, then decide whether to reuse or replace them.

---

**User**

Create the requested clean branch from origin/main and ignore current untracked work.


---

**Cursor**

Understood — I’ll branch cleanly from `origin/main` now and then continue the full requested workflow on that branch while ignoring the existing untracked work.

Preflight left a stale git lock file, so I’m clearing it and re-running branch creation now.

---

**User**

stuck? try again

---

**Cursor**

I can see it got interrupted mid-run; I’ll check whether that branch command finished in the background and then retry safely if it didn’t.

Branch creation succeeded and is now cleanly based on `origin/main` (`0 0`). Next I’ll create the GitHub label/issues exactly as specified, then implement the Issue 5 files/tests and commit only that foundation layer.

The branch and issues are now in place (`#452`–`#456`). I’m moving on to implementing Issue 5 by overwriting the foundation files/modules and tests on this branch, then running the exact pytest command.

Implementation and tests are now passing locally; I’m running the full mandated preflight sequence next, then I’ll commit, push, and open the PR referencing issues `#452-#456`.

Created the clean branch from `origin/main`, opened all 5 GitHub issues, implemented the Issue 5 foundation layer, ran tests, committed, pushed, and opened the PR.

## CLOSEOUT_RECEIPT

- **COMMIT_SHA:** `15b8cd57558f34401737ff11ce9e406bec311cd6`
- **BRANCH:** `agent/rhetorical-architecture-issues-and-scorer-20260416`
- **ISSUE_NUMBERS:** `#452`, `#453`, `#454`, `#455`, `#456`
- **PR_NUMBER:** `#457` ([PR link](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/457))
- **TEST_RESULTS:** `python3 -m pytest tests/test_rhetorical_memory.py tests/test_rhetorical_scorer.py -v` → `13 passed in 0.12s`
- **FILES_CREATED:**
  - `config/rendering/rhetorical_style_taxonomy.yaml`
  - `phoenix_v4/rendering/rhetorical_memory.py`
  - `phoenix_v4/rendering/rhetorical_scorer.py`
  - `tests/test_rhetorical_memory.py`
  - `tests/test_rhetorical_scorer.py`
- **FILES_MODIFIED:** none (commit contains only newly created files above)
- **NEXT_ACTION:** `Issues 1-4 can now be developed in parallel on branches forked from this PR's branch. Each subsystem selector imports from rhetorical_memory and rhetorical_scorer.`



