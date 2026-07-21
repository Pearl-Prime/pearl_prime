"""Regression guard for the PR #1590 atom-header over-match (task_fe5d9042).

PR #1590 (SHA 0d1cf1520) prepended ``## `` to legitimate body-text lines that read
like header tokens, promoting them into metadata-less ``## <LABEL> vNN`` headers and
breaking ``assembly_compiler._parse_canonical_txt`` on 1,215 CANONICAL.txt files —
collapsing their engine pools to NO_STORY_POOL. These tests lock in:

  1. the tree-wide parse-sweep is GREEN (no parse failure or over-match signature
     outside the documented pre-existing baseline);
  2. the over-match signature detector fires on a #1590-shaped file and is silent on a
     well-formed one;
  3. the corporate_managers/financial_anxiety engine pools (the named broken tuple)
     parse cleanly and yield a non-empty STORY pool (no NO_STORY_POOL).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GUARD_PATH = REPO_ROOT / "scripts" / "ci" / "check_canonical_atom_parse_sweep.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("canonical_parse_sweep_guard", GUARD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GUARD = _load_guard()


def test_parse_sweep_is_green_tree_wide() -> None:
    """No NEW parse failures, over-match signatures, or stub-content signatures outside baseline."""
    report = GUARD.sweep()
    assert report["new_parse_failures"] == [], (
        "NEW strict-parse failures (PR #1590-class over-match regression): "
        + ", ".join(report["new_parse_failures"][:20])
    )
    assert report["new_overmatch_signatures"] == [], (
        "NEW metadata-less '## <LABEL> vNN' over-match headers: "
        + ", ".join(report["new_overmatch_signatures"][:20])
    )
    assert report["new_stub_failures"] == [], (
        "NEW bare-header-text stub prose (check D): "
        + ", ".join(report["new_stub_failures"][:20])
    )
    assert report["ok"] is True


def test_overmatch_signature_detects_1590_shape() -> None:
    """The exact #1590 corruption: a body line promoted to a metadata-less header."""
    mangled = (
        "## RECOGNITION v01\n"
        "---\n"
        "path: the number that won't move\n"
        "BAND: 2\n"
        "---\n"
        "## RECOGNITION v02\n"  # <-- this was the BODY of v01, wrongly promoted by #1590
        "---\n"
        "\n"
        "## RECOGNITION v03\n"
        "---\n"
        "path: the email about stock options\n"
        "---\n"
        "RECOGNITION v04\n"
        "---\n"
    )
    assert GUARD.overmatch_signature_hits(mangled) >= 1


def test_overmatch_signature_silent_on_wellformed() -> None:
    """A correctly-authored bank (each block has real metadata + a body line) is clean."""
    good = (
        "## RECOGNITION v01\n"
        "---\n"
        "path: the number that won't move\n"
        "BAND: 2\n"
        "---\n"
        "RECOGNITION v02\n"  # body line == role/version, but it is BODY, not a header
        "---\n"
        "## RECOGNITION v03\n"
        "---\n"
        "path: the email about stock options\n"
        "---\n"
        "Some real body prose here.\n"
        "---\n"
    )
    assert GUARD.overmatch_signature_hits(good) == 0


def test_named_financial_anxiety_tuple_resolves_story_pool() -> None:
    """corporate_managers/financial_anxiety/{overwhelm,shame,spiral} render a pool."""
    import sys

    sys.path.insert(0, str(REPO_ROOT))
    from phoenix_v4.gates.check_tuple_viability import _load_story_atoms_for_engine

    atoms_root = REPO_ROOT / "atoms"
    for engine in ("overwhelm", "shame", "spiral"):
        pool = _load_story_atoms_for_engine(
            atoms_root, "corporate_managers", "financial_anxiety", engine
        )
        assert pool, f"NO_STORY_POOL for financial_anxiety/{engine} (PR #1590 regression)"


def test_named_burnout_overwhelm_pool_resolves_story_pool() -> None:
    """corporate_managers/burnout/overwhelm — the STORY pool #1623 missed and #1630 restored."""
    import sys

    sys.path.insert(0, str(REPO_ROOT))
    from phoenix_v4.gates.check_tuple_viability import _load_story_atoms_for_engine

    pool = _load_story_atoms_for_engine(
        REPO_ROOT / "atoms", "corporate_managers", "burnout", "overwhelm"
    )
    assert pool, "NO_STORY_POOL for burnout/overwhelm (PR #1590 over-match; restored #1630)"


