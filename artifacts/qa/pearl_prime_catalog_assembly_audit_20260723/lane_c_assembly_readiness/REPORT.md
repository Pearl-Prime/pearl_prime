# Lane C — Catalog-Scale Assembly-Readiness Prediction

**Agent:** Pearl_Prime | **Date:** 2026-07-23 | **Anchor:** `origin/main` = `848c726c66` (re-fetched; authoring
anchor `244955eaa0…` and Lane A's anchor `633273c97f…` are both behind this — this lane's checked-out worktree
tip is `848c726c66d`, which includes Lane A's merge #221 and the dispatcher's Lane A correction).

**Scope discipline:** read-only static-analysis lane. **Zero** `run_pipeline.py` / `build_epub.py` / renderer
invocations. `config/source_of_truth/**` was read, never edited. The one executable check used —
`phoenix_v4/gates/check_tuple_viability.check_tuple_viability()` — is the exact function Lane A's CLI spot-checks
called; it performs no writes and issues no render (confirmed by reading its full source before use, see
`evidence/build_cell_table.py` / `evidence/batch_tuple_viability.py` docstrings).

**Prerequisite gate:** Lane A **MERGED** as PR #221 (`46d971d642cc4076d065a2466be9e55fb3f940cb`), confirmed directly
in `origin/main`'s commit log before starting. Lane A's `REPORT.md` was read from `origin/main`, not substituted.

---

## 0. Headline finding

**At catalog scale, only 1.4% of planned en_US books (465 of 32,401) predict to a research_fit-BOUND cell.
98.5% (31,912) predict to `UNBOUND-thin` — capped at `structurally clear` (Layer 1) regardless of how clean
their register_gate score is — and 0.07% (24) predict to `UNKNOWN`, meaning no atom bank resolves for their
exact engine at all.** This is not a sample estimate: it is a full, exact enumeration of every one of the
**657 distinct (persona, topic, engine) cells** that appear anywhere across all 32,401 en_US book-plan files
(all 40 brand archetypes), weighted by how many planned books actually use each cell.

