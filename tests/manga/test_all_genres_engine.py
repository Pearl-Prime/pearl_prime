"""All-genres engine: every commercial genre bank loads + generates a
topic-pinned, genre-authentic, placeholder-free story. The "all topics x all
genres" coverage guard.
"""
import pytest

from phoenix_v4.manga.story_strategy_loader import (
    list_available_genres,
    load_character_pool,
    strategy_bank_exists,
)
from phoenix_v4.manga.series.story_architect import build_story_architecture_internal

# (genre, a representative embedded topic that pins a device-strategy)
COMMERCIAL = [
    ("psychological_horror", "anxiety"),
    ("dark_fantasy", "grief"),
    ("isekai", "impostor_syndrome"),
    ("psychological_thriller", "overthinking"),
    ("romance_josei_drama", "social_anxiety"),
    ("sci_fi_cyberpunk", "identity"),
    ("action_battle", "courage"),
    ("sports_competition", "perfectionism"),
    ("supernatural_mystery", "guilt"),
    ("historical_period", "duty"),
    ("workplace_drama", "burnout"),
]


def test_all_commercial_genres_have_banks():
    avail = set(list_available_genres())
    for genre, _ in COMMERCIAL:
        assert genre in avail, f"missing strategy bank: {genre}"
        assert strategy_bank_exists(genre)


@pytest.mark.parametrize("genre,topic", COMMERCIAL)
def test_genre_generates_topic_pinned_story(genre, topic):
    internal = build_story_architecture_internal(
        series_id=f"b_{topic}_{genre}", arc_id="a", genre_id=genre, topic=topic
    )
    assert internal["transmission_audit"]["note"] == "strategy_driven"
    ch1 = internal["chapters"][0]
    txt = " ".join(b["beat_text"] for b in ch1["plot_beats"])
    assert "{" not in txt  # placeholders resolved from the bank's character_pool
    assert len(ch1["plot_beats"]) >= 5


@pytest.mark.parametrize("genre,_t", COMMERCIAL)
def test_genre_is_self_contained(genre, _t):
    cp = load_character_pool(genre)
    assert cp.get("protagonist") and cp.get("setting")
