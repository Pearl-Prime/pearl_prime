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

from manga_100pct_final_integrator import integrate

def test_final_integrator_is_not_green_when_closeouts_missing(tmp_path: Path):
    cfg=tmp_path/"cfg.yaml"
    cfg.write_text("""lanes:
  I:
    closeout: artifacts/analysis/I.md
  M:
    closeout: artifacts/analysis/M.md
""")
    report=integrate(tmp_path,cfg)
    assert report["manga-100pct-final"]=="NOT_GREEN"
