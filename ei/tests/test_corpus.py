"""Unit tests for ei.corpus (CPU-only; no Pearl Star needed)."""
from ei import config as C
from ei import corpus as corp


def test_fifteen_teacher_banks():
    ids = C.all_teacher_ids()
    assert len(ids) == 15, f"expected 15 teacher banks, got {len(ids)}"
    assert "ahjan" in ids and "sai_ma" in ids


def test_atoms_load_with_provenance():
    # load one bank fully to keep the test fast under FS contention
    atoms = corp.load_atoms(teacher_ids=["adi_da"])
    assert len(atoms) > 50
    for a in atoms:
        assert a.atom_id
        assert a.teacher_id == "adi_da"
        assert a.text.strip()
        assert a.atom_type


def test_doctrine_has_forbidden_claims():
    doc = corp.load_doctrine("ahjan")
    assert doc is not None
    assert any("Buddhism" in fc for fc in doc.forbidden_claims)
    assert doc.prohibited_outcomes  # non-empty


def test_composite_oracle_is_anxiety_only():
    # verified real-corpus fact: only anxiety has authored content on origin/main
    comps = corp.all_composites()
    assert len(comps) >= 10
    topics = {c.topic for c in comps}
    assert topics == {"anxiety"}, f"expected anxiety-only oracle, got {topics}"
    # each synthesis has a thesis + body
    for c in comps:
        assert c.thesis and c.body


def test_ei_v2_kb_is_marketing_not_doctrine():
    # the motivating fact: EI v2 loads the 15-entry marketing KB, not the doctrine
    kb = corp.load_ei_v2_kb()
    assert len(kb) == 15
    assert "source_type" in kb[0]


def test_gold_ref_books_present():
    books = corp.find_gold_ref_books()
    assert len(books) >= 5
    assert all(b.name.startswith("book_") and "15min" in b.name for b in books)
