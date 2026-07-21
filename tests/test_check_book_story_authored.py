#!/usr/bin/env python3
"""Unit tests for scripts/ci/check_book_story_authored.py (Lane 01,
docs/agent_prompt_packs/20260721_bestseller_atom_flow/01_ci_gate_research_fit_and_story_authored.md).

Advisory-mode contract under test:
  - unbound research_fit → WARN + book_acceptance_stamp.json written, exit 0
  - --strict flips the same finding to exit 1 (documented, off-by-default)
  - a missing/unreadable target is always a hard error (exit 1) regardless
    of --strict, since that is a real I/O problem, not a binding judgment.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.ci.check_book_story_authored import (
    STAMP_FILENAME,
    BookAuditUnreadableError,
    classify_research_fit,
    evaluate_book_target,
    main,
    stamp_book_acceptance,
)


def _write_audit(book_dir: Path, audit: dict) -> Path:
    book_dir.mkdir(parents=True, exist_ok=True)
    audit_path = book_dir / "enrichment_audit.json"
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    return audit_path


def test_classify_bound_mode_with_spine_pins() -> None:
    bound, reason = classify_research_fit(
        {
            "research_fit": {
                "mode": "research_fit_v1",
                "spine_pins": [{"chapter": 1, "arc_position": "recognition", "status": "PINNED"}],
            }
        }
    )
    assert bound is True
    assert reason == ""


def test_classify_skipped_no_story_atoms() -> None:
    bound, reason = classify_research_fit(
        {
            "research_fit": {"mode": "skipped", "skip_reason": "no_story_atoms: courage"},
            "research_fit_skip_reason": "no_story_atoms: courage",
        }
    )
    assert bound is False
    assert "no_story_atoms" in reason


def test_classify_bare_empty_dict_is_unbound_equivalent_to_no_story_atoms() -> None:
    """The real-world case (seed 43001 + every current proof-root book):
    research_fit: {} with no mode/skip_reason at all."""
    bound, reason = classify_research_fit({"research_fit": {}})
    assert bound is False
    assert "no_story_atoms" in reason or "legacy_planner" in reason


def test_classify_missing_research_fit_key_is_unbound() -> None:
    bound, reason = classify_research_fit({})
    assert bound is False
    assert reason


def test_classify_active_mode_missing_structure_is_unbound() -> None:
    bound, reason = classify_research_fit({"research_fit": {"mode": "research_fit_v1"}})
    assert bound is False
    assert "research_fit_v1" in reason


def test_evaluate_book_target_stamps_unbound(tmp_path: Path) -> None:
    book_dir = tmp_path / "cell_43001"
    _write_audit(book_dir, {"research_fit": {}})
    bound, reason, stamp = evaluate_book_target(book_dir)
    assert bound is False
    assert stamp["research_fit_bound"] is False
    assert stamp["acceptance_layer"] == "structurally_clear_only"
    assert stamp["research_fit_unbound_reason"] == reason

    stamp_path = book_dir / STAMP_FILENAME
    assert stamp_path.is_file()
    on_disk = json.loads(stamp_path.read_text())
    assert on_disk == stamp


def test_evaluate_book_target_stamps_bound_with_no_cap(tmp_path: Path) -> None:
    book_dir = tmp_path / "cell_bound"
    _write_audit(
        book_dir,
        {
            "research_fit": {
                "mode": "twelve_shape_continuity",
                "motif_ledger": {"book_idea": "x"},
            }
        },
    )
    bound, reason, stamp = evaluate_book_target(book_dir)
    assert bound is True
    assert reason == ""
    assert stamp["research_fit_bound"] is True
    assert "acceptance_layer" not in stamp


def test_stamp_book_acceptance_clears_stale_cap_on_rebind(tmp_path: Path) -> None:
    audit_path = _write_audit(tmp_path, {"research_fit": {}})
    stamp_book_acceptance(audit_path, bound=False, reason="no_story_atoms: x")
    stamp = stamp_book_acceptance(audit_path, bound=True, reason="")
    assert stamp["research_fit_bound"] is True
    assert "acceptance_layer" not in stamp
    assert "research_fit_unbound_reason" not in stamp


def test_evaluate_book_target_missing_audit_raises(tmp_path: Path) -> None:
    with pytest.raises(BookAuditUnreadableError):
        evaluate_book_target(tmp_path / "no_such_book")


def test_cli_advisory_default_exits_zero_on_unbound(tmp_path: Path) -> None:
    book_dir = tmp_path / "cell_a"
    _write_audit(book_dir, {"research_fit": {}})
    assert main(["--book-dir", str(book_dir)]) == 0
    assert (book_dir / STAMP_FILENAME).is_file()


def test_cli_strict_exits_one_on_unbound(tmp_path: Path) -> None:
    book_dir = tmp_path / "cell_b"
    _write_audit(book_dir, {"research_fit": {}})
    assert main(["--book-dir", str(book_dir), "--strict"]) == 1


def test_cli_exits_zero_on_bound_even_with_strict(tmp_path: Path) -> None:
    book_dir = tmp_path / "cell_c"
    _write_audit(
        book_dir,
        {"research_fit": {"mode": "research_fit_v1", "spine_pins": [{"status": "PINNED"}]}},
    )
    assert main(["--book-dir", str(book_dir), "--strict"]) == 0


def test_cli_missing_target_is_hard_error_regardless_of_strict(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"
    assert main(["--book-dir", str(missing)]) == 1
    assert main(["--book-dir", str(missing), "--strict"]) == 1


def test_cli_no_targets_returns_two() -> None:
    assert main([]) == 2


def test_cli_no_stamp_flag_skips_write(tmp_path: Path) -> None:
    book_dir = tmp_path / "cell_d"
    _write_audit(book_dir, {"research_fit": {}})
    assert main(["--book-dir", str(book_dir), "--no-stamp"]) == 0
    assert not (book_dir / STAMP_FILENAME).is_file()
