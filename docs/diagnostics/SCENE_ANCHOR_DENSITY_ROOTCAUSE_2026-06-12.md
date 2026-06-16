# scene_anchor_density — Root-Cause + Fix Diagnosis (Roadmap B.1 P0, lane L2)

**Date:** 2026-06-12
**Author:** Pearl_Dev (L2 execution subagent)
**Roadmap row:** B.1 P0 row 1 — "scene_anchor_density 87% pre-render block (174/200 rejected)"
**Verdict:** The gate is **already fixed** on `main` (PR #1091, merged 2026-05-12). The
"174/200 / 87%" figure the roadmap cites is a **stale audit artifact** measured at the
*legacy* cap=2, never regenerated after the fix. This session: (1) confirmed the fix is live,
(2) repaired the downstream report that kept presenting the fixed gate as the #1 open blocker,
(3) added a regression test so the cap cannot silently re-tighten.

---

## 1. The claim under investigation

`artifacts/qa/en_us_catalog_bestseller_audit_2026-05-13.md` (TL;DR):

> - **200 BookSpecs assembled** … **26 books (13.0%) rendered** … the remaining **174 (87.0%)
>   failed at production quality gates pre-render**.
> - **Dominant failure mode: `scene_anchor_density` (168 books, 84.0% of catalog)**.
> - Until scene_anchor_density failures are addressed, ~87% … never reach the scoring stage.

This is the source of the roadmap's "#1 critical-path 87% block."

## 2. What `scene_anchor_density` actually gates

Config: `config/quality/scene_anchor_density_config.yaml` → `default_cap_per_chapter`.
Gate: `scripts/run_pipeline.py`:
- `_load_scene_anchor_density_config()` (L405) loads the cap.
- `_scene_anchor_density_violations(prose, cap)` (L438) enumerates every overlapping 4..8-word
  n-gram per paragraph **within each chapter**; a phrase appearing in **more than `cap`
  paragraphs of one chapter** is a violation (predicate `len(indices) > cap`, L469).
- The book cap is `min(scene_plan.scene_anchor_cap | default)` across chapters (L850-853), so a
  hand-tuned plan can only *tighten*, never loosen.

Semantics: per-**chapter**, on ≥4-word phrases. (The stale report prose mis-described it as
"≥4-word phrases capped at 2 **per book**" — wrong on both the unit and the value.)

## 3. Root cause — stale artifact, not an open gate

**The cap was raised 2→3 and the audit was never re-run.** Evidence chain, three independent
sources, all reproduced this session:

### 3a. The config is already cap=3, and loads correctly
`config/quality/scene_anchor_density_config.yaml` → `default_cap_per_chapter: 3`. Executing the
real loader from `run_pipeline.py` on current `main`:
```
_load_scene_anchor_density_config() -> {'default_cap_per_chapter': 3, 'collapse_overlapping_ngrams': True}
```
The config header itself documents the change: *"With cap=2 (legacy default), 168/200 BookSpecs
failed … 156 of 168 had max paragraph_count = 3 (one over cap) … Raising the default to cap=3
recovers ~91% catalog yield."* — dated 2026-05-13, PR #1089/#1091.

### 3b. The audit MD predates the fix wiring through
The MD is dated **2026-05-13**; the live render `run.log`s from **2026-05-17/05-18** still emit:
```
Scene anchor density cap: FAIL — repeated >3-word phrases exceed cap 2.
```
i.e. those render inputs were produced under the **old cap=2**. The 168/200 in the MD is the
cap=2 snapshot. No catalog re-render at cap=3 was ever aggregated, so the MD never updated.

### 3c. Empirical: every observed cap=2 failure is recovered by cap=3
Swept all 16 `scene_anchor_density_report.json` files present in `artifacts/`:

| bucket | count | meaning |
|---|---:|---|
| already PASS (no violations) | 11 | incl. all 9 gold_reference_ladder 2026-05-30 runs (these ran at **cap=3**) |
| FAIL@cap2 but max paragraph_count ≤ 3 → **PASS@cap3** | 5 | the "one-over-cap2" natural-motif case |
| FAIL@cap2 AND max paragraph_count ≥ 4 → still FAIL@cap3 | **0** | no genuine 4+ repetition in the sample |

This matches PR #1091's own sweep of all 168 failures (156 at pc=3, 11 at pc=4, 1 at pc=5):
the overwhelming majority are a single paragraph over the legacy cap.

### 3d. Unit test confirms the gate predicate
`scripts/pearl_prime_en_us/tests/test_scene_anchor_density_gate.py`, run on current `main`:
```
PASS  test_live_default_cap_is_at_least_three
PASS  test_aggregator_reports_live_cap
PASS  test_max_pc_three_flips_fail_to_pass            # max pc==3: FAIL@2 -> PASS@3
PASS  test_genuine_repetition_stays_blocked_at_cap_three  # max pc>=4: still FAIL@3
4/4 passed
```
So cap=3 recovers the natural-motif yield **without lowering genuine quality** — the 4+ repetition
overuse case stays blocked.

## 4. Merged work that already fixed this (do NOT redo)

- **PR #1089** (MERGED 2026-05-12) — the catalog audit that produced the 168/200 number.
- **PR #1091** (MERGED 2026-05-12) — *"scene_anchor_density yield recovery (13% -> 94%)"*: raised
  default cap 2→3, centralized in the config. **This is the fix.**
- **PR #1234** (MERGED 2026-05-19) — OPD-108: scene_anchor_cap 2→3 in the anxiety authored plans
  (`config/plans/anxiety_*` now carry `scene_anchor_cap: 3`, consistent with the default).
- **PR #1180/#1183/#1185** (MERGED) — per-book phrase/wrapper diversification that cleared
  individual chapter-12 hard-fails for the ahjan×gen_z×anxiety production ladder.

## 5. What this PR changes (the remaining real gap)

The gate is fixed; the **reporting was lying**. Two fixes + a guard:

1. `scripts/pearl_prime_en_us/aggregate_bestseller_audit.py`
   - New `live_scene_anchor_cap()` sources the cap from config (single source of truth).
   - Replaced the hardcoded *"~87% never reach scoring"* TL;DR and the
     *"caps repeated >3-word phrases at 2 per book"* remediation line with text that (a) derives
     the yield-loss % from this run's actual inputs, (b) states the **live** cap, (c) explicitly
     tells the reader that any non-trivial `scene_anchor_density` count on **pre-#1091 render
     inputs is stale — re-render at the live cap before treating it as current**, and not to
     re-loosen the gate.
2. `scripts/pearl_prime_en_us/tests/test_scene_anchor_density_gate.py` — locks: default cap ≥ 3;
   aggregator sources cap live; max-pc-3 flips FAIL@2→PASS@3; max-pc≥4 stays FAIL@3.
3. This diagnosis doc.

**Not changed:** the cap value (already 3), the gate algorithm, the authored plans (already 3).
Re-running the gate on current `main` is the fix — there is no code defect left in the gate path.

## 6. Residual / what is gated (honest)

- **Cannot re-verify the catalog ship-rate at scale this session.** The aggregator reads
  `artifacts/pearl_prime_en_us/first_100_qa/renders/**`, which is **git-ignored / absent** in the
  repo (only `assembly_summary.json` + `filter_report.json` are tracked). Running
  `aggregate_bestseller_audit.py` on `main` prints `No renders at …` and exits without writing.
  Regenerating the audit requires **rendering the 200-book catalog at cap=3**, which is a full
  Tier-1 LLM prose run (operator-present, hours) — out of scope for an unattended lane and not
  runnable from artifacts alone.
- **Therefore the headline before/after ship-rate is bounded, not full-catalog:**
  - BEFORE (committed audit, cap=2): **26/200 = 13.0%** rendered; scene_anchor_density blocked
    **168/200 = 84.0%**.
  - AFTER (this session's evidence): on the **16 reports available**, **5/5** scene_anchor cap=2
    failures recover at cap=3 and **0** genuine-repetition failures remain; the 9 most-recent
    (cap=3) reference renders all PASS. Extrapolating PR #1091's full-168 sweep, ~156/168 (≈93%)
    of the original blockers clear at cap=3. **A fresh 200-book cap=3 render is required to state
    the exact catalog ship-rate** — this doc does not invent that number.

## 7. Operator ask (surfaced, not actioned here)

To close B.1 P0 row 1 with a real catalog number: schedule one **cap=3 200-book re-render** of the
en_US first_100_qa catalog (Tier-1, operator-present), then run
`python3 scripts/pearl_prime_en_us/aggregate_bestseller_audit.py`. The aggregator (post this PR)
will self-report the live cap and the true yield. Roadmap B.1 P0 row 1 can then be marked
resolved-by-#1091 with the refreshed figure rather than the stale 13%/87%.
