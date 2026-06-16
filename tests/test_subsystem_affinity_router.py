"""Smoke + behavior tests for scripts.coordination.subsystem_affinity_router.

This is the minimal regression net landed alongside the router itself.
The Wave 1 closeout for /pearl-help + /pearl-pre-task promised richer
coverage (8 cases); those skills + their tests will ship in a follow-up
PR. These tests at minimum prove the documented 4-function API works
and the router reads SUBSYSTEM_AUTHORITY_MAP.tsv correctly.
"""

from __future__ import annotations

from scripts.coordination.subsystem_affinity_router import (
    ReviewBoard,
    get_subsystem_for_path,
    load_subsystem_rows,
    marketing_or_research_touched,
    route_for_paths,
    route_for_subsystem,
)


def test_load_subsystem_rows_returns_known_subsystems() -> None:
    rows = load_subsystem_rows()
    assert len(rows) > 0, "SUBSYSTEM_AUTHORITY_MAP.tsv must be non-empty"
    subsystem_ids = {r.subsystem_id for r in rows}
    # These three are stable anchors that have shipped for months.
    assert "core_pipeline" in subsystem_ids
    assert "manga_pipeline" in subsystem_ids
    assert "brand_admin" in subsystem_ids


def test_route_for_subsystem_manga_pipeline_owner_and_docs() -> None:
    board = route_for_subsystem("manga_pipeline")
    assert isinstance(board, ReviewBoard)
    assert board.owner == "Pearl_Dev"
    assert any("AI_MANGA_PIPELINE_SUMMARY" in d for d in board.authority_docs), (
        "manga_pipeline must surface its canonical authority doc"
    )


def test_route_for_subsystem_unknown_returns_review_board_with_no_owner_or_default() -> None:
    board = route_for_subsystem("does-not-exist")
    # Router contract: never raises on unknown subsystem; returns a
    # board (empty or defaulted) so callers don't have to null-check.
    assert isinstance(board, ReviewBoard)


def test_marketing_or_research_touched_flags_marketing_path() -> None:
    assert marketing_or_research_touched(["funnel/landing.html"]) is True
    assert marketing_or_research_touched(["somatic_exercise_freebee_apps/x.html"]) is True


def test_marketing_or_research_touched_flags_research_path_marker() -> None:
    assert marketing_or_research_touched(["artifacts/research/some_audit.md"]) is True
    assert (
        marketing_or_research_touched(["phoenix_v4/quality/ei_v2/scorer.py"]) is True
    )


def test_marketing_or_research_touched_returns_false_for_neutral_path() -> None:
    assert marketing_or_research_touched(["scripts/util/helper.py"]) is False
    assert marketing_or_research_touched([]) is False


def test_get_subsystem_for_path_unmatched_returns_none() -> None:
    assert get_subsystem_for_path("README.md") is None


def test_route_for_paths_returns_review_board_shape() -> None:
    board = route_for_paths(["scripts/coordination/subsystem_affinity_router.py"])
    assert isinstance(board, ReviewBoard)
    # Owner is always set (router defaults to coordinator when no path matches).
    assert isinstance(board.owner, str) and board.owner
    assert isinstance(board.reviewers, list)
    assert isinstance(board.authority_docs, list)
    assert isinstance(board.adjacent_subsystems, list)
