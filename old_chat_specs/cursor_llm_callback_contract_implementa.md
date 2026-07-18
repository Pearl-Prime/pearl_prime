# LLM callback contract implementation
_Exported on 4/3/2026 at 06:02:07 GMT+8 from Cursor (2.6.22)_

---

**User**

You are Pearl_Dev, the implementation agent for Phoenix Omega.

## Session Date
2026-03-30

## Your Identity
Pearl_Dev implements code changes specified by dev specs. You write Python, tests, and minimal config changes. You do not redesign architecture — you follow the spec and escalate when stop conditions are hit.

## Read First (in order)
1. SYSTEM_OWNER_VISION.md
2. docs/BESTSELLER_GRADE_PIPELINE_DEV_SPEC.md — section "BG-PR-11" is your task
3. config/quality/ei_v2_config.yaml — read fully; note safety_classifier.mode: heuristic_plus, cross_encoder.mode: heuristic. Both have LLM modes defined but not wired.
4. phoenix_v4/quality/ei_v2/safety_classifier.py — read EVERY line. Has call_llm_fn parameter in classify_safety() but NEVER INVOKES IT. Mode "llm" is accepted but falls through to heuristic.
5. phoenix_v4/quality/ei_v2/cross_encoder_reranker.py — read EVERY line. Has call_model_fn parameter in rerank_candidates(). Mode "model" DOES invoke call_model_fn(thesis, text) with heuristic fallback on error.
6. phoenix_v4/quality/bestseller_craft_gate.py — if it exists, read it; it accepts call_llm_json. If it doesn't exist yet (BG-PR-07 may not have landed), note the planned interface.
7. phoenix_v4/quality/ei_v2/hybrid_selector.py — read to understand call_llm_fn passthrough in the selection pipeline.
8. tests/test_ei_v2_hybrid.py — read existing LLM-related tests and mocks.

## Current State
- safety_classifier.py: accepts call_llm_fn but never calls it. LLM mode is dead code.
- cross_encoder_reranker.py: accepts call_model_fn AND uses it when mode=model. This is the only working LLM path.
- bestseller_craft_gate.py: planned call_llm_json interface (BG-PR-07 scope).
- No unified LLM callback contract exists — each module defines its own signature.
- Config has no cost guard, rate limit, or LLM budget settings.

## Task
Design and implement the LLM callback contract and wire it into safety_classifier per BG-PR-11 in the dev spec.

### 1. Callback Contract Module
Create `phoenix_v4/quality/ei_v2/llm_callback.py`:

Define:
a. `LLMTextCallback` protocol: `(prompt: str, text: str) -> float` — for cross-encoder style scoring. Returns a relevance/quality score 0–1.
b. `LLMJsonCallback` protocol: `(text: str, aspect: str, question: str) -> dict` — for craft gate style structured evaluation. Returns {"score": float, "reasoning": str}.
c. `LLMClassifyCallback` protocol: `(text: str, categories: list[str]) -> dict` — for safety classifier. Returns {"category": str, "confidence": float, "flags": list}.

### 2. Cost Guard Wrapper
In the same module, implement:

def cost_guarded(
    callback: Callable,
    *,
    max_calls_per_book: int = 100,
    max_calls_per_chapter: int = 10,
    budget_tracker: dict | None = None,
) -> Callable

Returns a wrapped callback that:
- Tracks call count in budget_tracker dict (mutable, shared across chapters)
- Raises `LLMBudgetExceeded` when limits are hit
- Falls back gracefully — the wrapped callback returns None on budget exhaustion, and callers must handle None as "use heuristic fallback"

### 3. Wire into safety_classifier.py
- Implement the actual LLM call path in classify_safety when mode == "llm" and call_llm_fn is provided.
- The LLM call should: send the text + safety categories → receive classification → merge with heuristic scores (LLM overrides heuristic when confidence > 0.8, otherwise average).
- If call_llm_fn is None or returns None (budget exhausted), fall back to heuristic_plus silently.

### 4. Config Additions
Add to ei_v2_config.yaml under a new `llm_quality` section:

llm_quality:
  enabled: false
  max_calls_per_book: 100
  max_calls_per_chapter: 10
  safety_classifier_mode: heuristic_plus
  cross_encoder_mode: heuristic
  fallback_on_budget_exceeded: heuristic

