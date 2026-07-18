"""FIX D: commercial-genre engine — mecha beat-bank + topic→strategy embed.

Guards that (a) the mecha strategy bank loads, (b) a topic pins its device
strategy (burnout → the failing-chassis arc), and (c) the generated chapter is
genre-authentic mecha prose, not the healing fallback.
"""
from phoenix_v4.manga.story_strategy_loader import (
    list_available_genres,
    resolve_topic_strategy,
)
from phoenix_v4.manga.series.story_architect import build_story_architecture_internal


def test_mecha_bank_available():
    assert "mecha" in list_available_genres()


def test_topic_pins_device_strategy():
    assert resolve_topic_strategy("mecha", "burnout") == "strategy_01"
    assert resolve_topic_strategy("mecha", "anxiety") == "strategy_02"
    assert resolve_topic_strategy("mecha", "grief") == "strategy_03"
    assert resolve_topic_strategy("mecha", "not_a_topic") is None


def test_burnout_mecha_generates_failing_chassis_arc():
    internal = build_story_architecture_internal(
        series_id="warrior_calm_cultivation_burnout_mecha",
        arc_id="arc_burnout",
        genre_id="mecha",
        topic="burnout",
    )
    assert internal["transmission_audit"]["note"] == "strategy_driven"
    ch1 = internal["chapters"][0]
    assert ch1["chapter_title"] == "The Chassis Is Listening"
    txt = " ".join(b["beat_text"] for b in ch1["plot_beats"]).lower()
    # The inner state (burnout) is carried by the machine device, not stated.
    assert "sync" in txt and "fatigue" in txt
    assert "{" not in txt  # placeholders resolved


def test_mecha_is_not_healing_fallback():
    internal = build_story_architecture_internal(
        series_id="x_overwhelm_mecha", arc_id="a", genre_id="mecha", topic="overwhelm")
    txt = " ".join(
        b["beat_text"] for ch in internal["chapters"] for b in ch["plot_beats"]
    ).lower()
    assert any(w in txt for w in ("reactor", "cockpit", "unit", "redline"))
