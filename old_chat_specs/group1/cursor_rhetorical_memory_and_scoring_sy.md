# Rhetorical memory and scoring system design
_Exported on 4/16/2026 at 19:20:10 GMT+8 from Cursor (3.1.15)_

---

**User**

You are Pearl_Architect + Pearl_Dev. Read these files before any work:
1. docs/SESSION_UNITY_PROTOCOL.md
2. phoenix_v4/rendering/chapter_composer.py (957 lines — full file)
3. phoenix_v4/rendering/golden_chapter_synthesis.py (949 lines — focus on: _resolve_location_placeholders line 62, dedupe_scene_furniture_book line 774, audit_repeated_phrases line 809, build_golden_chapter_report_payload line 853)
4. phoenix_v4/rendering/book_renderer.py (focus on: strengthen_rendered_spine_manuscript, governance_report usage, quality_summary output)
5. phoenix_v4/planning/chapter_planner.py (ChapterContract line 59, emotional_job values)
6. config/source_of_truth/chapter_purpose_contracts.yaml
7. artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
8. docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
STARTUP_RECEIPT
AGENT:              Pearl_Architect + Pearl_Dev
TASK:               Build unified rhetorical anti-repetition architecture — shared taxonomy, cross-layer memory, chapter-level orchestration
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;specs/PHOENIX_V4_5_WRITER_SPEC.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/SESSION_UNITY_PROTOCOL.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        config/rendering/rhetorical_style_taxonomy.yaml;phoenix_v4/rendering/rhetorical_memory.py;phoenix_v4/rendering/rhetorical_scorer.py;tests/test_rhetorical_memory.py;tests/test_rhetorical_scorer.py;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       atoms/;SOURCE_OF_TRUTH/;scripts/localization/;config/localization/;phoenix_v4/rendering/chapter_composer.py;phoenix_v4/rendering/golden_chapter_synthesis.py;phoenix_v4/rendering/book_renderer.py (these three files will be wired by SEPARATE follow-up workstreams — this workstream builds the shared infrastructure only)
BLOCKERS:           none
READY_STATUS:       ready
## Context
Four anti-repetition subsystems are being built in parallel workstreams:
| Layer | Config file | Primary target file | Memory class |
|---|---|---|---|
| 1. Environment fallback | `config/rendering/environment_fallback_families.yaml` | `golden_chapter_synthesis.py` → `_resolve_location_placeholders()` | `EnvironmentPhraseMemory` |
| 2. Bridge/transition | `config/rendering/bridge_transition_families.yaml` | `chapter_composer.py` → `_bridge_after_opening()`, etc. | `BridgeMemory` |
| 3. Mechanism/thesis | `config/rendering/mechanism_thesis_families.yaml` | `chapter_composer.py` → `_derive_thesis()`, `_distill_mechanism()` | `MechanismThesisMemory` |
| 4. Exercise wrapper | `config/rendering/exercise_wrapper_families.yaml` | `chapter_composer.py` → `_exercise_setup_sentence()`, etc. | `ExerciseWrapperMemory` |
Each subsystem independently improves variation. But without cross-layer coordination, you get a hidden failure mode: every layer independently converges on the same "soft, muted, explanatory, gently validating" voice. The chapters individually improve, but together they still create a consistent **generator fingerprint**.
**This workstream builds the shared infrastructure that the four subsystems will plug into.** It does NOT modify the four target files — it provides the taxonomy, memory, and scorer that they will import.
## What already exists in the codebase
- `audit_repeated_phrases()` (golden_chapter_synthesis.py:809) — counts 4-gram repetition in chapter text, reports PASS/WARN
- `dedupe_scene_furniture_book()` (golden_chapter_synthesis.py:774) — post-hoc caps on known repeated signatures
- `governance_report` dict — threaded through book render, collects `recurrence_report`, `frame_governance_chapters`, etc.
- `quality_summary.json` — written by book_renderer after render
- `ChapterContract.emotional_job` — canonical values: recognition, mechanism, deepening, reframe, practice, integration, resolution
## What to build
### A. `config/rendering/rhetorical_style_taxonomy.yaml`
The shared vocabulary that all four layer configs will reference. Each candidate line in any layer YAML should be taggable with fields from this taxonomy.
**Required taxonomy fields:**
```yaml
schema_version: 1

Every candidate entry in any layer YAML can be tagged with these fields.
The shared scorer uses these tags for cross-layer anti-repetition.
shapes:

direct_assertion
quiet_compression
embodied_noticing
causal_turn
contrast_turn
question_turn
forward_pull
permission_turn
data_framing
sensory_observation
object_grounding
systems_explanation
validation_line
reversal_explanation
implication_turn
evidence_turn
registers:

plain
warm
clinical_light
somatic
reflective
quiet_authoritative
soft_guiding
compressed
emotionally_open
movements:

naming
explaining
deepening
reframing
guiding
landing
validating
forwarding
instruction_tones:

directive
gentle_directive
permissive
observational
interpretive
non_grading
cadences:

short_clean
two_clause_balance
compression_then_release
long_then_short
question_then_answer
single_beat
abstraction_levels:

concrete
mid
abstract
Root noun families that create fingerprinting when over-concentrated
tracked_root_families:
somatic: [body, breath, chest, jaw, throat, shoulder, sternum, nervous system]
cognitive: [mind, thought, explanation, understanding, pattern, mechanism]
temporal: [moment, next, now, before, after, already]
spatial: [room, window, glass, light, outside, desk, screen]
emotional: [feeling, alarm, cost, shift, notice, permission]
action: [practice, move, try, start, begin, continue]
meta: [chapter, point, story, question, answer]

Chapter-level diversity budgets (soft targets, not hard gates)
chapter_rhetorical_budget:
max_same_shape_across_layers: 2 # e.g., don't use quiet_compression in environment AND bridge AND mechanism
max_same_register_across_layers: 3
max_same_root_family_per_chapter: 4 # e.g., max 4 "somatic" roots in one chapter across all layers
min_shape_diversity_per_chapter: 4 # at least 4 distinct shapes across the chapter's rhetorical lines
min_movement_diversity_per_chapter: 3 # at least 3 distinct movements

### B. `phoenix_v4/rendering/rhetorical_memory.py` (new module)
The shared cross-layer memory system. All four per-layer memory classes will delegate to this.
```python
"""
Unified rhetorical anti-repetition memory.

All four layer-specific memory classes (EnvironmentPhraseMemory, BridgeMemory,
MechanismThesisMemory, ExerciseWrapperMemory) delegate cross-layer tracking here.

This module provides:

RhetoricalMemory: book-level + optional series-level tracking
ChapterRhetoricalProfile: per-chapter diversity audit
cross-layer anti-repetition rules
"""
**`RhetoricalMemory` class:**
```python
class RhetoricalMemory:
"""Tracks rhetorical usage across all four layers for one book render."""

**Must track (per book):**
- `phrases_used: dict[str, list[int]]` — exact phrase → list of chapter indices where used
- `stems_used: dict[str, list[int]]` — stem → chapter indices
- `roots_used: dict[str, dict[str, int]]` — root → {chapter_index: count}
- `shapes_used: dict[str, list[int]]` — shape → chapter indices
- `registers_used: dict[str, list[int]]` — register → chapter indices
- `movements_used: dict[str, list[int]]` — movement → chapter indices
- `instruction_tones_used: dict[str, list[int]]` — tone → chapter indices
- `cadences_used: dict[str, list[int]]` — cadence → chapter indices
- `layer_usage: dict[str, dict[str, list[int]]]` — layer_name → {shape/register/etc → chapter indices}
**Must track (per chapter, transient):**
- `current_chapter_shapes: list[str]` — shapes used so far in current chapter (across all layers)
- `current_chapter_registers: list[str]`
- `current_chapter_movements: list[str]`
- `current_chapter_roots: dict[str, int]` — root → count in current chapter
- `current_chapter_layer_shapes: dict[str, list[str]]` — layer_name → shapes used
**Key methods:**
```python
def record_selection(
self,
*,
layer: str, # "environment" | "bridge" | "mechanism_thesis" | "exercise_wrapper"
chapter_index: int,
phrase: str,
stems: list[str],
roots: list[str],
shape: str,
register: str = "",
movement: str = "",
instruction_tone: str = "",
cadence: str = "",
) -> None:
"""Record a selection from any layer."""

