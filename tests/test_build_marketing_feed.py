"""Tests for marketing_feed.json builder (GHL schema v3)."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_build_feed_has_required_fields():
    from phoenix_v4.marketing.build_feed import build_marketing_feed, validate_feed

    feed = build_marketing_feed(brand_id="stillness_press", topics=["anxiety"])
    errors = validate_feed(feed)
    assert not errors, errors
    assert feed["schema_version"] == 3
    items = feed["items"]
    assert items
    e1 = next(i for i in items if i["email_slot"] == "e1")
    assert e1["pricing"] == "free"
    assert e1["archetype_id"]
    assert e1["funnel_variant"] in ("tight", "welcome_depth")
    assert "cta_url" in e1


def test_compassion_fatigue_welcome_depth_and_bonus():
    from phoenix_v4.marketing.build_feed import build_marketing_feed

    feed = build_marketing_feed(brand_id="stillness_press", topics=["compassion_fatigue"])
    items = feed["items"]
    variants = {i["funnel_variant"] for i in items}
    assert variants == {"welcome_depth"}
    slots = [i["email_slot"] for i in items]
    assert "bonus_pre_story" in slots


def test_anxiety_tight_no_bonus_pre_story():
    from phoenix_v4.marketing.build_feed import build_marketing_feed

    feed = build_marketing_feed(brand_id="stillness_press", topics=["anxiety"])
    slots = [i["email_slot"] for i in feed["items"]]
    assert "bonus_pre_story" not in slots


def test_e4_paid_when_book_present():
    from phoenix_v4.marketing.build_feed import build_marketing_feed

    feed = build_marketing_feed(
        brand_id="stillness_press",
        topics=["anxiety"],
        persona_id="corporate_managers",
    )
    e4 = [i for i in feed["items"] if i["email_slot"] == "e4"]
    assert len(e4) == 1
    assert e4[0]["pricing"] == "paid"
    assert "pearlprime.shop" in e4[0]["cta_url"]
    assert "anxiety_corporate_managers_ahjan" in e4[0]["cta_url"]
    assert feed.get("persona_id") == "corporate_managers"


def test_book_url_index_lookup():
    from phoenix_v4.marketing.book_url_index import resolve_book_url

    url = resolve_book_url("anxiety", "corporate_managers", locale="en_US", brand_id="stillness_press")
    assert url
    assert "anxiety_corporate_managers_ahjan" in url


def test_archetype_resolver_canonical_variant():
    from phoenix_v4.planning.freebie_archetype import resolve_archetype_for_topic

    row = resolve_archetype_for_topic("compassion_fatigue")
    assert row["funnel_variant"] == "welcome_depth"
    row2 = resolve_archetype_for_topic("anxiety")
    assert row2["funnel_variant"] == "tight"


def test_feed_metadata_slot_rules():
    from phoenix_v4.marketing.feed_metadata import validate_slot_rules

    bad = {"content_type": "guided_audio", "email_slot": "e1", "pricing": "free"}
    assert validate_slot_rules(bad)
