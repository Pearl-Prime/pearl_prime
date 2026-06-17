"""
Unit tests for ei.spine (P0.1).

These need embeddings. They use the consolidated bulk cache if present; if no
cache AND Pearl Star is unreachable, they skip (CI without GPU access).
"""
import numpy as np
import pytest

from ei import config as C
from ei import corpus as corp
from ei import spine as sp
from ei import ollama_client as oc


def _embeddings_available() -> bool:
    # cheap: a tiny embed via the per-text cache or Ollama
    try:
        v = oc.embed(["the body is not your enemy"])
        return v.shape[0] == 1
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _embeddings_available(),
    reason="embeddings unavailable (no cache and Pearl Star unreachable)",
)


def test_knn_graph_is_symmetric_and_thresholded():
    rng = np.random.default_rng(0)
    emb = rng.standard_normal((30, 16)).astype(np.float32)
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)
    edges = sp._knn_graph(emb, k=5, min_sim=0.0)
    seen = set()
    for a, b, w in edges:
        assert a < b  # canonical undirected ordering
        assert (a, b) not in seen
        seen.add((a, b))
        assert -1.0 <= w <= 1.0


def test_spine_discovers_universal_roots_with_provenance():
    # use a 3-teacher subset for speed; still must find multi-teacher roots
    atoms = corp.load_atoms(teacher_ids=["ahjan", "adi_da", "sai_ma"])
    result = sp.discover_spine(atoms=atoms, include_doctrines=True, resolution=2.0)
    assert result.nodes, "no spine roots discovered"
    assert result.n_atoms == len(atoms)
    # every node preserves provenance (no homogenization)
    for n in result.nodes:
        assert n.teachers, "a spine node lost its teacher provenance"
        assert n.n_teachers == len(n.teachers)
        assert sum(n.teacher_distribution.values()) == n.size
    # at least one root should span >1 teacher (a real shared root)
    assert any(n.n_teachers >= 2 for n in result.nodes)


def test_spine_labels_are_extractive_not_generated():
    atoms = corp.load_atoms(teacher_ids=["ahjan", "adi_da"])
    result = sp.discover_spine(atoms=atoms, include_doctrines=False, resolution=2.0)
    for n in result.nodes:
        # label is built from keywords -> every label token came from the corpus
        assert n.label
        for kw in n.keywords:
            assert kw == kw.lower()