def test_no_english_story_pool_carries_overmatch() -> None:
    """Check (C): an English base STORY pool with the #1590 over-match signature is ALWAYS a
    regression, independent of the baseline. This is the invariant whose absence let the
    burnout/overwhelm residual ship under #1623."""
    report = GUARD.sweep()
    assert report["story_pool_overmatch"] == [], (
        "English STORY pool(s) carry an over-match signature (NO_STORY_POOL) and must be "
        "RESTORED, never baselined: " + ", ".join(report["story_pool_overmatch"][:20])
    )


def test_stub_signature_detects_unpromoted_defect7_shape() -> None:
    """Check (D): the un-repaired sibling of the #1590 defect — a body that is the bare
    next-header label, but NEVER got promoted to a phantom ``##`` header, so it parses
    cleanly and would otherwise ship as one-line "prose" in a real book."""
    stubbed = (
        "## RECOGNITION v01\n"
        "---\n"
        "path: the number that won't move\n"
        "BAND: 2\n"
        "---\n"
        "RECOGNITION v02\n"  # <-- un-authored: the bare label, never promoted to a header
        "---\n"
        "\n"
        "## RECOGNITION v03\n"
        "---\n"
        "path: the email about stock options\n"
        "---\n"
        "Marco reads the email a fourth time, hunting for a tone problem that isn't there.\n"
        "---\n"
    )
    assert GUARD.stub_prose_signature_hits(stubbed) == 1


def test_stub_signature_silent_on_wellformed() -> None:
    """A block with real authored prose is clean, even if it happens to reference a role name."""
    good = (
        "## RECOGNITION v01\n"
        "---\n"
        "path: x\n"
        "BAND: 2\n"
        "---\n"
        "She thought about RECOGNITION v02 of the pattern and moved on with her day.\n"
        "---\n"
    )
    assert GUARD.stub_prose_signature_hits(good) == 0


def test_stub_signature_silent_on_legit_terse_bandfill() -> None:
    """Deliberately terse but REAL 'band-fill' prose (a full sentence, not a bare label)
    must never false-positive — the signature requires an EXACT bare-token match."""
    bandfill = (
        "## RECOGNITION v06\n"
        "---\n"
        "path: x\n"
        "BAND: 5\n"
        "---\n"
        "Crisis. Breakthrough. The moment of maximum intensity.\n"
        "---\n"
    )
    assert GUARD.stub_prose_signature_hits(bandfill) == 0


def test_stub_signature_distinct_from_overmatch_signature() -> None:
    """(D) and (B) target complementary, non-overlapping shapes: an unpromoted stub body
    (D) is not also flagged as an over-matched phantom header (B), and vice versa."""
    stubbed = (
        "## RECOGNITION v01\n---\npath: x\nBAND: 2\n---\nRECOGNITION v02\n---\n"
    )
    assert GUARD.stub_prose_signature_hits(stubbed) == 1
    assert GUARD.overmatch_signature_hits(stubbed) == 0

    overmatched = (
        "## RECOGNITION v01\n---\npath: x\nBAND: 2\n---\n"
        "## RECOGNITION v02\n---\n\n"  # promoted phantom header -> next block's metadata
        "## RECOGNITION v03\n---\npath: y\n---\nReal prose.\n---\n"
    )
    assert GUARD.overmatch_signature_hits(overmatched) >= 1
    assert GUARD.stub_prose_signature_hits(overmatched) == 0


def test_is_english_story_pool_classification() -> None:
    """Check (C) targets only English base STORY pools — not locale variants, not role banks."""
    atoms = GUARD.ATOMS_ROOT
    assert GUARD.is_english_story_pool(atoms / "corporate_managers/burnout/overwhelm/CANONICAL.txt")
    assert GUARD.is_english_story_pool(atoms / "first_responders/anxiety/spiral/CANONICAL.txt")
    # locale variants are a separate CJK backlog -> excluded
    assert not GUARD.is_english_story_pool(
        atoms / "corporate_managers/burnout/overwhelm/locales/ja-JP/CANONICAL.txt"
    )
    # non-STORY role banks -> excluded (they legitimately fail the STORY parser; baseline-able)
    assert not GUARD.is_english_story_pool(atoms / "first_responders/anxiety/QUOTE/CANONICAL.txt")
    assert not GUARD.is_english_story_pool(atoms / "corporate_managers/burnout/HOOK/CANONICAL.txt")
