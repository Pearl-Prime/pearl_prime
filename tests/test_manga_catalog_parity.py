from __future__ import annotations

import importlib.util
from collections import defaultdict
from pathlib import Path

import pytest
import yaml

from scripts.catalog.generate_full_catalog import iter_teacher_planning_rows

REPO = Path(__file__).resolve().parents[1]

LANE_PATH = REPO / "config/catalog_planning/teacher_brand_lane_assignments.yaml"
MANGA_PLAN_PATH = REPO / "config/manga/manga_brand_series_plan.yaml"
REGISTRY_PATH = REPO / "config/teachers/teacher_registry.yaml"
PROMPTS_PATH = REPO / "config/manga/teacher_character_prompts.yaml"

# Owner exception: Adi Da teacher-mode manga brand exists only on Taiwan (zh-TW).
TAIWAN_ONLY_MANGA_TEACHERS = frozenset({"adi_da"})


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_teacher_registry_ids_match_teacher_character_prompts() -> None:
    reg = _load(REGISTRY_PATH)
    reg_ids = frozenset((reg.get("teachers") or {}).keys())
    prompts = _load(PROMPTS_PATH)
    prompt_ids = frozenset((prompts.get("teachers") or {}).keys())
    assert reg_ids == prompt_ids, (
        f"registry vs teacher_character_prompts mismatch: "
        f"only_in_registry={reg_ids - prompt_ids!r} only_in_prompts={prompt_ids - reg_ids!r}"
    )


def test_manga_brand_teachers_cover_registry_with_taiwan_only_allowlist() -> None:
    reg = _load(REGISTRY_PATH)
    reg_ids = frozenset((reg.get("teachers") or {}).keys())
    manga = _load(MANGA_PLAN_PATH)
    brand_blocks = manga.get("brands") or {}
    teachers_in_plan: set[str] = set()
    taiwan_primary_slugs: list[str] = []
    for slug, block in brand_blocks.items():
        if not isinstance(block, dict):
            continue
        tid = block.get("teacher")
        assert tid, f"brand {slug!r} missing teacher"
        teachers_in_plan.add(str(tid))
        if block.get("primary_lane") == "taiwan":
            taiwan_primary_slugs.append(str(slug))

    assert teachers_in_plan == reg_ids
    assert taiwan_primary_slugs == ["bright_presence_tw"]
    assert brand_blocks["bright_presence_tw"]["teacher"] == "adi_da"

    global_primary_teachers = {
        str(b["teacher"])
        for b in brand_blocks.values()
        if isinstance(b, dict) and b.get("primary_lane") != "taiwan"
    }
    assert reg_ids - global_primary_teachers == TAIWAN_ONLY_MANGA_TEACHERS


def test_no_duplicate_teacher_per_lane_assignments() -> None:
    raw = _load(LANE_PATH)
    by_lane: dict[str, list[str]] = defaultdict(list)
    for lane, _bid, tid in iter_teacher_planning_rows(raw):
        by_lane[lane].append(tid)
    for lane, tids in sorted(by_lane.items()):
        assert len(tids) == len(set(tids)), f"lane {lane}: duplicate teacher ids in {tids!r}"


def test_taiwan_has_exactly_one_adi_da_brand() -> None:
    raw = _load(LANE_PATH)
    tw_adi = [bid for lane, bid, tid in iter_teacher_planning_rows(raw) if lane == "taiwan" and tid == "adi_da"]
    assert tw_adi == ["bright_presence_tw"]


def test_summary_counts_match_computed_lane_rows() -> None:
    raw = _load(LANE_PATH)
    summary = raw.get("summary") or {}
    teacher_total = len(iter_teacher_planning_rows(raw))
    assert teacher_total == summary["teacher_mode_brands"]["total"]

    std_n = len(summary["standard_mode_brands"]["base_names"])
    std_total = 12 * std_n
    assert std_total == summary["standard_mode_brands"]["total"]

    expected_instances = teacher_total + std_total
    assert expected_instances == summary["total_brand_instances"]


def test_manga_series_catalog_bounds_script_ok() -> None:
    script = REPO / "scripts/manga/validate_manga_series_catalog_bounds.py"
    spec = importlib.util.spec_from_file_location("validate_manga_series_catalog_bounds", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.main() == 0
