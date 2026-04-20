# Duration audit for catalog formats
_Exported on 4/16/2026 at 19:33:06 GMT+8 from Cursor (3.1.15)_

---

**User**

Act as Pearl_PM + Pearl_Dev + Pearl_Architect for Phoenix Omega.

Read these files before doing any work:

- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- config/duration/duration_registry.yaml (FULL — format durations by intent)
- config/duration/therapeutic_dose_rules.yaml (FULL — minimum effective doses)
- config/duration/persona_duration_profiles.yaml (FULL)
- config/duration/platform_duration_profiles.yaml (FULL)
- config/duration/serialization_cadence.yaml
- config/catalog/catalog_generation_config.yaml
- config/catalog_planning/canonical_topics.yaml
- config/catalog_planning/canonical_personas.yaml
- artifacts/catalog/full_catalog.csv (FULL — 12,483 rows, check estimated_word_count + runtime_format_id columns)
- registry/grief.yaml (first 30 lines + count all sections/variants)
- registry/anxiety.yaml (first 30 lines + count all sections/variants)
- scripts/run_pipeline.py (grep "word_count\|duration\|budget" — how duration is tracked)
- phoenix_v4/rendering/book_renderer.py (grep "word_count\|budget" — what gets measured)
- phoenix_v4/quality/ei_v2/duration_fit.py (FULL — CDIS duration scoring)
- config/quality/ei_v2_config.yaml (duration_fit section)
- specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md (if exists — first 60 lines)
- artifacts/production_run/ (ls — any existing production outputs with budget.json)
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

Emit a STARTUP_RECEIPT then execute.

TASK: Full duration audit — compare what the catalog PLANS (estimated
word count × format targets) against what the registries + pipeline
ACTUALLY PRODUCE. Identify every format where output duration misses
the target. Produce a gap report with specific fixes.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline, ei_v2

───────────────────────────────────────────────────────────────────────

THE QUESTION:

  The catalog says "short_book_30" should be a 30-minute audiobook
  (~4,500-5,500 words at 150 WPM). But when the pipeline renders a
  book from the registry, how many words does it ACTUALLY produce?
  Does it hit 4,500? Or does it produce 2,000 and call it done?

  Same question for every format:
    micro_book_15: target ~2,250 words (15 min at 150 WPM)
    short_book_30: target ~4,500-5,500 words (30 min)
    standard_book: target ~15,000-22,500 words (100-150 min)
    deep_book_4h: target ~36,000 words (4 hours)
    deep_book_6h: target ~54,000 words (6 hours)

───────────────────────────────────────────────────────────────────────

PHASE 1: CATALOG DURATION TARGETS

Analyze the full catalog to understand what durations are planned:

  python3 -c "
  import csv
  from collections import Counter, defaultdict

  with open('artifacts/catalog/full_catalog.csv') as f:
      reader = csv.DictReader(f)
      rows = list(reader)

  # Format distribution
  fmt_counts = Counter(r.get('runtime_format_id','') for r in rows)
  print('FORMAT DISTRIBUTION:')
  for fmt, cnt in fmt_counts.most_common():
      print(f'  {fmt}: {cnt} entries')

  # Estimated word counts per format
  fmt_words = defaultdict(list)
  for r in rows:
      fmt = r.get('runtime_format_id','')
      ewc = r.get('estimated_word_count','')
      if ewc and '-' in ewc:
          lo, hi = ewc.split('-')
          fmt_words[fmt].append((int(lo), int(hi)))
      elif ewc and ewc.isdigit():
          fmt_words[fmt].append((int(ewc), int(ewc)))

  print()
  print('WORD COUNT TARGETS PER FORMAT:')
  for fmt in sorted(fmt_words):
      ranges = fmt_words[fmt]
      lo_avg = sum(r[0] for r in ranges) / len(ranges)
      hi_avg = sum(r[1] for r in ranges) / len(ranges)
      dur_lo = lo_avg / 150  # minutes at 150 WPM
      dur_hi = hi_avg / 150
      print(f'  {fmt}: {lo_avg:.0f}-{hi_avg:.0f} words → {dur_lo:.0f}-{dur_hi:.0f} min audiobook')
  "

  ALSO check: does the catalog have explicit duration_minutes fields?
  Or only estimated_word_count?

