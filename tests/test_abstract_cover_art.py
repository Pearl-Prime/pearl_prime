"""Tests for the abstract cover-art background + deterministic per-author
fingerprint (scripts.publish.abstract_cover_art).

Pins the anti-spam invariant: same author -> identical signature; different
authors -> distinct signatures; composites (no brand seed) are well spread;
and the sai_ma/sai_maa alias resolves to one fingerprint.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.publish import abstract_cover_art as aca  # noqa: E402


def test_fingerprint_is_deterministic():
    a = aca.fingerprint("ahjan", "inner_light_press", "anxiety")
    b = aca.fingerprint("ahjan", "inner_light_press", "anxiety")
    assert a == b


def test_fingerprint_differs_across_authors():
    a = aca.fingerprint("auth_one", None, "imposter_syndrome")
    b = aca.fingerprint("auth_two", None, "imposter_syndrome")
    signature = lambda fp: (fp["grad_top"], fp["accent"], fp["style_var"], fp["direction"])
    assert signature(a) != signature(b)


def test_many_composites_are_visually_distinct():
    """30 composite authors (no brand seed) -> near-all-unique gradients."""
    tops = {aca.fingerprint(f"author_{i}", f"brand_{i}", "anxiety")["grad_top"]
            for i in range(30)}
    assert len(tops) >= 28


def test_sai_ma_alias_normalises_to_sai_maa():
    assert (aca.fingerprint("sai_ma", "healing_ground_press", "grief")
            == aca.fingerprint("sai_maa", "healing_ground_press", "grief"))


def test_seeded_palette_flagged_and_valid():
    fp = aca.fingerprint("x", "b", "anxiety", primary_hex="#1A4D5C")
    assert fp["seeded"] is True
    assert len(fp["grad_top"]) == 3 and all(0 <= c <= 255 for c in fp["grad_top"])


def test_topic_symbol_mapping():
    assert aca.fingerprint("x", None, "boundaries")["motif"] == "divider"
    assert aca.fingerprint("x", None, "self_worth")["motif"] == "whole_circle"
    assert aca.fingerprint("x", None, "imposter_syndrome")["motif"] == "twin_rings"


def test_build_background_returns_canvas_and_meta():
    bg, meta = aca.build_background(
        "imposter_syndrome", primary_hex="#FF6B6B",
        author_id="miki", brand_id="gen_spark",
        symbol_zone={"x_pct": [32, 68], "y_pct": [57, 80]},
        title_zone={"x_pct": [6, 94], "y_pct": [11, 41]},
    )
    assert bg.size == (1600, 2560)
    assert meta["abstract_background"] is True
    assert meta["text_hex"].startswith("#")
    assert "accent_hex" in meta and "title_family" in meta


def test_build_background_distinct_authors_differ_in_pixels():
    z = {"x_pct": [30, 70], "y_pct": [55, 80]}
    tz = {"x_pct": [8, 92], "y_pct": [11, 40]}
    a, _ = aca.build_background("boundaries", primary_hex="#D67054",
                               author_id="alpha", symbol_zone=z, title_zone=tz)
    b, _ = aca.build_background("boundaries", primary_hex="#D67054",
                               author_id="omega", symbol_zone=z, title_zone=tz)
    diff = sum(1 for pa, pb in zip(a.convert("RGB").getdata(),
                                   b.convert("RGB").getdata()) if pa != pb)
    assert diff > 1000, f"different fingerprints should differ visibly (diff_px={diff})"


def test_light_field_uses_dark_ink_text():
    """A light primary -> deep-ink title (no stroke); dark primary -> cream."""
    _, light = aca.build_background("boundaries", primary_hex="#F5EFE3",
                                    author_id="z", title_zone={"x_pct": [8, 92], "y_pct": [11, 40]})
    assert aca._lum(aca._hex_to_rgb(light["text_hex"])) < 0.5
