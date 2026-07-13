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

from validate_manga_contract_trace import validate_trace_rows

def row():
    return {"series_id":"s","episode_id":"e","chapter_id":"c","panel_id":"p","beat_id":"b","doctrine_id":"d","layer_role":"L2","support_zone_id":"floor","lettering_locale":"en_US"}

def test_trace_fails_beat_mismatch_and_passes_exact():
    assert validate_trace_rows([row()],[row()])["passed"]
    bad=row(); bad["beat_id"]="wrong"
    report=validate_trace_rows([row()],[bad])
    assert not report["passed"]
    assert any(x["rule"]=="TRACE-BEAT-001" for x in report["failures"])
