"""Tests for the Series Master Plan gate (manga process uplift Lane 06).

Mutation-tested per docs/agent_brief.txt §14: the golden fixture PASSES and
four surgical mutations each turn the gate RED for the named reason
(bad tiling / off-cadence / teacher named / stub marker). The real golden
example artifact on main must also PASS.

Run:
    PYTHONPATH=. python3 -m pytest tests/ci/test_manga_series_master_plan.py -v
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

import scripts.ci.check_manga_series_master_plan as gate

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "manga" / "series_master_plan"
GOLDEN_FIXTURE = FIXTURES / "golden_pass.master_plan.yaml"
GOLDEN_ARTIFACT = (
    REPO_ROOT
    / "artifacts"
    / "manga"
    / "series_master_plans"
    / "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying.master_plan.yaml"
)


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ── PASS paths ───────────────────────────────────────────────────────────────


def test_golden_fixture_passes():
    errors = gate.validate_master_plan(_load(GOLDEN_FIXTURE), path=GOLDEN_FIXTURE)
    assert errors == []


def test_golden_fixture_passes_via_cli():
    assert gate.main(["--plan", str(GOLDEN_FIXTURE)]) == 0


def test_real_golden_artifact_passes():
    assert GOLDEN_ARTIFACT.is_file(), "golden example master plan missing"
    errors = gate.validate_master_plan(_load(GOLDEN_ARTIFACT), path=GOLDEN_ARTIFACT)
    assert errors == []


# ── mutation fixtures (each must FAIL for the named reason) ─────────────────


@pytest.mark.parametrize(
    "fixture,expected_fragment",
    [
        ("mutation_bad_tiling.master_plan.yaml", "arcs must tile"),
        ("mutation_off_cadence.master_plan.yaml", "outside genre cadence"),
        ("mutation_teacher_named.master_plan.yaml", "brand teacher named"),
        ("mutation_stub_marker.master_plan.yaml", "stub marker"),
    ],
)
def test_mutation_fixture_fails(fixture: str, expected_fragment: str):
    path = FIXTURES / fixture
    errors = gate.validate_master_plan(_load(path), path=path)
    assert errors, f"{fixture} unexpectedly passed"
    assert any(expected_fragment in e for e in errors), errors
    assert gate.main(["--plan", str(path)]) == 1


# ── contract branches ────────────────────────────────────────────────────────


def test_null_shift_family_rejects_forced_shift():
    """healing has first_major_shift_by: null — forcing a shift must FAIL."""
    plan = _load(GOLDEN_ARTIFACT)
    plan["first_major_shift"] = {
        "arc_id": "cycle_01_the_alarm_in_four_rooms",
        "episode": 4,
        "description": "A forced status-quo shift that breaks the genre contract.",
    }
    errors = gate.validate_master_plan(plan)
    assert any("first_major_shift_by: null" in e for e in errors), errors


def test_null_shift_family_rejects_arc_level_shift():
    plan = _load(GOLDEN_ARTIFACT)
    plan["arcs"][0]["status_quo_shift"] = "The apartment burns down."
    errors = gate.validate_master_plan(plan)
    assert any("no-shift family" in e for e in errors), errors


def test_shift_family_requires_declared_shift():
    """mecha has first_major_shift_by: 30 — dropping the shift must FAIL."""
    plan = _load(GOLDEN_FIXTURE)
    plan["first_major_shift"] = None
    errors = gate.validate_master_plan(plan)
    assert any("first_major_shift must be declared" in e for e in errors), errors


def test_shift_beyond_family_cap_fails():
    plan = _load(GOLDEN_FIXTURE)
    plan["first_major_shift"]["episode"] = 60  # mecha cap: 30 +25% = 38
    plan["first_major_shift"]["arc_id"] = "arc_06_attrition_season"
    plan["arcs"][5]["status_quo_shift"] = "The wing is disbanded."
    errors = gate.validate_master_plan(plan)
    assert any("exceeds family first_major_shift_by" in e for e in errors), errors


def test_fixed_twelve_tiling_off_cadence_for_healing():
    """The old fixed-12 assumption must NOT validate against a [1,5]-range family."""
    plan = _load(GOLDEN_ARTIFACT)
    arcs = []
    for i in range(8):  # 8 arcs x 12 eps = 96 + final 4 = 100
        start = i * 12 + 1
        arcs.append(
            {
                **copy.deepcopy(plan["arcs"][0]),
                "arc_id": f"fixed12_{i+1}",
                "episode_start": start,
                "episode_end": start + 11,
                "detail_level": "outline",
            }
        )
    arcs.append(
        {
            **copy.deepcopy(plan["arcs"][0]),
            "arc_id": "fixed12_tail",
            "episode_start": 97,
            "episode_end": 100,
            "detail_level": "outline",
        }
    )
    for a in arcs:
        a.pop("episodes", None)
    plan["arcs"] = arcs
    errors = gate.validate_master_plan(plan)
    assert any("outside genre cadence" in e for e in errors), errors


def test_mode_mismatch_fails():
    plan = _load(GOLDEN_FIXTURE)
    plan["arcs"][0]["mode_arc"] = {"mode": "none"}
    errors = gate.validate_master_plan(plan)
    assert any("!= series mode" in e for e in errors), errors


def test_detailed_arc_requires_full_episode_coverage():
    plan = _load(GOLDEN_FIXTURE)
    plan["arcs"][0]["episodes"] = plan["arcs"][0]["episodes"][:3]  # 3 of 6
    errors = gate.validate_master_plan(plan)
    assert any("episode plans cover" in e for e in errors), errors


def test_genre_resolves_via_alias_map():
    """Canonical genre ids resolve through genre_family_aliases (never fixed)."""
    pacing = gate._pacing()
    assert gate.resolve_pacing_family("iyashikei", pacing) == "healing"
    assert gate.resolve_pacing_family("psychological_thriller", pacing) == "mystery"
    assert gate.resolve_pacing_family("mecha", pacing) == "mecha"
    assert gate.resolve_pacing_family("not_a_genre", pacing) is None


def test_default_scan_passes_repo():
    assert gate.main([]) == 0
