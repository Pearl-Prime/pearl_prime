# Environment fallback system implementation
_Exported on 4/16/2026 at 19:20:25 GMT+8 from Cursor (3.1.15)_

---

**User**

You are Pearl_Dev. Read these files before any work:
1. docs/SESSION_UNITY_PROTOCOL.md
2. phoenix_v4/rendering/golden_chapter_synthesis.py (full file, 949 lines)
3. tests/test_golden_chapter_synthesis.py
4. artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
5. docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
STARTUP_RECEIPT
AGENT:              Pearl_Dev
TASK:               Replace hardcoded location fallback map with rich ambient environment family system (Phase 1 + Phase 2)
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;specs/PHOENIX_V4_5_WRITER_SPEC.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/SESSION_UNITY_PROTOCOL.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        config/rendering/environment_fallback_families.yaml;phoenix_v4/rendering/golden_chapter_synthesis.py;tests/test_golden_chapter_synthesis.py;tests/test_environment_fallback.py;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       atoms/;SOURCE_OF_TRUTH/;scripts/localization/;config/localization/
BLOCKERS:           none
READY_STATUS:       ready
## Problem
In `phoenix_v4/rendering/golden_chapter_synthesis.py`, the function `_resolve_location_placeholders()` (line 62) hardcodes a tiny fallback vocabulary:
```python
replacements = {
"{weather_detail}": "Gray daylight filters in",
"{street_name}": "The street",
"{transit_line}": "train",
}

Plus ~10 regex-based repair rules that all produce the same "traffic / street below / gray daylight" phrases.
This causes every rendered book to repeat the same 3–5 ambient phrases across all chapters. For a 10-book series of 6-hour books, the repetition is immediately visible to human readers.
The secondary function `dedupe_scene_furniture_book()` (line 774) tries to cap overused phrases post-hoc, but only knows 5 signature strings. This treats the symptom, not the cause.
Location is intentionally NOT a focus of these books. The fix is NOT to add real locations. The fix is to make the fallback system rich enough that missing location placeholders resolve into varied, ambient, authored-feeling sensory detail.
## What to build — Phase 1 + Phase 2 combined
### A. Create `config/rendering/environment_fallback_families.yaml`
Define 6 families with structured metadata. Target: 250–400 total entries across all families and shapes.
**Families:**
1. **light_ambient** (40–60 entries) — for `{weather_detail}` and window-light placeholders
2. **outside_sound** (40–60 entries) — for `{street_name}` and exterior references
3. **interior_building** (30–50 entries) — for place-light spatial texture
4. **motion_transit** (30–50 entries) — for `{transit_line}` and movement references
5. **object_grounding** (60–100 entries) — highest priority family. Carries specificity without place. Examples: "the cursor waiting where you left it", "a coffee ring drying on the coaster", "the badge still in your pocket"
6. **window_reference** (25–40 entries) — visual edge framing without "the street"
**Each entry must have structured metadata:**
```yaml
families:
light_ambient:
entries:
- text: "muted light at the window"
shape: fragment
roots: ["light", "window"]
scene_bias: ["window", "glass"]
intensity: low
- text: "Muted light gathers at the window."
shape: sentence
roots: ["light", "window"]
scene_bias: ["window", "glass"]
intensity: low

**Required shapes per family (at least 3 of these per concept):**
- `fragment` — "muted light at the window"
- `sentence` — "Muted light gathers at the window."
- `embedded_clause` — "with muted light at the window"
- `object_led` — "The window holds a muted wash of light."
- `environment_led` — "The room is lit in a muted, colorless way."
- `motion_led` — "Light shifts faintly across the glass."
**object_grounding should be the largest family** because it hides repetition better than light/window/outside families and creates specificity without place dependency.
### B. Replace `_resolve_location_placeholders()` in `golden_chapter_synthesis.py`
Replace lines 62–96 with a family-based resolver. Add these new components:
**1. YAML loader with cache:**
```python
def _load_environment_fallback_families() -> dict[str, Any]

Loads from `config/rendering/environment_fallback_families.yaml`. Caches in module global.
**2. Placeholder-to-family mapping:**
- `{weather_detail}` → `light_ambient`
- `{street_name}` → `outside_sound` or `window_reference`
- `{transit_line}` → `motion_transit`
- Broken merge phrases ("street below", "is there below") → `outside_sound`
**3. Context-aware family ordering:**
Inspect nearby text to bias family choice:
- desk/keyboard/screen/monitor/cursor → favor `object_grounding`, `light_ambient`
- window/glass/outside → favor `window_reference`, `outside_sound`
- hallway/elevator/office/carpet/room → favor `interior_building`
- ride/doors/platform/movement → favor `motion_transit`
**4. EnvironmentPhraseMemory class (Phase 2 core):**
```python
class EnvironmentPhraseMemory:
"""Tracks phrase usage across chapter and book scope for anti-reuse."""

