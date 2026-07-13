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

import integrate_real_v5_structural as lane

def _panel(root: Path):
    p = root / "p1"; p.mkdir(parents=True)
    for name in ("layer_00.png","layer_01.png","layer_02.png"):
        Image.new("RGBA",(20,20),(1,2,3,255)).save(p/name)
    (p/"_telemetry.json").write_text(json.dumps({"panel_id":"p1"}))
    return p

def _assembler(**kwargs):
    out=Path(kwargs["out_dir"]); out.mkdir(parents=True,exist_ok=True)
    (out/"structural_plan.json").write_text("{}")
    (out/"assembly_manifest.yaml").write_text("layers:\\n- layer_01.png\\n- layer_02.png\\n")
    (out/"gate_report.json").write_text(json.dumps({"panels":[{"passed":True,"gates":[{"gate":g} for g in lane.REQUIRED_GATES]}]}))
    (out/"_provenance.json").write_text(json.dumps({"records":[{"asset":"layer_01.png"},{"asset":"layer_02.png"}]}))
    (out/"REAL_V5_STRUCTURAL_CLOSEOUT.json").write_text(json.dumps({"selected_candidate":{"source_name":"layer_02.png","removed_px":0}}))
    final=out/"p1.png"; Image.new("RGBA",(20,20),(4,5,6,255)).save(final)
    return SimpleNamespace(final_path=final)

def test_integrates_and_rejects_layer00_authority(tmp_path: Path):
    _panel(tmp_path/"workspace")
    report=lane.integrate_workspace(workspace=tmp_path/"workspace",out_dir=tmp_path/"out",assembler=_assembler)
    assert report["green_count"]==1
    assert "layer_00.png" not in (tmp_path/"out/p1/assembly_manifest.yaml").read_text()

def test_layer00_in_provenance_blocks(tmp_path: Path):
    _panel(tmp_path/"workspace")
    def bad(**kwargs):
        result=_assembler(**kwargs)
        (Path(kwargs["out_dir"])/"_provenance.json").write_text('{"records":[{"asset":"layer_00.png"}]}')
        return result
    with pytest.raises(Exception,match="layer_00"):
        lane.integrate_workspace(workspace=tmp_path/"workspace",out_dir=tmp_path/"out",assembler=bad)
