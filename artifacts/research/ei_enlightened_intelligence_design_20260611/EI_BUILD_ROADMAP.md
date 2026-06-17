# EI Build Roadmap — from EI v2 to the living loop

How to get from today's EMA-tuned scorer to the full Enlightened Intelligence loop, phased so each step ships value on its own and nothing is greenfield-rebuilt. Companion: [EI_FRONTIER_DESIGN.md](./EI_FRONTIER_DESIGN.md).

**Legend:** 🟢 **near-term win** (weeks, low risk, mostly CPU, rides existing structure) · 🟡 **engine build** (1–2 quarters, the real subsystems) · 🔴 **research-grade moonshot** (genuine research risk; gate behind a stable floor).

**Standing constraints (every phase):** free/local on Pearl Star, no paid LLM API at runtime (`CLAUDE.md`); Tier-2 (Gemma/Qwen) for unattended pipeline steps, Tier-1 (Claude) design-time only; nothing touches atoms / production config / hot governance files without an operator + Pearl_Architect gate; every learning step is fidelity-floored and human-gated before it becomes permanent.

**Sequencing principle:** PR #1516 (`ei-v2-strengthening`: multi-objective fitness `T×E×fidelity-floor` + qNEHVI/GA for atom selection) is the **near-term floor this roadmap consumes.** P0 assumes #1516 merges; P1's Garden wraps #1516's qNEHVI as the in-niche optimizer. Do not duplicate #1516 — extend it.

---

## Phase P0 — the substrate + the cheap wins (🟢, ride on #1516)

Goal: stand up the data + signal layers that everything else needs, shipping value as standalone QA upgrades. **All CPU-friendly; no GPU contention; mostly augments `ei_v2_config.yaml` rather than replacing it.**

| ID | Build | Why now | Agent | Free/local stack | Flag |
|---|---|---|---|---|---|
| **P0.1** | **Living Wisdom Graph v0** — embed all 2,418 atoms + 15 doctrines, k-NN similarity graph, Leiden communities → discover the **Contemplative Spine v0** (named via BERTopic, seeded by the Metzinger 12-factor taxonomy). Output: `spine_nodes.yaml` + `atom→spine` edges. | The spine is the backbone of pillars 01/04/05 and the moonshots; it's pure CPU and needs no new infra. | Pearl_Research → Pearl_Dev | `sentence-transformers` (BGE-m3), `igraph`+`leidenalg`, `BERTopic`, `networkx` | 🟢 |
| **P0.2** | **Felt-Arc State Machine v0** — add an **arousal axis** (NRC-VAD) to the existing valence felt-arc; formalize `somatic_healing_spine.yaml`'s `intensity_profile`/`trust_curve`/`permission_timing` as an explicit state graph; ship `somatic_state_fit` as a new advisory scoring dimension. | The spine YAMLs already pre-figure the state machine; this is mostly making implicit structure explicit + one new feature axis. | Pearl_Research → Pearl_Editor | numpy/regex, NRC-VAD lexicon *(check licensing, src #44)* | 🟢 |
| **P0.3** | **Reader Council v0** — 3–4 persona-agents on `gemma3:27b` + Outlines-constrained `ReaderResponse`; run as an **advisory QA gate** (sibling to G1–G6 craft gates), not yet a fitness driver. Persona cards grounded in real social-listening + reviews. | Turns persona from a weight into a reader; immediately useful as an editor aid; de-risks the fitness wiring in P1. | Pearl_Research → Pearl_Editor | Ollama `gemma3:27b`/`qwen2.5:14b`, **Outlines/XGrammar**, `sentence-transformers` | 🟢 |
| **P0.4** | **Provenance + doctrine gate v0** — compile each teacher's `forbidden_claims`/`prohibited_outcomes`/`prohibited_terms` into **SHACL/rule checks**; hard-block violations at assembly time. Extends the existing `prohibited_terms` lint. | Makes spiritual integrity *enforced by architecture* (guarantee #4) before any generative/evolutionary step can drift. | Pearl_Dev | `rdflib`/`pySHACL` (or a rules layer over current lint) | 🟢 |
| **P0.5** | **Feedback ledger v0** — append-only TSV capturing editor accept/reject/rewrite + (where available) completion/review/sales, attributed to the generating config. Sibling to `operator_decisions_log.tsv`. | The ML flywheel (P1.2) and the predict-oracle (P1.4) are only as good as this ledger; start collecting now. | Pearl_PM / Pearl_Dev | plain TSV + a small writer in the pipeline | 🟢 |