def is_phrase_used_in_book(self, phrase: str) -> bool:
"""Exact phrase already used anywhere in this book."""

def stem_count_in_window(self, stem: str, chapter_index: int, window: int = 4) -> int:
"""How many times this stem appeared in the last window chapters."""

def shape_count_in_window(self, shape: str, chapter_index: int, window: int = 3) -> int:
"""How many times this shape appeared in the last window chapters (across all layers)."""

def root_family_density(self, root_family: str, chapter_index: int) -> int:
"""How many roots from this family are in the current chapter."""

def chapter_shape_diversity(self, chapter_index: int) -> int:
"""Number of distinct shapes used in this chapter so far."""

def chapter_movement_diversity(self, chapter_index: int) -> int:
"""Number of distinct movements used in this chapter so far."""

def start_chapter(self, chapter_index: int) -> None:
"""Reset per-chapter transient state."""

def get_chapter_profile(self, chapter_index: int) -> "ChapterRhetoricalProfile":
"""Build audit profile for this chapter."""

**`ChapterRhetoricalProfile` dataclass:**
```python
@dataclass
class ChapterRhetoricalProfile:
chapter_index: int
shapes_used: dict[str, int] # shape → count
registers_used: dict[str, int]
movements_used: dict[str, int]
dominant_roots: list[str] # root families with count > budget
cross_layer_collisions: list[str] # e.g., "quiet_compression used in environment AND bridge"
shape_diversity: int
movement_diversity: int
budget_warnings: list[str] # which budget thresholds were exceeded

def to_dict(self) -> dict[str, Any]: ...
**`SeriesRhetoricalMemory` class (optional, for later):**
```python
class SeriesRhetoricalMemory:
"""Persistent series-level tracking across multiple book renders."""

For Phase 1, this can be a stub that loads/saves from `artifacts/render_memory/rhetorical_memory.json`. The four subsystem workstreams don't need series memory yet — book-level is the priority.
### C. `phoenix_v4/rendering/rhetorical_scorer.py` (new module)
The shared scoring engine that all four layer selectors will call.
```python
"""
Shared rhetorical candidate scorer.

Each layer-specific selector (environment, bridge, mechanism/thesis, exercise wrapper)
calls score_candidate() to get a cross-layer-aware score for a candidate line.
The highest-scoring candidate wins.
"""

**`RhetoricalCandidate` dataclass:**
```python
@dataclass
class RhetoricalCandidate:
"""A candidate line from any layer, with taxonomy tags."""
text: str
layer: str # "environment" | "bridge" | "mechanism_thesis" | "exercise_wrapper"
stems: list[str]
roots: list[str]
shape: str
register: str = ""
movement: str = ""
instruction_tone: str = ""
cadence: str = ""
emotional_job_match: bool = True
chapter_position_match: bool = True
topic_relevance: float = 1.0

