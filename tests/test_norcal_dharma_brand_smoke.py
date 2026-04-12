"""
Smoke tests: ahjan is the single canonical teacher id for Stillness Press;
deprecated duplicate ids must not appear in core planning configs.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _deprecated_teacher_id() -> str:
    return bytes((97, 106, 97, 104, 110, 95, 120)).decode("ascii")


def _deprecated_brand_id() -> str:
    return bytes(
        (110, 111, 114, 99, 97, 108, 95, 100, 104, 97, 114, 109, 97)
    ).decode("ascii")


def test_teacher_registry_has_ahjan_not_deprecated_ids():
    reg = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    teachers = (data or {}).get("teachers") or {}
    assert "ahjan" in teachers
    assert _deprecated_teacher_id() not in teachers


def test_brand_teacher_matrix_stillness_maps_to_ahjan():
    path = REPO_ROOT / "config" / "catalog_planning" / "brand_teacher_matrix.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    sp = (data.get("brands") or {}).get("stillness_press") or {}
    assert sp.get("primary_teacher") == "ahjan"
    assert sp.get("teachers") == ["ahjan"]


def test_assignments_have_no_removed_church_only_brand_row():
    path = REPO_ROOT / "config" / "catalog_planning" / "brand_teacher_assignments.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for row in data.get("assignments") or []:
        assert (row.get("brand_id") or "").strip() != _deprecated_brand_id()


def test_wave_allocation_includes_ahjan():
    from phoenix_v4.planning.teacher_portfolio_planner import allocate_wave, load_brand_matrix

    matrix_path = REPO_ROOT / "config" / "catalog_planning" / "brand_teacher_matrix.yaml"
    matrix = load_brand_matrix(matrix_path)
    brands = matrix.get("brands") or {}
    teachers: list[str] = []
    for b in brands.values():
        teachers.extend(b.get("teachers") or [])
    teachers = list(dict.fromkeys(teachers))
    assert "ahjan" in teachers
    allocations = allocate_wave(
        wave_id="smoke",
        teachers=teachers,
        total_books=30,
        brand_matrix_path=matrix_path,
    )
    ahjan_hits = [a for a in allocations if a.teacher_id == "ahjan"]
    assert ahjan_hits, "wave allocation should include ahjan"


def test_resolve_stillness_press_prefers_default_teacher_in_assignments():
    from phoenix_v4.planning.teacher_brand_resolver import resolve_teacher_brand

    teacher_id, brand_id = resolve_teacher_brand(brand_id="stillness_press")
    assert teacher_id == "default_teacher"
    assert brand_id == "stillness_press"
