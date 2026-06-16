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
    """No NEW parse failures and no NEW over-match signatures outside the baseline."""
    report = GUARD.sweep()
    assert report["new_parse_failures"] == [], (
        "NEW strict-parse failures (PR #1590-class over-match regression): "
        + ", ".join(report["new_parse_failures"][:20])
    )
    assert report["new_overmatch_signatures"] == [], (
        "NEW metadata-less '## <LABEL> vNN' over-match headers: "
        + ", ".join(report["new_overmatch_signatures"][:20])
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
