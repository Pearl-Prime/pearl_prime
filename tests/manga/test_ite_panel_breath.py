"""ITE panel breath engine."""
from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.ite_pipeline import annotate_panel_breath, load_ite_merged_config

FIXTURE = Path(__file__).resolve().parent.parent.parent / "fixtures" / "manga" / "ite_test_chapter.json"


def test_breath_places_sequence_with_four_phases():
    ch = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    out = annotate_panel_breath(ch, cfg=cfg)
    seqs = out.get("breath_sequences") or []
    assert len(seqs) >= 1
    s0 = seqs[0]
    phases = set(s0.get("phases_present") or [])
    assert phases == {"inhale", "hold", "exhale", "pause"}

    phases_on_panels = []
    for page in out.get("pages") or []:
        for p in page.get("panels") or []:
            if "breath_phase" in p:
                phases_on_panels.append(p["breath_phase"])
    assert "inhale" in phases_on_panels and "hold" in phases_on_panels
