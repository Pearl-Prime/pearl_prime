"""Story engine architect — governed genres, distinct beat structures, no generic fallback."""
from __future__ import annotations

import pytest

from phoenix_v4.manga.series.story_architect import (
    _generate_default_chapters,
    build_story_architecture_internal,
)
from phoenix_v4.manga.story_engine_loader import (
    StoryEngineError,
    governed_genres,
    is_engine_governed,
    resolve_engine_genre,
    validate_architect_chapters,
    validate_engine_blob,
    _blob_from_chapters,
)
from phoenix_v4.manga.story_strategy_loader import strategy_bank_exists


EXEMPLAR_PAIRS = [
    ("psychological_horror", "anxiety"),
    ("workplace_drama", "burnout"),
    ("action_battle", "courage"),
    ("romance_josei_drama", "social_anxiety"),
    ("sports_competition", "perfectionism"),
]


def _ch1_blob(genre: str, topic: str) -> str:
    out = build_story_architecture_internal(
        series_id=f"engine_test_{topic}_{genre}",
        arc_id="arc_a",
        genre_id=genre,
        topic=topic,
    )
    return _blob_from_chapters(out["chapters"])


def test_governed_genres_have_engine_specs():
    genres = governed_genres()
    assert "psychological_horror" in genres
    assert "workplace_drama" in genres
    assert "cultivation_martial" in genres
    assert len(genres) >= 8


def test_alias_resolution():
    assert resolve_engine_genre("horror") == "psychological_horror"
    assert resolve_engine_genre("sports") == "sports_competition"
    assert resolve_engine_genre("shonen") == "action_battle"


@pytest.mark.parametrize("genre,topic", EXEMPLAR_PAIRS)
def test_governed_genre_uses_strategy_not_generic(genre, topic):
    assert strategy_bank_exists(genre), f"missing strategy bank for {genre}"
    out = build_story_architecture_internal(
        series_id=f"strat_{topic}_{genre}",
        arc_id="a",
        genre_id=genre,
        topic=topic,
    )
    assert out["transmission_audit"]["note"] == "strategy_driven"
    assert out.get("story_engine_governed") is True
    assert out.get("story_engine_genre") == resolve_engine_genre(genre)
    assert validate_engine_blob(_blob_from_chapters(out["chapters"]), genre) == []


def test_cultivation_martial_hard_fails_without_strategy_bank():
    assert is_engine_governed("cultivation_martial")
    assert not strategy_bank_exists("cultivation_martial")
    with pytest.raises(StoryEngineError, match="generic _BEAT_TEMPLATES fallback blocked"):
        build_story_architecture_internal(
            series_id="cultivation_proof",
            arc_id="a",
            genre_id="cultivation_martial",
            topic="discipline",
        )


def test_generic_template_blob_fails_governed_validation():
    generic = _generate_default_chapters("generic_series", "arc", "shonen")
    with pytest.raises(StoryEngineError, match="story engine validation failed"):
        validate_architect_chapters(generic, "psychological_horror")


def test_exemplar_genres_produce_distinct_beat_structures():
    """Horror, workplace, and battle must not collapse to the same marker profile."""
    horror_blob = _ch1_blob("psychological_horror", "anxiety")
    workplace_blob = _ch1_blob("workplace_drama", "burnout")
    battle_blob = _ch1_blob("action_battle", "courage")

    horror_sig = {"dread", "wrong", "presence", "flinch", "shouldn't"}
    office_sig = {"office", "calendar", "badge", "meeting", "dashboard", "email"}
    battle_sig = {"strike", "guard", "blade", "bout", "opponent", "parry"}

    assert sum(1 for m in horror_sig if m in horror_blob) >= 1
    assert sum(1 for m in office_sig if m in workplace_blob) >= 2
    assert sum(1 for m in battle_sig if m in battle_blob) >= 2

    for blob in (horror_blob, workplace_blob, battle_blob):
        assert "dawn light, stillness before the day" not in blob
        assert "the world breathes" not in blob

    # First beats must be materially different (not the same scaffold with renamed nouns).
    h1 = horror_blob.split("\n")[0][:120]
    w1 = workplace_blob.split("\n")[0][:120]
    b1 = battle_blob.split("\n")[0][:120]
    assert len({h1, w1, b1}) == 3


def test_non_governed_legacy_still_uses_generic_fallback():
    """Legacy genres outside story_engines.yaml may still use _BEAT_TEMPLATES."""
    out = build_story_architecture_internal(
        series_id="legacy_memoir",
        arc_id="a",
        genre_id="memoir",
        topic="memory",
    )
    assert out["transmission_audit"]["note"] == "chunk_b_deterministic"
    assert out.get("story_engine_governed") is None
