# Core tests still-red diagnostic — post Phase 2 cover_art gate relaxation

**Project:** `PRJ-CI-BASELINE-RECOVERY-V1`  
**Subsystem:** `pearl_devops`  
**Run analyzed:** [GitHub Actions run 25614516443](https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/25614516443)  
**Workflow:** Core tests (`.github/workflows/core-tests.yml`)  
**`main` head at failure:** `805f62947d01c29820860785b8abce9d6a5f2c61` (merge commit associated with PR #1011 / Phase 2 cover_art relax)  
**Date:** 2026-05-10  

---

## 1. Capture (failure log excerpts; verbatim)

**Failing job:** `Core tests`  
**Failing step:** `Run fast/core pytest`  

Excerpt from `gh run view 25614516443 --log-failed`:

```text
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3518008Z collecting ... collected 14 items / 1 error
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3519234Z ==================================== ERRORS ====================================
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3520035Z ____ ERROR collecting tests/brand_wizard/test_music_survey_save_handler.py _____
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3520925Z ImportError while importing test module '/home/runner/work/phoenix_omega_v4.8/phoenix_omega_v4.8/tests/brand_wizard/test_music_survey_save_handler.py'.
...
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3530471Z brand-wizard-app/server/music_survey_routes.py:15: in <module>
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3530827Z     from fastapi import FastAPI, HTTPException
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3531444Z E   ModuleNotFoundError: No module named 'fastapi'
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3541779Z ERROR tests/brand_wizard/test_music_survey_save_handler.py
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3542435Z !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
Core tests	Run fast/core pytest	2026-05-09T23:30:38.3920797Z ##[error]Process completed with exit code 1.
```

**Pytest flags in CI:** `PYTHONPATH=. python -m pytest tests/ -v --tb=short -m "not slow" -x` (fail-fast stops after first error).

---

## 2. Root cause analysis (per failure)

### 2.1 Primary failure: missing `fastapi` in Core tests environment

| Item | Finding |
|------|--------|
| **Mechanism** | Pytest **collects** `tests/brand_wizard/test_music_survey_save_handler.py`, which adds `brand-wizard-app/server` to `sys.path` and imports `music_survey_routes`. That module imports `FastAPI` from `fastapi` at import time. |
| **CI install step** | `.github/workflows/core-tests.yml` runs `pip install -r requirements-test.txt` only. |
| **`requirements-test.txt` today** | Lists `pyyaml`, `pytest`, `pytest-timeout`, `jsonschema`, `feedparser`, `Pillow`, `ebooklib` — **no `fastapi` (and no explicit `pydantic`)**. |
| **Conclusion** | **Dependency gap:** Core tests is expected to run the full `tests/` tree (minus slow), but the minimal test requirements file does not include packages needed to import brand-wizard FastAPI routes under test. |

### 2.2 Is this the cover_art / Gate 18 path?

**No.** In this run, pytest **never reached** execution of production readiness gates. The workflow order is:

1. Install test dependencies  
2. **Run fast/core pytest** ← failed here during collection  
3. (Later steps: smoke manga CLI, marketing config, onboarding registry, freebie index rebuild, **`run_production_readiness_gates.py`** including Gate 18 cover art)

So **condition 18 / `check_author_cover_art.py` is not on the critical path for this failure.**

### 2.3 `COVER_ART_GATE_MODE` and `run_production_readiness_gates.py`

Investigation (read-only):

- `scripts/run_production_readiness_gates.py` invokes `check_author_cover_art.py` with `env = os.environ.copy()` and **does not** inject `COVER_ART_GATE_MODE`. The subprocess therefore uses whatever the workflow exports, or the script default.
- `scripts/ci/check_author_cover_art.py`: `resolve_gate_mode()` — **default is `warn`** unless `COVER_ART_GATE_MODE=fail` or `--gate-mode fail`.
- **Grep** `.github/workflows/*.yml` for `COVER_ART_GATE_MODE` / `check_author_cover_art`: **no matches**.

**Assessment:** For Gate 18, unset `COVER_ART_GATE_MODE` in CI is **consistent with warn-default** once the pytest step passes. The still-red Core tests run is **not** explained by a missing workflow env var for cover_art; it is explained by **pytest failing earlier**.

### 2.4 Multiple concurrent causes?

For **run 25614516443**, only **one** failure is visible (`-x` stops after first error). After fixing `fastapi`, Core tests may surface **additional** failures (e.g. Gate 18 if defaults regressed, or other tests). **Phase 2.5 should treat the missing dependency as the known first blocker;** follow-on reds require a new diagnostic slice if they appear.

---

## 3. Why Phase 2 did not fix Core tests on `main` (precise reason)

Phase 2 (PR #1011) addressed **author cover art strictness** (`check_author_cover_art.py` default warn, tests, and related policy). That only affects steps **after** a successful pytest collection and run, when `scripts/run_production_readiness_gates.py` reaches **Gate 18**.

The observed failure is **`ModuleNotFoundError: No module named 'fastapi'`** during **test collection** for `tests/brand_wizard/test_music_survey_save_handler.py`. That is a **separate regression class** (test dependency coverage vs. application code under test), **orthogonal** to cover_art gate mode.

---

## 4. Recommended Phase 2.5 plan

| Field | Recommendation |
|-------|----------------|
| **Workstream ID** | `ws_ci_recovery_phase_2_5_core_tests_brand_wizard_deps` |
| **Goal** | Align **Core tests** `pip install -r requirements-test.txt` with imports required by tests under `tests/brand_wizard/` that load FastAPI route modules. |
| **Primary change (follow-up implementation PR)** | Add **`fastapi`** (pin floor consistent with repo; modern FastAPI pulls compatible **pydantic**) to `requirements-test.txt`. **Single file**, very small diff. |
| **Estimated effort** | **S** (minutes to land + one Core tests run); low risk if version floor matches existing server code patterns. |
| **Validation** | `pip install -r requirements-test.txt && PYTHONPATH=. python -m pytest tests/brand_wizard/test_music_survey_save_handler.py -v --tb=short` locally; then full Core tests workflow on PR. |
| **Alternatives (not recommended first)** | (a) Refactor tests to avoid importing `music_survey_routes` (mock/stub) — larger change; (b) exclude `tests/brand_wizard` from Core tests — weakens signal. |

### 4.1 Proposed exact diff (paste into Phase 2.5 PR)

**File:** `requirements-test.txt`

```diff
--- a/requirements-test.txt
+++ b/requirements-test.txt
@@ -7,3 +7,4 @@ jsonschema>=4.0
 feedparser>=6.0
 Pillow>=9.0
 ebooklib>=0.18
+fastapi>=0.100.0
```

*Rationale:* `music_survey_routes.py` imports `fastapi` and `pydantic`; installing `fastapi` is the minimal CI alignment. If CI still complains about a secondary import, extend the same PR with the next missing package (unlikely for this module).

---

## 5. Anti-drift: gates and cover_art behavior

- **Production readiness Gate 18** should remain the **single** authoritative place for “missing `cover_art_base` on disk” policy (warn vs fail), via `check_author_cover_art.py` + env/CLI — **do not** duplicate that policy inside pytest brand-wizard tests.
- **Core tests** should continue to install **all** dependencies needed for any test module **importable** under `tests/` for the markers CI uses (`not slow`), or tests should be structured to avoid heavy optional imports at collection time. Prefer **requirements-test.txt completeness** over silent skips for required checks.
- After Phase 2.5, if Gate 18 ever needs **strict fail** in a specific workflow, set `COVER_ART_GATE_MODE=fail` in that job only — avoid re-tightening default for all contexts without policy review.

---

## 6. Summary

| Question | Answer |
|----------|--------|
| **Root cause (one line)** | Core tests installs `requirements-test.txt` without `fastapi`, but `tests/brand_wizard/test_music_survey_save_handler.py` imports a FastAPI route module → **collection-time `ModuleNotFoundError`**. |
| **Cover_art / Phase 2 relevance** | **None for this run;** pytest fails before readiness gates. |
| **Phase 2.5** | Add **`fastapi`** to `requirements-test.txt` under workstream **`ws_ci_recovery_phase_2_5_core_tests_brand_wizard_deps`**. |
