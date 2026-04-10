"""Smoke tests for unified pipeline job enforcement."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd or REPO,
        capture_output=True,
        text=True,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(REPO)},
    )


def test_create_job_and_render_blocked_without_prior_stages(tmp_path: Path) -> None:
    ws = tmp_path / "vj"
    r = _run(
        [
            sys.executable,
            str(REPO / "scripts/pipeline/create_job.py"),
            "--pipeline",
            "video",
            "--teacher",
            "ahjan",
            "--topic",
            "anxiety",
            "--brand",
            "stillness_press",
            "--format",
            "short",
            "--locale",
            "en-US",
            "--workspace",
            str(ws),
        ]
    )
    assert r.returncode == 0, r.stderr
    assert (ws / "job.json").is_file()

    r2 = _run(
        [
            sys.executable,
            str(REPO / "scripts/video/run_render.py"),
            str(REPO / "fixtures/video_pipeline/timeline.json"),
            "-o",
            str(ws / "out"),
            "--placeholder",
            "--workspace",
            str(ws),
        ]
    )
    assert r2.returncode != 0, "render should be blocked before earlier stages pass"


def test_acknowledge_enables_first_stage_only(tmp_path: Path) -> None:
    ws = tmp_path / "vj2"
    reg = REPO / "fixtures/video_pipeline/render_manifest.json"
    assert reg.is_file(), "fixture missing"
    r = _run(
        [
            sys.executable,
            str(REPO / "scripts/pipeline/create_job.py"),
            "--pipeline",
            "video",
            "--teacher",
            "ahjan",
            "--topic",
            "anxiety",
            "--brand",
            "stillness_press",
            "--format",
            "short",
            "--locale",
            "en-US",
            "--workspace",
            str(ws),
        ]
    )
    assert r.returncode == 0, r.stderr
    r_ack = _run(
        [sys.executable, str(REPO / "scripts/pipeline/acknowledge_guide.py"), "--workspace", str(ws)]
    )
    assert r_ack.returncode == 0, r_ack.stderr
    job = json.loads((ws / "job.json").read_text(encoding="utf-8"))
    assert job.get("guide_acknowledged") is True

    seg_out = ws / "script_segments.json"
    r_prep = _run(
        [
            sys.executable,
            str(REPO / "scripts/video/prepare_script_segments.py"),
            str(reg),
            "-o",
            str(seg_out),
            "--workspace",
            str(ws),
        ]
    )
    assert r_prep.returncode == 0, r_prep.stderr + r_prep.stdout
    job2 = json.loads((ws / "job.json").read_text(encoding="utf-8"))
    st = {s["name"]: s["status"] for s in job2.get("stages", [])}
    assert st.get("script_prep") == "pass"


def test_no_job_check_allows_render(tmp_path: Path) -> None:
    ws = tmp_path / "vj3"
    (ws / "out").mkdir(parents=True)
    tl = REPO / "fixtures/video_pipeline/timeline.json"
    r = _run(
        [
            sys.executable,
            str(REPO / "scripts/video/run_render.py"),
            str(tl),
            "-o",
            str(ws / "out"),
            "--placeholder",
            "--no-job-check",
        ]
    )
    assert r.returncode == 0, r.stderr
