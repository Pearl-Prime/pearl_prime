# Plan-Scale QA — PILOT verdict (corporate_managers × {burnout, anxiety} × 7 durations)

**Date:** 2026-06-30 · **Agent:** Pearl_Dev + Pearl_Research · **Harness:** `scripts/qa/plan_scale_qa_suite.py`
**Scope:** PILOT ONLY. This verdict gates the ~1000-plan sweep. The sweep was NOT run.

## The one question

> Are Pearl Prime book PLANS a trustworthy proxy for ASSEMBLED books on cohesion +
> therapeutic value, and are assembled books clean of pipeline leakage?

## Headline (report loudly, per mission)

**The proxy splits on two axes — answer them separately:**

| Axis | Verdict | Evidence |
|---|---|---|
| **Leakage** | ✅ CLEAN | 0/13 assembled books had any artifact/header/placeholder/FixtureReplay leak. `delivery_contract_gate` (canonical oracle) PASS on all. |
| **QUALITY proxy** (plan-cohesion PASS ⇒ assembled register PASS) | ⚠️ MOSTLY HOLDS, 1 BREAK | 12/13 assembled cells: plan-cohesion PASS → register PASS/WARN. **1 BREAK: `burnout × extended_book_2h`** — plan-cohesion PASS but assembled register **F2 HARD_FAIL**. |
| **STRUCTURAL proxy** (a plan-time chapter count predicts assembled chapter count) | ❌ **BROKEN** | **0/13** cells match. No plan-time count — not the format-registry default, not the arc SSOT `chapter_count` — predicts the assembled chapter count. |

### Why STRUCTURAL proxy is BROKEN (the real linchpin failure)

There are **three different chapter counts** in play and the assembler honours **none of the plan-visible ones**:

| Format | format_registry default | arc SSOT `chapter_count` | **ASSEMBLED (actual)** |
|---|---:|---:|---:|
| micro_book_15 | 5 | 7 (burnout F003) / 20 (anxiety F006) | **5** |
| micro_book_20 | 6 | 7 / 20 | **6** |
| short_book_30 | 8 | 7 / 20 | **8** |
| standard_book | 10 | 7 / 20 | **12** |
| extended_book_2h | 14 | 7 / 20 | **12** |
| deep_book_4h | 16 | 7 / 20 | **12** |
| deep_book_6h | 20 | 7 / 20 | **12** (burnout = BUILD_FAIL) |

The assembled chapter count is set by the **runtime word-ceiling beatmap** inside the
assembler (`run_pipeline.py` `_n_chapters = len(beatmap.chapters)`, shaped by the
runtime word ceiling), which is **invisible to any standalone plan-level scorer.**
A plan-level cohesion gate that reasons about "N chapters" is reasoning about a chapter
count the assembled book will not have for any format ≥ `standard_book` (all clamp to 12).

**Implication for the sweep:** plan-cohesion is a usable *quality* screen but is NOT a
structural proxy. Any sweep that ranks/accepts plans on chapter-level structure will be
scoring a structure the assembler discards. The sweep must either (a) score plans only
on count-invariant properties (band-arc shape, intensity cadence, structure variety —
all of which the harness already checks and which all PASS), or (b) the assembler's
runtime chapter-count contract must be exposed to the planner so the two agree.

### Human (free-Tier-1) read — the cohesion truth register PASS misses

Paragraph-level prose is **therapeutically strong and bestseller-adjacent** (accurate
burnout/anxiety signatures, somatic practices, warm contemplative voice). The assembled
weakness is **cohesion between atoms**: short interstitial bridge/scene-anchor fragments
inserted between paragraphs that do not connect to surrounding prose and recur near-verbatim
across chapters *and* across topics. Several cells PASS `register_gate` yet read as
cohesion-weak to a human. So **plan-cohesion + register PASS together still UNDER-predict
reader-felt cohesion.** Full per-book verdicts: `FREE_TIER1_READS.json`.

## Buildability census (14 cells)

- **PLANNABLE (assembled):** 13
- **BUILD_FAIL:** 1 — `burnout × deep_book_6h` (scene_anchor density cap: >3-word phrase
  repeats exceed cap 3; render halted before `book.txt`). `anxiety × deep_book_6h` built fine.
- NO_ARC / BAND_DEFICIT / NO_STORY_POOL: 0

## Plan-cohesion (deterministic, plan-only): **14/14 PASS**

All plans pass structural cohesion (chapter-count integrity, arc-position coverage, band-arc
smoothness, final-not-peak, dwell macro-cadence, bestseller-structure variety, cost-chapter
placement). The plan layer is clean — its limitation is that PASS does not survive into the
assembled chapter count, and once into one assembled register check (F2).

## EI v2 (deterministic weighted-sum, per assembled cell)

| cell | EI composite | bestseller craft (ONTGP) | register | book_pass |
|---|---:|---:|---|---|
| burnout micro_15 | 0.615 | 0.485 | PASS | PASS |
| burnout micro_20 | 0.602 | 0.498 | PASS | PASS |
| burnout short_30 | 0.596 | 0.499 | PASS | PASS |
| burnout standard | 0.626 | 0.500 | PASS | PASS |
| burnout extended_2h | 0.618 | 0.524 | **FAIL (F2)** | PASS |
| burnout deep_4h | 0.641 | 0.521 | PASS | PASS |
| burnout deep_6h | — | — | BUILD_FAIL | — |
| anxiety micro_15 | 0.587 | 0.474 | PASS | PASS |
| anxiety micro_20 | 0.611 | 0.495 | PASS | PASS |
| anxiety short_30 | 0.616 | 0.491 | PASS | PASS |
| anxiety standard | 0.632 | 0.547 | PASS | PASS |
| anxiety extended_2h | 0.655 | 0.565 | PASS | PASS |
| anxiety deep_4h | 0.640 | 0.622 | PASS | PASS |
| anxiety deep_6h | 0.666 | 0.651 | WARN | PASS |

EI composite is consistently above the 0.55 pass threshold; craft (ONTGP) rises with length.

## register-FAILs handed to OPD-20260629-002 (listed, NOT fixed)

1. `burnout × extended_book_2h` — register **F2 HARD_FAIL** (1). The single quality-proxy break.
2. `burnout × deep_book_6h` — **scene_anchor density cap** HARD_FAIL (>3-word phrase repeats > cap 3); blocks the deepest burnout build.
3. `anxiety × deep_book_6h` — register **WARN** (advisory; built and passed book_pass).

## Files

- `MATRIX.tsv` / `MATRIX.json` — full per-cell matrix + summary
- `cell__<duration>__<topic>.json` — per-cell stage detail (plan, plan-cohesion, equivalence, leakage, EI v2)
- `FREE_TIER1_READS.json` — agent's own read of each assembled book
- `renders/<duration>__<persona>__<topic>/` — assembled book.txt + all gate reports

## Verdict for the sweep gate

- **Leakage clean → GO** on the leakage axis.
- **Quality proxy usable** (1 break in 13) → GO with a caveat: track register breaks per cell.
- **Structural proxy BROKEN → the sweep must NOT rely on plan chapter-structure.**
  Recommend the orchestrator scale on count-invariant plan-cohesion only, OR first reconcile
  the planner ↔ assembler chapter-count contract. Pilot equivalence did NOT hold on structure.