**`score_candidate()` function:**
```python
def score_candidate(
candidate: RhetoricalCandidate,
memory: RhetoricalMemory,
chapter_index: int,
taxonomy: dict[str, Any],
) -> float:
"""
Score a candidate line for selection, incorporating cross-layer anti-repetition.

Returns a float score. Higher = better candidate.
Base score starts at 1.0, penalties subtract, rewards add.
"""
**Penalty rules (subtract from score):**
| Condition | Penalty |
|---|---|
| Exact phrase already used in book | -1.0 (effectively eliminates) |
| Same stem used in last 4 chapters | -0.4 per occurrence |
| Same shape used in last 3 chapters (any layer) | -0.2 per occurrence |
| Same shape already used in THIS chapter by ANOTHER layer | -0.3 (cross-layer collision) |
| Same register already dominant in this chapter (≥3 uses) | -0.2 |
| Same movement already dominant in this chapter (≥3 uses) | -0.15 |
| Root family already over budget in this chapter | -0.1 per root over budget |
| Same cadence used in adjacent chapter by same layer | -0.15 |
**Reward rules (add to score):**
| Condition | Reward |
|---|---|
| emotional_job_match == True | +0.3 |
| chapter_position_match == True | +0.2 |
| Shape underused in book (used < 2 times) | +0.2 |
| Register underused in this chapter (0 uses) | +0.15 |
| Movement underused in this chapter (0 uses) | +0.15 |
| Root family underused in chapter | +0.1 |
| topic_relevance > 0.5 | +0.1 × topic_relevance |
**`select_best_candidate()` function:**
```python
def select_best_candidate(
candidates: list[RhetoricalCandidate],
memory: RhetoricalMemory,
chapter_index: int,
taxonomy: dict[str, Any],
*,
salt: str = "",
) -> RhetoricalCandidate | None:
"""
Score all candidates and return the best one.
Ties broken by deterministic hash using salt.
Returns None if candidates list is empty.
"""