Tracks:
- exact phrases used (book-wide)
- family counts per chapter window
- dominant root nouns used recently
- shape counts
**Anti-reuse rules:**
- **Book-level:** exact phrase max 1 use/book. Same family max 2 uses in 3 adjacent chapters. Same dominant root (light, window, glass, room, outside, movement) max 3 uses in 4 chapters. Same shape max 2 in adjacent chapters.
- **Chapter-level:** never repeat exact fallback phrase in same chapter. Do not use same family in adjacent paragraphs. Do not reuse same root nouns too close together.
**5. Scorer-based selection (not random pick):**
Score all candidates and choose the best low-repetition candidate. Scoring factors:
- Subtract: exact phrase already used, root repeated recently, family used in previous paragraph/chapter, same shape used recently
- Add: underused family, underused shape, good scene-context match, novel roots
**6. Chapter-phase awareness:**
- Chapters 1–3: sharper sensory edges, object tension, desk/screen/threshold cues
- Chapters 4–8: plainer grounding, sound/room/body-contact cues
- Chapters 9–12: spacious, quieter, less externally vivid, integration-supportive
**7. The replacement function signature:**
```python
def _resolve_location_placeholders(
text: str,
*,
phrase_memory: EnvironmentPhraseMemory | None = None,
chapter_index: int = 0,
) -> str:

The `phrase_memory` parameter is optional so all existing callers still work without changes. When `None`, create a temporary memory (no book-level tracking — preserves backward compat). When passed, enables full anti-reuse.
**8. Wire memory through existing call sites:**
The function is called at lines 108, 146, 159, 165, 724, and 911. The book-level caller is around line 911 in the render flow. Create the `EnvironmentPhraseMemory` at book render start and thread it through the chapter loop. For the standalone extraction calls (lines 108, 146, 159), memory=None is fine.
### C. Update `dedupe_scene_furniture_book()` (line 774)
Keep as safety net but expand the signatures tuple to include the new family phrases that might still occasionally repeat. Add the top 2–3 entries from each family. This function should fire much less often with the new system.
### D. Tests — `tests/test_environment_fallback.py` (new file)
**Unit tests:**
1. `{weather_detail}` does not always resolve to the same phrase (run 10 times with different surrounding text)
2. `{street_name}` never resolves to raw "The street"
3. `{transit_line}` never resolves to bare "train"
4. Same fallback phrase is not reused within one synthetic 12-chapter book render
5. Context with desk/screen biases toward object_grounding or light_ambient family
6. Context with hallway/elevator biases toward interior_building family
7. Context with window/glass biases toward window_reference or outside_sound family
8. EnvironmentPhraseMemory correctly blocks repeated exact phrases
9. EnvironmentPhraseMemory correctly limits same-family density across chapter window
10. Chapter-phase awareness produces different family distributions for ch1 vs ch8 vs ch12
**Regression tests:**
11. Existing broken merge phrases ("street below is there below") resolve cleanly
12. Output remains grammatical (no empty replacements, no double spaces)
13. Function still works with `phrase_memory=None` (backward compat)
14. YAML config missing → graceful fallback to hardcoded defaults (not crash)
**Update existing tests in `tests/test_golden_chapter_synthesis.py`:**
- `test_dedupe_scene_furniture_book_caps_phrase` should still pass
- Add test that `_resolve_location_placeholders` output does not contain "Gray daylight filters in" when called with diverse input texts
### E. Non-goals
- Do NOT add city-specific or region-specific language
- Do NOT require geodata or real location names
- Do NOT turn scenes into place-description passages
- Do NOT modify any files outside WRITE_SCOPE
- Do NOT touch locale/translation code
## Acceptance criteria
1. `python3 -m py_compile phoenix_v4/rendering/golden_chapter_synthesis.py` passes
2. `python3 -m py_compile tests/test_environment_fallback.py` passes
3. `PYTHONPATH=. pytest tests/test_environment_fallback.py -v` — all pass
4. `PYTHONPATH=. pytest tests/test_golden_chapter_synthesis.py -v` — all existing tests still pass
5. `config/rendering/environment_fallback_families.yaml` has ≥250 total entries across families
6. No output of the resolver contains "Gray daylight filters in", "The street" (bare), or "train" (bare) when the YAML is loaded
7. Running the anxiety pilot shows varied ambient language across chapters:
PYTHONPATH=. python3 scripts/run_pipeline.py
--no-job-check --pipeline-mode spine
--topic anxiety --persona gen_z_professionals
--arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__false_alarm__F006.yaml
--runtime-format short_book_30 --render-book
--render-dir /tmp/env-fallback-pilot
--golden-chapter-pilot 1 --quality-profile draft

8. Push-guard and preflight pass
## Branch
```bash
git fetch origin
git checkout -b agent/environment-fallback-system-20260416 origin/main

