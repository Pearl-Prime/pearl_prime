"""Unit tests for scripts/video/assemble_mixed.py.

These do NOT require ffmpeg: the subprocess calls are mocked. We test only the pure
logic — CSV-row -> source-path resolution (regular / manga / fallback cases) and the
ffconcat manifest string builder.
"""
from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from scripts.video import assemble_mixed as am


# ── Fixtures: a fake on-disk frames/manga tree ─────────────────────────────────────


@pytest.fixture()
def tree(tmp_path):
    project = tmp_path / "proj"
    frames = project / "frames"
    manga = project / "manga_frames"
    frames.mkdir(parents=True)
    manga.mkdir(parents=True)
    # regular frames are .jpg; manga renders are .png (the real-world convention)
    (frames / "a.jpg").write_text("x")
    (frames / "b.jpg").write_text("x")
    (frames / "c.jpg").write_text("x")
    (manga / "manga_a.png").write_text("x")  # a has a manga render
    # b has NO manga render -> should trigger manga->regular fallback
    return {"project": project, "frames": frames, "manga": manga}


def _resolve(row, tree):
    return am.resolve_source(
        row,
        frames_dir=tree["frames"],
        manga_dir=tree["manga"],
        project_dir=tree["project"],
    )


# ── manga_path_for / extension normalization ───────────────────────────────────────


def test_manga_path_for_normalizes_jpg_to_png(tmp_path):
    p = am.manga_path_for("x.jpg", manga_dir=tmp_path)
    assert p == tmp_path / "manga_x.png"
    assert am.manga_path_for("y.jpeg", manga_dir=tmp_path) == tmp_path / "manga_y.png"
    assert am.manga_path_for("z.png", manga_dir=tmp_path) == tmp_path / "manga_z.png"


def test_normalize_manga_render_fixes_extension():
    assert am._normalize_manga_render("manga_frames/manga_a.jpg") == "manga_frames/manga_a.png"
    assert am._normalize_manga_render("manga_frames/manga_a.png") == "manga_frames/manga_a.png"


# ── resolve_source: REGULAR ────────────────────────────────────────────────────────