Do NOT change the existing safety_classifier.mode or cross_encoder.mode values — the new llm_quality section is the master switch.

### 5. Tests
Create `tests/test_llm_callback.py` (new):
- Test LLMTextCallback protocol with mock
- Test LLMJsonCallback protocol with mock
- Test LLMClassifyCallback protocol with mock
- Test cost_guarded: call count tracking, budget exceeded raises correctly, None fallback
- Test cost_guarded with per-book and per-chapter limits
- Test safety_classifier LLM path with mock callback (mode=llm, call_llm_fn=mock)
- Test safety_classifier LLM fallback when callback returns None
- Test safety_classifier LLM fallback when callback raises
- Test safety_classifier unchanged behavior when mode=heuristic_plus (no regression)
- Determinism: same inputs → same outputs (mock LLM returns deterministic responses)

## Scope Constraints
- Write scope: phoenix_v4/quality/ei_v2/llm_callback.py (new), phoenix_v4/quality/ei_v2/safety_classifier.py (modify LLM path), config/quality/ei_v2_config.yaml (add llm_quality section), tests/test_llm_callback.py (new)
- Do not modify: phoenix_v4/quality/ei_v2/cross_encoder_reranker.py (already works), phoenix_v4/quality/bestseller_craft_gate.py (BG-PR-07 owns it), specs/, phoenix_v4/rendering/
- Branch rule: git fetch origin && git checkout -b agent/bestseller-grade-pr11 origin/main
- Output: Working code + passing tests. Run pytest on new test file + existing safety tests before declaring done.

## Authority Chain
- Architecture authority: specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md
- Dev spec authority: docs/BESTSELLER_GRADE_PIPELINE_DEV_SPEC.md §BG-PR-11
- Config contract: config/quality/ei_v2_config.yaml

## Hard Rules
1. Read safety_classifier.py and cross_encoder_reranker.py EVERY line before writing. Understand what exists.
2. The callback contract must be backward-compatible — existing code that passes call_llm_fn=None must work exactly as before.
3. Cost guard is mandatory. No open-ended LLM spending.
4. llm_quality.enabled defaults to false. This is an opt-in upgrade, not a forced change.
5. Determinism: heuristic fallback path must remain deterministic. LLM path determinism depends on the callback, but the contract must document this.
6. Do not add any actual LLM API calls (no openai, anthropic, requests imports). The callback is injected by the caller — you define the interface only.
7. Follow push-guard rules before push:
   PYTHONPATH=. python3 scripts/git/push_guard.py
   scripts/ci/preflight_push.sh
   bash scripts/git/health_check.sh
8. If any stop condition from the dev spec is hit, STOP and report — do not improvise.

## Closeout
Return a CLOSEOUT_RECEIPT listing:
- Branch name + commit SHA
- Files created/modified (with line counts)
- Test results (full pytest output)
- Callback protocol summary (3 protocols defined)
- Cost guard behavior summary
- Safety classifier changes summary (what the LLM path does)
- Config diff (show exact YAML additions)
- Any escalations or spec gaps found

---

**Cursor**

Implementing BG-PR-11: reading required specs and source files, then implementing the LLM callback contract, cost guard, safety classifier wiring, config, and tests.



Locating the dev spec and reading `hybrid_selector.py`, `test_ei_v2_hybrid.py`, and `bestseller_craft_gate.py`.



Creating the branch and implementing `llm_callback.py`, updating `safety_classifier.py`, adding the config section, and adding tests. Escalation: `docs/BESTSELLER_GRADE_PIPELINE_DEV_SPEC.md` missing from the repo; `bestseller_craft_gate.py` not present.



Implementing `llm_callback.py`, updating `safety_classifier.py`, adding the YAML section, and creating tests.



Refactoring `safety_classifier.py`: extracting final aggregation and syncing reason codes, then adding the LLM merge path.



Removing unused threshold variables from `classify_safety`.



Appending LLM flags after finalize so they aren't discarded.



" from bad edit. Read file end.
`</think>`




" at line 225. Remove it with search_replace
`</think>`




`




`




`




` from a corrupted merge?

Looking at the full read output lines 224-226:
```
   224|    assert with_guard["mode"] == "llm"
   225|
   226| open_and_recently_viewed
```

