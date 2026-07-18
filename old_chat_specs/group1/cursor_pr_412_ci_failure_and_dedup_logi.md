# PR #412 CI failure and dedup logic
_Exported on 4/16/2026 at 19:22:30 GMT+8 from Cursor (3.1.15)_

---

**User**

STARTUP — Fix PR #412 CI failure: dedup stripping word budget in registry mode
═══════════════════════════════════════════════════════════════════════════════

You are operating in the Phoenix Omega repo (Ei V2 active).
Read before doing any work:

  1. docs/SESSION_UNITY_PROTOCOL.md
  2. phoenix_v4/rendering/book_renderer.py  (clean_for_delivery + _dedup_repeated_blocks)
  3. tests/test_spine_pipeline_integration.py  (failing test context)
  4. artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

Emit a STARTUP_RECEIPT before doing any work.

─────────────────────────────────────────────────────────────────────────────
PROJECT CONTEXT
─────────────────────────────────────────────────────────────────────────────

PROJECT_ID:   proj_state_convergence_20260328
SUBSYSTEM:    core_pipeline
BRANCH:       agent/book-output-qa-fix  (PR #412, open, not merged)
LAST COMMIT:  8918b89015

─────────────────────────────────────────────────────────────────────────────
FAILING CI CHECK
─────────────────────────────────────────────────────────────────────────────

Test:    tests/test_spine_pipeline_integration.py::test_registry_mode_still_runs_for_anxiety
Failure: Word count gate FAILED
         Runtime target : short_book_30 → 4,500–7,500 words
         Actual output  : 1,981 words (44% of minimum)
         Deficit        : 2,519 words

ROOT CAUSE:
  _dedup_repeated_blocks() added in PR #412 runs inside clean_for_delivery()
  on ALL render paths, including registry mode (short_book_30 / anxiety /
  gen_z_professionals). Registry mode already produces thin output (~2k words
  before dedup). The dedup pass removes repeated paragraphs that were
  previously counting toward the word budget, pushing the output below the
  4,500-word gate.

  This test was passing on main before PR #412. The dedup change introduced
  the regression.

─────────────────────────────────────────────────────────────────────────────
THE FIX
─────────────────────────────────────────────────────────────────────────────

FILE:  phoenix_v4/rendering/book_renderer.py

Guard _dedup_repeated_blocks so it does not run when doing so would drop the
output below the word count minimum. Two acceptable approaches — Pearl_Dev
chooses whichever is cleaner given the code:

  OPTION A — Post-dedup word count guard:
    After dedup, count words in result. If result word count is less than
    the pre-dedup count by more than 15% OR falls below 4,500 words,
    return the pre-dedup text instead and emit a warning in the returned
    text's leading comment block (stripped by clean_for_delivery later).
    Accept a `min_words` parameter (default 4500) in _dedup_repeated_blocks.

  OPTION B — Pipeline mode flag:
    Add a boolean parameter `dedup_enabled: bool = True` to clean_for_delivery.
    Pass dedup_enabled=False from the registry render path
    (book_renderer.py render_book / render_chapter, or wherever registry mode
    is detected). Spine mode keeps dedup_enabled=True.
    This is the cleaner separation if the registry path is clearly distinct.

  OPTION C — Minimum word floor per format:
    Accept a `word_floor: int = 0` parameter in _dedup_repeated_blocks.
    If post-dedup word count < word_floor, return pre-dedup text.
    Caller passes word_floor from the pipeline's known format target.

  Do NOT simply disable dedup globally — the spine pipeline benefit is real
  and must be preserved for grief_postfix and longer formats.

─────────────────────────────────────────────────────────────────────────────
TESTS
─────────────────────────────────────────────────────────────────────────────

  a. Add a test in tests/test_book_renderer.py (or test_clean_for_delivery.py)
     covering: when dedup would drop output below floor, pre-dedup text is
     returned (or dedup is skipped per chosen option).

  b. Confirm locally:
         PYTHONPATH=. python -m pytest tests/test_book_renderer.py \
           tests/test_spine_pipeline_integration.py -x -q

  c. Confirm no regression on the 22 existing tests in test_book_renderer.py.

─────────────────────────────────────────────────────────────────────────────
GIT
─────────────────────────────────────────────────────────────────────────────

  Push fix to existing branch agent/book-output-qa-fix.
  Run push_guard + preflight before pushing.
  PR #412 will re-run CI automatically on push.
  Do NOT open a new PR.

─────────────────────────────────────────────────────────────────────────────
OUT OF SCOPE
─────────────────────────────────────────────────────────────────────────────

  - Workers Builds: pearl-prime failure — Cloudflare build, unrelated, skip
  - micro_book_differentiation decision — owner decision pending, do not touch
  - ws_bestseller_spines_20260410 (active, do not interleave)

─────────────────────────────────────────────────────────────────────────────
DONE CRITERIA
─────────────────────────────────────────────────────────────────────────────

  ✓ test_registry_mode_still_runs_for_anxiety passes
  ✓ 22 existing test_book_renderer.py tests still pass
  ✓ grief_postfix dedup still active (spine path unaffected)
  ✓ Fix pushed to agent/book-output-qa-fix
  ✓ CLOSEOUT_RECEIPT with commit SHA, test results, CI link


---

**Cursor**

Reading required docs and code, then emitting STARTUP_RECEIPT and implementing the dedup guard fix.



Emitting STARTUP_RECEIPT and implementing the word-floor guard: derive the floor from the plan's `runtime_format_id` via `_runtime_word_range` so registry books keep pre-dedup text when dedup would drop below the format minimum; `plan=None` leaves `word_floor=0` (spine/enrichment paths unchanged).



Implementing code and tests.



Investigating why the word floor isn't applied: the test still reports 1,981 words — checking whether the plan includes `runtime_format_id` when `clean_for_delivery` runs.



Identifying the issue: the registry fast-path in `run_pipeline.py` calls `clean_for_delivery(prose)` without a plan, so `word_floor` stays 0. Passing a plan that includes `runtime_format_id`.



Running push preflight, then committing and pushing.



```
STARTUP_RECEIPT
AGENT:              Cursor Agent (Pearl_Dev)
TASK:               Fix PR #412 CI: registry-mode word gate after dedup in clean_for_delivery
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv;specs/PHOENIX_V4_5_WRITER_SPEC.md (via SUBSYSTEM_AUTHORITY_MAP core_pipeline)
READ_PATH_COMPLETE: yes — required reads 1–4 completed; ACTIVE_WORKSTREAMS reviewed (ws_bestseller_spines_20260410 active — not touched)
WRITE_SCOPE:        phoenix_v4/rendering/book_renderer.py;scripts/run_pipeline.py;tests/test_book_renderer.py
OUT_OF_SCOPE:       config/spines/*;Workers Builds;micro_book_differentiation;artifacts/coordination/ACTIVE_WORKSTREAMS.tsv edits
BLOCKERS:           none
READY_STATUS:       ready
```

## What was wrong

`_dedup_repeated_blocks` was doing the right thing when `clean_for_delivery` received a **plan with a runtime format**, but the **section-registry path** in `scripts/run_pipeline.py` called `clean_for_delivery(prose)` with **no `plan`**, so `word_floor` was always `0` and dedup could still shrink registry output. That kept the anxiety registry integration test failing the `short_book_30` minimum.

## What we changed

1. **`_dedup_repeated_blocks`** — Added optional `word_floor`. After dedup, if `post_wc < word_floor` (and `word_floor > 0`), return the pre-dedup string and **`logger.warning`** (no prose comment block).

2. **`clean_for_delivery`** — Sets `word_floor` from `_delivery_word_floor_from_plan(plan)` using `runtime_format_id` / `book_spec.runtime_format_id` and `format_registry.yaml`. **`plan=None`** keeps `word_floor=0` (same as before for spine helpers that pass no plan).

3. **`scripts/run_pipeline.py`** — Passes `plan={"runtime_format_id": ...}` into `clean_for_delivery` for **registry** and **spine** render paths so the floor is known.

4. **Tests** — `test_dedup_repeated_blocks_keeps_pre_dedup_when_below_word_floor` and `test_clean_for_delivery_dedup_respects_runtime_word_floor`.

## Verification

- `PYTHONPATH=. python3 -m pytest tests/test_book_renderer.py tests/test_spine_pipeline_integration.py -x -q` → **30 passed** (`test_book_renderer.py` now **24** tests, i.e. previous 22 + **2** new).

```
CLOSEOUT_RECEIPT
AGENT:          Cursor Agent (Pearl_Dev)
TASK:           Fix PR #412 CI: dedup vs registry word budget
COMMIT_SHA:     57da7cbced
FILES_WRITTEN:  phoenix_v4/rendering/book_renderer.py; scripts/run_pipeline.py; tests/test_book_renderer.py
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; phoenix_v4/rendering/book_renderer.py; tests/test_spine_pipeline_integration.py; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; scripts/run_pipeline.py (registry path)
STATUS:         completed
HANDOFF_TO:     none
NEXT_ACTION:    Watch PR #412 CI; https://github.com/Ahjan108/phoenix_omega_v4.8/pull/412
```

**CI:** [PR #412](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/412) should re-run on push to `agent/book-output-qa-fix` (`57da7cbced`).

**Spine dedup:** Spine output still uses dedup with a word floor derived from `runtime_fmt`; long manuscripts stay above the floor, so dedup is not disabled globally. Registry path now supplies the same floor so thin books do not fall through dedup below the format minimum.

---

**User**

do you have sai_maa_vid.mp4 or ra.mp4 ?
were you helping me move vids? 

---

**Cursor**

Searching the repo for those filenames. I don't have memory of a prior chat about moving videos unless it was in this thread (we only worked on the PR #412 dedup fix).



**This chat:** We only worked on the PR #412 dedup / registry word-count fix. There was no video move work in this thread.

**Those filenames:** I don’t store files myself. Under **`/Users/ahjan/phoenix_omega`**, a Spotlight search for exact names `sai_maa_vid.mp4` and `ra.mp4` returned **no paths**. That doesn’t prove they’re nowhere on your Mac—only that they’re **not showing up under that tree with those names** (or not indexed).

If you want to double-check locally:

```bash
mdfind 'kMDItemFSName == "sai_maa_vid.mp4" || kMDItemFSName == "ra.mp4"'
```

If you remember roughly where the “move vids” task lived (another agent chat, folder, or machine), say what you recall and we can narrow it down.

