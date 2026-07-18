"""
Unit tests for ei.fitness (P0.2).

Core logic (Pareto, hard floor) is tested WITHOUT embeddings using synthetic
FitnessVectors. The end-to-end evaluate_sequence test needs embeddings and skips
gracefully.
"""
import pytest

from ei import config as C
from ei import corpus as corp
from ei import fitness as fit
from ei import ollama_client as oc


def test_phi_is_a_hard_floor_not_a_weighted_term():
    """A high-T/high-E but INFEASIBLE candidate must rank below a feasible one."""
    feasible_low = fit.FitnessVector(T=0.30, E=0.30, phi=0.90, feasible=True,
                                     tau_phi=0.6, tau_phi_gated=True)
    infeasible_high = fit.FitnessVector(T=0.99, E=0.99, phi=0.10, feasible=False,
                                        tau_phi=0.6, tau_phi_gated=True)
    ranking = fit.pareto_rank([("infeasible_high", infeasible_high),
                               ("feasible_low", feasible_low)])
    # the feasible one must come first despite far lower T/E
    assert ranking["ranked"][0]["name"] == "feasible_low"
    assert ranking["ranked"][0]["feasible"] is True
    assert ranking["ranked"][-1]["name"] == "infeasible_high"
    assert ranking["ranked"][-1]["feasible"] is False


def test_ranking_is_not_a_weighted_sum():
    method = fit.pareto_rank([])["ranking_method"]
    assert "NOT a weighted sum" in method
    assert "HARD floor" in method


def test_pareto_front_is_nondominated():
    a = fit.FitnessVector(T=0.9, E=0.2, phi=0.9, feasible=True, tau_phi=0.6, tau_phi_gated=True)
    b = fit.FitnessVector(T=0.2, E=0.9, phi=0.9, feasible=True, tau_phi=0.6, tau_phi_gated=True)
    c = fit.FitnessVector(T=0.5, E=0.5, phi=0.9, feasible=True, tau_phi=0.6, tau_phi_gated=True)
    d = fit.FitnessVector(T=0.1, E=0.1, phi=0.9, feasible=True, tau_phi=0.6, tau_phi_gated=True)
    r = fit.pareto_rank([("a", a), ("b", b), ("c", c), ("d", d)])
    front1 = {x["name"] for x in r["pareto_front_1"]}
    # a and b are non-dominated extremes; d is dominated by all -> not in front 1
    assert "a" in front1 and "b" in front1
    assert "d" not in front1


def test_gated_params_surfaced():
    r = fit.pareto_rank([])
    assert r["tau_phi_gated"] is True
    assert r["real_signal_gated"] is True


def _embeddings_available() -> bool:
    try:
        return oc.embed(["the body is not your enemy"]).shape[0] == 1
    except Exception:
        return False


@pytest.mark.skipif(not _embeddings_available(),
                    reason="embeddings unavailable (no cache and Pearl Star unreachable)")
def test_evaluate_real_sequence_returns_vector():
    atoms = corp.load_atoms(teacher_ids=["ahjan"])[:8]
    fv = fit.evaluate_sequence(atoms)
    assert 0.0 <= fv.T <= 1.0
    assert 0.0 <= fv.E <= 1.0
    assert 0.0 <= fv.phi <= 1.0
    assert isinstance(fv.feasible, bool)
    # ahjan's own atoms should not trip ahjan's own doctrine -> Phi high, feasible
    assert fv.phi >= 0.6
    assert fv.feasible is True
