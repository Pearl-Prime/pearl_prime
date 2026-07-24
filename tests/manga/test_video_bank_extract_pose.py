"""extract_frames + make_pose_from_video_frame smoke tests (no cloud)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CLIP = REPO / "tests" / "fixtures" / "manga" / "video_bank" / "tiny_clip.mp4"
FRAME = REPO / "tests" / "fixtures" / "manga" / "video_bank" / "frames" / "frame_good.png"


@pytest.mark.skipif(not CLIP.is_file(), reason="tiny_clip fixture missing")
def test_extract_frames_keyed(tmp_path: Path) -> None:
    from scripts.manga.video_bank.extract_frames import extract_frames, keyed_timestamps

    times = keyed_timestamps(5.0, 10)
    assert 8 <= len(times) <= 12 or len(times) == 10
    cands = extract_frames(CLIP, tmp_path / "out", target_count=6, duration_s=1.0)
    assert len(cands) == 6
    assert any(c.kept for c in cands)
    meta = json.loads((tmp_path / "out" / "extract_manifest.json").read_text(encoding="utf-8"))
    assert meta["kept_count"] >= 1


def test_make_pose_stub_writes_sidecars(tmp_path: Path) -> None:
    from scripts.manga.video_bank.make_pose_from_video_frame import make_pose

    out = tmp_path / "pose.png"
    result = make_pose(
        FRAME,
        out,
        source_clip=str(CLIP),
        frame_index=0,
        backend="stub",
        pose_id="front_portrait_seated_calm",
        provenance="INTERIM",
    )
    out_path = Path(result["out"])
    assert out_path.name.endswith("_INTERIM.png")
    assert out_path.with_suffix(".provenance.json").is_file()
    # composition sidecar uses stem.composition.json
    comp = out_path.parent / (out_path.stem + ".composition.json")
    assert comp.is_file()
    prov = json.loads(out_path.with_suffix(".provenance.json").read_text(encoding="utf-8"))
    assert prov["provenance"] == "INTERIM"
    assert prov["source_clip"] == str(CLIP)
    assert prov["frame_index"] == 0
    assert "extraction_command" in prov
    assert "real_replacement" in prov
    composition = json.loads(comp.read_text(encoding="utf-8"))
    assert composition["layer_class"] == "L2"
    assert "anchor" in composition
