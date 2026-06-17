# EI v2 — Enhancement Roadmap: Scorer → Synthesis Engine

**Author:** Pearl_Architect · **Date:** 2026-06-11 · **From:** `EI_V2_CURRENT_STATE_AUDIT.md` · **To:** `EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md`

Prioritized P0→P2. Each item: **what to build · which agent · depends on · evidence anchor · exit criteria**. Sequencing is gated (right column of §4) — scale work (P2) does **not** start until its P0/P1 dependencies are merged (per the validation-before-scaling discipline). The cap-entry ratification rides a **serial lane** on `PEARL_ARCHITECT_STATE.md` and is explicitly out of scope for the audit session.

---

## P0 — Foundations everything downstream depends on

Without these two, every optimizer optimizes the wrong thing. **Build these first.**

### P0.1 — Explicit multi-objective fitness (THE highest-leverage piece)
- **Build:** `config/quality/ei_v2_fitness.yaml` (declares `T`, `E`, `Φ` sub-terms, the fidelity floor `τ_Φ`, the operator dial, the gold-holdout) + a **fitness evaluator** that returns the 3-vector `(T, E, Φ)` instead of one scalar. Reuse existing scored dimensions (somatic_precision, engagement, emotion_arc, TTS) as `T`/`E` inputs; `Φ` waits on P0.2's CEG.
- **Agent:** Pearl_Dev (evaluator) + Pearl_Research (sub-term definitions).
- **Depends on:** P0.2 for the `Φ` channel only; `T`/`E` channels can land first.
- **Evidence:** audit §4 (scorer/learner optimize *different* dimension sets — the incoherence a single explicit objective fixes); SOTA Topic 2 (Hu 2023 scalarization limits; MORLAIF; Gao overoptimization).
- **Exit:** evaluator emits `(T,E,Φ)` for a sample book; floor + dial unit-tested; gold-holdout wired; **zero paid-LLM calls** (`audit_llm_callers.py` clean).

### P0.2 — Spiritual-root synthesis → Composite Essence Graph (the heart)
- **Build:** the 3-stage pipeline (local contrastive embed → BERTopic cluster → cross-document coref merge → **Tier-1 attended Claude** names + provenances each root) producing `SOURCE_OF_TRUTH/composite_essence/ceg.json` + `provenance.jsonl`, with `convergence_strength` + `saturation` per root.
- **Agent:** Pearl_Research (pipeline + naming under operator review) + Pearl_Dev (the embed/cluster/merge code).
- **Depends on:** nothing (corpus exists: 15 teacher banks).
- **Evidence:** audit §3 Stage 1 (composite is hand-prose, not engineered; not wired to scorer); SOTA Topic 1 (SimCSE, BERTopic, cross-doc coref, De Paoli validity).
- **Exit:** CEG covers the 15 composite-doctrine topics; each root provenanced to ≥2 teachers; **recovers the hand-authored `composite_doctrine/` as a validation oracle** (≥ target overlap); saturation ≥ threshold; human spot-check signed off.

### P0.3 — *(gated, post-settle)* Ratify the EI-v2-strengthened cap
- **Build:** one cap entry in `PEARL_ARCHITECT_STATE.md` registering the strengthened architecture as canonical.
- **Agent:** Pearl_Architect.
- **Depends on:** operator approves P0.1+P0.2 design; cascade-settle ping (hot-file serial lane).
- **Exit:** single append on the serial lane; no stampede (one writer).

---

## P1 — The right optimizers + validation (after P0 merges)

### P1.1 — Retire the EMA learner; adopt qNEHVI Bayesian optimization for the weights
- **Build:** replace `phoenix_v4/quality/ei_v2/learner.py` (EMA) with a noise-aware multi-objective BO over the ≤8 continuous fitness knobs; state in `artifacts/ei_v2/bo_state.json`.
- **Agent:** Pearl_Dev.
- **Depends on:** P0.1 (the knobs to tune).
- **Evidence:** audit §4 (EMA on 45/7 records; sample-starved); SOTA Topic 3 (qEHVI/qNEHVI sample-efficiency on expensive noisy evals).
- **Exit:** BO reaches the EMA's quality in ≤ tens of evals on replayed feedback; deterministic seed; fail-open.

