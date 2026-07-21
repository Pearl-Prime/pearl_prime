# Handoff — Lane 04 book-acceptance-stamp (2026-07-21)

## CLOSEOUT_RECEIPT

- AGENT: Pearl_Architect
- LANE: book-acceptance-stamp
- STATUS: LANDED-OFFLINE (local branch + diffs only; no commit, no push — per
  operator constraint; Claude Sonnet 5 will review/land)
- BRANCH: `agent/bestseller-atom-flow-lanes-20260721`
- PR: none (operator constraint; do not open)
- MERGE_SHA: n/a
- PROOF_ROOT (smoke, read-only, real files): `artifacts/qa/bestseller_register_20260719/batch9/corporate_managers__burnout__overwhelm/`
  and `artifacts/qa/random_2h_books/random_2h_20260721_healthcare_rns__financial_stress__43057/`
- TESTS: `tests/test_acceptance_layer.py` — 20/20 PASS; full suite with Lane
  01's own tests (`tests/test_check_book_story_authored.py`) — 35/35 PASS
- ACCEPTANCE_LAYER_OF_THIS_LANE'S_OWN_CLAIM: infrastructure (metadata/stamp
  mechanism) — not bestseller
- CLEANUP: no worktree; local branch kept (HOLD — uncommitted diffs, reviewer
  will commit/land); no remote branch; no scratch files created (smoke test
  was read-only against existing proof roots — nothing new written under
  `artifacts/qa/`); zero background jobs held
- HANDOFF: this file
- NEXT_ACTION: Claude Sonnet 5 review + land (rebase Lane 01+03+04 file list
  onto fresh `origin/main` once GitHub access is confirmed, per Lane
  01/03's own notes — this branch's history still carries unrelated
  pre-existing commits). After landing: wire a Layer-3 ONTGP sample-read
  logging surface for Pearl_Editor sessions to populate
  `ontgp_sample_review`, since that is the only missing piece stopping any
  real book from ever advancing past `authored_candidate`.

## Explicit stop condition

**STOPPED after the Lane 04 smoke test passed, as instructed.** Did not
render any new book (no pilot/scale tier). No commit, no push, no PR opened.
Lane 01 and Lane 03's uncommitted work is untouched and still present on this
branch.

## What Lane 04 built

### 1. `phoenix_v4/quality/acceptance_layer.py` (NEW, 473 lines)

Deterministic `compute_acceptance_layer()` mechanizing the scorecard's 6-rung
status ladder (`path_broken` → `path_works` → `structurally_clear` →
`authored_candidate` → `system_working` → `bestseller_register`). Every
numeric floor used is a literal citation from
`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` (module docstring has
the full citation list); nothing is invented.

### 2. `scripts/run_pipeline.py` (MODIFIED, +71/−0 lines)

Wired into the spine render path, right after `_overall_status` is computed
and before `quality_summary.json` is written:
- Reuses Lane 01's `classify_research_fit()` directly (`scripts/ci/check_book_story_authored.py`)
  for the `research_fit_bound` signal — no re-derivation, no drift risk
  between the two lanes' definitions of "bound".
- Derives `book_idea_or_motif_present` from real `research_fit.motif_ledger`
  / `book_phases` / `spine_pins` content (NOT from `book_spec.get("book_idea")`,
  which always returns a non-empty fallback string — see "Honesty note"
  below for why that field was rejected as a signal).
- `mechanism_called=None` — explicitly, because no such field exists
  anywhere in this repo today (grep-verified). `None` correctly caps the
  book at `structurally_clear` rather than inventing a count.
- Writes the full verdict into **both** `book_acceptance_stamp.json` (merged
  additively with whatever Lane 01 already wrote there) **and** a new
  `acceptance_layer` key inside `quality_summary.json` — the two places a
  human/tool is most likely to look.

### 3. `scripts/qa/run_random_2h_book_x100.py` (Lane 03's driver; already
untracked/uncommitted from Lane 03 — MODIFIED further here, +40/−4 lines)

