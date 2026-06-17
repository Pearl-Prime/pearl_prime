# Enlightened Intelligence — Frontier Design

**The most powerful real way to build EI: the 5 pillars made real, composed into one living closed-loop technology — free, local, and faithful to the wisdom.**

Author: Pearl_Research (frontier-design mode) · Date: 2026-06-11 · Status: blue-sky design (not a ratified spec; ratification is a gated follow-up)
Companion files: [EI_RESEARCH_SOURCES.md](./EI_RESEARCH_SOURCES.md) · [EI_BUILD_ROADMAP.md](./EI_BUILD_ROADMAP.md) · EI_TECHNOLOGY_DECK.pptx

---

## 0. The thesis in one breath

**Enlightened Intelligence is a closed loop that turns living teachers' wisdom into healing that meets a specific young person where they actually are — and gets better every cycle without ever distorting the wisdom or paying a cloud API.**

Today "EI v2" is an EMA-tuned **weighted-sum editorial scorer** (`config/quality/ei_v2_config.yaml`): it *grades* a finished book. It has no knowledge graph, no model of the reader, no nervous-system model, no genetic algorithm, and the only "learning" is a moving average nudging five weights. It is a thermometer, not an engine.

This document designs the engine. We change everything we need to — but every idea here is (a) genuinely buildable, (b) free/self-hostable on **Pearl Star** (one ~16 GB GPU + 16 CPU threads, Ollama `gemma3:27b`/`qwen2.5:14b`, ComfyUI/FLUX, CosyVoice2) with open-source ML/optimization libraries and **no paid LLM API at runtime** per `CLAUDE.md`, and (c) faithful to the teachers' essence — the tech serves the wisdom, never flattens it.

The five pillars become five subsystems that compose into one loop:

| # | Pillar (operator's frame) | The subsystem we build | Poetic name |
|---|---|---|---|
| 01 | Knowledge Engineering | **The Living Wisdom Graph** — provenance-tracked KG + discovered cross-tradition "Contemplative Spine" + essence-as-heuristics | *The Spine* |
| 02 | Psychological Modeling | **The Reader Council** — each persona becomes a reactive generative agent that *reads a draft and reports felt response* | *The Mirror* |
| 03 | Somatic Heuristics | **The Felt-Arc State Machine** — the book as a designed autonomic itinerary, with a content→nervous-system-state estimator | *The Breath* |
| 04 | Organic Genetic Algorithms | **The Quality-Diversity Garden** — MAP-Elites breeding the best book *per niche*, mutated by a local LLM | *The Garden* |
| 05 | Machine Learning | **The Continual Learning Flywheel** — local LoRA/preference learning from real reader signal, fidelity-floored | *The Tide* |

---

## 1. What changes vs EI v2 (read this first)

| Dimension | EI v2 today | EI (this design) | The frontier move |
|---|---|---|---|
| **What it is** | A *scorer* that grades finished books | A *generative + evolutionary + learning engine* wired to the planners | Thermometer → engine |
| **01 Knowledge** | Flat YAML: `doctrine.yaml` fields + 2,418 `approved_atoms` as `{atom_id, band, body, teacher}` | Provenance-tracked knowledge graph; discovered universal **Contemplative Spine**; per-teacher "decoders"; essence-as-heuristic rules | Quotes → reasoning substrate |
| **02 Psychology** | Persona = a static `persona_weight ≈ 0.3` scalar in an embedding similarity | Persona = a **generative agent** that reads the actual prose and returns a beat-by-beat felt response + objections | Label → mind |
| **03 Somatic** | `somatic_precision` = count body-words ≥3/chapter, density ≥1.5/100w | A designed **autonomic state-machine** (activation→co-regulation→ventral-safety) + a content→state estimator with an **arousal** axis | Word-count → designed nervous-system arc |
| **04 Evolution** | None. An EMA nudges 5 weights | **MAP-Elites quality-diversity** over a grammar-constrained atom genome, local-LLM mutation, multi-objective fitness | Moving average → a garden of evolved books |
| **05 ML** | EMA (`ema_alpha=0.15`) on 5 composite weights; cross-encoder/embeddings are `model: null` stubs | Continual **LoRA + preference learning** (KTO/DPO) on `qwen2.5:14b`/`gemma`; the generators, the judge, and the GA-fitness all learn | 5-weight average → self-improving models |
| **Fitness** | Hand-set `composite_weights` (rerank .3, safety .2, …) | **T × E × F**: therapeutic-efficacy × resonance, with spiritual-fidelity as a **hard floor**, in a QD behavior-space | Scalar weights → multi-objective + diversity + floor |
| **Faithfulness** | `prohibited_terms` lint (prose check) | Provenance-by-construction (every sentence traces to an approved atom) + doctrine constraints as executable **SHACL** + frozen Wisdom-Constitution judge | Lint → guaranteed-by-architecture |

> **Relationship to PR #1516 (open, `ei-v2-strengthening`):** that workstream adds a multi-objective fitness (`T×E×fidelity-floor`) + qNEHVI/GA for atom selection — exactly the *floor* this design needs. We **consume** it, we do not conflict with it: #1516's NSGA-II/qNEHVI becomes the *in-niche* atom optimizer inside the QD Garden (§6 Pillar 04). This design is the north star #1516 ladders toward.

---

## 2. Pillar 01 — Knowledge Engineering → **The Living Wisdom Graph** (*The Spine*)

### 2a. SOTA baseline
LLM-assisted knowledge-graph construction is now a mature, **schema-guided** pattern. The reference techniques: **SPIRES / OntoGPT** (recursive, schema-constrained extraction to RDF/OWL that already runs on local LLMs) and the EMNLP-2024 **Extract–Define–Canonicalize (EDC)** framework (open-extract → auto-schema → canonicalize aliases). **GraphRAG** (Microsoft, 2024) turned the KG into a *reasoning substrate*: LLM-built entity graph → **Leiden** community detection → community summaries for global sense-making (~86% vs ~32% for naïve RAG on global questions). **HippoRAG / HippoRAG 2** (NeurIPS 2024) is the better fit for *wisdom*: OpenIE triples + synonymy edges + **Personalized PageRank**, every node linked back to the source passage, with **non-parametric continual learning** (add teachings without retraining). All have first-class local/OSS deployments (`graphrag-local-ollama`, `nano-graphrag`, LightRAG, vLLM).

