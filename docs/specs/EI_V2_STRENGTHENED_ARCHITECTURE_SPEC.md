# EI v2 — Strengthened Architecture Spec: The Synthesis Engine

**Status:** DESIGN (proposed) · **Author:** Pearl_Architect · **Date:** 2026-06-11
**Supersedes nothing yet** — this is the *target*. Ratification of the EI-v2-strengthened cap entry in `PEARL_ARCHITECT_STATE.md` is a **gated follow-up** (see roadmap), deliberately NOT done in this session to keep it parallel-safe.
**Reads:** `EI_V2_CURRENT_STATE_AUDIT.md` (where we are) · `EI_V2_SOTA_RESEARCH_NOTES.md` (the citation backbone) · `EI_V2_ENHANCEMENT_ROADMAP.md` (how to get there)

---

## 1. Purpose

Make EI v2 *true to its name*. Today it is a post-render editorial **scorer** with an EMA weight-nudge (see audit §4). The operator's vision is a **synthesis engine**: take all teachers' teachings, extract their **spiritual-root commonalities** into a composite essence, aim that essence at a reader's suffering through validated persona + somatic targeting, and use a **real optimizer against an explicit multi-objective fitness** to drive the catalog and book planners — getting **stronger from the world** over time.

This spec defines that engine as four corrected stages plus six strengtheners, each grounded in cited SOTA and wired concretely into the existing planner/atom system. **The single highest-leverage piece is the explicit multi-objective fitness (§6); the heart is the spiritual-root synthesis (§7).**

---

## 2. Design principles (from the research)

1. **Separate the objectives; never pre-collapse them.** A fixed linear weighted-sum provably cannot reach non-convex trade-offs and invites objective collapse / reward hacking (Hu 2023; Gao 2023; MORLAIF 2024). Keep therapeutic × engagement × fidelity as three channels.
2. **Right optimizer per sub-problem.** Evolutionary/memetic search for the *combinatorial* atom selection+sequencing; noise-aware Bayesian optimization (qNEHVI) for the *handful of continuous weights* (Deb 2002; Daulton 2020/2021).
3. **Fidelity is a floor, not a summand.** Protect spiritual-root fidelity as a constraint the optimizer may not average away (projection/Chebyshev scalarization).
4. **Trust nothing unvalidated.** A persona or somatic heuristic may drive the optimizer only after passing construct + predictive validity (Salminen 2023; Melhart 2023). Encode affective effects as uncertainty-bearing priors, not precise multipliers.
5. **Close the loop safely.** Learn from real signal as a contextual bandit with off-policy evaluation, and instrument the two failure modes — reward overoptimization (Gao) and degenerate feedback loops (Jiang 2019; Chaney 2018).
6. **Tier-correct by construction.** Synthesis embeddings/clustering and runtime scoring are **local / Tier-2** (Pearl Star, Ollama Gemma/Qwen); the *naming* of root nodes and design review are **Tier-1 attended Claude**. **No paid LLM API in runtime** (CLAUDE.md).

---

## 3. The corrected four-stage pipeline

```
  ┌──────────────────────────────────────────────────────────────────────────────────┐
  │ STAGE 1  SYNTHESIS                                                                  │
  │  teacher_banks/ (15 teachers) ──embed──cluster──coref-merge──name+provenance──▶     │
  │                                          Composite Essence Graph (CEG)              │
  │                                          [the spiritual-root spine]                 │
  └───────────────┬──────────────────────────────────────────────────────────────────┘
                  │
  ┌───────────────▼─────────────┐   ┌──────────────────────────┐   ┌────────────────────┐
  │ STAGE 2  PERSONA MODELS      │   │ STAGE 3  SOMATIC          │   │ STAGE 1b  ENGAGEMENT│
  │  psych research → personas   │   │  somatic research →       │   │  #1509 bestseller + │
  │  + VALIDATION gate (§9)      │   │  heuristics + VALIDATION   │   │  integration/dwell  │
  └───────────────┬─────────────┘   └────────────┬─────────────┘   └─────────┬──────────┘
                  │  TARGETING MODEL (§8): essence × persona × somatic delivery          │
                  └──────────────────────────────┬───────────────────────────┬──────────┘
                                                 ▼                           ▼
                          ┌───────────── MULTI-OBJECTIVE FITNESS (§6) ───────────────┐
                          │  f = ( therapeutic , engagement , fidelity[floor] )       │
                          └───────────┬───────────────────────────────┬─────────────┘
                                      │ GA / NSGA-II (combinatorial)   │ qNEHVI BO (weights)
                                      ▼                                ▼
                          CATALOG PLANNER (portfolio)        BOOK PLANNER (atom select+sequence)
                                      │                                │
                                      ▼                                ▼
                              render ──▶ bestseller_editor (EVAL gate + feedback tap, §10)
                                      │
                          ┌───────────▼───────────── CLOSED LOOP (§8b/§... ) ───────────┐
                          │  books out → reviews/sales/engagement → OPE → fitness update │
                          │  → BO retune → GA re-plan          (guards: Gao / Jiang)     │
                          └─────────────────────────────────────────────────────────────┘
```

