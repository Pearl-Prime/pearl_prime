"""Tests for manga profile loader."""
from __future__ import annotations

from pathlib import Path
import pytest
from phoenix_v4.manga.series.profile_loader import load_profile, MangaProfile
from phoenix_v4.manga.models.validation import repo_root


EXAMPLES_DIR = repo_root() / "config" / "source_of_truth" / "manga_profiles" / "examples"


def test_load_stillness_press():
    p = EXAMPLES_DIR / "stillness_press_anxiety_overwhelm.yaml"
    assert p.is_file(), f"Missing: {p}"
    profile = load_profile(p)
    assert profile.title_id == "anxiety_overwhelm_vol1"
    assert profile.market_demo == "josei"
    assert profile.emotional_engine == "cozy_restoration"
    assert profile.visual_grammar == "iyashikei_minimalism"


def test_load_battle_shonen():
    p = EXAMPLES_DIR / "example_battle_shonen.yaml"
    assert p.is_file(), f"Missing: {p}"
    profile = load_profile(p)
    assert profile.market_demo == "shonen"
    assert profile.visual_grammar == "kinetic_shonen"


def test_load_josei_workplace():
    p = EXAMPLES_DIR / "example_josei_workplace.yaml"
    assert p.is_file(), f"Missing: {p}"
    profile = load_profile(p)
    assert profile.market_demo == "josei"
    assert profile.visual_grammar == "grounded_josei_realism"


def test_profile_seed_deterministic():
    p = EXAMPLES_DIR / "stillness_press_anxiety_overwhelm.yaml"
    profile = load_profile(p)
    assert len(profile.profile_seed) == 12
    # seed is deterministic
    assert load_profile(p).profile_seed == profile.profile_seed


def test_missing_required_field_raises():
    import tempfile, yaml
    bad = {"title_id": "x", "brand_id": "y"}
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        yaml.dump(bad, f)
        path = Path(f.name)
    with pytest.raises(ValueError, match="missing required field"):
        load_profile(path)
    path.unlink(missing_ok=True)


def test_invalid_enum_raises():
    import tempfile, yaml
    bad = {
        "title_id": "x", "brand_id": "y",
        "market_demo": "WRONG", "genre_family": "battle",
        "emotional_engine": "aspiration", "reader_promise": "test",
        "serialization_engine": "episodic", "chapter_hook_family": "revelation",
        "visual_grammar": "kinetic_shonen",
    }
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        yaml.dump(bad, f)
        path = Path(f.name)
    with pytest.raises(ValueError, match="invalid market_demo"):
        load_profile(path)
    path.unlink(missing_ok=True)
