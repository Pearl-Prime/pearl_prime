"""ITE QC gates T-01–T-20."""
from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.ite_pipeline import (
    annotate_gutter_therapy,
    annotate_panel_breath,
    build_color_arc,
    load_ite_merged_config,
    run_fractal_check,
    run_ite_qc,
)

FIXTURE = Path(__file__).resolve().parent.parent.parent / "fixtures" / "manga" / "ite_test_chapter.json"


def test_ite_qc_runs_twenty_gates_and_computes_score():
    ch = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    breath = annotate_panel_breath(ch, cfg=cfg)
    color = build_color_arc(breath, None, cfg=cfg)
    gutter = annotate_gutter_therapy(breath, cfg=cfg)
    fractal = run_fractal_check({}, gutter, cfg=cfg)
    sabido = {"positive_model": {}, "negative_model": {}, "transitional": {}}
    report = run_ite_qc(
        chapter_enriched=gutter,
        color_arc=color,
        fractal_report=fractal,
        breath_doc=breath,
        sabido_map=sabido,
        cfg=cfg,
    )
    ids = [g["id"] for g in report["gates"]]
    for i in range(1, 21):
        assert f"T-{i:02d}" in ids
    assert "ITE_score" in report
    assert "dimensions" in report


def test_t04_blocks_on_forbidden_dialogue():
    ch = json.loads(FIXTURE.read_text(encoding="utf-8"))
    ch["pages"][0]["panels"][0]["dialogue"] = ["You need therapy."]
    cfg = load_ite_merged_config()
    breath = annotate_panel_breath(ch, cfg=cfg)
    gutter = annotate_gutter_therapy(breath, cfg=cfg)
    report = run_ite_qc(
        chapter_enriched=gutter,
        color_arc=None,
        fractal_report={"panels": []},
        breath_doc=breath,
        cfg=cfg,
    )
    t04 = next(g for g in report["gates"] if g["id"] == "T-04")
    assert t04["passed"] is False