**`load_rhetorical_taxonomy()` function:**
```python
_TAXONOMY_CACHE: dict[str, Any] | None = None

def load_rhetorical_taxonomy() -> dict[str, Any]:
"""Load config/rendering/rhetorical_style_taxonomy.yaml with cache."""

### D. Integration contract — how the four subsystems will use this
Each subsystem workstream will:
1. Import `RhetoricalMemory`, `RhetoricalCandidate`, `select_best_candidate`, `load_rhetorical_taxonomy`
2. Tag their YAML entries with taxonomy fields (shape, register, movement, etc.)
3. Build `RhetoricalCandidate` objects from their YAML entries
4. Call `select_best_candidate()` instead of hash-picking
5. Call `memory.record_selection()` after each pick
**The four subsystems do NOT need to be modified in this workstream.** This workstream builds the shared infrastructure. The subsystem workstreams will import from it.
**Single book render integration point:** In `compose_from_enriched_book()` (chapter_composer.py:799), the caller will create ONE `RhetoricalMemory` instance and pass it to all four subsystem memory objects. Each subsystem memory wraps the shared `RhetoricalMemory` for cross-layer awareness. This wiring happens in the subsystem workstreams, not here.
### E. Chapter rhetorical profile for quality_summary
Add a function that the book renderer can call after each chapter to get the profile:
```python
def build_chapter_rhetorical_audit(
memory: RhetoricalMemory,
chapter_index: int,
) -> dict[str, Any]:
"""
Build audit payload for quality_summary.json.

Returns dict like:
{
    "chapter_index": 3,
    "shapes_used": {"quiet_compression": 2, "causal_turn": 1, ...},
    "registers_used": {"somatic": 3, "plain": 1, ...},
    "movements_used": {"explaining": 2, "landing": 1, ...},
    "dominant_roots": ["body", "pattern"],
    "cross_layer_collisions": ["quiet_compression in environment AND bridge"],
    "shape_diversity": 5,
    "movement_diversity": 3,
    "budget_warnings": ["max_same_shape_across_layers exceeded: quiet_compression=3"]
}
"""
This integrates with the existing `governance_report` / `quality_summary.json` pipeline. The subsystem workstreams will wire the call; this workstream just provides the function.
---
## Non-goals
- Do NOT modify `chapter_composer.py`, `golden_chapter_synthesis.py`, or `book_renderer.py` — those are handled by the four subsystem workstreams
- Do NOT create the four layer-specific YAML configs (environment_fallback_families.yaml, bridge_transition_families.yaml, mechanism_thesis_families.yaml, exercise_wrapper_families.yaml) — those are handled by subsystem workstreams
- Do NOT implement series-level persistent memory beyond a stub — book-level is Phase 1 priority
- Do NOT add randomization for its own sake — this is controlled rhetorical distribution, not noise
- Do NOT sacrifice clarity for variation — clarity > variation, usefulness > novelty
## Important design constraint
The scorer must be **deterministic given the same inputs and memory state**. Use hash-based tiebreaking, not random. This ensures reproducible renders.
---
## Tests
### `tests/test_rhetorical_memory.py` (new file)
1. `record_selection()` correctly tracks phrases, stems, roots, shapes across layers
2. `is_phrase_used_in_book()` returns True after recording, False before
3. `stem_count_in_window()` correctly counts within rolling window
4. `shape_count_in_window()` counts across all layers (not just one)
5. `root_family_density()` correctly aggregates roots from taxonomy families
6. `start_chapter()` resets per-chapter transient state
7. `chapter_shape_diversity()` returns correct count of distinct shapes
8. `chapter_movement_diversity()` returns correct count
9. `get_chapter_profile()` correctly identifies cross-layer collisions (e.g., same shape in environment + bridge)
10. `get_chapter_profile()` correctly generates budget_warnings when thresholds exceeded
11. Memory works correctly across 12 synthetic chapters with mixed layer recordings
### `tests/test_rhetorical_scorer.py` (new file)
1. `score_candidate()` returns -1.0 (or very low) for exact phrase already used in book
2. `score_candidate()` penalizes same stem used in recent chapters
3. `score_candidate()` penalizes cross-layer shape collision (same shape already used in current chapter by different layer)
4. `score_candidate()` rewards emotional_job_match
5. `score_candidate()` rewards underused shapes
6. `select_best_candidate()` returns the highest-scoring candidate
7. `select_best_candidate()` is deterministic (same inputs → same output)
8. `select_best_candidate()` returns None for empty list
9. `load_rhetorical_taxonomy()` loads YAML correctly and caches
10. `load_rhetorical_taxonomy()` returns sensible defaults when YAML missing
11. Two candidates with same score are tiebroken deterministically by salt
12. Scoring produces measurably different rankings for diverse vs homogeneous candidate sets
13. `build_chapter_rhetorical_audit()` produces valid audit dict with expected keys
---
## Acceptance criteria
1. `python3 -m py_compile phoenix_v4/rendering/rhetorical_memory.py` passes
2. `python3 -m py_compile phoenix_v4/rendering/rhetorical_scorer.py` passes
3. `python3 -m py_compile tests/test_rhetorical_memory.py` passes
4. `python3 -m py_compile tests/test_rhetorical_scorer.py` passes
5. `PYTHONPATH=. pytest tests/test_rhetorical_memory.py -v` — all pass
6. `PYTHONPATH=. pytest tests/test_rhetorical_scorer.py -v` — all pass
7. `PYTHONPATH=. pytest tests/ -v` — no regressions in existing tests
8. `config/rendering/rhetorical_style_taxonomy.yaml` exists and is valid YAML with all taxonomy fields
9. `RhetoricalMemory` correctly detects cross-layer shape collisions
10. `select_best_candidate()` is deterministic
11. `build_chapter_rhetorical_audit()` produces a dict that could be embedded in quality_summary.json
12. Push-guard and preflight pass
## Branch
```bash
git fetch origin
git checkout -b agent/unified-rhetorical-architecture-20260416 origin/main

Emit CLOSEOUT_RECEIPT when done.

You are Pearl_Architect + Pearl_Dev. Read these files before any work:
1. docs/SESSION_UNITY_PROTOCOL.md
2. phoenix_v4/rendering/chapter_composer.py (957 lines — full file)
3. phoenix_v4/rendering/golden_chapter_synthesis.py (949 lines — focus on: _resolve_location_placeholders line 62, dedupe_scene_furniture_book line 774, audit_repeated_phrases line 809, build_golden_chapter_report_payload line 853)
4. phoenix_v4/rendering/book_renderer.py (focus on: strengthen_rendered_spine_manuscript, governance_report usage, quality_summary output)
5. phoenix_v4/planning/chapter_planner.py (ChapterContract line 59, emotional_job values)
6. config/source_of_truth/chapter_purpose_contracts.yaml
7. artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
8. docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
STARTUP_RECEIPT
AGENT:              Pearl_Architect + Pearl_Dev
TASK:               Build unified rhetorical anti-repetition architecture — shared taxonomy, cross-layer memory, chapter-level orchestration
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;specs/PHOENIX_V4_5_WRITER_SPEC.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/SESSION_UNITY_PROTOCOL.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        config/rendering/rhetorical_style_taxonomy.yaml;phoenix_v4/rendering/rhetorical_memory.py;phoenix_v4/rendering/rhetorical_scorer.py;tests/test_rhetorical_memory.py;tests/test_rhetorical_scorer.py;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       atoms/;SOURCE_OF_TRUTH/;scripts/localization/;config/localization/;phoenix_v4/rendering/chapter_composer.py;phoenix_v4/rendering/golden_chapter_synthesis.py;phoenix_v4/rendering/book_renderer.py (these three files will be wired by SEPARATE follow-up workstreams — this workstream builds the shared infrastructure only)
BLOCKERS:           none
READY_STATUS:       ready
## Context
Four anti-repetition subsystems are being built in parallel workstreams:
| Layer | Config file | Primary target file | Memory class |
|---|---|---|---|
| 1. Environment fallback | `config/rendering/environment_fallback_families.yaml` | `golden_chapter_synthesis.py` → `_resolve_location_placeholders()` | `EnvironmentPhraseMemory` |
| 2. Bridge/transition | `config/rendering/bridge_transition_families.yaml` | `chapter_composer.py` → `_bridge_after_opening()`, etc. | `BridgeMemory` |
| 3. Mechanism/thesis | `config/rendering/mechanism_thesis_families.yaml` | `chapter_composer.py` → `_derive_thesis()`, `_distill_mechanism()` | `MechanismThesisMemory` |
| 4. Exercise wrapper | `config/rendering/exercise_wrapper_families.yaml` | `chapter_composer.py` → `_exercise_setup_sentence()`, etc. | `ExerciseWrapperMemory` |
Each subsystem independently improves variation. But without cross-layer coordination, you get a hidden failure mode: every layer independently converges on the same "soft, muted, explanatory, gently validating" voice. The chapters individually improve, but together they still create a consistent **generator fingerprint**.
**This workstream builds the shared infrastructure that the four subsystems will plug into.** It does NOT modify the four target files — it provides the taxonomy, memory, and scorer that they will import.
## What already exists in the codebase
- `audit_repeated_phrases()` (golden_chapter_synthesis.py:809) — counts 4-gram repetition in chapter text, reports PASS/WARN
- `dedupe_scene_furniture_book()` (golden_chapter_synthesis.py:774) — post-hoc caps on known repeated signatures
- `governance_report` dict — threaded through book render, collects `recurrence_report`, `frame_governance_chapters`, etc.
- `quality_summary.json` — written by book_renderer after render
- `ChapterContract.emotional_job` — canonical values: recognition, mechanism, deepening, reframe, practice, integration, resolution
## What to build
### A. `config/rendering/rhetorical_style_taxonomy.yaml`
The shared vocabulary that all four layer configs will reference. Each candidate line in any layer YAML should be taggable with fields from this taxonomy.
**Required taxonomy fields:**
```yaml
schema_version: 1

