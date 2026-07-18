"""
ei — Enlightened Intelligence P0 build (additive + advisory).

A NEW, self-contained package that READS the Phoenix Omega corpora (teacher
banks, composite doctrine, personas, spines, gold-ref books) and produces
ADVISORY artifacts. It does NOT modify the production EI v2 scorer, the
production config, or the planners. P0 = additive + advisory; production-wiring
is a gated P1 follow-up into the #1516 spec.

Materializes the CONVERGED P0 set from both EI roadmaps (#1517 ceiling +
#1516 floor). The two roadmaps independently landed on the same architecture;
the P0 objects are the same under different names:

  - Contemplative Spine (#1517 P0.1)            == Composite Essence Graph / CEG (#1516 P0.2)
  - Multi-objective T x E x F fitness (#1517)   == Explicit multi-objective fitness (#1516 P0.1)
  - QD Garden / qNEHVI-BO / GA-for-atoms        == P1+ (NOT built this session)

Modules:
  ei.config            — central config; §13 open-questions parameterized (never hardcoded)
  ei.corpus            — read-only loaders for all corpora
  ei.ollama_client     — free/local embeddings + LLM via Pearl Star Ollama (ssh or http)
  ei.spine             — P0.1 Contemplative Spine / CEG discovery (Leiden over atom embeddings)
  ei.fitness           — P0.2 multi-objective T x E x F fitness (F = hard feasibility floor)
  ei.reader_council    — P0.3 Reader Council advisory gate (persona agents on Ollama)
  ei.provenance_gate   — P0.4 doctrine / forbidden-claim provenance gate
  ei.felt_arc          — P0.5 felt-arc valence+arousal state estimator (NRC-VAD)

Free/local only (CLAUDE.md): no paid LLM API. Stack: sentence-transformers OR
Ollama embeddings, leidenalg/igraph, networkx, scikit-learn, numpy.
"""

__version__ = "0.1.0-p0"

# Convergence name-alignment for the P1 handoff into #1516's spec.
SPINE_IS_CEG = True  # the discovered Spine artifact materializes #1516's ceg.json interface.
