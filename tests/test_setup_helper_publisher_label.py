"""
Tests for the Platform Setup Helper publisher/imprint label
(scripts/onboarding/gen_setup_helper_brands.py).

The helper must show the PUBLICATION CORP / IMPRINT name (KDP "Published by") per brand,
resolved by the SAME source of truth #1611 uses in gen_brand_admin_brands.py — the unified
registry's `publication_corp` (longest-prefix base→imprint baked at registry-build), with a
longest-prefix fallback against brand_display_names.yaml for ids absent from the registry.

These are direct function calls — no server, no fixtures write to the repo.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GEN_PATH = ROOT / "scripts" / "onboarding" / "gen_setup_helper_brands.py"


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen_setup_helper_brands", GEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load_gen()


@pytest.fixture(scope="module")
def indexes():
    return gen._load_corp_index(), gen._load_imprint_by_base()


# ── resolver: the two PROVE brands ──

def test_stillness_press_resolves_to_imprint(indexes):
    corp_by_id, imprint_by_base = indexes
    assert gen.resolve_publisher("stillness_press_en_us", corp_by_id, imprint_by_base) == "Stillness Press"


def test_devotion_path_resolves_to_open_vessel(indexes):
    corp_by_id, imprint_by_base = indexes
    assert gen.resolve_publisher("devotion_path_en_us", corp_by_id, imprint_by_base) == "Open Vessel Press"


# ── resolver: longest-prefix correctness across suffixes / locales / standard brands ──

@pytest.mark.parametrize("brand_id,expected", [
    ("warrior_calm_ja_jp", "Iron Gate Press"),          # CJK locale suffix
    ("optimizer_en_us", "Daybreak Editions"),           # standard (non-teacher) brand
    ("legacy_builder_zh_tw", "Second Mountain Press"),  # another locale lane
])
def test_resolver_longest_prefix_variants(indexes, brand_id, expected):
    corp_by_id, imprint_by_base = indexes
    assert gen.resolve_publisher(brand_id, corp_by_id, imprint_by_base) == expected


def test_resolver_falls_back_to_brand_name_for_unknown_id(indexes):
    """An id absent from registry + display-names uses the brand's own name, never crashes."""
    corp_by_id, imprint_by_base = indexes
    got = gen.resolve_publisher("way_stream_sanctuary", corp_by_id, imprint_by_base,
                                fallback_name="Waystream Sanctuary")
    assert got == "Waystream Sanctuary"


def test_resolver_never_returns_empty(indexes):
    corp_by_id, imprint_by_base = indexes
    assert gen.resolve_publisher("totally_made_up_brand_xyz", corp_by_id, imprint_by_base)


# ── generated public JSON: shape, PROVE brands, privacy gate ──

@pytest.fixture(scope="module")
def public_json():
    import json
    return json.loads(gen.render_public(gen.build()))


def test_public_json_has_prove_brands_with_publisher(public_json):
    assert public_json["stillness_press_en_us"]["publisher"] == "Stillness Press"
    assert public_json["devotion_path_en_us"]["publisher"] == "Open Vessel Press"


def test_public_json_operator_brand_keeps_prefill_and_publisher(public_json):
    e = public_json.get("way_stream_sanctuary")
    assert e and e.get("name") == "Waystream Sanctuary"
    assert e.get("publisher")  # has a publisher label too


def test_every_public_entry_has_a_publisher(public_json):
    missing = [bid for bid, e in public_json.items() if not e.get("publisher")]
    assert not missing, f"entries missing publisher: {missing[:10]}"


def test_public_json_has_no_email_or_pii(public_json):
    """Public URL: no contact email / phone / secrets may leak into the brand prefill."""
    import json
    blob = json.dumps(public_json, ensure_ascii=False)
    assert "@" not in blob, "an email address leaked into the public brand JSON"
    for k in ("email", "phone", "password", "secret", "token", "api_key", "apikey"):
        assert all(k not in e for e in public_json.values()), f"forbidden key '{k}' in public JSON"