Every candidate entry in any layer YAML can be tagged with these fields.
The shared scorer uses these tags for cross-layer anti-repetition.
shapes:

direct_assertion
quiet_compression
embodied_noticing
causal_turn
contrast_turn
question_turn
forward_pull
permission_turn
data_framing
sensory_observation
object_grounding
systems_explanation
validation_line
reversal_explanation
implication_turn
evidence_turn
registers:

plain
warm
clinical_light
somatic
reflective
quiet_authoritative
soft_guiding
compressed
emotionally_open
movements:

naming
explaining
deepening
reframing
guiding
landing
validating
forwarding
instruction_tones:

directive
gentle_directive
permissive
observational
interpretive
non_grading
cadences:

short_clean
two_clause_balance
compression_then_release
long_then_short
question_then_answer
single_beat
abstraction_levels:

concrete
mid
abstract
Root noun families that create fingerprinting when over-concentrated
tracked_root_families:
somatic: [body, breath, chest, jaw, throat, shoulder, sternum, nervous system]
cognitive: [mind, thought, explanation, understanding, pattern, mechanism]
temporal: [moment, next, now, before, after, already]
spatial: [room, window, glass, light, outside, desk, screen]
emotional: [feeling, alarm, cost, shift, notice, permission]
action: [practice, move, try, start, begin, continue]
meta: [chapter, point, story, question, answer]

Chapter-level diversity budgets (soft targets, not hard gates)
chapter_rhetorical_budget:
max_same_shape_across_layers: 2 # e.g., don't use quiet_compression in environment AND bridge AND mechanism
max_same_register_across_layers: 3
max_same_root_family_per_chapter: 4 # e.g., max 4 "somatic" roots in one chapter across all layers
min_shape_diversity_per_chapter: 4 # at least 4 distinct shapes across the chapter's rhetorical lines
min_movement_diversity_per_chapter: 3 # at least 3 distinct movements

### B. `phoenix_v4/rendering/rhetorical_memory.py` (new module)
The shared cross-layer memory system. All four per-layer memory classes will delegate to this.
```python
"""
Unified rhetorical anti-repetition memory.

All four layer-specific memory classes (EnvironmentPhraseMemory, BridgeMemory,
MechanismThesisMemory, ExerciseWrapperMemory) delegate cross-layer tracking here.

This module provides:

RhetoricalMemory: book-level + optional series-level tracking
ChapterRhetoricalProfile: per-chapter diversity audit
cross-layer anti-repetition rules
"""
**`RhetoricalMemory` class:**
```python
class RhetoricalMemory:
"""Tracks rhetorical usage across all four layers for one book render."""

**Must track (per book):**
- `phrases_used: dict[str, list[int]]` — exact phrase → list of chapter indices where used
- `stems_used: dict[str, list[int]]` — stem → chapter indices
- `roots_used: dict[str, dict[str, int]]` — root → {chapter_index: count}
- `shapes_used: dict[str, list[int]]` — shape → chapter indices
- `registers_used: dict[str, list[int]]` — register → chapter indices
- `movements_used: dict[str, list[int]]` — movement → chapter indices
- `instruction_tones_used: dict[str, list[int]]` — tone → chapter indices
- `cadences_used: dict[str, list[int]]` — cadence → chapter indices
- `layer_usage: dict[str, dict[str, list[int]]]` — layer_name → {shape/register/etc → chapter indices}
**Must track (per chapter, transient):**
- `current_chapter_shapes: list[str]` — shapes used so far in current chapter (across all layers)
- `current_chapter_registers: list[str]`
- `current_chapter_movements: list[str]`
- `current_chapter_roots: dict[str, int]` — root → count in current chapter
- `current_chapter_layer_shapes: dict[str, list[str]]` — layer_name → shapes used
**Key methods:**
```python
def record_selection(
self,
*,
layer: str, # "environment" | "bridge" | "mechanism_thesis" | "exercise_wrapper"
chapter_index: int,
phrase: str,
stems: list[str],
roots: list[str],
shape: str,
register: str = "",
movement: str = "",
instruction_tone: str = "",
cadence: str = "",
) -> None:
"""Record a selection from any layer."""

def is_phrase_used_in_book(self, phrase: str) -> bool:
"""Exact phrase already used anywhere in this book."""

def stem_count_in_window(self, stem: str, chapter_index: int, window: int = 4) -> int:
"""How many times this stem appeared in the last window chapters."""

def shape_count_in_window(self, shape: str, chapter_index: int, window: int = 3) -> int:
"""How many times this shape appeared in the last window chapters (across all layers)."""

def root_family_density(self, root_family: str, chapter_index: int) -> int:
"""How many roots from this family are in the current chapter."""

def chapter_shape_diversity(self, chapter_index: int) -> int:
"""Number of distinct shapes used in this chapter so far."""

def chapter_movement_diversity(self, chapter_index: int) -> int:
"""Number of distinct movements used in this chapter so far."""

def start_chapter(self, chapter_index: int) -> None:
"""Reset per-chapter transient state."""

def get_chapter_profile(self, chapter_index: int) -> "ChapterRhetoricalProfile":
"""Build audit profile for this chapter."""

**`ChapterRhetoricalProfile` dataclass:**
```python
@dataclass
class ChapterRhetoricalProfile:
chapter_index: int
shapes_used: dict[str, int] # shape → count
registers_used: dict[str, int]
movements_used: dict[str, int]
dominant_roots: list[str] # root families with count > budget
cross_layer_collisions: list[str] # e.g., "quiet_compression used in environment AND bridge"
shape_diversity: int
movement_diversity: int
budget_warnings: list[str] # which budget thresholds were exceeded

