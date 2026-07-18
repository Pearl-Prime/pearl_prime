"""Tests for pearl_news.pipeline.heading_selector.

Validates:
  - Heading-variant pools are loaded with the expected sizes.
  - Selection is deterministic across repeated calls for the same (slug, axis).
  - Two distinct slugs spread across the pool (probabilistic sanity check).
  - Missing pool -> fallback string returned.
  - Tradition phrase from teacher_sees is present in the variant (cross-check
    that the YAML variants reference the tradition, not the teacher's name).
"""
from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from pearl_news.pipeline.heading_selector import (  # noqa: E402
    pick_gen_z_heading,
    pick_teacher_sees_heading,
    pool_sizes,
)

ACTIVE_TOPICS = [
    "climate", "mental_health", "education", "peace_conflict",
    "partnerships", "inequality", "economy_work",
]
ACTIVE_LOCALES = ["en", "ja", "zh-cn"]
EN_TEACHERS = ["ahjan", "sai_ma", "maat", "master_sha"]
JA_TEACHERS = ["joshin", "junko", "miki", "omote"]
ZH_TEACHERS = ["master_feung", "master_wu"]
ALL_TEACHERS = EN_TEACHERS + JA_TEACHERS + ZH_TEACHERS


def test_gen_z_pool_has_5_variants_per_topic_locale():
    sizes = pool_sizes()["gen_z_impact"]
    for topic in ACTIVE_TOPICS:
        assert topic in sizes, f"gen_z_impact missing topic {topic}"
        for loc in ACTIVE_LOCALES:
            assert sizes[topic].get(loc) == 5, (
                f"gen_z_impact[{topic}][{loc}] must have exactly 5 variants, "
                f"got {sizes[topic].get(loc)}"
            )


def test_teacher_sees_pool_has_5_variants_per_teacher():
    sizes = pool_sizes()["teacher_sees"]
    for tid in ALL_TEACHERS:
        assert tid in sizes, f"teacher_sees missing teacher {tid}"
        assert sizes[tid] == 5, (
            f"teacher_sees[{tid}] must have exactly 5 variants, got {sizes[tid]}"
        )


def test_gen_z_selection_is_deterministic():
    slug = "pn-master_sha-climate-5"
    picks = {pick_gen_z_heading("climate", "en", slug, "FB") for _ in range(20)}
    assert len(picks) == 1, f"non-deterministic gen_z selection: {picks}"


def test_teacher_sees_selection_is_deterministic():
    slug = "pn-junko-mental_health-2"
    picks = {pick_teacher_sees_heading("junko", slug, "FB") for _ in range(20)}
    assert len(picks) == 1, f"non-deterministic teacher_sees selection: {picks}"


def test_gen_z_spreads_across_slugs():
    """Different slugs should reach different variants over a large sample."""
    seen = set()
    for n in range(40):
        slug = f"pn-ahjan-climate-{n}"
        seen.add(pick_gen_z_heading("climate", "en", slug, "FB"))
    assert len(seen) >= 4, (
        f"gen_z selection clustering on too few variants: only {len(seen)} hit "
        f"across 40 slugs ({seen})"
    )


def test_teacher_sees_spreads_across_slugs():
    seen = set()
    for n in range(40):
        slug = f"pn-master_sha-climate-{n}"
        seen.add(pick_teacher_sees_heading("master_sha", slug, "FB"))
    assert len(seen) >= 4


def test_gen_z_missing_pool_returns_fallback():
    """An unknown topic falls back to the provided string."""
    out = pick_gen_z_heading("not_a_topic", "en", "pn-x-y-1", "FALLBACK_GZ")
    assert out == "FALLBACK_GZ"


def test_teacher_sees_missing_pool_returns_fallback():
    out = pick_teacher_sees_heading("not_a_teacher", "pn-x-y-1", "FALLBACK_TS")
    assert out == "FALLBACK_TS"


def test_master_sha_uses_tradition_not_name():
    """Operator rule: the heading invokes the tradition, not the teacher's
    personal name. Master Sha variants should reference 'Tao Grandmaster',
    never 'Dr. and Master Sha' or 'Master Sha'.
    """
    for n in range(20):
        slug = f"pn-master_sha-climate-{n}"
        h = pick_teacher_sees_heading("master_sha", slug, "FB")
        assert "Tao Grandmaster" in h, f"master_sha variant missing tradition: {h}"
        assert "Master Sha" not in h, f"master_sha variant leaks personal name: {h}"


def test_junko_uses_tradition_not_name():
    for n in range(20):
        slug = f"pn-junko-mental_health-{n}"
        h = pick_teacher_sees_heading("junko", slug, "FB")
        assert "チャネラー" in h, f"junko variant missing 'チャネラー': {h}"
        assert "Junko" not in h, f"junko variant leaks personal name: {h}"
        assert "ジュンコ" not in h, f"junko variant leaks personal name: {h}"


if __name__ == "__main__":
    test_gen_z_pool_has_5_variants_per_topic_locale()
    test_teacher_sees_pool_has_5_variants_per_teacher()
    test_gen_z_selection_is_deterministic()
    test_teacher_sees_selection_is_deterministic()
    test_gen_z_spreads_across_slugs()
    test_teacher_sees_spreads_across_slugs()
    test_gen_z_missing_pool_returns_fallback()
    test_teacher_sees_missing_pool_returns_fallback()
    test_master_sha_uses_tradition_not_name()
    test_junko_uses_tradition_not_name()
    print("All 10 heading_selector tests passed.")
