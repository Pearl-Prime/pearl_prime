"""Tests for bubble_render_v2 (SVG hulls, furigana, vertical, manifests).

Does not assume ``cairosvg`` — raster path falls back to Pillow like v1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.svg_bubble_library import (  # type: ignore
    BUBBLE_STYLE_IDS,
    bubble_svg,
)
from phoenix_v4.manga.chapter.bubble_render_v2 import (  # type: ignore
    render_bubbles_onto_panel_v2,
    render_bubbles_on_panels_v2,
    _effective_bubble_style,
)


def _panel(tmp_path: Path, name: str = "panel.png"):
    from PIL import Image

    p = tmp_path / name
    Image.new("RGB", (240, 200), color=(128, 120, 100)).save(p)
    return p


def test_svg_styles_generate_markup_each():
    """All registered styles emit well-formed-ish SVG wrappers."""
    for sid in BUBBLE_STYLE_IDS:
        xml = bubble_svg(sid, 120, 80)
        assert xml.startswith("<svg")
        assert 'xmlns="http://www.w3.org/2000/svg"' in xml


def test_effective_style_demonic_maps_to_wave():
    line = {"bubble_style": "round_normal", "demonic_bubble": {"enabled": True}}
    assert _effective_bubble_style(line) == "wavy_supernatural"


def test_effective_style_respects_non_demonic():
    line = {"bubble_style": "cloud_thought"}
    assert _effective_bubble_style(line) == "cloud_thought"


def test_v2_writes_text_manifest_and_png(tmp_path):
    panel = _panel(tmp_path)
    lines = [{"speaker": "A", "text": "Yo", "intensity": "normal", "bubble_style": "round_normal"}]
    out = tmp_path / "out.png"
    mf = tmp_path / "manifest.json"
    layout = render_bubbles_onto_panel_v2(
        panel,
        lines,
        sfx=[],
        narrator_caption=None,
        out_path=out,
        locale="en_US",
        emit_text_manifest=True,
        manifest_out_path=mf,
    )
    assert out.is_file()
    assert mf.is_file()
    assert layout.get("text_manifest_path")
    data = json.loads(mf.read_text(encoding="utf-8"))
    assert data["rehydration_pattern"] == "text_rehydrated_at_publish_time"
    assert any(e.get("kind") == "dialogue" for e in data["entries"])


def test_skip_text_overlay_still_writes_manifest(tmp_path):
    panel = _panel(tmp_path, "p2.png")
    lines = [{"speaker": "A", "text": "Hidden", "bubble_style": "round_normal"}]
    out = tmp_path / "hidden.png"
    mf = tmp_path / "hidden.json"
    render_bubbles_onto_panel_v2(
        panel,
        lines,
        sfx=[],
        narrator_caption=None,
        out_path=out,
        skip_text_overlay=True,
        manifest_out_path=mf,
    )
    doc = json.loads(mf.read_text(encoding="utf-8"))
    lines_entry = [e for e in doc["entries"] if e.get("kind") == "dialogue"]
    assert lines_entry and lines_entry[0]["text"] == "Hidden"


def test_v3_text_by_locale_ja(tmp_path):
    panel = _panel(tmp_path, "jp.png")
    lines = [
        {
            "speaker": "A",
            "text_by_locale": {"ja_JP": "東京", "en_US": "Tokyo"},
            "bubble_style": "round_normal",
        }
    ]
    out = tmp_path / "jp_out.png"
    lay = render_bubbles_onto_panel_v2(
        panel, lines, sfx=[], narrator_caption=None, out_path=out, locale="ja_JP"
    )
    placed = [r for r in lay["bubbles"] if r.get("type") == "dialogue"]
    assert any("東京" in str(r.get("text", "")) for r in placed)


def test_furigana_line_metadata_in_layout(tmp_path):
    panel = _panel(tmp_path, "f.png")
    lines = [
        {
            "speaker": "A",
            "text_by_locale": {"ja_JP": "東京の漢字"},
            "bubble_style": "round_normal",
            "furigana": [{"base": "東京", "reading": "とうきょう"}],
        }
    ]
    out = tmp_path / "fu.png"
    lay = render_bubbles_onto_panel_v2(
        panel, lines, sfx=[], narrator_caption=None, out_path=out, locale="ja_JP"
    )
    dlg = [r for r in lay["bubbles"] if r.get("type") == "dialogue"]
    assert dlg[0].get("furigana")


def test_vertical_kanji_flag_in_layout(tmp_path):
    panel = _panel(tmp_path, "v.png")
    lines = [
        {
            "speaker": "A",
            "text_by_locale": {"ja_JP": "縦書き"},
            "vertical_kanji": True,
            "bubble_style": "shojo_soft",
        }
    ]
    lay = render_bubbles_onto_panel_v2(
        panel, lines, sfx=[], narrator_caption=None, out_path=tmp_path / "vv.png", locale="ja_JP"
    )
    dlg = [r for r in lay["bubbles"] if r.get("type") == "dialogue"]
    assert dlg and dlg[0].get("vertical_kanji") is True


def test_each_legacy_v1_style_renders(tmp_path):
    v1_styles = (
        "round_normal",
        "spiky_emphasis",
        "cloud_thought",
        "square_narration",
        "whisper_dashed",
        "scream_ultra",
        "electronic_sharp",
        "drip_horror",
        "shojo_soft",
    )
    idx = 0
    for st in v1_styles:
        panel = _panel(tmp_path, f"zs_{idx}.png")
        render_bubbles_onto_panel_v2(
            panel,
            [{"speaker": "Z", "text": "!", "bubble_style": st}],
            sfx=[],
            narrator_caption=None,
            out_path=tmp_path / f"zo_{idx}.png",
            locale="en_US",
            emit_text_manifest=False,
        )
        assert (tmp_path / f"zo_{idx}.png").is_file()
        idx += 1


def test_v2_exclusive_styles_render(tmp_path):
    for idx, st in enumerate(("wavy_supernatural", "off_panel", "singing")):
        panel = _panel(tmp_path, f"wv_{idx}.png")
        outp = tmp_path / f"wvo_{idx}.png"
        render_bubbles_onto_panel_v2(
            panel,
            [{"speaker": "Z", "text": "sing", "bubble_style": st}],
            sfx=[],
            narrator_caption=None,
            out_path=outp,
            emit_text_manifest=False,
        )
        assert outp.stat().st_size > 600


@pytest.mark.parametrize("style_id", BUBBLE_STYLE_IDS)
def test_bubble_svg_contains_shape_nodes(style_id: str):
    xml = bubble_svg(style_id, 60, 50)
    tags = ("<ellipse", "<rect", "<polygon", "<circle", "<path", "<g ")
    assert any(t in xml for t in tags)


def test_manifest_panel_level_on_panels_v2(tmp_path):
    from PIL import Image

    p_png = tmp_path / "pane.png"
    Image.new("RGB", (180, 180), color=(240, 240, 235)).save(p_png)
    manifest = {
        "artifact_type": "panel_images_manifest",
        "panels": [{"panel_id": "p01", "status": "ok", "path": str(p_png)}],
    }
    letter = {
        "artifact_type": "lettering_spec",
        "default_locale": "en_US",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "silence_confirmed": False,
                "dialogue_lines": [
                    {"speaker": "Hero", "text": "Fight", "bubble_style": "spiky_emphasis"}
                ],
            }
        ],
    }
    out_dir = tmp_path / "pub"
    upd = render_bubbles_on_panels_v2({}, letter, manifest, None, out_dir, locale="en_US")
    assert upd["bubble_render_v2_summary"]["panels_processed"] == 1
    entry = upd["panels"][0]
    assert entry.get("bubble_render_v2", {}).get("text_manifest_path")


def test_zh_vertical_dialogue_records(tmp_path):
    panel = _panel(tmp_path, "zc.png")
    lay = render_bubbles_onto_panel_v2(
        panel,
        [
            {
                "speaker": "A",
                "text_by_locale": {"zh_CN": "简体"},
                "vertical_kanji": True,
                "bubble_style": "round_normal",
            }
        ],
        sfx=[],
        narrator_caption=None,
        out_path=tmp_path / "zc_out.png",
        locale="zh_CN",
    )
    dlg = [r for r in lay["bubbles"] if r.get("type") == "dialogue"]
    assert dlg and dlg[0].get("vertical_kanji") is True


def test_narrator_caption_in_manifest(tmp_path):
    panel = _panel(tmp_path, "n.png")
    mf = tmp_path / "nar.json"
    render_bubbles_onto_panel_v2(
        panel,
        [],
        sfx=[],
        narrator_caption="Later.",
        manifest_out_path=mf,
        emit_text_manifest=True,
        out_path=tmp_path / "nout.png",
    )
    js = json.loads(mf.read_text(encoding="utf-8"))
    assert js["narrator_caption"] == "Later."
    kinds = [e["kind"] for e in js["entries"]]
    assert "narrator_caption" in kinds


def test_sfx_in_manifest_when_present(tmp_path):
    panel = _panel(tmp_path, "sx.png")
    mf = tmp_path / "sx.json"
    render_bubbles_onto_panel_v2(
        panel,
        [],
        sfx=["BANG"],
        narrator_caption=None,
        manifest_out_path=mf,
        out_path=tmp_path / "sxout.png",
    )
    js = json.loads(mf.read_text(encoding="utf-8"))
    assert "BANG" in js["sfx"]
