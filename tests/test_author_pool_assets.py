"""Wiring + asset-completeness lock for the clear_seeing_books and
felt_sense_publishing author pools (PR: 1 brand -> 3 brands).

- Every pooled author must load all four render assets with zero errors
  (run_pipeline hard-fails the build otherwise — Writer Spec §23.9).
- Each brand must resolve its primary topics to the intended pooled author.

The assignments path defaults to the shipped config; override with
AUTHOR_ASSIGNMENTS_PATH to point at a candidate file.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from phoenix_v4.planning.author_asset_loader import load_author_assets
from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSIGNMENTS_PATH = Path(
    os.environ.get("AUTHOR_ASSIGNMENTS_PATH", REPO_ROOT / "config" / "brand_author_assignments.yaml")
)

POOLED_AUTHORS = [
    # clear_seeing_books
    "ada_park", "joel_crane", "hana_lee", "marcus_stone", "yuki_tanabe", "elliot_vane",
    # felt_sense_publishing
    "claire_ashford", "james_fielding", "vera_osei", "alex_navarro",
    "helen_cross", "omar_brooks", "suki_moreno", "ben_archer",
]

# (brand, topic, expected_author) — one representative route per author.
ROUTES = [
    ("clear_seeing_books", "overthinking", "ada_park"),
    ("clear_seeing_books", "boundaries", "joel_crane"),
    ("clear_seeing_books", "social_anxiety", "hana_lee"),
    ("clear_seeing_books", "burnout", "marcus_stone"),
    ("clear_seeing_books", "grief", "yuki_tanabe"),
    ("clear_seeing_books", "financial_stress", "elliot_vane"),
    ("felt_sense_publishing", "anxiety", "claire_ashford"),
    ("felt_sense_publishing", "burnout", "james_fielding"),
    ("felt_sense_publishing", "grief", "vera_osei"),
    ("felt_sense_publishing", "social_anxiety", "alex_navarro"),
    ("felt_sense_publishing", "boundaries", "helen_cross"),
    ("felt_sense_publishing", "depression", "omar_brooks"),
    ("felt_sense_publishing", "financial_anxiety", "suki_moreno"),
    ("felt_sense_publishing", "somatic_healing", "ben_archer"),
]


def _brand_present(brand_id: str) -> bool:
    data = yaml.safe_load(ASSIGNMENTS_PATH.read_text()) or {}
    return any(r.get("brand_id") == brand_id for r in (data.get("assignments") or []))


@pytest.mark.parametrize("author_id", POOLED_AUTHORS)
def test_pooled_author_assets_load_without_errors(author_id):
    """The render gate (run_pipeline:2146) returns 1 if any asset is missing."""
    assets = load_author_assets(author_id)
    assert assets.get("errors") == [], f"{author_id}: {assets.get('errors')}"
    assert assets.get("bio"), f"{author_id}: empty bio"
    pre = assets.get("audiobook_pre_intro") or {}
    assert pre.get("author_background"), f"{author_id}: missing author_background"


@pytest.mark.parametrize("brand_id,topic_id,expected", ROUTES)
def test_brand_routes_topic_to_pooled_author(brand_id, topic_id, expected):
    if not _brand_present(brand_id):
        pytest.skip(f"{brand_id} not wired in {ASSIGNMENTS_PATH}")
    got = resolve_author_from_brand(
        brand_id=brand_id, topic_id=topic_id, assignments_path=ASSIGNMENTS_PATH
    )
    assert got == expected


def test_both_brands_have_a_default_author():
    for brand_id, expected in [("clear_seeing_books", "ada_park"), ("felt_sense_publishing", "claire_ashford")]:
        if not _brand_present(brand_id):
            pytest.skip(f"{brand_id} not wired in {ASSIGNMENTS_PATH}")
        assert resolve_author_from_brand(brand_id=brand_id, assignments_path=ASSIGNMENTS_PATH) == expected
