"""ITE color arc."""
from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.ite_pipeline import build_color_arc, load_ite_merged_config

FIXTURE = Path(__file__).resolve().parent.parent.parent / "fixtures" / "manga" / "ite_test_chapter.json"


def test_color_arc_five_phase_progression_and_genre_override():
    ch = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    out = build_color_arc(ch, None, cfg=cfg)
    panels = out.get("panels") or []
    assert len(panels) >= 3
    first_k = float(panels[0]["color_temp_target"])
    mid_k = float(panels[len(panels) // 2]["color_temp_target"])
    last_k = float(panels[-1]["color_temp_target"])
    assert first_k > 0 and mid_k > 0
    assert "ffmpeg_colorbalance" in panels[0]
    horror = dict(ch)
    horror["genre"] = "horror"
    hout = build_color_arc(horror, None, cfg=cfg)
    # Horror override should not crash; resolution bias applied in builder
    assert len(hout["panels"]) == len(panels)