The corrections vs. today: Stage 1 becomes an **engineered synthesis** producing a structured CEG (not hand-prose); Stages 2–3 gain **validation gates**; Stage 4 becomes **two optimizers against an explicit multi-objective fitness wired into the planners** (not an EMA re-ranker at the editorial gate); and a **closed loop** is added.

---

## 4. Data artifacts (the new contracts)

| Artifact | Path (proposed) | Produced by | Tier |
|---|---|---|---|
| **Composite Essence Graph (CEG)** | `SOURCE_OF_TRUTH/composite_essence/ceg.json` | synthesis pipeline | local embed/cluster + Tier-1 naming |
| Root-node provenance map | `SOURCE_OF_TRUTH/composite_essence/provenance.jsonl` | synthesis pipeline | local |
| Persona model + validity card | `config/catalog_planning/personas/<id>.yaml` + `..._validity.json` | persona derivation + validation | research + local |
| Somatic heuristic + validity card | `SOURCE_OF_TRUTH/exercises_v4/heuristics/<id>.yaml` + `..._validity.json` | somatic derivation + validation | research + local |
| Fitness spec | `config/quality/ei_v2_fitness.yaml` | this spec | n/a (config) |
| Learned weights (replaces EMA) | `artifacts/ei_v2/bo_state.json` | qNEHVI BO | local |
| Plan candidates / Pareto set | `artifacts/ei_v2/pareto/<scope>_<ts>.json` | GA | local |
| Real-world signal log | `artifacts/ei_v2/world_signal.jsonl` | feedback tap | n/a |

---

## 5. The Composite Essence Graph (CEG) — the structured spine

A typed graph that makes "spiritual-root fidelity" *measurable*:

```jsonc
// ceg.json (sketch)
{
  "roots": [
    {
      "id": "root.anxiety_is_information",
      "name": "Anxiety is information, not malfunction",
      "embedding": [/* centroid of merged cluster */],
      "teacher_instantiations": [
        {"teacher": "miki", "atom": "STORY_…", "quote": "…", "weight": 0.9},
        {"teacher": "ra",   "atom": "DOCTRINE_…", "quote": "…", "weight": 0.7}
      ],
      "somatic_affordances": ["exercise.breath_regulation", "exercise.body_awareness_scan"],
      "topics": ["anxiety", "overthinking"],
      "saturation": 0.82,           // De Paoli stability metric across teachers
      "convergence_strength": 0.74  // share of teachers that point at this root
    }
  ],
  "edges": [ /* root↔root relations: prerequisite, deepens, contrasts */ ]
}
```

`convergence_strength` and `teacher_instantiations` are precisely the operator's "spiritual root commonalities," now queryable and provenanced — a book's **fidelity** can be scored as *how well its selected atoms cover and align to the CEG roots it claims to teach*.

---

## 6. STRENGTHENER 1 — Explicit multi-objective fitness *(highest leverage)*

Replace the single scalar composite (audit §4) with a **3-vector**, evaluated per plan (book-level and catalog-level):

```
F(plan) = ( T(plan),  E(plan),  Φ(plan) )
```

