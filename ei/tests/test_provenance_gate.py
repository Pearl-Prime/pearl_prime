"""Unit tests for ei.provenance_gate (P0.4) — CPU-only."""
from ei import provenance_gate as pg
from ei import corpus as corp


def test_rules_compile_from_all_teachers():
    rules = pg.compile_rules()
    assert len(rules) >= 50
    kinds = {r.kind for r in rules}
    assert "forbidden_claim" in kinds


def test_negative_control_blocks_known_forbidden_claim():
    """The #1517 P0 exit criterion: the gate BLOCKS a known forbidden claim."""
    fake = pg.forbidden_test_case()  # claims "Buddhism as abstract intellectual system"
    rules = [r for r in pg.compile_rules(["ahjan"])]
    viols = pg.check_atom_against_rules(fake, rules)
    assert len(viols) >= 1
    assert any("Buddhism" in v.rule_text for v in viols)


def test_forbidden_sequence_is_infeasible():
    fake = pg.forbidden_test_case()
    feasible, viols = pg.is_sequence_feasible([fake])
    assert feasible is False
    assert viols


def test_missing_provenance_is_violation():
    from ei.corpus import Atom
    orphan = Atom(atom_id="X", teacher_id="not_a_real_teacher",
                  atom_type="HOOK", band="universal", body="hello world")
    bad = pg.check_provenance([orphan])
    assert "X" in bad
    feasible, _ = pg.is_sequence_feasible([orphan])
    assert feasible is False


def test_clean_real_atoms_are_feasible():
    # a small set of one teacher's own atoms should not trip that teacher's doctrine
    atoms = corp.load_atoms(teacher_ids=["adi_da"], atom_types=["COMPRESSION"])[:5]
    assert atoms
    feasible, viols = pg.is_sequence_feasible(atoms)
    assert feasible is True, f"clean atoms flagged: {[v.rule_text for v in viols]}"
