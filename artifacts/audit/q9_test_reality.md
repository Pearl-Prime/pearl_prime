# Q9 — Test-Suite Reality

**Date:** 2026-04-29

## A. Volume

- `tests/*.py` files: **233**
- `def test_*` / `async def test_*` functions: **1,246**
- Average ~5.3 tests per file.

## B. Distribution by subsystem

Method: `for kw in <subsystem>; do find tests/ -name '*.py' -exec grep -l "$kw" {} \; | wc -l`. (File-count, not test-function count, but a usable proxy.)

| subsystem | test files referencing |
|---|---:|
| manga | 52 |
| video | 22 |
| ei_v2 | 21 |
| pearl_news | 15 |
| translation | 6 |
| pearl_prime | **5** |
| marketing | 5 |
| freebie | 5 |
| recommend | 5 |
| audiobook | 3 |
| podcast | 2 |
| **brand_admin** | **0** |

## C. Findings

### C.1 The flagship is under-tested
**`pearl_prime` has 5 test files.** This is the canonical book pipeline — the system that owns `proj_pearl_prime_bestseller_rebase_20260425`, the 20-chapter arc, the variant coverage gate, the 2,584 atoms. It is gated by 5 test files. By contrast `manga` has 52.

### C.2 Revenue surfaces are under-tested
brand_admin (0), audiobook (3), podcast (2), marketing (5), freebie (5), recommend (5). These are the surfaces that produce or distribute revenue. `pearl_news` (15) is the exception — it ships, and it has tests.

**Pattern:** subsystems with a strong CI workflow (manga 16 workflows, video, ei_v2) have tests. Subsystems without CI have very few. The CI-test bond is intact; the incentive to write tests for non-CI'd code is missing.

### C.3 Aggregate pass rate (last 14d): 60.8%
Per [`q8_ci_health.md`](./q8_ci_health.md). 562/924 successful runs. **39.2% of CI runs are failing or never run.** That is the test-suite-and-environment quality envelope, not 100%.

### C.4 14 BROKEN + 13 DEAD workflows out of 75
Per q8. 27 of 75 (36%) workflows are broken or dead. Some of these are the very gates that "test the tests."

### C.5 EI V2: 21 tests, advisory only
21 tests for a system whose promotion gate has not been exercised (`learned_params.json` ≈ `learned_params_seed.json`). Tests pass; promotion does not. Tests are not the bottleneck — operator decision is.

### C.6 Spec-739 variant coverage gate: 4 tests
Modest coverage given the gate is now strict. Acceptable because the validator's failure modes are deterministic.

## D. Tests-vs-readiness mismatch

Cross-tabulating test count with subsystem readiness percent (from [`q4_subsystem_matrix.md`](./q4_subsystem_matrix.md)):

| subsystem | tests | readiness % | mismatch |
|---|---:|---:|---|
| manga_pipeline | 52 | 35 | OVER-tested for current shipping (good — building toward) |
| pearl_prime | 5 | 65 | **UNDER-tested for shipping rate** |
| audiobook | 3 | 35 | matched |
| pearl_news | 15 | 75 | well-matched |
| brand_admin | 0 | 55 | **CRITICAL UNDER-test** |
| ei_v2 | 21 | 70 | well-matched |
| podcast | 2 | 30 | matched |

**Single biggest test-coverage cliff:** `brand_admin` at 0 tests, 55% readiness, ratified architectural path (DASH-02). Should not advance to higher readiness without a test harness.

## E. Untested hot paths (spot-check)

Without running coverage tools, qualitative spot-check:

- `scripts/publish/kdp_comics_upload.py` — no test. Used as production entry to KDP.
- `scripts/publish/webtoon_canvas_upload.py` — no test. Used as production entry to WEBTOON.
- `scripts/run_pipeline.py:1438-1444` — no test of the silent `--pipeline-mode` default (q6 §B.2). Tested implicitly via downstream tests but not directly.
- The EPUB packager: doesn't exist (q5 C7), so trivially untested.

## F. Recommendations

1. **brand_admin test harness** — 2 engineer-days. Phase 4.
2. **pearl_prime end-to-end smoke test** — 1 engineer-day. Run the full book pipeline against one fixture (1 brand × 1 persona × 1 topic × 1 locale) and assert outputs. Phase 2.
3. **scripts/publish/* test harness** — 1 engineer-day. Mock the KDP/WEBTOON APIs; assert the package format is valid. Phase 1.
4. **Re-run q8 CI health pass quarterly** — 1 hour.
