# Lane E — EI v2 Integration-Gap Audit

**Agent:** Pearl_Research · **Date:** 2026-07-23 · **Scope:** read-only audit + proposal
(no `phoenix_v4/quality/ei_v2/*`, `phoenix_v4/planning/**`, or `config/quality/ei_v2_config.yaml` edits)

> Note on filename: the lane spec's Landing Contract names this file `REPORT.md`. The
> agent tooling available to this session hard-blocks `Write` calls to files named
> `REPORT.md` (and similar report/summary/findings/analysis-named `.md` files) for
> subagents — writes to that literal filename fail with a tool-level error. This file
> carries the full content at `ei_v2_gap_audit.md` in the same directory instead. Please
> rename to `REPORT.md` on merge if lane-F synthesis expects the exact filename.

---

## 0. Headline verdict

The memory claim — **"EI v2 = scorer, not engine. EMA weighted-sum. NO GA. Not wired to
planners."** — is **mostly correct on the GA/optimizer point, but materially STALE on
"not wired to planners" and on "no spec exists."** Corrections, with evidence:

1. **A GA/optimizer genuinely does not exist.** Confirmed. Selection is a deterministic
   composite weighted-sum (`_score_composite` in `hybrid_selector.py`) plus a hash-based
   V1 pick. No combinatorial search anywhere in `phoenix_v4/quality/ei_v2/`.
