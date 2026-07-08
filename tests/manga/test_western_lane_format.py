"""Tests for western_intent_led en_US illustrated self-help Phase A routing."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.manga.generate_series_plans_from_catalog import (  # type: ignore
    ROUTING_CFG,
    _load_yaml,
    resolve_flatten_exports,
    resolve_format,
)
from scripts.ci.check_western_lane_format import (  # type: ignore
    ILLUSTRATED_MASTER,
    run_checks,
)

PILOT_REGISTRY = REPO / "config" / "manga" / "us_illustrated_pilot_cells.yaml"
PLANS_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans" / "en_US"


@pytest.fixture(scope="module")
def routing():
    return _load_yaml(ROUTING_CFG)


@pytest.fixture(scope="module")
def pilot_registry():
    return _load_yaml(PILOT_REGISTRY)


def test_western_lane_override_forces_illustrated_master(routing):
    assert resolve_format(routing, "en_US", "iyashikei", "cozy_iyashikei") == ILLUSTRATED_MASTER
    assert resolve_format(routing, "en_US", "seinen", "dark_psychological") == ILLUSTRATED_MASTER
    assert resolve_format(routing, "en_US", "workplace_drama", "power_progression") == ILLUSTRATED_MASTER


def test_western_lane_override_clears_flatten_exports(routing):
    assert resolve_flatten_exports(routing, "en_US", "seinen") == []


def test_ja_jp_not_affected_by_western_override(routing):
    assert resolve_format(routing, "ja_JP", "seinen", "dark_psychological") == "bw_page_manga"


def test_pilot_registry_has_five_cells(pilot_registry):
    cells = pilot_registry["pilot_cells"]
    assert len(cells) == 5
    brands = {c["brand_id"] for c in cells}
    assert brands == {
        "stillness_press",
        "digital_ground",
        "cognitive_clarity",
        "healing_ground",
        "calm_student",
    }


def test_pilot_stubs_exist_and_validate_schema(pilot_registry):
    schema = json.loads(
        (REPO / "schemas" / "manga" / "series_plan.schema.json").read_text(encoding="utf-8")
    )
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft202012Validator(schema)

    for cell in pilot_registry["pilot_cells"]:
        path = PLANS_ROOT / cell["series_plan_stub"]
        assert path.is_file(), f"missing stub {cell['series_plan_stub']}"
        import yaml

        plan = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert plan["master_format"] == ILLUSTRATED_MASTER
        assert plan["connector_lane"] == "print_only"
        errors = list(validator.iter_errors(plan))
        assert not errors, errors[0].message


def test_ci_gate_passes():
    assert run_checks() == []


def test_ci_script_exit_zero():
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci" / "check_western_lane_format.py")],
        cwd=str(REPO),
        env={**dict(**{"PYTHONPATH": f"{REPO / 'scripts' / 'ci'}:{REPO}"})},
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