### 2b. Frontier options (the real swings)
1. **The Contemplative Spine via embedding-graph community detection + a VAE/perennialism framing.** Embed every atom + every `core_principle`, build a k-NN similarity graph, run **Leiden** to find cross-tradition communities, and treat recurring communities as *contemplative invariants* (impermanence/non-attachment, present-moment refuge, self-as-construct, surrender-vs-effort). Frame it explicitly: the shared spine = a latent **z**; each teacher = a distinct **decoder**. This gives a *principled reason never to flatten*: collapsing decoders = "posterior collapse" = degraded, generic spirituality — a measurable failure, not a vibe. Seed the clustering with the empirically-validated **12-factor structure of "pure awareness"** (Gamma & Metzinger, n=1,403, 5 languages) so we cluster *toward* known invariants. **Buildability:** `sentence-transformers` (BGE-m3, multilingual for CJK) + `igraph`+`leidenalg` + `BERTopic` for naming. Embedding 2,418 atoms + 15 doctrines is **CPU-minutes**; Leiden on a ~3k-node graph is sub-second. Zero GPU pressure.
2. **Provenance-tracked living KB as nanopublications.** Replace flat atom YAML with a graph where each atom is a **nanopublication**: `{assertion:(concept,relation,concept), provenance:(teacher, source_text, extraction_run, model, approver), pub-info:(version, timestamp)}`, modeled on a thin **CIDOC-CRM/PROV-O** profile. New teachings *append* (continuous enrichment); nothing is overwritten; every generated sentence can cite its exact atom + teacher + source. Crucially, each doctrine's `forbidden_claims`/`prohibited_outcomes` become **executable SHACL constraints** instead of inert prose — generation is hard-blocked if it would assert what a teacher forbids. **Buildability:** `rdflib`/`oxigraph` (or `neo4j-community`) + `pySHACL` + the `nanopub` lib. A triplestore for 15 teachers is **megabytes**; SHACL validation is CPU-cheap, no GPU.
3. **Essence-as-Heuristics (CBR over the graph).** Beyond storing quotes, distill each tradition into machine-readable **`IF [reader-state] THEN [this-tradition-would-say]`** rules (e.g. `IF perfectionism-spiral → Stoic:{dichotomy_of_control}; Zen:{drop the measuring mind}; Sufi:{surrender outcome to the Beloved}`). Store as **case-based-reasoning** cases keyed to persona features. This is the difference between a quote database and *an advisor that thinks like the teacher.* **Buildability:** Ollama `gemma3:27b` to draft rules (operator-reviewed, then frozen as data), `sentence-transformers` for case retrieval, `sqlite`/`networkx` for the case base. Generation-time retrieval is CPU-only.

### 2c. Recommended design — the layered Living Wisdom Graph
**Build all three as one system: a provenance graph (opt 2) whose nodes link to a discovered Contemplative Spine (opt 1), with an essence-heuristic layer on top (opt 3), served by a HippoRAG-style PPR walk.** Data flow, all local:
1. **Extract** — SPIRES/OntoGPT over each bank's `raw/*.md` with a **LinkML** schema encoding the doctrine fields → schema-conformant atoms (`gemma3:27b`/`qwen2.5:14b` via Ollama; design-time Claude may *draft the schema*, never run in the pipeline).
2. **Canonicalize** — merge "ego death" / "anatta" / "self-dissolution" to one concept node *while keeping each teacher's surface phrasing as a label*.
3. **Store as nanopubs** — `oxigraph` + PROV-O; `pySHACL` enforces forbidden claims.
4. **Discover the Spine** — embed → k-NN → `leidenalg` communities → name with BERTopic + the Metzinger seed → write `aligned_to: spine_node` edges back.
5. **Heuristic layer** — `IF reader-state THEN tradition-move` cases keyed to personas.
6. **Serve** — at generation time, a HippoRAG-style PPR walk seeded from (persona-struggle ∩ teacher) returns the right atoms + matching heuristic + provenance.

**What changes vs EI v2:** atoms stop being a flat list and become **nodes in a provenance graph** with three new edge types — `aligned_to` (→ spine), `derived_from` (→ source), `applies_when` (→ persona/heuristic). Doctrine prohibitions become **executable constraints**. Retrieval moves from "filter YAML by type/band" to a multi-hop, source-grounded reasoning walk. Nothing is deleted — the YAML can be *generated from* the graph for backward compatibility.

### 2d. Phoenix fit + the moonshot
The 10 atom types become typed nodes; `doctrine.yaml` becomes the per-decoder profile; every atom gains an `aligned_to` edge so "show how all 15 teachers handle *impermanence*" returns **15 distinctly-voiced answers pointing at one spine node** — the anti-flattening guarantee, in data form. **Integration moonshot → "The Spine as the Genome" (§7.1).**

---

## 3. Pillar 02 — Psychological Modeling → **The Reader Council** (*The Mirror*)

### 3a. SOTA baseline
**Generative Agents** (Park et al., 2023) proved an LLM with persona + memory-stream + reflection can be *run as a mind*. **Silicon sampling** (Argyle et al., 2023, "algorithmic fidelity") showed conditioning on real backstories reproduces sub-population responses; **Persona Hub** (Tencent, 2024) released a reusable persona-construction recipe. The frontier most relevant to EI is **simulated audiences as an optimization signal**: **Explore-Generate-Simulate (EGS)** (Liu et al., 2023) generates message candidates, *simulates diverse audience reactions, and uses those reactions to rank candidates* — beating chain-of-thought and matching human raters on 5/8 scenarios. This is *exactly* "persona reads a draft, reports felt response, content optimizes against it." Therapeutic frameworks are now computable: **CBT-Bench** (NAACL 2025) formalizes CBT into evaluable stages; **IFS** "comes with a user manual" (a parts→Self protocol shipping bots already encode as state machines); **Self-Determination Theory** now has computational formalizations (autonomy/competence/relatedness as scoreable features). The documented failure modes are real — **stereotype amplification** (~7× inflated polarization), **caricature**, **social-desirability bias**, **sycophancy**, **variance under-coverage** — with concrete mitigations (anonymized debate, human-grounded persona training, graded forced-choice).

