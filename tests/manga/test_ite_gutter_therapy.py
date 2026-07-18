"""ITE gutter therapy."""
from __future__ import annotations

import json
import math
from pathlib import Path

from phoenix_v4.manga.ite_pipeline import (
    annotate_gutter_therapy,
    annotate_panel_breath,
    load_ite_merged_config,
)

FIXTURE = Path(__file__).resolve().parent.parent.parent / "fixtures" / "manga" / "ite_test_chapter.json"


def test_post_high_band_gutter_classes():
    ch = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    with_breath = annotate_panel_breath(ch, cfg=cfg)
    out = annotate_gutter_therapy(with_breath, cfg=cfg)
    by_id = {}
    for page in out["pages"]:
        for p in page["panels"]:
            by_id[p["panel_id"]] = p
    assert by_id["p03"]["gutter_after_class"] in ("wide", "breath", "page_break")
    assert by_id["p04"]["gutter_after_class"] in ("breath", "page_break")


def test_resolution_pages_avoid_tight_gutter():
    ch = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    out = annotate_gutter_therapy(ch, cfg=cfg)
    page_count = len(out["pages"])
    res_page = max(1, int(math.ceil(page_count * 0.75)))
    for page in out["pages"]:
        pn = int(page.get("page_number") or 0)
        if pn < res_page:
            continue
        for p in page.get("panels") or []:
            assert str(p.get("gutter_after_class") or "").lower() != "tight"
