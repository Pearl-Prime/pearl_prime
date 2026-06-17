# EI v2 — Current-State Audit: Scorer vs. Synthesis-Engine

**Author:** Pearl_Research (verify pass) · **Date:** 2026-06-11 · **Status:** read-only audit, no code touched
**Companion docs:** `EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md` (the target), `EI_V2_ENHANCEMENT_ROADMAP.md` (the path), `EI_V2_SOTA_RESEARCH_NOTES.md` (the grounding)

---

## 0. The honest answer (read this first)

> **EI v2 today is a scorer, not the synthesis engine the vision describes.**
>
> It is a fail-open, **post-render editorial weighted-sum scorer** that picks among already-generated content atoms for a book slot, plus an **EMA (exponential moving average) weight-tuner** that nudges five scoring weights from **45 human accept/reject records — only 7 of them positive**. There is **no genetic algorithm anywhere in the repository**, **no spiritual-root synthesis step**, **no research→persona or research→somatic derivation**, and **no wiring into the catalog or book planner**. The operator's four-stage synthesis pipeline is **~30% built** (corpus + hand-authored composite prose + a scorer) and **~70% aspirational** (engineered synthesis, research-grounded targeting, explicit multi-objective fitness, a real optimizer, and a closed feedback loop).
>
> This is not a criticism of the work that exists — the scorer is competently built, config-rich, and fail-open. It is a precise statement of the **gap between what is built and what was envisioned**, which is the whole point of this audit.

---

## 1. Method & evidence base