───────────────────────────────────────────────────────────────────────

PHASE 2: REGISTRY ACTUAL OUTPUT

For each of the 15 registries, measure what they ACTUALLY produce:

  python3 -c "
  import yaml
  from pathlib import Path

  for reg_path in sorted(Path('registry').glob('*.yaml')):
      data = yaml.safe_load(reg_path.read_text())
      sections = data.get('sections', {})

      total_words = 0
      total_variants = 0
      chapter_words = []

      for ch_key, ch_data in sections.items():
          ch_words = 0
          for sec_key, sec_data in ch_data.get('sections', {}).items():
              variants = sec_data.get('variants', [])
              total_variants += len(variants)
              if variants:
                  # Use F1 (first variant) as the representative
                  content = variants[0].get('content', '')
                  words = len(content.split())
                  ch_words += words
          chapter_words.append(ch_words)
          total_words += ch_words

      duration_min = total_words / 150
      print(f'{reg_path.stem}: {total_words} words, {len(sections)} chapters, '
            f'{total_variants} variants, ~{duration_min:.0f} min at 150 WPM')
      print(f'  Per chapter: {[w for w in chapter_words]}')
  "

  KEY QUESTION: If a registry has 12 chapters × ~300 words per chapter
  (F1 variant only) = ~3,600 words = ~24 min. That's SHORT of a
  "short_book_30" target (4,500-5,500 words).

  But the pipeline also overlays teacher atoms and persona atoms.
  How much do those add?

───────────────────────────────────────────────────────────────────────

PHASE 3: PIPELINE RENDER ACTUAL OUTPUT

Run the pipeline for a SAMPLE of format × topic combinations and
measure actual rendered word counts:

  For 3 topics (grief, anxiety, burnout) × 1 persona (gen_z_professionals):

  python3 scripts/run_pipeline.py \
    --topic grief --persona gen_z_professionals \
    --arc $(ls config/source_of_truth/master_arcs/gen_z_professionals__grief__* | head -1) \
    --render-book --quality-profile draft \
    --out /tmp/duration-audit/grief.plan.json \
    2>/dev/null

  # Check rendered word count
  wc -w /tmp/duration-audit/book.txt
  # Check budget.json if produced
  cat /tmp/duration-audit/budget.json

  Repeat for anxiety and burnout.

  ALSO: If there are existing rendered books from prior production runs
  (artifacts/production_run/), read their budget.json or count words
  in their book.txt files.

  COMPARE: rendered word count vs catalog estimated_word_count target.

───────────────────────────────────────────────────────────────────────

PHASE 4: DURATION TARGET COMPLIANCE CHECK

Cross-reference duration_registry.yaml targets with actual output:

  For EACH runtime_format_id in the catalog:

  | Format | Catalog Word Target | Registry F1 Words | Rendered Words | Duration Target (min) | Actual Duration | Gap |
  |--------|--------------------|--------------------|----------------|----------------------|-----------------|-----|
  | micro_book_15 | 2,250 | ? | ? | 15 | ? | ? |
  | short_book_30 | 4,500-5,500 | ? | ? | 30 | ? | ? |
  | standard_book | 15,000-22,500 | ? | ? | 100-150 | ? | ? |

  Also check against duration_registry.yaml optimal values:
    audiobook_micro/discovery: optimal 25 min → 3,750 words
    audiobook_micro/therapeutic: optimal 90 min → 13,500 words
    audiobook_micro/deep_engagement: optimal 480 min → 72,000 words

  FLAG every format where actual output is:
    <80% of minimum target → RED (significantly short)
    80-95% of minimum target → YELLOW (slightly short)
    95-110% of target → GREEN (on target)
    >110% of maximum target → YELLOW (too long)

