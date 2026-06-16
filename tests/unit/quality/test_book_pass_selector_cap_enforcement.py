"""ws_flow_glue_selector_cap_enforcement_20260517 / OPD-20260518-002 follow-up.

Background
----------
The book_pass gate's ``identity_stages`` check used to read
``enrichment_audit.depth_modules_added`` exclusively. Depth-modules are a
word-budget side effect — they only fire when chapters fall short of their
target. Standard_book renders that meet target words without enrichment
never emit ``recognition_depth`` or ``integration_landing`` modules, so the
check spuriously FAILed for Junko + Miyuki standard_book smokes on
2026-05-19 even though the actual chapter prose covered all three identity
stages (``recognition``, ``mechanism``, ``integration`` were three of the
twelve roles already accepted by ``band_distribution``).

These tests pin the new behaviour:
  1. Standard_book renders with chapter roles but no depth-modules now PASS
     identity_stages.
  2. Deep_book renders that historically passed via depth-modules still
     PASS (depth-module signal is preserved as a secondary fallback).
  3. Renders missing two or more identity stages (e.g. only ``mechanism``
     chapters) correctly FAIL.
  4. Role substring matching tolerates the canonical role labels emitted by
     spine planners (e.g. ``pattern_mapping`` → recognition stage).
"""
from __future__ import annotations

import pytest

from phoenix_v4.quality.identity_stages_check import (
    INTEGRATION_ROLE_MARKERS,
    MECHANISM_ROLE_MARKERS,
    RECOGNITION_ROLE_MARKERS,
    compute_identity_stages,
)


# ---------------------------------------------------------------------------
# Standard_book: chapter roles drive the check; depth_modules can be empty
# ---------------------------------------------------------------------------


def _twelve_role_spine() -> list[str]:
    """The canonical 12-role spine emitted by the gen_z_professionals x anxiety
    spine planner (mirrors band_distribution.distinct_roles in Junko/Miyuki
    standard_book smokes, 2026-05-19)."""
    return [
        "recognition",
        "destabilization",
        "pattern_mapping",
        "origin",
        "mechanism",
        "cost_exposure",
        "identity_fracture",
        "somatic_legitimacy",
        "reframe",
        "practical_interruption",
        "practice_under_pressure",
        "integration",
    ]


def test_standard_book_roles_alone_yield_pass() -> None:
    """Twelve canonical spine roles + no depth modules → all three stages PASS."""
    roles = _twelve_role_spine()
    depth_modules: list[str] = []  # standard_book often emits zero depth modules

    stages, count, ok = compute_identity_stages(roles, depth_modules)
    assert stages == {"recognition": True, "mechanism": True, "integration": True}
    assert count == 3
    assert ok is True


def test_standard_book_minimal_roles_recognition_plus_mechanism_passes() -> None:
    """Two stages out of three meets the >=2 threshold."""
    roles = ["recognition", "mechanism", "mechanism", "recognition"]
    stages, count, ok = compute_identity_stages(roles, depth_modules=[])
    assert stages["recognition"] is True
    assert stages["mechanism"] is True
    assert stages["integration"] is False
    assert count == 2
    assert ok is True


def test_only_mechanism_role_fails() -> None:
    """A book with only ``mechanism`` roles (no recognition / integration) FAILs."""
    roles = ["mechanism", "mechanism", "mechanism", "mechanism"]
    stages, count, ok = compute_identity_stages(roles, depth_modules=[])
    assert stages == {"recognition": False, "mechanism": True, "integration": False}
    assert count == 1
    assert ok is False


# ---------------------------------------------------------------------------
# Deep_book: depth_modules are accepted as a secondary signal
# ---------------------------------------------------------------------------


def test_deep_book_depth_modules_alone_pass() -> None:
    """A render with NO chapter roles but with recognition_depth /
    integration_landing depth modules (the historic deep_book_6h path)
    still PASSes.
    """
    roles: list[str] = []
    modules = [
        "recognition_depth",
        "mechanism_depth",
        "integration_landing",
        "story_scene",
    ]
    stages, count, ok = compute_identity_stages(roles, modules)
    assert stages == {"recognition": True, "mechanism": True, "integration": True}
    assert count == 3
    assert ok is True


def test_deep_book_depth_modules_supplement_roles() -> None:
    """When both roles and modules are present, the union is taken."""
    roles = ["mechanism", "cost_exposure"]  # mechanism only
    modules = ["recognition_depth", "integration_landing", "story_scene"]
    stages, count, ok = compute_identity_stages(roles, modules)
    assert stages == {"recognition": True, "mechanism": True, "integration": True}
    assert count == 3
    assert ok is True


def test_practice_module_satisfies_integration_stage() -> None:
    """``integration`` stage accepts substrings ``practice`` / ``reframe`` /
    ``integration``. This was true in the legacy check and must remain true.
    """
    roles: list[str] = []
    modules = ["recognition_depth", "mechanism_depth", "practice_block"]
    stages, count, ok = compute_identity_stages(roles, modules)
    assert stages["integration"] is True, (
        "Modules containing 'practice' should satisfy the integration stage."
    )


# ---------------------------------------------------------------------------
# Empty / degenerate inputs
# ---------------------------------------------------------------------------


def test_empty_roles_and_modules_fail() -> None:
    """A render with no role data and no enrichment data FAILs."""
    stages, count, ok = compute_identity_stages([], [])
    assert stages == {"recognition": False, "mechanism": False, "integration": False}
    assert count == 0
    assert ok is False


def test_none_and_empty_strings_are_tolerated() -> None:
    """Defensive: empty strings and stray whitespace must not crash the check."""
    roles = ["", "   ", "recognition", ""]
    modules = ["", "mechanism_depth", "   "]
    stages, count, ok = compute_identity_stages(roles, modules)
    assert stages["recognition"] is True
    assert stages["mechanism"] is True
    assert ok is True


# ---------------------------------------------------------------------------
# Marker-list pinning (regression catch for future edits)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("marker", ["recognition", "pattern_mapping", "origin"])
def test_recognition_markers_include_canonical(marker: str) -> None:
    assert marker in RECOGNITION_ROLE_MARKERS


@pytest.mark.parametrize("marker", ["mechanism", "cost_exposure", "identity_fracture"])
def test_mechanism_markers_include_canonical(marker: str) -> None:
    assert marker in MECHANISM_ROLE_MARKERS


@pytest.mark.parametrize("marker", ["integration", "reframe", "practice"])
def test_integration_markers_include_canonical(marker: str) -> None:
    assert marker in INTEGRATION_ROLE_MARKERS


# ---------------------------------------------------------------------------
# Junko + Miyuki regression scenario
# ---------------------------------------------------------------------------


def test_junko_miyuki_standard_book_smoke_scenario_passes() -> None:
    """Concrete pin for the failing 2026-05-19 smokes.

    Both Junko and Miyuki standard_book smokes:
      * 12 chapters with the canonical role set above
      * enrichment_audit.depth_modules_added: only mechanism_depth (6x) and
        story_scene (1x) — neither recognition_depth nor integration_landing

    Pre-fix: identity_stages FAIL (recognition=False, integration=False).
    Post-fix: identity_stages PASS via role signal.
    """
    roles = _twelve_role_spine()
    depth_modules = ["mechanism_depth"] * 6 + ["story_scene"]

    stages, count, ok = compute_identity_stages(roles, depth_modules)
    assert ok is True, (
        "Junko/Miyuki standard_book regression: identity_stages should PASS when "
        f"chapter roles cover all three stages. Got stages={stages}."
    )
    assert count == 3
