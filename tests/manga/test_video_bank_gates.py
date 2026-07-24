"""Gate-chain mutation tests for validate_capture_frames."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FRAMES = REPO / "tests" / "fixtures" / "manga" / "video_bank" / "frames"


def test_good_frame_passes_class_a_and_outfit() -> None:
    from scripts.manga.video_bank.validate_capture_frames import validate_frame

    v = validate_frame(
        FRAMES / "frame_good.png",
        anchor=FRAMES / "anchor.png",
        outfit_ref=FRAMES / "outfit_ref.png",
        pose_id="front_portrait_seated_calm",
        distance_fn=lambda a, b: 0.1,
        skip_blob=True,
    )
    assert v.ok, v.to_dict()
    assert v.rejected_at is None


def test_bad_alpha_rejects_at_class_a() -> None:
    from scripts.manga.video_bank.validate_capture_frames import validate_frame

    v = validate_frame(
        FRAMES / "frame_bad_alpha.png",
        anchor=FRAMES / "anchor.png",
        outfit_ref=FRAMES / "outfit_ref.png",
        pose_id="front_portrait_seated_calm",
        distance_fn=lambda a, b: 0.1,
        skip_blob=True,
    )
    assert not v.ok
    assert v.rejected_at == "class_a_l2_gates"


def test_face_distance_over_threshold_rejects() -> None:
    from scripts.manga.video_bank.validate_capture_frames import validate_frame

    v = validate_frame(
        FRAMES / "frame_good.png",
        anchor=FRAMES / "anchor.png",
        outfit_ref=FRAMES / "outfit_ref.png",
        pose_id="front_portrait_seated_calm",
        distance_fn=lambda a, b: 0.55,
        skip_blob=True,
    )
    assert not v.ok
    assert v.rejected_at == "qa_face_distance"


def test_curate_drops_surplus(tmp_path: Path) -> None:
    from scripts.manga.video_bank.validate_capture_frames import (
        validate_capture_frames,
        write_verdict_tsv,
    )

    frames = [
        FRAMES / "frame_good.png",
        FRAMES / "outfit_ref.png",
        FRAMES / "anchor.png",
    ]
    verdicts = validate_capture_frames(
        frames,
        anchor=FRAMES / "anchor.png",
        demanded_pose_ids=["front_portrait_seated_calm"],
        outfit_ref=FRAMES / "outfit_ref.png",
        pose_ids=["front_portrait_seated_calm", "extra_a", "extra_b"],
        distance_fn=lambda a, b: 0.05,
        skip_blob=True,
    )
    n_pass = sum(1 for v in verdicts if v.ok)
    assert n_pass == 1
    out = tmp_path / "verdicts.tsv"
    write_verdict_tsv(verdicts, out)
    text = out.read_text(encoding="utf-8")
    assert "PASS" in text and "REJECT" in text