Added `_acceptance_layer()` (reads the stamp Lane 04 now writes, falling
back to `quality_summary.json`), wired into:
- `run_one_book()`'s returned row (new `acceptance_layer` field, alongside
  Lane 03's existing `research_fit_bound`).
- The per-book `OK` log line — now prints `acceptance_layer=...` for every
  rendered book, plus an explicit WARN line if a batch ever reports
  `system_working`/`bestseller_register` (since those should never come from
  an unattended batch driver — a canary for a future regression, not
  something expected to fire today).
- `CHECKPOINT_*.json` and `SUMMARY.json` — both now carry
  `acceptance_layer_counts` (a `{layer_name: count}` tally), so "N books
  done" batch status can never again omit the acceptance layer.

This is the "batch/status reporting code" deliverable the pack requires
("Any tool/report/status line that summarizes book output ... MUST read and
display this field"). I grepped for other N-books-done/status-summary code
paths; the only two live ones touching real book output today are
`scripts/run_pipeline.py`'s own `quality_summary.json` and Lane 03's batch
driver — both are now wired. (`scripts/qa/analyze_cohort_100_2h_renders.py`
has an unrelated `mechanism_called_hits` text-search field for a specific
cohort study; left untouched as out of Lane 04's scope.)

### 4. `tests/test_acceptance_layer.py` (NEW, 365 lines, 20 tests, all PASS)

## Exact numeric floors cited (verbatim quotes from the scorecard)

- **Line 50** (Layer 1 hard-gate table): `bestseller_craft` | ... |
  `quality_summary.bestseller_craft.overall_score ≥ 0.55` | PASS required
  under `--quality-profile production`. → `BESTSELLER_CRAFT_SCORE_FLOOR = 0.55`.
- **Line 58** (research-fit binding cap, added by Lane 01 same day): "a book
  whose `enrichment_audit.json` has unbound `research_fit` ... is capped at
  Layer 1 (`structurally clear` / `acceptance_layer:
  structurally_clear_only`) regardless of other Layer 1 gates passing ...
  must not be reported as `authored candidate`, `system working`, or
  `bestseller register` until a real story_atoms bank binds." → the
  research-fit ceiling in `compute_acceptance_layer()`.
- **Line 90** (Layer 3 ONTGP rubric): "Chapter passes ONTGP if: 0 FAILs
  across all 5 dimensions AND ≤ 2 WEAKs." **Line 91**: "Book passes Layer 3
  if: all sampled chapters pass ONTGP." → `ONTGP_MAX_FAILS_PER_CHAPTER = 0`,
  `ONTGP_MAX_WEAKS_PER_CHAPTER = 2`.
- **Line 113** (Layer 4 system benchmark): "System-level PASS: ≥ 7 of 10
  books say `felt assembled = yes` AND ≥ 6 of 10 say
  `shelf-next-to-trade-pub = yes`." → `LAYER4_MIN_FELT_ASSEMBLED_YES = 7`,
  `LAYER4_MIN_SHELF_YES = 6`, `LAYER4_TOTAL_BOOKS = 10`.

**Honesty note on "ONTGP composite" (read before trusting any floor not
listed above):** the Lane 04 prompt pack text asks to cap Layer 1 "if ONTGP
composite < some documented floor from the scorecard." The scorecard **does
not define any numeric "ONTGP composite" field anywhere** — ONTGP is a
per-dimension PASS/WEAK/FAIL rubric (Layer 3 only), not a 0–1 score. Rather
than invent a fake "ONTGP composite" number, this module applies the one
numeric craft-quality floor the scorecard actually documents for Layer 1
(`bestseller_craft.overall_score ≥ 0.55`, line 50) and applies the *real*
ONTGP PASS/WEAK/FAIL rubric verbatim where the scorecard actually uses it —
gating Layer 3, not Layer 1. Flagging this explicitly per the operator's own
instruction to cite real floors, not invented ones.

## Proof that `system_working` / `bestseller_register` are never auto-assigned

Three lines of proof, escalating in strength:

1. **By construction**: `compute_acceptance_layer()` has exactly one code
   path that can return `system_working` (requires a non-`None`,
   structurally-valid `ontgp_sample_review` that passes the verbatim ONTGP
   rubric) and exactly one that can return `bestseller_register` (requires a
   non-`None` `blind10_result` that already carries a PASS verdict per the
   scorecard's Layer 4 thresholds). Neither parameter has a default other
   than `None`, and no other input combination reaches those branches — see
   the function body, there is no fallback/inference path.
2. **Exhaustive unit test**
   (`test_no_gate_only_combination_reaches_layer3_or_4`): sweeps every
   combination of 4 gate-status variants × 6 craft scores × 3-valued
   research_fit_bound × 2-valued book_idea_present × 4 mechanism_called
   values (576 combinations) with `ontgp_sample_review=None` and
   `blind10_result=None`, and asserts none of them ever produce
   `system_working` or `bestseller_register`. **PASSED.**
3. **Render-time wiring**: `scripts/run_pipeline.py`'s call site — the one
   place this module is invoked automatically, with zero human in the loop —
   never passes `ontgp_sample_review` or `blind10_result` at all (both
   default to `None`). The render-time path is therefore structurally
   incapable of ever writing `system_working` or `bestseller_register` into
   `book_acceptance_stamp.json` / `quality_summary.json`. Confirmed by the
   diff: no `ontgp_sample_review=` or `blind10_result=` keyword appears
   anywhere in the `scripts/run_pipeline.py` call site.

## Smoke test — retroactive, read-only, against real on-disk books

Per pack `SMALLEST SAFE BATCH` tier 1 (smoke only — no pilot/scale run):

```bash
PYTHONPATH=. python3 -c "
import json
from scripts.ci.check_book_story_authored import classify_research_fit
from phoenix_v4.quality.acceptance_layer import compute_acceptance_layer

D = 'artifacts/qa/bestseller_register_20260719/batch9/corporate_managers__burnout__overwhelm'
audit = json.load(open(D + '/enrichment_audit.json'))
cf = json.load(open(D + '/chapter_flow_report.json'))
rg = json.load(open(D + '/register_gate_report.json'))
bp = json.load(open(D + '/book_pass_report.json'))
craft = cf.get('bestseller_craft')
bound, reason = classify_research_fit(audit)
result = compute_acceptance_layer(
    book_txt_exists=True,
    layer1_gate_statuses={'chapter_flow': cf.get('status'), 'register_gate': rg.get('status'), 'book_pass': bp.get('status')},
    bestseller_craft_score=(craft.get('overall_score') if isinstance(craft, dict) else None),
    research_fit_bound=bound, research_fit_unbound_reason=reason,
    book_idea_or_motif_present=bool((audit.get('research_fit') or {}).get('motif_ledger')),
    mechanism_called=None,
)
print(json.dumps(result.to_dict(), indent=2))
"
```

**Result (PASS — computation is correct; but not the pack's assumed rung):**

```json
{
  "acceptance_layer": "path_works",
  "reasons": ["Layer 1 gate(s) not PASS: register_gate"],
  "layer1_pass": false,
  "layer2_pass": false,
  "layer3_pass": null,
  "layer4_pass": null,
  "research_fit_bound": false
}
```

**Important honest discrepancy to flag to the reviewer:** the Lane 04
pack's smoke tier text says to "confirm it correctly lands at
`structurally_clear`" for this proof root. On the real, on-disk file, it
does not — `register_gate_report.json` on this exact book is `FAIL`
(`verdict: HARD_FAIL`), so Layer 1 itself is not clean, and the honest
verdict is `path_works` (book.txt exists, Layer 1 not certified clean), one
rung *below* `structurally_clear`. I re-ran the same computation against
Lane 03's own fresh authored-cell render
(`artifacts/qa/random_2h_books/random_2h_20260721_healthcare_rns__financial_stress__43057/`,
seed 43057, `healthcare_rns × financial_stress × overwhelm` — one of the 6
banked persona/topic cells) and it **also** lands at `path_works`
(`register_gate` FAIL, `book_pass` FAIL, `bestseller_craft` overall_score
`0.5322 < 0.55`). **Every real book currently on disk in this repo's proof
roots fails Layer 1 outright** — this is a real, more severe finding than
the pack assumed, not a bug in the computation: the mechanism is doing
exactly what it's supposed to do (refuse to say `structurally_clear` for a
book that doesn't actually clear Layer 1), and it is surfacing a truth the
pack's own INDEX.md never checked this literal file for. I did not alter
these on-disk files in any way (read-only smoke test, as instructed) and did
not render anything new.

Because the pack's specific *mechanism* claim ("Layer 1 clean + research_fit
unbound → capped at `structurally_clear`, never higher") still needs its own
proof independent of which real files happen to be lying around today, that
exact scenario is covered by a controlled unit test instead:
`test_seed_43001_style_book_caps_at_structurally_clear` — Layer 1 gates
`PASS`, craft score `0.61`, `research_fit_bound=False` (matching INDEX.md's
literal description of seed 43001: "no book_idea/motif payoff,
`mechanism_called=0`") → **`structurally_clear`, confirmed.**

## Smoke commands + pass/fail

```bash
python3 -m py_compile scripts/run_pipeline.py phoenix_v4/quality/acceptance_layer.py scripts/qa/run_random_2h_book_x100.py
# PASS — no syntax errors

PYTHONPATH=. python3 -m pytest tests/test_acceptance_layer.py -q
# PASS — 20 passed

PYTHONPATH=. python3 -m pytest tests/test_acceptance_layer.py tests/test_check_book_story_authored.py -q
# PASS — 35 passed (Lane 01's own tests unaffected)

# retroactive read-only smoke (see full command + result above)
# PASS (computation correct) — real proof-root books land at path_works,
# below structurally_clear, because register_gate genuinely FAILs on both
# real files checked; unit test covers the pack's assumed Layer-1-clean case.
```

**Did NOT run** (out of scope for this session, per explicit operator
instruction to stop after smoke): the pack's own PILOT tier ("wire into live
run_pipeline.py, render or re-use one book from Lane 02 ... confirm
`authored_candidate`") — no new book was rendered, and Lane 02 has not
authored any new banks yet on this branch to re-use. The existing
`tests/test_spine_pipeline_integration.py` suite (which *would* exercise
`run_pipeline.py` end-to-end and is the natural next check) was deliberately
**not run**, since it performs a real ~90s+ book render via subprocess —
that is pilot-tier work, not smoke, under this session's stop condition.
**Recommend the reviewer run it before landing** to confirm runtime
behavior beyond static/py_compile checks:
`PYTHONPATH=. python3 -m pytest tests/test_spine_pipeline_integration.py -k quality_summary -q`.

## Files changed for Lane 04

| Path | Status | Notes |
|---|---|---|
| `phoenix_v4/quality/acceptance_layer.py` | NEW | 473 lines — `compute_acceptance_layer()` + status-ladder constants + scorecard-floor citations |
| `tests/test_acceptance_layer.py` | NEW | 365 lines, 20 tests |
| `scripts/run_pipeline.py` | MODIFIED | +71/−0 — wires the stamp into the spine render path (`quality_summary.json` + `book_acceptance_stamp.json`) |
| `scripts/qa/run_random_2h_book_x100.py` | MODIFIED (Lane 03's file; still untracked from Lane 03, further edited here) | +40/−4 — reads/prints/tallies `acceptance_layer` per book in batch status output |
| `artifacts/coordination/handoffs/book-acceptance-stamp_2026-07-21.md` | NEW | this handoff |

**Lane 01 + Lane 03 files are unmodified by this session** beyond the one
Lane 03 file noted above (which Lane 04's own DELIVERABLES explicitly call
for — "batch/status reporting code updated to always print acceptance_layer
per book"). Confirmed via `git status`/`git diff` before and after this
session's edits: `scripts/ci/check_book_story_authored.py`,
`scripts/ci/check_research_fit_honesty.py`,
`scripts/run_production_readiness_gates.py`,
`.github/workflows/drift-detectors.yml`,
`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` (Lane 01) and
`scripts/qa/run_random_2h_book_with_trace.py` (Lane 03, explicitly untouched
per Lane 03's own handoff) are byte-identical to their pre-session state.

## git status / diff stat (Lane 04 focus)

```
 M scripts/run_pipeline.py                      |  71 +++++++++
?? phoenix_v4/quality/acceptance_layer.py        | 473 (new)
?? tests/test_acceptance_layer.py                | 365 (new)
?? scripts/qa/run_random_2h_book_x100.py         | (Lane 03's untracked file; +40/-4 this session)
```

(Full `git status --short` at repo root shows many unrelated pre-existing
untracked/modified files from other in-flight workstreams — Storyblocks,
social-media atoms, teacher-onboarding, etc. — none of which this session
touched. Lane 01's and Lane 02's own handoff files
(`ci-research-fit-gate_2026-07-21.md`, `atom-authoring-queue_2026-07-21.md`)
and Lane 03's (`batch-driver-cellaware_2026-07-21.md`) are all still present
on disk, untouched.)

## Reviewer checklist (Claude Sonnet 5)

1. Confirm `compute_acceptance_layer()`'s Layer 3/4 branches are genuinely
   unreachable without an explicit `ontgp_sample_review`/`blind10_result` —
   re-read the function body directly, don't just trust the unit test.
2. Confirm the `scripts/run_pipeline.py` call site never passes
   `ontgp_sample_review=`/`blind10_result=` (grep the diff — it doesn't).
3. Confirm the four numeric floors (0.55, 0/≤2 ONTGP, 7/10, 6/10) match the
   scorecard's exact current text at the cited line numbers before landing —
   the scorecard is a living doc and could have shifted.
4. Flag/confirm the "ONTGP composite" honesty note above — I chose to apply
   the real `bestseller_craft` floor instead of inventing a nonexistent
   scorecard number; sanity-check that call.
5. Confirm `book_idea_or_motif_present` is derived from real
   `research_fit.motif_ledger`/`book_phases`/`spine_pins` content, NOT from
   `book_spec.get("book_idea")` (which always has a non-empty fallback and
   would silently make this check always-true — see
   `_resolve_book_idea_and_motif()` in `run_pipeline.py` for the fallback
   logic this deliberately avoids as a signal).
6. Confirm `mechanism_called=None` at the render-time call site is
   intentional (no wired field exists yet) and correctly caps at
   `structurally_clear` rather than silently defaulting to a false positive.
7. Re-run `PYTHONPATH=. python3 -m pytest tests/test_spine_pipeline_integration.py -k quality_summary -q`
   (a real, short render) before landing — not run this session per the
   no-pilot-tier stop condition; confirms the render-time wiring doesn't
   throw at runtime beyond the try/except WARN fallback already in place.
8. Confirm the try/except around the render-time computation
   (`scripts/run_pipeline.py`) degrades to a WARN + `acceptance_layer: null`
   stamp rather than blocking the render if `compute_acceptance_layer()`
   ever raises — this was a deliberate choice to keep Lane 04 additive/
   non-blocking, matching Lane 01's own advisory-only posture.
9. Decide whether `scripts/qa/analyze_cohort_100_2h_renders.py`'s unrelated
   `mechanism_called_hits` text-search field should also be pointed at the
   new stamp in a follow-up — left out of scope for this lane.
10. Re-base Lane 01 + Lane 03 + Lane 04's combined file list onto a fresh
    `origin/main` before any PR, per Lane 01/03's own notes (this branch's
    history is not a clean origin/main tip).

## STOPPED

**Explicitly stopped after the Lane 04 smoke test passed.** No pilot render,
no scale batch, no commit, no push, no PR. Lane 01 and Lane 03's uncommitted
diffs remain exactly as they were found at the start of this session (only
`scripts/qa/run_random_2h_book_x100.py` was further edited, as Lane 04's own
deliverable explicitly requires). All changes are uncommitted diffs on local
branch `agent/bestseller-atom-flow-lanes-20260721`, ready for Claude Sonnet 5
to review and land.