───────────────────────────────────────────────────────────────────────

PHASE 5: IDENTIFY ROOT CAUSES

For each format that's RED or YELLOW, diagnose WHY:

  POSSIBLE CAUSES:
    a) Registry has too few sections per chapter
       (12 chapters × 3 sections = 36 sections → ~1,800 words at 50 words/section)
    b) Registry variant content is too short
       (each variant is 50-100 words instead of 200-400 words)
    c) Teacher overlay doesn't add enough volume
    d) Pipeline doesn't pad to target word count
    e) Format-specific rendering rules truncate output
    f) estimated_word_count in catalog doesn't match format spec

  For each cause found:
    What would fix it?
    How much effort?
    Which component needs to change (registry content, pipeline code, config)?

───────────────────────────────────────────────────────────────────────

PHASE 6: PRODUCE THE DURATION AUDIT REPORT

  artifacts/audit/CATALOG_DURATION_AUDIT.md

  ## Executive Summary
  - Total catalog entries: 12,483
  - Format distribution: short_book_30 (X%), micro_book_15 (Y%), standard_book (Z%)
  - Duration compliance rate: X% GREEN, Y% YELLOW, Z% RED
  - Biggest gap: {format} is {X}% short of target

  ## Duration Targets (from configs)
  | Format | Word Target | Duration Target (min) | Source Config |
  ...

  ## Registry Content Measurement (15 topics)
  | Topic | F1 Word Count | Chapters | Sections | Words/Section | Duration (min) |
  | grief | X | 12 | Y | Z | N |
  | anxiety | X | 12 | Y | Z | N |
  ...

  ## Pipeline Render Measurement (3 sample books)
  | Book | Format | Target Words | Rendered Words | Target Min | Actual Min | Gap |
  ...

  ## Compliance Matrix
  Per format × topic (where data available):
  GREEN / YELLOW / RED status

  ## Root Cause Analysis
  For each RED/YELLOW format:
  - What's short
  - Why
  - Fix needed
  - Effort estimate

  ## Recommendations
  P0: [formats that are critically short — can't ship]
  P1: [formats that are slightly short — ship with caveat]
  P2: [formats that are fine but could be better]

  ## Fix Options
  For each short format:
    Option A: Add more content to registries (more sections, longer variants)
    Option B: Pipeline word count padding (expand sections at render time)
    Option C: Adjust catalog targets (if current output is therapeutically appropriate)
    Option D: Multi-registry assembly (combine multiple chapters for longer formats)

───────────────────────────────────────────────────────────────────────

GIT WORKFLOW:
git fetch origin && git checkout -b agent/duration-audit origin/main
Commits:
  a) "docs: catalog duration audit — targets vs actual output"
Run preflight, push, PR against main.

WRITE_SCOPE:
  artifacts/audit/CATALOG_DURATION_AUDIT.md (NEW)
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (add workstream)

OUT_OF_SCOPE: Fixing duration gaps (audit only — fixes in follow-up);
registry content edits; pipeline code changes; config changes

NON-NEGOTIABLE:
  MEASURE ACTUAL OUTPUT — don't trust estimated_word_count alone.
  Count words in rendered book.txt, not just registry YAML.
  Every number in the report must cite its source (config file, rendered output, catalog row).
  If pipeline can't render a format (missing arc, missing registry), document why.
  duration_registry.yaml is the TARGET authority — compare against it.
  150 WPM is the standard audiobook narration rate — use this for word→minute conversion.
  RED = can't ship at this duration. GREEN = good to ship. Be honest.
  Check `gh pr diff <number> --stat | tail -1` before merging.
  If deletions > 50 files, STOP and ask the owner.


---

**Cursor**