### 3b. Frontier options
1. **The Reactive Reader-Agent (EGS-for-books).** Each persona becomes a Park-style agent that *reads a chapter and emits a structured felt-response*: a beat-by-beat **resonance curve**, where attention drops, what objection rises ("a teacher would never get my burnout"), what lands, where it feels preached-at vs *seen*. Converts the persona from a static weight into *a critic with a felt trajectory*. **Buildability:** Ollama `gemma3:27b` (EN)/`qwen2.5:14b` (CJK) as the agent brain + **Outlines/XGrammar** constrained decoding to force a typed `ReaderResponse` + `sentence-transformers` to chunk into beats. A 27B model at q4 fits ~16–18 GB (serialize); one read-pass over a 3k-word chapter ≈ 10–20 s; 13 personas batchable nightly.
2. **Framework-Grounded Appraisal Reader.** Run the draft through an **appraisal model** ("chain-of-emotion": goal-relevance, novelty, coping-potential, self-relevance per beat) and report which **IFS part** the passage activates (exile/manager/firefighter) and whether it moves the reader toward **Self-energy** or triggers defense; a CBT lens flags whether prose *reinforces* a distortion vs gently *restructures* it. This is the bridge from "engagement" to *therapeutic mechanism* — a clinically-literate edit target. **Buildability:** same models, a YAML rubric (CBT distortions + IFS parts + SDT needs) filled via Outlines; optionally a small grounded scorer fine-tuned with **Unsloth/PEFT LoRA**.
3. **Steerable Persona Ensemble (anti-caricature).** Use **persona/activation vectors** to *dial* trait intensity (anxiety, skepticism, openness) instead of a prompt the model caricatures; run an ensemble of steered variants per persona and aggregate via **anonymized debate** to recover the population *variance* single personas collapse. **Buildability:** `repeng`/`steering-vectors` + `TransformerLens` on the open weights — a one-time offline calibration; phase-2 hardening, not v1.

### 3c. Recommended design — the Framework-Grounded Reactive Reader-Agent ("Reader Council")
Build option 1 **fused with** option 2; option 3 is phase-2 hardening. For each of ~13 personas, build a **psychometrically-informed persona card** (YAML): grounded demographic backstory, Big-Five band, top SDT-need deficits, live stressors grounded in *real 2025-26 data* (not invented), and an IFS part-profile — seeded from Persona Hub + real social-listening/review snippets. At QA time, the relevant 3–4 persona-agents read the actual prose and return, via constrained decoding:
```
ReaderResponse{ resonance_curve:[0..1 per beat], dropoff_beat:int|null,
  felt_emotion:OCC_enum per beat, objections:[{beat,quote,why}],
  ifs_part_activated:enum, moves_toward_self:bool,
  reinforces_distortion:enum|null, lands_as:{seen|preached_at|generic},
  one_line_verdict:str }
```
Aggregate (anonymized, to avoid sycophancy) into `reader_fitness = mean(resonance) − dropoff_penalty − distortion_penalty + self_movement_bonus` **plus a diff-ready `edit_list`**. This is a true objective function computed on the real words.

**What changes vs EI v2:** the persona stops being a `0.3` multiplier that never sees the text; it **reads the prose** and the system can A/B two atom variants and *pick the one the simulated reader feels more met by.* The static score table becomes a *prior*; the agent's verdict is the *posterior measured on the actual words.*

### 3d. Validity guardrails (non-negotiable)
Treat the Council as a **hypothesis generator, never ground truth** (EGS matched humans only 5/8). Ground every card in real signal; audit for stereotype drift (verdicts must quote a specific beat). Run personas **independently + anonymized** before aggregation; prefer graded forced-choice over Likert. Trust the Council most on *resonance/dropoff/objection-detection* (behavioral, checkable against completion data), least on absolute emotional-intensity. **The moment real KDP review/completion data exists, it outranks the simulation** — and corrects it (§6 Pillar 05). **Integration moonshots → "Content Bred Against Simulated Minds" (§7.2) and "Predict-Before-You-Render" (§7.5).**

---

## 4. Pillar 03 — Somatic Heuristics → **The Felt-Arc State Machine** (*The Breath*)

### 4a. SOTA baseline (with honest caveats)
**Polyvagal theory** (ventral-vagal / sympathetic / dorsal-vagal states, neuroception, co-regulation) is the dominant *design vocabulary* of the somatic field — but its **biological claims are seriously contested** (Grossman 2023; a multi-author 2026 critique argues the core premises are "untenable"; RSA is *not* a clean index of vagal tone). **The honest synthesis: treat polyvagal as a useful metaphor and design language, not validated mechanism** — and anchor every reader-facing benefit claim to the *practices*, which have independent evidence that does not depend on PVT being neuroanatomically correct. The **breathing evidence is the strongest leg and maps perfectly to text/audio**: the Stanford **Balban/Huberman/Spiegel 2023 RCT** found **exhale-emphasized cyclic sighing beat mindfulness** for mood and arousal at 5 min/day; **resonance-frequency / coherent breathing (~6 breaths/min, 0.1 Hz)** reliably maximizes HRV; the convergent finding is **exhalation longer than inhalation raises cardiac-vagal activity** — exactly the "in for four, out for six" cue Phoenix already ships. Interoception/body-scan, **orienting** (Somatic Experiencing), and **prosody/pacing** (slow tempo → autonomic down-regulation in listeners) complete a toolkit that is *entirely deliverable through words and voice* — no wearable required.