That looks like corruption - "open_and_recently_viewed" shouldn't be there. Let me read the raw file with hexdump or tail
`</think>




`




, StrReplace. I'll rewrite the file cleanly by reading good content and writing full file without garbage.
`</think>`




`




Re-implementing changes — workspace files reverted.



Re-applying the full implementation.



## CLOSEOUT_RECEIPT

### Branch and commit
- **Branch:** `agent/bestseller-grade-pr11`
- **Commit:** `19321dd2` (full: `19321dd2` — run `git rev-parse HEAD` locally if you need the 40-char SHA)

### Files touched (line counts, current `wc -l`)
| File | Lines |
|------|------:|
| `phoenix_v4/quality/ei_v2/llm_callback.py` (new) | 91 |
| `phoenix_v4/quality/eи_v2/safety_classifier.py` (modified) | 359 |
| `config/quality/ei_v2_config.yaml` (modified) | 170 |
| `tests/test_llm_callback.py` (new) | 215 |

*(Commit stats: 4 files changed, 438 insertions, 37 deletions.)*

### Test results (`pytest` — new file + `TestSafetyClassifier`)
```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- ...
rootdir: /Users/ahjan/phoenix_omega
configfile: pytest.ini
plugins: anyio-4.12.1
collecting ... collected 20 items

tests/test_llm_callback.py::test_llm_text_callback_protocol_mock PASSED  [  5%]
tests/test_llm_callback.py::test_llm_json_callback_protocol_mock PASSED  [ 10%]
tests/test_llm_callback.py::test_llm_classify_callback_protocol_mock PASSED [ 15%]
tests/test_llm_callback.py::test_cost_guarded_tracks_book_and_chapter_calls PASSED [ 20%]
tests/test_llm_callback.py::test_cost_guarded_returns_none_when_exhausted PASSED [ 25%]
tests/test_llm_callback.py::test_cost_guarded_raises_when_configured PASSED [ 30%]
tests/test_llm_callback.py::test_cost_guarded_chapter_limit PASSED       [ 35%]
tests/test_llm_callback.py::test_safety_classifier_llm_path_merges_with_mock PASSED [ 40%]
tests/test_llm_callback.py::test_safety_classifier_llm_fallback_when_callback_returns_none PASSED [ 45%]
tests/test_llm_callback.py::test_safety_classifier_llm_fallback_when_callback_raises PASSED [ 50%]
tests/test_llm_callback.py::test_safety_classifier_heuristic_plus_no_llm_invocation PASSED [ 55%]
tests/test_llm_callback.py::test_safety_classifier_llm_low_confidence_averages PASSED [ 60%]
tests/test_llm_callback.py::test_safety_classifier_llm_determinism_with_mock PASSED [ 65%]
tests/test_llm_callback.py::test_safety_classifier_llm_with_cost_guard_none_fallback_matches_heuristic PASSED [ 70%]
tests/test_ei_v2.py::TestSafetyClassifier::test_safe_text_low_risk PASSED [ 75%]
tests/test_ei_v2.py::TestSafetyClassifier::test_unsafe_text_high_risk PASSED [ 80%]
tests/test_ei_v2.py::TestSafetyClassifier::test_promotional_detected PASSED [ 85%]
tests/test_ei_v2.py::TestSafetyClassifier::test_clinical_language_detected PASSED [ 90%]
tests/test_ei_v2.py::TestSafetyClassifier::test_pathologizing_detected PASSED [ 95%]
tests/test_ei_v2.py::TestSafetyClassifier::test_empty_text PASSED        [100%]

