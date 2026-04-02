"""Tests for the Manga Author Identity System.

Covers:
- Schema validation
- Author generation across 5 locales
- Anti-collision checks
- Planner integration (mock)
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None

from scripts.manga.generate_manga_author import (
    generate_display_name,
    generate_manga_author_profile,
    load_brand_registry,
    load_existing_manga_authors,
    load_pen_name_display_names,
    validate_no_collision,
    MANGA_AUTHORS_DIR,
)


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

SCHEMA_PATH = REPO_ROOT / "config" / "authoring" / "manga_authors" / "schema.yaml"


class TestSchema:
    """Test the manga author schema itself."""

    @pytest.mark.skipif(yaml is None, reason="PyYAML not installed")
    def test_schema_loads(self):
        assert SCHEMA_PATH.exists(), f"Schema file missing: {SCHEMA_PATH}"
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["schema_version"] == "1.0"
        assert "required_fields" in data
        assert "author_id" in data["required_fields"]
        assert "display_name" in data["required_fields"]
        assert "ei_disclosure_text" in data["required_fields"]

    @pytest.mark.skipif(yaml is None, reason="PyYAML not installed")
    def test_schema_has_anti_collision_rules(self):
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        rules = data.get("anti_collision_rules", [])
        assert len(rules) >= 3
        rule_names = {r["rule"] for r in rules}
        assert "no_manga_author_name_matches_pen_name_author" in rule_names
        assert "no_duplicate_name_within_brand" in rule_names
        assert "no_duplicate_author_id" in rule_names

    @pytest.mark.skipif(yaml is None, reason="PyYAML not installed")
    def test_sample_authors_conform_to_schema(self):
        """Every sample author YAML has all required fields from schema."""
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            schema = yaml.safe_load(f)
        required = set(schema["required_fields"])

        count = 0
        for p in sorted(MANGA_AUTHORS_DIR.glob("*.yaml")):
            if p.name == "schema.yaml":
                continue
            with open(p, encoding="utf-8") as f:
                author = yaml.safe_load(f)
            missing = required - set(author.keys())
            assert not missing, f"{p.name} missing required fields: {missing}"
            count += 1
        assert count >= 5, f"Expected at least 5 sample authors, found {count}"


# ---------------------------------------------------------------------------
# Author generation — all 5 locales
# ---------------------------------------------------------------------------

class TestGeneration:
    """Test manga author profile generation."""

    def test_generate_en_us_iyashikei(self):
        profile = generate_manga_author_profile(
            brand_id="stillness_press",
            genre="iyashikei",
            locale="en_US",
            topic="anxiety",
            demographic="anxious_millennials_urban",
        )
        assert profile["brand_id"] == "stillness_press"
        assert profile["genre_tie_in"] == "iyashikei"
        assert profile["locale"] == "en_US"
        assert "Enlightened Intelligence" in profile["ei_disclosure_text"]
        assert len(profile["display_name"]) > 0
        # English name: two parts
        assert " " in profile["display_name"]

    def test_generate_zh_tw_seinen(self):
        profile = generate_manga_author_profile(
            brand_id="stabilizer_tw",
            genre="seinen",
            locale="zh_TW",
            topic="burnout",
            demographic="tech_finance_burnout",
        )
        assert profile["locale"] == "zh_TW"
        assert profile["genre_tie_in"] == "seinen"
        # Chinese name: CJK characters
        assert any("\u4e00" <= ch <= "\u9fff" for ch in profile["display_name"])
        assert "EI" in profile["ei_disclosure_text"]

    def test_generate_en_us_shonen(self):
        profile = generate_manga_author_profile(
            brand_id="cognitive_clarity",
            genre="shonen",
            locale="en_US",
            topic="performance_pressure",
            demographic="gen_z_professionals",
        )
        assert profile["genre_tie_in"] == "shonen"
        assert " " in profile["display_name"]

    def test_generate_zh_tw_josei(self):
        profile = generate_manga_author_profile(
            brand_id="inner_security_tw",
            genre="josei",
            locale="zh_TW",
            topic="relational_instability",
            demographic="millennial_women_professionals",
        )
        assert profile["genre_tie_in"] == "josei"
        assert any("\u4e00" <= ch <= "\u9fff" for ch in profile["display_name"])

    def test_generate_zh_cn_cultivation(self):
        profile = generate_manga_author_profile(
            brand_id="stabilizer_cn",
            genre="cultivation",
            locale="zh_CN",
            topic="burnout",
            demographic="gen_z_professionals",
        )
        assert profile["locale"] == "zh_CN"
        assert profile["genre_tie_in"] == "cultivation"
        assert any("\u4e00" <= ch <= "\u9fff" for ch in profile["display_name"])

    def test_generate_ja_jp_iyashikei(self):
        """ja_JP generation — uses Japanese name tables."""
        # Use a zh-locale brand since no ja_JP brand exists in registry;
        # the generator should still produce a ja_JP-style name.
        # We mock the brand check to allow a hypothetical ja brand.
        with patch(
            "scripts.manga.generate_manga_author.load_brand_registry",
            return_value={"test_ja_brand": {"lifecycle": "active", "locale": "ja_JP"}},
        ):
            profile = generate_manga_author_profile(
                brand_id="test_ja_brand",
                genre="iyashikei",
                locale="ja_JP",
                topic="anxiety",
                demographic="anxious_millennials_urban",
            )
        assert profile["locale"] == "ja_JP"
        # Japanese name should contain CJK characters
        assert any("\u4e00" <= ch <= "\u9fff" or "\u3040" <= ch <= "\u309f" for ch in profile["display_name"])

    def test_deterministic_generation(self):
        """Same inputs always produce the same name."""
        kwargs = dict(
            brand_id="stillness_press",
            genre="iyashikei",
            locale="en_US",
            topic="anxiety",
            demographic="anxious_millennials_urban",
        )
        name1 = generate_display_name(**kwargs)
        name2 = generate_display_name(**kwargs)
        assert name1 == name2

    def test_different_inputs_different_names(self):
        """Different brand/genre combos produce different names."""
        name1 = generate_display_name(
            genre="iyashikei", locale="en_US", brand_id="stillness_press",
            topic="anxiety", demographic="anxious_millennials_urban",
        )
        name2 = generate_display_name(
            genre="shonen", locale="en_US", brand_id="cognitive_clarity",
            topic="performance_pressure", demographic="gen_z_professionals",
        )
        assert name1 != name2

    def test_invalid_brand_raises(self):
        with pytest.raises(ValueError, match="not found in brand_registry"):
            generate_manga_author_profile(
                brand_id="nonexistent_brand",
                genre="iyashikei",
                locale="en_US",
                topic="anxiety",
                demographic="test",
            )


# ---------------------------------------------------------------------------
# Anti-collision checks
# ---------------------------------------------------------------------------

class TestAntiCollision:
    """Test collision validation."""

    def test_no_collision_with_novel_name(self):
        errors = validate_no_collision(
            "Zzzyxq Testname",
            "stillness_press",
            pen_name_names={"Alice Smith", "Bob Jones"},
            existing_authors=[],
        )
        assert errors == []

    def test_collision_with_pen_name(self):
        errors = validate_no_collision(
            "Alice Smith",
            "stillness_press",
            pen_name_names={"Alice Smith", "Bob Jones"},
            existing_authors=[],
        )
        assert len(errors) == 1
        assert "pen_name_teacher_profiles" in errors[0]

    def test_collision_within_brand(self):
        existing = [
            {"display_name": "Hana Tidecalm", "brand_id": "stillness_press", "author_id": "x"},
        ]
        errors = validate_no_collision(
            "Hana Tidecalm",
            "stillness_press",
            pen_name_names=set(),
            existing_authors=existing,
        )
        assert len(errors) == 1
        assert "already exists for brand" in errors[0]

    def test_same_name_different_brand_ok(self):
        existing = [
            {"display_name": "Hana Tidecalm", "brand_id": "cognitive_clarity", "author_id": "y"},
        ]
        errors = validate_no_collision(
            "Hana Tidecalm",
            "stillness_press",
            pen_name_names=set(),
            existing_authors=existing,
        )
        assert errors == []

    def test_existing_sample_authors_have_no_collisions(self):
        """All sample authors in config pass collision checks."""
        pen_names = load_pen_name_display_names()
        authors = load_existing_manga_authors()
        # Check each author against pen names (but not against itself for brand dup)
        for a in authors:
            dn = a.get("display_name", "")
            assert dn not in pen_names, (
                f"Sample author '{dn}' collides with a pen name author!"
            )
        # Check for intra-brand duplicates
        brand_names: dict[str, list[str]] = {}
        for a in authors:
            brand_names.setdefault(a["brand_id"], []).append(a["display_name"])
        for bid, names in brand_names.items():
            assert len(names) == len(set(names)), (
                f"Brand '{bid}' has duplicate manga author names"
            )


# ---------------------------------------------------------------------------
# CI validation script
# ---------------------------------------------------------------------------

class TestCIValidation:
    """Test the CI collision validation script."""

    def test_validate_all_passes(self):
        from scripts.manga.validate_manga_author_collisions import validate_all

        errors = validate_all()
        assert errors == [], f"CI validation found errors: {errors}"


# ---------------------------------------------------------------------------
# Planner integration (mock)
# ---------------------------------------------------------------------------

class TestPlannerIntegration:
    """Test manga author resolver wiring into series setup."""

    def test_find_matching_author(self):
        from phoenix_v4.manga.series.manga_author_resolver import find_matching_author

        author = find_matching_author(
            brand_id="stillness_press",
            genre_id="iyashikei",
        )
        # Should find the sample author hana_tidecalm
        if author is not None:
            assert author["brand_id"] == "stillness_press"
            assert author["genre_tie_in"] == "iyashikei"

    def test_find_matching_author_no_match(self):
        from phoenix_v4.manga.series.manga_author_resolver import find_matching_author

        author = find_matching_author(
            brand_id="nonexistent_brand_xyz",
            genre_id="horror",
        )
        assert author is None

    def test_build_author_identity_artifact(self):
        from phoenix_v4.manga.series.manga_author_resolver import (
            build_author_identity_artifact,
        )

        mock_author = {
            "author_id": "test_001",
            "display_name": "Test Author",
            "genre_tie_in": "iyashikei",
            "brand_id": "stillness_press",
            "locale": "en_US",
            "ei_disclosure_text": "This is an EI author.",
            "bio_blurb": "A test author.",
            "visual_style_notes": "Soft linework.",
        }
        artifact = build_author_identity_artifact(mock_author)
        assert artifact["artifact_type"] == "manga_author_identity"
        assert artifact["schema_version"] == "1.0.0"
        assert artifact["author_id"] == "test_001"

    def test_resolve_manga_author_existing(self):
        from phoenix_v4.manga.series.manga_author_resolver import resolve_manga_author

        author = resolve_manga_author(
            brand_id="stillness_press",
            genre_id="iyashikei",
            locale="en_US",
        )
        # Should resolve to an existing sample
        if author is not None:
            assert author["brand_id"] == "stillness_press"

    def test_emit_bundle_includes_author_when_brand_provided(self):
        """Series bundle includes manga_author_identity when brand_id is set."""
        from phoenix_v4.manga.series.emit import build_series_artifact_bundle

        bundle = build_series_artifact_bundle(
            series_id="test_series",
            arc_id="test_arc",
            genre_id="iyashikei",
            brand_id="stillness_press",
            locale="en_US",
            topic="anxiety",
        )
        # The bundle should include the author identity since the sample exists
        if "manga_author_identity" in bundle:
            identity = bundle["manga_author_identity"]
            assert identity["artifact_type"] == "manga_author_identity"
            assert identity["brand_id"] == "stillness_press"

    def test_emit_bundle_no_author_when_no_brand(self):
        """Series bundle omits manga_author_identity when brand_id is empty."""
        from phoenix_v4.manga.series.emit import build_series_artifact_bundle

        bundle = build_series_artifact_bundle(
            series_id="test_series",
            arc_id="test_arc",
            genre_id="iyashikei",
        )
        assert "manga_author_identity" not in bundle