Read-only sweep of: `config/quality/ei_v2_config.yaml`, `phoenix_v4/quality/ei_v2/{__init__,learner,hybrid_selector}.py`, `phoenix_v4/qa/bestseller_editor.py`, `artifacts/ei_v2/{learned_params.json,learner_feedback.jsonl}`, `docs/EI_V2_REGISTRY_LEARNING_SPEC.md`, `docs/EI_V2_MARKETING_INTEGRATION_SPEC.md`, `docs/RESEARCH_CITATION_GAP_DEV_SPEC.md`, `SOURCE_OF_TRUTH/teacher_banks/`, `SOURCE_OF_TRUTH/composite_doctrine/`, `SOURCE_OF_TRUTH/exercises_v4/`, `config/catalog_planning/`, plus a full-repo grep for genetic-algorithm primitives. Load-bearing facts (the EMA update rule, the composite weights, the planner non-wiring, the feedback counts, PR #1509) were verified firsthand against source lines; corpus counts come from the discovery sweep. Where a claim is inferred rather than line-verified it is marked **[inferred]**.

---

## 2. The four-stage verdict table

| # | Vision stage | Verdict | One-line evidence |
|---|---|:---:|---|
| 1 | Teachings → **knowledge-engineered KB** → **spiritual-root commonalities** | **PARTIAL** | Corpus + a hand-authored cross-teacher composite exist; the *engineered synthesis* (structured, provenanced root extraction) and the KB the scorer actually loads (marketing lexicons) do not match the vision. |
| 2 | Psych research → **persona models** | **NOT-BUILT** (as research-grounded) | ~46 hand-authored persona voice-profiles exist; `RESEARCH_CITATION_GAP_DEV_SPEC.md` RCG-013 explicitly flags "personas as segments **without validation source**." No research→persona derivation. |
| 3 | Somatic research → **somatic heuristics** | **PARTIAL** | `exercises_v4` is somatic-informed (polyvagal/interoceptive language) and `somatic_precision` is a live quality gate; but there is **no citation trail / research→heuristic derivation** (RCG-007, RCG-022). |
| 4 | **Genetic algorithms** → tune **catalog + book planner** | **NOT-BUILT** | **Zero** GA primitives in the repo. EI v2 is an EMA-tuned weighted sum at the **post-render editorial gate**; `catalog_planner.py` / `chapter_planner.py` contain **no EI v2 import**. |

**Net:** of the four stages, **zero are BUILT to the vision**, two are PARTIAL (corpus/assets exist, the engineered/grounded mechanism does not), and two are NOT-BUILT. The connective tissue the vision is *about* — synthesis, grounding, a multi-objective fitness, an optimizer, a loop — is the part that is missing.

---

## 3. Stage-by-stage findings

### Stage 1 — Teachings → KB → spiritual-root commonalities — **PARTIAL**

**What exists.**
- **Teacher corpus:** `SOURCE_OF_TRUTH/teacher_banks/` — **15 teachers** (`adi_da, ahjan, joshin, junko, kenjin, maat, master_feung, master_sha, master_wu, miki, miyuki, omote, pamela_fellows, ra, sai_ma`), ~3,260 files, each teacher with doctrine + STORY/EXERCISE atoms.
- **A cross-teacher composite:** `SOURCE_OF_TRUTH/composite_doctrine/` — **15 topic folders** each with a `CANONICAL.txt` that synthesizes a unified per-topic doctrine across teachers (e.g. `anxiety/CANONICAL.txt` ≈34 KB, "anxiety is information" framing, multiple composite versions). **So a synthesis *did* happen.**

**Why it is PARTIAL, not BUILT.**
1. **The synthesis is hand-authored prose, not knowledge-engineered.** There is no structured representation of root concepts, no provenance map (which teacher's doctrine → which root), no typed concept graph, no derivation method or spec. It is an editorial composite, not an extracted, queryable spiritual-root KB.
2. **The KB the scorer actually loads is a *marketing* KB, not the doctrine spine.** `ei_v2_config.yaml` points `research_kb` at `artifacts/research/kb` (≈15 lexicon entries) and `marketing_sources` at `marketing_deep_research/` ([config:1-16](config/quality/ei_v2_config.yaml#L1)). The teacher_banks / composite_doctrine corpus is **not** wired into the scorer at all. The "KB" in EI v2 and the "composite essence" the operator means are two different things.
3. **`docs/EI_V2_REGISTRY_LEARNING_SPEC.md` is about registry *availability*, not synthesis.** Its "learning loop" blocks topics that lack a content registry (`REGISTRY_MISSING` → `BLOCK_TOPIC_UNTIL_REGISTRY_EXISTS`); it is not the spiritual-root engine.

**Verdict:** the *assets* of Stage 1 exist (corpus + a composite); the *engineered synthesis step* and the *scorer wiring* the vision requires do not. → **PARTIAL.**

---

### Stage 2 — Psych research → persona models — **NOT-BUILT (as research-grounded)**

**What exists.** ~46 personas across 12 locales (10 active en-US canonical) defined as hand-authored **voice profiles** (`config/catalog_planning/`, `docs/LOCALE_PERSONAS.md`): tone bias, jargon, forbidden markers, rewrite config.

**Why it is NOT-BUILT to the vision.** The personas are audience *voice* artifacts, not psychology-derived models. The repo's own citation audit is explicit:
- **RCG-013** — "*Twelve personas as segments **without validation source***" (severity MEDIUM; remediation: "Source list for segment model"). [`RESEARCH_CITATION_GAP_DEV_SPEC.md`]
- **RCG-004** — persona revenue/TAM ranges "no methodology" (HIGH).
- **RCG-008/009** — persona workforce sizes uncited.

There is **no psychological-research → persona derivation artifact** (no attachment theory, Big Five, Maslach burnout, etc. → persona mapping with sources). The vision's stage 2 — "the psychological deep research → persona models" — has the *output* (personas) but not the *derivation* or the *research input*. → **NOT-BUILT.**

---

### Stage 3 — Somatic research → somatic heuristics — **PARTIAL**

**What exists.**
- `SOURCE_OF_TRUTH/exercises_v4/` — 11 exercise types, ~12 approved (breath_regulation, grounding_orientation, vagal_stimulation, nervous_system_down/upregulation, etc.) with an `aha_noticing` "nervous-system interpretation layer." The language is genuinely somatic-aware (interoception, parasympathetic, vagal tone).
- A live **`somatic_precision` quality gate** in the scorer ([config:126-131](config/quality/ei_v2_config.yaml#L126): min somatic words/chapter, density target, pass/warn thresholds).

**Why it is PARTIAL.** The exercises are *informed by* somatic frameworks but carry **no citations and no research→heuristic derivation**. The repo flags this directly:
- **RCG-007** — the "nervous system's attempt to protect you… evolved to keep you alive" claim is uncited (needs Porges/polyvagal sourcing).
- **RCG-022** — `teacher_banks` pedagogical claims uncited.

So the *heuristics exist and run as gates*, but the "somatic research → heuristics" provenance the vision implies is absent, and the gate thresholds are hand-set numbers, not research-derived. → **PARTIAL.**

---

### Stage 4 — Genetic algorithms → tune catalog + book planner — **NOT-BUILT**

**There is no genetic algorithm.** A full-repo grep for `genetic / fitness / mutation / crossover / chromosome / genome / population / evolutionary / evolve` in the optimizer sense returns **zero** hits. The only `fitness` token is `compute_cta_fitness()` — a 0–100 ad-copy heuristic, unrelated to evolutionary search. No population, no selection, no crossover, no mutation operators exist anywhere.

**What runs instead is an EMA-tuned weighted sum, at the wrong stage of the pipeline:**
- **The "learning" is an exponential moving average,** not evolution: [`learner.py:191`](phoenix_v4/quality/ei_v2/learner.py#L191) — `new_weights[dim] = alpha * avg_contrib + (1.0 - alpha) * cur_w`, α=0.15 ([config:206](config/quality/ei_v2_config.yaml#L206)). It only updates after ≥10 records ([`learner.py:177`](phoenix_v4/quality/ei_v2/learner.py#L177)) and averages dimension scores **from accepted feedback only** ([`learner.py:184`](phoenix_v4/quality/ei_v2/learner.py#L184)).
- **It is not wired into the planner.** `catalog_planner.py` and `chapter_planner.py` contain **no EI v2 import** (grep-confirmed). The only live call site is the **post-render editorial gate**: `bestseller_editor.py` imports and calls `hybrid_select` ([`bestseller_editor.py:14,283`](phoenix_v4/qa/bestseller_editor.py#L283)) to pick among atom variants *after* prose is rendered. `enrichment_select.py` carries only a deferred `P0.9` flag, not a wiring.

**Verdict:** the optimizer the vision is built around — a GA tuning the planners — **does not exist**, and the thing that does exist (EMA weight-nudging) operates as an editorial re-ranker, not a planner driver. → **NOT-BUILT.**

---

## 4. What EI v2 actually *is* today (the scorer anatomy)

```
                       ┌─────────────── EI v2 (as built) ───────────────┐
catalog_planner ──▶ chapter_planner ──▶ render prose ──▶ bestseller_editor
   [NO EI v2]          [NO EI v2]                          │  hybrid_select()  ← the only live entry
                                                           ▼
                              candidate atoms for a slot ──▶ weighted-sum score ──▶ pick best
                                                           │  (rerank·safety·domain·tts·duration / arc gates)
                                                           ▼
                              human marks accept/reject ──▶ learner.py EMA ──▶ learned_params.json
                                   (45 records, 7 positive)        α=0.15           (5 weights + margin)
```

**The composite score** (config) is a fixed weighted sum: `rerank 0.30 · safety 0.20 · domain_similarity 0.15 · tts_readability 0.15 · duration_fit 0.20` ([config:78-83](config/quality/ei_v2_config.yaml#L78)), with a `hybrid.override_margin: 0.12` deciding when V2 overrides the legacy V1 pick ([config:84-92](config/quality/ei_v2_config.yaml#L84)). Quality **gates** exist for `engagement, somatic_precision, uniqueness, cohesion, listen_experience` ([config:105-141](config/quality/ei_v2_config.yaml#L105)) — so the *vocabulary* of the vision (engagement, somatic) is present, but as hand-set pass/warn thresholds, not as learned, research-grounded objectives.

**Learned state** ([`learned_params.json`](artifacts/ei_v2/learned_params.json)): 45 observations; weights `rerank 0.246, domain 0.223, safety 0.250, tts 0.126, emotion_arc 0.155`; override_margin 0.119.

**A coherence gap worth flagging:** the **scorer's composite** is over `{rerank, safety, domain_similarity, tts_readability, duration_fit}` (config) while the **learner tunes** `{rerank, domain, safety, tts, emotion_arc}` ([`learner.py:15-21`](phoenix_v4/quality/ei_v2/learner.py#L15)) — `duration_fit` is scored but not learned; `emotion_arc` is learned but not in the composite. The scorer and its learner optimize **different dimension sets**. This is the signature of a system assembled from parts rather than designed around one explicit objective — exactly the thing a multi-objective fitness fixes.

---

## 5. The scorer-vs-synthesis-engine gap (the core finding)

| Vision says EI v2… | Reality | Gap |
|---|---|---|
| **synthesizes** all teachers into a spiritual-root composite essence | Hand-authored per-topic composite prose; no engineered extraction, no provenance, not loaded by the scorer | **Synthesis step is editorial, not engineered.** No queryable root-concept KB. |
| derives **personas** from psychological research | Hand-authored voice profiles; RCG-013 flags "no validation source" | **No research→persona derivation.** Personas are unvalidated segments. |
| derives **somatic heuristics** from somatic research | Somatic-informed exercises + a hand-set gate; no citations (RCG-007/022) | **No research→heuristic derivation.** Provenance absent. |
| uses these to **tune genetic algorithms** | No GA exists; an EMA nudges 5 weights | **No optimizer of any evolutionary kind.** |
| that **drive the catalog + book planner** | EI v2 is a post-render editorial re-ranker; planners don't import it | **Wrong stage, wrong coupling.** It scores finished prose, it doesn't plan. |
| learns and gets **stronger from the world** | Open-loop EMA on 45 internal records (7 positive); no reviews/sales/engagement signal | **No closed loop.** No real-world signal enters. |
| optimizes for **therapeutic × engagement × fidelity** | One scalar weighted sum; objectives not separated; fidelity not even an objective | **No multi-objective fitness.** Fidelity is unmeasured. |

**One-sentence gap:** *EI v2 scores and lightly re-weights finished content; it does not synthesize, derive, evolve, plan, or close the loop — so it is a competent editorial scorer wearing the name of a synthesis engine.*

---

## 6. Honest caveats (what this audit does **not** claim)

- **Not "worthless."** The scorer is real, fail-open, config-rich, and the EMA learner is deterministic and sane for what it is. The gap is one of *scope vs. vision*, not of quality.
- **The composite essence partly exists.** `composite_doctrine/` is genuine cross-teacher synthesis — it just isn't engineered, provenanced, validated, or wired in. Stage 1 is the *closest* to the vision and the natural P0 to build on.
- **The vision's vocabulary is already in the config** (engagement/somatic gates), which means the strengthened design is an *evolution of naming already present*, not a green-field rename.
- **[inferred] items** (scorer internals beyond the lines quoted; full enumeration of persona files) come from the discovery sweep and should be spot-checked before any code change, per the build roadmap.

---

## 7. Bottom line

The operator asked: *"Is that what's happening?"* The truthful answer is **no — not yet**. EI v2 is **one-third of the engine** (a corpus, a hand-authored composite, and a scorer) and **two-thirds a vision** (engineered synthesis, research-grounded + validated targeting, an explicit multi-objective fitness, the right optimizer per sub-problem, and a world→fitness feedback loop). The good news: the missing two-thirds is designable from what exists, and the highest-leverage piece — an **explicit multi-objective fitness** (therapeutic × engagement × fidelity) plus a **first-class spiritual-root synthesis** — is exactly where the strengthened architecture spec begins.
