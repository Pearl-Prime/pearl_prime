# Pearl Prime Whole-Workflow Hardening Spec

**Purpose:** Turn Pearl Prime from "the pipeline can run" into "the pipeline can reliably produce the right book, with the right identity, quality, and guardrails, from one CLI entrypoint."  
**Status:** Execution spec for dev hardening work.  
**Merged runtime (Pearl Prime recovery PR #67 + PR #74 on `origin/main`, 2026-03):** `run_pipeline.py` exposes `--location` with governed render location profiles; `book_renderer` enforces page-one location grounding (`LocationGroundingError`, default `enforce_location_grounding`) and integrates `compose_chapter_prose` / `chapter_composer`; flow gates run on composed+cleaned text; `bestseller_editor`, `slot_resolver`, and `assembly_compiler` carry the PR #74 composition/editorial path. §1 below is a **2026-03-28** sentinel observation log. If it conflicts with current `main`, treat **§3 Desired end state** plus the code on `main` as authoritative for what is merged; §1 remains historical evidence of why hardening was required.  
**Authority:** [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md), [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md), [docs/PEARL_PRIME_RELEASE_CONTRACT.md](./PEARL_PRIME_RELEASE_CONTRACT.md), [docs/PEARL_PRIME_100_PERCENT_DEV_PLAN.md](./PEARL_PRIME_100_PERCENT_DEV_PLAN.md), [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md), [docs/TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md), [docs/V4_FEATURES_SCALE_AND_KNOBS.md](./V4_FEATURES_SCALE_AND_KNOBS.md).

---

## 1. Why this spec exists

Pearl Prime has strong architecture, many gates, and a functioning CLI, but a real user-style request can still miss the intended outcome.

Verified 2026-03-28 from a live CLI attempt:

```bash
python3 scripts/run_pipeline.py \
  --topic overthinking \
  --persona gen_z_professionals \
  --series overthinking \
  --angle analysis_paralysis \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__overthinking__spiral__F006.yaml \
  --teacher ahjan \
  --disable-v4-freeze \
  --runtime-format standard_book \
  --structural-format F006 \
  --out artifacts/user_runs/gen_z_nyc_overthinking_teacher_mode/plan.json \
  --render-book
```

Observed failure modes:

1. **Teacher Mode failed at coverage gate** — [artifacts/teacher_coverage_report.json](../artifacts/teacher_coverage_report.json) shows `HOOK`, `SCENE`, `REFLECTION`, `COMPRESSION`, and `INTEGRATION` shortages for `ahjan`.
2. **Topic identity drifted** — `overthinking` was aliased to `anxiety` via [config/identity_aliases.yaml](../config/identity_aliases.yaml), so the final fallback compile did not stay tightly on the requested topic.
3. **Location was not first-class in the sentinel run** — the logged command did not use `--location`; rendered prose used generic fallbacks from [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py), producing repeated lines like `gray light through the window`. **Current `main`** wires `--location`, profiles, and grounding enforcement (PR #67); generic fallback can still appear when inputs or profile coverage are missing—the hardening goal is honest failure, not silent generic prose.
4. **Editorial/bestseller quality did not block output** — the rendered fallback produced [chapter_flow_report.json](../artifacts/user_runs/gen_z_nyc_overthinking_book_cli/rendered/chapter_flow_report.json) with all 12 chapters failing, but the CLI still produced a book when the word-count gate was bypassed.
5. **Aha/integration craft was present in code but absent in output** — [phoenix_v4/exercises/overlay_substitution.py](../phoenix_v4/exercises/overlay_substitution.py) defines `aha_noticing` and integration callout rules, but the rendered book did not surface those patterns.
6. **One-hour runtime accuracy was not achieved** — [budget.json](../artifacts/user_runs/gen_z_nyc_overthinking_book_cli/rendered/budget.json) reported `4,798` words against the `standard_book` target of `9,000–11,000`.

This spec hardens the workflow around those exact failures.

---

## 2. Scope

This spec covers:

- the Pearl Prime CLI path in [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- Stage 1 identity resolution
- teacher readiness vs compile reality
- location grounding for rendered prose
- editorial/bestseller enforcement in the render path
- aha/integration exercise surface quality
- runtime-length truthfulness and preflight
- plan/output metadata completeness

This spec does **not** cover:

- writing new STORY atom libraries from scratch
- filling teacher banks with new content by hand
- brand-admin / Pearl News / manga / GitHub governance work
- changing the canonical arc-first architecture

Content creation may still be needed later. This spec is the dev hardening needed so the system either produces the right book or fails honestly and early.

---

## 3. Desired end state

For a real request like:

- Pearl Prime
- Teacher Mode
- one-hour book
- Gen Z
- New York City
- overthinking

the system must do one of two things:

1. **Produce the intended book cleanly**
   - requested topic preserved
   - location grounded in actual prose, not generic repeated fallback
   - teacher mode genuinely active if requested
   - book-pass/editorial gates green
   - runtime target met or within governed tolerance

2. **Fail early with an honest reason**
   - missing teacher slot coverage
   - topic has no compile-safe pool
   - location pack unavailable
   - estimated word budget cannot meet requested runtime
   - editorial gates fail

It must never silently produce the wrong topic, generic location prose, or a low-quality short book that still looks like success.

---

## 4. Sentinel acceptance tuple

All hardening in this spec must be proven against one sentinel request:

- `topic`: `overthinking`
- `persona`: `gen_z_professionals`
- `location`: `nyc_metro`
- `teacher`: `ahjan`
- `arc`: `config/source_of_truth/master_arcs/gen_z_professionals__overthinking__spiral__F006.yaml`
- `runtime`: `standard_book`
- `structural`: `F006`
- `angle`: `analysis_paralysis`

This tuple is intentionally demanding. If it cannot yet pass, the system must refuse cleanly with actionable diagnostics.

---

## 5. Workstreams

### 5A. Identity integrity: requested topic must not silently drift

**Problem:** `overthinking` currently aliases to `anxiety`, which allows the system to compile a different conceptual book than the user requested.

**Required changes**

1. Preserve both:
   - `requested_topic_id`
   - `canonical_topic_id`
2. If the requested topic differs from the canonical compile topic, the plan/output must say so explicitly.
3. Add a strict mode for explicit topic requests:
   - if user requests `overthinking` and the system would collapse it to `anxiety`, either:
     - resolve through a governed `overthinking` topic path, or
     - fail before compile with a clear topic-collapse error
4. Do not silently mix a topic-specific arc with a broader canonical atom pool without explicit plan metadata and warning/failure.

**Likely files**

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [config/identity_aliases.yaml](../config/identity_aliases.yaml)
- [phoenix_v4/planning/catalog_planner.py](../phoenix_v4/planning/catalog_planner.py)
- [phoenix_v4/planning/schema_v4.py](../phoenix_v4/planning/schema_v4.py)
- tests around alias resolution and plan serialization

**Acceptance**

- plan JSON contains `requested_topic_id` and `canonical_topic_id`
- explicit topic mismatch is impossible to miss
- sentinel tuple either compiles as overthinking or fails before compile for that reason

---

### 5B. Location grounding: NYC must be a first-class input, not a generic fallback

**Problem:** the current CLI has no location input, and unresolved location prose falls back to generic strings like `gray light through the window`, which repeated 11 times in the observed render.

**Required changes**

1. Add first-class location support to the pipeline:
   - new CLI input such as `--location nyc_metro`
2. Introduce a governed location source of truth:
   - location/profile registry or scene-pack config
3. Hydrate location variables through governed location data before Stage 6 cleanup.
4. Keep `_LOC_VAR_FALLBACKS` in [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py) as a last-resort safety net only.
5. Add anti-repetition constraints:
   - max reuse threshold for any single fallback phrase per book
   - repeated fallback beyond threshold = warning or fail
6. If a requested location cannot be honored, fail or warn explicitly rather than pretending the book is location-grounded.

**Likely files**

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- [phoenix_v4/planning/catalog_planner.py](../phoenix_v4/planning/catalog_planner.py)
- new config under `config/localization/` or `config/catalog_planning/`
- tests for location hydration and fallback repetition

**Acceptance**

- sentinel run accepts a NYC location input
- rendered book contains real NYC-grounded cues from governed config
- `gray light through the window` and other generic fallback phrases do not dominate the book

---

### 5C. Teacher Mode truth: readiness docs and compile gate must match

**Problem:** docs imply lighter readiness, but real teacher compile currently needs full slot coverage for the chosen format. This creates false confidence.

**Required changes**

1. Separate two truths clearly:
   - **minimal teacher readiness**
   - **full compile-ready teacher coverage**
2. Update readiness tooling so it reports both states explicitly.
3. Ensure [docs/TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md) matches [phoenix_v4/teacher/coverage_gate.py](../phoenix_v4/teacher/coverage_gate.py).
4. Add a single compile-readiness command/report that answers:
   - can this teacher compile this exact format/arc?
5. Improve CLI failure output:
   - teacher id
   - missing slot families
   - missing STORY bands
   - exact next action

**Likely files**

- [docs/TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md)
- [docs/TEACHER_MODE_SYSTEM_REFERENCE.md](./TEACHER_MODE_SYSTEM_REFERENCE.md)
- [phoenix_v4/teacher/coverage_gate.py](../phoenix_v4/teacher/coverage_gate.py)
- [scripts/ci/check_teacher_readiness.py](../scripts/ci/check_teacher_readiness.py)
- [scripts/ci/run_teacher_production_gates.py](../scripts/ci/run_teacher_production_gates.py)
- teacher smoke/integration tests

**Acceptance**

- teacher docs and code no longer contradict
- a teacher can be classified as:
  - not ready
  - minimally ready
  - full compile-ready for F006/standard_book
- sentinel teacher-mode run either passes honestly or fails with a precise coverage diagnosis

---

### 5D. Editorial/bestseller quality must be part of the default workflow

**Problem:** the workflow can render a book even when chapter flow is deeply broken. The strongest Pearl_Editor-style checks are optional or external.

**Required changes**

1. Add a standard quality profile for CLI renders:
   - `production`
   - `draft`
   - `debug`
2. Default production-oriented CLI runs should generate:
   - chapter flow report
   - budget report
   - bestseller/editor report
3. Wire [phoenix_v4/qa/bestseller_editor.py](../phoenix_v4/qa/bestseller_editor.py) into the main render/output path.
4. Add fail thresholds:
   - all chapters FAIL in chapter flow report = hard fail
   - book-pass fail = hard fail when production profile used
5. Make the CLI output clearer about which quality layers ran and which did not.

**Likely files**

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [phoenix_v4/qa/bestseller_editor.py](../phoenix_v4/qa/bestseller_editor.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- [phoenix_v4/qa/book_pass_gate.py](../phoenix_v4/qa/book_pass_gate.py)
- tests for profile/gate combinations

**Acceptance**

- a low-quality render cannot masquerade as a successful production book
- final output includes an editorial report by default in production mode
- sentinel fallback-quality issues would have failed the run clearly

---

### 5E. Aha and integration craft must surface in rendered output

**Problem:** the repo contains `aha_noticing` and integration callout logic, but the rendered book did not express that pattern.

**Required changes**

1. Trace where exercise/integration overlay logic should enter the render path.
2. Ensure rendered exercises can emit:
   - aha-noticing language
   - body-reference language
   - governed integration bridge phrasing
3. Add output-level validators for:
   - aha callout prefix
   - notice/body-reference requirement
   - integration bridge prefix
4. Prevent generic integration stubs from repeating chapter after chapter.

**Likely files**

- [phoenix_v4/exercises/overlay_substitution.py](../phoenix_v4/exercises/overlay_substitution.py)
- [phoenix_v4/planning/practice_selector.py](../phoenix_v4/planning/practice_selector.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- exercise rendering/composition modules
- tests for aha/integration output validation

**Acceptance**

- rendered book shows actual aha/integration language patterns
- zero silent regressions where the code path exists but the prose never uses it
- sentinel run contains visible, governed aha + integration phrasing

---

### 5F. Runtime truthfulness: one-hour requests must hit the range or fail early

**Problem:** `standard_book` is the right bucket for a one-hour book, but the observed render produced only 4,798 words and needed `--skip-word-count-gate` to finish.

**Required changes**

1. Add a pre-render budget sufficiency check:
   - estimate achievable word count from selected slots/atoms
2. If a requested runtime cannot be met, the system must:
   - switch to a shorter governed runtime, or
   - fail before render with a clear reason
3. Make runtime mismatch first-class in CLI output and plan metadata.
4. Improve density strategy so `standard_book` can realistically land near 9k–11k when valid source material exists.

**Likely files**

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- [config/format_selection/format_registry.yaml](../config/format_selection/format_registry.yaml)
- budget/word-count tests

**Acceptance**

- user asking for one-hour book gets either:
  - a real one-hour-class artifact, or
  - an explicit pre-render refusal
- no more “successful” output that only works because the gate was skipped

---

### 5G. Output contract completeness

**Problem:** the observed plan artifact did not surface enough end-user truth. Important fields like requested-vs-canonical topic, location, teacher-mode truth, and quality profile were not explicit enough.

**Required changes**

1. Plans and outputs must carry:
   - `requested_topic_id`
   - `canonical_topic_id`
   - `requested_location_id` / `resolved_location_id`
   - `teacher_mode`
   - `teacher_id`
   - quality profile used
   - runtime request vs runtime achieved
2. If the run fell back or downgraded anything, that fact must be stored in the artifact.
3. Final output summary should show the real state without needing shell archaeology.

**Likely files**

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [phoenix_v4/planning/schema_v4.py](../phoenix_v4/planning/schema_v4.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)

**Acceptance**

- plan/output artifacts tell the truth about what the system actually did
- a human can inspect one plan and know whether the request was faithfully honored

---

## 6. Recommended execution order

1. **5C Teacher Mode truth**
   - fix readiness-vs-coverage contradiction first
2. **5A Identity integrity**
   - stop silent topic drift
3. **5B Location grounding**
   - make NYC/location explicit
4. **5D Editorial/bestseller default wiring**
   - stop low-quality renders from passing as success
5. **5E Aha/integration surfacing**
   - make craft-layer behavior real in output
6. **5F Runtime truthfulness**
   - stop fake one-hour outputs
7. **5G Output contract completeness**
   - make artifacts self-explanatory

Do this as separate PRs or clearly separated commits. Do not mix teacher-bank content authoring into the same dev hardening lane.

---

## 7. Definition of done

This spec is complete when all of the following are true:

1. The sentinel tuple can be run from the CLI with a first-class location input.
2. Teacher Mode either passes honestly or fails before compile with a precise inventory explanation.
3. The system never silently converts an explicit overthinking request into a generic anxiety book without surfacing it.
4. Production-style runs generate and honor editorial/bestseller gating by default.
5. Rendered output uses governed aha/integration patterns rather than generic repeated bridge text.
6. One-hour runtime requests either hit the governed range or fail before render.
7. Output artifacts explicitly tell the truth about requested vs resolved topic, location, teacher mode, runtime, and quality profile.

---

## 8. Verification matrix

Minimum verification for this hardening lane:

```bash
# 1. Teacher readiness / compile truth
python3 scripts/ci/check_teacher_readiness.py --teacher ahjan
python3 scripts/ci/run_teacher_production_gates.py

# 2. Sentinel compile (teacher mode)
python3 scripts/run_pipeline.py \
  --topic overthinking \
  --persona gen_z_professionals \
  --series overthinking \
  --angle analysis_paralysis \
  --location nyc_metro \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__overthinking__spiral__F006.yaml \
  --teacher ahjan \
  --runtime-format standard_book \
  --structural-format F006 \
  --enforce-book-pass-gate \
  --render-book \
  --out artifacts/user_runs/sentinel_pearl_prime_whole_workflow/plan.json \
  --render-dir artifacts/user_runs/sentinel_pearl_prime_whole_workflow/rendered

# 3. Inspect generated reports
python3 -m json.tool artifacts/user_runs/sentinel_pearl_prime_whole_workflow/rendered/chapter_flow_report.json
python3 -m json.tool artifacts/user_runs/sentinel_pearl_prime_whole_workflow/rendered/budget.json
python3 -m json.tool artifacts/user_runs/sentinel_pearl_prime_whole_workflow/rendered/bestseller_editor_report.json

# 4. Repo governance
PYTHONPATH=. python3 scripts/ci/check_docs_governance.py --check-inventory
```

If the exact sentinel teacher tuple still cannot pass because content inventory is insufficient, the dev lane still succeeds if the system now fails **early, explicitly, and truthfully** at the correct stage.

---

## 9. Non-goals and guardrails

- Do not hide teacher/content gaps behind generic fallback prose.
- Do not declare success just because `book.txt` exists.
- Do not solve topic specificity by silently broadening the topic.
- Do not add NYC/location text through ad hoc string hacks; use governed config.
- Do not weaken the teacher coverage gate just to make the demo run.
- Do not mix content-writing backlog into this dev hardening lane unless a separate writer lane is explicitly opened.

---

## 10. Suggested lane name

`pearl_prime_whole_workflow_hardening`

Suggested first dev tranche:

`teacher_truth_identity_location_hardening`