**A second, independent full-corpus sweep — batch `check_tuple_viability()` (the actual preflight gate, not a
bank-presence proxy) — found 27.9% of planned books (9,051 of 32,401) would FAIL tuple-viability outright**
(`NO_BINDING` 177 cells / 8,704 books, `BAND_DEFICIT` 112 cells / 5,704 books, `POOL_TOO_SHALLOW` 18 cells /
54 books). Cross-tabbed against the bind-status prediction: **all 465 BOUND-predicted books also pass tuple
viability** (research_fit-bound cells are the best-invested cells on every axis), but of the 31,912
UNBOUND-thin books, **9,027 (28.3%) additionally fail tuple viability** — meaning for those, `structurally
clear` is optimistic; the more honest prediction is the render never produces a coherent `book.txt` at all
(`path broken`, per the scorecard's Layer 1 language).

**corporate_managers — the persona Lane A / the 07-22 audit already flagged as the zero-story_atoms EPUB
workhorse — is not uniquely worst on the bind-status axis (6 other personas tie it at literal 0% BOUND), but
it IS the single worst-exposed persona on the tuple-viability axis**: 32.5% of its 3,743 planned books
(1,218) fail tuple-viability outright, the highest failure rate of any of the 8 non-trivial personas, on the
single largest persona by catalog volume. See §3.

---

## 1. Discovery — mechanism confirmation before predicting

1. **Read Lane A's `REPORT.md` in full** (`artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/REPORT.md`,
   merged PR #221). Key inputs carried forward: 32,401 en_US book-plan files across 40 brand archetypes; 657
   distinct persona×topic×engine cells are what the planner actually resolves (persona/topic/engine are
   always baked into the filename — there is no unresolved-cell tier on disk); 3 brands
   (`qi_foundation`/`body_memory`/`still_forest`) have a **separate, orthogonal** arc-orphan defect (92% of
   each brand's series-plan pointers are broken) that Lane A found — this lane confirms below (§4) that
   arc-orphaning and research_fit bind-status are independent axes, not the same defect.
2. **Confirmed the six read-only tools/signals available for prediction without rendering:**
   - `scripts/inventory/atom_coverage_audit.py` — ran fresh (2026-07-23): reproduces the 07-22 audit's numbers
     exactly (29.8% complete on the full 57-topic list; 100.0% on the core 15/17 topics). This tool checks
     CANONICAL.txt presence at **persona×topic** granularity (any engine subdir, or legacy topic-level file) —
     coarser than the persona×topic×**engine** granularity this lane's cell table needed, so this lane wrote a
     supplementary engine-exact check (`evidence/build_cell_table.py`) rather than editing the existing tool.
   - `story_atoms/<persona>/anchored/<topic>/<engine>/` directory presence+non-emptiness — confirmed exactly 6
     personas have any bank at all (`educators`, `first_responders`, `gen_z_professionals`, `healthcare_rns`,
     `millennial_women_professionals`, `working_parents`) — unchanged from the 07-22 audit.
   - `config/planning/chapter_thesis_bank.yaml` — confirmed `topics:` overlay covers exactly 8 topics
     (`procrastination`, `perfectionism`, `burnout`, `anxiety`, `boundaries`, `overthinking`, `self_worth`,
     `grief`) out of the 15 core production topics; everything else falls to the `intents→engine` baseline.
   - **`phoenix_v4/gates/check_tuple_viability.check_tuple_viability()`** — read the full function body. It is
     a pure read: checks (1) topic+engine binding in `config/topic_engine_bindings.yaml`, (2) arc file exists
     in `master_arcs/`, (3) STORY pool (`atoms/<persona>/<topic>/<engine>/CANONICAL.txt`) non-empty, (4) min
     pool depth, (5) emotional-band coverage. No render, no write. This is the exact function Lane A's CLI
     spot-checks called — this lane imported it directly and ran it across **all 657 cells** (not 4), which is
     Lane A's explicit `NEXT_ACTION`.
   - **`scripts/ci/check_research_fit_honesty.py` / `scripts/ci/check_book_story_authored.py`** — read both
     scripts' headers/argument parsing in full. **Confirmed they require a post-render `enrichment_audit.json`
     as input** (`ap.add_argument("--audit", ...)`, `_load_audit(path).read_text()` on a JSON file that a
     pipeline render writes). **They cannot run against an unrendered/PLANNED cell — there is no
     `enrichment_audit.json` until something is rendered.** Per the mission's own contingency: this lane's
     prediction for unrendered cells is therefore inferred from bank presence/absence + tuple-viability, **not**
     a live gate run of these two honesty checks. Stated explicitly, not silently.
3. **Structural confirmation that made the "robust sample" into a full sweep:** `atoms/` and `story_atoms/` are
   keyed **only** by `persona/topic/engine` — there is no brand subdirectory anywhere under either tree. A
   direct enumeration of all 32,401 book-plan filenames shows every one of the 40 brand archetypes draws from
   **the same 13-persona pool** in near-identical proportions (`way_stream_sanctuary` is the only outlier: an
   even 80-per-persona split across all 10 of its personas, vs. the ~85-115 spread the other 39 brands show).
   Of the 657 distinct cells, the median cell appears in **all 40 brands** — brand literally does not change
   atom-bank presence or research_fit bind-status for the same persona×topic×engine tuple. **This means a
   sample restricted to "N cells per brand" would have re-measured the same 657 underlying answers N×40 times.**
   Given the mission's explicit instruction not to artificially cap scale below what static tooling can cheaply
   cover, this lane instead ran the **full 657-cell enumeration once**, weighted by real per-cell book counts —
   an exact catalog-scale tabulation rather than a projected sample.

---

## 2. Full sample table (mission-required format)

The table below shows the mission's required fields for a representative, brand-diverse selection — Waystream
plus 4 non-Waystream brands spanning different persona/topic mixes, including the two brand classes Lane A
flagged (arc-healthy majority brands, and the 3 arc-orphaned brands). **Every row is drawn from the full
657-cell / 32,401-book sweep in `evidence/full_cell_table_with_tuple_viability.csv`** — this is not a separate,
smaller ad-hoc sample; it is 13 illustrative rows pulled from the full tabulation to show the pattern concretely
against real `book_id`s.

| Brand | Persona × Topic × Engine | CANONICAL.txt present? | story_atoms present? | Predicted bind status | Tuple-viability (live check) | Thesis-bank overlay | Predicted acceptance ceiling |
|---|---|---|---|---|---|---|---|
| `way_stream_sanctuary` | corporate_managers × anxiety × comparison | Yes | No | UNBOUND-thin | **PASS** | Yes | structurally clear only |
| `way_stream_sanctuary` | healthcare_rns × burnout × overwhelm | Yes | **Yes** | **BOUND** | **PASS** | Yes | authored-candidate-possible (see §5 caution) |
| `way_stream_sanctuary` | millennial_women_professionals × courage × false_alarm | Yes | **Yes** | **BOUND** | **PASS** | No | authored-candidate-possible |
| `adhd_forge` | corporate_managers × anxiety × comparison | Yes | No | UNBOUND-thin | PASS | Yes | structurally clear only |
| `adhd_forge` | working_parents × anxiety × overwhelm | Yes | **Yes** | **BOUND** | PASS | Yes | authored-candidate-possible |
| `stillness_press` | corporate_managers × anxiety × comparison | Yes | No | UNBOUND-thin | PASS | Yes | structurally clear only |
| `stillness_press` | working_parents × somatic_healing × false_alarm (fully-authored plan, `_needs_authoring: false`) | Yes | No | UNBOUND-thin | **FAIL** (`NO_BINDING`) | No | **likely never renders** despite hand-finished plan copy — matches Lane A §5's exact finding |
| `qi_foundation` (arc-orphaned brand) | corporate_managers × anxiety × comparison | Yes | No | UNBOUND-thin | PASS | Yes | structurally clear only *if* this specific book's arc pointer resolves (92% of this brand's don't, per Lane A §4 — orthogonal defect) |
| `qi_foundation` | healthcare_rns × burnout × overwhelm | Yes | **Yes** | **BOUND** | PASS | Yes | authored-candidate-possible *if arc resolves* |
| `body_memory` (arc-orphaned brand) | corporate_managers × anxiety × comparison | Yes | No | UNBOUND-thin | PASS | Yes | structurally clear only *if arc resolves* |
| `still_forest` (arc-orphaned brand) | corporate_managers × anxiety × comparison | Yes | No | UNBOUND-thin | PASS | Yes | structurally clear only *if arc resolves* |
| `cognitive_clarity` (flagged `inactive_archetypes` yet 821 live books) | corporate_managers × anxiety × comparison | Yes | No | UNBOUND-thin | PASS | Yes | structurally clear only |
| `cognitive_clarity` | healthcare_rns × burnout × overwhelm | Yes | **Yes** | **BOUND** | PASS | Yes | authored-candidate-possible |
| (any of 40 brands) | gen_z_student × imposter_syndrome × grief | No | No | **UNKNOWN** | **FAIL** (`NO_BINDING`) | No | **likely-hard-fail** — see §6, engine-mismatch defect class |

**Reading the pattern:** because bank presence is persona-keyed, the *same* cell (e.g.
`corporate_managers × anxiety × comparison`) predicts identically across `way_stream_sanctuary`, `adhd_forge`,
`stillness_press`, `qi_foundation`, `body_memory`, `still_forest`, and `cognitive_clarity` — 7 brands, 7
identical UNBOUND-thin/PASS verdicts. The brand dimension changes *whether the arc pointer for that specific
book resolves* (Lane A's arc-orphan finding, 3 brands only) and *whether a `_needs_authoring: false` plan
exists* — it does not change bind-status or tuple-viability at all.

---

## 3. Catalog-scale rollup (the number the operator asked for)

Full tabulation: `evidence/full_cell_table.csv` (657 rows, bind-status only) and
`evidence/full_cell_table_with_tuple_viability.csv` (657 rows, both checks). Summaries:
`evidence/rollup_summary.json`, `evidence/tuple_viability_summary.json`.

### 3.1 Predicted research_fit bind status (bank-presence prediction, full 32,401-book weighting)

| Predicted status | Books | % of catalog | Distinct cells | Predicted ceiling |
|---|---:|---:|---:|---|
| **BOUND** (canon + story_atoms both present) | 465 | 1.4% | 10 / 657 | authored-candidate-**possible** (not guaranteed — §5) |
| **UNBOUND-thin** (canon only) | 31,912 | 98.5% | 639 / 657 | structurally clear only (Layer 1 research_fit cap, per scorecard) |
| **UNKNOWN** (neither bank resolves for the exact engine) | 24 | 0.07% | 8 / 657 | likely-hard-fail |

### 3.2 Live tuple-viability sweep (real preflight gate, not a proxy — full 657-cell batch run)

| Tuple-viability | Books | % of catalog | Distinct cells | Dominant error code(s) |
|---|---:|---:|---:|---|
| **PASS** | 23,350 | 72.1% | 457 / 657 | — |
| **FAIL** | 9,051 | 27.9% | 200 / 657 | `NO_BINDING` (8,704 books), `BAND_DEFICIT` (5,704 books), `POOL_TOO_SHALLOW` (54 books) |

### 3.3 Cross-tabulation (the honest combined ceiling)

| Bind status | Tuple-viability PASS | Tuple-viability FAIL |
|---|---:|---:|
| BOUND | 465 (100% of BOUND) | 0 |
| UNBOUND-thin | 22,885 (71.7% of UNBOUND-thin) | 9,027 (28.3% of UNBOUND-thin) |
| UNKNOWN | 0 | 24 (100% of UNKNOWN) |

**Honest combined read of "is our plan and assembly idea working, at scale":**
- **1.4% of the catalog (465 books)** has both banks and passes preflight — the best case, capped at
  `authored-candidate-possible` (Layer 2), **not** guaranteed shippable at Layer 3 (system working) — see §5.
- **70.6% of the catalog (22,885 books)** has only the canonical atom bank, no character bank, but *would*
  clear the tuple-viability preflight — these would very likely render a `book.txt` and could well
  `register_gate` PASS, but are capped at `structurally clear only` per the scorecard's research_fit rule, with
  no character through-line.
- **27.9% of the catalog (9,051 books)** fails tuple-viability outright — for these, `structurally clear` is
  too generous a prediction; the honest label is closer to the scorecard's `path broken` (pipeline would likely
  halt before producing a coherent book), not merely "unbound."

---

## 4. Where the ceiling is worst

**On the bind-status axis** (does a persona have *any* story_atoms bank at all): **corporate_managers is tied,
not uniquely worst.** Of 13 personas, **7 sit at literal 0.0% BOUND** — `corporate_managers` (3,743 books),
`gen_x_sandwich` (3,734), `tech_finance_burnout` (3,723), `entrepreneurs` (3,696), `gen_alpha_students` (2,425),
`gen_z_student` (82, plus 24 UNKNOWN), and `nyc_executives` (2). Together these 7 personas account for
**17,407 books — 53.7% of the entire en_US catalog** — with zero story_atoms bank for their persona under any
topic or engine. Even the 6 personas that *do* have a bank only reach 1.5%–4.7% BOUND
(`working_parents` 1.5%, `gen_z_professionals` 3.0%, `healthcare_rns` 3.1%, `first_responders` 3.3%,
`millennial_women_professionals` 4.7%; `educators` shows 100% but n=2 books, not a real rate). Full table:
`evidence/persona_rollup.csv`.

**On the tuple-viability axis** (would the preflight gate actually pass): **corporate_managers is the single
worst-exposed major persona.** 32.5% of its 3,743 books (1,218) FAIL tuple-viability — the highest failure rate
of any of the 8 non-trivial personas (`gen_x_sandwich` 28.6%, `healthcare_rns` 29.4%, `gen_z_professionals`
27.7%, `working_parents`/`millennial_women_professionals` 27.6%, `tech_finance_burnout`/`entrepreneurs` 27.3%,
`gen_alpha_students` 20.9%). Combined with being the single largest persona by catalog volume, corporate_managers
is where the two independent failure modes (no character bank, worst preflight pass rate) stack hardest — this
is the persona a repair lane should target first, consistent with (and now more precisely sized than) the 07-22
audit's qualitative flag.

**On the topic axis**, `NO_BINDING` clusters sharply and does **not** track the thesis-bank topic overlay:
`burnout` (55.7% of its 3,683 books), `imposter_syndrome` (56.3% of 3,479), `overthinking` (55.7% of 3,352), and
`sleep_anxiety` (55.6% of 3,246) each have **more than half their planned books** hit `NO_BINDING` — yet
`burnout` and `overthinking` are *among the 8 topics with thesis-bank overlay coverage*. Thesis-overlay presence
and topic-engine binding are independent gaps; fixing one does not fix the other. `somatic_healing` is the
cleanest topic on this axis (1.1% NO_BINDING). Full table: `evidence/topic_rollup.csv`,
`evidence/full_cell_table_with_tuple_viability.csv`.

**`BAND_DEFICIT`** (arc requires an emotional band the atom pool doesn't cover) clusters similarly:
`imposter_syndrome` (857 books), `sleep_anxiety` (800), `overthinking` (682), `burnout` (398) — the same four
topics as the `NO_BINDING` cluster, suggesting these four topics are simply under-invested across the board,
not failing for one isolated reason.

---

## 5. What "BOUND" does NOT mean — explicit caution (mission-required)

**This lane's BOUND prediction is necessary, not sufficient, and the 07-22 audit already has a live
counter-example for one of the exact 10 BOUND cells this lane found.** `healthcare_rns × burnout × overwhelm`
is one of this lane's 10 BOUND cells (60 planned books catalog-wide, all predicted BOUND + tuple-viability
PASS). The 07-22 audit's Axis 1.2 live re-scored a real render of this exact cell (`healthcare_rns × burnout`
seed 43006): research_fit was genuinely **bound** (`research_fit_v1`, spine_pins=4) — and it still **FAILed
`chapter_flow`** and got a **Reject on `book_quality_gate`**. Per the acceptance scorecard, that book never
clears Layer 1 despite having a real character through-line. **This lane does not, and cannot, promise that
the other 464 BOUND-predicted books would fare better** — bank presence at plan time says nothing about
whether the specific render, on that specific day, with that specific atom draw, passes the Layer 1 hard
gates. BOUND is a **precondition** for `authored candidate`/`system working`, not a guarantee of either.

---

## 6. What this lane did NOT verify (explicit boundary)

- **No book in this lane was rendered, assembled, or gate-scored live.** Every FAIL/PASS/BOUND/UNBOUND verdict
  above is a **prediction** from static bank-presence + a read-only preflight function — not a live
  `register_gate` / `chapter_flow` / `book_quality_gate` run. The 07-22 audit's 3 live-rescored samples remain
  the only real gate-execution evidence this lane cites (§5); this lane did not add new live gate runs.
- **`check_research_fit_honesty.py` / `check_book_story_authored.py` cannot be run against these unrendered
  cells at all** (§1) — confirmed by reading their arguments; they require a real `enrichment_audit.json`.
  Nothing in this report should be read as those gates having run.
- **The 8 UNKNOWN cells (24 books, `gen_z_student × imposter_syndrome/overthinking`) are a narrower defect than
  "no bank for this topic at all."** Spot-checked directly: `atoms/gen_z_student/imposter_syndrome/` and
  `.../overthinking/` both exist and are well-populated with *other* engine subdirectories (e.g. `false_alarm`,
  `shame`, `comparison`, plus the narrative-slot dirs `PIVOT`/`SCENE`/`HOOK`/etc.) — but the **exact** engine
  values the catalog planner resolved for these 8 cells (`grief`, `watcher`, `overwhelm`, `spiral` for
  imposter_syndrome; `overwhelm`, `shame`, `comparison`, `grief` for overthinking) have no populated directory.
  This reads as an **engine-resolution mismatch** for a thin persona (`gen_z_student`, only 82 books total),
  not a wholesale absent bank — worth flagging precisely rather than folding into the larger "no bank" story.
- **Non-en_US locales** — out of scope, per Lane A's own boundary; this lane did not extend the sweep to the
  other 13 `book_plans_<locale>` directories.
- **The 3 arc-orphaned brands' (`qi_foundation`/`body_memory`/`still_forest`) *actual* per-book resolution rate**
  — this lane confirms (§2) that bind-status and tuple-viability are computed identically regardless of arc-
  pointer health (both are persona/topic/engine-keyed, not tied to the arc file itself), but did not
  cross-reference Lane A's per-book orphan list against this lane's cell table to compute exactly how many of
  each brand's BOUND/PASS-predicted books also have a resolvable arc pointer. That intersection is a same-day
  follow-up Lane F or a future lane could run cheaply from the two CSVs already on disk.

---

## 7. Sample-size discipline

**This lane did not sample below what static tooling could cheaply cover — it ran a full census.** All 657
distinct (persona, topic, engine) cells that exist anywhere in the 32,401-file en_US catalog were checked for
(a) CANONICAL.txt presence, (b) story_atoms presence, (c) thesis-bank topic-overlay membership, and (d) live
`check_tuple_viability()` result — not sampled, not extrapolated. This exceeds the mission's "smoke → pilot →
scale" minimums (2-3 → 10-15 → as-large-as-cheaply-possible) by running the maximum: every cell that will ever
appear in a per-brand sample, once, weighted by real book counts. The only reason this is called a "sample
table" in §2 is presentational — 13 illustrative rows are shown against concrete `book_id`s spanning Waystream
+ 6 non-Waystream brands (including all 3 arc-orphaned brands and the "inactive-but-821-books-live"
`cognitive_clarity` anomaly Lane A flagged) — the underlying finding is the full 657-cell/32,401-book
tabulation in §3, not an inference from those 13 rows.

Runtime note: the batch tuple-viability sweep over 657 cells took ~2.5 minutes wall-clock (backgrounded past
the default 120s Bash timeout, not because of any render — the function itself is fast; the wall-clock cost is
YAML-parsing 657 arc files + walking 657 atom directories on a large repo tree).

---

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Prime
TASK:           Lane C — catalog-scale assembly-readiness prediction
COMMIT_SHA:     <filled after commit>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/REPORT.md
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/full_cell_table.csv
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/full_cell_table_with_tuple_viability.csv
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/persona_rollup.csv
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/topic_rollup.csv
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/rollup_summary.json
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/tuple_viability_summary.json
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/build_cell_table.py
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/evidence/batch_tuple_viability.py
FILES_READ:     artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/REPORT.md (full, merged PR #221);
                artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md (full);
                docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md (Layer 1/Layer 2/Layer 3/Layer 4 taxonomy);
                config/planning/chapter_thesis_bank.yaml; scripts/inventory/atom_coverage_audit.py (ran fresh);
                phoenix_v4/gates/check_tuple_viability.py (full, imported check_tuple_viability() directly);
                scripts/ci/check_research_fit_honesty.py, scripts/ci/check_book_story_authored.py (headers/args,
                confirmed post-render-only); full enumeration of 32,401 config/source_of_truth/book_plans_en_us/*.yaml
                filenames; atoms/ and story_atoms/ directory trees (full walk for all 657 cells)
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722 (Axis 1-3 methodology + BOUND cell list this lane
                cross-validates and extends); lane_a_plan_inventory (sampling frame; NEXT_ACTION this lane executes:
                batch tuple-viability sweep) | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md
                (Layer 1 / Layer 2 / Layer 3 / Layer 4 taxonomy — every verdict in this lane framed against it) | builds_on:
                atom_coverage_audit.py (re-run, not modified), check_tuple_viability.py (imported read-only,
                not modified), check_research_fit_honesty.py / check_book_story_authored.py (read, confirmed
                unusable on unrendered cells, not modified) | inventory: EXTENDS (full 657-cell census; zero
                code/config touched)
STATUS:         completed
HANDOFF_TO:     Lane F (synthesis)
NEXT_ACTION:    Lane F: reconcile this lane's 1.4% BOUND / 98.5% UNBOUND-thin / 0.07% UNKNOWN catalog-scale
                split (and the independent 72.1%/27.9% tuple-viability split) against Lane A's headline
                (per-brand volume ~800, "the operator's 800-per-branding framing is now closer to true") — volume
                and assembly-readiness are two different axes and both need to be in the same synthesis
                paragraph, not conflated. Concrete repair candidates surfaced but not fixed here (read-only
                scope): (1) author story_atoms for corporate_managers first (largest persona, worst
                tuple-viability rate, zero character bank); (2) investigate NO_BINDING/BAND_DEFICIT root cause
                for the 4 clustered topics (burnout/imposter_syndrome/overthinking/sleep_anxiety) in
                config/topic_engine_bindings.yaml — these affect >50% of each topic's books regardless of brand;
                (3) the 8-cell gen_z_student engine-mismatch (§6) is a small, precisely-scoped fix (either
                populate the 4 missing engine dirs or correct the planner's engine resolution for that persona).
SIGNAL:         lane-c-assembly-readiness-merged=<sha>
```
