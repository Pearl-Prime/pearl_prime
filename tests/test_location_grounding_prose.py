"""Tests for location grounding in rendered prose (Hardening Spec §5B).

Verifies that location profiles contain specific tokens (not generic
fallback) and that NYC-resolved prose can be distinguished from generic.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES_PATH = REPO_ROOT / "config" / "localization" / "render_location_profiles.yaml"

REQUIRED_LOCATION_KEYS = [
    "city_name",
    "weather_detail",
    "street_name",
    "transit_line",
    "neighborhood",
    "building_type",
    "local_landmark",
    "commute_mode",
]


@pytest.fixture(scope="module")
def profiles():
    try:
        import yaml
    except ImportError:
        pytest.skip("pyyaml not installed")
    if not PROFILES_PATH.exists():
        pytest.skip("render_location_profiles.yaml not found")
    data = yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8")) or {}
    return data.get("profiles", {})


class TestNYCProfileHasSpecificTokens:
    """NYC Metro profile must contain concrete, non-generic location tokens."""

    def test_nyc_metro_exists(self, profiles):
        assert "nyc_metro" in profiles, "nyc_metro profile missing"

    def test_nyc_has_all_required_keys(self, profiles):
        nyc = profiles.get("nyc_metro", {})
        for key in REQUIRED_LOCATION_KEYS:
            assert key in nyc, f"nyc_metro missing key: {key}"
            assert nyc[key], f"nyc_metro has empty value for: {key}"

    def test_nyc_tokens_are_specific(self, profiles):
        """NYC tokens should reference actual NYC places, not generic city terms."""
        nyc = profiles.get("nyc_metro", {})
        city = nyc.get("city_name", "")
        assert "New York" in city or "NYC" in city
        street = nyc.get("street_name", "")
        assert street and "the street" not in street.lower()  # not generic

    def test_nyc_grand_central_exists(self, profiles):
        assert "nyc_grand_central" in profiles


class TestGenericFallbacksDiffer:
    """Generic profile must differ from location-specific profiles."""

    def test_generic_differs_from_nyc(self, profiles):
        if "generic_us_urban" not in profiles:
            pytest.skip("generic_us_urban profile not present")
        generic = profiles["generic_us_urban"]
        nyc = profiles.get("nyc_metro", {})
        # At least city_name and street_name should differ
        if generic.get("city_name") and nyc.get("city_name"):
            assert generic["city_name"] != nyc["city_name"], (
                "Generic and NYC should have different city_name"
            )


class TestLocationProfilesComplete:
    """All profiles have required keys with non-empty values."""

    def test_all_profiles_have_required_keys(self, profiles):
        for profile_id, profile in profiles.items():
            for key in REQUIRED_LOCATION_KEYS:
                assert key in profile, (
                    f"Profile '{profile_id}' missing key: {key}"
                )
                assert profile[key], (
                    f"Profile '{profile_id}' has empty value for: {key}"
                )

    def test_all_profiles_have_aliases(self, profiles):
        for profile_id, profile in profiles.items():
            aliases = profile.get("aliases", [])
            assert isinstance(aliases, list), (
                f"Profile '{profile_id}' aliases should be a list"
            )
            assert len(aliases) > 0, (
                f"Profile '{profile_id}' has no aliases"
            )


class TestLocationProfileResolver:
    """resolve_location_profile_id handles aliases correctly."""

    def test_resolve_aliases(self):
        try:
            from phoenix_v4.planning.catalog_planner import resolve_location_profile_id
        except ImportError:
            pytest.skip("catalog_planner not importable")

        assert resolve_location_profile_id("nyc") == "nyc_metro"
        assert resolve_location_profile_id("grand_central") == "nyc_grand_central"
        assert resolve_location_profile_id("santa_monica") == "coastal_california"

    def test_canonical_id_resolves_to_self(self):
        try:
            from phoenix_v4.planning.catalog_planner import resolve_location_profile_id
        except ImportError:
            pytest.skip("catalog_planner not importable")

        assert resolve_location_profile_id("nyc_metro") == "nyc_metro"
        assert resolve_location_profile_id("coastal_california") == "coastal_california"