def to_dict(self) -> dict[str, Any]: ...
**`SeriesRhetoricalMemory` class (optional, for later):**
```python
class SeriesRhetoricalMemory:
"""Persistent series-level tracking across multiple book renders."""

For Phase 1, this can be a stub that loads/saves from `artifacts/render_memory/rhetorical_memory.json`. The four subsystem workstreams don't need series memory yet — book-level is the priority.
### C. `phoenix_v4/rendering/rhetorical_scorer.py` (new module)
The shared scoring engine that all four layer selectors will call.
```python
"""
Shared rhetorical candidate scorer.

Each layer-specific selector (environment, bridge, mechanism/thesis, exercise wrapper)
calls score_candidate() to get a cross-layer-aware score for a candidate line.
The highest-scoring candidate wins.
"""

**`RhetoricalCandidate` dataclass:**
```python
@dataclass
class RhetoricalCandidate:
"""A candidate line from any layer, with taxonomy tags."""
text: str
layer: str # "environment" | "bridge" | "mechanism_thesis" | "exercise_wrapper"
stems: list[str]
roots: list[str]
shape: str
register: str = ""
movement: str = ""
instruction_tone: str = ""
cadence: str = ""
emotional_job_match: bool = True
chapter_position_match: bool = True
topic_relevance: float = 1.0

**`score_candidate()` function:**
```python
def score_candidate(
candidate: RhetoricalCandidate,
memory: RhetoricalMemory,
chapter_index: int,
taxonomy: dict[str, Any],
) -> float:
"""
Score a candidate line for selection, incorporating cross-layer anti-repetition.

Returns a float score. Higher = better candidate.
Base score starts at 1.0, penalties subtract, rewards add.
"""
**Penalty rules (subtract from score):**
| Condition | Penalty |
|---|---|
| Exact phrase already used in book | -1.0 (effectively eliminates) |
| Same stem used in last 4 chapters | -0.4 per occurrence |
| Same shape used in last 3 chapters (any layer) | -0.2 per occurrence |
| Same shape already used in THIS chapter by ANOTHER layer | -0.3 (cross-layer collision) |
| Same register already dominant in this chapter (≥3 uses) | -0.2 |
| Same movement already dominant in this chapter (≥3 uses) | -0.15 |
| Root family already over budget in this chapter | -0.1 per root over budget |
| Same cadence used in adjacent chapter by same layer | -0.15 |
**Reward rules (add to score):**
| Condition | Reward |
|---|---|
| emotional_job_match == True | +0.3 |
| chapter_position_match == True | +0.2 |
| Shape underused in book (used < 2 times) | +0.2 |
| Register underused in this chapter (0 uses) | +0.15 |
| Movement underused in this chapter (0 uses) | +0.15 |
| Root family underused in chapter | +0.1 |
| topic_relevance > 0.5 | +0.1 × topic_relevance |
**`select_best_candidate()` function:**
```python
def select_best_candidate(
candidates: list[RhetoricalCandidate],
memory: RhetoricalMemory,
chapter_index: int,
taxonomy: dict[str, Any],
*,
salt: str = "",
) -> RhetoricalCandidate | None:
"""
Score all candidates and return the best one.
Ties broken by deterministic hash using salt.
Returns None if candidates list is empty.
"""

**`load_rhetorical_taxonomy()` function:**
```python
_TAXONOMY_CACHE: dict[str, Any] | None = None

def load_rhetorical_taxonomy() -> dict[str, Any]:
"""Load config/rendering/rhetorical_style_taxonomy.yaml with cache."""