============================== 20 passed in 0.52s ==============================
```

Also ran `tests/test_ei_v2.py` + `tests/test_ei_v2_marketing_lexicons.py` (**39 passed**).

**Preflight / guards:** `PYTHONPATH=. python3 scripts/git/push_guard.py` → **OK**. `bash scripts/ci/preflight_push.sh` → **Preflight OK.** `bash scripts/git/health_check.sh` reported **dirty tree** (unrelated modified `artifacts/...` logs and untracked dirs); fix or ignore before push.

---

### Callback protocol summary (3 protocols)
1. **`LLMTextCallback`** — `(prompt: str, text: str) -> float` (relevance/score in \([0,1]\)).
2. **`LLMJsonCallback`** — `(text: str, aspect: str, question: str) -> dict` (structured eval; craft-gate style `{score, reasoning}`).
3. **`LLMClassifyCallback`** — `(text: str, categories: list[str]) -> dict` (safety classify → `{category, confidence, flags}`).

Also: **`LLMBudgetExceeded`**, **`reset_chapter_budget`**, **`cost_guarded`**.

---

### Cost guard behavior
- Tracks **`book_calls`** and **`chapter_calls`** on a shared mutable **`budget_tracker`**.
- Before each delegated call: if **book** or **chapter** count is already at the cap, **does not** call the inner function.
- Default **`raise_on_exhaust=False`**: wrapper returns **`None`** (callers treat as heuristic fallback).
- **`raise_on_exhaust=True`**: raises **`LLMBudgetExceeded`** on the same condition (for strict / tests).
- **`reset_chapter_budget(tracker)`** zeroes **`chapter_calls`** between chapters.

---

### Safety classifier (LLM path)
- Still computes **full heuristic** scores first, then **`_finalize_aggregate_and_reason_codes`** (rebuilds non-marketing `reason_codes` + `risk_score`).
- If **`cfg["mode"] == "llm"`** and **`call_llm_fn`** is set: calls **`call_llm_fn(text, SAFETY_LLM_CATEGORIES)`**; normalizes **`category` / `confidence` / `flags`**.
- **Merge** (for the five weighted risk categories only): if **`confidence > 0.8`**, category score becomes **`confidence`**; else **`(heuristic + confidence) / 2`**, clamped to \([0,1]\); then **re-finalize** aggregate + reasons; **append** string **`flags`** to `reason_codes`.
- **`call_llm_fn` None**, **callback returns `None`**, **invalid payload**, or **exception** → **unchanged** heuristic final result (still **`mode`** from config, e.g. **`llm`** with heuristic numbers).
- **`heuristic_plus`** → **never** invokes **`call_llm_fn`** (backward compatible).

Public constant **`SAFETY_LLM_CATEGORIES`** documents the category list passed into the callback.

---

### Config addition (exact YAML)
```yaml
# ── LLM quality (opt-in master switch; budgets; mode hints for future wiring) ──
# Does not override safety_classifier.mode / cross_encoder.mode above unless the
# caller applies llm_quality.* when building runtime config.
llm_quality:
  enabled: false
  max_calls_per_book: 100
  max_calls_per_chapter: 10
  safety_classifier_mode: heuristic_plus
  cross_encoder_mode: heuristic
  fallback_on_budget_exceeded: heuristic
```
*(Inserted after `safety_classifier.cache_path`; existing **`safety_classifier.mode`** / **`cross_encoder.mode`** unchanged.)*

---

### Escalations / gaps
1. **`docs/BESTSELLER_GRADE_PIPELINE_DEV_SPEC.md`** — not present in this workspace; BG-PR-11 was implemented from your message only.
2. **`phoenix_v4/quality/bestseller_craft_gate.py`** — not in tree here; no changes (per scope).
3. **`run_ei_v2_analysis`** still does **not** pass **`call_llm_fn`** into **`classify_safety`**; enabling **`llm_quality`** + injecting a callback is **follow-up wiring** outside the stated file scope.
4. **`llm_quality`** block is **config-only** for this PR; **runtime** still keys off **`safety_classifier.mode`** and the injected callback.

---

**User**

### 2. Canary Config Override File
Create `config/canary/bestseller_canary_overrides.yaml`:
```yaml
# Canary-specific overrides — applied on top of ei_v2_config.yaml
dimension_gates:
  fail_mode: block
  dimension_gate_phase: 3
  blocked_dimensions:
    - engagement
    - somatic_precision
    - uniqueness
    - cohesion
    - listen_experience
llm_quality:
  enabled: false
canary:
  sentinel_default_persona: gen_z_professionals
  sentinel_default_topic: overthinking
  sentinel_default_engine: reflection
  sentinel_default_format: standard_20ch
