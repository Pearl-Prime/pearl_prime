"""Unit tests for scripts/video/build_beat_driven.py — STUBBED render/judge/assemble.

Every external/expensive seam (alignment, ComfyUI render, Ollama judge, ffmpeg
assemble, compat) is injected as a stub, so these run deterministically in CI with
NO GPU, no live Pearl Star box, and NO paid API (CLAUDE.md tier policy). Covers:
beat loading (.py + .json), seed-locked judge items, the AI-judge gate consuming
run_frame_judge, the W3 manifest emit (schema build_daily_batch.py accepts), the
publish-queue round-trip (build_daily_batch discovers + selects the emitted video),
skip flags, and the CLI --manifest-only path.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "video"))

import build_beat_driven as bbd  # noqa: E402
import run_frame_judge as rfj  # noqa: E402


# ───────────────────────── fixtures / stubs ─────────────────────────

def _beats_json(tmp_path: Path, n: int = 3) -> Path:
    beats = [
        {"id": f"b{i}", "text": f"narrative moment {i}", "prompt": f"scene: thing {i}",
         "decision": "render_new"}
        for i in range(n)
    ]
    p = tmp_path / "beats.json"
    p.write_text(json.dumps(beats), encoding="utf-8")
    return p


def _make_frames(frames_dir: Path, frame_base: int, n: int) -> None:
    frames_dir.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        (frames_dir / f"frame_{frame_base + i:04d}.png").write_bytes(b"\x89PNGstub")


def _config(tmp_path: Path, beats: Path, **kw) -> bbd.BeatVideoConfig:
    defaults = dict(
        video_id="test_beat_video",
        beats_path=beats,
        artifact_dir=tmp_path / "art",
        publish_queue_dir=tmp_path / "publish_queue",
        brand_id="stillness_press",
        title="A Test Narrative",
        tags=["test", "narrative"],
        skip_assemble=True,
    )
    defaults.update(kw)
    return bbd.BeatVideoConfig(**defaults)


class PassJudge:
    """Always passes (no re-render); records calls."""

    def __init__(self):
        self.calls = []

    def __call__(self, item: rfj.JudgeItem) -> dict:
        self.calls.append(item.id)
        return {"score": 95, "missing": [], "wrong": [], "present": ["x"], "suggested_fix": ""}


def _no_assemble(config, result):
    return result


def _no_compat(config, result):
    return result


# ───────────────────────── beat loading ─────────────────────────

def test_load_beats_json_list(tmp_path):
    beats = bbd.load_beats(_beats_json(tmp_path, 3))
    assert len(beats) == 3 and beats[0]["id"] == "b0"


def test_load_beats_json_wrapped(tmp_path):
    p = tmp_path / "w.json"
    p.write_text(json.dumps({"beats": [{"id": "x", "text": "t", "prompt": "p"}]}))
    assert bbd.load_beats(p)[0]["id"] == "x"


def test_load_beats_py_module(tmp_path):
    mod = tmp_path / "my_beats.py"
    mod.write_text("BEATS = [{'id': 'a', 'text': 't', 'prompt': 'p', 'decision': 'render_new'}]\n")
    beats = bbd.load_beats(mod)
    assert len(beats) == 1 and beats[0]["id"] == "a"


def test_load_beats_py_without_BEATS_raises(tmp_path):
    mod = tmp_path / "bad.py"
    mod.write_text("X = 1\n")
    with pytest.raises(ValueError):
        bbd.load_beats(mod)


# ───────────────────────── alignment fallback ─────────────────────────

def test_uniform_cadence_is_deterministic_and_sequential():
    beats = [{"id": "a"}, {"id": "b"}]
    timed = bbd.uniform_cadence(beats, per_beat_s=4.0)
    assert timed[0]["start_s"] == 0.0 and timed[0]["end_s"] == 4.0
    assert timed[1]["start_s"] == 4.0


def test_default_align_falls_back_without_whisper(tmp_path):
    cfg = _config(tmp_path, _beats_json(tmp_path, 2))
    timed = bbd.default_align(cfg, bbd.load_beats(cfg.beats_path))
    assert all("start_s" in b for b in timed)


# ───────────────────────── seed-locked judge items ─────────────────────────

def test_judge_items_seed_locked_per_beat(tmp_path):
    cfg = _config(tmp_path, _beats_json(tmp_path, 2))
    builder = bbd.BeatDrivenBuilder(cfg, judge_fn=PassJudge(),
                                    assemble_fn=_no_assemble, compat_fn=_no_compat)
    items = builder._judge_items(bbd.uniform_cadence(bbd.load_beats(cfg.beats_path)))
    # run_frame_judge.seed_for keys on character_id or id — verify determinism here.
    assert rfj.seed_for(items[0].id) != rfj.seed_for(items[1].id)
    assert rfj.seed_for(items[0].id) == rfj.seed_for("b0")


# ───────────────────────── the AI-judge gate (consumes run_frame_judge) ─────────────────────────

def test_build_runs_judge_gate_and_keeps_frames(tmp_path):
    beats = _beats_json(tmp_path, 3)
    cfg = _config(tmp_path, beats)
    _make_frames(cfg.frames_dir, cfg.frame_base, 3)
    judge = PassJudge()
    builder = bbd.BeatDrivenBuilder(cfg, judge_fn=judge, render_fn=None,
                                    assemble_fn=_no_assemble, compat_fn=_no_compat)
    result = builder.build()
    assert len(result.verdicts) == 3
    assert all(v.score == 95 for v in result.verdicts)
    assert len(judge.calls) == 3  # the gate actually ran via run_frame_judge
    assert len(result.kept_frames) == 3


def test_subthreshold_triggers_rerender_via_run_frame_judge(tmp_path):
    """A failing frame is re-rendered through the injected render_fn (keep-best)."""
    beats = _beats_json(tmp_path, 1)
    cfg = _config(tmp_path, beats, judge_threshold=80, judge_max_retries=2)
    _make_frames(cfg.frames_dir, cfg.frame_base, 1)

    scores = iter([55, 92])  # first fail, re-judge pass

    def judge(item):
        s = next(scores)
        return {"score": s, "missing": ["mountain"] if s < 80 else [],
                "wrong": [], "present": [], "suggested_fix": "add mountain"}

    rendered = {"n": 0}

    def render(item, prompt, seed):
        rendered["n"] += 1
        return b"\x89PNGrerender"

    builder = bbd.BeatDrivenBuilder(cfg, judge_fn=judge, rewrite_fn=lambda i, v: i.prompt + " +fix",
                                    render_fn=render, assemble_fn=_no_assemble, compat_fn=_no_compat)
    result = builder.build()
    assert rendered["n"] == 1  # the gate re-rendered the failing frame
    assert result.verdicts[0].score == 92 and result.verdicts[0].attempts == 1


def test_skip_judge_keeps_renders_as_is(tmp_path):
    beats = _beats_json(tmp_path, 2)
    cfg = _config(tmp_path, beats, skip_judge=True)
    _make_frames(cfg.frames_dir, cfg.frame_base, 2)
    builder = bbd.BeatDrivenBuilder(cfg, assemble_fn=_no_assemble, compat_fn=_no_compat)
    result = builder.build()
    assert len(result.verdicts) == 2
    assert all(v.attempts == 0 for v in result.verdicts)


# ───────────────────────── W3 manifest emit ─────────────────────────

def test_emit_manifest_has_canonical_and_routing_keys(tmp_path):
    beats = _beats_json(tmp_path, 2)
    cfg = _config(tmp_path, beats)
    out = bbd.emit_distribution_manifest(
        cfg, result_meta={"primary_asset_ids": ["b0", "b1"], "n_beats": 2,
                          "video_path": "x.mp4"},
        out_path=tmp_path / "m.json")
    doc = json.loads(out.read_text())
    # canonical write_metadata.py keys
    for k in ("video_id", "plan_id", "title", "description", "tags",
              "video_provenance_path", "batch_id", "format", "primary_asset_ids",
              "style_version"):
        assert k in doc, f"missing canonical key {k}"
    # build_daily_batch.py::discover_queue_items routing keys
    for k in ("brand_id", "channel_id", "content_type", "platforms", "created_at"):
        assert k in doc, f"missing routing key {k}"
    assert doc["pipeline"] == "beat_driven_v1"
    assert doc["primary_asset_ids"] == ["b0", "b1"]


def test_build_emits_manifest_into_publish_queue(tmp_path):
    beats = _beats_json(tmp_path, 2)
    cfg = _config(tmp_path, beats)
    _make_frames(cfg.frames_dir, cfg.frame_base, 2)
    builder = bbd.BeatDrivenBuilder(cfg, judge_fn=PassJudge(),
                                    assemble_fn=_no_assemble, compat_fn=_no_compat)
    result = builder.build()
    expected = cfg.publish_queue_dir / cfg.video_id / "distribution_manifest.json"
    assert result.manifest_path == expected
    assert expected.exists()


# ───────────────────────── publish-queue round-trip (the whole point) ─────────────────────────

def test_emitted_manifest_is_discoverable_and_selectable_by_build_daily_batch(tmp_path):
    """A best video, once built, ENTERS the publish queue build_daily_batch selects from."""
    import build_daily_batch as bdb  # noqa: E402

    beats = _beats_json(tmp_path, 2)
    queue = tmp_path / "publish_queue"
    cfg = _config(tmp_path, beats, video_id="round_trip_video",
                  publish_queue_dir=queue, brand_id="stillness_press")
    _make_frames(cfg.frames_dir, cfg.frame_base, 2)
    bbd.BeatDrivenBuilder(cfg, judge_fn=PassJudge(),
                          assemble_fn=_no_assemble, compat_fn=_no_compat).build()

    # build_daily_batch.discover_queue_items must find + parse the emitted manifest.
    items = bdb.discover_queue_items(queue, brand_filter="stillness_press")
    assert len(items) == 1
    found = items[0]
    assert found["video_id"] == "video-round_trip_video" or found["video_id"] == "round_trip_video"
    # scoring (the selection step) must accept the manifest without error.
    score = bdb.score_candidate(found, {"priority": {}}, "Monday")
    assert isinstance(score, float)
    # brand filter isolation: a different brand sees nothing.
    assert bdb.discover_queue_items(queue, brand_filter="other_brand") == []


# ───────────────────────── CLI ─────────────────────────

def test_cli_help():
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "video" / "build_beat_driven.py"), "--help"],
        cwd=REPO_ROOT, capture_output=True, text=True)
    assert r.returncode == 0
    assert "--beats" in r.stdout and "--video-id" in r.stdout
    assert "--comfyui-url" in r.stdout and "--manifest-only" in r.stdout


def test_cli_manifest_only_emits_queue_entry(tmp_path):
    beats = _beats_json(tmp_path, 2)
    queue = tmp_path / "publish_queue"
    r = subprocess.run([
        sys.executable, str(REPO_ROOT / "scripts" / "video" / "build_beat_driven.py"),
        "--video-id", "cli_video", "--beats", str(beats),
        "--artifact-dir", str(tmp_path / "art"),
        "--publish-queue-dir", str(queue),
        "--brand-id", "stillness_press", "--manifest-only",
    ], cwd=REPO_ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    manifest = queue / "cli_video" / "distribution_manifest.json"
    assert manifest.exists()
    doc = json.loads(manifest.read_text())
    assert doc["video_id"] == "cli_video" and doc["brand_id"] == "stillness_press"
    out = json.loads(r.stdout)
    assert out["enters_publish_queue"] is True


# NOTE: run_pipeline.py --pipeline-mode beat_driven wiring is INTENTIONALLY deferred
# to a separate PR (it flips run_pipeline's default path — a consequential change).
# See docs/specs/PEARL_VIDEO_BEAT_DRIVEN_RUN_PIPELINE_WIRING_FOLLOWON.md for the spec.
# The builder is fully exercised standalone above; the route test belongs with that PR.


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
