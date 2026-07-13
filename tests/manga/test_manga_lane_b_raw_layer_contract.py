from __future__ import annotations
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest
from PIL import Image
REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts" / "manga"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import yaml
import raw_v5_layer_contract as lane

def test_prompt_contract_has_required_negative_clauses():
    cfg=yaml.safe_load((REPO/"config/manga/raw_v5_layer_contract.yaml").read_text())
    positive,negative=lane.compile_prompt("hero",config=cfg)
    assert "layer_01" in positive
    assert "no ladder or background fragments in layer_02" in negative
    assert "no invisible legs" in negative

def test_contaminated_primary_role_is_not_green(tmp_path: Path):
    p=tmp_path/"p"; p.mkdir()
    Image.new("RGBA",(80,80),(1,1,1,255)).save(p/"layer_00.png")
    Image.new("RGBA",(80,80),(2,2,2,255)).save(p/"layer_01.png")
    fg=Image.new("RGBA",(80,80),(0,0,0,0))
    for box in ((20,5,55,70),(2,2,18,18)):
        for x in range(box[0],box[2]):
            for y in range(box[1],box[3]):
                fg.putpixel((x,y),(200,0,0,255))
    fg.save(p/"layer_02.png")
    (p/"_telemetry.json").write_text("{}")
    report=lane.assess_panel(p)
    assert report["raw-v5-layer-roles"]=="not-green"
    assert report["selected-component-fallback"]=="preserved"
