"""Tests for multi-brand GHL marketing profiles."""
from __future__ import annotations

from phoenix_v4.marketing.brand_profile import (
    get_brand_profile,
    list_brands,
    resolve_funnel_landing_path,
)
from phoenix_v4.marketing.build_feed import build_marketing_feed


def test_pilot_brands_enabled():
    brands = list_brands(ghl_enabled_only=True, rollout_phase="pilot")
    assert set(brands) == {"stillness_press", "devotion_path", "way_stream_sanctuary"}


def test_devotion_path_branded_landing_urls():
    profile = get_brand_profile("devotion_path")
    feed = build_marketing_feed(
        brand_id="devotion_path",
        topics=["anxiety"],
        persona_id=str(profile["default_persona"]),
        funnel_path_prefix=str(profile["funnel_path_prefix"]),
    )
    e1 = next(i for i in feed["items"] if i["email_slot"] == "e1")
    assert "/free/devotion_path/anxiety-nervous-system-reset/" in e1["cta_url"]


def test_stillness_legacy_landing_urls():
    feed = build_marketing_feed(brand_id="stillness_press", topics=["anxiety"])
    e1 = next(i for i in feed["items"] if i["email_slot"] == "e1")
    assert e1["cta_url"].endswith("/free/anxiety-nervous-system-reset/")
    assert "/free/stillness_press/" not in e1["cta_url"]


def test_resolve_funnel_landing_path():
    profile = get_brand_profile("way_stream_sanctuary")
    assert resolve_funnel_landing_path(profile, "burnout-energy-audit") == (
        "/free/way_stream_sanctuary/burnout-energy-audit/"
    )
