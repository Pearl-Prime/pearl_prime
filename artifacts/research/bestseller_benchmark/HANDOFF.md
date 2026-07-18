# Handoff: Bestseller benchmark + gate calibration sprint (Pearl_PM)

**If you only see `HANDOFF.md` in this folder:** the full benchmark tree (samples, scores, verdict, `book_corpus.yaml`, etc.) lives on branch **`agent/bestseller-benchmark-20260418`** until [PR #500](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/500) is merged. Fetch that branch or merge the PR, then re-open this file next to the other artifacts.

This document captures **everything** delivered for the “are we making bestsellers?” benchmark sprint: scope, constraints, what exists on disk, what is still blocked, git/PR pointers, commands, and **who does what next**.

---

## 1. Purpose (why this exists)

Settle **gates vs content vs both** with more than the prior **3-book anecdote** (Bourne / Wilson / Breslin). Target state:

- **N = 10** commercially successful titles (anxiety / overwhelm / burnout persona).
- Full deterministic **Phoenix gate stack** + **regression museum** + qualitative **Pearl_Editor** rubric.
- **$0 API spend**; legal text only (library, Kindle sample, publisher excerpt, Google Books preview — never piracy).

**Interim reality:** First-chapter files for the ten **copyrighted** titles were **not** available to commit in-repo during the implementation session. The sprint still produced a **reproducible harness**, **commercial corpus metadata**, **internal long-form calibration** (Phoenix `deep_book_6h` chapters 1–10), a **canary slice**, JSON scores, correlation notes, museum calibration, and a **single scenario verdict (C)** pending commercial ingest.

---

## 2. Git / PR (source of truth for merged files)

| Item | Value |
|------|--------|
| **Branch** | `agent/bestseller-benchmark-20260418` |
| **Base** | `origin/main` at time of branch creation |
| **Commit (tip of that work)** | `da3957cdb57f4de9947d10813cd8a7d4b5d4d1aa` |
| **Pull request** | https://github.com/Ahjan108/phoenix_omega_v4.8/pull/500 |
| **Commit message (summary)** | `research: bestseller benchmark harness + interim gate verdict` |

### If this folder is empty on your machine

The benchmark tree may only exist on the feature branch until PR **#500** is merged.

```bash
git fetch origin
git checkout agent/bestseller-benchmark-20260418
# or: git cherry-pick da3957cdb57f4de9947d10813cd8a7d4b5d4d1aa
```

**Local stash note (from the session that opened the branch):** If you had unrelated local edits on `main`, they may have been stashed as `agent temp stash bestseller branch`. Check `git stash list` before popping.

---

## 3. Directory layout (after branch / merge)

All under **`artifacts/research/bestseller_benchmark/`**:

| Path | Purpose |
|------|---------|
| `HANDOFF.md` | This file (operator + engineer continuity). |
| `book_corpus.yaml` | Ten **commercial targets** (metadata, ISBN, region, format, **ingest URL hints**, `legal_sample_path: null` until files exist). |
| `BESTSELLER_BENCHMARK_VERDICT.md` | Executive summary, **Scenario C**, matrix appendix, anti-recommendations, `NEXT_ACTION`. |
| `pearl_editor_markup.md` | 9-dimension Pearl_Editor scores for **11** on-disk samples + ranked list + canary position. |
| `gate_correlation_analysis.md` | Spearman notes (N=11), which correlations are valid **without** commercial text pairing. |
| `museum_calibration.md` | Which museum classes fired on internal probe; false-positive / refinement guidance. |
| `samples/` | `internal_deep6h_ch01.txt` … `ch10.txt` (+ canary `_canary_standard_book_ch1.txt`). **Not** the copyrighted chapters of the ten commercial titles. |
| `scores/` | One `*_scores.json` per sample from `scripts/analysis/score_external_text.py`. |

**Script (repo root relative):**

| Path | Purpose |
|------|---------|
| `scripts/analysis/score_external_text.py` | CLI: wrap chapter text → run gates → write JSON. |

**Regression museum (already on `main` in that repo lineage):**

| Path | Purpose |
|------|---------|
| `phoenix_v4/quality/regression_museum/` | Deterministic detectors + `run_museum_gates(book_dict, persona=...)`. |
| `config/governance/regression_museum.yaml` | Failure-class config. |
| `tests/test_regression_museum_backfill.py` | Fixture-based ratchet tests. |
| `tests/fixtures/regression_museum/known_bad_book.txt` | Known-bad corpus for CI. |

---

## 4. Operator prerequisites (from sprint spec)

Before treating results as **title-identified** “bestseller” evidence:

- [ ] **Canary / render path:** `book.txt` (or equivalent) exists where you expect QA renders (sprint mentioned `artifacts/qa_reader_run_<latest>/book.txt`; this run used **scratch** paths under `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/`).
- [ ] **Three-blocker triage green** (disk, Pearl Star, 403) — not re-verified in the handoff session; run your standard triage before large renders.
- [ ] **Ten legal first-chapter files** (≥ **2,000 words** each where possible; canary in this run was **1,595 words** and is explicitly flagged).
- [ ] **No API budget** for this research track (deterministic gates only in `score_external_text.py`).

---

## 5. How to run the scorer (copy-paste)

From repo root, `PYTHONPATH=.`:

```bash
mkdir -p artifacts/research/bestseller_benchmark/scores

PYTHONPATH=. python3 scripts/analysis/score_external_text.py \
  --input artifacts/research/bestseller_benchmark/samples/internal_deep6h_ch01.txt \
  --output artifacts/research/bestseller_benchmark/scores/internal_deep6h_ch01_scores.json \
  --persona gen_z_professionals \
  --gates all
```

Batch loop (all `.txt` in `samples/`):

```bash
for book in artifacts/research/bestseller_benchmark/samples/*.txt; do
  name=$(basename "$book" .txt)
  PYTHONPATH=. python3 scripts/analysis/score_external_text.py \
    --input "$book" \
    --output "artifacts/research/bestseller_benchmark/scores/${name}_scores.json" \
    --persona gen_z_professionals \
    --gates all \
    --label "$name"
done
```

**Gates included in `--gates all`:**  
`chapter_flow`, `bestseller_craft`, `ei_v2` (heuristic safety + TTS readability only — no LLM), `editorial`, `memorable_lines`, `transformation_arc` (single-chapter caveat in JSON), `book_quality_gate`, `regression_museum`.

**Museum input shape:** one chapter in `book["chapters"]` with `index` and `text`; cross-chapter detectors will not fire meaningful signals on single-chapter files (documented in analysis).

---

## 6. Commercial corpus (naming / geography / format)

Targets are listed in **`book_corpus.yaml`** under `commercial_targets` (10 rows), aligned to the sprint brief:

- US-heavy mix, UK, IE, AU, JP; workbook / illustrated / audio-first notes where applicable.
- Each row has **`text_sample_url`** / **`text_sample_source`** placeholders for **legal** acquisition.
- **`legal_sample_path`** must be filled when the operator drops normalized UTF-8 LF chapter files, e.g. `samples/clear_james_atomic-habits_ch1.txt` (example naming from sprint; match whatever convention you adopt).

**Critical honesty rule:** Do **not** rename internal `internal_deep6h_*.txt` files to commercial titles — that implies false literary provenance. Keep **internal calibration** and **commercial samples** in separate rows in YAML.

---

## 7. Results summary (interim run, internal + canary)

**Pearl_Editor (9-dimension aggregate, 1–10):** See `pearl_editor_markup.md`. Canary **`_canary_standard_book_ch1`** scored **lowest (11th of 11)** vs `internal_deep6h_ch01`–`ch10`.

**Museum:** **Blocked on 11 / 11** slices in the interim run — classes with highest prevalence included `repeated_scene_anchor`, `mid_paragraph_format_break`, `doctrinal_exposition_inline`, `doubled_word`, `off_persona_vocabulary`, `font_css_leak`. Details and refinement ideas: **`museum_calibration.md`**.

**Correlations (N = 11):** See **`gate_correlation_analysis.md`**. Spearman vs **Amazon rank** was **not** computed (text was not paired to commercial titles). Strongest internal signal: **editorial total vs ONTGP composite** (ρ ≈ 0.76, p ≈ 0.006).

**Verdict scenario:** **`C`** — parallel minimal **forward-fix** (canary / assembly quality) **and** **museum + book-quality recalibration** work, until legal commercial chapters allow choosing **A** or **B** on evidence. Full reasoning: **`BESTSELLER_BENCHMARK_VERDICT.md`**.

---

## 8. Anti-recommendations (do not waste effort)

From the verdict / analysis (condensed):

- Do **not** treat “museum green on single-chapter CI” as a ship gate for arbitrary prose until false-positive rate is measured on **commercial** chapters.
- Do **not** tune **ONTGP** thresholds using only `deep_book_6h` spiritual-adjacent prose — not representative of the full commercial list.
- Do **not** conclude **memorable_lines** is “fine forever” because it passed on this slice — **zero FAILs** means **no discriminating power** in this sample.

---

## 9. Governance / PR hygiene (from repo norms)

Before pushing further research commits:

```bash
git branch --show-current
git status --short
git fetch origin
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
```

Mass-delete merge policy and governance CI still apply to this repo — keep research PRs **scoped** to `artifacts/research/bestseller_benchmark/` + `scripts/analysis/score_external_text.py` unless you intentionally broaden.

---

## 10. CLOSEOUT_RECEIPT (paste into tickets)

```text
session_id: bestseller-benchmark-gate-calibration-20260418
branch: agent/bestseller-benchmark-20260418
commit: da3957cdb57f4de9947d10813cd8a7d4b5d4d1aa
pr: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/500
scenario: C (interim; commercial chapters not yet ingested)
api_spend_usd: 0
deliverables:
  - scripts/analysis/score_external_text.py
  - artifacts/research/bestseller_benchmark/book_corpus.yaml
  - artifacts/research/bestseller_benchmark/samples/*.txt (internal + canary)
  - artifacts/research/bestseller_benchmark/scores/*.json
  - artifacts/research/bestseller_benchmark/pearl_editor_markup.md
  - artifacts/research/bestseller_benchmark/gate_correlation_analysis.md
  - artifacts/research/bestseller_benchmark/museum_calibration.md
  - artifacts/research/bestseller_benchmark/BESTSELLER_BENCHMARK_VERDICT.md
  - artifacts/research/bestseller_benchmark/HANDOFF.md
blockers:
  - Legal first-chapter text for ten commercial titles not committed
next_action:
  - Operator ingests 10 chapter files → updates book_corpus.yaml legal_sample_path
  - Re-run score loop → update verdict scenario A vs B
  - Optional: museum regex / severity PR per museum_calibration.md
```

---

## 11. Contact surface (roles)

| Role | Responsibility |
|------|----------------|
| **Pearl_PM** | Keep sprint scope; merge order; unblock ingest. |
| **Pearl_Research** | Verify ranks (BookScan / Oricon / retailer) when needed; **Rakuten AI** only if operator policy allows (sprint mentioned it; this harness stayed $0). |
| **Pearl_Editor** | Re-score commercial chapters when files land; keep quotes **specific** (see markup doc style). |
| **Pearl_Architect** | Spearman / gates thresholds; museum refinement math; CI wiring after pattern changes. |

---

*Generated for continuity across sessions and machines. If PR #500 merged, this file should live on `main` under `artifacts/research/bestseller_benchmark/HANDOFF.md`; if not merged, fetch the branch above.*
