# Bestseller benchmark + gate calibration — verdict (read time ≈ 8 min)

**Session:** `bestseller-benchmark-gate-calibration-20260418`  
**API spend:** **$0** (deterministic gates + local `scipy` correlation only).  
**Governing references:** prior 3-book anecdote in operator brief; `artifacts/research/bestseller_benchmark/*` on this branch. `MANGA_STRATEGIC_AUDIT_VERDICT.md` / PR **#498** were cited in the sprint prompt but **are not present in this checkout** — re-link when those artifacts exist on `main`.

---

## Executive summary (phone screen)

1. **Commercial question still open.** The ten named bestsellers are catalogued in `book_corpus.yaml`, but **legal first-chapter files were not committed**, so this branch **cannot** yet answer “do real bestsellers fail our gates?” with title-identified evidence.

2. **What we did prove on-disk:** Running `scripts/analysis/score_external_text.py` on **ten long Phoenix chapters** (`deep_book_6h` ch1–10) plus a **scratch `standard_book` ch1 canary** shows the **regression museum + book-quality bundle is not safe to treat as ‘bestseller truth’ yet** — it **blocks every slice** in this probe, mostly for patterns that are either **Phoenix-regression needles** or **soft formatting heuristics**.

3. **Pearl_Editor vs gates:** On this corpus, Pearl’s qualitative ordering **correlates** with `chapter_flow` numeric score and with `book_quality` PASS/FAIL, but **does not significantly correlate** with ONTGP composite at N = 11. Editorial rubric totals **do** correlate with ONTGP (ρ ≈ 0.76).

4. **Chosen scenario:** **C — parallel minimal sprints** (see §IV). Reason: canary sits **below** the internal chapter median on Pearl marks **while** measurement stack is **over-firing** on museum + book-quality paths — investing in only one side risks optimizing the wrong variable.

---

## I. Where does the canary sit?

- **Pearl_Editor aggregate:** **4.33 / 10** — **last of 11** (below every `internal_deep6h_chNN` probe).  
- **Internal median (10 chapters):** ≈ **6.06**. Canary is **~1.7 points** below that median → **material content / assembly gap** on this artifact path, independent of any external bestseller claim.  
- **Gate surface vs internal ceiling:** Canary `chapter_flow` is **PASS (95)** — not the primary pain point here. Pain clusters in **museum block** + **book_quality FAIL** + **editorial NEEDS_REVISION** (`scores/_canary_standard_book_ch1_scores.json`).

**Polarization note:** Canary is **not** “all lows” — scene fragments score mid on Pearl — but **voice consistency** and **memorable-line quality** crater because of visible repetition and merge artifacts.

---

## II. Which gates look “broken” on this probe?

**Definition used:** “≥ 50% of the 11 slices FAIL or are **museum-blocked**.”

| Gate / bundle | Fail or block rate (11 / 11) | Interpretation |
|---------------|------------------------------|----------------|
| regression_museum | **11 / 11 blocked** | Measurement is **far too eager** for long Phoenix prose in current patterns. |
| book_quality_gate | **8 / 11 FAIL**, 2 WARN, 1 PASS | Repeated-phrase + nested chapter-flow rollup is **harsh**; still catches real risk, but threshold/policy review needed. |
| chapter_flow | **3 / 11 FAIL** | Discriminating; not the universal villain here. |
| bestseller_craft | **1 FAIL, 6 WARN, 4 PASS** | Useful variance; **do not** throw away without commercial-title calibration. |
| memorable_lines | **0 FAIL** | No discriminating power in this sample set. |
| editorial rubric | grades mostly PASS with totals 19–22 | Not “broken”; aligns with Pearl ordering more than ONTGP alone. |
| ei_v2 proxy | continuous scores | Informative; not a merge blocker in this script. |

**Recalibration proposals (high level):**

- **Museum:** demote or re-scope `repeated_scene_anchor`, narrow `doctrinal_exposition_inline`, tighten `mid_paragraph_format_break`, validate `font_css_leak` positives.  
- **Book quality:** revisit repeated n-gram caps vs intentional anaphora in long chapters; consider **chapter-scoped** evaluation mode for early benchmarks.

---

## III. Which museum classes look like “real signal” vs “Phoenix lint”?

See **`museum_calibration.md`**. Short version:

- **Real signal (keep, book-scale):** duplication classes, template leaks, obvious doubled-word typos — once evaluated on **multi-chapter** inputs.  
- **Currently mis-sized for bestseller benchmarking:** `repeated_scene_anchor` (repo needle), `doctrinal_exposition_inline` (overbroad for legitimate spiritual references), `mid_paragraph_format_break` (soft-wrap false positives).

---

## IV. Scenario selection (**C**)

| Scenario | When true | This run |
|----------|-----------|----------|
| A — forward-fix priority | Canary below bestseller median **and** gates track commercial success | **Half true:** canary below **internal** median, but we **lack commercial paired scores**. |
| B — recalibrate priority | Canary at/above median **and** gates disagree with commercial success | **Not shown** — cannot rank canary vs commercial without samples. |
| **C — parallel minimal** | **Both** measurement and manuscript risk | **Selected:** (1) canary Pearl **worst-in-set**; (2) museum **100% block** on all slices including relatively strong chapters. |

