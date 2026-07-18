"""Unit tests for brand↔teacher resolution (teacher_brand_resolver).

Guards the FIX-C wiring: the manga render path must resolve a brand's
primary teacher (e.g. devotion_path -> sai_ma) instead of the global
'ahjan' default.
"""
from phoenix_v4.planning.teacher_brand_resolver import (
    resolve_brand_for_teacher,
    resolve_teacher_for_brand,
)


def test_resolve_teacher_for_brand_known():
    assert resolve_teacher_for_brand("devotion_path") == "sai_ma"
    assert resolve_teacher_for_brand("stillness_press") == "ahjan"


def test_resolve_teacher_for_brand_unknown_returns_none():
    assert resolve_teacher_for_brand("not_a_brand") is None
    assert resolve_teacher_for_brand("") is None


def test_brand_teacher_round_trip():
    teacher = resolve_teacher_for_brand("devotion_path")
    assert teacher == "sai_ma"
    # Inverse resolution lands back on the home brand.
    assert resolve_brand_for_teacher(teacher) == "devotion_path"
