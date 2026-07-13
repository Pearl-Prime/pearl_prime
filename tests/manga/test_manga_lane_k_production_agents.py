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

def test_nine_roles_have_contracts_and_failure_handoffs():
    doc=yaml.safe_load((REPO/"config/manga/production_line_agents.yaml").read_text())
    roles=doc["roles"]
    assert len(roles)==9
    for role,row in roles.items():
        assert row["job"] and row["inputs"] and row["outputs"]
        assert row["contract"] and row["acceptance_tests"] and row["failure_handoff"]
