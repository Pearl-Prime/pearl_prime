"""Regression tests for the per-platform cover-output profile registry.

Covers config/publishing/platform_cover_profiles.yaml + its loader/validator.
SSOT for every asserted number: docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md §3/§4.
CPU-only; no image libraries required.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "publishing" / "platform_cover_profiles.yaml"
LOADER_PATH = REPO_ROOT / "scripts" / "publishing" / "load_cover_profiles.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("load_cover_profiles", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def loader():
    return _load_module()


@pytest.fixture(scope="module")
def registry(loader):
    return loader.load_cover_profiles(CONFIG_PATH)


@pytest.fixture(scope="module")
def profiles(registry):
    return registry["profiles"]


def test_registry_loads_and_validates(loader, registry):
    assert registry["registry_type"] == "platform_cover_profiles"
    errors = loader.validate_profiles(registry)
    assert errors == [], f"registry should validate clean, got: {errors}"


def test_expected_platforms_present(profiles):
    for key in (
        "kdp_ebook",
        "google_play_ebook",
        "kobo_ebook",
        "google_play_audiobook",
        "acx_audiobook",
        "findaway_voices_audiobook",
        "apple_books_ebook",
        "barnes_noble_ebook",
    ):
        assert key in profiles, f"missing profile {key}"


def test_kdp_is_5_by_8(profiles):
    ar = profiles["kdp_ebook"]["aspect_ratio"]
    assert ar["ratio"] == "5:8"
    assert ar["decimal"] == pytest.approx(0.625)
    rec = profiles["kdp_ebook"]["size_recommended"]
    assert (rec["width"], rec["height"]) == (1600, 2560)


def test_kobo_is_3_by_4(profiles):
    ar = profiles["kobo_ebook"]["aspect_ratio"]
    assert ar["ratio"] == "3:4"
    assert ar["decimal"] == pytest.approx(0.75)


def test_audiobook_surfaces_are_1_by_1(profiles):
    for key in ("google_play_audiobook", "acx_audiobook", "findaway_voices_audiobook"):
        ar = profiles[key]["aspect_ratio"]
        assert ar["ratio"] == "1:1", f"{key} should be 1:1"
        assert ar["decimal"] == pytest.approx(1.0)


def test_kobo_size_min_is_1400x1873(profiles):
    smin = profiles["kobo_ebook"]["size_min"]
    assert (smin["width"], smin["height"]) == (1400, 1873)


def test_kobo_rejects_kdp_aspect_asset(loader, profiles):
    """A KDP 1600x2560 (5:8) asset is the WRONG aspect for Kobo 3:4 and must be rejected."""
    kobo = profiles["kobo_ebook"]
    assert loader.aspect_matches(kobo, 1600, 2560) is False
    # The aspect-exact 3:4 recommended master passes.
    assert loader.aspect_matches(kobo, 1920, 2560) is True
    # The reject-below min asset (1400x1873) is within tolerance of 3:4.
    assert loader.aspect_matches(kobo, 1400, 1873) is True


def test_kobo_high_dpi_master_recorded(profiles):
    """Research §4 high-DPI master 2500x3500 is carried separately (it is 5:7, not pure 3:4)."""
    hi = profiles["kobo_ebook"]["size_high_dpi_master"]
    assert (hi["width"], hi["height"]) == (2500, 3500)


def test_acx_min_2400_and_no_borders(profiles):
    acx = profiles["acx_audiobook"]
    smin = acx["size_min"]
    assert (smin["width"], smin["height"]) == (2400, 2400)
    assert acx["size_recommended"] == {"width": 3000, "height": 3000}
    assert acx["borders_allowed"] is False
    assert acx["marketing_copy_allowed"] is False


def test_launch_priority_ordering(profiles):
    kdp = profiles["kdp_ebook"]["launch_priority"]
    gp_ebook = profiles["google_play_ebook"]["launch_priority"]
    kobo = profiles["kobo_ebook"]["launch_priority"]
    audiobook = min(
        profiles[k]["launch_priority"]
        for k in ("google_play_audiobook", "acx_audiobook", "findaway_voices_audiobook")
    )
    assert kdp == 0
    assert kdp < gp_ebook
    assert kdp < kobo
    assert gp_ebook < audiobook
    assert kobo < audiobook


def test_launch_order_helper(loader):
    order = loader.launch_order(CONFIG_PATH)
    assert order[0] == "kdp_ebook", "KDP must be first (priority 0)"
    # ordering must be non-decreasing by launch_priority
    profs = loader.get_profiles(CONFIG_PATH)
    priorities = [profs[k]["launch_priority"] for k in order]
    assert priorities == sorted(priorities)


def test_validator_catches_wrong_aspect(loader, registry):
    """Corrupt a profile so the aspect decimal no longer matches its size; validator must flag it."""
    import copy

    bad = copy.deepcopy(registry)
    bad["profiles"]["kdp_ebook"]["aspect_ratio"]["decimal"] = 0.75  # was 0.625
    errors = loader.validate_profiles(bad)
    assert any("aspect decimal" in e for e in errors), errors
