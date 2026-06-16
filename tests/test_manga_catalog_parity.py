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

# Owner exception (2026-05-20): registry-only teachers retained for doctrine/voice
# usage but NOT assigned as manga brand primaries. These teachers were migrated
# off brand primary status by recent OPDs but remain canonical:
#   - junko: PR #1221 (OPD-111 Phase 4) catalog migrated to miyuki; junko stays
#     in registry as the canonical channeling/light-language teacher
#   - joshin: PR #1208 (OPD-105 Phase 2) Cognitive Clarity catalog migrated to
#     kenjin; joshin stays in registry for cross-references / doctrine
# A teacher being in the registry but not a manga brand primary is now a valid
# architectural state. Add new entries here when migrations create more.
REGISTRY_ONLY_NON_BRAND_TEACHERS = frozenset({"junko", "joshin"})


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

    # Post-OPD-105/OPD-111 architecture: registry is a SUPERSET of brand plan
    # teachers. Some teachers (REGISTRY_ONLY_NON_BRAND_TEACHERS) remain in the
    # registry for doctrine/voice purposes after being migrated off brand
    # primary status. Brand plan teachers must all exist in the registry.
    assert teachers_in_plan <= reg_ids, (
        f"manga brand plan references teachers not in registry: "
        f"{sorted(teachers_in_plan - reg_ids)!r}"
    )
    assert reg_ids - teachers_in_plan == REGISTRY_ONLY_NON_BRAND_TEACHERS, (
        f"registry vs brand-plan delta drifted from expected "
        f"REGISTRY_ONLY_NON_BRAND_TEACHERS: "
        f"expected={sorted(REGISTRY_ONLY_NON_BRAND_TEACHERS)!r} "
        f"actual={sorted(reg_ids - teachers_in_plan)!r}"
    )
    assert taiwan_primary_slugs == ["bright_presence_tw"]
    assert brand_blocks["bright_presence_tw"]["teacher"] == "adi_da"

    global_primary_teachers = {
        str(b["teacher"])
        for b in brand_blocks.values()
        if isinstance(b, dict) and b.get("primary_lane") != "taiwan"
    }
    # Same architectural shift: registry-only-non-brand teachers + Taiwan-only
    # teacher land outside the global-primary set. Test that the residual matches
    # exactly the union (catches drift in either direction).
    assert reg_ids - global_primary_teachers == (
        TAIWAN_ONLY_MANGA_TEACHERS | REGISTRY_ONLY_NON_BRAND_TEACHERS
    )


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