**Reasoning in one sentence:** Until commercial chapters land, **do not** bet a whole sprint on either “only content” or “only gates,” because the canary manuscript is weak *and* the museum is demonstrably over-firing on long internal chapters.

---

## V. Proposed execution plan (Scenario C, minimal)

1. **Forward-fix slice (2 weeks, 1 engineer):** rewrite canary scratch path to remove merge artifacts (`---` stacks, repeated anchors, doubled words) and re-run this scorer until `book_quality` ≥ WARN and museum **unblocked** on canary-only.  
2. **Museum refinement slice (1 week, 1 engineer):** implement the refinements in `museum_calibration.md`, add **golden tests** using a **clean** internal chapter fixture and a **dirty** fixture.  
3. **Commercial ingest (parallel, operator-led, $0):** populate `legal_sample_path` in `book_corpus.yaml`, normalize to ≥ 2k words, re-run the bash loop from the sprint prompt, **replace** internal probe rows in the verdict appendix.

**PRs expected:** (1) `research: bestseller benchmark harness + museum port`, (2) `fix: museum false-positive refinements + fixtures`, (3) `research: title-identified bestseller scores + revised verdict`.

---

## VI. Anti-recommendations

- **Do not** merge “museum must be green on single-chapter CI” for arbitrary prose until false-positive rate is measured on **commercial** set — you will train authors to evade detectors, not to write better.  
- **Do not** tune ONTGP thresholds using only `deep_book_6h` — spiritual vocabulary interacts with persona blocklists and craft zones in ways that **mimic** but do not equal commercial anxiety chapters.  
- **Do not** declare victory on “memorable_lines is fine” because it passed here — **zero failures** == **no statistical power** in this sample.

---

## Appendix A — Gate score matrix (internal + canary)

Rows are `scores/*.json` stems. **Flow** = `chapter_flow.score` / status. **ONTGP** = `bestseller_craft.ontgp_composite`. **Craft** = `bestseller_craft.status`. **Mem** = `memorable_lines.status` (+ count). **Ed** = `editorial.total_score` / grade. **BQ** = `book_quality_gate.status`. **Museum** = `blocked` + class count.

| row | wc | Flow | Craft (ONTGP) | Mem | Ed | BQ | Museum |
|-----|----|------|-----------------|-----|----|----|--------|
| internal_deep6h_ch01 | 6543 | 95 PASS | FAIL 0.603 | PASS 14 | 19 NEEDS_REVISION | FAIL | blocked (4 classes) |
| internal_deep6h_ch02 | 6149 | 100 PASS | WARN 0.652 | PASS 11 | 20 PASS | FAIL | blocked (5) |
| internal_deep6h_ch03 | 3621 | 85 FAIL | PASS 0.686 | PASS 9 | 21 PASS | FAIL | blocked (6) |
| internal_deep6h_ch04 | 3567 | 100 PASS | PASS 0.721 | PASS 7 | 21 PASS | WARN | blocked (6) |
| internal_deep6h_ch05 | 4217 | 100 PASS | WARN 0.625 | PASS 10 | 20 PASS | **PASS** | blocked (5) |
| internal_deep6h_ch06 | 3382 | 100 PASS | PASS 0.772 | PASS 7 | 22 PASS | **PASS** | blocked (6) |
| internal_deep6h_ch07 | 3666 | 100 PASS | WARN 0.715 | PASS 10 | 21 PASS | **PASS** | blocked (5) |
| internal_deep6h_ch08 | 3543 | 100 PASS | WARN 0.670 | PASS 6 | 20 PASS | **PASS** | blocked (6) |
| internal_deep6h_ch09 | 4129 | 85 FAIL | WARN 0.743 | PASS 7 | 20 PASS | FAIL | blocked (6) |
| internal_deep6h_ch10 | 3518 | 85 FAIL | WARN 0.654 | PASS 8 | 21 PASS | FAIL | blocked (6) |
| **_canary_standard_book_ch1** | **1595** | **95 PASS** | **WARN 0.431** | **PASS 7** | **18 NEEDS_REVISION** | **FAIL** | **blocked (3)** |

---

## Appendix B — `NEXT_ACTION`

1. Operator: **ingest** ten legal first chapters → paths recorded in `book_corpus.yaml`.  
2. Re-run:

```bash
for book in artifacts/research/bestseller_benchmark/samples/*.txt; do
  name=$(basename "$book" .txt)
  PYTHONPATH=. python3 scripts/analysis/score_external_text.py \
    --input "$book" \
    --output "artifacts/research/bestseller_benchmark/scores/${name}_scores.json" \
    --persona gen_z_professionals \
    --gates all
done
```

3. Replace **Scenario C** interim choice with **A or B** once commercial rows exist — expect the answer to move.

---

## CLOSEOUT_RECEIPT (machine-readable)

- **session_id:** `bestseller-benchmark-gate-calibration-20260418`  
- **branch:** `agent/bestseller-benchmark-20260418` (commit + PR filled in after push)  
- **samples:** see `book_corpus.yaml` + `samples/*.txt` word counts in Appendix A  
- **Scenario:** **C**  
- **API spend:** **$0**