def test_resolve_regular_via_chosen_render(tree):
    row = {"chosen_frame": "a.jpg", "chosen_style": "regular", "chosen_render": "frames/a.jpg", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "regular"
    assert path == tree["frames"] / "a.jpg"


def test_resolve_regular_reconstructed_when_render_empty(tree):
    row = {"chosen_frame": "b.jpg", "chosen_style": "regular", "chosen_render": "", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "regular"
    assert path == tree["frames"] / "b.jpg"


def test_resolve_regular_missing_file_unresolved(tree):
    row = {"chosen_frame": "missing.jpg", "chosen_style": "regular", "chosen_render": "", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "unresolved"
    assert path is None


# ── resolve_source: MANGA ──────────────────────────────────────────────────────────


def test_resolve_manga_via_chosen_render_with_ext_normalization(tree):
    # builder exports manga_frames/manga_a.jpg (wrong ext); resolver must find .png
    row = {"chosen_frame": "a.jpg", "chosen_style": "manga", "chosen_render": "manga_frames/manga_a.jpg", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "manga"
    assert path == tree["manga"] / "manga_a.png"


def test_resolve_manga_reconstructed_when_render_empty(tree):
    row = {"chosen_frame": "a.jpg", "chosen_style": "manga", "chosen_render": "", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "manga"
    assert path == tree["manga"] / "manga_a.png"


def test_resolve_manga_missing_falls_back_to_regular(tree):
    # b has no manga render but b.jpg exists -> fallback_manga
    row = {"chosen_frame": "b.jpg", "chosen_style": "manga", "chosen_render": "manga_frames/manga_b.jpg", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "fallback_manga"
    assert path == tree["frames"] / "b.jpg"


def test_resolve_manga_missing_and_no_regular_twin_unresolved(tree):
    row = {"chosen_frame": "nope.jpg", "chosen_style": "manga", "chosen_render": "", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "unresolved"
    assert path is None


# ── resolve_source: EMPTY / UNPICKED ───────────────────────────────────────────────


def test_resolve_empty_pick_is_fallback_empty(tree):
    row = {"chosen_frame": "", "chosen_style": "regular", "chosen_render": "", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "fallback_empty"
    assert path is None


def test_resolve_unknown_style_defaults_to_regular(tree):
    # any non-manga style with a valid frame resolves as regular
    row = {"chosen_frame": "c.jpg", "chosen_style": "", "chosen_render": "", "start_sec": "0"}
    path, kind = _resolve(row, tree)
    assert kind == "regular"
    assert path == tree["frames"] / "c.jpg"


# ── build_timeline: counts + held-frame fallback ───────────────────────────────────


def test_build_timeline_counts_and_hold_previous(tree):
    rows = [
        {"section": "0", "chosen_frame": "a.jpg", "chosen_style": "regular", "chosen_render": "frames/a.jpg", "start_sec": "0"},
        {"section": "1", "chosen_frame": "a.jpg", "chosen_style": "manga", "chosen_render": "manga_frames/manga_a.jpg", "start_sec": "1"},
        {"section": "2", "chosen_frame": "b.jpg", "chosen_style": "manga", "chosen_render": "manga_frames/manga_b.jpg", "start_sec": "2"},  # fallback->regular
        {"section": "3", "chosen_frame": "", "chosen_style": "regular", "chosen_render": "", "start_sec": "3"},  # empty -> hold prev
    ]
    timeline, counts, warnings = am.build_timeline(
        rows, frames_dir=tree["frames"], manga_dir=tree["manga"], project_dir=tree["project"]
    )
    assert counts == {"regular": 1, "manga": 1, "fallback": 2}
    # 4 entries: regular a, manga a, fallback-regular b, held-prev (b again)
    assert len(timeline) == 4
    assert timeline[0][1] == tree["frames"] / "a.jpg"
    assert timeline[1][1] == tree["manga"] / "manga_a.png"
    assert timeline[2][1] == tree["frames"] / "b.jpg"
    assert timeline[3][1] == tree["frames"] / "b.jpg"  # held previous
    assert any("held previous frame" in w for w in warnings)


def test_build_timeline_sorts_by_start(tree):
    rows = [
        {"section": "0", "chosen_frame": "a.jpg", "chosen_style": "regular", "chosen_render": "frames/a.jpg", "start_sec": "5"},
        {"section": "1", "chosen_frame": "b.jpg", "chosen_style": "regular", "chosen_render": "frames/b.jpg", "start_sec": "1"},
    ]
    timeline, _, _ = am.build_timeline(
        rows, frames_dir=tree["frames"], manga_dir=tree["manga"], project_dir=tree["project"]
    )
    assert [t[0] for t in timeline] == [1.0, 5.0]


def test_build_timeline_empty_first_pick_skipped(tree):
    rows = [
        {"section": "0", "chosen_frame": "", "chosen_style": "regular", "chosen_render": "", "start_sec": "0"},
    ]
    timeline, counts, warnings = am.build_timeline(
        rows, frames_dir=tree["frames"], manga_dir=tree["manga"], project_dir=tree["project"]
    )
    assert timeline == []
    assert counts["fallback"] == 1
    assert any("no previous frame" in w for w in warnings)


# ── build_ffconcat: manifest string ────────────────────────────────────────────────


def test_build_ffconcat_shape_and_durations():
    timeline = [
        (0.0, Path("/x/a.jpg")),
        (2.0, Path("/x/b.png")),
        (5.0, Path("/x/c.jpg")),
    ]
    out = am.build_ffconcat(timeline, audio_end=10.0)
    lines = out.strip().split("\n")
    assert lines[0] == "ffconcat version 1.0"
    # 3 file+duration pairs + 1 trailing file (no duration) = 7 lines
    assert lines[1] == "file '/x/a.jpg'"
    assert lines[2] == "duration 2.000000"  # 2.0 - 0.0
    assert lines[3] == "file '/x/b.png'"
    assert lines[4] == "duration 3.000000"  # 5.0 - 2.0
    assert lines[5] == "file '/x/c.jpg'"
    assert lines[6] == "duration 5.000000"  # audio_end 10 - 5
    # trailing repeated entry, no duration
    assert lines[7] == "file '/x/c.jpg'"
    assert len(lines) == 8


def test_build_ffconcat_clamps_nonpositive_duration():
    # two entries with the same start would give 0s; must clamp to a positive epsilon
    timeline = [(0.0, Path("/x/a.jpg")), (0.0, Path("/x/b.jpg"))]
    out = am.build_ffconcat(timeline, audio_end=4.0)
    lines = out.strip().split("\n")
    assert lines[2] == "duration 0.001000"  # clamped


def test_build_ffconcat_empty_raises():
    with pytest.raises(ValueError):
        am.build_ffconcat([], audio_end=10.0)


# ── synth_default_rows: parse the v3.8 concat manifest ──────────────────────────────


def test_synth_default_rows_from_concat(tmp_path):
    concat = tmp_path / "frames_concat_v3_8.txt"
    concat.write_text(
        "ffconcat version 1.0\n"
        "file '/p/frames/a.jpg'\n"
        "duration 2.000000\n"
        "file '/p/frames/b.jpg'\n"
        "duration 3.000000\n"
        "file '/p/frames/b.jpg'\n"  # trailing repeat, no duration
    )
    rows = am.synth_default_rows(orig_concat=concat)
    assert len(rows) == 2  # trailing repeat not counted
    assert rows[0]["chosen_frame"] == "a.jpg"
    assert rows[0]["chosen_style"] == "regular"
    assert rows[0]["chosen_render"] == "frames/a.jpg"
    assert rows[0]["start_sec"] == "0.000000"
    assert rows[1]["start_sec"] == "2.000000"  # running sum
    assert rows[1]["chosen_frame"] == "b.jpg"


# ── encode/mux smoke: subprocess is mocked, no ffmpeg invoked ───────────────────────


def test_encode_silent_mocks_ffmpeg(tmp_path):
    concat = tmp_path / "c.txt"
    concat.write_text("ffconcat version 1.0\n")
    out = tmp_path / "out.mp4"

    def fake_run(cmd, **kw):
        # simulate ffmpeg writing the file
        out.write_bytes(b"\x00" * (3 * 1024 * 1024))
        return mock.Mock(returncode=0, stderr="")

    with mock.patch.object(am.subprocess, "run", side_effect=fake_run) as m:
        am.encode_silent(concat, out)
    assert m.called
    cmd = m.call_args[0][0]
    assert cmd[0] == "ffmpeg"
    assert "libx264" in cmd
    assert str(out) in cmd


def test_mux_audio_maps_streams(tmp_path):
    silent = tmp_path / "s.mp4"
    silent.write_bytes(b"\x00")
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"\x00")
    out = tmp_path / "final.mp4"

    def fake_run(cmd, **kw):
        out.write_bytes(b"\x00" * (1024 * 1024))
        return mock.Mock(returncode=0, stderr="")

    with mock.patch.object(am.subprocess, "run", side_effect=fake_run) as m:
        am.mux_audio(silent, audio, out, "EN")
    cmd = m.call_args[0][0]
    assert "-map" in cmd and "0:v" in cmd and "1:a" in cmd
    assert "aac" in cmd
