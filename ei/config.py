"""
ei.config — central configuration for the EI P0 build.

CRITICAL: §13 of the #1516 strengthened-architecture spec lists OPEN QUESTIONS
that are operator-gated and explicitly NOT decided this session. We parameterize
them as config with honest defaults + a [GATED] marker. The P0 prototypes READ
these values; they NEVER hardcode an answer. Changing the answer is a one-line
config edit, not a code change.

  §13.1 real-signal source of truth   -> FITNESS["real_signal_source"]   [GATED]
  §13.2 tau_Phi fidelity floor         -> FITNESS["tau_phi"]              [GATED]
  §13.3 validation data (held-out)     -> FITNESS["validation_holdout"]  [GATED]
  §13.4 build tiering (Pearl Star/CPU) -> EMBED["backend"]               [decided: local-first]
  §13.5 cap entry ratification         -> out of scope (no hot-file edit this session)
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo roots. The package is corpus-relative so it runs from the worktree OR
# the main tree without edits.
# ---------------------------------------------------------------------------
_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parents[1]  # .../ei/config.py -> repo root

SOURCE_OF_TRUTH = REPO_ROOT / "SOURCE_OF_TRUTH"
TEACHER_BANKS = SOURCE_OF_TRUTH / "teacher_banks"
COMPOSITE_DOCTRINE = SOURCE_OF_TRUTH / "composite_doctrine"
CONFIG_DIR = REPO_ROOT / "config"
PIPELINE_EXAMPLES = REPO_ROOT / "artifacts" / "pipeline_examples"
KB_ENTRIES = REPO_ROOT / "artifacts" / "research" / "kb" / "entries.jsonl"

# Output dir for all advisory artifacts.
ARTIFACTS_OUT = REPO_ROOT / "artifacts" / "ei_p0"
CACHE_DIR = ARTIFACTS_OUT / ".cache"


# ---------------------------------------------------------------------------
# Embedding backend (free/local only; CLAUDE.md bans paid LLM APIs).
# ---------------------------------------------------------------------------
EMBED = {
    # "auto": prefer local sentence-transformers if importable, else Ollama on
    # Pearl Star. Both are free/local. (§13.4 build-tiering: local-first.)
    "backend": os.environ.get("EI_EMBED_BACKEND", "auto"),  # auto | sentence_transformers | ollama
    # sentence-transformers model (CPU). BGE-m3 is the spec'd choice; all-MiniLM
    # is a lighter fallback if BGE is not cached.
    "st_model": os.environ.get("EI_ST_MODEL", "BAAI/bge-small-en-v1.5"),
    # Ollama model used for embeddings when backend=ollama (Pearl Star, GPU).
    # nomic-embed-text is a small, purpose-built embedding model (768-dim,
    # ~274MB) -> 10-50x faster than using a 14B generation model for embeddings.
    # This is the free/local stand-in for the spec's BGE-m3.
    "ollama_embed_model": os.environ.get("EI_OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    # deterministic on-disk cache so re-runs are reproducible and cheap.
    "cache": True,
}

# How to reach Pearl Star Ollama. On this box the Tailscale HTTP host does not
# always resolve for curl, but the ssh alias works -> we tunnel through ssh.
OLLAMA = {
    "ssh_host": os.environ.get("EI_PEARL_STAR_SSH", "pearl_star"),
    "http_url": os.environ.get("EI_OLLAMA_URL", "http://pearl_star:11434"),
    # "auto": try http first, fall back to ssh. ssh is the proven path here.
    "transport": os.environ.get("EI_OLLAMA_TRANSPORT", "auto"),  # auto | http | ssh
    "council_model": os.environ.get("EI_COUNCIL_MODEL", "gemma3:27b"),
    "timeout_s": int(os.environ.get("EI_OLLAMA_TIMEOUT", "180")),
}


# ---------------------------------------------------------------------------
# P0.1 Contemplative Spine / CEG discovery.
# ---------------------------------------------------------------------------
SPINE = {
    # Leiden resolution: higher -> more, smaller communities. 1.0 is the
    # canonical default; the spine experiment sweeps a small grid.
    "leiden_resolution": float(os.environ.get("EI_LEIDEN_RES", "1.0")),
    # k for the k-NN similarity graph fed to Leiden.
    "knn_k": int(os.environ.get("EI_KNN_K", "15")),
    # cosine-similarity edge threshold (drop weak edges before clustering).
    "edge_min_sim": float(os.environ.get("EI_EDGE_MIN_SIM", "0.30")),
    # community detection backend: leiden (igraph/leidenalg) preferred; networkx
    # greedy-modularity is the pure-python fallback.
    "backend": os.environ.get("EI_SPINE_BACKEND", "auto"),  # auto | leiden | networkx
    # a community must have atoms from >= this many distinct teachers to count as
    # a UNIVERSAL spine root (provenance-by-construction; integrity guarantee 2:
    # no homogenization -> we record every teacher, never collapse them).
    "universal_min_teachers": int(os.environ.get("EI_UNIVERSAL_MIN_TEACHERS", "3")),
    "random_seed": 42,
}


# ---------------------------------------------------------------------------
# P0.2 multi-objective fitness. §13 unknowns live here, flagged [GATED].
# ---------------------------------------------------------------------------
FITNESS = {
    # ---- §13.2 tau_Phi : the spiritual-fidelity FLOOR. [GATED — operator decides] ----
    # Φ in [0,1]; a sequence is INFEASIBLE if Φ < tau_phi. This is a HARD floor
    # (feasibility), NOT a weighted term. 0.60 is an HONEST DEFAULT, not a
    # decision. The operator sets the real value at ratification (§13.2:
    # "what minimum fidelity is non-negotiable for a Pearl Prime general book?").
    "tau_phi": float(os.environ.get("EI_TAU_PHI", "0.60")),
    "tau_phi_gated": True,  # surfaced in every artifact as operator-pending.

    # ---- §13.1 real-signal source of truth. [GATED] ----
    # Which engagement/sales feed is authoritative for E. Until decided, E uses
    # FREE PROXY signals derived from the corpus + bestseller-pattern research
    # (honest, labeled "proxy"). NOT a sales feed.
    "real_signal_source": os.environ.get("EI_REAL_SIGNAL", "corpus_proxy"),  # corpus_proxy | <gated feed>
    "real_signal_gated": True,

    # ---- §13.3 validation data (held-out outcome). [GATED] ----
    # What held-out outcome validates the fitness. Until instrumented, the
    # composite_doctrine corpus is used as a FREE validation oracle for Φ
    # (it is human-authored cross-teacher synthesis = a fidelity reference).
    "validation_holdout": os.environ.get("EI_VAL_HOLDOUT", "composite_doctrine_oracle"),
    "validation_holdout_gated": True,

    # T (therapeutic) and E (engagement) are objectives to MAXIMIZE; Φ is the floor.
    # Pareto / ε-feasibility ranking — explicitly NOT a weighted sum (the EMA the
    # #1516 audit flagged: 45 records / 7 positive, scorer & learner tune
    # different dims, no fidelity objective at all).
    "objective_sense": {"T": "max", "E": "max"},
    "epsilon": float(os.environ.get("EI_FITNESS_EPSILON", "0.0")),  # ε-feasibility slack on the floor
}


# ---------------------------------------------------------------------------
# P0.5 felt-arc (valence + arousal). NRC-VAD licensing is risk #4 in the #1517
# roadmap -> we ship a small open-licensed VAD lexicon subset and FLAG it.
# ---------------------------------------------------------------------------
FELT_ARC = {
    "vad_lexicon": "vendored_open_subset",  # see ei/data/vad_lexicon.tsv ; flagged for licence review
    "vad_licence_flag": "REVIEW: confirm open licence before commercial ship (roadmap risk #4)",
    "smooth_window": 3,  # sentence smoothing window for the arc
}


def all_teacher_ids() -> list[str]:
    """The 15 teacher banks (directories under teacher_banks/ with a doctrine.yaml)."""
    if not TEACHER_BANKS.exists():
        return []
    out = []
    for p in sorted(TEACHER_BANKS.iterdir()):
        if p.is_dir() and (p / "doctrine" / "doctrine.yaml").exists():
            out.append(p.name)
    return out


def composite_topics() -> list[str]:
    """The composite-doctrine struggle topics (dirs with a CANONICAL.txt)."""
    if not COMPOSITE_DOCTRINE.exists():
        return []
    out = []
    for p in sorted(COMPOSITE_DOCTRINE.iterdir()):
        if p.is_dir() and (p / "CANONICAL.txt").exists():
            out.append(p.name)
    return out


def ensure_dirs() -> None:
    ARTIFACTS_OUT.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
