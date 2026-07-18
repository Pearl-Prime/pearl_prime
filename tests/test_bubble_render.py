"""Tests for bubble_render.py — Pillow-based speech bubble renderer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.manga.chapter.bubble_render import (
    render_bubbles_onto_panel,
    render_bubbles_on_panels,
    _coverage_ratio,
    _zone_to_pixels,
    _ZONE_FRACTIONS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tiny_panel(tmp_path: Path) -> Path:
    """Create a 400×300 solid white RGBA PNG."""
    from PIL import Image
    p = tmp_path / "panel_p01.png"
    img = Image.new("RGBA", (400, 300), (200, 200, 200, 255))
    img.save(str(p))
    return p


@pytest.fixture()
def minimal_dialogue():
    return [
        {
            "speaker": "protagonist",
            "text": "I won't give up!",
            "emotion": "determination",
            "intensity": "shouting",
            "bubble_style": "spiky_emphasis",
            "position_hint": "top_right",
            "tail_style": "pointer",
            "font_override": "bold_action",
        }
    ]


@pytest.fixture()
def two_speaker_dialogue():
    return [
        {
            "speaker": "hero",
            "text": "Ready?",
            "emotion": "neutral",
            "intensity": "normal",
            "bubble_style": "round_normal",
            "position_hint": "top_right",
            "tail_style": "pointer",
            "font_override": None,
        },
        {
            "speaker": "rival",
            "text": "Don't hold back.",
            "emotion": "calm",
            "intensity": "calm",
            "bubble_style": "round_normal",
            "position_hint": "top_left",
            "tail_style": "pointer",
            "font_override": None,
        },
    ]


# ---------------------------------------------------------------------------
# _coverage_ratio
# ---------------------------------------------------------------------------

class TestCoverageRatio:
    def test_single_bubble_50pct(self):
        # 200×150 bubble inside 400×300 panel = 30000/120000 = 0.25
        bubbles = [(0, 0, 200, 150)]
        assert abs(_coverage_ratio(bubbles, 400, 300) - 0.25) < 1e-6

    def test_no_bubbles(self):
        assert _coverage_ratio([], 400, 300) == 0.0

    def test_zero_panel(self):
        assert _coverage_ratio([(0, 0, 10, 10)], 0, 0) == 0.0


# ---------------------------------------------------------------------------
# Zone-to-pixels
# ---------------------------------------------------------------------------

class TestZoneToPixels:
    def test_top_right_zone(self):
        x1, y1, x2, y2 = _zone_to_pixels("top_right", 400, 300)
        assert x1 >= 200 and x2 == 392  # 0.98 * 400
        assert y1 >= 0 and y2 <= 100   # 0.32 * 300 ≈ 96

    def test_all_zones_within_panel(self):
        for zone in _ZONE_FRACTIONS:
            x1, y1, x2, y2 = _zone_to_pixels(zone, 400, 300)
            assert 0 <= x1 < x2 <= 400, f"{zone}: x out of bounds"
            assert 0 <= y1 < y2 <= 300, f"{zone}: y out of bounds"


# ---------------------------------------------------------------------------
# render_bubbles_onto_panel — single bubble shapes
# ---------------------------------------------------------------------------

class TestRenderBubblesOntoPanel:

    def test_round_bubble_creates_file(self, tiny_panel, tmp_path):
        dialogue = [{"speaker": "h", "text": "Hello!", "intensity": "normal",
                     "bubble_style": "round_normal", "position_hint": "top_right",
                     "tail_style": "pointer", "font_override": None}]
        out = tmp_path / "out.png"
        layout = render_bubbles_onto_panel(tiny_panel, dialogue, [], None, out_path=out)
        assert out.is_file()
        assert layout["coverage_ratio"] > 0.0
        assert any(r["type"] == "dialogue" for r in layout["bubbles"])

    def test_spiky_bubble(self, tiny_panel, tmp_path):
        dialogue = [{"speaker": "h", "text": "NOOOOO!", "intensity": "shouting",
                     "bubble_style": "spiky_emphasis", "position_hint": "top_right",
                     "tail_style": "pointer", "font_override": "bold_action"}]
        out = tmp_path / "spiky.png"
        layout = render_bubbles_onto_panel(tiny_panel, dialogue, [], None, out_path=out)
        assert out.is_file()
        assert layout["bubbles"][0]["bubble_style"] == "spiky_emphasis"

    def test_cloud_thought_bubble(self, tiny_panel, tmp_path):
        dialogue = [{"speaker": "h", "text": "Why am I here?", "intensity": "internal",
                     "bubble_style": "cloud_thought", "position_hint": "top_left",
                     "tail_style": "dotless", "font_override": "italic_internal"}]
        out = tmp_path / "cloud.png"
        layout = render_bubbles_onto_panel(tiny_panel, dialogue, [], None, out_path=out)
        assert out.is_file()

    def test_caption_box(self, tiny_panel, tmp_path):
        out = tmp_path / "caption.png"
        layout = render_bubbles_onto_panel(
            tiny_panel, [], [], "Three years earlier...", out_path=out
        )
        assert out.is_file()
        assert any(r["type"] == "caption" for r in layout["bubbles"])

    def test_whisper_bubble(self, tiny_panel, tmp_path):
        dialogue = [{"speaker": "h", "text": "Don't tell anyone...", "intensity": "whisper",
                     "bubble_style": "whisper_dashed", "position_hint": "bottom_left",
                     "tail_style": "pointer", "font_override": "light_whisper"}]
        out = tmp_path / "whisper.png"
        layout = render_bubbles_onto_panel(tiny_panel, dialogue, [], None, out_path=out)
        assert out.is_file()

    def test_scream_bubble(self, tiny_panel, tmp_path):
        dialogue = [{"speaker": "h", "text": "AAAARGH!", "intensity": "screaming",
                     "bubble_style": "scream_ultra", "position_hint": "top_center",
                     "tail_style": "pointer", "font_override": "all_caps_scream"}]
        out = tmp_path / "scream.png"
        layout = render_bubbles_onto_panel(tiny_panel, dialogue, [], None, out_path=out)
        assert out.is_file()

    def test_multi_bubble_panel(self, tiny_panel, two_speaker_dialogue, tmp_path):
        out = tmp_path / "multi.png"
        layout = render_bubbles_onto_panel(
            tiny_panel, two_speaker_dialogue, [], None, out_path=out
        )
        assert out.is_file()
        dlg_records = [r for r in layout["bubbles"] if r["type"] == "dialogue"]
        assert len(dlg_records) == 2
        # Positions should differ
        pos_set = {r["position_hint"] for r in dlg_records}
        assert len(pos_set) == 2

    def test_sfx_rendered_on_panel(self, tiny_panel, tmp_path):
        out = tmp_path / "sfx.png"
        layout = render_bubbles_onto_panel(tiny_panel, [], ["CRACK", "BOOM"], None, out_path=out)
        assert out.is_file()
        sfx_records = [r for r in layout["bubbles"] if r["type"] == "sfx"]
        assert len(sfx_records) == 2

    def test_no_dialogue_panel_unchanged(self, tiny_panel, tmp_path):
        """Panel with no dialogue/sfx/caption: output is just the re-saved PNG."""
        from PIL import Image
        out = tmp_path / "unchanged.png"
        layout = render_bubbles_onto_panel(tiny_panel, [], [], None, out_path=out)
        assert out.is_file()
        # Should have no bubble records
        assert all(r["type"] in ("skipped",) or r.get("type") == "sfx"
                   for r in layout.get("bubbles", [])
                   if r.get("type") not in ("dialogue", "caption"))
        assert layout["coverage_ratio"] == 0.0

    def test_coverage_cap_enforced(self, tiny_panel, tmp_path):
        """Very tight coverage limit should not be exceeded."""
        # Very long text with very low limit to trigger coverage enforcement
        dialogue = [
            {
                "speaker": "h",
                "text": " ".join(["word"] * 50),
                "intensity": "normal",
                "bubble_style": "round_normal",
                "position_hint": "top_right",
                "tail_style": "pointer",
                "font_override": None,
            }
        ]
        out = tmp_path / "capped.png"
        layout = render_bubbles_onto_panel(
            tiny_panel, dialogue, [], None, out_path=out, coverage_limit=0.35
        )
        assert layout["coverage_ratio"] <= 0.35 + 0.01  # small tolerance for integer rounding

    def test_output_path_default(self, tiny_panel):
        """Default out_path is {stem}_bubbled.png beside the source."""
        dialogue = [{"speaker": "h", "text": "Hi", "intensity": "normal",
                     "bubble_style": "round_normal", "position_hint": "top_right",
                     "tail_style": "pointer", "font_override": None}]
        layout = render_bubbles_onto_panel(tiny_panel, dialogue, [], None)
        expected = tiny_panel.with_name("panel_p01_bubbled.png")
        assert Path(layout["out_path"]) == expected
        assert expected.is_file()
        # cleanup
        expected.unlink(missing_ok=True)

    def test_tail_direction_matches_hint(self, tiny_panel, tmp_path):
        """Basic sanity: tail-less (dotless) means no crash, file created."""
        dialogue = [{
            "speaker": "h", "text": "...", "intensity": "internal",
            "bubble_style": "cloud_thought", "position_hint": "top_right",
            "tail_style": "dotless", "font_override": None,
        }]
        out = tmp_path / "dotless.png"
        layout = render_bubbles_onto_panel(tiny_panel, dialogue, [], None, out_path=out)
        assert out.is_file()


# ---------------------------------------------------------------------------
# render_bubbles_on_panels — manifest-level
# ---------------------------------------------------------------------------

class TestRenderBubblesOnPanels:

    def _make_manifest(self, panel_paths: list[tuple[str, Path]]) -> dict:
        return {
            "schema_version": "1.0.0",
            "artifact_type": "panel_images_manifest",
            "panels": [
                {
                    "panel_id": pid,
                    "status": "ok",
                    "path": str(path),
                    "width": 400,
                    "height": 300,
                }
                for pid, path in panel_paths
            ],
        }

    def _make_lettering(self, panel_data: list[dict]) -> dict:
        return {
            "schema_version": "2.0.0",
            "artifact_type": "lettering_spec",
            "lettering_panels": panel_data,
        }

    def _make_panel_png(self, tmp_path: Path, pid: str) -> Path:
        from PIL import Image
        p = tmp_path / f"panel_{pid}.png"
        Image.new("RGBA", (400, 300), (200, 200, 200, 255)).save(str(p))
        return p

    def test_manifest_updated_for_dialogue_panel(self, tmp_path):
        p01 = self._make_panel_png(tmp_path, "p01")
        manifest = self._make_manifest([("p01", p01)])
        lettering = self._make_lettering([
            {
                "panel_id": "p01",
                "silence_confirmed": False,
                "dialogue_lines": [
                    {"speaker": "hero", "text": "Let's go!",
                     "intensity": "normal", "bubble_style": "round_normal",
                     "position_hint": "top_right", "tail_style": "pointer",
                     "font_override": None}
                ],
                "sfx": [],
                "narrator_caption": None,
            }
        ])
        out_dir = tmp_path / "bubbled"
        updated = render_bubbles_on_panels(
            {}, lettering, manifest, None, out_dir
        )
        panel_entry = updated["panels"][0]
        bubbled_path = Path(panel_entry["path"])
        assert "bubbled" in bubbled_path.name
        assert bubbled_path.is_file()
        assert panel_entry["bubble_render"]["applied"] is True

    def test_silent_panel_not_modified(self, tmp_path):
        p01 = self._make_panel_png(tmp_path, "p01")
        original_path = str(p01)
        manifest = self._make_manifest([("p01", p01)])
        lettering = self._make_lettering([
            {
                "panel_id": "p01",
                "silence_confirmed": True,
                "dialogue_lines": [],
                "sfx": [],
                "narrator_caption": None,
            }
        ])
        out_dir = tmp_path / "bubbled"
        updated = render_bubbles_on_panels(
            {}, lettering, manifest, None, out_dir
        )
        # Path should not have changed
        assert updated["panels"][0]["path"] == original_path

    def test_manifest_unchanged_original(self, tmp_path):
        """Original manifest should NOT be mutated (deep copy)."""
        p01 = self._make_panel_png(tmp_path, "p01")
        manifest = self._make_manifest([("p01", p01)])
        import copy
        original_path = manifest["panels"][0]["path"]
        lettering = self._make_lettering([
            {
                "panel_id": "p01",
                "silence_confirmed": False,
                "dialogue_lines": [
                    {"speaker": "h", "text": "Hi",
                     "intensity": "normal", "bubble_style": "round_normal",
                     "position_hint": "top_right", "tail_style": "pointer",
                     "font_override": None}
                ],
                "sfx": [],
                "narrator_caption": None,
            }
        ])
        out_dir = tmp_path / "bubbled"
        render_bubbles_on_panels({}, lettering, manifest, None, out_dir)
        # Original manifest must be unchanged
        assert manifest["panels"][0]["path"] == original_path

    def test_missing_image_path_skipped(self, tmp_path):
        manifest = {
            "schema_version": "1.0.0",
            "artifact_type": "panel_images_manifest",
            "panels": [
                {"panel_id": "p01", "status": "ok",
                 "path": str(tmp_path / "nonexistent.png"), "width": 400, "height": 300}
            ],
        }
        lettering = self._make_lettering([
            {
                "panel_id": "p01",
                "silence_confirmed": False,
                "dialogue_lines": [
                    {"speaker": "h", "text": "Exists?",
                     "intensity": "normal", "bubble_style": "round_normal",
                     "position_hint": "top_right", "tail_style": "pointer",
                     "font_override": None}
                ],
                "sfx": [],
                "narrator_caption": None,
            }
        ])
        out_dir = tmp_path / "bubbled"
        # Should not raise — panel is skipped gracefully
        updated = render_bubbles_on_panels({}, lettering, manifest, None, out_dir)
        # Path should remain as-is (not modified since file was missing)
        assert updated["panels"][0]["path"] == str(tmp_path / "nonexistent.png")
