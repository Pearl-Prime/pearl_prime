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

from check_release_readiness import check

def test_release_stays_partial_without_live_queue_and_approval(tmp_path: Path):
    (tmp_path/"docs").mkdir()
    (tmp_path/"docs/MANGA_RELEASE_RUNBOOK.md").write_text("# runbook")
    report=check(tmp_path)
    assert report["manga-release-readiness"]=="partial"
    assert report["manga-queue-repeatability"]=="blocked"
