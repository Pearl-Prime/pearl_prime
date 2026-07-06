"""Flagship 12-shape planner reconciliation."""
from phoenix_v4.planning.chapter_object_continuity import (
    assert_twelve_shape_plan,
    load_chapter_continuity_plan,
)


def test_flagship_plan_reconciles() -> None:
    plan = load_chapter_continuity_plan("gen_z_professionals", "anxiety")
    assert plan
    assert_twelve_shape_plan(plan)
    characters = {str(c.get("character")) for c in plan}
    assert characters == {"Priya"}


def test_twelve_shape_routes_spine_only() -> None:
    from phoenix_v4.planning.legacy_template_loader import resolve_template_library

    assert (
        resolve_template_library("anxiety", "gen_z_professionals", "extended_book_2h")
        == "spine_only"
    )
