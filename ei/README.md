# `ei/` — Enlightened Intelligence P0 build (additive + advisory)

A **new, self-contained** package that READS the Phoenix Omega corpora and
produces **advisory** artifacts. It does **not** modify the production EI v2
scorer, the production config, or the planners. P0 = additive + advisory;
production-wiring is a **gated P1 follow-up** into the #1516 spec.

## The convergence this materializes

Two independent EI investigations landed on the **same architecture**. Their P0
objects are the same under different names — we build the shared foundation once:

| Converged object | #1517 (ceiling) name | #1516 (floor) name | Module |
|---|---|---|---|
| **Contemplative Spine ≡ CEG** | P0.1 Living Wisdom Graph v0 | P0.2 Composite Essence Graph | `ei.spine` |
| **Multi-objective T×E×F fitness** | T×E×F fitness, F a hard floor | P0.1 Explicit multi-objective fitness | `ei.fitness` |
| **Reader Council** | P0.3 Reader Council v0 | psychology / validation pillar | `ei.reader_council` |
| **Provenance / doctrine gate** | P0.4 SHACL/rule checks | feasibility test internals | `ei.provenance_gate` |
| **Felt-Arc estimator** | P0.2 Felt-Arc State Machine v0 | somatic T input | `ei.felt_arc` |

**`spine ≡ CEG`** (`ei.SPINE_IS_CEG = True`): the discovered artifact materializes
**both** interfaces — `spine_nodes.yaml` (#1517) **and** `ceg.json` (#1516).

QD Garden / qNEHVI-BO / GA-for-atoms / LoRA flywheel are **P1+** in *both*
roadmaps and are **NOT built** here (P0 only).

## Modules

- **`ei.config`** — central config. The #1516 spec **§13 open questions**
  (real-signal source / τ_Φ fidelity floor / validation data) are
  **parameterized, never hardcoded**, each flagged `[GATED]` with an honest
  default. The operator decides them at ratification; changing the answer is a
  one-line config edit.
- **`ei.corpus`** — read-only loaders (atoms, doctrines, composite syntheses,
  gold-ref books, personas, the EI-v2 KB).
- **`ei.ollama_client`** — free/local embeddings + LLM via Pearl Star Ollama
  (ssh-tunnelled; batched). No paid API.
- **`ei.spine`** — P0.1 Contemplative Spine / CEG discovery (Leiden over atom
  embeddings, per-teacher provenance preserved).
- **`ei.fitness`** — P0.2 multi-objective `(T, E, Φ)` with Φ as a **hard
  feasibility floor** (Pareto, **not** a weighted sum).
- **`ei.reader_council`** — P0.3 persona agents (Ollama gemma3:27b) reading a
  real book, grounded in CBT/IFS/SDT (answers RCG-013).
- **`ei.provenance_gate`** — P0.4 doctrine forbidden-claim rule checks +
  provenance-by-construction.
- **`ei.felt_arc`** — P0.5 valence+arousal arc estimator (vendored open VAD
  lexicon) + `somatic_state_fit` (cites RCG-007/022).
- **`ei.experiments.composite_reproduction`** — the **lead experiment**: does the
  spine reproduce + exceed the hand-authored composite syntheses?

## Free/local stack (CLAUDE.md — no paid LLM API)

- Embeddings: Ollama `nomic-embed-text` on Pearl Star (768-dim; free stand-in for
  BGE-m3), with a consolidated disk cache. Local `sentence-transformers` is used
  automatically if installed.
- Clustering: `leidenalg` + `python-igraph` (fallback: `networkx`
  greedy-modularity).
- Reader Council: Ollama `gemma3:27b` (native `format=json`, the free
  Outlines-equivalent).
- `numpy`, `scikit-learn`, `pyyaml`.

## Run

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"   # optional
PYTHONPATH=. python3 -m ei.run_all          # builds every P0 artifact -> artifacts/ei_p0/
PYTHONPATH=. python3 -m pytest ei/tests -q  # unit tests
```

Requires Pearl Star reachable (ssh alias `pearl_star`) for embeddings + the
Reader Council. Everything else is pure CPU.

## Integrity guarantees honored

1. **provenance-by-construction** — every atom carries a real `teacher_id`; the
   gate hard-fails missing provenance.
2. **no homogenization** — spine roots record **every** contributing teacher and
   atom; traditions are never collapsed.
4. **fidelity-as-floor** — Φ is a hard feasibility floor, not a weighted term.
8. **EI never speaks AS a teacher** — spine labels are *extracted* phrases; the
   council speaks AS a *reader*, never as the author.
