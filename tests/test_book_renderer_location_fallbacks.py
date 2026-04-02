from __future__ import annotations

from phoenix_v4.rendering import book_renderer
from phoenix_v4.rendering.book_renderer import clean_for_delivery, location_grounding_report


def test_clean_for_delivery_uses_location_profile_when_present() -> None:
    text = "{transit_line} slows near {transit_stop}. {street_name} is below. {weather_detail}."
    plan = {"resolved_location_id": "nyc_metro"}

    cleaned = clean_for_delivery(text, plan=plan)

    assert "downtown Q train" in cleaned
    assert "Union Square platform" in cleaned
    assert "Lexington Avenue below" in cleaned
    assert "Fluorescent station light streaks" in cleaned


def test_clean_for_delivery_falls_back_to_universal_when_no_location() -> None:
    text = "{transit_line} slows near {transit_stop}. {street_name} is below."

    cleaned = clean_for_delivery(text)

    assert "the train" in cleaned
    assert "the platform" in cleaned
    assert "the street below" in cleaned


def test_clean_for_delivery_uses_grand_central_profile() -> None:
    text = "{transit_line} leaves {transit_stop}. {street_name} is below."
    plan = {"resolved_location_id": "nyc_grand_central"}

    cleaned = clean_for_delivery(text, plan=plan)

    assert "6 express" in cleaned
    assert "Grand Central" in cleaned
    assert "42nd Street below" in cleaned


def test_location_grounding_report_is_generic_across_profiles(monkeypatch) -> None:
    monkeypatch.setattr(
        book_renderer,
        "_LOCATION_PROFILE_CACHE",
        {
            "taipei_xinyi": {
                "city_name": "Taipei",
                "street_name": "Songren Road below",
                "transit_stop": "Taipei 101/World Trade Center",
                "local_landmark": "the Taipei 101 food court escalator",
            }
        },
    )
    text = (
        "Chapter 1\n\n"
        "Your shoulders rise before the meeting starts. Songren Road below keeps moving.\n\n"
        "You step off at Taipei 101/World Trade Center and feel the decision arrive before the words do.\n"
    )

    report = location_grounding_report(text, plan={"resolved_location_id": "taipei_xinyi"})

    assert report is not None
    assert report["status"] == "PASS"
    assert {hit["key"] for hit in report["signals_found"]} >= {"street_name", "transit_stop"}


def test_location_grounding_report_fails_when_opening_is_not_location_specific(monkeypatch) -> None:
    monkeypatch.setattr(
        book_renderer,
        "_LOCATION_PROFILE_CACHE",
        {
            "la_echo_park": {
                "city_name": "Los Angeles",
                "street_name": "Sunset Boulevard below",
                "coffee_shop": "the Echo Park cafe on the corner",
            }
        },
    )
    text = (
        "Chapter 1\n\n"
        "Your chest tightens before the conversation starts.\n\n"
        "You look at the floor and try to say the sentence anyway.\n"
    )

    report = location_grounding_report(text, plan={"resolved_location_id": "la_echo_park"})

    assert report is not None
    assert report["status"] == "FAIL"
    assert report["errors"]
