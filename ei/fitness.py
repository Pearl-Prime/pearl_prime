"""
ei.fitness — P0.2 MULTI-OBJECTIVE T x E x F FITNESS PROTOTYPE (advisory).

THE convergence (same object, two names):
  #1516 P0.1 "Explicit multi-objective fitness (THE highest-leverage piece)"
  #1517      "T x E x F fitness, F a hard floor"
  -> ONE fitness prototype. It returns the 3-vector (T, E, Φ) and ranks by
     Pareto / ε-feasibility, explicitly NOT a weighted sum.

WHY NOT A WEIGHTED SUM (the #1516 audit's sharpest finding):
  Today's EI v2 collapses to a scalar tuned by an EMA learner on 45 records / 7
  positive; the scorer and the learner optimize DIFFERENT dimension sets and
  there is NO fidelity objective at all. This prototype retires that: T and E are
  separate objectives to maximize, and Φ (spiritual fidelity) is a HARD
  FEASIBILITY FLOOR — a sequence with Φ < τ_Φ is INFEASIBLE and cannot be
  ranked above a feasible one, no matter how high its T or E.

§13 UNKNOWNS ARE PARAMETERIZED, NEVER HARDCODED (see ei.config.FITNESS):
  - τ_Φ floor (§13.2)            -> config, flagged [GATED]; honest default 0.60.
  - real-signal source (§13.1)    -> E uses a labeled CORPUS PROXY until the
                                     operator names an authoritative feed.
  - validation holdout (§13.3)    -> Φ validated against the composite_doctrine
                                     oracle until a held-out outcome is instrumented.

WHAT T, E, Φ ARE IN THE P0 PROTOTYPE (all free/local, honest proxies):
  T (therapeutic): coverage of the somatic felt-arc shape (ei.felt_arc) +
     type-diversity of the sequence (a book that only HOOKs has low T). [0,1]
  E (engagement) : embedding-space novelty/flow — low adjacent-atom redundancy
     (no two neighbors saying the same thing) + lexical hook density. Labeled a
     PROXY for the real engagement signal (§13.1). [0,1]
  Φ (fidelity)   : provenance + own-doctrine cleanliness from ei.provenance_gate
     (the hard floor), softened to [0,1] for reporting but THRESHOLDED as binary
     feasibility. A sequence that trips a teacher's own doctrine is infeasible.

OUTPUT IS ADVISORY: it ranks candidate atom-sequences and emits a Pareto menu.
It does NOT modify the production scorer, config, or planners.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict

import numpy as np

from . import config as C
from . import corpus as corp
from . import felt_arc as fa
from . import ollama_client as oc
from . import provenance_gate as pg


@dataclass
class FitnessVector:
    T: float
    E: float
    phi: float                 # Φ reported in [0,1]
    feasible: bool             # Φ >= τ_Φ (the HARD floor) AND provenance clean
    tau_phi: float
    tau_phi_gated: bool
    violations: list = field(default_factory=list)
    detail: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# T — therapeutic: felt-arc coverage + structural type diversity
# ---------------------------------------------------------------------------
def _therapeutic(atoms) -> tuple[float, dict]:
    text = "\n".join(a.text for a in atoms)
    # felt-arc coherence against the somatic intended arc (proxy for therapeutic shape)
    n_ch = min(len(atoms), 12) or 1
    rep = fa.somatic_state_fit(text, n_chapters=n_ch)
    arc_fit = rep.somatic_state_fit
    # type diversity: a healthy therapeutic sequence uses varied atom roles
    types = {a.atom_type for a in atoms}
    type_div = min(1.0, len(types) / 6.0)  # 6+ distinct roles -> full credit
    T = 0.6 * arc_fit + 0.4 * type_div
    return float(T), {"arc_fit": arc_fit, "type_diversity": round(type_div, 4),
                      "observation_before_intervention_ok": rep.observation_before_intervention_ok}


# ---------------------------------------------------------------------------
# E — engagement PROXY: embedding novelty (anti-redundancy) + hook density
# ---------------------------------------------------------------------------
def _engagement(atoms, emb_by_id: dict) -> tuple[float, dict]:
    # adjacent-atom redundancy: high cosine between consecutive atoms = stalling
    vecs = [emb_by_id[a.atom_id] for a in atoms if a.atom_id in emb_by_id]
    if len(vecs) >= 2:
        V = np.vstack(vecs)
        adj = np.sum(V[:-1] * V[1:], axis=1)  # cosine of neighbors (normalized)
        redundancy = float(np.clip(adj.mean(), 0, 1))
        novelty = 1.0 - redundancy
    else:
        novelty = 0.5
    # hook density: presence of HOOK/SCENE/STORY atoms keeps readers moving
    engaging_types = {"HOOK", "SCENE", "STORY", "PIVOT"}
    hook_density = sum(1 for a in atoms if a.atom_type in engaging_types) / max(len(atoms), 1)
    E = 0.7 * novelty + 0.3 * min(1.0, hook_density * 3.0)
    return float(np.clip(E, 0, 1)), {"novelty": round(novelty, 4),
                                     "hook_density": round(hook_density, 4),
                                     "signal": C.FITNESS["real_signal_source"]}


# ---------------------------------------------------------------------------
# Φ — fidelity: the hard floor (provenance + own-doctrine cleanliness)
# ---------------------------------------------------------------------------
def _fidelity(atoms) -> tuple[float, bool, list, dict]:
    feasible, viols = pg.is_sequence_feasible(atoms)
    # report Φ in [0,1]: 1.0 if clean; degrade by fraction of atoms in violation
    n = max(len(atoms), 1)
    bad_atoms = {v.atom_id for v in viols}
    # also penalize missing provenance
    known = set(C.all_teacher_ids())
    no_prov = sum(1 for a in atoms if a.teacher_id not in known)
    phi = 1.0 - (len(bad_atoms) + no_prov) / n
    phi = float(np.clip(phi, 0, 1))
    return phi, feasible, viols, {"violating_atoms": len(bad_atoms), "no_provenance": no_prov}


def evaluate_sequence(atoms, emb_by_id: dict | None = None,
                      tau_phi: float | None = None) -> FitnessVector:
    """Score one candidate atom-sequence as a (T, E, Φ) vector with a hard Φ floor."""
    tau = tau_phi if tau_phi is not None else C.FITNESS["tau_phi"]
    if emb_by_id is None:
        texts = [a.text for a in atoms]
        e = oc.embed(texts)
        emb_by_id = {a.atom_id: e[i] for i, a in enumerate(atoms)}

    T, tdet = _therapeutic(atoms)
    E, edet = _engagement(atoms, emb_by_id)
    phi, prov_feasible, viols, fdet = _fidelity(atoms)

    # the HARD floor: feasible iff provenance-clean AND Φ >= τ_Φ (with ε slack)
    eps = C.FITNESS["epsilon"]
    feasible = prov_feasible and (phi >= tau - eps)

    return FitnessVector(
        T=round(T, 4), E=round(E, 4), phi=round(phi, 4),
        feasible=feasible, tau_phi=tau, tau_phi_gated=C.FITNESS["tau_phi_gated"],
        violations=[{"atom_id": v.atom_id, "rule": v.rule_text} for v in viols[:10]],
        detail={"T": tdet, "E": edet, "phi": fdet},
    )


# ---------------------------------------------------------------------------
# Pareto ranking (NOT a weighted sum)
# ---------------------------------------------------------------------------
def _dominates(a: FitnessVector, b: FitnessVector) -> bool:
    """a Pareto-dominates b on (T, E) — feasibility handled separately."""
    return (a.T >= b.T and a.E >= b.E) and (a.T > b.T or a.E > b.E)


def pareto_rank(candidates: list[tuple[str, FitnessVector]]) -> dict:
    """
    Rank candidates by ε-feasibility Pareto:
      1. ALL feasible candidates rank above ALL infeasible ones (the hard floor).
      2. Within the feasible set, compute Pareto fronts on (T, E).
      3. Infeasible candidates are listed but flagged 'below floor'.
    Returns the front structure + a flat ranked list.
    """
    feas = [(name, fv) for name, fv in candidates if fv.feasible]
    infeas = [(name, fv) for name, fv in candidates if not fv.feasible]

    # Pareto fronts within feasible
    fronts = []
    remaining = list(feas)
    while remaining:
        front = []
        for name, fv in remaining:
            if not any(_dominates(other, fv) for on, other in remaining if on != name):
                front.append((name, fv))
        if not front:  # safety
            front = remaining
        fronts.append(front)
        front_names = {n for n, _ in front}
        remaining = [(n, fv) for n, fv in remaining if n not in front_names]

    ranked = []
    for fi, front in enumerate(fronts):
        for name, fv in sorted(front, key=lambda x: -(x[1].T + x[1].E)):
            ranked.append({"name": name, "front": fi + 1, "feasible": True,
                           "T": fv.T, "E": fv.E, "phi": fv.phi})
    for name, fv in sorted(infeas, key=lambda x: -(x[1].T + x[1].E)):
        ranked.append({"name": name, "front": None, "feasible": False,
                       "T": fv.T, "E": fv.E, "phi": fv.phi,
                       "reason": f"below tau_phi floor ({fv.tau_phi}) or provenance violation"})

    return {
        "n_candidates": len(candidates),
        "n_feasible": len(feas),
        "n_infeasible": len(infeas),
        "n_fronts": len(fronts),
        "tau_phi": C.FITNESS["tau_phi"],
        "tau_phi_gated": C.FITNESS["tau_phi_gated"],
        "real_signal_source": C.FITNESS["real_signal_source"],
        "real_signal_gated": C.FITNESS["real_signal_gated"],
        "ranking_method": "epsilon-feasibility Pareto on (T,E) with Phi as a HARD floor (NOT a weighted sum)",
        "pareto_front_1": [{"name": n, "T": fv.T, "E": fv.E, "phi": fv.phi} for n, fv in fronts[0]] if fronts else [],
        "ranked": ranked,
    }
