"""
ei.run_all — generate EVERY P0 artifact on the real corpus -> artifacts/ei_p0/.

Run:  PYTHONPATH=. python3 -m ei.run_all

Produces (all REAL outputs, no mock data):
  artifacts/ei_p0/
    ceg.json                              (P0.1 — the CEG interface)
    spine_nodes.yaml                      (P0.1 — the Spine interface; spine == CEG)
    spine_summary.json                    (P0.1 — universal roots + provenance)
    spine_viz.html                        (P0.1 — visualization)
    composite_reproduction_result.json    (P0.1 LEAD EXPERIMENT — reproduce + exceed)
    fitness_ranking.json                  (P0.2 — T x E x F-floor Pareto over real atom-sets)
    reader_council_report.json            (P0.3 — persona felt-responses on a real book)
    provenance_gate_report.json           (P0.4 — doctrine gate + negative control)
    felt_arc_report.json                  (P0.5 — somatic_state_fit on a real book)

Free/local only. Embeddings + Reader Council need Pearl Star (Ollama); everything
else is pure CPU. Steps degrade gracefully and report what ran.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

from . import config as C
from . import corpus as corp
from . import spine as spine_mod
from . import fitness as fit
from . import provenance_gate as pg
from . import felt_arc as fa
from . import reader_council as rc
from . import ollama_client as oc
from .experiments import composite_reproduction as exp
from . import spine_viz


def run_spine_and_experiment(atoms, out: Path, resolution: float = 4.0) -> dict:
    """P0.1: discover the spine at a fitting resolution + the lead experiment."""
    res = exp.run(resolution=resolution)
    result = res.get("spine_result_obj")
    if result is not None:
        paths = spine_mod.write_artifacts(result, out)
        spine_viz.write_spine_viz(result, out / "spine_viz.html")
        (out / "spine_summary.json").write_text(json.dumps({
            "n_atoms": result.n_atoms,
            "n_roots": len(result.nodes),
            "n_universal_roots": len(result.universal_nodes),
            "modularity": result.modularity,
            "cluster_backend": result.backend,
            "embedding_backend": result.embedding_backend,
            "params": result.params,
            "universal_roots": [
                {"node_id": n.node_id, "label": n.label, "n_teachers": n.n_teachers,
                 "teachers": n.teachers, "size": n.size, "keywords": n.keywords}
                for n in result.universal_nodes
            ],
        }, indent=2, ensure_ascii=False), encoding="utf-8")
    exp.write_report(res, out)
    return {k: v for k, v in res.items() if k != "spine_result_obj"}


def run_fitness_demo(atoms, out: Path) -> dict:
    """
    P0.2: rank REAL atom-sequences with T x E x Phi-floor Pareto.

    Build several candidate "mini-books" from real atoms:
      - SINGLE-TEACHER coherent sequences (high fidelity, expected feasible)
      - A DELIBERATELY-CONTAMINATED sequence (one teacher's atoms + a synthetic
        forbidden atom) -> expected INFEASIBLE (proves the floor bites)
      - A RANDOM grab-bag (low T, mixed) -> feasible but low on the front
    """
    random.seed(42)
    teachers = ["ahjan", "adi_da", "sai_ma", "maat"]
    candidates = {}

    # coherent single-teacher sequences (varied atom types = a real mini-book arc)
    arc_types = ["HOOK", "SCENE", "COMPRESSION", "REFLECTION", "PIVOT", "INTEGRATION", "TAKEAWAY"]
    for tid in teachers:
        seq = []
        for at in arc_types:
            pool = corp.load_atoms(teacher_ids=[tid], atom_types=[at])
            if pool:
                seq.append(pool[0])
        if len(seq) >= 4:
            candidates[f"coherent::{tid}"] = seq

    # contaminated: ahjan arc + a synthetic forbidden atom -> must be infeasible
    contaminated = list(candidates.get("coherent::ahjan", []))[:5] + [pg.forbidden_test_case()]
    candidates["contaminated::ahjan+forbidden"] = contaminated

    # random grab-bag across teachers
    alla = corp.load_atoms()
    candidates["random::mixed"] = random.sample(alla, 7)

    # embed everything once via the shared map
    pre = spine_mod.build_embedding_map(alla, include_doctrines=False)
    emb, meta_id, _, _, id_to_row = pre
    emb_by_id = {mid: emb[id_to_row[mid]] for mid in meta_id}
    # synthetic forbidden atom isn't in the corpus embedding -> embed it alone
    extra = [a for seq in candidates.values() for a in seq if a.atom_id not in emb_by_id]
    if extra:
        ev = oc.embed([a.text for a in extra])
        for i, a in enumerate(extra):
            emb_by_id[a.atom_id] = ev[i]

    scored = []
    for name, seq in candidates.items():
        fv = fit.evaluate_sequence(seq, emb_by_id=emb_by_id)
        scored.append((name, fv))

    ranking = fit.pareto_rank(scored)
    ranking["candidate_detail"] = {
        name: {"T": fv.T, "E": fv.E, "phi": fv.phi, "feasible": fv.feasible,
               "n_atoms": len(seq), "violations": fv.violations, "detail": fv.detail}
        for (name, fv), (_, seq) in zip(scored, candidates.items())
    }
    (out / "fitness_ranking.json").write_text(json.dumps(ranking, indent=2, ensure_ascii=False),
                                              encoding="utf-8")
    return ranking


def run_provenance_gate(atoms, out: Path) -> dict:
    """P0.4: full-corpus gate + the negative control."""
    report = pg.run_gate(atoms)
    fake = pg.forbidden_test_case()
    neg = pg.check_atom_against_rules(fake, pg.compile_rules(["ahjan"]), cross_teacher=False)
    neg_feasible, _ = pg.is_sequence_feasible([fake])
    payload = {
        **report.summary(),
        "negative_control": {
            "synthetic_atom": fake.body,
            "tripped_rules": [v.rule_text for v in neg],
            "blocked": (not neg_feasible),
            "exit_criterion_met": (len(neg) >= 1 and not neg_feasible),
        },
        "note": ("Provenance is EXACT (every atom maps to a known teacher). Framing "
                 "detection is LEXICAL (term-density + proximity + negation guard) — a "
                 "coarse free first-pass; true stance detection (X-is vs X-is-not) is a "
                 "P1 semantic/NLI need. Cross-teacher trips show where one tradition's "
                 "language would violate another's doctrine if atoms were mixed."),
        "sample_cross_teacher_violations": [
            {"atom_id": v.atom_id, "atom_teacher": v.teacher_id,
             "rule_teacher": v.rule_teacher, "rule": v.rule_text}
            for v in report.cross_teacher_violations[:8]
        ],
    }
    (out / "provenance_gate_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                                                    encoding="utf-8")
    return payload


def run_felt_arc(out: Path) -> dict:
    """P0.5: somatic_state_fit on a real (anxiety) gold-ref book."""
    book = corp.pick_gold_ref(topic="anxiety") or corp.find_gold_ref_books()[0]
    text = corp.load_gold_ref(book)
    rep = fa.somatic_state_fit(text)
    payload = {
        "book": book.name,
        "book_words": len(text.split()),
        "somatic_state_fit": rep.somatic_state_fit,
        "valence_rmse": rep.valence_rmse,
        "arousal_rmse": rep.arousal_rmse,
        "observation_before_intervention_ok": rep.observation_before_intervention_ok,
        "notes": rep.notes,
        "arc": [
            {"chapter": i + 1, "role": rep.intended[i]["role"],
             "intended_valence": rep.intended[i]["intended_valence"],
             "intended_arousal": rep.intended[i]["intended_arousal"],
             "measured_valence": m["valence"], "measured_arousal": m["arousal"],
             "vad_hits": m["n_vad_hits"]}
            for i, m in enumerate(rep.measured)
        ],
        "vad_licence_flag": C.FELT_ARC["vad_licence_flag"],
        "citations": "grounds nervous-system claims in a transparent VAD lexicon (RCG-007); "
                     "measures prose against the spine's intended pedagogy arc (RCG-022)",
    }
    (out / "felt_arc_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                                             encoding="utf-8")
    return payload


def run_reader_council(out: Path) -> dict:
    """P0.3: convene the council on a real gold-ref book."""
    book = corp.pick_gold_ref(topic="anxiety") or corp.find_gold_ref_books()[0]
    rep = rc.convene(book)
    payload = rc.report_to_dict(rep)
    (out / "reader_council_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                                                   encoding="utf-8")
    return payload


def main():
    C.ensure_dirs()
    out = C.ARTIFACTS_OUT
    atoms = corp.load_atoms()
    summary = {}

    print("[P0.4] provenance + doctrine gate ...", flush=True)
    summary["provenance_gate"] = run_provenance_gate(atoms, out)

    print("[P0.5] felt-arc estimator ...", flush=True)
    summary["felt_arc"] = run_felt_arc(out)

    print("[P0.1] spine/CEG discovery + lead experiment ...", flush=True)
    summary["spine_experiment"] = run_spine_and_experiment(atoms, out)

    print("[P0.2] multi-objective fitness demo ...", flush=True)
    summary["fitness"] = run_fitness_demo(atoms, out)

    print("[P0.3] reader council ...", flush=True)
    try:
        summary["reader_council"] = run_reader_council(out)
    except Exception as e:
        summary["reader_council"] = {"error": str(e)}

    (out / "run_all_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                             encoding="utf-8")
    print(f"\nDONE. artifacts in {out}", flush=True)
    return summary


if __name__ == "__main__":
    main()
