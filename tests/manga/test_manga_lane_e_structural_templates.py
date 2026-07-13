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

import validate_structural_template_coverage as lane

def test_all_eight_templates_and_bridges_are_present():
    report=lane.validate_coverage(REPO/"config/manga/structural_templates.yaml",REPO/"config/manga/panel_type_structural_bridge.yaml")
    assert report["passed"]
    assert report["manga-structural-template-count"]==8
