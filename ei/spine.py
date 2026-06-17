"""
ei.spine — P0.1 CONTEMPLATIVE SPINE / COMPOSITE ESSENCE GRAPH (CEG) discovery.

The converged heart of both roadmaps:
  #1517 P0.1 "Living Wisdom Graph v0 / Contemplative Spine"
  #1516 P0.2 "Spiritual-root synthesis -> Composite Essence Graph (CEG)"
  -> ONE object. The artifact materializes BOTH interfaces:
       spine_nodes.yaml  (#1517)
       ceg.json          (#1516)

Pipeline (pure local, no paid API):
  1. embed every approved atom (+ the 15 teacher doctrines) with a local encoder
     (sentence-transformers if available, else Ollama on Pearl Star).
  2. build a k-NN cosine similarity graph (drop edges below edge_min_sim).
  3. run Leiden community detection (igraph/leidenalg) -> communities.
       fallback: networkx greedy-modularity if leidenalg is unavailable.
  4. a community is a UNIVERSAL SPINE ROOT iff it draws atoms from
     >= universal_min_teachers distinct teachers (provenance-by-construction;
     NO homogenization — every contributing teacher + atom is recorded).
  5. name each root from its highest-centrality member atoms (extractive;
     EI never speaks AS a teacher — names are descriptive labels, not prose).

Integrity guarantees honored:
  #2 no homogenization  — per-teacher provenance preserved on every node.
  #4 fidelity-as-floor  — universality is measured, never assumed.
  #8 EI never speaks AS a teacher — node labels are extracted phrases, not
     generated teaching.

Output is ADVISORY. It does not touch production config or the EI v2 scorer.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np

from . import config as C
from . import corpus as corp
from . import ollama_client as oc


# ---------------------------------------------------------------------------
# data structures
# ---------------------------------------------------------------------------
@dataclass
class SpineNode:
    node_id: str
    label: str                       # extractive descriptive label
    size: int                        # number of atoms
    teachers: list[str]              # distinct contributing teachers (provenance)
    n_teachers: int
    is_universal: bool               # >= universal_min_teachers
    atom_types: dict                 # type -> count
    exemplar_atom_ids: list[str]     # most central atoms (provenance)
    exemplar_texts: list[str]        # their bodies (read-only quotes, attributed)
    keywords: list[str]              # top extracted terms
    teacher_distribution: dict       # teacher -> count


def _knn_graph(emb: np.ndarray, k: int, min_sim: float):
    """Return edge list [(i,j,weight)] for a symmetric k-NN cosine graph."""
    # emb is L2-normalized -> cosine = dot product
    sims = emb @ emb.T
    n = emb.shape[0]
    np.fill_diagonal(sims, -1.0)
    edges = {}
    for i in range(n):
        # top-k neighbours
        idx = np.argpartition(sims[i], -k)[-k:]
        for j in idx:
            w = float(sims[i, j])
            if w < min_sim:
                continue
            a, b = (i, int(j)) if i < j else (int(j), i)
            if a == b:
                continue
            # keep max weight for the undirected edge
            if (a, b) not in edges or w > edges[(a, b)]:
                edges[(a, b)] = w
    return [(a, b, w) for (a, b), w in edges.items()]


def _cluster_leiden(n: int, edges, resolution: float, seed: int):
    import igraph as ig
    import leidenalg

    g = ig.Graph(n=n, edges=[(a, b) for a, b, _ in edges])
    g.es["weight"] = [w for _, _, w in edges]
    part = leidenalg.find_partition(
        g, leidenalg.RBConfigurationVertexPartition,
        weights="weight", resolution_parameter=resolution, seed=seed,
    )
    labels = np.array(part.membership, dtype=int)
    return labels, ("leiden", float(part.modularity))


def _cluster_networkx(n: int, edges, resolution: float):
    import networkx as nx
    from networkx.algorithms.community import greedy_modularity_communities

    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a, b, w in edges:
        g.add_edge(a, b, weight=w)
    comms = greedy_modularity_communities(g, weight="weight", resolution=resolution)
    labels = np.full(n, -1, dtype=int)
    for ci, nodes in enumerate(comms):
        for v in nodes:
            labels[v] = ci
    # isolated nodes get their own singleton communities
    nxt = labels.max() + 1 if labels.size else 0
    for v in range(n):
        if labels[v] == -1:
            labels[v] = nxt
            nxt += 1
    try:
        mod = nx.algorithms.community.modularity(
            g, comms, weight="weight", resolution=resolution
        )
    except Exception:
        mod = float("nan")
    return labels, ("networkx_greedy_modularity", float(mod))


def _choose_backend():
    b = C.SPINE["backend"]
    if b in ("auto", "leiden"):
        try:
            import igraph  # noqa: F401
            import leidenalg  # noqa: F401

            return "leiden"
        except Exception:
            if b == "leiden":
                raise
    return "networkx"


# ---------------------------------------------------------------------------
# extractive labelling (no generation; EI never speaks as a teacher)
# ---------------------------------------------------------------------------
_STOP = set("""the a an and or but if then of to in on for with as is are was were be been being
this that these those it its their your you we they i he she them his her our not no do does did
have has had will would can could should may might must at by from into about over under again
very just so than too more most some any all each one two three what when where who how why which
your you yours their there here own same other another any every either neither also only out up
down off above below between through during before after while because about against among""".split())


def _keywords(texts: list[str], top: int = 8) -> list[str]:
    cnt = Counter()
    for t in texts:
        for w in "".join(ch.lower() if ch.isalnum() else " " for ch in t).split():
            if len(w) > 3 and w not in _STOP:
                cnt[w] += 1
    return [w for w, _ in cnt.most_common(top)]


def _label_from_keywords(kws: list[str]) -> str:
    return " / ".join(kws[:3]) if kws else "(unlabeled root)"


def _central_atoms(emb: np.ndarray, member_idx: list[int], top: int = 4) -> list[int]:
    """Most central = highest mean cosine to other members (medoid-ish)."""
    if len(member_idx) <= top:
        return member_idx
    sub = emb[member_idx]
    centroid = sub.mean(axis=0)
    centroid /= (np.linalg.norm(centroid) + 1e-9)
    scores = sub @ centroid
    order = np.argsort(-scores)[:top]
    return [member_idx[i] for i in order]


# ---------------------------------------------------------------------------
# main entry
# ---------------------------------------------------------------------------
@dataclass
class SpineResult:
    nodes: list[SpineNode]
    n_atoms: int
    n_teachers: int
    backend: str
    modularity: float
    embedding_backend: str
    params: dict
    universal_min_teachers: int

    @property
    def universal_nodes(self) -> list[SpineNode]:
        return [n for n in self.nodes if n.is_universal]


def build_embedding_map(atoms, include_doctrines: bool = True, use_bulk_cache: bool = True):
    """
    Embed atoms (+ optional doctrines) ONCE and return everything the spine and
    the experiments need, so no caller re-embeds. Returns
    (emb, meta_id, meta_teacher, meta_type, id_to_row).

    BULK CACHE: the per-text .npy cache means 2,400+ slow file-opens under FS
    contention. We additionally persist ONE consolidated (matrix.npy + manifest)
    keyed by the corpus signature, so a warm run is a SINGLE file read.
    """
    texts = [a.text for a in atoms]
    meta_teacher = [a.teacher_id for a in atoms]
    meta_type = [a.atom_type for a in atoms]
    meta_id = [a.atom_id for a in atoms]
    if include_doctrines:
        for tid in C.all_teacher_ids():
            dtxt = corp.doctrine_corpus_text(tid)
            if dtxt:
                texts.append(dtxt)
                meta_teacher.append(tid)
                meta_type.append("DOCTRINE")
                meta_id.append(f"{tid}_DOCTRINE")

    if use_bulk_cache:
        import hashlib
        sig = hashlib.sha256(
            (oc.embedding_backend_name() + "||" + "||".join(texts)).encode("utf-8")
        ).hexdigest()[:16]
        C.ensure_dirs()
        mat_p = C.CACHE_DIR / f"bulk_{sig}.npy"
        if mat_p.exists():
            try:
                emb = np.load(mat_p)
                if emb.shape[0] == len(texts):
                    id_to_row = {aid: i for i, aid in enumerate(meta_id)}
                    return emb, meta_id, meta_teacher, meta_type, id_to_row
            except Exception:
                pass
        emb = oc.embed(texts)  # uses per-text cache if warm; else computes
        try:
            np.save(mat_p, emb)
        except Exception:
            pass
    else:
        emb = oc.embed(texts)

    id_to_row = {aid: i for i, aid in enumerate(meta_id)}
    return emb, meta_id, meta_teacher, meta_type, id_to_row


def discover_spine(atoms=None, include_doctrines: bool = True,
                   resolution: float | None = None, precomputed=None) -> SpineResult:
    """
    Run the full spine/CEG discovery on the real corpus.

    precomputed: optional tuple from build_embedding_map(...) to avoid re-embedding
    (used by the resolution sweep + the lead experiment so we embed only once).
    """
    if atoms is None:
        atoms = corp.load_atoms()
    resolution = resolution if resolution is not None else C.SPINE["leiden_resolution"]

    if precomputed is not None:
        emb, meta_id, meta_teacher, meta_type, _ = precomputed
        texts = None  # not needed; we use embeddings + ids
    else:
        emb, meta_id, meta_teacher, meta_type, _ = build_embedding_map(atoms, include_doctrines)
        texts = None

    # we still need member texts for keyword labelling -> map id->text
    id_to_text = {a.atom_id: a.text for a in atoms}
    for tid in C.all_teacher_ids():
        d = corp.doctrine_corpus_text(tid)
        if d:
            id_to_text[f"{tid}_DOCTRINE"] = d
    texts = [id_to_text.get(mid, "") for mid in meta_id]
    n = emb.shape[0]

    edges = _knn_graph(emb, k=C.SPINE["knn_k"], min_sim=C.SPINE["edge_min_sim"])

    backend = _choose_backend()
    if backend == "leiden":
        labels, (bname, mod) = _cluster_leiden(n, edges, resolution, C.SPINE["random_seed"])
    else:
        labels, (bname, mod) = _cluster_networkx(n, edges, resolution)

    # group members
    groups: dict[int, list[int]] = defaultdict(list)
    for i, lab in enumerate(labels):
        groups[int(lab)].append(i)

    umin = C.SPINE["universal_min_teachers"]
    nodes: list[SpineNode] = []
    for cid, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(members) < 2:
            continue  # skip singletons as spine roots
        t_dist = Counter(meta_teacher[i] for i in members)
        ty_dist = Counter(meta_type[i] for i in members)
        member_texts = [texts[i] for i in members]
        kws = _keywords(member_texts)
        central = _central_atoms(emb, members, top=4)
        node = SpineNode(
            node_id=f"spine_{len(nodes):03d}",
            label=_label_from_keywords(kws),
            size=len(members),
            teachers=sorted(t_dist.keys()),
            n_teachers=len(t_dist),
            is_universal=len(t_dist) >= umin,
            atom_types=dict(ty_dist),
            exemplar_atom_ids=[meta_id[i] for i in central],
            exemplar_texts=[texts[i][:280] for i in central],
            keywords=kws,
            teacher_distribution=dict(t_dist),
        )
        nodes.append(node)

    return SpineResult(
        nodes=nodes,
        n_atoms=len(atoms),
        n_teachers=len(set(a.teacher_id for a in atoms)),
        backend=bname,
        modularity=mod,
        embedding_backend=oc.embedding_backend_name(),
        params={
            "leiden_resolution": resolution,
            "knn_k": C.SPINE["knn_k"],
            "edge_min_sim": C.SPINE["edge_min_sim"],
            "include_doctrines": include_doctrines,
            "random_seed": C.SPINE["random_seed"],
        },
        universal_min_teachers=umin,
    )


def sweep_resolution(atoms=None, resolutions=(1.0, 2.0, 4.0, 8.0),
                     include_doctrines: bool = True) -> dict:
    """
    Embed ONCE, then run Leiden at several resolutions to find the granularity
    where the spine is fine enough to surface topic-specific invariants (more
    roots) while staying universal (each root spans many teachers). Returns a
    summary per resolution + the SpineResult objects.
    """
    if atoms is None:
        atoms = corp.load_atoms()
    precomputed = build_embedding_map(atoms, include_doctrines)
    out = {"resolutions": [], "results": {}}
    for res in resolutions:
        r = discover_spine(atoms=atoms, include_doctrines=include_doctrines,
                           resolution=res, precomputed=precomputed)
        out["resolutions"].append({
            "resolution": res,
            "n_roots": len(r.nodes),
            "n_universal": len(r.universal_nodes),
            "modularity": round(r.modularity, 4),
            "median_root_size": int(np.median([n.size for n in r.nodes])) if r.nodes else 0,
            "median_teachers_per_root": int(np.median([n.n_teachers for n in r.nodes])) if r.nodes else 0,
        })
        out["results"][res] = r
    return out


# ---------------------------------------------------------------------------
# serialization: BOTH the #1517 spine_nodes.yaml AND the #1516 ceg.json
# ---------------------------------------------------------------------------
def write_artifacts(result: SpineResult, out_dir: Path) -> dict:
    import yaml

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # #1516 ceg.json (the CEG interface): roots with provenance + convergence_strength
    ceg = {
        "_schema": "composite_essence_graph/v0",
        "_alias": "this IS the #1517 Contemplative Spine (spine == CEG)",
        "_advisory": True,
        "embedding_backend": result.embedding_backend,
        "cluster_backend": result.backend,
        "modularity": result.modularity,
        "params": result.params,
        "n_atoms": result.n_atoms,
        "n_teachers": result.n_teachers,
        "universal_min_teachers": result.universal_min_teachers,
        "roots": [],
    }
    for node in result.nodes:
        # convergence_strength = fraction of the 15 traditions represented
        conv = node.n_teachers / max(result.n_teachers, 1)
        ceg["roots"].append({
            "root_id": node.node_id,
            "label": node.label,
            "convergence_strength": round(conv, 4),
            "is_universal": node.is_universal,
            "size": node.size,
            "provenance": {
                "teachers": node.teachers,
                "teacher_distribution": node.teacher_distribution,
                "exemplar_atom_ids": node.exemplar_atom_ids,
            },
            "atom_types": node.atom_types,
            "keywords": node.keywords,
            "exemplars": node.exemplar_texts,
        })
    ceg_path = out_dir / "ceg.json"
    ceg_path.write_text(json.dumps(ceg, indent=2, ensure_ascii=False), encoding="utf-8")

    # #1517 spine_nodes.yaml (the Spine interface)
    spine_yaml = {
        "_schema": "contemplative_spine/v0",
        "_alias": "this IS the #1516 Composite Essence Graph (spine == CEG)",
        "_advisory": True,
        "embedding_backend": result.embedding_backend,
        "cluster_backend": result.backend,
        "modularity": result.modularity,
        "universal_roots": [
            {
                "node_id": n.node_id,
                "label": n.label,
                "n_teachers": n.n_teachers,
                "teachers": n.teachers,
                "size": n.size,
                "keywords": n.keywords,
            }
            for n in result.universal_nodes
        ],
        "all_nodes_count": len(result.nodes),
        "universal_nodes_count": len(result.universal_nodes),
    }
    spine_path = out_dir / "spine_nodes.yaml"
    spine_path.write_text(yaml.safe_dump(spine_yaml, sort_keys=False, allow_unicode=True),
                          encoding="utf-8")

    return {"ceg_json": str(ceg_path), "spine_nodes_yaml": str(spine_path)}