### D. Integration contract — how the four subsystems will use this
Each subsystem workstream will:
1. Import `RhetoricalMemory`, `RhetoricalCandidate`, `select_best_candidate`, `load_rhetorical_taxonomy`
2. Tag their YAML entries with taxonomy fields (shape, register, movement, etc.)
3. Build `RhetoricalCandidate` objects from their YAML entries
4. Call `select_best_candidate()` instead of hash-picking
5. Call `memory.record_selection()` after each pick
**The four subsystems do NOT need to be modified in this workstream.** This workstream builds the shared infrastructure. The subsystem workstreams will import from it.
**Single book render integration point:** In `compose_from_enriched_book()` (chapter_composer.py:799), the caller will create ONE `RhetoricalMemory` instance and pass it to all four subsystem memory objects. Each subsystem memory wraps the shared `RhetoricalMemory` for cross-layer awareness. This wiring happens in the subsystem workstreams, not here.
### E. Chapter rhetorical profile for quality_summary
Add a function that the book renderer can call after each chapter to get the profile:
```python
def build_chapter_rhetorical_audit(
memory: RhetoricalMemory,
chapter_index: int,
) -> dict[str, Any]:
"""
Build audit payload for quality_summary.json.

Returns dict like:
{
    "chapter_index": 3,
    "shapes_used": {"quiet_compression": 2, "causal_turn": 1, ...},
    "registers_used": {"somatic": 3, "plain": 1, ...},
    "movements_used": {"explaining": 2, "landing": 1, ...},
    "dominant_roots": ["body", "pattern"],
    "cross_layer_collisions": ["quiet_compression in environment AND bridge"],
    "shape_diversity": 5,
    "movement_diversity": 3,
    "budget_warnings": ["max_same_shape_across_layers exceeded: quiet_compression=3"]
}
"""
This integrates with the existing `governance_report` / `quality_summary.json` pipeline. The subsystem workstreams will wire the call; this workstream just provides the function.
---
## Non-goals
- Do NOT modify `chapter_composer.py`, `golden_chapter_synthesis.py`, or `book_renderer.py` — those are handled by the four subsystem workstreams
- Do NOT create the four layer-specific YAML configs (environment_fallback_families.yaml, bridge_transition_families.yaml, mechanism_thesis_families.yaml, exercise_wrapper_families.yaml) — those are handled by subsystem workstreams
- Do NOT implement series-level persistent memory beyond a stub — book-level is Phase 1 priority
- Do NOT add randomization for its own sake — this is controlled rhetorical distribution, not noise
- Do NOT sacrifice clarity for variation — clarity > variation, usefulness > novelty
## Important design constraint
The scorer must be **deterministic given the same inputs and memory state**. Use hash-based tiebreaking, not random. This ensures reproducible renders.
---
## Tests
### `tests/test_rhetorical_memory.py` (new file)
1. `record_selection()` correctly tracks phrases, stems, roots, shapes across layers
2. `is_phrase_used_in_book()` returns True after recording, False before
3. `stem_count_in_window()` correctly counts within rolling window
4. `shape_count_in_window()` counts across all layers (not just one)
5. `root_family_density()` correctly aggregates roots from taxonomy families
6. `start_chapter()` resets per-chapter transient state
7. `chapter_shape_diversity()` returns correct count of distinct shapes
8. `chapter_movement_diversity()` returns correct count
9. `get_chapter_profile()` correctly identifies cross-layer collisions (e.g., same shape in environment + bridge)
10. `get_chapter_profile()` correctly generates budget_warnings when thresholds exceeded
11. Memory works correctly across 12 synthetic chapters with mixed layer recordings
### `tests/test_rhetorical_scorer.py` (new file)
1. `score_candidate()` returns -1.0 (or very low) for exact phrase already used in book
2. `score_candidate()` penalizes same stem used in recent chapters
3. `score_candidate()` penalizes cross-layer shape collision (same shape already used in current chapter by different layer)
4. `score_candidate()` rewards emotional_job_match
5. `score_candidate()` rewards underused shapes
6. `select_best_candidate()` returns the highest-scoring candidate
7. `select_best_candidate()` is deterministic (same inputs → same output)
8. `select_best_candidate()` returns None for empty list
9. `load_rhetorical_taxonomy()` loads YAML correctly and caches
10. `load_rhetorical_taxonomy()` returns sensible defaults when YAML missing
11. Two candidates with same score are tiebroken deterministically by salt
12. Scoring produces measurably different rankings for diverse vs homogeneous candidate sets
13. `build_chapter_rhetorical_audit()` produces valid audit dict with expected keys
---
## Acceptance criteria
1. `python3 -m py_compile phoenix_v4/rendering/rhetorical_memory.py` passes
2. `python3 -m py_compile phoenix_v4/rendering/rhetorical_scorer.py` passes
3. `python3 -m py_compile tests/test_rhetorical_memory.py` passes
4. `python3 -m py_compile tests/test_rhetorical_scorer.py` passes
5. `PYTHONPATH=. pytest tests/test_rhetorical_memory.py -v` — all pass
6. `PYTHONPATH=. pytest tests/test_rhetorical_scorer.py -v` — all pass
7. `PYTHONPATH=. pytest tests/ -v` — no regressions in existing tests
8. `config/rendering/rhetorical_style_taxonomy.yaml` exists and is valid YAML with all taxonomy fields
9. `RhetoricalMemory` correctly detects cross-layer shape collisions
10. `select_best_candidate()` is deterministic
11. `build_chapter_rhetorical_audit()` produces a dict that could be embedded in quality_summary.json
12. Push-guard and preflight pass
## Branch
```bash
git fetch origin
git checkout -b agent/unified-rhetorical-architecture-20260416 origin/main

Emit CLOSEOUT_RECEIPT when done.

---

**Cursor**

I’m going to follow your startup protocol first: read all required authority/context files (including the full rendering files you listed), then create the feature branch from `origin/main`, and only then implement the shared taxonomy + memory + scorer + tests within your declared write scope.