Emit CLOSEOUT_RECEIPT when done.



when done. pr and merge safely

---

**Cursor**

Understood — I’ll first read the five required files in full, then implement the environment family system in the scoped files, run the requested compile/tests/preflight flow, and finish with a safe PR + merge plus a closeout receipt. I’m starting by loading those required docs/code now.

I’ve loaded the protocol/spec/map; two required files weren’t found at the exact paths you gave, so I’m locating their actual paths now and will read them fully before editing.

I found the target file only under a git worktree (`.claude/worktrees/relaxed-tesla/...`), not at repo root. I’m now verifying active worktree/branch so I can apply changes in the correct checkout and keep the git/PR flow safe.

I’ve identified the target code in the active worktree and will proceed there on the requested branch base. I’m now reading the full synthesis/test files from that worktree plus `ACTIVE_WORKSTREAMS.tsv` to satisfy protocol before edits.

STARTUP_RECEIPT
AGENT:              Pearl_Dev
TASK:               Replace hardcoded location fallback map with rich ambient environment family system (Phase 1 + Phase 2)
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md;specs/PHOENIX_V4_5_WRITER_SPEC.md;docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;docs/SESSION_UNITY_PROTOCOL.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        config/rendering/environment_fallback_families.yaml;phoenix_v4/rendering/golden_chapter_synthesis.py;tests/test_golden_chapter_synthesis.py;tests/test_environment_fallback.py;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       atoms/;SOURCE_OF_TRUTH/;scripts/localization/;config/localization/
BLOCKERS:           none
READY_STATUS:       ready

I’m now loading the required Git/GitHub governance docs for this worktree, then I’ll create the requested branch from `origin/main` and start implementing the resolver + tests.

I hit a blocker in the current checkout: it already has many unrelated staged/unstaged files, so it’s not safe for the scoped branch work. I’m creating a fresh worktree directly from `origin/main` on your requested branch so I can proceed without touching those unrelated changes.

I’m in a clean branch/worktree now and confirmed the target paths; next I’m implementing in three steps: generate the new YAML family catalog (250+ entries), replace the resolver with cached/context-scored memory-aware selection, then add/adjust tests (including new `tests/test_environment_fallback.py`) before running the full compile/pytest/pipeline/preflight flow.

The resolver replacement is in; I’m now validating the inserted block and threading `phrase_memory/chapter_index` through call sites (`_strip_slot_artifacts`, sanitizer path, and pilot flow) plus dedupe signature updates.

I’ve added the new YAML catalog and initial resolver/memory/test wiring; next I’m running compile/tests now to catch syntax/logic issues, then I’ll tighten any failing heuristics before final validation and PR flow.

I’ve finished implementation and validation (compile, both pytest suites, and the anxiety spine pilot all pass). I’m now preparing the commit in this clean branch, then I’ll push, open a PR, run the local pre-merge governance checks, and merge safely.