### P1.2 — GA / memetic atom selection + sequencing in the book planner
- **Build:** NSGA-II (with local swap/insert refinement) over atom subset+order for one book, optimizing `(T,E)` s.t. `Φ≥τ_Φ`; wired into `chapter_planner`/book planner **behind a flag**; emits a Pareto menu.
- **Agent:** Pearl_Dev.
- **Depends on:** P0.1 (fitness), P0.2 (CEG for Φ), the delivery brief (P1.4).
- **Evidence:** audit §3 Stage 4 (no GA; planner not wired); SOTA Topic 3 (NSGA-II; memetic for sequence-dependent dwell/integration costs).
- **Exit:** flag-gated run produces an operator-reviewable Pareto menu for a sample title; integration/dwell-beat term measurably active; reversible (flag off = today's path).

### P1.3 — Validation layer (validity cards gate optimizer trust)
- **Build:** construct + predictive + stability validity cards for personas and somatic heuristics; the optimizer may weight a target only if its card passes.
- **Agent:** Pearl_Research.
- **Depends on:** P0.1 (defines what "trust" means in the fitness).
- **Evidence:** audit §3 Stages 2–3 (RCG-013/007/022 — unvalidated); SOTA Topic 5 (Salminen predictive personas; Melhart annotator reliability; De Paoli saturation).
- **Exit:** at least the active en-US personas + the live somatic gate carry validity cards; failing targets demoted to generation-only (no optimizer weight).

### P1.4 — Targeting model (`delivery_brief` assembly)
- **Build:** `delivery_brief(topic, persona, locale) = CEG ⊗ persona_model ⊗ somatic_delivery` as the GA's coverage spec.
- **Agent:** Pearl_Dev.
- **Depends on:** P0.2 (CEG), P1.3 (validated persona/somatic).
- **Exit:** briefs generated for the golden-set topics; consumed by P1.2's GA.

---

## P2 — Scale + close the loop (after P1 merges; gated on validation)

### P2.1 — GA for the catalog portfolio
- **Build:** NSGA-II over catalog configs for CEG-root coverage × engagement diversity under the fidelity floor; wired into `catalog_planner` behind a flag.
- **Agent:** Pearl_Dev. **Depends on:** P0.1, P0.2, P1.2.
- **Exit:** portfolio Pareto menu for a brand; coverage report vs. the 800-high-confidence-configs target.

### P2.2 — Closed feedback loop (bandit + OPE + guards)
- **Build:** `world_signal.jsonl` tap; Thompson-sampling plan policy (persona = context); off-policy evaluator to validate candidate fitness before ship; exploration-budget + diversity guard; proxy-vs-gold monitor.
- **Agent:** Pearl_Dev + Pearl_Research. **Depends on:** P0.1, P1.1; a real-signal feed (open question #1).
- **Evidence:** SOTA Topic 4 (RLAIF; contextual bandits; counterfactual OLTR; Jiang/Chaney degeneration; Gao overoptimization).
- **Exit:** loop updates `T`/`E` outcome terms from logged signal *through* OPE (not naively); both guards firing in tests.

### P2.3 — RLAIF doctrinal-fidelity rubric (Tier-2, unattended)
- **Build:** a written doctrinal-fidelity "constitution"; Gemma/Qwen (Ollama, Pearl Star) generate fidelity-preference data to feed the loop between human reviews.
- **Agent:** Pearl_Research. **Depends on:** P0.2 (CEG = the rubric's ground truth), P2.2.
- **Exit:** Tier-2 preference batch generated unattended; **no paid API**; sampled against human review.

### P2.4 — Research backfill feeding validation (RCG remediation)
- **Build:** the psychological-research → persona and somatic-research → heuristic derivations the audit found missing (RCG-013/004/008/009/007/022), with citations.
- **Agent:** Pearl_Research. **Depends on:** can run in parallel with P0/P1; feeds P1.3.
- **Exit:** citation bundles under `artifacts/research/citations/`; personas/somatic heuristics move from "hand-authored" to "research-grounded + validated."

---

## 4. Sequencing & gates

| Wave | Items | Gate to start |
|---|---|---|
| **Wave A (P0)** | P0.1 (T/E) ∥ P0.2 (CEG) | none — start now on operator approval |
| **ratify** | P0.3 | operator approves A; serial lane on `PEARL_ARCHITECT_STATE.md` (one writer, no stampede) |
| **Wave B (P1)** | P1.1, P1.2, P1.3, P1.4 | Wave A **merged** (don't stack on unmerged PRs) |
| **Wave C (P2)** | P2.1, P2.2, P2.3, P2.4 | Wave B merged; real-signal feed decided (open Q#1); validation (P1.3) passing |

**Cross-cutting (every PR):** `audit_llm_callers.py` clean (no paid LLM in runtime); flag-gated + reversible; bestseller_editor remains the post-render safety gate; operator reviews each Pareto menu before any plan ships.

---

## 5. The first concrete step

If the operator approves one thing today, make it **P0.1 + P0.2 in parallel**: the **explicit multi-objective fitness** (so the optimizer has a true target) and the **CEG synthesis** (so `Φ` and the targeting model have a spine). Everything else is downstream of these two. P0.1 alone already fixes the audit's sharpest finding — that today's scorer and its learner optimize *different dimension sets* with no fidelity objective at all.