I’ve finished the first half of required reads and I’m now reading the remaining target files (book renderer/planner/contracts/authority map/overlay spec), then I’ll run the mandated preflight and branch setup before editing.

I hit a size limit on `docs/DOCS_INDEX.md`, so I’m reading it in chunks now, and I’ll also read the additional required coordination/Git governance docs before I touch branch operations.

Context gathering is complete and I’m moving into execution: I’ll run the mandatory git preflight now, create your requested `agent/unified-rhetorical-architecture-20260416` branch from `origin/main`, then implement only the shared infrastructure files/tests in scope.

I’m starting implementation now: creating the shared taxonomy config first, then `rhetorical_memory` and `rhetorical_scorer` with deterministic scoring + audit payload support, and finally the two new test files.

I’ve added the taxonomy and memory module; I’m now finishing `rhetorical_scorer` coverage tests (determinism, penalties/rewards, cache/default behavior, and audit payload validation), then I’ll run compile + pytest + full suite checks.

I’m now running the required pytest checks: first the two new test files, then the full `tests/` suite for regression coverage.

Full regression suite is running in the background (1,757 tests collected so far); I’m monitoring it to completion and will fix anything that fails.

Quick update: the full suite is still running (now much farther along), and I already confirmed at least two early failures are in unrelated pre-existing atom coverage tests, not in the new rhetorical modules.

Implemented the shared rhetorical anti-repetition infrastructure on `agent/unified-rhetorical-architecture-20260416` within your declared scope, without modifying the out-of-scope renderer/composer wiring files.

### What I built

- Added shared taxonomy file at `config/rendering/rhetorical_style_taxonomy.yaml` with:
  - all required taxonomy fields (`shapes`, `registers`, `movements`, `instruction_tones`, `cadences`, `abstraction_levels`)
  - `tracked_root_families`
  - `chapter_rhetorical_budget` soft targets

- Added `phoenix_v4/rendering/rhetorical_memory.py`:
  - `RhetoricalMemory` with required tracking maps and per-chapter transient state
  - required API methods (`record_selection`, phrase/stem/shape/window lookups, diversity metrics, chapter lifecycle, profile builder)
  - `ChapterRhetoricalProfile` dataclass with `to_dict()`
  - `build_chapter_rhetorical_audit(memory, chapter_index)` for `quality_summary` integration payloads
  - `SeriesRhetoricalMemory` Phase-1 stub for persisted series memory
  - built-in default taxonomy fallback

- Added `phoenix_v4/rendering/rhetorical_scorer.py`:
  - `RhetoricalCandidate` dataclass
  - deterministic `score_candidate()` with your penalty/reward model
  - deterministic `select_best_candidate()` with hash tiebreaker + `salt`
  - cached `load_rhetorical_taxonomy()` with sensible defaults on missing YAML
  - exports `build_chapter_rhetorical_audit` for simple downstream use

- Added tests:
  - `tests/test_rhetorical_memory.py` (11 tests, covering all requested memory/profile behaviors)
  - `tests/test_rhetorical_scorer.py` (13 tests, covering penalties, rewards, determinism, cache/default fallback, audit payload)

- Updated workstream coordination:
  - appended completed row in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for `ws_unified_rhetorical_architecture_20260416`

### Validation run

- `python3 -m py_compile phoenix_v4/rendering/rhetorical_memory.py` ✅
- `python3 -m py_compile phoenix_v4/rendering/rhetorical_scorer.py` ✅
- `python3 -m py_compile tests/test_rhetorical_memory.py` ✅
- `python3 -m py_compile tests/test_rhetorical_scorer.py` ✅
- `PYTHONPATH=. python3 -m pytest tests/test_rhetorical_memory.py -v` ✅ (11 passed)
- `PYTHONPATH=. python3 -m pytest tests/test_rhetorical_scorer.py -v` ✅ (13 passed)
- `PYTHONPATH=. python3 -m pytest tests/ -v` ⚠️ completed with **2 failures, both pre-existing/unrelated atom coverage tests**:
  - `tests/test_atoms_coverage_100_percent.py::test_100_percent_atoms_for_all_books`
  - `tests/test_atoms_coverage_100_percent.py::test_100_percent_non_story_atoms_for_all_books`
- `PYTHONPATH=. python3 scripts/git/push_guard.py` ✅
- `bash scripts/ci/preflight_push.sh` ✅

CLOSEOUT_RECEIPT
AGENT:          Pearl_Architect + Pearl_Dev
TASK:           Build unified rhetorical anti-repetition architecture — shared taxonomy, cross-layer memory, chapter-level orchestration
COMMIT_SHA:     no commits
FILES_WRITTEN:  config/rendering/rhetorical_style_taxonomy.yaml;phoenix_v4/rendering/rhetorical_memory.py;phoenix_v4/rendering/rhetorical_scorer.py;tests/test_rhetorical_memory.py;tests/test_rhetorical_scorer.py;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md;phoenix_v4/rendering/chapter_composer.py;phoenix_v4/rendering/golden_chapter_synthesis.py;phoenix_v4/rendering/book_renderer.py;phoenix_v4/planning/chapter_planner.py;config/source_of_truth/chapter_purpose_contracts.yaml;artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
STATUS:         completed
HANDOFF_TO:     none
NEXT_ACTION:    Wire `RhetoricalMemory` + scorer imports into the four subsystem workstreams and hook chapter audit payload into existing `governance_report`/`quality_summary` emission path.