```

### 3. Integration Test
Create `tests/test_canary_integration.py`:
- Test canary script imports without error
- Test config loading + override merging
- Test sentinel tuple selection (finds a valid tuple from atoms/)
- Test evidence directory creation
- Test canary_summary.json schema (has required fields)
- Test graceful handling when a gate module is missing (mock import failure)
- Mock the full pipeline run with a single chapter and verify evidence files are produced

### 4. Dry-Run Evidence
Run the canary script once. It WILL likely fail (gates will block) because the feature branches aren't merged. That's expected and correct — the canary is proving the enforcement works.

Save the output as the first evidence bundle. The canary_summary.json should show:
- Which gates passed
- Which gates blocked
- Which modules were missing (if running against main without feature branches)

This evidence bundle IS the deliverable — it proves the canary pipeline works and documents the current gap between main and bestseller-grade.

## Scope Constraints
- Write scope: scripts/canary/run_bestseller_canary.py (new), config/canary/bestseller_canary_overrides.yaml (new), tests/test_canary_integration.py (new), artifacts/canary/<timestamp>/ (generated evidence)
- Do not modify: ANY existing Python modules, config/quality/ei_v2_config.yaml, specs/, phoenix_v4/
- Branch rule: git fetch origin && git checkout -b agent/bestseller-grade-pr12 origin/main
- Output: Working canary script + evidence bundle + passing integration tests.

## Authority Chain
- Architecture authority: specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md
- Dev spec authority: docs/BESTSELLER_GRADE_PIPELINE_DEV_SPEC.md §BG-PR-12
- Config contract: config/quality/ei_v2_config.yaml (read only)
- Pipeline entry: scripts/run_pipeline.py

## Hard Rules
1. Read run_pipeline.py BEFORE designing the canary. Understand the actual pipeline flow — do not invent a parallel pipeline.
2. The canary must be runnable with `PYTHONPATH=. python3 scripts/canary/run_bestseller_canary.py` — no extra dependencies.
3. Graceful degradation: missing modules = exit 2 with clear error, NOT a crash.
4. Collect ALL evidence even on failure — the evidence bundle is the product, not the pass/fail result.
5. No network calls. No LLM calls. Heuristic-only canary.
6. Determinism: same atoms + same config → same canary result.
7. The canary does NOT merge branches or modify the repo. It runs against whatever code is currently checked out.
8. Follow push-guard rules before push:
   PYTHONPATH=. python3 scripts/git/push_guard.py
   scripts/ci/preflight_push.sh
   bash scripts/git/health_check.sh
9. If any stop condition from the dev spec is hit, STOP and report — do not improvise.

## Closeout
Return a CLOSEOUT_RECEIPT listing:
- Branch name + commit SHA
- Files created (with line counts)
- Test results (pytest output)
- Dry-run canary result: PASS / FAIL / ERROR
- Evidence bundle path
- canary_summary.json contents (full)
- List of gates that passed vs blocked vs missing
- Any escalations or spec gaps found

---

**Cursor**

Implementing the bestseller canary: reading `run_pipeline.py` and related entry points to align the canary with the real pipeline.



Implementing the canary script, override config, integration tests, and running a dry-run to produce the evidence bundle.



Creating the override config, the canary script, and integration tests.



## CLOSEOUT_RECEIPT

### Branch and commit
- **Branch:** `agent/bestseller-grade-pr12`
- **Commit SHA:** `e3c80776`

### Files created (line counts, `wc -l`)
| Path | Lines |
|------|------:|
| `config/canary/bestseller_canary_overrides.yaml` | 17 |
| `scripts/canary/run_bestseller_canary.py` | 391 |
| `tests/test_canary_integration.py` | 129 |
| `artifacts/canary/bestseller_grade_first_bundle_20260331/canary_summary.json` | (JSON artifact) |
| `artifacts/canary/bestseller_grade_first_bundle_20260331/chapter_gates_detail.json` | |
| `artifacts/canary/bestseller_grade_first_bundle_20260331/safety_classifier_snapshot.json` | |
| `artifacts/canary/bestseller_grade_first_bundle_20260331/canary_stdout.txt` | |

### Test results (`pytest tests/test_canary_integration.py -v`)
```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- ...
rootdir: /Users/ahjan/phoenix_omega
configfile: pytest.ini
plugins: anyio-4.12.1
collecting ... collected 8 items

