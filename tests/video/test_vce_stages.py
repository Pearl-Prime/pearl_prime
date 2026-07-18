"""Unit tests for VCE stage CLIs (fixtures/video_pipeline)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIX = REPO_ROOT / "fixtures" / "video_pipeline"
VID = REPO_ROOT / "scripts" / "video"
PY = sys.executable
_NJC = ["--no-job-check"]


@pytest.fixture
def tmp_video_plan(tmp_path):
    out = tmp_path / "plan"
    out.mkdir()
    # Minimal resolved + shot_plan + timeline-like inputs built from golden flow
    manifest = FIX / "render_manifest.json"
    if not manifest.exists():
        pytest.skip("fixtures missing")
    r = subprocess.run(
        [PY, str(VID / "prepare_script_segments.py"), str(manifest), "-o", str(out / "script_segments.json"), "--force"] + _NJC,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    subprocess.run(
        [PY, str(VID / "run_shot_planner.py"), str(out / "script_segments.json"), "-o", str(out / "shot_plan.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    subprocess.run(
        [PY, str(VID / "run_asset_resolver.py"), str(out / "shot_plan.json"), "-o", str(out / "resolved_assets.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    subprocess.run(
        [PY, str(VID / "run_timeline_builder.py"), str(out / "shot_plan.json"), str(out / "resolved_assets.json"),
         "-o", str(out / "timeline.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    return out


def test_layer_compositor_help():
    r = subprocess.run([PY, str(VID / "run_layer_compositor.py"), "--help"], cwd=REPO_ROOT, capture_output=True, text=True)
    assert r.returncode == 0
    assert "Layer compositor" in r.stdout


def test_layer_compositor_writes_json(tmp_video_plan):
    out = tmp_video_plan
    r = subprocess.run(
        [PY, str(VID / "run_layer_compositor.py"), str(out / "resolved_assets.json"), str(out / "shot_plan.json"),
         "-o", str(out / "composited_layers.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads((out / "composited_layers.json").read_text(encoding="utf-8"))
    assert "shots" in data and data["shots"]
    assert "filter_complex" in data["shots"][0]


def test_animation_engine_writes_json(tmp_video_plan):
    out = tmp_video_plan
    subprocess.run(
        [PY, str(VID / "run_layer_compositor.py"), str(out / "resolved_assets.json"), str(out / "shot_plan.json"),
         "-o", str(out / "composited_layers.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    r = subprocess.run(
        [PY, str(VID / "run_animation_engine.py"), str(out / "composited_layers.json"), str(out / "shot_plan.json"),
         str(out / "timeline.json"), "-o", str(out / "animation_plan.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    ap = json.loads((out / "animation_plan.json").read_text(encoding="utf-8"))
    assert ap.get("shots") and ap["shots"][0].get("motion_type")


def test_soundtrack_engine_writes_json(tmp_video_plan):
    out = tmp_video_plan
    subprocess.run(
        [PY, str(VID / "prepare_script_segments.py"), str(FIX / "render_manifest.json"), "-o", str(out / "script_segments.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    subprocess.run(
        [PY, str(VID / "run_soundtrack_engine.py"), str(out / "timeline.json"), str(out / "shot_plan.json"),
         str(out / "script_segments.json"), "-o", str(out / "soundtrack_plan.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    sp = json.loads((out / "soundtrack_plan.json").read_text(encoding="utf-8"))
    assert sp.get("mix_spec") and sp.get("suno_api_calls")


def test_platform_and_multilang(tmp_video_plan):
    out = tmp_video_plan
    for script, outp in [
        ("run_layer_compositor.py", "composited_layers.json"),
        ("run_animation_engine.py", "animation_plan.json"),
    ]:
        cmd = [PY, str(VID / script)]
        if script == "run_layer_compositor.py":
            cmd += [str(out / "resolved_assets.json"), str(out / "shot_plan.json"), "-o", str(out / outp), "--force"]
        else:
            cmd += [str(out / "composited_layers.json"), str(out / "shot_plan.json"), str(out / "timeline.json"),
                    "-o", str(out / outp), "--force"]
        cmd += _NJC
        subprocess.run(cmd, cwd=REPO_ROOT, check=True)
    subprocess.run(
        [PY, str(VID / "prepare_script_segments.py"), str(FIX / "render_manifest.json"), "-o", str(out / "script_segments.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    subprocess.run(
        [PY, str(VID / "run_soundtrack_engine.py"), str(out / "timeline.json"), str(out / "shot_plan.json"),
         str(out / "script_segments.json"), "-o", str(out / "soundtrack_plan.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    stub = {"video_id": "v1", "plan_id": "plan-therapeutic-001", "title": "t", "description": "d", "tags": [], "primary_asset_ids": ["a"], "channel_id": "ch_001"}
    (out / "stub.json").write_text(json.dumps(stub), encoding="utf-8")
    subprocess.run(
        [PY, str(VID / "run_platform_adapter.py"), str(out / "timeline.json"), str(out / "stub.json"),
         str(out / "animation_plan.json"), "-o", str(out / "platform_variants.json"), "--platforms", "youtube", "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    subprocess.run(
        [PY, str(VID / "run_caption_adapter.py"), str(out / "timeline.json"), str(out / "script_segments.json"),
         "-o", str(out / "captions.json"), "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    subprocess.run(
        [PY, str(VID / "run_multilang_renderer.py"), str(out / "soundtrack_plan.json"), str(out / "platform_variants.json"),
         str(out / "captions.json"), "-o", str(out / "multilang_plan.json"), "--languages", "en,zh-CN", "--force"] + _NJC,
        cwd=REPO_ROOT, check=True,
    )
    ml = json.loads((out / "multilang_plan.json").read_text(encoding="utf-8"))
    assert len(ml["locales"]) == 2


def test_analytics_ingestor(tmp_path):
    dist = tmp_path / "dist.json"
    dist.write_text(json.dumps({"video_id": "v", "plan_id": "p", "hook_type": "light_reveal"}), encoding="utf-8")
    out = tmp_path / "af.json"
    subprocess.run(
        [PY, str(VID / "run_analytics_ingestor.py"), str(dist), "-o", str(out), "--force"],
        cwd=REPO_ROOT, check=True,
    )
    assert "shot_planner_feedback" in json.loads(out.read_text(encoding="utf-8"))


def test_pipeline_test_vce_001():
    man = FIX / "render_manifest_test_vce_001.json"
    if not man.exists():
        pytest.skip("fixture missing")
    r = subprocess.run(
        [PY, str(VID / "run_pipeline.py"), "--plan-id", "test-vce-001", "--fixtures-dir", str(FIX),
         "--format", "short", "--platforms", "youtube,tiktok", "--languages", "en,zh-CN", "--force",
         "--no-job-check", "--skip-render"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    root = REPO_ROOT / "artifacts" / "video" / "test-vce-001"
    for name in ("composited_layers.json", "animation_plan.json", "soundtrack_plan.json", "platform_variants.json",
                 "multilang_plan.json", "qc_summary.json", "analytics_feedback.json"):
        assert (root / name).exists(), name
