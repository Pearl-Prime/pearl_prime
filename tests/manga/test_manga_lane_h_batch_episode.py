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

from run_episode_production import run_episode

def _assembler(**kwargs):
    out=Path(kwargs["out_dir"]); out.mkdir(parents=True,exist_ok=True); pid=kwargs["panel_id"]
    (out/"structural_plan.json").write_text("{}")
    (out/"assembly_manifest.yaml").write_text("layers:\\n- layer_01.png\\n- layer_02.png\\n")
    gates=["L0_STRUCTURAL_PURITY","L2_STRUCTURAL_PURITY","L2_QUALITY","L0_SUPPORT_ZONE"]
    (out/"gate_report.json").write_text(json.dumps({"panels":[{"passed":True,"gates":[{"gate":g} for g in gates]}]}))
    (out/"_provenance.json").write_text('{"records":[{"asset":"layer_01.png"},{"asset":"layer_02.png"}]}')
    (out/"REAL_V5_STRUCTURAL_CLOSEOUT.json").write_text('{"selected_candidate":{"source_name":"layer_03.png","removed_px":25}}')
    final=out/f"{pid}.png"; Image.new("RGBA",(20,20),(1,1,1,255)).save(final)
    return SimpleNamespace(final_path=final)

def test_batch_episode_writes_required_status_artifacts(tmp_path: Path):
    p=tmp_path/"episode/p1"; p.mkdir(parents=True)
    for name in ("layer_00.png","layer_01.png","layer_02.png"):
        Image.new("RGBA",(20,20),(1,2,3,255)).save(p/name)
    (p/"_telemetry.json").write_text('{"panel_id":"p1"}')
    result=run_episode(episode_root=tmp_path/"episode",out_dir=tmp_path/"out",assembler=_assembler)
    assert result["manga-batch-episode-lane"]=="green"
    assert (tmp_path/"out/panel_status.tsv").is_file()
    assert json.loads((tmp_path/"out/gate_summary.json").read_text())["passed"]==1
