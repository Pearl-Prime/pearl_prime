# Pilot-10 Set, Run Plan, and Gated Fan-Out

**Governed by:** `docs/specs/PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM.md` §8–§9 + `PEARL_PRIME_WAVE_1_EXECUTION_SPEC.md` §4.
**Machine-readable:** `pilot_10_set.json` (this dir).

> **This is a PLAN, not an execution.** The authoring session built nothing — no book, no bank repair, no fan-out. The pilot build + Phase-B repairs are the gated fan-out the operator dispatches **after** reviewing Wave 1 + the fix-first queue.

## 10-book pilot set

Strongest 10 of the §6-clean Wave-1, persona-capped at 2 (6 personas). Bar = the §7 chapter-quality standard.

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

## Pilot run plan

1. **Canonical spine-mode CLI per book** — `scripts/pilot/run_spine_pipeline.py --persona <p> --topic <t> --teacher ahjan --format standard_book --seed pilot_v1 --output-dir artifacts/pearl_prime/pilot_10/<NN>_<p>__<t>` (or the full pipeline at production grade per overlay §570–577).
2. **STRICT gates, honest fail surfacing** — run the full strict stack (§3). Do NOT draft-mask. Production books are expected to HARD_FAIL today (register_gate HARD_FAIL, ei_v2 ≈0.53, chapter_flow partial, `book_pass` >20000-word ceiling) — the HARD_FAILs are the signal that trade-pub register is the real frontier. Only tests use `--quality-profile=draft`.
3. **Fallback report (§8)** — per book: fallback share by slot/chapter; source-share (teacher/persona/registry/practice/fallback); degraded-canonical parsing cases; chapter-level flow/craft/editorial failures. Validate with `scripts/qa/validate_spine_output.py`.
4. **Artifacts** — preserve `book.txt` + every gate report per book, plus a `run_summary` and cluster-level failure notes.
5. **No promotion without human review** — gate output is structural; promotion is the operator's editorial call (§10).

## Gated fan-out (dispatch on operator GO)

### Stage 1 — Phase-B glue-bank repair (parallel child-ws; Pearl_Editor / Pearl_Writer, Tier 1, en-US)

| Child-ws id | Repair program | Inputs | Outputs |
|---|---|---|---|
| ws_glue_first_responders_PERMISSION | first_responders / PERMISSION (15 topics) | fix_first #1; `atoms/first_responders/<topic>/` | block-structured PERMISSION CANONICAL ×15 |
| ws_glue_first_responders_PIVOT | first_responders / PIVOT | #2 | PIVOT ×15 |
| ws_glue_first_responders_TAKEAWAY | first_responders / TAKEAWAY | #3 | TAKEAWAY ×15 |
| ws_glue_first_responders_THREAD | first_responders / THREAD | #4 | THREAD ×15 |
| ws_glue_entrepreneurs_PERMISSION | entrepreneurs / PERMISSION | #5 | PERMISSION ×15 |
| ws_glue_healthcare_rns_PERMISSION | healthcare_rns / PERMISSION | #6 | PERMISSION ×16 |
| ws_glue_healthcare_rns_PIVOT | healthcare_rns / PIVOT | #7 | PIVOT ×16 |
| ws_glue_healthcare_rns_TAKEAWAY | healthcare_rns / TAKEAWAY | #8 | TAKEAWAY ×16 |
| ws_glue_healthcare_rns_THREAD | healthcare_rns / THREAD | #9 | THREAD ×16 |
| ws_glue_entrepreneurs_PIVOT_TAKEAWAY_THREAD | entrepreneurs / PIVOT·TAKEAWAY·THREAD | #10–12 | 3 glue banks ×14 |
| ws_glue_millennial_women_PPTT | millennial_women_professionals / PERMISSION·PIVOT·TAKEAWAY·THREAD | #13–16 | 4 glue banks ×16 |

(Phase C — `ws_depth_gen_z_student_SCENE` (#18) + STORY/SCENE deepening for top families — follows Phase B on the same gated cadence.)

### Stage 2 — 10-book pilot BUILD

`ws_pilot_10_build` — Inputs: `pilot_10_set.json` + the §8 run plan + the canonical spine CLI. Outputs: 10 rendered books + strict-gate reports + fallback report + run_summary. STRICT gates, honest fail surfacing.

### Stage 3 — machine gates → operator HUMAN review

§3 gate stack reports structural pass/fail; operator judges shelf-quality cohesion (chapter progression real? stories vivid? repetition controlled? middle not flat? endings land without generic uplift?).

### Stage 4 — promote / block per cluster

Promote a cluster when the majority of its books pass gates AND human review confirms real cohesion; block when chapters repeatedly feel stitched/flat, the same weak-bank pattern recurs, or it passes gates but fails shelf-quality.

### Then

Wave-1 25-book completion → 100-slate → scale toward 1,000 — each wave gated on the prior wave's human review.
