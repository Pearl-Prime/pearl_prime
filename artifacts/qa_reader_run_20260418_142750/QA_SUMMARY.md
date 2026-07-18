# QA canary — post–PR #492 (`main` @ 4aa14983d8)

**Run:** 2026-04-18 (local)  
**Worktree:** `/Users/ahjan/.cursor/phoenix_canary_wt` (reset to `origin/main` = `4aa14983d8`)  
**Output dir:** `artifacts/qa_reader_run_20260418_142750/`

---

## Render

| Field | Value |
|--------|--------|
| **Exit code** | **1** (Python traceback; pipeline did not finish) |
| **Wall clock (approx.)** | **~588 s** (`time` reported `real 588.12`) |
| **Failure** | `OSError: [Errno 28] No space left on device` writing `selected_content_variants.json` under this OUT dir |
| **`book.txt`** | **Not produced** (render aborted before completion) |

### Disk (at time of failure)

`df` on `/System/Volumes/Data`: **~598 MiB free**, volume reported **100%** used — insufficient for the pipeline’s intermediate JSON writes.

**Operator action:** free several GB (artifacts, old worktrees, Xcode/simulator caches, large `artifacts/` trees), then re-run the same `run_pipeline.py` command with a fresh `--render-dir`.

### Partial log

See `render.log` in this directory (early spine warnings + exercise fallbacks + traceback tail).

---

## Pearl Star Ollama

`curl http://192.168.1.101:11434/api/tags` (5s timeout): **unreachable** from this agent session.  
Recorded in `ollama_probe.txt`.

---

## Workers Builds: `pearl-prime` (health snapshot)

This check is a **GitHub Check Run** (not a repo workflow name usable with `gh run list --workflow=...`).

Sample on recent `main` commits (API: `commits/{sha}/check-runs`, filter name `Workers Builds: pearl-prime`):

| `main` tip (short) | `pearl-prime` conclusion |
|--------------------|---------------------------|
| `4aa1498` | **failure** |
| `35fb99f` | **failure** |
| `70a6908` | *none* (check absent on that commit) |
| `ac89e4e` … (older sampled) | **failure** when present |

**Finding:** **Consistently red** when the check is attached — not “green with one red merge.” Treat as **either broken integration / wrong required-check wiring**, or **intentionally non-blocking**; align branch protection with intent so merges are not “red by default.”

**Recommendation:** Operator decides: **required + fix Cloudflare Workers deploy**, or **not required + remove from required checks** (same pattern as prior “Change impact” cleanup).

---

## Museum (`run_museum_gates`)

**Not run** — no `book.txt` to analyze.

After a successful render, run from repo root (with `PYTHONPATH=.`):

```bash
export OUT=/path/to/this/run/dir
PYTHONPATH=. python3 - <<'PY'
# Use the same flat-book loader as CI (see .github/workflows/regression-museum-gate.yml)
# or the pipeline’s native book dict if exposed.
PY
```

---

## Pipeline gate scores / ONTGP / `score_external_text.py`

**N/A** — render did not complete; no gate report JSON or book-level scores in this OUT dir.

---

## Chapter excerpts

**N/A** — no `book.txt`.

---

## CLOSEOUT_RECEIPT

| Item | Value |
|------|--------|
| Workers `pearl-prime` | **Mostly failure** on sampled `main` SHAs when check exists → **stale/broken or wrong required-check posture** (operator decision) |
| Render exit + wall | **1**, **~588 s** |
| `book.txt` path + size | **Missing** |
| Museum JSON | **Not produced** |
| Gate scores / ONTGP | **N/A** |
| `QA_SUMMARY.md` | This file |
| PR | **Not opened** — deliverable incomplete until disk is freed and render finishes |
| **NEXT_ACTION** | Free disk space → re-run canary into a **new** `artifacts/qa_reader_run_*` → museum → PR with `book.txt` for Pearl_Editor markup |