tests/test_canary_integration.py::test_canary_script_imports_without_error PASSED [ 12%]
tests/test_canary_integration.py::test_config_loading_and_override_merging PASSED [ 25%]
tests/test_canary_integration.py::test_deep_merge_nested PASSED          [ 37%]
tests/test_canary_integration.py::test_sentinel_tuple_finds_valid_engine_and_prose PASSED [ 50%]
tests/test_canary_integration.py::test_evidence_directory_creation PASSED [ 62%]
tests/test_canary_integration.py::test_canary_summary_schema PASSED      [ 75%]
tests/test_canary_integration.py::test_graceful_handling_when_gate_module_import_fails PASSED [ 87%]
tests/test_canary_integration.py::test_mock_single_chapter_pipeline_evidence_files PASSED [100%]

============================== 8 passed in 0.24s ===============================
```

### Dry-run canary result
- **Result:** **FAIL** (process **exit code 1**)
- **Reason:** `dimension_gates.fail_mode: block` and **two blocked dimensions have no gate implementation** in this checkout (`cohesion`, `listen_experience`), so the canary treats enforcement as incomplete (expected gap vs main).

### Evidence bundle path
`artifacts/canary/bestseller_grade_first_bundle_20260331/`

### `canary_summary.json` (full)
```json
{
  "canary_version": 1,
  "pipeline_reference": "scripts/run_pipeline.py (EI slice: chapter prose + dimension gates + safety)",
  "repo_root": "/Users/ahjan/phoenix_omega",
  "gates_passed": [
    "engagement",
    "somatic_precision",
    "uniqueness"
  ],
  "gates_blocked": [],
  "gates_missing": [
    "cohesion",
    "listen_experience"
  ],
  "missing_modules": [],
  "errors": [],
  "overall_status": "FAIL",
  "evidence_dir": "/Users/ahjan/phoenix_omega/artifacts/canary/bestseller_grade_first_bundle_20260331",
  "sentinel": {
    "persona_id": "gen_z_professionals",
    "topic_id": "overthinking",
    "engine_id": "comparison",
    "format_id": "standard_20ch",
    "atoms_canonical_path": "atoms/gen_z_professionals/overthinking/comparison/CANONICAL.txt"
  },
  "dimension_gates_fail_mode": "block",
  "dimension_gate_phase": 3,
  "safety_classifier": {
    "risk_score": 0.0,
    "reason_codes": [],
    "mode": "heuristic_plus"
  },
  "fatal_errors": []
}
```

### Gates: passed vs blocked vs missing
| Category | Dimensions |
|----------|------------|
| **Passed** | `engagement`, `somatic_precision`, `uniqueness` |
| **Blocked** (ran, non-PASS) | *(none — all implemented gates returned PASS)* |
| **Missing** (no `gate_*` in `dimension_gates.py` for this checkout) | `cohesion`, `listen_experience` |

**`missing_modules`:** empty (the `dimension_gates` package imports successfully; only those two dimensions are unimplemented). **`exit 2`** is reserved for fatal cases such as missing base config, no chapter prose, or **`phoenix_v4.quality.ei_v2.dimension_gates` import failure** (handled without traceback; evidence still written when the evidence dir was created).

### Escalations / spec gaps
- **`docs/BESTSELLER_GRADE_PIPELINE_DEV_SPEC.md`** (§BG-PR-12) was not available in this workspace; behavior follows your task text plus **`scripts/run_pipeline.py`** (EI slice uses chapter prose → scoring; full compile is not reimplemented in the canary).
- **`sentinel_default_engine: reflection`** has no `atoms/.../reflection/CANONICAL.txt` here; the canary **falls back** to the first engine bank with prose (here **`comparison`**), recorded in `sentinel.engine_id`.

### Commands / hygiene
- **Runnable:** `PYTHONPATH=. python3 scripts/canary/run_bestseller_canary.py`
- **`PYTHONPATH=. python3 scripts/git/push_guard.py`:** OK  
- `scripts/ci/preflight_push.sh` was not executed in this session (use `bash scripts/ci/preflight_push.sh` if the executable bit is missing).

---

**User**

You are Pearl_GitHub, the GitHub operations agent for Phoenix Omega.

## Startup sequence

1. Read `CLAUDE.md`
2. Read `skills/pearl-github/SKILL.md`
3. Read `docs/RESEARCH_INTEGRATION_DEV_SPEC.md` §2 — all 6 PR definitions
4. Read `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
5. Read each orphaned research file fully:
   - `artifacts/research/deepseek_bestseller_plan_2026_03_23.md`
   - `artifacts/research/deepseek_gap_fill_round2_2026_03_23.md`
   - `artifacts/research/deepseek_market_data_followup_2026_03_23.md`
   - `artifacts/research/kdp_global_ebook_strategy_2026_03_23.md`
   - `artifacts/research/rakuten_ai_bestseller_titles_2026_03_23.md`
   - `artifacts/research/rakuten_ai_market_research_2026_03_23.md`
   - `artifacts/research/web_search_gap_fill_2026_03_23.md`
