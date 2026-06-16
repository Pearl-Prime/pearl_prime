# PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM

**Status:** v1 — program operating-system + materialized deliverables for the focus → repair → deepen → validate → scale path toward 1,000 cohesive Pearl Prime books.
**Effective:** 2026-06-14
**Owner:** Pearl_Architect (Pearl Prime Bestseller Program)
**Scope of THIS document:** the **operating system** for the build program — the governing-spec routing, the materialized §12 deliverables (active slate, Wave 1, fix-first queue, pilot set + run plan, gated fan-out), and the human-review gate. It is **not** a re-statement of the program theory; the 14-section program theory lives in the governing spec below and is referenced, not duplicated (anti-reinvention / reuse-not-greenfield).

---

## §0 — Anti-reinvention notice (read first)

This program does **not** introduce a new gate, a new craft spec, a new pipeline, or a parallel program. It **routes into** existing canonical authority and materializes the operator's deliverables on top of it. Every gate, craft rule, and runtime path cited here already exists; this doc cites the canonical file and never redefines it.

The program spec is registered in the Canonical Artifacts Registry under concept_key `pearl_prime_build_program` (`artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`). Any future "build program" work edits these files in place; it does not fork a competing program.

---

## §1 — Governing specs (the 14-section program theory lives here — do not duplicate)

| Concern | Canonical authority (route here; do not restate) |
|---|---|
| **Program theory — the 14 sections** (Objective, Core Thesis, Non-Goals, Operating Principle, Phases A–E, Book-Selection Standard, Chapter-Quality Standard, Runtime Standard, Acceptance Standard, Fix-First Standard, Deliverables, Definition of Done, Execution Order) | `docs/specs/PEARL_PRIME_1000_BOOK_BUILD_PROGRAM_V1_SPEC.md` |
| **Wave-1 execution** (roster, subwaves, preconditions, review standard, promote/block) | `docs/specs/PEARL_PRIME_WAVE_1_EXECUTION_SPEC.md` |
| **Source-of-truth analysis inputs** | `artifacts/analysis/PEARL_PRIME_THESIS_PLAN_VIEW_IDEA.md`; `artifacts/analysis/pearl_prime_analysis/pearl_prime_atom_analysis_pack.md` (+ `atom_inventory.json`, `atom_inventory_pairs.csv`, `atom_sparse_units.csv`, `bestseller_gap_map.{csv,json}`); `artifacts/analysis/pearl_prime_priorities/{best_current_100_build_list,fix_first_roadmap}.{md,csv,json}` |

The governing principle, verbatim from the thesis and the V1 spec, is:

> **focus → repair → deepen → validate → scale** — not **widen → fallback → gate-pass → declare done.**
> Scale from proven strong clusters, not from total-catalog ambition.

---

## §2 — Craft + chapter authority (Chapter-Quality Standard §7 routes here)

The chapter-quality bar (Orient → Name → Turn → Give → Pull; one dominant chapter role; one arguable thesis; one coherent emotional movement; one payoff; never a stitched slot checklist) is owned by:

- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` — the writing-craft overlay (declares the canonical CLI at §570–577; the four-piece-chord authority).
- **Dwell-beat craft gate + one-author/wrapper voice doctrine — PR #1527 (MERGED).** Integration-pacing (a REFLECTION / somatic-pause beat after each teaching beat *before* the next; a cap on new insights per section) is the operator's #1 recurring craft concern. The program treats integration-pacing as a first-class chapter requirement and routes its definition to #1527; it does **not** redefine the dwell-beat gate here. (Pinning integration-pacing as a named durable rule inside the overlay spec is tracked as an overlay amendment, out of scope for this program doc, which references it.)
- `phoenix_v4/planning/chapter_planner.py` — §7 chapter architecture (the planner; legacy-uniform fallback is the drift the program reduces, not a path it endorses).

Per the chapter-standard: **atom completeness must not stand in for authored cohesion.** A book whose slots are 100% filled is not thereby bestseller-grade; cohesion is the human bar (§7 below).

---

## §3 — Live quality gates (Acceptance Standard §9 uses THESE — build no new gate)

Machine acceptance = passing the existing gate stack. The program adds no gate. The §9 gates are:

| Gate | Canonical file | Role |
|---|---|---|
| Chapter flow | `phoenix_v4/quality/chapter_flow_gate.py` | per-chapter forward-motion / middle-not-flatten |
| Book quality | `phoenix_v4/quality/book_quality_gate.py` | book-level structural pass |
| Scene anti-genericity | `phoenix_v4/qa/scene_anti_genericity_gate.py` | SCENE originality (named-character, non-generic) |
| Bestseller craft / editor | `phoenix_v4/qa/bestseller_editor.py`, `phoenix_v4/quality/bestseller_craft_gate.py` | craft + editorial scoring |
| EI v2 (rigorous-evaluation track) | `phoenix_v4/quality/ei_v2/` | emotional-intelligence scorer; the #1516/#1517 strengthening + the EI P0 build (#1578) are the deepening of this track |
| Register / ship-readiness (spine-default) | `phoenix_v4/quality/register_gate.py`, `phoenix_v4/quality/ship_readiness_aggregator.py` | wired by PR #1536; the strict stack production books currently HARD_FAIL (see §6) |

**Machine pass = structural acceptance ONLY.** No agent self-clears the bestseller bar. Gate-green is necessary, never sufficient. The bestseller gate is the human/editorial review of §7. This is the load-bearing caveat of the whole program (V1 spec §9; analysis pack P5).

---

## §4 — Runtime (Runtime Standard §8 / Phase D route here)

- **Canonical bestseller CLI** (`docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` §570–577; registry `pearl_prime_bestseller_cli`):
  spine mode + a strict quality profile + `--exercise-journeys`. Without the chord, output silently degrades to `library_34` / `practice_library` generic content.
- **Spine-default enabler — PR #1536 (OPEN):** `scripts/run_pipeline.py` `--pipeline-mode` default registry→spine + `register_gate` wiring + `ship_readiness_aggregator`. This is Phase D's enabler — it makes spine+gates the production default.
- **10-book pilot runner — `scripts/pilot/run_spine_pipeline.py`** (standalone spine → KnobApply → BeatmapCompile → EnrichmentSelect → compose; args `--topic --persona --teacher --format --seed --output-dir`). Output validated by `scripts/qa/validate_spine_output.py`.
- **Fallback reporting (§8):** every production run must surface fallback share by slot/chapter, source-share (teacher/persona/registry/practice/fallback), and degraded-canonical parsing cases. A run that silently leans on fallback is **degraded** even when `book.txt` renders.

---

## §5 — TOP-100 ACTIVE BUILD SLATE (the slate the program maintains)

The canonical active slate is `artifacts/analysis/pearl_prime_priorities/best_current_100_build_list.{md,csv,json}` (100 rows; readiness bands: **47 `build_now` + 53 `build_soon`**). It is ranked by current atom-bank readiness (STORY/SCENE depth, slot coverage, locale overlays, low sparse-unit debt) with a diversity cap applied first — **not** by external sales/trend demand. Persona spread across the 100: gen_alpha_students, gen_z_professionals, corporate_managers, gen_x_sandwich, tech_finance_burnout, working_parents, entrepreneurs, first_responders (9 each), educators, nyc_executives (8), healthcare_rns (7), millennial_women_professionals (5). This program maintains that slate; it does not replace it.

---

## §6 — WAVE 1 = the strongest 25 (diversity-balanced, §6-eligible)

**Eligibility (program V1 §6, applied as a hard filter on the slate):** `readiness_band == build_now` **AND** `scene_blocks >= 30` (healthy SCENE depth) **AND** `sparse_unit_count == 0` (**no hard dependency on an unrepaired glue bank**). Healthy STORY depth (=20) holds across the eligible pool. **Diversity caps:** ≤4 books per persona, ≤5 per topic (soft) — no single persona or topic dominates; repeatable families preferred over lucky one-offs.

**Eligible pool:** 45 of the 100 slate rows. **Diversity result:** 25 books, **8 personas**, **8 topics**, max persona share **4/25 (16%)**.

> **Correction vs the draft Wave-1 (important):** the draft execution roster included `gen_z_professionals / anxiety`, which carries **sparse_unit_count = 1** in `PERMISSION_GRANT` — a dependency on an unrepaired glue bank. Per §6 it is **excluded from Wave 1 and the pilot** and deferred until fix-first item #19 (the `gen_z_professionals/anxiety` PERMISSION_GRANT pair-repair) lands. This is the §6 rule doing its job: Wave 1 carries zero unrepaired-glue dependencies.

Materialized: `artifacts/analysis/pearl_prime_priorities/program_v1/wave_1_slate.{csv,json}`.

| # | Persona | Topic | Score | STORY | SCENE | sparse | locales | Pilot-10 |
|---:|---|---|---:|---:|---:|---:|---:|:--:|
| 1 | gen_alpha_students | anxiety | 451 | 20 | 30 | 0 | 37 | ● |
| 2 | gen_z_professionals | burnout | 261 | 20 | 30 | 0 | 33 | ● |
| 3 | gen_z_professionals | financial_anxiety | 261 | 20 | 30 | 0 | 33 | ● |
| 4 | gen_z_professionals | imposter_syndrome | 261 | 20 | 30 | 0 | 33 | |
| 5 | corporate_managers | burnout | 251 | 20 | 30 | 0 | 27 | ● |
| 6 | corporate_managers | financial_anxiety | 251 | 20 | 30 | 0 | 22 | ● |
| 7 | corporate_managers | imposter_syndrome | 251 | 20 | 30 | 0 | 22 | |
| 8 | corporate_managers | social_anxiety | 251 | 20 | 30 | 0 | 22 | |
| 9 | educators | anxiety | 251 | 20 | 30 | 0 | 42 | ● |
| 10 | gen_alpha_students | boundaries | 251 | 20 | 30 | 0 | 37 | ● |
| 11 | gen_alpha_students | burnout | 251 | 20 | 30 | 0 | 37 | |
| 12 | gen_alpha_students | compassion_fatigue | 251 | 20 | 30 | 0 | 37 | |
| 13 | gen_x_sandwich | anxiety | 251 | 20 | 30 | 0 | 22 | ● |
| 14 | gen_x_sandwich | boundaries | 251 | 20 | 30 | 0 | 22 | ● |
| 15 | gen_x_sandwich | burnout | 251 | 20 | 30 | 0 | 22 | |
| 16 | gen_x_sandwich | compassion_fatigue | 251 | 20 | 30 | 0 | 22 | |
| 17 | gen_z_professionals | boundaries | 251 | 20 | 30 | 0 | 32 | |
| 18 | nyc_executives | anxiety | 251 | 20 | 30 | 0 | 38 | ● |
| 19 | tech_finance_burnout | burnout | 251 | 20 | 30 | 0 | 45 | |
| 20 | tech_finance_burnout | financial_anxiety | 251 | 20 | 30 | 0 | 46 | |
| 21 | tech_finance_burnout | imposter_syndrome | 251 | 20 | 30 | 0 | 46 | |
| 22 | tech_finance_burnout | overthinking | 251 | 20 | 30 | 0 | 46 | |
| 23 | working_parents | financial_anxiety | 251 | 20 | 30 | 0 | 32 | |
| 24 | working_parents | imposter_syndrome | 251 | 20 | 30 | 0 | 33 | |
| 25 | working_parents | social_anxiety | 251 | 20 | 30 | 0 | 33 | |

**Persona balance:** gen_alpha_students 4 · gen_z_professionals 4 · corporate_managers 4 · gen_x_sandwich 4 · tech_finance_burnout 4 · working_parents 3 · educators 1 · nyc_executives 1.
**Topic balance:** burnout 5 · anxiety 4 · financial_anxiety 4 · imposter_syndrome 4 · boundaries 3 · social_anxiety 2 · compassion_fatigue 2 · overthinking 1.

---

## §7 — FIX-FIRST RECURRING-BANK REPAIR QUEUE (prioritized)

Prioritized by: **(1) # top-100 books affected → (2) recurrence across topics for one persona → (3) glue-vs-core → (4) near-buildable pair repair.** Recurring persona-slot programs outrank one-off repairs. Source: `fix_first_roadmap.{csv,json}` (30 items). Materialized: `artifacts/analysis/pearl_prime_priorities/program_v1/fix_first_queue.{csv,json}`.

**Phase B — glue banks first (PERMISSION / PIVOT / TAKEAWAY / THREAD):**

| Pri | Program | Lift | Top-100 affected | Topics |
|---:|---|---:|---:|---:|
| 1–4 | **first_responders** / PERMISSION · PIVOT · TAKEAWAY · THREAD | 1216 ea | 9 | 15 |
| 5 | **entrepreneurs** / PERMISSION | 1125 | 8 | 15 |
| 6–9 | **healthcare_rns** / PERMISSION · PIVOT · TAKEAWAY · THREAD | 1042 ea | 7 | 16 |
| 10–12 | **entrepreneurs** / PIVOT · TAKEAWAY · THREAD | 1020 ea | 7 | 14 |
| 13–16 | **millennial_women_professionals** / PERMISSION · PIVOT · TAKEAWAY · THREAD | 866 ea | 5 | 16 |
| 17 | gen_z_professionals / PERMISSION_GRANT | 423 | 1 | 1 |

**Phase C — STORY/SCENE depth for the strongest families:**

| Pri | Program | Lift | Top-100 affected | Topics |
|---:|---|---:|---:|---:|
| 18 | gen_z_student / SCENE | 381 | 0 | 15 |

**Near-buildable pair repairs (PERMISSION|PIVOT|TAKEAWAY|THREAD, lift 283 ea; #19 = 319):** #19 gen_z_professionals/anxiety (PERMISSION_GRANT) — **this unblocks the Wave-1-deferred book**; #20–26 entrepreneurs/{burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing}; #27–30 first_responders/{burnout, compassion_fatigue, courage, depression}.

**Lead repair programs (the operator's named priority):** glue banks PERMISSION / PIVOT / TAKEAWAY / THREAD across **first_responders → entrepreneurs → healthcare_rns** first (Phase B), then STORY/SCENE depth for top families (Phase C). One glue-bank repair program strengthens many top-100 books at once — that is why it leads.

**Tier policy for the repairs:** atom authoring + glue-bank repairs are **Pearl_Writer / Pearl_Editor = Claude subagents (Tier 1, operator-present)** per CLAUDE.md. The slate personas (first_responders / entrepreneurs / healthcare_rns) are **en-US**. **No paid LLM API.**

---

## §8 — 10-BOOK PILOT SET + RUN PLAN

**Pilot-10** = the strongest 10 of the §6-clean Wave-1 (persona cap 2 so the pilot is itself diversity-spread: 6 personas). Bar = the §7 chapter-quality standard. Materialized: `artifacts/analysis/pearl_prime_priorities/program_v1/pilot_10_set.json`.

| # | Persona | Topic | Score |
|---:|---|---|---:|
| 1 | gen_alpha_students | anxiety | 451 |
| 2 | gen_z_professionals | burnout | 261 |
| 3 | gen_z_professionals | financial_anxiety | 261 |
| 4 | corporate_managers | burnout | 251 |
| 5 | corporate_managers | financial_anxiety | 251 |
| 6 | educators | anxiety | 251 |
| 7 | gen_alpha_students | boundaries | 251 |
| 8 | gen_x_sandwich | anxiety | 251 |
| 9 | gen_x_sandwich | boundaries | 251 |
| 10 | nyc_executives | anxiety | 251 |

### PILOT RUN PLAN (a plan — not executed in the authoring session)

> The pilot **RUN PLAN is a document.** Authoring this program did not build any book. The build is the gated fan-out (§9), dispatched only after operator review of Wave 1 + the fix-first queue.

1. **Per book — canonical spine-mode CLI.** Use the overlay §570–577 chord. The pilot tool is `scripts/pilot/run_spine_pipeline.py`:
   ```bash
   PYTHONPATH=. python3 scripts/pilot/run_spine_pipeline.py \
     --persona <persona> --topic <topic> --teacher ahjan \
     --format standard_book --seed pilot_v1 \
     --output-dir artifacts/pearl_prime/pilot_10/<NN>_<persona>__<topic>
   ```
   (Equivalently, the full pipeline at production grade: `scripts/run_pipeline.py --pipeline-mode spine --quality-profile production --exercise-journeys --persona <p> --topic <t> --arc <arc.yaml> --locale en-US --render-book --render-dir <out>`.)
2. **STRICT gates, honest fail surfacing (§3).** Run the full strict stack. **Do NOT draft-mask.** Production books are expected to HARD_FAIL the strict stack today (register_gate HARD_FAIL, ei_v2 ≈0.53, chapter_flow partial; `book_pass` fails the word ceiling >20000 even though `book.txt` renders). **The HARD_FAILs are the signal, not a bug to hide** — they are the concrete evidence that "books at trade-pub register is the real frontier." Only *tests* of the entrypoint use `--quality-profile=draft`; the pilot does not.
3. **Fallback report (§8).** For every book record: fallback share by slot and chapter; source-share (teacher / persona / registry / practice / fallback); degraded-canonical parsing cases; chapter-level flow/craft/editorial failures. Validate spine output with `scripts/qa/validate_spine_output.py`.
4. **Artifacts.** Preserve `book.txt` + every gate report per book under `artifacts/pearl_prime/pilot_10/<NN>_…/`, plus a `run_summary` (per-book exit code + scores) and cluster-level failure notes.
5. **No promotion without human review (§9 / V1 §9).** Gate output is structural; promotion is the operator's editorial call.

---

## §9 — GATED FAN-OUT PLAN (define here; dispatch on operator GO — do NOT execute)

The repair (Phase B) and the 10-book pilot BUILD are a **gated fan-out** the operator dispatches **after** reviewing Wave 1 + the fix-first queue produced by this session. Each child workstream is listed with inputs/outputs so it can be fired on the operator's GO.

**Stage 1 — Phase-B glue-bank repair (parallel child-ws, one per glue-bank × persona program; Pearl_Editor / Pearl_Writer, Tier 1, en-US):**

| Child-ws id | Repair program | Inputs | Outputs |
|---|---|---|---|
| `ws_glue_first_responders_PERMISSION` | first_responders / PERMISSION (15 topics) | fix_first_queue #1; `atoms/first_responders/<topic>/` | block-structured PERMISSION CANONICAL atoms across 15 topics |
| `ws_glue_first_responders_PIVOT` | first_responders / PIVOT | #2 | PIVOT atoms ×15 |
| `ws_glue_first_responders_TAKEAWAY` | first_responders / TAKEAWAY | #3 | TAKEAWAY atoms ×15 |
| `ws_glue_first_responders_THREAD` | first_responders / THREAD | #4 | THREAD atoms ×15 |
| `ws_glue_entrepreneurs_PERMISSION` | entrepreneurs / PERMISSION | #5 | PERMISSION atoms ×15 |
| `ws_glue_healthcare_rns_PERMISSION` | healthcare_rns / PERMISSION | #6 | PERMISSION atoms ×16 |
| `ws_glue_healthcare_rns_PIVOT` | healthcare_rns / PIVOT | #7 | PIVOT atoms ×16 |
| `ws_glue_healthcare_rns_TAKEAWAY` | healthcare_rns / TAKEAWAY | #8 | TAKEAWAY atoms ×16 |
| `ws_glue_healthcare_rns_THREAD` | healthcare_rns / THREAD | #9 | THREAD atoms ×16 |
| `ws_glue_entrepreneurs_PIVOT_TAKEAWAY_THREAD` | entrepreneurs / PIVOT·TAKEAWAY·THREAD | #10–12 | 3 glue banks ×14 |
| `ws_glue_millennial_women_PPTT` | millennial_women_professionals / PERMISSION·PIVOT·TAKEAWAY·THREAD | #13–16 | 4 glue banks ×16 |

(Phase C — `ws_depth_gen_z_student_SCENE` (#18) + STORY/SCENE deepening for top families — follows Phase B on the same gated cadence.)

**Stage 2 — 10-book pilot BUILD (one child-ws):** `ws_pilot_10_build` — Inputs: `pilot_10_set.json`, §8 run plan, the canonical spine CLI. Outputs: 10 rendered books + strict-gate reports + fallback report + run_summary. Runs STRICT gates, honest fail surfacing.

**Stage 3 — machine gates → operator HUMAN review (§3 / V1 §9):** the §3 gate stack reports structural pass/fail; the operator judges shelf-quality cohesion (chapter progression real? stories vivid? repetition controlled? middle not flat? endings land without generic uplift?).

**Stage 4 — promote / block per cluster:** promote a cluster only when the majority of its books pass gates **and** human review confirms real cohesion; block when chapters repeatedly feel stitched/flat, the same weak-bank pattern recurs, or it passes gates but fails shelf-quality.

**Then:** Wave-1 25-book completion → 100-slate → scale toward 1,000 — each wave gated on the prior wave's human review (V1 §12 Definition of Done).

---

## §10 — Human review requirement (the bestseller gate no agent self-clears)

A machine-gate pass is **structural acceptance only.** Final acceptance for any serious bestseller candidate requires human/editorial confirmation that chapter progression feels real, stories are vivid, repetition is controlled, the middle does not flatten, and endings land without generic uplift. **The program never scales or widens before the pilot's human review.** Atom-completeness never substitutes for authored cohesion.

---

## §11 — This-session boundary (focus + plan; no build)

This session authored the program operating-system + materialized the deliverables and **built nothing**: no book, no bank repair, no fan-out execution, no pilot run. The half-executed render scratch that pre-existed on disk (`artifacts/wave1a_proof_set/`) is **not** part of this program's deliverables and is intentionally not promoted — the pilot is a documented RUN PLAN the operator dispatches after review.

## §12 — Definition of done (this program)

Done enough to scale only when: the 10-book pilot is strong under human review; the 25-book Wave 1 holds quality without collapse; the 100-slate is built mainly from strong clusters (not fallback illusion); recurring glue banks are repaired in priority personas; STORY/SCENE depth is strong in top families; fallback reliance is measured and controlled. (Full DoD: V1 spec §12.)

---

## Bottom line

Pearl Prime reaches 1,000 cohesive books **by scaling from proven strong clusters** — strong source banks + chapter architecture + continuity glue + reduced fallback + corpus-level human validation — gated wave by wave. This document is the operating system that keeps that discipline; the program theory it serves lives in `PEARL_PRIME_1000_BOOK_BUILD_PROGRAM_V1_SPEC.md`.