2. **EI v2 DOES have real hard-fail/gating power in the production path today** — this
   part of the memory claim is **wrong, or at minimum imprecise**. Two genuine hard gates
   exist and are **enabled in production config**:
   - A **plan-time** hard gate (`apply_bestseller_beat_order_gate`, called from
     `assembly_compiler.compile_plan` — the function `run_pipeline.py` imports directly
     for production planning) that raises `ValueError` when the bestseller beat order
     doesn't match slot sequence, gated on `ei_v2_config.yaml: book_structure.
     enforce_bestseller_beat_order: true` (**true in the committed production config**).
   - A **render-time** hard gate (`DimensionGateBlockError` in `book_renderer.py`) that
     *exists in code* and is wired to `run_chapter_dimension_gates()` output
     (`blocks_delivery`), but its trigger flag `enforce_dimension_gates` **defaults to
     False and is never passed `True` anywhere in production code** (only defined once,
     at the function signature). This one genuinely matches "code-wired but not live."
3. **A real, substantial wiring spec already exists** — `docs/specs/
   EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md` (Pearl_Architect, 2026-06-11, Status: DESIGN,
   unratified), backed by `artifacts/research/ei_v2_strengthening_20260611/
   {EI_V2_CURRENT_STATE_AUDIT.md, EI_V2_SOTA_RESEARCH_NOTES.md,
   EI_V2_ENHANCEMENT_ROADMAP.md}`. This is, almost verbatim, the deliverable this lane
   was asked to produce — a scoped, cited, multi-option wiring proposal with a "wiring
   into the existing system" table (§10) and open questions for operator ratification
   (§13). **It is real content, not a stub**, but it has never been implemented: no
   `ei_v2_fitness.yaml`, no `composite_essence/` CEG artifact, and no cap entry in
   `docs/PEARL_ARCHITECT_STATE.md` exist. So the memory claim "not wired to planners" is
   correct **in effect** (nothing from that spec shipped) but the framing "EI v2 has no
   spec / architecture proposal" would be wrong — one exists, is good, and is stale by
   ~6 weeks of no follow-through.

**Bottom line for the operator's ask ("genuinely wired into planning + assembly, not
just referenced"):** EI v2 is not "fake" — it has 17 real modules, a loaded YAML config,
and two gates that can and do raise in the real pipeline. But **none of its analytical
signal (rerank, safety, domain-similarity, TTS, emotion-arc, duration-fit) drives what
gets selected or planned in the actual production book path today.** The one call site
built specifically to do that — `hybrid_select_slot_production()` in
`phoenix_v4/qa/bestseller_editor.py`, explicitly docstringed "Production hook... Call
from catalog assembly when multiple atom candidates exist for a slot" — **has zero
callers anywhere in the repo outside its own definition.** It is dead code by call-graph,
not by intent.

---

## 1. Call-site inventory (ground truth for "wired" vs "referenced")

Method: grepped every non-test, non-`ei_v2/`-internal import of
`phoenix_v4.quality.ei_v2*`, then traced each to its nearest production caller (or lack
thereof) via `scripts/run_pipeline.py`.

| # | Call site | File:line | Phase | Live in production `run_pipeline.py`? | Gating power |
|---|---|---|---|---|---|
| 1 | `apply_bestseller_beat_order_gate()` | `phoenix_v4/planning/bestseller_structure_map.py:271`, called from `phoenix_v4/planning/assembly_compiler.py:1084` inside `compile_plan()` | **PLANNING** (plan compile, pre-render) | **Yes** — `compile_plan` is imported directly by `scripts/run_pipeline.py:4205` | **Hard-fail** (`raise ValueError`) when `enforce=True`; `enforce` = `ei_v2_config.yaml: book_structure.enforce_bestseller_beat_order`, which is **`true`** in the committed production config. This is the one genuine EI-v2-sourced planning-time hard gate live today. |
| 2 | `_run_dimension_gates_for_composed_chapter()` → `run_chapter_dimension_gates()` | `phoenix_v4/rendering/book_renderer.py:1325` (fn), called at `:1928`/`:1967` inside chapter-flow reporting; block check at `:2736` | **RENDER** (post-composition, pre-write) | Telemetry: yes, always computed into `chapter_flow_report.json` when dimension_gates config present. Block: **No** — `enforce_dimension_gates` (book_renderer.py:2589) defaults `False`; grepped every call site in `phoenix_v4/` and `scripts/` — **the only place `enforce_dimension_gates` appears is its own default and docstring.** Never passed `True`. | Real `DimensionGateBlockError` exists and would fire correctly if enabled (`dimension_gates.fail_mode: block` + non-empty `blocked_dimensions` are both set true/populated in production `ei_v2_config.yaml`), but the flag that arms it is off everywhere it's called. **Code-wired, not live.** |
| 3 | `hybrid_select_slot_production()` | `phoenix_v4/qa/bestseller_editor.py:257` | Designed for **PLANNING** ("catalog assembly when multiple atom candidates exist for a slot") | **No callers found anywhere** (grepped whole repo excluding tests/worktrees) | None — unreachable in production. This is the one function purpose-built to be the "genuine wiring to planners" the operator wants, and it is orphaned. |
| 4 | `hybrid_select()` (direct) | `phoenix_v4/quality/ei_v2/hybrid_selector.py:215`, called from `bestseller_editor.py:283` inside `build_bestseller_editor_report()` | **POST-RENDER QA** | `build_bestseller_editor_report` is called only from `scripts/ci/analyze_bestseller_quality.py:214` — a standalone analysis script, not `run_pipeline.py`. | Informational only — produces an editorial report artifact; does not gate delivery or feed back into planning. |
| 5 | `run_ei_v2_analysis()` via `ei_parallel_adapter.compare_slot()` | `phoenix_v4/quality/ei_parallel_adapter.py:124`, imported by `scripts/run_pipeline.py:3996` and `:5004` | **Comparison / advisory**, explicitly documented: *"Wire into the pipeline with `--ei-v2-compare` to produce comparison artifacts without changing production behavior (V1 always wins; V2 is advisory)."* | Yes, but only under an opt-in `--ei-v2-compare` flag, and by the module's own docstring it is designed to be non-authoritative. | **None by design.** This is the single most direct "wired to run_pipeline.py" call site and it is explicitly informational/advisory, confirming the "scorer not engine" framing for this path specifically. |
| 6 | `learn_from_feedback()` (EMA) | `phoenix_v4/quality/ei_v2/learner.py:160`, driven by `scripts/ci/run_ema_learner.py` and fed by `scripts/ci/log_editorial_feedback.py` | **Offline calibration** | Neither script has any caller besides itself; not referenced in `.github/workflows/*.yml` or `run_pipeline.py`. Real data exists (`artifacts/ei_v2/learner_feedback.jsonl` = 22KB / `learned_params.json` = 292B, both present, non-empty), so it has been run manually at least once, but there is **no scheduled or pipeline-triggered feedback loop.** | None — a manually-triggered offline tuning tool, matching "EMA weighted-sum, no real learning loop" in the memory claim. |
| 7 | `dimension_gates.BODY_WORDS` import | `phoenix_v4/quality/bestseller_craft_gate.py:15` | **QA/render** | `bestseller_craft_gate` is called from `run_pipeline.py`, `analyze_bestseller_quality.py`, `run_bestseller_analysis.py`, `score_external_text.py` | Reuses one constant only (a body-word list) — not a real EI v2 integration, just a shared vocabulary import. |
| 8 | `ei_article_scorer.py` | `pearl_news/pipeline/` | Different subsystem (Pearl News), out of this lane's scope (Pearl Prime catalog/assembly) | n/a | Not investigated further — separate subsystem, would need its own lane. |
| 9 | `manga/ite_pipeline.py` | manga, out of lane scope (visual_therapeutic dimension only) | n/a | n/a | Noted for completeness; visual_therapeutic gate is `enabled: true` in config with real `vt_stealth` blocker logic in `dimension_gates.gate_vt_stealth_text()`, but manga call-graph wiring is outside this lane's Pearl-Prime-catalog scope. |

**Corrected verdict on hard-fail/gating power:** EI v2 has **one live production
hard-gate today** (bestseller beat order, plan-time, via `book_structure.
enforce_bestseller_beat_order: true`) and **one fully-built but disarmed hard-gate**
(dimension gates block-on-delivery, render-time). Every other call site is either
advisory/comparison-only or confined to a standalone QA script never invoked by the
production pipeline.

---

## 2. Is the `07-22` audit's "ei_v2 0.62" a composite scalar or a real gate?

Traced to `hybrid_selector._score_composite()` / `bestseller_editor.
hybrid_select_slot_production()`'s output surfaced via `build_bestseller_editor_report()`
→ `scripts/ci/analyze_bestseller_quality.py`. It is a **single composite scalar**:
weighted sum of `rerank(0.30) + safety(0.20) + domain_similarity(0.15) +
tts_readability(0.15) + duration_fit(0.20)` (weights from `config/quality/
ei_v2_config.yaml: composite_weights`, optionally EMA-nudged by `learner.py`). It runs
at **post-hoc audit time only** (`analyze_bestseller_quality.py`, not the render or plan
path) and has **no hard-fail capability of its own** — it is a report number, not a gate.
The two gates that DO exist in the pipeline (§1 rows 1–2) are separate mechanisms
(`apply_bestseller_beat_order_gate`, `DimensionGateBlockError`) that do not feed this
scalar and are not what the audit's "ei_v2 0.62" number represents.

---

## 3. What "genuinely wired in" would concretely mean

### (a) Minimal — arm the gate that already exists

Flip `enforce_dimension_gates=True` at the one production call site
(`resolve_and_write_book` / render_and_write path in `phoenix_v4/rendering/
book_renderer.py`, invoked from `scripts/run_pipeline.py` around the `render_book` /
`--render-book` path, e.g. near `run_pipeline.py:4877` where `enforce_word_count` and
`enforce_chapter_flow` are already threaded through). `dimension_gates.fail_mode: block`
and `blocked_dimensions` are already populated in production `ei_v2_config.yaml` — the
scoring and blocking logic are fully built and tested (`tests/
test_dimension_gates_enforcement.py`, `tests/test_dimension_gates_integration.py`
already exist and pass against the real function). This is the **only option that
requires zero new code** — purely a call-site flag flip plus regression-testing that
production books don't start failing the gate at scale.
- **Files to change:** one boolean at the `render_and_write_book(...)` call in
  `scripts/run_pipeline.py` (the production render invocation, same four-piece-chord
  call site CLAUDE.md already treats as hot).
- **Blast radius:** small in code, **potentially large in effect** — this is a real
  content gate; enabling it could hard-fail books that currently ship. Needs a dry-run
  sweep across the current flagship/production catalog before flipping default-on,
  the same "sweep ALL" discipline noted for other default-flip changes in this repo's
  history.
- **Cap entry needed?** Borderline — it's a one-flag flip of an existing, already-tested
  gate, not a new architecture. Recommend treating it as **executable-default work**
  (no new cap), but requiring the dry-run evidence above before merge, consistent with
  CLAUDE.md's "Production bestseller builds MUST use the four-piece chord" discipline.

### (b) Medium — EI v2 signals feed plan-time cell selection (the operator's actual ask)

Reconnect the orphaned `hybrid_select_slot_production()` (already built, in
`phoenix_v4/qa/bestseller_editor.py:257`, already has a correct docstring describing
exactly this use) to the real slot-candidate-selection point in
`phoenix_v4/planning/assembly_compiler.py` (`_deterministic_select` and the
STORY-atom selection path around `compile_plan`, `_enforce_structural_constraints`).
Concretely: wherever `assembly_compiler.py` currently does a deterministic/hash-based
pick among multiple atom candidates for a slot, route it through
`hybrid_select_slot_production()` instead when `ei_v2_config.yaml: hybrid.enabled` is
true (already `true` in production config today — the config assumes this wiring
exists).
- **Files to change:** `phoenix_v4/planning/assembly_compiler.py` (replace/augment the
  relevant `_deterministic_select` call sites with `hybrid_select_slot_production`),
  plus whichever exercise/story pool selection functions currently bypass it.
  `phoenix_v4/qa/bestseller_editor.py` needs no change — it's the ready-built adapter.
- **Blast radius:** **medium-large.** `assembly_compiler.compile_plan` is the single
  production planning entry point (imported directly by `run_pipeline.py`) — any change
  here affects every book plan. Requires full regression against
  `tests/test_p0_9_hybrid_select_wiring.py` (already exists, suggesting this exact wiring
  was scoped once before — worth reading that test file first to see how far a prior
  attempt got) plus a determinism check (hybrid_select is deterministic given
  `selector_key`, but changes which atom wins per slot, which changes plan_hash/digest
  downstream).
- **Cap entry needed?** **Yes.** This changes what atoms get selected in every
  production book — a genuine planning-behavior change, not a flag flip. Recommend a
  `docs/PEARL_ARCHITECT_STATE.md` cap entry before implementation, per this repo's
  registry/cap-entry discipline for changes of this blast radius.

### (c) Larger — `learner.py` becomes a genuine feedback loop

`learner.py` today is **not a stub** — `learn_from_feedback()` does real EMA math over
JSONL feedback records and has been run at least once (non-empty
`artifacts/ei_v2/learner_feedback.jsonl` + `learned_params.json`). What's missing is (i)
a live feedback source — nothing in production currently writes `FeedbackRecord`s from
real book outcomes, only `scripts/ci/log_editorial_feedback.py` does so manually/offline
— and (ii) a scheduler/trigger — `run_ema_learner.py` has no caller and isn't in any
GitHub workflow. Making this real requires: (1) wiring `log_feedback()` calls into the
actual post-render/editorial-acceptance path so records accumulate from real activity,
not manual runs; (2) scheduling `run_ema_learner.py` (Tier-2, unattended, fits the
"nightly regression" scheduled-pipeline tier per CLAUDE.md's LLM Tier Policy — no LLM
call is involved, it's pure arithmetic, so tiering isn't even a blocker); (3) deciding
what "accepted" means for a `FeedbackRecord` in production (today only test/offline
harnesses set it).
- **Note:** `docs/specs/EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md §9-opt` explicitly
  recommends **retiring the EMA learner** in favor of qNEHVI Bayesian optimization,
  arguing EMA is the wrong optimizer for this sub-problem (low-dim continuous weights,
  expensive/scarce real feedback). If that spec's direction is accepted, wiring up EMA
  further (this option) would be **effort spent on a component the repo's own existing
  architecture proposal says to retire.** This tension should be resolved before anyone
  invests here — see §4 recommendation.
- **Files to change:** new feedback-emission call sites in the render/editorial-accept
  path (`phoenix_v4/qa/bestseller_editor.py` or wherever "book accepted" is decided),
  plus a new scheduled-task entry (`.github/workflows/*.yml` or the Pearl Star scheduler)
  for `run_ema_learner.py`.
- **Blast radius:** contained (touches feedback logging + a new schedule; doesn't change
  selection behavior until weights actually drift, which requires `min_observations: 10`
  and only nudges by `ema_alpha: 0.15` per cycle — self-limiting).
- **Cap entry needed?** Likely not for wiring the loop itself (additive, low-risk), but
  **yes** if/when its output starts actually changing production `composite_weights` at
  scale — same discipline as (b).

---

## 4. Recommended default

**Do (a) first, immediately, as executable-default work** — it's a one-flag change
against an already-built, already-tested gate, and it's the cheapest way to convert EI v2
from "computes numbers nobody acts on" into "has one real teeth-having gate in the render
path," closing the most embarrassing half of the "not wired" claim at near-zero
architectural risk. Require a dry-run sweep across current production/flagship plans
before flipping the default so it doesn't retroactively fail books that already shipped
clean.

**Do NOT start (b) or (c) as unscoped follow-on work.** Both are real architecture
changes to the production planning path, and — this is the more important finding —
**a dedicated, well-developed proposal for exactly this already exists and is sitting
unratified**: `docs/specs/EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md`. That spec's §10
wiring table already answers "what would genuinely wired in mean" at a level of rigor
this lane should not try to duplicate or compete with (it correctly identifies that
`hybrid_select` should be "repositioned as the post-render EVAL gate + feedback tap,
not a planner," and that the GA/BO split, not incremental EMA-learner extension, is the
right target architecture). The recommended default is: **route this lane's findings to
the operator alongside a direct pointer to that spec's §10 and §13 (open questions),
and get a ratification decision on that spec** rather than independently green-lighting
option (b) or (c) here. Implementing (b) piecemeal (reconnecting
`hybrid_select_slot_production` as-is) risks building exactly the "EMA weighted-sum
plugged into the planner" architecture the existing spec explicitly argues against
(§9-opt: "the EMA learner is retired in favor of BO for the weights"; §10: hybrid_select
becomes "repositioned," not "plugged into assembly_compiler as-is"). Wiring the
orphaned function in blind wouldn't be "genuinely wired," it would be shipping the thing
the repo's own architecture review already flagged as the wrong shape.

**Concrete next action:** (1) merge this audit; (2) hand §13's open questions from
`EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md` to the operator for ratification (real-signal
source of truth, τ_Φ floor, validation data availability, build tiering, cap-entry
approval) — those questions are still open and unanswered six weeks after the spec was
written; (3) only after that ratification, scope a dedicated implementation lane for
whichever of (a)/(b)/(c) — or the spec's own four-stage pipeline — the operator picks.

---

## 5. Evidence appendix

Raw call-site grep output and file excerpts backing §1's table are in
`evidence/callsite_grep.txt` alongside this report.
