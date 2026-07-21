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

from build_blind_read_packet import validate_human_bar

def test_human_bar_blocks_missing_and_accepts_complete_human_approval(tmp_path: Path):
    assert validate_human_bar(scorecards=[],operator_approval=None)["blind-read-bar"]=="blocked"
    card={"reader_id":"r","episode_id":"e","story_flow_score":4,"genre_hook_score":4,"subtle_embed_score":4,"lettering_readability_score":4,"layout_readability_score":4,"visual_composition_score":4,"checklist":{k:True for k in ("no_floating_or_unclear_layered_panels","coherent_story_flow","genre_hook_works","subtle_embed_without_lecture","teacher_music_diegetic_if_enabled","lettering_readable","page_webtoon_layout_readable")},"approve":True}
    cp=tmp_path/"card.json"; cp.write_text(json.dumps(card))
    ap=tmp_path/"approval.json"; ap.write_text('{"approved":true,"operator_id":"op"}')
    assert validate_human_bar(scorecards=[cp],operator_approval=ap)["blind-read-bar"]=="green"
