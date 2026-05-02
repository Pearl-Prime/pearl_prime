"""Tests for R7 identity-system integration:

* identity_compose_prompt.py     — prompt composer using R6 YAML
* render_kdp_cover.py            — identity overlay (brand/author/book)
* cover_quality_gates.py         — 6 automated quality gates
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from PIL import Image

from scripts.publish import (
    cover_quality_gates,
    identity_compose_prompt,
    render_kdp_cover,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
IDENTITY_YAML = REPO_ROOT / "config" / "publishing" / "cover_identity_system.yaml"


# ─── identity YAML schema ────────────────────────────────────────────


def test_identity_yaml_loads_and_validates():
    cfg = identity_compose_prompt.load_identity_system()
    assert cfg["schema_version"] == 1
    assert "brands" in cfg and len(cfg["brands"]) >= 13
    assert "authors" in cfg and len(cfg["authors"]) >= 13
    assert "books" in cfg and len(cfg["books"]) >= 13
    # every book must point at an author that points at a brand
    for book_id, book in cfg["books"].items():
        author_id = book.get("author_id")
        assert author_id in cfg["authors"], f"{book_id} → unknown author {author_id}"
        brand_id = cfg["authors"][author_id]["brand_id"]
        assert brand_id in cfg["brands"], f"{book_id} → unknown brand {brand_id}"


# ─── identity_compose_prompt composer ────────────────────────────────


def test_compose_identity_positive_for_all_image_books():
    cfg = identity_compose_prompt.load_identity_system()
    image_books = [
        bid for bid, b in cfg["books"].items()
        if b.get("cover_kind") != "type_only"
    ]
    assert len(image_books) >= 8
    for book_id in image_books:
        prompt = identity_compose_prompt.compose_identity_positive(book_id)
        assert prompt and len(prompt) > 50, f"empty/short prompt for {book_id}"
        # Identity prompt must include the per-book unique subject.
        subject = cfg["books"][book_id]["this_book_subject"]
        # Loose check — first 4 substantive words appear in composed prompt.
        first_chunk = " ".join(subject.split()[:4]).lower()
        assert first_chunk in prompt.lower(), (
            f"{book_id}: composed prompt missing subject leader '{first_chunk}'"
        )


def test_compose_raises_for_type_only_books():
    # maat and miki are flagged type_only in R6.
    assert identity_compose_prompt.book_is_type_only("maat")
    assert identity_compose_prompt.book_is_type_only("miki")
    with pytest.raises(ValueError):
        identity_compose_prompt.compose_identity_positive("maat")


def test_compose_includes_brand_palette_and_motif():
    prompt = identity_compose_prompt.compose_identity_positive("ahjan")
    # ahjan → inner_light_press; brand palette primary 0E1B33; motif horizon
    assert "0E1B33".lower() in prompt.lower() or "0e1b33" in prompt.lower()
    assert "horizon" in prompt.lower()


# ─── render_kdp_cover identity overlay ───────────────────────────────


def test_brand_palette_overrides_template_primary(tmp_path):
    # ahjan_anxiety → R4 anxiety template; identity book 'ahjan' should
    # override palette.primary to brand inner_light_press primary 0E1B33.
    out_path = tmp_path / "ahjan.png"
    meta = render_kdp_cover.render_kdp_cover(
        illustration_path=None,
        title="The Alarm Is Lying",
        author="Ahjan",
        subtitle="A Nervous System Guide",
        genre="boundaries",  # type_dominant so we can render w/o imagery
        output_path=out_path,
        book_id="ahjan",
    )
    assert meta["identity"]["identity_applied"] is True
    assert meta["identity"]["brand_palette_primary"].lower() == "#0e1b33"
    assert meta["palette"]["primary"].lower() == "#0e1b33"


def test_signature_color_applied_to_subtitle(tmp_path):
    out_path = tmp_path / "ahjan_subtitle.png"
    meta = render_kdp_cover.render_kdp_cover(
        illustration_path=None,
        title="The Alarm Is Lying",
        author="Ahjan",
        subtitle="A Nervous System Guide",
        genre="boundaries",
        output_path=out_path,
        book_id="ahjan",
    )
    # ahjan signature = #7AA3C7 — should appear in identity meta
    assert meta["identity"]["author_signature_color"].lower() == "#7aa3c7"


def test_micro_palette_shift_recorded_on_book(tmp_path):
    out_path = tmp_path / "master_sha.png"
    meta = render_kdp_cover.render_kdp_cover(
        illustration_path=None,
        title="The Weight of Gone",
        author="Master Sha",
        subtitle="A Gentle Guide",
        genre="boundaries",
        output_path=out_path,
        book_id="master_sha",
    )
    assert meta["identity"]["micro_palette_shift"]
    assert "cream" in meta["identity"]["micro_palette_shift"].lower()


def test_type_only_book_forces_type_dominant(tmp_path):
    # 'maat' is type_only in R6. Even if we pass an image-bearing genre,
    # the identity layer must force type_dominant.
    out_path = tmp_path / "maat_type_only.png"
    meta = render_kdp_cover.render_kdp_cover(
        illustration_path=None,
        title="The No That Saved Me",
        author="Ma'at",
        subtitle="A Practical Guide",
        genre="anxiety",   # would normally need illustration
        output_path=out_path,
        book_id="maat",
    )
    assert meta["type_dominant"] is True
    assert meta["identity"]["type_only_override"] is True


def test_render_works_without_book_id(tmp_path):
    """Backward compatibility: omit book_id, no identity overlay applied."""
    out_path = tmp_path / "nobook.png"
    meta = render_kdp_cover.render_kdp_cover(
        illustration_path=None,
        title="Test Title",
        author="Author",
        subtitle="Subtitle",
        genre="boundaries",
        output_path=out_path,
    )
    assert meta["identity"]["identity_applied"] is False


# ─── cover_quality_gates ──────────────────────────────────────────────


def test_quality_gates_module_exposes_all_six_gates():
    expected = {
        "gate_focal_clarity_thumbnail",
        "gate_title_ocr_legibility",
        "gate_color_count_le_3",
        "gate_brand_palette_delta_e",
        "gate_signature_color_present",
        "gate_warm_off_white",
    }
    for name in expected:
        assert hasattr(cover_quality_gates, name), f"missing gate: {name}"


def test_color_count_gate_flags_high_color_image(tmp_path):
    # Build a 5-color image: 5 vertical bands.
    img = Image.new("RGB", (250, 200))
    bands = [(20, 40, 80), (200, 60, 60), (60, 200, 60), (200, 200, 60), (200, 60, 200)]
    for i, color in enumerate(bands):
        for x in range(i * 50, (i + 1) * 50):
            for y in range(200):
                img.putpixel((x, y), color)
    result = cover_quality_gates.gate_color_count_le_3(img)
    assert result["gate"] == "color_count_le_3"
    assert result["passed"] is False
    assert result["dominant_count"] >= 4


def test_color_count_gate_passes_two_color_image(tmp_path):
    img = Image.new("RGB", (200, 200), (14, 27, 51))
    # Add a small accent block (~10%).
    for x in range(80, 120):
        for y in range(80, 120):
            img.putpixel((x, y), (122, 163, 199))
    result = cover_quality_gates.gate_color_count_le_3(img)
    assert result["passed"] is True
    assert result["dominant_count"] <= 3


def test_run_all_gates_returns_six_gates(tmp_path):
    img = Image.new("RGB", (1600, 2560), (14, 27, 51))
    cover_path = tmp_path / "blank.png"
    img.save(cover_path)
    report = cover_quality_gates.run_all_gates(cover_path, book_id="ahjan")
    gate_names = {g["gate"] for g in report["gates"]}
    assert gate_names == {
        "focal_clarity_thumbnail",
        "title_ocr_legibility",
        "color_count_le_3",
        "warm_off_white",
        "brand_palette_delta_e",
        "signature_color_present",
    }
