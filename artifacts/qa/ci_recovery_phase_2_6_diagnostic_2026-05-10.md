# CI recovery — Phase 2.6 diagnostic (Core tests still red after Phase 2.5)

**PROJECT_ID:** `PRJ-CI-BASELINE-RECOVERY-V1`  
**SUBSYSTEM:** `pearl_devops`  
**Agent role:** Pearl_DevOps (read-only investigation; this file is evidence + recommendation only — no code or workflow changes in this PR).  
**Date:** 2026-05-10  

---

## STARTUP_RECEIPT

| Field | Value |
|--------|--------|
| Objective | Explain why **Core tests** remains **failure** on `main` after Phase 2.5 (`fastapi` in `requirements-test.txt`); identify the **next** blocker (not “missing fastapi”). |
| Evidence run | GitHub Actions run **25615226642** — `headSha` **f079451f3c5fa45e44993aa4da3affda844cf81f** — [run URL](https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/25615226642) |
| Scope | Diagnostic + Phase 2.6 fix **proposal** only. |

---

## 1. Capture (verbatim failure excerpts)

From `gh run view 25615226642 --log-failed` — job **Core tests** → step **Run fast/core pytest**:

```text
ERROR collecting tests/test_server_health.py
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/starlette/testclient.py:38: in <module>
    import httpx
E   ModuleNotFoundError: No module named 'httpx'
[...]
tests/test_server_health.py:20: in <module>
    from fastapi.testclient import TestClient
[...]
/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/starlette/testclient.py:40: in <module>
    raise RuntimeError(
E   RuntimeError: The starlette.testclient module requires the httpx package to be installed.
E   You can install this with:
E       $ pip install httpx
ERROR tests/test_server_health.py - RuntimeError: The starlette.testclient module requires the httpx package to be installed.
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
```

Pytest stopped with **`-x`** after this **collection error**; later steps (smoke CLI, marketing config, onboarding registry, freebie index, **production readiness gates / Gate 18**) did **not** execute in this run.

---

## 2. Root cause

| Item | Detail |
|------|--------|
| **Failing artifact** | `tests/test_server_health.py` imports `from fastapi.testclient import TestClient` at module import time (lines 19–25). |
| **Mechanism** | `fastapi.testclient` re-exports Starlette’s `TestClient`. Starlette’s `starlette.testclient` **imports `httpx`** and raises **`RuntimeError`** if `httpx` is missing — this is **not** satisfied by installing `fastapi` alone. |
| **CI install path** | `.github/workflows/core-tests.yml` installs **only** `pip install -r requirements-test.txt`. After Phase 2.5, that file includes **`fastapi>=0.100.0`** but **does not** list **`httpx`**. |
| **Contrast** | `.github/workflows/server-ci.yml` installs `requirements-test.txt` **and** runs **`pip install httpx`** as a separate step — so server CI already assumed `httpx` was needed for client-style tests; **Core tests** never gained the same dependency. |

**One-liner:** Core tests fail because **`httpx` is absent** while **`test_server_health`** uses **`TestClient`**, which hard-requires `httpx`.

---

## 3. Why Phase 2.5 did not fully fix Core tests (precise reason)

Phase 2.5 correctly addressed the **first** import failure class (**`ModuleNotFoundError: No module named 'fastapi'`**) by adding **FastAPI** to **`requirements-test.txt`**.

That change **enabled** the next import in the chain: **`fastapi.testclient` → `starlette.testclient` → `httpx`**. **`httpx` is an optional/runtime peer** for the test client stack; it is **not** pulled in as a guaranteed transitive dependency of a minimal `pip install fastapi` in the versions used on the runner. Therefore the workflow progressed to a **new** collection error — **missing `httpx`** — which pytest still treats as fatal under **`-x`**.

So Phase 2.5 fixed **FastAPI importability** but did not complete the **TestClient dependency closure** for `tests/test_server_health.py`.

---

## 4. Recommended Phase 2.6 plan

| Option | Action | Files | Effort |
|--------|--------|-------|--------|
| **A (preferred)** | Add **`httpx`** (with a sane lower bound, e.g. `httpx>=0.24.0` or align with Starlette/FastAPI docs) to **`requirements-test.txt`** so **every** workflow that only installs that file gets a consistent client stack. | `requirements-test.txt` | **S** (single dependency line + optional comment that TestClient needs it) |
| **B** | Add **`pip install httpx`** to **`.github/workflows/core-tests.yml`** only (mirrors `server-ci.yml`). | `core-tests.yml` | **S** (one step line; less DRY than A) |
| **C (test-local)** | Defer `TestClient` import behind a **`try`/`except`** and skip when `httpx` missing — **not recommended** here: the test module docstring already states **`Requires: pip install httpx fastapi uvicorn`**; CI should install what tests declare. | `tests/test_server_health.py` | **M** (behavior change; masks misconfigured CI) |

**Recommendation:** **Option A** — keeps **one** source of truth for test deps, aligns **Core tests** with **`server-ci.yml`** expectations without duplicating pip lines across workflows.

**Follow-on verification (implementation PR, out of scope here):** Re-run **Core tests** on `main`; expect either **green** through pytest or the **next** surfaced failure (e.g. **uvicorn** or app import issues, or a gate only reached after pytest completes). This diagnostic does not assert green gates until pytest completes.

---

## 5. References (repo paths)

- Workflow: `.github/workflows/core-tests.yml` — install step uses **only** `requirements-test.txt`.
- Test module: `tests/test_server_health.py` — docstring lines 1–6 document **`httpx`**; import of **`TestClient`** at line 20.
- Phase 2.5 dependency file: `requirements-test.txt` — lists **`fastapi`**; **no** **`httpx`** at time of diagnosis.
- Partial precedent: `.github/workflows/server-ci.yml` — explicit **`pip install httpx`**.

---

## CLOSEOUT_RECEIPT (diagnostic session)

| Field | Value |
|--------|--------|
| **Root cause (one-liner)** | **Missing `httpx`** for **`fastapi.testclient` / Starlette `TestClient`** in **Core tests** install set. |
| **Phase 2.6 fix scope** | **S** — add **`httpx`** to **`requirements-test.txt`** (or one-line workflow install in **`core-tests.yml`**). |
| **Production gates reached?** | **No** in run **25615226642** — pytest **collection error** stopped the job before later steps. |