6. Read `config/localization/` directory listing
7. Read `config/payouts/` directory listing
8. Read `config/catalog_planning/brand_archetype_registry.yaml` (first 80 lines)
9. Run mandatory preflight

## Mandatory preflight
```bash
git branch --show-current
git status --short
git fetch origin
git rev-list --left-right --count origin/main...HEAD
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
```

## Task: Execute all 6 integration PRs per RESEARCH_INTEGRATION_DEV_SPEC.md §2

For EACH of the 6 PRs defined in the spec:

### Per-PR workflow

1. **Branch from origin/main:**
```bash
   git fetch origin
   git checkout -b agent/research-integration-<topic> origin/main
```

2. **Extract data from the orphaned research file.** Create or update the target
   config file(s) as defined in the spec §2 table. For every data point extracted,
   add a `_source:` comment or sibling field pointing back to the research file path.

3. **If target config file doesn't exist,** create it with a proper YAML header
   including `schema_version: 1` and a comment referencing the research source.

4. **Preflight + commit + push:**
```bash
   PYTHONPATH=. python3 scripts/git/push_guard.py
   scripts/ci/preflight_push.sh
   bash scripts/git/health_check.sh
   git add <specific files>
   git commit -m "feat: integrate <topic> research into config (PR-RI-00N)

   Extracts actionable data from <research_file> into <target_config>.
   All values traced back to source via _source fields.

   Refs: RESEARCH_INTEGRATION_DEV_SPEC.md §2"
   git push -u origin agent/research-integration-<topic>
```

5. **Open PR** targeting `main`. Reference the spec and audit.

6. **Return to main before starting next PR:**
```bash
   git checkout main
   git pull origin main
```

### The 6 PRs

**PR-RI-001:** Asian bestseller strategy
- Source: `deepseek_bestseller_plan_2026_03_23.md`
- Extract: platform navigation, keyword translation tables, data collection phases
- Target: `config/localization/asian_market_strategy.yaml` (new file)

**PR-RI-002:** HK/SG market sizing
- Source: `deepseek_gap_fill_round2_2026_03_23.md`
- Extract: SG $18.5M→$54.58M, HK platform details, language preferences
- Target: `config/localization/asian_market_strategy.yaml` (append market_sizing section)
- Note: if PR-RI-001 hasn't merged yet, include both in one branch or create standalone file

**PR-RI-003:** Asian market sizing + mental wellness
- Source: `deepseek_market_data_followup_2026_03_23.md`
- Extract: 6-market CAGR 2024-2033, mental wellness $2.9B→$6.8B
- Target: `config/localization/` + update `docs/LOCALE_CATALOG_MARKETING_PLAN.md` references

**PR-RI-004:** KDP global ebook
- Source: `kdp_global_ebook_strategy_2026_03_23.md`
- Extract: 13 Kindle stores, royalty tiers 70%/35%, KDP Select rules
- Target: `config/payouts/` (new or existing royalty config)

**PR-RI-005:** Asia-Pacific bestsellers + market research
- Source: `rakuten_ai_bestseller_titles_2026_03_23.md` + `rakuten_ai_market_research_2026_03_23.md`
- Extract: competitor titles, platform URLs, polyvagal/somatic positioning
- Target: `config/catalog_planning/` competitive section

**PR-RI-006:** Taiwan/China platforms
- Source: `web_search_gap_fill_2026_03_23.md`
- Extract: Readmoo/Kobo TW, Ximalaya 303M MAU, ISBN/CSBN requirements, VAT
- Target: `config/localization/` + compliance doc

### After all 6

Update `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`:
- Set ws_research_integration_20260330 status to `pr-open` with all 6 PR numbers listed