**P0 exit criteria:** spine_nodes.yaml reviewed by operator; `somatic_state_fit` + Reader-Council verdicts visible in QA artifacts; SHACL gate blocks a known forbidden-claim test case; ledger accumulating rows. **No model training yet.**

---

## Phase P1 — the engine (🟡, the real subsystems)

Goal: turn the substrate into a closed loop — a generative/evolutionary Garden scored by learned fitness, a continual-learning Flywheel, and the graph/heuristic layer that makes retrieval reason.

| ID | Build | Depends on | Agent | Free/local stack | Flag |
|---|---|---|---|---|---|
| **P1.1** | **Quality-Diversity Garden v1** — `pyribs` MAP-Elites over a **grammar-constrained atom genome**; behavior descriptors = somatic-arc shape × persona-band × teacher-voice-mix × hook-intensity; **3-tier fitness** (free heuristics → embedding surrogate → budgeted `gemma3:27b` judge, ~150–300 evals/gen); **local-LLM mutation operator**. Wraps #1516's qNEHVI/NSGA-II as the **in-niche** atom optimizer. | P0.1–P0.4, #1516 | Pearl_Research → Pearl_Dev | `pyribs`, `pymoo`+`BoTorch`, Ollama, `PonyGE2` (grammar) | 🟡 |
| **P1.2** | **Continual Learning Flywheel v1** — feedback ledger → preference pairs/bits → **KTO/DPO LoRA (QLoRA 4-bit, DoRA)** on `qwen2.5:14b` (CJK)/gemma (EN); **frozen Wisdom-Constitution RLAIF judge**; `mergekit` TIES/DARE garbage-collection; **fidelity floor + KL-to-reference** guardrails. | P0.5, P0.4 | Pearl_Research → Pearl_Dev | **PEFT, TRL** (KTO/DPO), **Unsloth**, **mergekit**, Ollama (frozen judge) | 🟡 |
| **P1.3** | **Living Wisdom Graph v1** — promote v0 to a **nanopublication provenance store** (`oxigraph`/`rdflib`); add the **essence-as-heuristics CBR layer** (`IF reader-state THEN tradition-move`, operator-reviewed); **HippoRAG-style PPR retrieval** wired into the generator. | P0.1, P0.4 | Pearl_Research → Pearl_Dev | `oxigraph`, `pySHACL`, HippoRAG (local/vLLM), `sentence-transformers` | 🟡 |
| **P1.4** | **Predict-before-render calibration v1** — per-persona regression mapping Reader-Council `reader_fitness` → realized completion/review outcome; rank the ~800 high-confidence catalog configs/brand by predicted resonance before production. | P0.3, P0.5 (needs ledger volume) | Pearl_Research / Pearl_PM | `scikit-learn` | 🟡 |
| **P1.5** | **Fitness wiring** — make Reader-Council `E`, somatic `T`, and graph-fidelity `F` the actual objectives of the Garden (P1.1), with **F as a hard feasibility floor** (not a weighted term). Retire/demote the EMA to a fallback prior. | P1.1, P0.2, P0.3 | Pearl_Architect (spec) → Pearl_Dev | (config + glue) | 🟡 |

**P1 exit criteria:** the Garden produces a diverse archive of feasible books per niche; a LoRA adapter trained from real signal passes the fidelity floor and is operator-approved into serving; HippoRAG retrieval cites provenance for every generated passage; the predict-oracle's per-persona correlation is measured against real outcomes. **This is the first turn of the full loop.**

---

## Phase P2 — the moonshots (🔴, research-grade, gated behind a stable floor)

Goal: the genuine swings that connect pillars in ways no one has shipped. Each is gated behind a working P1 and an operator decision; none is on the critical path.