Executing the duration audit: reading required files, gathering measurements, and producing the audit report. Starting with parallel reads and repository setup.



Gathering catalog columns, runtime-format word ranges, and running measurement scripts.



Running pipeline renders and counting grief/anxiety registry sections/variants. Checking `run_pipeline.py` CLI for render output paths.



Emitting STARTUP_RECEIPT, writing the audit document, cleaning temporary artifacts, and running git workflow with preflight.



## STARTUP_RECEIPT

```
STARTUP_RECEIPT
AGENT:              Pearl_PM + Pearl_Dev + Pearl_Architect
TASK:               Full duration audit — catalog plans vs registry + pipeline output
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline, ei_v2
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md (§1–3); config/duration/*; config/catalog/catalog_generation_config.yaml; config/catalog_planning/canonical_*.yaml; config/format_selection/format_registry.yaml; config/quality/ei_v2_config.yaml; specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md (via SUBSYSTEM map)
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/audit/CATALOG_DURATION_AUDIT.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       Fixing gaps; registry/pipeline/config code changes
BLOCKERS:           none
READY_STATUS:       ready
```

---

## Execution summary

Deliverables are on branch **`agent/duration-audit`**, commit **`b7eb8f39c81a6dd26da058603abfb7fa321599b9`**, PR **[#365](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/365)**.

**Governance:** `git diff origin/main...HEAD --stat | tail -1` → `2 files changed, 257 insertions(+)` (no mass delete).

### Headline answers

| Question | Answer |
|----------|--------|
| **Catalog rows** | **8,287** rows (not 12,483 in this tree). **No** `duration_minutes` column — only `estimated_word_count`, `runtime_format_id`, etc. |
| **Planned vs `format_registry`** | Planning matches `config/format_selection/format_registry.yaml` for `micro_book_15` (2,500–3,000), `short_book_30` (4,500–5,500), `standard_book` (9,000–11,000). |
| **Registry F1 only (12×90 sections)** | Most topics **~3.8k–4.9k words** (~25–33 min @ 150 WPM) → **below `short_book_30` minimum (4,500)** for **13/15** topics; **`sleep_anxiety`** is **in band**; **`grief`** **~7,979 words** (over `short_book_30` max on F1 alone). **All 15 are under `standard_book` min (9,000).** |
| **Sample renders** (F006 arcs, `--no-job-check`, draft gates) | **Anxiety ~5,033 words** (`wc -w`) → **inside** 4,500–5,500. **Burnout ~4,817** → **inside**. **Grief ~7,235** → **above 5,500** (too long vs `short_book_30`). `budget.json` word counts are in the report. |
| **`runtime_format_id` in plans** | **`null` in registry render mode** → `word_count_gate` **skips** when there is no `word_range` (see `phoenix_v4/rendering/book_renderer.py`). |
| **CDIS authority** | `duration_registry.yaml` is **modality + intent** (`audiobook_micro`, …), **not** the same IDs as catalog `runtime_format_id`; `duration_fit.py` does **not** consume catalog formats. |

Full tables, sources, root causes, and P0/P1/P2 recommendations are in **`artifacts/audit/CATALOG_DURATION_AUDIT.md`**. Workstream **`ws_catalog_duration_audit_20260410`** is logged in **`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`**.

**Note:** Renders used **`--no-job-check`** because `--out` under `/tmp` triggered missing `job.json`; evidence paths were removed after measurement to stay inside WRITE_SCOPE. Re-run commands are documented in the audit.

---

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM + Pearl_Dev + Pearl_Architect
TASK:           Catalog duration audit (plans vs registry vs render)
COMMIT_SHA:     b7eb8f39c81a6dd26da058603abfb7fa321599b9
FILES_WRITTEN:  artifacts/audit/CATALOG_DURATION_AUDIT.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     (see FILES_READ list in audit doc § CLOSEOUT)
STATUS:         completed
HANDOFF_TO:     Pearl_PM / owner
NEXT_ACTION:    Review PR #365; before merge use repo’s PR diff stats (this PR: +257/−0 on two files). Merge only when governance checks are green.
```

---

**User**

Do this next:

1. Merge PR [#365](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/365) if its checks are green.
That lands the audit and gives you a canonical evidence file on `main`.

2. Open a follow-up implementation PR for the real bug:
- make registry-mode renders carry `runtime_format_id`
- so the word-count gate stops silently skipping in registry mode

3. After that, decide whether the content or the planning target is wrong:
- if F1 is supposed to satisfy `short_book_30`, expand registry content
- if F1 is intentionally a lighter scaffold, then change the planning/gating expectations

If you want the shortest answer: merge `#365`, then fix `runtime_format_id` propagation first. That is the highest-signal concrete bug from the audit.

---

**Cursor**

Checking PR #365 status, merging if checks pass, then implementing `runtime_format_id` propagation for registry-mode renders.



PR #365 shows failing Core tests. Investigating whether failures are PR-related and tracing registry-mode plan assembly to implement the fix.



Merging PR #365 only if checks pass (they're failing). Fixing `runtime_format_id` resolution (`format_runtime_id` alias) and propagating it through the registry path.



Implementing the helper and registry propagation.



## 1. PR #365 merge

**Not merged.** GitHub reports **`mergeStateStatus: BLOCKED`** (branch protection). Checks: **Core tests — failure**; **Workers Builds: pearl-prime — failure**; others passed. `gh pr merge 365` is rejected until requirements are satisfied.

**What to do next:** On the PR, **re-run failed jobs** (or rebase onto green `main` if fixes landed there). When **Core tests** and required rules are green, merge normally. The audit file will then be on `main`.

---

## 2. Follow-up implementation PR

**Opened:** [PR #367](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/367) — branch `agent/registry-runtime-format-id`, commit **`c5544196a1`**.

**What it does**

- Adds **`_resolved_runtime_format_id()`** so the effective runtime is **`args.runtime_format` → `format_plan_dict["runtime_format_id"]` → `format_plan_dict["format_runtime_id"]`** (Stage 2 only had the last key, so compiled plans often had an empty `runtime_format_id`).
- **Registry path:** plan JSON, **`budget.json`**, **`output_contract.json`**, optional freebie stub, **`quality_summary.json`** now include **`runtime_format_id`** and **`format_id`**.
- After **`book.txt`** is written, runs **`word_count_gate()`** when `_reg_runtime` is set, unless **`--skip-word-count-gate`** (same idea as atom **`render_book`**).
- **Atom path:** `out["runtime_format_id"]`, intro-contract resolution, and **pre-render budget check** use the same resolver.

**Tests:** `tests/test_registry_plan_runtime_format.py` (helpers + subprocess plan smoke).

**Governance:** `git diff origin/main...HEAD --stat | tail -1` → `2 files changed, 123 insertions(+), 10 deletions(+)`.

---

## 3. Content vs planning (short answer)

**Do not decide that in code yet.** With the gate actually enforced for registry renders, you’ll get **hard failures** wherever prose is under the **`format_registry.yaml`** minimum for the selected runtime (e.g. **`short_book_30`** 4,500 words).

**Decision rule**

- If the **12-chapter registry book is meant to ship as `short_book_30` / `standard_book` as labeled in the catalog →** treat **`estimated_word_count` as the promise** and **expand registry (and/or overlays)** until renders sit in band.
- If registry prose is an intentional **lighter scaffold** (draft / lead magnet / funnel step) → **change planning**: SKUs, `estimated_word_count`, and/or a dedicated **`runtime_format_id`** (e.g. micro) so gates and marketing match reality.

**Recommendation:** land **#367** first so the failure mode is **explicit**; then choose one of the two paths above with product/legal input, not by guessing from F1 counts alone.

