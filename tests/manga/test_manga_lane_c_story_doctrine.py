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
import validate_story_doctrine as lane

def test_manga_story_doctrine_passes_visual_carrier_and_rejects_lecture():
    contract=yaml.safe_load((REPO/"config/manga/story_doctrine_contract.yaml").read_text())
    story={"genre_id":"mecha","chapters":[{"chapter_end_hook":"launch","plot_beats":[{"beat_text":"The warning light returns.","story_function":"opening_hook","doctrine_id":"d1","craft_carrier":"metaphor","emotional_delta":"fear_to_choice"}]}]}
    assert lane.validate_story(story,contract=contract)["passed"]
    story["chapters"][0]["plot_beats"][0]["beat_text"]="The lesson is that you must understand."
    report=lane.validate_story(story,contract=contract)
    assert not report["passed"]
    assert any(x["rule"]=="STORY-LECTURE-001" for x in report["failures"])
