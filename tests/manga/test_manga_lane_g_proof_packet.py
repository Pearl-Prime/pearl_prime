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

from build_manga_100pct_proof_packet import ProofPacketError, build_packet

def test_packet_hashes_files_and_rejects_users_paths(tmp_path: Path):
    proof=tmp_path/"proof"; proof.mkdir()
    (proof/"a.json").write_text('{"ok":true}')
    assert build_packet(roots=[proof],out_dir=tmp_path/"out")["record_count"]==1
    (proof/"bad.json").write_text('{"path":"/Users/operator/x"}')
    with pytest.raises(ProofPacketError):
        build_packet(roots=[proof],out_dir=tmp_path/"badout")
