"""Tests for assemble_from_bank.py — deterministic bank assembly.

Covers:
    - manifest validation (provenance mandatory, bbox mandatory for cutout
      classes, bad layer_class refused)
    - §10 composite math: tight-crop, min-scale, centered paste
    - z-order: L3 above_L2 vs below_L2 occlusion actually flips pixels
    - L4 screen blend lightens, never darkens
    - determinism: same manifest → byte-identical panel output
    - provenance table written with REAL/INTERIM counts

Run from repo root:
    PYTHONPATH=. python3 -m pytest scripts/manga/tests/test_assemble_from_bank.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def bank(tmp_path: Path) -> dict[str, Path]:
    """Synthetic layer assets: green L0 plate, red L2 square, blue L3 dot."""
    paths = {}
    l0 = Image.new("RGBA", (200, 300), (0, 200, 0, 255))
    paths["l0"] = tmp_path / "l0.png"
    l0.save(paths["l0"])

    l2 = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(20, 80):
        for y in range(20, 80):
            l2.putpixel((x, y), (200, 0, 0, 255))
    paths["l2"] = tmp_path / "l2.png"
    l2.save(paths["l2"])

    l3 = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    for x in range(10, 50):
        for y in range(10, 50):
            l3.putpixel((x, y), (0, 0, 200, 255))
    paths["l3"] = tmp_path / "l3.png"
    l3.save(paths["l3"])

    l4 = Image.new("RGBA", (200, 300), (80, 80, 80, 120))
    paths["l4"] = tmp_path / "l4.png"
    l4.save(paths["l4"])
    return paths


def _manifest(bank: dict[str, Path], tmp_path: Path, *, l3_z: str = "above_L2",
              with_l4: bool = False) -> Path:
    layers = [
        {"layer_class": "L0", "asset": str(bank["l0"]), "provenance": "REAL"},
        {"layer_class": "L2", "asset": str(bank["l2"]),
         "bbox_pct": [25, 25, 50, 50], "provenance": "REAL"},
        {"layer_class": "L3", "asset": str(bank["l3"]),
         "bbox_pct": [30, 30, 30, 30], "z_order": l3_z, "provenance": "INTERIM",
         "provenance_note": "test sprite"},
    ]
    if with_l4:
        layers.append({"layer_class": "L4", "asset": str(bank["l4"]),
                       "blend": "screen", "provenance": "INTERIM"})
    m = {
        "schema_version": "1.0.0",
        "series_id": "test_series",
        "manifest_id": "t",
        "canvas": {"width": 200, "height": 300, "background_hex": "#FFFFFF"},
        "panels": [{"panel_id": "p1", "layers": layers}],
    }
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(m))
    return p


# ── validation ───────────────────────────────────────────────────────────────


def test_provenance_mandatory(bank, tmp_path):
    m = yaml.safe_load(_manifest(bank, tmp_path).read_text())
    del m["panels"][0]["layers"][1]["provenance"]
    errors = afb.validate_manifest(m)
    assert any("provenance" in e for e in errors)


def test_bbox_mandatory_for_cutouts(bank, tmp_path):
    m = yaml.safe_load(_manifest(bank, tmp_path).read_text())
    del m["panels"][0]["layers"][1]["bbox_pct"]
    errors = afb.validate_manifest(m)
    assert any("bbox_pct required" in e for e in errors)


def test_bad_layer_class_refused(bank, tmp_path):
    m = yaml.safe_load(_manifest(bank, tmp_path).read_text())
    m["panels"][0]["layers"][0]["layer_class"] = "L9"
    errors = afb.validate_manifest(m)
    assert any("bad layer_class" in e for e in errors)


# ── §10 math ─────────────────────────────────────────────────────────────────


def test_composite_scales_into_bbox_centered(bank):
    canvas = Image.new("RGBA", (200, 300), (255, 255, 255, 255))
    cutout = Image.open(bank["l2"]).convert("RGBA")
    afb.composite_layer(canvas, cutout, [25, 25, 50, 50])
    # tight content is 60x60 → min-scale into 100x150 target = ×1.667 → 100x100
    # centered: x span [50,150], y span [75+25=100, 200]
    assert canvas.getpixel((100, 150))[:3] == (200, 0, 0)   # center is red
    assert canvas.getpixel((40, 150))[:3] == (255, 255, 255)  # outside bbox untouched
    assert canvas.getpixel((100, 90))[:3] == (255, 255, 255)  # above centered paste


def test_z_order_flip_changes_occlusion(bank, tmp_path):
    out_a = tmp_path / "above"
    out_b = tmp_path / "below"
    afb.run(_manifest(bank, tmp_path, l3_z="above_L2"), out_a)
    # rewrite manifest with below_L2 (same file name → same panel id)
    afb.run(_manifest(bank, tmp_path, l3_z="below_L2"), out_b)
    a = Image.open(out_a / "p1.png")
    b = Image.open(out_b / "p1.png")
    # overlap zone: L3 bbox [30,30,30,30] on 200x300 → x∈[60,120], y∈[90,180]
    # above_L2 → blue wins in the overlap; below_L2 → red wins
    assert a.getpixel((90, 135))[:3] == (0, 0, 200)
    assert b.getpixel((90, 135))[:3] == (200, 0, 0)


def test_l4_screen_blend_never_darkens(bank, tmp_path):
    out = tmp_path / "l4out"
    afb.run(_manifest(bank, tmp_path, with_l4=True), out)
    img = Image.open(out / "p1.png").convert("RGB")
    base = Image.open(bank["l0"]).convert("RGB")
    # sample a pure-L0 pixel: screen blend must not darken any channel
    px, bx = img.getpixel((10, 290)), base.getpixel((10, 290))
    assert all(p >= b for p, b in zip(px, bx))


# ── determinism + provenance ─────────────────────────────────────────────────


def test_deterministic_output(bank, tmp_path):
    m = _manifest(bank, tmp_path)
    out1, out2 = tmp_path / "r1", tmp_path / "r2"
    afb.run(m, out1)
    afb.run(m, out2)
    assert (out1 / "p1.png").read_bytes() == (out2 / "p1.png").read_bytes()


def test_provenance_table_written(bank, tmp_path):
    out = tmp_path / "prov"
    result = afb.run(_manifest(bank, tmp_path), out)
    assert (out / "_provenance.json").is_file()
    assert (out / "_provenance.md").is_file()
    assert result["provenance"]["layers_real"] == 2
    assert result["provenance"]["layers_interim"] == 1


def test_refuses_unlabeled_manifest(bank, tmp_path):
    mp = _manifest(bank, tmp_path)
    m = yaml.safe_load(mp.read_text())
    del m["panels"][0]["layers"][2]["provenance"]
    mp.write_text(yaml.safe_dump(m))
    with pytest.raises(ValueError, match="provenance"):
        afb.run(mp, tmp_path / "refused")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