### 4b. Frontier options
1. **The Autonomic State Machine (book as a vagal-state itinerary).** Treat the book as an explicit FSM over autonomic states — `sympathetic-activation → titrated-contact → co-regulation → integration → ventral-safety` — where each chapter declares a target state *and a transition* (felt arc becomes a designed sequence of nervous-system states, borrowing SE's **titration/pendulation**: touch activation, return to safety, oscillate with decreasing amplitude). The current felt arc is a 1-D valence curve that can't say *what state the reader should be in or how to get them there.* **Buildability:** map each chapter to a target via a feature vector (below) using **NRC-VAD v2** lexicon + sentence-rhythm stats + breath/safety/orienting-cue detectors — pure numpy/regex, **zero GPU**; a small YAML state-graph holds legal transitions; an optional `gemma3:27b` pass validates that prose *language* matches the declared state.
2. **Prosody-Coupled Breath Pacing (audio that breathes the reader to 6/min).** Co-design the **CosyVoice2** output with the practice: the narrator's *own* exhale pacing slows across a down-regulation section, pauses stretch toward a ~0.1 Hz cadence during breath sequences, so the listener entrains to resonance frequency by following the voice. Audiobook is half the product; this turns the *voice* into the regulating agent. **Buildability:** annotate breath-spans → emit SSML-style pause/rate directives → measure realized inter-pause intervals from the audio's silence gaps (`librosa` RMS, CPU) and gate on cadence.
3. **Optional rPPG "Felt-Check" (graceful-degradation biofeedback).** An *optional* end-of-chapter check-in: hold a finger over the phone camera 60 s for an HRV/HR read via contact PPG, **or** tap a 1–5 "how settled do you feel," **or** skip. Never gates the book; personalizes pacing. **Buildability:** on-device peak-detection on the camera green-channel (JS/Swift) — Pearl Star only ingests anonymized aggregates later. **Hard requirement: identical behavior with the camera disabled — self-report is the floor, rPPG a bonus.**

### 4c. Recommended design — the Somatic State-Machine + a content→autonomic-state estimator
Replace the single valence curve with a **declared per-chapter target** over `{activation, titrated-contact, co-regulation, integration, ventral-safety, settling}` and a YAML transition table encoding titration/pendulation (a chapter must never *end* in raw activation without a return-to-safety beat). The **estimator** computes, per chapter (all CPU): **valence & arousal trajectory** (NRC-VAD — the arousal axis is genuinely new; today only valence is tracked); **rhythm / "breath of the prose"** (sentence-length mean/variance + a deceleration signal); **regulation-practice density** (extended-exhale cues, body-scan spans, orienting cues, safety/choice language); **co-regulation proxy** (2nd-person address, soft imperatives, pause-density). These → `(predicted_state, confidence)` per chapter + a book-level realized trajectory. **Crucially framed as estimating content's *affordances for* a state — "this passage is designed to invite down-regulation" — never "your nervous system is now in ventral vagal."** It becomes the `somatic_state_fit` fitness dimension = (trajectory match) × (transition execution) × (practice-cadence compliance).

**What changes vs EI v2:** `somatic_precision` (count body-words) is a bag-of-words proxy blind to whether words form a *regulating trajectory* — a chapter could hit the quota while autonomically yanking the reader around. The new dimension keeps body-word density as **one input** but adds (1) an **arousal** axis, (2) a **designed state sequence with legal transitions**, (3) **regulation-practice structure** (is there an exhale cue; does the chapter *return to safety*). **Phoenix already pre-figures this:** `config/spines/somatic_healing_spine.yaml` ships an `intensity_profile: [low,medium,…,low]`, a `trust_curve`, `permission_timing`, and `sequencing_rules` — a hand-authored proto-state-machine. We make it explicit, measured, and optimizable.

### 4d. Phoenix fit + integrity
The valence felt-arc is *subsumed* (valence + arousal). The "max 2 exercises/chapter" rule becomes the *cadence layer* — exercises get *typed* (breath = co-regulation; body-scan = titrated-contact; orienting = safety) and *placed* by the transition the chapter must execute. The manga `visual_therapeutic` block (`vt_parasympathetic`: cool-palette, breath-sequence, fractal density) is already a per-page autonomic-proxy estimator — **unify it under the same state machine** (one autonomic model, two modalities). **Integrity:** no medical overclaim (frame as content design, not physiology-reading; include a "not a substitute for care" line + an off-ramp for anyone who feels worse); honor the **stealth** doctrine (`vt_stealth` forbidden_terms + the spine `prohibited_terms`) — "polyvagal," "ventral vagal," "co-regulation" **never** appear on the page; the state machine lives in the build system, never in the prose. Not invoking PVT's terminology is *also* a scientific-integrity win, since the terminology is contested. **Integration moonshot → "The Cross-Modal Somatic Conductor" (§7.3).**

---

## 5. Pillar 04 — Organic Genetic Algorithms → **The Quality-Diversity Garden** (*The Garden*)

### 5a. SOTA baseline
For competing objectives, the mature core is **multi-objective evolutionary algorithms** — **NSGA-II/III**, **MOEA/D**, **SMS-EMOA** — in **pymoo**, returning a **Pareto front** rather than one scalar. (PR #1516's NSGA-II/qNEHVI sits here — the right *floor*, but a single front optimizes one trade-off surface, not a *catalog* of qualitatively different books.) The more important shift for a catalog product is **Quality-Diversity**: **MAP-Elites** (Mouret & Clune, 2015) discretizes a low-D **behavior space** into niches and keeps the best genome per niche, returning *thousands* of high-performing-yet-different solutions in one run (and often a better global optimum, because diversity provides stepping-stones). SOTA QD optimizers: **CMA-ME** and **CMA-MAE** (Fontaine & Nikolaidis, 2024), reference lib **pyribs** (Archive + Emitters + Scheduler); alternatives **qdpy**, **QDax**. **Novelty search** (Lehman & Stanley, 2011) defeats premature convergence — for content, "deception" = **formula collapse** (every book converging to the one combo the scorer rewards), so novelty pressure is first-class. The frontier that reframes everything for *text* genomes is **LLM-guided evolution**: **ELM** (LLM as smart mutation operator), **FunSearch** (Nature 2023), **Promptbreeder**, **EvoPrompt**, **ADAS** — and Pearl Star's local `gemma3:27b` *is* that operator.

### 5b. Frontier options
1. **QD over books with an LLM mutation operator (ELM-into-MAP-Elites).** Genome = an atom-assembly recipe; **behavior descriptors** = editorial axes (somatic-arc shape, teacher-voice mix, hook intensity, exercise density); **mutation = the local LLM** proposing a coherent atom swap or rewrite. The product *is* a grid — brand × persona × topic × locale — so QD natively returns "the best book in each niche," which is the catalog. **Buildability:** `pyribs` `GridArchive` + a custom `Emitter` whose `ask()` calls Ollama; CPU-side archive bookkeeping; cost is the LLM evals — cap **~150–300 judge-evals/generation**, batched, nightly Tier-2.
2. **Co-evolving content vs an evolving persona-agent (virulence-controlled).** Two populations: book genomes vs reader/persona simulators (the Reader Council). Books "win" by moving the persona toward resolution; personas evolve to be *harder to move*. Manufactures robustness and attacks reward-hacking (the judge is a moving target). **Buildability:** classic coevolution **disengages** (arms-race collapse); the literature fix is **reducing parasite virulence** (Cartlidge & Bullock, 2004) — select personas that are *occasionally* moved, not maximally resistant. `DEAP` two-population or hand-rolled around pyribs; doubles LLM cost → weekly cadence, μ≈20. Research moonshot behind the QD floor.
3. **Evolving the assembly *grammar*, not just the atoms.** Encode the *rules* that assemble books as a **BNF grammar** of legal structures and evolve the grammar itself via **Grammatical Evolution** (PonyGE2/GRAPE) — discovering genuinely new book *shapes*, not just recombinations. **Buildability:** `PonyGE2` (pure-Python, CPU-cheap); the grammar *guarantees* structural validity (free constraint-repair). Keep it human-curated initially; open-ended growth is later.

### 5c. Recommended design — MAP-Elites QD with a multi-objective core and a local-LLM operator
**Headline:** a **MAP-Elites / CMA-MAE** archive whose elites are scored by a **bounded multi-objective fitness** (extending #1516's qNEHVI, not replacing it), with the **local LLM as the smart mutation operator** over a **grammar-constrained atom genome**. QD is the outer loop (the catalog); MO fitness lives inside each cell (the trade-off); the LLM keeps mutations coherent.

- **Genome (structured/indirect, never a flat atom-ID vector):** a **structural gene** = a derivation from the assembly grammar (slot sequence + band-transition plan + callback/payoff links — makes invalid books unrepresentable) + **content genes** = per-slot references into the registry (`topic→band→role→family`) + a small "edit token" the LLM may apply. **Repair** is free (grammar generates only legal structures); the only filter is registry-miss → reuse `EI_V2_REGISTRY_LEARNING_SPEC.md`'s `BLOCK_TOPIC` logic as a lethal-genome filter.
- **Algorithm:** start with MAP-Elites in pyribs (debuggable), upgrade the emitter to **CMA-MAE**. Inside each cell, contend by **Pareto dominance** on the objective vector — **this is where #1516's NSGA-II/qNEHVI is consumed: as the per-cell atom optimizer, not the top loop.** QD chooses *which niches to fill*; #1516's MO solver chooses *the best atoms within a niche*.
- **Operators:** **mutation** = `gemma3:27b` given the genome + an (itself-evolvable, Promptbreeder-style) mutation-prompt → a coherent swap/rewrite; **crossover** = LLM-mediated arc-splice with grammar validation; **novelty injection** on a fraction of emitters.
- **Cheap fitness (3 tiers to respect budget):** (1) **free heuristics** every genome (band-transition smoothness, callback/payoff closure, exercise spacing, duplicate penalty — pure Python); (2) **embedding surrogate** (cosine coherence/redundancy, reused as the novelty descriptor); (3) **LLM-judge** only on genomes that pass tiers 1–2 *and* improve their cell (~150–300/gen, batched).
- **Behavior descriptors (2–4 D, cheap + interpretable):** somatic-arc shape (from §4), hook/confrontation intensity, exercise-vs-reflection density, teacher-voice composition. (Brand/persona/topic/locale are *contexts*, one archive per context, transfer-seeded.)

**What changes vs EI v2:** the EMA's one moving point becomes a **population + an archive of diverse elites** optimizing a *vector* of objectives with explicit anti-collapse novelty pressure. The EMA is demoted to a slow prior on objective weights (or retired per #1516's qNEHVI plan).

### 5d. Phoenix fit + the fitness crux → see §8. Integration moonshots → §7.1, §7.2, §7.6.

---

## 6. Pillar 05 — Machine Learning → **The Continual Learning Flywheel** (*The Tide*)

### 6a. SOTA baseline
**Parameter-efficient fine-tuning is commodity at this scale, and the 16 GB ceiling is *not* the binding constraint:** per Unsloth's own table, **QLoRA (4-bit) of a 14B model needs ~8.5 GB VRAM** — so `qwen2.5:14b` and gemma-class models are **both adapter-trainable on Pearl Star with headroom**. Stack: **PEFT + TRL + bitsandbytes + Unsloth**; **QLoRA** workhorse, **DoRA** the free one-flag quality upgrade. **Preference learning has migrated off the heavyweight PPO stack** onto cheap reference-light objectives in **TRL**: **DPO** (closed-form, no reward model), **ORPO** (no reference model, fused SFT+pref), **SimPO** (length-normalized, kills verbosity bias), and decisively **KTO** — which learns from **unpaired binary desirable/undesirable bits**, matching DPO from 1B–30B using only a thumbs-up/down. **RLAIF / Constitutional AI** manufactures preference data with a *local* judge (reaches RLHF parity, *exceeds* it on harmlessness — directly relevant since "therapeutic fidelity" is harmlessness-shaped). **Continual learning without forgetting** has three composable families: **adapter-per-domain + routing** (llama.cpp/Ollama hot-swap LoRA per request), **orthogonal-subspace** (**O-LoRA**), and **model merging** (**mergekit**: TIES/DARE/task-arithmetic, CPU-only).

### 6b. Frontier options
1. **KTO on real business signal — "the ledger is the reward model."** Skip explicit reward modeling: sold / 5-star / finished-the-audiobook = **desirable**; returned / 1-star / abandoned-at-20% = **undesirable**; run **KTO** directly. Phoenix's signal is exactly KTO's native diet (sparse, imbalanced, rarely paired). **Buildability:** TRL `KTOTrainer` + PEFT QLoRA on `qwen2.5:14b` (~8.5 GB), weekly idle-window retrain. Ships today.
2. **Evolutionary DARE-TIES merge as the continual-learning "garbage collector."** Train many disposable per-cohort LoRAs; periodically **merge the keepers** into the base with TIES/DARE (conflict-resolved, 90%-sparsified deltas); optionally **Sakana-style evolutionary merge** searches the recipe against a held-out fidelity metric. Solves forgetting *and* adapter sprawl; a bad cohort's adapter is simply never merged. **Buildability:** `mergekit` (CPU-only, GPU-free) + TRL/PEFT; evolutionary search is CMA-ES over merge coefficients, idle-window batch.
3. **RLAIF flywheel with a frozen "Wisdom-Constitution" judge.** A **frozen** `gemma3:27b` judge scores every draft against a written EI constitution (somatic-grounded? non-prescriptive? spiritually congruent? age-appropriate? *not* engagement-bait?); verdicts become the labels that train the *generator* adapter — a self-improvement loop with no human in the per-item path and no paid API. Because the judge is frozen + constitution-anchored, the target can't drift toward clickbait. **Buildability:** judge runs inference-only (quantized, <16 GB), policy trains (~8.5 GB) — generate, swap, score, swap, train via Ollama keep-alive.

### 6c. Recommended design — the closed-loop adapter flywheel
**Replace the EMA moving-average with an adapter flywheel; the EMA survives only as a fast, safe fallback for the 5 composite weights.** Three signal tributaries feed **one append-only feedback ledger** (sibling to `operator_decisions_log.tsv`): (1) **editor accept/reject/rewrite** — an accepted vs rejected sibling = a clean **DPO pair**, the rewrite is the gold "chosen"; (2) **A/B reader response + business outcome** (sold/rating/completion/return/Pearl-News), delayed+sparse so debiased with **IPS/DR** estimators → **KTO bits**; (3) **local RLAIF judge** → dense preference data covering what sparse signal misses. **Method: KTO-LoRA (QLoRA 4-bit, DoRA-enhanced) on `qwen2.5:14b` (CJK) / gemma (EN)** via TRL — KTO is primary because it ingests all three tributaries uniformly; promote clean pairs through DPO for a sharper gradient. **Adapter management:** one LoRA per cohort (brand × locale × persona), served via per-request hot-swap, **monthly TIES/DARE-merged** (only cohorts passing a quality+fidelity gate). **Every candidate adapter must clear a hard fidelity floor on a frozen held-out rubric before it can serve or merge.**

**What changes vs EI v2:** "ML" stops being a 5-D moving average that touches neither generator nor judge. After this: the **generators themselves learn** (tone, language, wisdom-delivery improve in the *weights*), the judge can be **distilled into a trained reward/critic** that *becomes the GA's fitness*, real reader+editor+sales signal **closes the loop continuously**, and merging makes improvement **cumulative without regression.**

### 6d. Phoenix fit + anti-Goodhart → see §8 + §9. Integration moonshots → §7.4, §7.5.

---

## 7. The integrated living system + the moonshots

### 7.0 The loop (the "living" claim made real)

```
                          ┌──────────────────────────────────────────────────────────┐
                          │                  ENLIGHTENED INTELLIGENCE                  │
                          │                     (one closed loop)                      │
                          └──────────────────────────────────────────────────────────┘

   15 living teachers' wisdom (approved atoms + doctrine)
            │
            ▼
   ┌───────────────────────┐     the wisdom substrate (provenance + universal spine + essence-heuristics)
   │ 01 LIVING WISDOM GRAPH │ ───────────────────────────────────────────────────────┐
   │      (The Spine)       │                                                          │
   └───────────────────────┘                                                          │
            │ targeted through                                                         │
            ▼                                                                          │
   ┌───────────────────────┐     ┌───────────────────────┐                            │
   │ 02 READER COUNCIL      │     │ 03 FELT-ARC STATE      │   the reader-model + the   │
   │    (The Mirror)        │ ◄──►│    MACHINE (The Breath)│   nervous-system itinerary │
   │  reactive persona-agents│     │  autonomic estimator   │                            │
   └───────────────────────┘     └───────────────────────┘                            │
            │                                │                                          │
            │   become FITNESS DIMENSIONS    │                                          │
            ▼                                ▼                                          │
   ┌──────────────────────────────────────────────────────────┐                       │
   │ 04 QUALITY-DIVERSITY GARDEN  (The Garden)                  │ ◄─── F = fidelity floor (from 01)
   │   MAP-Elites breeds the best book PER NICHE, mutated by a  │                       │
   │   local LLM, scored by  T × E  with  F  as a hard floor    │                       │
   └──────────────────────────────────────────────────────────┘                       │
            │ delivers a catalog of evolved books / audiobooks / manga                 │
            ▼                                                                          │
   ┌───────────────────────┐     real-world signal: reviews · sales · completion ·     │
   │   DELIVERY (Pearl)     │ ──  Pearl News impact · optional rPPG self-report ───┐   │
   └───────────────────────┘                                                      │   │
                                                                                  ▼   │
                          ┌───────────────────────────────────────────────────────┐  │
                          │ 05 CONTINUAL LEARNING FLYWHEEL  (The Tide)             │  │
                          │   local LoRA + preference learning, fidelity-floored   │  │
                          │   LEARNS: (a) the generators  (b) the judge/fitness    │  │
                          │           (c) recalibrates the persona-agents          │  │
                          │           (d) ENRICHES the spine from what resonates ──┼──┘  (feeds back to 01)
                          └───────────────────────────────────────────────────────┘
            └─────────────────────── every cycle, every model gets better ───────────────────────┘
```

**In words:** teachings → a synthesized **Living Wisdom Graph** → targeted through **persona-agents** + a **somatic state-machine** → content **evolved by the QD Garden** against a multi-objective fitness whose floor is spiritual fidelity → delivered → **real-world signal** → the **ML Flywheel** learns → the KB enriches (what resonates strengthens spine edges), the persona-agents recalibrate against real readers, the fitness sharpens, the generators improve → **the next cycle is measurably better.** Every pillar feeds the next; the last feeds the first. That is the "living" claim, made real and buildable.

### 7.1 Moonshot — **The Spine as the Genome** (01 × 04)
Evolve a book as a **path through the Contemplative Spine** (a sequence of invariants the reader traverses — *recognize-construction → loosen-grip → present-refuge → re-engage*), the Garden selecting, per spine-node, *which teacher's decoder voices it for this persona*, behind a hard provenance/SHACL gate. Turns the KG from a passive store into the **search space the optimizer reasons over** — every book becomes a provenance-verifiable, persona-fitted journey along the shared root, voiced in fifteen authentic registers. **Buildability:** `pyribs` archive over spine-paths + `leidenalg`-discovered spine nodes + `pySHACL` provenance gate. CPU-cheap structure; the LLM is used only to *voice* each node. (Near-term-adjacent: the spine itself is a P0 win.)

### 7.2 Moonshot — **Content Bred Against Simulated Minds** (02 × 04)
The Garden's fitness function *is* the Reader Council: content is evolved against a population of persona-agents that read each candidate and report felt response; then **co-evolve the personas** to be harder to move (virulence-controlled to avoid arms-race collapse). Books that only work on a credulous reader die. **Buildability:** Reader Council on `gemma3:27b` + `DEAP`/pyribs two-population coevolution + Cartlidge-Bullock virulence control. Doubles eval cost → weekly cadence, small μ. Research-grade; gate behind a stable QD floor.

### 7.3 Moonshot — **The Cross-Modal Somatic Conductor** (03 × 04)
The autonomic itinerary is *both* a behavior descriptor (niche) *and* an efficacy objective; the Garden evolves **text + manga panels + TTS prosody jointly** so the *combined* artifact executes one coherent `activation → co-regulation → ventral-safety` arc — the narrator's exhale pacing entraining the listener toward ~0.1 Hz resonance during breath sequences. The product stops being "a book that mentions the body" and becomes **a multi-sensory instrument designed to move a nervous system to safety.** **Buildability:** NRC-VAD arousal estimator (CPU) + CosyVoice2 SSML prosody directives + the manga `vt_parasympathetic` visual channel → one shared state classifier. All local.

### 7.4 Moonshot — **The Self-Enriching Spine** (05 × 01)
The ML Flywheel continually enriches the universal-spine graph from **what resonates**: when a spine-node's atoms consistently win `reader_fitness` + real signal, that edge strengthens; new teachings append as nanopubs; the essence-heuristics (`IF reader-state THEN tradition-move`) are refined by *outcome*. The KB literally **learns which cross-tradition moves heal which struggles** — the "living" KB made real. **Buildability:** feedback ledger → edge-weight updates on the graph (`networkx`) + KTO-LoRA on generators + **operator-gated** promotion (Tier-1). 

### 7.5 Moonshot — **The Predict-Before-You-Render Oracle** (02 × 05)
Because the Reader Council is continually calibrated against real KDP reviews/completion (a per-persona mapping from `reader_fitness` → realized outcome), pre-publication `reader_fitness` becomes an increasingly trustworthy **predictor** — EI can forecast whether a book will land *before spending a dollar rendering it*, and rank the ~800 high-confidence catalog configs per brand by predicted resonance before production. **Buildability:** a lightweight per-persona calibration regression (`scikit-learn`) on the feedback ledger; LCBM-style behavior modeling but post-hoc and free. Directly serves the catalog economics.

### 7.6 Moonshot — **Evolving the Assembly Grammar** (04, open-ended)
Evolve not just the atoms but the *rules that assemble books* (a BNF grammar via PonyGE2), discovering genuinely new chapter architectures — POET-style open-endedness where the structure space expands over time. **Buildability:** `PonyGE2` (CPU); guarantees structural validity; keep the grammar small/curated first, grow later. Research-grade.

---

## 8. The fitness function (the crux — everything depends on this)

We optimize **therapeutic efficacy × Gen-Z/Alpha resonance × spiritual-root fidelity**. The single most important design decision: **do not scalarize these into one weighted sum** — that *is* the EMA failure mode and is trivially reward-hacked (the optimizer inflates the cheapest axis). Instead:

**Three irreducible terms.**
- **T — Therapeutic efficacy** = `somatic_state_fit` (did the book execute its declared autonomic itinerary, ending in ventral-safety? — cheap, deterministic, from §4) + capacity-not-catharsis compliance (anti-overclaim) + IFS-move-correctness from the Reader Council (§3). Cheap deterministic core + a budgeted LLM-judge augment.
- **E — Gen-Z/Alpha resonance** = the Reader Council's met-ness: `mean(resonance_curve) − dropoff_penalty − preached_at_penalty + seen_bonus`, aggregated across the 3–4 targeted persona-agents (anonymized), later calibrated against real completion/reviews (§6).
- **F — Spiritual-root fidelity** = **a HARD FLOOR, never a tradeable objective.** F is the conjunction of: (a) **provenance** — every reader-facing sentence traces to an approved atom (graph/SHACL gate); (b) **voice-fidelity** — generated text stays near the teacher's decoder centroid and does not drift to the generic-self-help prior (embedding distance + the perennialism "no posterior collapse" criterion); (c) **spine-coverage** — touches the intended invariants; (d) **doctrine-compliance** — zero `forbidden_claims`/`prohibited_outcomes`/`prohibited_terms` violations.

**The optimization (precise).**
```
Feasible(c)  ⇔  F(c) ≥ F_floor  ∧  provenance_verified(c)  ∧  no_doctrine_violation(c)
Behavior niche  b(c) = ( somatic_arc_shape, persona_band, teacher_voice_mix, hook_intensity )
QD objective: fill archive A so that, for each niche b,
    A[b] = argmax over feasible c with b(c)=b  of   Pareto-elite( T(c), E(c) )  +  λ·Novelty(c)
where Novelty(c) = mean distance from c to its k nearest archive elites   (anti-formula-collapse)
Within a niche, ties/contention resolved by Pareto dominance on (T,E) via qNEHVI/NSGA-II  [#1516]
```
So: **QD behavior-space gives catalog coverage; multi-objective Pareto gives the T↔E trade; F is an ε-feasibility floor that engagement can never buy down; novelty pressure is the collapse-breaker.** A candidate that lifts E but drops F below floor is **non-viable**, full stop — the integrity guarantee is *in the optimizer's feasibility test*, not a hope.

**Anti-reward-hacking (the crux of the crux):** novelty pressure + QD structural diversity (rewarded for *new* niches → cannot collapse to one formula); **moving judges** (rotate/ensemble persona-agents, co-evolve them in the moonshot — a static rubric is a static exploit); **surrogate-vs-judge disagreement quarantine** (cheap-tier and LLM-judge diverging sharply = a hacking signature → human review); **fidelity floor + duplicate/redundancy penalties** (kill the two classic degenerate wins: lineage drift and padding with one high-scoring atom); and, in the ML loop, **KL-to-a-trusted-reference** + an **operator merge-gate** (§9).

---

## 9. Spiritual-integrity guarantees (the non-negotiable)

The teachers are **real, living masters** (the United Spiritual Leaders Forum; full EI disclosure is a *feature*). EI must amplify their essence, never impersonate or dilute it. Eight guarantees, each enforced by **architecture**, not goodwill:

1. **Provenance-by-construction.** Every reader-facing sentence traces to an approved atom + teacher + source (nanopublication/SHACL gate, §2). Ungrounded generation cannot ship — it fails `provenance_verified` in the fitness feasibility test (§8).
2. **Per-teacher decoder fidelity (no homogenization).** The VAE/perennialism framing makes *collapsing teachers into one generic voice* a **measurable failure** ("posterior collapse"), penalized in F. "Show how all 15 teachers handle impermanence" returns **15 voices pointing at one spine node**, never a blended average.
3. **Fidelity is a floor, never a knob.** F < threshold → candidate non-viable regardless of engagement. Engagement can **never** purchase a reduction in fidelity (§8, anti-Goodhart).
4. **Doctrine as executable law.** Each teacher's `forbidden_claims` / `prohibited_outcomes` / `glossary` / `prohibited_terms` become **SHACL constraints** that hard-block violations — e.g. Master Wu's doctrine forbids classical Wu-Wei framing; a candidate asserting it is rejected at the graph gate, not caught later in a prose lint.
5. **Stealth, preserved.** Wisdom lands as *lived experience*, never clinical/wellness jargon. The somatic state-machine and the polyvagal vocabulary live **only in the build system**; the page obeys `vt_stealth.forbidden_terms` + the spine `prohibited_terms` (already Phoenix doctrine). Not invoking contested terminology is also a scientific-integrity win (§4).
6. **A frozen, value-anchored judge.** The Wisdom-Constitution RLAIF judge (§6) is **frozen** so the optimization target cannot co-drift toward clickbait; its constitution explicitly **rewards** non-prescriptive, spiritually-congruent, age-appropriate output and **penalizes** engagement-bait (cliffhanger manipulation, parasocial hooks, false urgency).
7. **Human disposes (Tier-1 gate).** The flywheel *proposes*; no adapter merges into the base, and no spine-edge promotion lands, without automated `pr_governance_review`-style checks **and** an operator / Pearl_Architect sign-off — consistent with `CLAUDE.md`'s "a human reviews before it ships" Tier-1 policy and the serial-lane discipline on hot governance files.
8. **EI never speaks *as* a teacher.** It recombines **approved, teacher-vetted atoms** and discloses that it does. No fabricated teaching; no synthetic "the teacher would say." The essence-heuristics are operator-reviewed before they ever influence generation.

---

## 10. Free/local realization (the whole thing on Pearl Star, $0 runtime LLM)

**Compute:** one ~16 GB-VRAM GPU + 16 CPU threads. Ollama `gemma3:27b` (EN), `qwen2.5:14b` (CJK), ComfyUI/FLUX, CosyVoice2. Heavy GPU jobs **serialize** (no 2× GPU concurrency); CPU-bound work (embeddings, archive bookkeeping, SHACL, merges, the somatic estimator) runs concurrently. Pearl Star idle windows are the training/breeding budget.

| Subsystem | Runs on | OSS stack | GPU? | Cadence |
|---|---|---|---|---|
| 01 Living Wisdom Graph (build + enrich) | Ollama extract + CPU graph | OntoGPT/SPIRES, `rdflib`/`oxigraph`, `pySHACL`, `sentence-transformers` (BGE-m3), `igraph`+`leidenalg`, `BERTopic`, `networkx` | embeds only | one-time + incremental |
| 02 Reader Council | `gemma3:27b`/`qwen2.5:14b` (serialize) | Ollama, **Outlines/XGrammar**, `sentence-transformers` | yes (q4, ~16–18 GB) | nightly batch |
| 03 Felt-Arc State Machine | CPU | numpy/regex, **NRC-VAD v2** lexicon, `librosa` (audio), CosyVoice2 (SSML) | no (optional LLM label pass) | per-draft, ms |
| 04 QD Garden | CPU archive + Ollama mutation/judge | **`pyribs`** (+`qdpy`), `pymoo`+`BoTorch` (qNEHVI), `PonyGE2`, Ollama | judge/mutation only | nightly Tier-2 |
| 05 Continual Flywheel | 14B QLoRA train (~8.5 GB) + CPU merge | **PEFT, TRL** (KTO/DPO), **Unsloth**, **mergekit** (TIES/DARE), `scikit-learn` | train (~8.5 GB) | idle-window, weekly/monthly |

**Per `CLAUDE.md` LLM Tier Policy:** Tier-2 (Gemma/Qwen, unattended) runs every scheduled pipeline step (KG enrichment, nightly Council, QD breeding, idle-window LoRA). Tier-1 (Claude, operator-present) is **design-time only** — drafting the LinkML schema, seeding heuristics, reviewing the constitution — and **never in the runtime path.** No `ANTHROPIC_API_KEY`/OpenAI/DashScope-cloud anywhere in shipping code; `scripts/ci/audit_llm_callers.py` stays green. **Runtime LLM cost: $0.**

**Storage/disk:** the graph is megabytes; per-cohort LoRA adapters are tens of MB; the QD archive is small JSON/parquet. Nothing here strains Pearl Star or the repo. (This session's *authoring* worktree uses a tight sparse cone per `feedback_worktree_no_checkout_poison`.)

---

## 11. The one-paragraph pitch (for the forum)

*Enlightened Intelligence takes the living essence of fifteen masters' traditions and renders it as a graph that knows both each teacher's distinct voice and the universal root they share. It targets that wisdom through simulated young readers who actually report what lands and what feels preached-at, and through a model of the nervous system that designs each book as a journey from activation to genuine settledness. It then breeds hundreds of variations and keeps the best one for each kind of reader — never the most clickable, always the most faithful, because spiritual fidelity is a floor the optimizer cannot cross. Everything it ships, it learns from: real readers teach it, cycle after cycle, to deliver the wisdom better — and it does all of this on a single computer we own, with open-source tools, for no per-word cost, and without ever putting words in a teacher's mouth.*

---

*End of EI_FRONTIER_DESIGN.md. See [EI_BUILD_ROADMAP.md](./EI_BUILD_ROADMAP.md) for the phased P0/P1/P2 build and [EI_RESEARCH_SOURCES.md](./EI_RESEARCH_SOURCES.md) for the cited frontier.*
