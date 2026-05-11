# RunComfy dispatcher `ModuleNotFoundError` — regression fix (PR follow-up to #1054)

**Date:** 2026-05-12
**Branch:** `agent/runcomfy-pythonpath-fix-20260512`
**Base:** `origin/main` tip `dc78acecf`
**Subsystem:** image_generation (RunComfy path)
**Severity (pre-fix):** 11,908 / 13,540 v3 batches (87.9%) would have failed before billing

---

## 1. Symptom (from PR #1054 Conductor v3 Phase 1 smoke)

All 6 Qwen panel cells routed to `runcomfy` failed identically with:

```
ModuleNotFoundError: No module named 'scripts'
```

The fault-tolerance wrapper (#1044) classified the error as `unknown`,
fail-fast'd each cell after 1 attempt, wrote a clean sidecar TSV, and the
run completed without aborting. Pearl Star path was unaffected (6/6 GREEN).

Net effect on a hypothetical full v3 fan-out: ~88% of batches dead before
they could be billed by RunComfy. Fault-tolerance saved us from cascading
failure, but the dispatch path was effectively dark.

## 2. Root cause

`scripts/image_generation/batch_runner.py` is invocable two ways:

1. **As a module:** `python3 -m scripts.image_generation.batch_runner …`
   — Python adds CWD (repo root) to `sys.path[0]`. `scripts.*` imports work.
2. **As a script:** `python3 scripts/image_generation/batch_runner.py …`
   — Python adds **the script's directory** (`scripts/image_generation/`) to
   `sys.path[0]`. `scripts.*` is **not** importable.

The Conductor v3 dispatch path uses form (2). When `batch_runner._runcomfy()`
calls `_load_dispatcher_module("runcomfy_dispatcher")`, the dispatcher's
top-level imports run:

```python
# scripts/image_generation/dispatchers/runcomfy_dispatcher.py:19
from scripts.image_generation import runcomfy_dispatch as _rc
from scripts.image_generation import runcomfy_cost_tracker as _bill
from scripts.image_generation import batch_runner as _br
from scripts.image_generation import runcomfy_spend_ledger as _ledger
```

…which raise `ModuleNotFoundError: No module named 'scripts'`. The Pearl Star
dispatcher (`pearl_star_dispatcher.py`) does **not** do any `from scripts.* …`
imports — only `subprocess` (ssh/scp/curl), which is why that path stayed
green.

## 3. Fix

Two-line, two-call sys.path injection in `scripts/image_generation/batch_runner.py`:

1. **Module-load-time** (covers `python3 scripts/image_generation/batch_runner.py …`):

```python
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
```

2. **Defensive in-function** in `_load_dispatcher_module` (covers callers
   that mutated `sys.path` after batch_runner was imported):

```python
def _load_dispatcher_module(file_stem: str) -> Any:
    …
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(qualname, path)
    …
```

Both guards are idempotent (`if str(REPO_ROOT) not in sys.path:`). No other
files modified. No refactor of dispatcher architecture.

## 4. Reproduction — BEFORE the fix

`git stash` removed the patch, then:

```bash
python3 scripts/image_generation/batch_runner.py --plan /tmp/runcomfy_pp_smoke/plan.md
```

stderr tail (verbatim):

```
File "…/scripts/image_generation/batch_runner.py", line 279, in dispatch
    return _runcomfy().dispatch(batch, dry_run=dry_run, **kwargs)
File "…/scripts/image_generation/batch_runner.py", line 195, in _runcomfy
    _runcomfy_mod = _load_dispatcher_module("runcomfy_dispatcher")
File "…/scripts/image_generation/batch_runner.py", line 177, in _load_dispatcher_module
    spec.loader.exec_module(module)
File "<frozen importlib._bootstrap_external>", line 850, in exec_module
File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
File "…/scripts/image_generation/dispatchers/runcomfy_dispatcher.py", line 19, in <module>
    from scripts.image_generation import runcomfy_dispatch as _rc
ModuleNotFoundError: No module named 'scripts'
```

cells passing dispatcher load: **0 / 3**.

## 5. Reproduction — AFTER the fix

```bash
python3 scripts/image_generation/batch_runner.py --plan /tmp/runcomfy_pp_smoke/plan.md
```

`dispatch_path: runcomfy` cells emit:

```json
{
  "dispatch_path": "runcomfy",
  "dry_run": true,
  "plan": {
    "batch_id": "pp_smoke_001",
    "workflow_hint": "flux_txt2img_manga",
    "notes": "workflow_json=flux_txt2img_manga.json"
  },
  "runcomfy_dispatch": {
    "dry_run": true,
    "workflow_path": ".../comfyui_workflows/flux_txt2img_manga.json",
    "deployment_id": "677edba8-ace0-4b2b-bad2-8e94b9959065",
    "workflow_node_count": 8,
    "api_base": "https://api.runcomfy.net/prod/v1",
    "token_loaded": true,
    "cooldown": false,
    …
    "status": "dry_run",
    "http_would_call": "https://api.runcomfy.net/prod/v1/deployments/.../requests",
    "notes": "No HTTP request sent (dry_run=True)."
  },
  "status": "dry_run"
}
```

(repeated for `pp_smoke_002` and `pp_smoke_003`)

cells passing dispatcher load: **3 / 3**.
`ModuleNotFoundError` occurrences in stdout+stderr: **0**.
RunComfy token: loaded from Keychain; **never logged**.

The same `_load_dispatcher_module` → `exec_module` → top-level
`from scripts.image_generation import …` sequence that crashed before is
exercised end-to-end on the dry-run path. Adding `--activate` would only
swap `dry_run=True` to `dry_run=False` and proceed to the HTTP call; the
import-stage regression is independent of network or billing state.

## 6. Regression test

`tests/image_generation/test_runcomfy_subprocess_pythonpath.py` — 4 tests,
all passing:

| # | Test | What it asserts |
|---|------|------------------|
| 1 | `test_batch_runner_script_invocation_keeps_scripts_importable` | Spawns a child Python with `sys.path[0] = scripts/image_generation/` (mimicking direct script invocation), imports `batch_runner`, calls `_runcomfy()`, expects no `ModuleNotFoundError` and a successful dispatcher load. |
| 2 | `test_runcomfy_dispatcher_top_level_imports_resolve_via_repo_root` | Verifies the dispatcher module's top-level `from scripts.image_generation import …` resolves via REPO_ROOT injection. |
| 3 | `test_repo_root_injected_at_module_import` | Plain `from scripts.image_generation import batch_runner` puts REPO_ROOT on `sys.path`. |
| 4 | `test_repeated_dispatcher_load_does_not_duplicate_sys_path_entries` | The guarded `if not in sys.path` predicate stays idempotent across 4 reloads. |

```text
tests/image_generation/test_runcomfy_subprocess_pythonpath.py::test_batch_runner_script_invocation_keeps_scripts_importable PASSED
tests/image_generation/test_runcomfy_subprocess_pythonpath.py::test_runcomfy_dispatcher_top_level_imports_resolve_via_repo_root PASSED
tests/image_generation/test_runcomfy_subprocess_pythonpath.py::test_repo_root_injected_at_module_import PASSED
tests/image_generation/test_runcomfy_subprocess_pythonpath.py::test_repeated_dispatcher_load_does_not_duplicate_sys_path_entries PASSED
============================== 4 passed in 0.58s ===============================
```

Full `tests/image_generation/` suite: **55 passed, 0 failed** (51 pre-existing
+ 4 new). No regressions in fault-tolerance, dispatch routing, spend ledger,
or batch-plan parsing tests.

## 7. Conductor v3 fan-out — un-blocked at the import layer

Pre-fix:  RunComfy share of v3 = 11,908 / 13,540 batches → 100% would
ModuleNotFoundError before any HTTP call.
Post-fix: RunComfy dispatcher loads cleanly under direct-script invocation;
remaining gates are unchanged (cost cap, billing poll, queue, network).
No other smoke targets touched (no PNG outputs, no real spend, no fan-out armed).

## 8. WRITE_SCOPE

```
scripts/image_generation/batch_runner.py
tests/image_generation/test_runcomfy_subprocess_pythonpath.py
artifacts/qa/runcomfy_pythonpath_regression_fix_2026_05_12.md
```

3 files. No deletions. No paid-LLM key reads (`audit_llm_callers.py` → `violation_count: 0`).