## Rules
- Never branch from codex/*
- Never push without preflight
- One branch per PR — do not combine PRs
- Only extract data that exists in the research file — never extrapolate
- Every extracted value gets a _source field

---

**Cursor**

Executing Pearl_GitHub startup: reading required docs, the dev spec §2, research artifacts, and directory listings, then running preflight and implementing the six integration PRs.



Reading the seven research artifacts to extract factual content with provenance.



Implementing six separate branches from `origin/main` per `RESEARCH_INTEGRATION_DEV_SPEC.md` §2 (spec PR numbering differs from the user message). Creating YAML files with `_source` provenance, running preflight before each push, and updating `ACTIVE_WORKSTREAMS.tsv`.



Creating branch `agent/research-integration-asian-bestseller-plan` and adding `config/localization/asia_audiobook_research_brief.yaml`.



Recreating PR-RI-002: the remote branch points at main without the YAML; the commit landed on `agent/bestseller-grade-pr02`. Cherry-picking that commit onto `origin/main` and force-pushing the correct branch.



PR-RI-002 is fixed on `origin`. Reading the spec §2 and remaining research sources to implement PR-RI-003–006.



Implementing PR-RI-003 through PR-RI-006: checking out `main`, pulling, and creating each branch with its files.



Creating PR-RI-003: adding `kdp_store_royalty_reference.yaml` and updating `CHECKLIST.md`.



## Status: integration lane complete

### What was wrong and what was fixed
- **PR-RI-002:** The first push attached the YAML to the wrong history; the branch was rebuilt from `origin/main` with cherry-pick **`28d3bf2f`** and **force-pushed** to `agent/research-integration-hk-sg-markets`.
- **PR-RI-006:** The commit initially landed on **`agent/citation-convention`** (local **`db9f7af6`**). That branch was reset to **`origin/agent/citation-convention`**. PR-RI-006 was replayed on **`agent/research-integration-tw-cn-compliance`** as **`b935610e`** (includes **`CHECKLIST.md`**).
- **PR-RI-005:** An accidental commit picked up unrelated files; it was rewritten to **only** `asian_audiobook_market_data_followup.yaml` + `docs/LOCALE_CATALOG_MARKETING_PLAN.md` (**`4ef9b2d0`**, force-pushed).

### Open PRs (target `main`)
| PR ID | GitHub PR | Branch |
|--------|-----------|--------|
| PR-RI-001 | [#107](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/107) | `agent/research-integration-asian-bestseller-plan` |
| PR-RI-002 | [#108](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/108) | `agent/research-integration-hk-sg-markets` |
| PR-RI-003 | [#109](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/109) | `agent/research-integration-kdp-royalties` |
| PR-RI-004 | [#110](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/110) | `agent/research-integration-rakuten-apac` |
| PR-RI-005 | [#111](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/111) | `agent/research-integration-asian-market-followup` |
| PR-RI-006 | [#112](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/112) | `agent/research-integration-tw-cn-compliance` |

### Workstream TSV
- **`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`:** `ws_research_integration_20260330` → **`pr-open`**, with **#107–#112** in `temp_or_output_paths`, **`last_updated` `2026-03-31`**.
- This update is on **`agent/research-integration-workstreams-tsv`** — **[#113](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/113)**. Merge **#113** (or cherry-pick **`4e268e55`**) so `main` reflects the workstream row.

### Artifacts added (by spec §2)
- **PR-RI-003:** `config/payouts/kdp_store_royalty_reference.yaml` + `CHECKLIST` §KDP (on #109).
- **PR-RI-004:** `config/catalog_planning/competitive_intel_apac_audio.yaml`.
- **PR-RI-005:** `config/localization/asian_audiobook_market_data_followup.yaml` + Appendix **A.0** in `docs/LOCALE_CATALOG_MARKETING_PLAN.md`.
- **PR-RI-006:** `config/localization/tw_cn_distribution_compliance.yaml` + `config/payouts/cn_digital_tax_withholding_reference.yaml` + `CHECKLIST` China tax note.

### Note on `CHECKLIST.md`
- **PR-RI-006** adds the **China tax** block. **PR-RI-003** adds a **KDP** block on its own branch; if both merge cleanly you get both sections. If Git reports a conflict, resolve by **keeping both** sections.

### Local stashes
If you still need earlier WIP, check `git stash list` (e.g. `pearl ri003-006 local wip`, `pearl ri002 wip`, integration stash from the handoff).