| ID | Moonshot (→ design §) | What it adds | Agent | Free/local stack | Flag |
|---|---|---|---|---|---|
| **P2.1** | **Spine as the Genome** (§7.1) | Evolve a book as a **path through the Contemplative Spine**; the Garden picks which teacher voices each invariant for this persona, behind a provenance gate. The KG becomes the search space. | Pearl_Research → Pearl_Dev | `pyribs` over spine-paths, `leidenalg`, `pySHACL` | 🔴 |
| **P2.2** | **Content Bred Against Simulated Minds** (§7.2) | The Garden's fitness *is* the Reader Council; then **co-evolve** the personas to be harder to move (virulence-controlled). | Pearl_Research | `DEAP`/pyribs two-pop, Cartlidge-Bullock virulence control, Ollama | 🔴 |
| **P2.3** | **Cross-Modal Somatic Conductor** (§7.3) | Evolve **text + manga + TTS prosody jointly** to execute one coherent autonomic arc; narrator exhale-pacing entrains the listener toward ~0.1 Hz. | Pearl_Research + Pearl_Author (manga) | NRC-VAD estimator, CosyVoice2 SSML, manga `vt_parasympathetic` channel, `librosa` | 🔴 |
| **P2.4** | **Self-Enriching Spine** (§7.4) | The Flywheel rewrites **spine edge-weights from what resonates**; new teachings append as nanopubs; heuristics refined by outcome. The "living" KB made real. | Pearl_Research → Pearl_Dev | `networkx` edge updates, KTO-LoRA, operator-gated promotion | 🔴 |
| **P2.5** | **Predict-before-render Oracle, productized** (§7.5) | The calibrated oracle drives catalog prioritization + pre-render go/no-go at scale. | Pearl_PM / Pearl_Research | `scikit-learn`, ledger | 🔴 (P1.4 is the v1) |
| **P2.6** | **Evolving the Assembly Grammar** (§7.6) | Evolve the **rules** that assemble books (BNF grammar) → genuinely new chapter architectures (POET-style open-endedness). | Pearl_Research | `PonyGE2`/GRAPE | 🔴 |
| **P2.7** | **Optional rPPG felt-check loop** (§4b-3) | On-device phone-camera HRV/self-report check-ins feed an *optional* real-world fitness bonus; degrades gracefully to self-report. | Pearl_Dev (reader app) | on-device JS/Swift PPG; Pearl Star ingests aggregates only | 🔴 |
| **P2.8** | **Steerable Persona Ensemble** (§3b-3) | Activation-vector steering of persona traits to recover population variance + quantify caricature drift. | Pearl_Research | `repeng`/`steering-vectors`, `TransformerLens` | 🔴 |

---

## Compute scheduling on Pearl Star (one GPU — serialize the heavy)

| Window | Job | Tier |
|---|---|---|
| **Design-time (operator present)** | LinkML schema drafting, heuristic seeding, constitution authoring, spec review | Tier-1 (Claude) — never in runtime |
| **Nightly (idle)** | Reader-Council batch reads; QD-Garden breeding (budgeted LLM-judge) | Tier-2 (gemma/qwen) |
| **Weekly (idle)** | KTO/DPO LoRA training; co-evolution rounds (P2.2) | Tier-2 |
| **Monthly (idle)** | `mergekit` TIES/DARE adapter GC; spine re-clustering + enrichment | Tier-2 / CPU |
| **Continuous (CPU)** | Somatic estimator, SHACL gate, archive bookkeeping, ledger writes, embeddings | CPU — no GPU contention |

CPU-bound work (embeddings, archive, SHACL, merges, somatic) runs **alongside** GPU jobs; GPU-heavy work (Council, judge, training) **serializes** per the Pearl Star concurrency matrix.

---

## Risk register (top 5)

1. **Reader-Council validity** (over-trusting simulated readers). *Mitigation:* advisory-only until P1.4 calibration; anonymized ensembles; real signal outranks sim the moment it exists.
2. **Reward-hacking / formula collapse** in the Garden. *Mitigation:* fidelity floor as feasibility (not weight) + novelty pressure + moving judges + surrogate-vs-judge disagreement quarantine (§8).
3. **Catastrophic forgetting** in continual LoRA. *Mitigation:* O-LoRA orthogonality + mergekit GC + fidelity-floor gate before any merge.
4. **NRC-VAD licensing** for commercial use (src #44). *Mitigation:* confirm licence or swap to an open-licensed arousal lexicon/embedding regressor before shipping P0.2 commercially.
5. **Polyvagal over-claim.** *Mitigation:* PVT is a build-system metaphor only; reader-facing claims anchored to breath/interoception/prosody evidence; stealth doctrine keeps the vocabulary off the page (§4d, §9-5).

---

## The smallest first step

If only one thing ships next: **P0.1 (discover the Contemplative Spine) + P0.3 (Reader Council v0 as an advisory gate).** Together they prove the two highest-leverage frontier ideas — *the universal root made queryable* and *the persona made a mind* — on pure CPU + existing local models, with zero risk to production, and produce artifacts the operator can read and react to. Everything else ladders from there.