### 6.1 Therapeutic efficacy — `T(plan)`
A proxy assembled from **validated** heuristics (§9), refined by real outcomes (§8b):
- `somatic_precision` gate satisfaction ([config:126](config/quality/ei_v2_config.yaml#L126)) — density + placement of body-based atoms.
- **Integration / dwell-beat satisfaction** — does the plan give teachings room to *integrate* rather than racing point-to-point? (the operator's #1 craft concern; sibling gate to G1–G6; grounded in the #1509 integration-pacing research). Modeled as a sequence-dependent cost over the atom ordering.
- Teaching↔exercise coherence (each teaching has a somatic affordance delivered).
- Emotion-arc validity ([config:69-74](config/quality/ei_v2_config.yaml#L69)).
- **Outcome term (once loop is live):** held-out completion / self-reported benefit, OPE-estimated.

### 6.2 Reader engagement — `E(plan)`
- Hook density, tension markers, pull-forward ([config:120-123](config/quality/ei_v2_config.yaml#L120)).
- Bestseller beat-order conformance + proven-pattern fit (PR #1509).
- Listen-experience / TTS readability ([config:49-60](config/quality/ei_v2_config.yaml#L49)).
- **Outcome term (loop live):** completion rate, re-engagement, rating — OPE-estimated.

### 6.3 Spiritual-root fidelity — `Φ(plan)` *(new; the system has nothing like this today)*
- **Root coverage:** fraction of the CEG roots the plan claims to teach that are actually instantiated by a selected atom.
- **Alignment:** mean cosine similarity of selected teaching atoms to their CEG root embeddings.
- **Non-contradiction:** no selected atom contradicts a covered root (doctrinal-consistency check against `edges`).
- **Convergence-weighting:** roots with higher `convergence_strength` count more — the book carries what *all* teachers point at.

### 6.4 How they combine — **Pareto, with fidelity as a floor (not a weighted sum)**
- **Hard floor:** plans with `Φ(plan) < τ_Φ` are **infeasible** (constraint, per projection/Chebyshev guidance) — fidelity can never be "bought back" with engagement.
- **Among feasible plans:** keep the **non-dominated (Pareto) set** over `(T, E)` (NSGA-II crowding for diversity). The optimizer returns a *menu*, not one point.
- **Operator dial:** a single `engagement_vs_therapeutic` knob selects along the front at runtime; weight-interpolation (Rewarded Soups) gives a continuous family without re-optimizing.
- **Anti-Goodhart:** hold out a *gold* therapeutic signal; monitor `proxy − gold` divergence (Gao); cap optimization pressure (early-stop / trust-region) when the proxy detaches.

`config/quality/ei_v2_fitness.yaml` declares the sub-terms, the floor τ_Φ, the gold-holdout, and the dial — making the objective **explicit and auditable**, the opposite of today's scorer/learner dimension-set mismatch (audit §4).

---

## 7. STRENGTHENER 2 — Spiritual-root synthesis as a first-class step *(the heart)*

A three-stage pipeline (per SOTA Topic 1), not a single LLM summarization and not hand-prose:

1. **Embed** doctrine at claim granularity with a contrastive sentence encoder (SimCSE-style, **local**).
2. **Cluster** with BERTopic (UMAP→HDBSCAN→c-TF-IDF) to get candidate themes per topic (**local**).
3. **Cross-document coreference merge** — align clusters that are the *same root worn in different vocabulary across teachers* (the step naive clustering misses). This turns 15 parallel taxonomies into one shared-root graph (**local**).
4. **Name + provenance (Tier-1 attended Claude):** Claude *names and articulates* each merged root and writes provenance back to source passages. Every LLM-asserted root is a **hypothesis** validated by cluster coherence + a **saturation/stability** metric (De Paoli) + human spot-check — never ground truth.

Output = the **CEG (§5)**. This is what makes a book "Pearl Prime" (the composite essence) rather than "teacher X's book," and it is the feedstock for `Φ` (§6.3) and the targeting model (§8). The existing `composite_doctrine/` becomes the **validation oracle** for the engineered CEG (does the engineered root recover the hand-authored composite?), not the production artifact.

---

## 8. STRENGTHENER 3 — Targeting model: universal essence × persona × somatic delivery

Three composable layers turn one essence into 12-locale reach:

```
delivery_brief(topic, persona, locale) =
     CEG.roots[topic]                      // universal: what all teachers point at
   ⊗ persona_model(persona, locale)        // aim: this person's suffering, language, scripts
   ⊗ somatic_delivery(roots → exercises)   // felt: deliver as body experience, not concept
```

- **Universal layer:** the CEG roots for the topic (provenanced, convergence-weighted).
- **Persona layer:** a **validated** persona model (§9) selects emphasis, vocabulary, invisible-script alignment, forbidden markers — aiming the universal root at a specific reader.
- **Somatic layer:** maps each delivered root to its somatic affordance (`somatic_affordances` edge in CEG) so the teaching lands as **felt experience**, not abstraction.

The brief is the GA's *specification* of what a good plan must cover; the GA then selects+sequences atoms to satisfy it under the fitness `F`.

### 8b. STRENGTHENER 4 — Closed feedback loop
- **Signals:** reviews, sales, completion/engagement, returns; **Pearl News good-news tracking** as a candidate world-impact signal; bestseller_editor verdicts as an internal signal.
- **Policy:** select plans via **Thompson sampling** with persona as context (contextual bandit) — explicit exploration, not greedy exploitation. Log propensities.
- **Off-policy evaluation:** validate a candidate fitness/scorer on logged engagement via counterfactual estimators *before* shipping (Zhuang 2020; Thompson-OPE 2025) — the only honest way to learn from sparse, biased signal.
- **Update:** OPE-validated signal updates the `T`/`E` outcome terms → BO retunes weights (§9-opt) → GA re-plans.
- **Guards:** (1) reserve an **exploration budget** + exposure/diversity term to prevent the degenerate feedback loop that homogenizes the catalog (Jiang 2019; Chaney 2018); (2) monitor proxy-vs-gold gap (Gao 2023).
- **Tier-2 path:** for unattended refresh, generate fidelity-preference data via an **RLAIF doctrinal rubric** (Gemma/Qwen on Pearl Star) so the loop isn't starved waiting on human review.

---

## 9. STRENGTHENER 5 — Validation layer (gate the optimizer on validity)

A persona or somatic heuristic earns the right to be an optimization target only after a **validity card**:
- **Construct validity:** it measures the intended latent thing; for any felt-experience/affect labels, inter-annotator reliability is tested first (Melhart 2023) — unreliable labels ⇒ no model.
- **Predictive validity:** it predicts a *held-out* real outcome (completion, re-engagement, self-reported benefit) on data it was not fit to (Salminen 2023).
- **Stability:** persona/segment definitions pass a saturation metric (De Paoli) so they aren't single-run LLM artifacts.
- **Uncertainty-bearing:** affective/somatic effects enter `T` as priors **with explicit uncertainty**, not precise multipliers — emotion constructs have weak accuracy guarantees.

Until a target passes, it may inform *generation* but not *optimization weight*. This directly answers RCG-013/007/022 (audit §3): validation is the remediation, made architectural.

### 9-opt. STRENGTHENER 6 — Right optimizer per sub-problem

| Sub-problem | Space | Eval cost | Optimizer | Why |
|---|---|---|---|---|
| **Atom selection + sequencing** (book) | combinatorial / permutation, huge | cheap (vs. learned fitness) | **GA / NSGA-II, memetic** (local swap/insert) | evolutionary operators fit subset+order; local search materially helps sequence-dependent (dwell/integration) costs (Schiavinotto 2014) |
| **Catalog portfolio** (which configs, dwell pacing) | combinatorial, very large | cheap | **GA / NSGA-II** | portfolio coverage of CEG roots × engagement diversity under fidelity floor |
| **Scorer/fitness weights + thresholds** (≤ ~8 continuous knobs) | low-dim continuous | **expensive** (scarce human/real feedback) | **qNEHVI multi-objective BO** | sample-efficient (tens of evals), noise-aware — replaces the EMA learner |

**Do not swap these.** Using GA to tune 3–8 weights wastes scarce feedback; using GP-BO to search the discrete atom space fails (surrogates degrade in high-dim discrete). The **EMA learner is retired** in favor of BO for the weights.

---

## 10. Wiring into the existing system

| Component | Today (audit) | Strengthened |
|---|---|---|
| `catalog_planner.py` | enumerates topic×persona×market; **no EI v2** | consumes CEG + delivery briefs; **GA** produces a Pareto portfolio under fitness `F`; fidelity floor enforced |
| `chapter_planner.py` / book planner | structural beats; **no EI v2** | **GA/memetic** selects+sequences atoms to satisfy the delivery brief and maximize `(T,E)` s.t. `Φ≥τ` |
| atom system (`atoms/`, `exercises_v4/`) | hand-authored, uncited | unchanged as *content*; atoms gain CEG-root tags + somatic affordances (metadata only — **this session touches no atoms**) |
| `phoenix_v4/quality/ei_v2/` scorer | weighted-sum composite | becomes the **fitness evaluator** (`T,E,Φ` channels), not a single scalar |
| `learner.py` (EMA) | nudges 5 weights | **retired**; replaced by qNEHVI BO over `ei_v2_fitness.yaml` knobs |
| `bestseller_editor.py` hybrid_select | the *only* live entry; editorial re-rank | **repositioned** as the post-render **EVAL gate + feedback tap** (verifier, not planner) |
| feedback | 45 internal records (7+) | **world_signal.jsonl** from real outcomes, via bandit + OPE |

**Migration is additive and reversible:** the GA/fitness run *alongside* the current pipeline behind a flag; the Pareto menu is operator-reviewed before any plan ships; the existing scorer keeps working as the fallback and as the eval gate.

---

## 11. Tier & cost compliance (CLAUDE.md)

- **Local / Tier-2 (no paid API):** embeddings, BERTopic clustering, coreference merge, runtime fitness scoring, GA/BO search, OPE — all run local or on Pearl Star (Gemma/Qwen via Ollama).
- **Tier-1 attended Claude:** root-node *naming/articulation* (operator reviews), design review, and any prose generation — all operator-present, reviewed before ship.
- **RLAIF fidelity rubric** for unattended refresh runs on Gemma/Qwen (Tier-2), never a paid API.
- **Banned:** no `ANTHROPIC_API_KEY`/cloud-LLM reads in runtime code (enforced by `llm-policy-enforcement.yml`); run `scripts/ci/audit_llm_callers.py` before any build PR.

---

## 12. Risks & failure modes

- **Reward hacking / overoptimization** (Gao) → gold-holdout + proxy-gap monitor + capped pressure.
- **Degenerate feedback loop** (Jiang/Chaney) → exploration budget + diversity term + exposure-aware modeling.
- **Unvalidated targets** → validity gate (§9) blocks optimizer trust until construct+predictive validity pass.
- **Synthesis hallucination** → every CEG root is provenanced + saturation-checked + human spot-checked; `composite_doctrine/` is the recovery oracle.
- **Optimizer mis-assignment** → the §9-opt decision table is normative.
- **Scope creep into atoms/production** → migration is flag-gated and additive; bestseller_editor remains the safety gate.

---

## 13. Open questions (for operator / ratification)

1. **Real-signal source of truth** — which engagement/sales feed is authoritative, and is Pearl News good-news tracking in-scope as an impact signal?
2. **τ_Φ floor** — what minimum fidelity is non-negotiable for a "Pearl Prime" general book?
3. **Validation data** — what held-out outcome do we have today to validate personas/somatic heuristics, or must we instrument it first?
4. **Build tiering** — embeddings/clustering on Pearl Star vs. local CPU; capacity?
5. **Cap entry** — ratify the EI-v2-strengthened cap in `PEARL_ARCHITECT_STATE.md` only after operator approves the P0s (gated, post-settle — not this session).

---

## 14. The one-paragraph summary

EI v2-strengthened is a **synthesis engine**: an engineered **Composite Essence Graph** extracts what all 15 teachers point at; a **validated** targeting model (essence × persona × somatic) aims it at a specific reader as felt experience; a **genetic algorithm** selects and sequences atoms while **Bayesian optimization** tunes the weights; all of it optimized against an **explicit three-objective fitness** — therapeutic × engagement × fidelity-as-a-floor — that a **closed, guarded feedback loop** makes smarter from the world. It turns today's competent editorial *scorer* into the *engine* the operator described, and it does so additively, reversibly, and within tier policy.
